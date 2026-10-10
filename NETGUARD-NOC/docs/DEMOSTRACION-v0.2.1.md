# Demostración de NETGUARD NOC v0.2.1

Harwin Galeano Beltran · Ingeniería de Telecomunicaciones · 9 de octubre de 2026

## Antes de comenzar

Cerrar la instancia anterior con Ctrl+C e iniciar ABRIR-NETGUARD.cmd desde esta carpeta. Abrir http://127.0.0.1:8002 y actualizar con Ctrl+F5. El servidor solo debe escuchar en 127.0.0.1. No mostrar tokens ni contraseñas durante la exposición.

## 1. Mostrar dónde está el código

Abrir la carpeta completa en Visual Studio Code. Mostrar RULES y detect_threats en app/services/security_notifications.py. Explicar: «Busco patrones que pueden indicar una amenaza. La coincidencia requiere revisión; no confirma por sí sola un ataque».

Después mostrar register, send_telegram y deliver en ese mismo archivo. El evento se guarda antes del envío; una falla del canal no borra la recepción. Telegram recibe ID, origen, severidad y reglas, sin el texto completo del log.

## 2. Crear un evento de laboratorio

En Eventos Syslog, usar IP 127.0.0.1 e introducir un mensaje nuevo:

```text
<130>Failed password for admin - demostracion del profesor
```

Importar y abrir Amenazas y Telegram. Debe aparecer ACCESO_FALLIDO y una notificación. Si se repite el mismo evento antes de diez segundos, se rechaza como duplicado. El ejemplo es inventado para la prueba y no significa que haya ocurrido una intrusión real.

## 3. Explicar la notificación

Cuando el bot esté configurado, comprobar en el celular el aviso y contrastar su ID con el evento de la aplicación. Antes de configurar, el estado será SIN_CONFIGURAR; esto demuestra que la aplicación no inventa un envío exitoso. No presentar esa pantalla como prueba de recepción en Telegram.

El configurador local es CONFIGURAR_TELEGRAM.cmd. Requiere crear un bot con @BotFather, iniciar el chat y autorizar el destino. El código de ingreso a Telegram es distinto del token del bot.

## 4. Mostrar la consola orientada a equipos reales

Abrir app/services/ssh_console.py y mostrar query_device, PinnedHostKeyPolicy y connect_and_read. En la interfaz, señalar equipo, usuario, contraseña, comando y autorización. La aplicación comprueba el destino autorizado y su huella SSH antes de autenticar; solo permite las consultas de la lista del fabricante.

Si existe un equipo real o virtual autorizado con SSH accesible desde Windows, registrarlo en Inventario y CONFIGURAR_SSH.cmd, y consultar show version (Cisco), get system status (Fortinet) o display version (Huawei). Mostrar la salida recibida y Auditoría. No utilizar credenciales inventadas ni declarar una conexión que no se realizó.

Si no hay equipo disponible, mostrar la interfaz y los controles, aclarando: «La integración está implementada y tiene pruebas automatizadas; falta validar la respuesta con un equipo autorizado». Packet Tracer queda como práctica separada; no hay integración externa comprobada.

## 5. Comprobar el bloqueo y seguimiento

Un comando fuera de la lista, como erase startup-config, se bloquea antes de conectar. No hace falta usar credenciales reales para demostrar ese bloqueo. Mostrar el registro SSH_BLOQUEADO en Auditoría. No confundir la consola de simulación con SSH REAL.

Crear un incidente desde el evento, asignar responsable y agregar una nota. Para cerrarlo, registrar causa y resolución del caso de laboratorio. Marcar la alerta como revisada y comprobar el contador de pendientes.

## Estado de evidencia al publicar

Doce pruebas automatizadas aprobadas con base aislada. Se comprobó HTTP 200 para Amenazas y Consola en la instalación local tras reiniciar el servidor. Las pruebas de envío y conexión utilizan dobles controlados; no hay evidencia de un aviso recibido en Telegram ni de una consulta a un equipo externo. Ambas verificaciones deben realizarse antes de afirmar que funcionan de extremo a extremo.

Referencia para el cliente SSH: https://docs.paramiko.org/en/stable/api/client.html
Referencia para avisos: https://core.telegram.org/bots/api#sendmessage
