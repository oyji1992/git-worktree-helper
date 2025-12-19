# -*- coding: utf-8 -*-
"""GWT Status Command"""
import os
import subprocess
import textwrap
from pathlib import Path

from gwtlib.i18n import t
from gwtlib.utils import git_output, print_colored


def cmd_status(args):
    """Show status of main repository and submodules."""
    print_colored(t("status.main_repo"), "36", bold=True)
    subprocess.run(["git", "status", "-sb"])
    print("")

    if os.path.exists(".gitmodules"):
        print_colored(t("status.submodules"), "36", bold=True)
        submodules_status = git_output(["submodule", "status", "--recursive"])
        if submodules_status:
            for line in submodules_status.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    sm_path = parts[1]
                    sm_full_path = Path(sm_path)
                    if sm_full_path.exists():
                        proc_branch = subprocess.run(
                            ["git", "-C", sm_path, "branch", "--show-current"],
                            capture_output=True, text=True
                        )
                        branch = proc_branch.stdout.strip()
                        proc_stat = subprocess.run(
                            ["git", "-C", sm_path, "status", "-s"],
                            capture_output=True, text=True
                        )
                        stat = proc_stat.stdout.strip()

                        if stat:
                            print(f"  🔸 {sm_path} [{branch}]:")
                            print(textwrap.indent(stat, "      "))
                        else:
                            print(f"  {t('status.submodule_clean', path=sm_path, branch=branch)}")
