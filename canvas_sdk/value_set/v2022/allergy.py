from canvas_sdk.value_set._utilities import get_overrides

from ..value_set import ValueSet


class AceInhibitorOrArbIngredient(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications of angiotensin-converting enzyme (ACE) inhibitor and angiotensin-receptor blocker (ARB) ingredients.

    **Data Element Scope:** This value set may use a model element related to Allergy/Intolerance.

    **Inclusion Criteria:** Includes concepts that represent an allergy or intolerance for prescribable angiotensin-converting enzyme (ACE) inhibitor and angiotensin-receptor blocker (ARB) ingredients only.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS135v10
    """

    VALUE_SET_NAME = "ACE Inhibitor or ARB Ingredient"
    OID = "2.16.840.1.113883.3.526.3.1489"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "1998",  # captopril
        "3827",  # enalapril
        "18867",  # benazepril
        "29046",  # lisinopril
        "30131",  # moexipril
        "35208",  # quinapril
        "35296",  # ramipril
        "38454",  # trandolapril
        "50166",  # fosinopril
        "52175",  # losartan
        "54552",  # perindopril
        "69749",  # valsartan
        "73494",  # telmisartan
        "83515",  # eprosartan
        "83818",  # irbesartan
        "214354",  # candesartan
        "321064",  # olmesartan
    }


class BetaBlockerTherapyIngredient(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications containing ingredients for beta blocker therapy.

    **Data Element Scope:** This value set may use a model element related to Allergy/Intolerance.

    **Inclusion Criteria:** Includes concepts that represent an allergy or intolerance for prescribable beta blockers.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS144v10, CMS145v10
    """

    VALUE_SET_NAME = "Beta Blocker Therapy Ingredient"
    OID = "2.16.840.1.113883.3.526.3.1493"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "149",  # acebutolol
        "1202",  # atenolol
        "1520",  # betaxolol
        "2116",  # carteolol
        "6185",  # labetalol
        "6918",  # metoprolol
        "7226",  # nadolol
        "8332",  # pindolol
        "8787",  # propranolol
        "10600",  # timolol
        "19484",  # bisoprolol
        "20352",  # carvedilol
    }


class EggSubstance(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for an allergy or intolerance to an egg substance.

    **Data Element Scope:** This value set may use a model element related to Substance.

    **Inclusion Criteria:** Includes concepts that represent an allergy or intolerance to an egg substance.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS147v11
    """

    VALUE_SET_NAME = "Egg Substance"
    OID = "2.16.840.1.113883.3.526.3.1537"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "102263004",  # Eggs (edible) (substance)
        "226881001",  # Dried egg (substance)
        "226885005",  # Raw egg (substance)
        "229955000",  # Dried egg white (substance)
        "256442007",  # Egg yolk (substance)
        "256443002",  # Egg white (substance)
        "286550009",  # Hen's egg (substance)
        "303300008",  # Egg protein (substance)
        "414074006",  # Egg product (substance)
    }


class InfluenzaVaccination(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for an influenza vaccination.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent an influenza vaccination.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS147v11
    """

    VALUE_SET_NAME = "Influenza Vaccination"
    OID = "2.16.840.1.113883.3.526.3.402"
    DEFINITION_VERSION = "20170908"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90630",  # Influenza virus vaccine, quadrivalent (IIV4), split virus, preservative free, for intradermal use
        "90653",  # Influenza vaccine, inactivated (IIV), subunit, adjuvanted, for intramuscular use
        "90654",  # Influenza virus vaccine, trivalent (IIV3), split virus, preservative-free, for intradermal use
        "90655",  # Influenza virus vaccine, trivalent (IIV3), split virus, preservative free, 0.25 mL dosage, for intramuscular use
        "90656",  # Influenza virus vaccine, trivalent (IIV3), split virus, preservative free, 0.5 mL dosage, for intramuscular use
        "90657",  # Influenza virus vaccine, trivalent (IIV3), split virus, 0.25 mL dosage, for intramuscular use
        "90658",  # Influenza virus vaccine, trivalent (IIV3), split virus, 0.5 mL dosage, for intramuscular use
        "90661",  # Influenza virus vaccine, trivalent (ccIIV3), derived from cell cultures, subunit, preservative and antibiotic free, 0.5 mL dosage, for intramuscular use
        "90662",  # Influenza virus vaccine (IIV), split virus, preservative free, enhanced immunogenicity via increased antigen content, for intramuscular use
        "90666",  # Influenza virus vaccine (IIV), pandemic formulation, split virus, preservative free, for intramuscular use
        "90667",  # Influenza virus vaccine (IIV), pandemic formulation, split virus, adjuvanted, for intramuscular use
        "90668",  # Influenza virus vaccine (IIV), pandemic formulation, split virus, for intramuscular use
        "90673",  # Influenza virus vaccine, trivalent (RIV3), derived from recombinant DNA, hemagglutinin (HA) protein only, preservative and antibiotic free, for intramuscular use
        "90674",  # Influenza virus vaccine, quadrivalent (ccIIV4), derived from cell cultures, subunit, preservative and antibiotic free, 0.5 mL dosage, for intramuscular use
        "90682",  # Influenza virus vaccine, quadrivalent (RIV4), derived from recombinant DNA, hemagglutinin (HA) protein only, preservative and antibiotic free, for intramuscular use
        "90685",  # Influenza virus vaccine, quadrivalent (IIV4), split virus, preservative free, 0.25 mL dosage, for intramuscular use
        "90686",  # Influenza virus vaccine, quadrivalent (IIV4), split virus, preservative free, 0.5 mL dosage, for intramuscular use
        "90687",  # Influenza virus vaccine, quadrivalent (IIV4), split virus, 0.25 mL dosage, for intramuscular use
        "90688",  # Influenza virus vaccine, quadrivalent (IIV4), split virus, 0.5 mL dosage, for intramuscular use
        "90689",  # Influenza virus vaccine, quadrivalent (IIV4), inactivated, adjuvanted, preservative free, 0.25 mL dosage, for intramuscular use
        "90694",  # Influenza virus vaccine, quadrivalent (aIIV4), inactivated, adjuvanted, preservative free, 0.5 mL dosage, for intramuscular use
        "90756",  # Influenza virus vaccine, quadrivalent (ccIIV4), derived from cell cultures, subunit, antibiotic free, 0.5 mL dosage, for intramuscular use
    }
    HCPCSLEVELII = {
        "G0008",  # Administration of influenza virus vaccine
        "Q2034",  # Influenza virus vaccine, split virus, for intramuscular use (agriflu)
        "Q2035",  # Influenza virus vaccine, split virus, when administered to individuals 3 years of age and older, for intramuscular use (afluria)
        "Q2036",  # Influenza virus vaccine, split virus, when administered to individuals 3 years of age and older, for intramuscular use (flulaval)
        "Q2037",  # Influenza virus vaccine, split virus, when administered to individuals 3 years of age and older, for intramuscular use (fluvirin)
        "Q2038",  # Influenza virus vaccine, split virus, when administered to individuals 3 years of age and older, for intramuscular use (fluzone)
        "Q2039",  # Influenza virus vaccine, not otherwise specified
    }
    SNOMEDCT = {
        "86198006",  # Administration of vaccine product containing only Influenza virus antigen (procedure)
    }


class InfluenzaVaccine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for immunizations with influenza vaccines.

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent an influenza vaccine.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS147v11
    """

    VALUE_SET_NAME = "Influenza Vaccine"
    OID = "2.16.840.1.113883.3.526.3.1254"
    DEFINITION_VERSION = "20170908"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CVX = {
        "88",  # influenza virus vaccine, unspecified formulation
        "135",  # influenza, high dose seasonal, preservative-free
        "140",  # Influenza, seasonal, injectable, preservative free
        "141",  # Influenza, seasonal, injectable
        "144",  # seasonal influenza, intradermal, preservative free
        "149",  # influenza, live, intranasal, quadrivalent
        "150",  # Influenza, injectable, quadrivalent, preservative free
        "155",  # Seasonal, trivalent, recombinant, injectable influenza vaccine, preservative free
        "158",  # influenza, injectable, quadrivalent, contains preservative
        "161",  # Influenza, injectable,quadrivalent, preservative free, pediatric
        "166",  # influenza, intradermal, quadrivalent, preservative free, injectable
        "168",  # Seasonal trivalent influenza vaccine, adjuvanted, preservative free
        "171",  # Influenza, injectable, Madin Darby Canine Kidney, preservative free, quadrivalent
        "185",  # Seasonal, quadrivalent, recombinant, injectable influenza vaccine, preservative free
        "186",  # Influenza, injectable, Madin Darby Canine Kidney,  quadrivalent with preservative
        "197",  # influenza, high-dose seasonal, quadrivalent, .7mL dose, preservative free
        "205",  # influenza, seasonal vaccine, quadrivalent, adjuvanted, .5mL dose, preservative free
    }


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


__exports__ = get_overrides(locals().copy())
