from __future__ import annotations

import base64
import json
import random
import re
import shlex
import shutil
import sys
import threading
import time
import zlib
from collections.abc import Callable, Iterator
from datetime import UTC, datetime, timedelta
from typing import Any, NamedTuple, TypedDict, cast
from urllib.parse import urlencode, urlparse

import click
import requests
import typer
import websocket

from canvas_cli.apps.auth.utils import get_default_host, get_or_request_api_token, instance_slug
from canvas_cli.apps.platform.client import PlatformError
from canvas_cli.apps.platform.routing import managed_instance, platform_sign_out
from canvas_cli.apps.plugin.plugin import plugin_url
from canvas_cli.utils.platform_notice import notice_label

# Seconds before a minted token's expiry at which it is replaced.
EXPIRY_MARGIN_SECONDS = 30
# The instance answers an expired or revoked token with 403, since its logs endpoint tries
# session authentication first and so sends no WWW-Authenticate challenge. 401 is kept for a
# proxy or release that does send one.
REFUSED_TOKEN_STATUSES: tuple[int, ...] = (requests.codes.unauthorized, requests.codes.forbidden)
# The close code Console sends when it re-checks a Platform-issued token and finds it inactive.
STREAM_TOKEN_INACTIVE = 4401
# The refusal Console sends when the instance does not accept the token. Its other refusals,
# such as "No instance named '<slug>' was found.", are not about the token.
STREAM_TOKEN_REFUSAL = "Token authorization failed."
PING_INTERVAL_SECONDS = 30
PING_TIMEOUT_SECONDS = 10
RECONNECT_FIRST_DELAY_SECONDS = 1.0
RECONNECT_MAX_DELAY_SECONDS = 60.0
# A stream open at least this long resets the reconnect delay to its first value.
HEALTHY_STREAM_SECONDS = 60
# A guess at how long a line takes to become searchable in history, waited before fetching a
# gap so its last lines are found.
BACKFILL_DELAY_SECONDS = 10
# Seconds added to each side of a gap: Console subscribes to the instance's log channel only
# after it sends "Log stream connected.", and this machine's clock can differ from the instance's.
GAP_MARGIN_SECONDS = 5
# Held while printing log lines, so a backfill prints as one block between live lines.
_OUTPUT_LOCK = threading.Lock()


def _instance_answer(response: requests.Response) -> str:
    """Return the instance's ``detail`` as a sentence to quote, or an empty string.

    Args:
        response (requests.Response): The instance's refusal.

    Returns:
        str: ``The instance answered: <detail> `` with a trailing space, or "" when the body
            carries no ``detail``.
    """
    try:
        body: Any = response.json()
    except ValueError:
        return ""
    detail: Any = body.get("detail") if isinstance(body, dict) else None
    if not isinstance(detail, str) or not detail:
        return ""
    return f"The instance answered: {detail} "


class LogToken:
    """A bearer token for an instance's logs, and how to get a fresh one.

    The credentials.ini token is requested the way every instance command requests it and is
    not reissued on a refusal. A Platform-issued token is minted on first use, minted again once
    it nears expiry, and minted again when the instance answers 401 or 403.
    """

    def __init__(
        self,
        slug: str,
        mint: Callable[[], tuple[str, float | None]],
        *,
        reissuable: bool,
    ) -> None:
        """Hold a token source.

        Args:
            slug (str): The instance the token is for, used in messages.
            mint (Callable[[], tuple[str, float | None]]): Returns a token and its lifetime in
                seconds, or None for a token with no known expiry.
            reissuable (bool): Whether a 401 or 403 should mint a fresh token and retry.
        """
        self.slug: str = slug
        self.reissuable: bool = reissuable
        self._mint: Callable[[], tuple[str, float | None]] = mint
        self._token: str | None = None
        self._expires_at: float | None = None

    def get(self) -> str:
        """Return the held token, minting one first when none is held or it is near expiry.

        Returns:
            str: The bearer token.
        """
        if self._token is None or (
            self._expires_at is not None and time.monotonic() >= self._expires_at
        ):
            return self.refresh()
        return self._token

    def refresh(self) -> str:
        """Mint a fresh token.

        Returns:
            str: The new bearer token.
        """
        token, lifetime = self._mint()
        self._token = token
        self._expires_at = (
            None if lifetime is None else time.monotonic() + lifetime - EXPIRY_MARGIN_SECONDS
        )
        return token


def log_token_source(host: str) -> LogToken:
    """Choose where the log token for ``host`` comes from.

    Signed in to Canvas Platform, a Canvas instance goes through Platform: Platform issues the
    token for an instance it manages, and any other instance is refused with the way to sign
    out. Signed out, or for localhost and other hosts that are not Canvas instances, the
    credentials.ini token is used and the deprecation notice is printed. A failed Platform
    lookup or refusal raises and never falls back to credentials.ini.

    Args:
        host (str): The Canvas instance URL.

    Returns:
        LogToken: The token source.

    Raises:
        click.ClickException: Signed in, and Platform does not manage the instance.
    """
    if (managed := managed_instance(host, "logs")) is not None:
        client, slug = managed.client, managed.slug

        def mint() -> tuple[str, float | None]:
            try:
                body = client.log_token(slug)
            except PlatformError as error:
                # A 404 with no ``code`` means this Platform does not serve the route.
                if error.status == requests.codes.not_found and not error.code:
                    raise click.ClickException(
                        "Canvas Platform does not issue log tokens yet. To read the instance's "
                        "logs, sign out with `canvas logout` (or unset CANVAS_PLATFORM_TOKEN) "
                        "and use credentials.ini."
                    ) from error
                raise
            return body["access_token"], float(body["expires_in"])

        return LogToken(slug, mint, reissuable=True)

    return LogToken(
        instance_slug(host) or host,
        lambda: (get_or_request_api_token(host), None),
        reissuable=False,
    )


DURATION_REGEX = re.compile(
    r"""
    ^\s*                 # optional leading whitespace
    (?:(?P<d>\d+)d)?\s*  # optional days
    (?:(?P<h>\d+)h)?\s*  # optional hours
    (?:(?P<m>\d+)m)?\s*  # optional minutes
    (?:(?P<s>\d+)s)?\s*  # optional seconds
    \s*$                 # optional trailing whitespace
""",
    re.VERBOSE,
)
DEFAULT_PAGE_SIZE = 200
LAST_CURSOR: list[str] | None = None


def _format_line(hit: dict[str, Any], log_prefix: str = "") -> str:
    """Format a log entry for printing."""
    level = (hit.get("log", {}).get("level")).upper()
    asctime = hit.get("ts")
    message = hit.get("message") or ""
    service = hit.get("service", {}).get("name")
    prefix = f"{log_prefix}" if log_prefix else ""
    error = hit.get("error", {})

    output = f"{service} {prefix}{level} {asctime} {message}"

    if error:
        if (stack_trace := error.get("stack_trace")) and service == "plugin-runner":
            output = f"{output}\n{''.join(stack_trace)}".rstrip("\n")
        else:
            output = f"{output}: ({error.get('type', '').split('.')[-1]}: {error.get('message', '')})".strip()

    return output


def _parse_duration(s: str) -> timedelta:
    """
    Accepts '24h', '2h30m', '1d', '45m', '90s', '1d2h15m10s' etc.
    """
    m = DURATION_REGEX.match(s)

    if not m:
        raise typer.BadParameter("Use durations like '15m', '2h', '1d2h30m', '45s'.")

    days = int(m.group("d") or 0)
    hours = int(m.group("h") or 0)
    minutes = int(m.group("m") or 0)
    seconds = int(m.group("s") or 0)

    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


def _parse_when(s: str) -> datetime:
    """
    Parses ISO/RFC3339 or 'now'. Naive times treated as local and converted to UTC.
    """
    if s.lower() == "now":
        return datetime.now(UTC)
    try:
        dt = datetime.fromisoformat(s)
    except ValueError as e:
        raise typer.BadParameter(f"Invalid datetime '{s}': {e}") from None
    if dt.tzinfo is None:
        dt = dt.astimezone()  # assume local
    return dt.astimezone(UTC)


def _clear_line() -> None:
    """Clear the current line."""
    try:
        sys.stdout.write("\r\x1b[2K")  # CR + ClearLine
    except Exception:
        cols = shutil.get_terminal_size((120, 20)).columns
        sys.stdout.write("\r" + " " * cols + "\r")
    sys.stdout.flush()


def _clear_previous_line() -> None:
    """Move cursor up one line, then clear that line."""
    sys.stdout.write("\x1b[1A")
    _clear_line()


def _ask(prompt: str) -> str:
    """Show prompt, read answer and go back up and clear the original prompt line."""
    sys.stdout.write(prompt)
    sys.stdout.flush()
    try:
        ans = input().strip().lower()
    except EOFError:
        ans = "n"
    _clear_previous_line()
    return ans


def make_resume_token(**kwargs: Any) -> str:
    """Pack filters & cursor into a base64 token."""
    raw = json.dumps(kwargs, separators=(",", ":"), ensure_ascii=False).encode()
    comp = zlib.compress(raw, level=9)

    return base64.urlsafe_b64encode(comp).decode("ascii").rstrip("=")


def parse_resume_token(token: str) -> dict[str, Any]:
    """Return (params, cursor) from a base64 token."""
    token += "=" * (-len(token) % 4)
    comp = base64.urlsafe_b64decode(token.encode("ascii"))
    raw = zlib.decompress(comp)
    data = json.loads(raw.decode("utf-8"))

    if not isinstance(data, dict) or "cursor" not in data:
        raise ValueError("Invalid cursor.")

    return data


class SearchPage(TypedDict, total=False):
    """A page of search results."""

    hits: list[dict[str, Any]]
    next: dict[str, Any]


def search_logs(
    *,
    token: str | LogToken,
    host: str,
    source: str | None,
    levels: list[str],
    plugins: list[str] | None = None,
    handlers: list[str] | None = None,
    start_time: str | None,
    end_time: str | None,
    size: int,
    search_after: list[Any] | None,
    query: str | None = None,
) -> SearchPage:
    """Fetch logs from Canvas API.

    A ``LogToken`` is asked for its token on each call. On a 401 or 403 a reissuable one (the
    Platform path) mints a fresh token and the request is retried once; the credentials.ini
    path and a plain string token are sent as they are.
    """
    url = plugin_url(host, "/logs")

    params: dict[str, Any] = {
        "size": size,
    }

    if source:
        params["source"] = source
    if levels:
        params["level"] = levels
    if plugins:
        params["plugin"] = plugins
    if handlers:
        params["handler"] = handlers
    if start_time:
        params["start_time"] = start_time
    if end_time:
        params["end_time"] = end_time
    if query:
        params["query"] = query
    if search_after:
        params["search_after"] = json.dumps(search_after)

    def fetch(bearer: str) -> requests.Response:
        return requests.get(
            url,
            headers={"Authorization": f"Bearer {bearer}"},
            params=params,
            timeout=30,
        )

    if isinstance(token, LogToken):
        r = fetch(token.get())
        if r.status_code in REFUSED_TOKEN_STATUSES and token.reissuable:
            r = fetch(token.refresh())
            if r.status_code in REFUSED_TOKEN_STATUSES:
                raise _refused_platform_token(token, _instance_answer(r))
    else:
        r = fetch(token)
    r.raise_for_status()
    data = r.json()

    return {
        "hits": data.get("hits", []),
        "next": data.get("next", {}),
    }


def iter_history(
    *,
    token: str | LogToken,
    host: str,
    source: str | None,
    levels: list[str],
    plugins: list[str] | None = None,
    handlers: list[str] | None = None,
    start_time: str | None,
    end_time: str | None,
    page_size: int,
    limit: int | None,
    query: str | None = None,
    cursor: list[Any] | None = None,
    interactive: bool = False,
    fetch_all: bool = False,
) -> Iterator[dict[str, Any]]:
    """
    Iterate historical hits with search_after paging.

    Rules:
    - Default: fetch one page only.
    - --limit: fetch up to N docs across pages.
    - --interactive: prompt after each page.
    - --all: fetch until exhausted.
    """
    global LAST_CURSOR

    if interactive or fetch_all or limit:
        remaining = limit if limit is not None else float("inf")
    else:
        remaining = page_size

    next_cursor = cursor
    while remaining > 0:
        page = search_logs(
            host=host,
            token=token,
            source=source,
            levels=levels,
            plugins=plugins,
            handlers=handlers,
            start_time=start_time,
            end_time=end_time,
            size=min(page_size, int(remaining) if remaining != float("inf") else page_size),
            search_after=next_cursor,
            query=query,
        )
        hits = page.get("hits", []) if page else []
        next_cursor = (page.get("next") or {}).get("search_after")

        if not hits:
            break

        for h in hits:
            if remaining <= 0:
                break
            yield h
            remaining -= 1

        if remaining <= 0:
            break
        if not next_cursor:
            break

        if interactive:
            try:
                ans = _ask("Load more? [Y/n] ")
            except EOFError:
                ans = "n"
            if ans not in ("", "y", "yes"):
                break
        else:
            # default to a single page when no limit/all/interactive was requested
            if not fetch_all and limit is None:
                break

    LAST_CURSOR = next_cursor


def _on_message(ws: websocket.WebSocket, message: str) -> None:
    message_to_print = message
    try:
        message_json = json.loads(message)
        message_to_print = f"{message_json['timestamp']} | {message_json['message']}"
    except ValueError:
        pass
    print(message_to_print)


def _on_error(ws: websocket.WebSocket, error: str) -> None:
    print(f"Error: {error}")


def _on_close(ws: websocket.WebSocket, close_status_code: int | None, close_msg: str) -> None:
    print(f"Connection closed with status code {close_status_code}: {close_msg}")


def _on_open(ws: websocket.WebSocket) -> None:
    print("Connected to the logging service")


def logs(
    host: str | None = typer.Option(
        callback=get_default_host,
        help="Canvas instance to connect to",
        default=None,
    ),
    since: str | None = typer.Option(
        None,
        help="Lookback window (e.g. '24h', '2h30m'). Mutually exclusive with --start/--end.",
    ),
    start: str | None = typer.Option(None, help="Start time (ISO/RFC3339) or 'now'."),
    end: str | None = typer.Option(
        None, help="End time (ISO/RFC3339) or 'now'. Defaults to now if start is provided."
    ),
    no_follow: bool = typer.Option(
        False, "--no-follow", help="Historical only; do not stream live logs."
    ),
    level: list[str] = typer.Option([], help="Repeatable. --level ERROR --level WARN"),
    source: str | None = typer.Option(None, help="Filter by source/service."),
    plugin: list[str] = typer.Option(
        [], help="Repeatable. --plugin foo --plugin bar. Filters history and the live stream."
    ),
    handler: list[str] = typer.Option(
        [],
        help="Repeatable. Qualified handler name (e.g. my_plugin.handlers.Foo).",
    ),
    page_size: int = typer.Option(DEFAULT_PAGE_SIZE, help="Fetch size per page (historical)."),
    limit: int | None = typer.Option(None, help="Max historical logs to print."),
    all_: bool = typer.Option(False, "--all", help="Fetch all pages until exhausted (historical)."),
    interactive: bool = typer.Option(
        False, "--interactive", help="After each page, prompt to load more."
    ),
    cursor_opt: str | None = typer.Option(
        None, "--cursor", help="Resume token from a previous run."
    ),
) -> None:
    """
    Listens and prints log streams; optionally fetches historical logs first.
    """
    if not host:
        raise typer.BadParameter("Please specify a host or add one to the configuration file")

    token = log_token_source(host)

    if since and (start or end):
        raise typer.BadParameter("--since cannot be combined with --start/--end.")
    if all_ and (limit is not None):
        raise typer.BadParameter("--all cannot be combined with --limit.")
    if cursor_opt and any([since, start, end, level, source, plugin, handler]):
        raise typer.BadParameter(
            "--cursor cannot be combined with filters. "
            "Use --cursor alone to resume, or start a new query without --cursor."
        )
    if limit is not None and limit <= 0:
        raise typer.BadParameter("--limit must be a positive integer.")

    start_time = end_time = None

    if since:
        lte = datetime.now(UTC)
        gte = lte - _parse_duration(since)
        start_time, end_time = gte.isoformat(), lte.isoformat()
    elif start or end:
        gte = _parse_when(start) if start else None  # type: ignore[assignment]
        lte = _parse_when(end) if end else datetime.now(UTC)
        if gte and lte and lte < gte:
            raise typer.BadParameter("End must be after start.")
        start_time = gte.isoformat() if gte else None
        end_time = lte.isoformat() if lte else None

    # Historical first (if any filtering provided)
    historical_requested = bool(since or start or end or no_follow or cursor_opt)
    if historical_requested:
        cursor = {}
        if cursor_opt:
            try:
                cursor = parse_resume_token(cursor_opt)
                if not isinstance(cursor, dict):
                    raise ValueError("cursor must be an encoded base64 JSON dict")
            except Exception as e:
                raise typer.BadParameter(f"Invalid --cursor: {e}") from None

        args = {
            "source": cursor.get("source", source),
            "levels": cursor.get("levels", [lv.upper() for lv in level]),
            "plugins": cursor.get("plugins", plugin),
            "handlers": cursor.get("handlers", handler),
            "start_time": cursor.get("start", start_time),
            "end_time": cursor.get("end", end_time),
            "cursor": cursor.get("cursor"),
        }

        for hit in iter_history(
            token=token,
            host=host,
            fetch_all=all_,
            interactive=interactive and sys.stdout.isatty(),
            page_size=page_size,
            limit=limit,
            **args,
        ):
            print(_format_line(hit))

        # If there may be more, print a resume hint (stateless paging)
        next_cursor = LAST_CURSOR
        if next_cursor and no_follow and (interactive or (limit is None and not all_)):
            cursor_str = make_resume_token(**{**args, "cursor": next_cursor})

            parts = [
                "canvas logs",
                "  --no-follow",
            ]

            if page_size != DEFAULT_PAGE_SIZE:
                parts.append(f"  --page-size {page_size}")
            if limit:
                parts.append(f"  --limit {limit}")

            parts.append(f"  --cursor {cursor_str}")

            cmd = " \\\n  ".join(parts)

            typer.echo(f"\nMore available. To load the next page, run:\n  {cmd}")

    # Live stream unless --no-follow
    if not no_follow:
        if not historical_requested:
            print(
                "Connecting to the log stream. Please be patient as there may be a delay before log messages appear."
            )
        else:
            print()

        try:
            stream_logs(host, token, plugin)
        except KeyboardInterrupt:
            raise typer.Exit(0) from None


def _refused_platform_token(token: LogToken, answer: str = "") -> click.ClickException:
    """Return the error for a Platform-issued log token the instance or Console refused.

    Args:
        token (LogToken): The Platform token source.
        answer (str): What the instance answered, from ``_instance_answer``, or "".

    Returns:
        click.ClickException: The error naming the instance and the way off Platform.
    """
    return click.ClickException(
        f"{token.slug} refused the log token Canvas Platform issued. {answer}"
        f"Run the command again; if it keeps failing, {platform_sign_out()} "
        "to use credentials.ini."
    )


def _console_notice(message: str) -> dict[str, Any] | None:
    """Return ``message`` as one of Console's notices, or None for anything else.

    Before it starts the stream, Console sends JSON notices with a ``severity``: "Connecting to
    the log stream for '<slug>'..." (``info``) while it looks up the instance and checks the
    token, then a refusal such as "No instance named '<slug>' was found." or "Token
    authorization failed." (``error``) before it closes. Everything it sends once the token is
    accepted, from "Connecting to log stream..." on, is a plain string or a log line.

    Args:
        message (str): A message Console sent on the stream.

    Returns:
        dict[str, Any] | None: The notice, for a JSON object carrying ``severity``.
    """
    try:
        body: Any = json.loads(message)
    except ValueError:
        return None
    return body if isinstance(body, dict) and "severity" in body else None


class StreamResult(NamedTuple):
    """How one Console log stream connection ended.

    Attributes:
        opened (bool): Whether Console accepted the token and started the stream.
        close_code (int | None): The close code Console sent, None when the connection ended
            without one, such as on a lost connection or Ctrl-C.
        refusal (str): The last error notice Console sent before starting the stream, or "".
        error (str): The connection error websocket-client reported before the stream started,
            such as a rejected upgrade, or "". Ctrl-C is not an error.
        interrupted (bool): Whether the connection ended on Ctrl-C.
        last_received (datetime | None): When the last message, ping, or pong arrived.
    """

    opened: bool
    close_code: int | None
    refusal: str
    error: str
    interrupted: bool
    last_received: datetime | None


def _stream_once(url: str, on_start: Callable[[], None]) -> StreamResult:
    """Print one Console log stream connection until it closes.

    The stream counts as opened once Console sends a message other than one of its notices.
    websocket-client fires ``on_open`` at the HTTP upgrade, before Console checks the token, so
    a refused token also reaches ``on_open``. websocket-client catches Ctrl-C inside
    ``run_forever`` and reports it only by handing the ``KeyboardInterrupt`` to ``on_error``.

    Args:
        url (str): The stream URL, carrying the token.
        on_start (Callable[[], None]): Called once, when the stream opens.

    Returns:
        StreamResult: Whether the stream started, the close code, and Console's refusal.
    """
    opened: list[bool] = [False]
    close_code: list[int | None] = [None]
    refusal: list[str] = [""]
    error: list[str] = [""]
    interrupted: list[bool] = [False]
    last_received: list[datetime | None] = [None]

    def on_error(ws: websocket.WebSocket, exc: BaseException) -> None:
        if isinstance(exc, KeyboardInterrupt):
            interrupted[0] = True
        elif not opened[0] and isinstance(exc, Exception):
            error[0] = str(exc)
        _on_error(ws, str(exc))

    def on_message(ws: websocket.WebSocket, message: str) -> None:
        last_received[0] = datetime.now(UTC)
        notice: dict[str, Any] | None = _console_notice(message)
        if notice is None and not opened[0]:
            opened[0] = True
            on_start()
        elif notice is not None and not opened[0] and notice.get("severity") == "error":
            refusal[0] = str(notice.get("message", ""))
        with _OUTPUT_LOCK:
            _on_message(ws, message)

    def on_control_frame(ws: websocket.WebSocket, data: bytes) -> None:
        last_received[0] = datetime.now(UTC)

    def on_close(ws: websocket.WebSocket, close_status_code: int | None, close_msg: str) -> None:
        close_code[0] = close_status_code
        _on_close(ws, close_status_code, close_msg)

    ws = websocket.WebSocketApp(
        url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_ping=on_control_frame,
        on_pong=on_control_frame,
    )
    ws.on_open = _on_open
    ws.run_forever(ping_interval=PING_INTERVAL_SECONDS, ping_timeout=PING_TIMEOUT_SECONDS)
    return StreamResult(
        opened[0], close_code[0], refusal[0], error[0], interrupted[0], last_received[0]
    )


def _notice(message: str) -> None:
    """Print ``message`` to stderr as a labeled CLI notice."""
    typer.echo(f"{notice_label()} {message}", err=True)


def _gap_window(dropped: datetime, resumed: datetime) -> tuple[str, str]:
    """Return a stream gap's start and end, widened by GAP_MARGIN_SECONDS on each side.

    Args:
        dropped (datetime): When the dropped stream last received anything.
        resumed (datetime): When the reconnected stream started.

    Returns:
        tuple[str, str]: The start and end as ISO timestamps.
    """
    margin: timedelta = timedelta(seconds=GAP_MARGIN_SECONDS)
    start: datetime = dropped - margin
    end: datetime = resumed + margin
    return start.isoformat(timespec="seconds"), end.isoformat(timespec="seconds")


def _gap_notice(slug: str, plugins: list[str], dropped: datetime, resumed: datetime) -> str:
    """Return the line naming a stream gap and the history command that prints it.

    Args:
        slug (str): The instance, as ``--host`` takes it.
        plugins (list[str]): The stream's ``--plugin`` filter.
        dropped (datetime): When the dropped stream last received anything.
        resumed (datetime): When the reconnected stream started.

    Returns:
        str: The notice, with ``--start`` and ``--end`` from ``_gap_window``.
    """
    start, end = _gap_window(dropped, resumed)
    command: list[str] = ["canvas", "logs", "--host", slug, "--start", start, "--end", end]
    command += ["--no-follow", "--all"]
    for plugin in plugins:
        command += ["--plugin", plugin]
    return (
        f"The log stream dropped after {start} and resumed at "
        f"{resumed.isoformat(timespec='seconds')}. To print the lines sent in between, run: "
        f"{shlex.join(command)}"
    )


def _backfill(
    host: str,
    token: LogToken,
    plugins: list[str],
    dropped: datetime,
    resumed: datetime,
    cancelled: threading.Event,
) -> None:
    """Print a stream gap's lines from history, oldest first, formatted as history lines are.

    Runs on its own thread, because websocket-client calls ``on_start`` on the thread that
    reads pongs. A failed fetch prints the gap's history command instead. Nothing prints once
    ``cancelled`` is set, which ``stream_logs`` does under ``_OUTPUT_LOCK`` before it returns.

    Args:
        host (str): The Canvas instance URL.
        token (LogToken): The token source.
        plugins (list[str]): The stream's ``--plugin`` filter.
        dropped (datetime): When the dropped stream last received anything.
        resumed (datetime): When the reconnected stream started.
        cancelled (threading.Event): Set when the run ends.
    """
    if cancelled.wait(BACKFILL_DELAY_SECONDS):
        return
    start, end = _gap_window(dropped, resumed)
    hits: list[dict[str, Any]] | None
    try:
        hits = list(
            iter_history(
                token=token,
                host=host,
                source=None,
                levels=[],
                plugins=plugins,
                start_time=start,
                end_time=end,
                page_size=DEFAULT_PAGE_SIZE,
                limit=None,
                fetch_all=True,
            )
        )
    except (requests.RequestException, click.ClickException):
        hits = None
    with _OUTPUT_LOCK:
        if cancelled.is_set():
            return
        if hits is None:
            _notice(_gap_notice(token.slug, plugins, dropped, resumed))
            return
        sys.stdout.flush()
        _notice(
            f"Printing the {len(hits)} lines sent while the log stream was down, {start} to {end}."
        )
        # History answers newest first.
        for hit in reversed(hits):
            print(_format_line(hit))
        sys.stdout.flush()


def stream_logs(host: str, token: LogToken, plugins: list[str] | None = None) -> None:
    """Print the instance's live log stream from Console until Ctrl-C.

    A first connection Console refuses or closes before starting the stream, or that fails,
    ends the run quoting Console's notice, the close code, or the failure. Once a stream has
    started, any end but Ctrl-C reconnects after a jittered wait that doubles from 1s to 60s
    and resets after a stream open 60s. Each Platform reconnect mints a fresh token, which
    re-checks access and replaces one Console closed with ``STREAM_TOKEN_INACTIVE``; a 4401
    on a credentials.ini stream ends the run. Only a token refusal ends a reconnect; other
    failures retry. Console cannot replay a gap, so ``_backfill`` prints it from history.

    Args:
        host (str): The Canvas instance URL.
        token (LogToken): The token source.
        plugins (list[str] | None): Plugins whose lines Console sends; none sends every line.

    Raises:
        click.ClickException: The first connection failed, a token was refused, or Platform
            refused a fresh token.
    """
    # Resolve the instance name from the Canvas host URL (e.g., extract
    # 'example' from 'https://example.canvasmedical.com/')
    instance = instance_slug(host) or cast(str, urlparse(host).hostname)
    plugin_query: str = urlencode([("plugin", p) for p in plugins or []])
    streamed: bool = False
    dropped_at: datetime | None = None
    started_at: list[float] = [0.0]
    delay: float = RECONNECT_FIRST_DELAY_SECONDS
    cancelled: threading.Event = threading.Event()

    def on_start() -> None:
        started_at[0] = time.monotonic()
        if dropped_at is not None:
            gap: tuple[datetime, datetime] = (dropped_at, datetime.now(UTC))
            threading.Thread(
                target=lambda: _backfill(host, token, plugins or [], *gap, cancelled),
                name="canvas-logs-backfill",
                daemon=True,
            ).start()

    try:
        while True:
            if streamed:
                pause: float = delay / 2 + random.uniform(0, delay / 2)
                _notice(f"Reconnecting to the log stream in {pause:.1f}s.")
                time.sleep(pause)
                delay = min(delay * 2, RECONNECT_MAX_DELAY_SECONDS)
                try:
                    bearer: str = token.refresh() if token.reissuable else token.get()
                except click.ClickException as error:
                    unreachable: bool = isinstance(error.__cause__, requests.RequestException)
                    unavailable: bool = (
                        isinstance(error, PlatformError)
                        and error.status is not None
                        and error.status >= requests.codes.internal_server_error
                    )
                    if not (unreachable or unavailable):
                        raise
                    _notice(error.message)
                    continue
            else:
                bearer = token.get()
            url = f"wss://logs.console.canvasmedical.com/{instance}?token={bearer}"
            result: StreamResult = _stream_once(
                f"{url}&{plugin_query}" if plugin_query else url, on_start
            )
            if result.interrupted:
                return
            if (
                not result.opened
                and (result.close_code is not None or result.error)
                and (not streamed or result.refusal == STREAM_TOKEN_REFUSAL)
            ):
                if not result.refusal and result.close_code is None:
                    raise click.ClickException(
                        f"Could not reach Console's log stream for {token.slug}: {result.error}. "
                        "Run the command again."
                    )
                if not result.refusal:
                    raise click.ClickException(
                        f"Console closed the log stream for {token.slug} before starting it "
                        f"(close code {result.close_code}). Run the command again."
                    )
                answer: str = f"Console answered: {result.refusal} "
                if token.reissuable and result.refusal == STREAM_TOKEN_REFUSAL:
                    raise _refused_platform_token(token, answer)
                raise click.ClickException(
                    f"Console refused the log stream for {token.slug}. {answer}".rstrip()
                )
            if result.opened:
                streamed = True
                dropped_at = result.last_received
                if time.monotonic() - started_at[0] >= HEALTHY_STREAM_SECONDS:
                    delay = RECONNECT_FIRST_DELAY_SECONDS
                if result.close_code == STREAM_TOKEN_INACTIVE and not token.reissuable:
                    return
            elif not streamed:
                return
    finally:
        with _OUTPUT_LOCK:
            cancelled.set()
