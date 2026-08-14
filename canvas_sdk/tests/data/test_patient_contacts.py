"""Tests for the patient-contact read models exposed through `canvas_sdk.v1.data`."""

import datetime

import pytest

from canvas_sdk.v1.data import (
    ContactCategory,
    Patient,
    PatientContactCategory,
    PatientContactPerson,
)


@pytest.mark.parametrize(
    "field_name",
    ["relationship", "emergency_contact", "authorized_for_release_of_information"],
)
def test_patient_contact_person_hides_deprecated_fields(field_name: str) -> None:
    """The deprecated relationship/boolean columns are not exposed to plugins."""
    field_names = {field.name for field in PatientContactPerson._meta.get_fields()}

    assert field_name not in field_names


@pytest.mark.django_db
def test_patient_contacts_round_trip_through_the_orm() -> None:
    """A contact, its category coding, and a related-patient reference are all queryable."""
    patient = Patient.objects.create(
        id="a" * 32, first_name="Ada", last_name="Lovelace", birth_date=datetime.date(1815, 12, 10)
    )
    spouse = Patient.objects.create(
        id="b" * 32, first_name="Alan", last_name="Turing", birth_date=datetime.date(1912, 6, 23)
    )
    category = ContactCategory.objects.create(
        code="EMC", system="INTERNAL", name="Emergency contact"
    )

    inline_contact = PatientContactPerson.objects.create(
        patient=patient, name="Jane Doe", phone_number="5551234567", email="jane@example.com"
    )
    related_contact = PatientContactPerson.objects.create(patient=patient, related_patient=spouse)
    PatientContactCategory.objects.create(contact_person=inline_contact, category=category)

    contacts = PatientContactPerson.objects.filter(patient=patient).order_by("dbid")

    assert [contact.name for contact in contacts] == ["Jane Doe", ""]
    assert related_contact.related_patient == spouse
    assert [c.category.code for c in inline_contact.categories.all()] == ["EMC"]
    assert ContactCategory.objects.get(code="EMC").system == "INTERNAL"


@pytest.mark.django_db
def test_contact_models_render_readable_str() -> None:
    """Each contact read model has a human-readable __str__ for logs and the admin."""
    category = ContactCategory.objects.create(
        code="EMC", system="INTERNAL", name="Emergency contact"
    )
    contact = PatientContactPerson.objects.create(name="Jane Doe")
    link = PatientContactCategory.objects.create(contact_person=contact, category=category)

    assert str(category) == "Emergency contact (EMC)"
    assert str(contact) == f"PatientContactPerson(id={contact.id}, name=Jane Doe)"
    assert str(link) == f"PatientContactCategory(dbid={link.dbid})"
