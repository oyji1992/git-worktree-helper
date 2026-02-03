# -*- coding: utf-8 -*-
"""GWT i18n (very small runtime translation layer).

Language selection:
- `GWT_LANG` env var: `en` / `zh` (override)
- Otherwise auto-detect from `LC_ALL`, `LANGUAGE`, `LANG`, or OS locale.
"""

from __future__ import annotations

import locale
import os
from typing import Any, Dict


SUPPORTED_LANGS = ("zh", "en")


_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "zh": {
        # Generic
        "generic.cancelled": "已取消。",
        "generic.cancelled_en": "Cancelled.",
        "generic.invalid_selection": "❌ 选择无效。",
        "generic.tip_install_fzf": "💡 Tip: 安装 'fzf' 可获得更好的交互式选择体验。",
        "generic.not_git_repo": "❌ 不在 git 仓库中",
        "generic.not_git_dir": "❌ 不在 git 目录中。",
        "generic.select_number": "请选择编号 (1-{n}): ",
        "generic.select_number_or_name": "请选择编号 (1-{n}) 或输入名称: ",
        "generic.invalid_selection_simple": "❌ 选择无效。",
        "generic.dry_run": "🧪 Dry run（仅展示，不执行）",
        "generic.would_run": "   将执行: {cmd}",
        "generic.would_cd": "   将跳转到: {path}",
        "generic.internal_error": "❌ 内部错误，请使用 --debug 重新运行以查看详情。",
        # Help
        "help.title": "GWT: Git Worktree Manager (Python Core)",
        "help.subtitle_1": "基于 Git Worktree 的高效并行开发工具。",
        "help.subtitle_2": "允许你在不同的文件夹中同时检出多个分支，无需反复 stash/checkout。",
        "help.usage": "用法:",
        "help.usage_line": "  gwt <命令> [参数]",
        "help.core": "核心命令:",
        "help.ai": "AI Code Review 命令:",
        "help.review_line": "  \033[36mreview\033[0m              \033[90m, rv  \033[0m AI 代码评审 (默认: Codex, Uncommitted)",
        "help.review_target": "  \033[90mTarget (选择目标):\033[0m",
        "help.review_tool": "  \033[90mTool (选择工具):\033[0m",
        "help.review_target_staged": "    --staged, -s        暂存区 (Staged)",
        "help.review_target_last": "    --last, -l          上一次提交 (HEAD)",
        "help.review_target_commit": "    --commit, -c <sha>  对比指定 Commit (SHA vs HEAD)",
        "help.review_target_branch": "    --branch, -b <name> 对比指定分支 (Branch vs HEAD)",
        "help.review_tool_tool": "    --tool, -t <name>   指定工具 (claude, codex, gemini)",
        "help.new_detail": "New 命令详情:",
        "help.new_detail_1": "  \033[36mgwt new\033[0m               交互式选择分支 (fzf, 本地+远端)",
        "help.new_detail_2": "  \033[36mgwt new <branch>\033[0m      创建/切换到指定分支的 Worktree",
        "help.new_detail_3": "  \033[36mgwt new <branch> <base>\033[0m 从 base 分支创建新分支",
        "help.setting_detail": "Setting 命令详情:",
        "help.setting_detail_1": "  \033[36mgwt setting\033[0m           交互式配置当前仓库设置",
        "help.setting_detail_2": "  \033[36mgwt setting -g\033[0m        交互式配置全局设置",
        "help.setting_detail_3": "  \033[36mgwt setting -s\033[0m        显示当前生效的配置",
        "help.setting_detail_4": "  \033[36mgwt setting -i\033[0m        初始化配置 (检测工具)",
        "help.setting_detail_5": "  \033[36mgwt setting -r\033[0m        重置配置为默认值",
        "help.examples": "示例:",
        "help.ex1": "  1. 交互式选择分支创建 Worktree",
        "help.ex2": "  2. 直接创建 feature/login 分支的 Worktree",
        "help.ex3": "  3. 从 develop 分支创建新分支",
        "help.ex4": "  4. AI Code Review (默认: Codex, 未提交的改动)",
        "help.ex5": "  5. Review 暂存区 (使用 Gemini)",
        "help.ex6": "  6. 配置 gwt 设置",
        # Core command descriptions (for help)
        "help.cmd.list": "列出当前所有 Worktree (工作树)",
        "help.cmd.init": "输出 Shell/Pwsh wrapper（用于 pipx 安装）",
        "help.cmd.status": "查看各仓库和子模块的变动简报",
        "help.cmd.new": "新建 Worktree (无参数进入交互式选择，支持本地/远端分支)",
        "help.cmd.remove": "删除 Worktree (默认删当前，安全跳回主目录)",
        "help.cmd.prune": "清理已失效的 Worktree 记录",
        "help.cmd.cd": "交互式跳转目录 (推荐安装 fzf)",
        "help.cmd.update": "更新 gwt 工具 (git pull --ff-only)",
        "help.cmd.setting": "配置 gwt 设置 (--global 全局配置)",
        "help.cmd.merge": "合并分支 (交互式选择，冲突处理)",
        "help.cmd.commit": "快速提交 (使用 lazygit/gitui)",
        # Completion descriptions
        "completion.list": "列出 worktrees",
        "completion.init": "输出 wrapper",
        "completion.init.shell": "Shell (zsh/bash/powershell)",
        "completion.status": "查看状态",
        "completion.new": "创建 worktree",
        "completion.remove": "删除 worktree",
        "completion.prune": "清理无效 worktrees",
        "completion.cd": "跳转到 worktree",
        "completion.update": "更新 gwt 工具",
        "completion.merge": "合并分支",
        "completion.commit": "快速提交",
        "completion.setting": "配置设置",
        "completion.review": "AI 代码评审",
        "completion.help": "显示帮助",
        "completion.branch": "分支",
        "completion.setting.global": "编辑全局配置",
        "completion.setting.show": "显示当前配置",
        "completion.setting.init": "初始化并检测工具",
        "completion.setting.reset": "重置为默认",
        "completion.review.tool.claude": "Anthropic Claude",
        "completion.review.tool.codex": "OpenAI Codex",
        "completion.review.tool.gemini": "Google Gemini",
        "completion.review.staged": "评审暂存区改动",
        "completion.review.last": "评审上一次提交",
        "completion.review.commit": "评审指定提交差异",
        "completion.review.branch": "评审分支差异",
        "completion.review.tool": "选择 AI 工具",
        "completion.review.model": "覆盖模型",
        "completion.global.lang": "语言 (zh/en)",
        "completion.global.yes": "自动确认 (安全场景)",
        "completion.global.dry_run": "仅展示不执行",
        "completion.global.debug": "调试模式（显示堆栈）",
        # Config
        "config.load_failed": "⚠️  读取配置失败: {error}",
        "config.save_failed": "❌ 保存配置失败: {error}",
        # Utils
        "utils.gitignore.added": "📝 已将 {entry} 添加到 .gitignore",
        "utils.gitignore.created": "📝 已创建 .gitignore 并加入 {entry}",
        # Status
        "status.main_repo": "📌 主仓库:",
        "status.submodules": "📦 子模块:",
        "status.submodule_clean": "✅ {path} [{branch}] (clean)",
        # Update
        "update.updating_from": "🔄 正在更新 gwt（路径）: {path}",
        "update.not_git_repo": "❌ gwt 不是从 git 仓库安装的。",
        "update.cd_to": "📂 进入目录: {path}",
        "update.fetching": "📡 正在获取更新...",
        "update.pulling": "⬇️  正在拉取 (--ff-only)...",
        "update.already_up_to_date": "✅ gwt 已是最新。",
        "update.updated_ok": "✅ gwt 更新成功！",
        "update.failed": "❌ 更新失败，可能需要你手动处理冲突。",
        # Worktree
        "worktree.fetch_remote": "🔄 正在获取远端分支...",
        "worktree.no_branches": "❌ 未找到任何分支。",
        "worktree.no_branches_available": "❌ 没有可用的分支。",
        "worktree.branches_title": "📋 可选分支:",
        "worktree.branches_header": "   [L]=本地  [R]=远端\n",
        "worktree.branches_tip": "   或直接输入新分支名来创建它。\n",
        "worktree.fzf_prompt_branch": "选择分支 > ",
        "worktree.fzf_prompt_worktree": "选择 Worktree > ",
        "worktree.fzf_prompt_remove": "选择要删除的 Worktree > ",
        "worktree.fzf_header_branches": "  [L]=本地  [R]=远端",
        "worktree.create_worktree": "⚙️  创建 Worktree: {path} (分支: {branch})...",
        "worktree.branch_used": "\n⚠️  分支 '{branch}' 已被 worktree 使用:",
        "worktree.you_can": "\n💡 你可以:",
        "worktree.you_can_1": "   1. 使用 'gwt cd' 跳转到该 worktree",
        "worktree.you_can_2": "   2. 先用 'gwt rm' 删除它",
        "worktree.branch_exists_local": "🔹 本地已存在分支 '{branch}'，直接检出...",
        "worktree.found_remote_branch": "🔍 找到远端分支 '{branch}'.",
        "worktree.use_remote_prompt": "📌 使用远端分支? [Y/n]: ",
        "worktree.create_tracking": "🔹 创建本地分支 '{branch}' 并跟踪 '{remote}'...",
        "worktree.create_from_base": "🔹 从 {base} 创建新分支 '{branch}'...",
        "worktree.branch_not_found_create": "🔹 未找到分支 '{branch}'，从 {base} 创建...",
        "worktree.create_failed": "❌ 创建 worktree 失败。",
        "worktree.created_ok": "✅ Worktree 创建成功，正在跳转...",
        "worktree.submodules_detected": "📦 检测到子模块，正在更新...",
        "worktree.sync_submodules": "🔄 同步子模块分支...",
        "worktree.submodule_checkout_local": "🔹 子模块 {path}: 检出本地分支 {branch}",
        "worktree.submodule_found_remote": "🔍 子模块 {path}: 找到远端分支 '{remote}'.",
        "worktree.submodule_use_remote_prompt": "   📌 {path} 使用远端分支? [Y/n]: ",
        "worktree.submodule_create_tracking": "🔹 子模块 {path}: 创建分支并跟踪 '{remote}'",
        "worktree.submodule_create_local": "✨ 子模块 {path}: 创建新本地分支 {branch}",
        # Remove/cd/prune
        "worktree.no_worktrees": "❌ 未找到任何 worktree。",
        "worktree.no_removable": "⚠️  没有可删除的 worktree（只有主 worktree）。",
        "worktree.worktrees_title": "📋 可选 Worktrees:",
        "worktree.remove_select_prompt": "请选择要删除的编号 (1-{n}): ",
        "worktree.remove_prepare": "🗑️  准备删除: {path}",
        "worktree.remove_confirm": "Confirm? (y/N) ",
        "worktree.remove_inside_warn": "⚠️  你当前位于要删除的 worktree 内。",
        "worktree.remove_switching": "📂 先切换到主 worktree...",
        "worktree.remove_rerun": "💡 切换后请再次执行 remove。",
        "worktree.remove_main_forbidden": "⚠️  不能删除主 worktree ({path}).",
        "worktree.remove_no_match": "❌ 未找到匹配 '{key}' 的 worktree。",
        "worktree.removed_ok": "✅ 已删除。",
        "worktree.remove_failed": "❌ 删除 worktree 失败。",
        "worktree.prune_start": "🧹 正在清理无效 worktree 记录...",
        "worktree.prune_ok": "✅ 清理完成。",
        "worktree.prune_failed": "❌ 清理失败。",
        "worktree.cd_prompt": "请选择编号 (1-{n}): ",
        "worktree.invalid_selection": "❌ 选择无效。",
        # Review
        "review.preparing": "👀 准备 {tool} 评审: {mode} ...",
        "review.mode.uncommitted": "未提交的改动（暂存区 + 未暂存区）",
        "review.mode.staged": "仅暂存区改动",
        "review.mode.last": "上一次提交 (HEAD)",
        "review.mode.commit": "对比 {sha} vs HEAD",
        "review.mode.branch": "对比 {branch} vs HEAD",
        "review.using_model": "🤖 使用模型: {model}",
        "review.wsl_missing": "❌ 已启用 WSL 模式，但未找到 WSL。",
        "review.wsl_disable_tip": "💡 运行 'gwt setting' 关闭 WSL 模式，或先安装 WSL。",
        "review.cli_missing": "❌ 未找到 '{tool}' CLI，请先安装。",
        "review.no_changes": "✅ 没有检测到需要评审的改动。",
        "review.diff_captured": "📝 Diff 已保存至 {path}",
        "review.launching": "🚀 正在启动 {tool}...",
        "review.wsl_running": "🐧 正在通过 WSL 运行...",
        "review.cancelled": "\n已取消评审。",
        # Review prompt
        "review.prompt": """请对 '{diff_file}' 中捕获的代码变更进行 Code Review。

评审维度：
1. 🧐 **逻辑与语义审查**：
   - 代码是否实现了预期功能？逻辑是否严密？
   - **命名与语义**：变量/函数命名是否清晰表达意图？代码逻辑是否易读？
2. ⚡ **精简与去重**：
   - ❌ 冗余代码 (Dead Code/Redundant Logic)
   - 🔍 **重复造轮子检测**：新增方法是否在项目中已有类似实现？是否有必要新增？
   - 📉 认知负荷 (Cognitive Load) - 是否有更清晰简洁的写法？
3. 🌳 **可视化**：提供 ASCII 流程图展示变更后的逻辑流。

输出要求：
- 若发现可精简或重复之处，请务必用 "💡 **Optimization/Duplication Alert**" 标出。
- 保持回答结构清晰。

上下文:
- 项目: {project}
- 分支: {branch}
""",
        # Merge
        "merge.uncommitted": "❌ 你有未提交的改动，请先 commit 或 stash。",
        "merge.uncommitted_tip": "   可运行 'gwt commit' 进行提交，或 'git stash' 暂存。",
        "merge.title": "🔀 GWT Merge - 分支合并工具",
        "merge.source_prompt": "Source 分支",
        "merge.target_prompt": "Target 分支",
        "merge.select_source": "📌 选择 SOURCE 分支 (changes FROM):",
        "merge.select_target": "📌 选择 TARGET 分支 (merge INTO):",
        "merge.current_branch": "   💡 当前分支: {branch}",
        "merge.confirm": "🔀 将把 '{source}' 合并到 '{target}'",
        "merge.continue_prompt": "   继续? (y/N): ",
        "merge.checkout": "📂 正在切换到 {branch}...",
        "merge.checkout_failed": "❌ 切换到 {branch} 失败",
        "merge.merging": "🔀 正在合并 {source} -> {target}...",
        "merge.ok": "✅ 合并成功！",
        "merge.aborted": "❌ 已放弃合并。",
        "merge.failed": "❌ 合并失败:",
        "merge.conflicts_detected": "\n⚠️  检测到 {n} 个冲突文件:",
        "merge.choose_action": "请选择一个操作:",
        "merge.action1": "  [1] 手动解决 (Manual) - 重新检测冲突状态",
        "merge.action2": "  [2] 打开合并工具 (Merge Tool) - 使用配置的工具",
        "merge.action3": "  [3] 打开 lazygit - 交互式解决",
        "merge.action4": "  [4] 放弃合并 (Abort) - 取消所有合并",
        "merge.select_1_4": "\n> 请选择 (1-4): ",
        "merge.recheck": "🔍 重新检测冲突状态...",
        "merge.opening": "🔧 正在打开 {tool}...",
        "merge.opening_fallback": "🔧 正在打开 {tool} (fallback)...",
        "merge.no_merge_tool": "❌ 没有可用的合并工具，请先安装。",
        "merge.lazygit_missing": "❌ 未安装 lazygit",
        "merge.aborting": "🔄 正在放弃合并...",
        "merge.all_resolved": "✅ 冲突已全部解决！",
        "merge.completing": "   正在完成合并提交...",
        "merge.submodules_check": "📦 正在检查子模块...",
        "merge.submodule_has_conflicts": "⚠️  子模块 '{path}' 存在冲突",
        "merge.submodule_enter": "   正在进入子模块处理...",
        "merge.submodule_aborted": "❌ 子模块合并已放弃",
        "merge.submodule_resolved": "✅ 子模块 '{path}' 冲突已处理完成",
        # Commit
        "commit.title": "📝 GWT Commit - 快速提交工具",
        "commit.no_changes": "✅ 没有需要提交的改动。",
        "commit.status": "📋 当前状态:",
        "commit.launching": "🚀 正在启动 {tool}...",
        "commit.launching_fallback": "🚀 正在启动 {tool} (fallback)...",
        "commit.no_tui": "💡 未找到 git TUI 工具，使用简单提交模式。",
        "commit.no_tui_tip": "   建议安装 'lazygit' 或 'gitui' 获得更好体验。",
        "commit.stage_all": "暂存所有改动? (y/N): ",
        "commit.message": "提交信息: ",
        "commit.ok": "✅ 提交成功！",
        "commit.failed": "❌ 提交失败:",
        # Setting
        "setting.current_config": "📋 当前配置:",
        "setting.global_path": "   (Global: {path})",
        "setting.effective": "   (Effective: global + repo merged)",
        "setting.reset_ok": "✅ 配置已重置为默认值。",
        "setting.reset_confirm": "⚠️  删除 {path}? (y/N): ",
        "setting.no_config_file": "⚠️  未找到配置文件。",
        "setting.not_git_repo": "❌ 不在 git 仓库中",
        "setting.scope.global": "全局",
        "setting.scope.repo": "仓库",
        "setting.ui_lang": "🌐 界面语言",
        "setting.ui_lang_tip": "   💡 auto=跟随环境/终端；也可用 --lang 临时覆盖",
        "setting.ui_lang_prompt": "   > 选择 (1-3，回车保持不变): ",
        "setting.ui_lang_auto": "auto (自动)",
        "setting.ui_lang_zh": "zh (中文)",
        "setting.ui_lang_en": "en (English)",
        "setting.init_title": "🔧 正在初始化 {scope} 配置",
        "setting.title": "🔧 GWT 设置（{scope}）",
        "setting.detecting": "🔍 正在检测可用工具...",
        "setting.review_tools": "🤖 评审工具:",
        "setting.cli_tools": "🔧 CLI 工具:",
        "setting.main_branch": "📌 主分支",
        "setting.main_branch_prompt": "主分支",
        "setting.current": "   当前: {value}",
        "setting.select_tip": "   💡 从现有分支中选择，或输入新名字",
        "setting.changed_to": "   → Changed to: {value}",
        "setting.worktree_dir": "📁 Worktree 目录",
        "setting.worktree_dir_tip": "   💡 可用变量: {repo_name} = 仓库名, {sep} = 路径分隔符",
        "setting.enter_new": "   > 输入新值（回车保持不变）: ",
        "setting.default_review_tool": "🤖 默认评审工具",
        "setting.available": "   Available:",
        "setting.select_1_3": "   > 选择 (1-3，回车保持不变): ",
        "setting.wsl_mode": "🐧 WSL Mode (Windows only)",
        "setting.wsl_current": "   当前: {value}",
        "setting.wsl_available": "   WSL Available: {value}",
        "setting.wsl_tip": "   💡 仅 Codex 需要 WSL，Claude 和 Gemini 可直接在 Windows 运行",
        "setting.wsl_toggle": "   > Toggle WSL mode? (y/N): ",
        "setting.wsl_to": "   → WSL mode: {value}",
        "setting.submodule_settings": "📦 Submodule Settings",
        "setting.submodule_found": "   Found {n} submodule(s):",
        "setting.submodule_select": "   > 选择要编辑的编号（回车跳过）: ",
        "setting.submodule_editing": "\n   Editing: {path}",
        "setting.submodule_current_main": "   当前主分支: {branch}",
        "setting.submodule_tip": "   💡 从子模块分支中选择，或输入新名字",
        "setting.submodule_main_branch_prompt": "{path} 的主分支",
        "setting.no_submodules": "   未发现子模块。",
        "setting.saved_to": "✅ Settings saved to {path}",
        "setting.save_failed": "❌ Failed to save settings",
        # Branch picker
        "setting.branch_available": "   可选分支:",
        "setting.branch_select_or_enter": "   > 选择 (1-{n}) 或输入分支名（回车保持不变）: ",
        "setting.branch_enter_name": "   > 输入分支名（当前: {branch}）: ",
    },
    "en": {
        # Generic
        "generic.cancelled": "Cancelled.",
        "generic.invalid_selection": "❌ Invalid selection.",
        "generic.tip_install_fzf": "💡 Tip: Install 'fzf' for a better interactive experience.",
        "generic.not_git_repo": "❌ Not in a git repository",
        "generic.not_git_dir": "❌ Not in a git directory.",
        "generic.select_number": "Select number (1-{n}): ",
        "generic.select_number_or_name": "Select number (1-{n}) or enter name: ",
        "generic.dry_run": "🧪 Dry run (preview only)",
        "generic.would_run": "   Would run: {cmd}",
        "generic.would_cd": "   Would cd to: {path}",
        "generic.internal_error": "❌ Internal error. Re-run with --debug for details.",
        # Help
        "help.title": "GWT: Git Worktree Manager (Python Core)",
        "help.subtitle_1": "A high-efficiency parallel development tool built on Git Worktree.",
        "help.subtitle_2": "Work on multiple branches in different folders without stash/checkout switching.",
        "help.usage": "Usage:",
        "help.usage_line": "  gwt <command> [args]",
        "help.core": "Core Commands:",
        "help.ai": "AI Code Review:",
        "help.review_line": "  \033[36mreview\033[0m              \033[90m, rv  \033[0m AI Code Review (default: Codex, Uncommitted)",
        "help.review_target": "  \033[90mTarget:\033[0m",
        "help.review_tool": "  \033[90mTool:\033[0m",
        "help.review_target_staged": "    --staged, -s        Staged changes",
        "help.review_target_last": "    --last, -l          Last commit (HEAD)",
        "help.review_target_commit": "    --commit, -c <sha>  Commit diff (SHA vs HEAD)",
        "help.review_target_branch": "    --branch, -b <name> Branch diff (Branch vs HEAD)",
        "help.review_tool_tool": "    --tool, -t <name>   Tool (claude, codex, gemini)",
        "help.new_detail": "New Command Details:",
        "help.new_detail_1": "  \033[36mgwt new\033[0m               Interactive branch selection (fzf, local+remote)",
        "help.new_detail_2": "  \033[36mgwt new <branch>\033[0m      Create/switch worktree for the branch",
        "help.new_detail_3": "  \033[36mgwt new <branch> <base>\033[0m Create new branch from base",
        "help.setting_detail": "Setting Command Details:",
        "help.setting_detail_1": "  \033[36mgwt setting\033[0m           Interactive settings for current repo",
        "help.setting_detail_2": "  \033[36mgwt setting -g\033[0m        Interactive global settings",
        "help.setting_detail_3": "  \033[36mgwt setting -s\033[0m        Show effective config",
        "help.setting_detail_4": "  \033[36mgwt setting -i\033[0m        Initialize config (tool detection)",
        "help.setting_detail_5": "  \033[36mgwt setting -r\033[0m        Reset config to defaults",
        "help.examples": "Examples:",
        "help.ex1": "  1. Create a worktree by interactive branch selection",
        "help.ex2": "  2. Create a worktree for feature/login",
        "help.ex3": "  3. Create a new branch from develop",
        "help.ex4": "  4. AI Code Review (default: Codex, uncommitted changes)",
        "help.ex5": "  5. Review staged changes (Gemini)",
        "help.ex6": "  6. Configure gwt settings",
        # Core command descriptions (for help)
        "help.cmd.list": "List all worktrees",
        "help.cmd.init": "Print shell/Pwsh wrapper (for pipx installs)",
        "help.cmd.status": "Status summary for repo and submodules",
        "help.cmd.new": "Create worktree (interactive if no args, local/remote branches)",
        "help.cmd.remove": "Remove worktree (default: current; safely jumps back)",
        "help.cmd.prune": "Prune stale worktree records",
        "help.cmd.cd": "Interactive jump (fzf recommended)",
        "help.cmd.update": "Update gwt (git pull --ff-only)",
        "help.cmd.setting": "Configure gwt settings (--global for global)",
        "help.cmd.merge": "Merge branches (interactive, conflict handling)",
        "help.cmd.commit": "Quick commit (lazygit/gitui)",
        # Completion descriptions
        "completion.list": "List worktrees",
        "completion.init": "Print wrapper",
        "completion.init.shell": "Shell (zsh/bash/powershell)",
        "completion.status": "Show status",
        "completion.new": "Create worktree",
        "completion.remove": "Remove worktree",
        "completion.prune": "Prune stale worktrees",
        "completion.cd": "Jump to worktree",
        "completion.update": "Update gwt tool",
        "completion.merge": "Merge branches",
        "completion.commit": "Quick commit",
        "completion.setting": "Configure settings",
        "completion.review": "AI Code Review",
        "completion.help": "Show help",
        "completion.branch": "Branch",
        "completion.setting.global": "Edit global config",
        "completion.setting.show": "Show current config",
        "completion.setting.init": "Initialize with detection",
        "completion.setting.reset": "Reset to defaults",
        "completion.review.tool.claude": "Anthropic Claude",
        "completion.review.tool.codex": "OpenAI Codex",
        "completion.review.tool.gemini": "Google Gemini",
        "completion.review.staged": "Review staged changes",
        "completion.review.last": "Review last commit",
        "completion.review.commit": "Review specific commit diff",
        "completion.review.branch": "Review branch diff",
        "completion.review.tool": "Select AI tool",
        "completion.review.model": "Override model",
        "completion.global.lang": "Language (zh/en)",
        "completion.global.yes": "Auto-confirm prompts (safe cases)",
        "completion.global.dry_run": "Preview without executing",
        "completion.global.debug": "Debug mode (stack traces)",
        # Config
        "config.load_failed": "⚠️  Failed to load config: {error}",
        "config.save_failed": "❌ Failed to save config: {error}",
        # Utils
        "utils.gitignore.added": "📝 Added {entry} to .gitignore",
        "utils.gitignore.created": "📝 Created .gitignore with {entry} entry",
        # Status
        "status.main_repo": "📌 Main Repository:",
        "status.submodules": "📦 Submodules:",
        "status.submodule_clean": "✅ {path} [{branch}] (clean)",
        # Update
        "update.updating_from": "🔄 Updating gwt from: {path}",
        "update.not_git_repo": "❌ gwt is not installed from a git repository.",
        "update.cd_to": "📂 Changed to: {path}",
        "update.fetching": "📡 Fetching updates...",
        "update.pulling": "⬇️  Pulling with --ff-only...",
        "update.already_up_to_date": "✅ gwt is already up to date.",
        "update.updated_ok": "✅ gwt updated successfully!",
        "update.failed": "❌ Failed to update. You may need to resolve conflicts manually.",
        # Worktree
        "worktree.fetch_remote": "🔄 Fetching remote branches...",
        "worktree.no_branches": "❌ No branches found.",
        "worktree.no_branches_available": "❌ No branches available.",
        "worktree.branches_title": "📋 Available Branches:",
        "worktree.branches_header": "   [L]=Local  [R]=Remote\n",
        "worktree.branches_tip": "   Or enter a new branch name to create it.\n",
        "worktree.fzf_prompt_branch": "Select Branch > ",
        "worktree.fzf_prompt_worktree": "Select Worktree > ",
        "worktree.fzf_prompt_remove": "Select Worktree to Remove > ",
        "worktree.fzf_header_branches": "  [L]=Local  [R]=Remote",
        "worktree.create_worktree": "⚙️  Creating Worktree: {path} (Branch: {branch})...",
        "worktree.branch_used": "\n⚠️  Branch '{branch}' is already used by worktree:",
        "worktree.you_can": "\n💡 You can:",
        "worktree.you_can_1": "   1. Use 'gwt cd' to jump to that worktree",
        "worktree.you_can_2": "   2. Use 'gwt rm' to remove it first",
        "worktree.branch_exists_local": "🔹 Branch '{branch}' exists locally. Checking out...",
        "worktree.found_remote_branch": "🔍 Found remote branch '{branch}'.",
        "worktree.use_remote_prompt": "📌 Use remote branch? [Y/n]: ",
        "worktree.create_tracking": "🔹 Creating local branch '{branch}' tracking '{remote}'...",
        "worktree.create_from_base": "🔹 Creating new branch '{branch}' from {base}...",
        "worktree.branch_not_found_create": "🔹 Branch '{branch}' not found. Creating from {base}...",
        "worktree.create_failed": "❌ Failed to create worktree.",
        "worktree.created_ok": "✅ Worktree created successfully. Jumping in...",
        "worktree.submodules_detected": "📦 Detected submodules. Updating...",
        "worktree.sync_submodules": "🔄 Syncing submodule branches...",
        "worktree.submodule_checkout_local": "🔹 Submodule {path}: Checking out existing local branch {branch}",
        "worktree.submodule_found_remote": "🔍 Submodule {path}: Found remote branch '{remote}'.",
        "worktree.submodule_use_remote_prompt": "   📌 Use remote branch for {path}? [Y/n]: ",
        "worktree.submodule_create_tracking": "🔹 Submodule {path}: Creating branch tracking '{remote}'",
        "worktree.submodule_create_local": "✨ Submodule {path}: Creating new local branch {branch}",
        # Remove/cd/prune
        "worktree.no_worktrees": "❌ No worktrees found.",
        "worktree.no_removable": "⚠️  No removable worktrees found (only main worktree exists).",
        "worktree.worktrees_title": "📋 Available Worktrees:",
        "worktree.remove_select_prompt": "Select number to remove (1-{n}): ",
        "worktree.remove_prepare": "🗑️  Preparing to remove: {path}",
        "worktree.remove_confirm": "Confirm? (y/N) ",
        "worktree.remove_inside_warn": "⚠️  You are currently inside the worktree to be deleted.",
        "worktree.remove_switching": "📂 Switching to main worktree first...",
        "worktree.remove_rerun": "💡 Please run the remove command again after switching.",
        "worktree.remove_main_forbidden": "⚠️  Cannot remove main worktree ({path}).",
        "worktree.remove_no_match": "❌ No worktree found matching '{key}'.",
        "worktree.removed_ok": "✅ Removed.",
        "worktree.remove_failed": "❌ Failed to remove worktree.",
        "worktree.prune_start": "🧹 Pruning stale worktree entries...",
        "worktree.prune_ok": "✅ Prune completed.",
        "worktree.prune_failed": "❌ Prune failed.",
        "worktree.cd_prompt": "Select number (1-{n}): ",
        "worktree.invalid_selection": "❌ Invalid selection.",
        # Review
        "review.preparing": "👀 Preparing {tool} review for: {mode} ...",
        "review.mode.uncommitted": "Uncommitted changes (Staged + Unstaged)",
        "review.mode.staged": "Staged changes only",
        "review.mode.last": "Last commit (HEAD)",
        "review.mode.commit": "Diff {sha} vs HEAD",
        "review.mode.branch": "Diff {branch} vs HEAD",
        "review.using_model": "🤖 Using Model: {model}",
        "review.wsl_missing": "❌ WSL not found but WSL mode is enabled in config.",
        "review.wsl_disable_tip": "💡 Run 'gwt setting' to disable WSL mode, or install WSL.",
        "review.cli_missing": "❌ '{tool}' CLI not found. Please install it first.",
        "review.no_changes": "✅ No changes detected to review.",
        "review.diff_captured": "📝 Diff captured in {path}",
        "review.launching": "🚀 Launching {tool}...",
        "review.wsl_running": "🐧 Running in WSL mode...",
        "review.cancelled": "\nReview cancelled.",
        # Review prompt
        "review.prompt": """Please review the code changes captured in '{diff_file}'.

Review dimensions:
1. 🧐 Logic & Semantics:
   - Does the code implement the intended behavior? Is the logic sound?
   - Naming/semantics: are names clear and intention-revealing?
2. ⚡ Simplification & Deduplication:
   - Dead/redundant code
   - Duplicate wheel detection: is there similar existing code already?
   - Cognitive load: can it be made clearer and simpler?
3. 🌳 Visualization: provide an ASCII flow diagram of the updated logic.

Output requirements:
- If you spot simplification opportunities or duplication, mark them with \"💡 Optimization/Duplication Alert\".
- Keep the response well-structured.

Context:
- Project: {project}
- Branch: {branch}
""",
        # Merge
        "merge.uncommitted": "❌ You have uncommitted changes. Please commit or stash them first.",
        "merge.uncommitted_tip": "   Run 'gwt commit' to commit or 'git stash' to stash.",
        "merge.title": "🔀 GWT Merge - Branch Merge Tool",
        "merge.source_prompt": "Source Branch",
        "merge.target_prompt": "Target Branch",
        "merge.select_source": "📌 Select SOURCE branch (changes FROM):",
        "merge.select_target": "📌 Select TARGET branch (merge INTO):",
        "merge.current_branch": "   💡 Current branch: {branch}",
        "merge.confirm": "🔀 Will merge '{source}' INTO '{target}'",
        "merge.continue_prompt": "   Continue? (y/N): ",
        "merge.checkout": "📂 Checking out {branch}...",
        "merge.checkout_failed": "❌ Failed to checkout {branch}",
        "merge.merging": "🔀 Merging {source} into {target}...",
        "merge.ok": "✅ Merge completed successfully!",
        "merge.aborted": "❌ Merge aborted.",
        "merge.failed": "❌ Merge failed:",
        "merge.conflicts_detected": "\n⚠️  Merge conflicts detected in {n} file(s):",
        "merge.choose_action": "Choose an action:",
        "merge.action1": "  [1] Manual - re-check conflict status",
        "merge.action2": "  [2] Merge tool - open configured tool",
        "merge.action3": "  [3] Open lazygit",
        "merge.action4": "  [4] Abort - abort merge",
        "merge.select_1_4": "\n> Select (1-4): ",
        "merge.recheck": "🔍 Re-checking conflict status...",
        "merge.opening": "🔧 Opening {tool}...",
        "merge.opening_fallback": "🔧 Opening {tool} (fallback)...",
        "merge.no_merge_tool": "❌ No merge tool available. Please install one.",
        "merge.lazygit_missing": "❌ lazygit not installed",
        "merge.aborting": "🔄 Aborting merge...",
        "merge.all_resolved": "✅ All conflicts resolved!",
        "merge.completing": "   Completing merge...",
        "merge.submodules_check": "📦 Checking submodules...",
        "merge.submodule_has_conflicts": "⚠️  Submodule '{path}' has conflicts",
        "merge.submodule_enter": "   Entering submodule to resolve...",
        "merge.submodule_aborted": "❌ Submodule merge aborted",
        "merge.submodule_resolved": "✅ Submodule '{path}' conflicts resolved",
        # Commit
        "commit.title": "📝 GWT Commit - Quick Commit Tool",
        "commit.no_changes": "✅ No changes to commit.",
        "commit.status": "📋 Current status:",
        "commit.launching": "🚀 Launching {tool}...",
        "commit.launching_fallback": "🚀 Launching {tool} (fallback)...",
        "commit.no_tui": "💡 No git TUI tool found. Using simple commit mode.",
        "commit.no_tui_tip": "   Install 'lazygit' or 'gitui' for better experience.",
        "commit.stage_all": "Stage all changes? (y/N): ",
        "commit.message": "Commit message: ",
        "commit.ok": "✅ Committed successfully!",
        "commit.failed": "❌ Commit failed:",
        # Setting
        "setting.current_config": "📋 Current Configuration:",
        "setting.global_path": "   (Global: {path})",
        "setting.effective": "   (Effective: global + repo merged)",
        "setting.reset_ok": "✅ Configuration reset to defaults.",
        "setting.reset_confirm": "⚠️  Delete {path}? (y/N): ",
        "setting.no_config_file": "⚠️  No configuration file found.",
        "setting.not_git_repo": "❌ Not in a git repository",
        "setting.scope.global": "Global",
        "setting.scope.repo": "Repository",
        "setting.ui_lang": "🌐 UI Language",
        "setting.ui_lang_tip": "   💡 auto=follow environment/terminal; `--lang` overrides temporarily",
        "setting.ui_lang_prompt": "   > Select (1-3, Enter to keep): ",
        "setting.ui_lang_auto": "auto",
        "setting.ui_lang_zh": "zh",
        "setting.ui_lang_en": "en",
        "setting.init_title": "🔧 Initializing {scope} Configuration",
        "setting.title": "🔧 GWT Settings ({scope})",
        "setting.detecting": "🔍 Detecting available tools...",
        "setting.review_tools": "🤖 Review Tools:",
        "setting.cli_tools": "🔧 CLI Tools:",
        "setting.main_branch": "📌 Main Branch",
        "setting.main_branch_prompt": "Main Branch",
        "setting.current": "   Current: {value}",
        "setting.select_tip": "   💡 Select from existing branches or enter a new name",
        "setting.changed_to": "   → Changed to: {value}",
        "setting.worktree_dir": "📁 Worktree Directory",
        "setting.worktree_dir_tip": "   💡 Variables: {repo_name} = repo name, {sep} = path separator",
        "setting.enter_new": "   > Enter new value (or press Enter to keep): ",
        "setting.default_review_tool": "🤖 Default Review Tool",
        "setting.available": "   Available:",
        "setting.select_1_3": "   > Select (1-3 or press Enter to keep): ",
        "setting.wsl_mode": "🐧 WSL Mode (Windows only)",
        "setting.wsl_current": "   Current: {value}",
        "setting.wsl_available": "   WSL Available: {value}",
        "setting.wsl_tip": "   💡 Only Codex needs WSL; Claude and Gemini can run on Windows directly",
        "setting.wsl_toggle": "   > Toggle WSL mode? (y/N): ",
        "setting.wsl_to": "   → WSL mode: {value}",
        "setting.submodule_settings": "📦 Submodule Settings",
        "setting.submodule_found": "   Found {n} submodule(s):",
        "setting.submodule_select": "   > Select to edit (number) or press Enter to skip: ",
        "setting.submodule_editing": "\n   Editing: {path}",
        "setting.submodule_current_main": "   Current main branch: {branch}",
        "setting.submodule_tip": "   💡 Select from submodule's branches or enter a new name",
        "setting.submodule_main_branch_prompt": "Main Branch for {path}",
        "setting.no_submodules": "   No submodules found.",
        "setting.saved_to": "✅ Settings saved to {path}",
        "setting.save_failed": "❌ Failed to save settings",
        # Branch picker
        "setting.branch_available": "   Available branches:",
        "setting.branch_select_or_enter": "   > Select (1-{n}) or enter branch name, Enter to keep: ",
        "setting.branch_enter_name": "   > Enter branch name (current: {branch}): ",
    },
}


_current_lang: str | None = None


def _normalize_lang(value: str | None) -> str | None:
    if not value:
        return None
    v = value.strip().lower()
    if not v:
        return None

    # common forms: zh_CN, zh-CN, zh_Hans, en_US.UTF-8
    v = v.replace("-", "_")
    if v.startswith("zh"):
        return "zh"
    if v.startswith("en"):
        return "en"
    if v in ("cn", "zh_cn", "zh_hans", "zh_hans_cn", "zh_sg", "zh_tw", "zh_hk"):
        return "zh"
    return None


def detect_language() -> str:
    override = _normalize_lang(os.environ.get("GWT_LANG"))
    if override in SUPPORTED_LANGS:
        return override

    for env_key in ("LC_ALL", "LANGUAGE", "LANG"):
        lang = _normalize_lang(os.environ.get(env_key))
        if lang in SUPPORTED_LANGS:
            return lang

    # OS locale fallback (Windows/macOS/Linux)
    try:
        loc = locale.getlocale()  # e.g. ('en_US', 'UTF-8') or (None, None)
        lang = _normalize_lang(loc[0] if loc else None)
        if lang in SUPPORTED_LANGS:
            return lang
    except Exception:
        pass

    return "en"


def get_language() -> str:
    global _current_lang
    if _current_lang is None:
        _current_lang = detect_language()
    return _current_lang


def set_language(lang: str) -> None:
    global _current_lang
    normalized = _normalize_lang(lang) or lang.strip().lower()
    _current_lang = normalized if normalized in SUPPORTED_LANGS else "en"


def t(key: str, **kwargs: Any) -> str:
    lang = get_language()
    table = _TRANSLATIONS.get(lang, {})
    text = table.get(key) or _TRANSLATIONS["en"].get(key) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
