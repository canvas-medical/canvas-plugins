"""Tell the user, at most once a day, that authentication and deployment are changing."""

import json
import sys
import time
from pathlib import Path

MIGRATION_URL = "https://github.com/canvas-medical/canvas-plugins#migrating-from-credentialsini-to-canvas-platform"
CACHE_FILENAME = "platform_notice.json"
NOTICE_INTERVAL_SECONDS = 24 * 60 * 60


def _notice_label() -> str:
    return "\033[1;33m[notice]\033[0m" if sys.stderr.isatty() else "[notice]"


def print_install_deprecation() -> None:
    """Warn that installing straight onto an instance is deprecated."""
    print(
        f"{_notice_label()} Installing plugins straight onto an instance with credentials.ini "
        "is deprecated in favor of `canvas login` and `canvas deploy`. The deprecation window "
        f"will be announced through Canvas's standard channels. See {MIGRATION_URL}",
        file=sys.stderr,
    )


def show_platform_notice(app_dir: str) -> None:
    """Print the authentication and deployment notice unless it was shown in the last day."""
    cache_path = Path(app_dir) / CACHE_FILENAME
    try:
        last_shown = json.loads(cache_path.read_text())["last_shown"]
    except (OSError, ValueError, KeyError, TypeError):
        last_shown = 0

    now = time.time()
    if now - last_shown < NOTICE_INTERVAL_SECONDS:
        return

    print(
        f"{_notice_label()} Changes to authentication and deployment are coming to the canvas "
        f"CLI. See {MIGRATION_URL} for more.",
        file=sys.stderr,
    )
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps({"last_shown": now}))
    except OSError:
        pass
