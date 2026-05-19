import uuid

import pytest

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.commands import POCLabTestCommand
from canvas_sdk.commands.commands.poc_lab_test import TestValue
from canvas_sdk.test_utils.factories import (
    LabReportTemplateFactory,
    LabReportTemplateFieldFactory,
)


@pytest.fixture
def template_uuid(db: None) -> uuid.UUID:
    """Create an active POC template with one field and return its UUID."""
    template = LabReportTemplateFactory.create(name="Glucose POC", active=True, poc=True)
    LabReportTemplateFieldFactory.create(report_template=template, label="pH")
    return template.id


@pytest.fixture
def command(template_uuid: uuid.UUID) -> POCLabTestCommand:
    """A populated POCLabTestCommand wired against a real test-DB template."""
    return POCLabTestCommand(
        note_uuid="note-123",
        command_uuid="cmd-456",
        template=template_uuid,
        indications=["E11.9"],
        test_values=[TestValue(label="pH", value="6.5")],
        remarks="ok",
    )


def test_set_test_value_adds_a_new_entry() -> None:
    """`set_test_value` stores the (label, value) pair on the command."""
    cmd = POCLabTestCommand(note_uuid="n", command_uuid="c")
    cmd.set_test_value("pH", "6.5")

    assert cmd.test_values == [TestValue(label="pH", value="6.5")]


def test_set_test_value_marks_field_dirty() -> None:
    """The setter must reassign (not in-place mutate) so dirty tracking picks it up."""
    cmd = POCLabTestCommand(note_uuid="n", command_uuid="c")
    cmd.set_test_value("pH", "6.5")

    assert "test_values" in cmd._dirty_keys


def test_set_test_value_preserves_existing_entries() -> None:
    """Adding a new label keeps earlier entries intact."""
    cmd = POCLabTestCommand(
        note_uuid="n", command_uuid="c", test_values=[TestValue(label="pH", value="6.5")]
    )
    cmd.set_test_value("Glucose", "120")

    assert cmd.test_values == [
        TestValue(label="pH", value="6.5"),
        TestValue(label="Glucose", value="120"),
    ]


def test_set_test_value_overwrites_existing_label() -> None:
    """Calling with the same label replaces the prior value."""
    cmd = POCLabTestCommand(
        note_uuid="n", command_uuid="c", test_values=[TestValue(label="pH", value="6.5")]
    )
    cmd.set_test_value("pH", "7.0")

    assert cmd.test_values == [TestValue(label="pH", value="7.0")]


def test_test_value_to_dict_returns_label_value_dict() -> None:
    """`TestValue.to_dict()` returns the wire shape consumed by the home-app interpreter."""
    assert TestValue(label="pH", value="6.5").to_dict() == {"label": "pH", "value": "6.5"}


def test_template_accepts_uuid_string_via_strict_false() -> None:
    """`Field(strict=False)` on `template` overrides the model's strict=True for this field."""
    raw = "12345678-1234-5678-1234-567812345678"
    cmd = POCLabTestCommand(note_uuid="n", command_uuid="c", template=raw)  # type: ignore[arg-type]
    assert cmd.template == uuid.UUID(raw)


def test_validation_rejects_unknown_template_uuid(db: None) -> None:
    """Originate validation surfaces an error when the template UUID doesn't resolve."""
    cmd = POCLabTestCommand(
        note_uuid="n",
        command_uuid="c",
        template=uuid.uuid4(),
    )
    with pytest.raises(Exception, match="not found"):
        cmd.originate()


def test_validation_rejects_non_poc_template(template_uuid: uuid.UUID, db: None) -> None:
    """A template that isn't marked poc=True is treated as non-existent for this command."""
    sendout = LabReportTemplateFactory.create(active=True, poc=False)
    cmd = POCLabTestCommand(note_uuid="n", command_uuid="c", template=sendout.id)

    with pytest.raises(Exception, match="not found"):
        cmd.originate()


def test_validation_rejects_test_values_keys_outside_template_fields(
    template_uuid: uuid.UUID,
) -> None:
    """test_values labels must match one of the template's field labels (case-insensitive)."""
    cmd = POCLabTestCommand(
        note_uuid="n",
        command_uuid="c",
        template=template_uuid,
        test_values=[
            TestValue(label="pH", value="6.5"),
            TestValue(label="bogus_field", value="x"),
        ],
    )

    with pytest.raises(Exception, match="bogus_field"):
        cmd.originate()


def test_validation_rejects_test_values_without_template(db: None) -> None:
    """test_values without a resolved template can't be validated, so it errors."""
    cmd = POCLabTestCommand(
        note_uuid="n",
        command_uuid="c",
        test_values=[TestValue(label="pH", value="6.5")],
    )

    with pytest.raises(Exception, match="template is required"):
        cmd.originate()


def test_validation_accepts_test_values_keys_matching_template_fields(
    template_uuid: uuid.UUID,
) -> None:
    """Case-insensitive label match — `ph` matches the template's field labeled `pH`."""
    cmd = POCLabTestCommand(
        note_uuid="n",
        command_uuid="c",
        template=template_uuid,
        test_values=[TestValue(label="ph", value="6.5")],
    )

    assert cmd.originate().type == EffectType.ORIGINATE_POC_LAB_TEST_COMMAND
