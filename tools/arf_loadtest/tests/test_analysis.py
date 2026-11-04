from datetime import UTC, datetime, timedelta
from typing import Any

from arf_loadtest.analysis import (
    check_all_succeeded,
    check_chat_order,
    check_prioritized,
    check_serialized,
    max_overlap,
    percentile,
    summarize,
)

T0 = datetime(2026, 11, 4, tzinfo=UTC)


def at(seconds: float) -> str:
    """The ISO time ``seconds`` after T0."""
    return (T0 + timedelta(seconds=seconds)).isoformat()


def run(queued: float, started: float, finished: float, **fields: Any) -> dict[str, Any]:
    """An AgentRun row as /runs returns it."""
    return {
        "run_id": fields.get("run_id", f"r{queued}-{started}"),
        "status": fields.get("status", "succeeded"),
        "error_kind": fields.get("error_kind", ""),
        "attempts": fields.get("attempts", 1),
        "model_calls": 3,
        "scope_key": "key:x",
        "queued_at": at(queued),
        "started_at": at(started),
        "finished_at": at(finished),
    }


def record(seq: int, saw: int, started: float, finished: float) -> dict[str, Any]:
    """A probe record as /runs returns it."""
    return {
        "run_id": f"r{seq}",
        "seq": seq,
        "saw": saw,
        "started_at": at(started),
        "finished_at": at(finished),
    }


def test_percentile_is_nearest_rank() -> None:
    """Percentiles pick a value from the list, by nearest rank."""
    values = [float(n) for n in range(1, 101)]
    assert (percentile(values, 0.5), percentile(values, 0.95), percentile(values, 1.0)) == (
        50,
        95,
        100,
    )
    assert percentile([], 0.5) == 0.0


def test_back_to_back_intervals_do_not_overlap() -> None:
    """A run starting as another ends does not count as concurrent."""
    assert (
        max_overlap(
            [
                (T0, T0 + timedelta(seconds=1)),
                (T0 + timedelta(seconds=1), T0 + timedelta(seconds=2)),
            ]
        )
        == 1
    )
    assert (
        max_overlap(
            [
                (T0, T0 + timedelta(seconds=2)),
                (T0 + timedelta(seconds=1), T0 + timedelta(seconds=3)),
            ]
        )
        == 2
    )


def test_summarize_times_and_counts_runs() -> None:
    """Queue wait, run time, concurrency, throughput, and outcomes come from the records."""
    summary = summarize(
        [
            run(0, 1, 3),
            run(0, 2, 4, attempts=2),
            run(0, 0, 0, status="failed", error_kind="GATEWAY"),
        ]
    )

    assert summary.queue_wait["max"] == 2.0
    assert summary.run_time["p50"] == 2.0
    assert summary.max_concurrent == 2
    assert summary.throughput == 0.75
    assert (summary.retried, summary.statuses, summary.error_kinds) == (
        1,
        {"succeeded": 2, "failed": 1},
        {"GATEWAY": 1},
    )


def test_all_succeeded_counts_runs_without_a_record() -> None:
    """A run the platform never recorded, or one that did not succeed, fails the check."""
    assert check_all_succeeded([run(0, 1, 2)], 1).passed
    assert not check_all_succeeded([run(0, 1, 2)], 2).passed
    assert not check_all_succeeded([run(0, 1, 2, status="gave_up")], 1).passed


def test_serialized_runs_pass() -> None:
    """Runs one after another on a key read 0 to K-1 and leave the counter at K."""
    records = [record(n, n, n, n + 0.5) for n in range(3)]
    assert check_serialized(records, 3).passed


def test_overlapping_runs_on_one_key_fail() -> None:
    """Two runs that read the same count overlapped and lost an update."""
    records = [record(0, 0, 0, 2), record(1, 0, 1, 3), record(2, 1, 3, 4)]

    check = check_serialized(records, 2)

    assert not check.passed
    assert any("same counter value" in problem for problem in check.problems)
    assert any("counter is 2 after 3" in problem for problem in check.problems)


def test_chat_order_ignores_the_first_turn_and_catches_a_swap() -> None:
    """Turn n must see turn n-1; the first turn may see an earlier scenario's."""
    assert check_chat_order([record(1, 9, 0, 1), record(2, 1, 1, 2), record(3, 2, 2, 3)]).passed
    swapped = check_chat_order([record(1, 0, 0, 1), record(2, 3, 2, 3), record(3, 1, 1, 2)])
    assert not swapped.passed
    assert swapped.problems[0] == "turn 2 saw turn 3, expected 1"


def test_prioritized_compares_the_chat_tail_to_the_batch_median() -> None:
    """Chat passes when its p95 queue wait is under the batch median."""
    batch = summarize([run(0, wait, wait + 1) for wait in range(10, 20)])
    assert check_prioritized(summarize([run(0, 1, 2)]), batch).passed
    assert not check_prioritized(summarize([run(0, 30, 31)]), batch).passed
    assert not check_prioritized(summarize([]), batch).passed
