# Motor de USFQ-Schedule — operaciones, escenarios y casos borde

Estado: **borrador de Integrante 3 para completar y aprobar entre los tres integrantes** (requisito del paso 1–3 de `CMP3002-Proyecto.md`). Nada aquí es evidencia de ejecución. Las secciones de I1 e I2 son marcadores que ellos completan. Las hipótesis de «quién gana» son **hipótesis a verificar con mediciones reales**; si una no se cumple, se reemplaza la comparación.

## 1. La app

USFQ-Schedule es un planificador académico para estudiantes de `1CMP` y `1MAC`: dada la malla, las materias aprobadas y la oferta de paralelos, calcula qué materias están habilitadas y genera horarios sin cruces, ordenados por preferencias. Usa datos sintéticos; no hay datos personales reales.

## 2. Operaciones

### 2.1 Operaciones de I3 (scheduling)

| Operación | Entradas | Devuelve | Cambia datos | Candidatos propuestos |
|---|---|---|---|---|
| `generate` | solicitud + materias elegibles | horarios factibles (todos) | no | A: enumeración exhaustiva + filtro. B: backtracking con poda (opcional C: CSP con MRV/forward checking) |
| `top_k` | horarios puntuados, k | los k mejores, orden `(-score, nrcs)` | no | A: heap acotado de tamaño k (propio). B: ordenamiento completo + corte |
| `has_conflict` | dos ofertas / un conjunto de NRC | bool o lista de pares en conflicto | no | A: comparación por pares de reuniones. B: bitmask por día y franja. **A coordinar con I2** |
| `score` | horario, preferencias | `ScheduleResult` con explicaciones | no | A: recálculo completo. B: incremental con cota superior (para poda). Se incluye solo si pasa el filtro de «respuesta no obvia» |
| `validate` | lista de NRC, solicitud | lista de violaciones | no | **Pendiente de coordinar con I2** (índice por NRC): A: búsqueda lineal. B: índice hash. Probable que sea respuesta obvia; **no cuenta** si no hay escenario donde A gane |

Operaciones simples (implementadas, no analizadas): contar ofertas, existe NRC, listar materias elegibles.

### 2.2 Operaciones de I1 (grafo curricular) — a completar por I1
Marcador: habilitadas dado el conjunto de aprobadas; orden topológico; recorrido BFS/DFS; validación de DAG. Candidatos y casos borde: ver plan de I1.

### 2.3 Operaciones de I2 (índice AVL, importación) — a completar por I2
Marcador: buscar por código, rango por código, insertar, borrar. Candidatos y casos borde: ver plan de I2.

> La rúbrica pide **6 a 8 operaciones que cuentan en todo el motor**, cada una con dos candidatos y un escenario donde cada candidato gana. Total pendiente de acordar entre los tres.

## 3. Casos borde de las operaciones de I3

| Situación | Comportamiento definido | Prueba |
|---|---|---|
| Motor vacío (sin ofertas) | `generate` → lista vacía, sin error | pendiente |
| Materia requerida sin ninguna oferta | lista vacía | pendiente |
| Código de materia inexistente | `UNKNOWN_COURSE` | pendiente |
| NRC fijado inexistente | `UNKNOWN_NRC` | pendiente |
| NRC repetido en la oferta | `DUPLICATE_NRC` | pendiente |
| `max_results`/`k` < 1 | `INVALID_RANGE` | pendiente |
| `k` > número de horarios | devuelve todos | pendiente |
| Minutos o día fuera de rango | `INVALID_RANGE` | pendiente |
| Clases consecutivas (`end == start`) | no hay cruce | pendiente |
| Paralelo con varias reuniones | cruce si alguna reunión se solapa | pendiente |
| Materia no habilitada | `NOT_ELIGIBLE` | pendiente |
| Carrera distinta de `1CMP`/`1MAC` | `CAREER_NOT_SUPPORTED` | pendiente |

La columna «Prueba» se llena cuando exista la prueba ejecutada.

## 4. Escenarios (propuesta de motor completo, a aprobar entre los tres)

| Escenario | Mezcla de operaciones | Tamaño de datos | Forma de los datos |
|---|---|---|---|
| S1 — Semana de inscripción normal | 60% consultas, 30% `generate`+`top_k`, 10% cambios de oferta | 10³ a 10⁴ ofertas | al azar, pocos cruces |
| S2 — Hora pico de preferencias | 70% `generate`+`top_k` con preferencias variadas, 30% consultas | 10³ a 10⁴ ofertas | muchos paralelos solapados |
| S3 — Carga y limpieza de oferta | 70% inserciones/borrados de oferta, 30% consultas | 10⁴ a 10⁶ registros | ya ordenados / ids consecutivos |

Para la medición de `generate` el tamaño es el **número de combinaciones posibles** (producto de paralelos por materia), con cuatro valores entre 10³ y 10⁶ cuando la enumeración exhaustiva lo permita; si no llega, se documenta el límite en vez de omitirlo.

## 5. Hipótesis de dónde gana cada candidato (a verificar, no resultados)

- `generate`: la enumeración gana (menor sobrecarga) cuando casi no hay cruces; el backtracking gana cuando hay muchos cruces y la poda corta ramas. Si no existe un escenario real donde gane la enumeración, se reemplaza la comparación.
- `top_k`: el heap gana en **espacio extra** (O(k) frente a O(n)) y con flujo de actualizaciones y consultas repetidas con k pequeño; el ordenamiento completo puede ganar en tiempo de reloj para k cercano a n o por usar el `sorted` de Python en C. Se medirán **tiempo y conteo de comparaciones**. Si el heap no gana en ningún escenario, se propone una alternativa antes de consolidar.

## 6. Infraestructura de pruebas (propuesta)

- Versión lenta con listas simples y operaciones sobre el mismo estado observable.
- Cada integrante aporta la versión lenta de **sus** operaciones; I3 provee el arnés (semilla, generador de operaciones aleatorias, comparación de respuestas y estados).
- Mínimo 10.000 operaciones aleatorias sobre el motor completo, incluidos ids inexistentes, repetidos y valores fuera de rango.
- Medición: mismo computador, varias repeticiones, CSV y gráficos reproducibles (`matplotlib` solo como dependencia de desarrollo).
