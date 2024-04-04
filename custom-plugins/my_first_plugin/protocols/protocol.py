import json
from typing import TYPE_CHECKING

from canvas_sdk.commands import PlanCommand

from canvas_sdk.effects import Effect


class Protocol:
    RESPONDS_TO = "ASSESS_COMMAND__CONDITION_SELECTED"

    NARRATIVE_STRING = "zombie"

    def __init__(self, event) -> None:
        self.event = event
        self.payload = json.loads(event.target)

    def compute(self) -> list[Effect]:
        plan = PlanCommand(
            note_id=self.payload["note"]["uuid"],
            narrative=self.NARRATIVE_STRING,
            user_id=123
        )
        return [plan.originate()]
