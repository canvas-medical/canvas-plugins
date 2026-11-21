"""Inside the namespace: set it up, relay out of it, and run the runner in it.

    python -m plugin_runner.egress.confine STATE -- COMMAND...

STATE is the supervisor's directory, holding the configuration and the Unix sockets its
relays listen on.
"""

import asyncio
import os
import socket
import sys
from collections.abc import Sequence
from pathlib import Path

from plugin_runner.egress import linux, process, relay
from plugin_runner.egress.config import PROXY_PORT, EgressConfig, Forward

PROXY_URL = f"http://127.0.0.1:{PROXY_PORT}"
PROXY_VARIABLES = ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy")
BYPASS_VARIABLES = ("NO_PROXY", "no_proxy", "ALL_PROXY", "all_proxy")


def main(argv: Sequence[str]) -> int:
    """Confine this process, then run the command inside with relays out."""
    state, separator, *command = argv
    if separator != "--" or not command:
        raise SystemExit(__doc__)
    state_path = Path(state)
    config = EgressConfig.read(state_path / "config.json")

    linux.enter_namespaces()
    addresses = inside_addresses(config.forwards)
    _map_hostnames(state_path / "hosts", config.forwards, addresses)
    linux.bring_up_loopback()

    # Bound before capabilities go, in case a forwarded port is below 1024.
    proxy = _listener(socket.SOCK_STREAM, "127.0.0.1", PROXY_PORT)
    forwards = [
        _listener(_socket_kind(forward), address, forward.port)
        for forward, address in zip(config.forwards, addresses, strict=True)
    ]
    linux.drop_capabilities()

    return asyncio.run(_run(state_path, config, proxy, forwards, command))


def inside_addresses(forwards: Sequence[Forward]) -> list[str]:
    """The loopback address each forward listens on inside the namespace.

    Services on the container's loopback keep their address. Each other host gets its own,
    from 127.0.0.2 up, so services on different hosts but the same port do not collide.
    """
    by_host: dict[str, str] = {}
    for forward in forwards:
        if forward.is_loopback:
            by_host[forward.host] = "127.0.0.1" if forward.host == "localhost" else forward.host
        elif forward.host not in by_host:
            by_host[forward.host] = f"127.0.0.{len(by_host) + 2}"
    return [by_host[forward.host] for forward in forwards]


async def _run(
    state: Path,
    config: EgressConfig,
    proxy: socket.socket,
    forwards: Sequence[socket.socket],
    command: Sequence[str],
) -> int:
    await relay.serve_stream(proxy, relay.to_unix(config.proxy_socket(state)))
    for index, (forward, listener) in enumerate(zip(config.forwards, forwards, strict=True)):
        path = config.forward_socket(state, index)
        if forward.protocol == "tcp":
            await relay.serve_stream(listener, relay.to_unix(path))
        else:
            sender = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            sender.setblocking(False)
            await relay.serve_datagrams(listener, sender, str(path))

    env = {name: value for name, value in os.environ.items() if name not in BYPASS_VARIABLES}
    env.update(dict.fromkeys(PROXY_VARIABLES, PROXY_URL))
    return await process.run_child(command, env=env)


def _map_hostnames(hosts: Path, forwards: Sequence[Forward], addresses: Sequence[str]) -> None:
    """Resolve each forwarded hostname to its relay, so clients keep their configured names.

    Keeping the name keeps TLS hostname verification working. Nothing else resolves inside.
    """
    entries = {
        f"{address} {forward.host}\n"
        for forward, address in zip(forwards, addresses, strict=True)
        if not forward.is_loopback
    }
    existing = Path("/etc/hosts").read_text().rstrip("\n")
    hosts.write_text(f"{existing}\n{''.join(sorted(entries))}")
    linux.bind_mount(hosts, Path("/etc/hosts"))


def _socket_kind(forward: Forward) -> socket.SocketKind:
    return socket.SOCK_STREAM if forward.protocol == "tcp" else socket.SOCK_DGRAM


def _listener(kind: socket.SocketKind, address: str, port: int) -> socket.socket:
    sock = socket.socket(socket.AF_INET, kind)
    sock.bind((address, port))
    if kind == socket.SOCK_STREAM:
        sock.listen(128)
    sock.setblocking(False)
    return sock


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
