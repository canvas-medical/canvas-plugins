from decimal import Decimal
from typing import Any

from canvas_sdk.effects.payment_processor import (
    AddPaymentMethodResponse,
    CardTransaction,
    PaymentMethod,
    PaymentProcessorForm,
    RemovePaymentMethodResponse,
)
from canvas_sdk.handlers.payment_processors.card import (
    CardPaymentProcessor,
)
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import Patient
from logger import log
from paytheory_payment_processor.paytheory.api import PayorInput, PayTheoryAPI, TransactionInput
from paytheory_payment_processor.paytheory.exceptions import TransactionError


class PayTheoryPaymentProcessor(CardPaymentProcessor):
    """Custom payment processor for handling credit card payments with PayTheory."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the PayTheory payment processor."""
        super().__init__(*args, **kwargs)
        self.api = PayTheoryAPI(
            api_key=self.secrets["paytheory_secret_key"],
            merchant_id=self.secrets["paytheory_merchant_id"],
        )
        self.default_payor_id = self.secrets["paytheory_default_payor_id"]
        self.public_api_key = self.secrets["paytheory_public_key"]

    def payment_form(self, patient: Patient | None = None) -> PaymentProcessorForm:
        """Return the payment form for the credit card processor."""
        content = render_to_string(
            "templates/form.html",
            {
                "payor_id": self.default_payor_id,
                "intent": self.PaymentIntent.PAY,
                "public_api_key": self.public_api_key,
            },
        )

        return PaymentProcessorForm(content=content, intent=self.PaymentIntent.PAY)

    def add_card_form(self, patient: Patient | None = None) -> PaymentProcessorForm:
        """Return the form for adding a card."""
        payor_id = self.get_or_create_payor_id(patient)

        content = render_to_string(
            "templates/form.html",
            {
                "payor_id": payor_id,
                "intent": self.PaymentIntent.ADD_CARD,
                "public_api_key": self.public_api_key,
            },
        )

        return PaymentProcessorForm(content=content, intent=self.PaymentIntent.ADD_CARD)

    def get_or_create_payor_id(self, patient: Patient | None = None) -> str | None:
        """Retrieve or create a payor_id based on the patient_id."""
        if not patient:
            return None

        payor_id = self.api.get_payor_id(patient.id)

        if not payor_id:
            payor_id = self.api.create_payor(
                PayorInput(full_name=patient.full_name, metadata={"canvas_patient_id": patient.id})
            )

        return payor_id

    def charge(
        self, amount: Decimal, token: str, patient: Patient | None = None
    ) -> CardTransaction:
        """Charge the credit card using the PayTheory API."""
        try:
            transaction = self.api.create_transaction(
                TransactionInput(payment_method_id=token, amount=amount)
            )

            status = transaction["status"]
            success = status in ["PENDING", "SUCCEEDED"]
            error_code = transaction.get("failure_reasons", [])[0] if not success else None

            try:
                # disable payment method if it belongs to DEFAULT_PAYOR_ID
                if self.api.get_payment_method(token, self.default_payor_id):
                    self.api.disable_payment_method(token)
                    log.info("Payment method disabled")
            except Exception as ex:
                log.error(ex)

            return CardTransaction(
                success=success,
                transaction_id=transaction["transaction_id"],
                api_response=transaction,
                error_code=error_code,
            )

        except TransactionError as ex:
            return CardTransaction(
                success=False,
                transaction_id=None,
                api_response=ex.api_response,
            )

    def payment_methods(self, patient: Patient | None = None) -> list[PaymentMethod]:
        """Return the payment methods for the card payment processor."""
        if not patient:
            return []

        payor_id = self.get_or_create_payor_id(patient)

        payment_methods = self.api.get_payment_methods(payor_id=payor_id)

        return [
            PaymentMethod(
                payment_method_id=method["payment_method_id"],
                card_holder_name=method["full_name"],
                brand=method["card_brand"],
                postal_code=method["postal_code"],
                country=method["country"],
                expiration_month=int(method["exp_date"][:2]),
                expiration_year=int(f"20{method['exp_date'][-2:]}"),
                card_last_four_digits=method["last_four"],
            )
            for method in payment_methods
        ]

    def add_payment_method(self, token: str, patient: Patient) -> AddPaymentMethodResponse:
        """Add a new payment method for the patient."""
        return AddPaymentMethodResponse(success=True)

    def remove_payment_method(self, token, patient: Patient) -> RemovePaymentMethodResponse:
        """Remove a payment method for the patient."""
        payor_id = self.api.get_payor_id(patient.id)

        if not payor_id:
            log.warning(
                f"No payor_id found for patient {patient.id}, discarding remove_payment_method request."
            )
            return RemovePaymentMethodResponse(success=False)

        result = self.api.disable_payment_method(payment_method_id=token)

        return RemovePaymentMethodResponse(success=result)
