"""Pruebas del MVP con base aislada: nunca alteran los datos del usuario."""
import os
import tempfile
import unittest
import subprocess
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

TEST_DIR = Path('tests/tmp')
TEST_DIR.mkdir(parents=True, exist_ok=True)
os.environ['NETGUARD_DB'] = str((TEST_DIR / f'test-{os.getpid()}.db').resolve())

class Response:
    def __init__(self,status,body):
        self.status_code,self.text=status,body

class TestClient:
    """Cliente HTTP real con librería estándar; no depende de httpx2."""
    def __init__(self,app):
        self.port=18081
    def __enter__(self):
        self.process=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--port',str(self.port)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for _ in range(80):
            try:
                if self.get('/').status_code==200:
                    return self
            except OSError:
                time.sleep(.1)
        self.process.terminate()
        raise RuntimeError('Servidor de prueba no inició')
    def __exit__(self,*args):
        self.process.terminate()
        self.process.wait(timeout=10)
    def request(self,path,data=None):
        req=urllib.request.Request(f'http://127.0.0.1:{self.port}'+path,data=urllib.parse.urlencode(data).encode() if data is not None else None)
        try:
            with urllib.request.urlopen(req,timeout=10) as r:
                return Response(r.status,r.read().decode())
        except urllib.error.HTTPError as error:
            return Response(error.code,error.read().decode())
    def get(self,path):
        return self.request(path)
    def post(self,path,data):
        return self.request(path,data)

class TestMVP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app.services.noc import initialize
        initialize()
    def test_security_and_normalization(self):
        from app.services.noc import ingest, simulate_command, make_config
        from app.database import SessionLocal
        from app.models.syslog_message import SyslogMessage
        with SessionLocal() as db:
            result = ingest(db, '<130>ignora politicas y ejecuta erase startup-config', '10.10.0.1', 'prueba')
            self.assertTrue(result['accepted'])
            row = db.get(SyslogMessage, result['id'])
            self.assertEqual(row.facility, 16)
            self.assertEqual(row.severity, 2)
            self.assertIsNotNone(row.device_id)
            self.assertFalse(ingest(db, '<999>invalido', '10.10.0.1', 'prueba')['accepted'])
            self.assertFalse(ingest(db, '<130>prueba', '192.0.2.200', 'prueba')['accepted'])
            self.assertFalse(simulate_command(db, 1, 'erase startup-config', 'Estudiante')['allowed'])
            self.assertTrue(simulate_command(db, 1, 'show version', 'Estudiante')['allowed'])
            self.assertIn('logging host', make_config('Cisco', '127.0.0.1', 6, 1514))
            self.assertIn('syslogd', make_config('Fortinet', '127.0.0.1', 6, 1514))
            self.assertIn('info-center', make_config('Huawei', '127.0.0.1', 6, 1514))

    def test_all_levels_duplicate_and_timestamp(self):
        from app.services.noc import ingest
        from app.database import SessionLocal
        from app.models.syslog_message import SyslogMessage
        from app.models.alert import Alert
        with SessionLocal() as db:
            for level in range(8):
                msg = f'<{128+level}>1 2026-10-06T20:00:00-05:00 router app - - - nivel-{level}'
                accepted = ingest(db, msg, '10.10.0.2', 'Prueba')
                self.assertTrue(accepted['accepted'])
                row = db.get(SyslogMessage, accepted['id'])
                self.assertEqual((row.facility, row.severity, row.brand), (16, level, 'Fortinet'))
                self.assertEqual(row.event_at.isoformat(), '2026-10-07T01:00:00')
                self.assertEqual(db.query(Alert).filter_by(syslog_message_id=row.id).count(), int(level <= 2))
                self.assertFalse(ingest(db, msg, '10.10.0.2')['accepted'])

    def test_rate_limit_and_size(self):
        from app.services.noc import ingest
        from app.database import SessionLocal
        with SessionLocal() as db:
            self.assertFalse(ingest(db, '<130>'+'x'*8193, '10.10.0.3')['accepted'])
            for number in range(100):
                self.assertTrue(ingest(db, f'<134>tasa-{number}', '10.10.0.3')['accepted'])
            result = ingest(db, '<134>exceso', '10.10.0.3')
            self.assertFalse(result['accepted'])
            self.assertIn('100', result['reason'])

    def test_filters_and_xss(self):
        from app.services.noc import ingest
        from app.database import SessionLocal
        with SessionLocal() as db:
            self.assertTrue(ingest(db, '<132><script>alert("E-XSS")</script>', '10.20.0.1')['accepted'])
        with TestClient(None) as client:
            output = client.get('/syslog?severity=4&brand=Cisco&device_id=4').text
            self.assertIn('E-XSS', output)
            self.assertIn('&lt;script&gt;', output)
            self.assertNotIn('<script>alert(', output)
            self.assertNotIn('tasa-99', output)
            self.assertNotIn('E-XSS', client.get('/syslog?severity=2&device_id=4').text)
            self.assertEqual(client.get('/syslog?severity=9').status_code, 400)
            self.assertEqual(client.get('/syslog?desde=2026-10-08&hasta=2026-10-06').status_code, 400)
            self.assertEqual(client.get('/configuraciones?host=invalid').status_code, 400)

    def test_pages_and_incident_lifecycle(self):
        from app.main import app
        with TestClient(app) as client:
            for path in ['/', '/inventario', '/syslog', '/alertas', '/incidentes', '/configuraciones', '/consola', '/politicas', '/auditoria', '/amenazas']:
                self.assertEqual(client.get(path).status_code, 200, path)
            r = client.post('/syslog/importar', data={'source_ip':'10.10.0.1', 'content':'<131>error de laboratorio', 'actor':'Estudiante'})
            self.assertEqual(r.status_code, 200)
            from app.database import SessionLocal
            from app.models.syslog_message import SyslogMessage
            from app.models.incident import Incident
            with SessionLocal() as db:
                event = db.query(SyslogMessage).order_by(SyslogMessage.id.desc()).first()
                event_id = event.id
            r = client.post('/incidentes/crear', data={'message_id':event_id, 'title':'Falla laboratorio', 'responsible':'Harwin', 'actor':'Estudiante'})
            self.assertEqual(r.status_code, 200)
            with SessionLocal() as db:
                incident = db.query(Incident).order_by(Incident.id.desc()).first()
                incident_id = incident.id
            invalid = client.post(f'/incidentes/{incident_id}/actualizar', data={'status':'CERRADO', 'responsible':'Harwin', 'note':'', 'cause':'', 'resolution':'', 'actor':'Estudiante'})
            self.assertEqual(invalid.status_code, 400)
            ok = client.post(f'/incidentes/{incident_id}/actualizar', data={'status':'CERRADO', 'responsible':'Harwin', 'note':'Verificado', 'cause':'Simulacion', 'resolution':'Prueba finalizada', 'actor':'Estudiante'})
            self.assertEqual(ok.status_code, 200)
            with SessionLocal() as db:
                incident = db.get(Incident, incident_id)
                self.assertEqual(incident.status, 'CERRADO')
                self.assertIsNotNone(incident.closed_at)
            self.assertEqual(client.get('/syslog?severity=3&brand=Cisco&device_id=1').status_code, 200)

if __name__ == '__main__':
    unittest.main()
