from datetime import date
from typing import Self

from pydantic import model_validator
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.commands.constants import CodeSystems, Coding


class ImmunizationStatementCommand(BaseCommand):
    """A class for managing an ImmunizationStatement command within a specific note."""

    class Meta:
        key = "immunizationStatement"

    cpt_code: str | Coding | None = None
    cvx_code: str | Coding | None = None
    unstructured: Coding | None = None
    approximate_date: date | None = None
    comments: str | None = None

    def _has_value(self, value: str | Coding | None) -> bool:
        """Check if a value is set."""
        if value is None:
            return False
        if isinstance(value, str):
            return value.strip() != ""
        # For Coding objects (dicts), check if it exists
        return True

    @model_validator(mode="after")
    def check_needed_together_fields(self) -> Self:
        """Check that both 'cpt_code' and 'cvx_code' are set if one is provided."""
        has_cpt_code = self._has_value(self.cpt_code)
        has_cvx_code = self._has_value(self.cvx_code)

        if has_cpt_code ^ has_cvx_code:
            raise ValueError(
                "Both cpt_code and cvx_code must be provided if one is specified and cannot be empty."
            )

        return self

    def _get_error_details(self, method: str) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.unstructured and (self.cpt_code or self.cvx_code):
            message = "Unstructured codes cannot be used with CPT or CVX codes."
            errors.append(self._create_error_detail("value", message, self.cpt_code))

        if isinstance(self.cpt_code, dict) and self.cpt_code["system"] != CodeSystems.CPT:
            message = f"The 'cpt_code.system' field must be '{CodeSystems.CPT}'"
            errors.append(self._create_error_detail("value", message, self.cpt_code))

        if isinstance(self.cvx_code, dict) and self.cvx_code["system"] != CodeSystems.CVX:
            message = f"The 'cvx_code.system' field must be '{CodeSystems.CVX}'"
            errors.append(self._create_error_detail("value", message, self.cvx_code))

        if self.unstructured and self.unstructured["system"] != CodeSystems.UNSTRUCTURED:
            message = f"The 'unstructured.system' field must be '{CodeSystems.UNSTRUCTURED}'"
            errors.append(self._create_error_detail("value", message, self.unstructured))

        if self.comments and len(self.comments) > 255:
            errors.append(
                self._create_error_detail(
                    "comments", "Comments must be 255 characters or less.", self.comments
                )
            )

        return errors


__exports__ = ("ImmunizationStatementCommand",)
