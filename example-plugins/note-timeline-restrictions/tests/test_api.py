"""Tests for NoteRestrictionApi endpoints and NoteRestrictionDashboard."""

import json
from http import HTTPStatus
from unittest.mock import MagicMock, patch

from note_timeline_restrictions.handlers.event_handlers import (
    all_access_configs,
    get_access_config,
    set_access_config,
)

from canvas_sdk.effects import EffectType

NOTE_UUID = "aaaaaaaa-0000-0000-0000-000000000001"


# ---------------------------------------------------------------------------
# Access config helpers
# ---------------------------------------------------------------------------


@patch("note_timeline_restrictions.handlers.event_handlers.NoteTypeAccessConfig.objects")
def test_get_access_config_returns_allowed_ids(mock_objects: MagicMock) -> None:
    """Returns the allowed staff ID list when a config row exists."""
    mock_objects.filter.return_value.values_list.return_value.first.return_value = [
        "staff-1",
        "staff-2",
    ]
    result = get_access_config("note-type-uuid")
    assert result == ["staff-1", "staff-2"]


@patch("note_timeline_restrictions.handlers.event_handlers.NoteTypeAccessConfig.objects")
def test_get_access_config_returns_none_when_absent(mock_objects: MagicMock) -> None:
    """Returns None when no config row exists for the note type."""
    mock_objects.filter.return_value.values_list.return_value.first.return_value = None
    assert get_access_config("note-type-uuid") is None


@patch("note_timeline_restrictions.handlers.event_handlers.NoteTypeAccessConfig.objects")
def test_set_access_config_upserts_when_ids_provided(mock_objects: MagicMock) -> None:
    """Calls update_or_create with the provided staff IDs."""
    set_access_config("note-type-uuid", ["staff-1"])
    mock_objects.update_or_create.assert_called_once_with(
        note_type_id="note-type-uuid",
        defaults={"allowed_staff_ids": ["staff-1"]},
    )


@patch("note_timeline_restrictions.handlers.event_handlers.NoteTypeAccessConfig.objects")
def test_set_access_config_deletes_when_none(mock_objects: MagicMock) -> None:
    """Deletes the config row when allowed_staff_ids is None."""
    set_access_config("note-type-uuid", None)
    mock_objects.filter.assert_called_once_with(note_type_id="note-type-uuid")
    mock_objects.filter.return_value.delete.assert_called_once()


@patch("note_timeline_restrictions.handlers.event_handlers.NoteTypeAccessConfig.objects")
def test_all_access_configs_returns_mapping(mock_objects: MagicMock) -> None:
    """Returns a dict mapping note_type_id → allowed_staff_ids."""
    mock_objects.values.return_value = [
        {"note_type_id": "uuid-1", "allowed_staff_ids": ["staff-a"]},
        {"note_type_id": "uuid-2", "allowed_staff_ids": []},
    ]
    result = all_access_configs()
    assert result == {"uuid-1": ["staff-a"], "uuid-2": []}


@patch("note_timeline_restrictions.handlers.event_handlers.NoteTypeAccessConfig.objects")
def test_all_access_configs_returns_empty_when_no_rows(mock_objects: MagicMock) -> None:
    """Returns an empty dict when no config rows exist."""
    mock_objects.values.return_value = []
    assert all_access_configs() == {}


# ---------------------------------------------------------------------------
# NoteRestrictionDashboard
# ---------------------------------------------------------------------------


def test_dashboard_on_open_returns_page_modal() -> None:
    """on_open() renders the dashboard HTML and opens it as a full-page modal."""
    from note_timeline_restrictions.applications.application import NoteRestrictionDashboard

    from canvas_sdk.effects.launch_modal import LaunchModalEffect

    mock_event = MagicMock()

    with (
        patch(
            "note_timeline_restrictions.applications.application.render_to_string",
            return_value="<html>dashboard</html>",
        ) as mock_render,
        patch.object(LaunchModalEffect, "apply") as mock_apply,
    ):
        mock_apply.return_value = MagicMock()
        NoteRestrictionDashboard(event=mock_event).on_open()

    mock_render.assert_called_once_with("templates/note_restriction_dashboard.html")


# ---------------------------------------------------------------------------
# NoteRestrictionApi — /unrestrict
# ---------------------------------------------------------------------------


def _make_api_request(path_params: dict, headers: dict | None = None, body: str = "") -> MagicMock:
    """Build a minimal mock request object."""
    req = MagicMock()
    req.path_params = path_params
    req.headers = headers or {}
    req.body = body
    req.json.return_value = json.loads(body) if body else {}
    return req


@patch("note_timeline_restrictions.applications.api.Note.objects")
def test_unrestrict_returns_404_when_note_missing(mock_note_objects: MagicMock) -> None:
    """Returns 404 when the note UUID doesn't match any note."""
    from note_timeline_restrictions.applications.api import NoteRestrictionApi

    mock_note_objects.filter.return_value.exists.return_value = False
    api = MagicMock(spec=NoteRestrictionApi)
    api.request = _make_api_request({"note_id": NOTE_UUID})

    result = NoteRestrictionApi.unnote_restrictions(api)

    assert len(result) == 1
    assert result[0].status_code == HTTPStatus.NOT_FOUND


@patch("note_timeline_restrictions.applications.api.NoteEffect")
@patch("note_timeline_restrictions.applications.api.Note.objects")
def test_unrestrict_returns_clear_effects(
    mock_note_objects: MagicMock, mock_note_effect: MagicMock
) -> None:
    """Returns JSONResponse + metadata clear + broadcast when note exists."""
    from note_timeline_restrictions.applications.api import NoteRestrictionApi

    mock_note_objects.filter.return_value.exists.return_value = True
    mock_note_effect.return_value.upsert_metadata.return_value = MagicMock()
    api = MagicMock(spec=NoteRestrictionApi)
    api.request = _make_api_request({"note_id": NOTE_UUID})

    result = NoteRestrictionApi.unnote_restrictions(api)

    assert len(result) == 3
    assert result[0].status_code == HTTPStatus.OK
    assert result[2].type == EffectType.NOTE_RESTRICTIONS_UPDATED


# ---------------------------------------------------------------------------
# NoteRestrictionApi — /restrict
# ---------------------------------------------------------------------------


@patch("note_timeline_restrictions.applications.api.Note.objects")
def test_restrict_returns_404_when_note_missing(mock_note_objects: MagicMock) -> None:
    """Returns 404 when the note UUID doesn't exist."""
    from note_timeline_restrictions.applications.api import NoteRestrictionApi

    mock_note_objects.filter.return_value.exists.return_value = False
    api = MagicMock(spec=NoteRestrictionApi)
    api.request = _make_api_request({"note_id": NOTE_UUID})

    result = NoteRestrictionApi.note_restrictions(api)

    assert result[0].status_code == HTTPStatus.NOT_FOUND


@patch("note_timeline_restrictions.applications.api.NoteEffect")
@patch("note_timeline_restrictions.applications.api.Note.objects")
def test_restrict_returns_restriction_effects(
    mock_note_objects: MagicMock, mock_note_effect: MagicMock
) -> None:
    """Returns JSONResponse + metadata upsert + broadcast when note exists."""
    from note_timeline_restrictions.applications.api import NoteRestrictionApi

    mock_note_objects.filter.return_value.exists.return_value = True
    mock_note_effect.return_value.upsert_metadata.return_value = MagicMock()
    api = MagicMock(spec=NoteRestrictionApi)
    api.request = _make_api_request(
        {"note_id": NOTE_UUID},
        headers={"canvas-logged-in-user-id": "staff-uuid"},
    )

    result = NoteRestrictionApi.note_restrictions(api)

    assert len(result) == 3
    assert result[0].status_code == HTTPStatus.OK
    assert result[2].type == EffectType.NOTE_RESTRICTIONS_UPDATED


@patch("note_timeline_restrictions.applications.api.NoteEffect")
@patch("note_timeline_restrictions.applications.api.Note.objects")
def test_restrict_handles_empty_body(
    mock_note_objects: MagicMock, mock_note_effect: MagicMock
) -> None:
    """Applies default blur=True and default message when request body is empty."""
    from note_timeline_restrictions.applications.api import NoteRestrictionApi

    mock_note_objects.filter.return_value.exists.return_value = True
    captured: list[str] = []

    def _capture(key: str, value: str) -> MagicMock:
        captured.append(value)
        return MagicMock()

    mock_note_effect.return_value.upsert_metadata.side_effect = _capture
    api = MagicMock(spec=NoteRestrictionApi)
    api.request = _make_api_request({"note_id": NOTE_UUID})
    api.request.json.side_effect = Exception("no body")

    NoteRestrictionApi.note_restrictions(api)

    data = json.loads(captured[0])
    assert data["blur"] is True
    assert "message" in data


# ---------------------------------------------------------------------------
# NoteRestrictionApi — /states
# ---------------------------------------------------------------------------


def test_list_states_returns_all_note_states() -> None:
    """Returns a JSONResponse containing all NoteStates choices."""
    from note_timeline_restrictions.applications.api import NoteRestrictionApi

    from canvas_sdk.v1.data.note import NoteStates

    api = MagicMock(spec=NoteRestrictionApi)
    result = NoteRestrictionApi.list_states(api)

    assert len(result) == 1
    assert result[0].status_code == HTTPStatus.OK
    data = json.loads(result[0].content)
    assert "states" in data
    assert len(data["states"]) == len(NoteStates.choices)
    assert all("value" in s and "label" in s for s in data["states"])


# ---------------------------------------------------------------------------
# NoteRestrictionApi — /staff
# ---------------------------------------------------------------------------


@patch("note_timeline_restrictions.applications.api.Staff.objects")
def test_list_staff_returns_active_staff(mock_staff_objects: MagicMock) -> None:
    """Returns id and credentialed_name for each active staff member."""
    from note_timeline_restrictions.applications.api import NoteRestrictionApi

    staff_a = MagicMock()
    staff_a.id = "staff-uuid-1"
    staff_a.credentialed_name = "Dr. Alice"
    staff_b = MagicMock()
    staff_b.id = "staff-uuid-2"
    staff_b.credentialed_name = "Dr. Bob"
    mock_staff_objects.filter.return_value.order_by.return_value = [staff_a, staff_b]

    api = MagicMock(spec=NoteRestrictionApi)
    result = NoteRestrictionApi.list_staff(api)

    assert len(result) == 1
    assert result[0].status_code == HTTPStatus.OK
    data = json.loads(result[0].content)
    assert data["staff"] == [
        {"id": "staff-uuid-1", "name": "Dr. Alice"},
        {"id": "staff-uuid-2", "name": "Dr. Bob"},
    ]


@patch("note_timeline_restrictions.applications.api.Staff.objects")
def test_list_staff_returns_empty_when_none_active(mock_staff_objects: MagicMock) -> None:
    """Returns an empty list when no active staff exist."""
    from note_timeline_restrictions.applications.api import NoteRestrictionApi

    mock_staff_objects.filter.return_value.order_by.return_value = []
    api = MagicMock(spec=NoteRestrictionApi)
    result = NoteRestrictionApi.list_staff(api)

    assert json.loads(result[0].content)["staff"] == []


# ---------------------------------------------------------------------------
# NoteRestrictionApi — /note-types
# ---------------------------------------------------------------------------


@patch("note_timeline_restrictions.applications.api.NoteType.objects")
@patch("note_timeline_restrictions.applications.api.all_access_configs")
def test_list_note_types_marks_restricted_and_unrestricted(
    mock_configs: MagicMock, mock_nt_objects: MagicMock
) -> None:
    """Returns note types with restricted=True/False based on config."""
    from note_timeline_restrictions.applications.api import NoteRestrictionApi

    mock_configs.return_value = {"uuid-restricted": ["staff-1"]}
    mock_nt_objects.filter.return_value.order_by.return_value.values.return_value = [
        {"unique_identifier": "uuid-restricted", "name": "Office Visit", "category": "ENCOUNTER"},
        {"unique_identifier": "uuid-open", "name": "Progress Note", "category": "ENCOUNTER"},
    ]

    api = MagicMock(spec=NoteRestrictionApi)
    result = NoteRestrictionApi.list_note_types(api)

    data = json.loads(result[0].content)
    nt_by_id = {nt["id"]: nt for nt in data["note_types"]}
    assert nt_by_id["uuid-restricted"]["restricted"] is True
    assert nt_by_id["uuid-restricted"]["allowed_staff_ids"] == ["staff-1"]
    assert nt_by_id["uuid-open"]["restricted"] is False
    assert nt_by_id["uuid-open"]["allowed_staff_ids"] == []


# ---------------------------------------------------------------------------
# NoteRestrictionApi — /note-types/<id>/access (PUT)
# ---------------------------------------------------------------------------


@patch("note_timeline_restrictions.applications.api.set_access_config")
def test_set_note_type_access_saves_allowed_ids(mock_set: MagicMock) -> None:
    """Calls set_access_config with the provided IDs and returns success."""
    from note_timeline_restrictions.applications.api import NoteRestrictionApi

    api = MagicMock(spec=NoteRestrictionApi)
    api.request = _make_api_request(
        {"note_type_id": "uuid-1"},
        body=json.dumps({"allowed_staff_ids": ["staff-a", "staff-b"]}),
    )

    result = NoteRestrictionApi.set_note_type_access(api)

    mock_set.assert_called_once_with("uuid-1", ["staff-a", "staff-b"])
    assert result[0].status_code == HTTPStatus.OK
    data = json.loads(result[0].content)
    assert data["success"] is True
    assert data["allowed_staff_ids"] == ["staff-a", "staff-b"]


@patch("note_timeline_restrictions.applications.api.set_access_config")
def test_set_note_type_access_clears_when_null(mock_set: MagicMock) -> None:
    """Calls set_access_config with None when allowed_staff_ids is null."""
    from note_timeline_restrictions.applications.api import NoteRestrictionApi

    api = MagicMock(spec=NoteRestrictionApi)
    api.request = _make_api_request(
        {"note_type_id": "uuid-1"},
        body=json.dumps({"allowed_staff_ids": None}),
    )

    NoteRestrictionApi.set_note_type_access(api)

    mock_set.assert_called_once_with("uuid-1", None)


# ---------------------------------------------------------------------------
# NoteRestrictionApi — /notes (list with lock detection)
# ---------------------------------------------------------------------------


@patch("note_timeline_restrictions.applications.api.Note.objects")
def test_list_notes_locked_true_when_active(mock_note_objects: MagicMock) -> None:
    """Notes with active=true in metadata are shown as locked."""
    from note_timeline_restrictions.applications.api import NoteRestrictionApi

    restriction_meta = MagicMock()
    restriction_meta.key = "restriction"
    restriction_meta.value = json.dumps(
        {
            "active": True,
            "editor_staff_id": "staff-1",
            "message": "Editing.",
            "last_edited_at": "2026-01-01T12:00:00+00:00",
        }
    )

    note = MagicMock()
    note.id = NOTE_UUID
    note.patient.first_name = "Jane"
    note.patient.last_name = "Doe"
    note.patient.id = "patient-uuid"
    note.provider.credentialed_name = "Dr. Smith"
    note.note_type_version.name = "Office Visit"
    note.datetime_of_service = None
    note.current_state.state = "NEW"
    note.metadata.all.return_value = [restriction_meta]

    qs = MagicMock()
    qs.count.return_value = 1
    qs.__getitem__ = MagicMock(return_value=[note])
    mock_note_objects.select_related.return_value.prefetch_related.return_value.order_by.return_value.exclude.return_value = qs

    api = MagicMock(spec=NoteRestrictionApi)
    api.request.query_params.get.side_effect = lambda k, d="": {
        "patient_search": "",
        "state": "",
        "locked": "",
        "page": "1",
        "page_size": "25",
    }.get(k, d)

    result = NoteRestrictionApi.list_notes(api)
    data = json.loads(result[0].content)
    assert data["notes"][0]["locked"] is True
    assert data["notes"][0]["editor_staff_id"] == "staff-1"


@patch("note_timeline_restrictions.applications.api.Note.objects")
def test_list_notes_not_locked_when_no_metadata(mock_note_objects: MagicMock) -> None:
    """Notes with no restriction metadata are shown as not locked."""
    from note_timeline_restrictions.applications.api import NoteRestrictionApi

    note = MagicMock()
    note.id = NOTE_UUID
    note.patient = None
    note.provider = None
    note.note_type_version = None
    note.datetime_of_service = None
    note.current_state = None
    note.metadata.all.return_value = []

    qs = MagicMock()
    qs.count.return_value = 1
    qs.__getitem__ = MagicMock(return_value=[note])
    mock_note_objects.select_related.return_value.prefetch_related.return_value.order_by.return_value.exclude.return_value = qs

    api = MagicMock(spec=NoteRestrictionApi)
    api.request.query_params.get.side_effect = lambda k, d="": {
        "patient_search": "",
        "state": "",
        "locked": "",
        "page": "1",
        "page_size": "25",
    }.get(k, d)

    result = NoteRestrictionApi.list_notes(api)
    data = json.loads(result[0].content)
    assert data["notes"][0]["locked"] is False


@patch("note_timeline_restrictions.applications.api.Note.objects")
def test_list_notes_pagination_shape(mock_note_objects: MagicMock) -> None:
    """Response includes pagination metadata."""
    from note_timeline_restrictions.applications.api import NoteRestrictionApi

    qs = MagicMock()
    qs.count.return_value = 0
    qs.__getitem__ = MagicMock(return_value=[])
    mock_note_objects.select_related.return_value.prefetch_related.return_value.order_by.return_value.exclude.return_value = qs

    api = MagicMock(spec=NoteRestrictionApi)
    api.request.query_params.get.side_effect = lambda k, d="": {
        "patient_search": "",
        "state": "",
        "locked": "",
        "page": "1",
        "page_size": "25",
    }.get(k, d)

    result = NoteRestrictionApi.list_notes(api)
    data = json.loads(result[0].content)
    pagination = data["pagination"]
    assert "current_page" in pagination
    assert "total_pages" in pagination
    assert "total_count" in pagination
    assert pagination["total_count"] == 0
