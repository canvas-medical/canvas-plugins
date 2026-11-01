"""A reply cites only rows a citable tool returned, described from those rows."""

import json
from typing import Any

from canvas_sdk.agents import ToolRegistry, standard_tools
from canvas_sdk.agents.citations import CARD_FIELDS, Sources, cite

LAB = {
    "id": "lab-1",
    "test": "Hemoglobin A1c",
    "value": "7.4",
    "units": "%",
    "abnormal_flag": "H",
    "date": "2026-03-02",
}
NOTE = {
    "id": "note-1",
    "dbid": 4521,
    "title": "Follow-up",
    "note_type_name": "Office visit",
    "provider_name": "Dr. Lee",
    "datetime_of_service": "2026-03-01T10:00:00",
}


def _exchange(tool: str, result: Any, *, call_id: str = "t1", **extra: Any) -> list[dict[str, Any]]:
    """An assistant tool call and the user turn carrying its result, as stored."""
    return [
        {
            "role": "assistant",
            "content": [{"type": "tool_use", "id": call_id, "name": tool, "input": {}}],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": call_id,
                    "content": result if isinstance(result, str) else json.dumps(result),
                    **extra,
                }
            ],
        },
    ]


def _sources(*messages: list[dict[str, Any]]) -> Sources:
    return Sources(standard_tools).add_all([m for exchange in messages for m in exchange])


def test_a_cited_row_becomes_a_numbered_reference_described_from_the_row() -> None:
    """The card says what the tool returned, not what the model wrote."""
    sources = _sources(_exchange("find_lab_results", [LAB]))

    text, (citation,) = cite("Her A1c was 7.4% [[cite:lab-1]].", sources)

    assert text == "Her A1c was 7.4% [1]."
    assert citation.to_dict() == {
        "number": 1,
        "id": "lab-1",
        "kind": "Lab result",
        "label": "Hemoglobin A1c",
        "detail": "7.4, %, H",
        "date": "2026-03-02",
        "note_dbid": None,
    }


def test_a_record_cited_twice_keeps_its_number() -> None:
    """Numbers follow first appearance."""
    sources = _sources(
        _exchange("find_lab_results", [LAB]),
        _exchange("find_notes", [NOTE], call_id="t2"),
    )

    text, citations = cite(
        "Seen in March [[cite:note-1]]; A1c 7.4% [[cite:lab-1]], up since [[cite:note-1]].",
        sources,
    )

    assert text == "Seen in March [1]; A1c 7.4% [2], up since [1]."
    assert [(c.number, c.id) for c in citations] == [(1, "note-1"), (2, "lab-1")]


def test_a_cited_note_carries_its_handle_for_navigation() -> None:
    """A chart surface can scroll to the note a citation names."""
    _, (citation,) = cite("[[cite:note-1]]", _sources(_exchange("find_notes", [NOTE])))

    assert (citation.kind, citation.label, citation.note_dbid) == ("Note", "Follow-up", 4521)
    assert citation.detail == "Office visit, Dr. Lee"


def test_a_marker_for_a_record_no_tool_returned_is_removed() -> None:
    """An id the model made up, or remembered from elsewhere, cites nothing."""
    sources = _sources(_exchange("find_lab_results", [LAB]))

    text, citations = cite("Her LDL was 160 [[cite:lab-999]].", sources)

    assert (text, citations) == ("Her LDL was 160.", [])


def test_rows_from_a_configuration_tool_are_not_citable() -> None:
    """Note types and practice locations are not the patient's records."""
    sources = _sources(_exchange("find_note_types", [{"id": "nt-1", "name": "Review"}]))

    assert cite("Using the review type [[cite:nt-1]].", sources) == ("Using the review type.", [])


def test_failed_and_truncated_results_are_not_citable() -> None:
    """An error result, or one cut short to fit the context, has no rows to trust."""
    sources = _sources(
        _exchange("find_lab_results", [LAB], is_error=True),
        _exchange("find_notes", json.dumps([NOTE])[:40], call_id="t2"),
    )

    assert cite("[[cite:lab-1]] [[cite:note-1]]", sources) == ("", [])


def test_a_result_counts_only_after_the_call_that_produced_it() -> None:
    """A tool result whose call was never seen cannot be attributed to a tool."""
    call, result = _exchange("find_lab_results", [LAB])
    sources = Sources(standard_tools).add_all([result, call])

    assert sources.get("lab-1") is None


def test_a_plugin_tools_model_gets_a_generic_card() -> None:
    """A model the SDK has no card for is described by its first text field."""

    class SleepLog:
        pass

    tools = ToolRegistry()

    @tools.filter_search_tool(
        name="find_sleep_logs",
        description="x",
        queryset_factory=lambda args, pid: [],
        model=SleepLog,
    )
    def _row(row: Any) -> dict[str, Any]:
        return row

    sources = Sources(tools).add_all(
        _exchange("find_sleep_logs", [{"id": "s-1", "quality": "restless", "hours": 5}])
    )

    _, (citation,) = cite("[[cite:s-1]]", sources)

    assert (citation.kind, citation.label) == ("Sleep log", "restless")


def test_every_citable_standard_tool_has_a_card() -> None:
    """A new read tool decides how its rows are described when cited.

    Banner and protocol card rows carry no ``id``, so they are never cited.
    """
    citable_models = {
        metadata.get("record_type") or metadata["model"].__name__
        for definition in standard_tools.definitions()
        if (metadata := standard_tools.metadata_for(definition["name"])).get("citable")
    }

    assert citable_models - set(CARD_FIELDS) == {"BannerAlert", "ProtocolCurrent"}
