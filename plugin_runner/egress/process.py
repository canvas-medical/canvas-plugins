"""Run one child process, pass it the supervisor's signals, and stop when anything exits."""

import asyncio
import contextlib
import logging
import signal
from collections.abc import Mapping, Sequence

from plugin_runner.egress import linux

log = logging.getLogger(__name__)

FORWARDED_SIGNALS = (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)


async def run_child(
    command: Sequence[str],
    *,
    env: Mapping[str, str] | None = None,
    watch: Mapping[str, asyncio.subprocess.Process] | None = None,
) -> int:
    """Run `command` until it exits, and return its exit status.

    The child dies with this process, receives the signals this process does, and is killed
    when any process in `watch` exits first, since it cannot work without them.
    """
    child = await asyncio.create_subprocess_exec(
        *command, env=env, preexec_fn=linux.die_with_parent
    )
    loop = asyncio.get_running_loop()
    for signum in FORWARDED_SIGNALS:
        loop.add_signal_handler(signum, _send_signal, child, signum)

    waits = {
        asyncio.ensure_future(process.wait()): name
        for name, process in {command[0]: child, **(watch or {})}.items()
    }
    done, _ = await asyncio.wait(waits, return_when=asyncio.FIRST_COMPLETED)

    if child.returncode is None:
        for task in done:
            log.error(f"{waits[task]} exited with {task.result()}; stopping {command[0]}")
        child.kill()
        await child.wait()
        return 1

    return 128 - child.returncode if child.returncode < 0 else child.returncode


def _send_signal(child: asyncio.subprocess.Process, signum: int) -> None:
    with contextlib.suppress(ProcessLookupError):
        child.send_signal(signum)
