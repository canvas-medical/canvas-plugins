from typing import Optional
from urllib.parse import urlparse

import typer
import websocket

from canvas_cli.apps.auth.utils import get_default_host, get_or_request_api_token
from canvas_cli.utils.print import print


def _on_message(ws: websocket.WebSocketApp, message: str) -> None:
    print.json(message)


def _on_error(ws: websocket.WebSocketApp, error: str) -> None:
    print.json(f"Error: {error}", success=False)


def _on_close(ws: websocket.WebSocketApp, close_status_code: str, close_msg: str) -> None:
    print.json(f"Connection closed with status code {close_status_code}: {close_msg}")


def _on_open(ws: websocket.WebSocketApp) -> None:
    print.json("Connected to the logging service")


def logs(
    host: Optional[str] = typer.Option(
        callback=get_default_host, help="Canvas instance to connect to", default=None
    )
) -> None:
    """Listens and prints log streams from the instance."""
    if not host:
        raise typer.BadParameter("Please specify a host or add one to the configuration file")

    token = get_or_request_api_token(host)

    # Resolve the instance name from the Canvas host URL (e.g., extract
    # 'example' from 'https://example.canvasmedical.com/')
    hostname = urlparse(host).hostname
    instance = hostname.removesuffix(".canvasmedical.com")

    print.json(
        f"Connecting to the log stream. Please be patient as there may be a delay before log messages appear."
    )
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
        raise typer.Exit(0)
