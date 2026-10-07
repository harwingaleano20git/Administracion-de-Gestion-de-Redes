# Finalización del corte 2 - NETGUARD v0.2.0

Propósito: completar los requisitos docentes con un laboratorio local reproducible, sin afirmar conexión real ni fabricar pruebas.

Arquitectura: conservar FastAPI, SQLAlchemy y SQLite; ampliar los modelos existentes con migración aditiva; reutilizar el inventario y las alertas. Nuevo servicio común para recepción/importación, plantillas y consola. Incidentes y auditoría se almacenan de forma persistente. No se ejecutan comandos de equipos reales.

- [ ] Copia consistente de datos y pruebas aisladas.
- [ ] Normalización de PRI, facility, fabricante y dispositivo; lista de fuentes, deduplicación y límite de frecuencia.
- [ ] Incidentes: evento vinculado, responsable, estados, seguimiento, causa, resolución y cierre.
- [ ] UI común: inventario, eventos con filtros completos, dashboard, alertas, incidentes.
- [ ] Plantillas comentadas Cisco/Fortinet/Huawei y consola de consulta simulada con auditoría.
- [ ] Política IA y pruebas de inyección indirecta, comandos bloqueados, duplicados y datos inválidos.
- [ ] README, instalación, respaldo, recuperación, evidencias, matriz y PDF de 17 secciones.
- [ ] Git local con commits reales progresivos y etiqueta v0.2.0; publicación remota cuando se resuelva cuenta/repositorio.

Corte 3: SSH real, Telegram y marcha blanca requieren equipos, cuentas y autorizaciones reales; no se declararán realizados como parte de la simulación del MVP.
