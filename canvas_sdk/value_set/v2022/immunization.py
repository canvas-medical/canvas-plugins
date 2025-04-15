from canvas_sdk.value_set._utilities import get_overrides

from ..value_set import ValueSet


class DtapVaccine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for immunizations with diphtheria, tetanus, and pertussis (DTaP) vaccines.

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent a diphtheria, tetanus, and pertussis (DTaP) vaccine.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "DTaP Vaccine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1214"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CVX = {
        "20",  # diphtheria, tetanus toxoids and acellular pertussis vaccine
        "50",  # DTaP-Haemophilus influenzae type b conjugate vaccine
        "106",  # diphtheria, tetanus toxoids and acellular pertussis vaccine, 5 pertussis antigens
        "107",  # diphtheria, tetanus toxoids and acellular pertussis vaccine, unspecified formulation
        "110",  # DTaP-hepatitis B and poliovirus vaccine
        "120",  # diphtheria, tetanus toxoids and acellular pertussis vaccine, Haemophilus influenzae type b conjugate, and poliovirus vaccine, inactivated (DTaP-Hib-IPV)
    }


class HepatitisAVaccine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for immunizations with Hepatitis A vaccines.

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent a Hepatitis A vaccine.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Hepatitis A Vaccine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1215"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CVX = {
        "31",  # hepatitis A vaccine, pediatric dosage, unspecified formulation
        "83",  # hepatitis A vaccine, pediatric/adolescent dosage, 2 dose schedule
        "85",  # hepatitis A vaccine, unspecified formulation
    }


class HepatitisBVaccine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for immunizations with Hepatitis B vaccines.

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent a Hepatitis B vaccine.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Hepatitis B Vaccine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1216"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CVX = {
        "08",  # hepatitis B vaccine, pediatric or pediatric/adolescent dosage
        "44",  # hepatitis B vaccine, dialysis patient dosage
        "45",  # hepatitis B vaccine, unspecified formulation
        "51",  # Haemophilus influenzae type b conjugate and Hepatitis B vaccine
        "110",  # DTaP-hepatitis B and poliovirus vaccine
    }


class HibVaccine3DoseSchedule(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for immunizations with 3-dose haemophilus influenzae type b (Hib) vaccines.

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent a 3-dose haemophilus influenzae type b (Hib) vaccine.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Hib Vaccine (3 dose schedule)"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1083"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CVX = {
        "49",  # Haemophilus influenzae type b vaccine, PRP-OMP conjugate
    }


class HibVaccine4DoseSchedule(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for immunizations with 4-dose haemophilus influenzae type b (Hib) vaccines.

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent a 4-dose haemophilus influenzae type b (Hib) vaccine.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Hib Vaccine (4 dose schedule)"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1085"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CVX = {
        "48",  # Haemophilus influenzae type b vaccine, PRP-T conjugate
        "50",  # DTaP-Haemophilus influenzae type b conjugate vaccine
        "51",  # Haemophilus influenzae type b conjugate and Hepatitis B vaccine
        "120",  # diphtheria, tetanus toxoids and acellular pertussis vaccine, Haemophilus influenzae type b conjugate, and poliovirus vaccine, inactivated (DTaP-Hib-IPV)
        "148",  # Meningococcal Groups C and Y and Haemophilus b Tetanus Toxoid Conjugate Vaccine
    }


class InactivatedPolioVaccineIpv(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for immunizations with inactivated polio vaccines (IPV).

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent an inactivated polio vaccine (IPV).

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Inactivated Polio Vaccine (IPV)"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1219"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CVX = {
        "10",  # poliovirus vaccine, inactivated
        "89",  # poliovirus vaccine, unspecified formulation
        "110",  # DTaP-hepatitis B and poliovirus vaccine
        "120",  # diphtheria, tetanus toxoids and acellular pertussis vaccine, Haemophilus influenzae type b conjugate, and poliovirus vaccine, inactivated (DTaP-Hib-IPV)
    }


class InfluenzaVaccine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for immunizations with influenza vaccines.

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent an influenza vaccine.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS147v11, CMS117v10
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
        "153",  # Influenza, injectable, Madin Darby Canine Kidney, preservative free
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


class InfluenzaVirusLaivImmunization(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent live attenuated influenza vaccine.

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent a live attenuated influenza vaccine (quadrivalent and trivalent).

    **Exclusion Criteria:** Excludes concepts that represent the recombinant or inactivated influenza vaccine.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Influenza Virus LAIV Immunization"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1087"
    DEFINITION_VERSION = "20210224"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CVX = {
        "111",  # influenza virus vaccine, live, attenuated, for intranasal use
        "149",  # influenza, live, intranasal, quadrivalent
    }


class Measles_MumpsAndRubellaMmrVaccine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for immunizations with measles, mumps and rubella (MMR) vaccines.

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent a measles, mumps and rubella (MMR) vaccine.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Measles, Mumps and Rubella (MMR) Vaccine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1224"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CVX = {
        "03",  # measles, mumps and rubella virus vaccine
        "94",  # measles, mumps, rubella, and varicella virus vaccine
    }


class PneumococcalConjugateVaccine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for immunizations with pneumococcal conjugate vaccines.

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent a pneumococcal conjugate vaccine.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Pneumococcal Conjugate Vaccine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1221"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CVX = {
        "133",  # pneumococcal conjugate vaccine, 13 valent
        "152",  # Pneumococcal Conjugate, unspecified formulation
    }


class RotavirusVaccine3DoseSchedule(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for immunizations with 3-dose rotavirus vaccines.

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent a 3-dose rotavirus vaccine.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Rotavirus Vaccine (3 dose schedule)"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1223"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CVX = {
        "116",  # rotavirus, live, pentavalent vaccine
        "122",  # rotavirus vaccine, unspecified formulation
    }


class VaricellaZosterVaccineVzv(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for immunizations with varicella zoster vaccines.

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent a varicella zoster vaccine.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Varicella Zoster Vaccine (VZV)"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1170"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CVX = {
        "21",  # varicella virus vaccine
        "94",  # measles, mumps, rubella, and varicella virus vaccine
    }


class PneumococcalPolysaccharide23Vaccine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for immunizations with pneumococcal polysaccharide vaccines.

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent a pneumococcal polysaccharide 23-valent vaccine.

    **Exclusion Criteria:** Excludes concepts that represent the pneumococcal conjugate 7-valent and 13-valent vaccines.

    ** Used in:** CMS127v10
    """

    VALUE_SET_NAME = "Pneumococcal Polysaccharide 23 Vaccine"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1089"
    DEFINITION_VERSION = "20210224"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CVX = {
        "33",  # pneumococcal polysaccharide vaccine, 23 valent
        "109",  # pneumococcal vaccine, unspecified formulation
    }


__exports__ = get_overrides(locals().copy())
