from ..value_set import ValueSet


class FecalOccultBloodTestFobt(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for fecal occult blood tests.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for occult blood in stool.

    **Exclusion Criteria:** Excludes concepts that represent an order only and test for occult blood in other body fluids.

    ** Used in:** CMS130v14
    """

    VALUE_SET_NAME = "Fecal Occult Blood Test (FOBT)"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1011"
    DEFINITION_VERSION = "20171219"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "12503-9",  # Hemoglobin.gastrointestinal [Presence] in Stool --4th specimen
        "12504-7",  # Hemoglobin.gastrointestinal [Presence] in Stool --5th specimen
        "14563-1",  # Hemoglobin.gastrointestinal [Presence] in Stool --1st specimen
        "14564-9",  # Hemoglobin.gastrointestinal [Presence] in Stool --2nd specimen
        "14565-6",  # Hemoglobin.gastrointestinal [Presence] in Stool --3rd specimen
        "2335-8",  # Hemoglobin.gastrointestinal [Presence] in Stool
        "27396-1",  # Hemoglobin.gastrointestinal [Mass/mass] in Stool
        "27401-9",  # Hemoglobin.gastrointestinal [Presence] in Stool --6th specimen
        "27925-7",  # Hemoglobin.gastrointestinal [Presence] in Stool --7th specimen
        "27926-5",  # Hemoglobin.gastrointestinal [Presence] in Stool --8th specimen
        "29771-3",  # Hemoglobin.gastrointestinal.lower [Presence] in Stool by Immunoassay
        "56490-6",  # Hemoglobin.gastrointestinal.lower [Presence] in Stool by Immunoassay --2nd specimen
        "56491-4",  # Hemoglobin.gastrointestinal.lower [Presence] in Stool by Immunoassay --3rd specimen
        "57905-2",  # Hemoglobin.gastrointestinal.lower [Presence] in Stool by Immunoassay --1st specimen
        "58453-2",  # Hemoglobin.gastrointestinal.lower [Mass/volume] in Stool by Immunoassay
        "80372-6",  # Hemoglobin.gastrointestinal [Presence] in Stool by Rapid immunoassay
    }

class SdnaFitTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for colorectal cancer screening tests that include a combination of stool DNA and fecal immunochemical testing.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent colorectal cancer screening tests that include a combination of stool DNA and fecal immunochemical testing.

    **Exclusion Criteria:** Excludes concepts that represent an order only.

    ** Used in:** CMS130v14
    """

    VALUE_SET_NAME = "sDNA FIT Test"
    OID = "2.16.840.1.113883.3.464.1003.108.12.1039"
    DEFINITION_VERSION = "20171219"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "77353-1",  # Noninvasive colorectal cancer DNA and occult blood screening [Interpretation] in Stool Narrative
        "77354-9",  # Noninvasive colorectal cancer DNA and occult blood screening [Presence] in Stool
    }


__exports__ = (
    "FecalOccultBloodTestFobt",
    "SdnaFitTest",
)
