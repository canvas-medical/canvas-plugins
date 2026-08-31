from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.commands.base import _OptionalId
from canvas_sdk.v1.data import Condition


class ResolveConditionCommand(BaseCommand):
    """A class for managing a ResolveCondition command within a specific note."""

    class Meta:
        key = "resolveCondition"

    condition_id: _OptionalId = Field(
        default=None, json_schema_extra={"commands_api_name": "condition"}
    )
    show_in_condition_list: bool = False
    rationale: str | None = Field(max_length=1024, default=None)

    def _get_error_details(self, method: str) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.condition_id is None:
            return errors

        condition_patient_id = (
            Condition.objects.active()
            .filter(id=self.condition_id)
            .values_list("patient__id", flat=True)
            .first()
        )

        if condition_patient_id is None or not self._is_target_patient(condition_patient_id):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Condition {self.condition_id} does not belong to this command's patient",
                    self.condition_id,
                )
            )

        return errors


__exports__ = ("ResolveConditionCommand",)
