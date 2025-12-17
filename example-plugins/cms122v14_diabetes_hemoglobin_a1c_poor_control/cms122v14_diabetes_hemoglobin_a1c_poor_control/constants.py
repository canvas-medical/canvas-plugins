"""Constants for CMS122v14 Diabetes: Glycemic Status Assessment Greater Than 9% protocol."""

from canvas_sdk.commands.constants import CodeSystems

# Age range for the measure
AGE_RANGE_START = 18
AGE_RANGE_END = 75

# Glycemic threshold
GLYCEMIC_THRESHOLD = 9.0

# LOINC codes
GMI_LOINC_CODE = "97506-0"
PALLIATIVE_CARE_ASSESSMENT_LOINC = "71007-9"
HOSPICE_MDS_LOINC = "45755-6"
HOUSING_STATUS_LOINC = "71802-3"
MEDICAL_EQUIPMENT_LOINC = "98181-1"

# SNOMED codes
DISCHARGE_TO_HOME_HOSPICE_SNOMED = "428361000124107"
DISCHARGE_TO_FACILITY_HOSPICE_SNOMED = "428371000124100"
YES_QUALIFIER_SNOMED = "373066001"
LIVES_IN_NURSING_HOME_SNOMED = "160734000"

# Code system identifiers
LOINC_SYSTEM_IDENTIFIERS = ["LOINC", "http://loinc.org", CodeSystems.LOINC]
SNOMED_SYSTEM_IDENTIFIERS = ["SNOMED", "SNOMEDCT", "http://snomed.info/sct"]

# Protocol key
PROTOCOL_KEY = "CMS122v14"

# Test types
TEST_TYPE_GMI = "GMI"
TEST_TYPE_HBA1C = "HbA1c"

# Medical Nutrition Therapy codes
MNT_CPT_CODES = {"97802", "97803", "97804"}
MNT_HCPCS_CODES = {"G0270", "G0271"}

# Additional encounter SNOMED codes
ADDITIONAL_ENCOUNTER_SNOMED_CODES = {
    "308335008",
    "439708006",
    "185317003",
}

