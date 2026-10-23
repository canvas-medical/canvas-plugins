from typing import Any

from pydantic import Field

from canvas_sdk.effects.base import EffectType, _BaseEffect

# The most units one effect may record, so a loop gone wrong cannot record millions.
MAX_QUANTITY = 10_000
# The longest key Canvas stores.
MAX_KEY = 256


class RecordUsage(_BaseEffect):
    """
    Records units of a plugin's work that its catalog listing prices, such as one visit.

    `unit` names one of the units in the plugin's manifest `catalog.pricing`, matched without
    regard to case or repeated whitespace. `key` names the work being counted, such as
    `visit:<note id>`: Canvas records a key once per plugin, so recording it again (a retried
    handler, the same note finished twice) adds nothing.

    Canvas records the plugin's name and version itself and stamps the time the effect is
    applied. A unit is recorded only when the plugin's other effects from the same response
    were applied, so work that failed is not counted.
    """

    class Meta:
        effect_type = EffectType.RECORD_USAGE

    unit: str = Field(min_length=1, max_length=40)
    key: str = Field(min_length=1, max_length=MAX_KEY)
    quantity: int = Field(default=1, ge=1, le=MAX_QUANTITY)

    @property
    def values(self) -> dict[str, Any]:
        """The unit, the key and how many units."""
        return {"unit": self.unit, "key": self.key, "quantity": self.quantity}


__exports__ = ("RecordUsage",)
