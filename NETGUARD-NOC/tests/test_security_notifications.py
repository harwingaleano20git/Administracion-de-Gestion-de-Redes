"""Sin Telegram real ni datos del usuario: validación de detección y envíos."""
import os
import unittest
from pathlib import Path
from unittest.mock import patch

Path('tests/tmp').mkdir(parents=True, exist_ok=True)
os.environ.setdefault('NETGUARD_DB', str(Path(f'tests/tmp/security-{os.getpid()}.db').resolve()))

class TestSecurity(unittest.TestCase):
    def test_detection_does_not_execute_text(self):
        from app.services.security_notifications import detect_threats
        self.assertEqual(detect_threats('<134>Interfaz activa'), [])
        self.assertIn('ACCESO_FALLIDO', detect_threats('<134>Failed password for admin'))
        self.assertIn('XSS', detect_threats('<130><script>alert(1)</script>'))
        self.assertIn('COMANDO_DESTRUCTIVO', detect_threats('<130>erase startup-config'))

    def test_failure_preserves_event_and_success_is_not_resent(self):
        from app.services.noc import initialize, ingest
        from app.database import SessionLocal
        from app.models.security import Threat, Notification
        from app.models.syslog_message import SyslogMessage
        from app.services.security_notifications import deliver
        initialize()
        with SessionLocal() as db, patch('app.services.security_notifications.send_telegram', side_effect=RuntimeError('token secreto')):
            result = ingest(db, '<134>Failed password for test-security', '127.0.0.1')
            self.assertTrue(result['accepted'])
            self.assertIsNotNone(db.get(SyslogMessage, result['id']))
            self.assertEqual(db.query(Threat).filter_by(message_id=result['id']).count(), 1)
            notification = db.query(Notification).filter_by(message_id=result['id']).one()
            self.assertEqual(notification.status, 'ERROR')
            self.assertNotIn('token secreto', notification.detail)
            with patch('app.services.security_notifications.send_telegram', return_value=123) as sender:
                deliver(db, notification.id)
                deliver(db, notification.id)
                self.assertEqual(sender.call_count, 1)
                self.assertEqual(notification.status, 'ENVIADA')

    def test_missing_configuration_does_not_claim_delivery(self):
        from app.services.security_notifications import send_telegram
        with patch('app.services.security_notifications.settings', return_value={}):
            with self.assertRaises(ValueError):
                send_telegram('Prueba')

    def test_telegram_protocol_and_rejected_response(self):
        import io
        import json
        from app.services.security_notifications import send_telegram
        config = {'token': '123:TEST_ONLY', 'chat_id': '456'}
        with patch('app.services.security_notifications.settings', return_value=config), patch('app.services.security_notifications.urlopen', return_value=io.BytesIO(b'{"ok":true,"result":{"message_id":789}}')) as transport:
            self.assertEqual(send_telegram('Prueba'), 789)
            request = transport.call_args.args[0]
            self.assertTrue(request.full_url.startswith('https://api.telegram.org/'))
            self.assertEqual(json.loads(request.data)['chat_id'], '456')
            self.assertNotIn('parse_mode', json.loads(request.data))
        with patch('app.services.security_notifications.settings', return_value=config), patch('app.services.security_notifications.urlopen', return_value=io.BytesIO(b'{"ok":false}')):
            with self.assertRaises(RuntimeError):
                send_telegram('Prueba')

if __name__ == '__main__':
    unittest.main()
