from typing import Any

import pytest
from pydantic import ValidationError

from canvas_sdk.commands import (
    AssessCommand,
    DiagnoseCommand,
    GoalCommand,
    HistoryOfPresentIllnessCommand,
    MedicationStatementCommand,
    PlanCommand,
    PrescribeCommand,
    QuestionnaireCommand,
    ReasonForVisitCommand,
    StopMedicationCommand,
    UpdateGoalCommand,
)
from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.effects.protocol_card import ProtocolCard, Recommendation


def test_apply_method_succeeds_with_patient_id_and_key() -> None:
    p = ProtocolCard(patient_id="uuid", key="something-unique")
    applied = p.apply()
    assert (
        applied.payload
        == '{"patient": "uuid", "patient_filter": null, "key": "something-unique", "data": {"title": "", "narrative": "", "recommendations": [], "status": "due", "feedback_enabled": false, "due_in": -1}}'
    )


def test_apply_method_raises_error_without_patient_id_and_key() -> None:
    p = ProtocolCard()

    with pytest.raises(ValidationError) as e:
        p.apply()
    err_msg = repr(e.value)

    assert "2 validation errors for ProtocolCard" in err_msg
    assert (
        "Field 'patient_id' or 'patient_filter' is required to apply a ProtocolCard [type=missing, input_value=None, input_type=NoneType]"
        in err_msg
    )
    assert (
        "Field 'key' is required to apply a ProtocolCard [type=missing, input_value=None, input_type=NoneType]"
        in err_msg
    )


@pytest.mark.parametrize(
    "init_params,rec1_params,rec2_params",
    [
        (
            {
                "key": "link_rec",
                "patient_id": "patientuuid",
                "title": "This is a test!",
                "narrative": "we should only expect a link and a button",
            },
            {
                "title": "this is a link",
                "button": "click this",
                "href": "https://canvasmedical.com/",
            },
            {"title": "second link", "button": "don't click this", "href": "https://google.com/"},
        ),
        (
            {
                "key": "command_rec",
                "patient_id": "patientuuid",
                "title": "This is a test for command recommendations!",
                "narrative": "we should only expect buttons to insert commands",
            },
            {
                "title": "this is a command",
                "button": "click this",
                "command": "updategoal",
                "context": {"progress": "none"},
            },
            {
                "title": "another command",
                "button": "hypertension",
                "command": "diagnose",
                "context": {"background": "stuff"},
            },
        ),
        (
            {
                "patient_id": "patientuuid",
                "key": "command_rec_with_coding_filter",
                "title": "This is a test for command recommendations with coding filters!",
                "narrative": "we should only expect buttons to insert commands",
            },
            {
                "title": "hypertension",
                "button": "diagnose",
                "command": "diagnose",
                "context": {"background": "hey", "icd10_code": "I10"},
            },
            {
                "title": "fake medication",
                "button": "prescribe",
                "command": "prescribe",
                "context": {"sig": "1pobid"},
            },
        ),
    ],
)
def test_add_recommendations(
    init_params: dict[Any, Any], rec1_params: dict[Any, Any], rec2_params: dict[Any, Any]
) -> None:
    p = ProtocolCard(**init_params)
    p.add_recommendation(**rec1_params)
    p.recommendations.append(Recommendation(**rec2_params))
    assert p.values == {
        "title": init_params["title"],
        "narrative": init_params["narrative"],
        "recommendations": [
            {
                "title": rec1_params.get("title", None),
                "button": rec1_params.get("button", None),
                "href": rec1_params.get("href", None),
                "command": {"type": rec1_params["command"]} if "command" in rec1_params else {},
                "context": rec1_params.get("context", {}),
                "key": 0,
            },
            {
                "title": rec2_params.get("title", None),
                "button": rec2_params.get("button", None),
                "href": rec2_params.get("href", None),
                "command": {"type": rec2_params["command"]} if "command" in rec2_params else {},
                "context": rec2_params.get("context", {}),
                "key": 1,
            },
        ],
        "status": "due",
        "due_in": -1,
        "feedback_enabled": False,
    }


@pytest.mark.parametrize(
    "Command,init_params",
    [
        (AssessCommand, {}),
        (DiagnoseCommand, {"icd10_code": "I10"}),
        (GoalCommand, {}),
        (HistoryOfPresentIllnessCommand, {}),
        (MedicationStatementCommand, {"fdb_code": "fakeroo"}),
        (PlanCommand, {}),
        (PrescribeCommand, {"fdb_code": "fake"}),
        (QuestionnaireCommand, {}),
        (ReasonForVisitCommand, {}),
        (StopMedicationCommand, {}),
        (UpdateGoalCommand, {}),
    ],
)
def test_add_recommendations_from_commands(
    Command: type[_BaseCommand], init_params: dict[str, str]
) -> None:
    cmd = Command(**init_params)
    p = ProtocolCard(patient_id="uuid", key="commands")
    p.recommendations.append(cmd.recommend())
    p.recommendations.append(cmd.recommend(title="hello", button="click"))
    p.add_recommendation(
        title="yeehaw", button="click here", command=cmd.Meta.key.lower(), context=init_params
    )

    rec1, rec2, rec3 = p.values["recommendations"]
    assert rec1["title"] == ""
    assert rec1["button"] == cmd.constantized_key().lower().replace("_", " ")
    assert rec1["href"] is None
    assert rec1["context"] == cmd.values
    assert rec1["command"]["type"] == cmd.Meta.key.lower()

    assert rec2["title"] == "hello"
    assert rec2["button"] == "click"
    assert rec2["href"] is None
    assert rec2["context"] == cmd.values
    assert rec2["command"]["type"] == cmd.Meta.key.lower()

    assert rec3["title"] == "yeehaw"
    assert rec3["button"] == "click here"
    assert rec3["href"] is None
    assert rec3["command"]["type"] == cmd.Meta.key.lower()
    for k, v in init_params.items():
        assert rec3["context"][k] == v
