"""search_note_text finds the run's patient's notes by what their free text says."""

import json
import re
import sys
from datetime import UTC, datetime
from typing import Any

import pytest

from canvas_sdk.agents import standard_tools
from canvas_sdk.agents.citations import Sources, cite
from canvas_sdk.test_utils.factories import NoteFactory, PatientFactory
from canvas_sdk.v1.data.note import Note

# `canvas_sdk.agents.standard_tools` names the registry, so reach the module itself here.
STANDARD_TOOLS_MODULE = sys.modules["canvas_sdk.agents.standard_tools"]


def _ctx(patient_id: object) -> dict[str, object]:
    return {"patient_id": patient_id, "effects": []}


def _note(patient: object, day: int, *texts: str) -> Note:
    """A version 1 note on ``day`` of January 2026 whose body holds ``texts`` as text blocks."""
    return NoteFactory.create(
        patient=patient,
        datetime_of_service=datetime(2026, 1, day, tzinfo=UTC),
        _body=[{"type": "text", "value": text} for text in texts],
    )


def _search(patient: Any, **arguments: object) -> list[dict[str, Any]]:
    return standard_tools.execute("search_note_text", arguments, ctx=_ctx(patient.id))


@pytest.mark.django_db
def test_returns_notes_mentioning_the_words_newest_first_with_a_snippet() -> None:
    """Matching notes come back newest first; a note that does not mention the words is left out."""
    patient = PatientFactory.create()
    older = _note(patient, 3, "Patient reports chest pain on exertion.")
    newer = _note(patient, 20, "Follow-up.", "Chest pain resolved since last visit.")
    _note(patient, 25, "Knee pain, no other complaints.")

    rows = _search(patient, text="chest pain")

    assert [row["id"] for row in rows] == [str(newer.id), str(older.id)]
    assert rows[0]["snippet"] == "Follow-up. Chest pain resolved since last visit."
    assert rows[0]["dbid"] == newer.dbid
    json.dumps(rows)


@pytest.mark.django_db
def test_every_word_must_appear_in_any_order() -> None:
    """A note matches only when it holds every word, whatever their order and case."""
    patient = PatientFactory.create()
    both = _note(patient, 5, "Pain in the chest, left side.")
    _note(patient, 6, "Chest x-ray ordered.")

    rows = _search(patient, text="CHEST pain")

    assert [row["id"] for row in rows] == [str(both.id)]
    assert "chest" in rows[0]["snippet"].lower()


@pytest.mark.django_db
def test_another_patients_notes_are_absent() -> None:
    """With the same words on two charts, only the run's patient's note comes back."""
    patient, other = PatientFactory.create(), PatientFactory.create()
    own = _note(patient, 1, "Discussed sleep apnea.")
    _note(other, 2, "Discussed sleep apnea.")

    assert [row["id"] for row in _search(patient, text="sleep apnea")] == [str(own.id)]


@pytest.mark.django_db
def test_words_in_the_stored_body_structure_do_not_match() -> None:
    """A body stored as JSON holds "type" and "value" in every note; only typed text counts."""
    patient = PatientFactory.create()
    _note(patient, 1, "Blood pressure stable.")

    assert _search(patient, text="value") == []
    assert _search(patient, text="type") == []


@pytest.mark.django_db
def test_a_word_found_only_in_the_body_structure_does_not_complete_a_match() -> None:
    """The database matches "type" in every body; the typed text must hold every word itself."""
    patient = PatientFactory.create()
    _note(patient, 1, "Chest pain on exertion.")

    assert _search(patient, text="pain type") == []


@pytest.mark.django_db
@pytest.mark.parametrize("text", ['"chest pain"', "'chest pain'", "chest pain?", "(chest, pain)"])
def test_punctuation_around_the_words_is_ignored(text: str) -> None:
    """The model often quotes a phrase; quotes and trailing punctuation are not part of a word."""
    patient = PatientFactory.create()
    note = _note(patient, 1, "Chest pain resolved.")

    assert [row["id"] for row in _search(patient, text=text)] == [str(note.id)]


@pytest.mark.django_db
def test_the_snippet_centers_on_the_phrase_rather_than_its_first_word() -> None:
    """A note that says "chest" early and "chest pain" late shows the "chest pain" passage."""
    patient = PatientFactory.create()
    filler = "Unremarkable review of systems. " * 10
    _note(patient, 1, f"Chest x-ray clear. {filler}Today reports chest pain at rest.")

    snippet = _search(patient, text="chest pain")[0]["snippet"]

    assert "reports chest pain at rest" in snippet
    assert "Chest x-ray clear" not in snippet


@pytest.mark.django_db
def test_the_database_narrows_candidates_before_the_cap(monkeypatch: pytest.MonkeyPatch) -> None:
    """Newer notes without the word never use up the candidates the text check reads."""
    monkeypatch.setattr(STANDARD_TOOLS_MODULE, "SEARCH_NOTE_TEXT_MAX_CANDIDATES", 2)
    patient = PatientFactory.create()
    older = _note(patient, 1, "Headache since Monday.")
    for day in (10, 11, 12):
        _note(patient, day, "Knee exam unchanged.")

    assert [row["id"] for row in _search(patient, text="headache")] == [str(older.id)]


@pytest.mark.django_db
def test_limit_caps_the_rows() -> None:
    """``limit`` keeps the newest matching notes."""
    patient = PatientFactory.create()
    for day in range(1, 6):
        _note(patient, day, f"Headache, day {day}.")

    rows = _search(patient, text="headache", limit=2)

    assert [row["snippet"] for row in rows] == ["Headache, day 5.", "Headache, day 4."]


@pytest.mark.django_db
def test_a_long_note_gets_a_snippet_around_the_match() -> None:
    """A long note is cut to the text around the match, marked with ellipses."""
    patient = PatientFactory.create()
    text = f"{'Routine history. ' * 20}Noted a new heart murmur today. {'Plan unchanged. ' * 20}"
    _note(patient, 1, text)

    snippet = _search(patient, text="heart murmur")[0]["snippet"]

    assert snippet.startswith("…") and snippet.endswith("…")
    assert "Noted a new heart murmur today." in snippet
    assert len(snippet) < len(text) / 2


def test_text_with_no_words_is_refused() -> None:
    """Blank text is an error the model sees, not a search that matches every note."""
    with pytest.raises(ValueError, match="at least one word"):
        standard_tools.execute("search_note_text", {"text": "   "}, ctx=_ctx("p1"))


def test_a_run_without_a_patient_is_refused() -> None:
    """A patient-less run gets an error, never an empty chart read as no notes."""
    with pytest.raises(ValueError, match="not about a patient"):
        standard_tools.execute("search_note_text", {"text": "pain"}, ctx=_ctx(None))


@pytest.mark.django_db
def test_returns_description_names_exactly_the_fields_it_returns() -> None:
    """The model plans on the described fields, so the description must match the rows."""
    patient = PatientFactory.create()
    _note(patient, 1, "Shortness of breath.")
    returned = set(_search(patient, text="breath")[0])
    described = set(
        re.findall(
            r"`([a-z_]+)`", standard_tools.metadata_for("search_note_text")["returns_description"]
        )
    )

    assert described == returned


@pytest.mark.django_db
def test_a_reply_can_cite_a_found_note() -> None:
    """The rows are citable as notes, so a chat can open the note it cites."""
    patient = PatientFactory.create()
    note = _note(patient, 1, "Wheezing on exam.")
    rows = _search(patient, text="wheezing")
    messages = [
        {
            "role": "assistant",
            "content": [{"type": "tool_use", "id": "t1", "name": "search_note_text"}],
        },
        {
            "role": "user",
            "content": [{"type": "tool_result", "tool_use_id": "t1", "content": json.dumps(rows)}],
        },
    ]

    text, citations = cite(
        f"Wheezing was noted [[cite:{note.id}]].", Sources(standard_tools).add_all(messages)
    )

    assert text == "Wheezing was noted [1]."
    assert [(c.kind, c.note_dbid) for c in citations] == [("Note", note.dbid)]
