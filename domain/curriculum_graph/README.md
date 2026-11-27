# Grafo curricular propio — I1

Módulo Python sin dependencias externas. Implementa un DAG de prerrequisitos
AND; las reglas desconocidas bloquean la habilitación. No interpreta fuentes
académicas, OR, correquisitos, notas mínimas, carreras ni versiones de malla.

Desde la raíz de USFQ-Schedule, con Python 3.14 (versión comprobada):

```text
python -m unittest discover -s tests -p 'test_i1_curriculum_graph.py' -v
```

Son 12 pruebas, incluida una comparación de 10.000 operaciones con una referencia
independiente de listas. La comparación corresponde solo al grafo de I1.

```python
from domain.curriculum_graph import CourseGraph

graph = CourseGraph()
graph.add_course("SYN-A", prerequisites_known=True)
graph.add_course("SYN-B", prerequisites_known=True)
graph.add_course("SYN-C")  # requisitos desconocidos
graph.add_prerequisite("SYN-A", "SYN-B")
assert graph.eligible_courses(["SYN-A"]) == ("SYN-B",)
graph.check_invariants()
```

Las aristas apuntan del prerrequisito a su dependiente. `bfs` y `dfs` recorren
dependientes; `dependencies` consulta antecedentes. Todas las consultas de
colecciones devuelven tuplas separadas del estado interno. La topología usa
desempate lexicográfico. Insertar un ciclo falla antes de modificar el estado.

Interfaz y decisiones pendientes de revisión por I2/I3 en
[`docs/i1/CONTRATO_GRAFO_PROPUESTA.md`](../../docs/i1/CONTRATO_GRAFO_PROPUESTA.md).
El contrato común permanece sin modificaciones. Los consumidores deben acordar
nombres, errores y completitud antes de integrar el módulo.
