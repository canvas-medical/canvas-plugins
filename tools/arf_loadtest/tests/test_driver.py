import json
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import pytest
from arf_loadtest import driver

T0 = datetime(2026, 11, 4, tzinfo=UTC)


class FakeInstance:
    """The plugin's API, finishing every run the moment it starts; the probe counts per key."""

    def __init__(self) -> None:
        self.runs: dict[str, dict[str, Any]] = {}
        self.records: dict[str, dict[str, Any]] = {}
        self.counters: dict[str, int] = {}
        self.fanouts: list[int] = []
        self.chat_cookies: list[str] = []
        self.gateway_calls: list[str] = []
        self.clock = 0

    def _start(self, scope_key: str, seq: int, kind: str) -> str:
        run_id = f"run-{len(self.runs)}"
        started = T0 + timedelta(seconds=self.clock)
        finished = started + timedelta(seconds=1)
        self.clock += 1
        saw = self.counters.get(scope_key, 0)
        self.counters[scope_key] = seq if kind == "chat" else saw + 1
        self.runs[run_id] = {
            "run_id": run_id,
            "agent_id": kind,
            "scope_key": scope_key,
            "status": "succeeded",
            "error_kind": "",
            "attempts": 1,
            "model_calls": 3,
            "queued_at": T0.isoformat(),
            "started_at": started.isoformat(),
            "finished_at": finished.isoformat(),
        }
        self.records[run_id] = {
            "run_id": run_id,
            "kind": kind,
            "scope_key": scope_key,
            "seq": seq,
            "saw": saw,
            "started_at": started.isoformat(),
            "finished_at": finished.isoformat(),
        }
        return run_id

    def handle(self, request: httpx.Request) -> httpx.Response:
        """Answer one request to the plugin's API or the gateway."""
        path = request.url.path
        if request.url.host == "gateway":
            self.gateway_calls.append(path)
            if path == "/stats":
                return httpx.Response(200, json={"requests": 0, "max_in_flight": 0, "faults": {}})
            return httpx.Response(200, json={})
        assert path.startswith("/plugin-io/api/canvas__arf_loadtest/")
        endpoint = path.rsplit("/", 1)[1]
        body = json.loads(request.content) if request.content else {}
        if endpoint == "fanout":
            assert request.headers["Authorization"] == "key"
            self.fanouts.append(body["count"])
            ids = [
                self._start(
                    f"key:loadtest:{body['scenario']}:"
                    + ("shared" if body["shared"] else str(body["start"] + n)),
                    body["start"] + n,
                    "probe",
                )
                for n in range(body["count"])
            ]
            return httpx.Response(202, json={"run_ids": ids})
        if endpoint == "chat":
            self.chat_cookies.append(request.headers["Cookie"])
            return httpx.Response(202, json={"run_id": self._start("chat", body["seq"], "chat")})
        if endpoint == "runs":
            assert len(body["run_ids"]) <= driver.READ_BATCH
            ids = body["run_ids"]
            return httpx.Response(
                200,
                json={
                    "runs": [self.runs[i] for i in ids],
                    "records": [self.records[i] for i in ids],
                },
            )
        if endpoint == "counter":
            return httpx.Response(
                200, json={"value": self.counters.get(request.url.params["key"], 0)}
            )
        raise AssertionError(f"unexpected {path}")


@pytest.fixture
def instance(monkeypatch: pytest.MonkeyPatch) -> FakeInstance:
    """A fake instance and gateway behind every httpx client the driver makes."""
    fake = FakeInstance()
    real_client = httpx.Client

    def client(**kwargs: Any) -> httpx.Client:
        return real_client(transport=httpx.MockTransport(fake.handle), **kwargs)

    monkeypatch.setattr(driver.httpx, "Client", client)
    monkeypatch.setattr(driver.time, "sleep", lambda seconds: None)
    return fake


ARGS = [
    "--instance",
    "https://loadtest.example",
    "--api-key",
    "key",
    "--gateway",
    "http://gateway",
    "--session-cookie",
    "sessionid=abc",
    "--patient-id",
    "p1",
    "--poll",
    "0",
]


def test_throughput_fans_out_in_batches_and_passes(
    instance: FakeInstance, capsys: pytest.CaptureFixture[str]
) -> None:
    """A fanout goes out 100 runs per request, and every run is read back."""
    assert driver.main(["throughput", "--runs", "250", *ARGS]) == 0

    assert instance.fanouts == [100, 100, 50]
    assert len(instance.runs) == 250
    out = capsys.readouterr().out
    assert "== throughput: PASS" in out
    assert "250 runs" in out
    assert instance.gateway_calls == ["/reset", "/stats"]


def test_contention_and_chat_order_check_what_the_probes_saw(
    instance: FakeInstance, capsys: pytest.CaptureFixture[str]
) -> None:
    """The lease and ordering checks read the probes' records and the key's counter."""
    assert (
        driver.main(["contention", "chat-order", "--contention-runs", "30", "--chats", "5", *ARGS])
        == 0
    )

    out = capsys.readouterr().out
    assert "[pass] runs on one key serialized: 30 runs, counter 30, 0 overlaps" in out
    assert "[pass] chat turns ran in the order sent: 5 turns, 0 out of order" in out
    assert instance.chat_cookies == ["sessionid=abc"] * 5


def test_a_run_without_a_final_status_fails_after_the_timeout(
    instance: FakeInstance, capsys: pytest.CaptureFixture[str]
) -> None:
    """A scenario whose runs never finish fails instead of waiting forever."""
    original = instance._start

    def stuck(scope_key: str, seq: int, kind: str) -> str:
        run_id = original(scope_key, seq, kind)
        instance.runs[run_id].update(status="queued", started_at=None, finished_at=None)
        return run_id

    instance._start = stuck  # type: ignore[method-assign]

    assert driver.main(["throughput", "--runs", "3", "--timeout", "0", *ARGS]) == 1
    assert "[FAIL] all runs succeeded: 0/3 succeeded" in capsys.readouterr().out


def test_chat_scenarios_need_a_session_and_patient() -> None:
    """Chat turns run as a staff member about a patient, so both are required."""
    with pytest.raises(SystemExit):
        driver.parse(["priority", "--instance", "x", "--api-key", "k"])
