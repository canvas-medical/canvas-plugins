"""Tests for the ServiceProvider create/update/deactivate effects."""

import json
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.service_provider import ServiceProvider


@pytest.fixture
def mock_provider_exists() -> Generator[MagicMock]:
    """Mock the ServiceProvider existence check to return True by default."""
    with patch("canvas_sdk.effects.service_provider.ServiceProviderModel.objects") as mock_provider:
        mock_provider.filter.return_value.exists.return_value = True
        yield mock_provider


def test_create_serializes_only_explicitly_set_fields() -> None:
    """create() emits a payload with required fields plus ONLY the optional fields set."""
    effect = ServiceProvider(
        first_name="Jane",
        last_name="Doe",
        specialty="Cardiology",
        business_address="123 Main St",
        business_phone="555-1234",
        npi="1234567890",
        direct_address="jane.doe@direct.example.org",
    ).create()

    assert effect.type == EffectType.CREATE_SERVICE_PROVIDER

    payload = json.loads(effect.payload)
    data = payload["data"]

    assert "id" not in data
    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Doe"
    assert data["specialty"] == "Cardiology"
    assert data["business_address"] == "123 Main St"
    assert data["business_phone"] == "555-1234"
    assert data["npi"] == "1234567890"
    assert data["direct_address"] == "jane.doe@direct.example.org"
    # Fields the author never set must be ABSENT, not sent as null/True — create()
    # must never null-clobber or reactivate on the receiving end.
    assert "is_active" not in data
    assert "business_fax" not in data
    assert "practice_name" not in data
    assert "notes" not in data


def test_create_with_only_required_fields_omits_optionals() -> None:
    """create() with only the required fields sends exactly those keys."""
    effect = ServiceProvider(
        first_name="Jane",
        specialty="Cardiology",
        business_address="123 Main St",
    ).create()

    data = json.loads(effect.payload)["data"]
    assert set(data) == {"first_name", "specialty", "business_address"}


def test_create_with_explicit_is_active_false_is_present() -> None:
    """create() with is_active=False explicitly includes it as False."""
    effect = ServiceProvider(
        first_name="Jane",
        specialty="Cardiology",
        business_address="123 Main St",
        is_active=False,
    ).create()

    data = json.loads(effect.payload)["data"]
    assert data["is_active"] is False


def test_create_allows_organization_without_last_name() -> None:
    """create() succeeds for an organization provider that has no last name."""
    effect = ServiceProvider(
        first_name="Acme Imaging Center",
        specialty="Radiology",
        business_address="1 Hospital Way",
    ).create()

    assert effect.type == EffectType.CREATE_SERVICE_PROVIDER
    payload = json.loads(effect.payload)
    assert payload["data"]["first_name"] == "Acme Imaging Center"


def test_create_rejects_id() -> None:
    """create() raises when id is set, since create assigns a new id."""
    with pytest.raises(ValidationError) as exc_info:
        ServiceProvider(
            id="00000000-0000-0000-0000-000000000099",
            first_name="Jane",
            specialty="Cardiology",
            business_address="123 Main St",
        ).create()

    assert "id should not be set" in str(exc_info.value).lower()


def test_create_requires_first_name() -> None:
    """create() raises when first_name is missing."""
    with pytest.raises(ValidationError) as exc_info:
        ServiceProvider(specialty="Cardiology", business_address="123 Main St").create()

    assert "first_name" in str(exc_info.value)


def test_create_requires_specialty() -> None:
    """create() raises when specialty is missing."""
    with pytest.raises(ValidationError) as exc_info:
        ServiceProvider(first_name="Jane", business_address="123 Main St").create()

    assert "specialty" in str(exc_info.value)


def test_create_requires_business_address() -> None:
    """create() raises when business_address is missing."""
    with pytest.raises(ValidationError) as exc_info:
        ServiceProvider(first_name="Jane", specialty="Cardiology").create()

    assert "business_address" in str(exc_info.value)


def test_update_serializes_only_provided_fields(mock_provider_exists: MagicMock) -> None:
    """update() emits an UPDATE effect keyed by id containing only the fields the caller set."""
    effect = ServiceProvider(
        id="00000000-0000-0000-0000-000000000001",
        notes="updated notes",
    ).update()

    assert effect.type == EffectType.UPDATE_SERVICE_PROVIDER

    data = json.loads(effect.payload)["data"]
    assert data["id"] == "00000000-0000-0000-0000-000000000001"
    assert data["notes"] == "updated notes"
    # Fields the caller did not touch must NOT be present, so an update cannot
    # accidentally reactivate a deactivated provider or wipe other fields.
    assert "is_active" not in data
    assert "first_name" not in data
    assert "npi" not in data


def test_update_reactivation_sends_is_active(mock_provider_exists: MagicMock) -> None:
    """update(is_active=True) emits is_active in the payload to reactivate a provider."""
    effect = ServiceProvider(
        id="00000000-0000-0000-0000-000000000001",
        is_active=True,
    ).update()

    data = json.loads(effect.payload)["data"]
    assert data["is_active"] is True


def test_update_requires_id() -> None:
    """update() raises when id is missing."""
    with pytest.raises(ValidationError) as exc_info:
        ServiceProvider(notes="updated notes").update()

    assert "'id' is required to update" in str(exc_info.value)


def test_update_validates_provider_exists() -> None:
    """update() raises when no provider matches the supplied id."""
    with patch("canvas_sdk.effects.service_provider.ServiceProviderModel.objects") as mock_provider:
        mock_provider.filter.return_value.exists.return_value = False

        with pytest.raises(ValidationError) as exc_info:
            ServiceProvider(id="00000000-0000-0000-0000-000000000098", notes="x").update()

    assert "does not exist" in str(exc_info.value)


def test_update_rejects_explicit_null_first_name(mock_provider_exists: MagicMock) -> None:
    """update(first_name=None) raises a clean ValidationError (required identifier)."""
    with pytest.raises(ValidationError) as exc_info:
        ServiceProvider(id="00000000-0000-0000-0000-000000000001", first_name=None).update()

    assert "first_name" in str(exc_info.value)


def test_update_rejects_explicit_null_specialty(mock_provider_exists: MagicMock) -> None:
    """update(specialty=None) raises a clean ValidationError (required identifier)."""
    with pytest.raises(ValidationError) as exc_info:
        ServiceProvider(id="00000000-0000-0000-0000-000000000001", specialty=None).update()

    assert "specialty" in str(exc_info.value)


def test_update_allows_explicit_null_last_name(mock_provider_exists: MagicMock) -> None:
    """update(last_name=None) is allowed — last_name is legitimately blank-able."""
    effect = ServiceProvider(id="00000000-0000-0000-0000-000000000001", last_name=None).update()

    data = json.loads(effect.payload)["data"]
    assert "last_name" in data


def test_deactivate_serializes_payload(mock_provider_exists: MagicMock) -> None:
    """deactivate() emits a DEACTIVATE effect with only the id."""
    effect = ServiceProvider(id="00000000-0000-0000-0000-000000000002").deactivate()

    assert effect.type == EffectType.DEACTIVATE_SERVICE_PROVIDER
    assert json.loads(effect.payload) == {"data": {"id": "00000000-0000-0000-0000-000000000002"}}


def test_deactivate_requires_id() -> None:
    """deactivate() raises when id is missing."""
    with pytest.raises(ValidationError) as exc_info:
        ServiceProvider().deactivate()

    assert "'id' is required to deactivate" in str(exc_info.value)


def test_deactivate_validates_provider_exists() -> None:
    """deactivate() raises when no provider matches the supplied id."""
    with patch("canvas_sdk.effects.service_provider.ServiceProviderModel.objects") as mock_provider:
        mock_provider.filter.return_value.exists.return_value = False

        with pytest.raises(ValidationError) as exc_info:
            ServiceProvider(id="00000000-0000-0000-0000-000000000097").deactivate()

    assert "does not exist" in str(exc_info.value)
