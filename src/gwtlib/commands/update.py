# -*- coding: utf-8 -*-
"""GWT Update Command"""
import os
import subprocess

from gwtlib.i18n import t
from gwtlib.utils import run_cmd, print_colored


def _find_git_root(start_dir):
    cur = os.path.abspath(start_dir)
    while True:
        if os.path.exists(os.path.join(cur, ".git")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent


def cmd_update(args):
    """Update gwt by pulling latest changes from git repository."""
    # Find repository root by walking upwards from this file.
    gwt_dir = _find_git_root(os.path.dirname(__file__))
    display_path = gwt_dir or os.path.dirname(__file__)
    print_colored(t("update.updating_from", path=display_path), "36")

    if getattr(args, "dry_run", False):
        print_colored(t("generic.dry_run"), "33")
        print_colored(t("generic.would_run", cmd="git fetch"), "90")
        print_colored(t("generic.would_run", cmd="git pull --ff-only"), "90")
        return
    
    if not gwt_dir:
        print_colored(t("update.not_git_repo"), "31")
        return
    
    # Change to gwt directory and pull
    original_dir = os.getcwd()
    try:
        os.chdir(gwt_dir)
        print_colored(t("update.cd_to", path=gwt_dir), "90")
        
        # Fetch first
        print_colored(t("update.fetching"), "36")
        run_cmd(["git", "fetch"])
        
        # Pull with --ff-only
        print_colored(t("update.pulling"), "36")
        result = subprocess.run(["git", "pull", "--ff-only"], capture_output=True, text=True)
        
        if result.returncode == 0:
            if "Already up to date" in result.stdout or "Already up-to-date" in result.stdout:
                print_colored(t("update.already_up_to_date"), "32")
            else:
                print(result.stdout)
                print_colored(t("update.updated_ok"), "32")
        else:
            print_colored(t("update.failed"), "31")
            if result.stderr:
                print(result.stderr)
    finally:
        os.chdir(original_dir)
