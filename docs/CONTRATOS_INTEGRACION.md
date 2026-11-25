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
