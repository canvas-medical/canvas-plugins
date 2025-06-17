from enum import StrEnum
from typing import Any, Self

from pydantic import model_validator
from pydantic_core import InitErrorDetails

from canvas_sdk.effects import EffectType, _BaseEffect


class PortalWidget(_BaseEffect):
    """An Effect that will launch a modal."""

    class Meta:
        effect_type = EffectType.PORTAL_WIDGET

    class Component(StrEnum):
        APPOINTMENTS = "appointments"
        MESSAGING = "messaging"

    class Size(StrEnum):
        EXPANDED = "expanded"
        MEDIUM = "medium"
        COMPACT = "compact"

    url: str | None = None
    content: str | None = None
    component: Component | None = None
    priority: int = 100
    size: Size = Size.EXPANDED

    @property
    def values(self) -> dict[str, Any]:
        """The PortalWidget values."""
        return {
            "url": self.url,
            "content": self.content,
            "component": self.component,
            "size": self.size,
            "priority": self.priority,
        }

    @model_validator(mode="after")
    def check_mutually_exclusive_fields(self) -> Self:
        """Check that content and component are mutually exclusive."""
        if self.content is not None and self.component is not None:
            raise ValueError("'content' and 'component' are mutually exclusive")

        if self.content is not None and self.url is not None:
            raise ValueError("'content' and 'url' are mutually exclusive")

        if self.url is not None and self.component is not None:
            raise ValueError("'url' and 'component' are mutually exclusive")

        return self

    @model_validator(mode="after")
    def check_exclusive_fields(self) -> Self:
        """Check that at least one of mutually exclusive field is set."""
        if self.content is None and self.component is None and self.url is None:
            raise ValueError("one of 'content', 'component', 'url' is required")

        return self

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.component is not None and self.size != PortalWidget.Size.EXPANDED:
            errors.append(
                self._create_error_detail(
                    "value",
                    "Component only supports 'expanded' size",
                    self.size,
                )
            )

        return errors


__exports__ = ("PortalWidget",)
