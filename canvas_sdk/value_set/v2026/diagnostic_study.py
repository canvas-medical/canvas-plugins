from ..value_set import ValueSet


class CtColonography(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for computed tomographic (CT) colonography.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent computed tomographic (CT) colonography.

    **Exclusion Criteria:** Excludes concepts that represent order only codes.

    ** Used in:** CMS130v14
    """

    VALUE_SET_NAME = "CT Colonography"
    OID = "2.16.840.1.113883.3.464.1003.108.12.1038"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "60515-4",  # CT Colon and Rectum W air contrast PR
        "72531-7",  # CT Colon and Rectum W contrast IV and W air contrast PR
        "79069-1",  # CT Colon and Rectum for screening WO contrast IV and W air contrast PR
        "79071-7",  # CT Colon and Rectum WO contrast IV and W air contrast PR
        "79101-2",  # CT Colon and Rectum for screening W air contrast PR
        "82688-3",  # CT Colon and Rectum WO and W contrast IV and W air contrast PR
    }


__exports__ = (
    "CtColonography",
)
