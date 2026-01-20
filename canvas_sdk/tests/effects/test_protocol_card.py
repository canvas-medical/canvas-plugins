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


class NotACommand:
    """A class that is not a _BaseCommand subclass."""

    pass


def test_apply_method_succeeds_with_patient_id_and_key() -> None:
    """Test that the apply method succeeds with all required fields."""
    p = ProtocolCard(patient_id="uuid", key="something-unique")
    applied = p.apply()
    assert (
        applied.payload
        == '{"patient": "uuid", "patient_filter": null, "key": "something-unique", "data": {"title": "", "narrative": "", "recommendations": [], "status": "due", "feedback_enabled": false, "due_in": -1, "can_be_snoozed": false}}'
    )


def test_apply_method_raises_error_without_patient_id_and_key() -> None:
    """Test that the apply method raises an error when missing required fields."""
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
            {
                "title": "second link",
                "button": "don't click this",
                "href": "https://google.com/",
            },
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
                "commands": [UpdateGoalCommand(progress="none")],
            },
            {
                "title": "another command",
                "button": "hypertension",
                "commands": [DiagnoseCommand(icd10_code="I10")],
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
                "commands": [DiagnoseCommand(icd10_code="I10")],
            },
            {
                "title": "fake medication",
                "button": "prescribe",
                "commands": [PrescribeCommand(fdb_code="fake", sig="1pobid")],
            },
        ),
    ],
)
def test_add_recommendations(
    init_params: dict[Any, Any],
    rec1_params: dict[Any, Any],
    rec2_params: dict[Any, Any],
) -> None:
    """Test that the add_recommendation method adds recommendations to the ProtocolCard."""
    p = ProtocolCard(**init_params)
    p.add_recommendation(**rec1_params)
    p.recommendations.append(Recommendation(**rec2_params))

    # Get expected command contexts for validation
    rec1_commands = rec1_params.get("commands", [])
    rec2_commands = rec2_params.get("commands", [])

    assert p.values == {
        "title": init_params["title"],
        "narrative": init_params["narrative"],
        "recommendations": [
            {
                "title": rec1_params.get("title"),
                "button": rec1_params.get("button"),
                "href": rec1_params.get("href"),
                "commands": [cmd.recommendation_context() for cmd in rec1_commands]
                if rec1_commands
                else [],
                "key": 0,
            },
            {
                "title": rec2_params.get("title"),
                "button": rec2_params.get("button"),
                "href": rec2_params.get("href"),
                "commands": [cmd.recommendation_context() for cmd in rec2_commands]
                if rec2_commands
                else [],
                "key": 1,
            },
        ],
        "status": "due",
        "due_in": -1,
        "feedback_enabled": False,
        "can_be_snoozed": False,
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
    """Test that the add_recommendation method adds recommendations from commands to the ProtocolCard."""
    cmd = Command(**init_params)
    p = ProtocolCard(patient_id="uuid", key="commands")
    p.recommendations.append(cmd.recommend())
    p.recommendations.append(cmd.recommend(title="hello", button="click"))
    p.add_recommendation(
        title="yeehaw",
        button="click here",
        commands=[cmd],
    )

    rec1, rec2, rec3 = p.values["recommendations"]

    # First recommendation - using recommend() with defaults
    assert rec1["title"] == ""
    assert rec1["button"] == cmd.constantized_key().lower().replace("_", " ")
    assert rec1["href"] is None
    assert len(rec1["commands"]) == 1
    assert rec1["commands"][0]["context"] == cmd.values | {
        "effect_type": f"ORIGINATE_{cmd.constantized_key()}_COMMAND"
    }
    assert rec1["commands"][0]["command"]["type"] == cmd.Meta.key

    # Second recommendation - using recommend() with custom title/button
    assert rec2["title"] == "hello"
    assert rec2["button"] == "click"
    assert rec2["href"] is None
    assert len(rec2["commands"]) == 1
    assert rec2["commands"][0]["context"] == cmd.values | {
        "effect_type": f"ORIGINATE_{cmd.constantized_key()}_COMMAND"
    }
    assert rec2["commands"][0]["command"]["type"] == cmd.Meta.key

    # Third recommendation - using add_recommendation() with commands list
    assert rec3["title"] == "yeehaw"
    assert rec3["button"] == "click here"
    assert rec3["href"] is None
    assert len(rec3["commands"]) == 1
    assert rec3["commands"][0]["command"]["type"] == cmd.Meta.key
    for k, v in init_params.items():
        assert rec3["commands"][0]["context"][k] == v


def test_recommendation_check_subclass_validates_command_instances() -> None:
    """Test that check_subclass validator accepts valid _BaseCommand instances."""
    # Create a valid command
    cmd = PlanCommand(narrative="Test plan")

    # This should succeed - commands is a list of _BaseCommand instances
    rec = Recommendation(title="Test", button="Click", commands=[cmd])

    assert rec.commands is not None
    assert len(rec.commands) == 1
    assert isinstance(rec.commands[0], _BaseCommand)


def test_recommendation_check_subclass_rejects_non_command_instances() -> None:
    """Test that check_subclass validator rejects non-_BaseCommand instances."""
    # Create an invalid object
    not_a_command = NotACommand()

    # This should raise a TypeError
    with pytest.raises(TypeError) as exc_info:
        Recommendation(title="Test", button="Click", commands=[not_a_command])

    assert "must be subclass of _BaseCommand" in str(exc_info.value)
    assert "NotACommand" in str(exc_info.value)


def test_recommendation_check_subclass_validates_multiple_commands() -> None:
    """Test that check_subclass validator accepts multiple valid commands."""
    cmd1 = PlanCommand(narrative="Plan 1")
    cmd2 = DiagnoseCommand(icd10_code="I10")
    cmd3 = AssessCommand(narrative="Assessment")

    rec = Recommendation(
        title="Multiple commands", button="Insert all", commands=[cmd1, cmd2, cmd3]
    )

    assert rec.commands is not None
    assert len(rec.commands) == 3
    assert all(isinstance(cmd, _BaseCommand) for cmd in rec.commands)


def test_recommendation_check_subclass_rejects_mixed_valid_invalid() -> None:
    """Test that check_subclass validator rejects list with mix of valid and invalid items."""
    cmd = PlanCommand(narrative="Valid command")
    not_a_command = NotACommand()

    # This should raise a TypeError because one item is invalid
    with pytest.raises(TypeError) as exc_info:
        Recommendation(title="Test", button="Click", commands=[cmd, not_a_command])

    assert "must be subclass of _BaseCommand" in str(exc_info.value)


def test_recommendation_check_subclass_allows_none() -> None:
    """Test that check_subclass validator allows None for commands."""
    rec = Recommendation(title="Test", button="Click", commands=None)

    assert rec.commands is None


def test_recommendation_check_subclass_allows_empty_list() -> None:
    """Test that check_subclass validator allows empty list for commands."""
    rec = Recommendation(title="Test", button="Click", commands=[])

    assert rec.commands == []
