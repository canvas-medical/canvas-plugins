"""Re-export SDK test utilities for use in plugin tests.

This module provides a convenient way to import test utilities from the Canvas SDK.
Instead of defining custom helpers, we re-export the SDK's helpers which provide
the same functionality with better documentation and maintenance.

Usage:
    from cms125v14_breast_cancer_screening.canvas_sdk_test_utils import (
        create_condition_with_coding,
        create_imaging_report_with_coding,
        create_protocol_instance,
        create_qualifying_visit,
    )
"""

from canvas_sdk.test_utils.factories import (
    BillingLineItemFactory,
    ConditionCodingFactory,
    ConditionFactory,
    ImagingReportCodingFactory,
    ImagingReportFactory,
    NoteFactory,
    PatientFactory,
)
from canvas_sdk.test_utils.helpers import (
    create_condition_with_coding,
    create_imaging_report_with_coding,
    create_protocol_instance,
)
from canvas_sdk.test_utils.helpers import (
    create_encounter_with_billing as create_qualifying_visit,
)

__all__ = [
    # Factories
    "BillingLineItemFactory",
    "ConditionCodingFactory",
    "ConditionFactory",
    "ImagingReportCodingFactory",
    "ImagingReportFactory",
    "NoteFactory",
    "PatientFactory",
    # Helpers (re-exported from SDK)
    "create_condition_with_coding",
    "create_imaging_report_with_coding",
    "create_protocol_instance",
    "create_qualifying_visit",
]
