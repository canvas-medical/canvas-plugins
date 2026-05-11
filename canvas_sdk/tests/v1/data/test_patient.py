from unittest.mock import MagicMock, patch

import pytest

from canvas_sdk.v1.data.patient import (
    Patient,
    PatientIdentificationCard,
    PatientMetadata,
    PatientPhoto,
)


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


def _patient_with_photo(url: str | None) -> Patient:
    photo = PatientPhoto(url=url) if url is not None else None
    patient = Patient()
    patient.photos = MagicMock()
    patient.photos.first = MagicMock(return_value=photo)
    return patient


def test_patient_photo_returns_photo_when_avatar_prefix() -> None:
    """photo returns the PatientPhoto when its url is under patient-avatars."""
    patient = _patient_with_photo("patient-avatars/abc/photo.jpg")
    photo = patient.photo
    assert photo is not None
    assert photo.url == "patient-avatars/abc/photo.jpg"


def test_patient_photo_returns_none_when_no_photos() -> None:
    """photo returns None when the patient has no photos."""
    patient = _patient_with_photo(None)
    assert patient.photo is None


def test_patient_photo_returns_none_for_non_avatar_url() -> None:
    """photo returns None when the stored url is not a patient-avatars path."""
    patient = _patient_with_photo("some-other-bucket/foo.jpg")
    assert patient.photo is None


def test_patient_photo_url_returns_presigned_url() -> None:
    """photo_url returns a presigned URL when a photo exists."""
    patient = _patient_with_photo("patient-avatars/abc/photo.jpg")

    with patch(
        "canvas_sdk.v1.data.patient.presigned_url",
        return_value="https://s3.example.com/presigned",
    ) as mock:
        assert patient.photo_url == "https://s3.example.com/presigned"
        mock.assert_called_once_with("patient-avatars/abc/photo.jpg")


def test_patient_photo_url_returns_default_avatar_when_no_photo() -> None:
    """photo_url returns the default avatar URL when no photo is present."""
    patient = _patient_with_photo(None)
    assert patient.photo_url == "https://d3hn0m4rbsz438.cloudfront.net/avatar1.png"
