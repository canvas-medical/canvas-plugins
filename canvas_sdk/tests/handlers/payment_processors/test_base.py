import json

import pytest

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.payment_processor import PaymentProcessorMetadata
from canvas_sdk.events import EventType
from canvas_sdk.handlers.payment_processors.base import PaymentProcessor
from canvas_sdk.tests.handlers.payment_processors.utils import create_event


class DummyPaymentProcessor(PaymentProcessor):
    """A dummy payment processor for testing purposes."""

    TYPE = PaymentProcessorMetadata.PaymentProcessorType.CARD


@pytest.mark.parametrize(
    argnames="context, expected_nr_results",
    argvalues=[
        ({}, 1),
        ({"payment_type": PaymentProcessorMetadata.PaymentProcessorType.CARD}, 1),
        ({"payment_type": "other"}, 0),
    ],
    ids=["no_payment_type", "dummy_payment_type", "other_payment_type"],
)
def test_list_event_returns_metadata(context: dict, expected_nr_results: int) -> None:
    """Test that the list event returns the processor metadata."""
    processor = DummyPaymentProcessor(
        event=create_event(
            type=EventType.REVENUE__PAYMENT_PROCESSOR__LIST,
            context=context,
        ),
    )
    effects = processor.compute()

    assert len(effects) == expected_nr_results

    if expected_nr_results > 0:
        assert effects[0].type == EffectType.REVENUE__PAYMENT_PROCESSOR__METADATA
        data = json.loads(effects[0].payload)["data"]
        assert data["identifier"] == processor.identifier
        assert data["type"] == processor.TYPE
