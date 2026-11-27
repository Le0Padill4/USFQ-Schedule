# Scheduling — Integrante 3

Motor de horarios: validación de la solicitud, generación de horarios sin cruces, puntaje entero
determinista y selección de los mejores K. Solo biblioteca estándar. Todo el catálogo de pruebas y
benchmarks es **sintético** (`synthetic/`, códigos `SYN...`); no hay datos reales de la USFQ.

Mismas codificaciones que `domain/course_index/conflicts.py` de I2: día 0 (lunes) a 6, minutos
`[inicio, fin)`.

| Módulo | Contenido |
|---|---|
| `models.py`, `errors.py` | `Meeting`, `Offering`, `EligibleCourse`; errores tipados |
| `request.py` | `ScheduleRequest`, `Constraints`, `Preferences`, `build_problem` |
| `generation.py` | generadores exhaustivo, backtracking y CSP; contadores de pasos (`Stats`) |
| `scoring.py` | `score_schedule`, `rank_key` (orden `(-puntaje, NRC)`) |
| `topk.py` | `BoundedHeap` propio y Top-K con heap u ordenamiento |
| `optimize.py` | «mejores K»: todos + Top-K frente a branch and bound |
| `engine.py` | `generate_schedules`, `best_schedules` |
| `reference.py` | versión lenta independiente, para las pruebas diferenciales |

## Cómo se usa

```python
from domain.scheduling import ScheduleRequest, best_schedules
mejores = best_schedules(request, eligible_courses, method="branch_and_bound")
```

## Comandos (desde la raíz del repositorio)

Pruebas (incluye las de I1 e I2):

```text
python -m unittest discover -s tests -p "test*.py"
```

Solo las de I3: `python -m unittest discover -s tests -p "test_i3_*.py"`. La prueba diferencial del motor
completo (10 000 operaciones) y la equivalencia de cruces se **omiten con aviso** si faltan las piezas
de I1/I2 en la rama (grafo y `conflicts.py` en `main`, índice AVL en la rama de integración).

Mediciones (ver `benchmarks/README.md`):

```text
pip install -r requirements-i3-bench.txt
python -m benchmarks.run_all --repeats 3
```

Resultados de la corrida oficial: `benchmarks/results/`; análisis: `docs/benchmarks_i3.md`; informe de
esta parte: `docs/informe_i3.md`. Para armar el ZIP de entrega:
`python scripts/empaquetar_zip.py proyecto-apellido1-apellido2-apellido3`.
