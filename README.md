# sectools

A personal collection of small security tools, built and shared for anyone who finds them useful.

The tools focus on security research, bug bounty hunting, reconnaissance, and web security testing. Each tool is designed to be small, practical, and focused on a specific task.

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
git clone https://github.com/Pupsix/sectools.git
cd sectools
```

Run the installer:

```bash
./install.sh
```

After installation, tools can be run directly from the terminal:

```bash
injector
```

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