"""Autoriza destinos y huellas; no conecta ni guarda contraseñas."""
import json
import re
from app.database import SessionLocal
from app.models.device import Device
from app.services.noc import initialize
from app.services.ssh_console import TARGETS, load_targets

def main():
    initialize()
    with SessionLocal() as db:
        devices = {row.ip_address: row.name for row in db.query(Device).all()}
    for ip, name in devices.items():
        print(f'{ip}: {name}')
    address = input('IP del equipo autorizado en Inventario: ').strip()
    if address not in devices:
        print('Registra primero el equipo en Inventario.')
        return
    port = input('Puerto SSH [22]: ').strip() or '22'
    if not port.isdigit() or not 1 <= int(port) <= 65535:
        print('Puerto inválido.')
        return
    print('Solicita al administrador la huella SHA256 y verifícala por un canal de confianza.')
    fingerprint = input('Huella verificada (SHA256:...): ').strip()
    if not re.fullmatch(r'SHA256:[A-Za-z0-9+/]{43}', fingerprint):
        print('Huella inválida. No se guardó nada.')
        return
    if input('¿Verificaste la huella y tienes autorización? Escribe SI: ').strip().upper() != 'SI':
        return
    targets = load_targets()
    targets[address] = {'port': int(port), 'fingerprint': fingerprint}
    TARGETS.parent.mkdir(parents=True, exist_ok=True)
    TARGETS.write_text(json.dumps(targets, indent=2), encoding='utf-8')
    print('Destino registrado. Ya puedes usar la consulta SSH en Consola de equipos.')

if __name__ == '__main__':
    main()
