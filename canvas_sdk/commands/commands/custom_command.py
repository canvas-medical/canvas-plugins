from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand


class CustomCommand(_BaseCommand):
    """A class for managing a custom command within a specific note."""

    class Meta:
        key = "customCommand"

    schema_key: str | None = None
    content: str | None = None
    print_content: str | None = None

    def _get_error_details(self, method: str) -> list[InitErrorDetails]:
        """Get error details for the custom command."""
        errors = super()._get_error_details(method)

        if method == "originate":
            if not self.content:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Content must be provided for a custom command.",
                        self.content,
                    )
                )
            if not self.schema_key:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Schema key must be provided for a custom command.",
                        self.schema_key,
                    )
                )
        return errors


__exports__ = ("CustomCommand",)
