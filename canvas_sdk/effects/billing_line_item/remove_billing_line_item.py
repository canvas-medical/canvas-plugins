from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect


class RemoveBillingLineItem(_BaseEffect):
    """
    An Effect that will remove a billing line item in a note footer.
    """

    class Meta:
        effect_type = EffectType.REMOVE_BILLING_LINE_ITEM
        apply_required_fields = ("billing_line_item_id",)

    billing_line_item_id: str | None = None

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {
            "billing_line_item_id": self.billing_line_item_id,
        }


__exports__ = ("RemoveBillingLineItem",)
