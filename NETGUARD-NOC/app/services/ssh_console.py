"""SSH real de consulta: lista exacta, huella verificada y sin guardar contraseñas."""
import base64
import hashlib
import hmac
import json
import re
import time
from pathlib import Path
import paramiko
from app.models.device import Device
from app.services.noc import COMMANDS, audit

TARGETS = Path(__file__).resolve().parents[2] / 'data' / 'ssh_targets.json'

def load_targets():
    try:
        result = json.loads(TARGETS.read_text(encoding='utf-8'))
        return result if isinstance(result, dict) else {}
    except (OSError, ValueError):
        return {}

class PinnedHostKeyPolicy(paramiko.MissingHostKeyPolicy):
    def __init__(self, expected):
        self.expected = expected

    def missing_host_key(self, client, hostname, key):
        actual = 'SHA256:' + base64.b64encode(hashlib.sha256(key.asbytes()).digest()).decode().rstrip('=')
        if not hmac.compare_digest(actual, self.expected):
            raise paramiko.SSHException('Identidad SSH distinta de la huella autorizada')

def connect_and_read(host, port, fingerprint, username, password, command):
    client = paramiko.SSHClient()
    # Nunca AutoAddPolicy: comprobar identidad antes de entregar credenciales.
    client.set_missing_host_key_policy(PinnedHostKeyPolicy(fingerprint))
    channel = None
    try:
        client.connect(host, port=port, username=username, password=password,
            look_for_keys=False, allow_agent=False, timeout=5,
            banner_timeout=5, auth_timeout=5, channel_timeout=5)
        _, stdout, _ = client.exec_command(command, timeout=5, get_pty=False)
        channel = stdout.channel
        deadline, chunks, size = time.monotonic() + 15, [], 0
        while time.monotonic() < deadline:
            for ready, receive in [(channel.recv_ready, channel.recv), (channel.recv_stderr_ready, channel.recv_stderr)]:
                if ready():
                    chunk = receive(4096)
                    size += len(chunk)
                    if size > 65536:
                        raise RuntimeError('Respuesta supera 64 KiB')
                    chunks.append(chunk)
            if channel.exit_status_ready() and not channel.recv_ready() and not channel.recv_stderr_ready():
                if channel.recv_exit_status() != 0:
                    raise RuntimeError('El equipo no confirmó ejecución correcta')
                return b''.join(chunks).decode('utf-8', errors='replace')
            time.sleep(.05)
        raise TimeoutError('Consulta no completada')
    finally:
        if channel is not None:
            channel.close()
        client.close()

def query_device(db, device_id, command, actor, username, password, approved):
    device = db.get(Device, device_id)
    command = command.strip()
    target = load_targets().get(device.ip_address) if device else None
    allowed = (device and command in COMMANDS.get(device.brand, ()) and target
               and approved and actor.strip() and username.strip() and password)
    if not allowed:
        output = 'BLOQUEADO: verifica equipo registrado para SSH, comando permitido, credenciales y autorización.'
        audit(db, actor, 'SSH_BLOQUEADO', output, device.id if device else None,
              proposal=command[:500], approval='NO AUTORIZADA')
        db.commit()
        return {'allowed': False, 'output': output}
    try:
        port = int(target['port'])
        fingerprint = str(target['fingerprint'])
        if not 1 <= port <= 65535 or not re.fullmatch(r'SHA256:[A-Za-z0-9+/]{43}', fingerprint):
            raise ValueError('Perfil inválido')
        answer = connect_and_read(device.ip_address, port, fingerprint, username.strip(), password, command)
        answer = answer.replace(password, '[CREDENCIAL OCULTA]')
        output = f'SSH REAL · {device.name} · {device.ip_address}:{port}\nComando: {command}\n{answer}'
        action, success = 'SSH_CONSULTA_REAL', True
    except Exception:
        # No registrar excepciones crudas que puedan contener credenciales.
        output = 'SSH NO COMPLETADA: revisa IP, puerto, credenciales, huella y soporte de comandos SSH exec. No se produjo una respuesta simulada.'
        action, success = 'SSH_ERROR', False
    audit(db, actor, action, output, device.id, proposal=command,
          approval='CONSULTA DE LECTURA AUTORIZADA POR OPERADOR DECLARADO')
    db.commit()
    return {'allowed': success, 'output': output}
