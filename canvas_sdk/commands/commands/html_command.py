from typing import Any

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.commands.constants import CommandChartSection


class HtmlCommand(BaseCommand):
    """A class for managing an HTML command within a specific note."""

    class Meta:
        key = "htmlCommand"

    content: str | None = None

    def configure(self, label: str, section: CommandChartSection, **kwargs: Any) -> dict[str, Any]:
        """Configure the HTML command label and section."""
        return {"key": self.Meta.key, "label": label, "section": section.value}


__exports__ = ("HtmlCommand",)
