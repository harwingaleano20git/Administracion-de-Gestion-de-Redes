"""Colector UDP de laboratorio con políticas compartidas."""
import socket
from app.database import SessionLocal
from app.services.noc import initialize, ingest

def recibir_mensajes():
    initialize()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receptor:
        receptor.bind(('127.0.0.1',1514))
        print('NETGUARD v0.2.0: laboratorio UDP 127.0.0.1:1514. Ctrl+C para detener.')
        try:
            while True:
                data, origin = receptor.recvfrom(65535)
                with SessionLocal() as db:
                    try:
                        print(ingest(db,data.decode('utf-8',errors='replace'),origin[0]),flush=True)
                    except Exception as error:
                        db.rollback()
                        print('Error controlado:',error,flush=True)
        except KeyboardInterrupt:
            print('Receptor detenido')

if __name__ == '__main__':
    recibir_mensajes()
