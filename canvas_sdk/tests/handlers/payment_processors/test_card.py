from collections.abc import Generator
from decimal import Decimal
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

from canvas_sdk.effects.payment_processor import (
    AddPaymentMethodResponse,
    CardTransaction,
    PaymentMethod,
    PaymentProcessorForm,
    RemovePaymentMethodResponse,
)
from canvas_sdk.events import EventType
from canvas_sdk.handlers.payment_processors.card import CardPaymentProcessor
from canvas_sdk.tests.handlers.payment_processors.utils import create_event
from canvas_sdk.v1.data import Patient

PATIENT = {
    "id": "patient_key",
}


@pytest.fixture
def mock_patient_model() -> Generator[MagicMock, None, None]:
    """Fixture to mock the Patient model."""
    with patch(
        "canvas_sdk.handlers.payment_processors.card.Patient", autospec=True
    ) as mock_patient:
        mock_patient.objects.get.return_value = PATIENT
        yield mock_patient


class DummyCardProcessor(CardPaymentProcessor):
    """A dummy card payment processor for testing purposes."""

    @property
    def identifier(self) -> str:
        """Return a dummy identifier for the processor."""
        return "dummy_processor"

    def payment_form(self, patient: Patient | None = None) -> PaymentProcessorForm:  # type: ignore[empty-body]
        """Return a mock payment form."""
        pass

    def add_card_form(self, patient: Patient | None = None) -> PaymentProcessorForm:  # type: ignore[empty-body]
        """Return a mock form for adding a card."""
        pass

    def charge(  # type: ignore[empty-body]
        self, amount: Decimal, token: str, patient: Patient | None = None, **kwargs: Any
    ) -> CardTransaction:
        """Return a mock credit card transaction."""
        pass

    def payment_methods(self, patient: Patient | None = None) -> list[PaymentMethod]:  # type: ignore[empty-body]
        """Return a list of mock payment methods."""
        pass

    def add_payment_method(  # type: ignore[empty-body]
        self, token: str, patient: Patient, **kwargs: Any
    ) -> AddPaymentMethodResponse:
        """Return a mock response for adding a payment method."""
        pass

    def remove_payment_method(self, token: str, patient: Patient) -> RemovePaymentMethodResponse:  # type: ignore[empty-body]
        """Return a mock response for removing a payment method."""
        pass


@pytest.mark.parametrize(
    "context, expected_nr_results",
    [
        ({}, 0),
        ({"identifier": "dummy_processor"}, 2),
        ({"identifier": "dummy_processor", "patient": PATIENT}, 2),
        ({"identifier": "dummy_processor", "intent": CardPaymentProcessor.PaymentIntent.PAY}, 1),
        (
            {
                "identifier": "dummy_processor",
                "intent": CardPaymentProcessor.PaymentIntent.ADD_CARD,
            },
            1,
        ),
    ],
    ids=[
        "no_context",
        "dummy_processor_selected",
        "dummy_processor_selected_with_patient",
        "dummy_processor_selected_pay_intent",
        "dummy_processor_selected_add_card_intent",
    ],
)
@patch.object(
    DummyCardProcessor,
    "add_card_form",
    return_value=PaymentProcessorForm(
        content="", intent=CardPaymentProcessor.PaymentIntent.ADD_CARD
    ),
)
@patch.object(
    DummyCardProcessor,
    "payment_form",
    return_value=PaymentProcessorForm(content="", intent=CardPaymentProcessor.PaymentIntent.PAY),
)
def test_on_payment_processor_selected(
    payment_form: MagicMock,
    add_card_form: MagicMock,
    mock_patient_model: MagicMock,
    context: dict,
    expected_nr_results: int,
) -> None:
    """Test that on_payment_processor_selected under different contexts."""
    event = create_event(type=EventType.REVENUE__PAYMENT_PROCESSOR__SELECTED, context=context)
    processor = DummyCardProcessor(event=event)

    result = processor.compute()

    assert len(result) == expected_nr_results

    if expected_nr_results > 0:
        patient = context.get("patient")
        intent = context.get("intent")

        if not intent or intent == CardPaymentProcessor.PaymentIntent.PAY:
            args = patient if patient else None
            payment_form.assert_called_once_with(args)
        if not intent or intent == CardPaymentProcessor.PaymentIntent.ADD_CARD:
            args = patient if patient else None
            add_card_form.assert_called_once_with(args)

        if patient:
            mock_patient_model.objects.get.assert_called_once_with(id=patient.get("id"))


@pytest.mark.parametrize(
    "context, expected_nr_results",
    [
        ({}, 0),
        ({"identifier": "dummy_processor", "token": "pmt", "amount": "10.23"}, 1),
        (
            {
                "identifier": "dummy_processor",
                "token": "pmt",
                "amount": "10.23",
                "patient": PATIENT,
            },
            1,
        ),
    ],
    ids=[
        "no_context",
        "dummy_processor_charge",
        "dummy_processor_charge_with_patient",
    ],
)
@patch.object(
    DummyCardProcessor,
    "charge",
    return_value=CardTransaction(success=True, transaction_id="txn_123", api_response={}),
)
def test_charge(
    mock_charge: MagicMock, mock_patient_model: MagicMock, context: dict, expected_nr_results: int
) -> None:
    """Test the charge method under different contexts."""
    event = create_event(type=EventType.REVENUE__PAYMENT_PROCESSOR__CHARGE, context=context)
    processor = DummyCardProcessor(event=event)

    result = processor.compute()

    assert len(result) == expected_nr_results

    if expected_nr_results > 0:
        patient = context.get("patient")
        if patient:
            mock_patient_model.objects.get.assert_called_once_with(id=patient.get("id"))
        else:
            mock_patient_model.objects.get.assert_not_called()

        mock_charge.assert_called_once_with(
            amount=Decimal(cast(str, context.get("amount"))),
            token=context["token"],
            patient=patient,
            additional_context=None,
        )
    else:
        mock_charge.assert_not_called()


@pytest.mark.parametrize(
    "context, expected_nr_results",
    [
        ({}, 0),
        ({"identifier": "dummy_processor"}, 1),
        ({"identifier": "dummy_processor", "patient": PATIENT}, 1),
    ],
    ids=[
        "no_context",
        "dummy_processor_selected",
        "dummy_processor_selected_with_patient",
    ],
)
@patch.object(
    DummyCardProcessor,
    "payment_methods",
    return_value=[
        PaymentMethod(
            payment_method_id="pm_1",
            brand="Visa",
            expiration_year=2025,
            expiration_month=12,
            card_holder_name="John Doe",
            postal_code="12345",
            card_last_four_digits="1234",
        )
    ],
)
def test_payment_methods(
    mock_payment_methods: MagicMock,
    mock_patient_model: MagicMock,
    context: dict,
    expected_nr_results: int,
) -> None:
    """Test that the payment_methods under different contexts."""
    event = create_event(
        type=EventType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHODS__LIST,
        context=context,
    )
    processor = DummyCardProcessor(event=event)

    result = processor.compute()

    assert len(result) == expected_nr_results

    if expected_nr_results > 0:
        patient = context.get("patient")
        if patient:
            mock_patient_model.objects.get.assert_called_once_with(id=patient.get("id"))
        else:
            mock_patient_model.objects.get.assert_not_called()
        mock_payment_methods.assert_called_once_with(patient=patient)
    else:
        mock_payment_methods.assert_not_called()


@patch.object(
    DummyCardProcessor, "add_payment_method", return_value=AddPaymentMethodResponse(success=True)
)
@pytest.mark.parametrize(
    "context, expected_nr_results",
    [
        ({}, 0),
        ({"identifier": "dummy_processor", "token": "pmt"}, 0),
        ({"identifier": "dummy_processor", "token": "pmt", "patient": PATIENT}, 1),
    ],
    ids=[
        "no_context",
        "dummy_processor_selected_without_patient",
        "dummy_processor_selected_with_patient",
    ],
)
def test_add_payment_method(
    mock_add_payment_method: MagicMock,
    mock_patient_model: MagicMock,
    context: dict,
    expected_nr_results: int,
) -> None:
    """Test the add_payment_method under different contexts."""
    event = create_event(
        type=EventType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHODS__ADD,
        context=context,
    )
    processor = DummyCardProcessor(event=event)

    result = processor.compute()

    assert len(result) == expected_nr_results

    if expected_nr_results > 0:
        patient = context.get("patient")
        if patient:
            mock_patient_model.objects.get.assert_called_once_with(id=patient.get("id"))
        else:
            mock_patient_model.objects.get.assert_not_called()
        mock_add_payment_method.assert_called_once_with(
            token=context["token"], patient=patient, additional_context=None
        )
    else:
        mock_add_payment_method.assert_not_called()


@pytest.mark.parametrize(
    "additional_context, expected_kwargs",
    [
        (None, {"additional_context": None}),
        ('{"key": "value"}', {"key": "value"}),
        ("just a string", {"additional_context": "just a string"}),
        ("123", {"additional_context": 123}),
        ("true", {"additional_context": True}),
    ],
    ids=[
        "none",
        "stringified_dict",
        "plain_string",
        "stringified_number",
        "stringified_boolean",
    ],
)
@patch.object(
    DummyCardProcessor,
    "add_payment_method",
    return_value=CardTransaction(success=True, transaction_id="txn_123", api_response={}),
)
def test_add_payment_method_additional_context(
    mock_add_payment_method: MagicMock,
    mock_patient_model: MagicMock,
    additional_context: str | None,
    expected_kwargs: dict,
) -> None:
    """Test that add_payment_method is called with correctly parsed additional_context."""
    context = {
        "identifier": "dummy_processor",
        "token": "pmt_token",
        "patient": PATIENT,
        "additional_context": additional_context,
    }
    event = create_event(
        type=EventType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHODS__ADD, context=context
    )
    processor = DummyCardProcessor(event=event)

    result = processor.compute()

    assert len(result) == 1
    mock_add_payment_method.assert_called_once_with(
        token="pmt_token",
        patient=PATIENT,
        **expected_kwargs,
    )


@pytest.mark.parametrize(
    "additional_context, expected_kwargs",
    [
        (None, {"additional_context": None}),
        ('{"key": "value"}', {"key": "value"}),
        ("just a string", {"additional_context": "just a string"}),
        ("123", {"additional_context": 123}),
        ("true", {"additional_context": True}),
    ],
    ids=[
        "none",
        "stringified_dict",
        "plain_string",
        "stringified_number",
        "stringified_boolean",
    ],
)
@patch.object(
    DummyCardProcessor,
    "charge",
    return_value=CardTransaction(success=True, transaction_id="txn_123", api_response={}),
)
def test_charge_additional_context(
    mock_charge: MagicMock,
    mock_patient_model: MagicMock,
    additional_context: str | None,
    expected_kwargs: dict,
) -> None:
    """Test that charge is called with correctly parsed additional_context."""
    context = {
        "identifier": "dummy_processor",
        "token": "pmt_token",
        "amount": "10.00",
        "additional_context": additional_context,
    }
    event = create_event(type=EventType.REVENUE__PAYMENT_PROCESSOR__CHARGE, context=context)
    processor = DummyCardProcessor(event=event)

    result = processor.compute()

    assert len(result) == 1
    mock_charge.assert_called_once_with(
        amount=Decimal("10.00"),
        token="pmt_token",
        patient=None,
        **expected_kwargs,
    )


@patch.object(
    DummyCardProcessor,
    "remove_payment_method",
    return_value=RemovePaymentMethodResponse(success=True),
)
@pytest.mark.parametrize(
    "context, expected_nr_results",
    [
        ({}, 0),
        ({"identifier": "dummy_processor", "token": "pmt"}, 0),
        ({"identifier": "dummy_processor", "token": "pmt", "patient": PATIENT}, 1),
    ],
    ids=[
        "no_context",
        "dummy_processor_selected_without_patient",
        "dummy_processor_selected_with_patient",
    ],
)
def test_remove_payment_method(
    mock_remove_payment_method: MagicMock,
    mock_patient_model: MagicMock,
    context: dict,
    expected_nr_results: int,
) -> None:
    """Test the remove_payment_method under different contexts."""
    event = create_event(
        type=EventType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHODS__REMOVE,
        context=context,
    )
    processor = DummyCardProcessor(event=event)

    result = processor.compute()

    assert len(result) == expected_nr_results

    if expected_nr_results > 0:
        patient = context.get("patient")
        if patient:
            mock_patient_model.objects.get.assert_called_once_with(id=patient.get("id"))
        else:
            mock_patient_model.objects.get.assert_not_called()
        mock_remove_payment_method.assert_called_once_with(token=context["token"], patient=patient)
    else:
        mock_remove_payment_method.assert_not_called()
