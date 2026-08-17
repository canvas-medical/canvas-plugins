from typing import Any

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand as BaseCommand

_TEXT_MAX_LENGTH = 2048


class UpdateDiagnosisCommand(BaseCommand):
    """A class for managing an Update Diagnosis command within a specific note."""

    class Meta:
        key = "updateDiagnosis"

    condition_code: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "condition"}
    )
    new_condition_code: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "new_condition"}
    )
    background: str | None = None
    narrative: str | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Check the text fields against the length the record accepts.

        Checked when an effect is built rather than declared on the fields: `validate_assignment` is
        on, so a bound on the field raises at the line that assigns it, part-way through a handler.
        A caller assembling this text from a longer source would crash where it is set instead of
        being told when the command is written.
        """
        errors = super()._get_error_details(method)

        for name in ("background", "narrative"):
            value = getattr(self, name)
            if value is not None and len(value) > _TEXT_MAX_LENGTH:
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"{name} cannot be longer than {_TEXT_MAX_LENGTH} characters",
                        value,
                    )
                )

        return errors


__exports__ = ("UpdateDiagnosisCommand",)
