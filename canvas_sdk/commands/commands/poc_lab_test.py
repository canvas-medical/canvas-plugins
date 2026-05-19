from dataclasses import asdict, dataclass
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.v1.data.lab import LabReportTemplate


@dataclass
class TestValue:
    """A single POC lab test result, identified by its template field label."""

    __test__ = False  # opt out of pytest collection

    label: str
    value: str

    def to_dict(self) -> dict[str, str]:
        """Return the test value as a plain dict for the effect payload."""
        return asdict(self)


class POCLabTestCommand(BaseCommand):
    """A class for managing a Point-of-Care (POC) Lab Test command within a specific note."""

    class Meta:
        key = "pocLabTest"

    template: UUID | None = Field(default=None, strict=False)
    indications: list[str] = Field(default_factory=list)
    test_values: list[TestValue] = Field(default_factory=list)
    remarks: str | None = Field(default=None, max_length=512)

    @property
    def values(self) -> dict[str, Any]:
        """Override base ``values`` so test_values is serialized as a list of dicts."""
        result = super().values
        if "test_values" in result:
            result["test_values"] = [tv.to_dict() for tv in self.test_values]
        return result

    def set_test_value(self, label: str, value: str) -> None:
        """Add or replace a test value by template field label.

        Reassigns ``test_values`` (rather than mutating in place) so the field
        is properly marked dirty for the next effect emission. If a value with
        the same label already exists, it is replaced.
        """
        self.test_values = [
            *(tv for tv in self.test_values if tv.label != label),
            TestValue(label=label, value=value),
        ]

    def _get_error_details(self, method: str) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        template_obj = None
        if self.template:
            template_obj = (
                LabReportTemplate.objects.filter(id=self.template, poc=True, active=True)
                .prefetch_related("fields")
                .first()
            )
            if not template_obj:
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Active POC LabReportTemplate with id {self.template} not found",
                        self.template,
                    )
                )

        if self.test_values:
            if not template_obj and method == "originate":
                errors.append(
                    self._create_error_detail(
                        "value",
                        "template is required when test_values are provided",
                        self.test_values,
                    )
                )

            if template_obj:
                valid_labels = {field.label.lower() for field in template_obj.fields.all()}
                unknown_labels = [
                    tv.label for tv in self.test_values if tv.label.lower() not in valid_labels
                ]
                if unknown_labels:
                    errors.append(
                        self._create_error_detail(
                            "value",
                            f"test_values labels {unknown_labels} are not fields of template '{template_obj.name}'",
                            self.test_values,
                        )
                    )

        return errors


__exports__ = ("POCLabTestCommand", "TestValue")
