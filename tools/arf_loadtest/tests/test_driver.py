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
        self.cleared: list[str] = []
        # Model calls the gateway served since its last reset, and each run's share.
        self.served = 0
        self.calls_per_run = 3
        self.clock = 0

    def _start(self, scope_key: str, seq: int, kind: str) -> str:
        run_id = f"run-{len(self.runs)}"
        started = T0 + timedelta(seconds=self.clock)
        finished = started + timedelta(seconds=1)
        self.clock += 1
        self.served += self.calls_per_run
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
                return httpx.Response(
                    200, json={"requests": self.served, "max_in_flight": 0, "faults": {}}
                )
            if path == "/reset":
                self.served = 0
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
        if endpoint == "clear":
            self.cleared.append(body["scenario"])
            return httpx.Response(200, json={"deleted": 0})
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


@pytest.fixture(autouse=True)
def secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    """The plugin's API key and a staff session, from the environment."""
    monkeypatch.setenv(driver.API_KEY_ENV, "key")
    monkeypatch.setenv(driver.SESSION_COOKIE_ENV, "sessionid=abc")


ARGS = [
    "--instance",
    "https://loadtest.example",
    "--allow-remote-instance",
    "--gateway",
    "http://gateway",
    "--patient-id",
    "p1",
    "--poll",
    "0",
]


def test_throughput_fans_out_in_batches_and_passes(
    instance: FakeInstance, capsys: pytest.CaptureFixture[str]
) -> None:
    """After the one-run canary, a fanout goes out 100 runs per request, and every run is read back."""
    assert driver.main(["throughput", "--runs", "250", *ARGS]) == 0

    assert instance.fanouts == [1, 100, 100, 50]
    assert len(instance.runs) == 251
    out = capsys.readouterr().out
    assert "== throughput: PASS" in out
    assert "250 runs" in out
    assert instance.gateway_calls == ["/reset", "/stats", "/reset", "/stats"]
    assert [scenario.split("-")[0] for scenario in instance.cleared] == ["canary", "throughput"]


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
        if ":throughput-" in scope_key:
            instance.runs[run_id].update(status="queued", started_at=None, finished_at=None)
        return run_id

    instance._start = stuck  # type: ignore[method-assign]

    assert driver.main(["throughput", "--runs", "3", "--timeout", "0", *ARGS]) == 1
    assert "[FAIL] all runs succeeded: 0/3 succeeded" in capsys.readouterr().out


def test_chat_scenarios_need_a_session_and_patient(monkeypatch: pytest.MonkeyPatch) -> None:
    """Chat turns run as a staff member about a patient, so both are required."""
    monkeypatch.delenv(driver.SESSION_COOKIE_ENV)
    with pytest.raises(SystemExit):
        driver.parse(["priority", "--instance", "http://localhost:8000", "--patient-id", "p1"])


@pytest.mark.parametrize(
    "instance_url", ["https://customer.canvasmedical.com", "http://10.0.0.5:8000"]
)
def test_an_instance_other_than_localhost_needs_the_flag(instance_url: str) -> None:
    """A mistyped URL cannot put a thousand runs on an instance someone works in."""
    with pytest.raises(SystemExit):
        driver.parse(["throughput", "--instance", instance_url])

    assert driver.parse(["throughput", "--instance", instance_url, "--allow-remote-instance"])


def test_the_api_key_comes_from_the_environment_never_the_command_line(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A command line shows up in process lists and shell history."""
    with pytest.raises(SystemExit):
        driver.parse(["throughput", "--instance", "http://localhost:8000", "--api-key", "k"])
    monkeypatch.delenv(driver.API_KEY_ENV)
    with pytest.raises(SystemExit):
        driver.parse(["throughput", "--instance", "http://localhost:8000"])


def test_the_canary_stops_the_driver_when_another_gateway_served_it(
    instance: FakeInstance, capsys: pytest.CaptureFixture[str]
) -> None:
    """An instance pointed at a real gateway gets one run, not a scenario's thousand."""
    instance.calls_per_run = 0

    assert driver.main(["throughput", "--runs", "250", *ARGS]) == 2

    assert len(instance.runs) == 1
    assert "points at another gateway" in capsys.readouterr().err


def test_faults_fails_when_no_run_succeeded(
    instance: FakeInstance, capsys: pytest.CaptureFixture[str]
) -> None:
    """Every run reaching a final status is no pass when every one of them failed."""
    original = instance._start

    def failing(scope_key: str, seq: int, kind: str) -> str:
        run_id = original(scope_key, seq, kind)
        if ":faults-" in scope_key:
            instance.runs[run_id]["status"] = "failed"
        return run_id

    instance._start = failing  # type: ignore[method-assign]

    assert driver.main(["faults", "--fault-runs", "4", *ARGS]) == 1
    out = capsys.readouterr().out
    assert "[pass] every run reached a final status" in out
    assert "[FAIL] runs succeeded through the faults: 0/4 succeeded" in out
