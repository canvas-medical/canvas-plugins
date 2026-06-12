r"""Generate the agent-tools section of the SDK documentation.

Walks :data:`canvas_sdk.agents.standard_tools`, reads each tool's
runtime definition (name, description, JSON-Schema args) and the
docs-only metadata stashed by the helpers (model, returns_description,
backing class), and renders three sentinel-delimited blocks into the
target markdown file:

- ``<!-- AUTOGEN:categories ... -->`` — index of @category to tool names
- ``<!-- AUTOGEN:reads ... -->`` — per-read-tool detail
- ``<!-- AUTOGEN:writes ... -->`` — per-write-tool detail

The hand-written prose around the blocks (concepts, examples, design
tips) is preserved untouched. CI runs the generator with ``--check``;
authors run with ``--write`` after touching the catalog.

Usage::

    uv run python -m canvas_sdk.agents._docs_generator --check \\
        --target /path/to/documentation/collections/_sdk/agents/tools.md

    uv run python -m canvas_sdk.agents._docs_generator --write \\
        --target /path/to/documentation/collections/_sdk/agents/tools.md
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from canvas_sdk.agents import standard_tools

# Sentinel markers. Each block has a START and END comment; the
# generator replaces the contents between them, preserving the
# surrounding prose verbatim.
_SENTINEL_NAMES = ("categories", "reads", "writes")
_SENTINEL_RE = re.compile(
    r"(<!-- AUTOGEN:(?P<name>[a-z_]+) START -->)"
    r".*?"
    r"(<!-- AUTOGEN:(?P=name) END -->)",
    re.DOTALL,
)


def _is_write_kind(kind: str | None) -> bool:
    """Tools tagged 'add_effect' or 'originate_command' are write tools."""
    return kind in {"add_effect", "originate_command"}


def _classify_tools() -> tuple[list[str], list[str]]:
    """Split tool names into (reads, writes) preserving registration order.

    Tools without a metadata 'kind' (e.g., the demographics scalar
    registered via the raw ``tool()`` decorator) default to reads —
    they don't produce Effects.
    """
    reads: list[str] = []
    writes: list[str] = []
    for definition in standard_tools.definitions():
        name = definition["name"]
        kind = standard_tools.metadata_for(name).get("kind")
        if _is_write_kind(kind):
            writes.append(name)
        else:
            reads.append(name)
    return reads, writes


def _format_categories_block() -> str:
    """Render the @category index — one bullet per category."""
    reads, writes = _classify_tools()
    all_tools = reads + writes
    # Walk every tool, building category → tools mapping. We iterate
    # tools (not categories) so the within-category ordering matches
    # the registration order of the catalog itself.
    category_to_tools: dict[str, list[str]] = {}
    for name in all_tools:
        for category in standard_tools.categories_for(name):
            category_to_tools.setdefault(category, []).append(name)

    if not category_to_tools:
        return "_No categories declared._"

    lines: list[str] = []
    for category in sorted(category_to_tools):
        names = category_to_tools[category]
        rendered_names = ", ".join(f"`{n}`" for n in names)
        lines.append(
            f"- **`@{category}`** ({len(names)} tool{'s' if len(names) != 1 else ''}): {rendered_names}"
        )
    return "\n".join(lines)


def _arg_table_row(prop_name: str, prop_schema: dict[str, Any], required: bool) -> str:
    """Build one row of the per-tool args markdown table."""
    type_str = prop_schema.get("type", "?")
    fmt = prop_schema.get("format")
    if fmt:
        type_str = f"{type_str} ({fmt})"
    enum = prop_schema.get("enum")
    if enum:
        type_str = f"{type_str} (enum)"
    if type_str == "array" and "items" in prop_schema:
        items = prop_schema["items"]
        inner = items.get("type", "?")
        if items.get("enum"):
            inner = f"{inner} (enum)"
        type_str = f"array of {inner}"
    required_str = "yes" if required else "no"
    description = prop_schema.get("description", "").strip().replace("\n", " ")
    # Markdown table cells: escape pipe characters that would break the row.
    description = description.replace("|", "\\|")
    enum_suffix = ""
    if enum:
        enum_suffix = f" One of: {', '.join(f'`{v}`' for v in enum)}."
    return f"| `{prop_name}` | {type_str} | {required_str} | {description}{enum_suffix} |"


def _format_tool_block(name: str) -> str:
    """Render the per-tool markdown block: heading, description, args, returns, backing."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == name)
    metadata = standard_tools.metadata_for(name)
    categories = standard_tools.categories_for(name)

    parts: list[str] = []
    parts.append(f"#### `{name}`")
    parts.append("")
    if categories:
        category_tags = " · ".join(f"`@{c}`" for c in categories)
        parts.append(f"**Category:** {category_tags}")
        parts.append("")
    # Description: keep paragraphs together but normalize internal whitespace.
    description = " ".join(definition["description"].split())
    parts.append(description)
    parts.append("")

    schema = definition.get("input_schema", {})
    properties: dict[str, Any] = schema.get("properties", {}) or {}
    required = set(schema.get("required", []) or [])
    if properties:
        parts.append("**Arguments:**")
        parts.append("")
        parts.append("| Name | Type | Required | Description |")
        parts.append("|---|---|---|---|")
        for prop_name, prop_schema in properties.items():
            parts.append(_arg_table_row(prop_name, prop_schema, prop_name in required))
        parts.append("")
    else:
        parts.append("**Arguments:** none.")
        parts.append("")

    returns = metadata.get("returns_description")
    if returns:
        parts.append(f"**Returns:** {returns}")
        parts.append("")

    backing = _format_backing(metadata)
    if backing:
        parts.append(backing)
        parts.append("")

    return "\n".join(parts).rstrip()


def _format_backing(metadata: dict[str, Any]) -> str | None:
    """Render the 'backed by' line — model for reads, Command/Effect for writes."""
    model = metadata.get("model")
    if model is not None:
        return f"**Backing data model:** `{model.__name__}`."
    command_class = metadata.get("command_class")
    if command_class is not None:
        return f"**Backing Command:** `{command_class.__name__}`."
    effect_class = metadata.get("effect_class")
    if effect_class is not None:
        return f"**Backing Effect:** `{effect_class.__name__}`."
    return None


def _format_tool_section(names: Iterable[str]) -> str:
    """Render a sequence of per-tool blocks separated by blank lines."""
    blocks = [_format_tool_block(name) for name in names]
    if not blocks:
        return "_No tools in this section._"
    return "\n\n".join(blocks)


def _build_blocks() -> dict[str, str]:
    """Produce the rendered content for each AUTOGEN block, keyed by name."""
    reads, writes = _classify_tools()
    return {
        "categories": _format_categories_block(),
        "reads": _format_tool_section(reads),
        "writes": _format_tool_section(writes),
    }


def _substitute(text: str, blocks: dict[str, str]) -> str:
    """Replace each sentinel block's content with the freshly rendered output.

    Sentinels not present in the source are silently skipped — the
    target doc owns which blocks it opts into.
    """

    def replacer(match: re.Match[str]) -> str:
        name = match.group("name")
        if name not in blocks:
            # Unknown block name in the source; leave it alone.
            return match.group(0)
        start = match.group(1)
        end = match.group(3)
        body = blocks[name]
        return f"{start}\n{body}\n{end}"

    return _SENTINEL_RE.sub(replacer, text)


def main() -> int:
    """CLI entrypoint. Returns the desired process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        type=Path,
        required=True,
        help="Path to the tools.md file to update.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Exit 1 if the file would change.")
    mode.add_argument("--write", action="store_true", help="Rewrite the file in place.")
    args = parser.parse_args()

    target: Path = args.target
    if not target.exists():
        print(f"error: target file does not exist: {target}", file=sys.stderr)
        return 2

    original = target.read_text()
    blocks = _build_blocks()
    updated = _substitute(original, blocks)

    if args.check:
        if original == updated:
            print(f"ok: {target} is up to date")
            return 0
        print(
            f"error: {target} is out of date. Re-run with --write to regenerate.",
            file=sys.stderr,
        )
        return 1

    if original == updated:
        print(f"ok: {target} already up to date; no write needed")
        return 0
    target.write_text(updated)
    print(f"ok: {target} updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
