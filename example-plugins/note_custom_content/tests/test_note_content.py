import json
from unittest.mock import MagicMock

from note_custom_content.handlers.note_content import BASE_URL, NoteContent
from note_custom_content.handlers.refresh import COMMAND_CHANGED_EVENTS
from note_custom_content.sections import ADDS, LABELS, SCHEMA_KEYS, channel_for, section_for

from canvas_generated.messages.effects_pb2 import EffectType

NOTE_ID = "6d3f5b0e-2c4a-4f8b-9a1d-7e0c5b2f8a31"


def _blocks() -> list[dict]:
    """The content the handler places for one note, as the wire sees it."""
    handler = NoteContent(event=MagicMock())
    handler.event.target.id = NOTE_ID

    effects = handler.compute()
    assert all(effect.type == EffectType.NOTE__CUSTOM_CONTENT for effect in effects)

    return [json.loads(effect.payload)["data"] for effect in effects]


def test_responds_to_the_note_content_event() -> None:
    """The handler subscribes to the event Canvas fires while rendering a note."""
    assert NoteContent.RESPONDS_TO == ["NOTE__GET_CUSTOM_CONTENT"]


def test_places_a_block_above_the_note_and_one_in_every_section() -> None:
    """One block belongs to the note itself; the rest name a section it renders."""
    sections = [block["section"] for block in _blocks()]

    assert sections[0] is None
    assert sections[1:] == [section.value for section in SCHEMA_KEYS]


def test_every_block_is_served_rather_than_inlined() -> None:
    """A block holds a socket open, so it has to be a page rather than inline html."""
    for block in _blocks():
        assert block["content"] is None
        assert block["url"].startswith(BASE_URL)


def test_each_block_names_the_note_it_belongs_to() -> None:
    """Without the note on the url a block cannot count anything or pick a channel."""
    assert all(f"note_id={NOTE_ID}" in block["url"] for block in _blocks())


def test_section_blocks_name_their_own_section() -> None:
    """Each section's url asks for that section, so the cards do not all render alike."""
    blocks = _blocks()[1:]

    assert all(f"section={block['section']}" in block["url"] for block in blocks)


def test_channel_is_per_note() -> None:
    """A block hears about its own note and no other."""
    assert channel_for(NOTE_ID) != channel_for("other")
    assert NOTE_ID in channel_for(NOTE_ID)


def test_every_rendered_section_is_labelled() -> None:
    """A card with no label would render a blank heading."""
    assert set(LABELS) == set(SCHEMA_KEYS)


def test_sections_gather_commands_without_overlap() -> None:
    """A command counted in two sections would make the totals disagree with the note."""
    seen: set[str] = set()

    for keys in SCHEMA_KEYS.values():
        assert not (seen & keys)
        seen |= keys


def test_every_addable_section_is_one_the_note_renders() -> None:
    """A button for a section Canvas does not render could never be clicked."""
    assert set(ADDS) <= set(SCHEMA_KEYS)


def test_a_button_adds_a_command_its_own_section_gathers() -> None:
    """A button that added a command to another section would move the count elsewhere."""
    for section, command in ADDS.items():
        assert command.Meta.key in SCHEMA_KEYS[section]


def test_section_for_reads_the_wire_value() -> None:
    """The browser sends the section back as the string the url carried."""
    for section in SCHEMA_KEYS:
        assert section_for(section.value) is section


def test_section_for_rejects_anything_else() -> None:
    """A section Canvas does not render must not resolve, so a bad request is refused."""
    assert section_for("vitals") is None
    assert section_for("") is None


def test_listens_for_every_command_change() -> None:
    """There is no single originate event, so the per-command ones are all subscribed."""
    assert len(COMMAND_CHANGED_EVENTS) > 100
    assert all("_COMMAND__" in name for name in COMMAND_CHANGED_EVENTS)
    assert "PLAN_COMMAND__POST_ORIGINATE" in COMMAND_CHANGED_EVENTS
    assert "PLAN_COMMAND__POST_DELETE" in COMMAND_CHANGED_EVENTS
    assert "PLAN_COMMAND__POST_ENTER_IN_ERROR" in COMMAND_CHANGED_EVENTS


def test_ignores_events_that_leave_the_counts_alone() -> None:
    """Committing or editing a command does not change which commands the note holds."""
    assert not any(name.endswith(("POST_COMMIT", "POST_UPDATE")) for name in COMMAND_CHANGED_EVENTS)
