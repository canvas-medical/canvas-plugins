from canvas_sdk.effects.banner_alert import AddBannerAlert
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.questionnaire import Questionnaire
from logger import log


class CcmatMonthlyBannerProtocol(BaseProtocol):
    """Handler to add the patient's monthly banner alert for Chronic Care Management."""
    RESPONDS_TO = [
        EventType.Name(EventType.PATIENT_UPDATED),
        EventType.Name(EventType.PLUGIN_CREATED),
        EventType.Name(EventType.PLUGIN_UPDATED),
    ]

    QUESTIONNAIRE_CODE = "ccm_session_questionnaire"

    TEMPLATE_KEY = "ccm_monthly_banner"

    def compute(self):
        """Add the patient's monthly banner alert for Chronic Care Management."""
        questionnaire = Questionnaire.objects.filter(
            code=self.QUESTIONNAIRE_CODE,
        ).first()

        if not questionnaire:
            log.info(f"No questionnaire found with code {self.QUESTIONNAIRE_CODE} for patient {self.target}")
            return []

        patient = Patient.objects.get(id=self.target)

        interviews = patient.interviews.filter(
            questionnaires=questionnaire
        )

        if not interviews.exists():
            log.info(f"No interviews found for questionnaire {self.QUESTIONNAIRE_CODE} and patient {patient.id}")
            return []

        time_spent = 0
        for interview in interviews:
            for response in interview.interview_responses.filter(
                question__code="ccm_session_duration_question"
            ):
                if response.response_option_value.isdigit():
                    time_spent += int(response.response_option_value)
        log.info(f"Total time spent for patient {self.target} is {time_spent} minutes")

        banner = AddBannerAlert(
            key=self.TEMPLATE_KEY,
            narrative=f"Chronic Care Management Recorded This Month: {time_spent} minutes",
            placement=[
                AddBannerAlert.Placement.CHART,
                AddBannerAlert.Placement.PROFILE,
            ],
            intent=AddBannerAlert.Intent.INFO,
        )

        if self.event.type in [EventType.PLUGIN_CREATED, EventType.PLUGIN_UPDATED]:
            banner.patient_filter = {"active": True}
        else:
            banner.patient_id = self.target

        return [banner.apply()]
