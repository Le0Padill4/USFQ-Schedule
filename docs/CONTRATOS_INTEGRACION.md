# Contratos de integración

Estado: propuesta inicial; cambios mediante PR coordinado antes de modificar consumidores.

## Modelos

- `Course(code, title, credits, career_id)`.
- `PrerequisiteEdge(prerequisite_code, course_code)`; malla acíclica.
- `PassedCourse(user_id, course_code)`; identificador de prueba, sin expediente real.
- `Offering(term, nrc, course_code, section, instructor_label, meetings, source, retrieved_at)`.
- `Meeting(day, start_minute, end_minute)`; intervalo semiabierto para evitar falsos cruces en clases consecutivas.
- `ScheduleRequest(term, passed_codes, constraints, preferences, max_results)`.
- `ScheduleResult(nrcs, score, explanations)`.

## REST v1

- `POST /api/v1/auth/register`, `POST /api/v1/auth/login`.
- `GET /api/v1/careers`, `GET /api/v1/careers/{id}/curriculum`.
- `PUT /api/v1/me/passed-courses`.
- `GET /api/v1/offerings?term=&course_code=&instructor=`.
- `POST /api/v1/schedules/generate` con `ScheduleRequest`; devuelve lista ordenada de `ScheduleResult` y errores de validación explícitos.

La API no devuelve cupos o NRC inventados. Fechas, zona horaria, paginación y origen se documentan antes de integrar una fuente real.

## Contratos internos

`CourseGraph` valida aristas y produce habilitadas/orden topológico. `CourseAVL` indexa código y rangos. `ScheduleGenerator` solo consume candidatos cuyos prerrequisitos se cumplan y entrega combinaciones sin conflictos. MCP llama casos de uso de consulta; no escribe datos ni ejecuta consultas arbitrarias.

---

## Propuesta I3 — Scheduling v0.2 (PENDIENTE de revisión de Integrantes 1 y 2)

Estado: **propuesta**. Nada de esta sección es vigente hasta que el PR sea aprobado por I1 (modelos de malla/grafo) e I2 (oferta, índices, API). Los puntos marcados «Pregunta» requieren respuesta del dueño del módulo; mientras tanto el motor de scheduling usa fixtures sintéticos.

### Alcance de carreras

El MVP admite únicamente `1CMP` (Ingeniería en Ciencias de la Computación) y `1MAC` (Ingeniería en Matemáticas Aplicadas y Computación). El límite aplica a las carreras y mallas seleccionables, **no** a los prefijos de código: una materia compartida, de Colegio General, inglés, laboratorio, ejercicio, optativa o electiva pertenece a una malla solo si lo indica su entrada de malla verificada. No se asume que todo `CMP*`/`MAC*` pertenece a una malla.

- `Career(id, name)` con `id ∈ {"1CMP", "1MAC"}`.
- `CurriculumEntry(career_id, course_code, kind)` con `kind ∈ {core, shared, general_college, english, lab, exercise, optional, elective}`. Una materia puede tener entradas en varias carreras (reemplaza la lectura de `Course.career_id` como pertenencia única). **Pregunta I1:** ¿se conserva `Course.career_id` o se sustituye por `CurriculumEntry`?
- Los datos reales de mallas y oferta los provee el módulo de importación de I2; I3 solo consume fixtures sintéticos rotulados como tales.

### Prerrequisitos alternativos

`PrerequisiteEdge` solo expresa AND. Propuesta: `PrerequisiteGroup(course_code, group_id, alternatives: tuple[str, ...])`. Una materia es habilitable si **cada** grupo tiene **al menos una** alternativa aprobada (AND de ORs). Un grupo con una sola alternativa equivale a la arista actual. **Pregunta I1:** ¿el grafo propio soporta grupos OR o se expande a nodos auxiliares? **Pregunta I1:** ¿existen correquisitos que deban modelarse?

### Reuniones

`Offering.meetings` es una lista no vacía de `Meeting(day, start_minute, end_minute)`. Propuesta de rangos: `day` entero 0 (lunes) a 6 (domingo); `0 <= start_minute < end_minute <= 1440`; intervalo semiabierto `[start, end)`, de modo que `end == start'` no es cruce. Dos ofertas se cruzan si alguna reunión de una se solapa con alguna de la otra el mismo día. **Pregunta I2:** confirmar codificación de `day` y minutos.

### ScheduleRequest (tipado)

```
ScheduleRequest(
  term: str,
  career_id: "1CMP" | "1MAC",
  passed_codes: set[str],
  required_courses: tuple[str, ...],        # deben aparecer en el horario
  optional_courses: tuple[(str, int), ...], # (código, prioridad; mayor = más importante)
  pinned: dict[str, str],                   # course_code -> nrc fijado
  constraints: Constraints,                 # obligatorias
  preferences: Preferences,                 # flexibles
  max_results: int,                         # >= 1
)
Constraints(max_credits, min_credits, blocked_days: set[int], blocked_ranges: list[(day, start, end)])
Preferences(free_day: int|None, minimize_days: bool, minimize_gap_minutes: bool,
            preferred_ranges: list[(day,start,end)], avoided_ranges: list[(day,start,end)],
            weights: dict[str, int])
```

Obligatorias (nunca se violan): sin cruces, paralelos fijados, prerrequisitos cumplidos, créditos mínimo/máximo, días y franjas bloqueados, una sola oferta por materia. Flexibles (solo afectan el puntaje): viernes libre/día libre, menos días de clase, menos horas libres entre clases, franjas preferidas/evitadas, prioridades de materias opcionales.

### ScheduleResult y puntaje determinista

```
ScheduleResult(nrcs: tuple[str, ...], score: int, explanations: tuple[ScoreTerm, ...])
ScoreTerm(name: str, raw_value: int, weight: int, points: int)   # points = raw_value * weight
```

- `nrcs` ordenado ascendentemente; `score = sum(t.points for t in explanations)` (enteros, sin flotantes → resultado reproducible).
- Orden de resultados: `(-score, nrcs)`; desempate lexicográfico por la tupla de NRC. Todo candidato de una misma operación debe devolver exactamente la misma lista.

### Entradas y errores del generador

`ScheduleGenerator.generate(request, eligible) -> list[ScheduleResult]`, donde `eligible: list[EligibleCourse(course_code, credits, offerings)]` lo arma la capa de aplicación (habilitadas según el grafo de I1; ofertas desde I2). El generador no accede a BD, red ni frontend.

Errores explícitos (excepción tipada con código): `UNKNOWN_COURSE`, `UNKNOWN_NRC`, `DUPLICATE_NRC`, `NOT_ELIGIBLE`, `INVALID_RANGE` (p. ej. `max_results < 1`, minutos fuera de rango), `CAREER_NOT_SUPPORTED`. Solicitud sin cursos requeridos ni opcionales → lista vacía (no error). Sin horario factible → lista vacía.

### Coordinación de cruces e índices por NRC

La detección de cruces y el índice por NRC pueden ya existir como parte del módulo de I2. **Pregunta I2:** ¿implementarás un índice por NRC/código y una función de solape de `Meeting`? Si es así, I3 las consume y solo aporta candidatos alternativos para benchmarks, sin duplicar la API. Si no, I3 define una función mínima de solape dentro de `domain/scheduling`.
