# División del trabajo

## Responsables

- **Integrante 1:** Combat-Engine personajes/hash y pruebas; USFQ-Schedule grafo curricular y frontend de PAA.
- **Integrante 2:** Combat-Engine combate/turnos; USFQ-Schedule AVL, backend/API/BD, autenticación y MCP. Es el segundo integrante de PAA.
- **Integrante 3:** Combat-Engine historial/rankings; USFQ-Schedule generación, optimización, benchmarks y pruebas diferenciales. No se cuenta como integrante de la pareja PAA.

## Límites de propiedad

Integrante 1 posee `domain/curriculum_graph` y `web` vistas/malla. Integrante 2 posee `domain/course_index`, `api`, `adapters/postgres` y `mcp`. Integrante 3 posee `domain/scheduling`, `benchmarks` y referencia lenta. Modelos compartidos solo cambian con PR de contrato.

Cada persona configura su nombre y correo Git individualmente. Ningún integrante aprueba su propio PR. El revisor valida alcance, tests y comandos; la autoría y las contribuciones deben reflejar trabajo real.
