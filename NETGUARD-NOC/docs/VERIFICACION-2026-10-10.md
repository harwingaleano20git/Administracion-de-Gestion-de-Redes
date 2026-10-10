# Evidencias de Telegram y SSH en Packet Tracer

Actualización: 10 de octubre de 2026. Harwin Galeano Beltran.

## Telegram real

La captura del teléfono muestra el bot NETGUARD NOC Harwin, un mensaje de prueba y la alerta de laboratorio del evento 3. Origen 10.10.0.1, severidad 2 e indicio ACCESO_FALLIDO. El usuario confirmó la recepción. Esto acredita el envío desde la aplicación y la recepción en el chat; no significa que el evento de laboratorio fuera una intrusión real.

## Práctica de red

Router Cisco 2911, nombre NETGUARD-R1, interfaz GigabitEthernet0/0: 192.168.10.1/24. PC0: 192.168.10.2/24 y gateway 192.168.10.1. El ping respondió cuatro veces, con cero pérdidas. Antes de corregirlo, la interfaz estaba activa pero sin IP; se configuró la dirección y se repitió la prueba.

SSH habilitado en versión 2.0, autenticación local y usuario operador. La captura de PC0 muestra ssh -l operador 192.168.10.1. El primer intento fue rechazado y el segundo permitió acceder al prompt NETGUARD-R1>. show version respondió Cisco IOS 15.1(4)M4 y modelo CISCO2911/K9.

## Archivo guardado

Nombre: Simulacion Conexion SSH en Packer Tracer.pkt
Ubicación: carpeta NETGUARD-NOC de la entrega local.
Tamaño verificado: 48750 bytes.
SHA-256: 20fd823522adc1f77002aeb7c6f65e86757b625f5e0fa3d1b35aaa3a2833e4cc

Se verificaron la existencia y el hash del archivo. El análisis de configuración se basa en las capturas aportadas; no se extrajo ni validó el contenido binario interno del .pkt. Debe abrirse en Packet Tracer para confirmar que el estado guardado coincide con las capturas.

## Alcance pendiente

La práctica demuestra SSH dentro de Packet Tracer, no una conexión desde Python en Windows. Falta consultar desde la consola NETGUARD un equipo físico o virtual autorizado y accesible. No hay autenticación web ni RBAC efectivo. La aplicación se mantiene en 127.0.0.1.

El PDF y video anteriores reflejan su fecha de creación. Este registro actualiza las evidencias posteriores sin atribuirles pruebas que no realizaron.
