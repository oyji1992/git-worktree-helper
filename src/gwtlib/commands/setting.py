# -*- coding: utf-8 -*-
"""GWT Setting Command"""

import json
import os
import shutil
import subprocess

from gwtlib.i18n import t
from gwtlib.config import (
    DEFAULT_CONFIG,
    detect_available_tools,
    detect_submodules,
    get_effective_config,
    get_global_config_path,
    get_repo_config_path,
    load_config,
    save_config,
)
from gwtlib.utils import print_colored


def _select_branch_for_setting(current_branch, prompt_text="Select branch", cwd=None):
    """
    Interactive branch selection for settings.
    Returns selected branch name or None if cancelled.

    Args:
        current_branch: current branch value to show as default
        prompt_text: prompt text
        cwd: working directory for git commands (e.g. submodule path)
    """
    git_cmd = ["git"]
    if cwd:
        git_cmd.extend(["-C", cwd])

    result = subprocess.run(
        git_cmd + ["branch", "--format=%(refname:short)"],
        capture_output=True,
        text=True,
    )
    branches = result.stdout.strip().splitlines() if result.returncode == 0 else []

    if not branches:
        try:
            new_val = input(t("setting.branch_enter_name", branch=current_branch)).strip()
        except EOFError:
            new_val = ""
        return new_val if new_val else None

    if current_branch in branches:
        branches.remove(current_branch)
    branches.insert(0, current_branch)

    options = []
    for b in branches:
        options.append(f"{b} (current)" if b == current_branch else b)

    if shutil.which("fzf"):
        proc = subprocess.Popen(
            [
                "fzf",
                "--height",
                "40%",
                "--reverse",
                "--prompt",
                f"{prompt_text} > ",
                "--ansi",
                "--header",
                f"Current: {current_branch}",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
        stdout, _ = proc.communicate(input="\n".join(options))
        selected = stdout.strip()
        if not selected:
            return None
        if selected.endswith(" (current)"):
            selected = selected[:-10]
        return selected

    print(t("setting.branch_available"))
    for i, opt in enumerate(options):
        print(f"     [{i+1}] {opt}")
    print()

    try:
        choice = input(t("setting.branch_select_or_enter", n=len(options))).strip()
    except EOFError:
        choice = ""

    if not choice:
        return None

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(options):
            return branches[idx]
        print_colored(t("generic.invalid_selection"), "31")
        return None
    except ValueError:
        return choice


def cmd_setting(args):
    is_global = args.is_global

    if args.show:
        config = get_effective_config() if not is_global else load_config(is_global=True)
        print_colored(t("setting.current_config"), "36", bold=True)
        if is_global:
            print_colored(t("setting.global_path", path=get_global_config_path()), "90")
        else:
            print_colored(t("setting.effective"), "90")
        print()
        print(json.dumps(config, indent=2, ensure_ascii=False))
        return

    if args.reset:
        config_path = get_global_config_path() if is_global else get_repo_config_path()
        if config_path and config_path.exists():
            try:
                confirm = input(t("setting.reset_confirm", path=config_path)).strip().lower()
            except EOFError:
                confirm = ""
            if confirm == "y":
                config_path.unlink()
                print_colored(t("setting.reset_ok"), "32")
            else:
                print(t("generic.cancelled"))
        else:
            print_colored(t("setting.no_config_file"), "33")
        return

    scope_label = t("setting.scope.global") if is_global else t("setting.scope.repo")
    config_path = get_global_config_path() if is_global else get_repo_config_path()
    if not config_path:
        print_colored(t("setting.not_git_repo"), "31")
        return

    if args.init:
        config = {}
        print_colored(t("setting.init_title", scope=scope_label), "36", bold=True)
    else:
        config = load_config(is_global=is_global)
        print_colored(t("setting.title", scope=scope_label), "36", bold=True)

    print_colored("=" * 45, "36")
    print()

    print_colored(t("setting.detecting"), "90")
    available_tools = detect_available_tools()
    config["availableTools"] = available_tools

    print_colored(t("setting.review_tools"), "36")
    for tool, available in available_tools["reviewTools"].items():
        status = "✓" if available else "✗"
        color = "32" if available else "31"
        print_colored(f"   {tool}: {status}", color)

    print_colored(t("setting.cli_tools"), "36")
    for tool, available in available_tools["cliTools"].items():
        status = "✓" if available else "✗"
        color = "32" if available else "31"
        print_colored(f"   {tool}: {status}", color)
    print()

    current_main = config.get("mainBranch", DEFAULT_CONFIG["mainBranch"])
    print_colored(t("setting.main_branch"), "33")
    print(t("setting.current", value=current_main))
    print(t("setting.select_tip"))

    selected = _select_branch_for_setting(current_main, t("setting.main_branch_prompt"))
    if selected:
        config["mainBranch"] = selected
        if selected != current_main:
            print_colored(t("setting.changed_to", value=selected), "32")
    elif "mainBranch" not in config:
        config["mainBranch"] = current_main
    print()

    current_wt = config.get("worktreeDir", DEFAULT_CONFIG["worktreeDir"])
    print_colored(t("setting.worktree_dir"), "33")
    print(t("setting.current", value=current_wt))
    print(t("setting.worktree_dir_tip"))
    try:
        new_val = input(t("setting.enter_new")).strip()
    except EOFError:
        new_val = ""
    if new_val:
        config["worktreeDir"] = new_val
    elif "worktreeDir" not in config:
        config["worktreeDir"] = current_wt
    print()

    # UI Language
    config.setdefault("ui", {})
    current_lang = config["ui"].get("lang", DEFAULT_CONFIG.get("ui", {}).get("lang", "auto"))
    print_colored(t("setting.ui_lang"), "33")
    print(t("setting.current", value=current_lang))
    print(t("setting.ui_lang_tip"))
    print(f"   [1] {t('setting.ui_lang_auto')}")
    print(f"   [2] {t('setting.ui_lang_zh')}")
    print(f"   [3] {t('setting.ui_lang_en')}")
    try:
        choice = input(t("setting.ui_lang_prompt")).strip()
    except EOFError:
        choice = ""
    if choice in ("1", "2", "3"):
        new_lang = {"1": "auto", "2": "zh", "3": "en"}[choice]
        config["ui"]["lang"] = new_lang
        if new_lang != current_lang:
            print_colored(t("setting.changed_to", value=new_lang), "32")
    elif "lang" not in config["ui"]:
        config["ui"]["lang"] = current_lang
    print()

    available_review_tools = [t for t, v in available_tools["reviewTools"].items() if v]
    if available_review_tools:
        current_tool = config.get("review", {}).get(
            "defaultTool", DEFAULT_CONFIG["review"]["defaultTool"]
        )
        print_colored(t("setting.default_review_tool"), "33")
        print(t("setting.available"), end=" ")
        for i, tool in enumerate(["claude", "codex", "gemini"]):
            available = available_tools["reviewTools"].get(tool, False)
            status = "✓" if available else "✗"
            selected = " (current)" if tool == current_tool else ""
            print(f"[{i+1}] {tool} {status}{selected}", end="  ")
        print()
        try:
            choice = input(t("setting.select_1_3")).strip()
        except EOFError:
            choice = ""
        if choice in ["1", "2", "3"]:
            tools = ["claude", "codex", "gemini"]
            selected_tool = tools[int(choice) - 1]
            config.setdefault("review", {})
            config["review"]["defaultTool"] = selected_tool
        print()

    if os.name == "nt":
        current_wsl = config.get("review", {}).get("useWsl", DEFAULT_CONFIG["review"]["useWsl"])
        wsl_available = shutil.which("wsl") is not None
        print_colored(t("setting.wsl_mode"), "33")
        print(t("setting.wsl_current", value=("Enabled" if current_wsl else "Disabled")))
        print(t("setting.wsl_available", value=("✓" if wsl_available else "✗")))
        print(t("setting.wsl_tip"))
        try:
            choice = input(t("setting.wsl_toggle")).strip().lower()
        except EOFError:
            choice = ""
        if choice in ["y", "yes"]:
            config.setdefault("review", {})
            config["review"]["useWsl"] = not current_wsl
            new_status = "Enabled" if not current_wsl else "Disabled"
            print_colored(
                t("setting.wsl_to", value=new_status),
                "32" if not current_wsl else "33",
            )
        print()

    if not is_global:
        print_colored(t("setting.submodule_settings"), "33")
        detected_submodules = detect_submodules()
        if detected_submodules:
            print(t("setting.submodule_found", n=len(detected_submodules)))
            existing_sm_config = {sm["path"]: sm for sm in config.get("submodules", [])}

            for i, sm in enumerate(detected_submodules):
                existing = existing_sm_config.get(sm["path"], {})
                main_branch = existing.get("mainBranch", sm["mainBranch"])
                print(f"   [{i+1}] {sm['path']} (main branch: {main_branch})")

            try:
                choice = input(t("setting.submodule_select")).strip()
            except EOFError:
                choice = ""

            if choice.isdigit() and 1 <= int(choice) <= len(detected_submodules):
                idx = int(choice) - 1
                sm = detected_submodules[idx]
                existing = existing_sm_config.get(sm["path"], {})
                current_branch = existing.get("mainBranch", sm["mainBranch"])
                
                print(t("setting.submodule_editing", path=sm["path"]))
                print(t("setting.submodule_current_main", branch=current_branch))
                print(t("setting.submodule_tip"))
                
                new_branch = _select_branch_for_setting(
                    current_branch,
                    t("setting.submodule_main_branch_prompt", path=sm["path"]),
                    cwd=sm["path"],
                )

                if new_branch:
                    config.setdefault("submodules", [])

                    found = False
                    for item in config["submodules"]:
                        if item["path"] == sm["path"]:
                            item["mainBranch"] = new_branch
                            found = True
                            break
                    if not found:
                        config["submodules"].append(
                            {"path": sm["path"], "mainBranch": new_branch}
                        )

                    if new_branch != current_branch:
                        print_colored(t("setting.changed_to", value=new_branch), "32")
        else:
            print(t("setting.no_submodules"))
        print()
    
    if save_config(config, is_global=is_global):
        print_colored(t("setting.saved_to", path=config_path), "32")
    else:
        print_colored(t("setting.save_failed"), "31")
