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

    intent: str
    content: str

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the PaymentProcessorMetadata."""
        return {
            "intent": self.intent,
            "content": self.content,
        }


class CardTransaction(_BaseEffect):
    """CardTransaction effect class."""

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

    payment_method_id: str
    card_holder_name: str | None
    brand: str
    postal_code: str | None = None
    country: str | None = None
    expiration_year: int
    expiration_month: int
    card_last_four_digits: str

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the PaymentMethod."""
        return {
            "payment_method_id": self.payment_method_id,
            "card_holder_name": self.card_holder_name,
            "brand": self.brand,
            "postal_code": self.postal_code,
            "country": self.country,
            "expiration_year": self.expiration_year,
            "expiration_month": self.expiration_month,
            "card_last_four_digits": self.card_last_four_digits,
        }


class AddPaymentMethodResponse(_BaseEffect):
    """AddPaymentMethodResponse effect class."""

    class Meta:
        effect_type = EffectType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHOD__ADD_RESPONSE

    success: bool

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the AddPaymentMethodResponse."""
        return {"success": self.success}


class RemovePaymentMethodResponse(_BaseEffect):
    """RemovePaymentMethodResponse effect class."""

    class Meta:
        effect_type = EffectType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHOD__REMOVE_RESPONSE

    success: bool

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the RemovePaymentMethodResponse."""
        return {
            "success": self.success,
        }


__exports__ = (
    "PaymentProcessorMetadata",
    "PaymentProcessorForm",
    "CardTransaction",
    "PaymentMethod",
    "AddPaymentMethodResponse",
    "RemovePaymentMethodResponse",
)
