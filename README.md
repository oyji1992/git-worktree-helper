# Git Worktree Helper (gwt)

一个跨平台的 Git Worktree 工作流 CLI 封装工具，旨在让并行开发变得无缝且高效。它自动化了目录管理，智能处理子模块，并集成了 AI 驱动的代码评审功能。

## 功能特性

- **🚀 无缝 Worktree 管理**：轻松创建、列出、跳转和删除 Worktree。
- **📂 保持工作区整洁**：自动将所有 Worktree 管理在隐藏的 `.worktree/` 目录下，保持项目根目录清爽。
- **🔗 智能子模块**：在创建新 Worktree 时自动同步和更新子模块。
- **🤖 AI 代码评审**：内置支持 **Claude**、**OpenAI Codex** 和 **Google Gemini**，直接在 CLI 中评审你的代码变更。
- **⚡ 交互式导航**：完美支持 `fzf`，实现快速的 Worktree 切换。
- **💻 跨平台**：支持 macOS/Linux (Zsh/Bash) 和 Windows (PowerShell)。

## 安装

### macOS / Linux (Zsh / Bash)

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/git-worktree-helper.git ~/git-worktree-helper

# 2. 运行安装脚本
# 该脚本会自动检测你的 Shell (zsh/bash) 并更新 .zshrc/.bashrc
bash ~/git-worktree-helper/install.sh

# 3. 应用更改
source ~/.zshrc  # 或 ~/.bashrc
```

### Windows (PowerShell)

```powershell
# 1. 克隆仓库
git clone https://github.com/yourusername/git-worktree-helper.git $HOME/git-worktree-helper

# 2. 运行安装脚本
& "$HOME/git-worktree-helper/install.ps1"

# 3. 重启 PowerShell 或重载配置文件
. $PROFILE
```

### pipx (推荐给 Python 用户)

`pipx` 会把 `gwt` 安装成全局可用的命令。

```bash
pipx install git-worktree-helper
```

由于 `cd` 需要在父 Shell 中执行，建议把 wrapper 注入到你的 profile：

- Zsh：`gwt init --shell zsh >> ~/.zshrc && source ~/.zshrc`
- Bash：`gwt init --shell bash >> ~/.bashrc && source ~/.bashrc`
- PowerShell：`gwt init --shell powershell >> $PROFILE; . $PROFILE`

## 使用指南

### 🌲 基础命令

```bash
# 列出所有活跃的 Worktree
gwt list      # 别名: gwt ls

# 显示主仓库及子模块的状态验证信息
gwt status    # 别名: gwt st

# 清理已失效的 Worktree 记录
gwt prune
```

### 🌿 创建与管理 Worktree

```bash
# 创建一个新分支 'feature/ui' 并自动跳转进入
# - 会在 .worktree/feature-ui 创建 Worktree
# - 自动处理子模块初始化
gwt new feature/ui

# 删除当前 Worktree (会安全地先跳回主仓库)
gwt remove    # 别名: gwt rm

# 删除指定的 Worktree (支持 fzf 交互式选择，或通过部分名称匹配)
gwt remove feature/ui
```

### 🏃 导航

```bash
# 交互式跳转到另一个 Worktree
# (强烈推荐安装 fzf 以获得最佳体验)
gwt cd        # 别名: gwt jump
```

### 🤖 AI 代码评审

在提交代码前，使用 AI 辅助进行代码评审。

**语法:** `gwt review [选项]` (别名: `gwt rv`)

**选项:**
- `--tool, -t <name>`: 选择 AI 工具: `claude` (默认), `codex`, `gemini`。
- `--staged, -s`: 仅评审暂存区 (Staged) 的变更。
- `--last, -l`: 评审上一次提交 (HEAD)。
- `--commit, -c <sha>`: 评审指定 Commit 与 HEAD 之间的变更。
- `--branch, -b <name>`: 评审指定分支与 HEAD 之间的变更。

**示例:**

```bash
# 使用 Claude (默认) 评审未提交的变更 (暂存区 + 未暂存区)
gwt review

# 使用 Gemini 仅评审暂存区的变更
gwt review --staged --tool gemini

# 评审上一次提交
gwt review --last

# 使用 Codex 对比当前 HEAD 与 main 分支的差异
gwt review --branch main --tool codex
```

## 环境要求

- **Git** (必需)
- **Python 3** (必需)
- **fzf** (推荐用于交互式选择)
- **AI 工具** (可选 - `gwt review` 需要):
  - `claude` CLI
  - `gemini` CLI
  - `codex` CLI

## 语言 (i18n)

`gwt` 会根据系统/终端的 locale 自动选择语言（当前支持中文/英文）。

- 强制英文：`GWT_LANG=en gwt --help`
- 强制中文：`GWT_LANG=zh gwt --help`
- 也可持久化设置：`gwt setting` → `🌐 UI Language`（会写入配置 `ui.lang`）

## 全局选项

- `--lang {zh|en}`：临时切换语言（优先级最高）
- `--dry-run`：仅展示将执行的命令，不做任何修改
- `--yes`, `-y`：在安全场景下自动确认（如 `remove` 的确认、`new` 远端分支默认选择等）
- `--debug`：显示堆栈与更多诊断信息（同时启用 `GWT_DEBUG=1`）

## 它是如何工作的

- **目录结构**：Worktree 会创建在你项目根目录下的 `.worktree/` 文件夹中。
- **Gitignore**：工具会自动将 `.worktree/` 添加到你的 `.gitignore` 文件中，防止意外提交。
- **Shell 集成**：Shell 包装脚本 (`gwt.zsh` / `gwt.ps1`) 负责处理目录切换 (`cd`)，因为子进程 (Python) 无法直接更改父 Shell 的工作目录。

## 项目结构（维护者）

- `src/gwt.py`：Python CLI 入口（统一异常出口、全局参数、argparse 生成）
- `src/gwtlib/`：Python Core
  - `src/gwtlib/registry.py`：命令注册表（命令/别名/参数/handler 的单一真相）
  - `src/gwtlib/commands/`：子命令实现（按模块拆分）
  - `src/gwtlib/help.py`：`gwt --help` 自定义帮助信息
  - `src/gwtlib/completion.py`：自动补全逻辑（`gwt __complete`）
  - `src/gwtlib/config.py`：配置（默认/全局/仓库合并，加载/保存时会 migrate + sanitize）
  - `src/gwtlib/config_schema.py`：配置 schema 校验与迁移（`configVersion`）
  - `src/gwtlib/utils.py`：通用工具函数（git 调用、彩色输出、cd 通信等）

## 如何新增/修改命令

命令体系是 **registry 驱动** 的：根命令列表（help/completion）从 `src/gwtlib/registry.py` 生成，避免三处同步。

### 新增命令（维护者）

1. `src/gwtlib/commands/<cmd>.py`：实现 `cmd_<cmd>(args)`（建议返回 `int` 作为退出码）
2. `src/gwtlib/registry.py`：新增 `CommandSpec`（name/aliases/args/func/help_key/completion_key）
3. `src/gwtlib/i18n.py`：补齐 `help.cmd.<cmd>` 与 `completion.<cmd>` 的中英文文案
4. 若需要“命令详情/示例”：更新 `src/gwtlib/help.py`
5. 若需要动态补全（分支/commit/worktree 等）：更新 `src/gwtlib/completion.py`
6. 更新 `README.md` 使用示例（用户可见行为变更必须同步）
7. 视情况在 `src/gwtlib/tests/` 增加/更新单测

### 修改命令（维护者）

- 改命令名/别名/参数：优先改 `src/gwtlib/registry.py`，并同步 `src/gwtlib/i18n.py`、`README.md`
- 改交互文案/提示：同步 `src/gwtlib/i18n.py`
- 改补全行为：同步 `src/gwtlib/completion.py`

## License

MIT. See `LICENSE`.
