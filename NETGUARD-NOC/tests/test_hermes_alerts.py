import json
import os
import unittest
from unittest.mock import patch


class HermesAlertsTests(unittest.TestCase):
    def test_each_manual_query_starts_a_separate_session(self):
        from app.services.hermes_alerts import request_json
        with patch('http.client.HTTPConnection') as connect:
            connection = connect.return_value
            connection.getresponse.return_value.status = 200
            connection.getresponse.return_value.read.return_value = b'{}'
            for _ in range(2):
                request_json('POST', '/v1/chat/completions', 'test-key', {'messages': []})
            sessions = [call.kwargs['headers'].get('X-Hermes-Session-Id') for call in connection.request.call_args_list]
            self.assertTrue(all(sessions))
            self.assertNotEqual(*sessions)

    def test_route_escapes_recommendation_and_preserves_notification(self):
        import test_mvp  # Configura una SQLite aislada antes de importar la aplicación.
        from starlette.requests import Request
        from app.main import app
        from app.database import SessionLocal
        from app.models.security import Notification
        from app.routes_mvp import consult_hermes
        from app.services.hermes_alerts import HermesUnavailable
        from app.services.noc import ingest

        with SessionLocal() as db, patch('app.services.security_notifications.send_telegram', return_value=123):
            event_id = ingest(db, '<130>Failed password for hermes-route-test', '127.0.0.1')['id']
        scope = {'type': 'http', 'method': 'POST', 'path': f'/amenazas/{event_id}/hermes',
                 'headers': [(b'host', b'127.0.0.1:8002')], 'scheme': 'http', 'app': app}
        request = Request(scope)
        with patch('app.routes_mvp.consult_alert', return_value='<script>bad()</script>') as query:
            response = consult_hermes(request, event_id)
            query.assert_called_once_with(event_id, 2, ['ACCESO_FALLIDO'])
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'&lt;script&gt;', response.body)
            self.assertNotIn(b'<script>bad()', response.body)
        with patch('app.routes_mvp.consult_alert', side_effect=HermesUnavailable('No disponible')):
            self.assertEqual(consult_hermes(request, event_id).status_code, 503)
        with SessionLocal() as db:
            self.assertEqual(db.query(Notification).filter_by(message_id=event_id).one().status, 'ENVIADA')

    def test_disabled_never_contacts_gateway(self):
        from app.services.hermes_alerts import HermesUnavailable, consult_alert
        with patch.dict(os.environ, {'NETGUARD_HERMES_KEY': ''}), patch('http.client.HTTPConnection') as connect:
            with self.assertRaises(HermesUnavailable):
                consult_alert(42, 2, ['ACCESO_FALLIDO'])
            connect.assert_not_called()

    def test_only_known_metadata_reaches_model(self):
        from app.services.hermes_alerts import consult_alert
        reply = {'choices': [{'message': {'content': 'Revisa el acceso.'}}]}
        with patch.dict(os.environ, {'NETGUARD_HERMES_KEY': 'test-key'}), patch(
            'app.services.hermes_alerts.request_json', side_effect=[
                {'object': 'list', 'platform': 'api_server', 'data': [
                    {'enabled': False, 'tools': ['terminal']}
                ]}, reply
            ]
        ) as http:
            self.assertEqual(consult_alert(42, 2, ['ACCESO_FALLIDO', 'raw IP or credential']), 'Revisa el acceso.')
            args = http.call_args.args
            self.assertEqual(args[1], '/v1/chat/completions')
            self.assertEqual(json.loads(args[3]['messages'][-1]['content']), {
                'evento': 42, 'severidad': 2, 'indicios': ['ACCESO_FALLIDO']
            })

    def test_active_tools_stop_before_sending_alert(self):
        from app.services.hermes_alerts import HermesUnavailable, consult_alert
        tools = {'object': 'list', 'platform': 'api_server', 'data': [
            {'enabled': True, 'tools': ['terminal']}
        ]}
        with patch.dict(os.environ, {'NETGUARD_HERMES_KEY': 'test-key'}), patch(
            'app.services.hermes_alerts.request_json', return_value=tools
        ) as http:
            with self.assertRaises(HermesUnavailable):
                consult_alert(42, 2, [])
            self.assertEqual(http.call_count, 1)

    def test_malformed_response_or_tool_call_is_rejected(self):
        from app.services.hermes_alerts import HermesUnavailable, consult_alert
        for reply in ({'choices': []}, {'choices': [{'message': {'content': 'texto', 'tool_calls': [{}]}}]}):
            with self.subTest(reply=reply), patch.dict(os.environ, {'NETGUARD_HERMES_KEY': 'test-key'}), patch(
                'app.services.hermes_alerts.request_json', side_effect=[[], reply]
            ):
                with self.assertRaises(HermesUnavailable):
                    consult_alert(42, 2, [])
