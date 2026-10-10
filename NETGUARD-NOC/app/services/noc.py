"""Servicios del MVP: ninguna entrada de log ni comando ejecuta código."""
import hashlib
import re
from datetime import datetime, timedelta, timezone
from ipaddress import ip_address
from sqlalchemy import inspect, text
from app.database import Base, engine, SessionLocal
from app.models.device import Device
from app.models.syslog_message import SyslogMessage
from app.models.alert import Alert
from app.models.incident import Incident, IncidentNote
from app.models.audit import Audit
from app.services.security_notifications import register, deliver

LEVELS = ['Emergencia', 'Alerta', 'Crítico', 'Error', 'Advertencia', 'Aviso', 'Informativo', 'Depuración']
SOURCES = {
    'Cisco': 'https://netascode.cisco.com/docs/data_models/iosxe/device/logging/',
    'Fortinet': 'https://docs.fortinet.com/document/fortigate/7.0.1/cli-reference/445620/config-log-syslogd-setting',
    'Huawei': 'https://info.support.huawei.com/hedex/api/pages/EDOC1000053358/YEF0907R/25/resources/en-us_cliref_0133018022.html'
}

def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

def audit(db, actor, action, result, device_id=None, proposal='', approval='NO APLICA - SIMULACION'):
    record = Audit(actor=(actor or 'Operador local')[:100], action=action,
                   result=str(result), device_id=device_id, proposal=proposal,
                   approval=approval, evidence_hash=hashlib.sha256(str(result).encode()).hexdigest())
    db.add(record)
    return record

def initialize():
    """Migración aditiva: conserva la base de datos anterior y sus IDs."""
    Base.metadata.create_all(engine)
    cols = {x['name'] for x in inspect(engine).get_columns('syslog_messages')}
    additions = {'facility':'INTEGER', 'device_id':'INTEGER', 'brand':'VARCHAR(80)',
                 'event_at':'DATETIME', 'simulated':'INTEGER NOT NULL DEFAULT 1'}
    with engine.begin() as connection:
        for name, sqltype in additions.items():
            if name not in cols:
                connection.execute(text(f'ALTER TABLE syslog_messages ADD COLUMN {name} {sqltype}'))
    from app.services.seed import create_initial_devices
    create_initial_devices()
    with SessionLocal() as db:
        for row in db.query(SyslogMessage).filter(SyslogMessage.facility.is_(None)).all():
            match = re.match(r'^<(\d{1,3})>', row.message)
            if match and int(match[1]) <= 191:
                row.facility = int(match[1]) // 8
            device = db.query(Device).filter_by(ip_address=row.source_ip).first()
            if device:
                row.device_id, row.brand = device.id, device.brand
        db.commit()

def ingest(db, message, source_ip, actor='Receptor local'):
    """PRI válido + fuente permitida; 100 mensajes/minuto y deduplicación 10 s."""
    try:
        source_ip = str(ip_address(source_ip))
    except ValueError:
        return {'accepted':False, 'reason':'IP inválida'}
    device = db.query(Device).filter_by(ip_address=source_ip).first()
    if not device and source_ip != '127.0.0.1':
        audit(db, actor, 'FUENTE_BLOQUEADA', source_ip)
        db.commit()
        return {'accepted':False, 'reason':'Fuente no inventariada'}
    match = re.match(r'^<(\d{1,3})>', message)
    if not match or int(match[1]) > 191 or len(message.encode()) > 8192:
        audit(db, actor, 'FORMATO_BLOQUEADO', 'PRI inválido o mensaje mayor a 8 KiB', proposal=message[:200])
        db.commit()
        return {'accepted':False, 'reason':'Formato PRI inválido o mensaje demasiado largo'}
    now = utcnow()
    count = db.query(SyslogMessage).filter(SyslogMessage.source_ip == source_ip,
            SyslogMessage.received_at >= now-timedelta(minutes=1)).count()
    if count >= 100:
        return {'accepted':False, 'reason':'Límite de 100 mensajes/minuto por fuente'}
    duplicate = db.query(SyslogMessage).filter(SyslogMessage.source_ip == source_ip,
            SyslogMessage.message == message, SyslogMessage.received_at >= now-timedelta(seconds=10)).first()
    if duplicate:
        return {'accepted':False, 'reason':'Duplicado dentro de 10 segundos', 'id':duplicate.id}
    pri = int(match[1])
    # Timestamp RFC5424 opcional; conserva la hora de recepción cuando no existe.
    event_at = None
    timestamp = re.match(r'^<\d+>\d+\s+(\S+)', message)
    if timestamp and timestamp[1] != '-':
        try:
            parsed = datetime.fromisoformat(timestamp[1].replace('Z', '+00:00'))
            if parsed.tzinfo:
                event_at = parsed.astimezone(timezone.utc).replace(tzinfo=None)
        except ValueError:
            pass
    row = SyslogMessage(source_ip=source_ip, severity=pri % 8, facility=pri // 8,
          message=message, received_at=now, event_at=event_at,
          device_id=device.id if device else None, brand=device.brand if device else 'Laboratorio local', simulated=1)
    try:
        db.add(row)
        db.flush()
        if row.severity <= 2:
            db.add(Alert(syslog_message_id=row.id, status='PENDIENTE', created_at=now))
        audit(db, actor, 'EVENTO_RECIBIDO', f'Evento {row.id}; facility {row.facility}; severidad {row.severity}', row.device_id)
        notification_id = register(db, row, now)
        db.commit()
        if notification_id:
            deliver(db, notification_id)
        return {'accepted':True, 'id':row.id}
    except Exception:
        db.rollback()
        raise

COMMANDS = {
    'Cisco': ('show version','show ip interface brief','show logging'),
    'Fortinet': ('get system status','get system interface','show log syslogd setting'),
    'Huawei': ('display version','display interface brief','display info-center')
}

def simulate_command(db, device_id, command, actor):
    device = db.get(Device, device_id)
    allowed = bool(device and command.strip() in COMMANDS.get(device.brand, ()))
    if allowed:
        output = f'SIMULACIÓN - SIN CONEXIÓN SSH\nEquipo: {device.name}\nMarca: {device.brand}\nVersión registrada: {device.version or "No registrada"}\nComando: {command}\nRespuesta educativa. No verifica el estado real.'
    else:
        output = 'BLOQUEADO: comando o equipo fuera de la lista permitida. No se ejecutó ninguna acción.'
    audit(db, actor, 'CONSOLA_PERMITIDA' if allowed else 'CONSOLA_BLOQUEADA', output, device_id, command)
    db.commit()
    return {'allowed':allowed, 'output':output}

def make_config(brand, host, severity, port):
    address = ip_address(host)
    if address.version != 4 or not 0 <= severity <= 7 or not 1 <= port <= 65535:
        raise ValueError('Utiliza IPv4, nivel 0–7 y puerto 1–65535.')
    if brand not in COMMANDS:
        raise ValueError('Marca no soportada')
    header = '# PLANTILLA DE LABORATORIO: NO EJECUTADA\n# Validar SO, versión, modo, conectividad y autorización humana.\n# 127.0.0.1 solo sirve dentro del propio equipo; para equipos externos usar IP del colector.\n# Crear backup antes del cambio; no guardar hasta verificar recepción.\n'
    if brand == 'Cisco':
        body = f'configure terminal\nlogging host {host} transport udp port {port}\nlogging trap {severity}\nend\n! Verificación: show logging\n! Reversa: no logging host {host} transport udp port {port}\n'
    elif brand == 'Fortinet':
        levels = ['emergency','alert','critical','error','warning','notification','information','debug']
        body = f'config log syslogd setting\n    set status enable\n    set server "{host}"\n    set mode udp\n    set port {port}\nend\nconfig log syslogd filter\n    set severity {levels[severity]}\nend\n# Verificación: show log syslogd setting\n# Reversa: restaurar backup; deshabilitar syslogd solo si antes estaba deshabilitado.\n'
    else:
        levels = ['emergencies','alert','critical','error','warning','notification','informational','debugging']
        body = f'system-view\ninfo-center enable\ninfo-center loghost {host} channel 2 port {port}\ninfo-center source default channel 2 log level {levels[severity]}\nquit\n# Verificación: display info-center\n# Reversa: undo info-center loghost {host}; restaurar política anterior.\n# Revisar compatibilidad de port/channel en la versión VRP instalada.\n'
    return header + body + f'\n# Fuente oficial: {SOURCES[brand]}\n'
