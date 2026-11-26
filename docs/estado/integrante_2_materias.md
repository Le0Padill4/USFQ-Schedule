# Índice por código de materia — propuesta I2

`CourseIndex` indexa códigos exactos con AVL. Rechaza duplicados sin reemplazar,
devuelve rangos inclusivos en orden lexicográfico y no convierte códigos ni
infiere su pertenencia a una carrera. La representación canónica y la unión con
las dos mallas requieren revisión de I1/I3. Inserción, consulta y baja cuestan
O(log n), rango O(log n + k) y almacenamiento O(n), sin contar valores externos.

Las pruebas cubren bordes y 2.000 pasos sintéticos frente a un diccionario con
invariantes tras cada paso; no sustituyen las pruebas del motor completo.
Ejecutar `python3 -m unittest discover -s tests -p 'test_i2*.py' -v`.
