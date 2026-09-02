import hashlib
import json
import uuid
from typing import Any

import pytest
from django.core.exceptions import FieldError
from django.db import models
from django.db.models import Q

from canvas_sdk.test_utils.factories import NoteFactory
from canvas_sdk.v1.data.command import Command
from canvas_sdk.v1.data.note import (
    NOTE_BODY_FIELDS,
    NOTE_BODY_READ_FIELDS,
    CurrentNoteStateEvent,
    Note,
    NoteStates,
)


def _selected_columns(queryset: models.QuerySet[Any]) -> str:
    """Return the SELECT clause of a queryset's compiled SQL."""
    return str(queryset.query).split(" FROM ")[0]


def _quoted_column(field_name: str) -> str:
    """Return a Note field's database column as it appears in compiled SQL.

    Read off the model rather than hardcoded, because the sqlite test backend
    rewrites ArrayField and drops its `db_column`.
    """
    field = Note._meta.get_field(field_name)
    assert isinstance(field, models.Field)
    return f'"{field.column}"'


def _where_clause(queryset: models.QuerySet[Any]) -> str:
    """Return the WHERE clause of a queryset's compiled SQL."""
    sql = str(queryset.query)
    assert " WHERE " in sql, "query has no WHERE clause"
    return sql.split(" WHERE ")[1]


def test_current_note_state_event_editable() -> None:
    """
    The first assertion ensures all note states are accounted for in this test.
    The second assertion specifies whether a given note state should be considered editable.
    """
    note_state_editability = {
        NoteStates.NEW: True,
        NoteStates.PUSHED: True,
        NoteStates.LOCKED: False,
        NoteStates.UNLOCKED: True,
        NoteStates.DELETED: False,
        NoteStates.RELOCKED: False,
        NoteStates.RESTORED: True,
        NoteStates.RECALLED: False,
        NoteStates.UNDELETED: True,
        NoteStates.DISCHARGED: False,
        NoteStates.SCHEDULING: False,
        NoteStates.BOOKED: False,
        NoteStates.CONVERTED: True,
        NoteStates.CANCELLED: False,
        NoteStates.NOSHOW: False,
        NoteStates.REVERTED: False,
        NoteStates.CONFIRM_IMPORT: False,
        NoteStates.SIGNED: False,
    }

    assert len(NoteStates) == len(note_state_editability), (
        "There are note states defined in NoteStates which are not included in this test! Are they editable?"
    )

    current_note_state_event = CurrentNoteStateEvent()
    for state, should_be_considered_editable in note_state_editability.items():
        current_note_state_event.state = state
        assert current_note_state_event.editable() == should_be_considered_editable


def test_body_returns_stored_body_for_legacy_notes() -> None:
    """For notes without version 2, body returns the stored _body unchanged."""
    body = [{"type": "text", "value": "hello"}]
    note = Note(_body=body)

    assert note._version is None
    assert note.body == body


def test_body_v2_empty_lines() -> None:
    """UUIDs in _body_order without a _body_content entry become empty text nodes."""
    uuid1 = uuid.uuid4()
    uuid2 = uuid.uuid4()
    note = Note(_version=2, _body_order=[uuid1, uuid2], _body_content={})

    assert note.body == [
        {"type": "text", "value": ""},
        {"type": "text", "value": ""},
    ]


def test_body_v2_text_lines() -> None:
    """Text entries in _body_content are converted to text nodes with their values."""
    uuid1 = uuid.uuid4()
    uuid2 = uuid.uuid4()
    note = Note(
        _version=2,
        _body_order=[uuid1, uuid2],
        _body_content={
            str(uuid1): {"type": "text", "value": "hello"},
            str(uuid2): {"type": "text", "value": "world"},
        },
    )

    assert note.body == [
        {"type": "text", "value": "hello"},
        {"type": "text", "value": "world"},
    ]


def test_body_v2_command_lines() -> None:
    """Command entries are converted to command nodes preserving their value."""
    line_uuid = uuid.uuid4()
    note = Note(
        _version=2,
        _body_order=[line_uuid],
        _body_content={str(line_uuid): {"type": "command", "value": "plan"}},
    )

    assert note.body == [{"type": "command", "value": "plan"}]


def test_body_v2_mixed_content_preserves_order() -> None:
    """Empty lines, commands, and text are converted maintaining _body_order."""
    empty_uuid = uuid.uuid4()
    command_uuid = uuid.uuid4()
    text_uuid = uuid.uuid4()
    note = Note(
        _version=2,
        _body_order=[empty_uuid, command_uuid, text_uuid],
        _body_content={
            str(command_uuid): {"type": "command", "value": "plan"},
            str(text_uuid): {"type": "text", "value": "some note text"},
        },
    )

    assert note.body == [
        {"type": "text", "value": ""},
        {"type": "command", "value": "plan"},
        {"type": "text", "value": "some note text"},
    ]


def test_body_v2_empty_order_returns_empty_list() -> None:
    """A version 2 note with no ordered lines produces an empty body."""
    note = Note(_version=2, _body_order=[], _body_content={})

    assert note.body == []


def test_body_checksum_returns_md5_of_body() -> None:
    """body_checksum produces an MD5 hex digest of the sorted JSON body."""
    body = [{"type": "text", "value": "hello"}]
    note = Note(_body=body)
    expected = hashlib.md5(json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()
    assert note.body_checksum() == expected


def test_body_checksum_is_stable_for_same_body() -> None:
    """The same body always produces the same checksum."""
    body = [{"type": "command", "data": {"id": 1}}]
    note = Note(_body=body)
    assert note.body_checksum() == note.body_checksum()


def test_body_checksum_differs_for_different_bodies() -> None:
    """Different body content produces different checksums."""
    note_a = Note(_body=[{"type": "text", "value": "a"}])
    note_b = Note(_body=[{"type": "text", "value": "b"}])
    assert note_a.body_checksum() != note_b.body_checksum()


def test_note_body_fields_are_concrete_note_columns() -> None:
    """Every name in NOTE_BODY_FIELDS resolves to a real column on Note.

    Guards against the constant drifting away from the model, which would make
    deferring `body` silently defer nothing or raise FieldDoesNotExist.
    """
    for field_name in NOTE_BODY_FIELDS:
        assert Note._meta.get_field(field_name).concrete


def test_defer_body_defers_every_backing_field() -> None:
    """Deferring `body` marks all the fields behind it as deferred."""
    deferred, is_defer = Note.objects.defer("body").query.deferred_loading

    assert is_defer is True
    assert deferred == set(NOTE_BODY_FIELDS)


def test_defer_body_omits_body_columns_from_the_query() -> None:
    """The body columns are absent from the SELECT that defer('body') produces."""
    body_columns = [_quoted_column(name) for name in NOTE_BODY_FIELDS]

    # An undeferred query selects all of them, which proves the assertion below
    # can fail rather than passing on an empty or malformed SELECT clause.
    default = _selected_columns(Note.objects.all())
    assert all(column in default for column in body_columns)

    selected = _selected_columns(Note.objects.defer("body"))
    assert not any(column in selected for column in body_columns)


def test_defer_body_keeps_version_loaded() -> None:
    """`body` reads _version to pick a shape, so deferring it leaves that loaded."""
    assert _quoted_column("_version") in _selected_columns(Note.objects.defer("body"))


def test_defer_passes_other_fields_through_untouched() -> None:
    """Names other than `body` are deferred exactly as given."""
    queryset = Note.objects.defer("body", "related_data", "billing_note")
    deferred, is_defer = queryset.query.deferred_loading

    assert is_defer is True
    assert deferred == {*NOTE_BODY_FIELDS, "related_data", "billing_note"}


def test_defer_without_body_is_unchanged() -> None:
    """A defer that does not name `body` defers only what it asked for."""
    deferred, is_defer = Note.objects.defer("related_data").query.deferred_loading

    assert is_defer is True
    assert deferred == {"related_data"}


def test_defer_none_still_clears_deferred_loading() -> None:
    """`defer(None)` keeps its Django meaning of resetting the deferred set."""
    control = Command.objects.defer("data").defer(None).query.deferred_loading

    assert Note.objects.defer("body").defer(None).query.deferred_loading == control


def test_only_body_loads_every_field_the_property_reads() -> None:
    """only('body') loads the exact set the property reads, and nothing less.

    An equality check rather than a subset one: omitting any of these leaves the
    property triggering a deferred fetch per note.
    """
    fields, is_defer = Note.objects.only("body").query.deferred_loading

    assert is_defer is False
    assert fields == set(NOTE_BODY_READ_FIELDS)


def test_only_body_selects_the_version_column() -> None:
    """`_version` reaches the SELECT, so building a body costs no extra query."""
    assert _quoted_column("_version") in _selected_columns(Note.objects.only("body"))


def test_only_body_omits_unrelated_columns() -> None:
    """only('body') leaves columns the property does not need out of the SELECT."""
    selected = _selected_columns(Note.objects.only("body"))

    assert _quoted_column("related_data") not in selected
    assert _quoted_column("_body") in selected


def test_filter_on_body_reads_the_column_for_each_version() -> None:
    """A `body` filter reads _body_content for v2 notes and _body for the rest."""
    where = _where_clause(Note.objects.filter(body__icontains="outreach"))

    assert _quoted_column("_version") in where
    assert _quoted_column("_body_content") in where
    assert _quoted_column("_body") in where


def test_filter_without_body_is_left_alone() -> None:
    """A filter that does not mention `body` compiles without the alias."""
    where = _where_clause(Note.objects.filter(title__icontains="x"))

    assert "CASE" not in where
    assert where == _where_clause(Note.objects.filter(title__icontains="x"))


def test_exclude_on_body_resolves() -> None:
    """`body` is available to exclude as well as filter."""
    where = _where_clause(Note.objects.exclude(body__icontains="outreach"))

    assert where.startswith("NOT")
    assert _quoted_column("_body_content") in where


def test_filter_on_body_inside_a_q_object() -> None:
    """A `body` lookup nested in a Q is found and aliased."""
    queryset = Note.objects.filter(Q(body__icontains="x") | Q(title__icontains="x"))
    where = _where_clause(queryset)

    assert _quoted_column("_body_content") in where
    assert _quoted_column("title") in where


def test_filter_on_body_inside_a_nested_negated_q() -> None:
    """Q trees are searched at any depth, including under a negation."""
    queryset = Note.objects.filter(~Q(Q(body__icontains="x") & Q(dbid__gt=1)))

    assert _quoted_column("_body_content") in _where_clause(queryset)


def test_filter_on_body_after_another_filter() -> None:
    """The alias is added when `body` appears in a later call in the chain."""
    queryset = Note.objects.filter(title="t").filter(body__icontains="x")
    where = _where_clause(queryset)

    assert _quoted_column("title") in where
    assert _quoted_column("_body_content") in where


def test_repeated_body_filters_do_not_collide() -> None:
    """Filtering on `body` more than once does not re-add a conflicting alias."""
    queryset = Note.objects.filter(body__icontains="x").filter(body__icontains="y")

    assert _where_clause(queryset).count("CASE") == 2


def test_body_can_be_filtered_while_deferred() -> None:
    """Deferring the body still allows filtering on it, since WHERE needs no select."""
    queryset = Note.objects.defer("body").filter(body__icontains="x")
    body_columns = [_quoted_column(name) for name in NOTE_BODY_FIELDS]

    assert not any(column in _selected_columns(queryset) for column in body_columns)
    assert _quoted_column("_body_content") in _where_clause(queryset)


@pytest.mark.django_db
def test_filter_on_body_matches_both_note_versions() -> None:
    """A body filter finds text in a version 2 note and a legacy note alike."""
    line_uuid = uuid.uuid4()
    NoteFactory.create(
        _version=2,
        _body_order=[str(line_uuid)],
        _body_content={str(line_uuid): {"type": "text", "value": "outreach attempted"}},
    )
    NoteFactory.create(_body=[{"type": "text", "value": "legacy prose"}])

    assert Note.objects.filter(body__icontains="outreach").count() == 1
    assert Note.objects.filter(body__icontains="legacy prose").count() == 1
    # A term in neither body matches nothing, so the two assertions above are
    # not passing on a query that happens to match every row.
    assert Note.objects.filter(body__icontains="nonexistent").count() == 0


@pytest.mark.django_db
def test_only_body_builds_bodies_without_further_queries(
    django_assert_num_queries: Any,
) -> None:
    """A note fetched with only('body') builds its body from the row it came in.

    Omitting any field the property reads turns this into a query per note.
    """
    line_uuid = uuid.uuid4()
    NoteFactory.create(
        _version=2,
        _body_order=[str(line_uuid)],
        _body_content={str(line_uuid): {"type": "text", "value": "outreach attempted"}},
    )
    NoteFactory.create(_body=[{"type": "text", "value": "legacy prose"}])

    with django_assert_num_queries(1):
        bodies = [note.body for note in Note.objects.only("body").order_by("dbid")]

    assert bodies == [
        [{"type": "text", "value": "outreach attempted"}],
        [{"type": "text", "value": "legacy prose"}],
    ]


def test_values_rejects_body_with_an_actionable_message() -> None:
    """Selecting `body` with values() is refused, pointing at only('body')."""
    with pytest.raises(FieldError) as excinfo:
        Note.objects.values("body")

    message = str(excinfo.value)
    assert "values()" in message
    assert "only('body')" in message


def test_values_list_rejects_body_with_an_actionable_message() -> None:
    """Selecting `body` with values_list() is refused, pointing at only('body')."""
    with pytest.raises(FieldError) as excinfo:
        Note.objects.values_list("body", flat=True)

    message = str(excinfo.value)
    assert "values_list()" in message
    assert "only('body')" in message


def test_values_rejects_body_alongside_real_fields() -> None:
    """`body` is caught wherever it sits in the requested field list.

    Asserts the message, not just the exception type: Django raises FieldError
    for an unresolvable name anyway, so the type alone proves nothing.
    """
    with pytest.raises(FieldError) as excinfo:
        Note.objects.values("title", "body")

    assert "only('body')" in str(excinfo.value)


def test_values_rejects_body_after_a_body_filter() -> None:
    """The refusal replaces Django's advice on an already-aliased queryset.

    Once a body filter has added the alias, Django's own error suggests
    promoting it with annotate, which returns the stored column rather than
    the body.
    """
    with pytest.raises(FieldError) as excinfo:
        Note.objects.filter(body__icontains="x").values("body")

    message = str(excinfo.value)
    assert "only('body')" in message
    assert "annotate" not in message


def test_values_passes_real_fields_through() -> None:
    """Field names other than `body` reach the query untouched."""
    assert _quoted_column("title") in _selected_columns(Note.objects.values("title"))


def test_values_list_keeps_its_flat_and_named_arguments() -> None:
    """values_list still forwards flat and named to Django."""
    flat = Note.objects.values_list("title", flat=True)
    named = Note.objects.values_list("title", named=True)

    assert _quoted_column("title") in _selected_columns(flat)
    assert flat._iterable_class.__name__ == "FlatValuesListIterable"
    assert named._iterable_class.__name__ == "NamedValuesListIterable"
