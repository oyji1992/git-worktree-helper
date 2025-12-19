# -*- coding: utf-8 -*-
"""GWT Utility Module

This module provides common utility functions used across the GWT tool:
- Command execution helpers
- Git helpers
- Shell communication
- Terminal output formatting
"""
import os
import subprocess

from gwtlib.config import GWT_CD_FILE_ENV
from gwtlib.i18n import t


def run_cmd(cmd, capture_output=False, check=False, shell=False):
    """Runs a shell command."""
    try:
        result = subprocess.run(cmd, shell=shell, check=check, text=True,
                               stdout=subprocess.PIPE if capture_output else None,
                               stderr=subprocess.PIPE if capture_output else None)
        if capture_output:
            # Return output only if command succeeded, otherwise return None
            return result.stdout.strip() if result.returncode == 0 else None
        else:
            return result.returncode == 0
    except subprocess.CalledProcessError:
        if capture_output:
            return None
        return False


def git_output(args):
    """Runs a git command and returns output string."""
    cmd = ["git"] + args
    return run_cmd(cmd, capture_output=True)


def request_cd(path):
    """Writes the target directory to the communication file for the shell wrapper."""
    cd_file = os.environ.get(GWT_CD_FILE_ENV)
    if cd_file:
        try:
            with open(cd_file, "w", encoding="utf-8") as f:
                f.write(path)
        except Exception as e:
            print(f"❌ Error writing to CD file: {e}")


def get_main_worktree():
    """Returns the path of the main worktree."""
    output = git_output(["worktree", "list"])
    if output:
        return output.splitlines()[0].split()[0]
    return None


def is_inside_worktree():
    """Check if we're inside a git worktree."""
    return git_output(["rev-parse", "--is-inside-work-tree"]) == "true"


def get_branch_worktree(branch_name):
    """检查分支是否已被 worktree 使用，返回使用该分支的 worktree 路径，否则返回 None"""
    output = git_output(["worktree", "list", "--porcelain"])
    if not output:
        return None
    
    current_worktree = None
    for line in output.splitlines():
        if line.startswith("worktree "):
            current_worktree = line[9:]  # 移除 'worktree ' 前缀
        elif line.startswith("branch "):
            # 格式: branch refs/heads/branch-name
            wt_branch = line[7:]  # 移除 'branch ' 前缀
            if wt_branch.startswith("refs/heads/"):
                wt_branch = wt_branch[11:]  # 移除 'refs/heads/' 前缀
            if wt_branch == branch_name:
                return current_worktree
    return None


def print_colored(text, color_code, bold=False):
    """Simple ANSI color printer.
    
    Color codes:
    - 36: Cyan
    - 32: Green
    - 31: Red
    - 33: Yellow
    - 90: Gray
    - 0: Reset
    """
    style = "1;" if bold else ""
    print(f"\033[{style}{color_code}m{text}\033[0m")


def ensure_worktree_gitignore(repo_root, worktree_dir_name=".worktree"):
    """Ensure configured worktree directory is in .gitignore"""
    import os
    
    gitignore_path = os.path.join(repo_root, ".gitignore")
    # Always treat as a directory ignore entry.
    worktree_entry = f"{worktree_dir_name.rstrip('/')}/"

    # Read existing .gitignore
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Check if already present
        if worktree_entry in content or worktree_dir_name in content:
            return
        # Append to existing file
        with open(gitignore_path, 'a', encoding='utf-8') as f:
            f.write(f"\n# GWT worktree directory\n{worktree_entry}\n")
        print_colored(t("utils.gitignore.added", entry=worktree_entry), "90")
    else:
        # Create new .gitignore
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(f"# GWT worktree directory\n{worktree_entry}\n")
        print_colored(t("utils.gitignore.created", entry=worktree_entry), "90")
