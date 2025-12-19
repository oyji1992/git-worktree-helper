# -*- coding: utf-8 -*-
"""GWT Worktree Commands

Commands:
- list / ls
- new / add / create / (remote / rt kept as parser alias)
- remove / rm / del
- cd / jump
- prune
"""

import os
import shutil
import subprocess

from gwtlib.i18n import t
from gwtlib.config import get_effective_config
from gwtlib.utils import (
    ensure_worktree_gitignore,
    get_branch_worktree,
    get_main_worktree,
    git_output,
    is_inside_worktree,
    print_colored,
    request_cd,
    run_cmd,
)


def cmd_list(args):
    subprocess.run(["git", "worktree", "list"])


def _interactive_select_branch():
    """
    Interactive branch selection for `gwt new`.
    Returns (branch_name, is_remote) tuple.

    - branch_name: selected branch name (without origin/ prefix if remote)
    - is_remote: True if selected from remote branches
    """
    print_colored(t("worktree.fetch_remote"), "36")
    run_cmd(["git", "fetch", "--all", "--prune"])

    local_output = git_output(["branch", "--format=%(refname:short)"])
    local_branches = local_output.splitlines() if local_output else []

    remote_output = git_output(["branch", "-r", "--format=%(refname:short)"])
    remote_branches = []
    if remote_output:
        for branch in remote_output.splitlines():
            if not branch.endswith("/HEAD"):
                remote_branches.append(branch)

    if not local_branches and not remote_branches:
        print_colored(t("worktree.no_branches"), "31")
        return None, False

    options = []
    branch_map = {}

    for branch in local_branches:
        display = f"[L] {branch}"
        options.append(display)
        branch_map[display] = (branch, False)

    for remote in remote_branches:
        if remote.startswith("origin/"):
            local_name = remote[7:]
        else:
            parts = remote.split("/", 1)
            local_name = parts[1] if len(parts) > 1 else remote

        if local_name in local_branches:
            continue

        display = f"[R] {remote}"
        options.append(display)
        branch_map[display] = (local_name, True)

    if not options:
        print_colored(t("worktree.no_branches_available"), "31")
        return None, False

    selected = None

    if shutil.which("fzf"):
        proc = subprocess.Popen(
            [
                "fzf",
                "--height",
                "40%",
                "--reverse",
                "--prompt",
                t("worktree.fzf_prompt_branch"),
                "--ansi",
                "--header",
                t("worktree.fzf_header_branches"),
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
        stdout, _ = proc.communicate(input="\n".join(options))
        selected = stdout.strip()
        if not selected:
            print(t("generic.cancelled"))
            return None, False
    else:
        print(t("worktree.branches_title"))
        print(t("worktree.branches_header"))
        for i, opt in enumerate(options):
            print(f"  {i+1}. {opt}")
        print(f"\n{t('generic.tip_install_fzf')}")
        print(t("worktree.branches_tip"))

        try:
            choice = input(t("generic.select_number_or_name", n=len(options))).strip()
            if not choice:
                print(t("generic.cancelled"))
                return None, False

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    selected = options[idx]
                else:
                    print_colored(t("generic.invalid_selection"), "31")
                    return None, False
            except ValueError:
                return choice, False
        except EOFError:
            print(t("generic.cancelled"))
            return None, False

    if selected in branch_map:
        return branch_map[selected]

    return None, False


def cmd_new(args):
    branch_name = args.branch if getattr(args, "branch", None) else None
    base_branch = args.base if getattr(args, "base", None) else "HEAD"
    auto_yes = bool(getattr(args, "yes", False) or getattr(args, "dry_run", False))

    repo_root = get_main_worktree()
    if not repo_root:
        print_colored(t("generic.not_git_repo"), "31")
        return

    if not branch_name:
        branch_name, _is_remote = _interactive_select_branch()
        if not branch_name:
            return

    config = get_effective_config()
    worktree_dir_name = config.get("worktreeDir", ".worktree")

    ensure_worktree_gitignore(repo_root, worktree_dir_name)

    safe_branch_name = branch_name.replace("/", "-")
    worktree_dir = os.path.join(repo_root, worktree_dir_name)
    new_path = os.path.join(worktree_dir, safe_branch_name)

    print_colored(
        t("worktree.create_worktree", path=new_path, branch=branch_name),
        "36",
    )

    local_branch_exists = (
        run_cmd(["git", "rev-parse", "--verify", branch_name], capture_output=True)
        is not None
    )

    remote_branch = f"origin/{branch_name}"
    remote_branch_exists = (
        run_cmd(["git", "rev-parse", "--verify", remote_branch], capture_output=True)
        is not None
    )

    cmd = ["git", "worktree", "add"]
    if local_branch_exists:
        existing_worktree = get_branch_worktree(branch_name)
        if existing_worktree:
            print_colored(t("worktree.branch_used", branch=branch_name), "33")
            print_colored(f"   {existing_worktree}", "90")
            print_colored(t("worktree.you_can"), "36")
            print(t("worktree.you_can_1"))
            print(t("worktree.you_can_2"))
            return

        print_colored(t("worktree.branch_exists_local", branch=branch_name), "90")
        cmd.extend([new_path, branch_name])
    elif remote_branch_exists:
        print_colored(t("worktree.found_remote_branch", branch=remote_branch), "36")
        if auto_yes:
            choice = "y"
        else:
            try:
                choice = input(t("worktree.use_remote_prompt")).strip().lower()
            except EOFError:
                choice = ""

        if choice in ["", "y", "yes"]:
            print_colored(
                t("worktree.create_tracking", branch=branch_name, remote=remote_branch),
                "90",
            )
            cmd.extend(["-b", branch_name, new_path, remote_branch])
        else:
            print_colored(t("worktree.create_from_base", branch=branch_name, base=base_branch), "90")
            cmd.extend(["-b", branch_name, new_path, base_branch])
    else:
        print_colored(
            t("worktree.branch_not_found_create", branch=branch_name, base=base_branch),
            "90",
        )
        cmd.extend(["-b", branch_name, new_path, base_branch])

    if getattr(args, "dry_run", False):
        print_colored(t("generic.dry_run"), "33")
        print_colored(t("generic.would_run", cmd=" ".join(cmd)), "90")
        print_colored(t("generic.would_cd", path=new_path), "90")
        return

    if not run_cmd(cmd):
        print_colored(t("worktree.create_failed"), "31")
        return

    print_colored(t("worktree.created_ok"), "32")
    request_cd(new_path)
    os.chdir(new_path)

    if not os.path.exists(".gitmodules"):
        return

    print_colored(t("worktree.submodules_detected"), "36")
    run_cmd(["git", "submodule", "update", "--init", "--force"])

    print_colored(t("worktree.sync_submodules"), "36")
    output = git_output(["submodule", "foreach", "--recursive", "--quiet", "echo $path"])
    if not output:
        return

    for sm_path in output.splitlines():
        if not sm_path.strip():
            continue

        sm_local_exists = (
            subprocess.run(
                ["git", "-C", sm_path, "rev-parse", "--verify", branch_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
            == 0
        )

        sm_remote_branch = f"origin/{branch_name}"
        sm_remote_exists = (
            subprocess.run(
                ["git", "-C", sm_path, "rev-parse", "--verify", sm_remote_branch],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
            == 0
        )

        if sm_local_exists:
            print(t("worktree.submodule_checkout_local", path=sm_path, branch=branch_name))
            run_cmd(["git", "-C", sm_path, "checkout", branch_name])
        elif sm_remote_exists:
            print_colored(
                t("worktree.submodule_found_remote", path=sm_path, remote=sm_remote_branch),
                "36",
            )
            if auto_yes:
                choice = "y"
            else:
                try:
                    choice = input(t("worktree.submodule_use_remote_prompt", path=sm_path)).strip().lower()
                except EOFError:
                    choice = ""

            if choice in ["", "y", "yes"]:
                print(t("worktree.submodule_create_tracking", path=sm_path, remote=sm_remote_branch))
                run_cmd(
                    ["git", "-C", sm_path, "checkout", "-b", branch_name, sm_remote_branch]
                )
            else:
                print(t("worktree.submodule_create_local", path=sm_path, branch=branch_name))
                run_cmd(["git", "-C", sm_path, "checkout", "-b", branch_name])
        else:
            print(t("worktree.submodule_create_local", path=sm_path, branch=branch_name))
            run_cmd(["git", "-C", sm_path, "checkout", "-b", branch_name])


def cmd_remove(args):
    main_worktree = get_main_worktree()
    current_path = os.getcwd()
    target_path = ""
    target_key = args.target

    if not is_inside_worktree():
        print_colored(t("generic.not_git_dir"), "31")
        return

    wt_list = git_output(["worktree", "list"])
    if not wt_list:
        print_colored(t("worktree.no_worktrees"), "31")
        return

    worktrees = []
    for line in wt_list.splitlines():
        path = line.split()[0]
        if path != main_worktree:
            worktrees.append(path)

    if not worktrees:
        print_colored(t("worktree.no_removable"), "33")
        return

    if not target_key:
        if shutil.which("fzf"):
            proc = subprocess.Popen(
                [
                    "fzf",
                    "--height",
                    "40%",
                    "--reverse",
                    "--prompt",
                    t("worktree.fzf_prompt_remove"),
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
            )
            stdout, _ = proc.communicate(input="\n".join(worktrees))
            target_path = stdout.strip()
            if not target_path:
                print(t("generic.cancelled"))
                return
        else:
            print(t("worktree.worktrees_title"))
            for i, wt in enumerate(worktrees):
                print(f"  {i+1}. {wt}")
            print(f"\n{t('generic.tip_install_fzf')}")

            try:
                choice = input(t("worktree.remove_select_prompt", n=len(worktrees)))
                idx = int(choice) - 1
                if 0 <= idx < len(worktrees):
                    target_path = worktrees[idx]
                else:
                    print_colored(t("generic.invalid_selection"), "31")
                    return
            except (ValueError, EOFError):
                print(t("generic.cancelled"))
                return
    else:
        for line in wt_list.splitlines():
            path = line.split()[0]
            if target_key in path:
                target_path = path
                break

        if not target_path:
            print_colored(t("worktree.remove_no_match", key=target_key), "31")
            return

        if target_path == main_worktree:
            print_colored(t("worktree.remove_main_forbidden", path=main_worktree), "33")
            return

    normalized_current = os.path.normpath(os.path.normcase(current_path))
    normalized_target = os.path.normpath(os.path.normcase(target_path))
    normalized_main = os.path.normpath(os.path.normcase(main_worktree))

    is_inside_target = (
        normalized_current == normalized_target
        or normalized_current.startswith(normalized_target + os.sep)
    )

    if is_inside_target:
        print_colored(t("worktree.remove_inside_warn"), "33")
        print_colored(t("worktree.remove_switching"), "36")
        print_colored(t("worktree.remove_rerun"), "90")
        request_cd(main_worktree)
        return

    print_colored(t("worktree.remove_prepare", path=target_path), "33")

    auto_yes = bool(getattr(args, "yes", False) or getattr(args, "dry_run", False))
    if not auto_yes:
        try:
            confirm = input(t("worktree.remove_confirm"))
        except EOFError:
            confirm = "n"

        if confirm.lower() != "y":
            print(t("generic.cancelled"))
            return

    if getattr(args, "dry_run", False):
        print_colored(t("generic.dry_run"), "33")
        print_colored(t("generic.would_run", cmd=f"git worktree remove --force {target_path}"), "90")
        print_colored(t("generic.would_run", cmd="git worktree prune"), "90")
        return

    if normalized_current != normalized_main:
        print_colored("📂 Switching to main worktree...", "90")
        os.chdir(main_worktree)

    if run_cmd(["git", "worktree", "remove", "--force", target_path]):
        run_cmd(["git", "worktree", "prune"])
        print_colored(t("worktree.removed_ok"), "32")
    else:
        print_colored(t("worktree.remove_failed"), "31")


def cmd_prune(args):
    print_colored(t("worktree.prune_start"), "36")
    if getattr(args, "dry_run", False):
        print_colored(t("generic.dry_run"), "33")
        print_colored(t("generic.would_run", cmd="git worktree prune -v"), "90")
        return
    if run_cmd(["git", "worktree", "prune", "-v"]):
        print_colored(t("worktree.prune_ok"), "32")
    else:
        print_colored(t("worktree.prune_failed"), "31")


def cmd_cd(args):
    wt_output = git_output(["worktree", "list"])
    if not wt_output:
        return

    worktrees = [line.split()[0] for line in wt_output.splitlines()]

    if shutil.which("fzf"):
        proc = subprocess.Popen(
            ["fzf", "--height", "40%", "--reverse", "--prompt", t("worktree.fzf_prompt_worktree")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
        stdout, _ = proc.communicate(input="\n".join(worktrees))
        target = stdout.strip()
        if target:
            if getattr(args, "dry_run", False):
                print_colored(t("generic.dry_run"), "33")
                print_colored(t("generic.would_cd", path=target), "90")
            else:
                request_cd(target)
    else:
        print(t("worktree.worktrees_title"))
        for i, wt in enumerate(worktrees):
            print(f"  {i+1}. {wt}")
        print(f"\n{t('generic.tip_install_fzf')}")

        try:
            choice = input(t("worktree.cd_prompt", n=len(worktrees)))
            idx = int(choice) - 1
            if 0 <= idx < len(worktrees):
                if getattr(args, "dry_run", False):
                    print_colored(t("generic.dry_run"), "33")
                    print_colored(t("generic.would_cd", path=worktrees[idx]), "90")
                else:
                    request_cd(worktrees[idx])
            else:
                print(t("worktree.invalid_selection"))
        except ValueError:
            pass
