from unittest.mock import patch

import pytest

from canvas_sdk.v1.data.patient import PatientIdentificationCard, PatientMetadata


@pytest.mark.django_db
def test_patient_metadata_supports_large_values() -> None:
    """Test that PatientMetadata.value can store and retrieve up to 1000 characters."""
    large_value = "a" * 1000
    metadata = PatientMetadata.objects.create(key="test_key", value=large_value)

    metadata.refresh_from_db()

    assert metadata.value == large_value
    assert len(metadata.value) == 1000


def test_patient_identification_card_str() -> None:
    """__str__ returns a readable representation."""
    card = PatientIdentificationCard()
    card.dbid = 5
    card.title = "Driver License"

    assert str(card) == "PatientIdentificationCard(dbid=5, title=Driver License)"


def test_patient_identification_card_image_url_with_image() -> None:
    """image_url returns a presigned URL when image is set."""
    card = PatientIdentificationCard()
    card.image = "id_cards/front.jpg"

    with patch(
        "canvas_sdk.v1.data.patient.presigned_url",
        return_value="https://s3.example.com/presigned",
    ) as mock:
        assert card.image_url == "https://s3.example.com/presigned"
        mock.assert_called_once_with("id_cards/front.jpg")


def test_patient_identification_card_image_url_without_image() -> None:
    """image_url returns None when image is empty."""
    card = PatientIdentificationCard()
    card.image = ""

    assert card.image_url is None
