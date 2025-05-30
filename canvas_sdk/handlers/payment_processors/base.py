import base64
from abc import ABC

from canvas_sdk.effects import Effect
from canvas_sdk.effects.payment_processor import PaymentProcessorMetadata
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler


class PaymentProcessor(BaseHandler, ABC):
    """
    Abstract Base class for payment processors.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.REVENUE__LIST_PAYMENT_PROCESSORS),
        EventType.Name(EventType.REVENUE__ON_PAYMENT_PROCESSOR_SELECTED),
    ]

    TYPE: PaymentProcessorMetadata.PaymentProcessorType

    @property
    def identifier(self) -> str:
        """The application identifier."""
        identifier = f"{self.__class__.__module__}:{self.__class__.__qualname__}"

        return base64.b64encode(identifier.encode("utf-8")).decode("utf-8")

    def compute(self) -> list[Effect]:
        """Compute the effects to be applied."""
        if self.event.type == EventType.REVENUE__LIST_PAYMENT_PROCESSORS and (
            not self.event.context["payment_type"]
            or self.event.context["payment_type"] == self.TYPE
        ):
            return [self.metadata().apply()]
        elif self.event.type == EventType.REVENUE__ON_PAYMENT_PROCESSOR_SELECTED:
            effect = self._on_payment_processor_selected()
            return [effect] if effect else []

        return []

    def metadata(self) -> PaymentProcessorMetadata:
        """Return information about the payment processor."""
        return PaymentProcessorMetadata(identifier=self.identifier, type=self.TYPE)

    def _on_payment_processor_selected(self) -> Effect | None:
        """Handle the event when a payment processor is selected."""
        # This method should be overridden by subclasses to handle specific logic
        # when a payment processor is selected.
        return None


__exports__ = ("PaymentProcessor",)
