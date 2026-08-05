from enum import Enum
from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect


class ProviderMenuConfiguration(_BaseEffect):
    """
    An Effect that will decide which items appear on the provider (hamburger) menu.
    """

    class Meta:
        effect_type = EffectType.SHOW_PROVIDER_MENU_ITEMS

    class Items(Enum):
        SCHEDULE = "schedule"
        PATIENTS = "patients"
        REVENUE = "revenue"
        POPULATIONS = "populations"
        CAMPAIGNS = "campaigns"
        DATA_INTEGRATION = "data_integration"
        QUESTIONNAIRE_BUILDER = "questionnaire_builder"
        SETTINGS = "settings"
        MULTI_FACTOR_AUTHENTICATION = "multi_factor_authentication"
        CHANGELOG = "changelog"
        HELP_CENTER = "help_center"

    items: list[Items]

    @property
    def values(self) -> dict[str, Any]:
        """The ProviderMenuConfiguration's values."""
        return {"items": [i.value for i in self.items]}


__exports__ = ("ProviderMenuConfiguration",)
