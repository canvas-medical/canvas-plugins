from canvas_sdk.value_set._utilities import get_overrides

from ..value_set import ValueSet


class TobaccoUseScreening(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for assessments to screen for tobacco use.

    **Data Element Scope:** This value set may use a model element related to Assessment.

    **Inclusion Criteria:** Includes concepts that represent an assessment for tobacco use, including smoking and smoke-less tobacco products.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS138v10, CMS249v4
    """

    VALUE_SET_NAME = "Tobacco Use Screening"
    OID = "2.16.840.1.113883.3.526.3.1278"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "39240-7",  # Tobacco use status CPHS
        "68535-4",  # Have you used tobacco in the last 30 days [SAMHSA]
        "68536-2",  # Have you used smokeless tobacco product in the last 30 days [SAMHSA]
        "72166-2",  # Tobacco smoking status
    }


class FallsScreening(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for assessments using a falls screening tool.

    **Data Element Scope:** This value set may use a model element related to Assessment.

    **Inclusion Criteria:** Includes concepts that represent an assessment for fall risk.

    **Exclusion Criteria:** Excludes concepts that represent an assessment for falls for children.

    ** Used in:** CMS139v10
    """

    VALUE_SET_NAME = "Falls Screening"
    OID = "2.16.840.1.113883.3.464.1003.118.12.1028"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "52552-7",  # Falls in the past year [CMS Assessment]
        "57254-5",  # Standardized fall risk assessment was conducted [CMS Assessment]
        "59454-9",  # History of falling; immediate or within 3 months [Morse Fall Scale]
        "73830-2",  # Fall risk assessment
    }


class StandardizedToolsForAssessmentOfCognition(ValueSet):
    """
        **Clinical Focus:** The purpose of this value set is to define concepts for assessments representing total score results for standardized tools used for the evaluation of cognition.

        **Data Element Scope:** This value set may use a model element related to Assessment.

        **Inclusion Criteria:** Includes concepts that describe assessments with total score results for the following standardized tools:
    -Blessed Orientation-Memory-Concentration Test (BOMC)
    -Montreal Cognitive Assessment (MoCA)
    -St. Louis University Mental Status Examination (SLUMS)
    -Mini-Mental State Examination (MMSE) [Note: The MMSE has not been well validated for non-Alzheimer's dementias]
    -Short Informant Questionnaire on Cognitive Decline in the Elderly (IQCODE)
    -Ascertain Dementia 8 (AD8) Questionnaire
    -Minimum Data Set (MDS) Brief Interview of Mental Status (BIMS) [Note: Validated for use with nursing home patients only]
    -Formal neuropsychological evaluation
    -Mini-Cog.

        **Exclusion Criteria:** No exclusions.

        ** Used in:** CMS149v10
    """

    VALUE_SET_NAME = "Standardized Tools for Assessment of Cognition"
    OID = "2.16.840.1.113883.3.526.3.1006"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "58151-2",  # Prior assessment Brief Interview for Mental Status (BIMS) summary score [MDSv3]
        "71492-3",  # Total score [SLUMS]
        "71493-1",  # Total score [IQCODE]
        "71722-3",  # Total score [AD8]
        "72106-8",  # Total score [MMSE]
        "72172-0",  # Total score [MoCA]
        "72173-8",  # Total score [BOMC]
        "72233-0",  # Total score [Mini-Cog]
    }


class SexuallyActive(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for assessments to indicate vaginal intercourse.

    **Data Element Scope:** This value set may use a model element related to Assessment.

    **Inclusion Criteria:** Includes concepts that represent an assessment for intercourse.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS153v10
    """

    VALUE_SET_NAME = "Sexually Active"
    OID = "2.16.840.1.113883.3.464.1003.121.12.1040"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "64728-9",  # Have you ever had vaginal intercourse [PhenX]
    }


class StandardizedPainAssessmentTool(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for assessments using pain-focused tools or instruments to quantify pain intensity.

    **Data Element Scope:** This value set may use a model element related to Assessment.

    **Inclusion Criteria:** Includes concepts that represent an assessment of pain intensity.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS157v10
    """

    VALUE_SET_NAME = "Standardized Pain Assessment Tool"
    OID = "2.16.840.1.113883.3.526.3.1028"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "38208-5",  # Pain severity - Reported
        "38214-3",  # Pain severity [Score] Visual analog score
        "38221-8",  # Pain severity Wong-Baker FACES pain rating scale
        "72514-3",  # Pain severity - 0-10 verbal numeric rating [Score] - Reported
        "77565-0",  # Pain interference score [BPI Short Form]
    }


class Phq9AndPhq9MTools(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for the assessments of PHQ 9 and PHQ 9M resulting in a completed depression assessment scores for adults and adolescents.

    **Data Element Scope:** This value set may use a model element related to Assessment.

    **Inclusion Criteria:** Includes concepts that represent a completed assessment using PHQ 9 and PHQ 9M depression assessment tools for adults and adolescents with a summary score.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS159v10
    """

    VALUE_SET_NAME = "PHQ 9 and PHQ 9M Tools"
    OID = "2.16.840.1.113883.3.67.1.101.1.263"
    DEFINITION_VERSION = "20210219"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "44261-6",  # Patient Health Questionnaire 9 item (PHQ-9) total score [Reported]
        "89204-2",  # Patient Health Questionnaire-9: Modified for Teens total score [Reported.PHQ.Teen]
    }


class AverageNumberOfDrinksPerDrinkingDay(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for assessments measuring the number of alcoholic drinks per drinking day.

    **Data Element Scope:** This value set may use a model element related to Assessment.

    **Inclusion Criteria:** Includes concepts that represent an assessment of a quantitative observation of reported number of alcoholic drinks per drinking day.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS249v4
    """

    VALUE_SET_NAME = "Average Number of Drinks per Drinking Day"
    OID = "2.16.840.1.113883.3.464.1003.106.12.1018"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "11287-0",  # Alcoholic drinks per drinking day - Reported
    }


class HistoryOfHipFractureInParent(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for H145 assessments of a family history of hip fracture in a parent.

    **Data Element Scope:** This value set may use a model element related to Assessment.

    **Inclusion Criteria:** Includes concepts that represent an assessment for family history of hip fracture in a parent.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS249v4
    """

    VALUE_SET_NAME = "History of hip fracture in parent"
    OID = "2.16.840.1.113883.3.464.1003.113.12.1040"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "391096007",  # Family history: Maternal hip fracture (situation)
        "416072008",  # Family history: maternal hip fracture before age 75 (situation)
        "445121000124105",  # Family history of paternal hip fracture (situation)
        "445501000124107",  # Family history of hip fracture in parent (situation)
    }


__exports__ = get_overrides(locals().copy())
