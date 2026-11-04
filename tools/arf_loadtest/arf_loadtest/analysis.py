"""What a scenario's runs say: timings, concurrency, and the ordering and locking checks.

Every function here takes the rows the plugin's ``/runs`` endpoint returns: ``runs``,
the platform's ``AgentRun`` records, and ``records``, what each probe saw.
"""

import math
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

TERMINAL = frozenset({"succeeded", "failed", "refused", "abandoned", "gave_up"})


def _at(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _required_at(value: str) -> datetime:
    return datetime.fromisoformat(value)


def percentile(values: list[float], fraction: float) -> float:
    """The value ``fraction`` of the way through ``values`` sorted, by nearest rank."""
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(0, min(len(ordered) - 1, math.ceil(fraction * len(ordered)) - 1))
    return ordered[rank]


def spread(values: list[float]) -> dict[str, float]:
    """The count, median, tail, and maximum of a list of seconds."""
    return {
        "n": len(values),
        "p50": round(percentile(values, 0.50), 3),
        "p95": round(percentile(values, 0.95), 3),
        "p99": round(percentile(values, 0.99), 3),
        "max": round(max(values, default=0.0), 3),
    }


def max_overlap(intervals: list[tuple[datetime, datetime]]) -> int:
    """The most intervals open at one instant.

    Walks the starts and ends in time order, counting up at each start and down at each
    end; an end and a start at the same instant count the end first, so back-to-back
    runs do not overlap.
    """
    edges = sorted(
        [(start, 1) for start, _ in intervals] + [(end, -1) for _, end in intervals],
        key=lambda edge: (edge[0], edge[1]),
    )
    open_now = most = 0
    for _, step in edges:
        open_now += step
        most = max(most, open_now)
    return most


@dataclass
class Summary:
    """One group of runs' outcome and timings, in seconds."""

    runs: int
    statuses: dict[str, int]
    error_kinds: dict[str, int]
    queue_wait: dict[str, float]
    run_time: dict[str, float]
    end_to_end: dict[str, float]
    # Runs finished per second, from the first run queued to the last one finished.
    throughput: float
    max_concurrent: int
    retried: int
    model_calls: int


def summarize(runs: list[dict[str, Any]]) -> Summary:
    """Timings and outcomes for ``runs``."""
    queue_wait, run_time, end_to_end, intervals = [], [], [], []
    for run in runs:
        queued, started, finished = (
            _at(run["queued_at"]),
            _at(run["started_at"]),
            _at(run["finished_at"]),
        )
        if queued and started:
            queue_wait.append((started - queued).total_seconds())
        if started and finished:
            run_time.append((finished - started).total_seconds())
            intervals.append((started, finished))
        if queued and finished:
            end_to_end.append((finished - queued).total_seconds())
    queued_times = [t for run in runs if (t := _at(run["queued_at"]))]
    finished_times = [t for run in runs if (t := _at(run["finished_at"]))]
    window = (
        (max(finished_times) - min(queued_times)).total_seconds()
        if queued_times and finished_times
        else 0.0
    )
    return Summary(
        runs=len(runs),
        statuses=dict(Counter(run["status"] for run in runs)),
        error_kinds=dict(Counter(run["error_kind"] for run in runs if run["error_kind"])),
        queue_wait=spread(queue_wait),
        run_time=spread(run_time),
        end_to_end=spread(end_to_end),
        throughput=round(len(finished_times) / window, 3) if window > 0 else 0.0,
        max_concurrent=max_overlap(intervals),
        retried=sum(1 for run in runs if (run["attempts"] or 0) > 1),
        model_calls=sum(run["model_calls"] or 0 for run in runs),
    )


@dataclass
class Check:
    """One pass/fail property of a scenario, with what it found."""

    name: str
    passed: bool
    detail: str
    problems: list[str] = field(default_factory=list)


def check_all_succeeded(runs: list[dict[str, Any]], expected: int) -> Check:
    """Every run the driver started has a record, and every record succeeded."""
    statuses = Counter(run["status"] for run in runs)
    missing = expected - len(runs)
    passed = missing == 0 and statuses.get("succeeded", 0) == expected
    return Check(
        "all runs succeeded",
        passed,
        f"{statuses.get('succeeded', 0)}/{expected} succeeded, {missing} without a record, "
        f"statuses {dict(statuses)}",
    )


def check_serialized(records: list[dict[str, Any]], counter: int) -> Check:
    """Runs on one key ran one at a time and lost no update.

    Each run read the key's counter and wrote it one higher. Run one at a time, K runs
    read 0 to K-1 once each and leave the counter at K; two runs that overlapped read
    the same value, and the counter ends short.
    """
    problems = []
    seen = Counter(record["saw"] for record in records)
    if duplicates := sorted(value for value, n in seen.items() if n > 1):
        problems.append(f"runs read the same counter value: {duplicates[:10]}")
    if counter != len(records):
        problems.append(f"counter is {counter} after {len(records)} runs")
    ordered = sorted(records, key=lambda record: _required_at(record["started_at"]))
    overlaps = [
        f"{before['run_id']} and {after['run_id']}"
        for before, after in zip(ordered, ordered[1:], strict=False)
        if _required_at(after["started_at"]) < _required_at(before["finished_at"])
    ]
    if overlaps:
        problems.append(f"{len(overlaps)} runs started before the one before them finished")
    return Check(
        "runs on one key serialized",
        not problems,
        f"{len(records)} runs, counter {counter}, {len(overlaps)} overlaps",
        problems + overlaps[:10],
    )


def check_chat_order(records: list[dict[str, Any]]) -> Check:
    """Each chat turn ran after the one sent before it: turn n saw turn n-1.

    The first turn is not checked, since the conversation may hold an earlier
    scenario's last turn.
    """
    ordered = sorted(records, key=lambda record: record["seq"])
    out_of_order = [
        f"turn {after['seq']} saw turn {after['saw']}, expected {before['seq']}"
        for before, after in zip(ordered, ordered[1:], strict=False)
        if after["saw"] != before["seq"]
    ]
    return Check(
        "chat turns ran in the order sent",
        not out_of_order,
        f"{len(ordered)} turns, {len(out_of_order)} out of order",
        out_of_order[:10],
    )


def check_prioritized(chat: Summary, batch: Summary) -> Check:
    """Chat turns waited less in the queue than batch runs did.

    Passes when the slowest chat turns (p95) still waited less than the typical batch
    run (p50): with interactive runs ahead of batch runs in the queue, a chat waits only
    for a free run slot while a batch run waits behind the whole backlog.
    """
    passed = chat.queue_wait["n"] > 0 and chat.queue_wait["p95"] < batch.queue_wait["p50"]
    return Check(
        "chat prioritized over batch",
        passed,
        f"chat queue wait p95 {chat.queue_wait['p95']}s, batch queue wait p50 "
        f"{batch.queue_wait['p50']}s",
    )


def check_capped(summary: Summary, cap: int, what: str) -> Check:
    """No more than ``cap`` runs ran at once."""
    return Check(
        f"at most {cap} {what} at once",
        summary.max_concurrent <= cap,
        f"{summary.max_concurrent} ran at once",
    )
