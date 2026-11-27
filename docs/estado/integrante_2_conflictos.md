# Conflictos de reuniones — propuesta I2

`domain.course_index.conflicts` ofrece un valor inmutable `Interval` y funciones
`overlaps` y `conflicts` independientes de modelos compartidos. La codificación
propuesta es lunes=0 a domingo=6 y minutos desde medianoche, con intervalos
semiabiertos. Horarios consecutivos no se cruzan. La propuesta del integrante 3
usa la misma convención, pero esta API aún requiere revisión y adaptación al
modelo definitivo antes de integrarla.

`conflicts` recibe colecciones de reuniones y compara pares: O(m*n) tiempo y
O(n) espacio para materializar la segunda colección, compatible con iteradores.
Una colección vacía no certifica que la oferta sea válida: puede representar
datos desconocidos o clases asíncronas. La fuente real también puede contener
fechas de vigencia y marcadores de hora que aún no están modelados. No convertir
estos casos automáticamente en clases regulares ni declarar que no hay conflicto
sin resolver su significado.

Prueba: `python3 -m unittest discover -s tests -p 'test_i2_conflicts.py' -v`.
