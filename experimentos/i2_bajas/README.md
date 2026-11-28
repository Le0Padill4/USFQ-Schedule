# Experimento I2: baja en índice ordenado

Se comparan `CourseAVL.delete` y una lista ordenada con búsqueda binaria y
`pop`, con claves enteras sintéticas. Los dos casos eliminan 200 claves
existentes: al inicio (limpieza de códigos bajos) o al final (retiro de códigos
altos). Se prueban 1.000, 5.000, 10.000 y 50.000 claves, cinco repeticiones
por punto, alternando el orden de candidatos. El cronómetro incluye búsqueda y
baja, no construcción ni verificación. Después se compara el estado completo
con el resultado esperado y se verifican los invariantes del AVL.

Desde la raíz, en una rama que incluya este experimento y el AVL:

```sh
python3 experimentos/i2_bajas/benchmark.py
```

El comando sobrescribe CSV, SVG y entorno. El gráfico usa escalas verticales
independientes y mediana del lote en milisegundos; no compara directamente la
altura visual entre paneles. No se midieron memoria ni costo de construcción.

En la corrida incluida, con 50.000 claves, eliminar al inicio tomó una mediana
de 0,5120 ms con AVL y 1,1230 ms con lista. Al final fueron 0,5352 ms y
0,0258 ms respectivamente. En los demás tamaños la lista fue más rápida en
ambos casos. El AVL cuesta O(log n) por baja en el peor caso; la lista busca en
O(log n) pero desplaza hasta O(n) elementos, salvo al retirar al final. Las
constantes de Python influyen. Los resultados son de esta máquina y no prueban
un patrón real de oferta ni extrapolan a todos los tamaños.

La baja es distinta de la consulta de rango, pero esta medición aislada solo
puede contar como segunda operación evaluable si el motor integrado ofrece una
baja real con este contrato y el informe justifica ambos candidatos y sus
escenarios. También debe contabilizarse la actualización de todas las demás
estructuras que compartan esos datos. Hasta verificarlo, no se declara cumplido
el requisito de dos operaciones medidas del motor completo.
