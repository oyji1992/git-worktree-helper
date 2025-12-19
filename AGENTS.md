# git-worktree-helper (gwt) 维护指南

## 项目结构

- `src/gwt.py`：Python CLI 入口（统一异常出口、全局参数、argparse 生成）
- `src/gwtlib/`：Python Core（可维护的模块化实现）
  - `src/gwtlib/registry.py`：命令注册表（命令/别名/参数/handler 的单一真相）
  - `src/gwtlib/config.py`：配置读写与探测（默认/全局/仓库合并）
  - `src/gwtlib/config_schema.py`：配置 schema 校验与迁移
  - `src/gwtlib/errors.py`：结构化错误（统一出口与退出码）
  - `src/gwtlib/utils.py`：通用工具（git 调用、彩色输出、cd 通信等）
  - `src/gwtlib/help.py`：`gwt --help` 的自定义帮助信息
  - `src/gwtlib/completion.py`：Shell 自动补全入口（`__complete` 子命令）
  - `src/gwtlib/commands/`：各子命令实现（一个命令一个模块）
- `shell/gwt.zsh` / `shell/gwt.ps1`：Shell wrapper
  - 负责目录切换（通过环境变量 `GWT_CD_FILE` 与临时文件通信）
  - 负责调用 `__complete` 实现自动补全

## 新增命令（Checklist）

1. 在 `src/gwtlib/commands/` 新增模块，例如 `foo.py`，并提供 `cmd_foo(args)`。
2. 在 `src/gwtlib/registry.py` 注册 `CommandSpec`（name/aliases/args/func/help_key/completion_key）。
3. 在 `src/gwtlib/i18n.py` 补齐 `help.cmd.<cmd>` 与 `completion.<cmd>` 的中英文文案。
4. 若需要额外帮助说明（“命令详情/示例”）：更新 `src/gwtlib/help.py`。
5. 若需要动态补全（branch/commit/worktree 等）：更新 `src/gwtlib/completion.py`。
6. 更新 `README.md` 的使用说明/示例（对用户可见的行为变更必须同步文档）。
7. 视情况更新 `src/gwtlib/tests/`（推荐最少覆盖：i18n、registry、completion 的关键路径）。

## 修改命令（Checklist）

- 若修改了命令名/别名/参数：
  - 优先修改 `src/gwtlib/registry.py`，并同步 `src/gwtlib/i18n.py`、`README.md`。
- 若修改了全局参数（例如新增 `--foo`）：
  - 修改 `src/gwt.py`（common parser）+ `src/gwtlib/completion.py`（`_global_flags()`）+ `src/gwtlib/i18n.py`（`completion.global.*`）+ `README.md`。
- 若修改了 `cd` 行为：
  - 必须保持 `GWT_CD_FILE` 协议不变（Python 子进程不能直接改变父 Shell 的工作目录）。

## 快速自检

- `python3 src/gwt.py --help`
- `python3 src/gwt.py __complete --cmd=gwt --cur= --prev=`
- `python3 src/gwt.py __complete --cmd=rv --cur= --prev=-t`
- `python3 src/gwt.py init --shell zsh | head -n 3`
- `python3 -m unittest discover -s src/gwtlib/tests -q`
