import decimal
from datetime import date, datetime
from typing import get_origin

import pytest
import requests

import settings
from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.commands.constants import ClinicalQuantity, Coding
from canvas_sdk.commands.tests.test_utils import (
    COMMANDS,
    MaskedValue,
    create_new_note,
    get_token,
)


@pytest.fixture(scope="session")
def token() -> MaskedValue:
    return get_token()


@pytest.fixture(scope="session")
def new_note(token: MaskedValue) -> dict:
    return create_new_note(token)


@pytest.fixture
def command_type_map() -> dict[str, type]:
    return {
        "AutocompleteField": str,
        "MultiLineTextField": str,
        "TextField": str,
        "ChoiceField": str,
        "DateField": datetime,
        "ApproximateDateField": date,
        "IntegerField": int,
        "DecimalField": decimal.Decimal,
    }


@pytest.mark.integtest
@pytest.mark.parametrize(
    "Command",
    COMMANDS,
)
def test_command_schema_matches_command_api(
    token: MaskedValue,
    command_type_map: dict[str, str],
    new_note: dict,
    Command: _BaseCommand,
) -> None:
    # first create the command in the new note
    data = {"noteKey": new_note["externallyExposableId"], "schemaKey": Command.Meta.key}
    headers = {"Authorization": f"Bearer {token.value}"}
    url = f"{settings.INTEGRATION_TEST_URL}/core/api/v1/commands/"
    command_resp = requests.post(url, headers=headers, data=data).json()
    assert "uuid" in command_resp
    command_uuid = command_resp["uuid"]

    # next, request the fields of the newly created command
    url = f"{settings.INTEGRATION_TEST_URL}/core/api/v1/commands/{command_uuid}/fields/"
    command_fields_resp = requests.get(url, headers=headers).json()
    assert command_fields_resp["schema"] == Command.Meta.key

    command_fields = command_fields_resp["fields"]
    if Command.Meta.key == "questionnaire":
        # questionnaire's fields vary per questionnaire, so just check the first two fields which never vary
        command_fields = command_fields[:2]
    expected_fields = Command.command_schema()
    assert len(command_fields) == len(expected_fields)

    for actual_field in command_fields:
        name = actual_field["name"]
        assert name in expected_fields
        expected_field = expected_fields[name]

        assert expected_field["required"] == actual_field["required"]

        expected_type = expected_field["type"]
        if expected_type is Coding:
            expected_type = expected_type.__annotations__["code"]

        if expected_type is ClinicalQuantity:
            expected_type = expected_type.__annotations__["representative_ndc"]

        actual_type = command_type_map.get(actual_field["type"])
        if actual_field["type"] == "AutocompleteField" and name[-1] == "s":
            # this condition initially created for Prescribe.indications,
            # but could apply to other AutocompleteField fields that are lists
            # making the assumption here that if the field ends in 's' (like indications), it is a list
            assert get_origin(expected_type) == list

        else:
            assert expected_type == actual_type

        if (choices := actual_field["choices"]) is None:
            assert expected_field["choices"] is None
            continue

        assert len(expected_field["choices"]) == len(choices)
        for choice in choices:
            assert choice["value"] in expected_field["choices"]
