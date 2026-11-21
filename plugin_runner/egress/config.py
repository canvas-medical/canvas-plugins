"""What the confined runner may reach, derived from its settings and environment."""

import ipaddress
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured

import settings

# Allowlist entries are lowercase hostnames, optionally with a leading `*.` wildcard, which
# tinyproxy matches with fnmatch against the whole requested host.
ALLOWLIST_ENTRY = re.compile(r"(\*\.)?[a-z0-9-]+(\.[a-z0-9-]+)+")

# The Canvas services the SDK's own clients call. The defaults mirror the clients'
# (`canvas_sdk.utils.http`, `canvas_sdk.utils.pdf`); a test fails when they drift.
SDK_SERVICE_ENDPOINTS = {
    "ONTOLOGIES_ENDPOINT": "https://ontologies.canvasmedical.com",
    "SCIENCE_ENDPOINT": "https://science.canvasmedical.com",
    "PHARMACY_SERVICE_ENDPOINT": "https://pharmacy-2017071.canvasmedical.com",
    "WEB_TO_PDF_ENDPOINT": "https://web-to-pdf.canvasmedical.com",
    "CANVAS_PUBLIC_HOST": "",
}

# Inside the namespace the HTTP proxy listens here.
PROXY_PORT = 3128


@dataclass(frozen=True)
class Forward:
    """A non-HTTP service the confined runner reaches through its own relay."""

    host: str
    port: int
    protocol: Literal["tcp", "udp"]

    @property
    def is_loopback(self) -> bool:
        """Whether the service is on the container's own loopback."""
        return self.host == "localhost" or self.host.startswith("127.")


@dataclass(frozen=True)
class EgressConfig:
    """Everything the confined runner may reach."""

    allowlist: tuple[str, ...]
    forwards: tuple[Forward, ...]

    @staticmethod
    def proxy_socket(state: Path) -> Path:
        """The Unix socket that carries HTTP proxy connections out of the namespace."""
        return state / "proxy.sock"

    @staticmethod
    def forward_socket(state: Path, index: int) -> Path:
        """The Unix socket that carries forward `index` out of the namespace."""
        return state / f"forward-{index}.sock"

    def write(self, path: Path) -> None:
        """Save the configuration for the process inside the namespace."""
        path.write_text(json.dumps(asdict(self)))

    @classmethod
    def read(cls, path: Path) -> "EgressConfig":
        """Load a configuration saved with `write`."""
        data = json.loads(path.read_text())
        return cls(
            allowlist=tuple(data["allowlist"]),
            forwards=tuple(Forward(**forward) for forward in data["forwards"]),
        )


def load() -> EgressConfig | None:
    """The runner's egress configuration, or None when its network is not confined."""
    allowlist = parse_allowlist(settings.PLUGIN_RUNNER_EGRESS_ALLOWLIST)
    if not allowlist:
        return None

    if not settings.PLUGIN_RUNNER_GRPC_SOCKET:
        raise ImproperlyConfigured(
            "PLUGIN_RUNNER_EGRESS_ALLOWLIST is set but PLUGIN_RUNNER_GRPC_SOCKET is not: "
            "a confined runner is reachable only over its Unix socket."
        )

    forwards = runner_forwards()
    for forward in forwards:
        if forward.is_loopback and forward.port == PROXY_PORT:
            raise ImproperlyConfigured(
                f"{forward.host}:{forward.port} collides with the proxy inside the namespace."
            )
        if not forward.is_loopback and _is_ip_address(forward.host):
            raise ImproperlyConfigured(
                f"{forward.host} must be a hostname: inside the namespace only hostnames "
                "can be pointed at a relay."
            )

    return EgressConfig(
        allowlist=tuple(sorted(set(allowlist) | set(runner_hosts()))),
        forwards=forwards,
    )


def parse_allowlist(value: str) -> list[str]:
    """Split a comma- or space-separated allowlist, refusing entries that are not hostnames."""
    entries = [entry.lower() for entry in re.split(r"[\s,]+", value) if entry]
    invalid = [entry for entry in entries if not ALLOWLIST_ENTRY.fullmatch(entry)]
    if invalid:
        raise ImproperlyConfigured(
            f"PLUGIN_RUNNER_EGRESS_ALLOWLIST entries must be hostnames or *.domain: {invalid}"
        )
    return entries


def runner_hosts() -> list[str]:
    """The hosts the runner itself reaches over HTTP: plugin packages, logs, errors, services."""
    if not settings.LOGSTASH_PROTOCOL.endswith(".HttpTransport"):
        raise ImproperlyConfigured(
            "A confined runner ships logs over HTTP only; PLUGINS_LOGSTASH_PROTOCOL is "
            f"{settings.LOGSTASH_PROTOCOL}."
        )

    urls = [
        f"https://s3-{settings.AWS_REGION}.amazonaws.com",
        settings.LOGSTASH_HOST,
        settings.SENTRY_DSN,
        *(os.getenv(name, default) for name, default in SDK_SERVICE_ENDPOINTS.items()),
    ]
    return sorted({host for url in urls if url and (host := urlsplit(url).hostname)})


def runner_forwards() -> tuple[Forward, ...]:
    """The non-HTTP services the runner itself reaches: Postgres, Redis, and statsd."""
    forwards = []

    database = settings.DATABASES["default"]
    if database["ENGINE"] == "django.db.backends.postgresql":
        forwards.append(Forward(str(database["HOST"]), int(database["PORT"] or 5432), "tcp"))

    redis = urlsplit(settings.REDIS_ENDPOINT)
    if redis.hostname:
        forwards.append(Forward(redis.hostname, redis.port or 6379, "tcp"))

    forwards.append(
        Forward(os.getenv("STATSD_HOST", "localhost"), int(os.getenv("STATSD_PORT", "8125")), "udp")
    )
    return tuple(dict.fromkeys(forwards))


def _is_ip_address(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return False
    return True
