from enum import Enum
from typing import Any, Self
from pydantic import Field, model_validator, BaseModel

from canvas_sdk.effects.base import EffectType, _BaseEffect


class PatientPortalWidgetConfiguration(_BaseEffect):
    """
    An Effect that will decide which widget items appear on the patient portal landing page.
    """

    class Meta:
        effect_type = EffectType.SHOW_PATIENT_PORTAL_WIDGET_ITEMS

    class ComponentType(Enum):
        APPOINTMENTS = "appointments"
        MESSAGING = "messaging"

    class SizeType(Enum):
        FULL = "full"
        TWO_THIRDS = "two_thirds"
        ONE_THIRD = "one_third"

    class Payload(BaseModel):
        url: str | None = None
        content: str | None = None
        component: "PatientPortalWidgetConfiguration.ComponentType" = None
        size: "PatientPortalWidgetConfiguration.SizeType" = Field(default="PatientPortalWidgetConfiguration.SizeType.FULL")

        @model_validator(mode="after")
        def check_mutually_exclusive_fields(self) -> Self:
            """Check that content and component are mutually exclusive."""
            if self.content is not None and self.component is not None:
                raise ValueError("'content' and 'component' are mutually exclusive")

            return self

        @model_validator(mode="after")
        def check_exclusive_fields(self) -> Self:
            """Check that content and component are mutually exclusive."""
            if self.content is None and self.component is None:
                raise ValueError("one of 'content' or 'component' is required")

            return self

    items: list[Payload] = Field(min_length=1)

    @property
    def values(self) -> dict[str, Any]:
        """The PatientPortalWidgetConfiguration's values."""
        return {"items": [
            {
                "content": i.content,
                "component": i.component.value if i.component else None,
                "size": i.size.value
            }
            for i in self.items
        ]}

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}
