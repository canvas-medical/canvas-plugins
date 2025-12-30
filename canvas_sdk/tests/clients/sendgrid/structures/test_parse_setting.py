import pytest

from canvas_sdk.clients.sendgrid.structures.parse_setting import ParseSetting
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test ParseSetting dataclass has correct field types."""
    tested = ParseSetting
    fields = {
        "url": str,
        "hostname": str,
        "spam_check": bool,
        "send_raw": bool,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param(
            {
                "url": "https://example.com/parse",
                "hostname": "mail.example.com",
                "spam_check": True,
                "send_raw": False,
            },
            ParseSetting(
                url="https://example.com/parse",
                hostname="mail.example.com",
                spam_check=True,
                send_raw=False,
            ),
            id="basic_parse_setting",
        ),
        pytest.param(
            {
                "url": "https://test.com/incoming",
                "hostname": "inbound.test.com",
                "spam_check": 1,
                "send_raw": 1,
            },
            ParseSetting(
                url="https://test.com/incoming",
                hostname="inbound.test.com",
                spam_check=True,
                send_raw=True,
            ),
            id="parse_setting_with_integers",
        ),
    ],
)
def test_from_dict(data: dict, expected: ParseSetting) -> None:
    """Test ParseSetting.from_dict creates instance from dictionary."""
    test = ParseSetting
    result = test.from_dict(data)
    assert result == expected


@pytest.mark.parametrize(
    ("parse_setting", "expected"),
    [
        pytest.param(
            ParseSetting(
                url="https://example.com/parse",
                hostname="mail.example.com",
                spam_check=True,
                send_raw=False,
            ),
            {
                "url": "https://example.com/parse",
                "hostname": "mail.example.com",
                "spam_check": True,
                "send_raw": False,
            },
            id="parse_setting_to_dict",
        ),
        pytest.param(
            ParseSetting(
                url="https://test.com/incoming",
                hostname="inbound.test.com",
                spam_check=False,
                send_raw=True,
            ),
            {
                "url": "https://test.com/incoming",
                "hostname": "inbound.test.com",
                "spam_check": False,
                "send_raw": True,
            },
            id="another_parse_setting_to_dict",
        ),
    ],
)
def test_to_dict(parse_setting: ParseSetting, expected: dict) -> None:
    """Test ParseSetting.to_dict converts instance to dictionary."""
    result = parse_setting.to_dict()
    assert result == expected
