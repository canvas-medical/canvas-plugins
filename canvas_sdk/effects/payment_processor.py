from enum import StrEnum
from typing import Any

from canvas_sdk.effects import EffectType, _BaseEffect


class PaymentProcessorMetadata(_BaseEffect):
    """PaymentProcessorInfo effect class."""

    class Meta:
        effect_type = EffectType.REVENUE__PAYMENT_PROCESSOR_METADATA

    class PaymentProcessorType(StrEnum):
        """Enum for payment processor types."""

        CREDIT_CARD = "credit_card"

    identifier: str
    type: PaymentProcessorType

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the PaymentProcessorMetadata."""
        return {
            "identifier": self.identifier,
            "type": self.type.value,
        }


class PaymentProcessorForm(_BaseEffect):
    """PaymentProcessorForm effect class."""

    content: str

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the PaymentProcessorMetadata."""
        return {
            "content": self.content,
        }


__exports__ = ("PaymentProcessorMetadata", "PaymentProcessorForm")
