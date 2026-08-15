"""The correct form of every construct in `violations.py`.

This half of the fixture guards the other direction: the lint must stay silent
here. Without it, a rule that over-matches would still look like it passes,
because the violations file would go on reporting the codes it expects.
"""

from dataclasses import dataclass

from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler


@dataclass(frozen=True)
class Frozen:
    """@dataclass(frozen=True) loads fine in the sandbox and must not be flagged."""

    x: int = 0


@dataclass(slots=True)
class Slotted:
    """@dataclass(slots=True) loads fine in the sandbox and must not be flagged."""

    y: int = 0


class Handler(BaseHandler):
    """Handler that does the same work without any rejected construct."""

    RESPONDS_TO = EventType.Name(EventType.PATIENT_CREATED)

    def compute(self) -> list:
        """Mirror violations.py using only constructs the sandbox accepts."""
        obj = _Target()
        counts = {"a": 1}
        items = [1, 2, 3]

        # Augmented assignment to a plain variable is fine.
        tally = 0
        tally += 1

        # Attribute and item writes: explicit reassignment instead.
        obj.total = obj.total + 1
        counts["a"] = counts["a"] + 1
        items[0] = items[0] + 1

        # Reading a type: isinstance() and __class__.__name__ instead of type().
        is_target = isinstance(obj, _Target)
        kind_name = obj.__class__.__name__

        # Direct assignment and del instead of setattr()/delattr().
        obj.flag = True
        del obj.flag

        # bytes instead of bytearray.
        buffer = b"x"

        return [tally, is_target, kind_name, buffer, Frozen(1), Slotted(2)]


class _Target:
    """Plain plugin-defined class, used as the target of the writes above.

    ``flag`` is declared here rather than created on the fly so the assignment
    and ``del`` in ``compute`` type-check.
    """

    def __init__(self) -> None:
        self.total = 0
        self.flag = False
