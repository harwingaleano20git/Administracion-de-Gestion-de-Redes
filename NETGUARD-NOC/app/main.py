from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.services.noc import initialize, LEVELS
from app.models.incident import Incident
from app.models.audit import Audit
import app.routes_mvp as routes_mvp

from app.database import Base, engine, SessionLocal
from app.models.device import Device
from app.models.syslog_message import SyslogMessage
from app.models.alert import Alert
from app.services.seed import create_initial_devices
from datetime import datetime, timedelta, timezone
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from ipaddress import ip_address

app = FastAPI(
    title="NETGUARD NOC",
    description="Plataforma de monitoreo Syslog y gestión de incidentes",
    version="0.2.0"
)

initialize()

create_initial_devices()

app.mount("/static", StaticFiles(directory=str(Path(__file__).resolve().parent.parent / "static")), name="static")

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))
routes_mvp.templates = templates
app.include_router(routes_mvp.router)
templates.env.globals["levels"] = LEVELS


@app.get("/")
def inicio(request: Request):

    db = SessionLocal()

    try:
        devices = db.query(Device).all()
        pending_alert_count = db.query(Alert).filter(
            Alert.status == "PENDIENTE"
        ).count()
        desde = datetime.now(timezone.utc) - timedelta(hours=24)

        syslog_24h_count = db.query(SyslogMessage).filter(
            SyslogMessage.received_at >= desde
        ).count()
        critical_count = db.query(SyslogMessage).filter(
            SyslogMessage.severity.in_([0, 1, 2])
        ).count()

        error_count = db.query(SyslogMessage).filter(
            SyslogMessage.severity == 3
        ).count()

        warning_count = db.query(SyslogMessage).filter(
            SyslogMessage.severity == 4
        ).count()

        info_count = db.query(SyslogMessage).filter(
            SyslogMessage.severity == 6
        ).count()

        total_devices = len(devices)

        active_devices = sum(
            1 for device in devices
            if device.status == "ONLINE"
        )

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "devices": devices,
                "total_devices": total_devices,
                "active_devices": active_devices,
                 "critical_count": critical_count,
                "error_count": error_count,
                "warning_count": warning_count,
                "info_count": info_count,
                "syslog_24h_count": syslog_24h_count,
                "pending_alert_count": pending_alert_count,
                "recent_events": db.query(SyslogMessage).order_by(SyslogMessage.id.desc()).limit(5).all(),
                "open_incidents": db.query(Incident).filter(Incident.status != "CERRADO").count(),
                "levels": LEVELS
            }
        )

    finally:
        db.close()
@app.get("/inventario")
def inventario(request: Request):
    db = SessionLocal()

    try:
        devices = db.query(Device).all()

        return templates.TemplateResponse(
            request=request,
            name="inventario.html",
            context={"devices": devices}
        )
    finally:
        db.close()
@app.get("/syslog")
def ver_syslog(request: Request, gravedad: str = "todos", buscar: str = "", severity: str = "", brand: str = "", device_id: str = "", desde: str = "", hasta: str = ""):
    with SessionLocal() as db:
        consulta = db.query(SyslogMessage)
        grupos = {"criticos": [0,1,2], "error": [3], "advertencia": [4], "informativo": [6]}
        if gravedad in grupos:
            consulta = consulta.filter(SyslogMessage.severity.in_(grupos[gravedad]))
        if severity:
            if severity not in [str(x) for x in range(8)]:
                raise HTTPException(400, "Severidad inválida")
            consulta = consulta.filter(SyslogMessage.severity == int(severity))
        if brand:
            consulta = consulta.filter(SyslogMessage.brand == brand)
        if device_id:
            if not device_id.isdigit():
                raise HTTPException(400,"Equipo inválido")
            consulta = consulta.filter(SyslogMessage.device_id == int(device_id))
        try:
            if desde:
                consulta = consulta.filter(SyslogMessage.received_at >= datetime.fromisoformat(desde))
            if hasta:
                consulta = consulta.filter(SyslogMessage.received_at < datetime.fromisoformat(hasta) + timedelta(days=1))
            if desde and hasta and desde > hasta:
                raise ValueError("Rango invertido")
        except ValueError:
            raise HTTPException(400,"Fechas inválidas; usa AAAA-MM-DD y un rango ordenado")
        if buscar.strip():
            consulta = consulta.filter(SyslogMessage.message.icontains(buscar.strip(),autoescape=True))
        return templates.TemplateResponse(request=request,name="syslog.html",context={
            "mensajes":consulta.order_by(SyslogMessage.id.desc()).limit(100).all(),
            "gravedad":gravedad,"buscar":buscar,"severity":severity,"brand":brand,"device_id":device_id,
            "desde":desde,"hasta":hasta,"devices":db.query(Device).all(),"levels":LEVELS,
            "brands": [x[0] for x in db.query(SyslogMessage.brand).distinct().all() if x[0]]})

@app.post("/inventario/agregar")
def agregar_dispositivo(
    request: Request,
    name: str = Form(...),
    ip: str = Form(...),
    brand: str = Form(...),
    model: str = Form(""),
    version: str = Form(""),
    location: str = Form("")
):
    datos = {
        "name": name.strip(),
        "ip": ip.strip(),
        "brand": brand.strip(),
        "model": model.strip(),
        "version": version.strip(),
        "location": location.strip()
    }

    error = None

    if not datos["name"] or not datos["brand"]:
        error = "El nombre y la marca son obligatorios."

    try:
        datos["ip"] = str(ip_address(datos["ip"]))
    except ValueError:
        error = "Escribe una dirección IP válida."

    with SessionLocal() as db:
        if error is None:
            dispositivo = Device(
                name=datos["name"],
                ip_address=datos["ip"],
                brand=datos["brand"],
                model=datos["model"] or None,
                version=datos["version"] or None,
                location=datos["location"] or None,
                status="OFFLINE"
            )

            try:
                db.add(dispositivo)
                db.flush()
                routes_mvp.audit(db, "Operador local", "DISPOSITIVO_CREADO", dispositivo.name, dispositivo.id)
                db.commit()
            except IntegrityError:
                db.rollback()
                error = "No se pudo guardar: esa IP ya está registrada."

        if error is not None:
            devices = db.query(Device).all()

            return templates.TemplateResponse(
                request=request,
                name="inventario.html",
                context={
                    "devices": devices,
                    "error": error,
                    "datos": datos
                },
                status_code=400
            )

    return RedirectResponse(
        url="/inventario",
        status_code=303
    )       
@app.get("/inventario/{device_id}/editar")
def formulario_editar_dispositivo(
    request: Request,
    device_id: int
):
    with SessionLocal() as db:
        dispositivo = db.get(Device, device_id)

        if dispositivo is None:
            raise HTTPException(
                status_code=404,
                detail="Dispositivo no encontrado"
            )

        datos = {
            "name": dispositivo.name,
            "ip": dispositivo.ip_address,
            "brand": dispositivo.brand,
            "model": dispositivo.model or "",
            "version": dispositivo.version or "",
            "location": dispositivo.location or ""
        }

        return templates.TemplateResponse(
            request=request,
            name="editar_dispositivo.html",
            context={
                "device_id": device_id,
                "datos": datos
            }
        )
@app.post("/inventario/{device_id}/editar")
def guardar_edicion_dispositivo(
    request: Request,
    device_id: int,
    name: str = Form(...),
    ip: str = Form(...),
    brand: str = Form(...),
    model: str = Form(""),
    version: str = Form(""),
    location: str = Form("")
):
    datos = {
        "name": name.strip(),
        "ip": ip.strip(),
        "brand": brand.strip(),
        "model": model.strip(),
        "version": version.strip(),
        "location": location.strip()
    }

    error = None

    if not datos["name"] or not datos["brand"]:
        error = "El nombre y la marca son obligatorios."

    try:
        datos["ip"] = str(ip_address(datos["ip"]))
    except ValueError:
        error = "Escribe una dirección IP válida."

    with SessionLocal() as db:
        dispositivo = db.get(Device, device_id)

        if dispositivo is None:
            raise HTTPException(
                status_code=404,
                detail="Dispositivo no encontrado"
            )

        if error is None:
            dispositivo.name = datos["name"]
            dispositivo.ip_address = datos["ip"]
            dispositivo.brand = datos["brand"]
            dispositivo.model = datos["model"] or None
            dispositivo.version = datos["version"] or None
            dispositivo.location = datos["location"] or None
            dispositivo.updated_at = datetime.now(timezone.utc)

            try:
                routes_mvp.audit(db, "Operador local", "DISPOSITIVO_EDITADO", dispositivo.name, dispositivo.id)
                db.commit()
            except IntegrityError:
                db.rollback()
                error = "No se pudo guardar: esa IP ya está registrada."

        if error is not None:
            return templates.TemplateResponse(
                request=request,
                name="editar_dispositivo.html",
                context={
                    "device_id": device_id,
                    "datos": datos,
                    "error": error
                },
                status_code=400
            )

    return RedirectResponse(
        url="/inventario",
        status_code=303
    )        

@app.get("/alertas")
def ver_alertas(request: Request, estado: str = "todos"):
    opciones = {
        "todos": None,
        "pendientes": "PENDIENTE",
        "revisadas": "REVISADA"
    }

    if estado not in opciones:
        estado = "todos"

    with SessionLocal() as db:
        consulta = (
            db.query(Alert, SyslogMessage)
            .join(
                SyslogMessage,
                Alert.syslog_message_id == SyslogMessage.id
            )
        )

        if opciones[estado] is not None:
            consulta = consulta.filter(
                Alert.status == opciones[estado]
            )

        resultados = (
            consulta
            .order_by(Alert.id.desc())
            .limit(100)
            .all()
        )

        return templates.TemplateResponse(
            request=request,
            name="alertas.html",
            context={
                "alertas": resultados,
                "estado": estado
            }
        )
@app.post("/alertas/{alert_id}/revisar")
def revisar_alerta(alert_id: int):
    with SessionLocal() as db:
        alerta = db.get(Alert, alert_id)

        if alerta is None:
            raise HTTPException(
                status_code=404,
                detail="Alerta no encontrada"
            )

        if alerta.status == "PENDIENTE":
            alerta.status = "REVISADA"
            alerta.reviewed_at = datetime.now(timezone.utc)
            routes_mvp.audit(db, "Operador local", "ALERTA_REVISADA", f"Alerta {alert_id}")
            db.commit()

    return RedirectResponse(
        url="/alertas",
        status_code=303
    )