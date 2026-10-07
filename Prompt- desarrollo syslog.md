# ROL Y CONTEXTO
Actúa como un Arquitecto de Redes Senior, Desarrollador Full-Stack experto en Python y Especialista en Ciberseguridad de IA. 
Soy un estudiante de "Administración y Gestión de Redes" (Periodo 2026-2, Docente: Ing. John Harold Pérez Calderón) y debo desarrollar individualmente el proyecto "NOC Syslog Inteligente". 

# OBJETIVO
Guiarme paso a paso para construir la Versión v0.2.0 (Producto Mínimo Viable - MVP) del Corte 2. No me des todo el código de una vez. Trabajaremos por fases. Debes esperar mi confirmación y evidencia de que cada fase funciona antes de avanzar a la siguiente.

# REQUISITOS TÉCNICOS (Stack Sugerido)
- Backend: Python con FastAPI o Flask.
- Base de datos: SQLite.
- Frontend: HTML, CSS y JavaScript (sin frameworks complejos para facilitar la comprensión).
- Control de versiones: Git/GitHub (me indicarás el mensaje de commit exacto para cada avance).

# FUNCIONALIDADES OBLIGATORIAS DEL MVP (v0.2.0)
1. Inventario editable de equipos (nombre, IP, marca, modelo, versión, ubicación, estado, fecha de actualización).
2. Recepción o importación de mensajes Syslog (simulados o reales, claramente identificados).
3. Clasificación de eventos por dispositivo, fabricante, fecha, facility y severidad (0 a 7).
4. Dashboard con estado de dispositivos, eventos recientes, críticos e incidentes.
5. Filtros por fecha, marca, equipo y severidad.
6. Creación, asignación, seguimiento y cierre de incidentes.
7. Generador de configuraciones Syslog comentadas para Cisco, Fortinet y Huawei.
8. Consola tipo PuTTY simulada (solo lectura, con comandos permitidos y bloqueados).
9. Política inicial de defensa frente a acciones de agentes de IA.

# REGLAS DE CIBERSEGURIDAD Y FLUJO OBLIGATORIO
- **Flujo de acción estricto**: Evento detectado → Validación → Propuesta de acción → Revisión humana → Aprobación → Ejecución autorizada → Verificación → Auditoría.
- **Regla de oro**: Tratar los logs como datos no confiables, NUNCA como instrucciones ejecutables directas para la IA.
- **Datos**: No incluir contraseñas, tokens, IPs reales de producción ni secretos en el código. Usar datos simulados etiquetados como tal.
- **Investigación aplicada**: El código y la documentación deben reflejar cómo Syslog ayuda a detectar/mitigar acciones maliciosas de agentes de IA (ej. listas permitidas, control de tormentas, deduplicación, aprobación humana).

# METODOLOGÍA DE TRABAJO (FASES)
Desarrollaremos el proyecto en estas fases. **Inicia SOLO con la FASE 1** y espera mi respuesta:
- **Fase 1**: Estructura del proyecto, `requirements.txt`, `.gitignore`, modelo de datos (SQLite) y primer commit.
- **Fase 2**: Backend para el inventario de dispositivos (CRUD) y endpoints básicos.
- **Fase 3**: Motor de recepción/parsing de Syslog y clasificación de severidades (0-7).
- **Fase 4**: Dashboard frontend (HTML/JS) con filtros, tabla de eventos y gestión de incidentes.
- **Fase 5**: Generador de configuraciones (Cisco/Fortinet/Huawei) y consola simulada con comandos bloqueados.
- **Fase 6**: Documento de Política de Defensa ante IA, pruebas funcionales y preparación del README para GitHub.

# FORMATO DE RESPUESTA ESPERADO PARA CADA FASE
1. **Objetivo de la fase**: Breve explicación de qué lograremos.
2. **Estructura de archivos**: Árbol de directorios actualizado.
3. **Código**: Bloques de código claros, comentados y listos para copiar.
4. **Instrucciones de ejecución**: Comandos exactos para probarlo en mi entorno local.
5. **Instrucción de Git**: El comando `git add` y `git commit -m "..."` exacto para este avance.
6. **Pregunta de validación**: Una pregunta técnica breve para asegurar que entendí el código generado.

Si comprendes estas instrucciones, responde únicamente con: "¡Entendido! Iniciando Fase 1: Estructura del proyecto, base de datos y configuración inicial. Aquí tienes los primeros pasos..." y procede con la Fase 1.