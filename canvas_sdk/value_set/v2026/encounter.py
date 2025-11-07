from ..value_set import ValueSet


class AnnualWellnessVisit(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for annual wellness visits.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for a Medicare annual wellness visit.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS131v14
    """

    VALUE_SET_NAME = "Annual Wellness Visit"
    OID = "2.16.840.1.113883.3.526.3.1240"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    HCPCSLEVELII = {
        "G0402",  # Initial preventive physical examination; face-to-face visit, services limited to new beneficiary during the first 12 months of medicare enrollment
        "G0438",  # Annual wellness visit; includes a personalized prevention plan of service (pps), initial visit
        "G0439",  # Annual wellness visit, includes a personalized prevention plan of service (pps), subsequent visit
    }

    SNOMEDCT = {
        "444971000124105",  # Annual wellness visit (procedure)
        "456201000124103",  # Medicare annual wellness visit (procedure)
        "86013001",  # Periodic reevaluation and management of healthy individual (procedure)
        "866149003",  # Annual visit (procedure)
        "90526000",  # Initial evaluation and management of healthy individual (procedure)
    }


__exports__ = (AnnualWellnessVisit,)