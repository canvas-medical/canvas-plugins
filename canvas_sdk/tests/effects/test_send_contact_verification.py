from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from canvas_sdk.effects.send_contact_verification import SendContactVerificationEffect


@pytest.fixture
def valid_contact_point_id() -> str:
    """Fixture that provides a valid UUID string for a contact point."""
    return str(uuid4())


@pytest.fixture
def effect(valid_contact_point_id: str) -> SendContactVerificationEffect:
    """Fixture that provides a SendContactVerificationEffect instance with a valid contact_point_id."""
    return SendContactVerificationEffect(contact_point_id=valid_contact_point_id)


def test_values_property(
    effect: SendContactVerificationEffect, valid_contact_point_id: str
) -> None:
    """Test that the values property returns the correct contact_point_id mapping."""
    assert effect.values == {"contact_point_id": valid_contact_point_id}


@patch("canvas_sdk.effects.send_contact_verification.PatientContactPoint.objects.filter")
def test_get_error_details_valid_contact_point(
    mock_filter: MagicMock, effect: SendContactVerificationEffect
) -> None:
    """Test that no errors are returned if the contact point exists."""
    mock_filter.return_value.exists.return_value = True
    errors = effect._get_error_details(method=None)
    assert errors == []


@patch("canvas_sdk.effects.send_contact_verification.PatientContactPoint.objects.filter")
def test_get_error_details_invalid_contact_point(
    mock_filter: MagicMock, effect: SendContactVerificationEffect, valid_contact_point_id: str
) -> None:
    """Test that an error is returned if the contact point does not exist."""
    mock_filter.return_value.exists.return_value = False
    with patch.object(
        effect, "_create_error_detail", return_value="error_detail"
    ) as mock_create_error:
        errors = effect._get_error_details(method=None)
        mock_create_error.assert_called_once_with(
            "value",
            "Patient Contact Point does not exist",
            valid_contact_point_id,
        )
        assert errors == [mock_create_error.return_value]
