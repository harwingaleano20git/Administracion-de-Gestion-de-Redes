# Consulta de alertas con Hermes Agent

Agregar un botón **Consultar con Hermes** en Amenazas y Telegram. El operador elige una alerta concreta; NETGUARD solicita un resumen, una prioridad orientativa y próximos pasos de diagnóstico. La respuesta se muestra como recomendación para revisión humana.

## Alcance

- NETGUARD conserva el registro, la clasificación y el envío actual por Telegram. Hermes solo interviene cuando el operador pulsa el botón.
- La petición incluye el ID, la severidad y los códigos de indicios conocidos. No incluye la IP, el Syslog original, datos personales, credenciales ni el contenido de la base.
- El servidor de NETGUARD llama al endpoint `/v1/chat/completions` de una instancia local de Hermes Agent. La clave se configura fuera del repositorio y nunca se devuelve al navegador. El panel indica si la integración está desactivada.
- Usar un perfil de Hermes separado, sin herramientas de ejecución, archivos, SSH ni mensajería. Verificar la configuración del perfil antes de habilitar consultas. No ejecutar instrucciones de la respuesta ni aplicar cambios a alertas o equipos.
- Si Hermes no está disponible, mostrar un error de consulta. El registro y la notificación originales siguen disponibles.

## Prueba de aceptación

Consultar una alerta de laboratorio `ACCESO_FALLIDO` y ver una explicación en español, con pasos que el operador pueda decidir si aplica. Verificar que la solicitud solo contiene los campos permitidos, que no sale ninguna petición con la integración desactivada y que un fallo de Hermes no cambia la alerta. Separar las pruebas simuladas de la prueba con la instancia real.

Referencia: [API oficial de Hermes Agent](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server).
