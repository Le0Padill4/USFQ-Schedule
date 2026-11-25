# Instrucciones para agentes

- Lee `docs/ESTADO_PROYECTO.md`, `docs/PLAN_MAESTRO.md` y la especificación antes de cambiar código.
- La fuente del producto es USFQ-Schedule. No crear ni usar un proyecto llamado CurriculumEngine.
- No usar datos personales reales ni scraping hasta documentar fuente, permiso y límites. Fixtures siempre sintéticos.
- Conserva las interfaces de `docs/CONTRATOS_INTEGRACION.md`; propón cambios allí primero y coordínalos en PR.
- Trabaja en ramas pequeñas; no hagas push directo a `main`. Toda contribución requiere PR y revisión de otro integrante.
- Añade primero criterios/escenarios BDD y pruebas para cambios funcionales; registra comandos y resultados reales.
- No afirmes que pruebas, benchmarks, scraping, despliegues, errores de IA o aportes ocurrieron si no hay evidencia.
- MCP usa herramientas explícitas, validación de entrada y acceso de solo lectura. No exponer SQL arbitrario ni secretos.
- No añadas dependencias sin justificar su mantenimiento, licencia y costo.
