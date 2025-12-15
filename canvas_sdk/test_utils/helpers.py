"""Helper functions for creating test data in Canvas plugin tests."""

from datetime import date
from typing import Any, TypeVar
from unittest.mock import Mock

import arrow

from canvas_sdk.commands.constants import CodeSystems
from canvas_sdk.protocols.clinical_quality_measure import ClinicalQualityMeasure
from canvas_sdk.protocols.timeframe import Timeframe
from canvas_sdk.test_utils.factories import (
    BillingLineItemFactory,
    ConditionCodingFactory,
    ConditionFactory,
    ImagingReportCodingFactory,
    ImagingReportFactory,
    NoteFactory,
    ObservationFactory,
    ObservationValueCodingFactory,
)
from canvas_sdk.v1.data.billing import BillingLineItem
from canvas_sdk.v1.data.condition import Condition
from canvas_sdk.v1.data.imaging import ImagingReport
from canvas_sdk.v1.data.note import Note
from canvas_sdk.v1.data.observation import Observation
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.value_set.value_set import CodeConstants, ValueSet

_CQM = TypeVar("_CQM", bound=ClinicalQualityMeasure)


def create_protocol_instance(
    protocol_class: type[_CQM],
    timeframe_start: arrow.Arrow | None = None,
    timeframe_end: arrow.Arrow | None = None,
) -> _CQM:
    """
    Create a protocol instance with a custom timeframe for testing.

    This helper is useful for testing Clinical Quality Measures with specific
    measurement periods. It properly overrides the timeframe property which is
    normally derived from the protocol's configuration.

    Args:
        protocol_class: The ClinicalQualityMeasure class to instantiate.
        timeframe_start: Optional start date for the measurement period.
            Defaults to one year before timeframe_end.
        timeframe_end: Optional end date for the measurement period.
            Defaults to now.

    Returns:
        An instance of the protocol with the specified timeframe.

    Example:
        >>> from canvas_sdk.protocols.clinical_quality_measure import ClinicalQualityMeasure
        >>>
        >>> # Create protocol with default timeframe (last year)
        >>> protocol = create_protocol_instance(MyCQM)
        >>>
        >>> # Create protocol with specific measurement period
        >>> start = arrow.get("2023-01-01")
        >>> end = arrow.get("2023-12-31")
        >>> protocol = create_protocol_instance(MyCQM, start, end)
        >>> assert protocol.timeframe.start == start
        >>> assert protocol.timeframe.end == end
    """
    # Set timeframe (default to current year)
    if timeframe_end is None:
        timeframe_end = arrow.now()
    if timeframe_start is None:
        timeframe_start = timeframe_end.shift(years=-1)

    # Create a custom timeframe to return
    custom_timeframe = Timeframe(start=timeframe_start, end=timeframe_end)

    # Create a dynamic subclass that overrides the timeframe property.
    # Python property descriptors take precedence over instance __dict__ entries,
    # so we need to override at the class level to properly replace the property.
    class CustomTimeframeProtocol(protocol_class):  # type: ignore[valid-type, misc]
        @property
        def timeframe(self) -> Timeframe:
            return custom_timeframe

    # Create mock event
    mock_event = Mock()
    mock_event.type = 1

    # Instantiate the customized protocol
    protocol = CustomTimeframeProtocol(event=mock_event)

    # Set now for consistency
    protocol.now = timeframe_end

    return protocol


def create_condition_with_coding(
    patient: Patient,
    value_set_class: type[ValueSet],
    onset_date: date | arrow.Arrow | None = None,
    surgical: bool = True,
    **kwargs: Any,
) -> Condition:
    """
    Create a Condition with proper ConditionCoding from a ValueSet.

    This helper automatically selects the first available code from the ValueSet
    and creates the appropriate ConditionCoding with the correct system URL. This
    ensures that the condition will be found by ValueSet queries.

    Args:
        patient: The patient for this condition.
        value_set_class: ValueSet class containing the codes to use.
        onset_date: Date of onset. Defaults to today. Can be a date or arrow object.
        surgical: Whether this is a surgical condition. Defaults to True.
        **kwargs: Additional fields to pass to ConditionFactory.

    Returns:
        Condition instance with associated ConditionCoding.

    Example:
        >>> from canvas_sdk.value_set.v2022.condition import Diabetes
        >>>
        >>> condition = create_condition_with_coding(
        ...     patient=patient,
        ...     value_set_class=Diabetes,
        ...     onset_date=arrow.get("2023-01-15").date()
        ... )
        >>>
        >>> # The condition will have a ConditionCoding that matches the ValueSet
        >>> assert condition.codings.exists()
        >>>
        >>> # It will be found by ValueSet queries
        >>> from canvas_sdk.v1.data.condition import Condition
        >>> found = Condition.objects.filter(patient=patient).find(Diabetes)
        >>> assert condition in found
    """
    # Convert onset_date to date object if it's an arrow object
    if onset_date is None:
        onset_date = arrow.now().date()
    elif hasattr(onset_date, "date"):
        onset_date = onset_date.date()

    # For ongoing conditions, use a date far in the future
    resolution_date = kwargs.pop("resolution_date", arrow.get("9999-12-31").date())

    # Create condition using factory
    condition = ConditionFactory.create(
        patient=patient,
        onset_date=onset_date,
        resolution_date=resolution_date,
        surgical=surgical,
        **kwargs,
    )

    # Add coding if value set has codes
    # values is a dict of {code_constant: set[code]}
    # We need to map code_constant to the actual system URL
    if hasattr(value_set_class, "values") and value_set_class.values:
        for code_constant, codes in value_set_class.values.items():
            if codes:
                # Map code constant to system URL using CODE_SYSTEM_MAPPING
                system_url = value_set_class.CODE_SYSTEM_MAPPING.get(code_constant)
                if system_url:
                    # Get first code from the set
                    code = next(iter(codes))
                    ConditionCodingFactory.create(
                        condition=condition,
                        system=system_url,
                        code=code,
                    )
                    # Only need one coding for testing
                    break

    return condition


def create_encounter_with_billing(
    patient: Patient,
    encounter_date: date | arrow.Arrow,
    value_set_class: type[ValueSet] | None = None,
    cpt_code: str | None = None,
) -> tuple[Note, BillingLineItem]:
    """
    Create an encounter (Note) with associated BillingLineItem.

    This helper creates both a Note and a BillingLineItem with the appropriate
    CPT/HCPCS code from a ValueSet. This is useful for testing protocols that
    require qualifying encounters.

    Args:
        patient: The patient for this encounter.
        encounter_date: Date of the encounter. Can be a date or arrow object.
        value_set_class: Optional ValueSet class containing CPT/HCPCS codes.
            If provided, uses the first code from the ValueSet.
        cpt_code: Optional explicit CPT code. If not provided, extracts from
            value_set_class. If neither is provided, defaults to "99213".

    Returns:
        A tuple of (Note, BillingLineItem).

    Example:
        >>> from canvas_sdk.value_set.v2022.encounter import OfficeVisit
        >>>
        >>> # Create encounter with ValueSet
        >>> note, billing = create_encounter_with_billing(
        ...     patient=patient,
        ...     encounter_date=arrow.get("2023-06-15"),
        ...     value_set_class=OfficeVisit
        ... )
        >>>
        >>> # Create encounter with explicit CPT code
        >>> note, billing = create_encounter_with_billing(
        ...     patient=patient,
        ...     encounter_date=arrow.now().shift(days=-30),
        ...     cpt_code="99214"
        ... )
    """
    # Extract CPT/HCPCS code from value set if not explicitly provided
    if (
        cpt_code is None
        and value_set_class is not None
        and hasattr(value_set_class, "values")
        and value_set_class.values
    ):
        # Try HCPCS first (what BillingLineItem.find() looks for)
        if CodeConstants.HCPCS in value_set_class.values:
            codes = value_set_class.values[CodeConstants.HCPCS]
            if codes:
                cpt_code = next(iter(codes))

        # If no HCPCS, try CPT codes
        if not cpt_code and CodeConstants.CPT in value_set_class.values:
            codes = value_set_class.values[CodeConstants.CPT]
            if codes:
                cpt_code = next(iter(codes))

    # If no CPT code found, use a generic one
    if not cpt_code:
        cpt_code = "99213"  # Office visit code

    # Convert encounter_date to datetime if needed
    if hasattr(encounter_date, "datetime"):
        encounter_datetime = encounter_date.datetime
    elif hasattr(encounter_date, "date"):
        # It's a datetime.date, convert to arrow then to datetime
        encounter_datetime = arrow.get(encounter_date).datetime
    else:
        # Assume it's already a datetime
        encounter_datetime = encounter_date

    # Create a note with datetime_of_service using factory
    note = NoteFactory.create(
        patient=patient,
        datetime_of_service=encounter_datetime,
    )

    # Create billing line item using factory
    billing_item = BillingLineItemFactory.create(
        patient=patient,
        note=note,
        cpt=cpt_code,
    )

    return note, billing_item


def create_imaging_report_with_coding(
    patient: Patient,
    value_set_class: type[ValueSet],
    original_date: date | arrow.Arrow | None = None,
    result_date: date | arrow.Arrow | None = None,
    **kwargs: Any,
) -> ImagingReport:
    """
    Create an ImagingReport with proper ImagingReportCoding from a ValueSet.

    This helper automatically selects the first available code from the ValueSet
    and creates the appropriate ImagingReportCoding with the correct system URL.
    This ensures that the imaging report will be found by ValueSet queries.

    Args:
        patient: The patient for this imaging report.
        value_set_class: ValueSet class containing the codes to use.
        original_date: Date of imaging. Defaults to today. Can be a date or arrow object.
        result_date: Date results available. Defaults to original_date.
        **kwargs: Additional fields to pass to ImagingReportFactory.

    Returns:
        ImagingReport instance with associated ImagingReportCoding.

    Example:
        >>> from canvas_sdk.value_set.v2022.procedure import Mammography
        >>>
        >>> report = create_imaging_report_with_coding(
        ...     patient=patient,
        ...     value_set_class=Mammography,
        ...     original_date=arrow.get("2023-01-15").date()
        ... )
        >>>
        >>> # The report will have an ImagingReportCoding that matches the ValueSet
        >>> assert report.codings.exists()
        >>>
        >>> # It will be found by ValueSet queries
        >>> from canvas_sdk.v1.data.imaging import ImagingReport
        >>> found = ImagingReport.objects.filter(patient=patient).find(Mammography)
        >>> assert report in found
    """
    # Convert dates to date objects if they're arrow objects
    if original_date is None:
        original_date = arrow.now().date()
    elif hasattr(original_date, "date"):
        original_date = original_date.date()

    if result_date is None:
        result_date = original_date
    elif hasattr(result_date, "date"):
        result_date = result_date.date()

    # Create imaging report using factory
    report = ImagingReportFactory.create(
        patient=patient,
        original_date=original_date,
        result_date=result_date,
        **kwargs,
    )

    # Add coding if value set has codes
    # values is a dict of {code_constant: set[code]}
    # We need to map code_constant to the actual system URL
    if hasattr(value_set_class, "values") and value_set_class.values:
        for code_constant, codes in value_set_class.values.items():
            if codes:
                # Map code constant to system URL using CODE_SYSTEM_MAPPING
                system_url = value_set_class.CODE_SYSTEM_MAPPING.get(code_constant)
                if system_url:
                    # Get first code from the set
                    code = next(iter(codes))
                    ImagingReportCodingFactory.create(
                        report=report,
                        system=system_url,
                        code=code,
                    )
                    # Only need one coding for testing
                    break

    return report


def create_observation_with_value_coding(
    patient: Patient,
    snomed_code: str,
    effective_datetime: arrow.Arrow | None = None,
    display: str = "Test observation value",
    **kwargs: Any,
) -> Observation:
    """
    Create an Observation with proper ObservationValueCoding using a SNOMED code.

    Args:
        patient: The patient for this observation.
        snomed_code: The SNOMED code for the observation value.
        effective_datetime: When the observation was made. Defaults to now.
        display: Display text for the coding. Defaults to "Test observation value".
        **kwargs: Additional fields to pass to ObservationFactory.

    Returns:
        Observation instance with associated ObservationValueCoding.
    """
    if effective_datetime is None:
        effective_datetime = arrow.now()

    if hasattr(effective_datetime, "datetime"):
        effective_dt = effective_datetime.datetime
    else:
        effective_dt = effective_datetime

    observation = ObservationFactory.create(
        patient=patient,
        effective_datetime=effective_dt,
        **kwargs,
    )

    ObservationValueCodingFactory.create(
        observation=observation,
        system=CodeSystems.SNOMED,
        code=snomed_code,
        display=display,
    )

    return observation


__exports__ = (
    "create_condition_with_coding",
    "create_encounter_with_billing",
    "create_imaging_report_with_coding",
    "create_observation_with_value_coding",
    "create_protocol_instance",
)
