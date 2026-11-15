"""Drive load test scenarios against an instance running the canvas__adk_loadtest plugin.

Each scenario starts probe runs through the plugin's API, waits for every run to reach
a final status, reads back the platform's run records and what each probe saw, and
reports timings and pass/fail checks. The plugin's ``INFERENCE_GATEWAY_URL`` points
at the fake gateway (``adk_loadtest.gateway``), which the driver also controls.

Scenarios:

- ``throughput``: ``--runs`` batch runs, each on its own key.
- ``priority``: the same batch backlog, with a chat turn sent every ``--chat-every``
  seconds; chat turns queue as interactive and should wait less.
- ``chat-order``: ``--chats`` turns of one conversation sent at once; each turn should
  see the one before it.
- ``contention``: ``--contention-runs`` batch runs on one shared key; the lease should
  run them one at a time with no lost update.
- ``extended``: ``--extended-runs`` extended runs, which the plugin runner admits only
  ``--max-extended`` at a time.
- ``faults``: ``--fault-runs`` batch runs with the gateway failing a share of calls.

Before the scenarios, one canary run has to succeed through the fake gateway, so an
instance pointed at a real gateway stops the driver before it starts any load. The
plugin's API key and a staff session's Cookie header come from the environment
(``ADK_LOADTEST_API_KEY``, ``ADK_LOADTEST_SESSION_COOKIE``), and an instance other than
localhost needs ``--allow-remote-instance``.
"""

import argparse
import json
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from typing import Any
from urllib.parse import urlsplit

import httpx

from adk_loadtest.analysis import (
    TERMINAL,
    Check,
    Summary,
    check_all_succeeded,
    check_capped,
    check_chat_order,
    check_prioritized,
    check_serialized,
    summarize,
)

PLUGIN = "canvas__adk_loadtest"
# The plugin starts at most this many runs per fanout request, and reads back at most
# READ_BATCH per /runs request.
FANOUT_BATCH = 100
READ_BATCH = 1000
API_KEY_ENV = "ADK_LOADTEST_API_KEY"
SESSION_COOKIE_ENV = "ADK_LOADTEST_SESSION_COOKIE"
LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})


@dataclass
class Settings:
    """What the command line chose."""

    instance: str
    api_key: str
    gateway: str
    session_cookie: str
    patient_id: str
    runs: int
    chats: int
    chat_every: float
    contention_runs: int
    extended_runs: int
    max_extended: int
    fault_runs: int
    latency_ms: int
    tools: int
    timeout: float
    poll: float
    tag: str


@dataclass
class Result:
    """One scenario's outcome."""

    scenario: str
    groups: dict[str, Summary]
    checks: list[Check]
    gateway: dict[str, Any] = field(default_factory=dict)
    seconds: float = 0.0

    @property
    def passed(self) -> bool:
        """Whether every check passed."""
        return all(check.passed for check in self.checks)


class Driver:
    """Talks to the plugin's API and the fake gateway."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        base = f"{settings.instance.rstrip('/')}/plugin-io/api/{PLUGIN}"
        self.api = httpx.Client(
            base_url=base, headers={"Authorization": settings.api_key}, timeout=60
        )
        self.chat_api = httpx.Client(
            base_url=base, headers={"Cookie": settings.session_cookie}, timeout=60
        )
        self.gateway = httpx.Client(base_url=settings.gateway.rstrip("/"), timeout=10)

    def script(self, **overrides: Any) -> dict[str, Any]:
        """The fake gateway's script for a probe run: ``--tools`` config reads, then done."""
        return {
            "tools": [["find_note_types", {}]] * self.settings.tools,
            "latency_ms": self.settings.latency_ms,
            "text": "done",
            **overrides,
        }

    def scenario(self, name: str) -> str:
        """The scenario name the plugin records, unique to this driver invocation."""
        return f"{name}-{self.settings.tag}"

    def fanout(
        self, scenario: str, total: int, *, shared: bool = False, extended: bool = False
    ) -> list[str]:
        """Start ``total`` batch runs, ``FANOUT_BATCH`` per request; their run ids."""
        run_ids: list[str] = []
        for start in range(0, total, FANOUT_BATCH):
            response = self.api.post(
                "/fanout",
                json={
                    "scenario": scenario,
                    "count": min(FANOUT_BATCH, total - start),
                    "start": start,
                    "shared": shared,
                    "extended": extended,
                    "script": self.script(),
                },
            )
            response.raise_for_status()
            run_ids += response.json()["run_ids"]
        return run_ids

    def chat(self, scenario: str, seq: int) -> str:
        """Send chat turn ``seq`` as the session's staff member; its run id."""
        response = self.chat_api.post(
            "/chat",
            json={
                "scenario": scenario,
                "seq": seq,
                "patient_id": self.settings.patient_id,
                "script": self.script(),
            },
        )
        response.raise_for_status()
        run_id: str = response.json()["run_id"]
        return run_id

    def read(self, run_ids: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """The platform's records and the probes' records of ``run_ids``."""
        runs: list[dict[str, Any]] = []
        records: list[dict[str, Any]] = []
        for start in range(0, len(run_ids), READ_BATCH):
            response = self.api.post("/runs", json={"run_ids": run_ids[start : start + READ_BATCH]})
            response.raise_for_status()
            body = response.json()
            runs += body["runs"]
            records += body["records"]
        return runs, records

    def wait(self, run_ids: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Poll until every run is final or ``--timeout`` passes; the last read."""
        deadline = time.monotonic() + self.settings.timeout
        while True:
            runs, records = self.read(run_ids)
            done = sum(1 for run in runs if run["status"] in TERMINAL)
            print(f"  {done}/{len(run_ids)} final", file=sys.stderr)
            if done == len(run_ids) or time.monotonic() > deadline:
                return runs, records
            time.sleep(self.settings.poll)

    def counter(self, key: str) -> int:
        """A scope key's counter."""
        response = self.api.get("/counter", params={"key": key})
        response.raise_for_status()
        value: int = response.json()["value"]
        return value

    def clear(self, scenario: str) -> None:
        """Delete a scenario's probe records and counters; its AgentRun rows stay."""
        self.api.post("/clear", json={"scenario": scenario}).raise_for_status()

    def control(self, **settings: Any) -> None:
        """Set the fake gateway's latency or fault rates."""
        self.gateway.post("/control", json=settings).raise_for_status()

    def reset_gateway(self) -> None:
        """Zero the fake gateway's stats and restore its defaults."""
        self.gateway.post("/reset").raise_for_status()

    def gateway_stats(self) -> dict[str, Any]:
        """What the fake gateway served."""
        response = self.gateway.get("/stats")
        response.raise_for_status()
        stats: dict[str, Any] = response.json()
        return stats


def canary(driver: Driver) -> str | None:
    """Run one probe and confirm this fake gateway served its model calls; why not, or None."""
    driver.reset_gateway()
    scenario = driver.scenario("canary")
    run_ids = driver.fanout(scenario, 1)
    runs, _ = driver.wait(run_ids)
    served = driver.gateway_stats()["requests"]
    driver.clear(scenario)
    status = runs[0]["status"] if runs else "unrecorded"
    if status != "succeeded":
        return f"the canary run ended {status}"
    if not served:
        return (
            "the canary run succeeded without a call to this fake gateway, so the "
            "plugin's INFERENCE_GATEWAY_URL points at another gateway"
        )
    return None


def throughput(driver: Driver) -> Result:
    """Many batch runs on distinct keys: how fast the runner drains them, and how wide."""
    total = driver.settings.runs
    run_ids = driver.fanout(driver.scenario("throughput"), total)
    runs, _ = driver.wait(run_ids)
    batch = summarize(runs)
    return Result("throughput", {"batch": batch}, [check_all_succeeded(runs, total)])


def priority(driver: Driver) -> Result:
    """Chat turns sent into a batch backlog should jump it."""
    settings = driver.settings
    scenario = driver.scenario("priority")
    batch_ids = driver.fanout(scenario, settings.runs)
    chat_ids: list[str] = []
    for seq in range(1, settings.chats + 1):
        chat_ids.append(driver.chat(scenario, seq))
        time.sleep(settings.chat_every)
    runs, _ = driver.wait(batch_ids + chat_ids)
    chat_set = set(chat_ids)
    batch_runs = [run for run in runs if run["run_id"] not in chat_set]
    chat_runs = [run for run in runs if run["run_id"] in chat_set]
    batch, chat = summarize(batch_runs), summarize(chat_runs)
    return Result(
        "priority",
        {"batch": batch, "chat": chat},
        [
            check_all_succeeded(runs, len(batch_ids) + len(chat_ids)),
            check_prioritized(chat, batch),
        ],
    )


def chat_order(driver: Driver) -> Result:
    """One conversation's turns, sent at once, run in the order sent."""
    scenario = driver.scenario("chat-order")
    chat_ids = [driver.chat(scenario, seq) for seq in range(1, driver.settings.chats + 1)]
    runs, records = driver.wait(chat_ids)
    return Result(
        "chat-order",
        {"chat": summarize(runs)},
        [
            check_all_succeeded(runs, len(chat_ids)),
            check_chat_order(records, len(chat_ids)),
            check_capped(summarize(runs), 1, "turns of one conversation"),
        ],
    )


def contention(driver: Driver) -> Result:
    """Many runs on one key take its lease one at a time and lose no update."""
    total = driver.settings.contention_runs
    run_ids = driver.fanout(driver.scenario("contention"), total, shared=True)
    runs, records = driver.wait(run_ids)
    scope_keys = {run["scope_key"] for run in runs}
    counter = driver.counter(next(iter(scope_keys))) if len(scope_keys) == 1 else -1
    summary = summarize(runs)
    return Result(
        "contention",
        {"shared": summary},
        [
            check_all_succeeded(runs, total),
            check_serialized(records, counter, total),
            check_capped(summary, 1, "runs on one key"),
        ],
    )


def extended(driver: Driver) -> Result:
    """Extended runs hold their own few slots."""
    settings = driver.settings
    run_ids = driver.fanout(driver.scenario("extended"), settings.extended_runs, extended=True)
    runs, _ = driver.wait(run_ids)
    summary = summarize(runs)
    return Result(
        "extended",
        {"extended": summary},
        [
            check_all_succeeded(runs, len(run_ids)),
            check_capped(summary, settings.max_extended, "extended runs"),
        ],
    )


def faults(driver: Driver) -> Result:
    """Runs against a gateway that fails some calls: outages retried, refusals not."""
    driver.control(rate_429=0.05, rate_500=0.05, rate_401=0.02)
    try:
        run_ids = driver.fanout(driver.scenario("faults"), driver.settings.fault_runs)
        runs, _ = driver.wait(run_ids)
    finally:
        driver.control(rate_429=0.0, rate_500=0.0, rate_401=0.0)
    served = driver.gateway_stats()["requests"]
    unfinished = [run for run in runs if run["status"] not in TERMINAL]
    succeeded = sum(1 for run in runs if run["status"] == "succeeded")
    return Result(
        "faults",
        {"batch": summarize(runs)},
        [
            Check(
                "every run reached a final status",
                not unfinished and len(runs) == len(run_ids),
                f"{len(runs)}/{len(run_ids)} recorded, {len(unfinished)} not final",
            ),
            Check(
                "the gateway served every run's model calls",
                served >= len(run_ids),
                f"{served} calls for {len(run_ids)} runs",
            ),
            Check(
                "runs succeeded through the faults",
                succeeded > 0,
                f"{succeeded}/{len(run_ids)} succeeded",
            ),
        ],
    )


SCENARIOS = {
    "throughput": throughput,
    "priority": priority,
    "chat-order": chat_order,
    "contention": contention,
    "extended": extended,
    "faults": faults,
}
# The scenarios that send chat turns, which need a staff session and a patient.
CHAT_SCENARIOS = frozenset({"priority", "chat-order"})


def report(results: list[Result]) -> str:
    """A plain-text report of every scenario's timings and checks."""
    lines = []
    for result in results:
        lines.append(
            f"== {result.scenario}: {'PASS' if result.passed else 'FAIL'} ({result.seconds:.0f}s)"
        )
        for name, summary in result.groups.items():
            lines.append(
                f"  {name}: {summary.runs} runs, {summary.throughput}/s, "
                f"{summary.max_concurrent} at once, {summary.retried} retried, "
                f"statuses {summary.statuses}"
                + (f", errors {summary.error_kinds}" if summary.error_kinds else "")
            )
            for label, values in (
                ("queue wait", summary.queue_wait),
                ("run time", summary.run_time),
                ("end to end", summary.end_to_end),
            ):
                lines.append(
                    f"    {label:<11} p50 {values['p50']}s  p95 {values['p95']}s  "
                    f"p99 {values['p99']}s  max {values['max']}s"
                )
        if result.gateway:
            lines.append(
                f"  gateway: {result.gateway['requests']} calls, "
                f"{result.gateway['max_in_flight']} in flight at most, faults {result.gateway['faults']}"
            )
        for check in result.checks:
            lines.append(f"  [{'pass' if check.passed else 'FAIL'}] {check.name}: {check.detail}")
            lines += [f"      {problem}" for problem in check.problems]
    return "\n".join(lines)


def parse(argv: list[str] | None = None) -> tuple[list[str], Settings, str | None]:
    """The scenarios to run, the settings, and where to write the JSON report."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("scenarios", nargs="+", choices=[*SCENARIOS, "all"])
    parser.add_argument("--instance", required=True, help="the instance's base URL")
    parser.add_argument(
        "--allow-remote-instance",
        action="store_true",
        help="load an instance other than localhost, which must be a development instance",
    )
    parser.add_argument("--gateway", default="http://localhost:8765", help="the fake gateway's URL")
    parser.add_argument("--patient-id", default="", help="the patient chat turns are about")
    parser.add_argument(
        "--runs", type=int, default=1000, help="batch runs for throughput and priority"
    )
    parser.add_argument(
        "--chats", type=int, default=20, help="chat turns for priority and chat-order"
    )
    parser.add_argument(
        "--chat-every", type=float, default=2.0, help="seconds between priority's chat turns"
    )
    parser.add_argument("--contention-runs", type=int, default=50)
    parser.add_argument("--extended-runs", type=int, default=5)
    parser.add_argument(
        "--max-extended", type=int, default=1, help="PLUGIN_RUNNER_MAX_EXTENDED_AGENT_RUNS"
    )
    parser.add_argument("--fault-runs", type=int, default=200)
    parser.add_argument(
        "--latency-ms", type=int, default=1000, help="each fake model call's latency"
    )
    parser.add_argument("--tools", type=int, default=2, help="tool calls per probe run")
    parser.add_argument("--timeout", type=float, default=1800, help="seconds to wait per scenario")
    parser.add_argument("--poll", type=float, default=5, help="seconds between status reads")
    parser.add_argument("--json", dest="json_path", help="also write the report as JSON here")
    args = parser.parse_args(argv)
    scenarios = list(SCENARIOS) if "all" in args.scenarios else args.scenarios
    host = urlsplit(args.instance).hostname or ""
    if not (host in LOCAL_HOSTS or host.endswith(".localhost") or args.allow_remote_instance):
        parser.error(f"{host or args.instance!r} is not localhost; pass --allow-remote-instance")
    api_key = os.environ.get(API_KEY_ENV, "")
    session_cookie = os.environ.get(SESSION_COOKIE_ENV, "")
    if not api_key:
        parser.error(f"set {API_KEY_ENV} to the plugin's simpleapi-api-key secret")
    if CHAT_SCENARIOS & set(scenarios) and not (session_cookie and args.patient_id):
        parser.error(f"priority and chat-order need {SESSION_COOKIE_ENV} and --patient-id")
    settings = Settings(
        **{
            name: value
            for name, value in vars(args).items()
            if name not in ("scenarios", "json_path", "allow_remote_instance")
        },
        api_key=api_key,
        session_cookie=session_cookie,
        tag=time.strftime("%Y%m%d%H%M%S"),
    )
    return scenarios, settings, args.json_path


def main(argv: list[str] | None = None) -> int:
    """Run the canary, then the chosen scenarios in order.

    Exits 2 when the canary fails and 1 when any scenario's check fails.
    """
    scenarios, settings, json_path = parse(argv)
    driver = Driver(settings)
    print("canary...", file=sys.stderr)
    if problem := canary(driver):
        print(f"stopping before any load: {problem}", file=sys.stderr)
        return 2
    results = []
    for name in scenarios:
        print(f"{name}...", file=sys.stderr)
        driver.reset_gateway()
        started = time.monotonic()
        result = SCENARIOS[name](driver)
        result.seconds = time.monotonic() - started
        result.gateway = driver.gateway_stats()
        driver.clear(driver.scenario(name))
        results.append(result)
    print(report(results))
    if json_path:
        with open(json_path, "w") as out:
            json.dump([asdict(result) for result in results], out, indent=2, default=str)
    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
