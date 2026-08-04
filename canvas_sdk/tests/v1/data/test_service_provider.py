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
    assert persisted.is_customer_managed is False
    assert persisted.science_contact_id is None


@pytest.mark.django_db
def test_service_provider_new_fields_round_trip_explicit_values() -> None:
    """Explicit values for the new fields round-trip through the SDK model."""
    provider = ServiceProviderFactory.create(
        is_active=False,
        npi="9876543210",
        direct_address="john.smith@direct.example.org",
        science_contact_id=4242,
    )

    persisted = ServiceProvider.objects.get(pk=provider.pk)

    assert persisted.is_active is False
    assert persisted.npi == "9876543210"
    assert persisted.direct_address == "john.smith@direct.example.org"
    assert persisted.science_contact_id == 4242


@pytest.mark.django_db
def test_is_customer_managed_separates_local_from_global_providers() -> None:
    """is_customer_managed lets a plugin search the customer's own directory first.

    Unlike a null Science link, it is unambiguous: legacy rows that predate science_contact_id
    tracking are Science-derived and stay False.
    """
    local = ServiceProviderFactory.create(first_name="Local", is_customer_managed=True)
    science_derived = ServiceProviderFactory.create(first_name="Global", is_customer_managed=False)

    customer_owned = ServiceProvider.objects.filter(is_customer_managed=True)
    everything_else = ServiceProvider.objects.filter(is_customer_managed=False)

    assert list(customer_owned.values_list("pk", flat=True)) == [local.pk]
    assert list(everything_else.values_list("pk", flat=True)) == [science_derived.pk]


@pytest.mark.django_db
def test_as_search_result_threads_the_provider_id() -> None:
    """The autocomplete result carries the provider id, so a command reuses this exact record."""
    provider = ServiceProviderFactory.create(
        first_name="Casey",
        last_name="External",
        specialty="Cardiology",
        practice_name="Northside",
        business_address="123 Medical Plaza",
    )

    result = provider.as_search_result()

    assert result["text"] == "Casey External"
    assert result["description"] == "Cardiology • Northside • 123 Medical Plaza"
    assert result["extra"]["contact"]["service_provider_id"] == provider.dbid
    # The Science link is passed through as-is, never the provider's own id.
    assert result["extra"]["contact"]["science_contact_id"] is None
    assert result["extra"]["contact"]["firstName"] == "Casey"


@pytest.mark.django_db
def test_as_search_result_passes_through_a_real_science_link() -> None:
    """A Science-derived provider reports its real link rather than claiming to have none."""
    provider = ServiceProviderFactory.create(is_customer_managed=False, science_contact_id=4242)

    assert provider.as_search_result()["extra"]["contact"]["science_contact_id"] == 4242


@pytest.mark.django_db
def test_as_search_result_never_sends_the_provider_id_as_a_science_link() -> None:
    """A provider with no Science link sends null, so its own id cannot land in that column."""
    provider = ServiceProviderFactory.create(science_contact_id=None)

    contact = provider.as_search_result()["extra"]["contact"]

    assert contact["science_contact_id"] is None
    # No "id" key either: the write path reads one as a Science contact id when nothing else says
    # which provider this is.
    assert "id" not in contact


@pytest.mark.django_db
def test_as_search_contact_does_not_send_a_science_link() -> None:
    """The care team mutation takes exactly one identifier, so only serviceProviderId is sent."""
    provider = ServiceProviderFactory.create(is_customer_managed=False, science_contact_id=4242)

    assert "scienceContactId" not in provider.as_search_contact()


@pytest.mark.django_db
def test_as_search_result_omits_blank_description_parts() -> None:
    """Missing practice name and address do not leave empty separators in the description."""
    provider = ServiceProviderFactory.create(
        specialty="Cardiology", practice_name=None, business_address=None
    )

    assert provider.as_search_result()["description"] == "Cardiology"


@pytest.mark.django_db
def test_as_search_result_text_has_no_stray_whitespace() -> None:
    """An organization has no last name, so the text must not keep a trailing space."""
    provider = ServiceProviderFactory.create(first_name="Acme Imaging", last_name="")

    assert provider.as_search_result()["text"] == "Acme Imaging"


@pytest.mark.django_db
def test_as_search_contact_threads_the_provider_id() -> None:
    """The contact record carries serviceProviderId, so the care team mutation attaches to it."""
    provider = ServiceProviderFactory.create(first_name="Casey", business_fax="5550101")

    contact = provider.as_search_contact()

    assert contact["serviceProviderId"] == provider.dbid
    assert contact["id"] == provider.dbid
    assert contact["firstName"] == "Casey"
    assert contact["businessFax"] == "5550101"
    # A contact record is consumed directly, with no autocomplete wrapper.
    assert "extra" not in contact
    assert "text" not in contact


@pytest.mark.django_db
@pytest.mark.parametrize("method", ["as_search_result", "as_search_contact"])
def test_annotations_default_to_empty(method: str) -> None:
    """Annotations are the caller's to supply; nothing is inferred from is_active."""
    provider = ServiceProviderFactory.create(is_active=False)

    assert getattr(provider, method)()["annotations"] == []


@pytest.mark.django_db
@pytest.mark.parametrize("method", ["as_search_result", "as_search_contact"])
def test_annotations_are_copied_not_aliased(method: str) -> None:
    """The payload holds its own list, so a caller's list cannot mutate it afterwards."""
    provider = ServiceProviderFactory.create()
    annotations = ["Inactive"]

    payload = getattr(provider, method)(annotations)
    annotations.append("Mutated")

    assert payload["annotations"] == ["Inactive"]
