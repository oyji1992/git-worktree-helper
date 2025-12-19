# GWT - Git Worktree Manager
# This package provides the core functionality for the gwt command.

from gwtlib.config import (
    DEFAULT_CONFIG,
    DEFAULT_MODELS,
    GWT_CD_FILE_ENV,
    GWT_CONFIG_DIR,
    GWT_CONFIG_FILE,
    get_global_config_path,
    get_repo_config_path,
    load_config,
    save_config,
    deep_merge,
    get_effective_config,
    detect_available_tools,
    detect_submodules,
)

from gwtlib.utils import (
    run_cmd,
    git_output,
    request_cd,
    get_main_worktree,
    is_inside_worktree,
    get_branch_worktree,
    print_colored,
    ensure_worktree_gitignore,
)

from gwtlib.help import print_help
from gwtlib.completion import cmd_completion

__all__ = [
    # Config
    'DEFAULT_CONFIG',
    'DEFAULT_MODELS',
    'GWT_CD_FILE_ENV',
    'GWT_CONFIG_DIR',
    'GWT_CONFIG_FILE',
    'get_global_config_path',
    'get_repo_config_path',
    'load_config',
    'save_config',
    'deep_merge',
    'get_effective_config',
    'detect_available_tools',
    'detect_submodules',
    # Utils
    'run_cmd',
    'git_output',
    'request_cd',
    'get_main_worktree',
    'is_inside_worktree',
    'get_branch_worktree',
    'print_colored',
    'ensure_worktree_gitignore',
    # Help
    'print_help',
    # Completion
    'cmd_completion',
]
