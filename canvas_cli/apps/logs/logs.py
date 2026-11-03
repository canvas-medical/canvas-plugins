from __future__ import annotations

import base64
import json
import re
import shutil
import sys
import time
import zlib
from collections.abc import Callable, Iterator
from datetime import UTC, datetime, timedelta
from typing import Any, TypedDict, cast
from urllib.parse import urlparse

import click
import requests
import typer
import websocket

from canvas_cli.apps.auth.utils import get_default_host, get_or_request_api_token, instance_slug
from canvas_cli.apps.platform import auth as platform_auth
from canvas_cli.apps.platform.client import PlatformClient, PlatformError
from canvas_cli.apps.plugin.plugin import plugin_url
from canvas_cli.utils.platform_notice import print_credentials_ini_deprecation

# Seconds before a minted token's expiry at which it is replaced.
EXPIRY_MARGIN_SECONDS = 30
# The instance answers an expired or revoked token with 403, since its logs endpoint tries
# session authentication first and so sends no WWW-Authenticate challenge. 401 is kept for a
# proxy or release that does send one.
REFUSED_TOKEN_STATUSES: tuple[int, ...] = (requests.codes.unauthorized, requests.codes.forbidden)
# The close code Console sends when it re-checks a Platform-issued token and finds it inactive.
STREAM_TOKEN_INACTIVE = 4401


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


def _platform_sign_out() -> str:
    """Return how to stop using Canvas Platform for logs, for the credential in force.

    Returns:
        str: ``unset CANVAS_PLATFORM_TOKEN`` under a service account token, which ``canvas
            logout`` leaves in force, and "sign out with `canvas logout`" otherwise.
    """
    if platform_auth.service_token() is not None:
        return f"unset {platform_auth.SERVICE_TOKEN_ENV}"
    return "sign out with `canvas logout`"


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
    slug: str | None = instance_slug(host)
    platform: str = platform_auth.resolve_platform_url()
    if slug is not None and platform_auth.stored_tokens(platform) is not None:
        client = PlatformClient(platform)
        row = next((r for r in client.instances() if r.get("slug") == slug), None)
        if row is None or not row.get("managed"):
            cause: str = (
                f"{slug} is not one of your instances on Canvas Platform."
                if row is None
                else f"Canvas Platform does not manage {slug}."
            )
            raise click.ClickException(
                f"{cause} While you are signed in to Canvas Platform, instance commands go "
                f"through it. To read {slug}'s logs with credentials.ini, {_platform_sign_out()}."
            )

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

    print_credentials_ini_deprecation("logs")
    return LogToken(
        slug or host,
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
    re.X,
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
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
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
    plugin: list[str] = typer.Option([], help="Repeatable. --plugin foo --plugin bar."),
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
            print("")

        try:
            stream_logs(host, token)
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
        f"Run the command again; if it keeps failing, {_platform_sign_out()} "
        "to use credentials.ini."
    )


def _is_console_error(message: str) -> bool:
    """Return whether ``message`` is one of Console's error notices.

    Console sends a refusal, such as "Token authorization failed.", as JSON with ``severity``
    ``error`` before it closes the stream. Everything it sends once the token is accepted, from
    "Connecting to log stream..." on, is a plain string or a log line.

    Args:
        message (str): A message Console sent on the stream.

    Returns:
        bool: True for a JSON object whose ``severity`` is ``error``.
    """
    try:
        body: Any = json.loads(message)
    except ValueError:
        return False
    return isinstance(body, dict) and body.get("severity") == "error"


def _stream_once(url: str) -> tuple[bool, int | None]:
    """Print one Console log stream connection until it closes.

    The stream counts as opened once Console sends a message other than an error notice.
    websocket-client fires ``on_open`` at the HTTP upgrade, before Console checks the token, so
    a refused token also reaches ``on_open``.

    Args:
        url (str): The stream URL, carrying the token.

    Returns:
        tuple[bool, int | None]: Whether Console accepted the token and started the stream, and
            the close code Console sent (None when the connection ended without one, such as on
            Ctrl-C).
    """
    opened: list[bool] = [False]
    close_code: list[int | None] = [None]

    def on_message(ws: websocket.WebSocket, message: str) -> None:
        if not _is_console_error(message):
            opened[0] = True
        _on_message(ws, message)

    def on_close(ws: websocket.WebSocket, close_status_code: int | None, close_msg: str) -> None:
        close_code[0] = close_status_code
        _on_close(ws, close_status_code, close_msg)

    ws = websocket.WebSocketApp(
        url,
        on_message=on_message,
        on_error=_on_error,
        on_close=on_close,
    )
    ws.on_open = _on_open
    ws.run_forever()
    return opened[0], close_code[0]


def stream_logs(host: str, token: LogToken) -> None:
    """Print the instance's live log stream from Console until it closes.

    Console re-checks a Platform-issued token while the stream is open and closes the stream
    with ``STREAM_TOKEN_INACTIVE`` once the token is inactive. A Platform stream then mints a
    fresh token through Platform, which re-checks the person's access, and reconnects. Any
    other close ends the stream, as does a 4401 on a credentials.ini stream. A Platform stream
    that Console closes before starting it, as it does after "Token authorization failed.", is
    a refused token.

    Args:
        host (str): The Canvas instance URL.
        token (LogToken): The token source.

    Raises:
        click.ClickException: Console closed a Platform stream before starting it.
    """
    # Resolve the instance name from the Canvas host URL (e.g., extract
    # 'example' from 'https://example.canvasmedical.com/')
    instance = instance_slug(host) or cast(str, urlparse(host).hostname)
    while True:
        opened, close_code = _stream_once(
            f"wss://logs.console.canvasmedical.com/{instance}?token={token.get()}"
        )
        if token.reissuable and not opened and close_code is not None:
            # Also stops a re-minted token Console refuses from reconnecting in a loop.
            raise _refused_platform_token(token)
        if close_code != STREAM_TOKEN_INACTIVE or not token.reissuable:
            return
        print("Reconnecting with a fresh log token from Canvas Platform.", file=sys.stderr)
        token.refresh()
