from abc import ABC, abstractmethod
from decimal import Decimal
from enum import StrEnum

from canvas_sdk.effects import Effect
from canvas_sdk.effects.payment_processor import (
    CreditCardTransaction,
    PaymentMethod,
    PaymentProcessorForm,
    PaymentProcessorMetadata,
)
from canvas_sdk.handlers.payment_processors.base import PaymentProcessor
from canvas_sdk.v1.data import Patient


class CardPaymentProcessor(PaymentProcessor, ABC):
    """Base Card Payment Processor Handler."""

    TYPE = PaymentProcessorMetadata.PaymentProcessorType.CARD

    class PaymentIntent(StrEnum):
        """Enum for payment actions."""

        ADD_CARD = "add_card"
        PAY = "pay"

    def _on_payment_processor_selected(self) -> list[Effect]:
        """Handle the event when a payment processor is selected."""
        if self.event.context["identifier"] == self.identifier:
            intent = self.event.context["intent"]
            effects = self.on_payment_processor_selected(intent=intent)
            return [effect.apply() for effect in effects]

        return []

    def _charge(self) -> Effect | None:
        """Handle the event when a charge is made."""
        if self.event.context["identifier"] == self.identifier:
            patient = (
                Patient.objects.get(id=self.event.context.get("patient", {}).get("id"))
                if self.event.context.get("patient")
                else None
            )

            amount = Decimal(str(self.event.context.get("amount")))
            token = str(self.event.context.get("token"))
            effect = self.charge(amount=amount, token=token, patient=patient)

            return effect.apply() if effect else None

        return None

    def _payment_methods(self) -> list[Effect]:
        """List payment methods for the card payment processor."""
        if self.event.context["identifier"] == self.identifier:
            patient = (
                Patient.objects.get(id=self.event.context.get("patient", {}).get("id"))
                if self.event.context.get("patient")
                else None
            )
            effects = self.payment_methods(patient=patient)
            return [effect.apply() for effect in effects]

        return []

    def on_payment_processor_selected(self, intent: str | None) -> list[PaymentProcessorForm]:
        """Handle the event when a payment processor is selected."""
        patient = (
            Patient.objects.get(id=self.event.context.get("patient", {}).get("id"))
            if self.event.context.get("patient")
            else None
        )
        match intent:
            case self.PaymentIntent.ADD_CARD:
                return [self.add_card_form(patient)]
            case self.PaymentIntent.PAY:
                return [self.payment_form(patient)]
            case None:
                return [self.payment_form(patient), self.add_card_form(patient)]
            case _:
                return []

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

    def charge(
        self, amount: Decimal, token: str, patient: Patient | None = None
    ) -> CreditCardTransaction:
        """Return the form for charging a credit card.

        Args:
            amount (Decimal): The amount to charge.
            token (str): The token representing the credit card.
            patient (Patient | None): The patient for whom the charge is being made.

        Returns:
            PaymentProcessorForm: The form for charging a credit card.
        """
        raise NotImplementedError("Subclasses must implement the charge method.")

    def payment_methods(self, patient: Patient | None = None) -> list[PaymentMethod]:
        """List payment methods for the card payment processor.

        Args:
            patient (Patient | None): The patient for whom the payment methods are being listed.

        Returns:
            list[PaymentMethod]: A list of payment methods available for the card payment processor.
        """
        raise NotImplementedError("Subclasses must implement the payment_methods method.")


__exports__ = ("CardPaymentProcessor",)
