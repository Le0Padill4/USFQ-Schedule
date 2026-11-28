# Experimento I2: consultas por rango e inserciones

Compara la misma interfaz de mapa ordenado para claves enteras sintéticas:
`CourseAVL` frente a lista ordenada de Python con `bisect`. Cada consulta devuelve
las claves del intervalo inclusivo y cada inserción agrega una clave nueva.
Se validan todas las listas de resultados entre candidatos y repeticiones, y
se comprueban los invariantes AVL. Semilla y entorno están en `entorno.txt`.

Desde la raíz del repositorio que incluya el PR base del AVL:

```
python3 experimentos/i2_rangos/benchmark.py
```

Sobrescribe el CSV, SVG y entorno con la nueva medición. Se usan 1.000, 5.000,
10.000 y 50.000 claves iniciales, tres repeticiones por punto y un lote idéntico
de 400 operaciones en cada repetición. Los escenarios son 90 % consultas/10 %
inserciones y 10 % consultas/90 % inserciones, con rangos de anchura 20 y
claves iniciales pares; se insertan claves impares aleatorias. El orden de los
candidatos alterna entre repeticiones. El reloj mide el lote completo y la
materialización de respuestas, no la construcción inicial ni la verificación;
los resultados son medianas en milisegundos. El gráfico usa escala logarítmica
en tiempo y una escala vertical independiente por escenario.

En esta corrida, la lista fue más rápida en todos los tamaños con 90 % de
consultas y en tamaños hasta 10.000 con muchas inserciones; a 50.000 y muchas
inserciones, AVL tomó 1,48 ms y la lista 2,53 ms por lote. El crecimiento de las
inserciones en lista es compatible con desplazamientos O(n), mientras AVL tiene
inserciones O(log n); las constantes y la implementación optimizada de la lista
importan mucho. Esto no mide uso de memoria, concurrencia, datos reales, costo de
carga inicial, ni todos los patrones posibles. Un checksum se conserva solo como
referencia; la igualdad completa de las respuestas se comprueba durante la corrida.

Este es **un** experimento de operación, no los dos benchmarks del motor completo
ni evidencia de que se cumpla toda la rúbrica. Requiere revisión y coordinación
con I3 sobre escenarios globales, estructura compartida y reporte final.

La inserción aquí forma parte de la carga mixta y del costo de mantenimiento:
no se ha medido por separado ni debe contarse como una segunda operación
medida. Para que la consulta de rango cuente en la entrega, el motor integrado
debe exponerla como operación real y el informe debe justificar sus candidatos
y escenarios; este experimento aislado no demuestra esas condiciones.
