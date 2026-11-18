#!/usr/bin/env python3
"""Syntax-check the JavaScript module inside a single-file room planner.

Usage: python3 check_syntax.py path/to/index.html

Extracts every <script type="module"> block and runs `node --check` on it.
A passing check does not prove the page renders – runtime errors such as
using a `const` before its declaration still need a browser (or careful review).
"""
import pathlib
import re
import subprocess
import sys
import tempfile


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    html = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
    blocks = re.findall(r'<script type="module">(.*?)</script>', html, re.S)
    if not blocks:
        print("No <script type=\"module\"> block found.")
        return 1
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        for i, code in enumerate(blocks, 1):
            path = pathlib.Path(tmp) / f"module-{i}.mjs"
            path.write_text(code, encoding="utf-8")
            res = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
            if res.returncode == 0:
                print(f"module {i}: syntax OK ({code.count(chr(10)) + 1} lines)")
            else:
                ok = False
                print(f"module {i}: SYNTAX ERROR\n{res.stderr}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
