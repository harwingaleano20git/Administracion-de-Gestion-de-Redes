# NETGUARD NOC · v0.2.1

MVP académico individual de Harwin Galeano Beltran, UCompensar, Administración y Gestión de Redes, corte 2.

Inventario editable, recepción UDP local e importación Syslog, clasificación PRI (facility y niveles 0–7), filtros por fecha/marca/equipo/severidad/texto, dashboard, alertas, incidentes con asignación/seguimiento/cierre, plantillas Cisco/Fortinet/Huawei, consola de consulta SSH con modo de práctica separado, detección de indicios y notificaciones Telegram.

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

Los equipos iniciales son ejemplos de laboratorio. La versión v0.2.1 implementa consultas SSH y envíos Telegram configurables; su validación con equipo externo y cuenta Telegram sigue pendiente. No hay autenticación web ni RBAC efectivo. El actor se declara en los formularios. La aprobación de configuración documenta una revisión humana declarada; jamás ejecuta una configuración. Los estados ONLINE/OFFLINE se registran manualmente. La consola usa coincidencia exacta con una lista de comandos; el contenido del log nunca es una instrucción. La auditoría SQLite es editable por quien controla el archivo: el hash no garantiza inmutabilidad.

Los mensajes requieren PRI 0–191 y fuente inventariada o localhost. Se limitan a 8 KiB, 100 aceptados/minuto/fuente y deduplicación de 10 segundos. Son controles básicos locales; UDP no autentica al emisor. No exponer este MVP en Internet. Las plantillas requieren validación de sintaxis y versión en el dispositivo autorizado antes de cualquier uso real.

## Entrega y continuidad

El informe personal se entrega aparte; no subir la cédula a un repositorio público. Evidencias E04–E11 provienen de la ejecución local. Repositorio: https://github.com/harwingaleano20git/Administracion-de-Gestion-de-Redes. Las capturas E01–E02 se agregan al informe personal. No se reconstruye un historial anterior ficticio. Release: https://github.com/harwingaleano20git/Administracion-de-Gestion-de-Redes/releases/tag/v0.2.0.

Pendientes: prueba externa SSH y Telegram, RBAC y aprobaciones efectivas, gestión de secretos, carga, despliegue, reversa y recuperación. La v0.2.1 no certifica estos requisitos.

## Ampliación solicitada: amenazas y Telegram
Se agregó detección por patrones, historial de avisos y configuración local de Telegram. Consulta docs/Telegram-y-amenazas.md. Esta ampliación local es posterior al release v0.2.0: el release publicado conserva la entrega original.


## Consola SSH y código para el profesor
Consulta docs/Codigo-para-el-profesor.md. La ampliación local incluye consultas SSH con lista permitida y verificación de huella. Requiere un equipo autorizado accesible y una prueba externa pendiente. El PDF, video y release v0.2.0 anteriores conservan el alcance original.

## Demostración actual
Guion: [docs/DEMOSTRACION-v0.2.1.md](docs/DEMOSTRACION-v0.2.1.md). Código por requisito: [docs/Codigo-para-el-profesor.md](docs/Codigo-para-el-profesor.md). La release v0.2.0 conserva el PDF y video originales; no acreditan las funciones de v0.2.1.
