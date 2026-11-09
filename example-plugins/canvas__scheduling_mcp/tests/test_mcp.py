import json
from datetime import date
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import pytest
from canvas__scheduling_mcp.api import mcp as mcp_module
from canvas__scheduling_mcp.api.mcp import PATIENT_SEARCHES_PER_MINUTE, SchedulingMCP
from django.core.cache import caches

from canvas_sdk.agents import Capability, ToolRegistry
from canvas_sdk.handlers.simple_api import BearerCredentials
from canvas_sdk.test_utils.factories import NoteFactory, PatientFactory, StaffFactory
from canvas_sdk.v1.data import Appointment

KEY = "test-key"
# An operator who opts the key into the patient tools.
PATIENT_TOOLS = {
    "MCP_TOOLS": "find_patient, get_patient_demographics, find_appointments, @scheduling_reads"
}


@pytest.fixture(autouse=True)
def _fresh_rate_limits(monkeypatch: pytest.MonkeyPatch) -> None:
    """Each test starts with no patient searches counted against the key.

    The sandbox marks a plugin's modules as the plugin's, which the plugin cache reads to
    find its plugin; a test imports the module directly, so it sets the mark.
    """
    monkeypatch.setitem(vars(mcp_module), "__is_plugin__", True)
    caches["plugins"].clear()


def _server(secrets: dict[str, str] | None = None) -> SchedulingMCP:
    server = SchedulingMCP(event=SimpleNamespace(context={"method": "POST", "path": "/mcp"}))
    server.secrets = {"MCP_API_KEY": KEY, **(secrets or {})}
    return server


def _send(message: dict[str, Any], secrets: dict[str, str] | None = None) -> tuple[Any, list[Any]]:
    server = _server(secrets)
    server.request = SimpleNamespace(body=json.dumps(message).encode(), headers={})
    response, *effects = server.mcp()
    body = json.loads(response.content) if response.content else None
    return (response.status_code, body), effects


def _call(
    name: str, secrets: dict[str, str] | None = None, **arguments: Any
) -> tuple[Any, list[Any]]:
    (status, body), effects = _send(
        {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        },
        secrets,
    )
    return body["result"], effects


def _credentials(token: str) -> BearerCredentials:
    return BearerCredentials(SimpleNamespace(headers={"Authorization": f"Bearer {token}"}))


def test_only_the_plugins_key_is_let_in() -> None:
    """A wrong key, or a plugin with no key set, refuses every call."""
    assert _server().authenticate(_credentials(KEY)) is True
    assert _server().authenticate(_credentials("guess")) is False
    unset = _server()
    unset.secrets = {}
    assert unset.authenticate(_credentials("anything")) is False


def test_initialize_agrees_a_protocol_version_and_offers_tools() -> None:
    """A version the server knows is echoed; an unknown one gets the newest."""
    (status, body), _ = _send(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2025-03-26"},
        }
    )
    (_, newer), _ = _send(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "initialize",
            "params": {"protocolVersion": "2099-01-01"},
        }
    )

    assert status == 200
    assert body["result"]["protocolVersion"] == "2025-03-26"
    assert body["result"]["capabilities"] == {"tools": {"listChanged": False}}
    assert newer["result"]["protocolVersion"] == "2025-06-18"


def test_a_notification_is_accepted_without_an_answer() -> None:
    """notifications/initialized has no id, so the server answers 202 with no body."""
    (status, body), _ = _send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    assert (status, body) == (202, None)


def test_the_default_tool_list_reads_the_practice_and_no_patient() -> None:
    """Patient tools and writes are offered only when the operator lists them in MCP_TOOLS."""
    (_, body), _ = _send({"jsonrpc": "2.0", "id": 3, "method": "tools/list"})
    names = {tool["name"] for tool in body["result"]["tools"]}

    assert {"find_providers", "find_appointment_slots", "find_practice_locations"} <= names
    assert not names & {
        "find_patient",
        "get_patient_demographics",
        "find_appointments",
        "book_appointment",
        "reschedule_appointment",
        "cancel_appointment",
    }


def test_patient_tools_take_a_patient_id_and_practice_tools_do_not() -> None:
    """The patient is named once, on the call, and checked by the server."""
    (_, body), _ = _send({"jsonrpc": "2.0", "id": 4, "method": "tools/list"}, PATIENT_TOOLS)
    schemas = {tool["name"]: tool["inputSchema"] for tool in body["result"]["tools"]}

    assert "patient_id" in schemas["find_appointments"]["required"]
    assert "patient_id" not in schemas["find_providers"].get("properties", {})
    assert "patient_id" not in schemas["find_patient"].get("properties", {})


@pytest.mark.django_db
def test_a_tool_runs_for_the_patient_the_call_names() -> None:
    """find_patient names the patient; a patient tool then acts on that one."""
    patient = PatientFactory.create(
        first_name="Ada", last_name="Lovelace", birth_date=date(1980, 4, 2)
    )

    found, _ = _call("find_patient", PATIENT_TOOLS, last_name="Lovelace", birth_date="1980-04-02")
    demographics, _ = _call("get_patient_demographics", PATIENT_TOOLS, patient_id=patient.id)

    assert found["isError"] is False
    assert found["structuredContent"]["match"] == {"patient_id": patient.id}
    assert demographics["isError"] is False


@pytest.mark.django_db
def test_a_practice_search_runs_without_a_patient() -> None:
    """find_providers answers a call that names no patient."""
    StaffFactory.create(first_name="Grace", last_name="Hopper", active=True)

    result, _ = _call("find_providers", name_contains="Hopper")

    assert result["isError"] is False
    assert "Grace Hopper" in result["content"][0]["text"]


def test_a_call_missing_a_required_argument_names_it() -> None:
    """A missing argument is the tool's error result, not a server error."""
    result, effects = _call("find_appointment_slots", practice_location_id="loc")

    assert result["isError"] is True
    assert "start" in result["content"][0]["text"]
    assert effects == []


@pytest.mark.django_db
def test_a_patient_tool_without_a_known_patient_is_refused() -> None:
    """A missing or unknown patient_id runs nothing."""
    missing, _ = _call("find_appointments", PATIENT_TOOLS)
    unknown, _ = _call("find_appointments", PATIENT_TOOLS, patient_id="0" * 32)

    assert missing["isError"] and unknown["isError"]
    assert "find_patient" in missing["content"][0]["text"]


def test_a_tool_outside_the_grant_is_refused() -> None:
    """A write the operator has not listed is unknown to the client."""
    (_, body), effects = _send(
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "cancel_appointment", "arguments": {"appointment_id": "a"}},
        }
    )

    assert body["error"]["code"] == -32602
    assert effects == []


@pytest.mark.django_db
def test_a_listed_write_returns_its_effect_with_the_answer() -> None:
    """An operator who lists cancel_appointment lets the key cancel, applied with the response."""
    patient = PatientFactory.create()
    note = NoteFactory.create(patient=patient)
    appointment = Appointment.objects.create(
        patient=patient,
        note=note,
        note_type=note.note_type_version,
        provider=note.provider,
        location=note.location,
        start_time="2026-11-12T09:00:00+00:00",
        duration_minutes=30,
        status="confirmed",
        telehealth_instructions_sent=False,
    )

    result, effects = _call(
        "cancel_appointment",
        {"MCP_TOOLS": "find_patient, cancel_appointment"},
        patient_id=patient.id,
        appointment_id=str(appointment.id),
    )

    assert result["isError"] is False
    (effect,) = effects
    assert json.loads(effect.payload)["data"]["instance_id"] == str(appointment.id)


def test_an_unknown_method_and_a_malformed_message_are_json_rpc_errors() -> None:
    """The client gets the JSON-RPC codes it expects."""
    (_, unknown), _ = _send({"jsonrpc": "2.0", "id": 6, "method": "resources/list"})
    server = _server()
    server.request = SimpleNamespace(body=b"{not json", headers={})
    (parse,) = server.mcp()

    assert unknown["error"]["code"] == -32601
    assert json.loads(parse.content)["error"]["code"] == -32700


@pytest.mark.parametrize(
    "params",
    [
        [1],
        "x",
        {"name": "find_providers", "arguments": [1, 2]},
        {"name": "find_providers", "arguments": "x"},
    ],
)
def test_params_and_arguments_that_are_not_objects_are_invalid(params: Any) -> None:
    """A malformed call is the client's error, never a server failure."""
    (status, body), _ = _send({"jsonrpc": "2.0", "id": 8, "method": "tools/call", "params": params})

    assert (status, body["error"]["code"]) == (200, -32602)


@pytest.mark.django_db
def test_an_unexpected_failure_is_not_described_to_the_client() -> None:
    """A database or validation error's text stays on the server."""
    with patch.object(ToolRegistry, "execute", side_effect=RuntimeError("relation api_staff")):
        result, _ = _call("find_providers")

    assert result["isError"] is True
    assert "relation" not in result["content"][0]["text"]


@pytest.mark.django_db
def test_a_tools_refusal_reaches_the_client() -> None:
    """A ValueError is the tool explaining what to pass differently, which the client needs."""
    with patch.object(ToolRegistry, "execute", side_effect=ValueError("Pass a time zone")):
        result, _ = _call("find_providers")

    assert result["content"][0]["text"].endswith("Pass a time zone")


@pytest.mark.django_db
def test_patient_search_is_granted_only_with_find_patient() -> None:
    """The operator decides a key may search patients by listing find_patient."""
    seen: list[Any] = []

    def capture(self: ToolRegistry, name: str, arguments: dict, *, ctx: dict) -> dict:
        seen.append(ctx["capabilities"])
        return {}

    with patch.object(ToolRegistry, "execute", capture):
        _call("find_providers")
        _call("find_providers", PATIENT_TOOLS)

    assert seen == [frozenset(), frozenset({Capability.PATIENT_SEARCH})]


@pytest.mark.django_db
def test_patient_searches_are_limited_per_minute() -> None:
    """Last name and birth date are guessable, so a key cannot try birth dates at speed."""
    PatientFactory.create(last_name="Lovelace", birth_date=date(1980, 4, 2))
    results = [
        _call("find_patient", PATIENT_TOOLS, last_name="Lovelace", birth_date="1980-04-02")[0]
        for _ in range(PATIENT_SEARCHES_PER_MINUTE + 1)
    ]

    assert not any(result["isError"] for result in results[:-1])
    assert results[-1]["isError"] is True
    assert "limit" in results[-1]["content"][0]["text"]
