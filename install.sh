#!/usr/bin/env bash

# Installer script for Python tools.

# Installs tools from tools/ into ~/.local/bin.

set -e

tools=("injector" "racer" "subto")

INSTALL_DIR="$HOME/.local/bin"
TOOLS_DIR="$(cd "$(dirname "$0")/tools" && pwd)"

mkdir -p "$INSTALL_DIR"

echo
echo "Files will be installed to: $INSTALL_DIR"

while true; do
read -r -p "Are you sure you want to install? [y/n] " confirm

case "$confirm" in
    y|Y)
        break
        ;;
    n|N)
        echo "[!] Installation cancelled."
        exit 0
        ;;
    *)
        echo "[!] Please enter y or n."
        ;;
esac

done

echo

missing_shebang=()

install_tool() {
# Install a tool
local name="$1"
local file
local tool_dir
local venv_dir
local launcher

# All-in-one tool:
#   tools/<name>.py
if [ -f "$TOOLS_DIR/$name.py" ]; then
    file="$TOOLS_DIR/$name.py"

# Architecture tool:
#   tools/<name>/main.py
elif [ -f "$TOOLS_DIR/$name/main.py" ]; then
    file="$TOOLS_DIR/$name/main.py"
    tool_dir="$TOOLS_DIR/$name"

else
    echo "[!] Tool not found: $name"
    return
fi

if ! head -n 1 "$file" | grep -q '^#!.*python'; then
    missing_shebang+=("$file")
    return
fi

# Tool has its own requirements:
#   tools/<name>/requirements.txt
if [ -n "$tool_dir" ] && [ -f "$tool_dir/requirements.txt" ]; then

    venv_dir="$tool_dir/.venv"

    # Create virtual environment.
    if [ ! -d "$venv_dir" ]; then
        echo "[*] Creating environment for $name"
        python3 -m venv "$venv_dir"
    fi

    # Install dependencies.
    echo "[*] Installing dependencies for $name"
    "$venv_dir/bin/python" -m pip install -q \
        -r "$tool_dir/requirements.txt"

    # Create launcher.
    launcher="$INSTALL_DIR/$name"

    cat > "$launcher" <<EOF
#!/usr/bin/env bash

exec "$venv_dir/bin/python" "$file" "\$@"
EOF

    chmod +x "$launcher"

else

    # No private environment.
    chmod +x "$file"
    ln -sf "$file" "$INSTALL_DIR/$name"

fi

echo "[+] $name installed"

}

if [ -n "$1" ]; then
install_tool "$1"
else
for tool in "${tools[@]}"; do
install_tool "$tool"
done
fi

if [ ${#missing_shebang[@]} -gt 0 ]; then
echo

for file in "${missing_shebang[@]}"; do
    relative="${file#"$TOOLS_DIR"/}"
    echo "[!] tools/$relative missing Python shebang"
done

fi

echo
echo "[+] Done."