# -*- coding: utf-8 -*-
"""GWT Completion Module

This module handles auto-completion requests for shell integration.
"""
import os
from gwtlib.i18n import t
from gwtlib.registry import visible_commands
from gwtlib.utils import git_output


def _global_flags():
    return [
        f"--lang:{t('completion.global.lang')}",
        f"--yes:{t('completion.global.yes')}",
        f"-y:{t('completion.global.yes')}",
        f"--dry-run:{t('completion.global.dry_run')}",
        f"--debug:{t('completion.global.debug')}",
    ]


def _complete_commits(limit=50):
    out = git_output(["log", f"-n{limit}", "--pretty=format:%h"])
    if not out:
        return []
    return [f"{sha}:{t('completion.review.commit')}" for sha in out.splitlines() if sha.strip()]


def _complete_branches():
    out = git_output(["branch", "-a", "--format=%(refname:short)"])
    if not out:
        return []
    remotes_out = git_output(["remote"])
    remotes = {r.strip() for r in (remotes_out.splitlines() if remotes_out else []) if r.strip()}
    branches = []
    seen = set()
    for raw in out.splitlines():
        b = raw.strip()
        if not b or b.endswith("/HEAD"):
            continue
        if b.startswith("origin/"):
            b = b[7:]
        # Filter remote names like "origin"
        if b in remotes:
            continue
        if b not in seen:
            seen.add(b)
            branches.append(f"{b}:{t('completion.branch')}")
    return branches


def cmd_completion(args):
    """
    Handles auto-completion requests.
    Usage: gwt __complete <command> <current_word> [prev_word]
    """
    cmd = getattr(args, "comp_cmd_opt", None) or args.comp_cmd
    cur = getattr(args, "cur_opt", None)
    if cur is None:
        cur = args.cur
    prev = getattr(args, "prev_opt", None)
    if prev is None:
        prev = args.prev

    # Format: "value:description"
    options = []

    # Global option values
    if prev == "--lang":
        options = [
            f"zh:{t('setting.ui_lang_zh')}",
            f"en:{t('setting.ui_lang_en')}",
        ]
        matches = [opt for opt in options if opt.split(":")[0].startswith(cur)]
        print("\n".join(matches))
        return
    
    # Root level completion
    if cmd == "gwt":
        cmds = []
        for spec in visible_commands():
            if spec.name == "help":
                cmds.append(f"help:{t('completion.help')}")
                continue
            if spec.name == "review":
                cmds.append(f"review:{t('completion.review')}")
                for a in spec.aliases:
                    cmds.append(f"{a}:{t('completion.review')}")
                continue

            desc = t(spec.completion_key) if spec.completion_key else ""
            cmds.append(f"{spec.name}:{desc}")
            for a in spec.aliases:
                cmds.append(f"{a}:{desc}")
        options = cmds

        # Global options
        if cur.startswith("-"):
            options.extend(_global_flags())
        
    # 'new' command: complete branches (local + remote)
    elif cmd in ["new", "add", "create", "remote", "rt"]:
        # Get local and remote branches
        out = git_output(["branch", "-a", "--format=%(refname:short)"])
        if out:
            for line in out.splitlines():
                if not line.endswith("/HEAD"):
                    options.append(f"{line}:{t('completion.branch')}")

        if cur.startswith("-"):
            options.extend(_global_flags())

    # 'init' command
    elif cmd == "init":
        flags = [f"--shell:{t('completion.init.shell')}"]
        options = flags
        if prev == "--shell":
            options = [
                "zsh:zsh",
                "bash:bash",
                "powershell:powershell",
            ]
        if cur.startswith("-"):
            options.extend(_global_flags())

    # 'setting' command
    elif cmd in ["setting", "config"]:
        flags = [
            f"--global:{t('completion.setting.global')}",
            f"-g:{t('completion.setting.global')}",
            f"--show:{t('completion.setting.show')}",
            f"-s:{t('completion.setting.show')}",
            f"--init:{t('completion.setting.init')}",
            f"-i:{t('completion.setting.init')}",
            f"--reset:{t('completion.setting.reset')}",
            f"-r:{t('completion.setting.reset')}",
        ]
        options = flags
        if cur.startswith("-"):
            options.extend(_global_flags())

    # 'review' command
    elif cmd in ["review", "rv"]:
        if prev in ["-t", "--tool"]:
            options = [
                f"claude:{t('completion.review.tool.claude')}",
                f"codex:{t('completion.review.tool.codex')}",
                f"gemini:{t('completion.review.tool.gemini')}",
            ]
        elif prev in ["-c", "--commit"]:
            options = _complete_commits()
        elif prev in ["-b", "--branch"]:
            options = _complete_branches()
        else:
            flags = [
                f"--staged:{t('completion.review.staged')}",
                f"-s:{t('completion.review.staged')}",
                f"--last:{t('completion.review.last')}",
                f"-l:{t('completion.review.last')}",
                f"--commit:{t('completion.review.commit')}",
                f"-c:{t('completion.review.commit')}",
                f"--branch:{t('completion.review.branch')}",
                f"-b:{t('completion.review.branch')}",
                f"--tool:{t('completion.review.tool')}",
                f"-t:{t('completion.review.tool')}",
                f"--model:{t('completion.review.model')}",
                f"-m:{t('completion.review.model')}",
            ]
            options = flags
            if cur.startswith("-"):
                options.extend(_global_flags())
            
    # 'remove' or 'cd' command: complete worktrees
    elif cmd in ["remove", "rm", "del", "cd", "jump"]:
        out = git_output(["worktree", "list"])
        if out:
            # Format: "/path/to/wt  commit [branch]"
            for line in out.splitlines():
                parts = line.split()
                path = parts[0]
                branch = parts[2][1:-1] if len(parts) > 2 else "HEAD"
                
                # Full path
                options.append(f"{path}:{branch}")
                # Basename
                options.append(f"{os.path.basename(path)}:{branch}")

        if cur.startswith("-"):
            options.extend(_global_flags())

    # Filter by current word prefix
    matches = [opt for opt in options if opt.split(":")[0].startswith(cur)]
    print("\n".join(matches))
