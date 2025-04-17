from canvas_sdk.value_set._utilities import get_overrides

from ..value_set import ValueSet


class AntiHepatitisAIggAntigenTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for the detection of anti Hepatitis A immunoglobulin (IgG) antibodies.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for the IgG antibody to Hepatitis A in serum.

    **Exclusion Criteria:** Excludes concepts that represent an order only.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Anti Hepatitis A IgG Antigen Test"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1033"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "32018-4",  # Hepatitis A virus IgG Ab [Presence] in Serum
        "40724-7",  # Hepatitis A virus IgG Ab [Presence] in Serum by Immunoassay
        "51913-2",  # Hepatitis A virus IgG+IgM Ab [Presence] in Serum
    }


class AntiHepatitisBVirusSurfaceAb(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for the detection of the anti Hepatitis B surface antigen.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for the anti-surface antibody to Hepatitis B virus in serum.

    **Exclusion Criteria:** Excludes concepts that represent an order only.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Anti Hepatitis B Virus Surface Ab"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1073"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "10900-9",  # Hepatitis B virus surface Ab [Presence] in Serum by Immunoassay
        "22322-2",  # Hepatitis B virus surface Ab [Presence] in Serum
        "39535-0",  # Hepatitis B virus surface Ab [Presence] in Serum by Radioimmunoassay (RIA)
        "48070-7",  # Hepatitis B virus surface IgG Ab [Presence] in Serum by Immunoassay
        "49177-9",  # Hepatitis B virus surface IgG Ab [Presence] in Serum
        "75409-3",  # Hepatitis B virus surface Ab [Presence] in Serum, Plasma or Blood by Rapid immunoassay
    }


class MeaslesAntibodyTestIggAntibodyTiter(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests for the titer of measles IgG antibody.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for the measles IgG titer in serum or cerebrospinal fluid.

    **Exclusion Criteria:** Excludes concepts that represent an order only.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Measles Antibody Test (IgG Antibody Titer)"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1059"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "21500-4",  # Measles virus IgG Ab [Titer] in Cerebral spinal fluid by Immunofluorescence
        "21501-2",  # Measles virus IgG Ab [Titer] in Serum by Immunofluorescence
        "22501-1",  # Measles virus IgG Ab [Titer] in Cerebral spinal fluid
        "22502-9",  # Measles virus IgG Ab [Titer] in Serum
    }


class MeaslesAntibodyTestIggAntibodyPresence(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests for the presence of measles IgG antibody.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for the presence of measles IgG in serum, cerebrospinal fluid or body fluid.

    **Exclusion Criteria:** Excludes concepts that represent an order only.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Measles Antibody Test (IgG Antibody presence)"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1060"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "20479-2",  # Measles virus IgG Ab [Presence] in Serum
        "35275-7",  # Measles virus IgG Ab [Presence] in Serum by Immunoassay
        "40648-8",  # Measles virus IgG Ab [Presence] in Cerebral spinal fluid by Immunoassay
        "41132-2",  # Measles virus IgG Ab [Presence] in Cerebral spinal fluid
        "53536-9",  # Measles virus IgG Ab [Presence] in Body fluid by Immunoassay
    }


class MumpsAntibodyTestIggAntibodyTiter(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests for the titer of mumps IgG antibody.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for the mumps IgG titer in serum or cerebrospinal fluid.

    **Exclusion Criteria:** Excludes concepts that represent an order only.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Mumps Antibody Test (IgG Antibody Titer)"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1061"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "21401-5",  # Mumps virus IgG Ab [Titer] in Cerebral spinal fluid by Immunofluorescence
        "22416-2",  # Mumps virus IgG Ab [Titer] in Cerebral spinal fluid
        "22417-0",  # Mumps virus IgG Ab [Titer] in Serum
        "6477-4",  # Mumps virus IgG Ab [Titer] in Serum by Immunofluorescence
    }


class MumpsAntibodyTestIggAntibodyPresence(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests for the presence of mumps IgG antibody.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for the presence of mumps IgG in serum, cerebrospinal fluid or body fluid.

    **Exclusion Criteria:** Excludes concepts that represent an order only.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Mumps Antibody Test (IgG Antibody presence)"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1062"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "22415-4",  # Mumps virus IgG Ab [Presence] in Serum
        "39011-2",  # Mumps virus IgG Ab [Presence] in Cerebral spinal fluid
        "40737-9",  # Mumps virus IgG Ab [Presence] in Cerebral spinal fluid by Immunoassay
        "6476-6",  # Mumps virus IgG Ab [Presence] in Serum by Immunoassay
        "74422-7",  # Mumps virus IgG Ab [Presence] in Body fluid by Immunoassay
    }


class RubellaAntibodyTestIggAntibodyTiter(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests for the titer of rubella IgG antibody.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for the rubella IgG titer in serum or cerebrospinal fluid.

    **Exclusion Criteria:** Excludes concepts that represent an order only.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Rubella Antibody Test (IgG Antibody Titer)"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1063"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "41763-4",  # Rubella virus IgG Ab [Titer] in Serum
        "46110-3",  # Rubella virus IgG Ab [Titer] in Cerebral spinal fluid
    }


class RubellaAntibodyTestIggAntibodyPresence(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests for the presence of rubella IgG antibody.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for the presence of rubella IgG in serum, cerebrospinal fluid, body fluid.

    **Exclusion Criteria:** Excludes concepts that represent an order only.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Rubella Antibody Test (IgG Antibody presence)"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1064"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "25514-1",  # Rubella virus IgG Ab [Presence] in Serum
        "39013-8",  # Rubella virus IgG Ab [Presence] in Cerebral spinal fluid
        "40667-8",  # Rubella virus IgG Ab [Presence] in Serum or Plasma by Immunoassay
        "40668-6",  # Rubella virus IgG Ab [Presence] in Cerebral spinal fluid by Immunoassay
        "63462-6",  # Rubella virus IgG Ab [Presence] in Serum by Latex agglutination
        "74415-1",  # Rubella virus IgG Ab [Presence] in Body fluid by Immunoassay
    }


class VaricellaZosterAntibodyTestIggAntibodyPresence(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests for the presence of varicella zoster IgG antibody.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for the presence of varicella zoster IgG in serum, cerebrospinal fluid or body fluid.

    **Exclusion Criteria:** Excludes concepts that represent an order only.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Varicella Zoster Antibody Test (IgG Antibody Presence)"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1067"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "15410-4",  # Varicella zoster virus IgG Ab [Presence] in Serum by Immunoassay
        "19162-7",  # Varicella zoster virus IgG Ab [Presence] in Serum
        "41512-5",  # Varicella zoster virus IgG Ab [Presence] in Serum by Immunofluorescence
        "42537-1",  # Varicella zoster virus IgG Ab [Presence] in Cerebral spinal fluid
        "53534-4",  # Varicella zoster virus IgG Ab [Presence] in Body fluid by Immunoassay
    }


class VaricellaZosterAntibodyTestIggAntibodyTiter(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests for the titer of varicella zoster IgG antibody.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for the varicella zoster IgG titer in serum or cerebrospinal fluid.

    **Exclusion Criteria:** Excludes concepts that represent an order only.

    ** Used in:** CMS117v10
    """

    VALUE_SET_NAME = "Varicella Zoster Antibody Test (IgG Antibody Titer)"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1066"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "21595-4",  # Varicella zoster virus IgG Ab [Titer] in Cerebral spinal fluid by Immunofluorescence
        "22601-9",  # Varicella zoster virus IgG Ab [Titer] in Cerebral spinal fluid
        "22602-7",  # Varicella zoster virus IgG Ab [Titer] in Serum
        "6569-8",  # Varicella zoster virus IgG Ab [Titer] in Serum by Immunofluorescence
    }


class Hba1CLaboratoryTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for hemoglobin A1c tests.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for hemoglobin A1c.

    **Exclusion Criteria:** Excludes concepts that represent hemoglobin A1c laboratory tests that use the International Federation of Clinical Chemistry and Laboratory Medicine (IFCC) protocol and Japanese Diabetes Society (JDS)/Japanese Society of Clinical Chemistry (JSCC) protocol and exclude concepts that represent an order only.

    ** Used in:** CMS122v10
    """

    VALUE_SET_NAME = "HbA1c Laboratory Test"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1013"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "17856-6",  # Hemoglobin A1c/Hemoglobin.total in Blood by HPLC
        "4548-4",  # Hemoglobin A1c/Hemoglobin.total in Blood
        "4549-2",  # Hemoglobin A1c/Hemoglobin.total in Blood by Electrophoresis
    }


class HpvTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for human papilloma viruses (HPV).

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for high-risk HPV in cervical samples.

    **Exclusion Criteria:** Excludes concepts that represent tests for high-risk HPV conducted on non-cervical samples and tests that are ordered only.

    ** Used in:** CMS124v10
    """

    VALUE_SET_NAME = "HPV Test"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1059"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "21440-3",  # Human papilloma virus 16+18+31+33+35+45+51+52+56 DNA [Presence] in Cervix by Probe
        "30167-1",  # Human papilloma virus 16+18+31+33+35+39+45+51+52+56+58+59+68 DNA [Presence] in Cervix by Probe with signal amplification
        "38372-9",  # Human papilloma virus 6+11+16+18+31+33+35+39+42+43+44+45+51+52+56+58+59+68 DNA [Presence] in Cervix by Probe with signal amplification
        "59263-4",  # Human papilloma virus 16 DNA [Presence] in Cervix by Probe with signal amplification
        "59264-2",  # Human papilloma virus 18 DNA [Presence] in Cervix by Probe with signal amplification
        "59420-0",  # Human papilloma virus 16+18+31+33+35+39+45+51+52+56+58+59+66+68 DNA [Presence] in Cervix by Probe with signal amplification
        "69002-4",  # Human papilloma virus E6+E7 mRNA [Presence] in Cervix by NAA with probe detection
        "71431-1",  # Human papilloma virus 31+33+35+39+45+51+52+56+58+59+66+68 DNA [Presence] in Cervix by NAA with probe detection
        "75694-0",  # Human papilloma virus 18+45 E6+E7 mRNA [Presence] in Cervix by NAA with probe detection
        "77379-6",  # Human papilloma virus 16 and 18 and 31+33+35+39+45+51+52+56+58+59+66+68 DNA [Interpretation] in Cervix
        "77399-4",  # Human papilloma virus 16 DNA [Presence] in Cervix by NAA with probe detection
        "77400-0",  # Human papilloma virus 18 DNA [Presence] in Cervix by NAA with probe detection
        "82354-2",  # Human papilloma virus 16 and 18+45 E6+E7 mRNA [Identifier] in Cervix by NAA with probe detection
        "82456-5",  # Human papilloma virus 16 E6+E7 mRNA [Presence] in Cervix by NAA with probe detection
        "82675-0",  # Human papilloma virus 16+18+31+33+35+39+45+51+52+56+58+59+66+68 DNA [Presence] in Cervix by NAA with probe detection
    }


class PapTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for cervical cytology tests.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for cervical cytology.

    **Exclusion Criteria:** Excludes concepts that represent tests for cervical cytology conducted on non-cervical or non-vaginal samples and tests that are ordered only.

    ** Used in:** CMS124v10, CMS153v10
    """

    VALUE_SET_NAME = "Pap Test"
    OID = "2.16.840.1.113883.3.464.1003.108.12.1017"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "10524-7",  # Microscopic observation [Identifier] in Cervix by Cyto stain
        "18500-9",  # Microscopic observation [Identifier] in Cervix by Cyto stain.thin prep
        "19762-4",  # General categories [Interpretation] of Cervical or vaginal smear or scraping by Cyto stain
        "19764-0",  # Statement of adequacy [Interpretation] of Cervical or vaginal smear or scraping by Cyto stain
        "19765-7",  # Microscopic observation [Identifier] in Cervical or vaginal smear or scraping by Cyto stain
        "19766-5",  # Microscopic observation [Identifier] in Cervical or vaginal smear or scraping by Cyto stain Narrative
        "19774-9",  # Cytology study comment Cervical or vaginal smear or scraping Cyto stain
        "33717-0",  # Cytology Cervical or vaginal smear or scraping study
        "47527-7",  # Cytology report of Cervical or vaginal smear or scraping Cyto stain.thin prep
        "47528-5",  # Cytology report of Cervical or vaginal smear or scraping Cyto stain
    }


class ProstateSpecificAntigenTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests measuring the prostate specific antigen (PSA).

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent a laboratory test for a prostate specific antigen (PSA).

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS129v11
    """

    VALUE_SET_NAME = "Prostate Specific Antigen Test"
    OID = "2.16.840.1.113883.3.526.3.401"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "10508-0",  # Prostate specific Ag [Presence] in Tissue by Immune stain
        "10886-0",  # Prostate Specific Ag Free [Mass/volume] in Serum or Plasma
        "12841-3",  # Prostate Specific Ag Free/Prostate specific Ag.total in Serum or Plasma
        "15323-9",  # Prostate specific Ag/Prostate volume calculated from height, width and length
        "15324-7",  # Prostate specific Ag/Prostate volume calculated from planimetry
        "15325-4",  # Prostate specific Ag/Prostate volume calculated
        "19195-7",  # Prostate specific Ag [Units/volume] in Serum or Plasma
        "19201-3",  # Prostate Specific Ag Free [Units/volume] in Serum or Plasma
        "2857-1",  # Prostate specific Ag [Mass/volume] in Serum or Plasma
        "33667-7",  # Prostate specific Ag.protein bound [Mass/volume] in Serum or Plasma
        "34611-4",  # Prostate specific Ag [Mass/volume] in Urine
        "35741-8",  # Prostate specific Ag [Mass/volume] in Serum or Plasma by Detection limit <= 0.01 ng/mL
    }


class FitDna(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for fecal immunochemical (FIT) DNA tests.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent fecal immunochemical (FIT) DNA tests.

    **Exclusion Criteria:** Excludes concepts that represent an order only.

    ** Used in:** CMS130v10
    """

    VALUE_SET_NAME = "FIT DNA"
    OID = "2.16.840.1.113883.3.464.1003.108.12.1039"
    DEFINITION_VERSION = "20171219"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "77353-1",  # Noninvasive colorectal cancer DNA and occult blood screening [Interpretation] in Stool Narrative
        "77354-9",  # Noninvasive colorectal cancer DNA and occult blood screening [Presence] in Stool
    }


class FecalOccultBloodTestFobt(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for fecal occult blood tests.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for occult blood in stool.

    **Exclusion Criteria:** Excludes concepts that represent an order only and test for occult blood in other body fluids.

    ** Used in:** CMS130v10
    """

    VALUE_SET_NAME = "Fecal Occult Blood Test (FOBT)"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1011"
    DEFINITION_VERSION = "20171219"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

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


class UrineProteinTests(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for tests that measure urine protein.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for protein in urine.

    **Exclusion Criteria:** Excludes concepts that represent an order only.

    ** Used in:** CMS134v10
    """

    VALUE_SET_NAME = "Urine Protein Tests"
    OID = "2.16.840.1.113883.3.464.1003.109.12.1024"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "11218-5",  # Microalbumin [Mass/volume] in Urine by Test strip
        "12842-1",  # Protein [Mass/volume] in 12 hour Urine
        "13705-9",  # Albumin/Creatinine [Mass Ratio] in 24 hour Urine
        "13801-6",  # Protein/Creatinine [Mass Ratio] in 24 hour Urine
        "13986-5",  # Albumin/Protein.total in 24 hour Urine by Electrophoresis
        "13992-3",  # Albumin/Protein.total in Urine by Electrophoresis
        "14956-7",  # Microalbumin [Mass/time] in 24 hour Urine
        "14957-5",  # Microalbumin [Mass/volume] in Urine
        "14958-3",  # Microalbumin/Creatinine [Mass Ratio] in 24 hour Urine
        "14959-1",  # Microalbumin/Creatinine [Mass Ratio] in Urine
        "1753-3",  # Albumin [Presence] in Urine
        "1754-1",  # Albumin [Mass/volume] in Urine
        "1755-8",  # Albumin [Mass/time] in 24 hour Urine
        "1757-4",  # Albumin renal clearance in 24 hour Urine and Serum or Plasma
        "17819-4",  # Albumin/Protein.total by Electrophoresis in Urine collected for unspecified duration
        "18373-1",  # Protein [Mass/time] in 6 hour Urine
        "20454-5",  # Protein [Presence] in Urine by Test strip
        "20621-9",  # Albumin/Creatinine [Presence] in Urine by Test strip
        "21059-1",  # Albumin [Mass/volume] in 24 hour Urine
        "21482-5",  # Protein [Mass/volume] in 24 hour Urine
        "26801-1",  # Protein [Mass/time] in 12 hour Urine
        "27298-9",  # Protein [Units/volume] in Urine
        "2887-8",  # Protein [Presence] in Urine
        "2888-6",  # Protein [Mass/volume] in Urine
        "2889-4",  # Protein [Mass/time] in 24 hour Urine
        "2890-2",  # Protein/Creatinine [Mass Ratio] in Urine
        "29946-1",  # Albumin [Presence] in 24 hour Urine by Electrophoresis
        "30000-4",  # Microalbumin/Creatinine [Ratio] in Urine
        "30001-2",  # Microalbumin/Creatinine [Ratio] in Urine by Test strip
        "30003-8",  # Microalbumin [Mass/volume] in 24 hour Urine
        "32209-9",  # Protein [Presence] in 24 hour Urine by Test strip
        "32294-1",  # Albumin/Creatinine [Ratio] in Urine
        "32551-4",  # Protein [Mass] in Urine collected for unspecified duration
        "34366-5",  # Protein/Creatinine [Ratio] in Urine
        "35663-4",  # Protein [Mass/volume] in Urine collected for unspecified duration
        "40486-3",  # Protein/Creatinine [Ratio] in 24 hour Urine
        "40662-9",  # Protein [Mass/time] in 12 hour Urine --resting
        "40663-7",  # Protein [Mass/time] in 12 hour Urine --upright
        "43605-5",  # Microalbumin [Mass/volume] in 4 hour Urine
        "43606-3",  # Microalbumin [Mass/time] in 4 hour Urine
        "43607-1",  # Microalbumin [Mass/time] in 12 hour Urine
        "44292-1",  # Microalbumin/Creatinine [Mass Ratio] in 12 hour Urine
        "47558-2",  # Microalbumin/Protein.total in 24 hour Urine
        "49002-9",  # Albumin [Mass/time] in Urine collected for unspecified duration
        "49023-5",  # Microalbumin [Mass/time] in Urine collected for unspecified duration
        "50209-6",  # Albumin [Mass/time] in Urine collected for unspecified duration --supine
        "50561-0",  # Protein [Mass/volume] in Urine by Automated test strip
        "50949-7",  # Albumin [Presence] in Urine by Test strip
        "51190-7",  # Albumin [Mass/volume] in 24 hour Urine by Electrophoresis
        "53121-0",  # Protein [Mass/time] in 1 hour Urine
        "53525-2",  # Protein [Presence] in Urine by SSA method
        "53530-2",  # Microalbumin [Mass/volume] in 24 hour Urine by Detection limit <= 1.0 mg/L
        "53531-0",  # Microalbumin [Mass/volume] in Urine by Detection limit <= 1.0 mg/L
        "53532-8",  # Microalbumin [Mass/time] in 24 hour Urine by Detection limit <= 1.0 mg/L
        "56553-1",  # Microalbumin [Mass/time] in 8 hour Urine
        "57369-1",  # Microalbumin [Mass/volume] in 12 hour Urine
        "57735-3",  # Protein [Presence] in Urine by Automated test strip
        "5804-0",  # Protein [Mass/volume] in Urine by Test strip
        "58448-2",  # Microalbumin ug/min [Mass/time] in 24 hour Urine
        "58992-9",  # Protein [Mass/time] in 18 hour Urine
        "59159-4",  # Microalbumin/Creatinine [Ratio] in 24 hour Urine
        "60678-0",  # Protein/Creatinine [Mass Ratio] in 12 hour Urine
        "63474-1",  # Microalbumin [Mass/time] in 18 hour Urine
        "6941-9",  # Albumin [Mass/time] in 24 hour Urine by Electrophoresis
        "6942-7",  # Albumin [Mass/volume] in Urine by Electrophoresis
        "76401-9",  # Albumin/Creatinine [Ratio] in 24 hour Urine
        "77253-3",  # Microalbumin/Creatinine [Ratio] in Urine by Detection limit <= 1.0 mg/L
        "77254-1",  # Microalbumin/Creatinine [Ratio] in 24 hour Urine by Detection limit <= 1.0 mg/L
        "77940-5",  # Albumin [Mass/volume] by Electrophoresis in Urine collected for unspecified duration
        "89998-9",  # Albumin/Creatinine [Ratio] in Urine by Detection limit <= 3.0 mg/L
        "89999-7",  # Albumin [Mass/volume] in Urine by Detection limit <= 3.0 mg/L
        "90000-1",  # Albumin [Mass/time] in 24 hour Urine by Detection limit <= 3.0 mg/L
        "9318-7",  # Albumin/Creatinine [Mass Ratio] in Urine
        "93746-6",  # Protein catabolic rate based on 24 hour Urine [Calculated]
        "95232-5",  # Microalbumin [Presence] in Urine by Test strip
        "95233-3",  # Microalbumin/Creatinine [Presence] in Urine by Test strip
    }


class GroupAStreptococcusTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for group A streptococcus tests.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests to identify the presence of group A streptococcus.

    **Exclusion Criteria:** Excludes concepts that represent an order only.

    ** Used in:** CMS146v10
    """

    VALUE_SET_NAME = "Group A Streptococcus Test"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1012"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "11268-0",  # Streptococcus pyogenes [Presence] in Throat by Organism specific culture
        "17656-0",  # Streptococcus pyogenes [Presence] in Specimen by Organism specific culture
        "17898-8",  # Bacteria identified in Throat by Aerobe culture
        "18481-2",  # Streptococcus pyogenes Ag [Presence] in Throat
        "31971-5",  # Streptococcus pyogenes Ag [Presence] in Specimen
        "49610-9",  # Streptococcus pyogenes DNA [Identifier] in Specimen by NAA with probe detection
        "5036-9",  # Streptococcus pyogenes rRNA [Presence] in Specimen by Probe
        "60489-2",  # Streptococcus pyogenes DNA [Presence] in Throat by NAA with probe detection
        "626-2",  # Bacteria identified in Throat by Culture
        "6557-3",  # Streptococcus pyogenes Ag [Presence] in Throat by Immunofluorescence
        "6558-1",  # Streptococcus pyogenes Ag [Presence] in Specimen by Immunoassay
        "6559-9",  # Streptococcus pyogenes Ag [Presence] in Specimen by Immunofluorescence
        "68954-7",  # Streptococcus pyogenes rRNA [Presence] in Throat by Probe
        "78012-2",  # Streptococcus pyogenes Ag [Presence] in Throat by Rapid immunoassay
        "96331-4",  # Streptococcus pyogenes DNA [NCncRange] in Lower respiratory specimen Qualitative by NAA with non-probe detection
    }


class ChlamydiaScreening(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for chlamydia tests.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent screening for chlamydia infections.

    **Exclusion Criteria:** Excludes concepts that represent an order only.

    ** Used in:** CMS153v10
    """

    VALUE_SET_NAME = "Chlamydia Screening"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1052"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "14463-4",  # Chlamydia trachomatis [Presence] in Cervix by Organism specific culture
        "14464-2",  # Chlamydia trachomatis [Presence] in Vaginal fluid by Organism specific culture
        "14467-5",  # Chlamydia trachomatis [Presence] in Urine sediment by Organism specific culture
        "14474-1",  # Chlamydia trachomatis Ag [Presence] in Urine sediment by Immunoassay
        "14513-6",  # Chlamydia trachomatis Ag [Presence] in Urine sediment by Immunofluorescence
        "16600-9",  # Chlamydia trachomatis rRNA [Presence] in Genital specimen by Probe
        "21190-4",  # Chlamydia trachomatis DNA [Presence] in Cervix by NAA with probe detection
        "21191-2",  # Chlamydia trachomatis DNA [Presence] in Urethra by NAA with probe detection
        "21613-5",  # Chlamydia trachomatis DNA [Presence] in Specimen by NAA with probe detection
        "23838-6",  # Chlamydia trachomatis rRNA [Presence] in Genital fluid by Probe
        "31775-0",  # Chlamydia trachomatis Ag [Presence] in Urine sediment
        "31777-6",  # Chlamydia trachomatis Ag [Presence] in Specimen
        "36902-5",  # Chlamydia trachomatis+Neisseria gonorrhoeae DNA [Presence] in Specimen by NAA with probe detection
        "36903-3",  # Chlamydia trachomatis and Neisseria gonorrhoeae DNA [Identifier] in Specimen by NAA with probe detection
        "42931-6",  # Chlamydia trachomatis rRNA [Presence] in Urine by NAA with probe detection
        "43304-5",  # Chlamydia trachomatis rRNA [Presence] in Specimen by NAA with probe detection
        "43404-3",  # Chlamydia trachomatis DNA [Presence] in Specimen by Probe with signal amplification
        "43405-0",  # Chlamydia trachomatis and Neisseria gonorrhoeae DNA [Identifier] in Specimen by Probe with signal amplification
        "43406-8",  # Chlamydia trachomatis+Neisseria gonorrhoeae DNA [Presence] in Specimen by Probe with signal amplification
        "44806-8",  # Chlamydia trachomatis+Neisseria gonorrhoeae DNA [Presence] in Urine by NAA with probe detection
        "44807-6",  # Chlamydia trachomatis+Neisseria gonorrhoeae DNA [Presence] in Genital specimen by NAA with probe detection
        "45068-4",  # Chlamydia trachomatis+Neisseria gonorrhoeae DNA [Presence] in Cervix by NAA with probe detection
        "45069-2",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Genital specimen by Probe
        "45075-9",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Urethra by Probe
        "45076-7",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Specimen by Probe
        "45084-1",  # Chlamydia trachomatis DNA [Presence] in Vaginal fluid by NAA with probe detection
        "45091-6",  # Chlamydia trachomatis Ag [Presence] in Genital specimen
        "45095-7",  # Chlamydia trachomatis [Presence] in Genital specimen by Organism specific culture
        "45098-1",  # Chlamydia sp identified in Cervix by Organism specific culture
        "45100-5",  # Chlamydia sp identified in Vaginal fluid by Organism specific culture
        "47211-8",  # Chlamydia trachomatis L2 DNA [Presence] in Specimen by NAA with probe detection
        "47212-6",  # Chlamydia trachomatis DNA [Identifier] in Specimen by NAA with probe detection
        "49096-1",  # Chlamydia trachomatis DNA [Units/volume] in Specimen by NAA with probe detection
        "4993-2",  # Chlamydia trachomatis rRNA [Presence] in Specimen by Probe
        "50387-0",  # Chlamydia trachomatis rRNA [Presence] in Cervix by NAA with probe detection
        "53925-4",  # Chlamydia trachomatis rRNA [Presence] in Urethra by NAA with probe detection
        "53926-2",  # Chlamydia trachomatis rRNA [Presence] in Vaginal fluid by NAA with probe detection
        "557-9",  # Chlamydia sp identified in Genital specimen by Organism specific culture
        "560-3",  # Chlamydia sp identified in Specimen by Organism specific culture
        "6349-5",  # Chlamydia trachomatis [Presence] in Specimen by Organism specific culture
        "6354-5",  # Chlamydia trachomatis Ag [Presence] in Specimen by Immunoassay
        "6355-2",  # Chlamydia trachomatis Ag [Presence] in Specimen by Immunofluorescence
        "6356-0",  # Chlamydia trachomatis DNA [Presence] in Genital specimen by NAA with probe detection
        "6357-8",  # Chlamydia trachomatis DNA [Presence] in Urine by NAA with probe detection
        "80360-1",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Urine by NAA with probe detection
        "80361-9",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Cervix by NAA with probe detection
        "80362-7",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Vaginal fluid by NAA with probe detection
        "91860-7",  # Chlamydia trachomatis Ag [Presence] in Genital specimen by Immunofluorescence
    }


class LabTestsDuringPregnancy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests conducted during pregnancy.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests conducted during pregnancy.

    **Exclusion Criteria:** Excludes concepts that represent an order only.

    ** Used in:** CMS153v10
    """

    VALUE_SET_NAME = "Lab Tests During Pregnancy"
    OID = "2.16.840.1.113883.3.464.1003.111.12.1007"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "15019-3",  # Alpha-1-Fetoprotein [Moles/volume] in Amniotic fluid
        "1832-5",  # Alpha-1-Fetoprotein [Mass/volume] in Amniotic fluid
        "1834-1",  # Alpha-1-Fetoprotein [Mass/volume] in Serum or Plasma
        "19171-8",  # Alpha-1-Fetoprotein [Units/volume] in Amniotic fluid
        "19176-7",  # Alpha-1-Fetoprotein [Units/volume] in Serum or Plasma
        "19177-5",  # Alpha-1-Fetoprotein [Moles/volume] in Serum or Plasma
        "20403-2",  # Fibronectin.fetal [Mass/volume] in Vaginal fluid
        "20404-0",  # Fibronectin.fetal [Presence] in Vaginal fluid
        "31993-9",  # Alpha-1-Fetoprotein [Presence] in Serum or Plasma
        "34493-7",  # PRF1 gene targeted mutation analysis in Amniotic fluid by Molecular genetics method
        "35457-1",  # Maternal cell contamination [Identifier] in Amniotic fluid Nominal
        "41067-0",  # PRF1 gene mutations found [Identifier] in Amniotic fluid by Molecular genetics method Nominal
        "41096-9",  # KEL gene allele [Genotype] in Amniotic fluid by Molecular genetics method Nominal
        "41273-4",  # Alpha-1-Fetoprotein interpretation in Amniotic fluid
        "41274-2",  # Alpha-1-Fetoprotein interpretation in Serum or Plasma
        "43798-8",  # Alpha-1-Fetoprotein [Presence] in Amniotic fluid
        "46989-0",  # CFTR gene targeted mutation analysis in Amniotic fluid by Molecular genetics method
        "48039-2",  # Fibronectin.fetal [Presence] in Specimen
        "48781-9",  # CYP21A2 gene mutations found [Identifier] in Amniotic fluid by Molecular genetics method Nominal
        "48802-3",  # Alpha-1-Fetoprotein panel - Serum or Plasma
        "49246-2",  # Alpha-1-Fetoprotein interpretation in Serum or Plasma Narrative
        "49318-9",  # Alpha-1-Fetoprotein interpretation in Amniotic fluid Narrative
        "83072-9",  # Alpha-1-Fetoprotein [Units/volume] in Serum or Plasma by Immunoassay
        "83073-7",  # Alpha-1-Fetoprotein [Mass/volume] in Serum or Plasma by Immunoassay
        "83075-2",  # Alpha-1-Fetoprotein [Mass/volume] in Amniotic fluid by Immunoassay
    }


class LabTestsForSexuallyTransmittedInfections(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests for sexually transmitted infections.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for sexually transmitted infections.

    **Exclusion Criteria:** Excludes concepts that represent an order only.

    ** Used in:** CMS153v10
    """

    VALUE_SET_NAME = "Lab Tests for Sexually Transmitted Infections"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1051"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "10705-2",  # Human papilloma virus Ag [Presence] in Tissue by Immune stain
        "11083-3",  # Human papilloma virus identified in Cervix
        "11084-1",  # Reagin Ab [Titer] in Serum
        "11481-9",  # Human papilloma virus identified in Specimen
        "11597-2",  # Treponema pallidum Ab [Units/volume] in Serum
        "12222-6",  # Human papilloma virus Ag [Presence] in Genital specimen
        "12223-4",  # Human papilloma virus 16+18 Ag [Presence] in Genital specimen
        "13288-6",  # Treponema pallidum Ab [Units/volume] in Blood by Immunofluorescence
        "13321-5",  # Human papilloma virus IgG Ab [Presence] in Serum
        "13322-3",  # Human papilloma virus IgM Ab [Presence] in Serum
        "14499-8",  # Human papilloma virus Ag [Presence] in Cervix
        "14500-3",  # Human papilloma virus Ag [Presence] in Vaginal fluid
        "14502-9",  # Human papilloma virus Ag [Presence] in Urethra
        "14503-7",  # Human papilloma virus 16+18 Ag [Presence] in Cervix
        "14504-5",  # Human papilloma virus 16+18 Ag [Presence] in Vaginal fluid
        "14506-0",  # Human papilloma virus 16+18 Ag [Presence] in Urethra
        "16280-0",  # Human papilloma virus DNA [Presence] in Specimen by Probe with amplification
        "17398-9",  # Human papilloma virus 11 Ag [Presence] in Specimen
        "17399-7",  # Human papilloma virus 16 Ag [Presence] in Specimen
        "17400-3",  # Human papilloma virus 16+18 Ag [Presence] in Specimen
        "17401-1",  # Human papilloma virus 18 Ag [Presence] in Specimen
        "17402-9",  # Human papilloma virus 31 Ag [Presence] in Specimen
        "17403-7",  # Human papilloma virus 31+33+35 Ag [Presence] in Specimen
        "17404-5",  # Human papilloma virus 33 Ag [Presence] in Specimen
        "17405-2",  # Human papilloma virus 42 Ag [Presence] in Specimen
        "17406-0",  # Human papilloma virus 43 Ag [Presence] in Specimen
        "17407-8",  # Human papilloma virus 44 Ag [Presence] in Specimen
        "17408-6",  # Human papilloma virus 45 Ag [Presence] in Specimen
        "17409-4",  # Human papilloma virus 5 Ag [Presence] in Specimen
        "17410-2",  # Human papilloma virus 51 Ag [Presence] in Specimen
        "17411-0",  # Human papilloma virus 6 Ag [Presence] in Specimen
        "17412-8",  # Human papilloma virus 6+11 Ag [Presence] in Specimen
        "17723-8",  # Treponema pallidum Ab [Presence] in Serum by Immobilization
        "17724-6",  # Treponema pallidum Ab [Units/volume] in Serum by Immunofluorescence
        "17725-3",  # Treponema pallidum Ab [Units/volume] in Serum by Latex agglutination
        "17726-1",  # Treponema pallidum IgG Ab [Presence] in Serum by Immunofluorescence
        "17727-9",  # Treponema pallidum IgG Ab [Units/volume] in Serum by Immunofluorescence
        "17728-7",  # Treponema pallidum IgM Ab [Units/volume] in Serum by Immunofluorescence
        "17729-5",  # Treponema pallidum IgM Ab [Presence] in Serum by Immunofluorescence
        "18478-8",  # Human papilloma virus 16+18 DNA [Presence] in Tissue by Probe
        "18479-6",  # Human papilloma virus 31+35+51 DNA [Presence] in Tissue by Probe
        "18480-4",  # Human papilloma virus 6+11 DNA [Presence] in Tissue by Probe
        "20507-0",  # Reagin Ab [Presence] in Serum by RPR
        "20508-8",  # Reagin Ab [Units/volume] in Serum by RPR
        "21414-8",  # Neisseria gonorrhoeae DNA [Presence] in Cervical mucus by NAA with probe detection
        "21415-5",  # Neisseria gonorrhoeae DNA [Presence] in Urethra by NAA with probe detection
        "21440-3",  # Human papilloma virus 16+18+31+33+35+45+51+52+56 DNA [Presence] in Cervix by Probe
        "21441-1",  # Human papilloma virus 6+11+42+43+44 DNA [Presence] in Cervix by Probe
        "22430-3",  # Neisseria gonorrhoeae Ab [Titer] in Serum
        "22434-5",  # Human papilloma virus Ab [Presence] in Tissue
        "22461-8",  # Reagin Ab [Presence] in Serum
        "22462-6",  # Reagin Ab [Units/volume] in Serum
        "22585-4",  # Treponema pallidum Ab [Units/volume] in Blood
        "22587-0",  # Treponema pallidum Ab [Presence] in Serum
        "22590-4",  # Treponema pallidum Ab [Titer] in Serum
        "22592-0",  # Treponema pallidum IgG Ab [Units/volume] in Serum
        "22594-6",  # Treponema pallidum IgM Ab [Units/volume] in Serum
        "24110-9",  # Treponema pallidum Ab [Presence] in Serum by Immunoassay
        "24111-7",  # Neisseria gonorrhoeae DNA [Presence] in Specimen by NAA with probe detection
        "24312-1",  # Treponema pallidum Ab [Presence] in Serum by Agglutination
        "26009-1",  # Treponema pallidum Ab [Titer] in Serum by Hemagglutination
        "29311-8",  # Neisseria gonorrhoeae Ag [Presence] in Specimen by Immunofluorescence
        "30167-1",  # Human papilloma virus 16+18+31+33+35+39+45+51+52+56+58+59+68 DNA [Presence] in Cervix by Probe with signal amplification
        "31147-2",  # Reagin Ab [Titer] in Serum by RPR
        "31905-3",  # Neisseria gonorrhoeae Ag [Presence] in Genital specimen
        "31906-1",  # Neisseria gonorrhoeae Ag [Presence] in Specimen
        "32047-3",  # Human papilloma virus 16+18+31+33+35+39+45+51+52+56+58+68+70 DNA [Presence] in Tissue by Probe
        "32198-4",  # Neisseria gonorrhoeae rRNA [Presence] in Cervix by Probe
        "32199-2",  # Neisseria gonorrhoeae rRNA [Presence] in Urethra by Probe
        "32704-9",  # Neisseria gonorrhoeae Ab [Presence] in Serum
        "32705-6",  # Neisseria gonorrhoeae DNA [Presence] in Vaginal fluid by NAA with probe detection
        "34147-9",  # Treponema pallidum IgG+IgM Ab [Presence] in Serum
        "34382-2",  # Treponema pallidum Ab [Titer] in Serum by Immunofluorescence
        "38372-9",  # Human papilloma virus 6+11+16+18+31+33+35+39+42+43+44+45+51+52+56+58+59+68 DNA [Presence] in Cervix by Probe with signal amplification
        "40679-3",  # Treponema pallidum IgG Ab [Presence] in Serum by Immunoblot
        "40680-1",  # Treponema pallidum IgM Ab [Presence] in Serum by Immunoblot
        "41122-3",  # Treponema pallidum Ab [Units/volume] in Specimen
        "42481-2",  # Human papilloma virus 6+11+42+43+44 DNA [Presence] in Cervix by Probe with signal amplification
        "43170-0",  # Human papilloma virus 31+33 DNA [Presence] in Tissue by Probe with signal amplification
        "43305-2",  # Neisseria gonorrhoeae rRNA [Presence] in Specimen by NAA with probe detection
        "43403-5",  # Neisseria gonorrhoeae DNA [Presence] in Specimen by Probe with signal amplification
        "44543-7",  # Human papilloma virus 31+33 Ag [Presence] in Specimen
        "44544-5",  # Human papilloma virus 35 Ag [Presence] in Specimen
        "44545-2",  # Human papilloma virus DNA [Presence] in Urethra by Probe
        "44546-0",  # Human papilloma virus DNA [Presence] in Vaginal fluid by Probe
        "44547-8",  # Human papilloma virus DNA [Presence] in Specimen by Probe with signal amplification
        "44548-6",  # Human papilloma virus DNA [Presence] in Urethra by Probe with signal amplification
        "44549-4",  # Human papilloma virus DNA [Presence] in Vaginal fluid by Probe with signal amplification
        "44550-2",  # Human papilloma virus DNA [Presence] in Cervix by Probe
        "44551-0",  # Human papilloma virus DNA [Presence] in Tissue by Probe
        "47236-5",  # Treponema pallidum IgG+IgM Ab [Presence] in Serum by Immunoassay
        "47237-3",  # Treponema pallidum IgM Ab [Presence] in Serum by Immunoassay
        "47238-1",  # Treponema pallidum IgG Ab [Presence] in Serum by Immunoassay
        "47387-6",  # Neisseria gonorrhoeae DNA [Presence] in Genital specimen by NAA with probe detection
        "48560-7",  # Human papilloma virus genotype [Identifier] in Specimen by NAA with probe detection
        "49891-5",  # Human papilloma virus DNA [Presence] in Specimen by NAA with probe detection
        "49896-4",  # Human papilloma virus 16+18+31+33+35+39+45+51+52+56+58+59+68 DNA [Presence] in Specimen by NAA with probe detection
        "5028-6",  # Neisseria gonorrhoeae rRNA [Presence] in Specimen by Probe
        "50326-8",  # Neisseria gonorrhoeae DNA [Presence] in Specimen from Donor by NAA with probe detection
        "50388-8",  # Neisseria gonorrhoeae rRNA [Presence] in Cervix by NAA with probe detection
        "50412-6",  # Neisseria gonorrhoeae rRNA [Presence] in Specimen from Donor by NAA with probe detection
        "50690-7",  # Reagin Ab [Titer] in Serum by VDRL
        "51838-1",  # Treponema pallidum IgG Ab [Units/volume] in Serum by Immunoassay
        "51839-9",  # Treponema pallidum IgM Ab [Units/volume] in Serum by Immunoassay
        "5291-0",  # Reagin Ab [Units/volume] in Serum by VDRL
        "5292-8",  # Reagin Ab [Presence] in Serum by VDRL
        "53762-1",  # Neisseria gonorrhoeae IgG Ab [Titer] in Serum
        "53879-3",  # Neisseria gonorrhoeae rRNA [Presence] in Vaginal fluid by NAA with probe detection
        "5392-6",  # Treponema pallidum Ab [Units/volume] in Serum by Immobilization
        "53927-0",  # Neisseria gonorrhoeae rRNA [Presence] in Urethra by NAA with probe detection
        "5393-4",  # Treponema pallidum Ab [Presence] in Serum by Immunofluorescence
        "5394-2",  # Treponema pallidum Ab [Titer] in Serum by Latex agglutination
        "55298-4",  # Human papilloma virus 6+11+42+43+44 DNA [Presence] in Urethra by Probe with signal amplification
        "55299-2",  # Human papilloma virus 6+11+42+43+44 DNA [Presence] in Specimen by Probe with signal amplification
        "57032-5",  # Treponema pallidum Ab [Presence] in Serum by Immunoblot
        "59263-4",  # Human papilloma virus 16 DNA [Presence] in Cervix by Probe with signal amplification
        "59264-2",  # Human papilloma virus 18 DNA [Presence] in Cervix by Probe with signal amplification
        "59420-0",  # Human papilloma virus 16+18+31+33+35+39+45+51+52+56+58+59+66+68 DNA [Presence] in Cervix by Probe with signal amplification
        "61372-9",  # Human papilloma virus 16 DNA [Presence] in Specimen by NAA with probe detection
        "61373-7",  # Human papilloma virus 18 DNA [Presence] in Specimen by NAA with probe detection
        "61374-5",  # Human papilloma virus 26 DNA [Presence] in Specimen by NAA with probe detection
        "61375-2",  # Human papilloma virus 31 DNA [Presence] in Specimen by NAA with probe detection
        "61376-0",  # Human papilloma virus 33 DNA [Presence] in Specimen by NAA with probe detection
        "61377-8",  # Human papilloma virus 35 DNA [Presence] in Specimen by NAA with probe detection
        "61378-6",  # Human papilloma virus 39 DNA [Presence] in Specimen by NAA with probe detection
        "61379-4",  # Human papilloma virus 44 DNA [Presence] in Specimen by NAA with probe detection
        "61380-2",  # Human papilloma virus 45 DNA [Presence] in Specimen by NAA with probe detection
        "61381-0",  # Human papilloma virus 51 DNA [Presence] in Specimen by NAA with probe detection
        "61382-8",  # Human papilloma virus 52 DNA [Presence] in Specimen by NAA with probe detection
        "61383-6",  # Human papilloma virus 53 DNA [Presence] in Specimen by NAA with probe detection
        "61384-4",  # Human papilloma virus 58 DNA [Presence] in Specimen by NAA with probe detection
        "61385-1",  # Human papilloma virus 59 DNA [Presence] in Specimen by NAA with probe detection
        "61386-9",  # Human papilloma virus 66 DNA [Presence] in Specimen by NAA with probe detection
        "61387-7",  # Human papilloma virus 67 DNA [Presence] in Specimen by NAA with probe detection
        "61388-5",  # Human papilloma virus 68 DNA [Presence] in Specimen by NAA with probe detection
        "61389-3",  # Human papilloma virus 69 DNA [Presence] in Specimen by NAA with probe detection
        "61390-1",  # Human papilloma virus 70 DNA [Presence] in Specimen by NAA with probe detection
        "61391-9",  # Human papilloma virus 73 DNA [Presence] in Specimen by NAA with probe detection
        "61392-7",  # Human papilloma virus 82 DNA [Presence] in Specimen by NAA with probe detection
        "61393-5",  # Human papilloma virus 6 DNA [Presence] in Specimen by NAA with probe detection
        "61394-3",  # Human papilloma virus 11 DNA [Presence] in Specimen by NAA with probe detection
        "61395-0",  # Human papilloma virus 42 DNA [Presence] in Specimen by NAA with probe detection
        "61396-8",  # Human papilloma virus 56 DNA [Presence] in Specimen by NAA with probe detection
        "63464-2",  # Treponema pallidum Ab [Units/volume] in Serum by Immunoassay
        "6487-3",  # Neisseria gonorrhoeae Ag [Presence] in Genital specimen by Immunoassay
        "6488-1",  # Neisseria gonorrhoeae Ag [Presence] in Genital specimen by Immunofluorescence
        "6489-9",  # Neisseria gonorrhoeae Ag [Presence] in Genital specimen by Latex agglutination
        "6490-7",  # Neisseria gonorrhoeae Ag [Presence] in Urethra
        "6510-2",  # Human papilloma virus Ab [Presence] in Genital specimen by Immunoassay
        "6511-0",  # Human papilloma virus Ab [Presence] in Genital specimen by Immunoblot
        "6512-8",  # Human papilloma virus Ab [Presence] in Tissue by Immunoassay
        "6513-6",  # Human papilloma virus Ab [Presence] in Tissue by Immunoblot
        "6514-4",  # Human papilloma virus rRNA [Presence] in Genital specimen by NAA with probe detection
        "6515-1",  # Human papilloma virus rRNA [Presence] in Tissue by NAA with probe detection
        "6516-9",  # Human papilloma virus rRNA [Presence] in Specimen by NAA with probe detection
        "6561-5",  # Treponema pallidum IgG Ab [Presence] in Serum
        "6562-3",  # Treponema pallidum IgM Ab [Presence] in Serum
        "688-2",  # Neisseria gonorrhoeae [Presence] in Cervix by Organism specific culture
        "690-8",  # Neisseria gonorrhoeae [Presence] in Endometrium by Organism specific culture
        "69002-4",  # Human papilloma virus E6+E7 mRNA [Presence] in Cervix by NAA with probe detection
        "691-6",  # Neisseria gonorrhoeae [Presence] in Genital specimen by Organism specific culture
        "692-4",  # Neisseria gonorrhoeae [Presence] in Genital lochia by Organism specific culture
        "693-2",  # Neisseria gonorrhoeae [Presence] in Vaginal fluid by Organism specific culture
        "697-3",  # Neisseria gonorrhoeae [Presence] in Urethra by Organism specific culture
        "698-1",  # Neisseria gonorrhoeae [Presence] in Specimen by Organism specific culture
        "70061-7",  # Human papilloma virus 16 and 18 DNA [Presence] in Specimen by NAA with probe detection
        "71431-1",  # Human papilloma virus 31+33+35+39+45+51+52+56+58+59+66+68 DNA [Presence] in Cervix by NAA with probe detection
        "71793-4",  # Treponema pallidum Ab [Titer] in Serum or Plasma by Agglutination
        "73732-0",  # Human papilloma virus 26+31+33+35+39+45+51+52+53+56+58+59+66+68+73+82 DNA [Presence] in Genital specimen by NAA with probe detection
        "73959-9",  # Human papilloma virus 16+18+31+33+35+39+45+51+52+56+58+66 DNA [Presence] in Tissue by Probe
        "75694-0",  # Human papilloma virus 18+45 E6+E7 mRNA [Presence] in Cervix by NAA with probe detection
        "77375-4",  # Human papilloma virus 31+33+35+39+45+51+52+56+58+59+66+68 DNA [Presence] in Specimen by NAA with probe detection
        "77399-4",  # Human papilloma virus 16 DNA [Presence] in Cervix by NAA with probe detection
        "77400-0",  # Human papilloma virus 18 DNA [Presence] in Cervix by NAA with probe detection
        "7975-6",  # Human papilloma virus Ab [Presence] in Genital specimen
        "8041-6",  # Treponema pallidum Ab [Presence] in Serum by Hemagglutination
        "82354-2",  # Human papilloma virus 16 and 18+45 E6+E7 mRNA [Identifier] in Cervix by NAA with probe detection
        "82456-5",  # Human papilloma virus 16 E6+E7 mRNA [Presence] in Cervix by NAA with probe detection
        "82675-0",  # Human papilloma virus 16+18+31+33+35+39+45+51+52+56+58+59+66+68 DNA [Presence] in Cervix by NAA with probe detection
        "86560-0",  # Human papilloma virus 16 DNA [Presence] in Tissue by NAA with probe detection
        "86561-8",  # Human papilloma virus 16+18+31+33+35+39+45+51+52+56+58+59+68 DNA [Presence] in Tissue by NAA with probe detection
        "86562-6",  # Human papilloma virus 18 DNA [Presence] in Tissue by NAA with probe detection
        "86563-4",  # Human papilloma virus 31+33+35+39+45+51+52+56+58+59+66+68 DNA [Presence] in Tissue by NAA with probe detection
        "86564-2",  # Human papilloma virus DNA [Presence] in Tissue by NAA with probe detection
        "91073-7",  # Human papilloma virus genotype [Identifier] in Tissue by NAA with probe detection
        "91851-6",  # Human papilloma virus genotype [Identifier] in Genital specimen by NAA with probe detection
        "91852-4",  # Human papilloma virus DNA [Presence] in Genital specimen by NAA with probe detection
        "91854-0",  # Human papilloma virus 18 DNA [Presence] in Genital specimen by NAA with probe detection
        "91855-7",  # Human papilloma virus 16+18+31+33+35+39+45+51+52+56+58+59+68 DNA [Presence] in Genital specimen by NAA with probe detection
        "91856-5",  # Human papilloma virus 16 DNA [Presence] in Genital specimen by NAA with probe detection
        "93777-1",  # Human papilloma virus 16+18 E6+E7 mRNA [Presence] in Tissue by Probe
        "93778-9",  # Human papilloma virus 6+11 E6+E7 mRNA [Presence] in Tissue by Probe
        "94425-6",  # Human papilloma virus E6+E7 mRNA [Presence] in Specimen by NAA with probe detection
        "95533-6",  # Human papilloma virus 56+59+66 DNA [Presence] in Cervix by NAA with probe detection
        "95534-4",  # Human papilloma virus 52 DNA [Presence] in Cervix by NAA with probe detection
        "95535-1",  # Human papilloma virus 51 DNA [Presence] in Cervix by NAA with probe detection
        "95536-9",  # Human papilloma virus 45 DNA [Presence] in Cervix by NAA with probe detection
        "95537-7",  # Human papilloma virus 35+39+68 DNA [Presence] in Cervix by NAA with probe detection
        "95538-5",  # Human papilloma virus 33+58 DNA [Presence] in Cervix by NAA with probe detection
        "95539-3",  # Human papilloma virus 31 DNA [Presence] in Cervix by NAA with probe detection
        "9568-7",  # Neisseria gonorrhoeae Ab [Titer] in Serum by Complement fixation
        "95938-7",  # Fetal Cerebellum Diameter transverse percentile per estimated gestational age
        "95939-5",  # Fetal Crown Rump length percentile per estimated gestational age
        "95940-3",  # Fetal Head Diameter.biparietal percentile per estimated gestational age
        "96124-3",  # Fetal femur diaphysis length percentile per estimated gestational age
        "96125-0",  # Fetal Abdomen Circumference Per estimated gestational age
        "96426-2",  # Fetal Nasal bone
        "96599-6",  # Neisseria gonorrhoeae DNA [Presence] in Cervix by NAA with probe detection
    }


class PregnancyTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for pregnancy tests.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for pregnancy including in urine, serum or plasma.

    **Exclusion Criteria:** Excludes concepts that represent an order only.

    ** Used in:** CMS153v10
    """

    VALUE_SET_NAME = "Pregnancy Test"
    OID = "2.16.840.1.113883.3.464.1003.111.12.1011"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "19080-1",  # Choriogonadotropin [Units/volume] in Serum or Plasma
        "19180-9",  # Choriogonadotropin.beta subunit free [Units/volume] in Serum or Plasma
        "20415-6",  # Choriogonadotropin.beta subunit [Units/volume] in Serum or Plasma by Immunoassay (EIA) 3rd IS
        "20994-0",  # Choriogonadotropin [Interpretation] in Serum or Plasma
        "2106-3",  # Choriogonadotropin (pregnancy test) [Presence] in Urine
        "2107-1",  # Choriogonadotropin [Moles/volume] in Urine
        "2110-5",  # Choriogonadotropin.beta subunit (pregnancy test) [Presence] in Serum or Plasma
        "2111-3",  # Choriogonadotropin.beta subunit [Moles/volume] in Serum or Plasma
        "2112-1",  # Choriogonadotropin.beta subunit (pregnancy test) [Presence] in Urine
        "2113-9",  # Choriogonadotropin.beta subunit [Mass/time] in 24 hour Urine
        "2114-7",  # Choriogonadotropin.beta subunit [Moles/volume] in Urine
        "2115-4",  # Choriogonadotropin.beta subunit free [Moles/volume] in Serum or Plasma
        "2118-8",  # Choriogonadotropin (pregnancy test) [Presence] in Serum or Plasma
        "2119-6",  # Choriogonadotropin [Moles/volume] in Serum or Plasma
        "21198-7",  # Choriogonadotropin.beta subunit [Units/volume] in Serum or Plasma
        "25372-4",  # Choriogonadotropin [Units/volume] in Urine
        "25373-2",  # Choriogonadotropin.beta subunit free [Mass/volume] in Serum or Plasma
        "34670-0",  # Choriogonadotropin [Mass/volume] in Serum or Plasma
        "45194-8",  # Choriogonadotropin.intact+Beta subunit [Units/volume] in Serum or Plasma
        "55869-2",  # Choriogonadotropin.beta subunit [Mass/volume] in Serum or Plasma
        "55870-0",  # Choriogonadotropin [Units/volume] in Cord blood
        "56497-1",  # Choriogonadotropin.beta subunit [Units] in 24 hour Urine
        "80384-1",  # Choriogonadotropin (pregnancy test) [Presence] in Urine by Rapid immunoassay
        "80385-8",  # Choriogonadotropin (pregnancy test) [Presence] in Serum by Rapid immunoassay
        "83086-9",  # Choriogonadotropin [Units/volume] in Serum or Plasma by Immunoassay
        "93769-8",  # Choriogonadotropin.intact+Beta subunit [Mass/volume] in Serum or Plasma
    }


class LaboratoryTestsForHypertension(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for lab  tests that are commonly performed on patients with hypertension.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent concepts for lab tests that are commonly performed on patients with hypertension.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS22v10
    """

    VALUE_SET_NAME = "Laboratory Tests for Hypertension"
    OID = "2.16.840.1.113883.3.600.1482"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "24320-4",  # Basic metabolic 1998 panel - Serum or Plasma
        "24321-2",  # Basic metabolic 2000 panel - Serum or Plasma
        "24323-8",  # Comprehensive metabolic 2000 panel - Serum or Plasma
        "24356-8",  # Urinalysis complete panel - Urine
        "24357-6",  # Urinalysis macro (dipstick) panel - Urine
        "24362-6",  # Renal function 2000 panel - Serum or Plasma
        "2888-6",  # Protein [Mass/volume] in Urine
        "57021-8",  # CBC W Auto Differential panel - Blood
        "57782-5",  # CBC W Ordered Manual Differential panel - Blood
        "58410-2",  # CBC panel - Blood by Automated count
    }


class LdlCholesterol(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests commonly used for low-density lipoproteins (LDL) cholesterol measurement.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent a laboratory test measuring low-density lipoprotein  cholesterol (LDL-C) using the specimen type of serum or plasma based on a measurement scale of mass per volume.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS347v5
    """

    VALUE_SET_NAME = "LDL Cholesterol"
    OID = "2.16.840.1.113883.3.526.3.1573"
    DEFINITION_VERSION = "20200307"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "13457-7",  # Cholesterol in LDL [Mass/volume] in Serum or Plasma by calculation
        "18261-8",  # Cholesterol in LDL [Mass/volume] in Serum or Plasma ultracentrifugate
        "18262-6",  # Cholesterol in LDL [Mass/volume] in Serum or Plasma by Direct assay
        "2089-1",  # Cholesterol in LDL [Mass/volume] in Serum or Plasma
        "43394-6",  # Cholesterol in LDL acylated [Mass/volume] in Serum or Plasma
        "49132-4",  # Cholesterol in LDL [Mass/volume] in Serum or Plasma by Electrophoresis
        "50193-2",  # Cholesterol in LDL.narrow density [Mass/volume] in Serum or Plasma
        "55440-2",  # Cholesterol.in LDL (real) [Mass/volume] in Serum or Plasma by VAP
        "86911-5",  # Cholesterol in LDL goal [Mass/volume] Serum or Plasma
        "90364-1",  # Cholesterol.in LDL.small dense [Mass/volume] in Serum by Immunoassay
        "91105-7",  # Cholesterol in LDL 1 [Mass/volume] in Serum or Plasma
        "91106-5",  # Cholesterol in LDL 2 [Mass/volume] in Serum or Plasma
        "91107-3",  # Cholesterol in LDL 3 [Mass/volume] in Serum or Plasma
        "91108-1",  # Cholesterol in LDL 4 [Mass/volume] in Serum or Plasma
        "91109-9",  # Cholesterol in LDL 5 [Mass/volume] in Serum or Plasma
        "91110-7",  # Cholesterol in LDL 6 [Mass/volume] in Serum or Plasma
        "91111-5",  # Cholesterol in LDL 7 [Mass/volume] in Serum or Plasma
        "96259-7",  # Cholesterol in LDL [Mass/volume] in Serum or Plasma by Calculated by Martin-Hopkins
        "96597-0",  # Cholesterol in LDL [Mass/volume] in DBS by Direct assay
    }


class HumanImmunodeficiencyVirusHivLaboratoryTestCodesAbAndAg(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests used for Human Immunodeficiency Virus (HIV) screening.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent a laboratory test for HIV-1 and HIV-2 antibodies or antigens.

    **Exclusion Criteria:** Excludes concepts that represent tests and procedures that might be associated with HIV infection but not used for screening or testing to establish an HIV diagnosis such as home/self HIV testing, HIV genotyping tests, HIV RNA tests, HIV cultures, clinical codes used to document care provided to HIV-infected patients.

    ** Used in:** CMS349v4
    """

    VALUE_SET_NAME = "Human Immunodeficiency Virus (HIV) Laboratory Test Codes (Ab and Ag)"
    OID = "2.16.840.1.113762.1.4.1056.50"
    DEFINITION_VERSION = "20210226"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "10901-7",  # HIV 2 gp125 Ab [Presence] in Serum by Immunoblot
        "10902-5",  # HIV 2 gp36 Ab [Presence] in Serum by Immunoblot
        "11078-3",  # HIV 2 gp80 Ab [Presence] in Serum by Immunoblot
        "11079-1",  # HIV 2 p26 Ab [Presence] in Serum by Immunoblot
        "11080-9",  # HIV 2 p53 Ab [Presence] in Serum by Immunoblot
        "11081-7",  # HIV 2 p56 Ab [Presence] in Serum by Immunoblot
        "11082-5",  # HIV 2 p68 Ab [Presence] in Serum by Immunoblot
        "12855-3",  # HIV 1 p23 Ab [Presence] in Serum by Immunoblot
        "12856-1",  # HIV 1 p65 Ab [Presence] in Serum by Immunoblot
        "12857-9",  # HIV 1 p28 Ab [Presence] in Serum by Immunoblot
        "12858-7",  # HIV 1 p32 Ab [Presence] in Serum by Immunoblot
        "12859-5",  # HIV 1 p18 Ab [Presence] in Serum by Immunoblot
        "12870-2",  # HIV 1 gp34 Ab [Presence] in Serum by Immunoblot
        "12871-0",  # HIV 1 p26 Ab [Presence] in Serum by Immunoblot
        "12872-8",  # HIV 1 p15 Ab [Presence] in Serum by Immunoblot
        "12875-1",  # HIV 1 p64 Ab [Presence] in Serum by Immunoblot
        "12876-9",  # HIV 1 p53 Ab [Presence] in Serum by Immunoblot
        "12893-4",  # HIV 1 gp105 Ab [Presence] in Serum by Immunoblot
        "12894-2",  # HIV 1 p68 Ab [Presence] in Serum by Immunoblot
        "12895-9",  # HIV 1 p58 Ab [Presence] in Serum by Immunoblot
        "13499-9",  # HIV 1 Ab band pattern [Interpretation] in Serum by Immunoblot
        "13920-4",  # HIV 2 p41 Ab [Presence] in Serum by Immunoblot
        "14092-1",  # HIV 1 Ab [Presence] in Serum by Immunofluorescence
        "14126-7",  # HIV 1 gp120+gp160 Ab [Presence] in Serum by Immunoblot
        "16132-3",  # HIV 1 p15+p18 Ab [Presence] in Serum by Immunoblot
        "16974-8",  # HIV 1 Ab [Presence] in Cerebral spinal fluid
        "16975-5",  # HIV 1 IgG Ab [Presence] in Serum
        "16976-3",  # HIV 1 Ag [Units/volume] in Serum
        "16977-1",  # HIV 1 Ag [Presence] in Cerebral spinal fluid
        "16978-9",  # HIV 1 p24 Ab [Units/volume] in Serum
        "16979-7",  # HIV 1 p24 Ag [Units/volume] in Cerebral spinal fluid
        "18396-2",  # HIV 1 p24 Ag [Presence] in Serum or Plasma by Immunoassay
        "19110-6",  # HIV 1 gp41+gp43 Ab [Presence] in Serum by Immunoblot
        "21007-0",  # HIV 1 Ab [Presence] in Serum from Donor
        "21331-4",  # HIV 1 p24 Ab [Titer] in Serum by Immunoblot
        "21332-2",  # HIV 1 p41 Ab [Titer] in Serum by Immunoblot
        "21334-8",  # HIV 2 gp105 Ab [Presence] in Serum by Immunoblot
        "21335-5",  # HIV 2 gp120 Ab [Presence] in Serum by Immunoblot
        "21336-3",  # HIV 2 gp15 Ab [Presence] in Serum by Immunoblot
        "21337-1",  # HIV 2 gp34 Ab [Presence] in Serum by Immunoblot
        "21338-9",  # HIV 2 p31 Ab [Presence] in Serum by Immunoblot
        "21339-7",  # HIV 2 p55 Ab [Presence] in Serum by Immunoblot
        "21340-5",  # HIV 2 p58 Ab [Presence] in Serum by Immunoblot
        "22356-0",  # HIV 1 Ab [Units/volume] in Serum
        "22357-8",  # HIV 1+2 Ab [Units/volume] in Serum
        "22358-6",  # HIV 2 Ab [Units/volume] in Serum
        "24012-7",  # HIV 1 Ag [Presence] in Serum
        "28004-0",  # HIV 1 IgG Ab [Presence] in Cerebral spinal fluid by Immunoblot
        "28052-9",  # HIV 1 IgG band pattern [Interpretation] in Cerebral spinal fluid by Immunoblot
        "29327-4",  # HIV 1 Ab [Presence] in Body fluid
        "29893-5",  # HIV 1 Ab [Presence] in Serum or Plasma by Immunoassay
        "30361-0",  # HIV 2 Ab [Presence] in Serum or Plasma by Immunoassay
        "31072-2",  # HIV 1 p41 Ab [Presence] in Serum by Immunoblot
        "31073-0",  # HIV 2 Ab band pattern [Interpretation] in Serum by Immunoblot
        "31201-7",  # HIV 1+2 Ab [Presence] in Serum or Plasma by Immunoassay
        "31430-2",  # HIV 1 IgG Ab [Presence] in Cerebral spinal fluid
        "32571-2",  # HIV 1 Ab [Presence] in Urine by Immunoblot
        "32602-5",  # HIV 1+2 Ab [Presence] in Cerebral spinal fluid
        "32827-8",  # HIV 1 p17+p18 Ab [Presence] in Serum by Immunoblot
        "32842-7",  # HIV 1 p17+p18 Ab [Presence] in Serum
        "33508-3",  # HIV 1 p65+p66 Ab [Presence] in Serum by Immunoblot
        "33660-2",  # HIV 1 p24 Ag [Presence] in Serum or Plasma by Neutralization test
        "33806-1",  # HIV 2 IgG Ab [Presence] in Serum by Immunoblot
        "33807-9",  # HIV 2 IgG Ab [Presence] in Serum
        "33866-5",  # HIV 1 Ab [Presence] in Capillary blood by Immunoassay
        "34591-8",  # HIV 1 Ab [Presence] in Body fluid by Immunoassay
        "34592-6",  # HIV 1 Ab [Presence] in Body fluid by Immunoblot
        "35437-3",  # HIV 1 Ab [Presence] in Saliva (oral fluid) by Immunoassay
        "35438-1",  # HIV 1 Ab [Units/volume] in Saliva (oral fluid) by Immunoassay
        "35439-9",  # HIV 1 Ab [Presence] in Saliva (oral fluid) by Immunoblot
        "35440-7",  # HIV 1 gp160 Ab [Presence] in Saliva (oral fluid) by Immunoblot
        "35441-5",  # HIV 1 gp120 Ab [Presence] in Saliva (oral fluid) by Immunoblot
        "35442-3",  # HIV 1 p66 Ab [Presence] in Saliva (oral fluid) by Immunoblot
        "35443-1",  # HIV 1 p65 Ab [Presence] in Saliva (oral fluid) by Immunoblot
        "35444-9",  # HIV 1 p55 Ab [Presence] in Saliva (oral fluid) by Immunoblot
        "35445-6",  # HIV 1 p51 Ab [Presence] in Saliva (oral fluid) by Immunoblot
        "35446-4",  # HIV 1 gp41 Ab [Presence] in Saliva (oral fluid) by Immunoblot
        "35447-2",  # HIV 1 p31 Ab [Presence] in Saliva (oral fluid) by Immunoblot
        "35448-0",  # HIV 1 p24 Ab [Presence] in Saliva (oral fluid) by Immunoblot
        "35449-8",  # HIV 1 p17 Ab [Presence] in Saliva (oral fluid) by Immunoblot
        "35450-6",  # HIV 1 p18 Ab [Presence] in Saliva (oral fluid) by Immunoblot
        "35452-2",  # HIV 1 gp40 Ab [Presence] in Serum by Immunoblot
        "35564-4",  # HIV 1 p31+p32 Ab [Presence] in Serum by Immunoblot
        "35565-1",  # HIV 1 p40 Ab [Presence] in Serum by Immunoblot
        "40437-6",  # HIV 1 p24 Ab [Presence] in Serum or Plasma by Immunoassay
        "40438-4",  # HIV 1 gp41 Ab [Presence] in Serum or Plasma by Immunoassay
        "40439-2",  # HIV 1 gp120+gp160 Ab [Presence] in Serum or Plasma by Immunoassay
        "40732-0",  # HIV 1 IgG Ab [Presence] in Serum by Immunoblot
        "40733-8",  # HIV 1+2 IgG Ab [Presence] in Serum or Plasma by Immunoassay
        "41143-9",  # HIV 1 Ab [Units/volume] in Saliva (oral fluid)
        "41144-7",  # HIV 1 Ab [Presence] in Saliva (oral fluid)
        "41145-4",  # HIV 1 Ab [Presence] in Capillary blood
        "41290-8",  # HIV 1+2 IgM Ab [Units/volume] in Serum or Plasma by Immunoassay
        "42339-2",  # HIV 1 p24 Ag [Mass/volume] in Serum or Plasma by Immunoassay
        "42600-7",  # HIV 1+2 Ab [Presence] in Specimen by Immunoassay
        "42627-0",  # HIV 1 Ab [Presence] in Cerebral spinal fluid by Immunofluorescence
        "42768-2",  # HIV 1 and 2 Ab [Interpretation] in Serum Narrative
        "43008-2",  # HIV 1+2 IgM Ab [Units/volume] in Serum
        "43009-0",  # HIV 1+2 IgG Ab [Presence] in Serum
        "43010-8",  # HIV 1+2 Ab [Presence] in Specimen
        "43011-6",  # HIV 1 p24 Ab [Presence] in Serum
        "43012-4",  # HIV 1 gp41 Ab [Presence] in Serum
        "43013-2",  # HIV 1 gp120+gp160 Ab [Presence] in Serum
        "43185-8",  # HIV 1 and 2 Ab band pattern [Interpretation] in Serum by Immunoblot
        "43599-0",  # HIV 1 Ab [Units/volume] in Serum by Immunofluorescence
        "44531-2",  # HIV 1 Ag [Presence] in Serum from Donor
        "44532-0",  # HIV 1 gp120 Ab [Presence] in Serum
        "44533-8",  # HIV 1+2 Ab [Presence] in Serum from Donor
        "44607-0",  # HIV 1 [Interpretation] in Serum or Plasma by Immunoassay
        "44872-0",  # HIV 1 p24 Ag [Presence] in Serum or Plasma from Donor by Immunoassay
        "44873-8",  # HIV 1+2 Ab [Presence] in Serum by Immunoblot
        "45212-8",  # HIV 2 p31+p34 Ab [Presence] in Serum by Immunoblot
        "47029-4",  # HIV 2 Ab [Presence] in Cerebral spinal fluid by Immunoblot
        "48345-3",  # HIV 1+O+2 Ab [Presence] in Serum or Plasma
        "48346-1",  # HIV 1+O+2 Ab [Units/volume] in Serum or Plasma
        "49483-1",  # HIV 1 [Interpretation] in Serum or Plasma by Immunoassay Narrative
        "49580-4",  # HIV 1+2 Ab [Presence] in Specimen by Rapid immunoassay
        "49718-0",  # HIV 1 p24 Ag [Presence] in Cerebral spinal fluid
        "49905-3",  # HIV 1 Ab [Presence] in Specimen by Rapid immunoassay
        "49965-7",  # Deprecated HIV 1 Ab/HIV 2 Ab Ab [Ratio] in Serum by Immunoblot (IB)
        "51786-2",  # HIV 2 Ab Signal/Cutoff in Serum or Plasma by Immunoassay
        "51866-2",  # Deprecated HIV 1 Ab+Ag [Presence] in Serum
        "5220-9",  # HIV 1 Ab [Units/volume] in Serum or Plasma by Immunoassay
        "5221-7",  # HIV 1 Ab [Presence] in Serum or Plasma by Immunoblot
        "5222-5",  # HIV 1 Ag [Presence] in Serum or Plasma by Immunoassay
        "5223-3",  # HIV 1+2 Ab [Units/volume] in Serum or Plasma by Immunoassay
        "5224-1",  # HIV 2 Ab [Units/volume] in Serum or Plasma by Immunoassay
        "5225-8",  # HIV 2 Ab [Presence] in Serum by Immunoblot
        "53379-4",  # HIV 1 Ab [Presence] in Specimen
        "53601-1",  # HIV 1 p24 Ag [Units/volume] in Serum or Plasma by Immunoassay
        "54086-4",  # HIV 1+2 IgG Ab [Presence] in DBS
        "56888-1",  # HIV 1+2 Ab+HIV1 p24 Ag [Presence] in Serum or Plasma by Immunoassay
        "57974-8",  # HIV 1 Ab [Presence] in Cerebral spinal fluid by Immunoblot
        "57975-5",  # HIV 1+O+2 Ab [Presence] in Body fluid
        "57976-3",  # HIV 2 gp140 Ab [Presence] in Serum by Immunoblot
        "57977-1",  # HIV 2 p16 Ab [Presence] in Serum by Immunoblot
        "57978-9",  # HIV 2 p34 Ab [Presence] in Serum by Immunoblot
        "58900-2",  # HIV 1+2 Ab+HIV1 p24 Ag [Units/volume] in Serum or Plasma by Immunoassay
        "62456-9",  # HIV 2 p15 Ab [Presence] in Serum by Immunoblot
        "68961-2",  # HIV 1 Ab [Presence] in Serum, Plasma or Blood by Rapid immunoassay
        "69668-2",  # HIV 1 and 2 Ab [Identifier] in Serum or Plasma by Rapid immunoassay
        "73905-2",  # HIV 1+2 IgG Ab [Presence] in Serum or Plasma by Rapid immunoassay
        "73906-0",  # HIV 1+2 IgG Ab [Presence] in Blood by Rapid immunoassay
        "75622-1",  # HIV 1 and 2 tests - Meaningful Use set
        "75666-8",  # HIV 1+2 Ab and HIV1 p24 Ag [Identifier] in Serum, Plasma or Blood by Rapid immunoassay
        "77685-6",  # HIV 1 and 2 IgG Ab [Identifier] in Serum or Plasma by Immunoblot
        "7917-8",  # HIV 1 Ab [Presence] in Serum
        "7918-6",  # HIV 1+2 Ab [Presence] in Serum
        "7919-4",  # HIV 2 Ab [Presence] in Serum
        "80203-3",  # HIV 1 and 2 Ab [Identifier] in Serum, Plasma or Blood by Rapid immunoassay
        "80387-4",  # HIV 1+2 Ab [Presence] in Serum, Plasma or Blood by Rapid immunoassay
        "81641-3",  # HIV 2 Ab [Presence] in Serum, Plasma or Blood by Rapid immunoassay
        "83101-6",  # HIV 1+2 Ab and HIV1 p24 Ag panel - Serum or Plasma by Immunoassay
        "85037-0",  # HIV 1 and 2 Ab and HIV 1 p24 Ag panel - Serum or Plasma by Immunoassay
        "85686-4",  # HIV 1 Ab [Presence] in Serum, Plasma or Blood by Immunofluorescence
        "86233-4",  # HIV 1 Ab [Presence] in Serum, Plasma or Blood by Immunoblot
        "86657-4",  # HIV 1 and 2 tests - FPAR 2.0 set
        "89365-1",  # HIV 1 and 2 Ab panel - Serum, Plasma or Blood by Rapid immunoassay
        "89374-3",  # HIV 1 Ab [Presence] in Specimen by Immunoassay
        "9660-2",  # HIV 1 gp160 Ab [Presence] in Serum by Immunoblot
        "9661-0",  # HIV 1 gp120 Ab [Presence] in Serum by Immunoblot
        "9662-8",  # HIV 1 gp41 Ab [Presence] in Serum by Immunoblot
        "9663-6",  # HIV 1 p17 Ab [Presence] in Serum by Immunoblot
        "9664-4",  # HIV 1 p24 Ab [Presence] in Serum by Immunoblot
        "9665-1",  # HIV 1 p24 Ag [Units/volume] in Serum
        "9666-9",  # HIV 1 p31 Ab [Presence] in Serum by Immunoblot
        "9667-7",  # HIV 1 p51 Ab [Presence] in Serum by Immunoblot
        "9668-5",  # HIV 1 p55 Ab [Presence] in Serum by Immunoblot
        "9669-3",  # HIV 1 p66 Ab [Presence] in Serum by Immunoblot
        "9821-0",  # HIV 1 p24 Ag [Presence] in Serum
    }


__exports__ = get_overrides(locals().copy())
