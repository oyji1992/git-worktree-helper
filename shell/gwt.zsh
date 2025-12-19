#!/bin/bash
# This script should be sourced (e.g., 'source gwt.zsh')

# --- 1. Locate gwt.py at source time ---
# We capture this ONCE when the script is sourced, so completion functions know where to look.

if [ -n "$ZSH_VERSION" ]; then
    _GWT_SOURCE_PATH="${(%):-%x}"
elif [ -n "$BASH_VERSION" ]; then
    _GWT_SOURCE_PATH="${BASH_SOURCE[0]}"
else
    _GWT_SOURCE_PATH="$0"
fi

_GWT_SCRIPT_DIR="$(cd "$(dirname "$_GWT_SOURCE_PATH")" && pwd)"
_GWT_REPO_DIR="$(cd "$_GWT_SCRIPT_DIR/.." && pwd)"
export _GWT_PY_PATH="$_GWT_REPO_DIR/src/gwt.py"

# --- 2. Main Wrapper Function ---
function gwt() {
    local tmp_cd_file="/tmp/gwt_cd_target_$$"

    # Fallback check if env var was lost
    local py_script="${_GWT_PY_PATH}"
    if [ -z "$py_script" ] || [ ! -f "$py_script" ]; then
        # Try to guess based on current location (dev mode)
        if [ -f "./src/gwt.py" ]; then
            py_script="./src/gwt.py"
        else
            echo "⚠️  gwt: Could not locate gwt.py. Expected at: $_GWT_PY_PATH"
            return 1
        fi
    fi

    # Run Python script
    GWT_CD_FILE="$tmp_cd_file" python3 "$py_script" "$@"
    local ret=$?

    # Check if cd request was made
    if [ -f "$tmp_cd_file" ]; then
        local target_dir=$(cat "$tmp_cd_file")
        if [ -n "$target_dir" ]; then
            cd "$target_dir"
        fi
        rm -f "$tmp_cd_file"
    fi

    return $ret
}

# --- 3. Zsh Completion ---
if [[ -n "$ZSH_VERSION" ]]; then
    function _gwt_zsh_completions() {
        local -a reply
        local cmd="gwt"
        local cur="${words[CURRENT]}"
        local prev="${words[CURRENT-1]}"
        
        # Context detection
        if [[ $CURRENT -eq 2 ]]; then
            cmd="gwt"
            prev=""
        else
            cmd="${words[2]}"
        fi

        # Use the captured path
        if [ -f "$_GWT_PY_PATH" ]; then
            local result=("${(@f)$(python3 "$_GWT_PY_PATH" __complete --cmd="$cmd" --cur="$cur" --prev="$prev")}")
            if [[ -n "$result" ]]; then
                # Support descriptions (value:desc)
                _describe 'command' result
            fi
        fi
    }
    # Register
    compdef _gwt_zsh_completions gwt
fi

# --- 4. Bash Completion ---
if [[ -n "$BASH_VERSION" ]]; then
    function _gwt_bash_completions() {
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

        if [ -f "$_GWT_PY_PATH" ]; then
            local opts=$(python3 "$_GWT_PY_PATH" __complete --cmd="$cmd" --cur="$cur" --prev="$prev")
            # Bash doesn't support descriptions easily, strip them (value:desc -> value)
            opts=$(echo "$opts" | cut -d':' -f1)
            local IFS=$'\n'
            COMPREPLY=( $(compgen -W "$opts" -- "$cur") )
        fi
    }
    # Register
    complete -F _gwt_bash_completions gwt
fi
