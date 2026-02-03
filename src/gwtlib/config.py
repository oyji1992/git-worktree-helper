# -*- coding: utf-8 -*-
"""GWT Configuration Module

This module handles all configuration-related functionality including:
- Loading and saving config files
- Merging configurations (default <- global <- repo)
- Detecting available tools
- Detecting submodules
"""
import os
import json
import shutil
import subprocess
from pathlib import Path

from gwtlib.config_schema import LATEST_CONFIG_VERSION, migrate_config, validate_and_sanitize_config

# Import utils - note: this creates a circular import issue, so we use late import
# For functions that need utils, we import inside the function

# --- Constants ---
GWT_CD_FILE_ENV = "GWT_CD_FILE"
GWT_CONFIG_DIR = ".gwt"
GWT_CONFIG_FILE = "setting.json"

DEFAULT_MODELS = {
    "claude": "claude-opus-4-5-20251101",
    "codex": "gpt-5.2",
    "gemini": "gemini-3-pro-high"
}

DEFAULT_CONFIG = {
    "configVersion": LATEST_CONFIG_VERSION,
    "mainBranch": "main",
    "worktreeDir": "..{sep}{repo_name}_wt",
    "submodules": [],
    "ui": {
        "lang": "auto"  # auto, zh, en
    },
    "review": {
        "defaultTool": "codex",
        "models": DEFAULT_MODELS.copy(),
        "useWsl": False  # On Windows, use WSL to run review tools
    },
    "merge": {
        "tool": "lazygit",  # lazygit, cursor, code, p4merge, meld, kdiff3
        "toolPriority": ["lazygit", "cursor", "code", "p4merge", "meld"]
    },
    "gitTool": "lazygit",  # lazygit, gitui, tig
    "availableTools": {
        "reviewTools": {},
        "cliTools": {},
        "mergeTools": {}
    }
}


def get_global_config_path():
    """Get global config file path (~/.gwt/setting.json)"""
    return Path.home() / GWT_CONFIG_DIR / GWT_CONFIG_FILE


def get_repo_config_path():
    """Get repository config file path (<repo>/.gwt/setting.json)"""
    from gwtlib.utils import get_main_worktree
    repo_root = get_main_worktree()
    if repo_root:
        return Path(repo_root) / GWT_CONFIG_DIR / GWT_CONFIG_FILE
    return None


def load_config(is_global=False):
    """Load config from file"""
    from gwtlib.i18n import t
    from gwtlib.utils import print_colored
    
    if is_global:
        config_path = get_global_config_path()
    else:
        config_path = get_repo_config_path()
    
    if config_path and config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                raw = json.load(f)
                migrated, mig_warnings = migrate_config(raw)
                sanitized, val_warnings = validate_and_sanitize_config(migrated, DEFAULT_CONFIG)

                if os.environ.get("GWT_DEBUG") == "1":
                    for w in mig_warnings + val_warnings:
                        print_colored(f"⚠️  config: {w}", "33")
                return sanitized
        except (json.JSONDecodeError, IOError) as e:
            print_colored(t("config.load_failed", error=e), "33")
    return {}


def save_config(config, is_global=False):
    """Save config to file"""
    from gwtlib.i18n import t
    from gwtlib.utils import print_colored
    
    if is_global:
        config_path = get_global_config_path()
    else:
        config_path = get_repo_config_path()
    
    if not config_path:
        print_colored(t("generic.not_git_repo"), "31")
        return False
    
    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        if isinstance(config, dict):
            migrated, _ = migrate_config(config)
            config, _ = validate_and_sanitize_config(migrated, DEFAULT_CONFIG)
            config["configVersion"] = LATEST_CONFIG_VERSION
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print_colored(t("config.save_failed", error=e), "31")
        return False


def deep_merge(base, override):
    """Deep merge two dictionaries, override takes precedence"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def get_effective_config():
    """Get merged config: default <- global <- repo"""
    global_config = load_config(is_global=True)
    repo_config = load_config(is_global=False)
    
    # Merge: default <- global <- repo
    merged = deep_merge(DEFAULT_CONFIG.copy(), global_config)
    merged = deep_merge(merged, repo_config)
    
    return merged


def detect_available_tools():
    """Detect available CLI tools"""
    review_tools = {
        "claude": shutil.which("claude") is not None,
        "codex": shutil.which("codex") is not None,
        "gemini": shutil.which("gemini") is not None
    }
    cli_tools = {
        "fzf": shutil.which("fzf") is not None,
        "git": shutil.which("git") is not None
    }
    merge_tools = {
        "lazygit": shutil.which("lazygit") is not None,
        "gitui": shutil.which("gitui") is not None,
        "cursor": shutil.which("cursor") is not None,
        "code": shutil.which("code") is not None,
        "p4merge": shutil.which("p4merge") is not None,
        "meld": shutil.which("meld") is not None,
        "kdiff3": shutil.which("kdiff3") is not None
    }
    return {
        "reviewTools": review_tools,
        "cliTools": cli_tools,
        "mergeTools": merge_tools
    }


def detect_submodules():
    """Recursively detect all submodules"""
    from gwtlib.utils import git_output
    
    submodules = []
    output = git_output(["submodule", "status", "--recursive"])
    if output:
        for line in output.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                sm_path = parts[1]
                # Get current branch of submodule
                sm_branch = subprocess.run(
                    ["git", "-C", sm_path, "branch", "--show-current"],
                    capture_output=True, text=True
                ).stdout.strip() or "main"
                submodules.append({
                    "path": sm_path,
                    "mainBranch": sm_branch
                })
    return submodules
