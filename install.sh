#!/usr/bin/env bash

set -e

INSTALL_DIR="$HOME/.local/bin"
TOOLS_DIR="$(cd "$(dirname "$0")/tools" && pwd)"

mkdir -p "$INSTALL_DIR"

while IFS= read -r -d '' file; do
    name="$(basename "$file" .py)"

    if ! head -n 1 "$file" | grep -q '^#!.*python'; then
        echo "[!] Skipping $file: missing Python shebang"
        echo "[!] Please add '#!/usr/bin/env python3' at the beginning of the file"
        continue
    fi

    echo "[+] Installing $name"

    chmod +x "$file"
    ln -sf "$file" "$INSTALL_DIR/$name"

done < <(find "$TOOLS_DIR" -type f -name "*.py" -print0)

echo
echo "[+] Done."