"""Reglas docentes explícitas: indicios, nunca prueba definitiva de un ataque.

Los logs son datos: ninguna coincidencia ejecuta código, HTML o comandos.
Telegram recibe únicamente ID, IP, nivel y reglas; no se envía el log completo,
que podría contener contraseñas o datos personales. Token fuera del repositorio.
"""
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from app.models.security import Threat, Notification
from app.models.syslog_message import SyslogMessage

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / 'data' / 'telegram.json'
# Ejemplos explicables al profesor; pueden producir falsos positivos.
RULES = {
    'ACCESO_FALLIDO': (r'failed password|authentication fail(?:ed|ure)|login failed|acceso denegado|contrase[nñ]a incorrecta', 'Posible intento de acceso no autorizado. Revisar usuario y origen.'),
    'ATAQUE_RED': (r'\b(?:ddos|dos attack|port scan|syn flood|brute force|fuerza bruta)\b', 'Indicio de ataque de red o fuerza bruta reportado por el dispositivo.'),
    'MALWARE': (r'\b(?:malware|ransomware|trojan|botnet)\b', 'El evento menciona posible software malicioso. Validar la evidencia.'),
    'XSS': (r'<script\b|javascript:|onerror\s*=', 'Texto con patrón de inyección web. Se muestra escapado y nunca se ejecuta.'),
    'COMANDO_DESTRUCTIVO': (r'\berase\s+startup-config\b|\brm\s+-rf\b|\bformat\s+flash\b', 'Comando potencialmente destructivo dentro del log. No se ejecuta.'),
    'INYECCION_INSTRUCCIONES': (r'ignore (?:all |previous )?instructions|ignora (?:las )?instrucciones|revela (?:el |los )?(?:token|secretos)', 'Intento de introducir instrucciones en un evento. El log se trata como datos.')
}

def detect_threats(message):
    return [name for name, (pattern, _) in RULES.items() if re.search(pattern, message, re.I)]

def settings():
    try:
        config = json.loads(CONFIG.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        config = {}
    return {'token': os.environ.get('NETGUARD_TELEGRAM_TOKEN') or config.get('token', ''),
            'chat_id': os.environ.get('NETGUARD_TELEGRAM_CHAT_ID') or config.get('chat_id', '')}

def send_telegram(message):
    config = settings()
    if not re.fullmatch(r'\d+:[A-Za-z0-9_-]+', str(config.get('token', ''))) or not re.fullmatch(r'-?\d+', str(config.get('chat_id', ''))):
        raise ValueError('Telegram sin configurar')
    request = Request('https://api.telegram.org/bot' + config['token'] + '/sendMessage',
        data=json.dumps({'chat_id': config['chat_id'], 'text': message, 'link_preview_options': {'is_disabled': True}}).encode(),
        headers={'Content-Type': 'application/json'})
    # HTTPS verifica el certificado. No se utiliza parse_mode: texto plano.
    with urlopen(request, timeout=5) as response:
        result = json.load(response)
    if not result.get('ok') or 'message_id' not in result.get('result', {}):
        raise RuntimeError('Telegram no confirmó el envío')
    return result['result']['message_id']

def register(db, event, now):
    rules = detect_threats(event.message)
    for rule in rules:
        db.add(Threat(message_id=event.id, rule=rule, description=RULES[rule][1], detected_at=now))
    if rules or event.severity <= 2:
        notification = Notification(message_id=event.id, created_at=now, status='PENDIENTE')
        db.add(notification)
        db.flush()
        return notification.id
    return None

def deliver(db, notification_id):
    """La recepción ya fue confirmada: un fallo de Telegram no pierde el evento.

    Sin reintentos automáticos: ante un timeout Telegram pudo recibir el aviso.
    El reintento manual advierte esa posibilidad. Una ENVIADA nunca se repite.
    """
    row = db.get(Notification, notification_id)
    if not row or row.status == 'ENVIADA':
        return
    event = db.get(SyslogMessage, row.message_id)
    rules = [x.rule for x in db.query(Threat).filter_by(message_id=event.id).all()]
    message = (f'NETGUARD NOC · ALERTA DE LABORATORIO\nEvento: {event.id}\n'
               f'Origen: {event.source_ip}\nSeveridad: {event.severity}\n'
               f'Indicios: {", ".join(rules) if rules else "Evento crítico; requiere revisión"}\n'
               'Revisar Eventos Syslog, Amenazas y Alertas en la aplicación local.')
    try:
        row.telegram_message_id = send_telegram(message)
        row.status = 'ENVIADA'
        row.sent_at = datetime.now(timezone.utc).replace(tzinfo=None)
        row.detail = 'Telegram confirmó la aceptación del mensaje; no confirma lectura.'
    except ValueError:
        row.status, row.detail = 'SIN_CONFIGURAR', 'Configura el bot y el chat en este computador.'
    except Exception:
        # Nunca mostrar excepción/URL: podrían revelar el token del bot.
        row.status, row.detail = 'ERROR', 'Envío no confirmado. Revisa conexión, bot y chat; un reintento podría duplicarlo.'
    db.commit()
