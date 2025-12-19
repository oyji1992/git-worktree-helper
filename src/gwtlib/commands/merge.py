# -*- coding: utf-8 -*-
"""GWT Merge/Commit Commands"""

import os
import shutil
import subprocess

from gwtlib.i18n import t
from gwtlib.config import detect_available_tools, get_effective_config
from gwtlib.utils import git_output, print_colored


def has_uncommitted_changes(path=None):
    cmd = ["git", "status", "--porcelain"]
    if path:
        cmd = ["git", "-C", path, "status", "--porcelain"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return bool(result.stdout.strip())


def get_all_branches():
    output = git_output(["branch", "-a", "--format=%(refname:short)"])
    if not output:
        return []

    branches = []
    for line in output.splitlines():
        branch = line.strip()
        if "HEAD" in branch:
            continue
        if branch.startswith("origin/"):
            branch = branch[7:]
        if branch and branch not in branches:
            branches.append(branch)
    return branches


def select_branch_fzf(prompt, exclude=None):
    branches = get_all_branches()
    if exclude:
        branches = [b for b in branches if b != exclude]

    if not branches:
        print_colored(t("worktree.no_branches"), "31")
        return None

    if shutil.which("fzf"):
        proc = subprocess.Popen(
            ["fzf", "--height", "40%", "--reverse", "--prompt", f"{prompt} > "],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
        stdout, _ = proc.communicate(input="\n".join(branches))
        return stdout.strip() if stdout.strip() else None

    print(f"📋 {prompt}:")
    for i, branch in enumerate(branches):
        print(f"  {i+1}. {branch}")
    print(f"\n{t('generic.tip_install_fzf')}")
    try:
        choice = input(f"Select number (1-{len(branches)}): ")
        idx = int(choice) - 1
        if 0 <= idx < len(branches):
            return branches[idx]
    except (ValueError, EOFError):
        pass
    return None


def has_merge_conflicts():
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


def get_conflicted_files():
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        return result.stdout.strip().split("\n")
    return []


def open_merge_tool(tool, files=None):
    if tool == "lazygit":
        subprocess.run(["lazygit"])
    elif tool == "gitui":
        subprocess.run(["gitui"])
    elif tool == "cursor":
        if files:
            for f in files:
                subprocess.run(["cursor", "--wait", f])
        else:
            subprocess.run(["cursor", "."])
    elif tool == "code":
        if files:
            for f in files:
                subprocess.run(["code", "--wait", f])
        else:
            subprocess.run(["code", "."])
    elif tool == "p4merge":
        subprocess.run(["git", "mergetool", "--tool=p4merge"])
    elif tool == "meld":
        subprocess.run(["git", "mergetool", "--tool=meld"])
    elif tool == "kdiff3":
        subprocess.run(["git", "mergetool", "--tool=kdiff3"])
    else:
        subprocess.run(["git", "mergetool"])


def handle_merge_conflicts(config):
    while has_merge_conflicts():
        conflicted = get_conflicted_files()
        print_colored(t("merge.conflicts_detected", n=len(conflicted)), "33")
        for f in conflicted:
            print(f"   • {f}")
        
        print()
        print_colored(t("merge.choose_action"), "36")
        print(t("merge.action1"))
        print(t("merge.action2"))
        print(t("merge.action3"))
        print(t("merge.action4"))
        
        try:
            choice = input(t("merge.select_1_4")).strip()
        except (EOFError, KeyboardInterrupt):
            choice = "4"
        
        if choice == "1":
            print_colored(t("merge.recheck"), "90")
            continue
        if choice == "2":
            merge_tool = config.get("merge", {}).get("tool", "lazygit")
            available = detect_available_tools().get("mergeTools", {})
            
            if available.get(merge_tool):
                print_colored(t("merge.opening", tool=merge_tool), "36")
                open_merge_tool(merge_tool, conflicted)
            else:
                priority = config.get("merge", {}).get("toolPriority", [])
                for tool in priority:
                    if available.get(tool):
                        print_colored(t("merge.opening_fallback", tool=tool), "36")
                        open_merge_tool(tool, conflicted)
                        break
                else:
                    print_colored(t("merge.no_merge_tool"), "31")
        elif choice == "3":
            if shutil.which("lazygit"):
                print_colored(t("merge.opening", tool="lazygit"), "36")
                subprocess.run(["lazygit"])
            else:
                print_colored(t("merge.lazygit_missing"), "31")
        elif choice == "4":
            print_colored(t("merge.aborting"), "33")
            subprocess.run(["git", "merge", "--abort"])
            return False

    return True


def cmd_merge(args):
    config = get_effective_config()
    auto_yes = bool(getattr(args, "yes", False) or getattr(args, "dry_run", False))
    
    if has_uncommitted_changes():
        print_colored(t("merge.uncommitted"), "31")
        print_colored(t("merge.uncommitted_tip"), "90")
        return
    
    print_colored(t("merge.title"), "36", bold=True)
    print_colored("=" * 40, "36")
    print()
    
    print_colored(t("merge.select_source"), "33")
    source = select_branch_fzf(t("merge.source_prompt"))
    if not source:
        print(t("generic.cancelled"))
        return

    print(f"   Selected: {source}")
    print()

    current_branch = git_output(["branch", "--show-current"]).strip()
    print_colored(t("merge.select_target"), "33")
    print_colored(t("merge.current_branch", branch=current_branch), "90")
    target = select_branch_fzf(t("merge.target_prompt"), exclude=source)
    if not target:
        print(t("generic.cancelled"))
        return

    print(f"   Selected: {target}")
    print()

    print_colored(t("merge.confirm", source=source, target=target), "33")
    if auto_yes:
        confirm = "y"
    else:
        try:
            confirm = input(t("merge.continue_prompt")).strip().lower()
        except EOFError:
            confirm = ""
    
    if confirm != "y":
        print(t("generic.cancelled"))
        return

    if getattr(args, "dry_run", False):
        print_colored(t("generic.dry_run"), "33")
        if current_branch != target:
            print_colored(t("generic.would_run", cmd=f"git checkout {target}"), "90")
        print_colored(t("generic.would_run", cmd=f"git merge {source}"), "90")
        return
    
    if current_branch != target:
        print_colored(t("merge.checkout", branch=target), "36")
        result = subprocess.run(["git", "checkout", target], capture_output=True, text=True)
        if result.returncode != 0:
            print_colored(t("merge.checkout_failed", branch=target), "31")
            print(result.stderr)
            return
    
    print_colored(t("merge.merging", source=source, target=target), "36")
    result = subprocess.run(["git", "merge", source], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout)
        print_colored(t("merge.ok"), "32")
    else:
        print(result.stdout)
        if has_merge_conflicts():
            if not handle_merge_conflicts(config):
                print_colored(t("merge.aborted"), "31")
                return
            
            if not has_merge_conflicts():
                print_colored(t("merge.all_resolved"), "32")
                print_colored(t("merge.completing"), "90")
                subprocess.run(["git", "commit", "--no-edit"])
                print_colored(t("merge.ok"), "32")
        else:
            print_colored(t("merge.failed"), "31")
            print(result.stderr)

    if not os.path.exists(".gitmodules"):
        return

    print()
    print_colored(t("merge.submodules_check"), "36")
    sm_output = git_output(["submodule", "foreach", "--recursive", "--quiet", "echo $path"])
    if not sm_output:
        return

    for sm_path in sm_output.splitlines():
        if not sm_path.strip():
            continue

        sm_conflicts = subprocess.run(
            ["git", "-C", sm_path, "diff", "--name-only", "--diff-filter=U"],
            capture_output=True,
            text=True,
        )

        if sm_conflicts.stdout.strip():
            print_colored(t("merge.submodule_has_conflicts", path=sm_path), "33")
            print_colored(t("merge.submodule_enter"), "90")

            original_dir = os.getcwd()
            os.chdir(sm_path)

            if not handle_merge_conflicts(config):
                os.chdir(original_dir)
                print_colored(t("merge.submodule_aborted"), "31")
                continue
            
            os.chdir(original_dir)
            print_colored(t("merge.submodule_resolved", path=sm_path), "32")


def cmd_commit(args):
    config = get_effective_config()
    git_tool = config.get("gitTool", "lazygit")
    available = detect_available_tools().get("mergeTools", {})

    print_colored(t("commit.title"), "36", bold=True)
    print()
    
    if not has_uncommitted_changes():
        print_colored(t("commit.no_changes"), "32")
        return
    
    print_colored(t("commit.status"), "36")
    subprocess.run(["git", "status", "-s"])
    print()
    
    if available.get(git_tool):
        print_colored(t("commit.launching", tool=git_tool), "36")
        subprocess.run([git_tool])
        return
    
    for tool in ["lazygit", "gitui"]:
        if available.get(tool):
            print_colored(t("commit.launching_fallback", tool=tool), "36")
            subprocess.run([tool])
            return
    
    print_colored(t("commit.no_tui"), "33")
    print_colored(t("commit.no_tui_tip"), "90")
    print()
    
    try:
        stage_all = input(t("commit.stage_all")).strip().lower()
    except EOFError:
        stage_all = ""
    
    if stage_all == "y":
        subprocess.run(["git", "add", "-A"])
    
    try:
        msg = input(t("commit.message")).strip()
    except EOFError:
        msg = ""
    
    if not msg:
        print(t("generic.cancelled"))
        return

    result = subprocess.run(["git", "commit", "-m", msg], capture_output=True, text=True)
    if result.returncode == 0:
        print_colored(t("commit.ok"), "32")
        print(result.stdout)
    else:
        print_colored(t("commit.failed"), "31")
        print(result.stderr)
