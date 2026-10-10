# Estado comprobado · v0.2.1

Actualización del 9 de octubre de 2026. Se mantiene la entrega histórica v0.2.0.

- Implementados: inventario, Syslog, filtros, alertas, incidentes, auditoría, reglas de amenazas, avisos Telegram configurables y consultas SSH restringidas.
- Doce pruebas automatizadas aprobadas con base aislada. SSH y Telegram se verifican con dobles de prueba, sin destinos externos.
- Página Amenazas y Consola verificadas con HTTP 200 en la instalación local.
- Pendientes: bot configurado y mensaje recibido en Telegram; equipo externo autorizado, huella e identidad verificadas y respuesta SSH real.
- No hay autenticación web ni RBAC efectivo. El actor y la autorización son declarados.
- El PDF y video v0.2.0 conservan el alcance original. El anexo y guion v0.2.1 describen esta ampliación y sus límites.
- No publicar data, .env, contraseñas o tokens. Los datos iniciales no prueban conectividad.
