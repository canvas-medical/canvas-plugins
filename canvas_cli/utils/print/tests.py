import json
from typing import Any
from unittest.mock import Mock

import pytest
from requests import Response

from canvas_cli.utils.print import print


@pytest.mark.parametrize(
    "message", ["a simple message", ["an array", "of messages"], {"one": "test"}]
)
def test_print_json_outputs_valid_json(message: Any, capfd: pytest.CaptureFixture[str]) -> None:
    """Test the output of print is always valid json."""
    print.json(message)
    output, _ = capfd.readouterr()
    try:
        json.loads(output)
    except ValueError as exc:
        assert False, f"{output} is not valid json: {exc}"


def test_print_json_outputs_kwargs(capfd: pytest.CaptureFixture[str]) -> None:
    """Test the output of print contains all given kwargs."""
    print.json("A message", status_code=200, a_string="a_value", an_array=[1, 2], a_dict={"one": 2})
    output, _ = capfd.readouterr()
    try:
        json_dict = json.loads(output)

        assert json_dict.get("a_string") == "a_value"
        assert json_dict.get("an_array") == [1, 2]
        assert json_dict.get("a_dict") == {"one": 2}

    except ValueError as exc:
        assert False, f"{output} is not valid json: {exc}"


def test_print_overrides_default(capfd: pytest.CaptureFixture[str]) -> None:
    """Test using `print` defaults to Rich."""
    message = "Testing print"
    print(message)
    output, _ = capfd.readouterr()
    assert message + "\n" == output


def test_print_response_non_json_text(capfd: pytest.CaptureFixture[str]) -> None:
    """Test print.response with a non-json response."""
    response = Mock(spec=Response)
    response.status_code = 200
    response.text = "testing text"
    response.json.side_effect = json.JSONDecodeError("", "", 0)
    print.response(response)
    output, _ = capfd.readouterr()
    assert json.loads(output) == json.loads(
        '{"status_code": 200, "success": true, "message": "testing text"}'
    )


def test_print_response_json_text(capfd: pytest.CaptureFixture[str]) -> None:
    """Test print.response with a json response."""
    response = Mock(spec=Response)
    response.status_code = 201
    response.json.return_value = {"something": True}
    print.response(response)
    output, _ = capfd.readouterr()
    assert json.loads(output) == json.loads(
        '{"status_code": 201, "success": true, "message": {"something": true} }'
    )
