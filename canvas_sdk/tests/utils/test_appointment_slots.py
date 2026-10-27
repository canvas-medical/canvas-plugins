"""Tests for the appointment slot search client."""

from datetime import UTC, datetime, timedelta, timezone
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import requests

from canvas_sdk.utils.appointment_slots import (
    AppointmentSlotsHttp,
    Slot,
    SlotSearchError,
    appointment_slots_http,
)

PACIFIC = timezone(timedelta(hours=-8))
START = datetime(2026, 11, 2, 9, 0, tzinfo=PACIFIC)
END = datetime(2026, 11, 2, 17, 0, tzinfo=PACIFIC)


class FakeSlotsResponse:
    """A mock requests.Response carrying a slot search result."""

    def __init__(self, status_code: int = 200, payload: Any = None) -> None:
        self.status_code = status_code
        self._payload = payload
        # A real response also carries the request, whose headers hold the pre-shared key.
        self.request = MagicMock()
        self.request.headers = {"Authorization": "the-pre-shared-key"}

    def json(self) -> Any:
        """Return the configured payload."""
        return self._payload


def search(**overrides: Any) -> list[Slot]:
    """Search with the required arguments, plus any overrides."""
    arguments: dict[str, Any] = {
        "location_id": "location-1",
        "start": START,
        "end": END,
        "duration": 30,
        **overrides,
    }
    return appointment_slots_http.search_slots(**arguments)


@patch("requests.Session.post")
def test_search_slots_returns_typed_slots(mock_post: MagicMock) -> None:
    """Each slot comes back with its provider and timezone-aware start and end."""
    mock_post.return_value = FakeSlotsResponse(
        payload={
            "slots": [
                {
                    "staff_id": "a" * 32,
                    "start": "2026-11-02T09:00:00-08:00",
                    "end": "2026-11-02T09:30:00-08:00",
                }
            ]
        }
    )

    slots = search()

    assert slots == [
        Slot(
            staff_id="a" * 32,
            start=datetime(2026, 11, 2, 9, 0, tzinfo=PACIFIC),
            end=datetime(2026, 11, 2, 9, 30, tzinfo=PACIFIC),
        )
    ]
    assert slots[0].start.utcoffset() == timedelta(hours=-8)


@patch("requests.Session.post")
def test_search_slots_sends_the_required_fields_and_defaults(mock_post: MagicMock) -> None:
    """Only the required fields and the defaults are sent when nothing else is given."""
    mock_post.return_value = FakeSlotsResponse(payload={"slots": []})

    search()

    _, kwargs = mock_post.call_args

    assert kwargs["json"] == {
        "location_id": "location-1",
        "start": "2026-11-02T09:00:00-08:00",
        "end": "2026-11-02T17:00:00-08:00",
        "duration": 30,
        "grid_minutes": 15,
        "respect_holds": True,
    }


@patch("requests.Session.post")
def test_search_slots_sends_the_optional_fields(mock_post: MagicMock) -> None:
    """Every optional field reaches the endpoint when supplied."""
    mock_post.return_value = FakeSlotsResponse(payload={"slots": []})

    search(
        staff_ids=["a" * 32, "b" * 32],
        visit_type_id="visit-type-1",
        exclude_appointment_id="appointment-1",
        grid_minutes=30,
        respect_holds=False,
    )

    _, kwargs = mock_post.call_args

    assert kwargs["json"]["staff_ids"] == ["a" * 32, "b" * 32]
    assert kwargs["json"]["visit_type_id"] == "visit-type-1"
    assert kwargs["json"]["exclude_appointment_id"] == "appointment-1"
    assert kwargs["json"]["grid_minutes"] == 30
    assert kwargs["json"]["respect_holds"] is False


@patch("requests.Session.post")
def test_search_slots_posts_to_canvas(mock_post: MagicMock) -> None:
    """The request goes to the slot search endpoint on Canvas itself."""
    mock_post.return_value = FakeSlotsResponse(payload={"slots": []})

    search()

    assert mock_post.call_args[0][0].endswith("/appointment-slots/search/")


@pytest.mark.parametrize("field", ["start", "end"])
@patch("requests.Session.post")
def test_search_slots_refuses_naive_datetimes(mock_post: MagicMock, field: str) -> None:
    """A naive datetime is refused before any request, since Canvas cannot know its zone."""
    with pytest.raises(ValueError, match=field):
        search(**{field: datetime(2026, 11, 2, 9, 0)})

    mock_post.assert_not_called()


@patch("requests.Session.post")
def test_search_slots_accepts_any_utc_offset(mock_post: MagicMock) -> None:
    """A UTC datetime is sent with its own offset."""
    mock_post.return_value = FakeSlotsResponse(payload={"slots": []})

    search(start=datetime(2026, 11, 2, 17, 0, tzinfo=UTC))

    _, kwargs = mock_post.call_args

    assert kwargs["json"]["start"] == "2026-11-02T17:00:00+00:00"


@patch("requests.Session.post")
def test_search_slots_raises_on_bad_input(mock_post: MagicMock) -> None:
    """A 400 names the bad field in the error, rather than returning no slots."""
    mock_post.return_value = FakeSlotsResponse(
        status_code=400, payload={"visit_type_id": ["No visit type has this id."]}
    )

    with pytest.raises(SlotSearchError) as excinfo:
        search(visit_type_id="nope")

    assert excinfo.value.status_code == 400
    assert "visit_type_id" in excinfo.value.message


@patch("requests.Session.post")
def test_search_slots_raises_when_calendars_are_unavailable(mock_post: MagicMock) -> None:
    """A 503 is an error, so a booking screen never shows times Canvas could not check."""
    mock_post.return_value = FakeSlotsResponse(
        status_code=503, payload={"error": "Canvas could not read the provider calendars."}
    )

    with pytest.raises(SlotSearchError) as excinfo:
        search()

    assert excinfo.value.status_code == 503


@pytest.mark.parametrize("payload", [None, [], {}, {"slots": "x"}, {"slots": [{"start": 1}]}])
@patch("requests.Session.post")
def test_search_slots_raises_on_a_malformed_body(mock_post: MagicMock, payload: Any) -> None:
    """A 200 whose body is not a list of slots is still a failure."""
    mock_post.return_value = FakeSlotsResponse(payload=payload)

    with pytest.raises(SlotSearchError, match="unexpected"):
        search()


@patch("requests.Session.post")
def test_search_slots_wraps_a_transport_failure(mock_post: MagicMock) -> None:
    """A timeout or DNS failure surfaces as the one error type this module documents."""
    mock_post.side_effect = requests.exceptions.ConnectTimeout("no route")

    with pytest.raises(SlotSearchError) as excinfo:
        search()

    assert excinfo.value.status_code == 0
    assert "Could not reach Canvas" in excinfo.value.message


@patch("requests.Session.post")
def test_search_slots_transport_failure_chains_nothing(mock_post: MagicMock) -> None:
    """The documented error is raised on its own, with no underlying error chained to it."""
    request = requests.Request("POST", "https://example.canvasmedical.com/x").prepare()
    request.headers["Authorization"] = "test-credential"
    mock_post.side_effect = requests.exceptions.ConnectTimeout("no route", request=request)

    with pytest.raises(SlotSearchError) as excinfo:
        search()

    assert excinfo.value.__cause__ is None
    assert excinfo.value.__context__ is None


def test_appointment_slots_exports_only_search_slots() -> None:
    """Plugin code can reach `search_slots` and nothing else."""
    assert AppointmentSlotsHttp.__exports__ == ("search_slots",)


def test_slot_is_immutable() -> None:
    """A slot is a value, so plugin code cannot change one in place."""
    slot = Slot(staff_id="a" * 32, start=START, end=END)

    with pytest.raises(AttributeError):
        slot.staff_id = "b" * 32  # type: ignore[misc]


@pytest.mark.parametrize(
    "public_host",
    ["https://example.canvasmedical.com", "https://example.canvasmedical.com/"],
)
@patch("requests.Session.post")
def test_appointment_slots_uses_the_instance_public_host(
    mock_post: MagicMock, public_host: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The base URL is the instance's own host, with or without a trailing slash."""
    monkeypatch.setenv("CANVAS_PUBLIC_HOST", public_host)
    mock_post.return_value = FakeSlotsResponse(payload={"slots": []})

    AppointmentSlotsHttp().search_slots(location_id="l", start=START, end=END, duration=30)

    assert (
        mock_post.call_args[0][0] == "https://example.canvasmedical.com/appointment-slots/search/"
    )
