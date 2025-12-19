# -*- coding: utf-8 -*-
"""GWT Review Command"""

import datetime
import os
import shutil
import subprocess
from pathlib import Path

from gwtlib.i18n import t
from gwtlib.config import DEFAULT_MODELS, get_effective_config
from gwtlib.utils import git_output, print_colored


def cmd_review(args):
    config = get_effective_config()
    config_default_tool = config.get("review", {}).get("defaultTool", "codex")
    config_models = config.get("review", {}).get("models", DEFAULT_MODELS)

    tool_map = {
        "claude": "claude",
        "c": "claude",
        "codex": "codex",
        "x": "codex",
        "gemini": "gemini",
        "g": "gemini",
    }
    tool_input = args.tool.lower() if args.tool else config_default_tool
    tool_bin = tool_map.get(tool_input, config_default_tool)

    default_model = config_models.get(tool_bin, DEFAULT_MODELS.get(tool_bin, ""))
    model = args.model if args.model else default_model

    diff_cmd = ["git", "diff", "HEAD"]
    mode_label = t("review.mode.uncommitted")

    if args.staged:
        diff_cmd = ["git", "diff", "--staged"]
        mode_label = t("review.mode.staged")
    elif args.last:
        diff_cmd = ["git", "show", "HEAD"]
        mode_label = t("review.mode.last")
    elif args.commit:
        diff_cmd = ["git", "diff", args.commit, "HEAD"]
        mode_label = t("review.mode.commit", sha=args.commit)
    elif args.branch:
        diff_cmd = ["git", "diff", args.branch, "HEAD"]
        mode_label = t("review.mode.branch", branch=args.branch)

    print_colored(t("review.preparing", tool=tool_bin.capitalize(), mode=mode_label), "36")
    print_colored(t("review.using_model", model=model), "90")

    use_wsl = config.get("review", {}).get("useWsl", False) and os.name == "nt"

    if use_wsl:
        if not shutil.which("wsl"):
            print_colored(t("review.wsl_missing"), "31")
            print_colored(t("review.wsl_disable_tip"), "90")
            return
        tool_path = tool_bin
    else:
        found_path = shutil.which(tool_bin)
        if not found_path:
            print_colored(t("review.cli_missing", tool=tool_bin), "31")
            return
        tool_path = found_path if os.name == "nt" else tool_bin

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]

    diff_dir = Path.cwd() / ".gwt" / "review_contexts"
    diff_dir.mkdir(parents=True, exist_ok=True)

    diff_file = diff_dir / f"{tool_bin}_review_context_{timestamp}.diff"

    with open(diff_file, "w", encoding="utf-8") as f:
        subprocess.run(diff_cmd, stdout=f, stderr=subprocess.PIPE)

    if os.path.getsize(diff_file) == 0:
        print_colored(t("review.no_changes"), "32")
        try:
            os.remove(diff_file)
        except OSError:
            pass
        return

    print_colored(t("review.diff_captured", path=diff_file), "90")
    print_colored(t("review.launching", tool=tool_bin.capitalize()), "36")

    project_name = os.path.basename(git_output(["rev-parse", "--show-toplevel"]).strip())
    branch_name = git_output(["branch", "--show-current"]).strip()

    prompt = t(
        "review.prompt",
        diff_file=diff_file,
        project=project_name,
        branch=branch_name,
    )
    if tool_bin == "claude":
        prompt += (
            "\nPS: Please use your most advanced reasoning capabilities "
            "(UltraThink/DeepAnalysis) to verify the necessity of these changes."
        )

    cmd = [tool_path, "--model", model]

    if tool_bin == "codex":
        cmd.extend(["-c", "reasoning_effort=high"])
        cmd.extend(["--sandbox", "read-only"])
        cmd.extend(["--ask-for-approval", "on-request"])
        cmd.append(prompt)
    elif tool_bin == "gemini":
        cmd.extend(["-i", prompt])
    else:
        cmd.append(prompt)

    if use_wsl:
        import shlex

        cmd_str = " ".join(shlex.quote(arg) for arg in cmd)
        cmd = ["wsl", "bash", "-i", "-c", cmd_str]
        print_colored(t("review.wsl_running"), "90")

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print(t("review.cancelled"))
