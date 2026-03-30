"""Check PyPI for newer versions of the canvas CLI and notify the user."""

import json
import os
import sys
import time
import urllib.request
from pathlib import Path

from packaging.version import Version

PYPI_URL = "https://pypi.org/pypi/canvas/json"
CACHE_FILENAME = "update_check.json"
CHECK_INTERVAL_SECONDS = 12 * 60 * 60  # 12 hours


def _get_cache_path(app_dir: str) -> Path:
    return Path(app_dir) / CACHE_FILENAME


def _read_cache(cache_path: Path) -> dict | None:
    if not cache_path.is_file():
        return None
    try:
        with open(cache_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, KeyError):
        # Treat a corrupt or incomplete cache file as a cache miss
        return None


def _write_cache(cache_path: Path, latest_version: str) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump({"last_checked": time.time(), "latest_version": latest_version}, f)


# Excluded from coverage because this hits the network (PyPI) and is always mocked in tests.
def _fetch_latest_version() -> str:  # pragma: no cover
    req = urllib.request.Request(PYPI_URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read())
    return data["info"]["version"]


def _print_notice(current: str, latest: str) -> None:
    message = (
        f"A newer version of canvas is available ({current} \u2192 {latest}). "
        f"Upgrade with: pip install --upgrade canvas"
    )
    # Use ANSI bold+yellow for "[notice]" on terminals that support it.
    notice_label = "\033[1;33m[notice]\033[0m" if sys.stderr.isatty() else "[notice]"
    print(f"{notice_label} {message}", file=sys.stderr)


def check_for_updates(current_version: str, app_dir: str) -> None:
    """Check if a newer version is available on PyPI and print a notice if so.

    This is best-effort — any error is silently ignored so it never
    interferes with normal CLI operation.
    """
    if os.environ.get("CANVAS_NO_UPDATE_CHECK"):
        return

    try:
        cache_path = _get_cache_path(app_dir)
        cache = _read_cache(cache_path)

        now = time.time()
        if cache and now - cache.get("last_checked", 0) < CHECK_INTERVAL_SECONDS:
            latest_version = cache["latest_version"]
        else:
            latest_version = _fetch_latest_version()
            _write_cache(cache_path, latest_version)

        if Version(latest_version) > Version(current_version):
            _print_notice(current_version, latest_version)
    except Exception:
        # Never let the update check break the CLI.
        pass
