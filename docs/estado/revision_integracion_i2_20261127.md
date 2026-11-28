# Integración académica I1–I2–I3: evidencia y cuestiones abiertas

Árbol de verificación: combinación local de #17 (`27244f6`) y la rama de #23
(`f5152ad`), sin fusionar en main. Pruebas el 27 nov 2026:
`python3 -m unittest discover -s tests -p 'test_*.py' -v`: 111 pruebas,
110 correctas y una omitida por falta de matplotlib. El diferencial de 10.000
pasos incluye grafo, índice de materias, adaptador de elegibilidad y scheduling;
la semilla principal produjo 915 consultas con horarios no vacíos. No cubre el
índice NRC ni acredita mallas reales, soporte OR o integración publicada.

## Contrato propuesto desde I2

- `Interval` usa lunes=0 a domingo=6 y minutos `[inicio, fin)`; coincide con
  `Meeting` de I3. Los tests de equivalencia ejecutados comparan 5.000 pares y
  3.000 ofertas. Una reunión desconocida no equivale a disponibilidad.
- `CourseIndex` busca código exacto; `NRCIndex` usa `(term, nrc)` como cadenas y
  conserva ceros iniciales. Las ofertas deben corresponder al período solicitado y
  su clave de NRC al registro de la oferta; se requiere acordar errores y la
  responsabilidad de validar coherencia antes de integrar.
- El grafo actual expresa AND y reglas desconocidas bloquean elegibilidad; no
  inferir pertenencia a carrera por prefijo ni afirmar OR hasta acordarlo con I1.

## Hallazgo reproducido: período

Con `ScheduleRequest(term="ACTUAL", career_id="1CMP", required_courses=("SYN1",))`
y una única `Offering` de período `OTRO`, NRC `001`, materia `SYN1`, reunión
`Meeting(0,480,540)`, `generate_schedules` devuelve un horario con `001`.
`build_problem` no valida o filtra `off.term` frente a `request.term`. La referencia
lenta tampoco detecta este caso: coincidir con ella no demuestra aislamiento por
período. Acordar con I3 si se rechaza catálogo inconsistente o se filtra por
período; cubrir ambos candidatos, referencia, NRC repetido entre períodos y
paralelo fijado. No modificar unilateralmente el motor de I3.

## Benchmarks y límites

Los CSV existentes de I3 miden generación, selección Top-K y mejores K sobre
problemas de scheduling ya construidos. No miden el flujo de consulta con grafo,
CourseIndex y NRCIndex. Son evidencia de esas operaciones, no del costo total
integrado. Pendientes mediciones de las operaciones finales, candidatos comparables,
mantenimiento de índices, memoria y revisión conjunta del informe antes del ZIP.
