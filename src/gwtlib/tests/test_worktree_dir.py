# -*- coding: utf-8 -*-
"""Tests for worktree directory template functionality."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))


class TestWorktreeDirTemplate(unittest.TestCase):
    """Test worktreeDir template variable substitution."""

    def test_default_config_has_template(self):
        """Test that default config uses template syntax."""
        from gwtlib.config import DEFAULT_CONFIG

        self.assertIn("{repo_name}", DEFAULT_CONFIG["worktreeDir"])
        self.assertIn("{sep}", DEFAULT_CONFIG["worktreeDir"])

    def test_template_variable_substitution(self):
        """Test {repo_name} and {sep} variable substitution."""
        template = "..{sep}{repo_name}_wt"
        repo_name = "my-project"
        expected = f"..{os.sep}{repo_name}_wt"

        result = template.format(repo_name=repo_name, sep=os.sep)

        self.assertEqual(result, expected)

    def test_custom_template_with_variables(self):
        """Test custom templates with variables."""
        template = "/home/user/worktrees/{repo_name}{sep}branches"
        repo_name = "test-repo"
        expected = f"/home/user/worktrees/{repo_name}{os.sep}branches"

        result = template.format(repo_name=repo_name, sep=os.sep)

        self.assertEqual(result, expected)

    def test_static_path_unchanged(self):
        """Test that static paths (no template vars) remain unchanged."""
        template = ".worktree"
        repo_name = "any-repo"

        result = template.format(repo_name=repo_name, sep=os.sep)

        self.assertEqual(result, ".worktree")


class TestWorktreePathResolution(unittest.TestCase):
    """Test worktree path resolution logic."""

    def test_parent_directory_path_recognized(self):
        """Test that paths starting with ../ are recognized as external."""
        path_unix = "../repo_wt"
        path_windows = "..\\repo_wt"

        is_external_unix = path_unix.startswith("../") or path_unix.startswith(".." + os.sep)
        is_external_windows = path_windows.startswith("../") or path_windows.startswith(".." + os.sep) or path_windows.startswith("..\\")

        self.assertTrue(is_external_unix)
        self.assertTrue(is_external_windows)

    def test_internal_directory_path_not_external(self):
        """Test that internal paths are not marked as external."""
        path = ".worktree"

        is_external = path.startswith("../") or path.startswith(".." + os.sep)

        self.assertFalse(is_external)

    def test_normpath_resolves_parent_references(self):
        """Test that normpath correctly resolves ../ paths."""
        import pathlib
        repo_root = str(pathlib.PurePosixPath("/home/user/projects/myrepo"))
        worktree_dir_name = "../myrepo_wt"

        # Use posixpath for consistent test behavior
        import posixpath
        worktree_dir = posixpath.normpath(posixpath.join(repo_root, worktree_dir_name))

        expected = "/home/user/projects/myrepo_wt"
        self.assertEqual(worktree_dir, expected)


class TestGitignoreLogic(unittest.TestCase):
    """Test .gitignore handling for different path types."""

    def test_external_path_skips_gitignore(self):
        """Test that external paths (../) skip .gitignore entry."""
        # Test Unix-style path
        worktree_dir_name = "../myrepo_wt"
        is_external = worktree_dir_name.startswith("../") or worktree_dir_name.startswith(".." + os.sep)
        self.assertTrue(is_external)

        # Test Windows-style path
        worktree_dir_name_win = "..\\myrepo_wt"
        is_external_win = worktree_dir_name_win.startswith("../") or worktree_dir_name_win.startswith(".." + os.sep) or worktree_dir_name_win.startswith("..\\")
        self.assertTrue(is_external_win)

    def test_internal_path_needs_gitignore(self):
        """Test that internal paths need .gitignore entry."""
        worktree_dir_name = ".worktree"

        is_external = worktree_dir_name.startswith("../") or worktree_dir_name.startswith(".." + os.sep)

        # For internal paths, we SHOULD call ensure_worktree_gitignore
        self.assertFalse(is_external)


class TestFullIntegration(unittest.TestCase):
    """Integration tests for the complete worktree path building logic."""

    def test_new_worktree_path_with_default_template(self):
        """Test complete path building with default template."""
        from gwtlib.config import DEFAULT_CONFIG
        import posixpath

        repo_root = "/home/user/projects/myrepo"
        repo_name = "myrepo"
        branch_name = "feature/test"
        safe_branch_name = branch_name.replace("/", "-")

        # Simulate the logic from cmd_new
        worktree_dir_template = DEFAULT_CONFIG["worktreeDir"]
        worktree_dir_name = worktree_dir_template.format(repo_name=repo_name, sep="/")

        is_external = worktree_dir_name.startswith("../") or worktree_dir_name.startswith("../")
        self.assertTrue(is_external)

        worktree_dir = posixpath.normpath(posixpath.join(repo_root, worktree_dir_name))
        new_path = posixpath.join(worktree_dir, safe_branch_name)

        expected_base = "/home/user/projects/myrepo_wt"
        expected_path = f"{expected_base}/{safe_branch_name}"

        self.assertEqual(worktree_dir, expected_base)
        self.assertEqual(new_path, expected_path)

    def test_new_worktree_path_with_legacy_config(self):
        """Test path building with legacy .worktree config."""
        repo_root = "/home/user/projects/myrepo"
        worktree_dir_template = ".worktree"
        branch_name = "feature-branch"
        safe_branch_name = branch_name.replace("/", "-")

        worktree_dir_name = worktree_dir_template.format(repo_name="myrepo", sep=os.sep)
        is_external = worktree_dir_name.startswith("../") or worktree_dir_name.startswith(".." + os.sep)

        self.assertFalse(is_external)

        worktree_dir = os.path.join(repo_root, worktree_dir_name)
        new_path = os.path.join(worktree_dir, safe_branch_name)

        expected = f"/home/user/projects/myrepo{os.sep}.worktree{os.sep}feature-branch"
        self.assertEqual(new_path, expected)


if __name__ == "__main__":
    unittest.main()
