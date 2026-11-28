# Benchmarks del motor de horarios (Integrante 3) — resultados y análisis

Datos: `benchmarks/results/` (CSV crudos y resumen, `environment.json`, un PNG por operación).
Comando: `python -m benchmarks.run_all --repeats 3` (semilla 20261127, corrida completa, no `--quick`).

**Entorno:** CPython 3.13.9, Windows 11, Intel64 Family 6 Model 142 (8 CPU lógicas), 2026-11-27.
Una sola máquina, 3 repeticiones por punto (se reporta la mediana y el rango min–max).

## Qué se comparó

| Operación | Candidatos | Mismo problema / mismo desempate |
|---|---|---|
| Generar todos los horarios válidos | exhaustiva, backtracking con poda, CSP (forward checking + MRV) | mismos horarios, ordenados por tupla de NRC |
| Top-K de resultados ya puntuados | heap acotado propio, ordenamiento completo + corte | mismo orden `(-puntaje, NRC)`; el arnés aborta si las respuestas difieren |
| Mejores K horarios | A: generar todos (CSP) + puntuar + heap · B: branch and bound con cota optimista | mismo orden `(-puntaje, NRC)`; el arnés aborta si las respuestas difieren |

Tamaño = combinaciones del espacio de búsqueda (generación y mejores K) o N resultados (Top-K).
Datos sintéticos (`synthetic/`), no datos reales de la USFQ.

## 1. Generación de todos los horarios

Razón de tiempos de la mediana, exhaustiva / CSP: de 1,8x (pocos cruces, 10³) a 8,7x (10⁶); de 2,2x a 122x con muchos cruces; de 3,6x a 1044x con cruces extremos. Backtracking / CSP: entre 1,5x y 4,1x a favor del CSP, salvo un punto.

- **Exhaustiva: no gana en ningún escenario ni tamaño** (rangos min–max separados en los 12 puntos). Con cruces extremos a 10⁶ tarda 7,2 s contra 6,9 ms del CSP, porque visita las 10⁶ combinaciones y el CSP 137 nodos.
- **CSP gana en 11 de 12 puntos.** En `muchos_cruces` con 10³ el backtracking tiene la mediana menor (3,2 contra 3,9 ms), pero los rangos se solapan: es ruido, no una victoria.
- **Backtracking tampoco gana de forma sostenida.** Visita casi los mismos nodos que el CSP, pero hace entre 1,8 y 6,5 veces más comprobaciones de cruce (a 10⁶, pocos cruces: 2,9 M contra 0,58 M).
- **Coincide con la teoría:** el costo de la exhaustiva es el producto de opciones por el filtro de pares; la poda lo reduce a lo que cabe sin cruces, y el forward checking evita ramas que fallarían más abajo.

**Conclusión:** en esta operación no existe un escenario donde cada candidato gane. La exhaustiva se conserva como línea base de corrección (y como candidata a O1 solo para explicar por qué pierde), no como alternativa viable. Esto motivó proponer «mejores K horarios».

## 2. Top-K

| Escenario | Gana | Razón mediana (ordenamiento / heap) a 10⁶ | Memoria extra a 10⁶ |
|---|---|---|---|
| k=10, aleatorio | heap (desde N≥10⁴) | 5,4x | 1 KiB contra 109 MiB |
| k=N/10, aleatorio | ordenamiento (N≥10⁴) | 0,29x | 2 MiB contra 109 MiB |
| k=N/10, ascendente (peor caso del heap) | ordenamiento | 0,02x | 2 MiB contra 99 MiB |
| 10 consultas sobre flujo, k=10 | heap | 15x | 3 KiB contra 115 MiB |

- **Cada candidato gana en al menos un escenario**, con rangos separados salvo N=10³ (k=10 y k=N/10 aleatorio se solapan).
- **Comparaciones:** el heap hace ≈N comparaciones con k=10 (1,0 M a 10⁶, cada elemento se compara una vez con el peor retenido) contra 18,6 M del ordenamiento; en el caso ascendente invierte: 29 M contra 1 M, porque cada elemento entra al heap, mientras Timsort detecta la corrida ya ordenada y cuesta O(N).
- **Discrepancia a explicar, no a esconder:** con k=N/10 aleatorio el heap hace menos comparaciones que el ordenamiento (8,1 M contra 18,6 M) y aun así tarda 3,5 veces más (12,8 s contra 3,65 s). El heap es código Python y el ordenamiento usa `sorted` con `key` en C. El conteo de pasos no predice el tiempo entre implementaciones de lenguajes distintos; la columna de comparaciones del ordenamiento sale de una corrida instrumentada con `cmp_to_key`, distinta de la que se cronometra.
- **El heap siempre gana en memoria** (O(k) contra O(N)), incluso donde pierde en tiempo.
- **No se midió el punto de cruce** entre k=10 y k=N/10. La estimación k≈N/100 vino de la medición preliminar y **no está respaldada** por esta corrida; falta un escenario con k intermedio.

## 3. Mejores K horarios (branch and bound)

| Escenario | Gana | Razón (todos+Top-K / B&B) a 10³ … 10⁶ |
|---|---|---|
| preferencias fuertes, k=10 | B&B | 17,9x · 51,8x · 118,8x · **193,8x** (a 10⁶: 146 ms contra 28,2 s) |
| sin preferencias, k=10 | todos+Top-K | 0,74 · 0,63 · 0,73 · 0,82 |
| preferencias fuertes, k=100000 | todos+Top-K hasta 10⁵; **B&B a 10⁶** | 0,89 · 0,85 · 0,82 · **1,31** |
| solo huecos, k=10 | todos+Top-K | 0,91 · 0,91 · 0,83 · 0,75 (con solapes a 10³ y 10⁵) |

- **Cada candidato gana en algún escenario con rangos separados**, que es el criterio acordado: B&B con preferencias fuertes y k pequeño; «todos + Top-K» sin preferencias o con la cota de huecos, que es débil por diseño.
- **Poda:** con preferencias fuertes a 10⁶ B&B visita 2.106 nodos contra 469.521 y descarta 1.923 ramas. Sin preferencias o con solo huecos hace 0 podas, y es entre 10 % y 60 % más lento por calcular cotas.
- **k grande:** con k=10⁵ el heap no se llena mientras haya menos de 10⁵ factibles (55.020 a 10⁵), así que no hay umbral y B&B no poda (`pruned = 0`). A 10⁶ hay 414.575 factibles, el heap se llena, B&B poda 43.669 ramas y gana 1,31x con rangos separados (29,8–33,7 s contra 41,6–42,3 s).
- **Amenaza a la validez:** B&B se apoya en el orden del backtracking, no en el forward checking del CSP. Sin podas hace 2,9 M comprobaciones de cruce contra 0,58 M de «todos + Top-K», lo que explica parte de su desventaja (entre 10 % y 60 % más lento). Una variante con forward checking no está implementada, así que la comparación mezcla dos factores (estrategia de poda y estrategia de cruces) y no aísla la cota.
- **Sesgo de escenarios:** «preferencias fuertes» se eligió porque la cota funciona ahí; el factor 194x no debe generalizarse a datos reales. Cuánto poda en la práctica depende de los pesos que elija cada estudiante.

## Limitaciones

- Una máquina, Windows, 3 repeticiones, sin control de carga de fondo; el repositorio vive en OneDrive (los benchmarks trabajan en memoria, pero no se aisló el efecto).
- Datos sintéticos; las razones no son predicciones sobre los horarios reales de `1CMP` y `1MAC`.
- Python 3.13; no se repitió con 3.11 (versión del CI de I2).
- Los pasos (nodos, cruces, comparaciones) son contadores del código propio, no una medida de CPU.
- Los CSV `*_raw.csv` permiten recalcular medianas y rangos; `*_summary.csv` es lo que usan los gráficos.
