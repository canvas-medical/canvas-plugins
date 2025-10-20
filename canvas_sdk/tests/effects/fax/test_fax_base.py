from collections.abc import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from pydantic_core import ValidationError

from canvas_sdk.effects.fax import FaxNoteEffect


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock], None, None]:
    """Mock PracticeLocation and Note database queries."""
    with (
        patch("canvas_sdk.v1.data.PracticeLocation.objects") as mock_pl,
        patch("canvas_sdk.v1.data.Note.objects") as mock_note,
    ):
        mock_pl.filter.return_value.exists.return_value = True
        mock_note.filter.return_value.exists.return_value = True
        yield {
            "practice_location": mock_pl,
            "note": mock_note,
        }


def test_fax_effect_apply_success_without_coversheet(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test successful fax effect apply without coversheet."""
    fax = FaxNoteEffect(
        recipient_name="Dr. John Doe",
        recipient_fax_number="555-123-4567",
        note_id=str(uuid4()),
        include_coversheet=False,
    )

    effect = fax.apply()
    assert effect is not None


def test_fax_effect_apply_success_with_coversheet(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test successful fax effect apply with coversheet and all required fields."""
    location_id = str(uuid4())
    note_id = str(uuid4())

    fax = FaxNoteEffect(
        recipient_name="Dr. John Doe",
        recipient_fax_number="555-123-4567",
        note_id=note_id,
        include_coversheet=True,
        subject="Patient Records",
        comment="Enclosed please find patient records",
        location_id=location_id,
    )

    effect = fax.apply()
    assert effect is not None


def test_fax_effect_missing_subject_with_coversheet(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that missing subject raises error when include_coversheet is True."""
    fax = FaxNoteEffect(
        recipient_name="Dr. John Doe",
        recipient_fax_number="555-123-4567",
        note_id=str(uuid4()),
        include_coversheet=True,
        comment="Test comment",
        location_id=str(uuid4()),
    )

    with pytest.raises(ValidationError) as exc_info:
        fax.apply()

    errors = exc_info.value.errors()
    assert any("subject is required when include_coversheet is True" in str(e) for e in errors)


def test_fax_effect_missing_comment_with_coversheet(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that missing comment raises error when include_coversheet is True."""
    fax = FaxNoteEffect(
        recipient_name="Dr. John Doe",
        recipient_fax_number="555-123-4567",
        note_id=str(uuid4()),
        include_coversheet=True,
        subject="Patient Records",
        location_id=str(uuid4()),
    )

    with pytest.raises(ValidationError) as exc_info:
        fax.apply()

    errors = exc_info.value.errors()
    assert any("comment is required when include_coversheet is True" in str(e) for e in errors)


def test_fax_effect_missing_location_id_with_coversheet(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that missing location_id raises error when include_coversheet is True."""
    fax = FaxNoteEffect(
        recipient_name="Dr. John Doe",
        recipient_fax_number="555-123-4567",
        note_id=str(uuid4()),
        include_coversheet=True,
        subject="Patient Records",
        comment="Test comment",
    )

    with pytest.raises(ValidationError) as exc_info:
        fax.apply()

    errors = exc_info.value.errors()
    assert any("location_id is required when include_coversheet is True" in str(e) for e in errors)


def test_fax_effect_nonexistent_location_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that nonexistent location_id raises error."""
    mock_db_queries["practice_location"].filter.return_value.exists.return_value = False
    location_id = str(uuid4())

    fax = FaxNoteEffect(
        recipient_name="Dr. John Doe",
        recipient_fax_number="555-123-4567",
        note_id=str(uuid4()),
        include_coversheet=True,
        subject="Patient Records",
        comment="Test comment",
        location_id=location_id,
    )

    with pytest.raises(ValidationError) as exc_info:
        fax.apply()

    errors = exc_info.value.errors()
    assert any(f"Practice Location {location_id} does not exist" in str(e) for e in errors)


def test_fax_effect_multiple_errors_with_coversheet(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that multiple validation errors are collected when coversheet is enabled."""
    fax = FaxNoteEffect(
        recipient_name="Dr. John Doe",
        recipient_fax_number="555-123-4567",
        note_id=str(uuid4()),
        include_coversheet=True,
        # Missing subject, comment, and location_id
    )

    with pytest.raises(ValidationError) as exc_info:
        fax.apply()

    errors = exc_info.value.errors()
    error_messages = [str(e) for e in errors]

    # Should have 3 errors
    assert len(errors) == 3
    assert any(
        "subject is required when include_coversheet is True" in msg for msg in error_messages
    )
    assert any(
        "comment is required when include_coversheet is True" in msg for msg in error_messages
    )
    assert any(
        "location_id is required when include_coversheet is True" in msg for msg in error_messages
    )


def test_fax_effect_empty_subject_with_coversheet(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that empty string subject is treated as missing."""
    fax = FaxNoteEffect(
        recipient_name="Dr. John Doe",
        recipient_fax_number="555-123-4567",
        note_id=str(uuid4()),
        include_coversheet=True,
        subject="",
        comment="Test comment",
        location_id=str(uuid4()),
    )

    with pytest.raises(ValidationError) as exc_info:
        fax.apply()

    errors = exc_info.value.errors()
    assert any("subject is required when include_coversheet is True" in str(e) for e in errors)


def test_fax_effect_empty_comment_with_coversheet(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that empty string comment is treated as missing."""
    fax = FaxNoteEffect(
        recipient_name="Dr. John Doe",
        recipient_fax_number="555-123-4567",
        note_id=str(uuid4()),
        include_coversheet=True,
        subject="Patient Records",
        comment="",
        location_id=str(uuid4()),
    )

    with pytest.raises(ValidationError) as exc_info:
        fax.apply()

    errors = exc_info.value.errors()
    assert any("comment is required when include_coversheet is True" in str(e) for e in errors)


def test_fax_effect_none_subject_with_coversheet(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that None subject raises error when coversheet is enabled."""
    fax = FaxNoteEffect(
        recipient_name="Dr. John Doe",
        recipient_fax_number="555-123-4567",
        note_id=str(uuid4()),
        include_coversheet=True,
        subject=None,
        comment="Test comment",
        location_id=str(uuid4()),
    )

    with pytest.raises(ValidationError) as exc_info:
        fax.apply()

    errors = exc_info.value.errors()
    assert any("subject is required when include_coversheet is True" in str(e) for e in errors)


def test_fax_effect_none_comment_with_coversheet(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that None comment raises error when coversheet is enabled."""
    fax = FaxNoteEffect(
        recipient_name="Dr. John Doe",
        recipient_fax_number="555-123-4567",
        note_id=str(uuid4()),
        include_coversheet=True,
        subject="Patient Records",
        comment=None,
        location_id=str(uuid4()),
    )

    with pytest.raises(ValidationError) as exc_info:
        fax.apply()

    errors = exc_info.value.errors()
    assert any("comment is required when include_coversheet is True" in str(e) for e in errors)


def test_fax_effect_nonexistent_note_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that nonexistent note_id raises error."""
    mock_db_queries["note"].filter.return_value.exists.return_value = False
    note_id = str(uuid4())

    fax = FaxNoteEffect(
        recipient_name="Dr. John Doe",
        recipient_fax_number="555-123-4567",
        note_id=note_id,
        include_coversheet=False,
    )

    with pytest.raises(ValidationError) as exc_info:
        fax.apply()

    errors = exc_info.value.errors()
    assert any(f"Note with ID {note_id} does not exist" in str(e) for e in errors)
