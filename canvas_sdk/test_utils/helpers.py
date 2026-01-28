"""Test helper functions for creating test data with codings and protocol instances."""

from datetime import date, datetime
from typing import Any
from unittest.mock import Mock

import arrow
from django.utils import timezone

from canvas_sdk.events import EventType
from canvas_sdk.v1.data.condition import ClinicalStatus, Condition, ConditionCoding
from canvas_sdk.v1.data.medication import Medication, MedicationCoding
from canvas_sdk.v1.data.medication import Status as MedicationStatus
from canvas_sdk.v1.data.patient import Patient

# Common code system URIs
SNOMED_CT_SYSTEM = "http://snomed.info/sct"
ICD10_CM_SYSTEM = "http://hl7.org/fhir/sid/icd-10-cm"
RXNORM_SYSTEM = "http://www.nlm.nih.gov/research/umls/rxnorm"
LOINC_SYSTEM = "http://loinc.org"
CPT_SYSTEM = "http://www.ama-assn.org/go/cpt"
HCPCS_SYSTEM = "https://www.cms.gov/Medicare/Coding/HCPCSReleaseCodeSets"

# Code system attribute to URI mapping
CODE_SYSTEM_MAP = {
    "SNOMEDCT": SNOMED_CT_SYSTEM,
    "ICD10CM": ICD10_CM_SYSTEM,
    "RXNORM": RXNORM_SYSTEM,
    "LOINC": LOINC_SYSTEM,
    "CPT": CPT_SYSTEM,
    "HCPCSLEVELII": HCPCS_SYSTEM,
}


def create_condition_with_coding(
    patient: Patient,
    value_set: Any,
    onset_date: date | None = None,
    resolution_date: date | None = None,
    clinical_status: str = ClinicalStatus.ACTIVE,
) -> Condition:
    """
    Create a Condition with associated ConditionCoding from a value set.

    Args:
        patient: The patient to associate with the condition.
        value_set: A value set class that has code attributes (SNOMEDCT, ICD10CM, etc.).
        onset_date: The onset date for the condition. Defaults to today.
        resolution_date: The resolution date for the condition. Defaults to a far future date.
        clinical_status: The clinical status. Defaults to ACTIVE.

    Returns:
        The created Condition instance.
    """
    if onset_date is None:
        onset_date = date.today()

    # For active conditions, use a far future date as resolution_date
    # This satisfies the NOT NULL constraint while representing an unresolved condition
    if resolution_date is None:
        resolution_date = date(9999, 12, 31)

    condition = Condition.objects.create(
        patient=patient,
        onset_date=onset_date,
        resolution_date=resolution_date,
        clinical_status=clinical_status,
        surgical=False,
        deleted=False,
    )

    # Find the first available code from supported code systems
    code = None
    system = None

    for attr_name, system_uri in CODE_SYSTEM_MAP.items():
        if hasattr(value_set, attr_name):
            codes_set = getattr(value_set, attr_name)
            if codes_set:
                codes = list(codes_set)
                if codes:
                    code = codes[0]
                    system = system_uri
                    break

    if code and system:
        ConditionCoding.objects.create(
            condition=condition,
            code=code,
            system=system,
            display=f"{value_set.__name__} condition",
        )

    return condition


def create_medication_with_coding(
    patient: Patient,
    code: str,
    system: str,
    start_date: date | None = None,
    end_date: date | None = None,
    display: str = "Test Medication",
    status: str = MedicationStatus.ACTIVE,
) -> Medication:
    """
    Create a Medication with associated MedicationCoding.

    Args:
        patient: The patient to associate with the medication.
        code: The medication code (e.g., RXNORM code).
        system: The code system URI (e.g., "http://www.nlm.nih.gov/research/umls/rxnorm").
        start_date: The start date for the medication. Defaults to today.
        end_date: The end date for the medication. Defaults to a far future date.
        display: The display name for the medication coding.
        status: The medication status. Defaults to ACTIVE.

    Returns:
        The created Medication instance.
    """
    if start_date is None:
        start_date = date.today()

    start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))

    # For active medications, use a far future date as end_date (but not too far to avoid overflow)
    if end_date is None:
        end_datetime = timezone.make_aware(datetime(2199, 12, 31, 23, 59, 59))
    else:
        end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))

    medication = Medication.objects.create(
        patient=patient,
        status=status,
        start_date=start_datetime,
        end_date=end_datetime,
        deleted=False,
        quantity_qualifier_description="",
        clinical_quantity_description="",
        potency_unit_code="",
        national_drug_code="",
        erx_quantity=0.0,
    )

    MedicationCoding.objects.create(
        medication=medication,
        code=code,
        system=system,
        display=display,
    )

    return medication


def create_protocol_instance(
    protocol_class: type,
    timeframe_start: arrow.Arrow | None = None,
    timeframe_end: arrow.Arrow | None = None,
    event_type: EventType = EventType.PATIENT_UPDATED,
    patient_id: str = "test-patient-id",
) -> Any:
    """
    Create a protocol instance for testing with a mock event.

    Args:
        protocol_class: The protocol class to instantiate.
        timeframe_start: The start of the measurement period. Defaults to 1 year ago.
        timeframe_end: The end of the measurement period. Defaults to now.
        event_type: The type of event to mock. Defaults to PATIENT_UPDATED.
        patient_id: The patient ID to use in the event context.

    Returns:
        The instantiated protocol with mocked event.
    """
    mock_event_request = Mock()
    mock_event_request.type = event_type
    mock_event_request.target = patient_id
    mock_event_request.target_type = "Patient"
    mock_event_request.context = f'{{"patient": {{"id": "{patient_id}"}}}}'
    mock_event_request.actor = None
    mock_event_request.source = "test"

    from canvas_sdk.events import Event

    event = Event(mock_event_request)

    protocol = protocol_class(event=event)

    if timeframe_start is not None or timeframe_end is not None:
        now = timeframe_end or arrow.utcnow()
        start = timeframe_start or now.shift(years=-1)

        protocol.now = now

        from canvas_sdk.protocols.timeframe import Timeframe

        custom_timeframe = Timeframe(start=start, end=now)

        object.__setattr__(protocol, "_custom_timeframe", custom_timeframe)

        original_class = type(protocol)

        class _ProtocolWithCustomTimeframe(original_class):  # type: ignore[valid-type, misc]
            @property
            def timeframe(self) -> Timeframe:
                return self._custom_timeframe

        protocol.__class__ = _ProtocolWithCustomTimeframe

    return protocol


def set_protocol_patient_context(protocol: Any, patient_id: str) -> None:
    """
    Set patient context and target ID in a protocol's event for testing.

    This updates both event.context and event.target.id to match the given patient_id.

    Args:
        protocol: The protocol instance to update.
        patient_id: The patient ID to set.
    """
    protocol.event.context = {"patient": {"id": str(patient_id)}}
    protocol.event.target.id = str(patient_id)


__all__ = (
    # Constants
    "CODE_SYSTEM_MAP",
    "CPT_SYSTEM",
    "HCPCS_SYSTEM",
    "ICD10_CM_SYSTEM",
    "LOINC_SYSTEM",
    "RXNORM_SYSTEM",
    "SNOMED_CT_SYSTEM",
    # Functions
    "create_condition_with_coding",
    "create_medication_with_coding",
    "create_protocol_instance",
    "set_protocol_patient_context",
)
