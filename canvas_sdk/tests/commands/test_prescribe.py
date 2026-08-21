import json
from decimal import Decimal
from unittest.mock import patch
from uuid import uuid4

import pytest
from pydantic import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.commands.commands.adjust_prescription import AdjustPrescriptionCommand
from canvas_sdk.commands.commands.prescribe import PrescribeCommand
from canvas_sdk.commands.commands.refill import RefillCommand

NOTE_UUID = "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
COMMAND_UUID = "1b9d6bcd-bbfd-4b2d-9b5d-ab8dfbbd4bed"


def test_send_without_override_omits_key() -> None:
    """send() with no override produces the unchanged command-only payload."""
    cmd = PrescribeCommand(command_uuid="cmd-456")

    effect = cmd.send()

    assert effect.type == EffectType.SEND_PRESCRIBE_COMMAND
    assert json.loads(effect.payload) == {"command": "cmd-456"}


def test_send_with_override_includes_key() -> None:
    """send() with a valid override adds practice_location_override to the payload."""
    location_id = str(uuid4())
    cmd = PrescribeCommand(command_uuid="cmd-456")

    with patch("canvas_sdk.v1.data.PracticeLocation.objects") as mock_pl:
        mock_pl.filter.return_value.exists.return_value = True
        effect = cmd.send(practice_location_override=location_id)

    payload = json.loads(effect.payload)
    assert payload["command"] == "cmd-456"
    assert payload["practice_location_override"] == location_id


def test_send_with_invalid_override_raises() -> None:
    """A nonexistent override id raises ValueError before an effect is produced."""
    cmd = PrescribeCommand(command_uuid="cmd-456")

    with patch("canvas_sdk.v1.data.PracticeLocation.objects") as mock_pl:
        mock_pl.filter.return_value.exists.return_value = False
        with pytest.raises(ValueError, match="does not exist"):
            cmd.send(practice_location_override=str(uuid4()))


# The two Surescripts-bound text fields are held to their length and nothing else. The characters
# Surescripts refuses are left alone for now — Canvas rejects those at review, as it did before —
# so this is a length pass only.
#
# Length is checked when an effect is built rather than when the field is set. On the field it raised
# at the assigning line, which breaks a plugin filling a command in from a model's output part-way
# through a handler. Deferring keeps the over-long value off the chart without crashing the handler
# that produced it.


@pytest.mark.parametrize(("field", "limit"), [("sig", 1000), ("note_to_pharmacist", 210)])
def test_text_at_the_limit_is_accepted(field: str, limit: int) -> None:
    """The boundary belongs on the allowed side, and the value is not rewritten."""
    text = "x" * limit

    command = PrescribeCommand.model_validate({"note_uuid": NOTE_UUID, field: text})

    assert getattr(command, field) == text
    assert command.originate()


@pytest.mark.parametrize(("field", "limit"), [("sig", 1000), ("note_to_pharmacist", 210)])
def test_over_long_text_can_be_set_without_raising(field: str, limit: int) -> None:
    """The regression this shape exists to prevent: assignment stays quiet."""
    text = "x" * (limit + 500)
    command = PrescribeCommand()

    setattr(command, field, text)

    assert getattr(command, field) == text


@pytest.mark.parametrize(
    ("field", "limit", "message"),
    [
        ("sig", 1000, "Sig cannot be longer than 1000 characters"),
        ("note_to_pharmacist", 210, "Note to pharmacist cannot be longer than 210 characters"),
    ],
)
def test_over_long_text_is_refused_when_the_effect_is_built(
    field: str, limit: int, message: str
) -> None:
    """Refused at the boundary instead, so it never reaches the chart.

    The note's limit is 210 — not the 1024 some callers assume — so this is the one most likely to
    be hit.
    """
    command = PrescribeCommand.model_validate({"note_uuid": NOTE_UUID, field: "x" * (limit + 500)})

    with pytest.raises(ValidationError) as caught:
        command.originate()

    assert message in str(caught.value)


@pytest.mark.parametrize("field", ["sig", "note_to_pharmacist"])
def test_over_long_text_is_refused_on_an_edit_too(field: str) -> None:
    """An edit carries the data as well, so the same limit applies."""
    command = PrescribeCommand.model_validate({"command_uuid": COMMAND_UUID, field: "x" * 2000})

    with pytest.raises(ValidationError):
        command.edit()


@pytest.mark.parametrize("field", ["sig", "note_to_pharmacist"])
def test_characters_surescripts_cannot_carry_are_not_touched_yet(field: str) -> None:
    """Explicit about the scope of this pass, so a reader knows it is unhandled, not overlooked.

    A smart quote or a newline still reaches the chart and still fails at REVIEW, exactly as it
    does today. What this pass guarantees is only that it does not raise here.
    """
    text = "Do not crush — don’t chew\nsecond line"

    assert getattr(PrescribeCommand.model_validate({field: text}), field) == text


def test_the_note_to_pharmacist_may_be_absent_or_empty() -> None:
    """The field is optional, and an empty note stays empty."""
    assert PrescribeCommand().note_to_pharmacist is None
    assert PrescribeCommand(note_to_pharmacist="").note_to_pharmacist == ""


def test_refill_and_adjust_prescription_inherit_the_limits() -> None:
    """The limits are declared once on PrescribeCommand; the other two Rx commands subclass it.

    Asserted because the kit this replaced had to check the same lengths in three separate parsers,
    and a fourth Rx command added later would have needed a fourth check.
    """
    for command_cls in (RefillCommand, AdjustPrescriptionCommand):
        command = command_cls(note_uuid=NOTE_UUID, note_to_pharmacist="x" * 400)

        with pytest.raises(ValidationError):
            command.originate()


def test_a_command_filled_in_from_a_models_output_reaches_the_chart() -> None:
    """The four fields a scribe assigns in sequence, with the text such a caller really produces.

    Each assignment is its own validation pass, so this is the case that would have raised four
    separate times. Every value is within its limits on purpose: the ones that are not are refused
    at the effect rather than here, which is asserted above.
    """
    sig = "Take 1 tablet by mouth twice daily — don’t crush; 250µg"
    command = PrescribeCommand(note_uuid=str(uuid4()), fdb_code="12345")

    command.sig = sig
    command.note_to_pharmacist = "Patient prefers ½ tablets. Call if unavailable…"
    command.refills = 2
    command.quantity_to_dispense = Decimal("30")

    assert command.sig == sig
    assert json.loads(command.originate().payload)["data"]["sig"] == sig


# The counts Canvas bounds on a prescription. Each is asserted at its boundary rather than at a
# comfortable value, because an off-by-one here is a real prescription.
#
# `refills` and `quantity_to_dispense` are bounded when an effect is built, not when they are set.
# The bound is the same one Canvas enforces; what moved is *when* it fires. On the field it raised
# at the assigning line, which breaks a plugin filling a command in from a model's output — the one
# that does this seeds -1 for "not extracted" in both of them. Deferring keeps the bad value off the
# chart without crashing the handler that produced it.


@pytest.mark.parametrize(
    ("field", "value"),
    [("refills", -1), ("refills", 100), ("quantity_to_dispense", 0), ("quantity_to_dispense", -1)],
)
def test_an_out_of_range_count_can_be_set_without_raising(field: str, value: int) -> None:
    """The regression this shape exists to prevent: assignment stays quiet."""
    command = PrescribeCommand()

    setattr(command, field, value)

    assert getattr(command, field) == value
    assert PrescribeCommand.model_validate({field: value})


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("refills", -1, "Refills must be between 0 and 99"),
        ("refills", 100, "Refills must be between 0 and 99"),
        ("quantity_to_dispense", 0, "Quantity to dispense must be greater than 0"),
        ("quantity_to_dispense", -1, "Quantity to dispense must be greater than 0"),
    ],
)
def test_an_out_of_range_count_is_refused_when_the_effect_is_built(
    field: str, value: int, message: str
) -> None:
    """Refused at the boundary instead, so it never reaches the chart."""
    command = PrescribeCommand.model_validate({"note_uuid": NOTE_UUID, field: value})

    with pytest.raises(ValidationError) as caught:
        command.originate()

    assert message in str(caught.value)


@pytest.mark.parametrize("field", ["refills", "quantity_to_dispense"])
def test_an_out_of_range_count_is_refused_on_an_edit_too(field: str) -> None:
    """An edit carries data as well, so the same bound applies."""
    command = PrescribeCommand.model_validate({"command_uuid": COMMAND_UUID, field: -1})

    with pytest.raises(ValidationError):
        command.edit()


def test_the_bounds_are_not_gated_by_method() -> None:
    """Every effect is checked, not just the two that carry data.

    The consequence worth knowing: an object holding an out-of-range value cannot be deleted or
    entered in error through that same object. In practice those calls need only `command_uuid`, so
    the counts are None and nothing is checked — it takes a fully populated command to hit this.
    """
    command = PrescribeCommand.model_validate({"command_uuid": COMMAND_UUID, "refills": -1})

    with pytest.raises(ValidationError):
        command.delete()

    assert PrescribeCommand(command_uuid=COMMAND_UUID).delete()


@pytest.mark.parametrize(("value", "expected"), [(0, 0), (99, 99), ("3", 3)])
def test_refills_inside_the_range_is_accepted(value: object, expected: int) -> None:
    """Both ends of the range are valid: no refills, and the maximum Surescripts allows."""
    command = PrescribeCommand.model_validate({"note_uuid": NOTE_UUID, "refills": value})

    assert command.refills == expected
    assert command.originate()


@pytest.mark.parametrize("value", [0, 30, -1])
def test_days_supply_is_not_bounded_at_all(value: int) -> None:
    """Canvas puts no bound on days supply, so neither does this — including a negative one.

    `canvas_core.commands.definitions.prescribe` declares it `fields.IntegerField(required=False)`
    with no `min_value`, and inventing a stricter rule than the chart enforces would refuse a
    prescription Canvas accepts.
    """
    command = PrescribeCommand.model_validate({"note_uuid": NOTE_UUID, "days_supply": value})

    assert command.days_supply == value
    assert command.originate()


def test_a_count_that_is_not_a_number_is_still_refused_immediately() -> None:
    """Moving the *bound* to the effect does not make the field untyped.

    A value that cannot be an integer has no bound to defer — it would reach the payload as
    nonsense — so the type error still raises where it is set.
    """
    with pytest.raises(ValidationError):
        PrescribeCommand.model_validate({"refills": "abc"})


@pytest.mark.parametrize("value", [-1, -0.5, "-1", Decimal("-2.5"), 0, Decimal("0"), 0.0])
def test_a_quantity_to_dispense_at_or_below_zero_is_refused(value: object) -> None:
    """Nothing to dispense is not a prescription.

    The bound holds across the field's whole union — Decimal, float and int alike, and the string
    a JSON body would carry, which arrives as a Decimal and compares like one.
    """
    command = PrescribeCommand.model_validate(
        {"note_uuid": NOTE_UUID, "quantity_to_dispense": value}
    )

    with pytest.raises(ValidationError) as caught:
        command.originate()

    assert "Quantity to dispense must be greater than 0" in str(caught.value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [(Decimal("2.5"), Decimal("2.5")), ("2.5", Decimal("2.5")), (2.5, 2.5), (30, 30)],
)
def test_a_quantity_to_dispense_is_read_from_whatever_carries_it(
    value: object, expected: object
) -> None:
    """A quantity arrives as a decimal, a float, an int, or the string a JSON body carries."""
    assert PrescribeCommand.model_validate(
        {"quantity_to_dispense": value}
    ).quantity_to_dispense == (expected)


@pytest.mark.parametrize("value", [Decimal("0.5"), 0.5, "0.5", Decimal("0.25")])
def test_a_fractional_quantity_to_dispense_is_accepted(value: object) -> None:
    """Half a tablet and 0.5 mL of a suspension are real quantities.

    The bound is `gt=0` and not a minimum of one for this reason, which is also what Canvas
    enforces (`canvas_core/commands/definitions/prescribe.py::dispense_quantity_validator`).
    """
    assert PrescribeCommand.model_validate({"quantity_to_dispense": value})
