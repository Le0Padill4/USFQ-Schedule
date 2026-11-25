# Arquitectura — USFQ-Schedule

## Capas

- `domain`: modelos, grafo, AVL, reglas y generación sin dependencias de web/BD.
- `application`: casos de uso, validación y composición de servicios.
- `adapters`: repositorios PostgreSQL, fuente de oferta y servidor MCP.
- `api`: FastAPI REST y autenticación.
- `web`: Next.js/TypeScript, estado de pantalla y calendario.

El motor Python es la fuente de reglas de prerrequisitos y generación. La API recibe/devuelve JSON; Next.js presenta resultados. PostgreSQL en Docker Compose permite correr el flujo sin pago ni conexión a Supabase. MCP se ejecuta localmente con consultas de lectura limitada.

## Tecnología y costo

FastAPI/Python comparte el lenguaje del motor; PostgreSQL almacena oferta y progreso; Next.js/TypeScript cubre web. Docker asegura versiones entre Windows y macOS. Vercel Hobby y Supabase Free son opciones para demo con límites, no dependencias del entorno reproducible.

## Seguridad

No usar calificaciones ni identidades reales. Datos sintéticos. Contraseñas con hash robusto, consultas parametrizadas, autorización por usuario, secretos fuera del repositorio y rol de solo lectura para MCP.

> Se usa el nombre en minúsculas exigido por la guía oficial de Programación Asistida para evitar un conflicto de mayúsculas/minúsculas en Windows y macOS.
