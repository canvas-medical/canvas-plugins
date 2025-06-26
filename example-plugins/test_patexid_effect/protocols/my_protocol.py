from canvas_sdk.effects.patient import CreatePatientExternalIdentifier
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.effects import Effect

class Protocol(BaseProtocol):
    RESPONDS_TO = EventType.Name(EventType.PATIENT_CREATED)

    def compute(self) -> list[Effect]:
        add_patient_exid_effect = CreatePatientExternalIdentifier(
            patient_id=self.target,
            value="1234567890",
            system="https://example.com/patient-external-identifier-test",
        )
        return [add_patient_exid_effect.create()]
