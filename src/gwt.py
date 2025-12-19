#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import sys
import traceback

# Fix encoding for Windows
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from gwtlib.completion import cmd_completion
from gwtlib.config import get_effective_config
from gwtlib.errors import GWTError
from gwtlib.help import print_help
from gwtlib.i18n import set_language
from gwtlib.i18n import t
from gwtlib.registry import iter_commands
from gwtlib.utils import print_colored


def _cmd_help(_args):
    print_help()


def _extract_lang_argv(argv):
    for i, tok in enumerate(argv):
        if tok == "--lang" and i + 1 < len(argv):
            return argv[i + 1]
        if tok.startswith("--lang="):
            return tok.split("=", 1)[1]
    return None


def _init_language(argv):
    lang = _extract_lang_argv(argv)
    if lang:
        set_language(lang)
        return

    # Apply persisted config if present and not overridden by env var.
    # Priority:
    #   --lang > GWT_LANG > config(ui.lang) > locale
    if "GWT_LANG" in os.environ:
        return
    config = get_effective_config()
    ui_lang = (config.get("ui") or {}).get("lang", "auto")
    if ui_lang in ("zh", "en"):
        set_language(ui_lang)


def main():
    _init_language(sys.argv[1:])

    if "-h" in sys.argv or "--help" in sys.argv:
        print_help()
        sys.exit(0)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--lang", choices=["zh", "en"], help="Language override (zh/en)")
    common.add_argument("--yes", "-y", action="store_true", help="Auto-confirm prompts where safe")
    common.add_argument("--dry-run", action="store_true", help="Print actions without executing")
    common.add_argument("--debug", action="store_true", help="Show stack traces and debug info")

    parser = argparse.ArgumentParser(description="GWT: Git Worktree Manager", add_help=False, parents=[common])
    subparsers = parser.add_subparsers(dest="command")

    p_comp = subparsers.add_parser("__complete", parents=[common])
    # New (robust) style: supports values like "--" without argparse swallowing them.
    p_comp.add_argument("--cmd", dest="comp_cmd_opt")
    p_comp.add_argument("--cur", dest="cur_opt")
    p_comp.add_argument("--prev", dest="prev_opt")
    # Backward-compatible positional style (used by older wrappers)
    p_comp.add_argument("comp_cmd", nargs="?", default="gwt")
    p_comp.add_argument("cur", nargs="?", default="")
    p_comp.add_argument("prev", nargs="?", default="")
    p_comp.set_defaults(func=cmd_completion)

    # Build subcommands from registry.
    for spec in iter_commands():
        if spec.name == "help":
            p_help = subparsers.add_parser("help", parents=[common])
            p_help.set_defaults(func=_cmd_help)
            continue

        p = subparsers.add_parser(spec.name, aliases=list(spec.aliases), parents=[common])

        # Special-case review: needs a mutually exclusive group for targets.
        if spec.name == "review":
            for arg in spec.args:
                p.add_argument(*arg.args, **arg.kwargs)

            group = p.add_mutually_exclusive_group()
            group.add_argument("--staged", "-s", action="store_true", help="Review staged changes")
            group.add_argument("--last", "-l", action="store_true", help="Review last commit (HEAD)")
            group.add_argument("--commit", "-c", metavar="SHA", help="Review specific commit vs HEAD")
            group.add_argument("--branch", "-b", metavar="BRANCH", help="Review branch vs HEAD")
        else:
            for arg in spec.args:
                p.add_argument(*arg.args, **arg.kwargs)

        if spec.func:
            p.set_defaults(func=spec.func)

    try:
        args = parser.parse_args()
    except Exception:
        print_help()
        sys.exit(1)

    if getattr(args, "lang", None):
        set_language(args.lang)

    if getattr(args, "debug", False):
        os.environ["GWT_DEBUG"] = "1"

    if not args.command:
        print_help()
        return

    try:
        if hasattr(args, "func"):
            rc = args.func(args)
            if isinstance(rc, int):
                sys.exit(rc)
            sys.exit(0)
        print_help()
        sys.exit(1)
    except GWTError as e:
        print_colored(str(e), "31")
        if getattr(args, "debug", False):
            traceback.print_exc()
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception:
        print_colored(t("generic.internal_error"), "31")
        if getattr(args, "debug", False):
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
