from canvas_sdk.value_set._utilities import get_overrides

from ..value_set import ValueSet


class DtapVaccineAdministered(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for diphtheria, tetanus, and whooping cough (pertussis) (DTaP) vaccination.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a diphtheria, tetanus, and whooping cough (pertussis) (DTaP) vaccination.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "DTaP Vaccine Administered"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1022"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90698",  # Diphtheria, tetanus toxoids, acellular pertussis vaccine, Haemophilus influenzae type b, and inactivated poliovirus vaccine, (DTaP-IPV/Hib), for intramuscular use
        "90700",  # Diphtheria, tetanus toxoids, and acellular pertussis vaccine (DTaP), when administered to individuals younger than 7 years, for intramuscular use
        "90723",  # Diphtheria, tetanus toxoids, acellular pertussis vaccine, hepatitis B, and inactivated poliovirus vaccine (DTaP-HepB-IPV), for intramuscular use
    }
    SNOMEDCT = {
        "170395004",  # First diphtheria, pertussis and tetanus triple vaccination (procedure)
        "170396003",  # Second diphtheria, pertussis and tetanus triple vaccination (procedure)
        "170397007",  # Third diphtheria, pertussis and tetanus triple vaccination (procedure)
        "170399005",  # Diphtheria, pertussis and tetanus triple and polio vaccination (procedure)
        "170400003",  # First diphtheria, pertussis and tetanus triple and polio vaccination (procedure)
        "170401004",  # Second diphtheria, pertussis and tetanus triple and polio vaccination (procedure)
        "170402006",  # Third diphtheria, pertussis and tetanus triple and polio vaccination (procedure)
        "310306005",  # Administration of first dose of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Human poliovirus antigens (procedure)
        "310307001",  # Administration of second dose of Vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Human poliovirus antigens (procedure)
        "310308006",  # Administration of third dose of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Human poliovirus antigens (procedure)
        "312870000",  # Administration of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Human poliovirus antigens (procedure)
        "313383003",  # Administration of fourth dose of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Human poliovirus antigens (procedure)
        "390846000",  # Administration of booster dose of vaccine product containing only acellular Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae antigens (procedure)
        "390865008",  # Administration of booster dose of vaccine product containing only acellular Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Human poliovirus antigens (procedure)
        "399014008",  # Administration of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae antigens (procedure)
        "412755006",  # Administration of first dose of vaccine product containing only acellular Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae antigens (procedure)
        "412756007",  # Administration of second dose of vaccine product containing only acellular Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae antigens (procedure)
        "412757003",  # Administration of third dose of vaccine product containing only acellular Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae antigens (procedure)
        "412762002",  # Administration of first dose of vaccine product containing only acellular Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Human poliovirus antigens (procedure)
        "412763007",  # Administration of second dose of vaccine product containing only acellular Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Human poliovirus antigens (procedure)
        "412764001",  # Administration of third dose of vaccine product containing only acellular Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Human poliovirus antigens (procedure)
        "414001002",  # Administration of vaccine product containing only five component acellular Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and inactivated whole Human poliovirus antigens (procedure)
        "414259000",  # Administration of first dose of vaccine product containing only five component acellular Bordetella pertussis, Clostridium tetani, Corynebacterium diphtheriae, Haemophilus influenzae type B and inactivated whole Human poliovirus antigens (procedure)
        "414620004",  # Administration of vaccine product containing only acellular Bordetella pertussis five component and Clostridium tetani and low dose Corynebacterium diphtheriae and inactivated whole Human poliovirus antigens (procedure)
        "415507003",  # Administration of second dose of vaccine product containing only five component acellular Bordetella pertussis, Clostridium tetani, Corynebacterium diphtheriae, Haemophilus influenzae type B and inactivated whole Human poliovirus antigens (procedure)
        "415712004",  # Administration of third dose of vaccine product containing only five component acellular Bordetella pertussis, Clostridium tetani, Corynebacterium diphtheriae, Haemophilus influenzae type B and inactivated whole Human poliovirus antigens (procedure)
        "770608009",  # Administration of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Hepatitis B virus antigens (procedure)
        "770616000",  # Administration of first dose of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Hepatitis B virus antigens (procedure)
        "770617009",  # Administration of second dose of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Hepatitis B virus antigens (procedure)
        "770618004",  # Administration of third dose of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Hepatitis B virus antigens (procedure)
        "787436003",  # Administration of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B antigens (procedure)
        "787438002",  # Vaccination for diphtheria, pertussis, tetanus, poliomyelitis, Hepatitis B virus and Haemophilus influenzae type b (procedure)
        "866158005",  # Administration of first dose of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae antigens (procedure)
        "866159002",  # Administration of second dose of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae antigens (procedure)
        "866226006",  # Administration of third dose of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae antigens (procedure)
        "428251000124104",  # Tetanus, diphtheria and acellular pertussis vaccination (procedure)
        "571571000119105",  # Administration of vaccine product containing only acellular Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae antigens (procedure)
        "572561000119108",  # Administration of vaccine product containing only acellular Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Hepatitis B virus and inactivated whole Human poliovirus antigens (procedure)
        "16290681000119103",  # Administration of vaccine product containing only acellular Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and inactivated whole Human poliovirus antigens (procedure)
        "16298561000119108",  # Administration of tetanus, diphtheria, and acellular pertussis vaccine (procedure)
    }


class HepatitisAVaccineAdministered(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a Hepatitis A vaccination.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a Hepatitis A vaccination.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Hepatitis A Vaccine Administered"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1041"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90633",  # Hepatitis A vaccine (HepA), pediatric/adolescent dosage-2 dose schedule, for intramuscular use
    }
    SNOMEDCT = {
        "170378007",  # Administration of first dose of pediatric vaccine product containing only Hepatitis A virus antigen (procedure)
        "170379004",  # Administration of second dose of vaccine product containing only Hepatitis A virus antigen (procedure)
        "170380001",  # Administration of third dose of vaccine product containing only Hepatitis A virus antigen (procedure)
        "170381002",  # Administration of booster dose of vaccine product containing only Hepatitis A virus antigen (procedure)
        "170434002",  # Administration of first dose of vaccine product containing only Hepatitis A and Hepatitis B virus antigens (procedure)
        "170435001",  # Administration of second dose of vaccine product containing only Hepatitis A and B virus antigens (procedure)
        "170436000",  # Administration of third dose of vaccine product containing only Hepatitis A and Hepatitis B virus antigens (procedure)
        "170437009",  # Administration of booster dose of vaccine product containing only Hepatitis A and Hepatitis B virus antigens (procedure)
        "243789007",  # Administration of vaccine product containing only Hepatitis A virus antigen (procedure)
        "312868009",  # Administration of vaccine product containing only Hepatitis A and Hepatitis B virus antigens (procedure)
        "313188000",  # First hepatitis A junior vaccination (procedure)
        "313189008",  # Second hepatitis A junior vaccination (procedure)
        "314177003",  # Administration of vaccine product containing only Hepatitis A virus and Salmonella enterica subspecies enterica serovar Typhi antigens (procedure)
        "314178008",  # Administration of first dose of vaccine product containing only Hepatitis A virus and Salmonella enterica subspecies enterica serovar Typhi antigens (procedure)
        "314179000",  # Administration of second dose of vaccine product containing only Hepatitis A virus and Salmonella enterica subspecies enterica serovar Typhi antigens (procedure)
        "394691002",  # Administration of booster dose of vaccine product containing only Hepatitis A virus and Salmonella enterica subspecies enterica serovar Typhi antigens (procedure)
        "412742005",  # Third hepatitis A junior vaccination (procedure)
        "412743000",  # Booster hepatitis A junior vaccination (procedure)
        "871752004",  # Administration of second dose of pediatric vaccine product containing only Hepatitis A virus antigen (procedure)
        "871753009",  # Administration of third dose of pediatric vaccine product containing only Hepatitis A virus antigen (procedure)
        "871754003",  # Administration of booster dose of pediatric vaccine product containing only Hepatitis A virus antigen (procedure)
    }


class HepatitisBVaccineAdministered(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a Hepatitis B vaccination.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a procedure for a Hepatitis B vaccination.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Hepatitis B Vaccine Administered"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1042"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90723",  # Diphtheria, tetanus toxoids, acellular pertussis vaccine, hepatitis B, and inactivated poliovirus vaccine (DTaP-HepB-IPV), for intramuscular use
        "90740",  # Hepatitis B vaccine (HepB), dialysis or immunosuppressed patient dosage, 3 dose schedule, for intramuscular use
        "90744",  # Hepatitis B vaccine (HepB), pediatric/adolescent dosage, 3 dose schedule, for intramuscular use
        "90747",  # Hepatitis B vaccine (HepB), dialysis or immunosuppressed patient dosage, 4 dose schedule, for intramuscular use
        "90748",  # Hepatitis B and Haemophilus influenzae type b vaccine (Hib-HepB), for intramuscular use
    }
    ICD10PCS = {
        "3E0234Z",  # Introduction of Serum, Toxoid and Vaccine into Muscle, Percutaneous Approach
    }
    ICD9CM = {
        "9955",  # Prophylactic administration of vaccine against other diseases
    }
    SNOMEDCT = {
        "16584000",  # Administration of vaccine product containing only Hepatitis B virus antigen (procedure)
        "170370000",  # Administration of first dose of vaccine product containing only Hepatitis B virus antigen (procedure)
        "170371001",  # Administration of second dose of vaccine product containing only Hepatitis B virus antigen (procedure)
        "170372008",  # Administration of third dose of vaccine product containing only Hepatitis B virus antigen (procedure)
        "170373003",  # Administration of booster dose of vaccine product containing only Hepatitis B virus antigen (procedure)
        "170434002",  # Administration of first dose of vaccine product containing only Hepatitis A and Hepatitis B virus antigens (procedure)
        "170435001",  # Administration of second dose of vaccine product containing only Hepatitis A and B virus antigens (procedure)
        "170436000",  # Administration of third dose of vaccine product containing only Hepatitis A and Hepatitis B virus antigens (procedure)
        "170437009",  # Administration of booster dose of vaccine product containing only Hepatitis A and Hepatitis B virus antigens (procedure)
        "312868009",  # Administration of vaccine product containing only Hepatitis A and Hepatitis B virus antigens (procedure)
        "396456003",  # Administration of vaccine product containing only acellular Bordetella pertussis and Corynebacterium diphtheriae and Hepatitis B virus and inactivated whole Human poliovirus antigens (procedure)
        "770608009",  # Administration of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Hepatitis B virus antigens (procedure)
        "770616000",  # Administration of first dose of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Hepatitis B virus antigens (procedure)
        "770617009",  # Administration of second dose of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Hepatitis B virus antigens (procedure)
        "770618004",  # Administration of third dose of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Hepatitis B virus antigens (procedure)
        "786846001",  # Administration of vaccine product containing only Haemophilus influenzae type B and Hepatitis B virus antigens (procedure)
        "787438002",  # Vaccination for diphtheria, pertussis, tetanus, poliomyelitis, Hepatitis B virus and Haemophilus influenzae type b (procedure)
        "572561000119108",  # Administration of vaccine product containing only acellular Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Hepatitis B virus and inactivated whole Human poliovirus antigens (procedure)
    }


class HibVaccine3DoseScheduleAdministered(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a 3-dose haemophilus influenzae type b (Hib) vaccination.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a 3-dose haemophilus influenzae type b (Hib) vaccination.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Hib Vaccine (3 dose schedule) Administered"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1084"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90647",  # Haemophilus influenzae type b vaccine (Hib), PRP-OMP conjugate, 3 dose schedule, for intramuscular use
    }
    SNOMEDCT = {
        "127787002",  # Administration of vaccine product containing only Haemophilus influenzae type B antigen (procedure)
        "170343007",  # Administration of first dose of vaccine product containing only Haemophilus influenzae type B antigen (procedure)
        "170344001",  # Administration of second dose of vaccine product containing only Haemophilus influenzae type B antigen (procedure)
        "170345000",  # Administration of third dose of vaccine product containing only Haemophilus influenzae type B antigen (procedure)
        "170346004",  # Administration of booster dose of vaccine product containing only Haemophilus influenzae type B antigen (procedure)
    }


class HibVaccine4DoseScheduleAdministered(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a 4-dose haemophilus influenzae type b (Hib) vaccines.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a procedure for a 4-dose haemophilus influenzae type b (Hib) vaccination.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Hib Vaccine (4 dose schedule) Administered"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1086"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90644",  # Meningococcal conjugate vaccine, serogroups C & Y and Haemophilus influenzae type b vaccine (Hib-MenCY), 4 dose schedule, when administered to children 6 weeks-18 months of age, for intramuscular use
        "90648",  # Haemophilus influenzae type b vaccine (Hib), PRP-T conjugate, 4 dose schedule, for intramuscular use
        "90698",  # Diphtheria, tetanus toxoids, acellular pertussis vaccine, Haemophilus influenzae type b, and inactivated poliovirus vaccine, (DTaP-IPV/Hib), for intramuscular use
        "90748",  # Hepatitis B and Haemophilus influenzae type b vaccine (Hib-HepB), for intramuscular use
    }
    SNOMEDCT = {
        "127787002",  # Administration of vaccine product containing only Haemophilus influenzae type B antigen (procedure)
        "170343007",  # Administration of first dose of vaccine product containing only Haemophilus influenzae type B antigen (procedure)
        "170344001",  # Administration of second dose of vaccine product containing only Haemophilus influenzae type B antigen (procedure)
        "170345000",  # Administration of third dose of vaccine product containing only Haemophilus influenzae type B antigen (procedure)
        "170346004",  # Administration of booster dose of vaccine product containing only Haemophilus influenzae type B antigen (procedure)
        "310306005",  # Administration of first dose of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Human poliovirus antigens (procedure)
        "310307001",  # Administration of second dose of Vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Human poliovirus antigens (procedure)
        "310308006",  # Administration of third dose of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Human poliovirus antigens (procedure)
        "312869001",  # Administration of vaccine product containing only Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Human poliovirus antigens (procedure)
        "312870000",  # Administration of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Human poliovirus antigens (procedure)
        "414001002",  # Administration of vaccine product containing only five component acellular Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and inactivated whole Human poliovirus antigens (procedure)
        "414259000",  # Administration of first dose of vaccine product containing only five component acellular Bordetella pertussis, Clostridium tetani, Corynebacterium diphtheriae, Haemophilus influenzae type B and inactivated whole Human poliovirus antigens (procedure)
        "415507003",  # Administration of second dose of vaccine product containing only five component acellular Bordetella pertussis, Clostridium tetani, Corynebacterium diphtheriae, Haemophilus influenzae type B and inactivated whole Human poliovirus antigens (procedure)
        "415712004",  # Administration of third dose of vaccine product containing only five component acellular Bordetella pertussis, Clostridium tetani, Corynebacterium diphtheriae, Haemophilus influenzae type B and inactivated whole Human poliovirus antigens (procedure)
    }


class InactivatedPolioVaccineIpvAdministered(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for an inactivated polio vaccination (IPV).

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent an inactivated polio vaccination (IPV).

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Inactivated Polio Vaccine (IPV) Administered"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1045"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90698",  # Diphtheria, tetanus toxoids, acellular pertussis vaccine, Haemophilus influenzae type b, and inactivated poliovirus vaccine, (DTaP-IPV/Hib), for intramuscular use
        "90713",  # Poliovirus vaccine, inactivated (IPV), for subcutaneous or intramuscular use
        "90723",  # Diphtheria, tetanus toxoids, acellular pertussis vaccine, hepatitis B, and inactivated poliovirus vaccine (DTaP-HepB-IPV), for intramuscular use
    }
    SNOMEDCT = {
        "310306005",  # Administration of first dose of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Human poliovirus antigens (procedure)
        "310307001",  # Administration of second dose of Vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Human poliovirus antigens (procedure)
        "310308006",  # Administration of third dose of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Human poliovirus antigens (procedure)
        "312869001",  # Administration of vaccine product containing only Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Human poliovirus antigens (procedure)
        "312870000",  # Administration of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Human poliovirus antigens (procedure)
        "313383003",  # Administration of fourth dose of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and Human poliovirus antigens (procedure)
        "390865008",  # Administration of booster dose of vaccine product containing only acellular Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Human poliovirus antigens (procedure)
        "396456003",  # Administration of vaccine product containing only acellular Bordetella pertussis and Corynebacterium diphtheriae and Hepatitis B virus and inactivated whole Human poliovirus antigens (procedure)
        "412762002",  # Administration of first dose of vaccine product containing only acellular Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Human poliovirus antigens (procedure)
        "412763007",  # Administration of second dose of vaccine product containing only acellular Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Human poliovirus antigens (procedure)
        "412764001",  # Administration of third dose of vaccine product containing only acellular Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Human poliovirus antigens (procedure)
        "414001002",  # Administration of vaccine product containing only five component acellular Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Haemophilus influenzae type B and inactivated whole Human poliovirus antigens (procedure)
        "414259000",  # Administration of first dose of vaccine product containing only five component acellular Bordetella pertussis, Clostridium tetani, Corynebacterium diphtheriae, Haemophilus influenzae type B and inactivated whole Human poliovirus antigens (procedure)
        "414619005",  # Administration of vaccine product containing only Clostridium tetani and low dose Corynebacterium diphtheriae and inactivated Human poliovirus antigens (procedure)
        "414620004",  # Administration of vaccine product containing only acellular Bordetella pertussis five component and Clostridium tetani and low dose Corynebacterium diphtheriae and inactivated whole Human poliovirus antigens (procedure)
        "415507003",  # Administration of second dose of vaccine product containing only five component acellular Bordetella pertussis, Clostridium tetani, Corynebacterium diphtheriae, Haemophilus influenzae type B and inactivated whole Human poliovirus antigens (procedure)
        "415712004",  # Administration of third dose of vaccine product containing only five component acellular Bordetella pertussis, Clostridium tetani, Corynebacterium diphtheriae, Haemophilus influenzae type B and inactivated whole Human poliovirus antigens (procedure)
        "416144004",  # Administration of third dose of vaccine product containing only Clostridium tetani and low dose Corynebacterium diphtheriae and inactivated Human poliovirus antigens (procedure)
        "416591003",  # Administration of first dose of vaccine product containing only Clostridium tetani and low dose Corynebacterium diphtheriae and inactivated Human poliovirus antigens (procedure)
        "417211006",  # Administration of first booster of vaccine product containing only Clostridium tetani and low dose Corynebacterium diphtheriae and inactivated Human poliovirus antigens (procedure)
        "417384007",  # Administration of second booster of vaccine product containing only Clostridium tetani and low dose Corynebacterium diphtheriae and inactivated Human poliovirus antigens (procedure)
        "417615007",  # Administration of second dose of vaccine product containing only Clostridium tetani and low dose Corynebacterium diphtheriae and inactivated Human poliovirus antigens (procedure)
        "786846001",  # Administration of vaccine product containing only Haemophilus influenzae type B and Hepatitis B virus antigens (procedure)
        "866186002",  # Administration of vaccine product containing only Clostridium tetani and Corynebacterium diphtheriae and Human poliovirus antigens (procedure)
        "866227002",  # Administration of booster dose of vaccine product containing only Clostridium tetani and Corynebacterium diphtheriae and Human poliovirus antigens (procedure)
        "868266002",  # Administration of second dose of vaccine product containing only Clostridium tetani and Corynebacterium diphtheriae and Human poliovirus antigens (procedure)
        "868267006",  # Administration of first dose of vaccine product containing only Clostridium tetani and Corynebacterium diphtheriae and Human poliovirus antigens (procedure)
        "868268001",  # Administration of third dose of vaccine product containing only Clostridium tetani and Corynebacterium diphtheriae and Human poliovirus antigens (procedure)
        "868273007",  # Administration of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Human poliovirus antigens (procedure)
        "868274001",  # Administration of second dose of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Human poliovirus antigens (procedure)
        "868276004",  # Administration of third dose of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Human poliovirus antigens (procedure)
        "868277008",  # Administration of first dose of vaccine product containing only Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Human poliovirus antigens (procedure)
        "870670004",  # Preschool administration of vaccine product containing only Clostridium tetani and Corynebacterium diphtheriae and Human poliovirus antigens (procedure)
        "572561000119108",  # Administration of vaccine product containing only acellular Bordetella pertussis and Clostridium tetani and Corynebacterium diphtheriae and Hepatitis B virus and inactivated whole Human poliovirus antigens (procedure)
    }


class InfluenzaVaccineAdministered(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for an influenza vaccination.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent an influenza vaccination.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Influenza Vaccine Administered"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1044"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90655",  # Influenza virus vaccine, trivalent (IIV3), split virus, preservative free, 0.25 mL dosage, for intramuscular use
        "90657",  # Influenza virus vaccine, trivalent (IIV3), split virus, 0.25 mL dosage, for intramuscular use
        "90661",  # Influenza virus vaccine, trivalent (ccIIV3), derived from cell cultures, subunit, preservative and antibiotic free, 0.5 mL dosage, for intramuscular use
        "90662",  # Influenza virus vaccine (IIV), split virus, preservative free, enhanced immunogenicity via increased antigen content, for intramuscular use
        "90673",  # Influenza virus vaccine, trivalent (RIV3), derived from recombinant DNA, hemagglutinin (HA) protein only, preservative and antibiotic free, for intramuscular use
        "90685",  # Influenza virus vaccine, quadrivalent (IIV4), split virus, preservative free, 0.25 mL dosage, for intramuscular use
        "90686",  # Influenza virus vaccine, quadrivalent (IIV4), split virus, preservative free, 0.5 mL dosage, for intramuscular use
        "90687",  # Influenza virus vaccine, quadrivalent (IIV4), split virus, 0.25 mL dosage, for intramuscular use
        "90688",  # Influenza virus vaccine, quadrivalent (IIV4), split virus, 0.5 mL dosage, for intramuscular use
    }
    SNOMEDCT = {
        "86198006",  # Administration of vaccine product containing only Influenza virus antigen (procedure)
    }


class InfluenzaVirusLaivProcedure(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent administration of live attenuated influenza vaccine.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent procedures for live attenuated influenza vaccination (quadrivalent and trivalent).

    **Exclusion Criteria:** Excludes concepts that represent procedures for recombinant or inactivated influenza vaccination.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Influenza Virus LAIV Procedure"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1088"
    DEFINITION_VERSION = "20210224"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90660",  # Influenza virus vaccine, trivalent, live (LAIV3), for intranasal use
        "90672",  # Influenza virus vaccine, quadrivalent, live (LAIV4), for intranasal use
    }


class Measles_MumpsAndRubellaMmrVaccineAdministered(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for measles, mumps and rubella (MMR) vaccination.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent measles, mumps and rubella (MMR) vaccination.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Measles, Mumps and Rubella (MMR) Vaccine Administered"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1031"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90707",  # Measles, mumps and rubella virus vaccine (MMR), live, for subcutaneous use
        "90710",  # Measles, mumps, rubella, and varicella vaccine (MMRV), live, for subcutaneous use
    }
    SNOMEDCT = {
        "38598009",  # Administration of vaccine product containing only Measles morbillivirus and Mumps orthorubulavirus and Rubella virus antigens (procedure)
        "170433008",  # Administration of second dose of vaccine product containing only Measles morbillivirus and Mumps orthorubulavirus and Rubella virus antigens (procedure)
        "432636005",  # Administration of vaccine product containing only Human alphaherpesvirus 3 and Measles morbillivirus and Mumps orthorubulavirus and Rubella virus antigens (procedure)
        "433733003",  # Administration of second dose of vaccine product containing only Human alphaherpesvirus 3 and Measles morbillivirus and Mumps orthorubulavirus and Rubella virus antigens (procedure)
        "150971000119104",  # Measles, mumps and rubella vaccination given (situation)
        "571591000119106",  # Administration of vaccine product containing only live attenuated Measles morbillivirus and Mumps orthorubulavirus and Rubella virus antigens (procedure)
        "572511000119105",  # Administration of vaccine product containing only live attenuated Measles morbillivirus and Mumps orthorubulavirus and Rubella virus and Human alphaherpesvirus 3 antigens (procedure)
    }


class PneumococcalConjugateVaccineAdministered(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a pneumococcal conjugate vaccination.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a pneumococcal conjugate vaccination.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Pneumococcal Conjugate Vaccine Administered"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1046"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90670",  # Pneumococcal conjugate vaccine, 13 valent (PCV13), for intramuscular use
    }
    SNOMEDCT = {
        "434751000124102",  # Pneumococcal conjugate vaccination (procedure)
    }


class RotavirusVaccine2DoseScheduleAdministered(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a 2-dose rotavirus vaccination.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent the administration of a 2-dose rotavirus vaccine.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Rotavirus Vaccine (2 dose schedule) Administered"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1048"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90681",  # Rotavirus vaccine, human, attenuated (RV1), 2 dose schedule, live, for oral use
    }
    SNOMEDCT = {
        "434741000124104",  # Rotavirus vaccination, 2 dose schedule (procedure)
    }


class RotavirusVaccine3DoseScheduleAdministered(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a 3-dose rotavirus vaccination.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent the administration of a 3-dose rotavirus vaccine.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Rotavirus Vaccine (3 dose schedule) Administered"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1047"
    DEFINITION_VERSION = "20190316"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90680",  # Rotavirus vaccine, pentavalent (RV5), 3 dose schedule, live, for oral use
    }
    SNOMEDCT = {
        "434731000124109",  # Rotavirus vaccination, 3 dose schedule (procedure)
    }


class VaricellaZosterVaccineVzvAdministered(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a varicella zoster vaccination.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a varicella zoster vaccination.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Varicella Zoster Vaccine (VZV) Administered"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1040"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90710",  # Measles, mumps, rubella, and varicella vaccine (MMRV), live, for subcutaneous use
        "90716",  # Varicella virus vaccine (VAR), live, for subcutaneous use
    }
    SNOMEDCT = {
        "425897001",  # Administration of first dose of vaccine product containing only Human alphaherpesvirus 3 antigen for chickenpox (procedure)
        "428502009",  # Administration of second dose of vaccine product containing only Human alphaherpesvirus 3 antigen for chickenpox (procedure)
        "473164004",  # History of varicella vaccination (situation)
        "571611000119101",  # Administration of varicella live vaccine (procedure)
    }


class HysterectomyWithNoResidualCervix(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for hysterectomies that include removal of the patient's cervix.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent total or radical hysterectomies.

    **Exclusion Criteria:** Excludes concepts that represent partial hysterectomies and hysterectomies that leave the patient's cervix intact.

    ** Used in:** CMS124v10
    """

    VALUE_SET_NAME = "Hysterectomy with No Residual Cervix"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1014"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "51925",  # Closure of vesicouterine fistula; with hysterectomy
        "56308",  # Laparoscopy, surgical; with vaginal hysterectomy with or without removal of tube(s), with or without removal of ovary(s) (laparoscopic assisted vaginal hysterectomy)
        "57530",  # Trachelectomy (cervicectomy), amputation of cervix (separate procedure)
        "57531",  # Radical trachelectomy, with bilateral total pelvic lymphadenectomy and para-aortic lymph node sampling biopsy, with or without removal of tube(s), with or without removal of ovary(s)
        "57540",  # Excision of cervical stump, abdominal approach
        "57545",  # Excision of cervical stump, abdominal approach; with pelvic floor repair
        "57550",  # Excision of cervical stump, vaginal approach
        "57555",  # Excision of cervical stump, vaginal approach; with anterior and/or posterior repair
        "57556",  # Excision of cervical stump, vaginal approach; with repair of enterocele
        "58150",  # Total abdominal hysterectomy (corpus and cervix), with or without removal of tube(s), with or without removal of ovary(s)
        "58152",  # Total abdominal hysterectomy (corpus and cervix), with or without removal of tube(s), with or without removal of ovary(s); with colpo-urethrocystopexy (eg, Marshall-Marchetti-Krantz, Burch)
        "58200",  # Total abdominal hysterectomy, including partial vaginectomy, with para-aortic and pelvic lymph node sampling, with or without removal of tube(s), with or without removal of ovary(s)
        "58210",  # Radical abdominal hysterectomy, with bilateral total pelvic lymphadenectomy and para-aortic lymph node sampling (biopsy), with or without removal of tube(s), with or without removal of ovary(s)
        "58240",  # Pelvic exenteration for gynecologic malignancy, with total abdominal hysterectomy or cervicectomy, with or without removal of tube(s), with or without removal of ovary(s), with removal of bladder and ureteral transplantations, and/or abdominoperineal resection of rectum and colon and colostomy, or any combination thereof
        "58260",  # Vaginal hysterectomy, for uterus 250 g or less
        "58262",  # Vaginal hysterectomy, for uterus 250 g or less; with removal of tube(s), and/or ovary(s)
        "58263",  # Vaginal hysterectomy, for uterus 250 g or less; with removal of tube(s), and/or ovary(s), with repair of enterocele
        "58267",  # Vaginal hysterectomy, for uterus 250 g or less; with colpo-urethrocystopexy (Marshall-Marchetti-Krantz type, Pereyra type) with or without endoscopic control
        "58270",  # Vaginal hysterectomy, for uterus 250 g or less; with repair of enterocele
        "58275",  # Vaginal hysterectomy, with total or partial vaginectomy
        "58280",  # Vaginal hysterectomy, with total or partial vaginectomy; with repair of enterocele
        "58285",  # Vaginal hysterectomy, radical (Schauta type operation)
        "58290",  # Vaginal hysterectomy, for uterus greater than 250 g
        "58291",  # Vaginal hysterectomy, for uterus greater than 250 g; with removal of tube(s) and/or ovary(s)
        "58292",  # Vaginal hysterectomy, for uterus greater than 250 g; with removal of tube(s) and/or ovary(s), with repair of enterocele
        "58293",  # Vaginal hysterectomy, for uterus greater than 250 g; with colpo-urethrocystopexy (Marshall-Marchetti-Krantz type, Pereyra type) with or without endoscopic control
        "58294",  # Vaginal hysterectomy, for uterus greater than 250 g; with repair of enterocele
        "58548",  # Laparoscopy, surgical, with radical hysterectomy, with bilateral total pelvic lymphadenectomy and para-aortic lymph node sampling (biopsy), with removal of tube(s) and ovary(s), if performed
        "58550",  # Laparoscopy, surgical, with vaginal hysterectomy, for uterus 250 g or less
        "58552",  # Laparoscopy, surgical, with vaginal hysterectomy, for uterus 250 g or less; with removal of tube(s) and/or ovary(s)
        "58553",  # Laparoscopy, surgical, with vaginal hysterectomy, for uterus greater than 250 g
        "58554",  # Laparoscopy, surgical, with vaginal hysterectomy, for uterus greater than 250 g; with removal of tube(s) and/or ovary(s)
        "58570",  # Laparoscopy, surgical, with total hysterectomy, for uterus 250 g or less
        "58571",  # Laparoscopy, surgical, with total hysterectomy, for uterus 250 g or less; with removal of tube(s) and/or ovary(s)
        "58572",  # Laparoscopy, surgical, with total hysterectomy, for uterus greater than 250 g
        "58573",  # Laparoscopy, surgical, with total hysterectomy, for uterus greater than 250 g; with removal of tube(s) and/or ovary(s)
        "58575",  # Laparoscopy, surgical, total hysterectomy for resection of malignancy (tumor debulking), with omentectomy including salpingo-oophorectomy, unilateral or bilateral, when performed
        "58951",  # Resection (initial) of ovarian, tubal or primary peritoneal malignancy with bilateral salpingo-oophorectomy and omentectomy; with total abdominal hysterectomy, pelvic and limited para-aortic lymphadenectomy
        "58953",  # Bilateral salpingo-oophorectomy with omentectomy, total abdominal hysterectomy and radical dissection for debulking
        "58954",  # Bilateral salpingo-oophorectomy with omentectomy, total abdominal hysterectomy and radical dissection for debulking; with pelvic lymphadenectomy and limited para-aortic lymphadenectomy
        "58956",  # Bilateral salpingo-oophorectomy with total omentectomy, total abdominal hysterectomy for malignancy
        "59135",  # Surgical treatment of ectopic pregnancy; interstitial, uterine pregnancy requiring total hysterectomy
    }
    ICD10PCS = {
        "0UTC0ZZ",  # Resection of Cervix, Open Approach
        "0UTC4ZZ",  # Resection of Cervix, Percutaneous Endoscopic Approach
        "0UTC7ZZ",  # Resection of Cervix, Via Natural or Artificial Opening
        "0UTC8ZZ",  # Resection of Cervix, Via Natural or Artificial Opening Endoscopic
    }
    ICD9CM = {
        "6185",  # Prolapse of vaginal vault after hysterectomy
        "6841",  # Laparoscopic total abdominal hysterectomy
        "6849",  # Other and unspecified total abdominal hysterectomy
        "6851",  # Laparoscopically assisted vaginal hysterectomy (LAVH)
        "6859",  # Other and unspecified vaginal hysterectomy
        "6861",  # Laparoscopic radical abdominal hysterectomy
        "6869",  # Other and unspecified radical abdominal hysterectomy
        "6871",  # Laparoscopic radical vaginal hysterectomy [LRVH]
        "6879",  # Other and unspecified radical vaginal hysterectomy
        "688",  # Pelvic evisceration
    }
    SNOMEDCT = {
        "24293001",  # Excision of cervical stump by abdominal approach (procedure)
        "27950001",  # Total hysterectomy with unilateral removal of ovary (procedure)
        "28301000",  # Manchester-Fothergill operation on uterus (procedure)
        "31545000",  # Total hysterectomy with unilateral removal of tube (procedure)
        "35955002",  # Radical vaginal hysterectomy (procedure)
        "41566006",  # Excision of cervical stump by vaginal approach (procedure)
        "46226009",  # Cervicectomy with synchronous colporrhaphy (procedure)
        "59750000",  # Total hysterectomy with unilateral removal of tube and ovary (procedure)
        "82418001",  # Manchester operation on uterus (procedure)
        "86477000",  # Total hysterectomy with removal of both tubes and ovaries (procedure)
        "88144003",  # Removal of ectopic interstitial uterine pregnancy requiring total hysterectomy (procedure)
        "116140006",  # Total hysterectomy (procedure)
        "116142003",  # Radical hysterectomy (procedure)
        "116143008",  # Total abdominal hysterectomy (procedure)
        "116144002",  # Total abdominal hysterectomy with bilateral salpingo-oophorectomy (procedure)
        "176697007",  # Repair of vaginal prolapse and amputation of cervix uteri (procedure)
        "236888001",  # Laparoscopic total hysterectomy (procedure)
        "236891001",  # Laparoscopic radical hysterectomy (procedure)
        "287924009",  # Excision of cervix stump (procedure)
        "307771009",  # Radical abdominal hysterectomy (procedure)
        "361222003",  # Wertheim-Meigs abdominal hysterectomy (procedure)
        "361223008",  # Wertheim operation (procedure)
        "387626007",  # Amputation of cervix (procedure)
        "414575003",  # Laparoscopic total abdominal hysterectomy and bilateral salpingo-oophorectomy (procedure)
        "440383008",  # Radical amputation of cervix with bilateral total pelvic lymphadenectomy and paraaortic lymph node biopsy (procedure)
        "446446002",  # Total abdominal hysterectomy and removal of vaginal cuff (procedure)
        "446679008",  # Total laparoscopic excision of uterus by abdominal approach (procedure)
        "447771005",  # Abdominal hysterectomy and excision of periuterine tissue (procedure)
        "473171009",  # History of vaginal hysterectomy (situation)
        "708877008",  # Laparoscopic total hysterectomy using robotic assistance (procedure)
        "708878003",  # Laparoscopic radical hysterectomy using robotic assistance (procedure)
        "739671004",  # Total hysterectomy with left oophorectomy (procedure)
        "739672006",  # Total hysterectomy with right oophorectomy (procedure)
        "739673001",  # Total hysterectomy with left salpingo-oophorectomy (procedure)
        "739674007",  # Total hysterectomy with right salpingo-oophorectomy (procedure)
        "740514001",  # Total hysterectomy with right salpingectomy (procedure)
        "740515000",  # Total hysterectomy with left salpingectomy (procedure)
        "767610009",  # Total hysterectomy via vaginal approach (procedure)
        "767611008",  # Total abdominal hysterectomy using intrafascial technique (procedure)
        "767612001",  # Total hysterectomy via vaginal approach using intrafascial technique (procedure)
    }


class BilateralMastectomy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for bilateral mastectomy.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a procedure for bilateral mastectomy.

    **Exclusion Criteria:** Excludes concepts that represent procedures for a unilateral or unspecified mastectomy.

    ** Used in:** CMS125v10
    """

    VALUE_SET_NAME = "Bilateral Mastectomy"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1005"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    ICD10PCS = {
        "0HTV0ZZ",  # Resection of Bilateral Breast, Open Approach
    }
    ICD9CM = {
        "8542",  # Bilateral simple mastectomy
        "8544",  # Bilateral extended simple mastectomy
        "8546",  # Bilateral radical mastectomy
        "8548",  # Bilateral extended radical mastectomy
    }
    SNOMEDCT = {
        "14693006",  # Bilateral subcutaneous mammectomy (procedure)
        "14714006",  # Bilateral mastectomy with excision of bilateral regional lymph nodes (procedure)
        "17086001",  # Modified radical mastectomy, bilateral (procedure)
        "22418005",  # Bilateral simple mastectomy (procedure)
        "27865001",  # Bilateral mastectomy (procedure)
        "52314009",  # Bilateral mastectomy extended simple (procedure)
        "60633004",  # Bilateral subcutaneous mammectomy with synchronous implant (procedure)
        "76468001",  # Bilateral radical mastectomy (procedure)
        "456903003",  # Bilateral extended radical mastectomy (procedure)
        "726636007",  # Prophylactic bilateral mastectomy (procedure)
        "836436008",  # Simple mastectomy of bilateral breasts using robotic assistance (procedure)
        "870629001",  # Bilateral mastectomy for female to male transsexual (procedure)
    }


class UnilateralMastectomyLeft(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for unilateral mastectomy of the left breast.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a procedure for a unilateral mastectomy of the left breast.

    **Exclusion Criteria:** Excludes concepts that represent procedures for right or bilateral, or unspecified mastectomy.

    ** Used in:** CMS125v10
    """

    VALUE_SET_NAME = "Unilateral Mastectomy Left"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1133"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    ICD10PCS = {
        "0HTU0ZZ",  # Resection of Left Breast, Open Approach
    }
    SNOMEDCT = {
        "428571003",  # Mastectomy of left breast (procedure)
        "726429001",  # Radical mastectomy of left breast (procedure)
        "726435001",  # Subcutaneous mastectomy of left breast (procedure)
        "726437009",  # Modified radical mastectomy of left breast (procedure)
        "741009001",  # Simple mastectomy of left breast (procedure)
        "741018004",  # Subcutaneous mastectomy of left breast with prosthetic implant (procedure)
        "451211000124109",  # Prophylactic mastectomy of left breast (procedure)
    }


class UnilateralMastectomyRight(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for unilateral mastectomy of the right breast.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a procedure for unilateral mastectomy of the right breast.

    **Exclusion Criteria:** Excludes concepts that represent procedures for left or bilateral, or unspecified mastectomy.

    ** Used in:** CMS125v10
    """

    VALUE_SET_NAME = "Unilateral Mastectomy Right"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1134"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    ICD10PCS = {
        "0HTT0ZZ",  # Resection of Right Breast, Open Approach
    }
    SNOMEDCT = {
        "429400009",  # Mastectomy of right breast (procedure)
        "726430006",  # Radical mastectomy of right breast (procedure)
        "726434002",  # Subcutaneous mastectomy of right breast (procedure)
        "726436000",  # Modified radical mastectomy of right breast (procedure)
        "741010006",  # Simple mastectomy of right breast (procedure)
        "741019007",  # Subcutaneous mastectomy of right breast with prosthetic implant (procedure)
        "451201000124106",  # Prophylactic mastectomy of right breast (procedure)
        "12275171000119105",  # Postmastectomy lymphedema syndrome of right upper limb (disorder)
    }


class ProstateCancerTreatment(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of procedures for prostate cancer treatments.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a procedure for interstitial prostate brachytherapy, external beam radiotherapy to the prostate, and radical prostatectomy.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS129v11
    """

    VALUE_SET_NAME = "Prostate Cancer Treatment"
    OID = "2.16.840.1.113883.3.526.3.398"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "55810",  # Prostatectomy, perineal radical
        "55812",  # Prostatectomy, perineal radical; with lymph node biopsy(s) (limited pelvic lymphadenectomy)
        "55815",  # Prostatectomy, perineal radical; with bilateral pelvic lymphadenectomy, including external iliac, hypogastric and obturator nodes
        "55840",  # Prostatectomy, retropubic radical, with or without nerve sparing
        "55842",  # Prostatectomy, retropubic radical, with or without nerve sparing; with lymph node biopsy(s) (limited pelvic lymphadenectomy)
        "55845",  # Prostatectomy, retropubic radical, with or without nerve sparing; with bilateral pelvic lymphadenectomy, including external iliac, hypogastric, and obturator nodes
        "55866",  # Laparoscopy, surgical prostatectomy, retropubic radical, including nerve sparing, includes robotic assistance, when performed
        "55875",  # Transperineal placement of needles or catheters into prostate for interstitial radioelement application, with or without cystoscopy
        "77427",  # Radiation treatment management, 5 treatments
        "77435",  # Stereotactic body radiation therapy, treatment management, per treatment course, to 1 or more lesions, including image guidance, entire course not to exceed 5 fractions
        "77772",  # Remote afterloading high dose rate radionuclide interstitial or intracavitary brachytherapy, includes basic dosimetry, when performed; over 12 channels
        "77778",  # Interstitial radiation source application, complex, includes supervision, handling, loading of radiation source, when performed
        "77799",  # Unlisted procedure, clinical brachytherapy
    }
    SNOMEDCT = {
        "8782006",  # Radical perineal prostatectomy (procedure)
        "10492003",  # Radionuclide therapy for glandular suppression (procedure)
        "14473006",  # Surface brachytherapy (procedure)
        "19149007",  # Subtotal retropubic prostatectomy (procedure)
        "21190008",  # Two stage subtotal suprapubic prostatectomy (procedure)
        "21372000",  # Radium therapy (procedure)
        "24242005",  # Cobalt-60 therapy (procedure)
        "26294005",  # Radical prostatectomy (procedure)
        "27877006",  # Excision of lesion of periprostatic tissue (procedure)
        "28579000",  # Radical retropubic prostatectomy with lymph node biopsy (procedure)
        "30426000",  # Subtotal prostatectomy (procedure)
        "36253005",  # Suprapubic prostatectomy (procedure)
        "37851009",  # Radical perineal prostatectomy with bilateral pelvic lymphadenectomy (procedure)
        "38915000",  # Radionuclide therapy for gland ablation (procedure)
        "41371003",  # Perineal prostatectomy (procedure)
        "41416003",  # Radical retropubic prostatectomy with bilateral pelvic lymphadenectomy (procedure)
        "57525009",  # Subtotal perineal prostatectomy (procedure)
        "62867004",  # Teleradiotherapy with radioactive cesium (procedure)
        "65381004",  # Intra-articular radionuclide therapy (procedure)
        "65551008",  # Radical retropubic prostatectomy (procedure)
        "67598001",  # Retropubic prostatectomy (procedure)
        "68986004",  # Transurethral resection of prostate, first stage of two stages (procedure)
        "72388004",  # Radical perineal prostatectomy with lymph node biopsy (procedure)
        "77613002",  # Teleradiotherapy with iodine-125 (procedure)
        "81232004",  # Radical cystoprostatectomy (procedure)
        "83154001",  # Excision of lesion of prostate (procedure)
        "84755001",  # Radiation therapy treatment management (procedure)
        "85768003",  # Excision of median bar of prostate by transurethral approach (procedure)
        "87795007",  # Complete transurethral resection of prostate, including control of postoperative bleeding (procedure)
        "90199006",  # Transurethral prostatectomy (procedure)
        "90470006",  # Prostatectomy (procedure)
        "91531008",  # One stage subtotal suprapubic prostatectomy (procedure)
        "113120007",  # Interstitial brachytherapy (procedure)
        "116244007",  # Enucleation of prostate (procedure)
        "118161009",  # Laser enucleation of the prostate (procedure)
        "118162002",  # Laser enucleation of the prostate with intravesical morcellation (procedure)
        "118163007",  # Open enucleation of the prostate (procedure)
        "168922004",  # Interstitial contrast radiology (procedure)
        "169327006",  # Radium contact therapy (procedure)
        "169328001",  # Beta source contact therapy (procedure)
        "169329009",  # Mold technique gamma/beta (procedure)
        "169340001",  # Internal metabolic radiotherapy (procedure)
        "169349000",  # Internal radiotherapy - unsealed source (procedure)
        "169359004",  # Internal radiotherapy - permanent seeds (procedure)
        "176106009",  # Radical cystoprostatourethrectomy (procedure)
        "176258007",  # Open prostatectomy (procedure)
        "176260009",  # Transvesical two stage prostatectomy (procedure)
        "176261008",  # Radical prostatectomy without pelvic node excision (procedure)
        "176262001",  # Radical prostatectomy with pelvic node sampling (procedure)
        "176263006",  # Radical prostatectomy with pelvic lymphadenectomy (procedure)
        "176267007",  # Open excision of prostatic lesion (procedure)
        "176288003",  # Transurethral laser prostatectomy (procedure)
        "228677009",  # Cesium 137 brachytherapy (procedure)
        "228684001",  # Iridium 192 brachytherapy (procedure)
        "228688003",  # Californium 252 brachytherapy (procedure)
        "228690002",  # Iodine 125 brachytherapy (procedure)
        "228692005",  # Radon 222 brachytherapy (procedure)
        "228693000",  # Ruthenium 106 brachytherapy (procedure)
        "228694006",  # Strontium 90 brachytherapy (procedure)
        "228695007",  # Tantalum 182 brachytherapy (procedure)
        "228697004",  # Yttrium 90 therapy (procedure)
        "228698009",  # Iodine 131 therapy (procedure)
        "228699001",  # Phosphorus 32 therapy (procedure)
        "228701001",  # Strontium 89 therapy (procedure)
        "228702008",  # Gold 198 therapy (procedure)
        "236252003",  # Revision of transurethral prostatectomy (procedure)
        "271291003",  # Temporary implant radiotherapy (procedure)
        "312235007",  # Radiolabeled antibody therapy (procedure)
        "314202001",  # Endoscopic resection of prostate using an electrotome (procedure)
        "359922007",  # Excisional periprostatic biopsy (procedure)
        "359926005",  # Excision of periprostatic tissue (procedure)
        "384691004",  # Intraluminal brachytherapy (procedure)
        "384692006",  # Intracavitary brachytherapy (procedure)
        "394902000",  # High dose brachytherapy (procedure)
        "394918006",  # Iodine seed radiotherapy (procedure)
        "399124002",  # Unsealed radionuclide procedure (procedure)
        "399180008",  # Interstitial radioactive colloid therapy (procedure)
        "399315003",  # Radionuclide therapy (procedure)
        "427985002",  # Endoscopic excision of prostate using laser (procedure)
        "433224001",  # Radionuclide rhenium 186 hydroxyethylidene diphosphonate therapy (procedure)
        "440093006",  # Insertion of radioactive implant into interstitial tissue using ultrasound guidance (procedure)
        "440094000",  # Insertion of radioactive implant into interstitial tissue of prostate with transperineal insertion of catheter (procedure)
        "764675000",  # Radionuclide imaging using samarium (153-Sm) lexidronam (procedure)
        "427541000119103",  # Intravenous radionuclide therapy (procedure)
    }


class SalvageTherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of procedures for salvage therapy.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a procedure for salvage therapy.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS129v11
    """

    VALUE_SET_NAME = "Salvage Therapy"
    OID = "2.16.840.1.113883.3.526.3.399"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "51597",  # Pelvic exenteration, complete, for vesical, prostatic or urethral malignancy, with removal of bladder and ureteral transplantations, with or without hysterectomy and/or abdominoperineal resection of rectum and colon and colostomy, or any combination thereof
        "55860",  # Exposure of prostate, any approach, for insertion of radioactive substance
        "55862",  # Exposure of prostate, any approach, for insertion of radioactive substance; with lymph node biopsy(s) (limited pelvic lymphadenectomy)
        "55865",  # Exposure of prostate, any approach, for insertion of radioactive substance; with bilateral pelvic lymphadenectomy, including external iliac, hypogastric and obturator nodes
    }
    SNOMEDCT = {
        "236209003",  # Salvage cystoprostatourethrectomy (procedure)
        "236211007",  # Salvage cystoprostatectomy (procedure)
    }


class Colonoscopy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a colonoscopy.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a screening or diagnostic colonoscopy.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS130v10
    """

    VALUE_SET_NAME = "Colonoscopy"
    OID = "2.16.840.1.113883.3.464.1003.108.12.1020"
    DEFINITION_VERSION = "20171219"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "44388",  # Colonoscopy through stoma; diagnostic, including collection of specimen(s) by brushing or washing, when performed (separate procedure)
        "44389",  # Colonoscopy through stoma; with biopsy, single or multiple
        "44390",  # Colonoscopy through stoma; with removal of foreign body(s)
        "44391",  # Colonoscopy through stoma; with control of bleeding, any method
        "44392",  # Colonoscopy through stoma; with removal of tumor(s), polyp(s), or other lesion(s) by hot biopsy forceps
        "44393",  # Colonoscopy through stoma; with ablation of tumor(s), polyp(s), or other lesion(s) not amenable to removal by hot biopsy forceps, bipolar cautery or snare technique
        "44394",  # Colonoscopy through stoma; with removal of tumor(s), polyp(s), or other lesion(s) by snare technique
        "44397",  # Colonoscopy through stoma; with transendoscopic stent placement (includes predilation)
        "44401",  # Colonoscopy through stoma; with ablation of tumor(s), polyp(s), or other lesion(s) (includes pre-and post-dilation and guide wire passage, when performed)
        "44402",  # Colonoscopy through stoma; with endoscopic stent placement (including pre- and post-dilation and guide wire passage, when performed)
        "44403",  # Colonoscopy through stoma; with endoscopic mucosal resection
        "44404",  # Colonoscopy through stoma; with directed submucosal injection(s), any substance
        "44405",  # Colonoscopy through stoma; with transendoscopic balloon dilation
        "44406",  # Colonoscopy through stoma; with endoscopic ultrasound examination, limited to the sigmoid, descending, transverse, or ascending colon and cecum and adjacent structures
        "44407",  # Colonoscopy through stoma; with transendoscopic ultrasound guided intramural or transmural fine needle aspiration/biopsy(s), includes endoscopic ultrasound examination limited to the sigmoid, descending, transverse, or ascending colon and cecum and adjacent structures
        "44408",  # Colonoscopy through stoma; with decompression (for pathologic distention) (eg, volvulus, megacolon), including placement of decompression tube, when performed
        "45355",  # Colonoscopy, rigid or flexible, transabdominal via colotomy, single or multiple
        "45378",  # Colonoscopy, flexible; diagnostic, including collection of specimen(s) by brushing or washing, when performed (separate procedure)
        "45379",  # Colonoscopy, flexible; with removal of foreign body(s)
        "45380",  # Colonoscopy, flexible; with biopsy, single or multiple
        "45381",  # Colonoscopy, flexible; with directed submucosal injection(s), any substance
        "45382",  # Colonoscopy, flexible; with control of bleeding, any method
        "45383",  # Colonoscopy, flexible, proximal to splenic flexure; with ablation of tumor(s), polyp(s), or other lesion(s) not amenable to removal by hot biopsy forceps, bipolar cautery or snare technique
        "45384",  # Colonoscopy, flexible; with removal of tumor(s), polyp(s), or other lesion(s) by hot biopsy forceps
        "45385",  # Colonoscopy, flexible; with removal of tumor(s), polyp(s), or other lesion(s) by snare technique
        "45386",  # Colonoscopy, flexible; with transendoscopic balloon dilation
        "45387",  # Colonoscopy, flexible, proximal to splenic flexure; with transendoscopic stent placement (includes predilation)
        "45388",  # Colonoscopy, flexible; with ablation of tumor(s), polyp(s), or other lesion(s) (includes pre- and post-dilation and guide wire passage, when performed)
        "45389",  # Colonoscopy, flexible; with endoscopic stent placement (includes pre- and post-dilation and guide wire passage, when performed)
        "45390",  # Colonoscopy, flexible; with endoscopic mucosal resection
        "45391",  # Colonoscopy, flexible; with endoscopic ultrasound examination limited to the rectum, sigmoid, descending, transverse, or ascending colon and cecum, and adjacent structures
        "45392",  # Colonoscopy, flexible; with transendoscopic ultrasound guided intramural or transmural fine needle aspiration/biopsy(s), includes endoscopic ultrasound examination limited to the rectum, sigmoid, descending, transverse, or ascending colon and cecum, and adjacent structures
        "45393",  # Colonoscopy, flexible; with decompression (for pathologic distention) (eg, volvulus, megacolon), including placement of decompression tube, when performed
        "45398",  # Colonoscopy, flexible; with band ligation(s) (eg, hemorrhoids)
    }
    HCPCSLEVELII = {
        "G0105",  # Colorectal cancer screening; colonoscopy on individual at high risk
        "G0121",  # Colorectal cancer screening; colonoscopy on individual not meeting criteria for high risk
    }
    SNOMEDCT = {
        "8180007",  # Fiberoptic colonoscopy through colostomy (procedure)
        "12350003",  # Colonoscopy with rigid sigmoidoscope through colotomy (procedure)
        "25732003",  # Fiberoptic colonoscopy with biopsy (procedure)
        "34264006",  # Intraoperative colonoscopy (procedure)
        "73761001",  # Colonoscopy (procedure)
        "174158000",  # Open colonoscopy (procedure)
        "235150006",  # Total colonoscopy (procedure)
        "235151005",  # Limited colonoscopy (procedure)
        "310634005",  # Check colonoscopy (procedure)
        "367535003",  # Fiberoptic colonoscopy (procedure)
        "425672002",  # Diagnostic endoscopic examination of ileoanal pouch and biopsy of ileoanal pouch using colonoscope (procedure)
        "425937002",  # Diagnostic endoscopic examination of enteric pouch using colonoscope (procedure)
        "427459009",  # Diagnostic endoscopic examination of colonic pouch and biopsy of colonic pouch using colonoscope (procedure)
        "443998000",  # Colonoscopy through colostomy with endoscopic biopsy of colon (procedure)
        "444783004",  # Screening colonoscopy (procedure)
        "446521004",  # Colonoscopy and excision of mucosa of colon (procedure)
        "446745002",  # Colonoscopy and biopsy of colon (procedure)
        "447021001",  # Colonoscopy and tattooing (procedure)
        "709421007",  # Colonoscopy and dilatation of stricture of colon (procedure)
        "710293001",  # Colonoscopy using fluoroscopic guidance (procedure)
        "711307001",  # Colonoscopy using X-ray guidance (procedure)
        "713154003",  # Endoscopic submucosal dissection of rectum using colonoscope (procedure)
        "851000119109",  # History of colonoscopy (situation)
    }


class FlexibleSigmoidoscopy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a flexible sigmoidoscopy.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a flexible sigmoidoscopy.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS130v10
    """

    VALUE_SET_NAME = "Flexible Sigmoidoscopy"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1010"
    DEFINITION_VERSION = "20171219"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "44397",  # Colonoscopy through stoma; with transendoscopic stent placement (includes predilation)
        "45330",  # Sigmoidoscopy, flexible; diagnostic, including collection of specimen(s) by brushing or washing, when performed (separate procedure)
        "45331",  # Sigmoidoscopy, flexible; with biopsy, single or multiple
        "45332",  # Sigmoidoscopy, flexible; with removal of foreign body(s)
        "45333",  # Sigmoidoscopy, flexible; with removal of tumor(s), polyp(s), or other lesion(s) by hot biopsy forceps
        "45334",  # Sigmoidoscopy, flexible; with control of bleeding, any method
        "45335",  # Sigmoidoscopy, flexible; with directed submucosal injection(s), any substance
        "45337",  # Sigmoidoscopy, flexible; with decompression (for pathologic distention) (eg, volvulus, megacolon), including placement of decompression tube, when performed
        "45338",  # Sigmoidoscopy, flexible; with removal of tumor(s), polyp(s), or other lesion(s) by snare technique
        "45339",  # Sigmoidoscopy, flexible; with ablation of tumor(s), polyp(s), or other lesion(s) not amenable to removal by hot biopsy forceps, bipolar cautery or snare technique
        "45340",  # Sigmoidoscopy, flexible; with transendoscopic balloon dilation
        "45341",  # Sigmoidoscopy, flexible; with endoscopic ultrasound examination
        "45342",  # Sigmoidoscopy, flexible; with transendoscopic ultrasound guided intramural or transmural fine needle aspiration/biopsy(s)
        "45345",  # Sigmoidoscopy, flexible; with transendoscopic stent placement (includes predilation)
        "45346",  # Sigmoidoscopy, flexible; with ablation of tumor(s), polyp(s), or other lesion(s) (includes pre- and post-dilation and guide wire passage, when performed)
        "45347",  # Sigmoidoscopy, flexible; with placement of endoscopic stent (includes pre- and post-dilation and guide wire passage, when performed)
        "45349",  # Sigmoidoscopy, flexible; with endoscopic mucosal resection
        "45350",  # Sigmoidoscopy, flexible; with band ligation(s) (eg, hemorrhoids)
    }
    HCPCSLEVELII = {
        "G0104",  # Colorectal cancer screening; flexible sigmoidoscopy
    }
    SNOMEDCT = {
        "44441009",  # Flexible fiberoptic sigmoidoscopy (procedure)
        "396226005",  # Flexible fiberoptic sigmoidoscopy with biopsy (procedure)
        "425634007",  # Diagnostic endoscopic examination of lower bowel and sampling for bacterial overgrowth using fiberoptic sigmoidoscope (procedure)
        "841000119107",  # History of flexible sigmoidoscopy (situation)
    }


class TotalColectomy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a total colectomy.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a total colectomy.

    **Exclusion Criteria:** Excludes concepts that represent partial colectomies.

    ** Used in:** CMS130v10
    """

    VALUE_SET_NAME = "Total Colectomy"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1019"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "44150",  # Colectomy, total, abdominal, without proctectomy; with ileostomy or ileoproctostomy
        "44151",  # Colectomy, total, abdominal, without proctectomy; with continent ileostomy
        "44152",  # Colectomy, total, abdominal, without proctectomy; with rectal mucosectomy, ileoanal anastomosis, with or without loop ileostomy
        "44153",  # Colectomy, total, abdominal, without proctectomy; with rectal mucosectomy, ileoanal anastomosis, creation of ileal reservoir (S or J), with or without loop ileostomy
        "44155",  # Colectomy, total, abdominal, with proctectomy; with ileostomy
        "44156",  # Colectomy, total, abdominal, with proctectomy; with continent ileostomy
        "44157",  # Colectomy, total, abdominal, with proctectomy; with ileoanal anastomosis, includes loop ileostomy, and rectal mucosectomy, when performed
        "44158",  # Colectomy, total, abdominal, with proctectomy; with ileoanal anastomosis, creation of ileal reservoir (S or J), includes loop ileostomy, and rectal mucosectomy, when performed
        "44210",  # Laparoscopy, surgical; colectomy, total, abdominal, without proctectomy, with ileostomy or ileoproctostomy
        "44211",  # Laparoscopy, surgical; colectomy, total, abdominal, with proctectomy, with ileoanal anastomosis, creation of ileal reservoir (S or J), with loop ileostomy, includes rectal mucosectomy, when performed
        "44212",  # Laparoscopy, surgical; colectomy, total, abdominal, with proctectomy, with ileostomy
    }
    ICD10PCS = {
        "0DTE0ZZ",  # Resection of Large Intestine, Open Approach
        "0DTE4ZZ",  # Resection of Large Intestine, Percutaneous Endoscopic Approach
        "0DTE7ZZ",  # Resection of Large Intestine, Via Natural or Artificial Opening
        "0DTE8ZZ",  # Resection of Large Intestine, Via Natural or Artificial Opening Endoscopic
    }
    ICD9CM = {
        "4581",  # Laparoscopic total intra-abdominal colectomy
        "4582",  # Open total intra-abdominal colectomy
        "4583",  # Other and unspecified total intra-abdominal colectomy
    }
    SNOMEDCT = {
        "456004",  # Total abdominal colectomy with ileostomy (procedure)
        "26390003",  # Total colectomy (procedure)
        "31130001",  # Total abdominal colectomy with proctectomy and ileostomy (procedure)
        "36192008",  # Total abdominal colectomy with ileoproctostomy (procedure)
        "44751009",  # Total abdominal colectomy with proctectomy and continent ileostomy (procedure)
        "80294005",  # Total abdominal colectomy with rectal mucosectomy and ileoanal anastomosis (procedure)
        "303401008",  # Parks panproctocolectomy, anastomosis of ileum to anus and creation of pouch (procedure)
        "307666008",  # Total colectomy and ileostomy (procedure)
        "307667004",  # Total colectomy, ileostomy and rectal mucous fistula (procedure)
        "307669001",  # Total colectomy, ileostomy and closure of rectal stump (procedure)
        "713165008",  # Laparoscopic total colectomy with ileo-rectal anastomosis (procedure)
        "787108001",  # Laparoscopic restorative proctocolectomy with ileal pouch anal anastomosis (procedure)
        "787109009",  # Excision of entire colon and entire rectum (procedure)
        "787874000",  # Laparoscopic total colectomy (procedure)
        "787875004",  # Laparoscopic total colectomy and loop ileostomy (procedure)
        "787876003",  # Laparoscopic total colectomy and ileostomy (procedure)
        "858579005",  # Excision of entire colon, entire rectum and entire anal canal (procedure)
        "119771000119101",  # History of total colectomy (situation)
    }


class CataractSurgery(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of procedures for cataract surgery.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a procedure of cataract surgery.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS133v10
    """

    VALUE_SET_NAME = "Cataract Surgery"
    OID = "2.16.840.1.113883.3.526.3.1411"
    DEFINITION_VERSION = "20210210"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "66840",  # Removal of lens material; aspiration technique, 1 or more stages
        "66850",  # Removal of lens material; phacofragmentation technique (mechanical or ultrasonic) (eg, phacoemulsification), with aspiration
        "66852",  # Removal of lens material; pars plana approach, with or without vitrectomy
        "66920",  # Removal of lens material; intracapsular
        "66930",  # Removal of lens material; intracapsular, for dislocated lens
        "66940",  # Removal of lens material; extracapsular (other than 66840, 66850, 66852)
        "66982",  # Extracapsular cataract removal with insertion of intraocular lens prosthesis (1-stage procedure), manual or mechanical technique (eg, irrigation and aspiration or phacoemulsification), complex, requiring devices or techniques not generally used in routine cataract surgery (eg, iris expansion device, suture support for intraocular lens, or primary posterior capsulorrhexis) or performed on patients in the amblyogenic developmental stage; without endoscopic cyclophotocoagulation
        "66983",  # Intracapsular cataract extraction with insertion of intraocular lens prosthesis (1 stage procedure)
        "66984",  # Extracapsular cataract removal with insertion of intraocular lens prosthesis (1 stage procedure), manual or mechanical technique (eg, irrigation and aspiration or phacoemulsification); without endoscopic cyclophotocoagulation
    }
    SNOMEDCT = {
        "5130002",  # Extraction of primary membranous cataract by discission (procedure)
        "9137006",  # Discission of membranous cataract, secondary (procedure)
        "10178000",  # Extracapsular extraction of cataract by inferior temporal route (procedure)
        "12163000",  # Needling of secondary cataract (procedure)
        "31705006",  # Extraction of cataract by rotoextraction with aspiration by posterior route (procedure)
        "35717002",  # Discission of congenital cataract (procedure)
        "39243005",  # Mechanical fragmentation of cataract with extraction by posterior route (procedure)
        "46309001",  # Extraction of primary membranous cataract by excision (procedure)
        "46426006",  # Cryoextraction of cataract by inferior temporal route (procedure)
        "46562009",  # Incisional discission of secondary membranous cataract and anterior hyaloid (procedure)
        "50538003",  # Discission of membranous cataract, primary (procedure)
        "51839008",  # Extraction of primary membranous cataract by needling (procedure)
        "54885007",  # Extraction of cataract (procedure)
        "65812008",  # Removal of secondary membranous cataract with iridectomy (procedure)
        "67760003",  # Extracapsular extraction of cataract by rotoextraction with aspiration (procedure)
        "69360005",  # Extracapsular extraction of cataract by mechanical fragmentation with aspiration by posterior route (procedure)
        "74490003",  # Mechanical fragmentation of primary membranous cataract (procedure)
        "75814005",  # Erysiphake extraction of cataract by inferior temporal route (procedure)
        "79611007",  # Extracapsular extraction of cataract by curette evacuation (procedure)
        "82155009",  # Extracapsular extraction of cataract by emulsification with aspiration (procedure)
        "84149000",  # Aspiration of cataract by phacoemulsification (procedure)
        "85622008",  # Cryoextraction of cataract by intracapsular approach (procedure)
        "88282000",  # Extracapsular extraction of cataract by mechanical fragmentation with aspiration (procedure)
        "89153001",  # Extracapsular extraction of cataract by rotoextraction with aspiration by posterior route (procedure)
        "110473004",  # Cataract surgery (procedure)
        "112963003",  # Aspiration of cataract (procedure)
        "112964009",  # Extraction of cataract by rotoextraction with aspiration (procedure)
        "172523009",  # Intracapsular extraction of lens (procedure)
        "231744001",  # Cataract extraction, insertion of intraocular lens and trabeculectomy (procedure)
        "308694002",  # Extracapsular cataract extraction and insertion of intraocular lens (procedure)
        "308695001",  # Intracapsular cataract extraction and insertion of intraocular lens (procedure)
        "313999004",  # Small incision phacoemulsification of cataract and insertion of intraocular lens (procedure)
        "335636001",  # Extraction of primary membranous cataract by phacofragmentation (procedure)
        "336651000",  # Extraction of primary membranous cataract by mechanical fragmentation (procedure)
        "361191005",  # Extraction of cataract by ultrasonic phacofragmentation (procedure)
        "385468004",  # Cataract extraction and insertion of intraocular lens (procedure)
        "397544007",  # Complicated cataract surgery (procedure)
        "404628003",  # Intracapsular cataract extraction (procedure)
        "415089008",  # Phacoemulsification of cataract with intraocular lens implantation (procedure)
        "417493007",  # Small incision manual extracapsular cataract extraction (procedure)
        "418430006",  # Bimanual phacoemulsification of cataract with intraocular lens implantation (procedure)
        "419767009",  # Bimanual microincisional phacoemulsification of cataract with intraocular lens implantation (procedure)
        "420260004",  # Bimanual phacoemulsification (procedure)
        "420526005",  # Coaxial phacoemulsfication (procedure)
        "424945000",  # Torsional phacoemulsification (procedure)
        "446548003",  # Extraction of cataract and trabeculectomy (procedure)
        "860930005",  # Surgery of cataract of left eye (procedure)
        "860934001",  # Surgery of cataract of right eye (procedure)
    }


class DialysisServices(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for dialysis services.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent dialysis services.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS165v10, CMS134v10
    """

    VALUE_SET_NAME = "Dialysis Services"
    OID = "2.16.840.1.113883.3.464.1003.109.12.1013"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90935",  # Hemodialysis procedure with single evaluation by a physician or other qualified health care professional
        "90937",  # Hemodialysis procedure requiring repeated evaluation(s) with or without substantial revision of dialysis prescription
        "90945",  # Dialysis procedure other than hemodialysis (eg, peritoneal dialysis, hemofiltration, or other continuous renal replacement therapies), with single evaluation by a physician or other qualified health care professional
        "90947",  # Dialysis procedure other than hemodialysis (eg, peritoneal dialysis, hemofiltration, or other continuous renal replacement therapies) requiring repeated evaluations by a physician or other qualified health care professional, with or without substantial revision of dialysis prescription
        "90997",  # Hemoperfusion (eg, with activated charcoal or resin)
        "90999",  # Unlisted dialysis procedure, inpatient or outpatient
        "99512",  # Home visit for hemodialysis
    }
    HCPCSLEVELII = {
        "G0257",  # Unscheduled or emergency dialysis treatment for an esrd patient in a hospital outpatient department that is not certified as an esrd facility
        "S9339",  # Home therapy; peritoneal dialysis, administrative services, professional pharmacy services, care coordination and all necessary supplies and equipment (drugs and nursing visits coded separately), per diem
    }
    SNOMEDCT = {
        "676002",  # Peritoneal dialysis including cannulation (procedure)
        "10848006",  # Removal of peritoneal dialysis catheter (procedure)
        "11932001",  # Stabilizing hemodialysis (procedure)
        "14684005",  # Peritoneal dialysis excluding cannulation (procedure)
        "34897002",  # Hemodialysis, maintenance in hospital (procedure)
        "57274006",  # Initial hemodialysis (procedure)
        "67970008",  # Hemodialysis, maintenance at home (procedure)
        "68341005",  # Hemodialysis, supervision at home (procedure)
        "71192002",  # Peritoneal dialysis (procedure)
        "108241001",  # Dialysis procedure (procedure)
        "180273006",  # Removal of chronic ambulatory peritoneal dialysis catheter (procedure)
        "225230008",  # Chronic peritoneal dialysis (procedure)
        "225231007",  # Stab peritoneal dialysis (procedure)
        "233575001",  # Intermittent hemodialysis (procedure)
        "233576000",  # Intermittent hemodialysis with sequential ultrafiltration (procedure)
        "233577009",  # Intermittent hemodialysis with continuous ultrafiltration (procedure)
        "233578004",  # Continuous hemodialysis (procedure)
        "233579007",  # Continuous arteriovenous hemodialysis (procedure)
        "233580005",  # Continuous venovenous hemodialysis (procedure)
        "233581009",  # Hemofiltration (procedure)
        "233582002",  # Intermittent hemofiltration (procedure)
        "233583007",  # Continuous hemofiltration (procedure)
        "233584001",  # Continuous arteriovenous hemofiltration (procedure)
        "233585000",  # Continuous venovenous hemofiltration (procedure)
        "233586004",  # Hemodiafiltration (procedure)
        "233587008",  # Intermittent hemodiafiltration (procedure)
        "233588003",  # Continuous hemodiafiltration (procedure)
        "233589006",  # Continuous arteriovenous hemodiafiltration (procedure)
        "233590002",  # Continuous venovenous hemodiafiltration (procedure)
        "238316008",  # Aspiration of chronic ambulatory peritoneal dialysis catheter (procedure)
        "238317004",  # Flushing of chronic ambulatory peritoneal dialysis catheter (procedure)
        "238318009",  # Continuous ambulatory peritoneal dialysis (procedure)
        "238319001",  # Continuous cycling peritoneal dialysis (procedure)
        "238321006",  # Intermittent peritoneal dialysis (procedure)
        "238322004",  # Tidal peritoneal dialysis (procedure)
        "238323009",  # Night-time intermittent peritoneal dialysis (procedure)
        "265764009",  # Renal dialysis (procedure)
        "288182009",  # Extracorporeal kidney (procedure)
        "302497006",  # Hemodialysis (procedure)
        "427053002",  # Extracorporeal albumin hemodialysis (procedure)
        "428648006",  # Automated peritoneal dialysis (procedure)
        "439278006",  # Measurement of static venous pressure in hemodialysis vascular access (procedure)
        "439976001",  # Measurement of recirculation in hemodialysis vascular access (procedure)
        "714749008",  # Continuous renal replacement therapy (procedure)
    }


class KidneyTransplant(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a kidney transplant.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent kidney transplants.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS165v10, CMS134v10
    """

    VALUE_SET_NAME = "Kidney Transplant"
    OID = "2.16.840.1.113883.3.464.1003.109.12.1012"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "50360",  # Renal allotransplantation, implantation of graft; without recipient nephrectomy
        "50365",  # Renal allotransplantation, implantation of graft; with recipient nephrectomy
        "50380",  # Renal autotransplantation, reimplantation of kidney
    }
    HCPCSLEVELII = {
        "S2065",  # Simultaneous pancreas kidney transplantation
    }
    ICD10PCS = {
        "0TY00Z0",  # Transplantation of Right Kidney, Allogeneic, Open Approach
        "0TY00Z1",  # Transplantation of Right Kidney, Syngeneic, Open Approach
        "0TY00Z2",  # Transplantation of Right Kidney, Zooplastic, Open Approach
        "0TY10Z0",  # Transplantation of Left Kidney, Allogeneic, Open Approach
        "0TY10Z1",  # Transplantation of Left Kidney, Syngeneic, Open Approach
        "0TY10Z2",  # Transplantation of Left Kidney, Zooplastic, Open Approach
    }
    SNOMEDCT = {
        "52213001",  # Renal homotransplantation excluding donor and recipient nephrectomy (procedure)
        "70536003",  # Transplant of kidney (procedure)
        "175899003",  # Autotransplantation of kidney (procedure)
        "175901007",  # Live donor renal transplant (procedure)
        "175902000",  # Cadaveric renal transplant (procedure)
        "236138007",  # Xenograft renal transplant (procedure)
        "313030004",  # Donor renal transplantation (procedure)
        "711411006",  # Allotransplantation of kidney from beating heart cadaver (procedure)
        "711413009",  # Allotransplantation of kidney from non-beating heart cadaver (procedure)
        "765478004",  # Allotransplantation of left kidney (procedure)
        "765479007",  # Allotransplantation of right kidney (procedure)
        "782655004",  # Laparoscopic transplant of kidney using robotic assistance (procedure)
        "6471000179103",  # Transplantation of kidney and pancreas (procedure)
    }


class CardiacSurgery(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of procedures for cardiac surgery.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a procedure for cardiac surgery.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS145v10
    """

    VALUE_SET_NAME = "Cardiac Surgery"
    OID = "2.16.840.1.113883.3.526.3.371"
    DEFINITION_VERSION = "20210218"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "33140",  # Transmyocardial laser revascularization, by thoracotomy; (separate procedure)
        "33510",  # Coronary artery bypass, vein only; single coronary venous graft
        "33511",  # Coronary artery bypass, vein only; 2 coronary venous grafts
        "33512",  # Coronary artery bypass, vein only; 3 coronary venous grafts
        "33513",  # Coronary artery bypass, vein only; 4 coronary venous grafts
        "33514",  # Coronary artery bypass, vein only; 5 coronary venous grafts
        "33516",  # Coronary artery bypass, vein only; 6 or more coronary venous grafts
        "33533",  # Coronary artery bypass, using arterial graft(s); single arterial graft
        "33534",  # Coronary artery bypass, using arterial graft(s); 2 coronary arterial grafts
        "33535",  # Coronary artery bypass, using arterial graft(s); 3 coronary arterial grafts
        "33536",  # Coronary artery bypass, using arterial graft(s); 4 or more coronary arterial grafts
        "92920",  # Percutaneous transluminal coronary angioplasty; single major coronary artery or branch
        "92924",  # Percutaneous transluminal coronary atherectomy, with coronary angioplasty when performed; single major coronary artery or branch
        "92928",  # Percutaneous transcatheter placement of intracoronary stent(s), with coronary angioplasty when performed; single major coronary artery or branch
        "92933",  # Percutaneous transluminal coronary atherectomy, with intracoronary stent, with coronary angioplasty when performed; single major coronary artery or branch
        "92937",  # Percutaneous transluminal revascularization of or through coronary artery bypass graft (internal mammary, free arterial, venous), any combination of intracoronary stent, atherectomy and angioplasty, including distal protection when performed; single vessel
        "92941",  # Percutaneous transluminal revascularization of acute total/subtotal occlusion during acute myocardial infarction, coronary artery or coronary artery bypass graft, any combination of intracoronary stent, atherectomy and angioplasty, including aspiration thrombectomy when performed, single vessel
        "92943",  # Percutaneous transluminal revascularization of chronic total occlusion, coronary artery, coronary artery branch, or coronary artery bypass graft, any combination of intracoronary stent, atherectomy and angioplasty; single vessel
        "92980",  # Transcatheter placement of an intracoronary stent(s), percutaneous, with or without other therapeutic intervention, any method; single vessel
        "92981",  # Transcatheter placement of an intracoronary stent(s), percutaneous, with or without other therapeutic intervention, any method; each additional vessel (List separately in addition to code for primary procedure)
        "92982",  # Percutaneous transluminal coronary balloon angioplasty; single vessel
        "92984",  # Percutaneous transluminal coronary balloon angioplasty; each additional vessel (List separately in addition to code for primary procedure)
        "92995",  # Percutaneous transluminal coronary atherectomy, by mechanical or other method, with or without balloon angioplasty; single vessel
        "92996",  # Percutaneous transluminal coronary atherectomy, by mechanical or other method, with or without balloon angioplasty; each additional vessel (List separately in addition to code for primary procedure)
    }
    SNOMEDCT = {
        "3546002",  # Aortocoronary artery bypass graft with saphenous vein graft (procedure)
        "10326007",  # Coronary artery bypass with autogenous graft, three grafts (procedure)
        "15256002",  # Transmyocardial revascularization by laser technique (procedure)
        "30670000",  # Anastomosis of thoracic artery to coronary artery, double (procedure)
        "39202005",  # Coronary artery bypass with autogenous graft, four grafts (procedure)
        "39724006",  # Anastomosis of internal mammary artery to coronary artery, double vessel (procedure)
        "48431000",  # Anastomosis of thoracic artery to coronary artery, single (procedure)
        "67166004",  # Aortocoronary artery bypass graft (procedure)
        "74371005",  # Coronary artery bypass with autogenous graft, two grafts (procedure)
        "81266008",  # Heart revascularization (procedure)
        "82247006",  # Coronary artery bypass with autogenous graft, five grafts (procedure)
        "90205004",  # Cardiac revascularization with bypass anastomosis (procedure)
        "119564002",  # Internal mammary-coronary artery bypass graft (procedure)
        "119565001",  # Coronary artery bypass graft, anastomosis of artery of thorax to coronary artery (procedure)
        "174911007",  # Revascularization of wall of heart (procedure)
        "175007008",  # Saphenous vein graft replacement of one coronary artery (procedure)
        "175008003",  # Saphenous vein graft replacement of two coronary arteries (procedure)
        "175009006",  # Saphenous vein graft replacement of three coronary arteries (procedure)
        "175011002",  # Saphenous vein graft replacement of four or more coronary arteries (procedure)
        "175021005",  # Allograft bypass of coronary artery (procedure)
        "175022003",  # Allograft replacement of one coronary artery (procedure)
        "175024002",  # Allograft replacement of two coronary arteries (procedure)
        "175025001",  # Allograft replacement of three coronary arteries (procedure)
        "175026000",  # Allograft replacement of four or more coronary arteries (procedure)
        "175036008",  # Revision of bypass for coronary artery (procedure)
        "175037004",  # Revision of bypass for one coronary artery (procedure)
        "175038009",  # Revision of bypass for two coronary arteries (procedure)
        "175039001",  # Revision of bypass for three coronary arteries (procedure)
        "175040004",  # Revision of bypass for four or more coronary arteries (procedure)
        "175041000",  # Revision of connection of thoracic artery to coronary artery (procedure)
        "175045009",  # Connection of mammary artery to coronary artery (procedure)
        "175047001",  # Double implantation of mammary arteries into coronary arteries (procedure)
        "175048006",  # Single anastomosis of mammary artery to left anterior descending coronary artery (procedure)
        "175050003",  # Single implantation of mammary artery into coronary artery (procedure)
        "232717009",  # Coronary artery bypass grafting (procedure)
        "232719007",  # Coronary artery bypass graft x 1 (procedure)
        "232720001",  # Coronary artery bypass grafts x 2 (procedure)
        "232721002",  # Coronary artery bypass grafts x 3 (procedure)
        "232722009",  # Coronary artery bypass grafts x 4 (procedure)
        "232723004",  # Coronary artery bypass grafts x 5 (procedure)
        "232724005",  # Coronary artery bypass grafts greater than 5 (procedure)
        "265481001",  # Double anastomosis of mammary arteries to coronary arteries (procedure)
        "275215001",  # Left internal mammary artery single anastomosis (procedure)
        "275216000",  # Right internal mammary artery single anastomosis (procedure)
        "275227003",  # Myocardial revascularization (procedure)
        "275252001",  # Left internal mammary artery sequential anastomosis (procedure)
        "275253006",  # Right internal mammary artery sequential anastomosis (procedure)
        "287277008",  # Indirect heart revascularization (procedure)
        "309814006",  # Aortocoronary bypass grafting (procedure)
        "359597003",  # Single internal mammary-coronary artery bypass (procedure)
        "359601003",  # Coronary artery bypass with autogenous graft of internal mammary artery, single graft (procedure)
        "414088005",  # Emergency coronary artery bypass graft (procedure)
        "418551006",  # Laparoscopic coronary artery bypass using robotic assistance (procedure)
        "418824004",  # Off-pump coronary artery bypass (procedure)
        "419132001",  # Minimally invasive direct coronary artery bypass (procedure)
        "736966005",  # Aortocoronary artery bypass of four or more coronary arteries with saphenous vein graft (procedure)
        "736967001",  # Aortocoronary artery bypass of one coronary artery with saphenous vein graft (procedure)
        "736968006",  # Aortocoronary artery bypass of three coronary arteries with saphenous vein graft (procedure)
        "736969003",  # Aortocoronary artery bypass of two coronary arteries with saphenous vein graft (procedure)
        "736970002",  # Allograft bypass of four or more coronary arteries (procedure)
        "736971003",  # Allograft bypass of one coronary artery (procedure)
        "736972005",  # Allograft bypass of three coronary arteries (procedure)
        "736973000",  # Allograft bypass of two coronary arteries (procedure)
        "871496000",  # Sequential anastomosis of left internal thoracic artery to coronary artery (procedure)
        "871497009",  # Sequential anastomosis of right internal thoracic artery to coronary artery (procedure)
    }


class Hemodialysis(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for hemodialysis.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent hemodialysis.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS147v11
    """

    VALUE_SET_NAME = "Hemodialysis"
    OID = "2.16.840.1.113883.3.526.3.1083"
    DEFINITION_VERSION = "20180331"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90951",  # End-stage renal disease (ESRD) related services monthly, for patients younger than 2 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents; with 4 or more face-to-face visits by a physician or other qualified health care professional per month
        "90952",  # End-stage renal disease (ESRD) related services monthly, for patients younger than 2 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents; with 2-3 face-to-face visits by a physician or other qualified health care professional per month
        "90953",  # End-stage renal disease (ESRD) related services monthly, for patients younger than 2 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents; with 1 face-to-face visit by a physician or other qualified health care professional per month
        "90954",  # End-stage renal disease (ESRD) related services monthly, for patients 2-11 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents; with 4 or more face-to-face visits by a physician or other qualified health care professional per month
        "90955",  # End-stage renal disease (ESRD) related services monthly, for patients 2-11 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents; with 2-3 face-to-face visits by a physician or other qualified health care professional per month
        "90956",  # End-stage renal disease (ESRD) related services monthly, for patients 2-11 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents; with 1 face-to-face visit by a physician or other qualified health care professional per month
        "90957",  # End-stage renal disease (ESRD) related services monthly, for patients 12-19 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents; with 4 or more face-to-face visits by a physician or other qualified health care professional per month
        "90958",  # End-stage renal disease (ESRD) related services monthly, for patients 12-19 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents; with 2-3 face-to-face visits by a physician or other qualified health care professional per month
        "90959",  # End-stage renal disease (ESRD) related services monthly, for patients 12-19 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents; with 1 face-to-face visit by a physician or other qualified health care professional per month
        "90960",  # End-stage renal disease (ESRD) related services monthly, for patients 20 years of age and older; with 4 or more face-to-face visits by a physician or other qualified health care professional per month
        "90961",  # End-stage renal disease (ESRD) related services monthly, for patients 20 years of age and older; with 2-3 face-to-face visits by a physician or other qualified health care professional per month
        "90962",  # End-stage renal disease (ESRD) related services monthly, for patients 20 years of age and older; with 1 face-to-face visit by a physician or other qualified health care professional per month
        "90963",  # End-stage renal disease (ESRD) related services for home dialysis per full month, for patients younger than 2 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents
        "90964",  # End-stage renal disease (ESRD) related services for home dialysis per full month, for patients 2-11 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents
        "90965",  # End-stage renal disease (ESRD) related services for home dialysis per full month, for patients 12-19 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents
        "90966",  # End-stage renal disease (ESRD) related services for home dialysis per full month, for patients 20 years of age and older
        "90967",  # End-stage renal disease (ESRD) related services for dialysis less than a full month of service, per day; for patients younger than 2 years of age
        "90968",  # End-stage renal disease (ESRD) related services for dialysis less than a full month of service, per day; for patients 2-11 years of age
        "90969",  # End-stage renal disease (ESRD) related services for dialysis less than a full month of service, per day; for patients 12-19 years of age
        "90970",  # End-stage renal disease (ESRD) related services for dialysis less than a full month of service, per day; for patients 20 years of age and older
        "99512",  # Home visit for hemodialysis
    }
    SNOMEDCT = {
        "302497006",  # Hemodialysis (procedure)
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


class PeritonealDialysis(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for peritoneal dialysis.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent peritoneal dialysis.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS147v11
    """

    VALUE_SET_NAME = "Peritoneal Dialysis"
    OID = "2.16.840.1.113883.3.526.3.1084"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90945",  # Dialysis procedure other than hemodialysis (eg, peritoneal dialysis, hemofiltration, or other continuous renal replacement therapies), with single evaluation by a physician or other qualified health care professional
        "90947",  # Dialysis procedure other than hemodialysis (eg, peritoneal dialysis, hemofiltration, or other continuous renal replacement therapies) requiring repeated evaluations by a physician or other qualified health care professional, with or without substantial revision of dialysis prescription
        "90951",  # End-stage renal disease (ESRD) related services monthly, for patients younger than 2 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents; with 4 or more face-to-face visits by a physician or other qualified health care professional per month
        "90952",  # End-stage renal disease (ESRD) related services monthly, for patients younger than 2 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents; with 2-3 face-to-face visits by a physician or other qualified health care professional per month
        "90953",  # End-stage renal disease (ESRD) related services monthly, for patients younger than 2 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents; with 1 face-to-face visit by a physician or other qualified health care professional per month
        "90954",  # End-stage renal disease (ESRD) related services monthly, for patients 2-11 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents; with 4 or more face-to-face visits by a physician or other qualified health care professional per month
        "90955",  # End-stage renal disease (ESRD) related services monthly, for patients 2-11 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents; with 2-3 face-to-face visits by a physician or other qualified health care professional per month
        "90956",  # End-stage renal disease (ESRD) related services monthly, for patients 2-11 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents; with 1 face-to-face visit by a physician or other qualified health care professional per month
        "90957",  # End-stage renal disease (ESRD) related services monthly, for patients 12-19 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents; with 4 or more face-to-face visits by a physician or other qualified health care professional per month
        "90958",  # End-stage renal disease (ESRD) related services monthly, for patients 12-19 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents; with 2-3 face-to-face visits by a physician or other qualified health care professional per month
        "90959",  # End-stage renal disease (ESRD) related services monthly, for patients 12-19 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents; with 1 face-to-face visit by a physician or other qualified health care professional per month
        "90960",  # End-stage renal disease (ESRD) related services monthly, for patients 20 years of age and older; with 4 or more face-to-face visits by a physician or other qualified health care professional per month
        "90961",  # End-stage renal disease (ESRD) related services monthly, for patients 20 years of age and older; with 2-3 face-to-face visits by a physician or other qualified health care professional per month
        "90962",  # End-stage renal disease (ESRD) related services monthly, for patients 20 years of age and older; with 1 face-to-face visit by a physician or other qualified health care professional per month
        "90963",  # End-stage renal disease (ESRD) related services for home dialysis per full month, for patients younger than 2 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents
        "90964",  # End-stage renal disease (ESRD) related services for home dialysis per full month, for patients 2-11 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents
        "90965",  # End-stage renal disease (ESRD) related services for home dialysis per full month, for patients 12-19 years of age to include monitoring for the adequacy of nutrition, assessment of growth and development, and counseling of parents
        "90966",  # End-stage renal disease (ESRD) related services for home dialysis per full month, for patients 20 years of age and older
        "90967",  # End-stage renal disease (ESRD) related services for dialysis less than a full month of service, per day; for patients younger than 2 years of age
        "90968",  # End-stage renal disease (ESRD) related services for dialysis less than a full month of service, per day; for patients 2-11 years of age
        "90969",  # End-stage renal disease (ESRD) related services for dialysis less than a full month of service, per day; for patients 12-19 years of age
        "90970",  # End-stage renal disease (ESRD) related services for dialysis less than a full month of service, per day; for patients 20 years of age and older
    }
    SNOMEDCT = {
        "676002",  # Peritoneal dialysis including cannulation (procedure)
        "14684005",  # Peritoneal dialysis excluding cannulation (procedure)
        "71192002",  # Peritoneal dialysis (procedure)
        "225230008",  # Chronic peritoneal dialysis (procedure)
        "238318009",  # Continuous ambulatory peritoneal dialysis (procedure)
        "238319001",  # Continuous cycling peritoneal dialysis (procedure)
        "238321006",  # Intermittent peritoneal dialysis (procedure)
        "238322004",  # Tidal peritoneal dialysis (procedure)
        "238323009",  # Night-time intermittent peritoneal dialysis (procedure)
        "428648006",  # Automated peritoneal dialysis (procedure)
    }


class ProceduresUsedToIndicateSexualActivity(ValueSet):
    """Procedures Used to Indicate Sexual Activity Value Set.

    **Clinical Focus:** The purpose of this value set is to represent procedures indicating history of sexual activity

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a procedure for pregnancy or postpartum or contraceptive use.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS153v10
    """

    VALUE_SET_NAME = "Procedures Used to Indicate Sexual Activity"
    OID = "2.16.840.1.113883.3.464.1003.111.12.1017"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "11976",  # Removal, implantable contraceptive capsules
        "57022",  # Incision and drainage of vaginal hematoma; obstetrical/postpartum
        "57170",  # Diaphragm or cervical cap fitting with instructions
        "58300",  # Insertion of intrauterine device (IUD)
        "58301",  # Removal of intrauterine device (IUD)
        "58600",  # Ligation or transection of fallopian tube(s), abdominal or vaginal approach, unilateral or bilateral
        "58605",  # Ligation or transection of fallopian tube(s), abdominal or vaginal approach, postpartum, unilateral or bilateral, during same hospitalization (separate procedure)
        "58615",  # Occlusion of fallopian tube(s) by device (eg, band, clip, Falope ring) vaginal or suprapubic approach
        "58970",  # Follicle puncture for oocyte retrieval, any method
        "58974",  # Embryo transfer, intrauterine
        "58976",  # Gamete, zygote, or embryo intrafallopian transfer, any method
        "59000",  # Amniocentesis; diagnostic
        "59001",  # Amniocentesis; therapeutic amniotic fluid reduction (includes ultrasound guidance)
        "59012",  # Cordocentesis (intrauterine), any method
        "59015",  # Chorionic villus sampling, any method
        "59020",  # Fetal contraction stress test
        "59025",  # Fetal non-stress test
        "59030",  # Fetal scalp blood sampling
        "59050",  # Fetal monitoring during labor by consulting physician (ie, non-attending physician) with written report; supervision and interpretation
        "59051",  # Fetal monitoring during labor by consulting physician (ie, non-attending physician) with written report; interpretation only
        "59070",  # Transabdominal amnioinfusion, including ultrasound guidance
        "59072",  # Fetal umbilical cord occlusion, including ultrasound guidance
        "59074",  # Fetal fluid drainage (eg, vesicocentesis, thoracocentesis, paracentesis), including ultrasound guidance
        "59076",  # Fetal shunt placement, including ultrasound guidance
        "59100",  # Hysterotomy, abdominal (eg, for hydatidiform mole, abortion)
        "59120",  # Surgical treatment of ectopic pregnancy; tubal or ovarian, requiring salpingectomy and/or oophorectomy, abdominal or vaginal approach
        "59121",  # Surgical treatment of ectopic pregnancy; tubal or ovarian, without salpingectomy and/or oophorectomy
        "59130",  # Surgical treatment of ectopic pregnancy; abdominal pregnancy
        "59135",  # Surgical treatment of ectopic pregnancy; interstitial, uterine pregnancy requiring total hysterectomy
        "59136",  # Surgical treatment of ectopic pregnancy; interstitial, uterine pregnancy with partial resection of uterus
        "59140",  # Surgical treatment of ectopic pregnancy; cervical, with evacuation
        "59150",  # Laparoscopic treatment of ectopic pregnancy; without salpingectomy and/or oophorectomy
        "59151",  # Laparoscopic treatment of ectopic pregnancy; with salpingectomy and/or oophorectomy
        "59160",  # Curettage, postpartum
        "59200",  # Insertion of cervical dilator (eg, laminaria, prostaglandin) (separate procedure)
        "59300",  # Episiotomy or vaginal repair, by other than attending
        "59320",  # Cerclage of cervix, during pregnancy; vaginal
        "59325",  # Cerclage of cervix, during pregnancy; abdominal
        "59350",  # Hysterorrhaphy of ruptured uterus
        "59400",  # Routine obstetric care including antepartum care, vaginal delivery (with or without episiotomy, and/or forceps) and postpartum care
        "59409",  # Vaginal delivery only (with or without episiotomy and/or forceps)
        "59410",  # Vaginal delivery only (with or without episiotomy and/or forceps); including postpartum care
        "59412",  # External cephalic version, with or without tocolysis
        "59414",  # Delivery of placenta (separate procedure)
        "59425",  # Antepartum care only; 4-6 visits
        "59426",  # Antepartum care only; 7 or more visits
        "59430",  # Postpartum care only (separate procedure)
        "59510",  # Routine obstetric care including antepartum care, cesarean delivery, and postpartum care
        "59514",  # Cesarean delivery only
        "59515",  # Cesarean delivery only; including postpartum care
        "59525",  # Subtotal or total hysterectomy after cesarean delivery (List separately in addition to code for primary procedure)
        "59610",  # Routine obstetric care including antepartum care, vaginal delivery (with or without episiotomy, and/or forceps) and postpartum care, after previous cesarean delivery
        "59612",  # Vaginal delivery only, after previous cesarean delivery (with or without episiotomy and/or forceps)
        "59614",  # Vaginal delivery only, after previous cesarean delivery (with or without episiotomy and/or forceps); including postpartum care
        "59618",  # Routine obstetric care including antepartum care, cesarean delivery, and postpartum care, following attempted vaginal delivery after previous cesarean delivery
        "59620",  # Cesarean delivery only, following attempted vaginal delivery after previous cesarean delivery
        "59622",  # Cesarean delivery only, following attempted vaginal delivery after previous cesarean delivery; including postpartum care
        "59812",  # Treatment of incomplete abortion, any trimester, completed surgically
        "59820",  # Treatment of missed abortion, completed surgically; first trimester
        "59821",  # Treatment of missed abortion, completed surgically; second trimester
        "59830",  # Treatment of septic abortion, completed surgically
        "59840",  # Induced abortion, by dilation and curettage
        "59841",  # Induced abortion, by dilation and evacuation
        "59850",  # Induced abortion, by 1 or more intra-amniotic injections (amniocentesis-injections), including hospital admission and visits, delivery of fetus and secundines
        "59851",  # Induced abortion, by 1 or more intra-amniotic injections (amniocentesis-injections), including hospital admission and visits, delivery of fetus and secundines; with dilation and curettage and/or evacuation
        "59852",  # Induced abortion, by 1 or more intra-amniotic injections (amniocentesis-injections), including hospital admission and visits, delivery of fetus and secundines; with hysterotomy (failed intra-amniotic injection)
        "59855",  # Induced abortion, by 1 or more vaginal suppositories (eg, prostaglandin) with or without cervical dilation (eg, laminaria), including hospital admission and visits, delivery of fetus and secundines
        "59856",  # Induced abortion, by 1 or more vaginal suppositories (eg, prostaglandin) with or without cervical dilation (eg, laminaria), including hospital admission and visits, delivery of fetus and secundines; with dilation and curettage and/or evacuation
        "59857",  # Induced abortion, by 1 or more vaginal suppositories (eg, prostaglandin) with or without cervical dilation (eg, laminaria), including hospital admission and visits, delivery of fetus and secundines; with hysterotomy (failed medical evacuation)
        "59866",  # Multifetal pregnancy reduction(s) (MPR)
        "59870",  # Uterine evacuation and curettage for hydatidiform mole
        "59871",  # Removal of cerclage suture under anesthesia (other than local)
        "59897",  # Unlisted fetal invasive procedure, including ultrasound guidance, when performed
        "59898",  # Unlisted laparoscopy procedure, maternity care and delivery
        "59899",  # Unlisted procedure, maternity care and delivery
    }
    HCPCSLEVELII = {
        "S0199",  # Medically induced abortion by oral ingestion of medication including all associated services and supplies (e.g., patient counseling, office visits, confirmation of pregnancy by hcg, ultrasound to confirm duration of pregnancy, ultrasound to confirm completion of abortion) except drugs
        "S4981",  # Insertion of levonorgestrel-releasing intrauterine system
        "S8055",  # Ultrasound guidance for multifetal pregnancy reduction(s), technical component (only to be used when the physician doing the reduction procedure does not perform the ultrasound, guidance is included in the cpt code for multifetal pregnancy reduction - 59866)
    }
    SNOMEDCT = {
        "4504004",  # Potter's obstetrical version with extraction (procedure)
        "5048009",  # External cephalic version with tocolysis (procedure)
        "5191001",  # Surgical treatment of missed abortion of second trimester (procedure)
        "5556001",  # Manually assisted spontaneous delivery (procedure)
        "6708002",  # Intrauterine cordocentesis (procedure)
        "9221009",  # Surgical treatment of septic abortion (procedure)
        "9724000",  # Repair of current obstetric laceration of uterus (procedure)
        "10455003",  # Removal of ectopic cervical pregnancy by evacuation (procedure)
        "10745001",  # Delivery of transverse presentation (procedure)
        "10763001",  # Therapeutic abortion by insertion of laminaria (procedure)
        "11466000",  # Cesarean section (procedure)
        "14119008",  # Braxton Hicks obstetrical version with extraction (procedure)
        "15413009",  # High forceps delivery with episiotomy (procedure)
        "16819009",  # Delivery of face presentation (procedure)
        "17744000",  # Subtotal hysterectomy after cesarean delivery (procedure)
        "17860005",  # Low forceps delivery with episiotomy (procedure)
        "18302006",  # Therapeutic abortion by hysterotomy (procedure)
        "18489003",  # Surgical treatment of missed abortion of first trimester (procedure)
        "18625004",  # Low forceps delivery (procedure)
        "19390001",  # Partial breech delivery with forceps to aftercoming head (procedure)
        "22633006",  # Vaginal delivery, medical personnel present (procedure)
        "24068006",  # Hysterectomy for removal of hydatidiform mole (procedure)
        "25296001",  # Delivery by Scanzoni maneuver (procedure)
        "25828002",  # Mid forceps delivery with episiotomy (procedure)
        "26313002",  # Delivery by vacuum extraction with episiotomy (procedure)
        "26578004",  # Hysterotomy with removal of hydatidiform mole (procedure)
        "28107008",  # Wright's obstetrical version (procedure)
        "28379004",  # Dilation and curettage of uterus after abortion (procedure)
        "28542003",  # Wigand-Martin maneuver (procedure)
        "28860009",  # Prague maneuver (procedure)
        "29613008",  # Delivery by double application of forceps (procedure)
        "30476003",  # Barton's forceps delivery (procedure)
        "33807004",  # Internal and combined version with extraction (procedure)
        "36708009",  # External fetal monitor surveillance (regime/therapy)
        "38479009",  # Frank breech delivery (procedure)
        "40219000",  # Delivery by Malstrom's extraction with episiotomy (procedure)
        "40704000",  # Wright's obstetrical version with extraction (procedure)
        "40792007",  # Kristeller maneuver (procedure)
        "41058005",  # Salpingectomy for tubal ectopic pregnancy by abdominal approach (procedure)
        "41059002",  # Cesarean hysterectomy (procedure)
        "41780001",  # External fetal monitor removal (regime/therapy)
        "43096003",  # Insertion of laminaria into vagina (procedure)
        "45460008",  # Intrauterine transfusion (procedure)
        "45718005",  # Vaginal delivery with forceps including postpartum care (procedure)
        "46681009",  # Cerclage of cervix during pregnancy by abdominal approach (procedure)
        "46706006",  # Replacement of contraceptive intrauterine device (procedure)
        "48204000",  # Spontaneous unassisted delivery, medical personnel present (procedure)
        "52660002",  # Induced abortion following intra-amniotic injection with hysterotomy (procedure)
        "54973000",  # Total breech delivery with forceps to aftercoming head (procedure)
        "56620000",  # Delivery of placenta following delivery of infant outside of hospital (procedure)
        "57271003",  # Extraperitoneal cesarean section (procedure)
        "58391006",  # Diaphragm fitting with education (procedure)
        "58705005",  # Bracht maneuver (procedure)
        "61586001",  # Delivery by vacuum extraction (procedure)
        "61893009",  # Laparoscopic treatment of ectopic pregnancy with oophorectomy (procedure)
        "62508004",  # Mid forceps delivery (procedure)
        "62688006",  # Surgical treatment of spontaneous abortion of any trimester (procedure)
        "63407004",  # Episioproctotomy (procedure)
        "63596003",  # Laparoscopic treatment of ectopic pregnancy with salpingectomy (procedure)
        "65200003",  # Insertion of intrauterine contraceptive device (procedure)
        "65243006",  # Delivery by midwife (procedure)
        "65378009",  # Delayed repair of episiotomy (procedure)
        "68254000",  # Removal of intrauterine device (procedure)
        "69422002",  # Trial forceps delivery (procedure)
        "69621003",  # Surgical treatment of missed abortion of third trimester (procedure)
        "71166009",  # Forceps delivery with rotation of fetal head (procedure)
        "72492007",  # Footling breech delivery (procedure)
        "73341009",  # Removal of ectopic fetus from ovary without oophorectomy (procedure)
        "75456002",  # Embryo transfer (procedure)
        "75928003",  # Pinard maneuver (procedure)
        "81130000",  # Removal of intraligamentous ectopic pregnancy (procedure)
        "81855008",  # Internal fetal monitoring during labor (regime/therapy)
        "82688001",  # Removal of ectopic fetus (procedure)
        "84195007",  # Classical cesarean section (procedure)
        "84275009",  # Obstetrical hysterotomy (procedure)
        "85179000",  # Insertion of laminaria into cervix (procedure)
        "85403009",  # Delivery, medical personnel present (procedure)
        "85548006",  # Episiotomy (procedure)
        "87431004",  # Dilation of cervical canal (procedure)
        "87663001",  # External fetal monitor surveillance during multiple pregnancy (regime/therapy)
        "88144003",  # Removal of ectopic interstitial uterine pregnancy requiring total hysterectomy (procedure)
        "88362001",  # Removal of ectopic fetus from fallopian tube without salpingectomy (procedure)
        "89053004",  # Vaginal cesarean section (procedure)
        "89346004",  # Delivery by Kielland rotation (procedure)
        "89849000",  # High forceps delivery (procedure)
        "90438006",  # Delivery by Malstrom's extraction (procedure)
        "90442009",  # Cerclage of cervix during pregnancy by vaginal approach (procedure)
        "133875007",  # Injection of prostaglandin (procedure)
        "169553002",  # Insertion of subcutaneous contraceptive (procedure)
        "176749004",  # Removal of intrauterine contraceptive device from pouch of Douglas (procedure)
        "176833006",  # Dilation of cervix uteri and curettage of uterus for removal of missed abortion (procedure)
        "176839005",  # Removal of displaced intrauterine contraceptive device (procedure)
        "176850008",  # Intra-amniotic prostaglandin instillation (procedure)
        "176852000",  # Extra-amniotic prostaglandin instillation (procedure)
        "176854004",  # Insertion of prostaglandin abortifacient suppository (procedure)
        "176928008",  # Excision of ectopic ovarian pregnancy (procedure)
        "176929000",  # Excision of ruptured ectopic tubal pregnancy (procedure)
        "176996001",  # Endoscopic intrafallopian transfer of gamete (procedure)
        "177037000",  # Oocyte recovery (procedure)
        "177038005",  # Endoscopic transurethral ultrasound directed oocyte recovery (procedure)
        "177039002",  # Endoscopic transvesical oocyte recovery (procedure)
        "177042008",  # Transvaginal oocyte recovery (procedure)
        "177091002",  # Fetoscopic sampling of fetal blood (procedure)
        "177100008",  # Percutaneous fetal procedure (procedure)
        "177101007",  # Percutaneous insertion of vesicoamniotic shunt (procedure)
        "177102000",  # Percutaneous insertion of pleuroamniotic shunt (procedure)
        "177106002",  # Percutaneous biopsy of fetus (procedure)
        "177107006",  # Percutaneous sampling of chorionic villus (procedure)
        "177112007",  # Therapeutic drainage of amniotic fluid (procedure)
        "177122001",  # External version of breech (procedure)
        "177136006",  # Prostaglandin induction of labor (procedure)
        "177141003",  # Elective cesarean section (procedure)
        "177142005",  # Elective upper segment cesarean section (procedure)
        "177143000",  # Elective lower segment cesarean section (procedure)
        "177152009",  # Breech extraction delivery with version (procedure)
        "177157003",  # Spontaneous breech delivery (procedure)
        "177158008",  # Assisted breech delivery (procedure)
        "177161009",  # Forceps cephalic delivery (procedure)
        "177162002",  # High forceps cephalic delivery with rotation (procedure)
        "177164001",  # Midforceps cephalic delivery with rotation (procedure)
        "177167008",  # Barton forceps cephalic delivery with rotation (procedure)
        "177168003",  # DeLee forceps cephalic delivery with rotation (procedure)
        "177170007",  # Piper forceps delivery (procedure)
        "177173009",  # High vacuum delivery (procedure)
        "177174003",  # Low vacuum delivery (procedure)
        "177175002",  # Vacuum delivery before full dilation of cervix (procedure)
        "177176001",  # Trial of vacuum delivery (procedure)
        "177179008",  # Cephalic vaginal delivery with abnormal presentation of head at delivery without instrument (procedure)
        "177180006",  # Manipulative cephalic vaginal delivery with abnormal presentation of head at delivery without instrument (procedure)
        "177181005",  # Non-manipulative cephalic vaginal delivery with abnormal presentation of head at delivery without instrument (procedure)
        "177184002",  # Normal delivery procedure (procedure)
        "177185001",  # Water birth delivery (procedure)
        "177212000",  # Normal delivery of placenta (procedure)
        "177222006",  # Repair of episiotomy (procedure)
        "215192006",  # Uterine evacuation and curettage of hydatidiform mole (procedure)
        "216209009",  # Removal of hydatidiform mole (procedure)
        "225251006",  # Fitting of cervical cap (procedure)
        "225256001",  # Removal of cervical cap (procedure)
        "225257005",  # Insertion of cervical cap (procedure)
        "233560009",  # Percutaneous intraperitoneal fetal blood transfusion (procedure)
        "233561008",  # Percutaneous intravascular fetal blood transfusion (procedure)
        "236892008",  # Removal of displaced intrauterine contraceptive device from peritoneal cavity (procedure)
        "236894009",  # Frozen embryo transfer (procedure)
        "236912008",  # Gamete intrafallopian transfer (procedure)
        "236913003",  # Fallopian replacement of egg with delayed insemination (procedure)
        "236914009",  # Zygote intrafallopian transfer (procedure)
        "236915005",  # Tubal embryo transfer (procedure)
        "236952005",  # Therapeutic drainage of amniotic fluid by single aspiration (procedure)
        "236953000",  # Therapeutic drainage of amniotic fluid by indwelling catheter (procedure)
        "236954006",  # Diagnostic amniocentesis with fluid replacement (procedure)
        "236955007",  # Hyperalimentation of fetus through amniotic cavity (procedure)
        "236956008",  # Amnioinfusion (procedure)
        "236966000",  # Cervical ripening with Prostaglandin E2 (procedure)
        "236974004",  # Instrumental delivery (procedure)
        "236975003",  # Nonrotational forceps delivery (procedure)
        "236976002",  # Outlet forceps delivery (procedure)
        "236977006",  # Forceps delivery, face to pubes (procedure)
        "236978001",  # Forceps delivery to the aftercoming head (procedure)
        "236980007",  # Groin traction at breech delivery (procedure)
        "236981006",  # Lovset's maneuver (procedure)
        "236982004",  # Delivery of the after coming head (procedure)
        "236983009",  # Burns Marshall maneuver (procedure)
        "236984003",  # Mauriceau Smellie Veit maneuver (procedure)
        "236985002",  # Emergency lower segment cesarean section (procedure)
        "236986001",  # Emergency upper segment cesarean section (procedure)
        "236987005",  # Emergency cesarean hysterectomy (procedure)
        "236988000",  # Elective cesarean hysterectomy (procedure)
        "236989008",  # Abdominal delivery for shoulder dystocia (procedure)
        "236990004",  # Postmortem cesarean section (procedure)
        "236992007",  # Right mediolateral episiotomy (procedure)
        "236993002",  # Vacuum dilatation of cervix (procedure)
        "236994008",  # Placental delivery procedure (procedure)
        "237017007",  # Intramyometrial injection of prostaglandin (procedure)
        "237025009",  # Repair of right mediolateral episiotomy (procedure)
        "237311001",  # Breech delivery (procedure)
        "240278000",  # External cephalic version (procedure)
        "240284002",  # Multifetal pregnancy reduction (procedure)
        "240285001",  # Percutaneous insertion of fetal shunt (procedure)
        "240286000",  # Percutaneous insertion of ventriculoamniotic shunt (procedure)
        "240288004",  # Percutaneous insertion of peritoneal-amniotic shunt (procedure)
        "240289007",  # Percutaneous aspiration of fetal lesion (procedure)
        "240290003",  # Percutaneous aspiration of fetal ascites (procedure)
        "240291004",  # Percutaneous aspiration of fetal pleural effusion (procedure)
        "240292006",  # Percutaneous aspiration of fetal pericardial effusion (procedure)
        "243773009",  # Fetal blood sampling (procedure)
        "243774003",  # Transvaginal fetal blood sampling (procedure)
        "259863001",  # Removal of Shirodkar suture from cervix (procedure)
        "265082003",  # Laparoscopic oocyte recovery (procedure)
        "265635006",  # Diagnostic amniocentesis (procedure)
        "265639000",  # Midforceps delivery without rotation (procedure)
        "265642006",  # Obstetric monitoring (regime/therapy)
        "274042004",  # Transvaginal removal of coil (procedure)
        "274130007",  # Emergency cesarean section (procedure)
        "274973002",  # Dilation of cervix uteri and curettage for termination of pregnancy (procedure)
        "275168001",  # Neville-Barnes forceps delivery (procedure)
        "275169009",  # Simpson's forceps delivery (procedure)
        "275222009",  # Transcervical sampling of chorionic villus (procedure)
        "275223004",  # Transabdominal chorionic villus biopsy (procedure)
        "275811000",  # Diaphragm fit (procedure)
        "281568006",  # Fetal heart monitoring (regime/therapy)
        "281570002",  # Fetal heart monitoring in labor (regime/therapy)
        "285409006",  # Medical termination of pregnancy (procedure)
        "285416007",  # Resuture of episiotomy (procedure)
        "285417003",  # Resuture of episiotomy dehiscence (procedure)
        "285434006",  # Insertion of abortifacient suppository (procedure)
        "287954004",  # Intrauterine exchange transfusion (procedure)
        "288042004",  # Hysterectomy and fetus removal (procedure)
        "288045002",  # Injection of amnion for termination of pregnancy (procedure)
        "288193006",  # Supervision - normal delivery (procedure)
        "288194000",  # Routine episiotomy and repair (procedure)
        "301806003",  # Insertion of subcutaneous contraceptive in arm (procedure)
        "301807007",  # Removal of subcutaneous contraceptive (procedure)
        "302375005",  # Operative termination of pregnancy (procedure)
        "302382009",  # Breech extraction with internal podalic version (procedure)
        "302383004",  # Forceps delivery (procedure)
        "302384005",  # Controlled cord traction of placenta (procedure)
        "303720006",  # Sampling of chorionic villus (procedure)
        "306727001",  # Breech presentation, delivery, no version (procedure)
        "309877008",  # Intrapartum cardiotochogram monitoring (regime/therapy)
        "315308008",  # Dilatation of cervix for delivery (procedure)
        "359940006",  # Partial breech extraction (procedure)
        "359943008",  # Partial breech delivery (procedure)
        "384729004",  # Delivery of vertex presentation (procedure)
        "384730009",  # Delivery of cephalic presentation (procedure)
        "386276009",  # Electronic fetal monitoring: antepartum (regime/therapy)
        "386277000",  # Electronic fetal monitoring: intrapartum (regime/therapy)
        "386639001",  # Termination of pregnancy (procedure)
        "386641000",  # Therapeutic abortion procedure (procedure)
        "387615001",  # Removal of ectopic pregnancy from fallopian tube (procedure)
        "387616000",  # Fimbrial extraction of tubal pregnancy (procedure)
        "387673001",  # Nonstress test (regime/therapy)
        "387678005",  # External obstetrical version (procedure)
        "387709005",  # Removal of ectopic fetus from abdominal cavity (procedure)
        "387710000",  # Removal of extrauterine ectopic fetus (procedure)
        "391896006",  # Therapeutic abortion by aspiration curettage (procedure)
        "391897002",  # Aspiration curettage of uterus for termination of pregnancy (procedure)
        "391998006",  # Dilation and curettage of uterus after delivery (procedure)
        "392000009",  # Hysterotomy for retained placenta (procedure)
        "398221005",  # Fetal pH monitoring (regime/therapy)
        "408804006",  # Continuous fetal heart monitoring during labor (regime/therapy)
        "408805007",  # Intermittent fetal heart monitoring during labor (regime/therapy)
        "408806008",  # Fetal heart monitoring using hand held doppler (regime/therapy)
        "408807004",  # Fetal heart monitoring using fetal scalp electrode (regime/therapy)
        "408808009",  # Fetal heart monitoring using ultrasound transducer (regime/therapy)
        "408819007",  # Delivery of placenta by maternal effort (procedure)
        "408840008",  # Extra-amniotic termination of pregnancy (procedure)
        "408845003",  # Fetal heart monitoring with Pinard stethoscope (regime/therapy)
        "416055001",  # Total breech extraction (procedure)
        "417121007",  # Breech extraction (procedure)
        "425707001",  # Serial drainage of amniotic fluid (procedure)
        "425939004",  # Endoscopic serial drainage of amniotic fluid (procedure)
        "426287008",  # Amniocentesis for possible neural tube defect (procedure)
        "426737000",  # Endoscopic serial drainage of amniotic fluid for twin-twin transfusion syndrome (procedure)
        "427230007",  # Amniocentesis for possible chromosomal abnormality (procedure)
        "427320001",  # Serial drainage of amniotic fluid for twin-twin transfusion syndrome (procedure)
        "429613009",  # Percutaneous insertion of tracheal plug for congenital diaphragmatic hernia of fetus (procedure)
        "429737004",  # Percutaneous laser ablation of lesion of fetus (procedure)
        "433153009",  # Chorionic villus sampling using obstetric ultrasound guidance (procedure)
        "440148001",  # Partial excision of uterus for removal of interstitial ectopic pregnancy (procedure)
        "440668008",  # Replacement of implantable contraceptive capsule (procedure)
        "442490009",  # Removal of etonogestrel implant (procedure)
        "443005005",  # Diagnostic amniocentesis using ultrasound guidance (procedure)
        "445865006",  # Sampling of fetal blood using ultrasound guidance (procedure)
        "445912000",  # Excision of fallopian tube and surgical removal of ectopic pregnancy (procedure)
        "446135006",  # Amnioinfusion using ultrasound guidance (procedure)
        "446341008",  # Sampling of fetal blood and biopsy of fetus (procedure)
        "446934006",  # Retrieval of oocyte by transabdominal approach (procedure)
        "447214008",  # Ligation of umbilical cord of fetus (procedure)
        "447771005",  # Abdominal hysterectomy and excision of periuterine tissue (procedure)
        "447972007",  # Medical termination of pregnancy using prostaglandin (procedure)
        "448543003",  # Transmyometrial transfer of embryo to uterus (procedure)
        "450483001",  # Cesarean section through inverted T shaped incision of uterus (procedure)
        "450484007",  # Cesarean section through J shaped incision of uterus (procedure)
        "450563004",  # Laparoscopic excision of ectopic ovarian pregnancy (procedure)
        "450798003",  # Delivery of occipitoposterior presentation (procedure)
        "450836008",  # Removal of etonogestrel radiopaque contraceptive implant (procedure)
        "472837007",  # Insertion of hormone releasing intrauterine contraceptive device (procedure)
        "472838002",  # Removal of hormone releasing intrauterine contraceptive device (procedure)
        "699999008",  # Obstetrical version with extraction (procedure)
        "700000006",  # Vaginal delivery of fetus (procedure)
        "700041001",  # Induced termination of pregnancy under unsafe conditions (procedure)
        "709004006",  # Emergency lower segment cesarean section with inverted T incision (procedure)
        "713117007",  # Monitoring fetal development (regime/therapy)
        "713120004",  # Counting fetal movement (regime/therapy)
        "714812005",  # Induced termination of pregnancy (procedure)
        "716100006",  # Doppler ultrasonography of vascular structure of fetal head (procedure)
        "725927001",  # Pronuclear transfer mitochondrial replacement therapy (procedure)
        "726556001",  # Maternal spindle transfer mitochondrial replacement therapy (procedure)
        "732970000",  # Controlled ovarian stimulation (procedure)
        "734275002",  # Delivery by outlet vacuum extraction (procedure)
        "734276001",  # Delivery by mid-vacuum extraction (procedure)
        "736018001",  # Elective upper segment cesarean section with bilateral tubal ligation (procedure)
        "736020003",  # Emergency upper segment cesarean section with bilateral tubal ligation (procedure)
        "736026009",  # Elective lower segment cesarean section with bilateral tubal ligation (procedure)
        "736118004",  # Emergency lower segment cesarean section with bilateral tubal ligation (procedure)
        "737099004",  # Abdominal hysterectomy with sacrocolpopexy using mesh (procedure)
        "480571000119102",  # Doppler ultrasound velocimetry of umbilical artery of fetus (procedure)
    }


class ChemotherapyAdministration(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for the procedure of chemotherapy administration.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a procedure for chemotherapy administration.

    **Exclusion Criteria:** Excludes concepts that describe a procedure for topical chemotherapy.

    ** Used in:** CMS157v10
    """

    VALUE_SET_NAME = "Chemotherapy Administration"
    OID = "2.16.840.1.113883.3.526.3.1027"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "51720",  # Bladder instillation of anticarcinogenic agent (including retention time)
        "96401",  # Chemotherapy administration, subcutaneous or intramuscular; non-hormonal anti-neoplastic
        "96405",  # Chemotherapy administration; intralesional, up to and including 7 lesions
        "96406",  # Chemotherapy administration; intralesional, more than 7 lesions
        "96409",  # Chemotherapy administration; intravenous, push technique, single or initial substance/drug
        "96413",  # Chemotherapy administration, intravenous infusion technique; up to 1 hour, single or initial substance/drug
        "96416",  # Chemotherapy administration, intravenous infusion technique; initiation of prolonged chemotherapy infusion (more than 8 hours), requiring use of a portable or implantable pump
        "96420",  # Chemotherapy administration, intra-arterial; push technique
        "96422",  # Chemotherapy administration, intra-arterial; infusion technique, up to 1 hour
        "96425",  # Chemotherapy administration, intra-arterial; infusion technique, initiation of prolonged infusion (more than 8 hours), requiring the use of a portable or implantable pump
        "96440",  # Chemotherapy administration into pleural cavity, requiring and including thoracentesis
        "96446",  # Chemotherapy administration into the peritoneal cavity via indwelling port or catheter
        "96450",  # Chemotherapy administration, into CNS (eg, intrathecal), requiring and including spinal puncture
        "96521",  # Refilling and maintenance of portable pump
        "96522",  # Refilling and maintenance of implantable pump or reservoir for drug delivery, systemic (eg, intravenous, intra-arterial)
        "96523",  # Irrigation of implanted venous access device for drug delivery systems
        "96542",  # Chemotherapy injection, subarachnoid or intraventricular via subcutaneous reservoir, single or multiple agents
        "96549",  # Unlisted chemotherapy procedure
    }
    SNOMEDCT = {
        "4114003",  # Parenteral chemotherapy for malignant neoplasm (procedure)
        "6872008",  # Perfusion chemotherapy for malignant neoplasm (procedure)
        "31652009",  # Intracavitary chemotherapy for malignant neoplasm (procedure)
        "38216008",  # Infusion chemotherapy for malignant neoplasm (procedure)
        "51534007",  # Oral chemotherapy for malignant neoplasm (procedure)
        "77738002",  # Local chemotherapy for malignant neoplasm (procedure)
        "169396008",  # Radiomimetic chemotherapy (procedure)
        "265760000",  # Intravenous chemotherapy (procedure)
        "265761001",  # Intramuscular chemotherapy (procedure)
        "265762008",  # Subcutaneous chemotherapy (procedure)
        "266719004",  # Oral chemotherapy (procedure)
        "268500004",  # Prophylactic chemotherapy (procedure)
        "315601005",  # Ambulatory chemotherapy (procedure)
        "367336001",  # Chemotherapy (procedure)
        "394894008",  # Pre-operative chemotherapy (procedure)
        "394895009",  # Postoperative chemotherapy (procedure)
        "394935005",  # Combined post-operative chemotherapy and radiotherapy (procedure)
        "716872004",  # Antineoplastic chemotherapy regimen (regime/therapy)
    }


class RadiationTreatmentManagement(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for the procedure of radiation management.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a procedure for radiation treatment management.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS157v10
    """

    VALUE_SET_NAME = "Radiation Treatment Management"
    OID = "2.16.840.1.113883.3.526.3.1026"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "77427",  # Radiation treatment management, 5 treatments
        "77431",  # Radiation therapy management with complete course of therapy consisting of 1 or 2 fractions only
        "77432",  # Stereotactic radiation treatment management of cranial lesion(s) (complete course of treatment consisting of 1 session)
        "77435",  # Stereotactic body radiation therapy, treatment management, per treatment course, to 1 or more lesions, including image guidance, entire course not to exceed 5 fractions
    }
    SNOMEDCT = {
        "84755001",  # Radiation therapy treatment management (procedure)
    }


class GastricBypassSurgery(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for gastric bypass surgery.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a gastric bypass surgery.

    **Exclusion Criteria:** Excludes concepts that represent endoscopic excision of stomach tissue, excision/laparoscopic wedge resection of lesion of the stomach and incisional biopsy of the stomach.

    ** Used in:** CMS249v4
    """

    VALUE_SET_NAME = "Gastric Bypass Surgery"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1050"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "43117",  # Partial esophagectomy, distal two-thirds, with thoracotomy and separate abdominal incision, with or without proximal gastrectomy; with thoracic esophagogastrostomy, with or without pyloroplasty (Ivor Lewis)
        "43118",  # Partial esophagectomy, distal two-thirds, with thoracotomy and separate abdominal incision, with or without proximal gastrectomy; with colon interposition or small intestine reconstruction, including intestine mobilization, preparation, and anastomosis(es)
        "43121",  # Partial esophagectomy, distal two-thirds, with thoracotomy only, with or without proximal gastrectomy, with thoracic esophagogastrostomy, with or without pyloroplasty
        "43122",  # Partial esophagectomy, thoracoabdominal or abdominal approach, with or without proximal gastrectomy; with esophagogastrostomy, with or without pyloroplasty
        "43123",  # Partial esophagectomy, thoracoabdominal or abdominal approach, with or without proximal gastrectomy; with colon interposition or small intestine reconstruction, including intestine mobilization, preparation, and anastomosis(es)
        "43620",  # Gastrectomy, total; with esophagoenterostomy
        "43621",  # Gastrectomy, total; with Roux-en-Y reconstruction
        "43622",  # Gastrectomy, total; with formation of intestinal pouch, any type
        "43631",  # Gastrectomy, partial, distal; with gastroduodenostomy
        "43632",  # Gastrectomy, partial, distal; with gastrojejunostomy
        "43633",  # Gastrectomy, partial, distal; with Roux-en-Y reconstruction
        "43634",  # Gastrectomy, partial, distal; with formation of intestinal pouch
        "43775",  # Laparoscopy, surgical, gastric restrictive procedure; longitudinal gastrectomy (ie, sleeve gastrectomy)
        "43845",  # Gastric restrictive procedure with partial gastrectomy, pylorus-preserving duodenoileostomy and ileoileostomy (50 to 100 cm common channel) to limit absorption (biliopancreatic diversion with duodenal switch)
        "48150",  # Pancreatectomy, proximal subtotal with total duodenectomy, partial gastrectomy, choledochoenterostomy and gastrojejunostomy (Whipple-type procedure); with pancreatojejunostomy
        "48152",  # Pancreatectomy, proximal subtotal with total duodenectomy, partial gastrectomy, choledochoenterostomy and gastrojejunostomy (Whipple-type procedure); without pancreatojejunostomy
    }
    SNOMEDCT = {
        "9102008",  # Proximal subtotal gastrectomy by thoracic approach (procedure)
        "10002003",  # Resection of stomach fundus (procedure)
        "10869008",  # Hemigastrectomy with vagotomy (procedure)
        "21538007",  # Distal subtotal gastrectomy with vagotomy (procedure)
        "24431004",  # Esophagoduodenostomy with complete gastrectomy (procedure)
        "24506003",  # Esophagogastrectomy (procedure)
        "24883002",  # Biliopancreatic bypass to ileum with partial gastrectomy (procedure)
        "26452005",  # Total gastrectomy (procedure)
        "26565004",  # Polya operation, gastrectomy (procedure)
        "40234006",  # Hemigastrectomy (procedure)
        "43344006",  # Hofmeister operation, gastrectomy (procedure)
        "46936007",  # Hemigastrectomy by thoracic approach (procedure)
        "49209004",  # Subtotal gastrectomy (procedure)
        "53442002",  # Excision of stomach structure (procedure)
        "68342003",  # Ramstedt operation, pyloromyotomy with wedge resection (procedure)
        "83371007",  # Proximal subtotal gastrectomy by abdominal approach (procedure)
        "83857006",  # Gastroduodenectomy (procedure)
        "83985009",  # Resection of stomach with gastrojejunal anastomosis (procedure)
        "85217002",  # Distal subtotal gastrectomy (procedure)
        "87604009",  # Sleeve resection of stomach (procedure)
        "90063003",  # Pyloric antrectomy (procedure)
        "90410003",  # Wedge resection of stomach (procedure)
        "91621005",  # Total gastrectomy with intestinal interposition (procedure)
        "112860004",  # Hemigastrectomy by abdominal approach (procedure)
        "116175006",  # Proximal subtotal gastrectomy (procedure)
        "173560002",  # Esophagogastrectomy and anastomosis of esophagus to transposed jejunum (procedure)
        "173714001",  # Total gastrectomy and excision of surrounding tissue (procedure)
        "173715000",  # Total gastrectomy and interposition of jejunum (procedure)
        "173716004",  # Total gastrectomy and anastomosis of esophagus to transposed jejunum (procedure)
        "173720000",  # Partial gastrectomy and anastomosis of stomach to transposed jejunum (procedure)
        "173722008",  # Maki's pylorus-preserving gastrectomy (procedure)
        "173794002",  # Pyloromyotomy and wedge resection (procedure)
        "235165007",  # Partial esophagectomy and total gastrectomy (procedure)
        "235214008",  # Billroth I partial gastrectomy - Horsley modification (procedure)
        "235215009",  # Billroth I partial gastrectomy - von Haberer-Finney modification (procedure)
        "235216005",  # Billroth I partial gastrectomy - von Haberer modification (procedure)
        "235217001",  # Billroth I partial gastrectomy - Schoemaker modification (procedure)
        "235218006",  # Billroth II partial gastrectomy - Moynihan modification (procedure)
        "235219003",  # Billroth II partial gastrectomy - Balfour modification (procedure)
        "265340005",  # Partial esophagectomy and proximal gastrectomy (procedure)
        "265459006",  # Pancreaticoduodenectomy with distal gastrectomy (procedure)
        "275007007",  # Ivor Lewis partial esophagogastrectomy (procedure)
        "275162000",  # Hofmeister valved gastrectomy (procedure)
        "275194005",  # Bancroft partial gastrectomy and esophagogastrostomy (procedure)
        "287809004",  # Total gastroduodenectomy (procedure)
        "287816003",  # Radical gastrectomy (procedure)
        "287818002",  # Partial gastroduodenectomy (procedure)
        "287819005",  # Pylorectomy (procedure)
        "287821000",  # Cardiectomy (procedure)
        "307303006",  # Billroth I gastric antrectomy (procedure)
        "307304000",  # Polya gastric antrectomy (procedure)
        "359575000",  # Gastrectomy with jejunal transposition (procedure)
        "359579006",  # Partial gastrectomy with jejunal transposition (procedure)
        "427074001",  # Laparoscopic sleeve gastrectomy (procedure)
        "427980007",  # Sleeve gastrectomy with duodenal switch (procedure)
        "430715008",  # Bariatric operative procedure (procedure)
        "438338008",  # Total gastrectomy with extended lymphadenectomy (procedure)
        "439878001",  # Completion gastrectomy (procedure)
        "445831005",  # Partial excision of stomach and jejunal transposition and excision of intestine (procedure)
        "445983004",  # Endoscopic excision of mucosa of stomach (procedure)
        "446650001",  # Excision of mucosa of stomach (procedure)
    }


class CabgSurgeries(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of coronary artery bypass graft (CABG) procedures.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a procedure for coronary artery bypass graft (CABG) surgery.

    **Exclusion Criteria:** Excludes concepts that represent a  coronary artery bypass graft (CABG) performed using a scope.

    ** Used in:** CMS347v5
    """

    VALUE_SET_NAME = "CABG Surgeries"
    OID = "2.16.840.1.113883.3.666.5.694"
    DEFINITION_VERSION = "20160331"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    ICD10PCS = {
        "0210083",  # Bypass Coronary Artery, One Artery from Coronary Artery with Zooplastic Tissue, Open Approach
        "0210088",  # Bypass Coronary Artery, One Artery from Right Internal Mammary with Zooplastic Tissue, Open Approach
        "0210089",  # Bypass Coronary Artery, One Artery from Left Internal Mammary with Zooplastic Tissue, Open Approach
        "021008C",  # Bypass Coronary Artery, One Artery from Thoracic Artery with Zooplastic Tissue, Open Approach
        "021008F",  # Bypass Coronary Artery, One Artery from Abdominal Artery with Zooplastic Tissue, Open Approach
        "021008W",  # Bypass Coronary Artery, One Artery from Aorta with Zooplastic Tissue, Open Approach
        "0210093",  # Bypass Coronary Artery, One Artery from Coronary Artery with Autologous Venous Tissue, Open Approach
        "0210098",  # Bypass Coronary Artery, One Artery from Right Internal Mammary with Autologous Venous Tissue, Open Approach
        "0210099",  # Bypass Coronary Artery, One Artery from Left Internal Mammary with Autologous Venous Tissue, Open Approach
        "021009C",  # Bypass Coronary Artery, One Artery from Thoracic Artery with Autologous Venous Tissue, Open Approach
        "021009F",  # Bypass Coronary Artery, One Artery from Abdominal Artery with Autologous Venous Tissue, Open Approach
        "021009W",  # Bypass Coronary Artery, One Artery from Aorta with Autologous Venous Tissue, Open Approach
        "02100A3",  # Bypass Coronary Artery, One Artery from Coronary Artery with Autologous Arterial Tissue, Open Approach
        "02100A8",  # Bypass Coronary Artery, One Artery from Right Internal Mammary with Autologous Arterial Tissue, Open Approach
        "02100A9",  # Bypass Coronary Artery, One Artery from Left Internal Mammary with Autologous Arterial Tissue, Open Approach
        "02100AC",  # Bypass Coronary Artery, One Artery from Thoracic Artery with Autologous Arterial Tissue, Open Approach
        "02100AF",  # Bypass Coronary Artery, One Artery from Abdominal Artery with Autologous Arterial Tissue, Open Approach
        "02100AW",  # Bypass Coronary Artery, One Artery from Aorta with Autologous Arterial Tissue, Open Approach
        "02100J3",  # Bypass Coronary Artery, One Artery from Coronary Artery with Synthetic Substitute, Open Approach
        "02100J8",  # Bypass Coronary Artery, One Artery from Right Internal Mammary with Synthetic Substitute, Open Approach
        "02100J9",  # Bypass Coronary Artery, One Artery from Left Internal Mammary with Synthetic Substitute, Open Approach
        "02100JC",  # Bypass Coronary Artery, One Artery from Thoracic Artery with Synthetic Substitute, Open Approach
        "02100JF",  # Bypass Coronary Artery, One Artery from Abdominal Artery with Synthetic Substitute, Open Approach
        "02100JW",  # Bypass Coronary Artery, One Artery from Aorta with Synthetic Substitute, Open Approach
        "02100K3",  # Bypass Coronary Artery, One Artery from Coronary Artery with Nonautologous Tissue Substitute, Open Approach
        "02100K8",  # Bypass Coronary Artery, One Artery from Right Internal Mammary with Nonautologous Tissue Substitute, Open Approach
        "02100K9",  # Bypass Coronary Artery, One Artery from Left Internal Mammary with Nonautologous Tissue Substitute, Open Approach
        "02100KC",  # Bypass Coronary Artery, One Artery from Thoracic Artery with Nonautologous Tissue Substitute, Open Approach
        "02100KF",  # Bypass Coronary Artery, One Artery from Abdominal Artery with Nonautologous Tissue Substitute, Open Approach
        "02100KW",  # Bypass Coronary Artery, One Artery from Aorta with Nonautologous Tissue Substitute, Open Approach
        "02100Z3",  # Bypass Coronary Artery, One Artery from Coronary Artery, Open Approach
        "02100Z8",  # Bypass Coronary Artery, One Artery from Right Internal Mammary, Open Approach
        "02100Z9",  # Bypass Coronary Artery, One Artery from Left Internal Mammary, Open Approach
        "02100ZC",  # Bypass Coronary Artery, One Artery from Thoracic Artery, Open Approach
        "02100ZF",  # Bypass Coronary Artery, One Artery from Abdominal Artery, Open Approach
        "0210483",  # Bypass Coronary Artery, One Artery from Coronary Artery with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "0210488",  # Bypass Coronary Artery, One Artery from Right Internal Mammary with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "0210489",  # Bypass Coronary Artery, One Artery from Left Internal Mammary with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "021048C",  # Bypass Coronary Artery, One Artery from Thoracic Artery with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "021048F",  # Bypass Coronary Artery, One Artery from Abdominal Artery with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "021048W",  # Bypass Coronary Artery, One Artery from Aorta with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "0210493",  # Bypass Coronary Artery, One Artery from Coronary Artery with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "0210498",  # Bypass Coronary Artery, One Artery from Right Internal Mammary with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "0210499",  # Bypass Coronary Artery, One Artery from Left Internal Mammary with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "021049C",  # Bypass Coronary Artery, One Artery from Thoracic Artery with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "021049F",  # Bypass Coronary Artery, One Artery from Abdominal Artery with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "021049W",  # Bypass Coronary Artery, One Artery from Aorta with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "02104A3",  # Bypass Coronary Artery, One Artery from Coronary Artery with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02104A8",  # Bypass Coronary Artery, One Artery from Right Internal Mammary with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02104A9",  # Bypass Coronary Artery, One Artery from Left Internal Mammary with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02104AC",  # Bypass Coronary Artery, One Artery from Thoracic Artery with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02104AF",  # Bypass Coronary Artery, One Artery from Abdominal Artery with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02104AW",  # Bypass Coronary Artery, One Artery from Aorta with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02104J3",  # Bypass Coronary Artery, One Artery from Coronary Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02104J8",  # Bypass Coronary Artery, One Artery from Right Internal Mammary with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02104J9",  # Bypass Coronary Artery, One Artery from Left Internal Mammary with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02104JC",  # Bypass Coronary Artery, One Artery from Thoracic Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02104JF",  # Bypass Coronary Artery, One Artery from Abdominal Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02104JW",  # Bypass Coronary Artery, One Artery from Aorta with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02104K3",  # Bypass Coronary Artery, One Artery from Coronary Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02104K8",  # Bypass Coronary Artery, One Artery from Right Internal Mammary with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02104K9",  # Bypass Coronary Artery, One Artery from Left Internal Mammary with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02104KC",  # Bypass Coronary Artery, One Artery from Thoracic Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02104KF",  # Bypass Coronary Artery, One Artery from Abdominal Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02104KW",  # Bypass Coronary Artery, One Artery from Aorta with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02104Z3",  # Bypass Coronary Artery, One Artery from Coronary Artery, Percutaneous Endoscopic Approach
        "02104Z8",  # Bypass Coronary Artery, One Artery from Right Internal Mammary, Percutaneous Endoscopic Approach
        "02104Z9",  # Bypass Coronary Artery, One Artery from Left Internal Mammary, Percutaneous Endoscopic Approach
        "02104ZC",  # Bypass Coronary Artery, One Artery from Thoracic Artery, Percutaneous Endoscopic Approach
        "02104ZF",  # Bypass Coronary Artery, One Artery from Abdominal Artery, Percutaneous Endoscopic Approach
        "0211083",  # Bypass Coronary Artery, Two Arteries from Coronary Artery with Zooplastic Tissue, Open Approach
        "0211088",  # Bypass Coronary Artery, Two Arteries from Right Internal Mammary with Zooplastic Tissue, Open Approach
        "0211089",  # Bypass Coronary Artery, Two Arteries from Left Internal Mammary with Zooplastic Tissue, Open Approach
        "021108C",  # Bypass Coronary Artery, Two Arteries from Thoracic Artery with Zooplastic Tissue, Open Approach
        "021108F",  # Bypass Coronary Artery, Two Arteries from Abdominal Artery with Zooplastic Tissue, Open Approach
        "021108W",  # Bypass Coronary Artery, Two Arteries from Aorta with Zooplastic Tissue, Open Approach
        "0211093",  # Bypass Coronary Artery, Two Arteries from Coronary Artery with Autologous Venous Tissue, Open Approach
        "0211098",  # Bypass Coronary Artery, Two Arteries from Right Internal Mammary with Autologous Venous Tissue, Open Approach
        "0211099",  # Bypass Coronary Artery, Two Arteries from Left Internal Mammary with Autologous Venous Tissue, Open Approach
        "021109C",  # Bypass Coronary Artery, Two Arteries from Thoracic Artery with Autologous Venous Tissue, Open Approach
        "021109F",  # Bypass Coronary Artery, Two Arteries from Abdominal Artery with Autologous Venous Tissue, Open Approach
        "021109W",  # Bypass Coronary Artery, Two Arteries from Aorta with Autologous Venous Tissue, Open Approach
        "02110A3",  # Bypass Coronary Artery, Two Arteries from Coronary Artery with Autologous Arterial Tissue, Open Approach
        "02110A8",  # Bypass Coronary Artery, Two Arteries from Right Internal Mammary with Autologous Arterial Tissue, Open Approach
        "02110A9",  # Bypass Coronary Artery, Two Arteries from Left Internal Mammary with Autologous Arterial Tissue, Open Approach
        "02110AC",  # Bypass Coronary Artery, Two Arteries from Thoracic Artery with Autologous Arterial Tissue, Open Approach
        "02110AF",  # Bypass Coronary Artery, Two Arteries from Abdominal Artery with Autologous Arterial Tissue, Open Approach
        "02110AW",  # Bypass Coronary Artery, Two Arteries from Aorta with Autologous Arterial Tissue, Open Approach
        "02110J3",  # Bypass Coronary Artery, Two Arteries from Coronary Artery with Synthetic Substitute, Open Approach
        "02110J8",  # Bypass Coronary Artery, Two Arteries from Right Internal Mammary with Synthetic Substitute, Open Approach
        "02110J9",  # Bypass Coronary Artery, Two Arteries from Left Internal Mammary with Synthetic Substitute, Open Approach
        "02110JC",  # Bypass Coronary Artery, Two Arteries from Thoracic Artery with Synthetic Substitute, Open Approach
        "02110JF",  # Bypass Coronary Artery, Two Arteries from Abdominal Artery with Synthetic Substitute, Open Approach
        "02110JW",  # Bypass Coronary Artery, Two Arteries from Aorta with Synthetic Substitute, Open Approach
        "02110K3",  # Bypass Coronary Artery, Two Arteries from Coronary Artery with Nonautologous Tissue Substitute, Open Approach
        "02110K8",  # Bypass Coronary Artery, Two Arteries from Right Internal Mammary with Nonautologous Tissue Substitute, Open Approach
        "02110K9",  # Bypass Coronary Artery, Two Arteries from Left Internal Mammary with Nonautologous Tissue Substitute, Open Approach
        "02110KC",  # Bypass Coronary Artery, Two Arteries from Thoracic Artery with Nonautologous Tissue Substitute, Open Approach
        "02110KF",  # Bypass Coronary Artery, Two Arteries from Abdominal Artery with Nonautologous Tissue Substitute, Open Approach
        "02110KW",  # Bypass Coronary Artery, Two Arteries from Aorta with Nonautologous Tissue Substitute, Open Approach
        "02110Z3",  # Bypass Coronary Artery, Two Arteries from Coronary Artery, Open Approach
        "02110Z8",  # Bypass Coronary Artery, Two Arteries from Right Internal Mammary, Open Approach
        "02110Z9",  # Bypass Coronary Artery, Two Arteries from Left Internal Mammary, Open Approach
        "02110ZC",  # Bypass Coronary Artery, Two Arteries from Thoracic Artery, Open Approach
        "02110ZF",  # Bypass Coronary Artery, Two Arteries from Abdominal Artery, Open Approach
        "0211483",  # Bypass Coronary Artery, Two Arteries from Coronary Artery with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "0211488",  # Bypass Coronary Artery, Two Arteries from Right Internal Mammary with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "0211489",  # Bypass Coronary Artery, Two Arteries from Left Internal Mammary with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "021148C",  # Bypass Coronary Artery, Two Arteries from Thoracic Artery with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "021148F",  # Bypass Coronary Artery, Two Arteries from Abdominal Artery with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "021148W",  # Bypass Coronary Artery, Two Arteries from Aorta with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "0211493",  # Bypass Coronary Artery, Two Arteries from Coronary Artery with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "0211498",  # Bypass Coronary Artery, Two Arteries from Right Internal Mammary with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "0211499",  # Bypass Coronary Artery, Two Arteries from Left Internal Mammary with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "021149C",  # Bypass Coronary Artery, Two Arteries from Thoracic Artery with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "021149F",  # Bypass Coronary Artery, Two Arteries from Abdominal Artery with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "021149W",  # Bypass Coronary Artery, Two Arteries from Aorta with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "02114A3",  # Bypass Coronary Artery, Two Arteries from Coronary Artery with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02114A8",  # Bypass Coronary Artery, Two Arteries from Right Internal Mammary with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02114A9",  # Bypass Coronary Artery, Two Arteries from Left Internal Mammary with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02114AC",  # Bypass Coronary Artery, Two Arteries from Thoracic Artery with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02114AF",  # Bypass Coronary Artery, Two Arteries from Abdominal Artery with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02114AW",  # Bypass Coronary Artery, Two Arteries from Aorta with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02114J3",  # Bypass Coronary Artery, Two Arteries from Coronary Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02114J8",  # Bypass Coronary Artery, Two Arteries from Right Internal Mammary with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02114J9",  # Bypass Coronary Artery, Two Arteries from Left Internal Mammary with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02114JC",  # Bypass Coronary Artery, Two Arteries from Thoracic Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02114JF",  # Bypass Coronary Artery, Two Arteries from Abdominal Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02114JW",  # Bypass Coronary Artery, Two Arteries from Aorta with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02114K3",  # Bypass Coronary Artery, Two Arteries from Coronary Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02114K8",  # Bypass Coronary Artery, Two Arteries from Right Internal Mammary with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02114K9",  # Bypass Coronary Artery, Two Arteries from Left Internal Mammary with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02114KC",  # Bypass Coronary Artery, Two Arteries from Thoracic Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02114KF",  # Bypass Coronary Artery, Two Arteries from Abdominal Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02114KW",  # Bypass Coronary Artery, Two Arteries from Aorta with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02114Z3",  # Bypass Coronary Artery, Two Arteries from Coronary Artery, Percutaneous Endoscopic Approach
        "02114Z8",  # Bypass Coronary Artery, Two Arteries from Right Internal Mammary, Percutaneous Endoscopic Approach
        "02114Z9",  # Bypass Coronary Artery, Two Arteries from Left Internal Mammary, Percutaneous Endoscopic Approach
        "02114ZC",  # Bypass Coronary Artery, Two Arteries from Thoracic Artery, Percutaneous Endoscopic Approach
        "02114ZF",  # Bypass Coronary Artery, Two Arteries from Abdominal Artery, Percutaneous Endoscopic Approach
        "0212083",  # Bypass Coronary Artery, Three Arteries from Coronary Artery with Zooplastic Tissue, Open Approach
        "0212088",  # Bypass Coronary Artery, Three Arteries from Right Internal Mammary with Zooplastic Tissue, Open Approach
        "0212089",  # Bypass Coronary Artery, Three Arteries from Left Internal Mammary with Zooplastic Tissue, Open Approach
        "021208C",  # Bypass Coronary Artery, Three Arteries from Thoracic Artery with Zooplastic Tissue, Open Approach
        "021208F",  # Bypass Coronary Artery, Three Arteries from Abdominal Artery with Zooplastic Tissue, Open Approach
        "021208W",  # Bypass Coronary Artery, Three Arteries from Aorta with Zooplastic Tissue, Open Approach
        "0212093",  # Bypass Coronary Artery, Three Arteries from Coronary Artery with Autologous Venous Tissue, Open Approach
        "0212098",  # Bypass Coronary Artery, Three Arteries from Right Internal Mammary with Autologous Venous Tissue, Open Approach
        "0212099",  # Bypass Coronary Artery, Three Arteries from Left Internal Mammary with Autologous Venous Tissue, Open Approach
        "021209C",  # Bypass Coronary Artery, Three Arteries from Thoracic Artery with Autologous Venous Tissue, Open Approach
        "021209F",  # Bypass Coronary Artery, Three Arteries from Abdominal Artery with Autologous Venous Tissue, Open Approach
        "021209W",  # Bypass Coronary Artery, Three Arteries from Aorta with Autologous Venous Tissue, Open Approach
        "02120A3",  # Bypass Coronary Artery, Three Arteries from Coronary Artery with Autologous Arterial Tissue, Open Approach
        "02120A8",  # Bypass Coronary Artery, Three Arteries from Right Internal Mammary with Autologous Arterial Tissue, Open Approach
        "02120A9",  # Bypass Coronary Artery, Three Arteries from Left Internal Mammary with Autologous Arterial Tissue, Open Approach
        "02120AC",  # Bypass Coronary Artery, Three Arteries from Thoracic Artery with Autologous Arterial Tissue, Open Approach
        "02120AF",  # Bypass Coronary Artery, Three Arteries from Abdominal Artery with Autologous Arterial Tissue, Open Approach
        "02120AW",  # Bypass Coronary Artery, Three Arteries from Aorta with Autologous Arterial Tissue, Open Approach
        "02120J3",  # Bypass Coronary Artery, Three Arteries from Coronary Artery with Synthetic Substitute, Open Approach
        "02120J8",  # Bypass Coronary Artery, Three Arteries from Right Internal Mammary with Synthetic Substitute, Open Approach
        "02120J9",  # Bypass Coronary Artery, Three Arteries from Left Internal Mammary with Synthetic Substitute, Open Approach
        "02120JC",  # Bypass Coronary Artery, Three Arteries from Thoracic Artery with Synthetic Substitute, Open Approach
        "02120JF",  # Bypass Coronary Artery, Three Arteries from Abdominal Artery with Synthetic Substitute, Open Approach
        "02120JW",  # Bypass Coronary Artery, Three Arteries from Aorta with Synthetic Substitute, Open Approach
        "02120K3",  # Bypass Coronary Artery, Three Arteries from Coronary Artery with Nonautologous Tissue Substitute, Open Approach
        "02120K8",  # Bypass Coronary Artery, Three Arteries from Right Internal Mammary with Nonautologous Tissue Substitute, Open Approach
        "02120K9",  # Bypass Coronary Artery, Three Arteries from Left Internal Mammary with Nonautologous Tissue Substitute, Open Approach
        "02120KC",  # Bypass Coronary Artery, Three Arteries from Thoracic Artery with Nonautologous Tissue Substitute, Open Approach
        "02120KF",  # Bypass Coronary Artery, Three Arteries from Abdominal Artery with Nonautologous Tissue Substitute, Open Approach
        "02120KW",  # Bypass Coronary Artery, Three Arteries from Aorta with Nonautologous Tissue Substitute, Open Approach
        "02120Z3",  # Bypass Coronary Artery, Three Arteries from Coronary Artery, Open Approach
        "02120Z8",  # Bypass Coronary Artery, Three Arteries from Right Internal Mammary, Open Approach
        "02120Z9",  # Bypass Coronary Artery, Three Arteries from Left Internal Mammary, Open Approach
        "02120ZC",  # Bypass Coronary Artery, Three Arteries from Thoracic Artery, Open Approach
        "02120ZF",  # Bypass Coronary Artery, Three Arteries from Abdominal Artery, Open Approach
        "0212488",  # Bypass Coronary Artery, Three Arteries from Right Internal Mammary with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "0212489",  # Bypass Coronary Artery, Three Arteries from Left Internal Mammary with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "021248C",  # Bypass Coronary Artery, Three Arteries from Thoracic Artery with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "021248F",  # Bypass Coronary Artery, Three Arteries from Abdominal Artery with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "021248W",  # Bypass Coronary Artery, Three Arteries from Aorta with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "0212493",  # Bypass Coronary Artery, Three Arteries from Coronary Artery with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "0212498",  # Bypass Coronary Artery, Three Arteries from Right Internal Mammary with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "0212499",  # Bypass Coronary Artery, Three Arteries from Left Internal Mammary with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "021249C",  # Bypass Coronary Artery, Three Arteries from Thoracic Artery with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "021249F",  # Bypass Coronary Artery, Three Arteries from Abdominal Artery with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "021249W",  # Bypass Coronary Artery, Three Arteries from Aorta with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "02124A3",  # Bypass Coronary Artery, Three Arteries from Coronary Artery with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02124A8",  # Bypass Coronary Artery, Three Arteries from Right Internal Mammary with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02124A9",  # Bypass Coronary Artery, Three Arteries from Left Internal Mammary with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02124AC",  # Bypass Coronary Artery, Three Arteries from Thoracic Artery with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02124AF",  # Bypass Coronary Artery, Three Arteries from Abdominal Artery with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02124AW",  # Bypass Coronary Artery, Three Arteries from Aorta with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02124J3",  # Bypass Coronary Artery, Three Arteries from Coronary Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02124J8",  # Bypass Coronary Artery, Three Arteries from Right Internal Mammary with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02124J9",  # Bypass Coronary Artery, Three Arteries from Left Internal Mammary with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02124JC",  # Bypass Coronary Artery, Three Arteries from Thoracic Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02124JF",  # Bypass Coronary Artery, Three Arteries from Abdominal Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02124JW",  # Bypass Coronary Artery, Three Arteries from Aorta with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02124K3",  # Bypass Coronary Artery, Three Arteries from Coronary Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02124K8",  # Bypass Coronary Artery, Three Arteries from Right Internal Mammary with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02124K9",  # Bypass Coronary Artery, Three Arteries from Left Internal Mammary with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02124KC",  # Bypass Coronary Artery, Three Arteries from Thoracic Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02124KF",  # Bypass Coronary Artery, Three Arteries from Abdominal Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02124KW",  # Bypass Coronary Artery, Three Arteries from Aorta with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02124Z3",  # Bypass Coronary Artery, Three Arteries from Coronary Artery, Percutaneous Endoscopic Approach
        "02124Z8",  # Bypass Coronary Artery, Three Arteries from Right Internal Mammary, Percutaneous Endoscopic Approach
        "02124Z9",  # Bypass Coronary Artery, Three Arteries from Left Internal Mammary, Percutaneous Endoscopic Approach
        "02124ZC",  # Bypass Coronary Artery, Three Arteries from Thoracic Artery, Percutaneous Endoscopic Approach
        "02124ZF",  # Bypass Coronary Artery, Three Arteries from Abdominal Artery, Percutaneous Endoscopic Approach
        "0213083",  # Bypass Coronary Artery, Four or More Arteries from Coronary Artery with Zooplastic Tissue, Open Approach
        "0213088",  # Bypass Coronary Artery, Four or More Arteries from Right Internal Mammary with Zooplastic Tissue, Open Approach
        "0213089",  # Bypass Coronary Artery, Four or More Arteries from Left Internal Mammary with Zooplastic Tissue, Open Approach
        "021308C",  # Bypass Coronary Artery, Four or More Arteries from Thoracic Artery with Zooplastic Tissue, Open Approach
        "021308F",  # Bypass Coronary Artery, Four or More Arteries from Abdominal Artery with Zooplastic Tissue, Open Approach
        "021308W",  # Bypass Coronary Artery, Four or More Arteries from Aorta with Zooplastic Tissue, Open Approach
        "0213093",  # Bypass Coronary Artery, Four or More Arteries from Coronary Artery with Autologous Venous Tissue, Open Approach
        "0213098",  # Bypass Coronary Artery, Four or More Arteries from Right Internal Mammary with Autologous Venous Tissue, Open Approach
        "0213099",  # Bypass Coronary Artery, Four or More Arteries from Left Internal Mammary with Autologous Venous Tissue, Open Approach
        "021309C",  # Bypass Coronary Artery, Four or More Arteries from Thoracic Artery with Autologous Venous Tissue, Open Approach
        "021309F",  # Bypass Coronary Artery, Four or More Arteries from Abdominal Artery with Autologous Venous Tissue, Open Approach
        "021309W",  # Bypass Coronary Artery, Four or More Arteries from Aorta with Autologous Venous Tissue, Open Approach
        "02130A3",  # Bypass Coronary Artery, Four or More Arteries from Coronary Artery with Autologous Arterial Tissue, Open Approach
        "02130A8",  # Bypass Coronary Artery, Four or More Arteries from Right Internal Mammary with Autologous Arterial Tissue, Open Approach
        "02130A9",  # Bypass Coronary Artery, Four or More Arteries from Left Internal Mammary with Autologous Arterial Tissue, Open Approach
        "02130AC",  # Bypass Coronary Artery, Four or More Arteries from Thoracic Artery with Autologous Arterial Tissue, Open Approach
        "02130AF",  # Bypass Coronary Artery, Four or More Arteries from Abdominal Artery with Autologous Arterial Tissue, Open Approach
        "02130AW",  # Bypass Coronary Artery, Four or More Arteries from Aorta with Autologous Arterial Tissue, Open Approach
        "02130J3",  # Bypass Coronary Artery, Four or More Arteries from Coronary Artery with Synthetic Substitute, Open Approach
        "02130J8",  # Bypass Coronary Artery, Four or More Arteries from Right Internal Mammary with Synthetic Substitute, Open Approach
        "02130J9",  # Bypass Coronary Artery, Four or More Arteries from Left Internal Mammary with Synthetic Substitute, Open Approach
        "02130JC",  # Bypass Coronary Artery, Four or More Arteries from Thoracic Artery with Synthetic Substitute, Open Approach
        "02130JF",  # Bypass Coronary Artery, Four or More Arteries from Abdominal Artery with Synthetic Substitute, Open Approach
        "02130JW",  # Bypass Coronary Artery, Four or More Arteries from Aorta with Synthetic Substitute, Open Approach
        "02130K3",  # Bypass Coronary Artery, Four or More Arteries from Coronary Artery with Nonautologous Tissue Substitute, Open Approach
        "02130K8",  # Bypass Coronary Artery, Four or More Arteries from Right Internal Mammary with Nonautologous Tissue Substitute, Open Approach
        "02130K9",  # Bypass Coronary Artery, Four or More Arteries from Left Internal Mammary with Nonautologous Tissue Substitute, Open Approach
        "02130KC",  # Bypass Coronary Artery, Four or More Arteries from Thoracic Artery with Nonautologous Tissue Substitute, Open Approach
        "02130KF",  # Bypass Coronary Artery, Four or More Arteries from Abdominal Artery with Nonautologous Tissue Substitute, Open Approach
        "02130KW",  # Bypass Coronary Artery, Four or More Arteries from Aorta with Nonautologous Tissue Substitute, Open Approach
        "02130Z3",  # Bypass Coronary Artery, Four or More Arteries from Coronary Artery, Open Approach
        "02130Z8",  # Bypass Coronary Artery, Four or More Arteries from Right Internal Mammary, Open Approach
        "02130Z9",  # Bypass Coronary Artery, Four or More Arteries from Left Internal Mammary, Open Approach
        "02130ZC",  # Bypass Coronary Artery, Four or More Arteries from Thoracic Artery, Open Approach
        "02130ZF",  # Bypass Coronary Artery, Four or More Arteries from Abdominal Artery, Open Approach
        "0213483",  # Bypass Coronary Artery, Four or More Arteries from Coronary Artery with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "0213488",  # Bypass Coronary Artery, Four or More Arteries from Right Internal Mammary with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "0213489",  # Bypass Coronary Artery, Four or More Arteries from Left Internal Mammary with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "021348C",  # Bypass Coronary Artery, Four or More Arteries from Thoracic Artery with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "021348F",  # Bypass Coronary Artery, Four or More Arteries from Abdominal Artery with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "021348W",  # Bypass Coronary Artery, Four or More Arteries from Aorta with Zooplastic Tissue, Percutaneous Endoscopic Approach
        "0213493",  # Bypass Coronary Artery, Four or More Arteries from Coronary Artery with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "0213498",  # Bypass Coronary Artery, Four or More Arteries from Right Internal Mammary with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "0213499",  # Bypass Coronary Artery, Four or More Arteries from Left Internal Mammary with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "021349C",  # Bypass Coronary Artery, Four or More Arteries from Thoracic Artery with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "021349F",  # Bypass Coronary Artery, Four or More Arteries from Abdominal Artery with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "021349W",  # Bypass Coronary Artery, Four or More Arteries from Aorta with Autologous Venous Tissue, Percutaneous Endoscopic Approach
        "02134A3",  # Bypass Coronary Artery, Four or More Arteries from Coronary Artery with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02134A8",  # Bypass Coronary Artery, Four or More Arteries from Right Internal Mammary with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02134A9",  # Bypass Coronary Artery, Four or More Arteries from Left Internal Mammary with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02134AC",  # Bypass Coronary Artery, Four or More Arteries from Thoracic Artery with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02134AF",  # Bypass Coronary Artery, Four or More Arteries from Abdominal Artery with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02134AW",  # Bypass Coronary Artery, Four or More Arteries from Aorta with Autologous Arterial Tissue, Percutaneous Endoscopic Approach
        "02134J3",  # Bypass Coronary Artery, Four or More Arteries from Coronary Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02134J8",  # Bypass Coronary Artery, Four or More Arteries from Right Internal Mammary with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02134J9",  # Bypass Coronary Artery, Four or More Arteries from Left Internal Mammary with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02134JC",  # Bypass Coronary Artery, Four or More Arteries from Thoracic Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02134JF",  # Bypass Coronary Artery, Four or More Arteries from Abdominal Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02134JW",  # Bypass Coronary Artery, Four or More Arteries from Aorta with Synthetic Substitute, Percutaneous Endoscopic Approach
        "02134K3",  # Bypass Coronary Artery, Four or More Arteries from Coronary Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02134K8",  # Bypass Coronary Artery, Four or More Arteries from Right Internal Mammary with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02134K9",  # Bypass Coronary Artery, Four or More Arteries from Left Internal Mammary with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02134KC",  # Bypass Coronary Artery, Four or More Arteries from Thoracic Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02134KF",  # Bypass Coronary Artery, Four or More Arteries from Abdominal Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02134KW",  # Bypass Coronary Artery, Four or More Arteries from Aorta with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "02134Z3",  # Bypass Coronary Artery, Four or More Arteries from Coronary Artery, Percutaneous Endoscopic Approach
        "02134Z8",  # Bypass Coronary Artery, Four or More Arteries from Right Internal Mammary, Percutaneous Endoscopic Approach
        "02134Z9",  # Bypass Coronary Artery, Four or More Arteries from Left Internal Mammary, Percutaneous Endoscopic Approach
        "02134ZC",  # Bypass Coronary Artery, Four or More Arteries from Thoracic Artery, Percutaneous Endoscopic Approach
        "02134ZF",  # Bypass Coronary Artery, Four or More Arteries from Abdominal Artery, Percutaneous Endoscopic Approach
    }
    ICD9CM = {
        "3610",  # Aortocoronary bypass for heart revascularization, not otherwise specified
        "3611",  # (Aorto)coronary bypass of one coronary artery
        "3612",  # (Aorto)coronary bypass of two coronary arteries
        "3613",  # (Aorto)coronary bypass of three coronary arteries
        "3614",  # (Aorto)coronary bypass of four or more coronary arteries
        "3615",  # Single internal mammary-coronary artery bypass
        "3616",  # Double internal mammary-coronary artery bypass
        "3617",  # Abdominal-coronary artery bypass
        "3619",  # Other bypass anastomosis for heart revascularization
    }
    SNOMEDCT = {
        "3546002",  # Aortocoronary artery bypass graft with saphenous vein graft (procedure)
        "8876004",  # Aortocoronary artery bypass graft with prosthesis (procedure)
        "10190003",  # Aortocoronary bypass of four or more coronary arteries (procedure)
        "10326007",  # Coronary artery bypass with autogenous graft, three grafts (procedure)
        "14323007",  # Aortocoronary bypass of three coronary arteries (procedure)
        "17073005",  # Aortocoronary artery bypass graft with vein graft (procedure)
        "29819009",  # Aortocoronary bypass of one coronary artery (procedure)
        "39202005",  # Coronary artery bypass with autogenous graft, four grafts (procedure)
        "39724006",  # Anastomosis of internal mammary artery to coronary artery, double vessel (procedure)
        "67166004",  # Aortocoronary artery bypass graft (procedure)
        "74371005",  # Coronary artery bypass with autogenous graft, two grafts (procedure)
        "82247006",  # Coronary artery bypass with autogenous graft, five grafts (procedure)
        "90487008",  # Aortocoronary bypass of two coronary arteries (procedure)
        "119564002",  # Internal mammary-coronary artery bypass graft (procedure)
        "119565001",  # Coronary artery bypass graft, anastomosis of artery of thorax to coronary artery (procedure)
        "175021005",  # Allograft bypass of coronary artery (procedure)
        "175029007",  # Prosthetic bypass of coronary artery (procedure)
        "175036008",  # Revision of bypass for coronary artery (procedure)
        "175037004",  # Revision of bypass for one coronary artery (procedure)
        "175038009",  # Revision of bypass for two coronary arteries (procedure)
        "175039001",  # Revision of bypass for three coronary arteries (procedure)
        "175040004",  # Revision of bypass for four or more coronary arteries (procedure)
        "175066001",  # Percutaneous transluminal balloon angioplasty of bypass graft of coronary artery (procedure)
        "232717009",  # Coronary artery bypass grafting (procedure)
        "232719007",  # Coronary artery bypass graft x 1 (procedure)
        "232720001",  # Coronary artery bypass grafts x 2 (procedure)
        "232721002",  # Coronary artery bypass grafts x 3 (procedure)
        "232722009",  # Coronary artery bypass grafts x 4 (procedure)
        "232723004",  # Coronary artery bypass grafts x 5 (procedure)
        "232724005",  # Coronary artery bypass grafts greater than 5 (procedure)
        "252427007",  # Coronary bypass graft angiography (procedure)
        "309814006",  # Aortocoronary bypass grafting (procedure)
        "359597003",  # Single internal mammary-coronary artery bypass (procedure)
        "359601003",  # Coronary artery bypass with autogenous graft of internal mammary artery, single graft (procedure)
        "405598005",  # Aortocoronary artery bypass graft with two vein grafts (procedure)
        "405599002",  # Aortocoronary artery bypass graft with three vein grafts (procedure)
        "414088005",  # Emergency coronary artery bypass graft (procedure)
        "418551006",  # Laparoscopic coronary artery bypass using robotic assistance (procedure)
        "419132001",  # Minimally invasive direct coronary artery bypass (procedure)
        "438530000",  # Magnetic resonance angiography of coronary artery bypass graft (procedure)
        "440332008",  # Fluoroscopic angiography of left ventricle and coronary artery bypass graft (procedure)
        "450506009",  # Computed tomography angiography of coronary artery bypass graft (procedure)
        "736970002",  # Allograft bypass of four or more coronary arteries (procedure)
        "736971003",  # Allograft bypass of one coronary artery (procedure)
        "736972005",  # Allograft bypass of three coronary arteries (procedure)
        "736973000",  # Allograft bypass of two coronary arteries (procedure)
    }


class Cabg_PciProcedure(ValueSet):
    """CABG, PCI Procedure Value Set.

    **Clinical Focus:** CABG and PCI procedures

    **Data Element Scope:** CABG and PCI procedures

    **Inclusion Criteria:** Codes from 2018_Registry_SingleSource_v2.2

    **Exclusion Criteria:** None

    ** Used in:** CMS347v5
    """

    VALUE_SET_NAME = "CABG, PCI Procedure"
    OID = "2.16.840.1.113762.1.4.1138.566"
    DEFINITION_VERSION = "20180818"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "33510",  # Coronary artery bypass, vein only; single coronary venous graft
        "33511",  # Coronary artery bypass, vein only; 2 coronary venous grafts
        "33512",  # Coronary artery bypass, vein only; 3 coronary venous grafts
        "33513",  # Coronary artery bypass, vein only; 4 coronary venous grafts
        "33514",  # Coronary artery bypass, vein only; 5 coronary venous grafts
        "33516",  # Coronary artery bypass, vein only; 6 or more coronary venous grafts
        "33517",  # Coronary artery bypass, using venous graft(s) and arterial graft(s); single vein graft (List separately in addition to code for primary procedure)
        "33518",  # Coronary artery bypass, using venous graft(s) and arterial graft(s); 2 venous grafts (List separately in addition to code for primary procedure)
        "33519",  # Coronary artery bypass, using venous graft(s) and arterial graft(s); 3 venous grafts (List separately in addition to code for primary procedure)
        "33521",  # Coronary artery bypass, using venous graft(s) and arterial graft(s); 4 venous grafts (List separately in addition to code for primary procedure)
        "33522",  # Coronary artery bypass, using venous graft(s) and arterial graft(s); 5 venous grafts (List separately in addition to code for primary procedure)
        "33523",  # Coronary artery bypass, using venous graft(s) and arterial graft(s); 6 or more venous grafts (List separately in addition to code for primary procedure)
        "33533",  # Coronary artery bypass, using arterial graft(s); single arterial graft
        "33534",  # Coronary artery bypass, using arterial graft(s); 2 coronary arterial grafts
        "33535",  # Coronary artery bypass, using arterial graft(s); 3 coronary arterial grafts
        "33536",  # Coronary artery bypass, using arterial graft(s); 4 or more coronary arterial grafts
        "92920",  # Percutaneous transluminal coronary angioplasty; single major coronary artery or branch
        "92924",  # Percutaneous transluminal coronary atherectomy, with coronary angioplasty when performed; single major coronary artery or branch
        "92928",  # Percutaneous transcatheter placement of intracoronary stent(s), with coronary angioplasty when performed; single major coronary artery or branch
        "92933",  # Percutaneous transluminal coronary atherectomy, with intracoronary stent, with coronary angioplasty when performed; single major coronary artery or branch
        "92937",  # Percutaneous transluminal revascularization of or through coronary artery bypass graft (internal mammary, free arterial, venous), any combination of intracoronary stent, atherectomy and angioplasty, including distal protection when performed; single vessel
        "92941",  # Percutaneous transluminal revascularization of acute total/subtotal occlusion during acute myocardial infarction, coronary artery or coronary artery bypass graft, any combination of intracoronary stent, atherectomy and angioplasty, including aspiration thrombectomy when performed, single vessel
        "92943",  # Percutaneous transluminal revascularization of chronic total occlusion, coronary artery, coronary artery branch, or coronary artery bypass graft, any combination of intracoronary stent, atherectomy and angioplasty; single vessel
    }
    HCPCSLEVELII = {
        "S2205",  # Minimally invasive direct coronary artery bypass surgery involving mini-thoracotomy or mini-sternotomy surgery, performed under direct vision; using arterial graft(s), single coronary arterial graft
        "S2206",  # Minimally invasive direct coronary artery bypass surgery involving mini-thoracotomy or mini-sternotomy surgery, performed under direct vision; using arterial graft(s), two coronary arterial grafts
        "S2207",  # Minimally invasive direct coronary artery bypass surgery involving mini-thoracotomy or mini-sternotomy surgery, performed under direct vision; using venous graft only, single coronary venous graft
        "S2208",  # Minimally invasive direct coronary artery bypass surgery involving mini-thoracotomy or mini-sternotomy surgery, performed under direct vision; using single arterial and venous graft(s), single venous graft
        "S2209",  # Minimally invasive direct coronary artery bypass surgery involving mini-thoracotomy or mini-sternotomy surgery, performed under direct vision; using two arterial grafts and single venous graft
    }


class CarotidIntervention(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for procedures for carotid surgical intervention.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a procedure carotid intervention surgery.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS347v5
    """

    VALUE_SET_NAME = "Carotid Intervention"
    OID = "2.16.840.1.113883.3.117.1.7.1.204"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    ICD10PCS = {
        "031H09G",  # Bypass Right Common Carotid Artery to Intracranial Artery with Autologous Venous Tissue, Open Approach
        "031H09J",  # Bypass Right Common Carotid Artery to Right Extracranial Artery with Autologous Venous Tissue, Open Approach
        "031H09K",  # Bypass Right Common Carotid Artery to Left Extracranial Artery with Autologous Venous Tissue, Open Approach
        "031H09Y",  # Bypass Right Common Carotid Artery to Upper Artery with Autologous Venous Tissue, Open Approach
        "031H0AG",  # Bypass Right Common Carotid Artery to Intracranial Artery with Autologous Arterial Tissue, Open Approach
        "031H0AJ",  # Bypass Right Common Carotid Artery to Right Extracranial Artery with Autologous Arterial Tissue, Open Approach
        "031H0AK",  # Bypass Right Common Carotid Artery to Left Extracranial Artery with Autologous Arterial Tissue, Open Approach
        "031H0AY",  # Bypass Right Common Carotid Artery to Upper Artery with Autologous Arterial Tissue, Open Approach
        "031H0JG",  # Bypass Right Common Carotid Artery to Intracranial Artery with Synthetic Substitute, Open Approach
        "031H0JJ",  # Bypass Right Common Carotid Artery to Right Extracranial Artery with Synthetic Substitute, Open Approach
        "031H0JK",  # Bypass Right Common Carotid Artery to Left Extracranial Artery with Synthetic Substitute, Open Approach
        "031H0JY",  # Bypass Right Common Carotid Artery to Upper Artery with Synthetic Substitute, Open Approach
        "031H0KG",  # Bypass Right Common Carotid Artery to Intracranial Artery with Nonautologous Tissue Substitute, Open Approach
        "031H0KJ",  # Bypass Right Common Carotid Artery to Right Extracranial Artery with Nonautologous Tissue Substitute, Open Approach
        "031H0KK",  # Bypass Right Common Carotid Artery to Left Extracranial Artery with Nonautologous Tissue Substitute, Open Approach
        "031H0KY",  # Bypass Right Common Carotid Artery to Upper Artery with Nonautologous Tissue Substitute, Open Approach
        "031H0ZG",  # Bypass Right Common Carotid Artery to Intracranial Artery, Open Approach
        "031H0ZJ",  # Bypass Right Common Carotid Artery to Right Extracranial Artery, Open Approach
        "031H0ZK",  # Bypass Right Common Carotid Artery to Left Extracranial Artery, Open Approach
        "031H0ZY",  # Bypass Right Common Carotid Artery to Upper Artery, Open Approach
        "031J09G",  # Bypass Left Common Carotid Artery to Intracranial Artery with Autologous Venous Tissue, Open Approach
        "031J09J",  # Bypass Left Common Carotid Artery to Right Extracranial Artery with Autologous Venous Tissue, Open Approach
        "031J09K",  # Bypass Left Common Carotid Artery to Left Extracranial Artery with Autologous Venous Tissue, Open Approach
        "031J09Y",  # Bypass Left Common Carotid Artery to Upper Artery with Autologous Venous Tissue, Open Approach
        "031J0AG",  # Bypass Left Common Carotid Artery to Intracranial Artery with Autologous Arterial Tissue, Open Approach
        "031J0AJ",  # Bypass Left Common Carotid Artery to Right Extracranial Artery with Autologous Arterial Tissue, Open Approach
        "031J0AK",  # Bypass Left Common Carotid Artery to Left Extracranial Artery with Autologous Arterial Tissue, Open Approach
        "031J0AY",  # Bypass Left Common Carotid Artery to Upper Artery with Autologous Arterial Tissue, Open Approach
        "031J0JG",  # Bypass Left Common Carotid Artery to Intracranial Artery with Synthetic Substitute, Open Approach
        "031J0JJ",  # Bypass Left Common Carotid Artery to Right Extracranial Artery with Synthetic Substitute, Open Approach
        "031J0JK",  # Bypass Left Common Carotid Artery to Left Extracranial Artery with Synthetic Substitute, Open Approach
        "031J0JY",  # Bypass Left Common Carotid Artery to Upper Artery with Synthetic Substitute, Open Approach
        "031J0KG",  # Bypass Left Common Carotid Artery to Intracranial Artery with Nonautologous Tissue Substitute, Open Approach
        "031J0KJ",  # Bypass Left Common Carotid Artery to Right Extracranial Artery with Nonautologous Tissue Substitute, Open Approach
        "031J0KK",  # Bypass Left Common Carotid Artery to Left Extracranial Artery with Nonautologous Tissue Substitute, Open Approach
        "031J0KY",  # Bypass Left Common Carotid Artery to Upper Artery with Nonautologous Tissue Substitute, Open Approach
        "031J0ZG",  # Bypass Left Common Carotid Artery to Intracranial Artery, Open Approach
        "031J0ZJ",  # Bypass Left Common Carotid Artery to Right Extracranial Artery, Open Approach
        "031J0ZK",  # Bypass Left Common Carotid Artery to Left Extracranial Artery, Open Approach
        "031J0ZY",  # Bypass Left Common Carotid Artery to Upper Artery, Open Approach
        "031K09J",  # Bypass Right Internal Carotid Artery to Right Extracranial Artery with Autologous Venous Tissue, Open Approach
        "031K09K",  # Bypass Right Internal Carotid Artery to Left Extracranial Artery with Autologous Venous Tissue, Open Approach
        "031K0AJ",  # Bypass Right Internal Carotid Artery to Right Extracranial Artery with Autologous Arterial Tissue, Open Approach
        "031K0AK",  # Bypass Right Internal Carotid Artery to Left Extracranial Artery with Autologous Arterial Tissue, Open Approach
        "031K0JJ",  # Bypass Right Internal Carotid Artery to Right Extracranial Artery with Synthetic Substitute, Open Approach
        "031K0JK",  # Bypass Right Internal Carotid Artery to Left Extracranial Artery with Synthetic Substitute, Open Approach
        "031K0KJ",  # Bypass Right Internal Carotid Artery to Right Extracranial Artery with Nonautologous Tissue Substitute, Open Approach
        "031K0KK",  # Bypass Right Internal Carotid Artery to Left Extracranial Artery with Nonautologous Tissue Substitute, Open Approach
        "031K0ZJ",  # Bypass Right Internal Carotid Artery to Right Extracranial Artery, Open Approach
        "031K0ZK",  # Bypass Right Internal Carotid Artery to Left Extracranial Artery, Open Approach
        "031L09J",  # Bypass Left Internal Carotid Artery to Right Extracranial Artery with Autologous Venous Tissue, Open Approach
        "031L09K",  # Bypass Left Internal Carotid Artery to Left Extracranial Artery with Autologous Venous Tissue, Open Approach
        "031L0AJ",  # Bypass Left Internal Carotid Artery to Right Extracranial Artery with Autologous Arterial Tissue, Open Approach
        "031L0AK",  # Bypass Left Internal Carotid Artery to Left Extracranial Artery with Autologous Arterial Tissue, Open Approach
        "031L0JJ",  # Bypass Left Internal Carotid Artery to Right Extracranial Artery with Synthetic Substitute, Open Approach
        "031L0JK",  # Bypass Left Internal Carotid Artery to Left Extracranial Artery with Synthetic Substitute, Open Approach
        "031L0KJ",  # Bypass Left Internal Carotid Artery to Right Extracranial Artery with Nonautologous Tissue Substitute, Open Approach
        "031L0KK",  # Bypass Left Internal Carotid Artery to Left Extracranial Artery with Nonautologous Tissue Substitute, Open Approach
        "031L0ZJ",  # Bypass Left Internal Carotid Artery to Right Extracranial Artery, Open Approach
        "031L0ZK",  # Bypass Left Internal Carotid Artery to Left Extracranial Artery, Open Approach
        "031M09J",  # Bypass Right External Carotid Artery to Right Extracranial Artery with Autologous Venous Tissue, Open Approach
        "031M09K",  # Bypass Right External Carotid Artery to Left Extracranial Artery with Autologous Venous Tissue, Open Approach
        "031M0AJ",  # Bypass Right External Carotid Artery to Right Extracranial Artery with Autologous Arterial Tissue, Open Approach
        "031M0AK",  # Bypass Right External Carotid Artery to Left Extracranial Artery with Autologous Arterial Tissue, Open Approach
        "031M0JJ",  # Bypass Right External Carotid Artery to Right Extracranial Artery with Synthetic Substitute, Open Approach
        "031M0JK",  # Bypass Right External Carotid Artery to Left Extracranial Artery with Synthetic Substitute, Open Approach
        "031M0KJ",  # Bypass Right External Carotid Artery to Right Extracranial Artery with Nonautologous Tissue Substitute, Open Approach
        "031M0KK",  # Bypass Right External Carotid Artery to Left Extracranial Artery with Nonautologous Tissue Substitute, Open Approach
        "031M0ZJ",  # Bypass Right External Carotid Artery to Right Extracranial Artery, Open Approach
        "031M0ZK",  # Bypass Right External Carotid Artery to Left Extracranial Artery, Open Approach
        "031N09J",  # Bypass Left External Carotid Artery to Right Extracranial Artery with Autologous Venous Tissue, Open Approach
        "031N09K",  # Bypass Left External Carotid Artery to Left Extracranial Artery with Autologous Venous Tissue, Open Approach
        "031N0AJ",  # Bypass Left External Carotid Artery to Right Extracranial Artery with Autologous Arterial Tissue, Open Approach
        "031N0AK",  # Bypass Left External Carotid Artery to Left Extracranial Artery with Autologous Arterial Tissue, Open Approach
        "031N0JJ",  # Bypass Left External Carotid Artery to Right Extracranial Artery with Synthetic Substitute, Open Approach
        "031N0JK",  # Bypass Left External Carotid Artery to Left Extracranial Artery with Synthetic Substitute, Open Approach
        "031N0KJ",  # Bypass Left External Carotid Artery to Right Extracranial Artery with Nonautologous Tissue Substitute, Open Approach
        "031N0KK",  # Bypass Left External Carotid Artery to Left Extracranial Artery with Nonautologous Tissue Substitute, Open Approach
        "031N0ZJ",  # Bypass Left External Carotid Artery to Right Extracranial Artery, Open Approach
        "031N0ZK",  # Bypass Left External Carotid Artery to Left Extracranial Artery, Open Approach
        "035H0ZZ",  # Destruction of Right Common Carotid Artery, Open Approach
        "035H3ZZ",  # Destruction of Right Common Carotid Artery, Percutaneous Approach
        "035H4ZZ",  # Destruction of Right Common Carotid Artery, Percutaneous Endoscopic Approach
        "035J0ZZ",  # Destruction of Left Common Carotid Artery, Open Approach
        "035J3ZZ",  # Destruction of Left Common Carotid Artery, Percutaneous Approach
        "035J4ZZ",  # Destruction of Left Common Carotid Artery, Percutaneous Endoscopic Approach
        "035K0ZZ",  # Destruction of Right Internal Carotid Artery, Open Approach
        "035K3ZZ",  # Destruction of Right Internal Carotid Artery, Percutaneous Approach
        "035K4ZZ",  # Destruction of Right Internal Carotid Artery, Percutaneous Endoscopic Approach
        "035L0ZZ",  # Destruction of Left Internal Carotid Artery, Open Approach
        "035L3ZZ",  # Destruction of Left Internal Carotid Artery, Percutaneous Approach
        "035L4ZZ",  # Destruction of Left Internal Carotid Artery, Percutaneous Endoscopic Approach
        "035M0ZZ",  # Destruction of Right External Carotid Artery, Open Approach
        "035M3ZZ",  # Destruction of Right External Carotid Artery, Percutaneous Approach
        "035M4ZZ",  # Destruction of Right External Carotid Artery, Percutaneous Endoscopic Approach
        "035N0ZZ",  # Destruction of Left External Carotid Artery, Open Approach
        "035N3ZZ",  # Destruction of Left External Carotid Artery, Percutaneous Approach
        "035N4ZZ",  # Destruction of Left External Carotid Artery, Percutaneous Endoscopic Approach
        "037H046",  # Dilation of Right Common Carotid Artery, Bifurcation, with Drug-eluting Intraluminal Device, Open Approach
        "037H04Z",  # Dilation of Right Common Carotid Artery with Drug-eluting Intraluminal Device, Open Approach
        "037H056",  # Dilation of Right Common Carotid Artery, Bifurcation, with Two Drug-eluting Intraluminal Devices, Open Approach
        "037H05Z",  # Dilation of Right Common Carotid Artery with Two Drug-eluting Intraluminal Devices, Open Approach
        "037H066",  # Dilation of Right Common Carotid Artery, Bifurcation, with Three Drug-eluting Intraluminal Devices, Open Approach
        "037H06Z",  # Dilation of Right Common Carotid Artery with Three Drug-eluting Intraluminal Devices, Open Approach
        "037H076",  # Dilation of Right Common Carotid Artery, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Open Approach
        "037H07Z",  # Dilation of Right Common Carotid Artery with Four or More Drug-eluting Intraluminal Devices, Open Approach
        "037H0D6",  # Dilation of Right Common Carotid Artery, Bifurcation, with Intraluminal Device, Open Approach
        "037H0DZ",  # Dilation of Right Common Carotid Artery with Intraluminal Device, Open Approach
        "037H0E6",  # Dilation of Right Common Carotid Artery, Bifurcation, with Two Intraluminal Devices, Open Approach
        "037H0EZ",  # Dilation of Right Common Carotid Artery with Two Intraluminal Devices, Open Approach
        "037H0F6",  # Dilation of Right Common Carotid Artery, Bifurcation, with Three Intraluminal Devices, Open Approach
        "037H0FZ",  # Dilation of Right Common Carotid Artery with Three Intraluminal Devices, Open Approach
        "037H0G6",  # Dilation of Right Common Carotid Artery, Bifurcation, with Four or More Intraluminal Devices, Open Approach
        "037H0GZ",  # Dilation of Right Common Carotid Artery with Four or More Intraluminal Devices, Open Approach
        "037H0Z6",  # Dilation of Right Common Carotid Artery, Bifurcation, Open Approach
        "037H0ZZ",  # Dilation of Right Common Carotid Artery, Open Approach
        "037H346",  # Dilation of Right Common Carotid Artery, Bifurcation, with Drug-eluting Intraluminal Device, Percutaneous Approach
        "037H34Z",  # Dilation of Right Common Carotid Artery with Drug-eluting Intraluminal Device, Percutaneous Approach
        "037H356",  # Dilation of Right Common Carotid Artery, Bifurcation, with Two Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037H35Z",  # Dilation of Right Common Carotid Artery with Two Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037H366",  # Dilation of Right Common Carotid Artery, Bifurcation, with Three Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037H36Z",  # Dilation of Right Common Carotid Artery with Three Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037H376",  # Dilation of Right Common Carotid Artery, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037H37Z",  # Dilation of Right Common Carotid Artery with Four or More Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037H3D6",  # Dilation of Right Common Carotid Artery, Bifurcation, with Intraluminal Device, Percutaneous Approach
        "037H3DZ",  # Dilation of Right Common Carotid Artery with Intraluminal Device, Percutaneous Approach
        "037H3E6",  # Dilation of Right Common Carotid Artery, Bifurcation, with Two Intraluminal Devices, Percutaneous Approach
        "037H3EZ",  # Dilation of Right Common Carotid Artery with Two Intraluminal Devices, Percutaneous Approach
        "037H3F6",  # Dilation of Right Common Carotid Artery, Bifurcation, with Three Intraluminal Devices, Percutaneous Approach
        "037H3FZ",  # Dilation of Right Common Carotid Artery with Three Intraluminal Devices, Percutaneous Approach
        "037H3G6",  # Dilation of Right Common Carotid Artery, Bifurcation, with Four or More Intraluminal Devices, Percutaneous Approach
        "037H3GZ",  # Dilation of Right Common Carotid Artery with Four or More Intraluminal Devices, Percutaneous Approach
        "037H3Z6",  # Dilation of Right Common Carotid Artery, Bifurcation, Percutaneous Approach
        "037H3ZZ",  # Dilation of Right Common Carotid Artery, Percutaneous Approach
        "037H446",  # Dilation of Right Common Carotid Artery, Bifurcation, with Drug-eluting Intraluminal Device, Percutaneous Endoscopic Approach
        "037H44Z",  # Dilation of Right Common Carotid Artery with Drug-eluting Intraluminal Device, Percutaneous Endoscopic Approach
        "037H456",  # Dilation of Right Common Carotid Artery, Bifurcation, with Two Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037H45Z",  # Dilation of Right Common Carotid Artery with Two Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037H466",  # Dilation of Right Common Carotid Artery, Bifurcation, with Three Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037H46Z",  # Dilation of Right Common Carotid Artery with Three Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037H476",  # Dilation of Right Common Carotid Artery, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037H47Z",  # Dilation of Right Common Carotid Artery with Four or More Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037H4D6",  # Dilation of Right Common Carotid Artery, Bifurcation, with Intraluminal Device, Percutaneous Endoscopic Approach
        "037H4DZ",  # Dilation of Right Common Carotid Artery with Intraluminal Device, Percutaneous Endoscopic Approach
        "037H4E6",  # Dilation of Right Common Carotid Artery, Bifurcation, with Two Intraluminal Devices, Percutaneous Endoscopic Approach
        "037H4EZ",  # Dilation of Right Common Carotid Artery with Two Intraluminal Devices, Percutaneous Endoscopic Approach
        "037H4F6",  # Dilation of Right Common Carotid Artery, Bifurcation, with Three Intraluminal Devices, Percutaneous Endoscopic Approach
        "037H4FZ",  # Dilation of Right Common Carotid Artery with Three Intraluminal Devices, Percutaneous Endoscopic Approach
        "037H4G6",  # Dilation of Right Common Carotid Artery, Bifurcation, with Four or More Intraluminal Devices, Percutaneous Endoscopic Approach
        "037H4GZ",  # Dilation of Right Common Carotid Artery with Four or More Intraluminal Devices, Percutaneous Endoscopic Approach
        "037H4Z6",  # Dilation of Right Common Carotid Artery, Bifurcation, Percutaneous Endoscopic Approach
        "037H4ZZ",  # Dilation of Right Common Carotid Artery, Percutaneous Endoscopic Approach
        "037J046",  # Dilation of Left Common Carotid Artery, Bifurcation, with Drug-eluting Intraluminal Device, Open Approach
        "037J04Z",  # Dilation of Left Common Carotid Artery with Drug-eluting Intraluminal Device, Open Approach
        "037J056",  # Dilation of Left Common Carotid Artery, Bifurcation, with Two Drug-eluting Intraluminal Devices, Open Approach
        "037J05Z",  # Dilation of Left Common Carotid Artery with Two Drug-eluting Intraluminal Devices, Open Approach
        "037J066",  # Dilation of Left Common Carotid Artery, Bifurcation, with Three Drug-eluting Intraluminal Devices, Open Approach
        "037J06Z",  # Dilation of Left Common Carotid Artery with Three Drug-eluting Intraluminal Devices, Open Approach
        "037J076",  # Dilation of Left Common Carotid Artery, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Open Approach
        "037J07Z",  # Dilation of Left Common Carotid Artery with Four or More Drug-eluting Intraluminal Devices, Open Approach
        "037J0D6",  # Dilation of Left Common Carotid Artery, Bifurcation, with Intraluminal Device, Open Approach
        "037J0DZ",  # Dilation of Left Common Carotid Artery with Intraluminal Device, Open Approach
        "037J0E6",  # Dilation of Left Common Carotid Artery, Bifurcation, with Two Intraluminal Devices, Open Approach
        "037J0EZ",  # Dilation of Left Common Carotid Artery with Two Intraluminal Devices, Open Approach
        "037J0F6",  # Dilation of Left Common Carotid Artery, Bifurcation, with Three Intraluminal Devices, Open Approach
        "037J0FZ",  # Dilation of Left Common Carotid Artery with Three Intraluminal Devices, Open Approach
        "037J0G6",  # Dilation of Left Common Carotid Artery, Bifurcation, with Four or More Intraluminal Devices, Open Approach
        "037J0GZ",  # Dilation of Left Common Carotid Artery with Four or More Intraluminal Devices, Open Approach
        "037J0Z6",  # Dilation of Left Common Carotid Artery, Bifurcation, Open Approach
        "037J0ZZ",  # Dilation of Left Common Carotid Artery, Open Approach
        "037J346",  # Dilation of Left Common Carotid Artery, Bifurcation, with Drug-eluting Intraluminal Device, Percutaneous Approach
        "037J34Z",  # Dilation of Left Common Carotid Artery with Drug-eluting Intraluminal Device, Percutaneous Approach
        "037J356",  # Dilation of Left Common Carotid Artery, Bifurcation, with Two Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037J35Z",  # Dilation of Left Common Carotid Artery with Two Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037J366",  # Dilation of Left Common Carotid Artery, Bifurcation, with Three Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037J36Z",  # Dilation of Left Common Carotid Artery with Three Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037J376",  # Dilation of Left Common Carotid Artery, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037J37Z",  # Dilation of Left Common Carotid Artery with Four or More Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037J3D6",  # Dilation of Left Common Carotid Artery, Bifurcation, with Intraluminal Device, Percutaneous Approach
        "037J3DZ",  # Dilation of Left Common Carotid Artery with Intraluminal Device, Percutaneous Approach
        "037J3E6",  # Dilation of Left Common Carotid Artery, Bifurcation, with Two Intraluminal Devices, Percutaneous Approach
        "037J3EZ",  # Dilation of Left Common Carotid Artery with Two Intraluminal Devices, Percutaneous Approach
        "037J3F6",  # Dilation of Left Common Carotid Artery, Bifurcation, with Three Intraluminal Devices, Percutaneous Approach
        "037J3FZ",  # Dilation of Left Common Carotid Artery with Three Intraluminal Devices, Percutaneous Approach
        "037J3G6",  # Dilation of Left Common Carotid Artery, Bifurcation, with Four or More Intraluminal Devices, Percutaneous Approach
        "037J3GZ",  # Dilation of Left Common Carotid Artery with Four or More Intraluminal Devices, Percutaneous Approach
        "037J3Z6",  # Dilation of Left Common Carotid Artery, Bifurcation, Percutaneous Approach
        "037J3ZZ",  # Dilation of Left Common Carotid Artery, Percutaneous Approach
        "037J446",  # Dilation of Left Common Carotid Artery, Bifurcation, with Drug-eluting Intraluminal Device, Percutaneous Endoscopic Approach
        "037J44Z",  # Dilation of Left Common Carotid Artery with Drug-eluting Intraluminal Device, Percutaneous Endoscopic Approach
        "037J456",  # Dilation of Left Common Carotid Artery, Bifurcation, with Two Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037J45Z",  # Dilation of Left Common Carotid Artery with Two Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037J466",  # Dilation of Left Common Carotid Artery, Bifurcation, with Three Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037J46Z",  # Dilation of Left Common Carotid Artery with Three Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037J476",  # Dilation of Left Common Carotid Artery, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037J47Z",  # Dilation of Left Common Carotid Artery with Four or More Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037J4D6",  # Dilation of Left Common Carotid Artery, Bifurcation, with Intraluminal Device, Percutaneous Endoscopic Approach
        "037J4DZ",  # Dilation of Left Common Carotid Artery with Intraluminal Device, Percutaneous Endoscopic Approach
        "037J4E6",  # Dilation of Left Common Carotid Artery, Bifurcation, with Two Intraluminal Devices, Percutaneous Endoscopic Approach
        "037J4EZ",  # Dilation of Left Common Carotid Artery with Two Intraluminal Devices, Percutaneous Endoscopic Approach
        "037J4F6",  # Dilation of Left Common Carotid Artery, Bifurcation, with Three Intraluminal Devices, Percutaneous Endoscopic Approach
        "037J4FZ",  # Dilation of Left Common Carotid Artery with Three Intraluminal Devices, Percutaneous Endoscopic Approach
        "037J4G6",  # Dilation of Left Common Carotid Artery, Bifurcation, with Four or More Intraluminal Devices, Percutaneous Endoscopic Approach
        "037J4GZ",  # Dilation of Left Common Carotid Artery with Four or More Intraluminal Devices, Percutaneous Endoscopic Approach
        "037J4Z6",  # Dilation of Left Common Carotid Artery, Bifurcation, Percutaneous Endoscopic Approach
        "037J4ZZ",  # Dilation of Left Common Carotid Artery, Percutaneous Endoscopic Approach
        "037K046",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Drug-eluting Intraluminal Device, Open Approach
        "037K04Z",  # Dilation of Right Internal Carotid Artery with Drug-eluting Intraluminal Device, Open Approach
        "037K056",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Two Drug-eluting Intraluminal Devices, Open Approach
        "037K05Z",  # Dilation of Right Internal Carotid Artery with Two Drug-eluting Intraluminal Devices, Open Approach
        "037K066",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Three Drug-eluting Intraluminal Devices, Open Approach
        "037K06Z",  # Dilation of Right Internal Carotid Artery with Three Drug-eluting Intraluminal Devices, Open Approach
        "037K076",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Open Approach
        "037K07Z",  # Dilation of Right Internal Carotid Artery with Four or More Drug-eluting Intraluminal Devices, Open Approach
        "037K0D6",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Intraluminal Device, Open Approach
        "037K0DZ",  # Dilation of Right Internal Carotid Artery with Intraluminal Device, Open Approach
        "037K0E6",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Two Intraluminal Devices, Open Approach
        "037K0EZ",  # Dilation of Right Internal Carotid Artery with Two Intraluminal Devices, Open Approach
        "037K0F6",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Three Intraluminal Devices, Open Approach
        "037K0FZ",  # Dilation of Right Internal Carotid Artery with Three Intraluminal Devices, Open Approach
        "037K0G6",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Four or More Intraluminal Devices, Open Approach
        "037K0GZ",  # Dilation of Right Internal Carotid Artery with Four or More Intraluminal Devices, Open Approach
        "037K0Z6",  # Dilation of Right Internal Carotid Artery, Bifurcation, Open Approach
        "037K0ZZ",  # Dilation of Right Internal Carotid Artery, Open Approach
        "037K346",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Drug-eluting Intraluminal Device, Percutaneous Approach
        "037K34Z",  # Dilation of Right Internal Carotid Artery with Drug-eluting Intraluminal Device, Percutaneous Approach
        "037K356",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Two Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037K35Z",  # Dilation of Right Internal Carotid Artery with Two Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037K366",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Three Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037K36Z",  # Dilation of Right Internal Carotid Artery with Three Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037K376",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037K37Z",  # Dilation of Right Internal Carotid Artery with Four or More Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037K3D6",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Intraluminal Device, Percutaneous Approach
        "037K3DZ",  # Dilation of Right Internal Carotid Artery with Intraluminal Device, Percutaneous Approach
        "037K3E6",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Two Intraluminal Devices, Percutaneous Approach
        "037K3EZ",  # Dilation of Right Internal Carotid Artery with Two Intraluminal Devices, Percutaneous Approach
        "037K3F6",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Three Intraluminal Devices, Percutaneous Approach
        "037K3FZ",  # Dilation of Right Internal Carotid Artery with Three Intraluminal Devices, Percutaneous Approach
        "037K3G6",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Four or More Intraluminal Devices, Percutaneous Approach
        "037K3GZ",  # Dilation of Right Internal Carotid Artery with Four or More Intraluminal Devices, Percutaneous Approach
        "037K3Z6",  # Dilation of Right Internal Carotid Artery, Bifurcation, Percutaneous Approach
        "037K3ZZ",  # Dilation of Right Internal Carotid Artery, Percutaneous Approach
        "037K446",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Drug-eluting Intraluminal Device, Percutaneous Endoscopic Approach
        "037K44Z",  # Dilation of Right Internal Carotid Artery with Drug-eluting Intraluminal Device, Percutaneous Endoscopic Approach
        "037K456",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Two Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037K45Z",  # Dilation of Right Internal Carotid Artery with Two Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037K466",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Three Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037K46Z",  # Dilation of Right Internal Carotid Artery with Three Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037K476",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037K47Z",  # Dilation of Right Internal Carotid Artery with Four or More Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037K4D6",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Intraluminal Device, Percutaneous Endoscopic Approach
        "037K4DZ",  # Dilation of Right Internal Carotid Artery with Intraluminal Device, Percutaneous Endoscopic Approach
        "037K4E6",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Two Intraluminal Devices, Percutaneous Endoscopic Approach
        "037K4EZ",  # Dilation of Right Internal Carotid Artery with Two Intraluminal Devices, Percutaneous Endoscopic Approach
        "037K4F6",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Three Intraluminal Devices, Percutaneous Endoscopic Approach
        "037K4FZ",  # Dilation of Right Internal Carotid Artery with Three Intraluminal Devices, Percutaneous Endoscopic Approach
        "037K4G6",  # Dilation of Right Internal Carotid Artery, Bifurcation, with Four or More Intraluminal Devices, Percutaneous Endoscopic Approach
        "037K4GZ",  # Dilation of Right Internal Carotid Artery with Four or More Intraluminal Devices, Percutaneous Endoscopic Approach
        "037K4Z6",  # Dilation of Right Internal Carotid Artery, Bifurcation, Percutaneous Endoscopic Approach
        "037K4ZZ",  # Dilation of Right Internal Carotid Artery, Percutaneous Endoscopic Approach
        "037L046",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Drug-eluting Intraluminal Device, Open Approach
        "037L04Z",  # Dilation of Left Internal Carotid Artery with Drug-eluting Intraluminal Device, Open Approach
        "037L056",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Two Drug-eluting Intraluminal Devices, Open Approach
        "037L05Z",  # Dilation of Left Internal Carotid Artery with Two Drug-eluting Intraluminal Devices, Open Approach
        "037L066",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Three Drug-eluting Intraluminal Devices, Open Approach
        "037L06Z",  # Dilation of Left Internal Carotid Artery with Three Drug-eluting Intraluminal Devices, Open Approach
        "037L076",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Open Approach
        "037L07Z",  # Dilation of Left Internal Carotid Artery with Four or More Drug-eluting Intraluminal Devices, Open Approach
        "037L0D6",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Intraluminal Device, Open Approach
        "037L0DZ",  # Dilation of Left Internal Carotid Artery with Intraluminal Device, Open Approach
        "037L0E6",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Two Intraluminal Devices, Open Approach
        "037L0EZ",  # Dilation of Left Internal Carotid Artery with Two Intraluminal Devices, Open Approach
        "037L0F6",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Three Intraluminal Devices, Open Approach
        "037L0FZ",  # Dilation of Left Internal Carotid Artery with Three Intraluminal Devices, Open Approach
        "037L0G6",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Four or More Intraluminal Devices, Open Approach
        "037L0GZ",  # Dilation of Left Internal Carotid Artery with Four or More Intraluminal Devices, Open Approach
        "037L0Z6",  # Dilation of Left Internal Carotid Artery, Bifurcation, Open Approach
        "037L0ZZ",  # Dilation of Left Internal Carotid Artery, Open Approach
        "037L346",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Drug-eluting Intraluminal Device, Percutaneous Approach
        "037L34Z",  # Dilation of Left Internal Carotid Artery with Drug-eluting Intraluminal Device, Percutaneous Approach
        "037L356",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Two Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037L35Z",  # Dilation of Left Internal Carotid Artery with Two Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037L366",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Three Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037L36Z",  # Dilation of Left Internal Carotid Artery with Three Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037L376",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037L37Z",  # Dilation of Left Internal Carotid Artery with Four or More Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037L3D6",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Intraluminal Device, Percutaneous Approach
        "037L3DZ",  # Dilation of Left Internal Carotid Artery with Intraluminal Device, Percutaneous Approach
        "037L3E6",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Two Intraluminal Devices, Percutaneous Approach
        "037L3EZ",  # Dilation of Left Internal Carotid Artery with Two Intraluminal Devices, Percutaneous Approach
        "037L3F6",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Three Intraluminal Devices, Percutaneous Approach
        "037L3FZ",  # Dilation of Left Internal Carotid Artery with Three Intraluminal Devices, Percutaneous Approach
        "037L3G6",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Four or More Intraluminal Devices, Percutaneous Approach
        "037L3GZ",  # Dilation of Left Internal Carotid Artery with Four or More Intraluminal Devices, Percutaneous Approach
        "037L3Z6",  # Dilation of Left Internal Carotid Artery, Bifurcation, Percutaneous Approach
        "037L3ZZ",  # Dilation of Left Internal Carotid Artery, Percutaneous Approach
        "037L446",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Drug-eluting Intraluminal Device, Percutaneous Endoscopic Approach
        "037L44Z",  # Dilation of Left Internal Carotid Artery with Drug-eluting Intraluminal Device, Percutaneous Endoscopic Approach
        "037L456",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Two Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037L45Z",  # Dilation of Left Internal Carotid Artery with Two Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037L466",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Three Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037L46Z",  # Dilation of Left Internal Carotid Artery with Three Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037L476",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037L47Z",  # Dilation of Left Internal Carotid Artery with Four or More Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037L4D6",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Intraluminal Device, Percutaneous Endoscopic Approach
        "037L4DZ",  # Dilation of Left Internal Carotid Artery with Intraluminal Device, Percutaneous Endoscopic Approach
        "037L4E6",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Two Intraluminal Devices, Percutaneous Endoscopic Approach
        "037L4EZ",  # Dilation of Left Internal Carotid Artery with Two Intraluminal Devices, Percutaneous Endoscopic Approach
        "037L4F6",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Three Intraluminal Devices, Percutaneous Endoscopic Approach
        "037L4FZ",  # Dilation of Left Internal Carotid Artery with Three Intraluminal Devices, Percutaneous Endoscopic Approach
        "037L4G6",  # Dilation of Left Internal Carotid Artery, Bifurcation, with Four or More Intraluminal Devices, Percutaneous Endoscopic Approach
        "037L4GZ",  # Dilation of Left Internal Carotid Artery with Four or More Intraluminal Devices, Percutaneous Endoscopic Approach
        "037L4Z6",  # Dilation of Left Internal Carotid Artery, Bifurcation, Percutaneous Endoscopic Approach
        "037L4ZZ",  # Dilation of Left Internal Carotid Artery, Percutaneous Endoscopic Approach
        "037M046",  # Dilation of Right External Carotid Artery, Bifurcation, with Drug-eluting Intraluminal Device, Open Approach
        "037M04Z",  # Dilation of Right External Carotid Artery with Drug-eluting Intraluminal Device, Open Approach
        "037M056",  # Dilation of Right External Carotid Artery, Bifurcation, with Two Drug-eluting Intraluminal Devices, Open Approach
        "037M05Z",  # Dilation of Right External Carotid Artery with Two Drug-eluting Intraluminal Devices, Open Approach
        "037M066",  # Dilation of Right External Carotid Artery, Bifurcation, with Three Drug-eluting Intraluminal Devices, Open Approach
        "037M06Z",  # Dilation of Right External Carotid Artery with Three Drug-eluting Intraluminal Devices, Open Approach
        "037M076",  # Dilation of Right External Carotid Artery, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Open Approach
        "037M07Z",  # Dilation of Right External Carotid Artery with Four or More Drug-eluting Intraluminal Devices, Open Approach
        "037M0D6",  # Dilation of Right External Carotid Artery, Bifurcation, with Intraluminal Device, Open Approach
        "037M0DZ",  # Dilation of Right External Carotid Artery with Intraluminal Device, Open Approach
        "037M0E6",  # Dilation of Right External Carotid Artery, Bifurcation, with Two Intraluminal Devices, Open Approach
        "037M0EZ",  # Dilation of Right External Carotid Artery with Two Intraluminal Devices, Open Approach
        "037M0F6",  # Dilation of Right External Carotid Artery, Bifurcation, with Three Intraluminal Devices, Open Approach
        "037M0FZ",  # Dilation of Right External Carotid Artery with Three Intraluminal Devices, Open Approach
        "037M0G6",  # Dilation of Right External Carotid Artery, Bifurcation, with Four or More Intraluminal Devices, Open Approach
        "037M0GZ",  # Dilation of Right External Carotid Artery with Four or More Intraluminal Devices, Open Approach
        "037M0Z6",  # Dilation of Right External Carotid Artery, Bifurcation, Open Approach
        "037M0ZZ",  # Dilation of Right External Carotid Artery, Open Approach
        "037M346",  # Dilation of Right External Carotid Artery, Bifurcation, with Drug-eluting Intraluminal Device, Percutaneous Approach
        "037M34Z",  # Dilation of Right External Carotid Artery with Drug-eluting Intraluminal Device, Percutaneous Approach
        "037M356",  # Dilation of Right External Carotid Artery, Bifurcation, with Two Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037M35Z",  # Dilation of Right External Carotid Artery with Two Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037M366",  # Dilation of Right External Carotid Artery, Bifurcation, with Three Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037M36Z",  # Dilation of Right External Carotid Artery with Three Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037M376",  # Dilation of Right External Carotid Artery, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037M37Z",  # Dilation of Right External Carotid Artery with Four or More Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037M3D6",  # Dilation of Right External Carotid Artery, Bifurcation, with Intraluminal Device, Percutaneous Approach
        "037M3DZ",  # Dilation of Right External Carotid Artery with Intraluminal Device, Percutaneous Approach
        "037M3E6",  # Dilation of Right External Carotid Artery, Bifurcation, with Two Intraluminal Devices, Percutaneous Approach
        "037M3EZ",  # Dilation of Right External Carotid Artery with Two Intraluminal Devices, Percutaneous Approach
        "037M3F6",  # Dilation of Right External Carotid Artery, Bifurcation, with Three Intraluminal Devices, Percutaneous Approach
        "037M3FZ",  # Dilation of Right External Carotid Artery with Three Intraluminal Devices, Percutaneous Approach
        "037M3G6",  # Dilation of Right External Carotid Artery, Bifurcation, with Four or More Intraluminal Devices, Percutaneous Approach
        "037M3GZ",  # Dilation of Right External Carotid Artery with Four or More Intraluminal Devices, Percutaneous Approach
        "037M3Z6",  # Dilation of Right External Carotid Artery, Bifurcation, Percutaneous Approach
        "037M3ZZ",  # Dilation of Right External Carotid Artery, Percutaneous Approach
        "037M446",  # Dilation of Right External Carotid Artery, Bifurcation, with Drug-eluting Intraluminal Device, Percutaneous Endoscopic Approach
        "037M44Z",  # Dilation of Right External Carotid Artery with Drug-eluting Intraluminal Device, Percutaneous Endoscopic Approach
        "037M456",  # Dilation of Right External Carotid Artery, Bifurcation, with Two Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037M45Z",  # Dilation of Right External Carotid Artery with Two Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037M466",  # Dilation of Right External Carotid Artery, Bifurcation, with Three Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037M46Z",  # Dilation of Right External Carotid Artery with Three Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037M476",  # Dilation of Right External Carotid Artery, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037M47Z",  # Dilation of Right External Carotid Artery with Four or More Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037M4D6",  # Dilation of Right External Carotid Artery, Bifurcation, with Intraluminal Device, Percutaneous Endoscopic Approach
        "037M4DZ",  # Dilation of Right External Carotid Artery with Intraluminal Device, Percutaneous Endoscopic Approach
        "037M4E6",  # Dilation of Right External Carotid Artery, Bifurcation, with Two Intraluminal Devices, Percutaneous Endoscopic Approach
        "037M4EZ",  # Dilation of Right External Carotid Artery with Two Intraluminal Devices, Percutaneous Endoscopic Approach
        "037M4F6",  # Dilation of Right External Carotid Artery, Bifurcation, with Three Intraluminal Devices, Percutaneous Endoscopic Approach
        "037M4FZ",  # Dilation of Right External Carotid Artery with Three Intraluminal Devices, Percutaneous Endoscopic Approach
        "037M4G6",  # Dilation of Right External Carotid Artery, Bifurcation, with Four or More Intraluminal Devices, Percutaneous Endoscopic Approach
        "037M4GZ",  # Dilation of Right External Carotid Artery with Four or More Intraluminal Devices, Percutaneous Endoscopic Approach
        "037M4Z6",  # Dilation of Right External Carotid Artery, Bifurcation, Percutaneous Endoscopic Approach
        "037M4ZZ",  # Dilation of Right External Carotid Artery, Percutaneous Endoscopic Approach
        "037N046",  # Dilation of Left External Carotid Artery, Bifurcation, with Drug-eluting Intraluminal Device, Open Approach
        "037N04Z",  # Dilation of Left External Carotid Artery with Drug-eluting Intraluminal Device, Open Approach
        "037N056",  # Dilation of Left External Carotid Artery, Bifurcation, with Two Drug-eluting Intraluminal Devices, Open Approach
        "037N05Z",  # Dilation of Left External Carotid Artery with Two Drug-eluting Intraluminal Devices, Open Approach
        "037N066",  # Dilation of Left External Carotid Artery, Bifurcation, with Three Drug-eluting Intraluminal Devices, Open Approach
        "037N06Z",  # Dilation of Left External Carotid Artery with Three Drug-eluting Intraluminal Devices, Open Approach
        "037N076",  # Dilation of Left External Carotid Artery, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Open Approach
        "037N07Z",  # Dilation of Left External Carotid Artery with Four or More Drug-eluting Intraluminal Devices, Open Approach
        "037N0D6",  # Dilation of Left External Carotid Artery, Bifurcation, with Intraluminal Device, Open Approach
        "037N0DZ",  # Dilation of Left External Carotid Artery with Intraluminal Device, Open Approach
        "037N0E6",  # Dilation of Left External Carotid Artery, Bifurcation, with Two Intraluminal Devices, Open Approach
        "037N0EZ",  # Dilation of Left External Carotid Artery with Two Intraluminal Devices, Open Approach
        "037N0F6",  # Dilation of Left External Carotid Artery, Bifurcation, with Three Intraluminal Devices, Open Approach
        "037N0FZ",  # Dilation of Left External Carotid Artery with Three Intraluminal Devices, Open Approach
        "037N0G6",  # Dilation of Left External Carotid Artery, Bifurcation, with Four or More Intraluminal Devices, Open Approach
        "037N0GZ",  # Dilation of Left External Carotid Artery with Four or More Intraluminal Devices, Open Approach
        "037N0Z6",  # Dilation of Left External Carotid Artery, Bifurcation, Open Approach
        "037N0ZZ",  # Dilation of Left External Carotid Artery, Open Approach
        "037N346",  # Dilation of Left External Carotid Artery, Bifurcation, with Drug-eluting Intraluminal Device, Percutaneous Approach
        "037N34Z",  # Dilation of Left External Carotid Artery with Drug-eluting Intraluminal Device, Percutaneous Approach
        "037N356",  # Dilation of Left External Carotid Artery, Bifurcation, with Two Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037N35Z",  # Dilation of Left External Carotid Artery with Two Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037N366",  # Dilation of Left External Carotid Artery, Bifurcation, with Three Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037N36Z",  # Dilation of Left External Carotid Artery with Three Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037N376",  # Dilation of Left External Carotid Artery, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037N37Z",  # Dilation of Left External Carotid Artery with Four or More Drug-eluting Intraluminal Devices, Percutaneous Approach
        "037N3D6",  # Dilation of Left External Carotid Artery, Bifurcation, with Intraluminal Device, Percutaneous Approach
        "037N3DZ",  # Dilation of Left External Carotid Artery with Intraluminal Device, Percutaneous Approach
        "037N3E6",  # Dilation of Left External Carotid Artery, Bifurcation, with Two Intraluminal Devices, Percutaneous Approach
        "037N3EZ",  # Dilation of Left External Carotid Artery with Two Intraluminal Devices, Percutaneous Approach
        "037N3F6",  # Dilation of Left External Carotid Artery, Bifurcation, with Three Intraluminal Devices, Percutaneous Approach
        "037N3FZ",  # Dilation of Left External Carotid Artery with Three Intraluminal Devices, Percutaneous Approach
        "037N3G6",  # Dilation of Left External Carotid Artery, Bifurcation, with Four or More Intraluminal Devices, Percutaneous Approach
        "037N3GZ",  # Dilation of Left External Carotid Artery with Four or More Intraluminal Devices, Percutaneous Approach
        "037N3Z6",  # Dilation of Left External Carotid Artery, Bifurcation, Percutaneous Approach
        "037N3ZZ",  # Dilation of Left External Carotid Artery, Percutaneous Approach
        "037N446",  # Dilation of Left External Carotid Artery, Bifurcation, with Drug-eluting Intraluminal Device, Percutaneous Endoscopic Approach
        "037N44Z",  # Dilation of Left External Carotid Artery with Drug-eluting Intraluminal Device, Percutaneous Endoscopic Approach
        "037N456",  # Dilation of Left External Carotid Artery, Bifurcation, with Two Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037N45Z",  # Dilation of Left External Carotid Artery with Two Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037N466",  # Dilation of Left External Carotid Artery, Bifurcation, with Three Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037N46Z",  # Dilation of Left External Carotid Artery with Three Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037N476",  # Dilation of Left External Carotid Artery, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037N47Z",  # Dilation of Left External Carotid Artery with Four or More Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "037N4D6",  # Dilation of Left External Carotid Artery, Bifurcation, with Intraluminal Device, Percutaneous Endoscopic Approach
        "037N4DZ",  # Dilation of Left External Carotid Artery with Intraluminal Device, Percutaneous Endoscopic Approach
        "037N4E6",  # Dilation of Left External Carotid Artery, Bifurcation, with Two Intraluminal Devices, Percutaneous Endoscopic Approach
        "037N4EZ",  # Dilation of Left External Carotid Artery with Two Intraluminal Devices, Percutaneous Endoscopic Approach
        "037N4F6",  # Dilation of Left External Carotid Artery, Bifurcation, with Three Intraluminal Devices, Percutaneous Endoscopic Approach
        "037N4FZ",  # Dilation of Left External Carotid Artery with Three Intraluminal Devices, Percutaneous Endoscopic Approach
        "037N4G6",  # Dilation of Left External Carotid Artery, Bifurcation, with Four or More Intraluminal Devices, Percutaneous Endoscopic Approach
        "037N4GZ",  # Dilation of Left External Carotid Artery with Four or More Intraluminal Devices, Percutaneous Endoscopic Approach
        "037N4Z6",  # Dilation of Left External Carotid Artery, Bifurcation, Percutaneous Endoscopic Approach
        "037N4ZZ",  # Dilation of Left External Carotid Artery, Percutaneous Endoscopic Approach
        "039H00Z",  # Drainage of Right Common Carotid Artery with Drainage Device, Open Approach
        "039H0ZX",  # Drainage of Right Common Carotid Artery, Open Approach, Diagnostic
        "039H0ZZ",  # Drainage of Right Common Carotid Artery, Open Approach
        "039H30Z",  # Drainage of Right Common Carotid Artery with Drainage Device, Percutaneous Approach
        "039H3ZX",  # Drainage of Right Common Carotid Artery, Percutaneous Approach, Diagnostic
        "039H3ZZ",  # Drainage of Right Common Carotid Artery, Percutaneous Approach
        "039H40Z",  # Drainage of Right Common Carotid Artery with Drainage Device, Percutaneous Endoscopic Approach
        "039H4ZX",  # Drainage of Right Common Carotid Artery, Percutaneous Endoscopic Approach, Diagnostic
        "039H4ZZ",  # Drainage of Right Common Carotid Artery, Percutaneous Endoscopic Approach
        "039J00Z",  # Drainage of Left Common Carotid Artery with Drainage Device, Open Approach
        "039J0ZX",  # Drainage of Left Common Carotid Artery, Open Approach, Diagnostic
        "039J0ZZ",  # Drainage of Left Common Carotid Artery, Open Approach
        "039J30Z",  # Drainage of Left Common Carotid Artery with Drainage Device, Percutaneous Approach
        "039J3ZX",  # Drainage of Left Common Carotid Artery, Percutaneous Approach, Diagnostic
        "039J3ZZ",  # Drainage of Left Common Carotid Artery, Percutaneous Approach
        "039J40Z",  # Drainage of Left Common Carotid Artery with Drainage Device, Percutaneous Endoscopic Approach
        "039J4ZX",  # Drainage of Left Common Carotid Artery, Percutaneous Endoscopic Approach, Diagnostic
        "039J4ZZ",  # Drainage of Left Common Carotid Artery, Percutaneous Endoscopic Approach
        "039K00Z",  # Drainage of Right Internal Carotid Artery with Drainage Device, Open Approach
        "039K0ZX",  # Drainage of Right Internal Carotid Artery, Open Approach, Diagnostic
        "039K0ZZ",  # Drainage of Right Internal Carotid Artery, Open Approach
        "039K30Z",  # Drainage of Right Internal Carotid Artery with Drainage Device, Percutaneous Approach
        "039K3ZX",  # Drainage of Right Internal Carotid Artery, Percutaneous Approach, Diagnostic
        "039K3ZZ",  # Drainage of Right Internal Carotid Artery, Percutaneous Approach
        "039K40Z",  # Drainage of Right Internal Carotid Artery with Drainage Device, Percutaneous Endoscopic Approach
        "039K4ZX",  # Drainage of Right Internal Carotid Artery, Percutaneous Endoscopic Approach, Diagnostic
        "039K4ZZ",  # Drainage of Right Internal Carotid Artery, Percutaneous Endoscopic Approach
        "039L00Z",  # Drainage of Left Internal Carotid Artery with Drainage Device, Open Approach
        "039L0ZX",  # Drainage of Left Internal Carotid Artery, Open Approach, Diagnostic
        "039L0ZZ",  # Drainage of Left Internal Carotid Artery, Open Approach
        "039L30Z",  # Drainage of Left Internal Carotid Artery with Drainage Device, Percutaneous Approach
        "039L3ZX",  # Drainage of Left Internal Carotid Artery, Percutaneous Approach, Diagnostic
        "039L3ZZ",  # Drainage of Left Internal Carotid Artery, Percutaneous Approach
        "039L40Z",  # Drainage of Left Internal Carotid Artery with Drainage Device, Percutaneous Endoscopic Approach
        "039L4ZX",  # Drainage of Left Internal Carotid Artery, Percutaneous Endoscopic Approach, Diagnostic
        "039L4ZZ",  # Drainage of Left Internal Carotid Artery, Percutaneous Endoscopic Approach
        "039M00Z",  # Drainage of Right External Carotid Artery with Drainage Device, Open Approach
        "039M0ZX",  # Drainage of Right External Carotid Artery, Open Approach, Diagnostic
        "039M0ZZ",  # Drainage of Right External Carotid Artery, Open Approach
        "039M30Z",  # Drainage of Right External Carotid Artery with Drainage Device, Percutaneous Approach
        "039M3ZX",  # Drainage of Right External Carotid Artery, Percutaneous Approach, Diagnostic
        "039M3ZZ",  # Drainage of Right External Carotid Artery, Percutaneous Approach
        "039M40Z",  # Drainage of Right External Carotid Artery with Drainage Device, Percutaneous Endoscopic Approach
        "039M4ZX",  # Drainage of Right External Carotid Artery, Percutaneous Endoscopic Approach, Diagnostic
        "039M4ZZ",  # Drainage of Right External Carotid Artery, Percutaneous Endoscopic Approach
        "039N00Z",  # Drainage of Left External Carotid Artery with Drainage Device, Open Approach
        "039N0ZX",  # Drainage of Left External Carotid Artery, Open Approach, Diagnostic
        "039N0ZZ",  # Drainage of Left External Carotid Artery, Open Approach
        "039N30Z",  # Drainage of Left External Carotid Artery with Drainage Device, Percutaneous Approach
        "039N3ZX",  # Drainage of Left External Carotid Artery, Percutaneous Approach, Diagnostic
        "039N3ZZ",  # Drainage of Left External Carotid Artery, Percutaneous Approach
        "039N40Z",  # Drainage of Left External Carotid Artery with Drainage Device, Percutaneous Endoscopic Approach
        "039N4ZX",  # Drainage of Left External Carotid Artery, Percutaneous Endoscopic Approach, Diagnostic
        "039N4ZZ",  # Drainage of Left External Carotid Artery, Percutaneous Endoscopic Approach
        "03BH0ZX",  # Excision of Right Common Carotid Artery, Open Approach, Diagnostic
        "03BH0ZZ",  # Excision of Right Common Carotid Artery, Open Approach
        "03BH3ZX",  # Excision of Right Common Carotid Artery, Percutaneous Approach, Diagnostic
        "03BH3ZZ",  # Excision of Right Common Carotid Artery, Percutaneous Approach
        "03BH4ZX",  # Excision of Right Common Carotid Artery, Percutaneous Endoscopic Approach, Diagnostic
        "03BH4ZZ",  # Excision of Right Common Carotid Artery, Percutaneous Endoscopic Approach
        "03BJ0ZX",  # Excision of Left Common Carotid Artery, Open Approach, Diagnostic
        "03BJ0ZZ",  # Excision of Left Common Carotid Artery, Open Approach
        "03BJ3ZX",  # Excision of Left Common Carotid Artery, Percutaneous Approach, Diagnostic
        "03BJ3ZZ",  # Excision of Left Common Carotid Artery, Percutaneous Approach
        "03BJ4ZX",  # Excision of Left Common Carotid Artery, Percutaneous Endoscopic Approach, Diagnostic
        "03BJ4ZZ",  # Excision of Left Common Carotid Artery, Percutaneous Endoscopic Approach
        "03BK0ZX",  # Excision of Right Internal Carotid Artery, Open Approach, Diagnostic
        "03BK0ZZ",  # Excision of Right Internal Carotid Artery, Open Approach
        "03BK3ZX",  # Excision of Right Internal Carotid Artery, Percutaneous Approach, Diagnostic
        "03BK3ZZ",  # Excision of Right Internal Carotid Artery, Percutaneous Approach
        "03BK4ZX",  # Excision of Right Internal Carotid Artery, Percutaneous Endoscopic Approach, Diagnostic
        "03BK4ZZ",  # Excision of Right Internal Carotid Artery, Percutaneous Endoscopic Approach
        "03BL0ZX",  # Excision of Left Internal Carotid Artery, Open Approach, Diagnostic
        "03BL0ZZ",  # Excision of Left Internal Carotid Artery, Open Approach
        "03BL3ZX",  # Excision of Left Internal Carotid Artery, Percutaneous Approach, Diagnostic
        "03BL3ZZ",  # Excision of Left Internal Carotid Artery, Percutaneous Approach
        "03BL4ZX",  # Excision of Left Internal Carotid Artery, Percutaneous Endoscopic Approach, Diagnostic
        "03BL4ZZ",  # Excision of Left Internal Carotid Artery, Percutaneous Endoscopic Approach
        "03BM0ZX",  # Excision of Right External Carotid Artery, Open Approach, Diagnostic
        "03BM0ZZ",  # Excision of Right External Carotid Artery, Open Approach
        "03BM3ZX",  # Excision of Right External Carotid Artery, Percutaneous Approach, Diagnostic
        "03BM3ZZ",  # Excision of Right External Carotid Artery, Percutaneous Approach
        "03BM4ZX",  # Excision of Right External Carotid Artery, Percutaneous Endoscopic Approach, Diagnostic
        "03BM4ZZ",  # Excision of Right External Carotid Artery, Percutaneous Endoscopic Approach
        "03BN0ZX",  # Excision of Left External Carotid Artery, Open Approach, Diagnostic
        "03BN0ZZ",  # Excision of Left External Carotid Artery, Open Approach
        "03BN3ZX",  # Excision of Left External Carotid Artery, Percutaneous Approach, Diagnostic
        "03BN3ZZ",  # Excision of Left External Carotid Artery, Percutaneous Approach
        "03BN4ZX",  # Excision of Left External Carotid Artery, Percutaneous Endoscopic Approach, Diagnostic
        "03BN4ZZ",  # Excision of Left External Carotid Artery, Percutaneous Endoscopic Approach
        "03CH0Z6",  # Extirpation of Matter from Right Common Carotid Artery, Bifurcation, Open Approach
        "03CH0ZZ",  # Extirpation of Matter from Right Common Carotid Artery, Open Approach
        "03CH3Z6",  # Extirpation of Matter from Right Common Carotid Artery, Bifurcation, Percutaneous Approach
        "03CH3Z7",  # Extirpation of Matter from Right Common Carotid Artery using Stent Retriever, Percutaneous Approach
        "03CH3ZZ",  # Extirpation of Matter from Right Common Carotid Artery, Percutaneous Approach
        "03CH4Z6",  # Extirpation of Matter from Right Common Carotid Artery, Bifurcation, Percutaneous Endoscopic Approach
        "03CH4ZZ",  # Extirpation of Matter from Right Common Carotid Artery, Percutaneous Endoscopic Approach
        "03CJ0Z6",  # Extirpation of Matter from Left Common Carotid Artery, Bifurcation, Open Approach
        "03CJ0ZZ",  # Extirpation of Matter from Left Common Carotid Artery, Open Approach
        "03CJ3Z6",  # Extirpation of Matter from Left Common Carotid Artery, Bifurcation, Percutaneous Approach
        "03CJ3Z7",  # Extirpation of Matter from Left Common Carotid Artery using Stent Retriever, Percutaneous Approach
        "03CJ3ZZ",  # Extirpation of Matter from Left Common Carotid Artery, Percutaneous Approach
        "03CJ4Z6",  # Extirpation of Matter from Left Common Carotid Artery, Bifurcation, Percutaneous Endoscopic Approach
        "03CJ4ZZ",  # Extirpation of Matter from Left Common Carotid Artery, Percutaneous Endoscopic Approach
        "03CK0Z6",  # Extirpation of Matter from Right Internal Carotid Artery, Bifurcation, Open Approach
        "03CK0ZZ",  # Extirpation of Matter from Right Internal Carotid Artery, Open Approach
        "03CK3Z6",  # Extirpation of Matter from Right Internal Carotid Artery, Bifurcation, Percutaneous Approach
        "03CK3Z7",  # Extirpation of Matter from Right Internal Carotid Artery using Stent Retriever, Percutaneous Approach
        "03CK3ZZ",  # Extirpation of Matter from Right Internal Carotid Artery, Percutaneous Approach
        "03CK4Z6",  # Extirpation of Matter from Right Internal Carotid Artery, Bifurcation, Percutaneous Endoscopic Approach
        "03CK4ZZ",  # Extirpation of Matter from Right Internal Carotid Artery, Percutaneous Endoscopic Approach
        "03CL0Z6",  # Extirpation of Matter from Left Internal Carotid Artery, Bifurcation, Open Approach
        "03CL0ZZ",  # Extirpation of Matter from Left Internal Carotid Artery, Open Approach
        "03CL3Z6",  # Extirpation of Matter from Left Internal Carotid Artery, Bifurcation, Percutaneous Approach
        "03CL3Z7",  # Extirpation of Matter from Left Internal Carotid Artery using Stent Retriever, Percutaneous Approach
        "03CL3ZZ",  # Extirpation of Matter from Left Internal Carotid Artery, Percutaneous Approach
        "03CL4Z6",  # Extirpation of Matter from Left Internal Carotid Artery, Bifurcation, Percutaneous Endoscopic Approach
        "03CL4ZZ",  # Extirpation of Matter from Left Internal Carotid Artery, Percutaneous Endoscopic Approach
        "03CM0Z6",  # Extirpation of Matter from Right External Carotid Artery, Bifurcation, Open Approach
        "03CM0ZZ",  # Extirpation of Matter from Right External Carotid Artery, Open Approach
        "03CM3Z6",  # Extirpation of Matter from Right External Carotid Artery, Bifurcation, Percutaneous Approach
        "03CM3Z7",  # Extirpation of Matter from Right External Carotid Artery using Stent Retriever, Percutaneous Approach
        "03CM3ZZ",  # Extirpation of Matter from Right External Carotid Artery, Percutaneous Approach
        "03CM4Z6",  # Extirpation of Matter from Right External Carotid Artery, Bifurcation, Percutaneous Endoscopic Approach
        "03CM4ZZ",  # Extirpation of Matter from Right External Carotid Artery, Percutaneous Endoscopic Approach
        "03CN0Z6",  # Extirpation of Matter from Left External Carotid Artery, Bifurcation, Open Approach
        "03CN0ZZ",  # Extirpation of Matter from Left External Carotid Artery, Open Approach
        "03CN3Z6",  # Extirpation of Matter from Left External Carotid Artery, Bifurcation, Percutaneous Approach
        "03CN3Z7",  # Extirpation of Matter from Left External Carotid Artery using Stent Retriever, Percutaneous Approach
        "03CN3ZZ",  # Extirpation of Matter from Left External Carotid Artery, Percutaneous Approach
        "03CN4Z6",  # Extirpation of Matter from Left External Carotid Artery, Bifurcation, Percutaneous Endoscopic Approach
        "03CN4ZZ",  # Extirpation of Matter from Left External Carotid Artery, Percutaneous Endoscopic Approach
        "03HH03Z",  # Insertion of Infusion Device into Right Common Carotid Artery, Open Approach
        "03HH0DZ",  # Insertion of Intraluminal Device into Right Common Carotid Artery, Open Approach
        "03HH33Z",  # Insertion of Infusion Device into Right Common Carotid Artery, Percutaneous Approach
        "03HH3DZ",  # Insertion of Intraluminal Device into Right Common Carotid Artery, Percutaneous Approach
        "03HH43Z",  # Insertion of Infusion Device into Right Common Carotid Artery, Percutaneous Endoscopic Approach
        "03HH4DZ",  # Insertion of Intraluminal Device into Right Common Carotid Artery, Percutaneous Endoscopic Approach
        "03HJ03Z",  # Insertion of Infusion Device into Left Common Carotid Artery, Open Approach
        "03HJ0DZ",  # Insertion of Intraluminal Device into Left Common Carotid Artery, Open Approach
        "03HJ33Z",  # Insertion of Infusion Device into Left Common Carotid Artery, Percutaneous Approach
        "03HJ3DZ",  # Insertion of Intraluminal Device into Left Common Carotid Artery, Percutaneous Approach
        "03HJ43Z",  # Insertion of Infusion Device into Left Common Carotid Artery, Percutaneous Endoscopic Approach
        "03HJ4DZ",  # Insertion of Intraluminal Device into Left Common Carotid Artery, Percutaneous Endoscopic Approach
        "03HK03Z",  # Insertion of Infusion Device into Right Internal Carotid Artery, Open Approach
        "03HK0DZ",  # Insertion of Intraluminal Device into Right Internal Carotid Artery, Open Approach
        "03HK0MZ",  # Insertion of Stimulator Lead into Right Internal Carotid Artery, Open Approach
        "03HK33Z",  # Insertion of Infusion Device into Right Internal Carotid Artery, Percutaneous Approach
        "03HK3DZ",  # Insertion of Intraluminal Device into Right Internal Carotid Artery, Percutaneous Approach
        "03HK3MZ",  # Insertion of Stimulator Lead into Right Internal Carotid Artery, Percutaneous Approach
        "03HK43Z",  # Insertion of Infusion Device into Right Internal Carotid Artery, Percutaneous Endoscopic Approach
        "03HK4DZ",  # Insertion of Intraluminal Device into Right Internal Carotid Artery, Percutaneous Endoscopic Approach
        "03HK4MZ",  # Insertion of Stimulator Lead into Right Internal Carotid Artery, Percutaneous Endoscopic Approach
        "03HL03Z",  # Insertion of Infusion Device into Left Internal Carotid Artery, Open Approach
        "03HL0DZ",  # Insertion of Intraluminal Device into Left Internal Carotid Artery, Open Approach
        "03HL0MZ",  # Insertion of Stimulator Lead into Left Internal Carotid Artery, Open Approach
        "03HL33Z",  # Insertion of Infusion Device into Left Internal Carotid Artery, Percutaneous Approach
        "03HL3DZ",  # Insertion of Intraluminal Device into Left Internal Carotid Artery, Percutaneous Approach
        "03HL3MZ",  # Insertion of Stimulator Lead into Left Internal Carotid Artery, Percutaneous Approach
        "03HL43Z",  # Insertion of Infusion Device into Left Internal Carotid Artery, Percutaneous Endoscopic Approach
        "03HL4DZ",  # Insertion of Intraluminal Device into Left Internal Carotid Artery, Percutaneous Endoscopic Approach
        "03HL4MZ",  # Insertion of Stimulator Lead into Left Internal Carotid Artery, Percutaneous Endoscopic Approach
        "03HM03Z",  # Insertion of Infusion Device into Right External Carotid Artery, Open Approach
        "03HM0DZ",  # Insertion of Intraluminal Device into Right External Carotid Artery, Open Approach
        "03HM33Z",  # Insertion of Infusion Device into Right External Carotid Artery, Percutaneous Approach
        "03HM3DZ",  # Insertion of Intraluminal Device into Right External Carotid Artery, Percutaneous Approach
        "03HM43Z",  # Insertion of Infusion Device into Right External Carotid Artery, Percutaneous Endoscopic Approach
        "03HM4DZ",  # Insertion of Intraluminal Device into Right External Carotid Artery, Percutaneous Endoscopic Approach
        "03HN03Z",  # Insertion of Infusion Device into Left External Carotid Artery, Open Approach
        "03HN0DZ",  # Insertion of Intraluminal Device into Left External Carotid Artery, Open Approach
        "03HN33Z",  # Insertion of Infusion Device into Left External Carotid Artery, Percutaneous Approach
        "03HN3DZ",  # Insertion of Intraluminal Device into Left External Carotid Artery, Percutaneous Approach
        "03HN43Z",  # Insertion of Infusion Device into Left External Carotid Artery, Percutaneous Endoscopic Approach
        "03HN4DZ",  # Insertion of Intraluminal Device into Left External Carotid Artery, Percutaneous Endoscopic Approach
        "03LH0BZ",  # Occlusion of Right Common Carotid Artery with Bioactive Intraluminal Device, Open Approach
        "03LH0CZ",  # Occlusion of Right Common Carotid Artery with Extraluminal Device, Open Approach
        "03LH0DZ",  # Occlusion of Right Common Carotid Artery with Intraluminal Device, Open Approach
        "03LH0ZZ",  # Occlusion of Right Common Carotid Artery, Open Approach
        "03LH3BZ",  # Occlusion of Right Common Carotid Artery with Bioactive Intraluminal Device, Percutaneous Approach
        "03LH3CZ",  # Occlusion of Right Common Carotid Artery with Extraluminal Device, Percutaneous Approach
        "03LH3DZ",  # Occlusion of Right Common Carotid Artery with Intraluminal Device, Percutaneous Approach
        "03LH3ZZ",  # Occlusion of Right Common Carotid Artery, Percutaneous Approach
        "03LH4BZ",  # Occlusion of Right Common Carotid Artery with Bioactive Intraluminal Device, Percutaneous Endoscopic Approach
        "03LH4CZ",  # Occlusion of Right Common Carotid Artery with Extraluminal Device, Percutaneous Endoscopic Approach
        "03LH4DZ",  # Occlusion of Right Common Carotid Artery with Intraluminal Device, Percutaneous Endoscopic Approach
        "03LH4ZZ",  # Occlusion of Right Common Carotid Artery, Percutaneous Endoscopic Approach
        "03LJ0BZ",  # Occlusion of Left Common Carotid Artery with Bioactive Intraluminal Device, Open Approach
        "03LJ0CZ",  # Occlusion of Left Common Carotid Artery with Extraluminal Device, Open Approach
        "03LJ0DZ",  # Occlusion of Left Common Carotid Artery with Intraluminal Device, Open Approach
        "03LJ0ZZ",  # Occlusion of Left Common Carotid Artery, Open Approach
        "03LJ3BZ",  # Occlusion of Left Common Carotid Artery with Bioactive Intraluminal Device, Percutaneous Approach
        "03LJ3CZ",  # Occlusion of Left Common Carotid Artery with Extraluminal Device, Percutaneous Approach
        "03LJ3DZ",  # Occlusion of Left Common Carotid Artery with Intraluminal Device, Percutaneous Approach
        "03LJ3ZZ",  # Occlusion of Left Common Carotid Artery, Percutaneous Approach
        "03LJ4BZ",  # Occlusion of Left Common Carotid Artery with Bioactive Intraluminal Device, Percutaneous Endoscopic Approach
        "03LJ4CZ",  # Occlusion of Left Common Carotid Artery with Extraluminal Device, Percutaneous Endoscopic Approach
        "03LJ4DZ",  # Occlusion of Left Common Carotid Artery with Intraluminal Device, Percutaneous Endoscopic Approach
        "03LJ4ZZ",  # Occlusion of Left Common Carotid Artery, Percutaneous Endoscopic Approach
        "03LK0BZ",  # Occlusion of Right Internal Carotid Artery with Bioactive Intraluminal Device, Open Approach
        "03LK0CZ",  # Occlusion of Right Internal Carotid Artery with Extraluminal Device, Open Approach
        "03LK0DZ",  # Occlusion of Right Internal Carotid Artery with Intraluminal Device, Open Approach
        "03LK0ZZ",  # Occlusion of Right Internal Carotid Artery, Open Approach
        "03LK3BZ",  # Occlusion of Right Internal Carotid Artery with Bioactive Intraluminal Device, Percutaneous Approach
        "03LK3CZ",  # Occlusion of Right Internal Carotid Artery with Extraluminal Device, Percutaneous Approach
        "03LK3DZ",  # Occlusion of Right Internal Carotid Artery with Intraluminal Device, Percutaneous Approach
        "03LK3ZZ",  # Occlusion of Right Internal Carotid Artery, Percutaneous Approach
        "03LK4BZ",  # Occlusion of Right Internal Carotid Artery with Bioactive Intraluminal Device, Percutaneous Endoscopic Approach
        "03LK4CZ",  # Occlusion of Right Internal Carotid Artery with Extraluminal Device, Percutaneous Endoscopic Approach
        "03LK4DZ",  # Occlusion of Right Internal Carotid Artery with Intraluminal Device, Percutaneous Endoscopic Approach
        "03LK4ZZ",  # Occlusion of Right Internal Carotid Artery, Percutaneous Endoscopic Approach
        "03LL0BZ",  # Occlusion of Left Internal Carotid Artery with Bioactive Intraluminal Device, Open Approach
        "03LL0CZ",  # Occlusion of Left Internal Carotid Artery with Extraluminal Device, Open Approach
        "03LL0DZ",  # Occlusion of Left Internal Carotid Artery with Intraluminal Device, Open Approach
        "03LL0ZZ",  # Occlusion of Left Internal Carotid Artery, Open Approach
        "03LL3BZ",  # Occlusion of Left Internal Carotid Artery with Bioactive Intraluminal Device, Percutaneous Approach
        "03LL3CZ",  # Occlusion of Left Internal Carotid Artery with Extraluminal Device, Percutaneous Approach
        "03LL3DZ",  # Occlusion of Left Internal Carotid Artery with Intraluminal Device, Percutaneous Approach
        "03LL3ZZ",  # Occlusion of Left Internal Carotid Artery, Percutaneous Approach
        "03LL4BZ",  # Occlusion of Left Internal Carotid Artery with Bioactive Intraluminal Device, Percutaneous Endoscopic Approach
        "03LL4CZ",  # Occlusion of Left Internal Carotid Artery with Extraluminal Device, Percutaneous Endoscopic Approach
        "03LL4DZ",  # Occlusion of Left Internal Carotid Artery with Intraluminal Device, Percutaneous Endoscopic Approach
        "03LL4ZZ",  # Occlusion of Left Internal Carotid Artery, Percutaneous Endoscopic Approach
        "03LM0BZ",  # Occlusion of Right External Carotid Artery with Bioactive Intraluminal Device, Open Approach
        "03LM0CZ",  # Occlusion of Right External Carotid Artery with Extraluminal Device, Open Approach
        "03LM0DZ",  # Occlusion of Right External Carotid Artery with Intraluminal Device, Open Approach
        "03LM0ZZ",  # Occlusion of Right External Carotid Artery, Open Approach
        "03LM3BZ",  # Occlusion of Right External Carotid Artery with Bioactive Intraluminal Device, Percutaneous Approach
        "03LM3CZ",  # Occlusion of Right External Carotid Artery with Extraluminal Device, Percutaneous Approach
        "03LM3DZ",  # Occlusion of Right External Carotid Artery with Intraluminal Device, Percutaneous Approach
        "03LM3ZZ",  # Occlusion of Right External Carotid Artery, Percutaneous Approach
        "03LM4BZ",  # Occlusion of Right External Carotid Artery with Bioactive Intraluminal Device, Percutaneous Endoscopic Approach
        "03LM4CZ",  # Occlusion of Right External Carotid Artery with Extraluminal Device, Percutaneous Endoscopic Approach
        "03LM4DZ",  # Occlusion of Right External Carotid Artery with Intraluminal Device, Percutaneous Endoscopic Approach
        "03LM4ZZ",  # Occlusion of Right External Carotid Artery, Percutaneous Endoscopic Approach
        "03LN0BZ",  # Occlusion of Left External Carotid Artery with Bioactive Intraluminal Device, Open Approach
        "03LN0CZ",  # Occlusion of Left External Carotid Artery with Extraluminal Device, Open Approach
        "03LN0DZ",  # Occlusion of Left External Carotid Artery with Intraluminal Device, Open Approach
        "03LN0ZZ",  # Occlusion of Left External Carotid Artery, Open Approach
        "03LN3BZ",  # Occlusion of Left External Carotid Artery with Bioactive Intraluminal Device, Percutaneous Approach
        "03LN3CZ",  # Occlusion of Left External Carotid Artery with Extraluminal Device, Percutaneous Approach
        "03LN3DZ",  # Occlusion of Left External Carotid Artery with Intraluminal Device, Percutaneous Approach
        "03LN3ZZ",  # Occlusion of Left External Carotid Artery, Percutaneous Approach
        "03LN4BZ",  # Occlusion of Left External Carotid Artery with Bioactive Intraluminal Device, Percutaneous Endoscopic Approach
        "03LN4CZ",  # Occlusion of Left External Carotid Artery with Extraluminal Device, Percutaneous Endoscopic Approach
        "03LN4DZ",  # Occlusion of Left External Carotid Artery with Intraluminal Device, Percutaneous Endoscopic Approach
        "03LN4ZZ",  # Occlusion of Left External Carotid Artery, Percutaneous Endoscopic Approach
        "03NH0ZZ",  # Release Right Common Carotid Artery, Open Approach
        "03NH3ZZ",  # Release Right Common Carotid Artery, Percutaneous Approach
        "03NH4ZZ",  # Release Right Common Carotid Artery, Percutaneous Endoscopic Approach
        "03NJ0ZZ",  # Release Left Common Carotid Artery, Open Approach
        "03NJ3ZZ",  # Release Left Common Carotid Artery, Percutaneous Approach
        "03NJ4ZZ",  # Release Left Common Carotid Artery, Percutaneous Endoscopic Approach
        "03NK0ZZ",  # Release Right Internal Carotid Artery, Open Approach
        "03NK3ZZ",  # Release Right Internal Carotid Artery, Percutaneous Approach
        "03NK4ZZ",  # Release Right Internal Carotid Artery, Percutaneous Endoscopic Approach
        "03NL0ZZ",  # Release Left Internal Carotid Artery, Open Approach
        "03NL3ZZ",  # Release Left Internal Carotid Artery, Percutaneous Approach
        "03NL4ZZ",  # Release Left Internal Carotid Artery, Percutaneous Endoscopic Approach
        "03NM0ZZ",  # Release Right External Carotid Artery, Open Approach
        "03NM3ZZ",  # Release Right External Carotid Artery, Percutaneous Approach
        "03NM4ZZ",  # Release Right External Carotid Artery, Percutaneous Endoscopic Approach
        "03NN0ZZ",  # Release Left External Carotid Artery, Open Approach
        "03NN3ZZ",  # Release Left External Carotid Artery, Percutaneous Approach
        "03NN4ZZ",  # Release Left External Carotid Artery, Percutaneous Endoscopic Approach
        "03QH0ZZ",  # Repair Right Common Carotid Artery, Open Approach
        "03QH3ZZ",  # Repair Right Common Carotid Artery, Percutaneous Approach
        "03QH4ZZ",  # Repair Right Common Carotid Artery, Percutaneous Endoscopic Approach
        "03QJ0ZZ",  # Repair Left Common Carotid Artery, Open Approach
        "03QJ3ZZ",  # Repair Left Common Carotid Artery, Percutaneous Approach
        "03QJ4ZZ",  # Repair Left Common Carotid Artery, Percutaneous Endoscopic Approach
        "03QK0ZZ",  # Repair Right Internal Carotid Artery, Open Approach
        "03QK3ZZ",  # Repair Right Internal Carotid Artery, Percutaneous Approach
        "03QK4ZZ",  # Repair Right Internal Carotid Artery, Percutaneous Endoscopic Approach
        "03QL0ZZ",  # Repair Left Internal Carotid Artery, Open Approach
        "03QL3ZZ",  # Repair Left Internal Carotid Artery, Percutaneous Approach
        "03QL4ZZ",  # Repair Left Internal Carotid Artery, Percutaneous Endoscopic Approach
        "03QM0ZZ",  # Repair Right External Carotid Artery, Open Approach
        "03QM3ZZ",  # Repair Right External Carotid Artery, Percutaneous Approach
        "03QM4ZZ",  # Repair Right External Carotid Artery, Percutaneous Endoscopic Approach
        "03QN0ZZ",  # Repair Left External Carotid Artery, Open Approach
        "03QN3ZZ",  # Repair Left External Carotid Artery, Percutaneous Approach
        "03QN4ZZ",  # Repair Left External Carotid Artery, Percutaneous Endoscopic Approach
        "03RH07Z",  # Replacement of Right Common Carotid Artery with Autologous Tissue Substitute, Open Approach
        "03RH0JZ",  # Replacement of Right Common Carotid Artery with Synthetic Substitute, Open Approach
        "03RH0KZ",  # Replacement of Right Common Carotid Artery with Nonautologous Tissue Substitute, Open Approach
        "03RH47Z",  # Replacement of Right Common Carotid Artery with Autologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03RH4JZ",  # Replacement of Right Common Carotid Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "03RH4KZ",  # Replacement of Right Common Carotid Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03RJ07Z",  # Replacement of Left Common Carotid Artery with Autologous Tissue Substitute, Open Approach
        "03RJ0JZ",  # Replacement of Left Common Carotid Artery with Synthetic Substitute, Open Approach
        "03RJ0KZ",  # Replacement of Left Common Carotid Artery with Nonautologous Tissue Substitute, Open Approach
        "03RJ47Z",  # Replacement of Left Common Carotid Artery with Autologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03RJ4JZ",  # Replacement of Left Common Carotid Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "03RJ4KZ",  # Replacement of Left Common Carotid Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03RK07Z",  # Replacement of Right Internal Carotid Artery with Autologous Tissue Substitute, Open Approach
        "03RK0JZ",  # Replacement of Right Internal Carotid Artery with Synthetic Substitute, Open Approach
        "03RK0KZ",  # Replacement of Right Internal Carotid Artery with Nonautologous Tissue Substitute, Open Approach
        "03RK47Z",  # Replacement of Right Internal Carotid Artery with Autologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03RK4JZ",  # Replacement of Right Internal Carotid Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "03RK4KZ",  # Replacement of Right Internal Carotid Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03RL07Z",  # Replacement of Left Internal Carotid Artery with Autologous Tissue Substitute, Open Approach
        "03RL0JZ",  # Replacement of Left Internal Carotid Artery with Synthetic Substitute, Open Approach
        "03RL0KZ",  # Replacement of Left Internal Carotid Artery with Nonautologous Tissue Substitute, Open Approach
        "03RL47Z",  # Replacement of Left Internal Carotid Artery with Autologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03RL4JZ",  # Replacement of Left Internal Carotid Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "03RL4KZ",  # Replacement of Left Internal Carotid Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03RM07Z",  # Replacement of Right External Carotid Artery with Autologous Tissue Substitute, Open Approach
        "03RM0JZ",  # Replacement of Right External Carotid Artery with Synthetic Substitute, Open Approach
        "03RM0KZ",  # Replacement of Right External Carotid Artery with Nonautologous Tissue Substitute, Open Approach
        "03RM47Z",  # Replacement of Right External Carotid Artery with Autologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03RM4JZ",  # Replacement of Right External Carotid Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "03RM4KZ",  # Replacement of Right External Carotid Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03RN07Z",  # Replacement of Left External Carotid Artery with Autologous Tissue Substitute, Open Approach
        "03RN0JZ",  # Replacement of Left External Carotid Artery with Synthetic Substitute, Open Approach
        "03RN0KZ",  # Replacement of Left External Carotid Artery with Nonautologous Tissue Substitute, Open Approach
        "03RN47Z",  # Replacement of Left External Carotid Artery with Autologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03RN4JZ",  # Replacement of Left External Carotid Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "03RN4KZ",  # Replacement of Left External Carotid Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03SH0ZZ",  # Reposition Right Common Carotid Artery, Open Approach
        "03SH3ZZ",  # Reposition Right Common Carotid Artery, Percutaneous Approach
        "03SH4ZZ",  # Reposition Right Common Carotid Artery, Percutaneous Endoscopic Approach
        "03SJ0ZZ",  # Reposition Left Common Carotid Artery, Open Approach
        "03SJ3ZZ",  # Reposition Left Common Carotid Artery, Percutaneous Approach
        "03SJ4ZZ",  # Reposition Left Common Carotid Artery, Percutaneous Endoscopic Approach
        "03SK0ZZ",  # Reposition Right Internal Carotid Artery, Open Approach
        "03SK3ZZ",  # Reposition Right Internal Carotid Artery, Percutaneous Approach
        "03SK4ZZ",  # Reposition Right Internal Carotid Artery, Percutaneous Endoscopic Approach
        "03SL0ZZ",  # Reposition Left Internal Carotid Artery, Open Approach
        "03SL3ZZ",  # Reposition Left Internal Carotid Artery, Percutaneous Approach
        "03SL4ZZ",  # Reposition Left Internal Carotid Artery, Percutaneous Endoscopic Approach
        "03SM0ZZ",  # Reposition Right External Carotid Artery, Open Approach
        "03SM3ZZ",  # Reposition Right External Carotid Artery, Percutaneous Approach
        "03SM4ZZ",  # Reposition Right External Carotid Artery, Percutaneous Endoscopic Approach
        "03SN0ZZ",  # Reposition Left External Carotid Artery, Open Approach
        "03SN3ZZ",  # Reposition Left External Carotid Artery, Percutaneous Approach
        "03SN4ZZ",  # Reposition Left External Carotid Artery, Percutaneous Endoscopic Approach
        "03UH07Z",  # Supplement Right Common Carotid Artery with Autologous Tissue Substitute, Open Approach
        "03UH0JZ",  # Supplement Right Common Carotid Artery with Synthetic Substitute, Open Approach
        "03UH0KZ",  # Supplement Right Common Carotid Artery with Nonautologous Tissue Substitute, Open Approach
        "03UH37Z",  # Supplement Right Common Carotid Artery with Autologous Tissue Substitute, Percutaneous Approach
        "03UH3JZ",  # Supplement Right Common Carotid Artery with Synthetic Substitute, Percutaneous Approach
        "03UH3KZ",  # Supplement Right Common Carotid Artery with Nonautologous Tissue Substitute, Percutaneous Approach
        "03UH47Z",  # Supplement Right Common Carotid Artery with Autologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03UH4JZ",  # Supplement Right Common Carotid Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "03UH4KZ",  # Supplement Right Common Carotid Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03UJ07Z",  # Supplement Left Common Carotid Artery with Autologous Tissue Substitute, Open Approach
        "03UJ0JZ",  # Supplement Left Common Carotid Artery with Synthetic Substitute, Open Approach
        "03UJ0KZ",  # Supplement Left Common Carotid Artery with Nonautologous Tissue Substitute, Open Approach
        "03UJ37Z",  # Supplement Left Common Carotid Artery with Autologous Tissue Substitute, Percutaneous Approach
        "03UJ3JZ",  # Supplement Left Common Carotid Artery with Synthetic Substitute, Percutaneous Approach
        "03UJ3KZ",  # Supplement Left Common Carotid Artery with Nonautologous Tissue Substitute, Percutaneous Approach
        "03UJ47Z",  # Supplement Left Common Carotid Artery with Autologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03UJ4JZ",  # Supplement Left Common Carotid Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "03UJ4KZ",  # Supplement Left Common Carotid Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03UK07Z",  # Supplement Right Internal Carotid Artery with Autologous Tissue Substitute, Open Approach
        "03UK0JZ",  # Supplement Right Internal Carotid Artery with Synthetic Substitute, Open Approach
        "03UK0KZ",  # Supplement Right Internal Carotid Artery with Nonautologous Tissue Substitute, Open Approach
        "03UK37Z",  # Supplement Right Internal Carotid Artery with Autologous Tissue Substitute, Percutaneous Approach
        "03UK3JZ",  # Supplement Right Internal Carotid Artery with Synthetic Substitute, Percutaneous Approach
        "03UK3KZ",  # Supplement Right Internal Carotid Artery with Nonautologous Tissue Substitute, Percutaneous Approach
        "03UK47Z",  # Supplement Right Internal Carotid Artery with Autologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03UK4JZ",  # Supplement Right Internal Carotid Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "03UK4KZ",  # Supplement Right Internal Carotid Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03UL07Z",  # Supplement Left Internal Carotid Artery with Autologous Tissue Substitute, Open Approach
        "03UL0JZ",  # Supplement Left Internal Carotid Artery with Synthetic Substitute, Open Approach
        "03UL0KZ",  # Supplement Left Internal Carotid Artery with Nonautologous Tissue Substitute, Open Approach
        "03UL37Z",  # Supplement Left Internal Carotid Artery with Autologous Tissue Substitute, Percutaneous Approach
        "03UL3JZ",  # Supplement Left Internal Carotid Artery with Synthetic Substitute, Percutaneous Approach
        "03UL3KZ",  # Supplement Left Internal Carotid Artery with Nonautologous Tissue Substitute, Percutaneous Approach
        "03UL47Z",  # Supplement Left Internal Carotid Artery with Autologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03UL4JZ",  # Supplement Left Internal Carotid Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "03UL4KZ",  # Supplement Left Internal Carotid Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03UM07Z",  # Supplement Right External Carotid Artery with Autologous Tissue Substitute, Open Approach
        "03UM0JZ",  # Supplement Right External Carotid Artery with Synthetic Substitute, Open Approach
        "03UM0KZ",  # Supplement Right External Carotid Artery with Nonautologous Tissue Substitute, Open Approach
        "03UM37Z",  # Supplement Right External Carotid Artery with Autologous Tissue Substitute, Percutaneous Approach
        "03UM3JZ",  # Supplement Right External Carotid Artery with Synthetic Substitute, Percutaneous Approach
        "03UM3KZ",  # Supplement Right External Carotid Artery with Nonautologous Tissue Substitute, Percutaneous Approach
        "03UM47Z",  # Supplement Right External Carotid Artery with Autologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03UM4JZ",  # Supplement Right External Carotid Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "03UM4KZ",  # Supplement Right External Carotid Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03UN07Z",  # Supplement Left External Carotid Artery with Autologous Tissue Substitute, Open Approach
        "03UN0JZ",  # Supplement Left External Carotid Artery with Synthetic Substitute, Open Approach
        "03UN0KZ",  # Supplement Left External Carotid Artery with Nonautologous Tissue Substitute, Open Approach
        "03UN37Z",  # Supplement Left External Carotid Artery with Autologous Tissue Substitute, Percutaneous Approach
        "03UN3JZ",  # Supplement Left External Carotid Artery with Synthetic Substitute, Percutaneous Approach
        "03UN3KZ",  # Supplement Left External Carotid Artery with Nonautologous Tissue Substitute, Percutaneous Approach
        "03UN47Z",  # Supplement Left External Carotid Artery with Autologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03UN4JZ",  # Supplement Left External Carotid Artery with Synthetic Substitute, Percutaneous Endoscopic Approach
        "03UN4KZ",  # Supplement Left External Carotid Artery with Nonautologous Tissue Substitute, Percutaneous Endoscopic Approach
        "03VH0BZ",  # Restriction of Right Common Carotid Artery with Bioactive Intraluminal Device, Open Approach
        "03VH0CZ",  # Restriction of Right Common Carotid Artery with Extraluminal Device, Open Approach
        "03VH0DZ",  # Restriction of Right Common Carotid Artery with Intraluminal Device, Open Approach
        "03VH0ZZ",  # Restriction of Right Common Carotid Artery, Open Approach
        "03VH3BZ",  # Restriction of Right Common Carotid Artery with Bioactive Intraluminal Device, Percutaneous Approach
        "03VH3CZ",  # Restriction of Right Common Carotid Artery with Extraluminal Device, Percutaneous Approach
        "03VH3DZ",  # Restriction of Right Common Carotid Artery with Intraluminal Device, Percutaneous Approach
        "03VH3ZZ",  # Restriction of Right Common Carotid Artery, Percutaneous Approach
        "03VH4BZ",  # Restriction of Right Common Carotid Artery with Bioactive Intraluminal Device, Percutaneous Endoscopic Approach
        "03VH4CZ",  # Restriction of Right Common Carotid Artery with Extraluminal Device, Percutaneous Endoscopic Approach
        "03VH4DZ",  # Restriction of Right Common Carotid Artery with Intraluminal Device, Percutaneous Endoscopic Approach
        "03VH4ZZ",  # Restriction of Right Common Carotid Artery, Percutaneous Endoscopic Approach
        "03VJ0BZ",  # Restriction of Left Common Carotid Artery with Bioactive Intraluminal Device, Open Approach
        "03VJ0CZ",  # Restriction of Left Common Carotid Artery with Extraluminal Device, Open Approach
        "03VJ0DZ",  # Restriction of Left Common Carotid Artery with Intraluminal Device, Open Approach
        "03VJ0ZZ",  # Restriction of Left Common Carotid Artery, Open Approach
        "03VJ3BZ",  # Restriction of Left Common Carotid Artery with Bioactive Intraluminal Device, Percutaneous Approach
        "03VJ3CZ",  # Restriction of Left Common Carotid Artery with Extraluminal Device, Percutaneous Approach
        "03VJ3DZ",  # Restriction of Left Common Carotid Artery with Intraluminal Device, Percutaneous Approach
        "03VJ3ZZ",  # Restriction of Left Common Carotid Artery, Percutaneous Approach
        "03VJ4BZ",  # Restriction of Left Common Carotid Artery with Bioactive Intraluminal Device, Percutaneous Endoscopic Approach
        "03VJ4CZ",  # Restriction of Left Common Carotid Artery with Extraluminal Device, Percutaneous Endoscopic Approach
        "03VJ4DZ",  # Restriction of Left Common Carotid Artery with Intraluminal Device, Percutaneous Endoscopic Approach
        "03VJ4ZZ",  # Restriction of Left Common Carotid Artery, Percutaneous Endoscopic Approach
        "03VK0BZ",  # Restriction of Right Internal Carotid Artery with Bioactive Intraluminal Device, Open Approach
        "03VK0CZ",  # Restriction of Right Internal Carotid Artery with Extraluminal Device, Open Approach
        "03VK0DZ",  # Restriction of Right Internal Carotid Artery with Intraluminal Device, Open Approach
        "03VK0ZZ",  # Restriction of Right Internal Carotid Artery, Open Approach
        "03VK3BZ",  # Restriction of Right Internal Carotid Artery with Bioactive Intraluminal Device, Percutaneous Approach
        "03VK3CZ",  # Restriction of Right Internal Carotid Artery with Extraluminal Device, Percutaneous Approach
        "03VK3DZ",  # Restriction of Right Internal Carotid Artery with Intraluminal Device, Percutaneous Approach
        "03VK3ZZ",  # Restriction of Right Internal Carotid Artery, Percutaneous Approach
        "03VK4BZ",  # Restriction of Right Internal Carotid Artery with Bioactive Intraluminal Device, Percutaneous Endoscopic Approach
        "03VK4CZ",  # Restriction of Right Internal Carotid Artery with Extraluminal Device, Percutaneous Endoscopic Approach
        "03VK4DZ",  # Restriction of Right Internal Carotid Artery with Intraluminal Device, Percutaneous Endoscopic Approach
        "03VK4ZZ",  # Restriction of Right Internal Carotid Artery, Percutaneous Endoscopic Approach
        "03VL0BZ",  # Restriction of Left Internal Carotid Artery with Bioactive Intraluminal Device, Open Approach
        "03VL0CZ",  # Restriction of Left Internal Carotid Artery with Extraluminal Device, Open Approach
        "03VL0DZ",  # Restriction of Left Internal Carotid Artery with Intraluminal Device, Open Approach
        "03VL0ZZ",  # Restriction of Left Internal Carotid Artery, Open Approach
        "03VL3BZ",  # Restriction of Left Internal Carotid Artery with Bioactive Intraluminal Device, Percutaneous Approach
        "03VL3CZ",  # Restriction of Left Internal Carotid Artery with Extraluminal Device, Percutaneous Approach
        "03VL3DZ",  # Restriction of Left Internal Carotid Artery with Intraluminal Device, Percutaneous Approach
        "03VL3ZZ",  # Restriction of Left Internal Carotid Artery, Percutaneous Approach
        "03VL4BZ",  # Restriction of Left Internal Carotid Artery with Bioactive Intraluminal Device, Percutaneous Endoscopic Approach
        "03VL4CZ",  # Restriction of Left Internal Carotid Artery with Extraluminal Device, Percutaneous Endoscopic Approach
        "03VL4DZ",  # Restriction of Left Internal Carotid Artery with Intraluminal Device, Percutaneous Endoscopic Approach
        "03VL4ZZ",  # Restriction of Left Internal Carotid Artery, Percutaneous Endoscopic Approach
        "03VM0BZ",  # Restriction of Right External Carotid Artery with Bioactive Intraluminal Device, Open Approach
        "03VM0CZ",  # Restriction of Right External Carotid Artery with Extraluminal Device, Open Approach
        "03VM0DZ",  # Restriction of Right External Carotid Artery with Intraluminal Device, Open Approach
        "03VM0ZZ",  # Restriction of Right External Carotid Artery, Open Approach
        "03VM3BZ",  # Restriction of Right External Carotid Artery with Bioactive Intraluminal Device, Percutaneous Approach
        "03VM3CZ",  # Restriction of Right External Carotid Artery with Extraluminal Device, Percutaneous Approach
        "03VM3DZ",  # Restriction of Right External Carotid Artery with Intraluminal Device, Percutaneous Approach
        "03VM3ZZ",  # Restriction of Right External Carotid Artery, Percutaneous Approach
        "03VM4BZ",  # Restriction of Right External Carotid Artery with Bioactive Intraluminal Device, Percutaneous Endoscopic Approach
        "03VM4CZ",  # Restriction of Right External Carotid Artery with Extraluminal Device, Percutaneous Endoscopic Approach
        "03VM4DZ",  # Restriction of Right External Carotid Artery with Intraluminal Device, Percutaneous Endoscopic Approach
        "03VM4ZZ",  # Restriction of Right External Carotid Artery, Percutaneous Endoscopic Approach
        "03VN0BZ",  # Restriction of Left External Carotid Artery with Bioactive Intraluminal Device, Open Approach
        "03VN0CZ",  # Restriction of Left External Carotid Artery with Extraluminal Device, Open Approach
        "03VN0DZ",  # Restriction of Left External Carotid Artery with Intraluminal Device, Open Approach
        "03VN0ZZ",  # Restriction of Left External Carotid Artery, Open Approach
        "03VN3BZ",  # Restriction of Left External Carotid Artery with Bioactive Intraluminal Device, Percutaneous Approach
        "03VN3CZ",  # Restriction of Left External Carotid Artery with Extraluminal Device, Percutaneous Approach
        "03VN3DZ",  # Restriction of Left External Carotid Artery with Intraluminal Device, Percutaneous Approach
        "03VN3ZZ",  # Restriction of Left External Carotid Artery, Percutaneous Approach
        "03VN4BZ",  # Restriction of Left External Carotid Artery with Bioactive Intraluminal Device, Percutaneous Endoscopic Approach
        "03VN4CZ",  # Restriction of Left External Carotid Artery with Extraluminal Device, Percutaneous Endoscopic Approach
        "03VN4DZ",  # Restriction of Left External Carotid Artery with Intraluminal Device, Percutaneous Endoscopic Approach
        "03VN4ZZ",  # Restriction of Left External Carotid Artery, Percutaneous Endoscopic Approach
        "0G560ZZ",  # Destruction of Left Carotid Body, Open Approach
        "0G563ZZ",  # Destruction of Left Carotid Body, Percutaneous Approach
        "0G564ZZ",  # Destruction of Left Carotid Body, Percutaneous Endoscopic Approach
        "0G570ZZ",  # Destruction of Right Carotid Body, Open Approach
        "0G573ZZ",  # Destruction of Right Carotid Body, Percutaneous Approach
        "0G574ZZ",  # Destruction of Right Carotid Body, Percutaneous Endoscopic Approach
        "0G580ZZ",  # Destruction of Bilateral Carotid Bodies, Open Approach
        "0G583ZZ",  # Destruction of Bilateral Carotid Bodies, Percutaneous Approach
        "0G584ZZ",  # Destruction of Bilateral Carotid Bodies, Percutaneous Endoscopic Approach
        "0G9600Z",  # Drainage of Left Carotid Body with Drainage Device, Open Approach
        "0G960ZX",  # Drainage of Left Carotid Body, Open Approach, Diagnostic
        "0G960ZZ",  # Drainage of Left Carotid Body, Open Approach
        "0G9630Z",  # Drainage of Left Carotid Body with Drainage Device, Percutaneous Approach
        "0G963ZX",  # Drainage of Left Carotid Body, Percutaneous Approach, Diagnostic
        "0G963ZZ",  # Drainage of Left Carotid Body, Percutaneous Approach
        "0G9640Z",  # Drainage of Left Carotid Body with Drainage Device, Percutaneous Endoscopic Approach
        "0G964ZX",  # Drainage of Left Carotid Body, Percutaneous Endoscopic Approach, Diagnostic
        "0G964ZZ",  # Drainage of Left Carotid Body, Percutaneous Endoscopic Approach
        "0G9700Z",  # Drainage of Right Carotid Body with Drainage Device, Open Approach
        "0G970ZX",  # Drainage of Right Carotid Body, Open Approach, Diagnostic
        "0G970ZZ",  # Drainage of Right Carotid Body, Open Approach
        "0G9730Z",  # Drainage of Right Carotid Body with Drainage Device, Percutaneous Approach
        "0G973ZX",  # Drainage of Right Carotid Body, Percutaneous Approach, Diagnostic
        "0G973ZZ",  # Drainage of Right Carotid Body, Percutaneous Approach
        "0G9740Z",  # Drainage of Right Carotid Body with Drainage Device, Percutaneous Endoscopic Approach
        "0G974ZX",  # Drainage of Right Carotid Body, Percutaneous Endoscopic Approach, Diagnostic
        "0G974ZZ",  # Drainage of Right Carotid Body, Percutaneous Endoscopic Approach
        "0G9800Z",  # Drainage of Bilateral Carotid Bodies with Drainage Device, Open Approach
        "0G980ZX",  # Drainage of Bilateral Carotid Bodies, Open Approach, Diagnostic
        "0G980ZZ",  # Drainage of Bilateral Carotid Bodies, Open Approach
        "0G9830Z",  # Drainage of Bilateral Carotid Bodies with Drainage Device, Percutaneous Approach
        "0G983ZX",  # Drainage of Bilateral Carotid Bodies, Percutaneous Approach, Diagnostic
        "0G983ZZ",  # Drainage of Bilateral Carotid Bodies, Percutaneous Approach
        "0G9840Z",  # Drainage of Bilateral Carotid Bodies with Drainage Device, Percutaneous Endoscopic Approach
        "0G984ZX",  # Drainage of Bilateral Carotid Bodies, Percutaneous Endoscopic Approach, Diagnostic
        "0G984ZZ",  # Drainage of Bilateral Carotid Bodies, Percutaneous Endoscopic Approach
        "0GB60ZX",  # Excision of Left Carotid Body, Open Approach, Diagnostic
        "0GB60ZZ",  # Excision of Left Carotid Body, Open Approach
        "0GB63ZX",  # Excision of Left Carotid Body, Percutaneous Approach, Diagnostic
        "0GB63ZZ",  # Excision of Left Carotid Body, Percutaneous Approach
        "0GB64ZX",  # Excision of Left Carotid Body, Percutaneous Endoscopic Approach, Diagnostic
        "0GB64ZZ",  # Excision of Left Carotid Body, Percutaneous Endoscopic Approach
        "0GB70ZX",  # Excision of Right Carotid Body, Open Approach, Diagnostic
        "0GB70ZZ",  # Excision of Right Carotid Body, Open Approach
        "0GB73ZX",  # Excision of Right Carotid Body, Percutaneous Approach, Diagnostic
        "0GB73ZZ",  # Excision of Right Carotid Body, Percutaneous Approach
        "0GB74ZX",  # Excision of Right Carotid Body, Percutaneous Endoscopic Approach, Diagnostic
        "0GB74ZZ",  # Excision of Right Carotid Body, Percutaneous Endoscopic Approach
        "0GB80ZX",  # Excision of Bilateral Carotid Bodies, Open Approach, Diagnostic
        "0GB80ZZ",  # Excision of Bilateral Carotid Bodies, Open Approach
        "0GB83ZX",  # Excision of Bilateral Carotid Bodies, Percutaneous Approach, Diagnostic
        "0GB83ZZ",  # Excision of Bilateral Carotid Bodies, Percutaneous Approach
        "0GB84ZX",  # Excision of Bilateral Carotid Bodies, Percutaneous Endoscopic Approach, Diagnostic
        "0GB84ZZ",  # Excision of Bilateral Carotid Bodies, Percutaneous Endoscopic Approach
        "0GC60ZZ",  # Extirpation of Matter from Left Carotid Body, Open Approach
        "0GC63ZZ",  # Extirpation of Matter from Left Carotid Body, Percutaneous Approach
        "0GC64ZZ",  # Extirpation of Matter from Left Carotid Body, Percutaneous Endoscopic Approach
        "0GC70ZZ",  # Extirpation of Matter from Right Carotid Body, Open Approach
        "0GC73ZZ",  # Extirpation of Matter from Right Carotid Body, Percutaneous Approach
        "0GC74ZZ",  # Extirpation of Matter from Right Carotid Body, Percutaneous Endoscopic Approach
        "0GC80ZZ",  # Extirpation of Matter from Bilateral Carotid Bodies, Open Approach
        "0GC83ZZ",  # Extirpation of Matter from Bilateral Carotid Bodies, Percutaneous Approach
        "0GC84ZZ",  # Extirpation of Matter from Bilateral Carotid Bodies, Percutaneous Endoscopic Approach
        "0GN60ZZ",  # Release Left Carotid Body, Open Approach
        "0GN63ZZ",  # Release Left Carotid Body, Percutaneous Approach
        "0GN64ZZ",  # Release Left Carotid Body, Percutaneous Endoscopic Approach
        "0GN70ZZ",  # Release Right Carotid Body, Open Approach
        "0GN73ZZ",  # Release Right Carotid Body, Percutaneous Approach
        "0GN74ZZ",  # Release Right Carotid Body, Percutaneous Endoscopic Approach
        "0GN80ZZ",  # Release Bilateral Carotid Bodies, Open Approach
        "0GN83ZZ",  # Release Bilateral Carotid Bodies, Percutaneous Approach
        "0GN84ZZ",  # Release Bilateral Carotid Bodies, Percutaneous Endoscopic Approach
        "0GQ60ZZ",  # Repair Left Carotid Body, Open Approach
        "0GQ63ZZ",  # Repair Left Carotid Body, Percutaneous Approach
        "0GQ64ZZ",  # Repair Left Carotid Body, Percutaneous Endoscopic Approach
        "0GQ70ZZ",  # Repair Right Carotid Body, Open Approach
        "0GQ73ZZ",  # Repair Right Carotid Body, Percutaneous Approach
        "0GQ74ZZ",  # Repair Right Carotid Body, Percutaneous Endoscopic Approach
        "0GQ80ZZ",  # Repair Bilateral Carotid Bodies, Open Approach
        "0GQ83ZZ",  # Repair Bilateral Carotid Bodies, Percutaneous Approach
        "0GQ84ZZ",  # Repair Bilateral Carotid Bodies, Percutaneous Endoscopic Approach
        "0GT60ZZ",  # Resection of Left Carotid Body, Open Approach
        "0GT64ZZ",  # Resection of Left Carotid Body, Percutaneous Endoscopic Approach
        "0GT70ZZ",  # Resection of Right Carotid Body, Open Approach
        "0GT74ZZ",  # Resection of Right Carotid Body, Percutaneous Endoscopic Approach
        "0GT80ZZ",  # Resection of Bilateral Carotid Bodies, Open Approach
        "0GT84ZZ",  # Resection of Bilateral Carotid Bodies, Percutaneous Endoscopic Approach
        "B3060ZZ",  # Plain Radiography of Right Internal Carotid Artery using High Osmolar Contrast
        "B3061ZZ",  # Plain Radiography of Right Internal Carotid Artery using Low Osmolar Contrast
        "B306YZZ",  # Plain Radiography of Right Internal Carotid Artery using Other Contrast
        "B3070ZZ",  # Plain Radiography of Left Internal Carotid Artery using High Osmolar Contrast
        "B3071ZZ",  # Plain Radiography of Left Internal Carotid Artery using Low Osmolar Contrast
        "B307YZZ",  # Plain Radiography of Left Internal Carotid Artery using Other Contrast
        "B3080ZZ",  # Plain Radiography of Bilateral Internal Carotid Arteries using High Osmolar Contrast
        "B3081ZZ",  # Plain Radiography of Bilateral Internal Carotid Arteries using Low Osmolar Contrast
        "B308YZZ",  # Plain Radiography of Bilateral Internal Carotid Arteries using Other Contrast
        "B3160ZZ",  # Fluoroscopy of Right Internal Carotid Artery using High Osmolar Contrast
        "B3161ZZ",  # Fluoroscopy of Right Internal Carotid Artery using Low Osmolar Contrast
        "B316YZZ",  # Fluoroscopy of Right Internal Carotid Artery using Other Contrast
        "B3170ZZ",  # Fluoroscopy of Left Internal Carotid Artery using High Osmolar Contrast
        "B3171ZZ",  # Fluoroscopy of Left Internal Carotid Artery using Low Osmolar Contrast
        "B317YZZ",  # Fluoroscopy of Left Internal Carotid Artery using Other Contrast
        "B3180ZZ",  # Fluoroscopy of Bilateral Internal Carotid Arteries using High Osmolar Contrast
        "B3181ZZ",  # Fluoroscopy of Bilateral Internal Carotid Arteries using Low Osmolar Contrast
        "B318YZZ",  # Fluoroscopy of Bilateral Internal Carotid Arteries using Other Contrast
    }
    ICD9CM = {
        "0061",  # Percutaneous angioplasty of extracranial vessel(s)
        "0062",  # Percutaneous angioplasty of intracranial vessel(s)
        "0063",  # Percutaneous insertion of carotid artery stent(s)
        "0064",  # Percutaneous insertion of other extracranial artery stent(s)
        "0065",  # Percutaneous insertion of intracranial vascular stent(s)
        "3802",  # Incision of vessel, other vessels of head and neck
        "3812",  # Endarterectomy, other vessels of head and neck
        "3822",  # Percutaneous angioscopy
        "3830",  # Resection of vessel with anastomosis, unspecified site
        "3831",  # Resection of vessel with anastomosis, intracranial vessels
        "3832",  # Resection of vessel with anastomosis, other vessels of head and neck
        "3842",  # Resection of vessel with replacement, other vessels of head and neck
        "3922",  # Aorta-subclavian-carotid bypass
        "3928",  # Extracranial-intracranial (EC-IC) vascular bypass
        "8841",  # Arteriography of cerebral arteries
    }
    SNOMEDCT = {
        "9339002",  # Perfusion of carotid artery (procedure)
        "15023006",  # Thromboendarterectomy with graft of carotid artery by neck incision (procedure)
        "18674003",  # Creation of carotid-vertebral artery shunt (procedure)
        "22928005",  # Ligation of internal carotid artery (procedure)
        "31573003",  # Anastomosis of carotid-subclavian artery (procedure)
        "34214004",  # Creation of aorta-subclavian-carotid vascular bypass (procedure)
        "39887009",  # Thrombectomy with catheter of carotid artery by neck incision (procedure)
        "43628009",  # Insertion of needle into carotid artery (procedure)
        "46912008",  # Ligation of external carotid artery for nasal hemorrhage (procedure)
        "51382002",  # Creation of carotid-carotid shunt (procedure)
        "53412000",  # Ligation of common carotid artery (procedure)
        "59012002",  # Carotid-subclavian artery bypass graft with vein (procedure)
        "59109003",  # Ligation of external carotid artery (procedure)
        "66951008",  # Carotid endarterectomy (procedure)
        "74720005",  # Embolectomy with catheter of carotid artery by neck incision (procedure)
        "79507006",  # Carotid-vertebral artery bypass graft with vein (procedure)
        "80102005",  # Creation of external-internal carotid bypass (procedure)
        "80104006",  # Exteriorization of carotid artery (procedure)
        "87314005",  # Exploration of carotid artery (procedure)
        "90931006",  # Introduction of catheter into carotid artery (procedure)
        "112823003",  # Creation of aorta-carotid-brachial vascular bypass (procedure)
        "175363002",  # Reconstruction of carotid artery (procedure)
        "175364008",  # Replacement of carotid artery using graft (procedure)
        "175365009",  # Intracranial bypass to carotid artery (procedure)
        "175367001",  # Endarterectomy of carotid artery and patch repair of carotid artery (procedure)
        "175373000",  # Ligation of carotid artery (procedure)
        "175374006",  # Open embolectomy of carotid artery (procedure)
        "175376008",  # Operation on aneurysm of carotid artery (procedure)
        "175379001",  # Transluminal operations on carotid artery (procedure)
        "175380003",  # Percutaneous transluminal angioplasty of carotid artery (procedure)
        "175398004",  # Anastomosis of circle of Willis (procedure)
        "233259003",  # Angioplasty of external carotid artery (procedure)
        "233260008",  # Percutaneous balloon angioplasty of extracranial carotid artery (procedure)
        "233296007",  # Endarterectomy of internal carotid artery (procedure)
        "233297003",  # Endarterectomy of external carotid artery (procedure)
        "233298008",  # Endarterectomy of common carotid artery (procedure)
        "233405004",  # Insertion of carotid artery stent (procedure)
        "241219006",  # Internal carotid arteriogram (procedure)
        "276949008",  # Percutaneous endarterectomy of internal carotid artery (procedure)
        "276950008",  # Percutaneous endarterectomy of external carotid artery (procedure)
        "276951007",  # Percutaneous endarterectomy of common carotid artery (procedure)
        "287606009",  # Selective carotid artery arteriography (procedure)
        "302053004",  # Embolectomy of carotid artery (procedure)
        "303161001",  # Patch repair of carotid artery (procedure)
        "405326004",  # Angioplasty of internal carotid artery (procedure)
        "405379009",  # Repair of internal carotid artery (procedure)
        "405407008",  # Endarterectomy and angioplasty of internal carotid artery (procedure)
        "405408003",  # Endarterectomy and angioplasty of internal carotid artery with prosthesis (procedure)
        "405409006",  # Endarterectomy and angioplasty of internal carotid artery with vein (procedure)
        "405411002",  # Endarterectomy and angioplasty of external carotid artery (procedure)
        "405412009",  # Endarterectomy of internal carotid artery with eversion and end-to-end anastomosis (procedure)
        "405415006",  # Angioplasty of internal carotid artery with vein (procedure)
        "417884003",  # Fluoroscopic angioplasty of external carotid artery (procedure)
        "418405008",  # Fluoroscopic angiography of carotid artery and insertion of stent (procedure)
        "418838006",  # Fluoroscopic angiography of internal carotid artery (procedure)
        "419014003",  # Fluoroscopic angioplasty of internal carotid artery (procedure)
        "420026003",  # Fluoroscopic angioplasty of common carotid artery (procedure)
        "420046008",  # Fluoroscopic angioplasty of carotid artery (procedure)
        "420171008",  # Fluoroscopic angiography of carotid artery (procedure)
        "425611003",  # Percutaneous transluminal insertion of stent into carotid artery (procedure)
        "427486009",  # Bypass of carotid artery by anastomosis of superficial temporal artery to middle cerebral artery (procedure)
        "428802000",  # Endovascular repair of carotid artery (procedure)
        "429287007",  # Angioplasty of carotid artery (procedure)
        "431515004",  # Fluoroscopic angiography of external carotid artery using contrast with insertion of stent (procedure)
        "431519005",  # Fluoroscopic angiography of common carotid artery using contrast with insertion of stent (procedure)
        "431535003",  # Percutaneous transluminal angioplasty of external carotid artery using fluoroscopic guidance (procedure)
        "431659001",  # Percutaneous transluminal angioplasty of common carotid artery using fluoroscopic guidance (procedure)
        "432039002",  # Percutaneous transluminal angioplasty of internal carotid artery using fluoroscopic guidance (procedure)
        "432785007",  # Fluoroscopic angiography of common carotid artery using contrast with insertion of drug eluting stent (procedure)
        "433056003",  # Fluoroscopic angiography of internal carotid artery using contrast with insertion of stent (procedure)
        "433061001",  # Fluoroscopic intravenous digital subtraction angiography of carotid artery (procedure)
        "433591001",  # Fluoroscopic angiography of common carotid artery using contrast with insertion of stent graft (procedure)
        "433683001",  # Fluoroscopic angiography of internal carotid artery using contrast with insertion of drug eluting stent (procedure)
        "433690006",  # Fluoroscopic angiography of external carotid artery using contrast with insertion of drug eluting stent (procedure)
        "433711000",  # Percutaneous transluminal cutting balloon angioplasty of external carotid artery using fluoroscopic guidance (procedure)
        "433734009",  # Percutaneous transluminal cutting balloon angioplasty of internal carotid artery using fluoroscopic guidance (procedure)
        "434159001",  # Fluoroscopic angiography of external carotid artery using contrast with insertion of stent graft (procedure)
        "434378006",  # Fluoroscopic angiography of internal carotid artery using contrast with insertion of stent graft (procedure)
        "434433007",  # Percutaneous transluminal cutting balloon angioplasty of common carotid artery using fluoroscopic guidance (procedure)
        "438615003",  # Procedure on carotid artery using imaging guidance (procedure)
        "440221006",  # Bypass of carotid artery to brachial artery using vein graft (procedure)
        "440453000",  # Fluoroscopic angiography of aortic arch and carotid artery (procedure)
        "440518005",  # Fluoroscopic angiography of carotid artery with direct puncture (procedure)
        "449242004",  # Clipping of carotid artery by cervical approach (procedure)
    }


class Pci(ValueSet):
    """
    **Clinical Focus:** This value set contains concepts that represent procedures used to define percutaneous coronary intervention (PCI).

    **Data Element Scope:** This value set may use the Quality Data Model (QDM) datatype related to Procedure, Performed. The intent of this data element is to identify patients who had percutaneous coronary intervention (PCI) during an episode of acute myocardial infarction.

    **Inclusion Criteria:** Includes only relevant concepts associated with identifying patients receiving percutaneous coronary intervention (PCI). This is a grouping of ICD-10-PCS and SNOMED CT codes.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS347v5
    """

    VALUE_SET_NAME = "PCI"
    OID = "2.16.840.1.113762.1.4.1045.67"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    ICD10PCS = {
        "0270346",  # Dilation of Coronary Artery, One Artery, Bifurcation, with Drug-eluting Intraluminal Device, Percutaneous Approach
        "027034Z",  # Dilation of Coronary Artery, One Artery with Drug-eluting Intraluminal Device, Percutaneous Approach
        "0270356",  # Dilation of Coronary Artery, One Artery, Bifurcation, with Two Drug-eluting Intraluminal Devices, Percutaneous Approach
        "027035Z",  # Dilation of Coronary Artery, One Artery with Two Drug-eluting Intraluminal Devices, Percutaneous Approach
        "0270366",  # Dilation of Coronary Artery, One Artery, Bifurcation, with Three Drug-eluting Intraluminal Devices, Percutaneous Approach
        "027036Z",  # Dilation of Coronary Artery, One Artery with Three Drug-eluting Intraluminal Devices, Percutaneous Approach
        "0270376",  # Dilation of Coronary Artery, One Artery, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Percutaneous Approach
        "027037Z",  # Dilation of Coronary Artery, One Artery with Four or More Drug-eluting Intraluminal Devices, Percutaneous Approach
        "02703D6",  # Dilation of Coronary Artery, One Artery, Bifurcation, with Intraluminal Device, Percutaneous Approach
        "02703DZ",  # Dilation of Coronary Artery, One Artery with Intraluminal Device, Percutaneous Approach
        "02703E6",  # Dilation of Coronary Artery, One Artery, Bifurcation, with Two Intraluminal Devices, Percutaneous Approach
        "02703EZ",  # Dilation of Coronary Artery, One Artery with Two Intraluminal Devices, Percutaneous Approach
        "02703F6",  # Dilation of Coronary Artery, One Artery, Bifurcation, with Three Intraluminal Devices, Percutaneous Approach
        "02703FZ",  # Dilation of Coronary Artery, One Artery with Three Intraluminal Devices, Percutaneous Approach
        "02703G6",  # Dilation of Coronary Artery, One Artery, Bifurcation, with Four or More Intraluminal Devices, Percutaneous Approach
        "02703GZ",  # Dilation of Coronary Artery, One Artery with Four or More Intraluminal Devices, Percutaneous Approach
        "02703T6",  # Dilation of Coronary Artery, One Artery, Bifurcation, with Radioactive Intraluminal Device, Percutaneous Approach
        "02703TZ",  # Dilation of Coronary Artery, One Artery with Radioactive Intraluminal Device, Percutaneous Approach
        "02703Z6",  # Dilation of Coronary Artery, One Artery, Bifurcation, Percutaneous Approach
        "02703ZZ",  # Dilation of Coronary Artery, One Artery, Percutaneous Approach
        "0270446",  # Dilation of Coronary Artery, One Artery, Bifurcation, with Drug-eluting Intraluminal Device, Percutaneous Endoscopic Approach
        "027044Z",  # Dilation of Coronary Artery, One Artery with Drug-eluting Intraluminal Device, Percutaneous Endoscopic Approach
        "0270456",  # Dilation of Coronary Artery, One Artery, Bifurcation, with Two Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "027045Z",  # Dilation of Coronary Artery, One Artery with Two Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "0270466",  # Dilation of Coronary Artery, One Artery, Bifurcation, with Three Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "027046Z",  # Dilation of Coronary Artery, One Artery with Three Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "0270476",  # Dilation of Coronary Artery, One Artery, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "027047Z",  # Dilation of Coronary Artery, One Artery with Four or More Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "02704D6",  # Dilation of Coronary Artery, One Artery, Bifurcation, with Intraluminal Device, Percutaneous Endoscopic Approach
        "02704DZ",  # Dilation of Coronary Artery, One Artery with Intraluminal Device, Percutaneous Endoscopic Approach
        "02704E6",  # Dilation of Coronary Artery, One Artery, Bifurcation, with Two Intraluminal Devices, Percutaneous Endoscopic Approach
        "02704EZ",  # Dilation of Coronary Artery, One Artery with Two Intraluminal Devices, Percutaneous Endoscopic Approach
        "02704F6",  # Dilation of Coronary Artery, One Artery, Bifurcation, with Three Intraluminal Devices, Percutaneous Endoscopic Approach
        "02704FZ",  # Dilation of Coronary Artery, One Artery with Three Intraluminal Devices, Percutaneous Endoscopic Approach
        "02704G6",  # Dilation of Coronary Artery, One Artery, Bifurcation, with Four or More Intraluminal Devices, Percutaneous Endoscopic Approach
        "02704GZ",  # Dilation of Coronary Artery, One Artery with Four or More Intraluminal Devices, Percutaneous Endoscopic Approach
        "02704T6",  # Dilation of Coronary Artery, One Artery, Bifurcation, with Radioactive Intraluminal Device, Percutaneous Endoscopic Approach
        "02704TZ",  # Dilation of Coronary Artery, One Artery with Radioactive Intraluminal Device, Percutaneous Endoscopic Approach
        "02704Z6",  # Dilation of Coronary Artery, One Artery, Bifurcation, Percutaneous Endoscopic Approach
        "02704ZZ",  # Dilation of Coronary Artery, One Artery, Percutaneous Endoscopic Approach
        "0271346",  # Dilation of Coronary Artery, Two Arteries, Bifurcation, with Drug-eluting Intraluminal Device, Percutaneous Approach
        "027134Z",  # Dilation of Coronary Artery, Two Arteries with Drug-eluting Intraluminal Device, Percutaneous Approach
        "0271356",  # Dilation of Coronary Artery, Two Arteries, Bifurcation, with Two Drug-eluting Intraluminal Devices, Percutaneous Approach
        "027135Z",  # Dilation of Coronary Artery, Two Arteries with Two Drug-eluting Intraluminal Devices, Percutaneous Approach
        "0271366",  # Dilation of Coronary Artery, Two Arteries, Bifurcation, with Three Drug-eluting Intraluminal Devices, Percutaneous Approach
        "027136Z",  # Dilation of Coronary Artery, Two Arteries with Three Drug-eluting Intraluminal Devices, Percutaneous Approach
        "0271376",  # Dilation of Coronary Artery, Two Arteries, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Percutaneous Approach
        "027137Z",  # Dilation of Coronary Artery, Two Arteries with Four or More Drug-eluting Intraluminal Devices, Percutaneous Approach
        "02713D6",  # Dilation of Coronary Artery, Two Arteries, Bifurcation, with Intraluminal Device, Percutaneous Approach
        "02713DZ",  # Dilation of Coronary Artery, Two Arteries with Intraluminal Device, Percutaneous Approach
        "02713E6",  # Dilation of Coronary Artery, Two Arteries, Bifurcation, with Two Intraluminal Devices, Percutaneous Approach
        "02713EZ",  # Dilation of Coronary Artery, Two Arteries with Two Intraluminal Devices, Percutaneous Approach
        "02713F6",  # Dilation of Coronary Artery, Two Arteries, Bifurcation, with Three Intraluminal Devices, Percutaneous Approach
        "02713FZ",  # Dilation of Coronary Artery, Two Arteries with Three Intraluminal Devices, Percutaneous Approach
        "02713G6",  # Dilation of Coronary Artery, Two Arteries, Bifurcation, with Four or More Intraluminal Devices, Percutaneous Approach
        "02713GZ",  # Dilation of Coronary Artery, Two Arteries with Four or More Intraluminal Devices, Percutaneous Approach
        "02713T6",  # Dilation of Coronary Artery, Two Arteries, Bifurcation, with Radioactive Intraluminal Device, Percutaneous Approach
        "02713TZ",  # Dilation of Coronary Artery, Two Arteries with Radioactive Intraluminal Device, Percutaneous Approach
        "02713Z6",  # Dilation of Coronary Artery, Two Arteries, Bifurcation, Percutaneous Approach
        "02713ZZ",  # Dilation of Coronary Artery, Two Arteries, Percutaneous Approach
        "0271446",  # Dilation of Coronary Artery, Two Arteries, Bifurcation, with Drug-eluting Intraluminal Device, Percutaneous Endoscopic Approach
        "027144Z",  # Dilation of Coronary Artery, Two Arteries with Drug-eluting Intraluminal Device, Percutaneous Endoscopic Approach
        "0271456",  # Dilation of Coronary Artery, Two Arteries, Bifurcation, with Two Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "027145Z",  # Dilation of Coronary Artery, Two Arteries with Two Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "0271466",  # Dilation of Coronary Artery, Two Arteries, Bifurcation, with Three Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "027146Z",  # Dilation of Coronary Artery, Two Arteries with Three Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "0271476",  # Dilation of Coronary Artery, Two Arteries, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "027147Z",  # Dilation of Coronary Artery, Two Arteries with Four or More Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "02714D6",  # Dilation of Coronary Artery, Two Arteries, Bifurcation, with Intraluminal Device, Percutaneous Endoscopic Approach
        "02714DZ",  # Dilation of Coronary Artery, Two Arteries with Intraluminal Device, Percutaneous Endoscopic Approach
        "02714E6",  # Dilation of Coronary Artery, Two Arteries, Bifurcation, with Two Intraluminal Devices, Percutaneous Endoscopic Approach
        "02714EZ",  # Dilation of Coronary Artery, Two Arteries with Two Intraluminal Devices, Percutaneous Endoscopic Approach
        "02714F6",  # Dilation of Coronary Artery, Two Arteries, Bifurcation, with Three Intraluminal Devices, Percutaneous Endoscopic Approach
        "02714FZ",  # Dilation of Coronary Artery, Two Arteries with Three Intraluminal Devices, Percutaneous Endoscopic Approach
        "02714G6",  # Dilation of Coronary Artery, Two Arteries, Bifurcation, with Four or More Intraluminal Devices, Percutaneous Endoscopic Approach
        "02714GZ",  # Dilation of Coronary Artery, Two Arteries with Four or More Intraluminal Devices, Percutaneous Endoscopic Approach
        "02714T6",  # Dilation of Coronary Artery, Two Arteries, Bifurcation, with Radioactive Intraluminal Device, Percutaneous Endoscopic Approach
        "02714TZ",  # Dilation of Coronary Artery, Two Arteries with Radioactive Intraluminal Device, Percutaneous Endoscopic Approach
        "02714Z6",  # Dilation of Coronary Artery, Two Arteries, Bifurcation, Percutaneous Endoscopic Approach
        "02714ZZ",  # Dilation of Coronary Artery, Two Arteries, Percutaneous Endoscopic Approach
        "0272346",  # Dilation of Coronary Artery, Three Arteries, Bifurcation, with Drug-eluting Intraluminal Device, Percutaneous Approach
        "027234Z",  # Dilation of Coronary Artery, Three Arteries with Drug-eluting Intraluminal Device, Percutaneous Approach
        "0272356",  # Dilation of Coronary Artery, Three Arteries, Bifurcation, with Two Drug-eluting Intraluminal Devices, Percutaneous Approach
        "027235Z",  # Dilation of Coronary Artery, Three Arteries with Two Drug-eluting Intraluminal Devices, Percutaneous Approach
        "0272366",  # Dilation of Coronary Artery, Three Arteries, Bifurcation, with Three Drug-eluting Intraluminal Devices, Percutaneous Approach
        "027236Z",  # Dilation of Coronary Artery, Three Arteries with Three Drug-eluting Intraluminal Devices, Percutaneous Approach
        "0272376",  # Dilation of Coronary Artery, Three Arteries, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Percutaneous Approach
        "027237Z",  # Dilation of Coronary Artery, Three Arteries with Four or More Drug-eluting Intraluminal Devices, Percutaneous Approach
        "02723D6",  # Dilation of Coronary Artery, Three Arteries, Bifurcation, with Intraluminal Device, Percutaneous Approach
        "02723DZ",  # Dilation of Coronary Artery, Three Arteries with Intraluminal Device, Percutaneous Approach
        "02723E6",  # Dilation of Coronary Artery, Three Arteries, Bifurcation, with Two Intraluminal Devices, Percutaneous Approach
        "02723EZ",  # Dilation of Coronary Artery, Three Arteries with Two Intraluminal Devices, Percutaneous Approach
        "02723F6",  # Dilation of Coronary Artery, Three Arteries, Bifurcation, with Three Intraluminal Devices, Percutaneous Approach
        "02723FZ",  # Dilation of Coronary Artery, Three Arteries with Three Intraluminal Devices, Percutaneous Approach
        "02723G6",  # Dilation of Coronary Artery, Three Arteries, Bifurcation, with Four or More Intraluminal Devices, Percutaneous Approach
        "02723GZ",  # Dilation of Coronary Artery, Three Arteries with Four or More Intraluminal Devices, Percutaneous Approach
        "02723T6",  # Dilation of Coronary Artery, Three Arteries, Bifurcation, with Radioactive Intraluminal Device, Percutaneous Approach
        "02723TZ",  # Dilation of Coronary Artery, Three Arteries with Radioactive Intraluminal Device, Percutaneous Approach
        "02723Z6",  # Dilation of Coronary Artery, Three Arteries, Bifurcation, Percutaneous Approach
        "02723ZZ",  # Dilation of Coronary Artery, Three Arteries, Percutaneous Approach
        "0272446",  # Dilation of Coronary Artery, Three Arteries, Bifurcation, with Drug-eluting Intraluminal Device, Percutaneous Endoscopic Approach
        "027244Z",  # Dilation of Coronary Artery, Three Arteries with Drug-eluting Intraluminal Device, Percutaneous Endoscopic Approach
        "0272456",  # Dilation of Coronary Artery, Three Arteries, Bifurcation, with Two Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "027245Z",  # Dilation of Coronary Artery, Three Arteries with Two Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "0272466",  # Dilation of Coronary Artery, Three Arteries, Bifurcation, with Three Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "027246Z",  # Dilation of Coronary Artery, Three Arteries with Three Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "0272476",  # Dilation of Coronary Artery, Three Arteries, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "027247Z",  # Dilation of Coronary Artery, Three Arteries with Four or More Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "02724D6",  # Dilation of Coronary Artery, Three Arteries, Bifurcation, with Intraluminal Device, Percutaneous Endoscopic Approach
        "02724DZ",  # Dilation of Coronary Artery, Three Arteries with Intraluminal Device, Percutaneous Endoscopic Approach
        "02724E6",  # Dilation of Coronary Artery, Three Arteries, Bifurcation, with Two Intraluminal Devices, Percutaneous Endoscopic Approach
        "02724EZ",  # Dilation of Coronary Artery, Three Arteries with Two Intraluminal Devices, Percutaneous Endoscopic Approach
        "02724F6",  # Dilation of Coronary Artery, Three Arteries, Bifurcation, with Three Intraluminal Devices, Percutaneous Endoscopic Approach
        "02724FZ",  # Dilation of Coronary Artery, Three Arteries with Three Intraluminal Devices, Percutaneous Endoscopic Approach
        "02724G6",  # Dilation of Coronary Artery, Three Arteries, Bifurcation, with Four or More Intraluminal Devices, Percutaneous Endoscopic Approach
        "02724GZ",  # Dilation of Coronary Artery, Three Arteries with Four or More Intraluminal Devices, Percutaneous Endoscopic Approach
        "02724T6",  # Dilation of Coronary Artery, Three Arteries, Bifurcation, with Radioactive Intraluminal Device, Percutaneous Endoscopic Approach
        "02724TZ",  # Dilation of Coronary Artery, Three Arteries with Radioactive Intraluminal Device, Percutaneous Endoscopic Approach
        "02724Z6",  # Dilation of Coronary Artery, Three Arteries, Bifurcation, Percutaneous Endoscopic Approach
        "02724ZZ",  # Dilation of Coronary Artery, Three Arteries, Percutaneous Endoscopic Approach
        "0273346",  # Dilation of Coronary Artery, Four or More Arteries, Bifurcation, with Drug-eluting Intraluminal Device, Percutaneous Approach
        "027334Z",  # Dilation of Coronary Artery, Four or More Arteries with Drug-eluting Intraluminal Device, Percutaneous Approach
        "0273356",  # Dilation of Coronary Artery, Four or More Arteries, Bifurcation, with Two Drug-eluting Intraluminal Devices, Percutaneous Approach
        "027335Z",  # Dilation of Coronary Artery, Four or More Arteries with Two Drug-eluting Intraluminal Devices, Percutaneous Approach
        "0273366",  # Dilation of Coronary Artery, Four or More Arteries, Bifurcation, with Three Drug-eluting Intraluminal Devices, Percutaneous Approach
        "027336Z",  # Dilation of Coronary Artery, Four or More Arteries with Three Drug-eluting Intraluminal Devices, Percutaneous Approach
        "0273376",  # Dilation of Coronary Artery, Four or More Arteries, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Percutaneous Approach
        "027337Z",  # Dilation of Coronary Artery, Four or More Arteries with Four or More Drug-eluting Intraluminal Devices, Percutaneous Approach
        "02733D6",  # Dilation of Coronary Artery, Four or More Arteries, Bifurcation, with Intraluminal Device, Percutaneous Approach
        "02733DZ",  # Dilation of Coronary Artery, Four or More Arteries with Intraluminal Device, Percutaneous Approach
        "02733E6",  # Dilation of Coronary Artery, Four or More Arteries, Bifurcation, with Two Intraluminal Devices, Percutaneous Approach
        "02733EZ",  # Dilation of Coronary Artery, Four or More Arteries with Two Intraluminal Devices, Percutaneous Approach
        "02733F6",  # Dilation of Coronary Artery, Four or More Arteries, Bifurcation, with Three Intraluminal Devices, Percutaneous Approach
        "02733FZ",  # Dilation of Coronary Artery, Four or More Arteries with Three Intraluminal Devices, Percutaneous Approach
        "02733G6",  # Dilation of Coronary Artery, Four or More Arteries, Bifurcation, with Four or More Intraluminal Devices, Percutaneous Approach
        "02733GZ",  # Dilation of Coronary Artery, Four or More Arteries with Four or More Intraluminal Devices, Percutaneous Approach
        "02733T6",  # Dilation of Coronary Artery, Four or More Arteries, Bifurcation, with Radioactive Intraluminal Device, Percutaneous Approach
        "02733TZ",  # Dilation of Coronary Artery, Four or More Arteries with Radioactive Intraluminal Device, Percutaneous Approach
        "02733Z6",  # Dilation of Coronary Artery, Four or More Arteries, Bifurcation, Percutaneous Approach
        "02733ZZ",  # Dilation of Coronary Artery, Four or More Arteries, Percutaneous Approach
        "0273446",  # Dilation of Coronary Artery, Four or More Arteries, Bifurcation, with Drug-eluting Intraluminal Device, Percutaneous Endoscopic Approach
        "027344Z",  # Dilation of Coronary Artery, Four or More Arteries with Drug-eluting Intraluminal Device, Percutaneous Endoscopic Approach
        "0273456",  # Dilation of Coronary Artery, Four or More Arteries, Bifurcation, with Two Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "027345Z",  # Dilation of Coronary Artery, Four or More Arteries with Two Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "0273466",  # Dilation of Coronary Artery, Four or More Arteries, Bifurcation, with Three Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "027346Z",  # Dilation of Coronary Artery, Four or More Arteries with Three Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "0273476",  # Dilation of Coronary Artery, Four or More Arteries, Bifurcation, with Four or More Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "027347Z",  # Dilation of Coronary Artery, Four or More Arteries with Four or More Drug-eluting Intraluminal Devices, Percutaneous Endoscopic Approach
        "02734D6",  # Dilation of Coronary Artery, Four or More Arteries, Bifurcation, with Intraluminal Device, Percutaneous Endoscopic Approach
        "02734DZ",  # Dilation of Coronary Artery, Four or More Arteries with Intraluminal Device, Percutaneous Endoscopic Approach
        "02734E6",  # Dilation of Coronary Artery, Four or More Arteries, Bifurcation, with Two Intraluminal Devices, Percutaneous Endoscopic Approach
        "02734EZ",  # Dilation of Coronary Artery, Four or More Arteries with Two Intraluminal Devices, Percutaneous Endoscopic Approach
        "02734F6",  # Dilation of Coronary Artery, Four or More Arteries, Bifurcation, with Three Intraluminal Devices, Percutaneous Endoscopic Approach
        "02734FZ",  # Dilation of Coronary Artery, Four or More Arteries with Three Intraluminal Devices, Percutaneous Endoscopic Approach
        "02734G6",  # Dilation of Coronary Artery, Four or More Arteries, Bifurcation, with Four or More Intraluminal Devices, Percutaneous Endoscopic Approach
        "02734GZ",  # Dilation of Coronary Artery, Four or More Arteries with Four or More Intraluminal Devices, Percutaneous Endoscopic Approach
        "02734T6",  # Dilation of Coronary Artery, Four or More Arteries, Bifurcation, with Radioactive Intraluminal Device, Percutaneous Endoscopic Approach
        "02734TZ",  # Dilation of Coronary Artery, Four or More Arteries with Radioactive Intraluminal Device, Percutaneous Endoscopic Approach
        "02734Z6",  # Dilation of Coronary Artery, Four or More Arteries, Bifurcation, Percutaneous Endoscopic Approach
        "02734ZZ",  # Dilation of Coronary Artery, Four or More Arteries, Percutaneous Endoscopic Approach
    }
    SNOMEDCT = {
        "11101003",  # Percutaneous transluminal coronary angioplasty (procedure)
        "36969009",  # Placement of stent in coronary artery (procedure)
        "68466008",  # Removal of coronary artery obstruction by percutaneous transluminal balloon, single vessel (procedure)
        "85053006",  # Percutaneous transluminal coronary angioplasty, multiple vessels (procedure)
        "175066001",  # Percutaneous transluminal balloon angioplasty of bypass graft of coronary artery (procedure)
        "397193006",  # Percutaneous transluminal coronary angioplasty by rotoablation (procedure)
        "397431004",  # Percutaneous transluminal coronary angioplasty with rotoablation, single vessel (procedure)
        "414089002",  # Emergency percutaneous coronary intervention (procedure)
        "415070008",  # Percutaneous coronary intervention (procedure)
        "428488008",  # Placement of stent in anterior descending branch of left coronary artery (procedure)
        "429499003",  # Placement of stent in circumflex branch of left coronary artery (procedure)
        "429639007",  # Percutaneous transluminal balloon angioplasty with insertion of stent into coronary artery (procedure)
        "429809004",  # Fluoroscopic percutaneous transluminal angioplasty of coronary artery (procedure)
        "609153008",  # Percutaneous insertion of drug eluting stent into coronary artery using fluoroscopic guidance (procedure)
        "609154002",  # Percutaneous transluminal insertion of metal stent into coronary artery using fluoroscopic guidance (procedure)
        "698740005",  # Percutaneous transluminal atherectomy of coronary artery by rotary cutter using fluoroscopic guidance (procedure)
        "707828002",  # Percutaneous transluminal cutting balloon angioplasty of coronary artery (procedure)
        "737085003",  # Percutaneous insertion of bioresorbable stent into coronary artery using fluoroscopic guidance (procedure)
    }


class PrimaryThaProcedure(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of primary total hip arthroplasty (THA).

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent primary total hip arthroplasty (THA).

    **Exclusion Criteria:** Excludes concepts that represent revision or partial hip arthroplasty.

    ** Used in:** CMS56v10
    """

    VALUE_SET_NAME = "Primary THA Procedure"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1006"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "27130",  # Arthroplasty, acetabular and proximal femoral prosthetic replacement (total hip arthroplasty), with or without autograft or allograft
    }
    HCPCSLEVELII = {
        "S2118",  # Metal-on-metal total hip resurfacing, including acetabular and femoral components
    }
    SNOMEDCT = {
        "15163009",  # Total arthroplasty of hip, low friction (procedure)
        "19954002",  # Reconstruction of hip with use of methyl methacrylate (procedure)
        "52734007",  # Total replacement of hip (procedure)
        "53081006",  # Arthroplasty, acetabular and proximal femoral, prosthetic replacement (procedure)
        "57589001",  # Arthroplasty, acetabular and proximal femoral prosthetic replacement, with allograft (procedure)
        "76915002",  # Arthroplasty, acetabular and proximal femoral prosthetic replacement, with autograft (procedure)
        "179294005",  # Conversion to cemented total hip replacement (procedure)
        "179304004",  # Primary uncemented total hip replacement (procedure)
        "179305003",  # Conversion to uncemented total hip replacement (procedure)
        "265157000",  # Total prosthetic replacement of hip joint using cement (procedure)
        "265158005",  # Primary cemented total hip replacement (procedure)
        "265160007",  # Total prosthetic replacement of hip joint not using cement (procedure)
        "314489006",  # Primary hybrid total replacement of hip joint (procedure)
        "314491003",  # Prosthetic hybrid total replacement of hip joint (procedure)
        "426618001",  # Prosthetic hybrid total replacement of hip joint using cemented femoral component (procedure)
        "426904006",  # Prosthetic hybrid total replacement of hip joint using cemented acetabular component (procedure)
        "427728006",  # Primary hybrid total prosthetic replacement of hip joint using cemented femoral component (procedure)
        "429156003",  # Primary hybrid total prosthetic replacement of hip joint using cemented acetabular component (procedure)
        "443435007",  # Total replacement of right hip joint (procedure)
        "450813004",  # Primary total prosthetic replacement of hip (procedure)
        "770606008",  # Total replacement of left hip joint (procedure)
    }


class CystectomyForUrologyCare(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for procedures of cystectomy.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that identify a procedure of cystectomy.

    **Exclusion Criteria:** Excludes concepts that identify a surgery for the bladder other than cystectomy.

    ** Used in:** CMS646v2
    """

    VALUE_SET_NAME = "Cystectomy for Urology Care"
    OID = "2.16.840.1.113762.1.4.1151.55"
    DEFINITION_VERSION = "20180406"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "51550",  # Cystectomy, partial; simple
        "51555",  # Cystectomy, partial; complicated (eg, postradiation, previous surgery, difficult location)
        "51565",  # Cystectomy, partial, with reimplantation of ureter(s) into bladder (ureteroneocystostomy)
        "51570",  # Cystectomy, complete; (separate procedure)
        "51575",  # Cystectomy, complete; with bilateral pelvic lymphadenectomy, including external iliac, hypogastric, and obturator nodes
        "51585",  # Cystectomy, complete, with ureterosigmoidostomy or ureterocutaneous transplantations; with bilateral pelvic lymphadenectomy, including external iliac, hypogastric, and obturator nodes
        "51590",  # Cystectomy, complete, with ureteroileal conduit or sigmoid bladder, including intestine anastomosis
        "51595",  # Cystectomy, complete, with ureteroileal conduit or sigmoid bladder, including intestine anastomosis; with bilateral pelvic lymphadenectomy, including external iliac, hypogastric, and obturator nodes
    }
    SNOMEDCT = {
        "112902005",  # Partial urinary cystectomy (procedure)
        "176106009",  # Radical cystoprostatourethrectomy (procedure)
        "176107000",  # Radical cystourethrectomy - female (procedure)
        "176108005",  # Simple cystectomy (procedure)
    }


class PrimaryTkaProcedure(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for primary total knee arthroplasty (TKA).

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a primary total knee arthroplasty (TKA).

    **Exclusion Criteria:** Excludes concepts that represent revision or partial knee arthroplasty.

    ** Used in:** CMS66v10
    """

    VALUE_SET_NAME = "Primary TKA Procedure"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1007"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "27447",  # Arthroplasty, knee, condyle and plateau; medial AND lateral compartments with or without patella resurfacing (total knee arthroplasty)
    }
    SNOMEDCT = {
        "179344006",  # Primary cemented total knee replacement (procedure)
        "179345007",  # Conversion to cemented total knee replacement (procedure)
        "179351002",  # Primary uncemented total knee replacement (procedure)
        "179352009",  # Conversion to uncemented total knee replacement (procedure)
        "265170009",  # Total prosthetic replacement of knee joint using cement (procedure)
        "265172001",  # Total prosthetic replacement of knee joint not using cement (procedure)
        "392237008",  # Total arthroplasty of knee, geomedic or polycentric (procedure)
        "443681002",  # Total replacement of left knee joint (procedure)
        "443682009",  # Total replacement of right knee joint (procedure)
        "444463001",  # Bilateral replacement of knee joints (procedure)
        "609588000",  # Total knee replacement (procedure)
        "764931001",  # Revision of one component of total prosthetic replacement of knee joint not using cement (procedure)
        "764932008",  # Revision of one component of total prosthetic replacement of knee joint using cement (procedure)
    }


class FluorideVarnishApplicationForChildren(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for fluoride varnish applications.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent fluoride varnish applications.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS74v11
    """

    VALUE_SET_NAME = "Fluoride Varnish Application for Children"
    OID = "2.16.840.1.113883.3.464.1003.125.12.1002"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CDT = {
        "D1206",  # topical application of fluoride varnish
        "D1208",  # topical application of fluoride - excluding varnish
    }
    CPT = {
        "99188",  # Application of topical fluoride varnish by a physician or other qualified health care professional
    }
    SNOMEDCT = {
        "35889000",  # Topical application of fluoride excluding prophylaxis, child (procedure)
        "70468009",  # Topical application of fluoride including prophylaxis, child (procedure)
        "234723000",  # Topical application of fluoride - tooth (procedure)
        "313042009",  # Application of dental fluoride varnish (procedure)
    }


__exports__ = get_overrides(locals().copy())
