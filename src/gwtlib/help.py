# -*- coding: utf-8 -*-
"""GWT Help Module

This module provides the help message display functionality.
"""

from gwtlib.i18n import t
from gwtlib.registry import visible_commands
from gwtlib.utils import print_colored


def print_help():
    """Print a pretty, custom help message."""
    print("")
    print_colored(t("help.title"), "36", bold=True)
    print(t("help.subtitle_1"))
    print(t("help.subtitle_2"))
    print("")

    print_colored(t("help.usage"), "33", bold=True)
    print(t("help.usage_line"))
    print("")

    print_colored(t("help.core"), "33", bold=True)
    for spec in visible_commands():
        if spec.name in ("review", "help"):
            continue
        alias = spec.aliases[0] if spec.aliases else ""
        desc = t(spec.help_key) if spec.help_key else ""
        alias_str = f", {alias}" if alias else "    "
        print(f"  \033[36m{spec.name:<12}\033[0m \033[90m{alias_str:<6}\033[0m {desc}")

    print("")
    print_colored(t("help.ai"), "33", bold=True)
    print(t("help.review_line"))

    print(t("help.review_target"))
    print(t("help.review_target_staged"))
    print(t("help.review_target_last"))
    print(t("help.review_target_commit"))
    print(t("help.review_target_branch"))

    print(t("help.review_tool"))
    print(t("help.review_tool_tool"))

    print("")
    print_colored(t("help.new_detail"), "33", bold=True)
    print(t("help.new_detail_1"))
    print(t("help.new_detail_2"))
    print(t("help.new_detail_3"))

    print("")
    print_colored(t("help.setting_detail"), "33", bold=True)
    print(t("help.setting_detail_1"))
    print(t("help.setting_detail_2"))
    print(t("help.setting_detail_3"))
    print(t("help.setting_detail_4"))
    print(t("help.setting_detail_5"))

    print("")
    print_colored(t("help.examples"), "33", bold=True)

    print(t("help.ex1"))
    print("     \033[32m$ gwt new\033[0m")
    print("")

    print(t("help.ex2"))
    print("     \033[32m$ gwt new feature/login\033[0m")
    print("")

    print(t("help.ex3"))
    print("     \033[32m$ gwt new feature/new-ui develop\033[0m")
    print("")

    print(t("help.ex4"))
    print("     \033[32m$ gwt review\033[0m")
    print("")

    print(t("help.ex5"))
    print("     \033[32m$ gwt review -s -t gemini\033[0m")
    print("")

    print(t("help.ex6"))
    print("     \033[32m$ gwt setting\033[0m")
    print("")
