# Contributing to sectools

Thanks for contributing to **sectools**!

`sectools` is a community-driven collection of small, practical security tools. If you have a useful tool that you think others may benefit from, feel free to contribute it.

## Tool requirements

Currently, `sectools` supports **Python (`.py`) tools only**.

### 1. Add a Python shebang

Every Python tool must start with:

```python
#!/usr/bin/env python3
```

This allows the installer to make the tool directly executable.

### 2. Use a unique tool name

Please make sure your tool name does not conflict with an existing tool in the repository.

For example, if `tools/injector.py` already exists, do not submit another tool named `injector.py`.

Choose a clear and descriptive name that reflects what the tool does.

### 3. Keep tools practical

Tools **Don't** need to be large, highly advanced, or built as a full framework.

Small and focused tools are encouraged.

However, please avoid submitting **toy tools** that are only demonstrations, trivial wrappers, or impractical for real-world security research.

A good contribution should provide some practical value to security researchers, bug bounty hunters, penetration testers, or other users.

### 4. Keep the scope focused

A tool should generally focus on one specific task rather than trying to become a large framework.

For example:

* Recon utilities
* URL or parameter fuzzers
* Scanners
* Enumeration tools
* Web security testing utilities
* Exploit helpers
* Payload generators
* Other useful security research utilities

## Adding a tool

Place your Python tool inside the `tools/` directory:

```text
sectools/
├── tools/
│   ├── injector.py
│   ├── yourtool.py
│   └── ...
├── install.sh
├── uninstall.sh
└── CONTRIBUTING.md
```

Make sure the file starts with the required shebang:

```python
#!/usr/bin/env python3
```

Then test that it works correctly before submitting your contribution.

## Pull requests

When submitting a pull request:

* Explain what the tool does.
* Explain how it can be used.
* Make sure the tool works as expected.
* Make sure the tool name does not conflict with existing tools.
* Keep the contribution focused and reasonably self-contained.

There is no requirement for a contribution to be huge or highly sophisticated. **Useful and practical is more important than large or complex.**

## License

By contributing to `sectools`, you agree that your contribution will be licensed under the **MIT License**.

Only submit code that you have the right to license under the MIT License.


Thanks for helping build `sectools`!