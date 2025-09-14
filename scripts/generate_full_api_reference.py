#!/usr/bin/env python3
"""Generate an exhaustive API reference (API_REFERENCE_FULL.md) including every endpoint,
its input parameters (path/query/body), success response schema, error envelope, and
whether responses are paginated.

Usage:
    python scripts/generate_full_api_reference.py [--output API_REFERENCE_FULL.md]

The script attempts to read a cached openapi json (openapi_cached.json) else fetches
from http://localhost:8000/openapi.json.
"""
from __future__ import annotations
import json
import sys
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.request

OPENAPI_URL = "http://localhost:8000/openapi.json"
CACHE_FILE = Path("openapi_cached.json")
DEFAULT_OUTPUT = Path("API_REFERENCE_FULL.md")

# Fields in the standard success envelope we expect
SUCCESS_ENVELOPE_FIELDS = ["success", "message", "data", "meta", "timestamp"]
ERROR_ENVELOPE_FIELDS = ["success", "error_code", "message", "details", "timestamp"]


def load_spec() -> Dict[str, Any]:
    if CACHE_FILE.exists() and CACHE_FILE.stat().st_size > 0:
        return json.loads(CACHE_FILE.read_text())
    try:
        with urllib.request.urlopen(OPENAPI_URL) as resp:  # nosec - dev usage
            data = resp.read().decode()
        spec = json.loads(data)
        CACHE_FILE.write_text(json.dumps(spec, indent=2))
        return spec
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: Could not load OpenAPI spec: {e}", file=sys.stderr)
        sys.exit(1)


def is_paginated(op: Dict[str, Any]) -> bool:
    # Heuristic: look for standard pagination query params or meta schema in responses
    params = op.get("parameters", [])
    for p in params:
        if p.get("in") == "query" and p.get("name") in {"page", "per_page", "limit", "offset"}:
            return True
    # Check 200 schema for meta structure referencing total/count/page
    responses = op.get("responses", {})
    resp_200 = responses.get("200") or responses.get("201")
    if resp_200:
        content = resp_200.get("content", {})
        for mt in content.values():
            schema = mt.get("schema", {})
            if references_pagination(schema):
                return True
    return False


def references_pagination(schema: Dict[str, Any]) -> bool:
    if not schema:
        return False
    # Walk schema for 'meta' object with pagination keys
    stack = [schema]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            if cur.get("type") == "object" and "properties" in cur:
                props = cur["properties"]
                if "meta" in props:
                    meta = props["meta"].get("properties", {}) if isinstance(props["meta"], dict) else {}
                    if any(k in meta for k in ("total", "count", "page", "pages", "per_page", "limit", "offset")):
                        return True
                # push nested properties
                for v in props.values():
                    if isinstance(v, dict):
                        stack.append(v)
            elif cur.get("type") in ("array",) and "items" in cur:
                stack.append(cur["items"])
            for k in ("oneOf", "anyOf", "allOf"):
                if k in cur and isinstance(cur[k], list):
                    stack.extend(cur[k])
    return False


def format_params(params: List[Dict[str, Any]]) -> str:
    if not params:
        return "None"
    lines = ["| Name | In | Required | Type | Description |", "|------|----|----------|------|-------------|"]
    for p in params:
        schema = p.get("schema", {})
        p_type = schema.get("type") or schema.get("$ref", "")
        desc_raw = p.get('description', '') or ''
        desc = desc_raw.replace('|', '\\|')
        lines.append(f"| {p.get('name')} | {p.get('in')} | {p.get('required', False)} | {p_type} | {desc} |")
    return "\n".join(lines)


def extract_body_schema(op: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    rq = op.get("requestBody")
    if not rq:
        return None
    content = rq.get("content", {})
    # Prefer JSON media types
    for mt in ("application/json", "application/*+json"):
        if mt in content:
            return content[mt].get("schema")
    # Fallback first content entry
    if content:
        return next(iter(content.values())).get("schema")
    return None


def schema_to_table(schema: Dict[str, Any], components: Dict[str, Any]) -> str:
    if not schema:
        return "None"
    resolved = resolve_schema(schema, components)
    if not resolved or resolved.get("type") != "object" or "properties" not in resolved:
        return f"``{json.dumps(resolved, indent=2)}``"
    lines = ["| Field | Type | Required | Description |", "|-------|------|----------|-------------|"]
    required = set(resolved.get("required", []))
    for name, prop in resolved.get("properties", {}).items():
        p_type = infer_type(prop)
        desc_raw = prop.get("description", "") or ""
        desc = desc_raw.replace('|','\\|')
        lines.append(f"| {name} | {p_type} | {name in required} | {desc} |")
    return "\n".join(lines)


def infer_type(prop: Dict[str, Any]) -> str:
    if "$ref" in prop:
        return prop["$ref"].split("/")[-1]
    t = prop.get("type")
    if t == "array":
        items = prop.get("items", {})
        return f"array[{infer_type(items)}]"
    if t == "object" and "properties" not in prop:
        return "object"
    return t or "object"


def resolve_schema(schema: Dict[str, Any], components: Dict[str, Any]) -> Dict[str, Any]:
    # Basic $ref resolver (no circular handling needed for doc use)
    if "$ref" in schema:
        ref = schema["$ref"].split("/")[-1]
        return components.get("schemas", {}).get(ref, {})
    # Handle allOf merges simply (shallow)
    if "allOf" in schema:
        merged: Dict[str, Any] = {"type": "object", "properties": {}, "required": []}
        for part in schema["allOf"]:
            res = resolve_schema(part, components)
            if res.get("properties"):
                merged["properties"].update(res["properties"])
            if res.get("required"):
                merged["required"].extend(res["required"])
        return merged
    return schema


def extract_success_response(op: Dict[str, Any], components: Dict[str, Any]) -> str:
    responses = op.get("responses", {})
    # Prefer 200 then 201
    for code in ("200", "201"):
        if code in responses:
            content = responses[code].get("content", {})
            for mt, mtdata in content.items():
                schema = mtdata.get("schema")
                if schema:
                    return schema_to_table(schema, components)
    return "None"


def generate(spec: Dict[str, Any]) -> str:
    components = spec.get("components", {})
    lines: List[str] = []
    lines.append("# SOFinance Full API Reference\n")
    lines.append("> Exhaustive machine-derived reference. For narrative overview see API_REFERENCE.md. Regenerate via `python scripts/generate_full_api_reference.py`.\n")
    info = spec.get("info", {})
    lines.append(f"**Title:** {info.get('title','')}  ")
    lines.append(f"**Version:** {info.get('version','')}  ")
    lines.append(f"**Total Endpoints:** {len(spec.get('paths', {}))}\n")

    lines.append("## Conventions\n")
    lines.append("- All responses use the unified envelope unless explicitly stated.\n- Pagination indicated where detected.\n- Error envelope fields: `" + ", ".join(ERROR_ENVELOPE_FIELDS) + "`.\n")

    # Group by first path segment
    paths: Dict[str, Dict[str, Any]] = spec.get("paths", {})
    grouped: Dict[str, List[tuple[str, str, Dict[str, Any]]]] = {}
    for path, path_item in paths.items():
        seg = path.strip("/").split("/")[0] or "root"
        for method, op in path_item.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete", "options", "head"}:
                continue
            grouped.setdefault(seg, []).append((path, method.upper(), op))

    for seg in sorted(grouped):
        lines.append(f"\n## Segment: /{seg}\n")
        for path, method, op in sorted(grouped[seg], key=lambda x: (x[0], x[1])):
            summary = op.get("summary") or op.get("operationId", "")
            tags = ", ".join(op.get("tags", []))
            auth = "Yes" if any(sec for sec in op.get("security", spec.get("security", []))) else "Maybe"  # global security may apply
            paginated = is_paginated(op)
            lines.append(f"### {method} {path}\n")
            if summary:
                lines.append(f"**Summary:** {summary}\n")
            if tags:
                lines.append(f"**Tags:** {tags}\n")
            lines.append(f"**Auth Required:** {auth}\n")
            lines.append(f"**Paginated:** {paginated}\n")

            # Parameters
            all_params: List[Dict[str, Any]] = []
            if op.get("parameters"):
                all_params.extend(op["parameters"])
            # Path-level parameters
            # (Already merged per spec, but we'll merge explicitly)
            # Build parameter table
            lines.append("**Path & Query Parameters**\n")
            lines.append(format_params(all_params))

            # Request body
            body_schema = extract_body_schema(op)
            lines.append("\n**Request Body Schema**\n")
            if body_schema:
                lines.append(schema_to_table(body_schema, components))
            else:
                lines.append("None")

            # Success response
            lines.append("\n**Success Response Schema (Envelope `data` field focus)**\n")
            lines.append(extract_success_response(op, components))

            # Error envelope (standard)
            lines.append("\n**Error Envelope**\n")
            lines.append("| Field | Type | Description |\n|-------|------|-------------|\n| success | boolean | Always false on error |\n| error_code | string | Stable machine error code |\n| message | string | Human-readable summary |\n| details | object|array|null | Extra validation or domain details |\n| timestamp | string | ISO-8601 UTC timestamp |")

            lines.append("\n---\n")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    spec = load_spec()
    markdown = generate(spec)
    args.output.write_text(markdown)
    print(f"Wrote {args.output} ({len(markdown.splitlines())} lines)")


if __name__ == "__main__":  # pragma: no cover
    main()
