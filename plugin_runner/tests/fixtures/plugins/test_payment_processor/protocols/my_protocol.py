from decimal import Decimal

from canvas_sdk.effects.payment_processor import (
    AddPaymentMethodResponse,
    CardTransaction,
    PaymentMethod,
    PaymentProcessorForm,
    RemovePaymentMethodResponse,
)
from canvas_sdk.handlers.payment_processors.card import CardPaymentProcessor
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import Patient


class CustomPaymentProcessor(CardPaymentProcessor):
    """Custom payment processor for testing purposes."""

    def add_card_form(self, patient: Patient | None = None) -> PaymentProcessorForm:
        """Return a form for adding a card."""
        form = render_to_string("forms/card.html")
        return PaymentProcessorForm(
            content=form, intent=CardPaymentProcessor.PaymentIntent.ADD_CARD
        )

    def payment_form(self, patient: Patient | None = None) -> PaymentProcessorForm:
        """Return a form for processing a payment."""
        form = render_to_string("forms/payment.html")
        return PaymentProcessorForm(content=form, intent=CardPaymentProcessor.PaymentIntent.PAY)

    def charge(
        self, amount: Decimal, token: str, patient: Patient | None = None
    ) -> CardTransaction:
        """Process a charge using the provided token."""
        return CardTransaction(success=True, transaction_id="txn_123", api_response={})

    def payment_methods(self, patient: Patient | None = None) -> list[PaymentMethod]:
        """List payment methods for the patient."""
        return [
            PaymentMethod(
                payment_method_id="pm_1",
                brand="Visa",
                expiration_year=2025,
                expiration_month=12,
                card_holder_name="John Doe",
                postal_code="12345",
                card_last_four_digits="1234",
            )
        ]

    def add_payment_method(self, token: str, patient: Patient) -> AddPaymentMethodResponse:
        """Add a payment method for the patient using the provided token."""
        return AddPaymentMethodResponse(success=True)

    def remove_payment_method(self, token: str, patient: Patient) -> RemovePaymentMethodResponse:
        """Remove a payment method for the patient using the provided token."""
        return RemovePaymentMethodResponse(success=True)
