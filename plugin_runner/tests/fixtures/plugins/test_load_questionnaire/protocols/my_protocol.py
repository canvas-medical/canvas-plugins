import json

from canvas_sdk.effects import Effect
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.questionnaires import from_yaml


class ValidQuestionnaire(BaseProtocol):
    """You should put a helpful description of this protocol's behavior here."""

    RESPONDS_TO = [EventType.Name(EventType.UNKNOWN)]

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        config = from_yaml("questionnaires/example_questionnaire.yml")
        return [Effect(payload=json.dumps(config))]


class InvalidQuestionnaire(BaseProtocol):
    """You should put a helpful description of this protocol's behavior here."""

    RESPONDS_TO = [EventType.Name(EventType.UNKNOWN)]

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        from_yaml("questionnaires/example_questionnaire1.yml")
        return []


class ForbiddenQuestionnaire(BaseProtocol):
    """You should put a helpful description of this protocol's behavior here."""

    RESPONDS_TO = [EventType.Name(EventType.UNKNOWN)]

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        from_yaml("../../questionnaires/example_questionnaire.yml")
        return []
