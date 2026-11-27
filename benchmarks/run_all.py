"""Ejecuta los benchmarks de I3: ``python -m benchmarks.run_all [--quick]``."""

from __future__ import annotations

import argparse
from pathlib import Path

from . import bench_generation, bench_topk
from .common import DEFAULT_SEED, write_environment


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=Path("benchmarks/results"))
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument("--quick", action="store_true", help="tamanos reducidos para una prueba rapida")
    ap.add_argument("--no-plot", action="store_true", help="solo CSV, sin graficos")
    args = ap.parse_args(argv)

    gen_sizes = bench_generation.QUICK_SIZES if args.quick else bench_generation.FULL_SIZES
    topk_sizes = bench_topk.QUICK_SIZES if args.quick else bench_topk.FULL_SIZES
    write_environment(args.out, repeats=args.repeats, seed=args.seed, quick=args.quick)
    print("generacion...", flush=True)
    bench_generation.run(args.out, sizes=gen_sizes, repeats=args.repeats, seed=args.seed)
    print("topk...", flush=True)
    bench_topk.run(args.out, sizes=topk_sizes, repeats=args.repeats, seed=args.seed)
    if not args.no_plot:
        try:
            from .plot import plot_operation

            for op in ("generacion", "topk"):
                print("grafico:", plot_operation(op, args.out))
        except ImportError:
            print("matplotlib no esta instalado: se omiten los graficos "
                  "(pip install -r requirements-i3-bench.txt)")
    print("listo:", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
