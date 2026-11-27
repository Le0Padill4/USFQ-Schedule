# Benchmarks de I3

Dos operaciones, cada una con candidatos que resuelven **exactamente el mismo problema** y
devuelven resultados equivalentes (el arnes lo comprueba antes de medir y falla si difieren).

| Operacion | Candidatos | Escenarios |
|---|---|---|
| Generacion de todos los horarios factibles | exhaustiva, backtracking con poda, CSP (forward checking + MRV) | `pocos_cruces`, `muchos_cruces`, `cruces_extremos` |
| Top-K de resultados puntuados | heap acotado propio, ordenamiento completo | `k10_aleatorio`, `k_decimo_aleatorio`, `k_decimo_ascendente`, `flujo_10_consultas` |

Tamanos completos: 10^3, 10^4, 10^5 y 10^6 (combinaciones del espacio de busqueda en
generacion; N resultados en Top-K).

## Comandos

Desde la raiz del repositorio (solo `matplotlib` es una dependencia, y solo para los graficos):

```text
pip install -r requirements-i3-bench.txt
python -m benchmarks.run_all
```

- `--quick`: tamanos reducidos (unos 20 s) para comprobar que todo funciona; usar `--out OTRA_CARPETA`
  para no mezclar con los resultados oficiales.
- `--no-plot`: solo CSV. `--repeats N` (por defecto 5). `--seed S` (por defecto 20261127).

Salida en `benchmarks/results/`: `generacion_raw.csv`, `generacion_summary.csv`, `topk_raw.csv`,
`topk_summary.csv`, `generacion.png`, `topk.png` y `environment.json`.

## Metodologia

- **Tiempo:** `time.perf_counter`, `gc.collect()` antes de cada repeticion, `--repeats` repeticiones;
  se reporta mediana y minimo-maximo (`*_raw.csv` trae cada repeticion).
- **Pasos:** contadores propios en una corrida aparte: nodos y comparaciones de cruce
  (generacion); comparaciones de ranking (Top-K). En el ordenamiento se cuentan con
  `functools.cmp_to_key`, lo que lo hace mas lento solo en esa corrida de conteo.
- **Memoria (Top-K):** pico extra segun `tracemalloc` durante la operacion (los datos de entrada
  no cuentan). Mide asignaciones de Python, no la memoria del proceso.
- Instancias sinteticas y deterministas por semilla; no hay datos reales de la USFQ.
- **Todas las mediciones oficiales deben hacerse en el mismo computador**, sin otras cargas pesadas.
  `environment.json` registra version de Python y plataforma. Los numeros de otro equipo no son
  comparables entre si.

## Limitaciones

- Mide Python (CPython), no la complejidad teorica en abstracto: el `sorted` y `product`
  son codigo en C, mientras el heap y el backtracking son bytecode, lo que desplaza los puntos de cruce.
- Los escenarios son sinteticos; cuanto se parecen a una inscripcion real no esta demostrado.
- Una unica semilla por instancia; las repeticiones miden ruido de ejecucion, no variabilidad entre instancias.
