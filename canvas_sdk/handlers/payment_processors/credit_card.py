from abc import ABC, abstractmethod
from enum import StrEnum

from canvas_sdk.effects import Effect
from canvas_sdk.effects.payment_processor import PaymentProcessorForm, PaymentProcessorMetadata
from canvas_sdk.handlers.payment_processors.base import PaymentProcessor
from canvas_sdk.v1.data import Patient


class CreditCardPaymentProcessor(PaymentProcessor, ABC):
    """Base Credit Card Payment Processor Handler."""

    TYPE = PaymentProcessorMetadata.PaymentProcessorType.CREDIT_CARD

    class PaymentIntent(StrEnum):
        """Enum for payment actions."""

        ADD_CARD = "add_card"
        PAY = "pay"

    def _on_payment_processor_selected(self) -> Effect | None:
        """Handle the event when a payment processor is selected."""
        if self.event.context["payment_type"] == self.TYPE:
            intent = self.event.context["intent"]
            effect = self.on_payment_processor_selected(intent=intent)
            return effect.apply() if effect else None

        return None

    def on_payment_processor_selected(self, intent: str | None) -> PaymentProcessorForm | None:
        """Handle the event when a payment processor is selected."""
        patient = (
            Patient.objects.get(id=self.event.context.get("patient", {}).get("id"))
            if self.event.context.get("patient")
            else None
        )
        match intent:
            case self.PaymentIntent.ADD_CARD:
                return self.add_card_form(patient)
            case self.PaymentIntent.PAY:
                return self.payment_form(patient)
            case None:
                return self.payment_form(patient)
            case _:
                return None

    @abstractmethod
    def payment_form(self, patient: Patient | None = None) -> PaymentProcessorForm:
        """Return the payment form for the credit card processor.

        Args:
            patient (Patient | None): The patient for whom the payment is being processed.

        Returns:
            PaymentProcessorForm: The form for processing the payment.
        """
        raise NotImplementedError("Subclasses must implement the payment_form method.")

    @abstractmethod
    def add_card_form(self, patient: Patient | None = None) -> PaymentProcessorForm:
        """Return the form for adding a card.

        Args:
            patient (Patient | None): The patient for whom the add is being added.

        Returns:
            PaymentProcessorForm: The form for adding a card.
        """
        raise NotImplementedError("Subclasses must implement the add_card_form method.")


__exports__ = ("CreditCardPaymentProcessor",)
