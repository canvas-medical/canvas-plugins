import asyncio
import gc
import os
import platform
import shutil
import socket
import subprocess
import sys
import tempfile
import textwrap
from collections.abc import Iterator
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from django.core.exceptions import ImproperlyConfigured

import settings
from canvas_sdk.utils.http import OntologiesHttp, PharmacyHttp, ScienceHttp
from canvas_sdk.utils.pdf import PdfGenerator
from plugin_runner.egress import config, process, relay
from plugin_runner.egress.config import EgressConfig, Forward
from plugin_runner.egress.confine import inside_addresses

POSTGRES = {"ENGINE": "django.db.backends.postgresql", "HOST": "db.example.in", "PORT": 21986}


@pytest.fixture
def socket_dir() -> Iterator[Path]:
    """A directory short enough for Unix socket paths, which `tmp_path` on macOS is not."""
    with tempfile.TemporaryDirectory(dir="/tmp") as directory:
        yield Path(directory)


@pytest.fixture
def confined(monkeypatch: pytest.MonkeyPatch) -> None:
    """An instance with an allowlist, Postgres, Redis, and the default endpoints."""
    monkeypatch.setattr(
        settings, "PLUGIN_RUNNER_EGRESS_ALLOWLIST", "api.example.com, *.Example.org"
    )
    monkeypatch.setattr(settings, "PLUGIN_RUNNER_GRPC_SOCKET", "/run/plugin-runner/grpc.sock")
    monkeypatch.setattr(settings, "DATABASES", {"default": POSTGRES})
    monkeypatch.setattr(settings, "REDIS_ENDPOINT", "rediss://cache.example.in:25107")
    monkeypatch.setattr(settings, "LOGSTASH_HOST", "https://logs.example.com")
    monkeypatch.setattr(settings, "LOGSTASH_PROTOCOL", "logger.logstash.HttpTransport")
    monkeypatch.setattr(settings, "SENTRY_DSN", "https://key@o1.ingest.sentry.io/2")
    for name in config.SDK_SERVICE_ENDPOINTS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.delenv("STATSD_HOST", raising=False)
    monkeypatch.delenv("STATSD_PORT", raising=False)


def test_no_allowlist_means_no_confinement(monkeypatch: pytest.MonkeyPatch) -> None:
    """An instance without an allowlist runs the runner as it is."""
    monkeypatch.setattr(settings, "PLUGIN_RUNNER_EGRESS_ALLOWLIST", " , ")

    assert config.load() is None


def test_load_adds_the_runners_own_hosts_and_services(confined: None) -> None:
    """The instance's hosts are joined by what the runner itself reaches."""
    egress = config.load()

    assert egress is not None
    assert egress.allowlist == (
        "*.example.org",
        "api.example.com",
        "logs.example.com",
        "o1.ingest.sentry.io",
        "ontologies.canvasmedical.com",
        "pharmacy-2017071.canvasmedical.com",
        f"s3-{settings.AWS_REGION}.amazonaws.com",
        "science.canvasmedical.com",
        "web-to-pdf.canvasmedical.com",
    )
    assert egress.forwards == (
        Forward("db.example.in", 21986, "tcp"),
        Forward("cache.example.in", 25107, "tcp"),
        Forward("localhost", 8125, "udp"),
    )


@pytest.mark.parametrize(
    "entry", ["*", "*.com.", "example", "https://example.com", "example.com/path", "a.*.com"]
)
def test_allowlist_entries_must_be_hostnames(entry: str) -> None:
    """Anything tinyproxy would match more broadly than a hostname is refused."""
    with pytest.raises(ImproperlyConfigured, match="hostnames"):
        config.parse_allowlist(f"example.com {entry}")


def test_confinement_requires_the_grpc_socket(
    confined: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A confined runner that home-app cannot reach is refused at start."""
    monkeypatch.setattr(settings, "PLUGIN_RUNNER_GRPC_SOCKET", None)

    with pytest.raises(ImproperlyConfigured, match="PLUGIN_RUNNER_GRPC_SOCKET"):
        config.load()


def test_forwarded_services_must_be_hostnames(
    confined: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An IP address cannot be pointed at a relay inside the namespace."""
    monkeypatch.setattr(settings, "DATABASES", {"default": {**POSTGRES, "HOST": "10.0.0.5"}})

    with pytest.raises(ImproperlyConfigured, match="must be a hostname"):
        config.load()


def test_logs_must_ship_over_http(confined: None, monkeypatch: pytest.MonkeyPatch) -> None:
    """A log transport the proxy cannot carry is refused at start."""
    monkeypatch.setattr(settings, "LOGSTASH_PROTOCOL", "logstash_async.transport.TcpTransport")

    with pytest.raises(ImproperlyConfigured, match="HTTP only"):
        config.load()


@pytest.mark.parametrize("override", [False, True])
def test_runner_hosts_cover_the_sdk_service_clients(
    confined: None, monkeypatch: pytest.MonkeyPatch, override: bool
) -> None:
    """Every Canvas service an SDK client calls is allowed, at its default or its override."""
    if override:
        for name in config.SDK_SERVICE_ENDPOINTS:
            monkeypatch.setenv(name, f"https://{name.lower().replace('_', '-')}.example.com")

    clients = [OntologiesHttp(), ScienceHttp(), PharmacyHttp(), PdfGenerator()]
    hosts = config.runner_hosts()

    for client in clients:
        assert urlsplit(client._http_client._base_url).hostname in hosts


def test_config_survives_the_trip_into_the_namespace(confined: None, tmp_path: Path) -> None:
    """The process inside reads back exactly what the supervisor wrote."""
    egress = config.load()
    assert egress is not None

    egress.write(tmp_path / "config.json")

    assert EgressConfig.read(tmp_path / "config.json") == egress


def test_each_forwarded_host_gets_its_own_loopback_address() -> None:
    """Hosts sharing a port do not collide, and one host keeps one address."""
    forwards = [
        Forward("db.example.in", 5432, "tcp"),
        Forward("cache.example.in", 5432, "tcp"),
        Forward("db.example.in", 6379, "tcp"),
        Forward("localhost", 8125, "udp"),
        Forward("127.0.0.9", 9000, "tcp"),
    ]

    assert inside_addresses(forwards) == [
        "127.0.0.2",
        "127.0.0.3",
        "127.0.0.2",
        "127.0.0.1",
        "127.0.0.9",
    ]


def test_stream_relay_carries_both_directions_across_a_unix_socket(socket_dir: Path) -> None:
    """TCP in, Unix socket across, TCP out, and the reply comes back the same way."""

    async def scenario() -> bytes:
        async def echo(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
            writer.write(b"echo:" + await reader.read())
            await writer.drain()
            writer.close()

        upstream = await asyncio.start_server(echo, "127.0.0.1", 0)
        upstream_port = upstream.sockets[0].getsockname()[1]

        crossing = socket_dir / "relay.sock"
        outside = socket.socket(socket.AF_UNIX)
        outside.bind(str(crossing))
        outside.listen()
        await relay.serve_stream(outside, relay.to_tcp("127.0.0.1", upstream_port))

        inside = socket.socket()
        inside.bind(("127.0.0.1", 0))
        inside.listen()
        await relay.serve_stream(inside, relay.to_unix(crossing))

        reader, writer = await asyncio.open_connection(*inside.getsockname())
        writer.write(b"hello")
        writer.write_eof()
        return await reader.read()

    assert asyncio.run(scenario()) == b"echo:hello"


def test_stream_relay_keeps_relaying_after_the_client_disconnects() -> None:
    """A handler still waiting on the upstream survives garbage collection.

    The stream protocol drops its reference to a handler when the client's connection is lost,
    and the event loop holds tasks only weakly.
    """

    async def scenario() -> list[str]:
        loop = asyncio.get_running_loop()
        errors: list[str] = []
        loop.set_exception_handler(lambda _loop, context: errors.append(context["message"]))
        answered: asyncio.Future[None] = loop.create_future()

        async def slow(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
            await reader.read()
            await asyncio.sleep(0.2)
            writer.write(b"late")
            await writer.drain()
            writer.close()
            answered.set_result(None)

        upstream = await asyncio.start_server(slow, "127.0.0.1", 0)
        inside = socket.socket()
        inside.bind(("127.0.0.1", 0))
        inside.listen()
        await relay.serve_stream(inside, relay.to_tcp(*upstream.sockets[0].getsockname()[:2]))

        _, writer = await asyncio.open_connection(*inside.getsockname())
        writer.write(b"request")
        writer.close()
        await writer.wait_closed()
        await asyncio.sleep(0.05)
        gc.collect()
        await asyncio.wait_for(answered, 5)
        await asyncio.sleep(0.05)
        gc.collect()
        return errors

    assert asyncio.run(scenario()) == []


def test_datagram_relay_carries_metrics_across_a_unix_socket(socket_dir: Path) -> None:
    """UDP in, Unix datagram socket across, UDP out."""

    async def scenario() -> bytes:
        loop = asyncio.get_running_loop()
        received: asyncio.Future[bytes] = loop.create_future()

        class Collector(asyncio.DatagramProtocol):
            def datagram_received(self, data: bytes, addr: object) -> None:
                received.set_result(data)

        collector, _ = await loop.create_datagram_endpoint(Collector, local_addr=("127.0.0.1", 0))

        crossing = socket_dir / "metrics.sock"
        outside = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        outside.bind(str(crossing))
        await relay.serve_datagrams(
            outside,
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM),
            collector.get_extra_info("sockname"),
        )

        inside = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        inside.bind(("127.0.0.1", 0))
        await relay.serve_datagrams(
            inside, socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM), str(crossing)
        )

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
            client.sendto(b"runner.metric:1|c", inside.getsockname())
        return await asyncio.wait_for(received, 5)

    assert asyncio.run(scenario()) == b"runner.metric:1|c"


linux_only = pytest.mark.skipif(sys.platform != "linux", reason="uses Linux process controls")


@linux_only
def test_run_child_returns_the_childs_exit_status() -> None:
    """The supervisor exits the way the runner did."""
    status = asyncio.run(process.run_child([sys.executable, "-c", "raise SystemExit(3)"]))

    assert status == 3


@linux_only
def test_run_child_stops_the_child_when_a_watched_process_exits() -> None:
    """Without the proxy the runner cannot work, so it is stopped rather than left running."""

    async def scenario() -> int:
        proxy = await asyncio.create_subprocess_exec(sys.executable, "-c", "pass")
        return await process.run_child(
            [sys.executable, "-c", "import time; time.sleep(60)"], watch={"proxy": proxy}
        )

    assert asyncio.run(scenario()) == 1


def test_no_allowlist_runs_the_command_as_it_is() -> None:
    """Without an allowlist the launcher becomes the command, with its output and status."""
    command = [sys.executable, "-c", "print('ran'); raise SystemExit(4)"]
    result = subprocess.run(
        [sys.executable, "-m", "plugin_runner.egress", "--", *command],
        env={**os.environ, "PLUGIN_RUNNER_EGRESS_ALLOWLIST": ""},
        capture_output=True,
        text=True,
    )

    assert (result.returncode, result.stdout) == (4, "ran\n")


def _can_confine() -> bool:
    if platform.system() != "Linux" or not shutil.which("tinyproxy"):
        return False
    probe = subprocess.run(["unshare", "--user", "--net", "true"], capture_output=True)
    return probe.returncode == 0


PROBES = textwrap.dedent(
    """
    import socket, sys, urllib.request

    def attempt(name, action):
        try:
            action()
        except Exception as error:
            print(f"{name}: blocked {type(error).__name__}")
        else:
            print(f"{name}: allowed")

    def fetch(url):
        request = urllib.request.Request(url, headers={"User-Agent": "egress-test"})
        urllib.request.urlopen(request, timeout=15).read(1)

    def capabilities():
        status = dict(line.split(":", 1) for line in open("/proc/self/status"))
        if int(status["CapEff"], 16) or int(status["CapBnd"], 16):
            raise RuntimeError(status["CapEff"].strip() + " " + status["CapBnd"].strip())

    def forward():
        with socket.create_connection((sys.argv[1], int(sys.argv[2])), timeout=5) as sock:
            sock.sendall(b"through")

    attempt("allowlisted", lambda: fetch("https://example.com/"))
    attempt("other host", lambda: fetch("https://www.google.com/"))
    attempt("raw socket", lambda: socket.create_connection(("1.1.1.1", 443), timeout=5))
    attempt("dns", lambda: socket.getaddrinfo("example.com", 443))
    attempt("capabilities", capabilities)
    print(f"forward address: {socket.gethostbyname(sys.argv[1])}")
    attempt("forward", forward)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as metrics:
        metrics.sendto(b"metric:1|c", ("localhost", int(sys.argv[3])))
    """
)


@pytest.mark.skipif(not _can_confine(), reason="needs Linux user namespaces and tinyproxy")
def test_confined_command_reaches_only_the_allowlist(socket_dir: Path) -> None:
    """The whole launcher, end to end, against the internet and two local services.

    The forwarded service is addressed by this machine's hostname, which resolves outside to
    a non-loopback address, so inside it has to be mapped to its relay.
    """
    hostname = socket.gethostname()
    if socket.gethostbyname(hostname).startswith("127."):
        pytest.skip("this machine's hostname resolves to loopback")
    forward = socket.socket()
    forward.bind(("0.0.0.0", 0))
    forward.listen()
    forward.settimeout(30)
    metrics = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    metrics.bind(("127.0.0.1", 0))
    metrics.settimeout(30)
    forward_port, metrics_port = forward.getsockname()[1], metrics.getsockname()[1]

    env = {
        **os.environ,
        "PLUGIN_RUNNER_EGRESS_ALLOWLIST": "example.com",
        "PLUGIN_RUNNER_GRPC_SOCKET": str(socket_dir / "grpc.sock"),
        "REDIS_ENDPOINT": f"redis://{hostname}:{forward_port}",
        "STATSD_PORT": str(metrics_port),
    }
    command = [sys.executable, "-c", PROBES, hostname, str(forward_port), str(metrics_port)]
    result = subprocess.run(
        [sys.executable, "-m", "plugin_runner.egress", "--", *command],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    outcomes = dict(line.split(": ", 1) for line in result.stdout.splitlines() if ": " in line)

    assert result.returncode == 0, result.stderr
    assert outcomes["allowlisted"] == "allowed"
    assert outcomes["other host"].startswith("blocked")
    assert outcomes["raw socket"].startswith("blocked")
    assert outcomes["dns"].startswith("blocked")
    assert outcomes["capabilities"] == "allowed"
    assert outcomes["forward address"] == "127.0.0.2"
    assert outcomes["forward"] == "allowed"
    assert forward.accept()[0].recv(16) == b"through"
    assert metrics.recv(64) == b"metric:1|c"
    assert 'Proxying refused on filtered domain "www.google.com"' in result.stdout
