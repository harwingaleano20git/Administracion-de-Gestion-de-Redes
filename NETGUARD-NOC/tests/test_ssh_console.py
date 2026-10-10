"""Consultas SSH: bloqueos antes de conectar y verificaciÃ³n del servidor."""
import os
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

Path('tests/tmp').mkdir(parents=True, exist_ok=True)
os.environ.setdefault('NETGUARD_DB', str(Path(f'tests/tmp/ssh-{os.getpid()}.db').resolve()))

class TestSSH(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app.services.noc import initialize
        initialize()

    def test_unapproved_and_destructive_commands_never_connect(self):
        from app.services.ssh_console import query_device
        from app.database import SessionLocal
        with SessionLocal() as db, patch('app.services.ssh_console.load_targets', return_value={}), patch('app.services.ssh_console.connect_and_read') as connection:
            result = query_device(db, 1, 'show version', 'Prueba', 'user', 'secret', False)
            self.assertFalse(result['allowed'])
            result = query_device(db, 1, 'erase startup-config', 'Prueba', 'user', 'secret', True)
            self.assertFalse(result['allowed'])
            connection.assert_not_called()

    def test_pinned_target_success_and_failure_never_log_password(self):
        from app.services.ssh_console import query_device
        from app.database import SessionLocal
        from app.models.audit import Audit
        target = {'10.10.0.1': {'port': 22, 'fingerprint': 'SHA256:' + 'a' * 43}}
        with SessionLocal() as db, patch('app.services.ssh_console.load_targets', return_value=target), patch('app.services.ssh_console.connect_and_read', return_value='Cisco IOS: salida de prueba'):
            result = query_device(db, 1, 'show version', 'Prueba', 'user', 'secret-test', True)
            self.assertTrue(result['allowed'])
            self.assertIn('SSH REAL', result['output'])
        with SessionLocal() as db, patch('app.services.ssh_console.load_targets', return_value=target), patch('app.services.ssh_console.connect_and_read', side_effect=RuntimeError('secret-test')):
            result = query_device(db, 1, 'show version', 'Prueba', 'user', 'secret-test', True)
            self.assertFalse(result['allowed'])
            row = db.query(Audit).order_by(Audit.id.desc()).first()
            self.assertNotIn('secret-test', row.result)

    def test_host_fingerprint_mismatch_rejected(self):
        import paramiko
        from app.services.ssh_console import PinnedHostKeyPolicy
        with self.assertRaises(paramiko.SSHException):
            PinnedHostKeyPolicy('SHA256:incorrecta').missing_host_key(MagicMock(), 'test', paramiko.RSAKey.generate(2048))

if __name__ == '__main__':
    unittest.main()
