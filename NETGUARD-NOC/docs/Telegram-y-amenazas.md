# Amenazas y notificaciones por Telegram

Esta ampliación agrega reglas explicables en `app/services/security_notifications.py` y la página `/amenazas`. Detecta indicios de acceso fallido, ataques de red, malware, inyección web, comandos destructivos e instrucciones incrustadas en logs. Son patrones de laboratorio con posibles falsos positivos; no reemplazan un sistema de detección de intrusiones.

Una alerta crítica (severidad 0–2) o un evento con coincidencias genera un aviso. Telegram recibe el ID, IP, severidad y nombres de reglas. No recibe el texto completo del evento ni ejecuta sus instrucciones. La recepción se guarda antes de intentar el envío.

## Configuración local

1. En Telegram abre el bot oficial `@BotFather`, envía `/newbot` y sigue sus instrucciones.
2. Abre tu nuevo bot y envía `/start`.
3. Ejecuta `CONFIGURAR_TELEGRAM.cmd` desde la carpeta de la aplicación. Pega el token en el configurador local; el texto se oculta. Selecciona el ID de tu chat mostrado por el configurador.
4. Comprueba el mensaje de prueba en Telegram. Reinicia la aplicación si aún ejecuta el código anterior.
5. Importa desde Eventos Syslog, con IP `127.0.0.1`, el texto `<130>Failed password for admin - prueba de laboratorio`.
6. Abre Amenazas y Telegram. Deben aparecer ACCESO_FALLIDO y la notificación. Confirma además el mensaje recibido en Telegram.

La configuración se almacena en `data/telegram.json`, excluido por `.gitignore`. No publicar, enviar ni incluir la carpeta `data` en ZIP. Alternativa para despliegues: variables `NETGUARD_TELEGRAM_TOKEN` y `NETGUARD_TELEGRAM_CHAT_ID`. El almacenamiento local no cifra el token: protege tu cuenta Windows y sus archivos.

ENVIADA significa que la API aceptó el mensaje, sin probar lectura. ERROR indica envío no confirmado; un timeout puede ocurrir después de que Telegram lo recibió. El botón Reintentar envío requiere una acción humana y puede duplicar ese aviso. No hay reintentos automáticos. El envío síncrono tiene un límite de espera de cinco segundos por aviso: esta versión es de laboratorio, no está diseñada para grandes volúmenes ni acceso público multiusuario.

Los bloqueos por fuente desconocida o formato inválido siguen en Auditoría; las reglas de la página Amenazas analizan eventos aceptados. Los eventos históricos no se notifican retroactivamente.

API oficial: https://core.telegram.org/bots/api#sendmessage
Creación de bots: https://core.telegram.org/bots/features#botfather
