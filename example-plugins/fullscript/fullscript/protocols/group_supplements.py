from canvas_sdk.effects import Effect
from canvas_sdk.effects.group import Group
from canvas_sdk.effects.patient_chart_group import PatientChartGroup
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler

class GroupSupplements(BaseHandler):
    """Groups supplement medications together in the patient summary chart."""

    RESPONDS_TO = EventType.Name(EventType.PATIENT_CHART__MEDICATIONS)

    def compute(self) -> list[Effect]:
        """
        Groups supplement medications together in the patient summary chart.
        """
        groups: dict[str, Group] = {}
        groups.setdefault("Supplements", Group(priority=100, items=[], name="Supplements"))

        for medication in self.event.context:
            for coding in medication["codings"]:
                if coding["code"].startswith("fullscript-"):
                    groups["Supplements"].items.append(medication)

        return [PatientChartGroup(items=groups).apply()]
