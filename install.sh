#!/bin/bash
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detect shell config file
detect_shell_config() {
    local shell_name=""
    
    # 1. Try to detect parent process (the shell that called this script)
    if command -v ps >/dev/null 2>&1; then
        # Handle different ps syntax for BSD/macOS vs GNU/Linux
        # -p $PPID matches parent process
        # -o comm= (or command=) gets the command name
        shell_name=$(ps -p $PPID -o comm= 2>/dev/null || ps -p $PPID -o args= 2>/dev/null)
        shell_name="${shell_name%% *}" # Remove args
        shell_name="${shell_name##*/}" # Remove path (basename)
        shell_name="${shell_name#-}"   # Remove leading hyphen (login shell)
    fi

    # 2. Fallback to SHELL env var if ps failed or gave generic result
    if [[ -z "$shell_name" || "$shell_name" == "login" || "$shell_name" == "sudo" ]]; then
        shell_name="${SHELL##*/}"
    fi

    # 3. Determine target file based on detected name
    if [[ "$shell_name" == *"zsh"* ]]; then
        echo "$HOME/.zshrc"
        return
    elif [[ "$shell_name" == *"bash"* ]]; then
        echo "$HOME/.bashrc"
        return
    fi

    # 4. Fallback based on file existence and OS preference
    if [[ -f "$HOME/.zshrc" ]]; then
        echo "$HOME/.zshrc"
    elif [[ -f "$HOME/.bashrc" ]]; then
        echo "$HOME/.bashrc"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "$HOME/.zshrc" # macOS default
    else
        echo "$HOME/.bashrc" # Linux default
    fi
}

TARGET_FILE=$(detect_shell_config)

echo "🔧 Configuring gwt to $TARGET_FILE ..."

START_MARK="# --- BEGIN GWT CONFIG ---"
END_MARK="# --- END GWT CONFIG ---"

# Backup
cp "$TARGET_FILE" "$TARGET_FILE.bak"

# Clean up function
clean_file() {
    local file="$1"
    # 1. Remove legacy simple lines containing 'gwt.zsh' (cleanup old versions)
    # 2. Remove the managed block
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' '/source .*gwt\.zsh/d' "$file"
        sed -i '' "/$START_MARK/,/$END_MARK/d" "$file"
    else
        sed -i '/source .*gwt\.zsh/d' "$file"
        sed -i "/$START_MARK/,/$END_MARK/d" "$file"
    fi
}

clean_file "$TARGET_FILE"

# Append new block
{
    echo ""
    echo "$START_MARK"
    echo "# Do not edit this block manually. It is managed by install.sh"
    echo "source \"$REPO_DIR/shell/gwt.zsh\""
    echo "$END_MARK"
} >> "$TARGET_FILE"

echo "✅ Configuration updated (Backup created at $TARGET_FILE.bak)."
echo "👉 Run 'source $TARGET_FILE' to apply."