# Consultar alertas con Hermes Agent

NETGUARD agrega una consulta manual en **Amenazas y Telegram → Historial de notificaciones**. Envía a Hermes el ID del evento, su severidad y los códigos de indicios conocidos. La recomendación se muestra como texto para revisión humana. No se envía el mensaje Syslog original, la IP ni credenciales del NOC. No se altera la alerta ni se reenvía Telegram.

## Configuración local

1. Instala y configura [Hermes Agent](https://hermes-agent.nousresearch.com/docs) con un perfil dedicado a NETGUARD y un proveedor de modelos de tu elección. Según ese proveedor, Hermes puede enviarle los metadatos que recibe.
2. En ese perfil, usa `hermes tools` para desactivar las herramientas de la plataforma API Server. Mantén también desactivadas las integraciones, la memoria externa y las tareas automáticas que no necesites. Revisa que `/v1/toolsets` no anuncie herramientas activas. Si NETGUARD no puede verificarlo, rechaza la consulta antes de enviar los metadatos.
3. Activa el [servidor API oficial](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server) con `API_SERVER_ENABLED=true`, una `API_SERVER_KEY` privada, `API_SERVER_HOST=127.0.0.1` y `API_SERVER_PORT=8642`. Inicia `hermes gateway` con el perfil dedicado. No habilites acceso desde la red.
4. En la terminal donde inicias NETGUARD, define `NETGUARD_HERMES_KEY` con la misma clave. Para introducirla sin escribirla en el historial de PowerShell:

   ```powershell
   $env:NETGUARD_HERMES_KEY = Read-Host 'Clave privada del gateway Hermes' -MaskInput
   ```

   Si tu perfil publica un nombre de modelo distinto a `hermes-agent`, define `NETGUARD_HERMES_MODEL` con ese nombre. Desde esa misma terminal, inicia NETGUARD con el comando habitual de tu instalación. Mantén la aplicación en loopback.
5. Abre **Amenazas y Telegram**, elige una alerta de laboratorio y pulsa **Consultar con Hermes**. Sin la clave, el panel muestra **Desactivado** y no envía solicitudes.

La clave del gateway se utiliza en la cabecera HTTP de autenticación local. No se guarda en la base ni se incluye en la consulta al modelo. No la compartas con el token del bot ni la subas al repositorio. La comprobación de herramientas depende de la configuración declarada por el gateway; conserva el perfil dedicado y no le des acceso a datos del NOC.

## Verificación

Las pruebas automatizadas simulan el gateway: comprueban la lista de datos permitidos, el bloqueo de herramientas, las respuestas inválidas y el resultado mostrado en la interfaz. La consulta real también se comprobó por separado en el PC de NETGUARD. Véase [el resultado del 7 de noviembre](VERIFICACION-HERMES-2026-11-07.md).
