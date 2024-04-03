import random
import string
from datetime import datetime
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
    QuestionnaireCommand,
    ReasonForVisitCommand,
    StopMedicationCommand,
)
from canvas_sdk.commands.constants import Coding


def get_field_type_unformatted(field_props: dict[str, Any]) -> str:
    if t := field_props.get("type"):
        return field_props.get("format") or t

    first_in_union: dict = field_props.get("anyOf")[0]  # type: ignore
    if "$ref" in first_in_union:
        return first_in_union["$ref"].split("#/$defs/")[-1]
    return first_in_union.get("format") or first_in_union["type"]


def get_field_type(field_props: dict) -> str:
    return get_field_type_unformatted(field_props).replace("-", "")


def random_string() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=7))


def fake(
    field_props: dict,
    Command: (
        AssessCommand
        | DiagnoseCommand
        | GoalCommand
        | HistoryOfPresentIllnessCommand
        | MedicationStatementCommand
        | PlanCommand
        | QuestionnaireCommand
        | ReasonForVisitCommand
        | StopMedicationCommand
    ),
) -> Any:
    t = get_field_type(field_props)
    match t:
        case "string":
            return random_string()
        case "integer":
            return random.randint(1, 10)
        case "datetime":
            return datetime.now()
        case "boolean":
            return random.choice([True, False])
        case "Coding":
            return Coding(system=random_string(), code=random_string(), display=random_string())
    if t[0].isupper():
        return random.choice([e for e in getattr(Command, t)])


def raises_missing_error(
    base: dict,
    Command: (
        AssessCommand
        | DiagnoseCommand
        | GoalCommand
        | HistoryOfPresentIllnessCommand
        | MedicationStatementCommand
        | PlanCommand
        | QuestionnaireCommand
        | ReasonForVisitCommand
        | StopMedicationCommand
    ),
    field: str,
) -> None:
    err_kwargs = base.copy()
    err_kwargs.pop(field)
    with pytest.raises(ValidationError) as e:
        Command(**err_kwargs)
    err_msg = repr(e.value)
    assert (
        f"1 validation error for {Command.__name__}\n{field}\n  Field required [type=missing"
        in err_msg
    )


def raises_none_error(
    base: dict,
    Command: (
        AssessCommand
        | DiagnoseCommand
        | GoalCommand
        | HistoryOfPresentIllnessCommand
        | MedicationStatementCommand
        | PlanCommand
        | QuestionnaireCommand
        | ReasonForVisitCommand
        | StopMedicationCommand
    ),
    field: str,
) -> None:
    field_type = get_field_type(Command.model_json_schema()["properties"][field])

    with pytest.raises(ValidationError) as e1:
        err_kwargs = base | {field: None}
        Command(**err_kwargs)
    err_msg1 = repr(e1.value)

    valid_kwargs = base | {field: fake({"type": field_type}, Command)}
    cmd = Command(**valid_kwargs)
    with pytest.raises(ValidationError) as e2:
        setattr(cmd, field, None)
    err_msg2 = repr(e2.value)

    expected_msg = f"1 validation error for {Command.__name__}\n{field}\n  Input should be a valid {field_type}"
    assert expected_msg in err_msg1
    assert expected_msg in err_msg2


def raises_wrong_type_error(
    base: dict,
    Command: (
        AssessCommand
        | DiagnoseCommand
        | GoalCommand
        | HistoryOfPresentIllnessCommand
        | MedicationStatementCommand
        | PlanCommand
        | QuestionnaireCommand
        | ReasonForVisitCommand
        | StopMedicationCommand
    ),
    field: str,
) -> None:
    field_type = get_field_type(Command.model_json_schema()["properties"][field])
    wrong_field_type = "integer" if field_type == "string" else "string"

    with pytest.raises(ValidationError) as e1:
        err_kwargs = base | {field: fake({"type": wrong_field_type}, Command)}
        Command(**err_kwargs)
    err_msg1 = repr(e1.value)

    valid_kwargs = base | {field: fake({"type": field_type}, Command)}
    cmd = Command(**valid_kwargs)
    err_value = fake({"type": wrong_field_type}, Command)
    with pytest.raises(ValidationError) as e2:
        setattr(cmd, field, err_value)
    err_msg2 = repr(e2.value)

    assert f"1 validation error for {Command.__name__}\n{field}" in err_msg1
    assert f"1 validation error for {Command.__name__}\n{field}" in err_msg2

    field_type = "dictionary" if field_type == "Coding" else field_type
    if field_type[0].isupper():
        assert f"Input should be an instance of {Command.__name__}.{field_type}" in err_msg1
        assert f"Input should be an instance of {Command.__name__}.{field_type}" in err_msg2
    else:
        assert f"Input should be a valid {field_type}" in err_msg1
        assert f"Input should be a valid {field_type}" in err_msg2