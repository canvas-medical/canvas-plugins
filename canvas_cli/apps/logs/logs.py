from __future__ import annotations

import base64
import json
import re
import shutil
import sys
import zlib
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import Any, TypedDict, cast
from urllib.parse import urlparse

import requests
import typer
import websocket

from canvas_cli.apps.auth.utils import get_default_host, get_or_request_api_token
from canvas_cli.apps.plugin.plugin import plugin_url

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
    token: str,
    host: str,
    source: str | None,
    levels: list[str],
    start_time: str | None,
    end_time: str | None,
    size: int,
    search_after: list[Any] | None,
    query: str | None = None,
) -> SearchPage:
    """Fetch logs from Canvas API."""
    url = plugin_url(host, "/logs")

    params: dict[str, Any] = {
        "size": size,
    }

    if source:
        params["source"] = source
    if levels:
        params["level"] = levels
    if start_time:
        params["start_time"] = start_time
    if end_time:
        params["end_time"] = end_time
    if query:
        params["query"] = query
    if search_after:
        params["search_after"] = json.dumps(search_after)

    r = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()

    return {
        "hits": data.get("hits", []),
        "next": data.get("next", {}),
    }


def iter_history(
    *,
    token: str,
    host: str,
    source: str | None,
    levels: list[str],
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


def _on_close(ws: websocket.WebSocket, close_status_code: str, close_msg: str) -> None:
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

    token = get_or_request_api_token(host)

    if since and (start or end):
        raise typer.BadParameter("--since cannot be combined with --start/--end.")
    if all_ and (limit is not None):
        raise typer.BadParameter("--all cannot be combined with --limit.")
    if cursor_opt and any([since, start, end, level, source]):
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

        # Resolve the instance name from the Canvas host URL (e.g., extract
        # 'example' from 'https://example.canvasmedical.com/')
        hostname = cast(str, urlparse(host).hostname)
        instance = hostname.removesuffix(".canvasmedical.com")
        websocket_uri = f"wss://logs.console.canvasmedical.com/{instance}?token={token}"

        try:
            ws = websocket.WebSocketApp(
                websocket_uri,
                on_message=_on_message,
                on_error=_on_error,
                on_close=_on_close,
            )
            ws.on_open = _on_open
            ws.run_forever()
        except KeyboardInterrupt:
            raise typer.Exit(0) from None
