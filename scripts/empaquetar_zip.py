"""Arma el ZIP de entrega del Proyecto (CMP3002) desde la raiz del repositorio.

Uso (desde la raiz):

    python scripts/empaquetar_zip.py proyecto-apellido1-apellido2-apellido3

El nombre lleva el primer apellido de cada integrante en orden alfabetico. Genera
``<nombre>.zip`` en la carpeta padre de la raiz (o en ``--salida``), con todo dentro de una
carpeta ``<nombre>/``. Excluye el historial de Git, caches, entornos virtuales, ejecutables y
archivos de secretos o datos personales tipicos; los resultados ``benchmarks/results`` SI se
incluyen. Solo usa la biblioteca estandar.
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

EXCLUDED_DIRS = {
    ".git", "__pycache__", ".venv", "venv", "env", "node_modules", ".ruff_cache",
    ".mypy_cache", ".pytest_cache", ".idea", ".vscode", "dist", "build", ".android",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".exe", ".dll", ".so", ".dylib", ".zip", ".db", ".sqlite",
                     ".sqlite3", ".pem", ".key"}
EXCLUDED_NAMES = {".env", ".DS_Store", "Thumbs.db"}


def collect_files(root: Path) -> list[Path]:
    """Archivos a incluir, ordenados, relativos a ``root``."""
    found = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if not path.is_file() or any(part in EXCLUDED_DIRS for part in rel.parts[:-1]):
            continue
        if (path.name in EXCLUDED_NAMES or path.suffix.lower() in EXCLUDED_SUFFIXES
                or path.name.startswith(".env.")):
            continue
        found.append(rel)
    return found


def build_zip(root: Path, dest_dir: Path, name: str) -> tuple[Path, int]:
    if not name or "/" in name or "\\" in name or name.endswith(".zip"):
        raise ValueError("el nombre debe ser sin extension ni rutas, p. ej. proyecto-mora-vega")
    files = collect_files(root)
    target = dest_dir / f"{name}.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in files:
            zf.write(root / rel, f"{name}/{rel.as_posix()}")
    return target, len(files)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("nombre", help="p. ej. proyecto-apellido1-apellido2-apellido3")
    parser.add_argument("--salida", type=Path, default=None, help="carpeta de destino")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parent.parent
    dest = (args.salida or root.parent).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    if root in (dest, *dest.parents) and dest != root.parent:
        print("La carpeta de salida no debe estar dentro del repositorio.", file=sys.stderr)
        return 2
    target, count = build_zip(root, dest, args.nombre)
    print(f"{target} ({count} archivos, {target.stat().st_size / 1024:.0f} KiB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
