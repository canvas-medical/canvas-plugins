import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.note_custom_content import NoteCustomContent


def test_effect_type() -> None:
    """Effect type must be NOTE__CUSTOM_CONTENT."""
    assert NoteCustomContent.Meta.effect_type == EffectType.NOTE__CUSTOM_CONTENT


def test_content_without_section() -> None:
    """Content alone is valid and targets the top of the note."""
    effect = NoteCustomContent(content="<p>hello</p>")
    assert effect.content == "<p>hello</p>"
    assert effect.section is None


def test_url_with_section() -> None:
    """Url plus a section is valid."""
    effect = NoteCustomContent(url="https://example.com", section=NoteCustomContent.Section.EXAM)
    assert effect.url == "https://example.com"
    assert effect.section is NoteCustomContent.Section.EXAM


def test_section_members() -> None:
    """The sections a note renders, with the values Canvas matches them on."""
    assert {section.name: section.value for section in NoteCustomContent.Section} == {
        "HISTORY": "history",
        "EXAM": "exam",
        "ASSESSMENT_PLAN": "assessment-plan",
        "INTERNAL": "internal",
    }


def test_section_must_be_an_enum_member() -> None:
    """A bare string must raise, so a typo cannot silently land content nowhere."""
    with pytest.raises(ValidationError):
        NoteCustomContent(content="<p>hello</p>", section="assessment-plan")  # type: ignore[arg-type]


def test_no_fields_raises() -> None:
    """Neither url nor content must raise."""
    with pytest.raises(ValidationError, match="must be provided"):
        NoteCustomContent()


def test_section_without_body_raises() -> None:
    """A section with no url or content must raise."""
    with pytest.raises(ValidationError, match="must be provided"):
        NoteCustomContent(section=NoteCustomContent.Section.HISTORY)


def test_url_and_content_raises() -> None:
    """Url plus content must raise."""
    with pytest.raises(ValidationError, match="mutually exclusive"):
        NoteCustomContent(url="https://example.com", content="<p>hello</p>")


def test_adding_conflicting_url_after_init_raises() -> None:
    """Setting url when content is already set must raise."""
    effect = NoteCustomContent(content="<p>hello</p>")
    with pytest.raises(ValidationError, match="mutually exclusive"):
        effect.url = "https://example.com"


def test_clearing_content_after_init_raises() -> None:
    """Clearing the only body field must raise."""
    effect = NoteCustomContent(content="<p>hello</p>")
    with pytest.raises(ValidationError, match="must be provided"):
        effect.content = None


def test_values_serialize_section_as_string() -> None:
    """Values must carry the section's string value, not the enum member."""
    effect = NoteCustomContent(content="<p>hello</p>", section=NoteCustomContent.Section.INTERNAL)
    assert effect.values == {
        "section": "internal",
        "url": None,
        "content": "<p>hello</p>",
    }


def test_values_with_no_section() -> None:
    """A top-of-note effect must report a null section."""
    effect = NoteCustomContent(url="https://example.com")
    assert effect.values == {
        "section": None,
        "url": "https://example.com",
        "content": None,
    }


def test_apply_payload() -> None:
    """Apply must wrap values under a data key."""
    effect = NoteCustomContent(content="<p>hi</p>", section=NoteCustomContent.Section.HISTORY)
    payload = json.loads(effect.apply().payload)
    assert payload == {"data": {"section": "history", "url": None, "content": "<p>hi</p>"}}
