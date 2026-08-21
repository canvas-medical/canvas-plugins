from datetime import date
from uuid import uuid4

import pytest
from pydantic import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.commands.commands.immunize import ImmunizeCommand
from canvas_sdk.test_utils.factories.vaccine import VaccineFactory, VaccineLotFactory

NOTE_UUID = "note-uuid"


def test_lot_id_and_lot_number_are_mutually_exclusive() -> None:
    """A lot is either drawn from inventory or recorded as free text, never both."""
    with pytest.raises(ValidationError, match="Only one of 'lot_id' and 'lot_number' may be set"):
        ImmunizeCommand(note_uuid=NOTE_UUID, lot_id=uuid4(), lot_number="FREE-TEXT-01").originate()


def test_a_free_text_lot_number_alone_is_accepted() -> None:
    """A lot that is not stocked is recorded as free text."""
    command = ImmunizeCommand(note_uuid=NOTE_UUID, lot_number="FREE-TEXT-01")

    assert command.originate().type == EffectType.ORIGINATE_IMMUNIZE_COMMAND


def test_lot_number_is_held_to_the_length_the_record_accepts() -> None:
    """Lot numbers longer than the record accepts are rejected."""
    with pytest.raises(ValidationError):
        ImmunizeCommand(note_uuid=NOTE_UUID, lot_number="X" * 21)


def test_values_serializes_uuids_and_dates_for_the_payload(db: None) -> None:
    """UUIDs and dates reach the effect payload as JSON-safe strings."""
    lot_id = uuid4()
    command = ImmunizeCommand(
        note_uuid=NOTE_UUID,
        lot_id=lot_id,
        expiration_date=date(2027, 6, 30),
        sig="0.5 mL IM",
        consent_given=True,
    )

    values = command.values

    assert values["lot_id"] == str(lot_id)
    assert values["expiration_date"] == "2027-06-30"
    assert values["sig"] == "0.5 mL IM"
    assert values["consent_given"] is True


def test_can_be_originated_without_any_values() -> None:
    """An empty Immunize is a valid starting point for a provider to fill in."""
    assert (
        ImmunizeCommand(note_uuid=NOTE_UUID).originate().type
        == EffectType.ORIGINATE_IMMUNIZE_COMMAND
    )


@pytest.mark.django_db
def test_a_lot_fills_in_the_details_the_caller_left_alone() -> None:
    """Referencing a lot carries its manufacturer and expiration."""
    lot = VaccineLotFactory.create(mvx_code="ASZ", expiration_date=date(2027, 6, 30))

    values = ImmunizeCommand(note_uuid=NOTE_UUID, lot_id=lot.id).values

    assert values["manufacturer"] == "AstraZeneca"
    assert values["expiration_date"] == "2027-06-30"


@pytest.mark.django_db
def test_details_the_caller_set_are_never_derived_over() -> None:
    """An explicit manufacturer or expiration is passed through untouched."""
    lot = VaccineLotFactory.create(mvx_code="ASZ", expiration_date=date(2027, 6, 30))

    values = ImmunizeCommand(
        note_uuid=NOTE_UUID,
        lot_id=lot.id,
        manufacturer="Acme Vaccines",
        expiration_date=date(2028, 1, 31),
    ).values

    assert values["manufacturer"] == "Acme Vaccines"
    assert values["expiration_date"] == "2028-01-31"


@pytest.mark.django_db
def test_an_explicit_none_is_respected() -> None:
    """Clearing a field is a deliberate act, not an absence to be filled."""
    lot = VaccineLotFactory.create(mvx_code="ASZ", expiration_date=date(2027, 6, 30))

    values = ImmunizeCommand(note_uuid=NOTE_UUID, lot_id=lot.id, manufacturer=None).values

    assert values["manufacturer"] is None


@pytest.mark.django_db
def test_a_free_text_lot_derives_nothing() -> None:
    """There is no inventory record behind a free-text lot."""
    values = ImmunizeCommand(note_uuid=NOTE_UUID, lot_number="NOT-IN-INVENTORY").values

    assert "manufacturer" not in values
    assert "expiration_date" not in values


@pytest.mark.django_db
def test_a_lot_with_no_manufacturer_on_record_derives_nothing() -> None:
    """A lot missing these details contributes nothing rather than blanks."""
    lot = VaccineLotFactory.create(mvx_code="", expiration_date=None)

    values = ImmunizeCommand(note_uuid=NOTE_UUID, lot_id=lot.id).values

    assert "manufacturer" not in values
    assert "expiration_date" not in values


@pytest.mark.django_db
def test_a_lot_must_belong_to_the_chosen_vaccine() -> None:
    """A lot must be a lot of the selected vaccine."""
    vaccine = VaccineFactory.create()
    other_lot = VaccineLotFactory.create(vaccine=VaccineFactory.create())

    with pytest.raises(ValidationError, match="does not belong to vaccine"):
        ImmunizeCommand(note_uuid=NOTE_UUID, vaccine_id=vaccine.id, lot_id=other_lot.id).originate()


@pytest.mark.django_db
def test_a_lot_of_the_chosen_vaccine_is_accepted() -> None:
    """The matching case passes validation."""
    vaccine = VaccineFactory.create()
    lot = VaccineLotFactory.create(vaccine=vaccine)

    command = ImmunizeCommand(note_uuid=NOTE_UUID, vaccine_id=vaccine.id, lot_id=lot.id)

    assert command.originate().type == EffectType.ORIGINATE_IMMUNIZE_COMMAND


@pytest.mark.django_db
def test_a_lot_without_a_vaccine_cannot_match_one() -> None:
    """A lot whose vaccine was removed is not a lot of anything."""
    vaccine = VaccineFactory.create()
    orphan = VaccineLotFactory.create(vaccine=None)

    with pytest.raises(ValidationError, match="does not belong to vaccine"):
        ImmunizeCommand(note_uuid=NOTE_UUID, vaccine_id=vaccine.id, lot_id=orphan.id).originate()


@pytest.mark.django_db
def test_a_lot_alone_is_not_checked_against_a_vaccine() -> None:
    """With no vaccine named there is nothing to match against."""
    lot = VaccineLotFactory.create()

    command = ImmunizeCommand(note_uuid=NOTE_UUID, lot_id=lot.id)

    assert command.originate().type == EffectType.ORIGINATE_IMMUNIZE_COMMAND


@pytest.mark.django_db
def test_an_inactive_vaccine_is_rejected() -> None:
    """A vaccine that is no longer active cannot be administered."""
    vaccine = VaccineFactory.create(active=False)

    with pytest.raises(ValidationError, match="No active vaccine found"):
        ImmunizeCommand(note_uuid=NOTE_UUID, vaccine_id=vaccine.id).originate()


@pytest.mark.django_db
def test_an_unknown_lot_id_is_rejected() -> None:
    """A lot id that matches no inventory record is rejected."""
    with pytest.raises(ValidationError, match="Vaccine lot with id .* not found"):
        ImmunizeCommand(note_uuid=NOTE_UUID, lot_id=uuid4()).originate()
