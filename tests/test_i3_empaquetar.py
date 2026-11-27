"""El empaquetado excluye historial, caches y ejecutables, e incluye resultados de benchmarks."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "empaquetar_zip.py"


@unittest.skipUnless(SCRIPT.exists(), "scripts/empaquetar_zip.py no existe en esta rama")
class PackagingTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("empaquetar_zip", SCRIPT)
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)

    def test_excludes_and_includes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, out = Path(tmp) / "repo", Path(tmp) / "out"
            for rel in ("README.md", "domain/a.py", "benchmarks/results/topk_raw.csv",
                        ".git/config", "domain/__pycache__/a.pyc", "tool.exe", ".env",
                        "old.zip", ".venv/lib/x.py"):
                f = root / rel
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text("x")
            out.mkdir()
            target, count = self.mod.build_zip(root, out, "proyecto-a-b")
            with zipfile.ZipFile(target) as zf:
                names = sorted(zf.namelist())
            self.assertEqual(names, ["proyecto-a-b/README.md", "proyecto-a-b/benchmarks/results/topk_raw.csv",
                                     "proyecto-a-b/domain/a.py"])
            self.assertEqual(count, 3)

    def test_rejects_bad_name(self):
        for bad in ("", "a/b", "x.zip"):
            with self.assertRaises(ValueError):
                self.mod.build_zip(Path("."), Path("."), bad)


if __name__ == "__main__":
    unittest.main()
