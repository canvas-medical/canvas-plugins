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
        EventType.Name(EventType.REVENUE__PAYMENT_PROCESSOR__LIST),
        EventType.Name(EventType.REVENUE__PAYMENT_PROCESSOR__SELECTED),
        EventType.Name(EventType.REVENUE__PAYMENT_PROCESSOR__CHARGE),
        EventType.Name(EventType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHODS__LIST),
        EventType.Name(EventType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHODS__ADD),
        EventType.Name(EventType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHODS__REMOVE),
    ]

    TYPE: PaymentProcessorMetadata.PaymentProcessorType

    @property
    def identifier(self) -> str:
        """The application identifier."""
        identifier = f"{self.__class__.__module__}:{self.__class__.__qualname__}"

        return base64.b64encode(identifier.encode("utf-8")).decode("utf-8")

    def compute(self) -> list[Effect]:
        """Compute the effects to be applied."""
        if self.event.type == EventType.REVENUE__PAYMENT_PROCESSOR__LIST and (
            "payment_type" not in self.event.context
            or self.event.context["payment_type"] == self.TYPE
        ):
            return [self.metadata().apply()]
        elif self.event.type == EventType.REVENUE__PAYMENT_PROCESSOR__SELECTED:
            effects = self._on_payment_processor_selected()
            return effects
        elif self.event.type == EventType.REVENUE__PAYMENT_PROCESSOR__CHARGE:
            effect = self._charge()
            return [effect] if effect else []
        elif self.event.type == EventType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHODS__LIST:
            # This event is used to list payment methods, which may not be applicable for all processors.
            # Subclasses should override this method if they support listing payment methods.
            return self._payment_methods()
        elif self.event.type == EventType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHODS__ADD:
            effect = self._add_payment_method()
            return [effect] if effect else []
        elif self.event.type == EventType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHODS__REMOVE:
            effect = self._remove_payment_method()
            return [effect] if effect else []

        return []

    def metadata(self) -> PaymentProcessorMetadata:
        """Return information about the payment processor."""
        return PaymentProcessorMetadata(identifier=self.identifier, type=self.TYPE)

    def _on_payment_processor_selected(self) -> list[Effect]:
        """Handle the event when a payment processor is selected."""
        # This method should be overridden by subclasses to handle specific logic
        # when a payment processor is selected.
        return []

    def _charge(self) -> Effect | None:
        """Handle the event when a charge is made."""
        # This method should be overridden by subclasses to handle specific logic
        # when a charge is made.
        return None

    def _payment_methods(self) -> list[Effect]:
        """List payment methods for the processor."""
        # This method should be overridden by subclasses if they support listing payment methods.
        return []

    def _add_payment_method(self) -> Effect | None:
        """Handle the event when a payment method is added."""
        # This method should be overridden by subclasses to handle specific logic
        # when a payment method is added.
        return None

    def _remove_payment_method(self) -> Effect | None:
        """Handle the event when a payment method is removed."""
        # This method should be overridden by subclasses to handle specific logic
        # when a payment method is removed.
        return None


__exports__ = ("PaymentProcessor",)
