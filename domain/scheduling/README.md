# Scheduling — I3

Modelos de horario (`Meeting`, `Offering`, `EligibleCourse`), errores tipados y
solape de reuniones. Solo biblioteca estandar. Mismas codificaciones que
`domain/course_index/conflicts.py` de I2: dia 0 (lunes) a 6, minutos `[inicio, fin)`.

Los fixtures sinteticos estan en `synthetic/` (todo `SYN...`, sin datos reales).
`synthetic.eligible_courses` es un MOCK de la habilitacion de I1.

Desde la raiz de USFQ-Schedule:

```text
python -m unittest discover -s tests -p "test_i3_*.py" -v
```
