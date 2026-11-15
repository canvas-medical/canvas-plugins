"""The imaging order and referral tools: the directory and study lookups, and their drafts."""

import json
from typing import Any
from urllib.parse import unquote

import pytest

from canvas_sdk.agents import standard_tools
from canvas_sdk.test_utils.factories import (
    CommandTypeSettingFactory,
    PatientFactory,
    ServiceProviderFactory,
)
from canvas_sdk.tests.agents.test_history_tools import _serve

NOTE = "00000000-0000-0000-0000-000000000001"


def _run(tool: str, **arguments: Any) -> tuple[Any, list[Any]]:
    effects: list[Any] = []
    patient = PatientFactory.create()
    result = standard_tools.execute(
        tool, arguments, ctx={"patient_id": patient.id, "note_id": NOTE, "effects": effects}
    )
    return result, effects


def _data(effect: Any) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(effect.payload)["data"]
    return data


# Looking up -------------------------------------------------------------------------


def test_imaging_studies_come_back_with_the_code_the_order_takes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The study's code comes from the chart's own list, never from the model."""
    science = _serve(
        monkeypatch,
        "science_http",
        lambda path: {
            "results": [
                {"code": "73721", "name": "MRI knee without contrast"},
                {"name": "a template with no code"},
            ]
        },
    )

    rows = standard_tools.execute(
        "find_clinical_codes", {"kind": "imaging_study", "query": "knee mri"}, ctx={}
    )

    assert rows == [{"image_code": "73721", "display": "MRI knee without contrast"}]
    assert unquote(science.paths[0]).startswith("/parse-templates/imaging-reports?")
    assert "query=knee mri" in unquote(science.paths[0])


@pytest.mark.django_db
def test_the_provider_directory_is_searched_by_specialty_and_leaves_out_inactive_providers() -> (
    None
):
    """Only providers the chart's commands can pick from are offered."""
    cardiologist = ServiceProviderFactory.create(specialty="Cardiology", last_name="Heart")
    ServiceProviderFactory.create(specialty="Cardiology", is_active=False)
    ServiceProviderFactory.create(specialty="Dermatology")

    rows = standard_tools.execute(
        "find_service_providers",
        {"specialty_contains": "cardio"},
        ctx={"patient_id": PatientFactory.create().id},
    )

    assert [row["id"] for row in rows] == [str(cardiologist.id)]
    assert rows[0]["specialty"] == "Cardiology"


# Drafting ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_an_imaging_order_is_drafted_with_its_study_indications_and_facility() -> None:
    """The facility the model picked is sent as the directory holds it."""
    facility = ServiceProviderFactory.create(specialty="Radiology", practice_name="Valley Imaging")

    result, (effect,) = _run(
        "originate_imaging_order",
        image_code="73721",
        diagnosis_codes=["M25.561"],
        priority="Urgent",
        service_provider_id=str(facility.id),
        additional_details="Right knee",
    )

    assert (result["ok"], result["committed"], result["command"]) == (True, False, "imagingOrder")
    data = _data(effect)
    assert (data["image_code"], data["diagnosis_codes"], data["priority"]) == (
        "73721",
        ["M25.561"],
        "Urgent",
    )
    assert data["service_provider"]["practice_name"] == "Valley Imaging"


@pytest.mark.django_db
def test_a_referral_is_drafted_to_the_provider_the_directory_holds() -> None:
    """The referral names a real directory entry, never one the model wrote."""
    specialist = ServiceProviderFactory.create(specialty="Cardiology", last_name="Heart")

    result, (effect,) = _run(
        "originate_refer",
        service_provider_id=str(specialist.id),
        diagnosis_codes=["I48.91"],
        clinical_question="Diagnostic Uncertainty",
        notes_to_specialist="New irregular rhythm on exam.",
    )

    assert (result["ok"], result["command"]) == (True, "refer")
    data = _data(effect)
    assert data["service_provider"]["last_name"] == "Heart"
    assert data["service_provider"]["specialty"] == "Cardiology"
    assert data["clinical_question"] == "Diagnostic Uncertainty"
    assert data["diagnosis_codes"] == ["I48.91"]


@pytest.mark.django_db
@pytest.mark.parametrize("tool", ["originate_refer", "originate_imaging_order"])
def test_an_order_naming_a_provider_outside_the_directory_is_refused(tool: str) -> None:
    """An inactive or unknown provider id stages nothing."""
    inactive = ServiceProviderFactory.create(is_active=False)

    with pytest.raises(ValueError, match="find_service_providers"):
        _run(tool, image_code="73721", service_provider_id=str(inactive.id))


@pytest.mark.django_db
def test_a_referral_is_refused_when_the_instance_turned_referrals_off() -> None:
    """The draft would be one the clinician could not add from the command menu."""
    CommandTypeSettingFactory._meta.model.objects.filter(schema_key="refer").update(active=False)
    specialist = ServiceProviderFactory.create()

    result, effects = _run("originate_refer", service_provider_id=str(specialist.id))

    assert result["ok"] is False
    assert "refer command is turned off" in result["error"]
    assert effects == []
