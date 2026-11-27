# Índice AVL — Integrante 2

`domain.course_index.avl.CourseAVL` es un mapa en memoria con claves únicas
comparables, sin dependencia de modelos compartidos. `put` inserta o reemplaza;
`get` y `delete` levantan `KeyError` si falta la clave. `range_items` devuelve
pares en orden con extremos inclusivos y rechaza límites invertidos. Para
ofertas pueden usarse claves compuestas `(periodo, codigo, nrc)`: el convenio
exacto de normalización y la interfaz con scheduling aún requieren acuerdo.

Inserción, consulta y eliminación cuestan O(log n) en peor caso, y el rango
O(log n + k), para k resultados. El almacenamiento es O(n); el recorrido usa
O(log n) de pila en un árbol válido, sin contar los resultados. Si se mantienen
índices separados por materia y NRC, cada actualización debe modificar ambos y
su costo y espacio se suman. Esta implementación aislada no proporciona todavía
transacciones entre índices, persistencia ni validación de horarios.

Invariantes: claves estrictamente ordenadas, altura almacenada correcta,
diferencia de alturas de hijos a lo sumo 1 y tamaño coherente. La prueba
aleatoria compara 5.000 operaciones de este mapa con un diccionario y valida
invariantes tras cada paso; no es la comparación de 10.000 operaciones del motor
completo que exige CMP3002. No se ha realizado benchmark.

Prueba: `python3 -m unittest discover -s tests -p 'test_i2_avl.py' -v`.

## Continuidad del 25 de noviembre

El PR #6 tiene un flujo `i2-python` que ejecuta unittest y compileall; pasó en
GitHub Actions. Se solicitó revisión a I1 e I3; sigue en borrador. El check
obligatorio `docs` depende del PR #5 y aún no aparece en este PR. Los PR #10,
#13 y #14 conservan la base AVL; cambiarlos a main solo cuando #6 se integre,
revisando su historial y pruebas. No se ha fusionado ningún PR.
