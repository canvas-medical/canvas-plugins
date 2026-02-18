import pytest

from canvas_sdk.clients.sendgrid.structures.address import Address
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test Address dataclass has correct field types."""
    tested = Address
    fields = {
        "email": str,
        "name": str,
    }
    assert is_dataclass(tested, fields)


@pytest.mark.parametrize(
    ("address", "expected"),
    [
        pytest.param(
            Address(email="test@example.com", name="Test User"),
            {"email": "test@example.com", "name": "Test User"},
            id="basic_address",
        ),
        pytest.param(
            Address(email="jane.doe@company.org", name="Jane Doe"),
            {"email": "jane.doe@company.org", "name": "Jane Doe"},
            id="another_address",
        ),
    ],
)
def test_to_dict(address: Address, expected: dict) -> None:
    """Test Address.to_dict converts instance to dictionary."""
    result = address.to_dict()
    assert result == expected
