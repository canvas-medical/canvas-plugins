"""Constants for CMS130v14 Colorectal Cancer Screening protocol."""

from canvas_sdk.commands.constants import CodeSystems

# Age range for the measure
AGE_RANGE_START = 46
AGE_RANGE_END = 75

# Screening intervals in days
SCREENING_INTERVALS_DAYS = {
    "FOBT": 365,
    "FIT-DNA": 730,  # 2 years
    "Flexible sigmoidoscopy": 1460,  # 4 years
    "CT Colonography": 1460,  # 4 years
    "Colonoscopy": 3285,  # 9 years
}

# Screening lookback periods in years
SCREENING_LOOKBACK_YEARS = {
    "FOBT": 1,
    "FIT-DNA": 2,
    "Flexible sigmoidoscopy": 4,
    "CT Colonography": 4,
    "Colonoscopy": 9,
}

# SNOMED codes for hospice discharge dispositions
DISCHARGE_TO_HOME_HOSPICE_SNOMED = "428361000124107"
DISCHARGE_TO_FACILITY_HOSPICE_SNOMED = "428371000124100"

# Code system identifiers
LOINC_SYSTEM_IDENTIFIERS = ["LOINC", CodeSystems.LOINC]
SNOMED_SYSTEM_IDENTIFIERS = ["SNOMED", "SNOMEDCT", "http://snomed.info/sct"]

# LOINC codes
HOUSING_STATUS_LOINC = "71802-3"
PALLIATIVE_CARE_ASSESSMENT_LOINC = "71007-9"

# SNOMED codes
LIVES_IN_NURSING_HOME_SNOMED = "160734000"

# ICD-10 codes
SCREENING_DIAGNOSIS_CODE = "Z1211"

# Screening context for protocol cards
SCREENING_CONTEXT = {
    "conditions": [
        [
            {
                "code": SCREENING_DIAGNOSIS_CODE,
                "system": "ICD-10",
                "display": "Encounter for screening for malignant neoplasm of colon",
            }
        ]
    ]
}
