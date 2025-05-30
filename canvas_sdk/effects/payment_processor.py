from enum import StrEnum
from typing import Any

from canvas_sdk.effects import EffectType, _BaseEffect


class PaymentProcessorMetadata(_BaseEffect):
    """PaymentProcessorInfo effect class."""

    class Meta:
        effect_type = EffectType.REVENUE__PAYMENT_PROCESSOR__METADATA

    class PaymentProcessorType(StrEnum):
        """Enum for payment processor types."""

        CARD = "card"

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

    class Meta:
        effect_type = EffectType.REVENUE__PAYMENT_PROCESSOR__FORM

    intent: str | None = None
    content: str

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the PaymentProcessorMetadata."""
        return {
            "intent": self.intent,
            "content": self.content,
        }


class CreditCardTransaction(_BaseEffect):
    """CreditCardTransaction effect class."""

    class Meta:
        effect_type = EffectType.REVENUE__PAYMENT_PROCESSOR__CREDIT_CARD_TRANSACTION

    success: bool
    transaction_id: str | None
    error_code: str | None = None
    api_response: dict

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the CreditCardTransaction."""
        return {
            "success": self.success,
            "transaction_id": self.transaction_id,
            "api_response": self.api_response,
            "error_code": self.error_code,
        }


class PaymentMethod(_BaseEffect):
    """PaymentMethod effect class."""

    class Meta:
        effect_type = EffectType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHOD

    token: str
    address_line1: str | None
    address_line2: str | None
    card_brand: str
    city: str | None
    country: str | None
    exp_date: str
    full_name: str | None
    last_four: str

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the PaymentMethod."""
        return {
            "token": self.token,
            "address_line1": self.address_line1,
            "address_line2": self.address_line2,
            "card_brand": self.card_brand,
            "city": self.city,
            "country": self.country,
            "exp_date": self.exp_date,
            "full_name": self.full_name,
            "last_four": self.last_four,
        }


__exports__ = (
    "PaymentProcessorMetadata",
    "PaymentProcessorForm",
    "CreditCardTransaction",
    "PaymentMethod",
)
