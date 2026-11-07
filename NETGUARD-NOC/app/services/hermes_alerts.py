"""Consulta opcional de Hermes Agent, sin acceso directo a alertas ni equipos."""
import http.client
import json
import os
import re
from uuid import uuid4

from app.services.security_notifications import RULES


class HermesUnavailable(Exception):
    """Mensaje apto para la interfaz, sin datos del proveedor ni secretos."""


def configured_key():
    key = os.environ.get('NETGUARD_HERMES_KEY', '').strip()
    return key if re.fullmatch(r'[!-~]{1,512}', key) else ''


def request_json(method, path, key, payload=None):
    # Conexión directa al loopback, sin proxies ni redirecciones.
    # Un modelo local en CPU puede tardar más en cargar y generar la primera respuesta.
    conn = http.client.HTTPConnection('127.0.0.1', 8642, timeout=90 if payload else 3)
    try:
        headers = {'Authorization': f'Bearer {key}', 'Accept': 'application/json'}
        body = None
        if payload is not None:
            headers['Content-Type'] = 'application/json'
            # Hermes reusa sesiones según el contenido si el cliente no indica una nueva.
            headers['X-Hermes-Session-Id'] = f'netguard-{uuid4().hex}'
            body = json.dumps(payload).encode('utf-8')
        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()
        if response.status != 200:
            raise HermesUnavailable('Hermes no aceptó la consulta. Revisa el gateway y su configuración.')
        content = response.read(65537)
        if len(content) > 65536:
            raise HermesUnavailable('La respuesta de Hermes supera el tamaño permitido.')
        return json.loads(content)
    except TimeoutError:
        raise HermesUnavailable('Hermes tardó más de lo permitido. Vuelve a consultar cuando el modelo esté listo.') from None
    except (OSError, http.client.HTTPException, ValueError):
        raise HermesUnavailable('Hermes no está disponible o devolvió una respuesta inválida.') from None
    finally:
        conn.close()


def consult_alert(event_id, severity, indicators):
    key = configured_key()
    if not key:
        raise HermesUnavailable('La consulta con Hermes está desactivada.')

    toolsets = request_json('GET', '/v1/toolsets', key)
    if isinstance(toolsets, dict) and toolsets.get('object') == 'list' and toolsets.get('platform') == 'api_server':
        toolsets = toolsets.get('data')
    if not isinstance(toolsets, list) or any(
        not isinstance(entry, dict)
        or type(entry.get('enabled')) is not bool
        or (entry['enabled'] and entry.get('tools') != [])
        for entry in toolsets
    ):
        raise HermesUnavailable('No se verificó un perfil de Hermes sin herramientas activas. No se envió la alerta.')

    metadata = {
        'evento': int(event_id),
        'severidad': severity if type(severity) is int and 0 <= severity <= 7 else None,
        'indicios': sorted(set(indicators).intersection(RULES)),
    }
    payload = {
        'model': os.environ.get('NETGUARD_HERMES_MODEL', 'hermes-agent'),
        'stream': False,
        'messages': [
            {'role': 'system', 'content': (
                'Asiste al operador de un NOC en español. Resume el evento, sugiere una prioridad '
                'y ofrece hasta tres pasos de verificación. Usa solo los metadatos dados. Distingue '
                'indicios de incidentes confirmados. No ejecutes acciones ni propongas cambios automáticos.'
            )},
            {'role': 'user', 'content': json.dumps(metadata)},
        ],
    }
    data = request_json('POST', '/v1/chat/completions', key, payload)
    try:
        message = data['choices'][0]['message']
        answer = message['content']
        if message.get('tool_calls') or message.get('function_call') or not isinstance(answer, str) or not answer.strip():
            raise ValueError
    except (KeyError, IndexError, TypeError, AttributeError, ValueError):
        raise HermesUnavailable('Hermes no devolvió un resumen de texto válido.') from None
    return answer.strip()[:4000]
