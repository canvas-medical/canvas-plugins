from canvas_sdk.clients.sendgrid.constants.recipient_type import RecipientType
from canvas_sdk.clients.sendgrid.structures.address import Address
from canvas_sdk.clients.sendgrid.structures.recipient import Recipient
from canvas_sdk.tests.conftest import is_dataclass


def test_class() -> None:
    """Test Recipient dataclass has correct field types."""
    tested = Recipient
    fields = {
        "address": Address,
        "type": RecipientType,
    }
    assert is_dataclass(tested, fields)
