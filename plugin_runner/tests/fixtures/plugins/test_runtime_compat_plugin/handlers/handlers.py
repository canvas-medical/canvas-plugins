from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from test_runtime_compat_plugin.helpers import patterns


class _PatternHandler(BaseHandler):
    """Runs one helper pattern and logs its result."""

    RESPONDS_TO = EventType.Name(EventType.UNKNOWN)
    PATTERN = ""

    def compute(self) -> list[Effect]:
        """Run the pattern."""
        return [Effect(type=EffectType.LOG, payload=getattr(patterns, self.PATTERN)())]


class SuperCall(_PatternHandler):
    """super() reaching a parent's underscore method."""

    PATTERN = "super_call"


class BuiltinsInUse(_PatternHandler):
    """NotImplemented, bytearray and format."""

    PATTERN = "builtins_in_use"


class NumbersAndFrames(_PatternHandler):
    """Number rounding methods and frame line numbers."""

    PATTERN = "numbers_and_frames"


class FuzzyMatch(_PatternHandler):
    """rapidfuzz submodule functions."""

    PATTERN = "fuzzy_match"


class ListItemAssignment(_PatternHandler):
    """Item assignment with a method-named index variable."""

    PATTERN = "list_item_assignment"


class MissingRelation(_PatternHandler):
    """An AttributeError subclass caught by its own type."""

    PATTERN = "missing_relation"


class ModelMeta(_PatternHandler):
    """SDK model field introspection."""

    PATTERN = "model_meta"


class ExceptionAncestry(_PatternHandler):
    """An exception class's __mro__."""

    PATTERN = "exception_ancestry"


class ErrorReporting(_PatternHandler):
    """Naming an error's type in a report, past an except clause that does not match."""

    PATTERN = "error_reporting"


class Introspection(_PatternHandler):
    """Listing a module's names, a lazy statistics import, and copying a docstring."""

    PATTERN = "introspection"
