from canvas_sdk.effects import Effect
from canvas_sdk.effects.usage import RecordUsage
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler


class Handler(BaseHandler):
    """Test fixture: records usage in a priced unit, an unpriced one and the token unit."""

    RESPONDS_TO = EventType.Name(EventType.UNKNOWN)

    def compute(self) -> list[Effect]:
        """One record of each kind."""
        return [
            RecordUsage(unit="  VISIT ", key="visit:1").apply(),
            RecordUsage(unit="minute", key="minute:1", quantity=5).apply(),
            RecordUsage(unit="token", key="token:1").apply(),
        ]
