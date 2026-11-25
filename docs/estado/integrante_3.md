# Estado individual — Integrante 3

Registro individual para evitar conflictos de edición en `docs/ESTADO_PROYECTO.md`. Enlazar desde ese archivo cuando el PR #5 (CI documental) esté integrado, para no colisionar con su cambio.

## 2026-11-24
- Revisado: repo `Le0Padill4/USFQ-Schedule` (`main` en `bc13726`), documentos del repo y `CMP3002-Proyecto.md`.
- Hecho: propuesta T0 (contrato de scheduling v0.2 en `docs/CONTRATOS_INTEGRACION.md`, `docs/motor_operaciones.md`, este archivo). **Solo documentación; no se ejecutó código ni pruebas.**
- Pendiente de revisión: I1 (carreras/mallas, prerrequisitos alternativos, correquisitos) e I2 (codificación de reuniones, índice por NRC, función de solape).

## Bloqueos y límites conocidos
- No se pudo consultar la lista de Issues y PRs (la web bloquea `robots`; sin acceso de API). Revisar manualmente PRs #1–#5.
- Aceptación docente del trío pendiente (la rúbrica habla de grupos de dos).
- No hay `pyproject.toml`, pytest ni Ruff en `main`. No se crean hasta confirmar que nadie más los está trabajando (configuración compartida única).
- Datos reales de mallas y oferta: provienen del módulo de I2; I3 usa solo fixtures sintéticos.
