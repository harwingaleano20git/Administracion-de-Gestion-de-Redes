# Código y alcance de la ampliación

Harwin Galeano Beltran · Ingeniería de Telecomunicaciones

## Qué archivo mostrar

| Requisito | Archivo | Qué hace |
|---|---|---|
| Amenazas | app/services/security_notifications.py | RULES y detect_threats identifican indicios de acceso fallido, ataques de red, malware, XSS, comandos destructivos e instrucciones maliciosas. |
| Avisos Telegram | app/services/security_notifications.py | send_telegram usa HTTPS; register crea la notificación y deliver guarda su resultado. No envía el log completo. |
| Registro de amenazas y avisos | app/models/security.py | Tablas Threat y Notification. |
| Recepción de eventos | app/services/noc.py | ingest guarda el evento, analiza patrones y solicita el aviso después de confirmar la recepción. |
| Conexión a equipos | app/services/ssh_console.py | query_device valida destino y comando; connect_and_read conecta por SSH. PinnedHostKeyPolicy comprueba la huella SHA256 antes de autenticar. |
| Rutas de la aplicación | app/routes_mvp.py | /amenazas muestra evidencias; /consola/ssh consulta el equipo seleccionado. |
| Interfaz de consola | templates/consola.html | Formulario SSH separado de la consola de práctica. |
| Configuración local | configurar_ssh.py y configurar_telegram.py | Preparan destinos y bot sin incluir credenciales en GitHub. |
| Pruebas | tests/test_ssh_console.py y tests/test_security_notifications.py | Validan bloqueos, identidad, detección y manejo de fallos. |

## Estado comprobado

Las doce pruebas automatizadas pasaron sobre una base aislada. Incluyen la funcionalidad anterior, fallos/success de Telegram mediante dobles de prueba y consultas SSH con conexión sustituida para verificar reglas. No constituyen evidencia de entrega real en Telegram ni de conexión a un router físico.

Pendiente de prueba externa: el usuario debe iniciar sesión en Telegram, crear el bot y ejecutar CONFIGURAR_TELEGRAM.cmd. Para SSH se necesita un equipo autorizado, accesible desde Windows, con SSH activo, usuario de lectura y huella SHA256 verificada por un canal de confianza.

## Preparación de SSH

1. Registrar en Inventario la IP y marca reales del equipo.
2. Solicitar al administrador usuario de consulta y huella SHA256 de la clave pública SSH del servidor. No compartir la contraseña en el chat ni incluirla en la entrega.
3. Ejecutar CONFIGURAR_SSH.cmd y registrar IP, puerto y huella verificada.
4. Reiniciar NETGUARD con ABRIR-NETGUARD.cmd si aún usa el código anterior.
5. En Consola de equipos, introducir usuario y contraseña, seleccionar la consulta permitida y declarar autorización.
6. Mostrar la respuesta SSH REAL y su registro en Auditoría. Si falla, conservar el resultado SSH_ERROR y corregir el acceso; no reemplazarlo por una simulación.

Este adaptador utiliza solicitudes SSH exec. Algunos sistemas de red requieren una sesión CLI interactiva; esos equipos necesitarán un adaptador específico y validación con su modelo/versión. La aplicación no ejecuta cambios de configuración. No hay RBAC efectivo ni autenticación web; el servidor debe seguir limitado a 127.0.0.1 y un computador de confianza. La autorización declarada no sustituye el permiso del propietario del equipo.

Packet Tracer se conserva como práctica separada de configuración; la conexión desde Python en Windows no está verificada. Para demostrar integración, utilizar un equipo físico o una máquina virtual de red con SSH accesible y autorizado.

No publicar la carpeta data: contiene base de datos y configuración local. La contraseña SSH no se guarda; el token Telegram sí queda en un archivo local sin cifrado, protegido por la cuenta Windows. Las salidas consultadas pueden contener datos operativos y se guardan en Auditoría: revisar antes de compartir evidencias.

Esta ampliación es posterior al release v0.2.0 publicado; ese release mantiene la entrega original. El PDF y video anteriores no se han modificado y no demuestran estas nuevas funciones.

Referencia del cliente SSH: https://docs.paramiko.org/en/stable/api/client.html

## Actualización comprobada · 10 de octubre de 2026

Telegram ya tiene recepción real confirmada por captura y por el usuario. La práctica SSH dentro de Packet Tracer también está acreditada mediante ping, inicio de sesión y show version. Los apartados anteriores describen el estado al publicar v0.2.1; este resultado posterior lo actualiza. Sigue pendiente la conexión SSH desde la consola NETGUARD a un equipo externo. Detalle: docs/VERIFICACION-2026-10-10.md (desde docs: VERIFICACION-2026-10-10.md).
