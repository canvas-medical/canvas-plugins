from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from canvas_sdk.templates import render_to_string


class ValidTemplate(BaseHandler):
    """Handler used in unit tests."""

    RESPONDS_TO = [EventType.Name(EventType.UNKNOWN)]

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        return [
            Effect(type=EffectType.LOG, payload=render_to_string("templates/template.html", None))
        ]


class TemplateInheritance(BaseHandler):
    """Handler used in unit tests."""

    RESPONDS_TO = [EventType.Name(EventType.UNKNOWN)]

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        return [
            Effect(
                type=EffectType.LOG, payload=render_to_string("templates/inheritence.html", None)
            )
        ]


class InvalidTemplate(BaseHandler):
    """Handler used in unit tests."""

    RESPONDS_TO = [EventType.Name(EventType.UNKNOWN)]

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        return [
            Effect(type=EffectType.LOG, payload=render_to_string("templates/template1.html", None))
        ]


class ForbiddenTemplate(BaseHandler):
    """Handler used in unit tests."""

    RESPONDS_TO = [EventType.Name(EventType.UNKNOWN)]

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        return [
            Effect(
                type=EffectType.LOG,
                payload=render_to_string("../../templates/template.html", None),
            )
        ]
