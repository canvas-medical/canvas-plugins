"""The reason for visit and HPI tools: the configured reasons, and their drafts."""

import json
from typing import Any

import pytest

from canvas_sdk.agents import standard_tools
from canvas_sdk.test_utils.factories import PatientFactory, ReasonForVisitSettingCodingFactory

NOTE = "00000000-0000-0000-0000-000000000001"


def _ctx() -> dict[str, Any]:
    return {"patient_id": PatientFactory.create().id, "note_id": NOTE, "effects": []}


def _data(effect: Any) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(effect.payload)["data"]
    return data


@pytest.mark.django_db
def test_only_the_reasons_the_practice_selected_are_offered() -> None:
    """The list matches the chart's Reason for Visit picker."""
    follow_up = ReasonForVisitSettingCodingFactory.create(display="Follow-up visit")
    ReasonForVisitSettingCodingFactory.create(display="Follow-up hidden", user_selected=False)

    rows = standard_tools.execute(
        "find_reason_for_visit_codes", {"display_contains": "follow"}, ctx=_ctx()
    )

    assert [(row["id"], row["display"]) for row in rows] == [(str(follow_up.id), "Follow-up visit")]


@pytest.mark.django_db
def test_a_reason_for_visit_names_the_configured_reason() -> None:
    """A configured reason is sent as structured, with the visit's own words beside it."""
    reason = ReasonForVisitSettingCodingFactory.create(display="Annual physical")
    ctx = _ctx()

    result = standard_tools.execute(
        "originate_reason_for_visit",
        {"coding_id": str(reason.id), "comment": "Yearly checkup, no concerns"},
        ctx=ctx,
    )

    assert (result["ok"], result["command"]) == (True, "reasonForVisit")
    data = _data(ctx["effects"][0])
    assert (data["structured"], data["coding"], data["comment"]) == (
        True,
        str(reason.id),
        "Yearly checkup, no concerns",
    )


@pytest.mark.django_db
def test_a_free_text_reason_for_visit_is_unstructured() -> None:
    """Without a configured reason, the comment is the whole reason."""
    ctx = _ctx()

    standard_tools.execute("originate_reason_for_visit", {"comment": "Cough for two days"}, ctx=ctx)

    data = _data(ctx["effects"][0])
    assert data["comment"] == "Cough for two days"
    assert not data.get("structured")
    assert not data.get("coding")


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("arguments", "message"),
    [({}, "Give a comment"), ({"coding_id": "not-configured"}, "find_reason_for_visit_codes")],
)
def test_a_reason_for_visit_that_says_nothing_or_names_no_configured_reason_is_refused(
    arguments: dict[str, Any], message: str
) -> None:
    """An empty draft, or a reason the practice did not configure, stages nothing."""
    ctx = _ctx()

    with pytest.raises(ValueError, match=message):
        standard_tools.execute("originate_reason_for_visit", arguments, ctx=ctx)

    assert ctx["effects"] == []


@pytest.mark.django_db
def test_an_hpi_is_drafted_with_its_narrative() -> None:
    """The narrative is staged as written, uncommitted."""
    ctx = _ctx()

    result = standard_tools.execute(
        "originate_hpi", {"narrative": "Two days of productive cough, no fever."}, ctx=ctx
    )

    assert (result["ok"], result["committed"], result["command"]) == (True, False, "hpi")
    assert _data(ctx["effects"][0])["narrative"] == "Two days of productive cough, no fever."
