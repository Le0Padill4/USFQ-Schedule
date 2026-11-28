# Índice de NRC — propuesta I2

`NRCIndex` utiliza `CourseAVL` para indexar pares de cadenas `(periodo, NRC)`;
el mismo NRC puede existir en períodos distintos. Rechaza duplicados dentro de
un período sin sobrescribir, y conserva ceros iniciales. No infiere reglas de
normalización ni validación numérica de fuentes reales; requiere acuerdo con I3
para conexión a `Offering`. La adaptación a una actualización completa de
catálogo o transacciones múltiples sigue pendiente.

Altas, búsquedas y bajas son O(log n) en peor caso; espacio O(n). Se probaron
casos borde y 2.000 pasos sintéticos reproducibles frente a un diccionario,
validando invariantes tras cada paso. Esta es una prueba de la estructura, no
la prueba de 10.000 operaciones del motor completo ni un benchmark.

Prueba: `python3 -m unittest discover -s tests -p 'test_i2_*index.py' -v`.
