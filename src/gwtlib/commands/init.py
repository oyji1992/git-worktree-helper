# -*- coding: utf-8 -*-
"""Emit shell wrapper snippets (useful for pipx installs).

The wrapper enables:
- directory switching via GWT_CD_FILE
- completion by delegating to `gwt __complete`
"""

from __future__ import annotations

import os
import sys

from gwtlib.i18n import t


def _detect_shell():
    if os.name == "nt":
        return "powershell"
    shell = (os.environ.get("SHELL") or "").lower()
    if "zsh" in shell:
        return "zsh"
    if "bash" in shell:
        return "bash"
    return "zsh"


def _snippet_zsh():
    return r"""# --- BEGIN GWT (pipx) ---
function gwt() {
  local tmp_cd_file="/tmp/gwt_cd_target_$$"
  GWT_CD_FILE="$tmp_cd_file" command gwt "$@"
  local ret=$?
  if [ -f "$tmp_cd_file" ]; then
    local target_dir
    target_dir="$(cat "$tmp_cd_file")"
    if [ -n "$target_dir" ]; then
      cd "$target_dir"
    fi
    rm -f "$tmp_cd_file"
  fi
  return $ret
}

function _gwt_zsh_completions() {
  local -a reply
  local cmd="gwt"
  local cur="${words[CURRENT]}"
  local prev="${words[CURRENT-1]}"

  if [[ $CURRENT -eq 2 ]]; then
    cmd="gwt"
    prev=""
  else
    cmd="${words[2]}"
  fi

  local result=("${(@f)$(command gwt __complete --cmd=\"$cmd\" --cur=\"$cur\" --prev=\"$prev\")}")
  if [[ -n "$result" ]]; then
    _describe 'command' result
  fi
}
compdef _gwt_zsh_completions gwt
# --- END GWT (pipx) ---
"""


def _snippet_bash():
    return r"""# --- BEGIN GWT (pipx) ---
gwt() {
  local tmp_cd_file="/tmp/gwt_cd_target_$$"
  GWT_CD_FILE="$tmp_cd_file" command gwt "$@"
  local ret=$?
  if [ -f "$tmp_cd_file" ]; then
    local target_dir
    target_dir="$(cat "$tmp_cd_file")"
    if [ -n "$target_dir" ]; then
      cd "$target_dir"
    fi
    rm -f "$tmp_cd_file"
  fi
  return $ret
}

_gwt_bash_completions() {
  local cur prev cmd
  COMPREPLY=()
  cur="${COMP_WORDS[COMP_CWORD]}"
  prev="${COMP_WORDS[COMP_CWORD-1]}"

  if [[ $COMP_CWORD -eq 1 ]]; then
    cmd="gwt"
    prev=""
  else
    cmd="${COMP_WORDS[1]}"
  fi

  local opts
  opts="$(command gwt __complete --cmd=\"$cmd\" --cur=\"$cur\" --prev=\"$prev\" | cut -d':' -f1)"
  local IFS=$'\n'
  COMPREPLY=( $(compgen -W "$opts" -- "$cur") )
}
complete -F _gwt_bash_completions gwt
# --- END GWT (pipx) ---
"""


def _snippet_powershell():
    return r"""# --- BEGIN GWT (pipx) ---
function gwt {
  param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Args
  )

  $exe = (Get-Command gwt -CommandType Application -ErrorAction SilentlyContinue)
  if (-not $exe) { Write-Error "Cannot find gwt executable"; return }

  $tmpCdFile = [System.IO.Path]::GetTempFileName()
  $env:GWT_CD_FILE = $tmpCdFile

  try {
    & $exe.Source @Args
  } finally {
    if (Test-Path $tmpCdFile) {
      $targetDir = Get-Content -Path $tmpCdFile -ErrorAction SilentlyContinue
      if (-not [string]::IsNullOrWhiteSpace($targetDir)) {
        $targetDir = $targetDir.Trim()
        if (Test-Path $targetDir) { Set-Location -Path $targetDir }
      }
      Remove-Item -Path $tmpCdFile -ErrorAction SilentlyContinue
    }
    Remove-Item Env:\GWT_CD_FILE -ErrorAction SilentlyContinue
  }
}

if (Get-Command Register-ArgumentCompleter -ErrorAction SilentlyContinue) {
  Register-ArgumentCompleter -Native -CommandName gwt -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)

    $exe = (Get-Command gwt -CommandType Application -ErrorAction SilentlyContinue)
    if (-not $exe) { return }

    $inputStr = $commandAst.ToString()
    $tokens = $inputStr.Split(" ", [System.StringSplitOptions]::RemoveEmptyEntries)
    $cmd = "gwt"
    $prev = ""

    $trimmedLen = $inputStr.TrimEnd().Length
    $isCompletingNewArg = $cursorPosition -gt $trimmedLen

    if ($tokens.Count -gt 1) {
      if ($tokens.Count -eq 2 -and -not $isCompletingNewArg) {
        $cmd = "gwt"
      } else {
        $cmd = $tokens[1]
        if ($tokens.Count -gt 2) {
          $prev = $tokens[$tokens.Count - 1]
          if (-not $isCompletingNewArg) {
            $prev = $tokens[$tokens.Count - 2]
          }
        }
      }
    }

    try {
      $results = & $exe.Source __complete --cmd=$cmd --cur=$wordToComplete --prev=$prev
      foreach ($res in $results) {
        $parts = $res -split ":", 2
        $val = $parts[0]
        $desc = if ($parts.Count -gt 1) { $parts[1] } else { $val }
        [System.Management.Automation.CompletionResult]::new($val, $val, 'ParameterValue', $desc)
      }
    } catch {}
  }
}
# --- END GWT (pipx) ---
"""


def cmd_init(args):
    shell = (getattr(args, "shell", None) or "").lower() or _detect_shell()
    if shell in ("zsh",):
        sys.stdout.write(_snippet_zsh())
        return 0
    if shell in ("bash",):
        sys.stdout.write(_snippet_bash())
        return 0
    if shell in ("powershell", "pwsh", "ps"):
        sys.stdout.write(_snippet_powershell())
        return 0

    sys.stderr.write(t("generic.invalid_selection") + "\n")
    return 2

