#!/usr/bin/env bash

# Uninstaller script for Python tools.

set -e

tools=("injector" "racer" "subto")

INSTALL_DIR="$HOME/.local/bin"
TOOLS_DIR="$(cd "$(dirname "$0")/tools" && pwd)"

echo
echo "Files will be uninstalled from: $INSTALL_DIR"

while true; do
    read -r -p "Are you sure you want to uninstall? [y/n] " confirm

    case "$confirm" in
        y|Y)
            break
            ;;
        n|N)
            echo "[!] Uninstallation cancelled."
            exit 0
            ;;
        *)
            echo "[!] Please enter y or n."
            ;;
    esac
done

echo

uninstall_tool() {
    local name="$1"
    local target="$INSTALL_DIR/$name"
    local tool_dir="$TOOLS_DIR/$name"

    if [ ! -e "$target" ] && [ ! -L "$target" ]; then
        echo "[!] Tool is not installed: $name"
        return
    fi

    rm -f "$target"

    if [ -d "$tool_dir/.venv" ]; then
        echo "[*] Removing environment for $name"
        rm -rf "$tool_dir/.venv"
    fi

    echo "[+] $name uninstalled"
}

if [ -n "$1" ]; then
    uninstall_tool "$1"
else
    for tool in "${tools[@]}"; do
        uninstall_tool "$tool"
    done
fi

echo
echo "[+] Done."