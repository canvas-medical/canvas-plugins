"""Relays that carry connections and datagrams across the network namespace boundary.

A Unix socket is a file, so it reaches across network namespaces where TCP and UDP cannot.
Inside the namespace a relay listens on a loopback address and passes everything to a Unix
socket; outside, a relay listens on that Unix socket and passes everything to the real
destination.
"""

import asyncio
import contextlib
import socket
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

Connect = Callable[[], Awaitable[tuple[asyncio.StreamReader, asyncio.StreamWriter]]]

_CHUNK = 64 * 1024

# The stream protocol drops its reference to a connection's handler when the client side is
# lost, and the event loop holds tasks only weakly, so running handlers are held here.
_handlers: set[asyncio.Task[None]] = set()


def to_tcp(host: str, port: int) -> Connect:
    """Connect to a TCP address."""
    return lambda: asyncio.open_connection(host, port)


def to_unix(path: Path) -> Connect:
    """Connect to a Unix socket."""
    return lambda: asyncio.open_unix_connection(path)


async def serve_stream(listener: socket.socket, connect: Connect) -> asyncio.Server:
    """Pass each connection accepted on `listener` to a new connection made with `connect`."""

    async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        handler = asyncio.current_task()
        assert handler is not None
        _handlers.add(handler)
        try:
            await _relay(reader, writer, connect)
        finally:
            _handlers.discard(handler)

    if listener.family == socket.AF_UNIX:
        return await asyncio.start_unix_server(handle, sock=listener)
    return await asyncio.start_server(handle, sock=listener)


async def serve_datagrams(
    listener: socket.socket, sender: socket.socket, destination: Any
) -> asyncio.DatagramTransport:
    """Send each datagram received on `listener` to `destination` through `sender`."""
    transport, _ = await asyncio.get_running_loop().create_datagram_endpoint(
        lambda: _DatagramForwarder(sender, destination), sock=listener
    )
    return transport


async def _relay(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter, connect: Connect
) -> None:
    try:
        upstream_reader, upstream_writer = await connect()
    except OSError:
        writer.close()
        return
    try:
        await asyncio.gather(_pipe(reader, upstream_writer), _pipe(upstream_reader, writer))
    finally:
        writer.close()
        upstream_writer.close()


async def _pipe(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """Copy until end of stream, then pass the end on; on a broken connection, close both."""
    try:
        while data := await reader.read(_CHUNK):
            writer.write(data)
            await writer.drain()
        if writer.can_write_eof():
            writer.write_eof()
    except OSError:
        writer.close()


class _DatagramForwarder(asyncio.DatagramProtocol):
    def __init__(self, sender: socket.socket, destination: Any) -> None:
        self._sender = sender
        self._destination = destination

    def datagram_received(self, data: bytes, addr: Any) -> None:
        # Datagrams here are metrics, which are best effort: a full buffer drops one.
        with contextlib.suppress(OSError):
            self._sender.sendto(data, self._destination)
