from ..value_set import ValueSet


class AceInhibitorOrArbOrArniIngredient(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications of angiotensin-converting enzyme (ACE) inhibitor, angiotensin-receptor blocker (ARB), and angiotensin receptor/neprilysin inhibitor (ARNI) ingredients.

    **Data Element Scope:** This value set may use a model element related to Allergy/Intolerance.

    **Inclusion Criteria:** Includes concepts that represent an allergy or intolerance for prescribable angiotensin-converting enzyme (ACE) inhibitor, angiotensin-receptor blocker (ARB), and angiotensin receptor/neprilysin inhibitor (ARNI) ingredients only.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "ACE Inhibitor or ARB or ARNI Ingredient"
    OID = "2.16.840.1.113883.3.526.3.1489"
    DEFINITION_VERSION = "20230217"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1091643",  # azilsartan
        "1656328",  # sacubitril
        "18867",  # benazepril
        "1998",  # captopril
        "214354",  # candesartan
        "29046",  # lisinopril
        "30131",  # moexipril
        "321064",  # olmesartan
        "35208",  # quinapril
        "35296",  # ramipril
        "3827",  # enalapril
        "38454",  # trandolapril
        "50166",  # fosinopril
        "52175",  # losartan
        "54552",  # perindopril
        "69749",  # valsartan
        "73494",  # telmisartan
        "83515",  # eprosartan
        "83818",  # irbesartan
    }


class BetaBlockerTherapyIngredient(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications containing ingredients for beta blocker therapy.

    **Data Element Scope:** This value set may use a model element related to Allergy/Intolerance.

    **Inclusion Criteria:** Includes concepts that represent an allergy or intolerance for prescribable beta blockers.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Beta Blocker Therapy Ingredient"
    OID = "2.16.840.1.113883.3.526.3.1493"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "10600",  # timolol
        "10824",  # metipranolol
        "1202",  # atenolol
        "149",  # acebutolol
        "1520",  # betaxolol
        "1813",  # levobunolol
        "19484",  # bisoprolol
        "20352",  # carvedilol
        "2116",  # carteolol
        "31555",  # nebivolol
        "49737",  # esmolol
        "6185",  # labetalol
        "6918",  # metoprolol
        "7226",  # nadolol
        "8332",  # pindolol
        "8787",  # propranolol
        "9947",  # sotalol
    }


class StatinAllergen(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of an allergy to statin medications.

    **Data Element Scope:** This value set may use a model element related to Allergy/Intolerance.

    **Inclusion Criteria:** Includes concepts that define an allergy to statin medications.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Statin Allergen"
    OID = "2.16.840.1.113762.1.4.1110.42"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "301542",  # rosuvastatin
        "36567",  # simvastatin
        "41127",  # fluvastatin
        "42463",  # pravastatin
        "6472",  # lovastatin
        "83367",  # atorvastatin
        "861634",  # pitavastatin
    }

    SNOMEDCT = {
        "372912004",  # Substance with 3-hydroxy-3-methylglutaryl-coenzyme A reductase inhibitor mechanism of action (substance)
        "96302009",  # Product containing 3-hydroxy-3-methylglutaryl-coenzyme A reductase inhibitor (product)
    }


__exports__ = (
    "AceInhibitorOrArbOrArniIngredient",
    "BetaBlockerTherapyIngredient",
    "StatinAllergen",
)
