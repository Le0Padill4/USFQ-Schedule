# Contrato local de I1 — pendiente de revisión, 25 nov 2026

No sustituye `docs/CONTRATOS_INTEGRACION.md` ni aprueba la propuesta de I3.
El desarrollo local implementa únicamente `CourseGraph`, mencionado en el contrato
vigente, con códigos exactos y aristas AND `prerrequisito -> materia`.
No crea modelos Course/Offering ni interpreta fuentes reales.

## Interfaz propuesta para revisión

- `add_course(code, prerequisites_known=False)`, `remove_course(code)`.
- `add_prerequisite(prerequisite_code, course_code) -> bool`: duplicado idempotente.
- `remove_prerequisite(prerequisite_code, course_code) -> bool`.
- `set_rules_known(code, known)`; el importador debe confirmar explícitamente
  que la regla está completa. No se infiere que ausencia de aristas significa
  ausencia de requisitos.
- `eligible_courses(passed_codes) -> tuple[str, ...]`: códigos ordenados,
  aprobadas excluidas, todos los requisitos directos aprobados y reglas conocidas.
- `bfs(start)`, `dfs(start)`: recorren dependientes, incluyen el inicio.
- `dependencies(code, transitive=True)`, `dependents(code, transitive=True)`:
  códigos ordenados, excluyen el inicio.
- `topological_order()`, `check_invariants()`, `snapshot()`; vistas inmutables.

`GraphError.code`: `INVALID_CODE`, `INVALID_FLAG`, `UNKNOWN_COURSE`,
`DUPLICATE_COURSE`, `CYCLE`. Ningún error de entrada modifica el estado.
Códigos no vacíos, exactos, sin espacios exteriores; no se normalizan prefijos.
Eliminar una materia invalida la completitud de sus dependientes directos;
eliminar una arista invalida la completitud de su destino. Es necesario confirmar
de nuevo las reglas antes de habilitarlo. Esta política conservadora es propuesta.

## Integración pendiente

I1 entrega códigos habilitados; la capa de aplicación combina créditos y ofertas
de I2 para la entrada `eligible` de I3. No hay dependencia de BD, API ni scheduling.
I3 debe revisar nombres, tipos y errores antes de usar esta interfaz.

AND/OR, correquisitos, nota mínima, equivalencias, pertenencia múltiple y versiones
requieren contrato común. No se aplanan alternativas en aristas AND ni se omiten
condiciones desconocidas: la materia se conserva con `prerequisites_known=False`.
El grafo no pretende validar un expediente real ni resolver correquisitos.

La propuesta I3 de `CurriculumEntry` evita deducir pertenencia por prefijos y merece
revisión conjunta con I2. La detección de ciclos sobre una unión de alternativas
no basta para definir la semántica de reglas OR; no se implementa esa ampliación
sin acuerdo. Las dos carreras admitidas por el frontend son 1CMP y 1MAC.

## Casos y alcance de evidencia

BDD previo: `spec/features/i1_curriculum_graph.feature`.
Pruebas: `tests/test_i1_curriculum_graph.py`; oráculo independiente de listas en
`tests/i1_graph_reference.py`. El diferencial de este módulo no reemplaza las
10.000 operaciones del motor completo, a cargo del arnés de I3.
