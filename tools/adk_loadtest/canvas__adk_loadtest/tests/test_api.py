import json
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest
from canvas__adk_loadtest.api.loadtest import (
    CHAT_AGENT,
    EXTENDED_AGENT,
    PLUGIN_NAME,
    PROBE_AGENT,
    LoadTestAPI,
    LoadTestChatAPI,
)
from canvas__adk_loadtest.models import Counter, ProbeRecord

from canvas_sdk.v1.data import AgentRun, AgentRunStatus


def _api(cls: type, body: Any = None, query: dict[str, str] | None = None) -> Any:
    api = cls(event=SimpleNamespace(context={"method": "POST", "path": "/"}))
    api.request = SimpleNamespace(query_params=query or {}, headers={}, json=lambda: body)
    return api


def _data(effect: Any) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(effect.payload)["data"]
    return data


def test_fanout_starts_one_run_per_key() -> None:
    """Distinct runs each serialize on their own key, numbered from start."""
    response, *effects = _api(
        LoadTestAPI, {"scenario": "s1", "count": 3, "start": 10, "script": {"text": "x"}}
    ).fanout()

    runs = [_data(effect) for effect in effects]
    assert [r["scope_id"] for r in runs] == ["loadtest:s1:10", "loadtest:s1:11", "loadtest:s1:12"]
    assert {(r["agent_id"], r["scope"]) for r in runs} == {(PROBE_AGENT, "key")}
    assert [r["trigger_payload"]["seq"] for r in runs] == [10, 11, 12]
    assert json.loads(response.content)["run_ids"] == [r["run_id"] for r in runs]


def test_fanout_shares_one_key_and_starts_the_extended_probe() -> None:
    """A shared fanout puts every run on one key, to contend for its lease."""
    _, *effects = _api(
        LoadTestAPI, {"scenario": "s4", "count": 2, "shared": True, "extended": True}
    ).fanout()

    assert {(_data(e)["agent_id"], _data(e)["scope_id"]) for e in effects} == {
        (EXTENDED_AGENT, "loadtest:s4:shared")
    }


@pytest.mark.parametrize(
    "body",
    [
        {"scenario": "s1", "count": 0},
        {"scenario": "s1", "count": 101},
        {"count": 5},
        {"scenario": "s1", "count": "five"},
        {"scenario": "s1", "count": 5, "start": "ten"},
        {"scenario": "s1", "count": 5, "start": -1},
    ],
)
def test_fanout_refuses_a_bad_request(body: dict[str, Any]) -> None:
    """A fanout is 1 to 100 runs of a named scenario."""
    (response,) = _api(LoadTestAPI, body).fanout()

    assert response.status_code == 400


@pytest.mark.django_db
def test_runs_reads_back_the_platform_and_probe_records() -> None:
    """The driver gets each run's timings and what its probe saw."""
    run_id = uuid4()
    now = datetime(2026, 11, 4, tzinfo=UTC)
    AgentRun.objects.create(
        id=run_id,
        plugin_name=PLUGIN_NAME,
        agent_id=PROBE_AGENT,
        handler_name="",
        scope="key",
        scope_key="key:loadtest:s1:0",
        status=AgentRunStatus.SUCCEEDED,
        error_kind="",
        error="",
        queued_at=now,
        started_at=now,
        finished_at=now,
        attempts=1,
        stop_reason="",
        capabilities=[],
    )
    ProbeRecord.objects.create(
        run_id=str(run_id),
        scenario="s1",
        kind="probe",
        scope_key="key:loadtest:s1:0",
        seq=0,
        saw=0,
        started_at=now,
        finished_at=now,
    )

    (response,) = _api(LoadTestAPI, {"run_ids": [str(run_id), str(uuid4())]}).runs()

    body = json.loads(response.content)
    assert [(r["run_id"], r["status"]) for r in body["runs"]] == [(str(run_id), "succeeded")]
    assert [(r["run_id"], r["saw"]) for r in body["records"]] == [(str(run_id), 0)]


@pytest.mark.django_db
def test_clear_deletes_a_scenarios_records_and_counters() -> None:
    """Clearing one scenario leaves another's alone."""
    now = datetime(2026, 11, 4, tzinfo=UTC)
    for scenario in ("s1", "s2"):
        ProbeRecord.objects.create(
            run_id=str(uuid4()),
            scenario=scenario,
            kind="probe",
            scope_key=f"key:{scenario}",
            seq=0,
            saw=0,
            started_at=now,
            finished_at=now,
        )
        Counter.objects.create(key=f"key:{scenario}", value=1)

    (response,) = _api(LoadTestAPI, {"scenario": "s1"}).clear()

    assert json.loads(response.content)["deleted"] == 1
    assert list(ProbeRecord.objects.values_list("scenario", flat=True)) == ["s2"]
    assert list(Counter.objects.values_list("key", flat=True)) == ["key:s2"]
    (counter,) = _api(LoadTestAPI, query={"key": "key:s2"}).counter()
    assert json.loads(counter.content)["value"] == 1


def test_chat_runs_on_the_staff_members_conversation_with_the_patient() -> None:
    """A chat turn is the logged-in staff member's, so it queues as interactive."""
    response, effect = _api(
        LoadTestChatAPI, {"scenario": "s2", "seq": 4, "patient_id": "p1"}
    ).chat()

    data = _data(effect)
    assert (data["agent_id"], data["scope"], data["patient_id"]) == (
        CHAT_AGENT,
        "patient_and_staff",
        "p1",
    )
    assert data["trigger_payload"]["seq"] == 4
    assert json.loads(response.content)["run_id"] == data["run_id"]


@pytest.mark.parametrize("seq", ["four", 4.5, True])
def test_chat_refuses_a_seq_that_is_not_a_whole_number(seq: Any) -> None:
    """Bad input is a 400, not a server error."""
    (response,) = _api(LoadTestChatAPI, {"scenario": "s2", "seq": seq, "patient_id": "p1"}).chat()

    assert response.status_code == 400
