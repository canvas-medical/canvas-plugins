"""Tests for the agent-tools docs generator.

Two layers:

- **Unit**: substitution preserves prose outside sentinels and replaces
  only inside; unknown block names left alone; categories/reads/writes
  rendering exercises a fake tool catalog so the assertions don't drift
  with the real catalog's tool count.
- **Integration**: runs the generator against the live ``standard_tools``
  registry and asserts smoke-level structure (the three blocks render
  without raising, every read tool appears in the reads block, every
  write in the writes block).
"""

from pathlib import Path
from typing import Any

import pytest

from canvas_sdk.agents import _docs_generator, standard_tools
from canvas_sdk.agents.tool_registry import EffectField, ToolRegistry


class _FakeAddTaskEffect:
    """Stub matching what the real AddTask Effect.apply() returns shape-wise."""

    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    def apply(self) -> Any:
        return self


class _FakeModel:
    """Stand-in for a Django data model in filter_search_tool metadata."""

    pass


# ---------------------------------------------------------------------------
# Substitution
# ---------------------------------------------------------------------------


def test_substitute_replaces_block_contents_and_preserves_surrounding_prose() -> None:
    """Generator-managed blocks are rewritten; prose outside is byte-for-byte preserved."""
    source = (
        "# Heading\n"
        "\n"
        "Some hand-written intro.\n"
        "\n"
        "<!-- AUTOGEN:categories START -->\n"
        "stale content to be replaced\n"
        "<!-- AUTOGEN:categories END -->\n"
        "\n"
        "Hand-written outro that must survive.\n"
    )
    blocks = {"categories": "fresh content"}

    result = _docs_generator._substitute(source, blocks)

    assert "fresh content" in result
    assert "stale content" not in result
    assert "Some hand-written intro." in result
    assert "Hand-written outro that must survive." in result


def test_substitute_leaves_unknown_block_names_untouched() -> None:
    """Sentinels for block names the generator doesn't know about are not touched."""
    source = (
        "<!-- AUTOGEN:unknown_block START -->\n"
        "preserved content\n"
        "<!-- AUTOGEN:unknown_block END -->\n"
    )

    result = _docs_generator._substitute(source, {"categories": "x"})

    assert "preserved content" in result


def test_substitute_handles_multiple_known_blocks() -> None:
    """Multiple known blocks are each replaced independently."""
    source = (
        "<!-- AUTOGEN:reads START -->\n"
        "old reads\n"
        "<!-- AUTOGEN:reads END -->\n"
        "intermission prose\n"
        "<!-- AUTOGEN:writes START -->\n"
        "old writes\n"
        "<!-- AUTOGEN:writes END -->\n"
    )
    blocks = {"reads": "new reads", "writes": "new writes"}

    result = _docs_generator._substitute(source, blocks)

    assert "new reads" in result
    assert "new writes" in result
    assert "intermission prose" in result
    assert "old reads" not in result
    assert "old writes" not in result


def test_substitute_is_idempotent() -> None:
    """Running substitute twice with the same blocks produces the same output."""
    source = "<!-- AUTOGEN:categories START -->\nx\n<!-- AUTOGEN:categories END -->\n"
    blocks = {"categories": "fresh"}

    first = _docs_generator._substitute(source, blocks)
    second = _docs_generator._substitute(first, blocks)

    assert first == second


def test_substitute_returns_unchanged_when_no_sentinels_present() -> None:
    """A doc with no AUTOGEN markers is returned byte-for-byte."""
    source = "# Just prose, no sentinels here.\n"

    result = _docs_generator._substitute(source, {"categories": "x"})

    assert result == source


# ---------------------------------------------------------------------------
# Rendering — uses fake registry so assertions don't drift with the catalog
# ---------------------------------------------------------------------------


def test_arg_table_row_marks_required_and_inlines_enum_values() -> None:
    """Required column reads 'yes'/'no'; enum values append to description."""
    row = _docs_generator._arg_table_row(
        "status",
        {
            "type": "string",
            "description": "The status.",
            "enum": ["open", "closed"],
        },
        required=True,
    )

    assert "`status`" in row
    assert "string (enum)" in row
    assert "yes" in row
    assert "`open`" in row
    assert "`closed`" in row


def test_arg_table_row_escapes_pipe_characters_in_description() -> None:
    """Pipe characters in tool descriptions can't break the markdown table."""
    row = _docs_generator._arg_table_row(
        "x",
        {"type": "string", "description": "a | b"},
        required=False,
    )

    assert "a \\| b" in row
    assert "| a | b |" not in row


def test_arg_table_row_renders_array_items_type() -> None:
    """Array fields show their item type ('array of string', etc.)."""
    row = _docs_generator._arg_table_row(
        "tags",
        {"type": "array", "items": {"type": "string"}, "description": "Tags."},
        required=False,
    )

    assert "array of string" in row


def test_format_categories_block_against_fake_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    """The categories block enumerates each @category and its tool list."""
    registry = ToolRegistry()
    registry.add_effect_tool(
        name="stage_one",
        description="...",
        effect_class=_FakeAddTaskEffect,
        fields={"x": EffectField(type="string", description="...", required=True)},
        categories=("task_writes",),
    )
    registry.add_effect_tool(
        name="stage_two",
        description="...",
        effect_class=_FakeAddTaskEffect,
        fields={"x": EffectField(type="string", description="...", required=True)},
        categories=("task_writes", "clinical_alerts"),
    )

    monkeypatch.setattr(_docs_generator, "standard_tools", registry)
    result = _docs_generator._format_categories_block()

    assert "**`@task_writes`**" in result
    assert "**`@clinical_alerts`**" in result
    assert "`stage_one`" in result
    assert "`stage_two`" in result
    # Tool appearing in two categories is listed in both.
    assert result.count("`stage_two`") == 2


def test_format_categories_block_pluralizes_count(monkeypatch: pytest.MonkeyPatch) -> None:
    """The category header shows '1 tool' vs 'N tools' correctly."""
    registry = ToolRegistry()
    registry.add_effect_tool(
        name="solo",
        description="...",
        effect_class=_FakeAddTaskEffect,
        fields={"x": EffectField(type="string", description="...", required=True)},
        categories=("task_writes",),
    )
    monkeypatch.setattr(_docs_generator, "standard_tools", registry)

    result = _docs_generator._format_categories_block()
    assert "(1 tool)" in result


def test_format_tool_block_renders_args_table_and_backing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A write tool's block has heading, category, args table, returns, and backing."""
    registry = ToolRegistry()
    registry.add_effect_tool(
        name="stage_fake",
        description="Stage a fake effect for the patient.",
        effect_class=_FakeAddTaskEffect,
        fields={
            "title": EffectField(type="string", description="The title.", required=True),
            "note": EffectField(type="string", description="Optional note."),
        },
        categories=("task_writes",),
        returns_description="`{ok: true}`.",
    )
    monkeypatch.setattr(_docs_generator, "standard_tools", registry)

    block = _docs_generator._format_tool_block("stage_fake")

    assert block.startswith("#### `stage_fake`")
    assert "**Category:** `@task_writes`" in block
    assert "Stage a fake effect" in block
    assert "**Arguments:**" in block
    assert "`title`" in block
    assert "`note`" in block
    assert "yes" in block  # title required
    assert "no" in block  # note optional
    assert "**Returns:** `{ok: true}`." in block
    assert "**Backing Effect:** `_FakeAddTaskEffect`." in block


def test_format_tool_block_uses_model_for_filter_search_tools(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """filter_search_tool metadata surfaces as 'Backing data model'."""
    registry = ToolRegistry()
    registry.filter_search_tool(
        name="find_fake",
        description="Find fake rows.",
        queryset_factory=lambda args, pid: [],
        model=_FakeModel,
        returns_description="Each row: id.",
    )(lambda row: {"id": row})
    monkeypatch.setattr(_docs_generator, "standard_tools", registry)

    block = _docs_generator._format_tool_block("find_fake")

    assert "**Backing data model:** `_FakeModel`." in block
    assert "**Returns:** Each row: id." in block


def test_format_tool_block_handles_zero_args_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tools with no input properties render an 'Arguments: none.' line."""
    registry = ToolRegistry()

    @registry.tool(
        name="bare",
        description="A bare tool.",
        input_schema={"type": "object", "properties": {}},
        returns_description="Just a number.",
    )
    def _bare(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> int:
        return 1

    monkeypatch.setattr(_docs_generator, "standard_tools", registry)
    block = _docs_generator._format_tool_block("bare")

    assert "**Arguments:** none." in block


def test_classify_tools_splits_by_metadata_kind(monkeypatch: pytest.MonkeyPatch) -> None:
    """add_effect / originate_command kinds land in writes; everything else in reads."""
    registry = ToolRegistry()
    registry.filter_search_tool(
        name="find_a",
        description="...",
        queryset_factory=lambda args, pid: [],
    )(lambda row: {})
    registry.add_effect_tool(
        name="stage_a",
        description="...",
        effect_class=_FakeAddTaskEffect,
        fields={"x": EffectField(type="string", description="...", required=True)},
    )

    @registry.tool(
        name="bare_scalar",
        description="...",
        input_schema={"type": "object", "properties": {}},
    )
    def _bare(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> int:
        return 1

    monkeypatch.setattr(_docs_generator, "standard_tools", registry)
    reads, writes = _docs_generator._classify_tools()

    assert reads == ["find_a", "bare_scalar"]
    assert writes == ["stage_a"]


# ---------------------------------------------------------------------------
# Integration — exercise against the live catalog
# ---------------------------------------------------------------------------


def test_build_blocks_returns_all_three_keys() -> None:
    """The generator always produces 'categories', 'reads', 'writes' blocks."""
    blocks = _docs_generator._build_blocks()
    assert set(blocks) == {"categories", "reads", "writes"}


def test_every_real_read_tool_appears_in_the_reads_block() -> None:
    """Every find_* / get_* tool in standard_tools shows up by name in the reads block."""
    blocks = _docs_generator._build_blocks()
    reads_block = blocks["reads"]
    for definition in standard_tools.definitions():
        name = definition["name"]
        metadata = standard_tools.metadata_for(name)
        if not _docs_generator._is_write_kind(metadata.get("kind")):
            assert f"`{name}`" in reads_block, f"{name} missing from reads block"


def test_every_real_write_tool_appears_in_the_writes_block() -> None:
    """Every add_effect tool in standard_tools shows up by name in the writes block."""
    blocks = _docs_generator._build_blocks()
    writes_block = blocks["writes"]
    for definition in standard_tools.definitions():
        name = definition["name"]
        metadata = standard_tools.metadata_for(name)
        if _docs_generator._is_write_kind(metadata.get("kind")):
            assert f"`{name}`" in writes_block, f"{name} missing from writes block"


# ---------------------------------------------------------------------------
# CLI — end-to-end via tmp_path
# ---------------------------------------------------------------------------


def test_main_check_mode_passes_when_file_is_up_to_date(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """--check exits 0 when the target already contains the freshly-rendered blocks."""
    blocks = _docs_generator._build_blocks()
    target = tmp_path / "tools.md"
    target.write_text(
        "# Heading\n"
        "<!-- AUTOGEN:categories START -->\n"
        f"{blocks['categories']}\n"
        "<!-- AUTOGEN:categories END -->\n"
        "<!-- AUTOGEN:reads START -->\n"
        f"{blocks['reads']}\n"
        "<!-- AUTOGEN:reads END -->\n"
        "<!-- AUTOGEN:writes START -->\n"
        f"{blocks['writes']}\n"
        "<!-- AUTOGEN:writes END -->\n"
    )

    monkeypatch.setattr("sys.argv", ["_docs_generator", "--check", "--target", str(target)])
    exit_code = _docs_generator.main()

    assert exit_code == 0


def test_main_check_mode_fails_when_file_is_stale(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """--check exits 1 when the target's blocks don't match the freshly-rendered ones."""
    target = tmp_path / "tools.md"
    target.write_text("<!-- AUTOGEN:categories START -->\nstale\n<!-- AUTOGEN:categories END -->\n")

    monkeypatch.setattr("sys.argv", ["_docs_generator", "--check", "--target", str(target)])
    exit_code = _docs_generator.main()

    assert exit_code == 1


def test_main_write_mode_updates_file_in_place(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """--write rewrites the file with fresh block contents."""
    target = tmp_path / "tools.md"
    target.write_text(
        "Hand-written.\n<!-- AUTOGEN:categories START -->\nstale\n<!-- AUTOGEN:categories END -->\n"
    )

    monkeypatch.setattr("sys.argv", ["_docs_generator", "--write", "--target", str(target)])
    exit_code = _docs_generator.main()

    assert exit_code == 0
    after = target.read_text()
    assert "stale" not in after
    assert "Hand-written.\n" in after
    assert "<!-- AUTOGEN:categories START -->" in after


def test_main_returns_2_when_target_does_not_exist(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Missing target file: exit 2 (distinct from check-mode-stale's exit 1)."""
    monkeypatch.setattr(
        "sys.argv",
        ["_docs_generator", "--check", "--target", str(tmp_path / "nope.md")],
    )
    exit_code = _docs_generator.main()

    assert exit_code == 2
