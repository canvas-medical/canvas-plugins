from abc import ABC, abstractmethod
from decimal import Decimal
from enum import StrEnum

from canvas_sdk.effects import Effect
from canvas_sdk.effects.payment_processor import (
    AddPaymentMethodResponse,
    CardTransaction,
    PaymentMethod,
    PaymentProcessorForm,
    PaymentProcessorMetadata,
    RemovePaymentMethodResponse,
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
        if self.event.context.get("identifier") == self.identifier:
            intent = self.event.context.get("intent")
            effects = self.on_payment_processor_selected(intent=intent)
            return [effect.apply() for effect in effects]

        return []

    def _charge(self) -> Effect | None:
        """Handle the event when a charge is made."""
        if self.event.context.get("identifier") == self.identifier:
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
        if self.event.context.get("identifier") == self.identifier:
            patient = (
                Patient.objects.get(id=self.event.context.get("patient", {}).get("id"))
                if self.event.context.get("patient")
                else None
            )
            effects = self.payment_methods(patient=patient)
            return [effect.apply() for effect in effects]

        return []

    def _add_payment_method(self) -> Effect | None:
        """Handle the event when a card is added."""
        if self.event.context.get("identifier") == self.identifier:
            patient = (
                Patient.objects.get(id=self.event.context.get("patient", {}).get("id"))
                if self.event.context.get("patient")
                else None
            )

            if not patient:
                return None

            token = str(self.event.context.get("token"))
            effect = self.add_payment_method(token=token, patient=patient)
            return effect.apply() if effect else None

        return None

    def _remove_payment_method(self) -> Effect | None:
        """Handle the event when a payment method is removed."""
        if self.event.context.get("identifier") == self.identifier:
            patient = (
                Patient.objects.get(id=self.event.context.get("patient", {}).get("id"))
                if self.event.context.get("patient")
                else None
            )

            if not patient:
                return None

            token = str(self.event.context.get("token"))
            effect = self.remove_payment_method(token=token, patient=patient)
            return effect.apply() if effect else None

        return None

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

    @abstractmethod
    def charge(
        self, amount: Decimal, token: str, patient: Patient | None = None
    ) -> CardTransaction:
        """Charge a credit/debit card using the provided token.

        Args:
            amount (Decimal): The amount to charge.
            token (str): The token representing the credit card.
            patient (Patient | None): The patient for whom the charge is being made.

        Returns:
            CardTransaction: The result of the card transaction.
        """
        raise NotImplementedError("Subclasses must implement the charge method.")

    @abstractmethod
    def payment_methods(self, patient: Patient | None = None) -> list[PaymentMethod]:
        """List payment methods for the card payment processor.

        Args:
            patient (Patient | None): The patient for whom the payment methods are being listed.

        Returns:
            list[PaymentMethod]: A list of payment methods available for the card payment processor.
        """
        raise NotImplementedError("Subclasses must implement the payment_methods method.")

    @abstractmethod
    def add_payment_method(self, token: str, patient: Patient) -> AddPaymentMethodResponse:
        """Add a payment method for the card payment processor.

        Args:
            token (str): The token representing the payment method.
            patient (Patient): The patient for whom the payment method is being added.

        Returns:
            AddPaymentMethodResponse: The response indicating the result of the addition operation.
        """
        raise NotImplementedError("Subclasses must implement the add_payment_method method.")

    @abstractmethod
    def remove_payment_method(self, token: str, patient: Patient) -> RemovePaymentMethodResponse:
        """Remove a payment method for the card payment processor.

        Args:
            token (str): The token representing the payment method to be removed.
            patient (Patient): The patient for whom the payment method is being removed.

        Returns:
            RemovePaymentMethodResponse: The response indicating the result of the removal operation.
        """
        raise NotImplementedError("Subclasses must implement the remove_payment_method method.")


__exports__ = ("CardPaymentProcessor",)
