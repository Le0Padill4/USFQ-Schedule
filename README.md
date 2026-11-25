# USFQ-Schedule

Planificador académico para explorar una malla de la USFQ, registrar materias aprobadas y construir horarios sin prerrequisitos incumplidos ni cruces.

**Estado:** repositorio inicial. La especificación y los contratos están en preparación; el producto aún no está implementado. No hay resultados de pruebas ni benchmarks publicados.

## Equipo y alcance

La pareja de Programación Asistida de Aplicaciones es Integrantes 1 y 2. El usuario autoriza que el equipo trabaje como trío; la rúbrica entregada indica parejas, así que la aceptación académica del trío queda pendiente de confirmación docente. El Integrante 3 participa en el motor académico, no en la nota de la aplicación por pareja.

## Decisiones

- Python/FastAPI para el motor y API.
- PostgreSQL local en Docker Compose para desarrollo reproducible.
- Next.js/TypeScript para interfaz.
- FastMCP local, lectura únicamente.
- GitHub Actions para validaciones. Vercel y Supabase son opciones de despliegue, no dependencias del entorno de prueba gratuito.

Consulta `docs/ESTADO_PROYECTO.md` para comandos que estén realmente disponibles y `docs/PLAN_MAESTRO.md` para los siguientes hitos.
