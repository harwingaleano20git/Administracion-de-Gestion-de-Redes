# NETGUARD NOC · v0.2.0

MVP académico individual de Harwin Galeano Beltran, UCompensar, Administración y Gestión de Redes, corte 2.

Inventario editable, recepción UDP local e importación Syslog, clasificación PRI (facility y niveles 0–7), filtros por fecha/marca/equipo/severidad/texto, dashboard, alertas, incidentes con asignación/seguimiento/cierre, plantillas Cisco/Fortinet/Huawei, consola de solo lectura simulada y auditoría exportable.

## Instalación y ejecución

Python 3.13. Desde esta carpeta, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8002
```

Abrir http://127.0.0.1:8002. La base SQLite se crea en `data/netguard.db`; revisar `app/database.py` para el nombre efectivo. Para usar otra base definir `NETGUARD_DB` con una ruta absoluta antes de iniciar. Los equipos iniciales y sus estados son ejemplos académicos: no prueban conectividad real.

En otra terminal, opcionalmente:

```powershell
.\.venv\Scripts\python.exe -m app.services.syslog_receiver
```

Receptor UDP **127.0.0.1:1514**. Si está ocupado, identificar primero el proceso; no iniciar dos receptores. Para el corte 2 también sirve la importación desde Eventos Syslog, por ejemplo fuente `10.10.0.1`, mensaje `<130>prueba critica`. Los equipos remotos no pueden enviar a este receptor local.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Utilizan una base aislada y un servidor temporal. No alteran la base de uso. Casos y evidencias en `docs/`.

## Seguridad y límites

Todos los datos son de laboratorio. No hay conexión SSH, ejecución de comandos reales, envío a Telegram ni autenticación/RBAC. El actor se declara en los formularios. La aprobación de configuración documenta una revisión humana declarada; jamás ejecuta una configuración. Los estados ONLINE/OFFLINE se registran manualmente. La consola usa coincidencia exacta con una lista de comandos; el contenido del log nunca es una instrucción. La auditoría SQLite es editable por quien controla el archivo: el hash no garantiza inmutabilidad.

Los mensajes requieren PRI 0–191 y fuente inventariada o localhost. Se limitan a 8 KiB, 100 aceptados/minuto/fuente y deduplicación de 10 segundos. Son controles básicos locales; UDP no autentica al emisor. No exponer este MVP en Internet. Las plantillas requieren validación de sintaxis y versión en el dispositivo autorizado antes de cualquier uso real.

## Entrega y continuidad

El informe personal se entrega aparte; no subir la cédula a un repositorio público. Evidencias E04–E11 provienen de la ejecución local. E01–E02 requieren cuenta/repositorio GitHub y publicación real. No se reconstruye un historial anterior ficticio. La etiqueta prevista es `v0.2.0`; su publicación se verifica en GitHub.

Corte 3 requiere desarrollo y validación adicionales: equipos autorizados, SSH/RBAC/aprobaciones reales, Telegram y gestión de secretos, carga, despliegue, reversa, recuperación y manuales. No están certificados por este MVP.
