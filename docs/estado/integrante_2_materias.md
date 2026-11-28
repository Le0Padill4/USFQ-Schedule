# Índice por código de materia — propuesta I2

`CourseIndex` indexa códigos exactos con AVL. Rechaza duplicados sin reemplazar,
devuelve rangos inclusivos en orden lexicográfico y no convierte códigos ni
infiere su pertenencia a una carrera. La representación canónica y la unión con
las dos mallas requieren revisión de I1/I3. Inserción, consulta y baja cuestan
O(log n), rango O(log n + k) y almacenamiento O(n), sin contar valores externos.

Las pruebas cubren bordes y 2.000 pasos sintéticos frente a un diccionario con
invariantes tras cada paso; no sustituyen las pruebas del motor completo.
Ejecutar `python3 -m unittest discover -s tests -p 'test_i2*.py' -v`.

## Referencia local para integración

`tests/reference/course_index_slow.py` implementa este índice con una lista,
independiente del AVL. Una prueba ejecutó 10.000 operaciones sintéticas de
alta, búsqueda, baja y rangos (incluidos duplicados, ausentes y límites
invertidos), comparó respuestas y errores, y verificó el AVL tras cada paso.
`python3 -m unittest discover -s tests -p 'test_i2*.py' -v`: 7 pruebas
correctas en Python 3.13.13. Semilla: 20261125. Esta referencia es solo del
índice; el arnés, los modelos y la versión lenta del motor completo siguen por
acordar con I3. PR #14 sigue dependiendo del AVL #6 y no está integrado.
