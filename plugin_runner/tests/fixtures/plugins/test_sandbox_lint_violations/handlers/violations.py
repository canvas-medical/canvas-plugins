"""Every construct `canvas validate` should reject, one per line.

Deliberately invalid. This file is a lint fixture, not example code — do not
copy anything out of it. Each line below is annotated with the lint code it
must produce; `clean.py` in this package holds the correct form of each.
"""

from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler


class Handler(BaseHandler):
    """Handler whose body contains one of each rejected construct."""

    RESPONDS_TO = EventType.Name(EventType.PATIENT_CREATED)

    def compute(self) -> list:
        """Trip every construct rule in plugin_lint.py."""
        obj = _Target()
        counts = {"a": 1}
        items = [1, 2, 3]

        # augmented-attribute — rejected at compile time by the sandbox,
        # including on a class this plugin defines itself.
        obj.total += 1

        # augmented-subscript — dict item, list item, and slice.
        counts["a"] += 1
        items[0] += 1
        items[0:1] += [4]

        # type-blocked — three-argument dynamic class creation.
        made = type("Made", (object,), {})

        return [made]


class _Target:
    """Plain plugin-defined class, used as the target of the writes above."""

    def __init__(self) -> None:
        self.total = 0
