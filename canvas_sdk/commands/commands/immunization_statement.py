from datetime import date

from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand as BaseCommand


class ImmunizationStatementCommand(BaseCommand):
    """A class for managing an ImmunizationStatement command within a specific note."""

    class Meta:
        key = "immunizationStatement"

    cpt_code: str
    cvx_code: str
    approximate_date: date | None = None
    comments: str | None = None

    def _get_error_details(self, method: str) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.comments and len(self.comments) > 255:
            errors.append(
                self._create_error_detail(
                    "comments", "Comments must be 255 characters or less.", self.comments
                )
            )

        return errors


__exports__ = ("ImmunizationStatementCommand",)
