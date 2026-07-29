import pytest

from canvas_sdk.test_utils.factories.service_provider import ServiceProviderFactory
from canvas_sdk.v1.data import ServiceProvider


@pytest.mark.django_db
def test_service_provider_new_fields_model_defaults() -> None:
    """The new fields fall back to model-level defaults when not supplied.

    Built directly (NOT via the factory, which sets the three fields explicitly) so the
    model's own default/null behavior is exercised and round-trips through the database.
    """
    provider = ServiceProvider(first_name="Jane", specialty="Cardiology")
    provider.save()

    persisted = ServiceProvider.objects.get(pk=provider.pk)

    assert persisted.is_active is True
    assert persisted.npi is None
    assert persisted.direct_address is None
    assert persisted.science_contact_id is None


@pytest.mark.django_db
def test_service_provider_new_fields_round_trip_explicit_values() -> None:
    """Explicit values for the new fields round-trip through the SDK model."""
    provider = ServiceProviderFactory.create(
        is_active=False,
        npi="9876543210",
        direct_address="john.smith@direct.example.org",
    )

    persisted = ServiceProvider.objects.get(pk=provider.pk)

    assert persisted.is_active is False
    assert persisted.npi == "9876543210"
    assert persisted.direct_address == "john.smith@direct.example.org"


@pytest.mark.django_db
def test_science_contact_id_separates_local_from_global_providers() -> None:
    """science_contact_id lets a plugin tell customer-created providers from Science-derived ones.

    This is what makes "search the customer's own providers first, fall back to the shared Science
    directory" implementable in a plugin.
    """
    local = ServiceProviderFactory.create(first_name="Local", science_contact_id=None)
    science_derived = ServiceProviderFactory.create(first_name="Global", science_contact_id=4242)

    local_only = ServiceProvider.objects.filter(science_contact_id__isnull=True)
    global_only = ServiceProvider.objects.filter(science_contact_id__isnull=False)

    assert list(local_only.values_list("pk", flat=True)) == [local.pk]
    assert list(global_only.values_list("pk", flat=True)) == [science_derived.pk]
    assert ServiceProvider.objects.get(pk=science_derived.pk).science_contact_id == 4242
