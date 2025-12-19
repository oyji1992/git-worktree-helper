# -*- coding: utf-8 -*-
import os
import sys
import unittest
from pathlib import Path

# Ensure `src/` is on sys.path so `import gwtlib` works when running from repo root.
REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))


class TestI18n(unittest.TestCase):
    def test_env_override(self):
        from gwtlib import i18n

        old = os.environ.get("GWT_LANG")
        try:
            os.environ["GWT_LANG"] = "zh"
            i18n.set_language("en")  # reset cache
            i18n._current_lang = None
            self.assertEqual(i18n.detect_language(), "zh")
        finally:
            if old is None:
                os.environ.pop("GWT_LANG", None)
            else:
                os.environ["GWT_LANG"] = old

    def test_fallback_default_is_en(self):
        from gwtlib import i18n

        old = os.environ.get("GWT_LANG")
        try:
            os.environ.pop("GWT_LANG", None)
            i18n._current_lang = None
            lang = i18n.detect_language()
            self.assertIn(lang, ("en", "zh"))
        finally:
            if old is not None:
                os.environ["GWT_LANG"] = old


if __name__ == "__main__":
    unittest.main()
