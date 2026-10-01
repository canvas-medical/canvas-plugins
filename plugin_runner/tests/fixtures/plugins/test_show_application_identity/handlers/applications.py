from canvas_sdk.effects import Effect
from canvas_sdk.effects.show_application import ShowApplicationEffect
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.handlers.application import ProviderMenuApplication

HONEST_IDENTIFIER = "test_show_application_identity__honest"


class Honest(ProviderMenuApplication):
    """A launcher that reports its own entry."""

    NAME = "Honest"
    IDENTIFIER = HONEST_IDENTIFIER

    def on_open(self) -> Effect | list[Effect]:
        """Launch nothing."""
        return []


class Impostor(ProviderMenuApplication):
    """A launcher that reports the honest launcher's identifier as its own entry."""

    NAME = "Impostor"
    IDENTIFIER = "test_show_application_identity__impostor"

    def compute(self) -> list[Effect]:
        """Report the honest launcher's entry in place of its own."""
        return [ShowApplicationEffect(name="Impostor", identifier=HONEST_IDENTIFIER).apply()]

    def on_open(self) -> Effect | list[Effect]:
        """Launch nothing."""
        return []


class Forger(BaseHandler):
    """A plain handler that reports the honest launcher's entry."""

    RESPONDS_TO = EventType.Name(EventType.APPLICATION__ON_CONTEXT_CHANGE)

    def compute(self) -> list[Effect]:
        """Hide the honest launcher."""
        return [
            ShowApplicationEffect(
                name="Forged", identifier=HONEST_IDENTIFIER, visible=False
            ).apply()
        ]
