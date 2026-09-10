# sectools

A community-driven collection of small security tools.

Have a useful security tool? Contribute it to the collection.

Recon tools, scanners, fuzzers, exploit helpers, web security tools, and other practical utilities are welcome. The goal is simple: build a shared toolbox where anyone can contribute and everyone can benefit.

> **Note:** Currently, only Python (`.py`) tools are supported.


## Structure

```text
sectools/
├── install.sh
├── LICENSE
├── README.md
└── tools/
    ├── injector.py
    └── ...
```

All tools are kept under the `tools/` directory.

`install.sh` recursively scans `tools/` for Python tools and installs them into `~/.local/bin`.

## Installation

Clone the repository:

```bash
git clone https://github.com/Just4Hunter/sectools.git
cd sectools
```

Run the installer to install all available tools:

```bash
./install.sh
```

After installation, tools can be run directly from the terminal:

```bash
injector
```

### Install a specific tool

To install only a specific tool:

```bash
./install.sh injector
```

This installs `injector.py` and makes it available as:

```bash
injector
```

### Uninstall

Remove a specific tool:

```bash
./uninstall.sh injector
```

Remove all installed tools:

```bash
./uninstall.sh
```

Uninstalling removes the installed symlinks only. The source files inside `tools/` are preserved.

## Adding a Tool

Add a Python script anywhere inside `tools/`.

For example:

```text
tools/
├── injector.py
└── recon/
    └── subenum.py
```

Make sure the script starts with a Python shebang:

```python
#!/usr/bin/env python3
```

Then run:

```bash
./install.sh
```

The installer will automatically discover and install the tool.

## Tools

| Tool       | Description                                                   |
| ---------- | ------------------------------------------------------------- |
| `injector` | Generic injection testing tool using custom payload wordlists |

More tools will be added over time.

## Philosophy

Keep it small.

These tools are built to solve specific problems encountered during security research. They are intentionally kept small, practical, and focused rather than trying to become a large all-in-one security framework.

## Disclaimer

These tools are intended for authorized security testing and research only.

Do not use them against systems without permission.

## License

MIT License