from ..value_set import ValueSet

class ChildInfluenzaVaccine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for immunizations with influenza vaccines for use in children 2 and younger.

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent an influenza vaccine for use in children 2 and younger.

    **Exclusion Criteria:** Excludes influenza vaccines not recommended for use in children 2 and younger.
    """

    VALUE_SET_NAME = "Child Influenza Vaccine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1218"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CVX = {
        "140",  # Influenza, split virus, trivalent, injectable, preservative free
        "141",  # Influenza, split virus, trivalent, injectable, contains preservative
        "150",  # Influenza, split virus, quadrivalent, injectable, preservative free
        "153",  # Influenza, Madin Darby Canine Kidney, subunit, trivalent, injectable, preservative free
        "155",  # Influenza, recombinant, trivalent, injectable, preservative free
        "158",  # Influenza, split virus, quadrivalent, injectable, contains preservative
        "161",  # Influenza, injectable,quadrivalent, preservative free, pediatric
        "171",  # Influenza, Madin Darby Canine Kidney, subunit, quadrivalent, injectable, preservative free
        "186",  # Influenza, Madin Darby Canine Kidney, subunit, quadrivalent, injectable, contains preservative
        "88",  # influenza virus vaccine, unspecified formulation
    }

class DtapVaccine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for immunizations with diphtheria, tetanus, and pertussis (DTaP) vaccines.

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent a diphtheria, tetanus, and pertussis (DTaP) vaccine.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "DTaP Vaccine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1214"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CVX = {
        "106",  # diphtheria, tetanus toxoids and acellular pertussis vaccine, 5 pertussis antigens
        "107",  # diphtheria, tetanus toxoids and acellular pertussis vaccine, unspecified formulation
        "110",  # DTaP-hepatitis B and poliovirus vaccine
        "120",  # diphtheria, tetanus toxoids and acellular pertussis vaccine, Haemophilus influenzae type b conjugate, and poliovirus vaccine, inactivated (DTaP-Hib-IPV)
        "146",  # Diphtheria and Tetanus Toxoids and Acellular Pertussis Adsorbed, Inactivated Poliovirus, Haemophilus b Conjugate (Meningococcal Protein Conjugate), and Hepatitis B (Recombinant) Vaccine.
        "198",  # Diphtheria, pertussis, tetanus, hepatitis B, Haemophilus Influenza Type b, (Pentavalent)
        "20",  # diphtheria, tetanus toxoids and acellular pertussis vaccine
        "50",  # DTaP-Haemophilus influenzae type b conjugate vaccine
    }

class HepatitisAVaccine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for immunizations with Hepatitis A vaccines.

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent a Hepatitis A vaccine.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Hepatitis A Vaccine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1215"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

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
    """

    VALUE_SET_NAME = "Hepatitis B Vaccine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1216"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CVX = {
        "08",  # hepatitis B vaccine, pediatric or pediatric/adolescent dosage
        "110",  # DTaP-hepatitis B and poliovirus vaccine
        "146",  # Diphtheria and Tetanus Toxoids and Acellular Pertussis Adsorbed, Inactivated Poliovirus, Haemophilus b Conjugate (Meningococcal Protein Conjugate), and Hepatitis B (Recombinant) Vaccine.
        "198",  # Diphtheria, pertussis, tetanus, hepatitis B, Haemophilus Influenza Type b, (Pentavalent)
        "44",  # Hepatitis B vaccine (Hep B), high-dosage, dialysis or immunocompromised patient
        "45",  # hepatitis B vaccine, unspecified formulation
        "51",  # Haemophilus influenzae type b conjugate and Hepatitis B vaccine
    }

class HibVaccine3DoseSchedule(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for immunizations with 3-dose haemophilus influenzae type b (Hib) vaccines.

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent a 3-dose haemophilus influenzae type b (Hib) vaccine.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Hib Vaccine (3 dose schedule)"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1083"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CVX = {
        "17",  # Haemophilus influenzae type b vaccine, conjugate unspecified formulation
        "49",  # Haemophilus influenzae type b vaccine, PRP-OMP conjugate
        "51",  # Haemophilus influenzae type b conjugate and Hepatitis B vaccine
    }

class HibVaccine4DoseSchedule(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for immunizations with 4-dose haemophilus influenzae type b (Hib) vaccines.

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent a 4-dose haemophilus influenzae type b (Hib) vaccine.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Hib Vaccine (4 dose schedule)"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1085"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CVX = {
        "120",  # diphtheria, tetanus toxoids and acellular pertussis vaccine, Haemophilus influenzae type b conjugate, and poliovirus vaccine, inactivated (DTaP-Hib-IPV)
        "146",  # Diphtheria and Tetanus Toxoids and Acellular Pertussis Adsorbed, Inactivated Poliovirus, Haemophilus b Conjugate (Meningococcal Protein Conjugate), and Hepatitis B (Recombinant) Vaccine.
        "148",  # Meningococcal Groups C and Y and Haemophilus b Tetanus Toxoid Conjugate Vaccine
        "48",  # Haemophilus influenzae type b vaccine, PRP-T conjugate
    }

class InactivatedPolioVaccineIpv(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for immunizations with inactivated polio vaccines (IPV).

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent an inactivated polio vaccine (IPV).

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Inactivated Polio Vaccine (IPV)"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1219"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CVX = {
        "10",  # poliovirus vaccine, inactivated
        "110",  # DTaP-hepatitis B and poliovirus vaccine
        "120",  # diphtheria, tetanus toxoids and acellular pertussis vaccine, Haemophilus influenzae type b conjugate, and poliovirus vaccine, inactivated (DTaP-Hib-IPV)
        "146",  # Diphtheria and Tetanus Toxoids and Acellular Pertussis Adsorbed, Inactivated Poliovirus, Haemophilus b Conjugate (Meningococcal Protein Conjugate), and Hepatitis B (Recombinant) Vaccine.
        "89",  # poliovirus vaccine, unspecified formulation
    }

class InfluenzaVirusLaivVaccine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent live attenuated influenza vaccine.

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent a live attenuated influenza vaccine (quadrivalent and trivalent).

    **Exclusion Criteria:** Excludes concepts that represent the recombinant or inactivated influenza vaccine.
    """

    VALUE_SET_NAME = "Influenza Virus LAIV Vaccine"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1087"
    DEFINITION_VERSION = "20210224"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CVX = {
        "111",  # Influenza, live, trivalent, intranasal
        "149",  # Influenza, live, quadrivalent, intranasal
    }

class MeaslesMumpsAndRubellaMmrVaccine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for immunizations with measles, mumps and rubella (MMR) vaccines.

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent a measles, mumps and rubella (MMR) vaccine.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Measles, Mumps and Rubella (MMR) Vaccine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1224"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

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
    """

    VALUE_SET_NAME = "Pneumococcal Conjugate Vaccine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1221"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CVX = {
        "109",  # pneumococcal vaccine, unspecified formulation
        "133",  # pneumococcal conjugate vaccine, 13 valent
        "152",  # Pneumococcal Conjugate, unspecified formulation
        "215",  # Pneumococcal conjugate vaccine 15-valent (PCV15), polysaccharide CRM197 conjugate, adjuvant, preservative free
        "216",  # Pneumococcal conjugate vaccine 20-valent (PCV20), polysaccharide CRM197 conjugate, adjuvant, preservative free
    }

class RotavirusVaccine3DoseSchedule(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for immunizations with 3-dose rotavirus vaccines.

    **Data Element Scope:** This value set may use a model element related to Immunization.

    **Inclusion Criteria:** Includes concepts that represent a 3-dose rotavirus vaccine.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Rotavirus Vaccine (3 dose schedule)"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1223"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

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
    """

    VALUE_SET_NAME = "Varicella Zoster Vaccine (VZV)"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1170"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CVX = {
        "21",  # varicella virus vaccine
        "94",  # measles, mumps, rubella, and varicella virus vaccine
    }

__exports__ = (
    "ChildInfluenzaVaccine",
    "DtapVaccine",
    "HepatitisAVaccine",
    "HepatitisBVaccine",
    "HibVaccine3DoseSchedule",
    "HibVaccine4DoseSchedule",
    "InactivatedPolioVaccineIpv",
    "InfluenzaVirusLaivVaccine",
    "MeaslesMumpsAndRubellaMmrVaccine",
    "PneumococcalConjugateVaccine",
    "RotavirusVaccine3DoseSchedule",
    "VaricellaZosterVaccineVzv",
)
