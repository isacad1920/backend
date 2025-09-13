"""Enforcement test: prevent reintroduction of raw `resp.body =` mutations.

Rationale:
    Direct assignment to `resp.body` on a JSONResponse can leave a stale
    Content-Length header, triggering runtime errors under Uvicorn like:
        RuntimeError: Response content longer than Content-Length

    We added `app.core.response.set_json_body` to centralize safe mutation.
    This test ensures future code changes use that helper instead of raw
    assignments. If you legitimately need to stream or rebuild the response,
    construct a new Response/JSONResponse or call the helper.

Allowed:
    - Any code inside `app/core/response.py` (helper definitions)
    - Comments containing the text (ignored by AST-based detection)

Detection strategy:
    Parse each Python file under `app/` (excluding `app/core/response.py`),
    walk the AST and flag assignments where:
        target is an Attribute with attr == 'body' AND its value is a
        Name/id 'resp'. This robustly ignores textual false positives in
        strings/comments.

    We also keep a simple fallback regex scan for resiliency. If either
    mechanism finds matches, the test fails with a list of offending lines.
"""
from __future__ import annotations

import ast
import pathlib
import re

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
APP_DIR = PROJECT_ROOT / "app"
ALLOWED_FILE = APP_DIR / "core" / "response.py"

RAW_PATTERN = re.compile(r"resp\.body\s*=")

def _ast_offenders(path: pathlib.Path) -> list[tuple[int,str]]:
    offenders: list[tuple[int,str]] = []
    try:
        source = path.read_text(encoding="utf-8")
    except Exception:
        return offenders
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return offenders
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Attribute) and target.attr == "body":
                    # target.value should be a Name 'resp'
                    if isinstance(target.value, ast.Name) and target.value.id == "resp":
                        # Exclude response.py itself
                        if path != ALLOWED_FILE:
                            # Get source line
                            try:
                                line = source.splitlines()[node.lineno - 1].rstrip()
                            except Exception:
                                line = "<unavailable>"
                            offenders.append((node.lineno, line))
    return offenders

def _regex_offenders(path: pathlib.Path) -> list[tuple[int,str]]:
    offenders: list[tuple[int,str]] = []
    try:
        for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if RAW_PATTERN.search(line):
                # Skip comments or lines inside response.py
                stripped = line.lstrip()
                if stripped.startswith('#'):
                    continue
                if path == ALLOWED_FILE:
                    continue
                offenders.append((idx, line.rstrip()))
    except Exception:
        pass
    return offenders

def test_no_direct_resp_body_mutation():
    py_files = [p for p in APP_DIR.rglob('*.py') if p.is_file()]
    all_offenders: dict[str, list[tuple[int,str]]] = {}
    for file_path in py_files:
        if file_path == ALLOWED_FILE:
            continue
        ast_hits = _ast_offenders(file_path)
        regex_hits = _regex_offenders(file_path)
        # Combine unique by line number
        combined = {ln: text for ln, text in ast_hits + regex_hits}
        if combined:
            all_offenders[str(file_path.relative_to(PROJECT_ROOT))] = sorted((ln, txt) for ln, txt in combined.items())
    if all_offenders:
        formatted = "\n".join(
            f"  {fname}:\n" + "\n".join(f"    L{ln}: {txt}" for ln, txt in entries)
            for fname, entries in sorted(all_offenders.items())
        )
        raise AssertionError(
            "Direct `resp.body =` assignments detected (use set_json_body instead):\n" + formatted
        )
