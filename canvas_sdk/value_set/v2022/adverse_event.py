from ..value_set import ValueSet


class StatinAllergen(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of an allergy to statin medications.

    **Data Element Scope:** This value set may use a model element related to Allergy/Intolerance.

    **Inclusion Criteria:** Includes concepts that define an allergy to statin medications.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS347v5
    """

    VALUE_SET_NAME = "Statin Allergen"
    OID = "2.16.840.1.113762.1.4.1110.42"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "6472",  # lovastatin
        "36567",  # simvastatin
        "41127",  # fluvastatin
        "42463",  # pravastatin
        "83367",  # atorvastatin
        "301542",  # rosuvastatin
        "861634",  # pitavastatin
    }
    SNOMEDCT = {
        "372912004",  # Substance with 3-hydroxy-3-methylglutaryl-coenzyme A reductase inhibitor mechanism of action (substance)
    }


__exports__ = ("StatinAllergen",)
