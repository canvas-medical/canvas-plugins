from typing import Any

import pytest

from canvas_sdk.agents import EffectField, FilterSpec, ToolNotAllowed, ToolRegistry


def _passthrough(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Echo back what was passed in — a useful test executor."""
    return {"args": arguments, "ctx": ctx}


def test_registry_starts_empty() -> None:
    """A fresh registry has no definitions and no executors."""
    registry = ToolRegistry()
    assert registry.definitions() == []


def test_register_adds_definition_and_executor() -> None:
    """A registered tool shows up in definitions() and executes via execute()."""
    registry = ToolRegistry()
    registry.register(
        {"name": "echo", "description": "echo", "input_schema": {"type": "object"}},
        _passthrough,
    )
    assert [d["name"] for d in registry.definitions()] == ["echo"]
    result = registry.execute("echo", {"hello": "world"}, ctx={"k": "v"})
    assert result == {"args": {"hello": "world"}, "ctx": {"k": "v"}}


def test_register_rejects_definition_without_name() -> None:
    """A definition missing the 'name' key is a programmer error, not a runtime case."""
    registry = ToolRegistry()
    with pytest.raises(ValueError, match="missing a 'name' key"):
        registry.register({"description": "no name here"}, _passthrough)


def test_register_rejects_duplicate_name() -> None:
    """Two tools cannot share a name in the same registry."""
    registry = ToolRegistry()
    registry.register(
        {"name": "echo", "description": "first", "input_schema": {"type": "object"}},
        _passthrough,
    )
    with pytest.raises(ValueError, match="already registered"):
        registry.register(
            {"name": "echo", "description": "second", "input_schema": {"type": "object"}},
            _passthrough,
        )


def test_tool_decorator_registers_with_executor() -> None:
    """The @registry.tool decorator pairs the definition with the decorated function."""
    registry = ToolRegistry()

    @registry.tool(name="ping", description="ping", input_schema={"type": "object"})
    def _ping(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> str:
        return "pong"

    assert [d["name"] for d in registry.definitions()] == ["ping"]
    assert registry.execute("ping", {}, ctx={}) == "pong"


def test_extend_copies_tools_from_other_registry() -> None:
    """extend() copies definitions and executor refs; later mutations don't leak."""
    source = ToolRegistry()

    @source.tool(name="a", description="a", input_schema={"type": "object"})
    def _a(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> str:
        return "a"

    target = ToolRegistry()
    target.extend(source)

    @target.tool(name="b", description="b", input_schema={"type": "object"})
    def _b(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> str:
        return "b"

    # Target has both; source still has only its own tool.
    assert sorted(d["name"] for d in target.definitions()) == ["a", "b"]
    assert [d["name"] for d in source.definitions()] == ["a"]


def test_extend_raises_on_name_collision() -> None:
    """extend() into a registry that already has the same tool name is a hard error."""
    source = ToolRegistry()
    source.register(
        {"name": "dup", "description": "from source", "input_schema": {"type": "object"}},
        _passthrough,
    )
    target = ToolRegistry()
    target.register(
        {"name": "dup", "description": "from target", "input_schema": {"type": "object"}},
        _passthrough,
    )

    with pytest.raises(ValueError, match="already registered"):
        target.extend(source)


def test_execute_unknown_tool_raises() -> None:
    """Asking for a tool that wasn't registered is a clean ValueError.

    The agent loop catches this and reports back as ``tool_result`` with
    ``is_error=True``, so the model self-corrects.
    """
    registry = ToolRegistry()
    with pytest.raises(ValueError, match="Unknown tool"):
        registry.execute("nonexistent", {}, ctx={})


def test_definitions_returns_a_copy() -> None:
    """definitions() must not return the internal list (callers might mutate it)."""
    registry = ToolRegistry()
    registry.register(
        {"name": "t", "description": "t", "input_schema": {"type": "object"}},
        _passthrough,
    )
    outside = registry.definitions()
    outside.clear()
    assert [d["name"] for d in registry.definitions()] == ["t"]


# ---------------------------------------------------------------------------
# Permission filtering — definitions(allowed=...) and execute(allowed=...)
# ---------------------------------------------------------------------------


def _three_tool_registry() -> ToolRegistry:
    """Build a registry with three tools, useful for filter-behavior tests."""
    registry = ToolRegistry()
    for name in ("read_chart", "write_task", "send_message"):
        registry.register(
            {"name": name, "description": name, "input_schema": {"type": "object"}},
            _passthrough,
        )
    return registry


def test_definitions_with_no_allowed_returns_everything() -> None:
    """Default behavior is backwards-compatible — no filter, all tools served."""
    registry = _three_tool_registry()
    assert sorted(d["name"] for d in registry.definitions()) == [
        "read_chart",
        "send_message",
        "write_task",
    ]


def test_definitions_with_allowed_filters_to_named_tools() -> None:
    """Passing allowed=... narrows the catalog before the model sees it."""
    registry = _three_tool_registry()
    filtered = registry.definitions(allowed={"read_chart", "write_task"})
    assert sorted(d["name"] for d in filtered) == ["read_chart", "write_task"]


def test_definitions_with_empty_allowed_returns_nothing() -> None:
    """allowed=set() is the "no tools" surface — distinct from allowed=None."""
    registry = _three_tool_registry()
    assert registry.definitions(allowed=set()) == []


def test_definitions_silently_ignores_unknown_names_in_allowed() -> None:
    """A manifest typo in the allowlist must NOT surface phantom tools to the model."""
    registry = _three_tool_registry()
    filtered = registry.definitions(allowed={"read_chart", "definitely-not-a-tool"})
    assert [d["name"] for d in filtered] == ["read_chart"]


def test_execute_with_no_allowed_dispatches_as_before() -> None:
    """Default execute() behavior is unchanged — no filter."""
    registry = _three_tool_registry()
    result = registry.execute("read_chart", {"x": 1}, ctx={})
    assert result["args"] == {"x": 1}


def test_execute_with_allowed_dispatches_when_name_in_set() -> None:
    """A tool name in the allowlist executes normally."""
    registry = _three_tool_registry()
    result = registry.execute("read_chart", {"x": 1}, ctx={}, allowed={"read_chart", "write_task"})
    assert result["args"] == {"x": 1}


def test_execute_with_allowed_raises_when_name_not_in_set() -> None:
    """A registered tool that's outside the allowlist raises ToolNotAllowed."""
    registry = _three_tool_registry()
    with pytest.raises(ToolNotAllowed, match="not in the caller's allowed set"):
        registry.execute("send_message", {}, ctx={}, allowed={"read_chart", "write_task"})


def test_execute_distinguishes_unknown_from_not_allowed() -> None:
    """ValueError ("Unknown tool") and ToolNotAllowed are distinct, not aliased."""
    registry = _three_tool_registry()
    # Truly unregistered → ValueError, not ToolNotAllowed.
    with pytest.raises(ValueError, match="Unknown tool"):
        registry.execute("ghost", {}, ctx={}, allowed={"ghost"})


def test_tool_not_allowed_is_a_lookup_error() -> None:
    """ToolNotAllowed inherits from LookupError so callers can broaden if useful."""
    assert issubclass(ToolNotAllowed, LookupError)


# ---------------------------------------------------------------------------
# scope() — the platform-side enforcement seam
# ---------------------------------------------------------------------------


def test_scope_returns_a_new_registry_with_only_named_tools() -> None:
    """scope() yields a fresh registry containing only the allowed entries."""
    source = _three_tool_registry()
    scoped = source.scope({"read_chart", "write_task"})

    assert sorted(d["name"] for d in scoped.definitions()) == ["read_chart", "write_task"]
    # The scoped registry can execute its tools directly — no allowed= needed.
    assert scoped.execute("read_chart", {"x": 1}, ctx={})["args"] == {"x": 1}


def test_scope_silently_drops_unknown_names() -> None:
    """A manifest typo in the allowlist results in an empty/narrowed scope, not an error."""
    source = _three_tool_registry()
    scoped = source.scope({"read_chart", "ghost-tool"})
    assert [d["name"] for d in scoped.definitions()] == ["read_chart"]


def test_scope_omits_disallowed_executors_entirely() -> None:
    """A disallowed tool isn't in the scope at all — execute() raises ValueError."""
    source = _three_tool_registry()
    scoped = source.scope({"read_chart"})
    # `send_message` exists in the source but not in the scope. The scope's
    # execute() sees it as a fully-unknown tool, so this is a ValueError
    # (Unknown tool), not a ToolNotAllowed. That distinction matters:
    # "unknown" means "no executor is reachable," which is the strongest
    # statement the platform can make from a non-isolation sandbox.
    with pytest.raises(ValueError, match="Unknown tool"):
        scoped.execute("send_message", {}, ctx={})


def test_scope_does_not_mutate_source_registry() -> None:
    """scope() is non-destructive — the source registry is unchanged."""
    source = _three_tool_registry()
    source.scope({"read_chart"})
    assert sorted(d["name"] for d in source.definitions()) == [
        "read_chart",
        "send_message",
        "write_task",
    ]


def test_scope_with_empty_set_returns_empty_registry() -> None:
    """scope(set()) is the explicit "no tools" surface."""
    source = _three_tool_registry()
    scoped = source.scope(set())
    assert scoped.definitions() == []


def test_scope_multiple_times_does_not_share_state() -> None:
    """Two scoped views off the same source can be narrowed independently."""
    source = _three_tool_registry()
    scope_a = source.scope({"read_chart", "write_task"})
    scope_b = source.scope({"send_message"})

    assert sorted(d["name"] for d in scope_a.definitions()) == ["read_chart", "write_task"]
    assert [d["name"] for d in scope_b.definitions()] == ["send_message"]


# ---------------------------------------------------------------------------
# filter_search_tool — the patient-scoped filter-spec read helper
# ---------------------------------------------------------------------------


class _FakeQuerySet:
    """Stand-in for a Django QuerySet — records the chained operations made on it.

    The filter_search_tool helper is duck-typed (it doesn't import Django);
    a fake that tracks ``.filter()`` / ``.order_by()`` / ``.select_related()``
    / ``.prefetch_related()`` / ``[:n]`` / iteration is enough to exercise it.
    """

    def __init__(self, rows: list[Any] | None = None, calls: list[tuple] | None = None) -> None:
        self._rows = rows if rows is not None else []
        self.calls: list[tuple] = calls if calls is not None else []

    def filter(self, **kwargs: Any) -> "_FakeQuerySet":
        self.calls.append(("filter", kwargs))
        return self

    def exclude(self, **kwargs: Any) -> "_FakeQuerySet":
        self.calls.append(("exclude", kwargs))
        return self

    def select_related(self, *args: Any) -> "_FakeQuerySet":
        self.calls.append(("select_related", args))
        return self

    def prefetch_related(self, *args: Any) -> "_FakeQuerySet":
        self.calls.append(("prefetch_related", args))
        return self

    def order_by(self, *args: Any) -> "_FakeQuerySet":
        self.calls.append(("order_by", args))
        return self

    def __getitem__(self, key: slice) -> "_FakeQuerySet":
        self.calls.append(("slice", (key.start, key.stop, key.step)))
        return self

    def __iter__(self) -> Any:
        return iter(self._rows)


def test_filter_search_tool_synthesizes_schema_from_filters() -> None:
    """The helper builds the JSON Schema from FilterSpec entries + auto-added limit."""
    registry = ToolRegistry()

    @registry.filter_search_tool(
        name="search_widgets",
        description="...",
        queryset_factory=lambda args, pid: _FakeQuerySet(),
        filters={
            "name_contains": FilterSpec(
                type="string", description="match on name", apply=lambda qs, v: qs
            ),
            "active_only": FilterSpec(type="boolean", description="active only"),
            "started_on_or_after": FilterSpec(
                type="string", format="date", description="ISO date", apply=lambda qs, v: qs
            ),
        },
        limit_default=25,
        limit_max=100,
    )
    def _serialize(widget: Any) -> dict[str, Any]:
        return {}

    definition = next(d for d in registry.definitions() if d["name"] == "search_widgets")
    props = definition["input_schema"]["properties"]

    assert set(props.keys()) == {"name_contains", "active_only", "started_on_or_after", "limit"}
    assert props["name_contains"] == {"type": "string", "description": "match on name"}
    assert props["active_only"] == {"type": "boolean", "description": "active only"}
    assert props["started_on_or_after"]["format"] == "date"
    assert props["limit"] == {
        "type": "integer",
        "minimum": 1,
        "maximum": 100,
        "description": "Max results. Defaults to 25; capped at 100.",
    }


def test_filter_search_tool_passes_patient_id_to_factory() -> None:
    """The queryset_factory receives the patient_id from ctx and uses it."""
    registry = ToolRegistry()
    seen: dict[str, Any] = {}

    def factory(arguments: dict[str, Any], patient_id: str) -> _FakeQuerySet:
        seen["patient_id"] = patient_id
        seen["arguments"] = arguments
        return _FakeQuerySet(rows=[])

    @registry.filter_search_tool(
        name="t",
        description="t",
        queryset_factory=factory,
    )
    def _serialize(row: Any) -> dict[str, Any]:
        return {}

    registry.execute("t", {"name_contains": "x"}, ctx={"patient_id": "p-42"})

    assert seen["patient_id"] == "p-42"
    assert seen["arguments"] == {"name_contains": "x"}


def test_filter_search_tool_applies_filters_only_when_truthy() -> None:
    """FilterSpec.apply runs when the argument is supplied and truthy; falsy/missing skip it."""
    registry = ToolRegistry()
    qs = _FakeQuerySet()

    @registry.filter_search_tool(
        name="t",
        description="t",
        queryset_factory=lambda args, pid: qs,
        filters={
            "name_contains": FilterSpec(
                type="string",
                description="...",
                apply=lambda qs_, v: qs_.filter(name__icontains=v),
            ),
            "active_only": FilterSpec(
                type="boolean",
                description="...",
                # apply=None → schema-only, queryset_factory consumes.
            ),
        },
    )
    def _serialize(row: Any) -> dict[str, Any]:
        return {}

    # Truthy value → apply called.
    registry.execute("t", {"name_contains": "x"}, ctx={"patient_id": "p"})
    assert any(call == ("filter", {"name__icontains": "x"}) for call in qs.calls)

    # Falsy value → apply NOT called.
    qs.calls.clear()
    registry.execute("t", {"name_contains": ""}, ctx={"patient_id": "p"})
    assert not any(call[0] == "filter" and "name__icontains" in call[1] for call in qs.calls)

    # Missing argument → apply NOT called.
    qs.calls.clear()
    registry.execute("t", {}, ctx={"patient_id": "p"})
    assert not any(call[0] == "filter" and "name__icontains" in call[1] for call in qs.calls)


def test_filter_search_tool_applies_ordering_and_prefetch() -> None:
    """ordering, prefetch_related, and select_related are applied to the queryset."""
    registry = ToolRegistry()
    qs = _FakeQuerySet()

    @registry.filter_search_tool(
        name="t",
        description="t",
        queryset_factory=lambda args, pid: qs,
        ordering=("-started_at", "name"),
        prefetch_related=("codings", "report__codings"),
        select_related=("report",),
    )
    def _serialize(row: Any) -> dict[str, Any]:
        return {}

    registry.execute("t", {}, ctx={"patient_id": "p"})

    assert ("select_related", ("report",)) in qs.calls
    assert ("prefetch_related", ("codings", "report__codings")) in qs.calls
    assert ("order_by", ("-started_at", "name")) in qs.calls


def test_filter_search_tool_clamps_limit_to_max() -> None:
    """A limit larger than limit_max is clamped down."""
    registry = ToolRegistry()
    qs = _FakeQuerySet()

    @registry.filter_search_tool(
        name="t",
        description="t",
        queryset_factory=lambda args, pid: qs,
        limit_default=25,
        limit_max=50,
    )
    def _serialize(row: Any) -> dict[str, Any]:
        return {}

    registry.execute("t", {"limit": 10_000}, ctx={"patient_id": "p"})

    slice_calls = [c for c in qs.calls if c[0] == "slice"]
    assert slice_calls[-1][1] == (None, 50, None)  # clamped to limit_max


def test_filter_search_tool_uses_default_limit_when_omitted() -> None:
    """When the model doesn't pass `limit`, the helper uses limit_default."""
    registry = ToolRegistry()
    qs = _FakeQuerySet()

    @registry.filter_search_tool(
        name="t",
        description="t",
        queryset_factory=lambda args, pid: qs,
        limit_default=7,
        limit_max=100,
    )
    def _serialize(row: Any) -> dict[str, Any]:
        return {}

    registry.execute("t", {}, ctx={"patient_id": "p"})

    slice_calls = [c for c in qs.calls if c[0] == "slice"]
    assert slice_calls[-1][1] == (None, 7, None)


def test_filter_search_tool_serializes_each_row() -> None:
    """The decorated function is called per row; results are returned as a list."""
    registry = ToolRegistry()

    @registry.filter_search_tool(
        name="t",
        description="t",
        queryset_factory=lambda args, pid: _FakeQuerySet(rows=[1, 2, 3]),
    )
    def _serialize(row: int) -> dict[str, Any]:
        return {"doubled": row * 2}

    result = registry.execute("t", {}, ctx={"patient_id": "p"})

    assert result == [{"doubled": 2}, {"doubled": 4}, {"doubled": 6}]


def test_filter_search_tool_custom_limit_description_is_used() -> None:
    """``limit_description`` overrides the auto-generated text on the limit property."""
    registry = ToolRegistry()

    @registry.filter_search_tool(
        name="t",
        description="t",
        queryset_factory=lambda args, pid: _FakeQuerySet(),
        limit_default=10,
        limit_max=50,
        limit_description="Max results. Defaults to 10.",
    )
    def _serialize(row: Any) -> dict[str, Any]:
        return {}

    definition = next(d for d in registry.definitions() if d["name"] == "t")
    assert definition["input_schema"]["properties"]["limit"]["description"] == (
        "Max results. Defaults to 10."
    )


def test_filter_search_tool_rejects_limit_in_filters() -> None:
    """'limit' is reserved; declaring it in `filters` is a programmer error."""
    registry = ToolRegistry()

    with pytest.raises(ValueError, match="'limit' is reserved"):

        @registry.filter_search_tool(
            name="t",
            description="t",
            queryset_factory=lambda args, pid: _FakeQuerySet(),
            filters={
                "limit": FilterSpec(type="integer", description="..."),
            },
        )
        def _serialize(row: Any) -> dict[str, Any]:
            return {}


def test_filter_search_tool_with_no_filters_only_advertises_limit() -> None:
    """An empty filters dict still produces a usable tool with just the limit param."""
    registry = ToolRegistry()

    @registry.filter_search_tool(
        name="t",
        description="t",
        queryset_factory=lambda args, pid: _FakeQuerySet(),
    )
    def _serialize(row: Any) -> dict[str, Any]:
        return {}

    definition = next(d for d in registry.definitions() if d["name"] == "t")
    assert list(definition["input_schema"]["properties"].keys()) == ["limit"]


# ---------------------------------------------------------------------------
# Categories + resolve_allowed — manifest @category shorthand expansion
# ---------------------------------------------------------------------------


def _categorized_registry() -> ToolRegistry:
    """A registry with three tools across two categories — fixture for resolve_allowed tests."""
    registry = ToolRegistry()
    registry.register(
        {"name": "read_a", "description": "...", "input_schema": {"type": "object"}},
        _passthrough,
        categories=("reads",),
    )
    registry.register(
        {"name": "read_b", "description": "...", "input_schema": {"type": "object"}},
        _passthrough,
        categories=("reads",),
    )
    registry.register(
        {"name": "write_c", "description": "...", "input_schema": {"type": "object"}},
        _passthrough,
        categories=("writes",),
    )
    return registry


def test_resolve_allowed_expands_a_single_category() -> None:
    """@category resolves to the set of tools tagged with it."""
    registry = _categorized_registry()
    assert registry.resolve_allowed(["@reads"]) == frozenset({"read_a", "read_b"})


def test_resolve_allowed_mixes_categories_and_literal_names() -> None:
    """An allowlist can contain a mix of @categories and literal tool names."""
    registry = _categorized_registry()
    assert registry.resolve_allowed(["@reads", "write_c"]) == frozenset(
        {"read_a", "read_b", "write_c"}
    )


def test_resolve_allowed_silently_drops_unknown_categories() -> None:
    """A @category that doesn't exist resolves to nothing (defense vs manifest typos)."""
    registry = _categorized_registry()
    assert registry.resolve_allowed(["@nonexistent"]) == frozenset()


def test_resolve_allowed_silently_drops_unknown_tool_names() -> None:
    """An unknown literal name is dropped (same defense in depth as @categories)."""
    registry = _categorized_registry()
    assert registry.resolve_allowed(["read_a", "ghost_tool"]) == frozenset({"read_a"})


def test_resolve_allowed_applies_denied_after_expansion() -> None:
    """``denied`` is subtracted from the resolved set; subtractions win."""
    registry = _categorized_registry()
    assert registry.resolve_allowed(["@reads"], denied=["read_a"]) == frozenset({"read_b"})


def test_resolve_allowed_denied_accepts_categories() -> None:
    """Both ``allowed`` and ``denied`` accept @category references."""
    registry = _categorized_registry()
    assert registry.resolve_allowed(["@reads", "@writes"], denied=["@writes"]) == frozenset(
        {"read_a", "read_b"}
    )


def test_resolve_allowed_with_empty_allowed_returns_empty() -> None:
    """allowed=[] yields the empty set even with categories in the registry."""
    registry = _categorized_registry()
    assert registry.resolve_allowed([]) == frozenset()


def test_filter_search_tool_categories_kwarg_tags_the_tool() -> None:
    """filter_search_tool's categories kwarg flows through to the registry tagging."""
    registry = ToolRegistry()

    @registry.filter_search_tool(
        name="find_x",
        description="...",
        queryset_factory=lambda args, pid: _FakeQuerySet(),
        categories=("reads",),
    )
    def _serialize(row: Any) -> dict[str, Any]:
        return {}

    assert registry.resolve_allowed(["@reads"]) == frozenset({"find_x"})


def test_extend_copies_categories_with_tools() -> None:
    """Tool categories carry across when one registry extends another."""
    source = _categorized_registry()
    target = ToolRegistry()
    target.extend(source)
    # The category-membership is preserved on the target registry.
    assert target.resolve_allowed(["@reads"]) == frozenset({"read_a", "read_b"})
    assert target.resolve_allowed(["@writes"]) == frozenset({"write_c"})


def test_scope_preserves_categories_for_included_tools() -> None:
    """Categories carry into a scoped registry for the tools that pass through."""
    source = _categorized_registry()
    scoped = source.scope({"read_a", "write_c"})
    assert scoped.resolve_allowed(["@reads"]) == frozenset({"read_a"})
    assert scoped.resolve_allowed(["@writes"]) == frozenset({"write_c"})


# ---------------------------------------------------------------------------
# originate_command_tool — the patient-scoped originate-on-note write helper
# ---------------------------------------------------------------------------


class _FakeOriginatedEffect:
    """Stand-in for an Effect produced by Command.originate()."""

    def __init__(self, note_uuid: str, payload: dict[str, Any]) -> None:
        self.note_uuid = note_uuid
        self.payload = payload


class _FakeCommand:
    """Stand-in for a canvas_sdk.commands.* Command class.

    Records its constructor kwargs and exposes them via the Effect that
    `originate()` returns — the tests assert on these to verify the
    helper passed the right values.
    """

    class Meta:
        key = "fake_command"

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs

    def originate(self) -> _FakeOriginatedEffect:
        return _FakeOriginatedEffect(
            note_uuid=self.kwargs.get("note_uuid", ""), payload=dict(self.kwargs)
        )


def test_originate_command_tool_builds_command_from_arguments() -> None:
    """The helper instantiates command_class with note_uuid + mapped arguments."""
    registry = ToolRegistry()
    registry.originate_command_tool(
        name="originate_fake",
        description="...",
        command_class=_FakeCommand,
        fields={
            "narrative": EffectField(type="string", description="...", required=True),
        },
    )

    effects: list[Any] = []
    result = registry.execute(
        "originate_fake",
        {"narrative": "Recheck A1c in 3 months."},
        ctx={"note_id": "note-abc", "effects": effects},
    )

    assert result["ok"] is True
    assert result["note_id"] == "note-abc"
    assert result["committed"] is False
    assert len(effects) == 1
    effect = effects[0]
    assert effect.note_uuid == "note-abc"
    assert effect.payload == {"note_uuid": "note-abc", "narrative": "Recheck A1c in 3 months."}


def test_originate_command_tool_synthesizes_schema_from_fields() -> None:
    """The helper translates EffectField entries into the JSON Schema."""
    registry = ToolRegistry()
    registry.originate_command_tool(
        name="originate_fake",
        description="...",
        command_class=_FakeCommand,
        fields={
            "narrative": EffectField(type="string", description="The narrative.", required=True),
            "optional_count": EffectField(
                type="integer", description="A count.", minimum=0, maximum=10
            ),
            "tags": EffectField(
                type="array",
                description="Tags.",
                items={"type": "string"},
                max_items=3,
            ),
        },
    )

    definition = next(d for d in registry.definitions() if d["name"] == "originate_fake")
    props = definition["input_schema"]["properties"]

    assert props["narrative"] == {"type": "string", "description": "The narrative."}
    assert props["optional_count"] == {
        "type": "integer",
        "description": "A count.",
        "minimum": 0,
        "maximum": 10,
    }
    assert props["tags"] == {
        "type": "array",
        "description": "Tags.",
        "items": {"type": "string"},
        "maxItems": 3,
    }
    assert definition["input_schema"]["required"] == ["narrative"]


def test_originate_command_tool_renames_via_command_field() -> None:
    """An EffectField with command_field=... maps the LLM-name to a different Command field."""
    registry = ToolRegistry()
    registry.originate_command_tool(
        name="originate_fake",
        description="...",
        command_class=_FakeCommand,
        fields={
            # LLM-facing name: "indications_icd10"; Command field: "icd10_codes".
            "indications_icd10": EffectField(
                type="array",
                items={"type": "string"},
                description="ICD-10 codes.",
                command_field="icd10_codes",
            ),
        },
    )

    effects: list[Any] = []
    registry.execute(
        "originate_fake",
        {"indications_icd10": ["E11.9"]},
        ctx={"note_id": "n1", "effects": effects},
    )

    assert effects[0].payload == {"note_uuid": "n1", "icd10_codes": ["E11.9"]}


def test_originate_command_tool_returns_structured_error_when_no_note() -> None:
    """When note_resolver returns None, the tool returns ok=False with the configured error."""
    registry = ToolRegistry()
    registry.originate_command_tool(
        name="originate_fake",
        description="...",
        command_class=_FakeCommand,
        fields={
            "narrative": EffectField(type="string", description="...", required=True),
        },
        no_note_error="custom no-note message",
    )

    effects: list[Any] = []
    # ctx omits note_id entirely → default resolver returns None.
    result = registry.execute(
        "originate_fake",
        {"narrative": "..."},
        ctx={"effects": effects},
    )

    assert result == {"ok": False, "error": "custom no-note message"}
    assert effects == [], "no effect should have been appended when the note lookup failed"


def test_originate_command_tool_custom_note_resolver() -> None:
    """A custom note_resolver is invoked instead of reading ctx['note_id']."""
    registry = ToolRegistry()
    captured: dict[str, Any] = {}

    def patient_to_note(ctx: dict[str, Any]) -> str | None:
        captured["patient_id"] = ctx["patient_id"]
        return "note-from-patient-lookup"

    registry.originate_command_tool(
        name="originate_fake",
        description="...",
        command_class=_FakeCommand,
        fields={"narrative": EffectField(type="string", description="...", required=True)},
        note_resolver=patient_to_note,
    )

    effects: list[Any] = []
    result = registry.execute(
        "originate_fake",
        {"narrative": "..."},
        ctx={"patient_id": "p1", "effects": effects},
    )

    assert captured["patient_id"] == "p1"
    assert result["note_id"] == "note-from-patient-lookup"


def test_originate_command_tool_pre_build_hook_can_override_arguments() -> None:
    """The pre_build hook's return dict merges over the model's arguments."""
    registry = ToolRegistry()

    def normalize(arguments: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
        # Truncate narrative and add a generated id.
        return {
            "narrative": arguments["narrative"].strip()[:50],
            "generated_id": "abc-123",
        }

    registry.originate_command_tool(
        name="originate_fake",
        description="...",
        command_class=_FakeCommand,
        fields={"narrative": EffectField(type="string", description="...", required=True)},
        pre_build=normalize,
    )

    effects: list[Any] = []
    registry.execute(
        "originate_fake",
        {"narrative": "  " + "x" * 100 + "  "},
        ctx={"note_id": "n1", "effects": effects},
    )

    payload = effects[0].payload
    # Stripped, truncated to 50.
    assert payload["narrative"] == "x" * 50
    # The pre_build hook contributed a field the EffectField didn't declare.
    assert payload["generated_id"] == "abc-123"


def test_originate_command_tool_categories_kwarg_tags_the_tool() -> None:
    """categories= on originate_command_tool flows through to registry tagging."""
    registry = ToolRegistry()
    registry.originate_command_tool(
        name="originate_fake",
        description="...",
        command_class=_FakeCommand,
        fields={"narrative": EffectField(type="string", description="...", required=True)},
        categories=("clinical_writes",),
    )
    assert registry.resolve_allowed(["@clinical_writes"]) == frozenset({"originate_fake"})


def test_originate_command_tool_skips_missing_optional_arguments() -> None:
    """Optional fields the model didn't pass aren't passed to command_class either.

    Lets the Command's own defaults apply rather than overriding them with
    explicit Nones.
    """
    registry = ToolRegistry()
    registry.originate_command_tool(
        name="originate_fake",
        description="...",
        command_class=_FakeCommand,
        fields={
            "required_field": EffectField(type="string", description="...", required=True),
            "optional_field": EffectField(type="string", description="..."),
        },
    )

    effects: list[Any] = []
    registry.execute(
        "originate_fake",
        {"required_field": "value"},  # optional_field omitted
        ctx={"note_id": "n1", "effects": effects},
    )

    # optional_field is NOT in the kwargs.
    assert "optional_field" not in effects[0].payload
    assert effects[0].payload["required_field"] == "value"


# ---------------------------------------------------------------------------
# add_effect_tool — the non-note-bound Effect.apply() helper
# ---------------------------------------------------------------------------


class _FakeAppliedEffect:
    """Stand-in for the Effect produced by .apply()."""

    def __init__(self, kwargs: dict[str, Any]) -> None:
        self.kwargs = kwargs


class _FakeEffect:
    """Stand-in for a canvas_sdk.effects.* Effect class.

    Records constructor kwargs; ``apply()`` returns a payload object the
    test can inspect to confirm the helper passed the right values.
    """

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = dict(kwargs)
        # Expose common attributes as instance attributes so
        # response_builder lambdas (e.g., lambda e: {"id": e.id}) work
        # the way they do on real Effects.
        for key, value in kwargs.items():
            setattr(self, key, value)

    def apply(self) -> _FakeAppliedEffect:
        return _FakeAppliedEffect(dict(self.kwargs))


def test_add_effect_tool_builds_effect_with_patient_id_from_ctx() -> None:
    """Helper auto-injects ctx['patient_id'] as the Effect's patient_id kwarg."""
    registry = ToolRegistry()
    registry.add_effect_tool(
        name="stage_fake",
        description="...",
        effect_class=_FakeEffect,
        fields={
            "title": EffectField(type="string", description="...", required=True),
        },
    )

    effects: list[Any] = []
    result = registry.execute(
        "stage_fake",
        {"title": "Recheck"},
        ctx={"patient_id": "pat-123", "effects": effects},
    )

    assert result == {"ok": True}
    assert len(effects) == 1
    assert effects[0].kwargs == {"patient_id": "pat-123", "title": "Recheck"}


def test_add_effect_tool_synthesizes_schema_from_fields() -> None:
    """The helper translates EffectField entries into a JSON Schema."""
    registry = ToolRegistry()
    registry.add_effect_tool(
        name="stage_fake",
        description="...",
        effect_class=_FakeEffect,
        fields={
            "title": EffectField(type="string", description="A title.", required=True),
            "count": EffectField(type="integer", description="A count.", minimum=1, maximum=99),
            "tags": EffectField(
                type="array",
                description="Tags.",
                items={"type": "string"},
                min_items=1,
                max_items=4,
            ),
        },
    )

    definition = next(d for d in registry.definitions() if d["name"] == "stage_fake")
    props = definition["input_schema"]["properties"]

    assert props["title"] == {"type": "string", "description": "A title."}
    assert props["count"] == {
        "type": "integer",
        "description": "A count.",
        "minimum": 1,
        "maximum": 99,
    }
    assert props["tags"] == {
        "type": "array",
        "description": "Tags.",
        "items": {"type": "string"},
        "minItems": 1,
        "maxItems": 4,
    }
    assert definition["input_schema"]["required"] == ["title"]


def test_add_effect_tool_pre_build_overrides_arguments_and_ctx() -> None:
    """pre_build's return dict layers over ctx-injected and model-supplied kwargs."""
    registry = ToolRegistry()
    registry.add_effect_tool(
        name="stage_fake",
        description="...",
        effect_class=_FakeEffect,
        fields={
            "title": EffectField(type="string", description="...", required=True),
        },
        pre_build=lambda arguments, ctx: {
            "id": "generated-uuid",
            "title": arguments["title"].upper(),  # transform
        },
    )

    effects: list[Any] = []
    registry.execute(
        "stage_fake",
        {"title": "recheck"},
        ctx={"patient_id": "pat-1", "effects": effects},
    )

    # patient_id from ctx, title overridden by pre_build, id added by pre_build.
    assert effects[0].kwargs == {
        "patient_id": "pat-1",
        "title": "RECHECK",
        "id": "generated-uuid",
    }


def test_add_effect_tool_response_builder_customizes_return() -> None:
    """response_builder shapes the model-facing return; receives the Effect."""
    registry = ToolRegistry()
    registry.add_effect_tool(
        name="stage_fake",
        description="...",
        effect_class=_FakeEffect,
        fields={
            "title": EffectField(type="string", description="...", required=True),
        },
        pre_build=lambda arguments, ctx: {"id": "fixed-uuid"},
        response_builder=lambda effect: {"ok": True, "task_id": effect.id},
    )

    effects: list[Any] = []
    result = registry.execute(
        "stage_fake",
        {"title": "X"},
        ctx={"patient_id": "pat-1", "effects": effects},
    )

    assert result == {"ok": True, "task_id": "fixed-uuid"}


def test_add_effect_tool_inject_ctx_can_be_customized() -> None:
    """Custom inject_ctx mapping pulls additional ctx keys into the Effect."""
    registry = ToolRegistry()
    registry.add_effect_tool(
        name="stage_fake",
        description="...",
        effect_class=_FakeEffect,
        fields={
            "title": EffectField(type="string", description="...", required=True),
        },
        inject_ctx={"patient_id": "patient_id", "encounter_id": "encounter_id"},
    )

    effects: list[Any] = []
    registry.execute(
        "stage_fake",
        {"title": "T"},
        ctx={"patient_id": "p1", "encounter_id": "e1", "effects": effects},
    )

    assert effects[0].kwargs == {
        "patient_id": "p1",
        "encounter_id": "e1",
        "title": "T",
    }


def test_add_effect_tool_inject_ctx_empty_skips_injection() -> None:
    """inject_ctx={} disables ctx-key injection entirely."""
    registry = ToolRegistry()
    registry.add_effect_tool(
        name="stage_fake",
        description="...",
        effect_class=_FakeEffect,
        fields={
            "title": EffectField(type="string", description="...", required=True),
        },
        inject_ctx={},
    )

    effects: list[Any] = []
    registry.execute(
        "stage_fake",
        {"title": "T"},
        ctx={"patient_id": "ignored", "effects": effects},
    )

    # No patient_id pulled from ctx — only the model-supplied title.
    assert effects[0].kwargs == {"title": "T"}


def test_add_effect_tool_inject_ctx_renames_to_target_field() -> None:
    """inject_ctx maps ctx_key → effect_kwarg_name, so the target name can differ."""
    registry = ToolRegistry()
    registry.add_effect_tool(
        name="stage_fake",
        description="...",
        effect_class=_FakeEffect,
        fields={
            "title": EffectField(type="string", description="...", required=True),
        },
        inject_ctx={"patient_id": "subject_patient"},
    )

    effects: list[Any] = []
    registry.execute(
        "stage_fake",
        {"title": "T"},
        ctx={"patient_id": "pat-7", "effects": effects},
    )

    # ctx['patient_id'] flowed into the Effect kwarg named 'subject_patient'.
    assert effects[0].kwargs == {"subject_patient": "pat-7", "title": "T"}


def test_add_effect_tool_command_field_renames_argument_to_effect_field() -> None:
    """The command_field rename maps an LLM-facing argument to a different Effect kwarg."""
    registry = ToolRegistry()
    registry.add_effect_tool(
        name="stage_fake",
        description="...",
        effect_class=_FakeEffect,
        fields={
            "note_text": EffectField(
                type="string",
                description="...",
                required=True,
                command_field="narrative",
            ),
        },
    )

    effects: list[Any] = []
    registry.execute(
        "stage_fake",
        {"note_text": "hello"},
        ctx={"patient_id": "p1", "effects": effects},
    )

    # Model argument 'note_text' lands as Effect kwarg 'narrative'.
    assert "note_text" not in effects[0].kwargs
    assert effects[0].kwargs["narrative"] == "hello"


def test_add_effect_tool_omits_optional_fields_when_not_supplied() -> None:
    """Optional fields that the model doesn't supply are not passed to the Effect."""
    registry = ToolRegistry()
    registry.add_effect_tool(
        name="stage_fake",
        description="...",
        effect_class=_FakeEffect,
        fields={
            "title": EffectField(type="string", description="...", required=True),
            "note": EffectField(type="string", description="..."),
        },
    )

    effects: list[Any] = []
    registry.execute(
        "stage_fake",
        {"title": "T"},  # 'note' omitted
        ctx={"patient_id": "p1", "effects": effects},
    )

    assert "note" not in effects[0].kwargs
    assert effects[0].kwargs["title"] == "T"


def test_add_effect_tool_categories_kwarg_tags_the_tool() -> None:
    """categories= flows through to the registry so @category resolution works."""
    registry = ToolRegistry()
    registry.add_effect_tool(
        name="stage_fake",
        description="...",
        effect_class=_FakeEffect,
        fields={"title": EffectField(type="string", description="...", required=True)},
        categories=("task_writes",),
    )

    resolved = registry.resolve_allowed(allowed=["@task_writes"])
    assert resolved == {"stage_fake"}


def test_add_effect_tool_enum_field_renders_in_schema() -> None:
    """EffectField.enum surfaces as a JSON-Schema ``enum`` on the property."""
    registry = ToolRegistry()
    registry.add_effect_tool(
        name="stage_fake",
        description="...",
        effect_class=_FakeEffect,
        fields={
            "intent": EffectField(
                type="string",
                description="...",
                enum=["info", "warning", "alert"],
                required=True,
            ),
        },
    )

    definition = next(d for d in registry.definitions() if d["name"] == "stage_fake")
    assert definition["input_schema"]["properties"]["intent"]["enum"] == [
        "info",
        "warning",
        "alert",
    ]


def test_originate_command_tool_enum_field_renders_in_schema() -> None:
    """EffectField.enum support is symmetric across both helpers."""
    registry = ToolRegistry()
    registry.originate_command_tool(
        name="originate_fake",
        description="...",
        command_class=_FakeCommand,
        fields={
            "severity": EffectField(
                type="string",
                description="...",
                enum=["mild", "moderate", "severe"],
                required=True,
            ),
        },
    )

    definition = next(d for d in registry.definitions() if d["name"] == "originate_fake")
    assert definition["input_schema"]["properties"]["severity"]["enum"] == [
        "mild",
        "moderate",
        "severe",
    ]


# ---------------------------------------------------------------------------
# Docs-oriented metadata — fields the LLM-facing definition doesn't carry
# ---------------------------------------------------------------------------


def test_metadata_for_returns_empty_dict_when_no_metadata_attached() -> None:
    """Tools registered without metadata still have a queryable (empty) entry."""
    registry = ToolRegistry()
    registry.register(
        {"name": "bare", "description": "...", "input_schema": {"type": "object"}},
        lambda args, *, ctx: None,
    )
    assert registry.metadata_for("bare") == {}


def test_metadata_for_returns_unknown_tool_as_empty() -> None:
    """Looking up metadata for an unregistered name returns {}, not a raise."""
    registry = ToolRegistry()
    assert registry.metadata_for("nonexistent") == {}


def test_tool_decorator_stores_returns_description_metadata() -> None:
    """The raw `tool()` decorator threads returns_description into metadata."""
    registry = ToolRegistry()

    @registry.tool(
        name="bare",
        description="...",
        input_schema={"type": "object"},
        returns_description="Returns an integer.",
    )
    def _bare(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> int:
        return 1

    assert registry.metadata_for("bare") == {"returns_description": "Returns an integer."}


def test_filter_search_tool_stores_model_and_returns_description() -> None:
    """filter_search_tool surfaces both `model` and `returns_description`."""
    registry = ToolRegistry()

    class _FakeModel:
        pass

    registry.filter_search_tool(
        name="find_fake",
        description="...",
        queryset_factory=lambda args, pid: [],
        model=_FakeModel,
        returns_description="Each row: id, name.",
    )(lambda row: {"id": row})

    metadata = registry.metadata_for("find_fake")
    assert metadata["kind"] == "filter_search"
    assert metadata["model"] is _FakeModel
    assert metadata["returns_description"] == "Each row: id, name."


def test_originate_command_tool_stores_command_class() -> None:
    """originate_command_tool surfaces the command_class in metadata."""
    registry = ToolRegistry()
    registry.originate_command_tool(
        name="originate_fake",
        description="...",
        command_class=_FakeCommand,
        fields={"narrative": EffectField(type="string", description="...", required=True)},
        returns_description="Returns ok + note_id.",
    )

    metadata = registry.metadata_for("originate_fake")
    assert metadata["kind"] == "originate_command"
    assert metadata["command_class"] is _FakeCommand
    assert metadata["returns_description"] == "Returns ok + note_id."


def test_add_effect_tool_stores_effect_class() -> None:
    """add_effect_tool surfaces the effect_class in metadata."""
    registry = ToolRegistry()
    registry.add_effect_tool(
        name="stage_fake",
        description="...",
        effect_class=_FakeEffect,
        fields={"title": EffectField(type="string", description="...", required=True)},
        returns_description="Returns ok.",
    )

    metadata = registry.metadata_for("stage_fake")
    assert metadata["kind"] == "add_effect"
    assert metadata["effect_class"] is _FakeEffect
    assert metadata["returns_description"] == "Returns ok."


def test_extend_carries_metadata_into_target_registry() -> None:
    """extend() copies metadata along with definitions/executors/categories."""
    source = ToolRegistry()

    class _FakeModel:
        pass

    source.filter_search_tool(
        name="find_fake",
        description="...",
        queryset_factory=lambda args, pid: [],
        model=_FakeModel,
        returns_description="Each row: id.",
    )(lambda row: {"id": row})

    target = ToolRegistry()
    target.extend(source)

    metadata = target.metadata_for("find_fake")
    assert metadata["model"] is _FakeModel
    assert metadata["returns_description"] == "Each row: id."


def test_scope_carries_metadata_into_scoped_registry() -> None:
    """scope() preserves metadata for the surviving tools."""
    registry = ToolRegistry()
    registry.add_effect_tool(
        name="stage_fake",
        description="...",
        effect_class=_FakeEffect,
        fields={"title": EffectField(type="string", description="...", required=True)},
        returns_description="Returns ok.",
    )

    scoped = registry.scope(["stage_fake"])
    assert scoped.metadata_for("stage_fake")["effect_class"] is _FakeEffect


def test_categories_for_returns_tuple_of_tag_names() -> None:
    """categories_for() exposes the tag set on a single tool."""
    registry = ToolRegistry()
    registry.add_effect_tool(
        name="stage_fake",
        description="...",
        effect_class=_FakeEffect,
        fields={"title": EffectField(type="string", description="...", required=True)},
        categories=("clinical_alerts", "task_writes"),
    )

    assert set(registry.categories_for("stage_fake")) == {"clinical_alerts", "task_writes"}


def test_categories_for_unknown_tool_returns_empty_tuple() -> None:
    """categories_for on an unregistered name returns ()."""
    registry = ToolRegistry()
    assert registry.categories_for("nonexistent") == ()
