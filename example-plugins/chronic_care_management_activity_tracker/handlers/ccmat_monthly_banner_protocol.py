import arrow

from canvas_sdk.effects import Effect
from canvas_sdk.effects.banner_alert import AddBannerAlert
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.questionnaire import Questionnaire, Interview
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

    def compute(self) -> list[Effect]:
        """Add the patient's monthly banner alert for Chronic Care Management."""
        questionnaire = Questionnaire.objects.filter(code=self.QUESTIONNAIRE_CODE).first()
        if not questionnaire:
            log.info(f"No questionnaire found with code {self.QUESTIONNAIRE_CODE}")
            return []

        is_bulk_operation = self.event.type in [EventType.PLUGIN_CREATED, EventType.PLUGIN_UPDATED]

        if is_bulk_operation:
            # Get all active patients with interviews for this questionnaire
            active_patients = Patient.objects.filter(active=True)

            effects = []
            for patient in active_patients:
                interviews = patient.interviews.filter(questionnaires=questionnaire)

                if not interviews.exists():
                    continue

                time_spent = self._calculate_time_spent(interviews)
                log.info(f"Total time spent for patient {patient.id} is {time_spent}")

                banner = AddBannerAlert(
                    key=self.TEMPLATE_KEY,
                    narrative=f"Chronic Care Management Recorded This Month: {time_spent}",
                    placement=[AddBannerAlert.Placement.CHART, AddBannerAlert.Placement.PROFILE],
                    intent=AddBannerAlert.Intent.INFO,
                    patient_id=patient.id,
                )
                effects.append(banner.apply())

            return effects
        else:
            # Single patient operation
            patient = Patient.objects.get(id=self.target)
            interviews = patient.interviews.filter(questionnaires=questionnaire)

            if not interviews.exists():
                log.info(f"No interviews found for questionnaire {self.QUESTIONNAIRE_CODE} and patient {patient.id}")
                return []

            time_spent = self._calculate_time_spent(interviews)
            log.info(f"Total time spent for patient {self.target} is {time_spent}")

            banner = AddBannerAlert(
                key=self.TEMPLATE_KEY,
                narrative=f"Chronic Care Management Recorded This Month: {time_spent}",
                placement=[AddBannerAlert.Placement.CHART, AddBannerAlert.Placement.PROFILE],
                intent=AddBannerAlert.Intent.INFO,
                patient_id=self.target,
            )

            return [banner.apply()]

    def _calculate_time_spent(self, interviews: list[Interview]) -> str:
        """Calculate total time spent from interview responses in hh:mm:ss format."""
        total_seconds = 0
        for interview in interviews:
            for response in interview.interview_responses.filter(question__code="ccm_session_duration_question"):
                time_str = response.response_option_value.strip()
                # Parse hh:mm:ss format using arrow
                if ":" in time_str:
                    try:
                        # Parse as time using arrow
                        time_obj = arrow.get(f"2000-01-01 {time_str}", "YYYY-MM-DD HH:mm:ss")
                        # Extract hours, minutes, seconds from the parsed time
                        total_seconds += time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
                    except (ValueError, arrow.parser.ParserError):
                        log.warning(f"Invalid time format: {time_str}")

        # Convert back to hh:mm:ss format
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
