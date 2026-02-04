from enum import Enum
from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect


class SetDefaultHomepage(_BaseEffect):
    """
    An Effect that will set the default homepage for a user.
    """

    class Meta:
        effect_type = EffectType.HOMEPAGE_CONFIGURATION_RESULT

    class Pages(Enum):
        PATIENTS = "/patients"
        SCHEDULE = "/schedule"
        REVENUE = "/revenue"
        CAMPAIGNS = "/campaigns"
        DATA_INTEGRATION = "/data-integration"

    page: Pages | None = None
    application_id: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The user's id."""
        return {
            "page": self.page.value if self.page else None,
            "application_id": self.application_id,
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.page is None and self.application_id is None:
            errors.append(
                self._create_error_detail(
                    "value",
                    "Either page or application_id must be provided",
                    self.page,
                )
            )

        if self.page not in self.Pages:
            errors.append(
                self._create_error_detail(
                    "value",
                    "Url is not valid",
                    self.page,
                )
            )

        return errors


__exports__ = ("SetDefaultHomepage",)
