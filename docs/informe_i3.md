# Informe — parte del Integrante 3: generación, validación y ranking de horarios

> Esta parte describe el motor de horarios (`domain/scheduling/`) y sigue los pasos 1 a 7 de la
> rúbrica. Las secciones sobre el grafo curricular (I1) y los índices (I2) resumen lo que este
> módulo consume; los análisis completos de esas estructuras están en los informes de sus autores.
> Todo el catálogo usado en pruebas y mediciones es **sintético**: no hay datos reales de la USFQ
> en este módulo.

## 1. La app y las operaciones de esta parte

**La app.** USFQ-Schedule ayuda a un estudiante de las carreras `1CMP` y `1MAC` a armar su horario
de un periodo: dado el conjunto de materias que puede tomar, elige un paralelo (NRC) por materia
requerida, decide qué materias opcionales agrega y propone los mejores horarios sin cruces según
las restricciones y preferencias que indica. No se construye interfaz; solo el motor.

**Operaciones de I3** (entradas → salida; todas son funciones puras: no modifican datos).

| Operación | Entradas | Devuelve |
|---|---|---|
| `build_problem` (validar) | `ScheduleRequest`, lista de `EligibleCourse` | un `Problem` normalizado o `ScheduleError` con código |
| `generate_schedules` | solicitud, elegibles, generador, selector | los `max_results` mejores horarios, del mejor al peor |
| `best_schedules` (**mejores K**) | solicitud, elegibles, método | igual resultado, por otro camino (ver §2) |
| `score_schedule` | tupla de NRC, `Problem` | `ScheduleResult` con puntaje entero y desglose por término |
| Top-K (`top_k_heap`, `top_k_sort`) | lista de resultados, k | los k mejores ordenados |
| cruce de dos ofertas (`offerings_conflict`) | dos `Offering` | booleano |

Un horario es una tupla de NRC ordenada; el orden de resultados es `(-puntaje, tupla de NRC)`, es
decir, mayor puntaje primero y, en empate, lexicográfico por NRC. El puntaje es entero
(`puntos = valor_crudo × peso`) con seis términos: día libre, días usados, minutos de huecos,
minutos en franjas preferidas, minutos en franjas evitadas y prioridad de opcionales.

**Casos borde (decisión → comportamiento).** Todos están probados en `tests/test_i3_generation.py`
y `tests/test_i3_differential.py`.

| Caso | Decisión |
|---|---|
| Carrera distinta de `1CMP`/`1MAC` | `CAREER_NOT_SUPPORTED` |
| `max_results` ≤ 0 o no entero | `INVALID_RANGE` |
| Materia pedida que no está entre las elegibles | `NOT_ELIGIBLE` |
| Materia requerida repetida, o a la vez requerida y opcional | `INVALID_RANGE` |
| NRC fijado que no pertenece a la materia | `UNKNOWN_NRC` |
| NRC repetido en el catálogo elegible | `DUPLICATE_NRC` |
| Día fuera de 0..6, `min_credits > max_credits`, prioridad < 1 | `INVALID_RANGE` |
| Solicitud sin materias | lista vacía (el horario vacío no se devuelve) |
| Ningún horario sin cruces | lista vacía, sin error |
| `max_results` mayor que los horarios posibles | se devuelven todos |
| Empate de puntaje | desempata la tupla de NRC; resultado determinista |
| Reuniones que se tocan en el borde (fin = inicio) | no hay cruce; los intervalos son `[inicio, fin)` |

El orden de validación está fijo (carrera, `max_results`, catálogo, restricciones, listas de
materias, elegibilidad, NRC fijados), de modo que dos implementaciones dan el mismo código ante
una solicitud con varios defectos.

## 2. Las operaciones que cuentan y sus candidatos

De este módulo cuentan **dos** operaciones; el equipo debe completar entre 6 y 8 con las de I1 e I2
(ver la lista de pendientes al final de esta sección).

| Operación | Candidato 1 | Candidato 2 | Cuándo gana cada uno |
|---|---|---|---|
| **Mejores K horarios** | A: generar todos (CSP) + puntuar + heap Top-K | B: branch and bound con cota optimista | B gana con preferencias fuertes y k pequeño: la cota descarta ramas completas. A gana sin preferencias o con la cota de huecos, que es débil: B paga el cálculo de cotas sin podar. |
| **Top-K de resultados ya puntuados** | heap acotado propio | ordenamiento completo + corte | El heap gana con k pequeño y en flujos de consultas repetidas (O(N log k), memoria O(k)). El ordenamiento gana con k grande (k = N/10) y con datos ya ordenados, porque `sorted` de C detecta corridas. |

**Operación descartada por respuesta obvia: «generar todos los horarios».** Se compararon tres
candidatos: producto cartesiano + filtro, backtracking con poda y CSP con forward checking y
heurística MRV. En las mediciones (§4) la exhaustiva no ganó en ningún escenario ni tamaño, y el
backtracking tampoco ganó de forma sostenida frente al CSP; por la regla de la rúbrica esa operación
no cuenta, así que se reemplazó por «mejores K», que es además lo que la app necesita. La generación
se sigue implementando: es el primer paso del candidato A de «mejores K». El análisis y los
resultados se conservan como evidencia de la decisión.

*Equivalencia de candidatos.* Todos resuelven el mismo problema con las mismas restricciones y el
mismo desempate, y devuelven resultados idénticos; el arnés de benchmarks aborta si dos candidatos
difieren.

**Pendiente con I1/I2 (no decidido por I3).** Para llegar a 6–8 operaciones que cuentan, el equipo
debe confirmar cuáles aportan I1 (por ejemplo elegibilidad/orden topológico) e I2 (búsqueda por
NRC con hash frente a AVL, rango de materias, índice de cruces). I3 no declara candidatos ni
resultados de esas operaciones.

## 3. Los escenarios

Cada escenario fija mezcla de operaciones, volumen y forma de los datos. Las mezclas son hipótesis
del diseño, no mediciones.

| Escenario | Mezcla | Datos | Qué decide |
|---|---|---|---|
| **S1. Planificación normal** | 70 % mejores K (k = 10, preferencias moderadas), 20 % elegibles/consultas de materias, 10 % altas/bajas de ofertas | 10³–10⁴ combinaciones por consulta; pocos cruces | B&B y «todos + Top-K» son parecidos; importa poco |
| **S2. Semana de inscripción** | 85 % mejores K con k = 10 y preferencias fuertes, 15 % cambios de ofertas | 10⁵–10⁶ combinaciones; muchos cruces | B&B (18×–194× más rápido en las mediciones); heap para el flujo de consultas |
| **S3. Exploración amplia** | 60 % pedidos con k grande (miles) o sin preferencias, 40 % consultas simples | 10⁵–10⁶ combinaciones | «Todos + Top-K» (sin poda posible), ordenamiento para k grande |

Los escenarios de medición se derivan de estos: `preferencias_fuertes_k10` (S2),
`sin_preferencias_k10` y `solo_huecos_k10` (S1/S3), `preferencias_fuertes_k_grande` (S3);
para Top-K, `k10_aleatorio`, `k_decimo_aleatorio`, `k_decimo_ascendente` y `flujo_10_consultas`.
Un escenario corto adicional, `cruces_extremos`, muestra dónde ganan las podas en la generación.

## 4. La comparación

### 4.1 Análisis teórico

Sea `C` el número de materias solicitadas, `o_i` los paralelos de la materia `i`, `P = Π o_i` el
espacio de búsqueda, `R` el número de horarios factibles y `N` el número de resultados puntuados.

| Operación y candidato | Tiempo | Espacio extra |
|---|---|---|
| Generar, exhaustiva | Θ(P · C²) en todos los casos (visita todo y filtra por pares) | O(R · C) por la salida |
| Generar, backtracking | O(P · C) peor caso; poda por cruces y por límites de créditos | O(C) pila + O(R · C) salida |
| Generar, CSP (forward checking + MRV) | O(P · C · o) peor caso; poda antes que backtracking, ejecuta menos comprobaciones por nodo | O(C · o) dominios + O(R · C) salida |
| Puntuar un horario | O(m log m), m = reuniones del horario (≤ ~30) | O(m) |
| Top-K con heap | O(N log k) peor caso (datos ascendentes); ≈ O(N) esperado con orden aleatorio, porque pocos elementos entran | **O(k)** |
| Top-K con ordenamiento | O(N log N) (O(N) si ya está ordenado) | O(N) |
| Mejores K, A (todos + heap) | tiempo de generar + R · puntuar + O(R log k) | O(R · C) |
| Mejores K, B (B&B) | O(P · C) peor caso (sin poda); con cota efectiva visita una fracción de P | O(C + k) |

*Cota del branch and bound.* Para cada término del puntaje se calcula el mejor valor posible de
cualquier completación del nodo (para pesos positivos y negativos); la suma es una cota optimista
del puntaje de cualquier horario que se pueda completar desde ese nodo. Se poda una rama solo si
su cota es **estrictamente menor** que el puntaje del peor resultado conservado por el heap lleno:
con igualdad no se poda, porque el desempate por NRC aún podría admitirla.

### 4.2 Mediciones (dos operaciones medidas con los dos candidatos)

Datos completos en `benchmarks/results/` y análisis en `docs/benchmarks_i3.md`. Corrida del
2026-11-27 en una sola máquina (CPython 3.13.9, Windows 11, 8 CPU lógicas), 4 tamaños (10³ a 10⁶),
3 repeticiones, medianas con rango min–max, contadores de pasos y, para Top-K, pico de memoria.

**Top-K** (razón tiempo ordenamiento / heap; > 1 gana el heap):

| Escenario | 10³ | 10⁴ | 10⁵ | 10⁶ |
|---|---|---|---|---|
| k = 10, aleatorio | 0,78 (solapado) | 1,54 | 2,81 | 5,36 |
| k = N/10, aleatorio | 1,18 (solapado) | 0,32 | 0,29 | 0,29 |
| k = N/10, ascendente | 0,06 | 0,05 | 0,03 | 0,02 |
| 10 consultas sobre flujo | 2,62 | 9,32 | 13,38 | 15,19 |

- *Confirma* el análisis: con k = 10 el heap hace ≈ N comparaciones (1,0 M a 10⁶ contra 18,6 M) y
  usa 1–3 KiB frente a más de 100 MiB; con datos ascendentes el heap hace 29 M comparaciones frente
  a 1 M del ordenamiento, que detecta la corrida ordenada.
- *Contradice en parte* el conteo de pasos: con k = N/10 aleatorio el heap hace menos comparaciones
  (8,1 M contra 18,6 M) pero tarda 3,5 veces más, porque es código Python y `sorted` es C. El
  número de comparaciones no predice el tiempo entre implementaciones de lenguajes distintos.
- No se midió el cruce de k entre 10 y N/10; no hay evidencia de dónde ocurre.

**Mejores K** (razón tiempo «todos + Top-K» / B&B; > 1 gana B&B):

| Escenario | 10³ | 10⁴ | 10⁵ | 10⁶ |
|---|---|---|---|---|
| preferencias fuertes, k = 10 | 17,9 | 51,8 | 118,8 | 193,8 |
| sin preferencias, k = 10 | 0,74 | 0,63 | 0,73 | 0,82 |
| preferencias fuertes, k = 100 000 | 0,89 | 0,85 | 0,82 | 1,31 |
| solo huecos, k = 10 | 0,91 (solapado) | 0,91 | 0,83 (solapado) | 0,75 |

- *Confirma*: B&B visita 2 106 nodos contra 469 521 a 10⁶ con preferencias fuertes (146 ms contra
  28,2 s). Sin preferencias o con solo huecos no poda y es entre 10 % y 60 % más lento.
- Con k = 100 000 no hay umbral mientras haya menos de k factibles (55 020 a 10⁵), así que no
  poda; a 10⁶ hay 414 575 factibles, poda 43 669 ramas y gana 1,31×.
- *Amenaza a la validez:* B&B se apoya en el backtracking y no en el forward checking del CSP:
  sin podas hace unas 5 veces más comprobaciones de cruce, lo que explica parte de su desventaja.
  El factor 194× corresponde a un escenario elegido para que la cota funcione.

**Generación** (medida como evidencia de la decisión del §2): exhaustiva / CSP entre 1,8× y 1 044×;
backtracking / CSP entre 1,5× y 4,1× a favor del CSP salvo un punto dentro del ruido.

## 5. El motor completo

**Qué estructuras usa y qué guarda cada una**

| Familia | Estructura | Dueño | Qué guarda | Persistente |
|---|---|---|---|---|
| Grafos | `CourseGraph` (listas de adyacencia) | I1 | prerrequisitos AND y reglas conocidas | sí |
| Árboles | AVL de materias (`CourseIndex`) / NRC | I2 | registro de materia u oferta por código | sí |
| Árboles | `BoundedHeap` (min-heap respecto a «peor») | **I3** | los k mejores resultados de una consulta | no (por consulta) |
| Hashing | `dict` `offerings_by_nrc` y de materias | I3 | NRC → oferta, materia → prioridad | no (por consulta) |
| Secuencias | tuplas y listas de slots y resultados | I3 | orden de materias, horarios | no |

**Costo de mantener las estructuras.** El módulo de I3 es sin estado: no guarda nada entre
consultas, así que no añade costo de mantenimiento al insertar o borrar materias. El costo aparece
en las estructuras compartidas, y cada cambio de catálogo toca las dos:

| Cambio | Grafo (I1) | Índice AVL (I2) | I3 |
|---|---|---|---|
| Agregar una materia | O(1) | O(log n) | ninguno |
| Quitar una materia | O(grado) y reglas de sus dependientes quedan desconocidas | O(log n) | ninguno |
| Agregar/quitar prerrequisito | O(V + E) (se verifica ciclos) | no aplica | ninguno |
| Consulta de horarios | elegibles O(V + E + V log V) | O(log n) por elegible | `build_problem` O(total de ofertas) + candidato elegido |

La contrapartida del diseño sin estado es que cada consulta reconstruye el `Problem`
(O(total de ofertas)); es barato frente a la generación, pero no se midió. Los costos de I1 e I2
están leídos del código y deben ser confirmados por sus autores. Existe además un riesgo de
**desincronización** entre grafo e índice (una materia elegible sin registro en el índice): el
adaptador propaga `KeyError` y la prueba del motor completo ejercita ese caso (846 veces).

**Qué cambiaría en otro escenario.** Con consultas repetidas sobre el mismo conjunto de elegibles
(S2 con muchos estudiantes iguales), conviene guardar el `Problem` y la cota entre consultas
(costo: invalidar al cambiar una oferta). Si los estudiantes casi nunca fijan preferencias,
conviene usar siempre «todos + Top-K» y no pagar cotas.

## 6. La implementación

| Módulo | Contenido |
|---|---|
| `domain/scheduling/models.py`, `errors.py` | `Meeting`, `Offering`, `EligibleCourse` validados; errores tipados |
| `request.py` | `ScheduleRequest`, `Constraints`, `Preferences`, `build_problem` |
| `generation.py` | los tres generadores y `Stats` (pasos) |
| `scoring.py` | `score_schedule`, `rank_key` |
| `topk.py` | `BoundedHeap` **propio**, `top_k_heap`, `top_k_sort` |
| `optimize.py` | candidatos A y B de «mejores K», cota optimista |
| `engine.py` | `generate_schedules`, `best_schedules` |
| `reference.py` | **versión lenta** independiente (listas y conjuntos de minutos) |

**Estructura propia y su propiedad.** `BoundedHeap` es un min-heap respecto a «peor»: cada padre es
peor o igual que sus hijos, la raíz es el peor de los k mejores conservados y `len ≤ k`;
`check_invariants()` lo comprueba y las pruebas lo llaman tras cada inserción. Otras propiedades
verificadas: toda solución es una tupla de NRC ordenada y sin cruces; los resultados salen
ordenados por `rank_key`; y la cota de cada nodo de B&B es ≥ al mejor puntaje de sus completaciones
(auditado en cada nodo en `tests/test_i3_bnb.py`).

La rúbrica exige al menos dos estructuras propias de Hashing, Árboles o Grafos en el equipo: el AVL
(I2), el grafo (I1) y el heap (I3) las cubren; **el equipo debe confirmarlo explícitamente** en su
informe conjunto.

## 7. Pruebas

Comando: `python -m unittest discover -s tests -p "test*.py"`.

| Archivo | Qué comprueba |
|---|---|
| `test_i3_models.py`, `test_i3_synthetic.py` | validaciones y reproducibilidad del catálogo sintético |
| `test_i3_generation.py` | casos calculados a mano sobre un catálogo con cruces conocidos, códigos de error, contadores |
| `test_i3_ranking.py` | puntajes calculados a mano, heap contra ordenamiento, invariantes |
| `test_i3_differential.py` | los 3 generadores y los pipelines contra la versión lenta con solicitudes aleatorias; 500 solicitudes inválidas con igualdad de códigos de error |
| `test_i3_bnb.py` | B&B contra la referencia con 600 solicitudes y pesos arbitrarios; auditoría de la cota en cada nodo; evidencia de poda; sin poda en empates |
| `test_i3_motor_completo.py` | **10 000 operaciones aleatorias** sobre grafo (I1) + índice AVL (I2) + adaptador + motor (I3) contra `ListGraph`, `SlowCourseIndex` y `reference_schedules`, con códigos existentes, inexistentes e inválidos, invariantes tras cada paso y umbrales de cobertura |
| `test_i3_equivalencia_cruces.py` | la detección de cruces de I3 contra la de I2 (5 000 pares) |
| `test_i3_benchmarks.py` | el arnés de benchmarks y la equivalencia entre candidatos |

Con las ramas de integración de I1 e I2 fusionadas, la suite completa tiene 108 pruebas y todas
pasan (Python 3.13). La calidad de las pruebas se comprobó con mutaciones: la poda `<=` en B&B,
el desempate invertido, un cálculo de elegibles de I1 con otro predicado, una baja del índice de I2
que no hace nada, un adaptador que descarta el último elegible, y `<=` en `overlaps` de I2 hacen
fallar las pruebas. Una mutación equivalente (valor absoluto de un hueco ya no negativo) no se
puede detectar.

## 8. Qué no demuestran las pruebas ni las mediciones

- Los datos son sintéticos; las razones de tiempo no predicen el comportamiento con los horarios
  reales de `1CMP` y `1MAC`, y la efectividad de la poda depende de los pesos que elija el usuario.
- Mediciones en una sola máquina, 3 repeticiones, sin control de carga; Python 3.13 (no se repitió
  con 3.11, la versión del CI de I2).
- Las mezclas de operaciones de los escenarios son hipótesis; no se midió el costo conjunto del
  motor ni la reconstrucción del `Problem` por consulta.
- No se midió el punto de cruce entre heap y ordenamiento para k entre 10 y N/10.
- El branch and bound mezcla dos factores (cota y estrategia de cruces) frente al candidato A.
- La prueba del motor completo no incluye el índice de NRC de I2 (no integrado) ni prerrequisitos
  con alternativas OR ni correquisitos (el grafo de I1 solo expresa AND).
- La versión lenta y la rápida de I3 comparten especificación y autor: un error de interpretación
  del enunciado estaría en ambas. Las pruebas calculadas a mano mitigan esto solo en casos pequeños.

## 9. Ayudas utilizadas

- **Claude (Anthropic), asistente de IA:** apoyó el diseño de la operación «mejores K» y de la cota,
  escribió y revisó código, pruebas y arnés de benchmarks, y redactó los documentos. El autor
  revisó, aplicó y publicó cada cambio y ejecutó la corrida oficial de benchmarks. Las conversaciones
  no se incluyen.
- Biblioteca estándar de Python (`unittest`, `itertools`, `tracemalloc`, `csv`; el heap es propio y no usa `heapq`); `matplotlib` solo para los gráficos de benchmarks (dependencia de
  desarrollo, `requirements-i3-bench.txt`).
- Compañeros de equipo: las versiones lentas y los módulos de I1 (grafo, `tests/i1_graph_reference.py`)
  e I2 (índice AVL, conflictos, `SlowCourseIndex`) se usan tal como los escribieron sus autores.
