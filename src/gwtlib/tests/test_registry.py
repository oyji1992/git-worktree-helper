# -*- coding: utf-8 -*-
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))


class TestRegistry(unittest.TestCase):
    def test_aliases_unique(self):
        from gwtlib.registry import iter_commands

        seen = {}
        for spec in iter_commands():
            for name in (spec.name,) + tuple(spec.aliases):
                if name in seen and seen[name] != spec.name:
                    self.fail(f"alias/name '{name}' maps to both {seen[name]} and {spec.name}")
                seen[name] = spec.name

    def test_hidden_remote_not_visible(self):
        from gwtlib.registry import visible_commands

        names = {c.name for c in visible_commands()}
        self.assertNotIn("remote", names)


if __name__ == "__main__":
    unittest.main()
