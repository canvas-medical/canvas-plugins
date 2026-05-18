from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler


class Handler(BaseHandler):
    """Test fixture: a handler whose compute() implicitly returns None.

    Plugin authors sometimes forget to return their effects list. The plugin
    runner must handle this gracefully without raising
    ``TypeError: 'NoneType' object is not iterable`` (KOALA-5365 / HOME-APP-RT8).
    """

    RESPONDS_TO = EventType.Name(EventType.UNKNOWN)

    def compute(self) -> None:  # type: ignore[override]
        """Forget to return anything — implicit None.

        The override is deliberate: this fixture exists to exercise the
        runner's fallback path when a handler misbehaves and returns None
        instead of the expected ``list[Effect]``.
        """
        return None
