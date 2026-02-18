from enum import StrEnum
from typing import Any

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data import Application


class DefaultHomepageEffect(_BaseEffect):
    """
    An Effect that will set the default homepage for a user.
    """

    class Meta:
        effect_type = EffectType.HOMEPAGE_CONFIGURATION

    class Pages(StrEnum):
        PATIENTS = "/patients"
        SCHEDULE = "/schedule"
        REVENUE = "/revenue"
        CAMPAIGNS = "/campaigns"
        DATA_INTEGRATION = "/data-integration"

    page: Pages | None = Field(default=None, strict=False)
    application_identifier: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Homepage configuration values."""
        return {
            "page": self.page.value if self.page else None,
            "application_identifier": self.application_identifier,
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.page is None and self.application_identifier is None:
            errors.append(
                self._create_error_detail(
                    "value",
                    "Either page or application must be provided",
                    self.page,
                )
            )

        if self.application_identifier:
            application = Application.objects.filter(
                identifier=self.application_identifier
            ).exists()
            if not application:
                errors.append(
                    self._create_error_detail(
                        "application_identifier",
                        f"Application with identifier {self.application_identifier} does not exist",
                        self.application_identifier,
                    )
                )

        return errors


__exports__ = ("DefaultHomepageEffect",)
