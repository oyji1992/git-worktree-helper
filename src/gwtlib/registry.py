# -*- coding: utf-8 -*-
"""Command registry (single source of truth).

This module centralizes:
- command names + aliases
- argparse argument definitions
- command handlers
- help/completion description keys

Goal: keep `src/gwt.py`, help, and completion in sync by generating from registry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from gwtlib.commands.merge import cmd_commit, cmd_merge
from gwtlib.commands.init import cmd_init
from gwtlib.commands.review import cmd_review
from gwtlib.commands.setting import cmd_setting
from gwtlib.commands.status import cmd_status
from gwtlib.commands.update import cmd_update
from gwtlib.commands.worktree import cmd_cd, cmd_list, cmd_new, cmd_prune, cmd_remove


Handler = Callable[[Any], Any]


@dataclass(frozen=True)
class ArgSpec:
    args: Tuple[str, ...]
    kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CommandSpec:
    name: str
    aliases: Tuple[str, ...] = ()
    func: Optional[Handler] = None
    args: Tuple[ArgSpec, ...] = ()
    hidden: bool = False
    help_key: Optional[str] = None
    completion_key: Optional[str] = None


def iter_commands() -> List[CommandSpec]:
    # Note: keep __complete/help special handling in gwt.py.
    return [
        CommandSpec(
            name="init",
            func=cmd_init,
            help_key="help.cmd.init",
            completion_key="completion.init",
            args=(
                ArgSpec(("--shell",), {"choices": ["zsh", "bash", "powershell"], "help": "Output wrapper for a shell"}),
            ),
        ),
        CommandSpec(
            name="list",
            aliases=("ls",),
            func=cmd_list,
            help_key="help.cmd.list",
            completion_key="completion.list",
        ),
        CommandSpec(
            name="status",
            aliases=("st", "s"),
            func=cmd_status,
            help_key="help.cmd.status",
            completion_key="completion.status",
        ),
        CommandSpec(
            name="new",
            aliases=("add", "create"),
            func=cmd_new,
            help_key="help.cmd.new",
            completion_key="completion.new",
            args=(
                ArgSpec(("branch",), {"nargs": "?", "help": "Branch name (optional, interactive if omitted)"}),
                ArgSpec(("base",), {"nargs": "?", "help": "Base branch to create from (default: HEAD)"}),
            ),
        ),
        CommandSpec(
            name="remove",
            aliases=("rm", "del"),
            func=cmd_remove,
            help_key="help.cmd.remove",
            completion_key="completion.remove",
            args=(ArgSpec(("target",), {"nargs": "?"}),),
        ),
        CommandSpec(
            name="prune",
            func=cmd_prune,
            help_key="help.cmd.prune",
            completion_key="completion.prune",
        ),
        CommandSpec(
            name="cd",
            aliases=("jump",),
            func=cmd_cd,
            help_key="help.cmd.cd",
            completion_key="completion.cd",
        ),
        CommandSpec(
            name="update",
            func=cmd_update,
            help_key="help.cmd.update",
            completion_key="completion.update",
        ),
        CommandSpec(
            # Hidden alias for backward compatibility.
            name="remote",
            aliases=("rt",),
            func=cmd_new,
            hidden=True,
            args=(
                ArgSpec(("branch",), {"nargs": "?", "help": "Branch name (optional)"}),
                ArgSpec(("base",), {"nargs": "?", "help": "Base branch to create from (default: HEAD)"}),
            ),
        ),
        CommandSpec(
            name="merge",
            func=cmd_merge,
            help_key="help.cmd.merge",
            completion_key="completion.merge",
        ),
        CommandSpec(
            name="commit",
            aliases=("ci",),
            func=cmd_commit,
            help_key="help.cmd.commit",
            completion_key="completion.commit",
        ),
        CommandSpec(
            name="setting",
            aliases=("config",),
            func=cmd_setting,
            help_key="help.cmd.setting",
            completion_key="completion.setting",
            args=(
                ArgSpec(("--global", "-g"), {"dest": "is_global", "action": "store_true", "help": "Edit global config"}),
                ArgSpec(("--show", "-s"), {"action": "store_true", "help": "Show current config"}),
                ArgSpec(("--init", "-i"), {"action": "store_true", "help": "Initialize config with detection"}),
                ArgSpec(("--reset", "-r"), {"action": "store_true", "help": "Reset config to defaults"}),
            ),
        ),
        CommandSpec(
            name="review",
            aliases=("rv",),
            func=cmd_review,
            help_key="completion.review",
            completion_key="completion.review",
            args=(
                ArgSpec(("--tool", "-t"), {"default": "codex", "help": "AI Tool (claude, codex, gemini)"}),
                ArgSpec(("--model", "-m"), {"help": "Specific model override"}),
                # review target flags (mutually exclusive group is handled in gwt.py)
            ),
        ),
        CommandSpec(
            name="help",
            func=None,
            help_key="completion.help",
            completion_key="completion.help",
        ),
    ]


def command_by_name() -> Dict[str, CommandSpec]:
    mapping: Dict[str, CommandSpec] = {}
    for spec in iter_commands():
        mapping[spec.name] = spec
        for a in spec.aliases:
            mapping[a] = spec
    return mapping


def visible_commands() -> List[CommandSpec]:
    return [c for c in iter_commands() if not c.hidden]
