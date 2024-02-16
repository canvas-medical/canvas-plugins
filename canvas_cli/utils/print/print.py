import json
from builtins import print as builtin_print
from typing import Any

from requests import Response
from rich import print as rich_print


class Printer:
    """Class to override Python's default print with json and Requests.response capabilities."""

    def __call__(self, *args: Any) -> None:
        """Default printing."""
        self._default_print(*args)

    @staticmethod
    def response(response: Response, success: bool = True) -> None:
        """Print a response object by getting its json or text response."""
        try:
            message = response.json()
        except json.JSONDecodeError:
            message = response.text

        Printer.json(message=message, success=success, status_code=response.status_code)

    @staticmethod
    def json(message: str | list[str] | dict | None, success: bool = True, **kwargs: Any) -> None:
        """Print a message in json format regardless of the input."""
        status = {"success": success}
        if message:
            try:
                json_message = json.loads(message)
            except (json.JSONDecodeError, TypeError):
                json_message = message

            status.update({"message": json_message})
        for key, value in kwargs.items():
            status.update({key: value})

        Printer._default_print(json.dumps(status))

    @staticmethod
    def verbose(*args: Any) -> None:
        """Print text only if `verbose` is set in context."""
        from canvas_cli.utils.context import context

        if context.verbose:
            Printer._default_print(*args)

    @staticmethod
    def _default_print(*args: Any) -> None:
        from canvas_cli.utils.context import context

        if context.no_ansi:
            builtin_print(*args)
        else:
            rich_print(*args)


print = Printer()
