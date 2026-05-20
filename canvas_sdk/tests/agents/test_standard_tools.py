"""Registry-level tests for ``canvas_sdk.agents.standard_tools``.

These verify the catalog's shape — every advertised tool is registered with
an executor, has a non-empty input schema, and shows up in ``definitions()``.
Data-touching behavior is exercised by the integration suite (the ORM
queries underneath each tool would otherwise require fixture setup that
isn't in scope for this PoC).
"""

from canvas_sdk.agents import standard_tools

EXPECTED_TOOLS = (
    "find_medications",
    "find_conditions",
    "find_lab_results",
    "find_assessments",
    "get_patient_demographics",
)


def test_expected_tools_are_registered() -> None:
    """Every advertised tool name resolves to a registered executor."""
    registered = {definition["name"] for definition in standard_tools.definitions()}
    assert set(EXPECTED_TOOLS).issubset(registered), (
        f"missing tools in standard_tools registry: {set(EXPECTED_TOOLS) - registered}"
    )


def test_every_tool_has_input_schema_and_description() -> None:
    """Each tool's Anthropic-shaped definition has the required keys."""
    for definition in standard_tools.definitions():
        assert definition["name"], "tool definition missing name"
        assert definition["description"], f"tool {definition['name']!r} missing description"
        schema = definition["input_schema"]
        assert isinstance(schema, dict), f"tool {definition['name']!r} input_schema is not a dict"
        assert schema.get("type") == "object", (
            f"tool {definition['name']!r} input_schema must be an object schema"
        )


def test_definitions_returns_a_copy() -> None:
    """``definitions()`` returns a fresh list — callers can't mutate the registry."""
    snapshot_a = standard_tools.definitions()
    snapshot_a.clear()
    snapshot_b = standard_tools.definitions()
    assert snapshot_b, "definitions() should still return tools after caller clears its copy"


def test_get_patient_demographics_takes_no_arguments() -> None:
    """Demographics is a fixed-shape read; its schema accepts no properties."""
    definition = next(
        d for d in standard_tools.definitions() if d["name"] == "get_patient_demographics"
    )
    assert definition["input_schema"].get("properties") == {}


def test_find_conditions_advertises_expected_filters() -> None:
    """find_conditions exposes name/code/active/onset/limit filter knobs."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_conditions")
    properties = definition["input_schema"]["properties"]
    for key in ("name_contains", "code_contains", "active_only", "onset_on_or_after", "limit"):
        assert key in properties, f"find_conditions missing filter {key!r}"


def test_find_lab_results_advertises_expected_filters() -> None:
    """find_lab_results exposes name/observed_on/abnormal/limit filter knobs."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_lab_results")
    properties = definition["input_schema"]["properties"]
    for key in ("name_contains", "observed_on_or_after", "abnormal_only", "limit"):
        assert key in properties, f"find_lab_results missing filter {key!r}"


def test_find_assessments_exposes_limit_only() -> None:
    """Assessments are a recency-ordered read; only ``limit`` is filterable today."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_assessments")
    properties = definition["input_schema"]["properties"]
    assert "limit" in properties
