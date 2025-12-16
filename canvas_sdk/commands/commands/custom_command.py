from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import CommandConfiguration, _BaseCommand
from canvas_sdk.commands.constants import CommandChartSection


class CustomCommand(_BaseCommand):
    """A class for managing a custom command within a specific note."""

    class Meta:
        key = "customCommand"

    content: str | None = None
    print_content: str | None = None

    def _get_error_details(self, method: str) -> list[InitErrorDetails]:
        """Get error details for the custom command."""
        errors = super()._get_error_details(method)

        if method == "originate" and not self.content:
            errors.append(
                self._create_error_detail(
                    "value",
                    "Content must be provided for a custom command.",
                    self.content,
                )
            )

        return errors

    def configure(
        self, label: str, section: CommandChartSection, **kwargs: Any
    ) -> CommandConfiguration:
        """Configure the custom command label and section."""
        return {"key": self.Meta.key, "label": label, "section": section.value}


__exports__ = ("CustomCommand",)
