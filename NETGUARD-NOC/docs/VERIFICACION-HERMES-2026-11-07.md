# Prueba local de Hermes en NETGUARD

Fecha: 7 de noviembre de 2026. Ruta probada: NETGUARD → Hermes Agent 0.23.0 → Ollama con Qwen3 4B Instruct en este PC. El gateway anunció cero herramientas activas. Se usó una alerta de laboratorio que ya existía en NETGUARD; no se creó ni se reenvió una alerta para la prueba.

- Evento 5, severidad Syslog 2, indicio `ACCESO_FALLIDO`.
- La consulta devolvió HTTP 200 y un resumen en 71,6 segundos.
- El estado Telegram fue `ENVIADA` antes y después.
- Pasaron 18 pruebas automatizadas de NETGUARD con base aislada.

Hermes sugirió prioridad **Media** y recomendó revisar la recurrencia en los registros de autenticación, identificar el origen en los registros locales y revisar la cuenta asociada. La prioridad es una recomendación, no una reclasificación: la severidad de NETGUARD permanece en **2 (crítica)**. Hermes no recibió la IP ni el mensaje Syslog original.

Para usarlo, abre **Amenazas y Telegram → Historial de notificaciones → Consultar con Hermes**. Después de reiniciar Windows, usa `ABRIR-NETGUARD-HERMES.cmd` en la carpeta de la aplicación. La primera respuesta puede demorar más de un minuto en este equipo. La consulta es manual y no modifica la alerta.
