"""Módulos docentes del MVP; ninguna ruta ejecuta comandos del sistema."""
import csv
import io
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from app.models.device import Device
from app.models.syslog_message import SyslogMessage
from app.models.incident import Incident, IncidentNote
from app.models.audit import Audit
from app.services.noc import audit, ingest, make_config, simulate_command, utcnow, COMMANDS, SOURCES

router = APIRouter()
templates = None

@router.get('/amenazas')
def threats(request: Request):
    from app.models.security import Threat, Notification
    from app.services.security_notifications import settings, RULES
    config = settings()
    with SessionLocal() as db:
        return page(request, 'amenazas.html', rules=RULES,
            configured=bool(config.get('token') and config.get('chat_id')),
            threats=db.query(Threat, SyslogMessage).join(SyslogMessage, Threat.message_id == SyslogMessage.id).order_by(Threat.id.desc()).limit(100).all(),
            notifications=db.query(Notification).order_by(Notification.id.desc()).limit(100).all())

@router.post('/notificaciones/{notification_id}/reintentar')
def retry_notification(notification_id: int):
    from app.models.security import Notification
    from app.services.security_notifications import deliver
    with SessionLocal() as db:
        if not db.get(Notification, notification_id):
            raise HTTPException(404, 'Notificación no encontrada')
        deliver(db, notification_id)
    return RedirectResponse('/amenazas', 303)

def page(request, name, **context):
    return templates.TemplateResponse(request=request, name=name, context=context)

@router.get('/incidentes')
def incidents(request: Request):
    with SessionLocal() as db:
        return page(request, 'incidentes.html', incidents=db.query(Incident).order_by(Incident.id.desc()).all(), events=db.query(SyslogMessage).order_by(SyslogMessage.id.desc()).limit(100).all(), notes=db.query(IncidentNote).order_by(IncidentNote.id.desc()).all())

@router.post('/incidentes/crear')
def create_incident(request: Request, message_id:int=Form(...), title:str=Form(...), responsible:str=Form(...), actor:str=Form(...)):
    with SessionLocal() as db:
        if not db.get(SyslogMessage,message_id):
            raise HTTPException(404,'Evento no encontrado')
        if not title.strip() or not responsible.strip() or not actor.strip():
            raise HTTPException(400,'Título, responsable y actor son obligatorios')
        row=Incident(message_id=message_id,title=title.strip()[:160],responsible=responsible.strip()[:100])
        db.add(row)
        try:
            db.flush()
            audit(db,actor,'INCIDENTE_CREADO',f'Incidente {row.id}; evento {message_id}; responsable {responsible}')
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(400,'El evento ya tiene un incidente')
    return RedirectResponse('/incidentes',303)

@router.post('/incidentes/{incident_id}/actualizar')
def update_incident(request:Request,incident_id:int,status:str=Form(...),responsible:str=Form(...),note:str=Form(''),cause:str=Form(''),resolution:str=Form(''),actor:str=Form(...)):
    if status not in ('ABIERTO','EN_PROCESO','CERRADO') or not responsible.strip() or not actor.strip():
        raise HTTPException(400,'Estado, responsable o actor inválido')
    if status=='CERRADO' and (not cause.strip() or not resolution.strip()):
        raise HTTPException(400,'El cierre requiere causa y resolución')
    with SessionLocal() as db:
        row=db.get(Incident,incident_id)
        if not row:
            raise HTTPException(404,'Incidente no encontrado')
        before=row.status
        row.status,row.responsible=status,responsible.strip()[:100]
        row.cause,row.resolution=cause.strip(),resolution.strip()
        row.updated_at=utcnow()
        if status=='CERRADO' and before!='CERRADO':
            row.closed_at=utcnow()
        elif status!='CERRADO':
            row.closed_at=None
        if note.strip():
            db.add(IncidentNote(incident_id=incident_id,actor=actor.strip(),note=note.strip()))
        audit(db,actor,'INCIDENTE_ACTUALIZADO',f'Incidente {incident_id}: {before} -> {status}; responsable {responsible}; nota {note}')
        db.commit()
    return RedirectResponse('/incidentes',303)

@router.post('/syslog/importar')
def import_syslog(request:Request,source_ip:str=Form(...),content:str=Form(...),actor:str=Form(...)):
    if len(content)>200000 or len(content.splitlines())>100:
        raise HTTPException(400,'Máximo 100 líneas y 200 KB por importación')
    with SessionLocal() as db:
        results=[ingest(db,line.strip(),source_ip,actor) for line in content.splitlines() if line.strip()]
    return page(request,'import_result.html',results=results)

@router.get('/configuraciones')
def config_page(request:Request,brand:str='Cisco',host:str='127.0.0.1',severity:int=6,port:int=1514):
    try:
        config=make_config(brand,host,severity,port)
    except ValueError as error:
        raise HTTPException(400,str(error))
    return page(request,'configuraciones.html',config=config,brand=brand,host=host,severity=severity,port=port,sources=SOURCES)

@router.post('/configuraciones/proponer')
def propose_config(brand:str=Form(...),host:str=Form(...),severity:int=Form(...),port:int=Form(...),actor:str=Form(...),approved:str=Form('')):
    try:
        config=make_config(brand,host,severity,port)
    except ValueError as error:
        raise HTTPException(400,str(error))
    with SessionLocal() as db:
        audit(db,actor,'PROPUESTA_CONFIGURACION','Plantilla documentada. NO ejecutada en equipos reales.',proposal=config,approval='REVISIÓN HUMANA DECLARADA' if approved=='si' else 'PENDIENTE DE APROBACIÓN')
        db.commit()
    return RedirectResponse('/auditoria',303)

@router.get('/consola')
def console_page(request:Request):
    with SessionLocal() as db:
        return page(request,'consola.html',devices=db.query(Device).all(),commands=COMMANDS,output=None)

@router.post('/consola')
def console_post(request:Request,device_id:int=Form(...),command:str=Form(...),actor:str=Form(...)):
    with SessionLocal() as db:
        result=simulate_command(db,device_id,command[:500],actor)
        return page(request,'consola.html',devices=db.query(Device).all(),commands=COMMANDS,output=result['output'])

@router.post('/consola/ssh')
def console_ssh(request:Request,device_id:int=Form(...),command:str=Form(...),actor:str=Form(...),username:str=Form(...),password:str=Form(...),approved:str=Form('')):
    from app.services.ssh_console import query_device
    from urllib.parse import urlsplit
    origin=request.headers.get('origin')
    if origin and urlsplit(origin).netloc != request.headers.get('host'):
        raise HTTPException(403,'Solicitud desde otro origen bloqueada')
    if len(command)>500 or len(username)>100 or len(password)>1024:
        raise HTTPException(400,'Campos demasiado largos')
    with SessionLocal() as db:
        result=query_device(db,device_id,command,actor,username,password,approved=='si')
        return page(request,'consola.html',devices=db.query(Device).all(),commands=COMMANDS,output=result['output'])

@router.get('/politicas')
def policies(request:Request):
    return page(request,'politicas.html')

@router.get('/auditoria')
def audit_page(request:Request):
    with SessionLocal() as db:
        return page(request,'auditoria.html',rows=db.query(Audit).order_by(Audit.id.desc()).limit(200).all())

@router.get('/auditoria/exportar')
def export_audit():
    out=io.StringIO()
    writer=csv.writer(out)
    writer.writerow(['ID','UTC','Actor declarado','Accion','Equipo','Propuesta','Aprobacion','Resultado','SHA256'])
    def safe(value):
        value=str(value or '')
        return "'"+value if value.startswith(('=','+','-','@','\t','\r')) else value
    with SessionLocal() as db:
        for row in db.query(Audit).order_by(Audit.id).all():
            writer.writerow([safe(x) for x in [row.id,row.created_at,row.actor,row.action,row.device_id,row.proposal,row.approval,row.result,row.evidence_hash]])
    return Response(out.getvalue(),media_type='text/csv',headers={'Content-Disposition':'attachment; filename="auditoria.csv"'})
