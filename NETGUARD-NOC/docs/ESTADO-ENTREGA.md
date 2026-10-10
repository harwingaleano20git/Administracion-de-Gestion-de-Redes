# Estado comprobado · v0.2.1

Actualización del 10 de octubre de 2026. Se mantiene la entrega histórica v0.2.0.

- Implementados: inventario, Syslog, filtros, alertas, incidentes, auditoría, reglas de amenazas, avisos Telegram configurables y consultas SSH restringidas.
- Doce pruebas automatizadas aprobadas con base aislada. SSH y Telegram se verifican con dobles de prueba, sin destinos externos.
- Página Amenazas y Consola verificadas con HTTP 200 en la instalación local.
- Telegram real: recepción confirmada por el usuario y captura del teléfono, evento 3, origen 10.10.0.1, severidad 2, ACCESO_FALLIDO.
- Packet Tracer: ping sin pérdidas, SSH v2 y acceso desde PC0 con consulta show version, acreditados por capturas.
- Pendiente: conectar la consola NETGUARD desde Windows a un equipo externo autorizado.
- Evidencia actualizada: docs/VERIFICACION-2026-10-10.md.
- No hay autenticación web ni RBAC efectivo. El actor y la autorización son declarados.
- El PDF y video v0.2.0 conservan el alcance original. El anexo y guion v0.2.1 describen esta ampliación y sus límites.
- No publicar data, .env, contraseñas o tokens. Los datos iniciales no prueban conectividad.
