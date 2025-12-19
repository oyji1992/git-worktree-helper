#!/bin/bash
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Detect shell config file
detect_shell_config() {
    local shell_name=""
    
    if command -v ps >/dev/null 2>&1; then
        shell_name=$(ps -p $PPID -o comm= 2>/dev/null || ps -p $PPID -o args= 2>/dev/null)
        shell_name="${shell_name%% *}"
        shell_name="${shell_name##*/}"
        shell_name="${shell_name#-}"
    fi

    if [[ -z "$shell_name" || "$shell_name" == "login" || "$shell_name" == "sudo" ]]; then
        shell_name="${SHELL##*/}"
    fi

    if [[ "$shell_name" == *"zsh"* ]]; then
        echo "$HOME/.zshrc"
        return
    elif [[ "$shell_name" == *"bash"* ]]; then
        echo "$HOME/.bashrc"
        return
    fi

    if [[ -f "$HOME/.zshrc" ]]; then
        echo "$HOME/.zshrc"
    elif [[ -f "$HOME/.bashrc" ]]; then
        echo "$HOME/.bashrc"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "$HOME/.zshrc"
    else
        echo "$HOME/.bashrc"
    fi
}

TARGET_FILE=$(detect_shell_config)

START_MARK="# --- BEGIN GWT CONFIG ---"
END_MARK="# --- END GWT CONFIG ---"

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}       GWT Uninstall Script${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Check if gwt config exists
if ! grep -q "$START_MARK" "$TARGET_FILE" 2>/dev/null && ! grep -q "gwt.zsh" "$TARGET_FILE" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  gwt configuration not found in $TARGET_FILE.${NC}"
    echo ""
    exit 0
fi

# Show what will be removed
echo -e "${YELLOW}📋 The following configuration will be removed:${NC}"
echo ""
echo -e "${CYAN}📄 File: $TARGET_FILE${NC}"
echo -e "${GRAY}   Content to be removed:${NC}"
echo -e "${GRAY}   ─────────────────────────────────────${NC}"

# Extract and display the content to be removed
in_block=false
while IFS= read -r line; do
    if [[ "$line" == *"$START_MARK"* ]]; then
        in_block=true
    fi
    
    if [[ "$in_block" == true ]]; then
        echo -e "${RED}   │ $line${NC}"
    elif [[ "$line" == *"gwt.zsh"* ]]; then
        echo -e "${RED}   │ $line${NC}"
    fi
    
    if [[ "$line" == *"$END_MARK"* ]]; then
        in_block=false
    fi
done < "$TARGET_FILE"

echo -e "${GRAY}   ─────────────────────────────────────${NC}"
echo ""

# Ask for confirmation
echo -e "${YELLOW}⚠️  This action will:${NC}"
echo -e "${GRAY}   1. Create a backup of the config file (.bak)${NC}"
echo -e "${GRAY}   2. Remove the gwt configuration blocks shown above${NC}"
echo ""

read -p "❓ Are you sure you want to continue? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${RED}❌ Uninstall cancelled.${NC}"
    exit 0
fi

echo ""

# Perform the uninstall
echo -e "${CYAN}🔧 Removing gwt from $TARGET_FILE ...${NC}"

# Backup
BACKUP_PATH="$TARGET_FILE.bak"
cp "$TARGET_FILE" "$BACKUP_PATH"
echo -e "${GRAY}   📦 Backup created: $BACKUP_PATH${NC}"

# Remove gwt configuration
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' '/source .*gwt\.zsh/d' "$TARGET_FILE"
    sed -i '' "/$START_MARK/,/$END_MARK/d" "$TARGET_FILE"
else
    sed -i '/source .*gwt\.zsh/d' "$TARGET_FILE"
    sed -i "/$START_MARK/,/$END_MARK/d" "$TARGET_FILE"
fi

# Remove trailing empty lines
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS sed
    perl -i -pe 'chomp if eof' "$TARGET_FILE" 2>/dev/null || true
else
    # GNU sed
    sed -i -e :a -e '/^\n*$/{$d;N;ba' -e '}' "$TARGET_FILE" 2>/dev/null || true
fi

echo -e "${GREEN}   ✅ Removed${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Uninstall complete!${NC}"
echo -e "${GRAY}   Restart your terminal or run:${NC}"
echo -e "${CYAN}   source $TARGET_FILE${NC}"
echo -e "${GREEN}========================================${NC}"
