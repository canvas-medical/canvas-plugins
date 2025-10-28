from abc import ABC
from typing import Any, Literal
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.effects import EffectType, _BaseEffect
from canvas_sdk.v1.data import PracticeLocation


class BaseFaxEffect(_BaseEffect, ABC):
    """Base class for fax effects."""

    class Meta:
        effect_type = EffectType.UNKNOWN_EFFECT

    recipient_name: str
    recipient_fax_number: str
    include_coversheet: bool = False
    subject: str | None = None
    comment: str | None = None
    location_id: str | UUID | None = None

    def _get_error_details(self, method: Literal["apply"]) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.include_coversheet:
            if not self.subject:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "subject is required when include_coversheet is True",
                        self.subject,
                    )
                )
            if not self.comment:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "comment is required when include_coversheet is True",
                        self.comment,
                    )
                )
            if self.location_id:
                if not PracticeLocation.objects.filter(id=self.location_id).exists():
                    errors.append(
                        self._create_error_detail(
                            "value",
                            f"Practice Location {self.location_id} does not exist",
                            self.location_id,
                        )
                    )
            else:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "location_id is required when include_coversheet is True",
                        self.location_id,
                    )
                )

        return errors

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the fax effect."""
        return {
            "recipient_name": self.recipient_name,
            "recipient_fax_number": self.recipient_fax_number,
            "include_coversheet": self.include_coversheet,
            "subject": self.subject,
            "comment": self.comment,
            "location_id": str(self.location_id) if self.location_id else None,
        }


__exports__ = ()
