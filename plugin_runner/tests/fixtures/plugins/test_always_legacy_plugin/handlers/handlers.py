from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from test_always_legacy_plugin.helpers import patterns


class _PatternHandler(BaseHandler):
    """Runs one helper pattern and logs its result."""

    RESPONDS_TO = EventType.Name(EventType.UNKNOWN)
    PATTERN = ""

    def compute(self) -> list[Effect]:
        """Run the pattern."""
        return [Effect(type=EffectType.LOG, payload=getattr(patterns, self.PATTERN)())]


class PrivateSdkAttribute(_PatternHandler):
    """An SDK object's private attribute."""

    PATTERN = "private_sdk_attribute"


class LazilyImportedNonlocal(_PatternHandler):
    """nonlocal in a module imported at request time."""

    PATTERN = "lazily_imported_nonlocal"


class OwnModuleName(_PatternHandler):
    """__module__ on the plugin's own object."""

    PATTERN = "own_module_name"
