#!/usr/bin/env bash

set -e

INSTALL_DIR="$HOME/.local/bin"
TOOLS_DIR="$(cd "$(dirname "$0")/tools" && pwd)"

if [ -n "$1" ]; then
file="$TOOLS_DIR/$1.py"

if [ ! -f "$file" ]; then
    echo "[!] Tool not found: $1"
    exit 1
fi

target="$INSTALL_DIR/$1"

if [ ! -L "$target" ]; then
    echo "[!] Tool is not installed: $1"
    exit 1
fi

echo "[+] Uninstalling $1"

rm "$target"

else
while IFS= read -r -d '' file; do
name="$(basename "$file" .py)"
target="$INSTALL_DIR/$name"

    if [ -L "$target" ]; then
        echo "[+] Uninstalling $name"
        rm "$target"
    fi

done < <(find "$TOOLS_DIR" -type f -name "*.py" -print0)

fi

echo
echo "[+] Done."