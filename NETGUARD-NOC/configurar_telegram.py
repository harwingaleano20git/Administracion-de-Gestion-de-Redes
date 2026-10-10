"""Configura el bot localmente: no imprime ni publica el token."""
import getpass
import json
import re
from urllib.request import Request, urlopen
from app.services.security_notifications import CONFIG, send_telegram

def main():
    print('En Telegram abre @BotFather, envía /newbot y crea tu bot.')
    print('Abre el chat de tu nuevo bot y pulsa Iniciar o envía /start.')
    token = getpass.getpass('Pega aquí el token de BotFather (no se muestra): ').strip()
    if not re.fullmatch(r'\d+:[A-Za-z0-9_-]+', token):
        print('El token no tiene el formato esperado. No se guardó nada.')
        return
    print('Buscando chats privados que iniciaron tu bot...')
    try:
        request = Request('https://api.telegram.org/bot' + token + '/getUpdates',
                          data=b'{}', headers={'Content-Type': 'application/json'})
        with urlopen(request, timeout=10) as response:
            result = json.load(response)
        if not result.get('ok'):
            raise ValueError()
        chats = {str(x['message']['chat']['id']): x['message']['chat'].get('first_name', 'Chat privado')
                 for x in result.get('result', []) if x.get('message', {}).get('chat', {}).get('type') == 'private'}
    except Exception:
        print('No fue posible consultar Telegram. Revisa el token y la conexión. No se guardó nada.')
        return
    if not chats:
        print('No aparece tu chat. Envía /start al nuevo bot y vuelve a ejecutar este configurador.')
        return
    for chat_id, name in chats.items():
        print(f'Chat disponible: {name} · ID {chat_id}')
    selected = input('Escribe el ID del chat al que autorizas enviar las alertas: ').strip()
    if selected not in chats:
        print('Selecciona un chat de la lista. No se guardó nada.')
        return
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps({'token': token, 'chat_id': selected}), encoding='utf-8')
    try:
        send_telegram('NETGUARD NOC: prueba de conexión. Este chat recibirá alertas críticas e indicios de amenazas del laboratorio.')
        print('Telegram aceptó el mensaje de prueba. Comprueba que llegó a tu chat.')
    except Exception:
        print('Configuración guardada, pero el envío no fue confirmado. Revisa bot, chat y conexión.')
    print('El token queda en data/telegram.json. No compartas ese archivo ni la carpeta data.')

if __name__ == '__main__':
    main()
