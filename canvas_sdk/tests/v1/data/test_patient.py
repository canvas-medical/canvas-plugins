import pytest

from canvas_sdk.v1.data.patient import PatientMetadata


@pytest.mark.django_db
def test_patient_metadata_supports_large_values() -> None:
    """Test that PatientMetadata.value can store and retrieve up to 1000 characters."""
    large_value = "a" * 1000
    metadata = PatientMetadata.objects.create(key="test_key", value=large_value)

    metadata.refresh_from_db()

    assert metadata.value == large_value
    assert len(metadata.value) == 1000
