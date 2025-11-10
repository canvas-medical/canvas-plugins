from ..value_set import ValueSet


class DiabeticRetinopathySeverityLevel(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for Diabetic Retinopathy Severity Level.

    **Data Element Scope:** This value set may use a model element related to Diabetic Retinopathy Severity Level.

    **Inclusion Criteria:** Includes concepts that represent severe, mild, moderate or no (non) proliferative retinopathy.

    **Exclusion Criteria:**  None

    ** Used in:** CMS131v14
    """

    VALUE_SET_NAME = "Diabetic Retinopathy Severity Level"
    OID = "2.16.840.1.113883.3.464.1003.1266"
    DEFINITION_VERSION = "20250109"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "LA186439",  # No apparent retinopathy
        "LA186447",  # Mild non-proliferative retinopathy
        "LA186454",  # Moderate non-proliferative retinopathy
        "LA186462",  # Severe non-proliferative retinopathy
        "LA186488",  # Proliferative retinopathy
    }


class AutonomousEyeExamResultOrFinding(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for an Autonomous Eye Exam Result or Finding.

    **Data Element Scope:** This value set was intended to identify patients who had a Autonomous Eye Exam Result or Finding.

    **Inclusion Criteria:** Includes codes that identify an Autonomous Eye Exam Result or Findings.

    **Exclusion Criteria:** Exclude order only codes and code that indicate narrative reports.

    ** Used in:** CMS131v14
    """

    VALUE_SET_NAME = "Autonomous Eye Exam Result or Finding"
    OID = "2.16.840.1.113883.3.464.1004.2616"
    DEFINITION_VERSION = "20250130"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "LA343980",  # ETDRS Level 20 or lower, without macular edema
        "LA343998",  # ETDRS Level 35 or higher, with or without macular edema
    }


__exports__ = (
    "AutonomousEyeExamResultOrFinding",
    "DiabeticRetinopathySeverityLevel",
)