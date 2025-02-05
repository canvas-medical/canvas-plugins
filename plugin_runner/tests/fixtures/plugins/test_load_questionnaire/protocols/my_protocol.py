import json

from canvas_sdk.effects import Effect
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.questionnaires import questionnaire_from_yaml


class ValidQuestionnaire(BaseHandler):
    """You should put a helpful description of this protocol's behavior here."""

    RESPONDS_TO = [EventType.Name(EventType.UNKNOWN)]

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        config = questionnaire_from_yaml("questionnaires/example_questionnaire.yml")
        return [Effect(payload=json.dumps(config))]


class InvalidQuestionnaire(BaseHandler):
    """You should put a helpful description of this protocol's behavior here."""

    RESPONDS_TO = [EventType.Name(EventType.UNKNOWN)]

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        questionnaire_from_yaml("questionnaires/example_questionnaire1.yml")
        return []


class ForbiddenQuestionnaire(BaseHandler):
    """You should put a helpful description of this protocol's behavior here."""

    RESPONDS_TO = [EventType.Name(EventType.UNKNOWN)]

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        questionnaire_from_yaml("../../questionnaires/example_questionnaire.yml")
        return []
