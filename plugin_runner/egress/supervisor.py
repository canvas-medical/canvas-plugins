"""Outside the namespace: the allowlisting proxy and the relays to the runner's services."""

import asyncio
import shutil
import socket
import sys
import tempfile
import time
from collections.abc import Sequence
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

from plugin_runner.egress import linux, process, relay
from plugin_runner.egress.config import EgressConfig

# Refusals log at Notice, to stdout alongside the runner's own output.
TINYPROXY_CONFIG = """\
Listen 127.0.0.1
Port {port}
Allow 127.0.0.1
Timeout 600
MaxClients 256
LogLevel Notice

Filter "{allowlist}"
FilterType fnmatch
FilterDefaultDeny Yes
FilterCaseSensitive Yes

ConnectPort 443
"""

TINYPROXY_START_SECONDS = 10


def supervise(config: EgressConfig, command: Sequence[str]) -> int:
    """Run `command` confined to `config`, and return its exit status."""
    tinyproxy = shutil.which("tinyproxy")
    if not tinyproxy:
        raise ImproperlyConfigured(
            "PLUGIN_RUNNER_EGRESS_ALLOWLIST is set but tinyproxy is missing."
        )

    with tempfile.TemporaryDirectory(prefix="plugin-runner-egress-") as directory:
        return asyncio.run(_supervise(config, command, Path(directory), tinyproxy))


async def _supervise(
    config: EgressConfig, command: Sequence[str], state: Path, tinyproxy_path: str
) -> int:
    config.write(state / "config.json")
    (state / "allowlist").write_text("".join(f"{host}\n" for host in config.allowlist))
    port = _free_port()
    (state / "tinyproxy.conf").write_text(
        TINYPROXY_CONFIG.format(port=port, allowlist=state / "allowlist")
    )

    tinyproxy = await asyncio.create_subprocess_exec(
        tinyproxy_path, "-d", "-c", str(state / "tinyproxy.conf"), preexec_fn=linux.die_with_parent
    )
    try:
        await _wait_for_listener(port, tinyproxy)

        await relay.serve_stream(
            _unix_listener(config.proxy_socket(state), socket.SOCK_STREAM),
            relay.to_tcp("127.0.0.1", port),
        )
        for index, forward in enumerate(config.forwards):
            path = config.forward_socket(state, index)
            if forward.protocol == "tcp":
                await relay.serve_stream(
                    _unix_listener(path, socket.SOCK_STREAM),
                    relay.to_tcp(forward.host, forward.port),
                )
            else:
                # IPv4, as the statsd client resolves it; `localhost` may list ::1 first.
                family, kind, _, _, destination = socket.getaddrinfo(
                    forward.host, forward.port, socket.AF_INET, socket.SOCK_DGRAM
                )[0]
                sender = socket.socket(family, kind)
                sender.setblocking(False)
                await relay.serve_datagrams(
                    _unix_listener(path, socket.SOCK_DGRAM), sender, destination
                )

        confined = [sys.executable, "-m", "plugin_runner.egress.confine", str(state), "--"]
        return await process.run_child([*confined, *command], watch={"tinyproxy": tinyproxy})
    finally:
        if tinyproxy.returncode is None:
            tinyproxy.terminate()
            await tinyproxy.wait()


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


async def _wait_for_listener(port: int, tinyproxy: asyncio.subprocess.Process) -> None:
    """Wait until tinyproxy listens, read from the kernel's socket table.

    Connecting to check would log an error in tinyproxy for a client that sent nothing.
    """
    listening = f" 0100007F:{port:04X} 00000000:0000 0A "
    deadline = time.monotonic() + TINYPROXY_START_SECONDS
    while listening not in Path("/proc/net/tcp").read_text():
        if tinyproxy.returncode is not None:
            raise RuntimeError(f"tinyproxy exited with {tinyproxy.returncode} on start")
        if time.monotonic() > deadline:
            raise TimeoutError(f"tinyproxy did not listen on {port} in {TINYPROXY_START_SECONDS}s")
        await asyncio.sleep(0.05)


def _unix_listener(path: Path, kind: socket.SocketKind) -> socket.socket:
    sock = socket.socket(socket.AF_UNIX, kind)
    sock.bind(str(path))
    if kind == socket.SOCK_STREAM:
        sock.listen(128)
    sock.setblocking(False)
    return sock
