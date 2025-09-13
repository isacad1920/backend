"""Audit script to verify all FastAPI route handlers use standardized response helpers.

Scans `app/modules/**/routes.py` for endpoint functions (decorated with
`@router.<method>(...)`) and checks their bodies for usage of one of:
  - success_response(
  - paginated_response(
  - ResponseBuilder.success(

Allowed exception patterns (no enforcement):
  - Returns FileResponse / StreamingResponse / WebSocket endpoints
  - Returns bare Response with status_code=304 (caching short-circuit)

Outputs a report listing any handlers that appear to return raw dicts or
JSONResponse constructions without the helper utilities.

Heuristic only (static text scan) – keeps implementation lightweight without AST.
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(__file__)
MODULES_DIR = os.path.join(ROOT, 'app', 'modules')

ROUTE_FILE_PATTERN = re.compile(r"routes\.py$")
ROUTE_DECORATOR = re.compile(r"^@router\.(get|post|put|delete|patch|options|head)\b")
FUNC_DEF_RE = re.compile(r"^async\s+def\s+(\w+)\s*\(")

SUCCESS_PATTERNS = [
    'success_response(',
    'paginated_response(',
    'ResponseBuilder.success('
]

ERROR_PATTERNS = [
    'error_response(',
    'ResponseBuilder.error(',
    'ResponseBuilder.already_exists(',
    'ResponseBuilder.not_found(',
    'ResponseBuilder.validation_error('
]

ALLOW_KEYWORDS = [
    'FileResponse(', 'StreamingResponse(', 'WebSocket', 'WebSocketRoute', 'status_code=304'
]

def scan_file(path: str):
    """Return list of (handler_name, snippet) lacking standardized helpers.

    First a quick read of the file content, then a simple split-based heuristic.
    Removed prior unused state variables to satisfy linter.
    """
    with open(path, encoding='utf-8') as fh:
        lines = fh.readlines()
    content = ''.join(lines)
    chunks = re.split(r"(async\s+def\s+\w+\s*\([^:]+:)", content)
    # The split keeps separators; pair them
    suspicious = []
    for idx in range(1, len(chunks), 2):
        header = chunks[idx]
        body = chunks[idx+1] if idx+1 < len(chunks) else ''
        name_match = re.match(r"async\s+def\s+(\w+)", header)
        if not name_match:
            continue
        name = name_match.group(1)
        # Only consider if preceding decorators in original file include @router.
        # Simple search backwards from header start in original content
        header_index = content.find(header)
        pre_segment = content[max(0, header_index-500):header_index]
        if '@router.' not in pre_segment:
            continue
        text_block = header + body
        has_success = any(p in text_block for p in SUCCESS_PATTERNS)
        has_error = any(p in text_block for p in ERROR_PATTERNS)
        if has_success or has_error:
            continue
        if any(a in text_block for a in ALLOW_KEYWORDS):
            continue
        # Likely missing standardized response usage
        # Try to extract first return line for context
        ret_match = re.search(r"return\s+(.+)", body)
        snippet = ret_match.group(0) if ret_match else '<no return found>'
        suspicious.append((name, snippet.strip()))
    return suspicious

def main():
    route_files = []
    for root, _, files in os.walk(MODULES_DIR):
        for f in files:
            if ROUTE_FILE_PATTERN.search(f):
                route_files.append(os.path.join(root, f))
    route_files.sort()
    all_suspicious = []
    for f in route_files:
        suspicious = scan_file(f)
        if suspicious:
            for name, snippet in suspicious:
                all_suspicious.append((f, name, snippet))
    if not all_suspicious:
        print(
            "All route handlers appear to use standardized response helpers or are allowed exceptions."
        )
        return 0
    print("Potential non-standard handlers detected (heuristic):\n")
    for path, name, snippet in all_suspicious:
        rel = os.path.relpath(path, ROOT)
        print(f"- {rel}:{name} -> {snippet}")
    print("\nReview the above handlers to ensure intentional exceptions only.")
    return 1

if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
