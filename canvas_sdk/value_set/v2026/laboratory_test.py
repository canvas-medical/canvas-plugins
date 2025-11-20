from ..value_set import ValueSet

class HematocritLabTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests measuring hematocrit.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent a laboratory test measuring hematocrit in the specimen source of blood.

    **Exclusion Criteria:** Excludes concepts that represent laboratory tests for hematocrit using the specimen source of capillary blood.
    """

    VALUE_SET_NAME = "Hematocrit Lab Test"
    OID = "2.16.840.1.113762.1.4.1045.114"
    DEFINITION_VERSION = "20250207"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "104826-3",  # Hematocrit [Pure volume fraction] of Blood
        "20570-8",  # Hematocrit [Volume Fraction] of Blood
        "31100-1",  # Hematocrit [Volume Fraction] of Blood by Impedance
        "32354-3",  # Hematocrit [Volume Fraction] of Arterial blood
        "41654-5",  # Hematocrit [Volume Fraction] of Venous blood
        "41655-2",  # Hematocrit [Volume Fraction] of Mixed venous blood
        "4544-3",  # Hematocrit [Volume Fraction] of Blood by Automated count
        "4545-0",  # Hematocrit [Volume Fraction] of Blood by Centrifugation
        "48703-3",  # Hematocrit [Volume Fraction] of Blood by Estimated
        "71829-6",  # Hematocrit [Pure volume fraction] of Venous blood
        "71830-4",  # Hematocrit [Pure volume fraction] of Mixed venous blood
        "71832-0",  # Hematocrit [Pure volume fraction] of Arterial blood
        "71833-8",  # Hematocrit [Pure volume fraction] of Blood by Automated count
    }

class WhiteBloodCellsCountLabTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests measuring white blood cells.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent a laboratory test measuring white blood cell count in the specimen source of blood.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "White Blood Cells Count Lab Test"
    OID = "2.16.840.1.113762.1.4.1045.129"
    DEFINITION_VERSION = "20230214"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "12227-5",  # Leukocytes [#/volume] corrected for nucleated erythrocytes in Blood
        "26464-8",  # Leukocytes [#/volume] in Blood
        "33256-9",  # Leukocytes [#/volume] corrected for nucleated erythrocytes in Blood by Automated count
        "49498-9",  # Leukocytes [#/volume] in Blood by Estimate
        "6690-2",  # Leukocytes [#/volume] in Blood by Automated count
        "804-5",  # Leukocytes [#/volume] in Blood by Manual count
        "92635-2",  # Leukocytes [#/volume] in Buffy Coat
    }

class Inr(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory test for international normalized ratio (INR).

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent a laboratory test of INR (International Normalized Ratio).

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "INR"
    OID = "2.16.840.1.113883.3.117.1.7.1.213"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "34714-6",  # INR in Blood by Coagulation assay
        "38875-1",  # INR in Platelet poor plasma or blood by Coagulation assay
        "46418-0",  # INR in Capillary blood by Coagulation assay
        "52129-4",  # INR in Platelet poor plasma by Coagulation assay --post heparin neutralization
        "6301-6",  # INR in Platelet poor plasma by Coagulation assay
    }

class GlycemicScreeningTests(ValueSet):
    """
    **Clinical Focus:** Screening for pre-diabetes

    **Data Element Scope:** Allowable glycemic tests for pre-diabetes screening

    **Inclusion Criteria:** Fasting plasma glucose, 2-h plasma glucose during a 75g oral glucose tolerance test (GTT), or A1C

    **Exclusion Criteria:** Glycemic tests not specified as "fasting" are excluded. Note: Fasting designation not required for GTT or A1C
    """

    VALUE_SET_NAME = "Glycemic Screening Tests"
    OID = "2.16.840.1.113762.1.4.1160.5"
    DEFINITION_VERSION = "20230107"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "3044F",  # Most recent hemoglobin A1c (HbA1c) level less than 7.0% (DM)
        "3046F",  # Most recent hemoglobin A1c level greater than 9.0% (DM)
        "3051F",  # Most recent hemoglobin A1c (HbA1c) level greater than or equal to 7.0% and less than 8.0% (DM)
        "3052F",  # Most recent hemoglobin A1c (HbA1c) level greater than or equal to 8.0% and less than or equal to 9.0% (DM)
        "82947",  # Glucose; quantitative, blood (except reagent strip)
        "82951",  # Glucose; tolerance test (GTT), 3 specimens (includes glucose)
        "83036",  # Hemoglobin; glycosylated (A1C)
    }

    LOINC = {
        "10450-5",  # Glucose [Mass/volume] in Serum or Plasma --10 hours fasting
        "14995-5",  # Glucose [Moles/volume] in Serum or Plasma --2 hours post 75 g glucose PO
        "1518-0",  # Glucose [Mass/volume] in Serum or Plasma --2 hours post 75 g glucose PO
        "1554-5",  # Glucose [Mass/volume] in Serum or Plasma --12 hours fasting
        "1557-8",  # Fasting glucose [Mass/volume] in Venous blood
        "1558-6",  # Fasting glucose [Mass/volume] in Serum or Plasma
        "17855-8",  # Hemoglobin A1c/Hemoglobin.total in Blood by calculation
        "17856-6",  # Hemoglobin A1c/Hemoglobin.total in Blood by HPLC
        "2345-7",  # Glucose [Mass/volume] in Serum or Plasma
        "4548-4",  # Hemoglobin A1c/Hemoglobin.total in Blood
        "4549-2",  # Hemoglobin A1c/Hemoglobin.total in Blood by Electrophoresis
        "96595-4",  # Hemoglobin A1c/Hemoglobin.total in DBS
    }

class HivViralLoadTests(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests associated with detecting the presence of HIV viral load.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent a laboratory test for detecting HIV viral load.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "HIV Viral Load Tests"
    OID = "2.16.840.1.113762.1.4.1248.377"
    DEFINITION_VERSION = "20250328"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "10351-5",  # HIV 1 RNA [Units/volume] (viral load) in Serum or Plasma by Probe with amplification
        "104762-0",  # HIV 1 RNA [Log #/volume] in Serum or Plasma by Molecular genetics method
        "104781-0",  # HIV 1 RNA [#/volume] in Serum or Plasma by Molecular genetics method
        "20447-9",  # HIV 1 RNA [#/volume] (viral load) in Serum or Plasma by NAA with probe detection
        "21008-8",  # HIV 1 RNA [#/volume] (viral load) in Serum or Plasma by Probe
        "21333-0",  # HIV 1 RNA [#/volume] in Serum
        "23876-6",  # HIV 1 RNA [Units/volume] (viral load) in Plasma by Probe with signal amplification
        "29539-4",  # HIV 1 RNA [Log #/volume] (viral load) in Plasma by Probe with signal amplification
        "29541-0",  # HIV 1 RNA [Log #/volume] (viral load) in Serum or Plasma by NAA with probe detection
        "41514-1",  # HIV 1 RNA [Log #/volume] (viral load) in Serum or Plasma by Probe with amplification detection limit = 2.6 log copies/mL
        "41515-8",  # HIV 1 RNA [#/volume] (viral load) in Serum or Plasma by Probe with amplification detection limit = 75 copies/mL
        "41516-6",  # HIV 1 RNA [Log #/volume] (viral load) in Serum or Plasma by Probe with amplification detection limit = 1.9 log copies/mL
        "48510-2",  # HIV 1 RNA [Log #/volume] (viral load) in Serum or Plasma by Probe and target amplification method detection limit = 1.7 log copies/mL
        "48511-0",  # HIV 1 RNA [#/volume] (viral load) in Serum or Plasma by Probe and target amplification method detection limit = 50 copies/mL
        "48552-4",  # HIV 1 RNA [Log #/volume] (viral load) in Serum or Plasma by Probe and target amplification method detection limit = 2.6 log copies/mL
        "51780-5",  # HIV 1 RNA [Log #/volume] (viral load) in Serum or Plasma by Probe and target amplification method detection limit = 0.5 log copies/mL
        "59419-2",  # HIV 1 RNA [#/volume] (viral load) in Plasma by Probe with signal amplification
        "62469-2",  # HIV 1 RNA [Units/volume] (viral load) in Serum or Plasma by NAA with probe detection
        "69354-9",  # HIV 2 RNA [Units/volume] (viral load) in Serum or Plasma by NAA with probe detection
        "70241-5",  # HIV 1 RNA [#/volume] (viral load) in Plasma by Probe and target amplification method detection limit = 20 copies/mL
    }

class ChlamydiaScreening(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for chlamydia tests.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent screening for chlamydia infections.

    **Exclusion Criteria:** Excludes concepts that represent an order only.
    """

    VALUE_SET_NAME = "Chlamydia Screening"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1052"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "14463-4",  # Chlamydia trachomatis [Presence] in Cervix by Organism specific culture
        "14464-2",  # Chlamydia trachomatis [Presence] in Vaginal fluid by Organism specific culture
        "14465-9",  # Chlamydia trachomatis [Presence] in Urethra by Organism specific culture
        "14467-5",  # Chlamydia trachomatis [Presence] in Urine sediment by Organism specific culture
        "14474-1",  # Chlamydia trachomatis Ag [Presence] in Urine sediment by Immunoassay
        "14513-6",  # Chlamydia trachomatis Ag [Presence] in Urine sediment by Immunofluorescence
        "16600-9",  # Chlamydia trachomatis rRNA [Presence] in Genital specimen by Probe
        "21190-4",  # Chlamydia trachomatis DNA [Presence] in Cervix by NAA with probe detection
        "21191-2",  # Chlamydia trachomatis DNA [Presence] in Urethra by NAA with probe detection
        "21613-5",  # Chlamydia trachomatis DNA [Presence] in Specimen by NAA with probe detection
        "23838-6",  # Chlamydia trachomatis rRNA [Presence] in Genital fluid by Probe
        "31775-0",  # Chlamydia trachomatis Ag [Presence] in Urine sediment
        "34710-4",  # Chlamydia trachomatis Ag [Presence] in Anal
        "42931-6",  # Chlamydia trachomatis rRNA [Presence] in Urine by NAA with probe detection
        "43304-5",  # Chlamydia trachomatis rRNA [Presence] in Specimen by NAA with probe detection
        "43404-3",  # Chlamydia trachomatis DNA [Presence] in Specimen by Probe with signal amplification
        "44806-8",  # Chlamydia trachomatis+Neisseria gonorrhoeae DNA [Presence] in Urine by NAA with probe detection
        "44807-6",  # Chlamydia trachomatis+Neisseria gonorrhoeae DNA [Presence] in Genital specimen by NAA with probe detection
        "45068-4",  # Chlamydia trachomatis+Neisseria gonorrhoeae DNA [Presence] in Cervix by NAA with probe detection
        "45069-2",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Genital specimen by Probe
        "45072-6",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Anal by Probe
        "45073-4",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Tissue by Probe
        "45075-9",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Urethra by Probe
        "45084-1",  # Chlamydia trachomatis DNA [Presence] in Vaginal fluid by NAA with probe detection
        "45089-0",  # Chlamydia trachomatis rRNA [Presence] in Anal by Probe
        "45090-8",  # Chlamydia trachomatis DNA [Presence] in Anal by NAA with probe detection
        "45091-6",  # Chlamydia trachomatis Ag [Presence] in Genital specimen
        "45093-2",  # Chlamydia trachomatis [Presence] in Anal by Organism specific culture
        "45095-7",  # Chlamydia trachomatis [Presence] in Genital specimen by Organism specific culture
        "4993-2",  # Chlamydia trachomatis rRNA [Presence] in Specimen by Probe
        "50387-0",  # Chlamydia trachomatis rRNA [Presence] in Cervix by NAA with probe detection
        "53925-4",  # Chlamydia trachomatis rRNA [Presence] in Urethra by NAA with probe detection
        "53926-2",  # Chlamydia trachomatis rRNA [Presence] in Vaginal fluid by NAA with probe detection
        "57287-5",  # Chlamydia trachomatis rRNA [Presence] in Anal by NAA with probe detection
        "6353-7",  # Chlamydia trachomatis Ag [Presence] in Tissue by Immunofluorescence
        "6356-0",  # Chlamydia trachomatis DNA [Presence] in Genital specimen by NAA with probe detection
        "6357-8",  # Chlamydia trachomatis DNA [Presence] in Urine by NAA with probe detection
        "80360-1",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Urine by NAA with probe detection
        "80361-9",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Cervix by NAA with probe detection
        "80362-7",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Vaginal fluid by NAA with probe detection
        "80363-5",  # Chlamydia trachomatis DNA [Presence] in Anorectal by NAA with probe detection
        "80364-3",  # Chlamydia trachomatis rRNA [Presence] in Anorectal by NAA with probe detection
        "80365-0",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Anorectal by NAA with probe detection
        "80367-6",  # Chlamydia trachomatis [Presence] in Anorectal by Organism specific culture
        "82306-2",  # Chlamydia trachomatis rRNA [Presence] in Throat by NAA with probe detection
        "87949-4",  # Chlamydia trachomatis DNA [Presence] in Tissue by NAA with probe detection
        "87950-2",  # Chlamydia trachomatis [Presence] in Tissue by Organism specific culture
        "88221-7",  # Chlamydia trachomatis DNA [Presence] in Throat by NAA with probe detection
        "89648-0",  # Chlamydia trachomatis [Presence] in Throat by Organism specific culture
        "91860-7",  # Chlamydia trachomatis Ag [Presence] in Genital specimen by Immunofluorescence
        "91873-0",  # Chlamydia trachomatis Ag [Presence] in Throat by Immunofluorescence
    }

class GonorrheaScreening(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent lab test concepts for gonorrhea.

    **Data Element Scope:** This value set may use a model element of Laboratory Test Performed.

    **Inclusion Criteria:** Includes codes that capture a combination of gonorrhea and chlamydia testing.

    **Exclusion Criteria:** None
    """

    VALUE_SET_NAME = "Gonorrhea Screening"
    OID = "2.16.840.1.113762.1.4.1258.1"
    DEFINITION_VERSION = "20250208"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "104765-3",  # Neisseria gonorrhoeae DNA [Presence] in Specimen by Molecular genetics method
        "104780-2",  # Neisseria gonorrhoeae rRNA [Presence] in Specimen by Molecular genetics method
        "105085-5",  # Neisseria gonorrhoeae rRNA [Presence] in Specimen
        "105922-9",  # Neisseria gonorrhoeae DNA [Presence] in Semen by NAA with probe detection
        "21415-5",  # Neisseria gonorrhoeae DNA [Presence] in Urethra by NAA with probe detection
        "21416-3",  # Neisseria gonorrhoeae DNA [Presence] in Urine by NAA with probe detection
        "24111-7",  # Neisseria gonorrhoeae DNA [Presence] in Specimen by NAA with probe detection
        "32705-6",  # Neisseria gonorrhoeae DNA [Presence] in Vaginal fluid by NAA with probe detection
        "33904-4",  # Neisseria gonorrhoeae rRNA [Presence] in Conjunctival specimen by Probe
        "35735-0",  # Neisseria gonorrhoeae DNA [Presence] in Conjunctival specimen by NAA with probe detection
        "36902-5",  # Chlamydia trachomatis+Neisseria gonorrhoeae DNA [Presence] in Specimen by NAA with probe detection
        "36903-3",  # Chlamydia trachomatis and Neisseria gonorrhoeae DNA [Identifier] in Specimen by NAA with probe detection
        "43305-2",  # Neisseria gonorrhoeae rRNA [Presence] in Specimen by NAA with probe detection
        "43403-5",  # Neisseria gonorrhoeae DNA [Presence] in Specimen by Probe with signal amplification
        "43405-0",  # Chlamydia trachomatis and Neisseria gonorrhoeae DNA [Identifier] in Specimen by Probe with signal amplification
        "43406-8",  # Chlamydia trachomatis+Neisseria gonorrhoeae DNA [Presence] in Specimen by Probe with signal amplification
        "44806-8",  # Chlamydia trachomatis+Neisseria gonorrhoeae DNA [Presence] in Urine by NAA with probe detection
        "44807-6",  # Chlamydia trachomatis+Neisseria gonorrhoeae DNA [Presence] in Genital specimen by NAA with probe detection
        "45068-4",  # Chlamydia trachomatis+Neisseria gonorrhoeae DNA [Presence] in Cervix by NAA with probe detection
        "45069-2",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Genital specimen by Probe
        "45072-6",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Anal by Probe
        "45073-4",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Tissue by Probe
        "45075-9",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Urethra by Probe
        "45076-7",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Specimen by Probe
        "47387-6",  # Neisseria gonorrhoeae DNA [Presence] in Genital specimen by NAA with probe detection
        "5028-6",  # Neisseria gonorrhoeae rRNA [Presence] in Specimen by Probe
        "50388-8",  # Neisseria gonorrhoeae rRNA [Presence] in Cervix by NAA with probe detection
        "53879-3",  # Neisseria gonorrhoeae rRNA [Presence] in Vaginal fluid by NAA with probe detection
        "53927-0",  # Neisseria gonorrhoeae rRNA [Presence] in Urethra by NAA with probe detection
        "57180-2",  # Neisseria gonorrhoeae DNA [Presence] in Nasopharynx by NAA with probe detection
        "57289-1",  # Neisseria gonorrhoeae rRNA [Presence] in Nasopharynx by NAA with probe detection
        "57458-2",  # Neisseria gonorrhoeae rRNA [Presence] in Anal by NAA with probe detection
        "60255-7",  # Neisseria gonorrhoeae rRNA [Presence] in Throat by NAA with probe detection
        "60256-5",  # Neisseria gonorrhoeae rRNA [Presence] in Urine by NAA with probe detection
        "80360-1",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Urine by NAA with probe detection
        "80361-9",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Cervix by NAA with probe detection
        "80362-7",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Vaginal fluid by NAA with probe detection
        "80365-0",  # Chlamydia trachomatis+Neisseria gonorrhoeae rRNA [Presence] in Anorectal by NAA with probe detection
        "80366-8",  # Neisseria gonorrhoeae rRNA [Presence] in Anorectal by NAA with probe detection
        "88224-1",  # Neisseria gonorrhoeae DNA [Presence] in Anorectal by NAA with probe detection
        "88225-8",  # Neisseria gonorrhoeae DNA [Presence] in Throat by NAA with probe detection
        "96599-6",  # Neisseria gonorrhoeae DNA [Presence] in Cervix by NAA with probe detection
        "97626-6",  # Neisseria gonorrhoeae DNA [Presence] in Synovial fluid by NAA with non-probe detection
        "99779-1",  # Neisseria gonorrhoeae rRNA [Presence] in Conjunctival specimen by NAA with probe detection
    }

class SyphilisTests(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for syphilis testing.

    **Data Element Scope:** This value set may use a model element related to Observation.

    **Inclusion Criteria:** Includes concepts that identify tests conducted at the point of care, rapid testing, or laboratory tests to detect syphilis.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Syphilis Tests"
    OID = "2.16.840.1.113762.1.4.1248.389"
    DEFINITION_VERSION = "20250404"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "11084-1",  # Reagin Ab [Titer] in Serum
        "11597-2",  # Treponema pallidum Ab [Units/volume] in Serum
        "13288-6",  # Treponema pallidum Ab [Units/volume] in Blood by Immunofluorescence
        "14904-7",  # Reagin Ab [Presence] in Specimen by VDRL
        "17723-8",  # Treponema pallidum Ab [Presence] in Serum by Immobilization
        "17724-6",  # Treponema pallidum Ab [Units/volume] in Serum by Immunofluorescence
        "17725-3",  # Treponema pallidum Ab [Units/volume] in Serum by Latex agglutination
        "17726-1",  # Treponema pallidum IgG Ab [Presence] in Serum by Immunofluorescence
        "17727-9",  # Treponema pallidum IgG Ab [Units/volume] in Serum by Immunofluorescence
        "17728-7",  # Treponema pallidum IgM Ab [Units/volume] in Serum by Immunofluorescence
        "17729-5",  # Treponema pallidum IgM Ab [Presence] in Serum by Immunofluorescence
        "20507-0",  # Reagin Ab [Presence] in Serum by RPR
        "20508-8",  # Reagin Ab [Units/volume] in Serum or Plasma by RPR
        "22461-8",  # Reagin Ab [Presence] in Serum
        "22462-6",  # Reagin Ab [Units/volume] in Serum
        "22464-2",  # Reagin Ab [Presence] in Specimen
        "22585-4",  # Treponema pallidum Ab [Units/volume] in Blood
        "22587-0",  # Treponema pallidum Ab [Presence] in Serum
        "22590-4",  # Treponema pallidum Ab [Titer] in Serum
        "22592-0",  # Treponema pallidum IgG Ab [Units/volume] in Serum
        "22594-6",  # Treponema pallidum IgM Ab [Units/volume] in Serum
        "24110-9",  # Treponema pallidum Ab [Presence] in Serum by Immunoassay
        "24312-1",  # Treponema pallidum Ab [Presence] in Serum by Agglutination
        "26009-1",  # Treponema pallidum Ab [Titer] in Serum by Hemagglutination
        "29310-0",  # Treponema pallidum [Presence] in Specimen by Immunofluorescence
        "31147-2",  # Reagin Ab [Titer] in Serum by RPR
        "34147-9",  # Treponema pallidum IgG+IgM Ab [Presence] in Serum
        "34382-2",  # Treponema pallidum Ab [Titer] in Serum by Immunofluorescence
        "39015-3",  # Treponema pallidum Ab [Units/volume] in Body fluid by Hemagglutination
        "40679-3",  # Treponema pallidum IgG Ab [Presence] in Serum by Immunoblot
        "40680-1",  # Treponema pallidum IgM Ab [Presence] in Serum by Immunoblot
        "41122-3",  # Treponema pallidum Ab [Units/volume] in Specimen
        "41163-7",  # Treponema pallidum DNA [Presence] in Specimen by NAA with probe detection
        "47235-7",  # Reagin Ab [Titer] in Specimen by VDRL
        "47236-5",  # Treponema pallidum IgG+IgM Ab [Presence] in Serum by Immunoassay
        "47237-3",  # Treponema pallidum IgM Ab [Presence] in Serum by Immunoassay
        "47238-1",  # Treponema pallidum IgG Ab [Presence] in Serum by Immunoassay
        "47476-7",  # Reagin Ab [Titer] in Specimen
        "47511-1",  # Treponema pallidum Ab [Units/volume] in Body fluid
        "50690-7",  # Reagin Ab [Titer] in Serum by VDRL
        "51838-1",  # Treponema pallidum IgG Ab [Units/volume] in Serum by Immunoassay
        "51839-9",  # Treponema pallidum IgM Ab [Units/volume] in Serum by Immunoassay
        "5291-0",  # Reagin Ab [Units/volume] in Serum by VDRL
        "5292-8",  # Reagin Ab [Presence] in Serum by VDRL
        "53605-2",  # Treponema pallidum DNA [Presence] in Blood by NAA with probe detection
        "5392-6",  # Treponema pallidum Ab [Units/volume] in Serum by Immobilization
        "5393-4",  # Treponema pallidum Ab [Presence] in Serum by Immunofluorescence
        "5394-2",  # Treponema pallidum Ab [Titer] in Serum by Latex agglutination
        "57032-5",  # Treponema pallidum Ab [Presence] in Serum by Immunoblot
        "63464-2",  # Treponema pallidum Ab [Units/volume] in Serum by Immunoassay
        "6561-5",  # Treponema pallidum IgG Ab [Presence] in Serum
        "6562-3",  # Treponema pallidum IgM Ab [Presence] in Serum
        "71793-4",  # Treponema pallidum Ab [Titer] in Serum or Plasma by Agglutination
        "73752-8",  # Reagin and Treponema pallidum IgG and IgM [Interpretation] in Serum or Plasma
        "76766-5",  # Treponema pallidum polA gene [Presence] in Genital specimen by NAA with probe detection
        "8041-6",  # Treponema pallidum Ab [Presence] in Serum by Hemagglutination
        "91846-6",  # Treponema pallidum DNA [Presence] in Genital specimen by NAA with probe detection
    }

class AlbuminLabTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for albumin blood tests

    **Data Element Scope:** This value set may use a model element related to Laboratory Test

    **Inclusion Criteria:** Includes concepts to represent albumin tests

    **Exclusion Criteria:** Excludes albumin challenge tests
    """

    VALUE_SET_NAME = "Albumin lab test"
    OID = "2.16.840.1.113762.1.4.1248.221"
    DEFINITION_VERSION = "20230520"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "1751-7",  # Albumin [Mass/volume] in Serum or Plasma
        "54347-0",  # Albumin [Moles/volume] in Serum or Plasma
    }

class ArterialBloodPh(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for arterial blood pH tests

    **Data Element Scope:** This value set may use a model element related to Laboratory test

    **Inclusion Criteria:** Includes concepts that represent arterial blood pH tests

    **Exclusion Criteria:** Excludes concepts that represent arterial blood pH from umbilical cord blood
    """

    VALUE_SET_NAME = "Arterial Blood pH"
    OID = "2.16.840.1.113762.1.4.1248.96"
    DEFINITION_VERSION = "20240109"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "2744-1",  # pH of Arterial blood
        "33254-4",  # pH of Arterial blood adjusted to patient's actual temperature
    }

class AspartateTransaminaseLabTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for Aspartate transaminase (AST, SGOT) lab tests

    **Data Element Scope:** This value set may use a model element related to Laboratory Test

    **Inclusion Criteria:** Includes concepts that represent aspartate transaminase (AST, SGOT) lab tests

    **Exclusion Criteria:** N/A
    """

    VALUE_SET_NAME = "Aspartate transaminase lab test"
    OID = "2.16.840.1.113762.1.4.1248.224"
    DEFINITION_VERSION = "20230520"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "1920-8",  # Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma
        "30239-8",  # Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma by With P-5'-P
        "88112-8",  # Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma by No addition of P-5'-P
    }

class BicarbonateLabTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests measuring bicarbonate in blood, serum, or plasma.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent a laboratory test measuring bicarbonate and carbon dioxide in the specimen source of blood, serum, or plasma.

    **Exclusion Criteria:** Excludes concepts that represent partial pressure laboratory tests and laboratory tests using the specimen source of capillary blood.
    """

    VALUE_SET_NAME = "Bicarbonate Lab Test"
    OID = "2.16.840.1.113762.1.4.1045.139"
    DEFINITION_VERSION = "20230214"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "14627-4",  # Bicarbonate [Moles/volume] in Venous blood
        "19223-7",  # Carbon dioxide, total [Moles/volume] in Mixed venous blood
        "19229-4",  # Bicarbonate [Moles/volume] in Mixed venous blood
        "19230-2",  # Bicarbonate [Moles/volume] standard in Arterial blood
        "19232-8",  # Bicarbonate [Moles/volume] standard in Venous blood
        "19233-6",  # Bicarbonate [Moles/volume] standard in Mixed venous blood
        "1959-6",  # Bicarbonate [Moles/volume] in Blood
        "1960-4",  # Bicarbonate [Moles/volume] in Arterial blood
        "1963-8",  # Bicarbonate [Moles/volume] in Serum or Plasma
        "2026-3",  # Carbon dioxide, total [Moles/volume] in Arterial blood
        "2027-1",  # Carbon dioxide, total [Moles/volume] in Venous blood
        "2028-9",  # Carbon dioxide, total [Moles/volume] in Serum or Plasma
        "20565-8",  # Carbon dioxide, total [Moles/volume] in Blood
        "41647-9",  # Carbon dioxide, total [Moles/volume] in Arterial blood by calculation
        "48391-7",  # Carbon dioxide, total [Moles/volume] in Venous blood by calculation
        "48631-6",  # Bicarbonate [Moles/volume] in Serum --post dialysis
        "54359-5",  # Bicarbonate [Moles/volume] in Plasma --post dialysis
        "57920-1",  # Carbon dioxide, total [Moles/volume] in Mixed venous blood by calculation
        "57922-7",  # Carbon dioxide, total [Moles/volume] in Serum or Plasma by calculation
        "69964-5",  # Bicarbonate [Moles/volume] standard in Plasma
        "74684-2",  # Carbon dioxide, total [Moles/volume] in Serum or Plasma --post dialysis
        "77143-6",  # Carbon dioxide, total [Moles/volume] in Serum, Plasma or Blood
        "97543-3",  # Bicarbonate [Moles/volume] in Central venous blood
        "97544-1",  # Bicarbonate [Moles/volume] standard in Central venous blood
        "97545-8",  # Carbon dioxide, total [Moles/volume] in Central venous blood
    }

class BilirubinLabTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for bilirubin lab tests

    **Data Element Scope:** This value set may use a model element related to Laboratory Test

    **Inclusion Criteria:** Includes concepts to represent bilirubin lab tests

    **Exclusion Criteria:** N/A
    """

    VALUE_SET_NAME = "Bilirubin lab test"
    OID = "2.16.840.1.113762.1.4.1248.223"
    DEFINITION_VERSION = "20250212"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "14631-6",  # Bilirubin.total [Moles/volume] in Serum or Plasma
        "1975-2",  # Bilirubin.total [Mass/volume] in Serum or Plasma
        "42719-5",  # Bilirubin.total [Mass/volume] in Blood
        "54363-7",  # Bilirubin.total [Moles/volume] in Blood
        "59827-6",  # Bilirubin.total [Mass/volume] in Arterial blood
        "59828-4",  # Bilirubin.total [Mass/volume] in Venous blood
        "77137-8",  # Bilirubin.total [Moles/volume] in Serum, Plasma or Blood
        "89871-8",  # Bilirubin.total [Moles/volume] in Venous blood
        "89872-6",  # Bilirubin.total [Moles/volume] in Arterial blood
        "97770-2",  # Bilirubin.total [Moles/volume] in Capillary blood
    }

class BloodUreaNitrogenLabTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for blood urea nitrogen (BUN) blood tests

    **Data Element Scope:** This value set may use a model element related to Laboratory Test

    **Inclusion Criteria:** Includes concepts to represent BUN tests

    **Exclusion Criteria:** N/A
    """

    VALUE_SET_NAME = "Blood urea nitrogen lab test"
    OID = "2.16.840.1.113762.1.4.1248.218"
    DEFINITION_VERSION = "20250212"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "11064-3",  # Urea nitrogen [Mass/volume] in Serum or Plasma --post dialysis
        "11065-0",  # Urea nitrogen [Mass/volume] in Serum or Plasma --pre dialysis
        "12961-9",  # Urea nitrogen [Mass/volume] in Arterial blood
        "12962-7",  # Urea nitrogen [Mass/volume] in Venous blood
        "12963-5",  # Urea nitrogen [Mass/volume] in Peripheral blood
        "14937-7",  # Urea nitrogen [Moles/volume] in Serum or Plasma
        "17759-2",  # Urea nitrogen [Mass/volume] in Arterial blood --post dialysis
        "17760-0",  # Urea nitrogen [Mass/volume] in Venous blood --pre dialysis
        "3094-0",  # Urea nitrogen [Mass/volume] in Serum or Plasma
        "48629-0",  # Urea nitrogen [Mass/volume] in Venous blood --post dialysis
        "48639-9",  # Urea nitrogen [Mass/volume] in Peripheral blood --post dialysis
        "59570-2",  # Urea nitrogen [Moles/volume] in Blood
        "6299-2",  # Urea nitrogen [Mass/volume] in Blood
    }

class CarbonDioxidePartialPressureInArterialBlood(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for carbon dioxide partial pressure in arterial blood

    **Data Element Scope:** This value set may use a model element related to Laboratory Test

    **Inclusion Criteria:** Includes concepts that represent tests for partial pressure of carbon dioxide in arterial blood

    **Exclusion Criteria:** Excludes concepts that represent tests for total pressure of carbon dioxide in arterial blood or tests for carbon dioxide in arterial cord blood
    """

    VALUE_SET_NAME = "Carbon Dioxide Partial Pressure in Arterial Blood"
    OID = "2.16.840.1.113762.1.4.1248.95"
    DEFINITION_VERSION = "20240109"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "2019-8",  # Carbon dioxide [Partial pressure] in Arterial blood
        "32771-8",  # Carbon dioxide [Partial pressure] adjusted to patient's actual temperature in Arterial blood
    }

class CreatinineLabTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests measuring creatinine in blood, serum, or plasma.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent a laboratory test measuring creatinine in the specimen source of blood, serum, or plasma.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Creatinine Lab Test"
    OID = "2.16.840.1.113883.3.666.5.2363"
    DEFINITION_VERSION = "20250207"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "101475-2",  # Creatinine [Moles/volume] in Venous blood
        "11041-1",  # Creatinine [Mass/volume] in Serum or Plasma --post dialysis
        "11042-9",  # Creatinine [Mass/volume] in Serum or Plasma --pre dialysis
        "14682-9",  # Creatinine [Moles/volume] in Serum or Plasma
        "21232-4",  # Creatinine [Mass/volume] in Arterial blood
        "2160-0",  # Creatinine [Mass/volume] in Serum or Plasma
        "38483-4",  # Creatinine [Mass/volume] in Blood
        "51619-5",  # Creatinine [Moles/volume] in Serum or Plasma --pre dialysis
        "51620-3",  # Creatinine [Moles/volume] in Serum or Plasma --post dialysis
        "59826-8",  # Creatinine [Moles/volume] in Blood
        "77140-2",  # Creatinine [Moles/volume] in Serum, Plasma or Blood
    }

class HemoglobinLabTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for hemoglobin blood tests

    **Data Element Scope:** This value set may use a model element related to Laboratory Test

    **Inclusion Criteria:** Includes concepts to represent hemoglobin blood tests

    **Exclusion Criteria:** N/A
    """

    VALUE_SET_NAME = "Hemoglobin lab test"
    OID = "2.16.840.1.113762.1.4.1248.219"
    DEFINITION_VERSION = "20250212"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "20509-6",  # Hemoglobin [Mass/volume] in Blood by calculation
        "24360-0",  # Hemoglobin and Hematocrit panel - Blood
        "30313-1",  # Hemoglobin [Mass/volume] in Arterial blood
        "30350-3",  # Hemoglobin [Mass/volume] in Venous blood
        "30351-1",  # Hemoglobin [Mass/volume] in Mixed venous blood
        "30352-9",  # Hemoglobin [Mass/volume] in Capillary blood
        "59260-0",  # Hemoglobin [Moles/volume] in Blood
        "718-7",  # Hemoglobin [Mass/volume] in Blood
        "75928-2",  # Hemoglobin [Moles/volume] in Arterial blood
        "93846-4",  # Hemoglobin [Moles/volume] in Venous blood
        "97550-8",  # Hemoglobin [Mass/volume] in Central venous blood by calculation
    }

class LeukocyteCountLabTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for leukocyte count blood tests

    **Data Element Scope:** This value set may use a model element related to Laboratory Test

    **Inclusion Criteria:** Includes concepts that represent leukocyte count lab tests

    **Exclusion Criteria:** N/A
    """

    VALUE_SET_NAME = "Leukocyte count lab test"
    OID = "2.16.840.1.113762.1.4.1248.222"
    DEFINITION_VERSION = "20240112"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "26464-8",  # Leukocytes [#/volume] in Blood
        "49498-9",  # Leukocytes [#/volume] in Blood by Estimate
        "51383-8",  # Leukocytes other [#/volume] in Blood by Automated count
        "6690-2",  # Leukocytes [#/volume] in Blood by Automated count
        "804-5",  # Leukocytes [#/volume] in Blood by Manual count
    }

class OxygenPartialPressureInArterialBlood(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for oxygen partial pressure in arterial blood

    **Data Element Scope:** This value set may use a model element related to Laboratory Test

    **Inclusion Criteria:** Includes concepts that represent tests for partial pressure of oxygen in arterial blood

    **Exclusion Criteria:** Excludes concepts that represent tests for oxygen saturation or total content, or tests for oxygen in arterial cord blood
    """

    VALUE_SET_NAME = "Oxygen Partial Pressure in Arterial Blood"
    OID = "2.16.840.1.113762.1.4.1248.94"
    DEFINITION_VERSION = "20240109"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "19214-6",  # Oxygen [Partial pressure] saturation adjusted to 0.5 in Arterial blood
        "19255-9",  # Oxygen [Partial pressure] adjusted to patient's actual temperature in Arterial blood
        "2703-7",  # Oxygen [Partial pressure] in Arterial blood
    }

class PlateletCountLabTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests measuring platelet count in blood, serum, or plasma.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent a laboratory test measuring platelet count in the specimen source of blood, serum, or plasma.

    **Exclusion Criteria:** Excludes concepts that represent laboratory tests for platelet count using the specimen source of capillary blood.
    """

    VALUE_SET_NAME = "Platelet Count Lab Test"
    OID = "2.16.840.1.113762.1.4.1045.127"
    DEFINITION_VERSION = "20230214"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "13056-7",  # Platelets [#/volume] in Plasma by Automated count
        "26515-7",  # Platelets [#/volume] in Blood
        "26516-5",  # Platelets [#/volume] in Plasma
        "34167-7",  # Platelets Large [Presence] in Blood by Automated count
        "48386-7",  # Platelets Large/Platelets in Blood by Automated count
        "777-3",  # Platelets [#/volume] in Blood by Automated count
        "778-1",  # Platelets [#/volume] in Blood by Manual count
        "96354-6",  # Platelets Large [#/volume] in Blood by Automated count
        "97995-5",  # Platelets [#/volume] in Blood by Automated count.optical
    }

class SodiumLabTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests measuring sodium in blood, serum, or plasma.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent a laboratory test measuring sodium in the specimen source of blood, serum, or plasma.

    **Exclusion Criteria:** Excludes concepts that represent laboratory tests for sodium using the specimen source of capillary blood.
    """

    VALUE_SET_NAME = "Sodium Lab Test"
    OID = "2.16.840.1.113762.1.4.1045.119"
    DEFINITION_VERSION = "20220218"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "2947-0",  # Sodium [Moles/volume] in Blood
        "2951-2",  # Sodium [Moles/volume] in Serum or Plasma
        "32717-1",  # Sodium [Moles/volume] in Arterial blood
        "39791-9",  # Sodium [Moles/volume] in Venous blood
        "41657-8",  # Sodium [Moles/volume] in Mixed venous blood
        "77139-4",  # Sodium [Moles/volume] in Serum, Plasma or Blood
    }

class Hba1cLaboratoryTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for hemoglobin A1c tests.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for hemoglobin A1c.

    **Exclusion Criteria:** Excludes concepts that represent hemoglobin A1c laboratory tests that use the International Federation of Clinical Chemistry and Laboratory Medicine (IFCC) protocol and Japanese Diabetes Society (JDS)/Japanese Society of Clinical Chemistry (JSCC) protocol and exclude concepts that represent an order only.
    """

    VALUE_SET_NAME = "HbA1c Laboratory Test"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1013"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "17855-8",  # Hemoglobin A1c/Hemoglobin.total in Blood by calculation
        "17856-6",  # Hemoglobin A1c/Hemoglobin.total in Blood by HPLC
        "4548-4",  # Hemoglobin A1c/Hemoglobin.total in Blood
        "4549-2",  # Hemoglobin A1c/Hemoglobin.total in Blood by Electrophoresis
        "96595-4",  # Hemoglobin A1c/Hemoglobin.total in DBS
    }

class HpvTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for human papilloma viruses (HPV).

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for high-risk HPV in cervical samples.

    **Exclusion Criteria:** Excludes concepts that represent tests for high-risk HPV conducted on non-cervical samples and tests that are ordered only.
    """

    VALUE_SET_NAME = "HPV Test"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1059"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "104132-6",  # Human papilloma virus 16 and 18 and 31 and 45+33+52+58 and 35+39+51+56+59+66+68 DNA [Interpretation] in Cervix by NAA with probe detection
        "104170-6",  # Human papilloma virus 31+33+52+58 DNA [Presence] in Cervix by NAA with probe detection
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
        "95539-3",  # Human papilloma virus 31 DNA [Presence] in Cervix by NAA with probe detection
    }

class PapTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for cervical cytology tests.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for cervical cytology.

    **Exclusion Criteria:** Excludes concepts that represent tests for cervical cytology conducted on non-cervical or non-vaginal samples and tests that are ordered only.
    """

    VALUE_SET_NAME = "Pap Test"
    OID = "2.16.840.1.113883.3.464.1003.108.12.1017"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "10524-7",  # Microscopic observation [Identifier] in Cervix by Cyto stain
        "18500-9",  # Microscopic observation [Identifier] in Cervix by Cyto stain.thin prep
        "19762-4",  # General categories [Interpretation] of Cervical or vaginal smear or scraping by Cyto stain
        "19764-0",  # Statement of adequacy [Interpretation] of Cervical or vaginal smear or scraping by Cyto stain
        "19765-7",  # Microscopic observation [Identifier] in Cervical or vaginal smear or scraping by Cyto stain
        "19766-5",  # Microscopic observation [Identifier] in Cervical or vaginal smear or scraping by Cyto stain Narrative
        "19774-9",  # Cytology study comment Cervical or vaginal smear or scraping Cyto stain
        "33717-0",  # Cervical AndOr vaginal cytology study
        "47527-7",  # Cytology report of Cervical or vaginal smear or scraping Cyto stain.thin prep
        "47528-5",  # Cytology report of Cervical or vaginal smear or scraping Cyto stain
    }

class ProstateSpecificAntigenTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests measuring the prostate specific antigen (PSA).

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent a laboratory test for a prostate specific antigen (PSA).

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Prostate Specific Antigen Test"
    OID = "2.16.840.1.113883.3.526.3.401"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "19195-7",  # Prostate specific Ag [Units/volume] in Serum or Plasma
        "2857-1",  # Prostate specific Ag [Mass/volume] in Serum or Plasma
        "35741-8",  # Prostate specific Ag [Mass/volume] in Serum or Plasma by Detection limit <= 0.01 ng/mL
        "83112-3",  # Prostate specific Ag [Mass/volume] in Serum or Plasma by Immunoassay
    }

class FecalOccultBloodTestFobt(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for fecal occult blood tests.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for occult blood in stool.

    **Exclusion Criteria:** Excludes concepts that represent an order only and test for occult blood in other body fluids.
    """

    VALUE_SET_NAME = "Fecal Occult Blood Test (FOBT)"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1011"
    DEFINITION_VERSION = "20171219"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

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

class SdnaFitTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for colorectal cancer screening tests that include a combination of stool DNA and fecal immunochemical testing.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent colorectal cancer screening tests that include a combination of stool DNA and fecal immunochemical testing.

    **Exclusion Criteria:** Excludes concepts that represent an order only.
    """

    VALUE_SET_NAME = "sDNA FIT Test"
    OID = "2.16.840.1.113883.3.464.1003.108.12.1039"
    DEFINITION_VERSION = "20171219"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "77353-1",  # Noninvasive colorectal cancer DNA and occult blood screening [Interpretation] in Stool Narrative
        "77354-9",  # Noninvasive colorectal cancer DNA and occult blood screening [Presence] in Stool
    }

class GroupAStreptococcusTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for group A streptococcus tests.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests to identify the presence of group A streptococcus.

    **Exclusion Criteria:** Excludes concepts that represent an order only.
    """

    VALUE_SET_NAME = "Group A Streptococcus Test"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1012"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "101300-2",  # Streptococcus pyogenes DNA [Presence] in Throat by NAA with non-probe detection
        "103627-6",  # Streptococcus pyogenes DNA [Presence] in Specimen by NAA with probe detection
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
    }

class LabTestsDuringPregnancy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests conducted during pregnancy.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests conducted during pregnancy.

    **Exclusion Criteria:** Excludes concepts that represent an order only.
    """

    VALUE_SET_NAME = "Lab Tests During Pregnancy"
    OID = "2.16.840.1.113883.3.464.1003.111.12.1007"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

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
        "83074-5",  # Alpha-1-Fetoprotein [Units/volume] in Amniotic fluid by Immunoassay
    }

class LabTestsForSexuallyTransmittedInfections(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests for sexually transmitted infections.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for sexually transmitted infections.

    **Exclusion Criteria:** Excludes concepts that represent an order only.
    """

    VALUE_SET_NAME = "Lab Tests for Sexually Transmitted Infections"
    OID = "2.16.840.1.113883.3.464.1003.110.12.1051"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

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
        "20508-8",  # Reagin Ab [Units/volume] in Serum or Plasma by RPR
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
        "97156-4",  # Human papilloma virus 16+18+31+33+35+39+45+51+52+56+58+59+68 DNA [Presence] in Genital specimen by Probe with signal amplification
        "97157-2",  # Human papilloma virus 6+11+42+43+44 DNA [Presence] in Genital specimen by Probe with signal amplification
        "98221-5",  # Treponema pallidum IgG bands [Identifier] in Serum by Immunoblot
        "98223-1",  # Treponema pallidum IgM bands [Identifier] in Serum by Immunoblot
    }

class PregnancyTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for pregnancy tests.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent tests for pregnancy including in urine, serum or plasma.

    **Exclusion Criteria:** Excludes concepts that represent an order only.
    """

    VALUE_SET_NAME = "Pregnancy Test"
    OID = "2.16.840.1.113883.3.464.1003.111.12.1011"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

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
        "99104-2",  # Choriogonadotropin [Mass/volume] in Urine
    }

class LaboratoryTestsForHypertension(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for lab tests that are commonly performed on patients with hypertension.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent concepts for lab tests that are commonly performed on patients with hypertension.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Laboratory Tests for Hypertension"
    OID = "2.16.840.1.113883.3.600.1482"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "24320-4",  # Basic metabolic 1998 panel - Serum or Plasma
        "24321-2",  # Basic metabolic 2000 panel - Serum or Plasma
        "24322-0",  # Comprehensive metabolic 1998 panel - Serum or Plasma
        "24323-8",  # Comprehensive metabolic 2000 panel - Serum or Plasma
        "24356-8",  # Urinalysis complete panel - Urine
        "24362-6",  # Renal function 2000 panel - Serum or Plasma
        "2888-6",  # Protein [Mass/volume] in Urine
        "51990-0",  # Basic metabolic panel - Blood
        "57021-8",  # CBC W Auto Differential panel - Blood
        "57022-6",  # CBC W Reflex Manual Differential panel - Blood
        "57782-5",  # CBC W Ordered Manual Differential panel - Blood
        "58077-9",  # Urinalysis complete W Reflex Culture panel - Urine
        "58410-2",  # CBC panel - Blood by Automated count
        "69742-5",  # CBC W Differential panel, method unspecified - Blood
    }

class LdlCholesterol(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests commonly used for low-density lipoproteins (LDL) cholesterol measurement.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent a laboratory test measuring low-density lipoprotein cholesterol (LDL-C) using the specimen type of serum or plasma based on a measurement scale of mass per volume.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "LDL Cholesterol"
    OID = "2.16.840.1.113883.3.526.3.1573"
    DEFINITION_VERSION = "20250228"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

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
        "90364-1",  # Cholesterol.in LDL.small dense [Mass/volume] in Serum or Plasma
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

class HivLabTests(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests used for Human Immunodeficiency Virus (HIV) screening.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent a laboratory test for HIV-1 and HIV-2 antibodies or antigens.

    **Exclusion Criteria:** Excludes concepts that represent tests and procedures that might be associated with HIV infection but not used for screening or testing to establish an HIV diagnosis such as home/self HIV testing, HIV genotyping tests, HIV RNA tests, HIV cultures, clinical codes used to document care provided to HIV-infected patients.
    """

    VALUE_SET_NAME = "HIV Lab Tests"
    OID = "2.16.840.1.113762.1.4.1056.50"
    DEFINITION_VERSION = "20250206"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "104732-3",  # HIV 1 Ab band pattern [Interpretation] in Serum
        "105080-6",  # HIV 1+2 Ab+HIV1 p24 Ag [Presence] in Serum or Plasma
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
        "51786-2",  # HIV 2 Ab Signal/Cutoff in Serum or Plasma by Immunoassay
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

class GlucoseLabTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests measuring glucose.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent a laboratory test measuring glucose in the specimen source of blood, serum, or plasma, including Point of Care (POC) testing.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Glucose Lab Test"
    OID = "2.16.840.1.113762.1.4.1045.134"
    DEFINITION_VERSION = "20250207"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "100746-7",  # Glucose [Moles/volume] in Mixed venous blood
        "101476-0",  # Fasting glucose [Moles/volume] in Venous blood
        "104597-0",  # Glucose [Mass/volume] in Venous blood by Glucometer
        "104598-8",  # Glucose [Mass/volume] in Arterial blood by Glucometer
        "104655-6",  # Glucose [Mass/volume] in Mixed venous blood
        "14743-9",  # Glucose [Moles/volume] in Capillary blood by Glucometer
        "14749-6",  # Glucose [Moles/volume] in Serum or Plasma
        "14768-6",  # Glucose [Moles/volume] in Serum or Plasma --baseline
        "14770-2",  # Fasting glucose [Moles/volume] in Capillary blood by Glucometer
        "14771-0",  # Fasting glucose [Moles/volume] in Serum or Plasma
        "15074-8",  # Glucose [Moles/volume] in Blood
        "1547-9",  # Glucose [Mass/volume] in Serum or Plasma --baseline
        "1556-0",  # Fasting glucose [Mass/volume] in Capillary blood
        "1557-8",  # Fasting glucose [Mass/volume] in Venous blood
        "1558-6",  # Fasting glucose [Mass/volume] in Serum or Plasma
        "2339-0",  # Glucose [Mass/volume] in Blood
        "2340-8",  # Glucose [Mass/volume] in Blood by Automated test strip
        "2341-6",  # Glucose [Mass/volume] in Blood by Test strip manual
        "2345-7",  # Glucose [Mass/volume] in Serum or Plasma
        "32016-8",  # Glucose [Mass/volume] in Capillary blood
        "35184-1",  # Fasting glucose [Mass or Moles/volume] in Serum or Plasma
        "39480-9",  # Glucose [Moles/volume] in Venous blood
        "39481-7",  # Glucose [Moles/volume] in Arterial blood
        "40858-3",  # Glucose [Mass/volume] in Capillary blood --baseline
        "41604-0",  # Fasting glucose [Mass/volume] in Capillary blood by Glucometer
        "41651-1",  # Glucose [Mass/volume] in Arterial blood
        "41652-9",  # Glucose [Mass/volume] in Venous blood
        "41653-7",  # Glucose [Mass/volume] in Capillary blood by Glucometer
        "50206-2",  # Glucose [Mass/volume] in Serum or Plasma --1st specimen
        "50212-0",  # Glucose [Mass/volume] in Serum or Plasma --2nd specimen
        "51596-5",  # Glucose [Moles/volume] in Capillary blood
        "53049-3",  # Glucose [Mass/volume] in Serum or Plasma --pre-meal
        "72516-8",  # Glucose [Moles/volume] in Blood by Automated test strip
        "74774-1",  # Glucose [Mass/volume] in Serum, Plasma or Blood
        "76629-5",  # Fasting glucose [Moles/volume] in Blood
        "77135-2",  # Glucose [Moles/volume] in Serum, Plasma or Blood
        "77145-1",  # Fasting glucose [Moles/volume] in Serum, Plasma or Blood
    }

class PotassiumLabTest(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests measuring potassium in blood, serum, or plasma.

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent a laboratory test measuring potassium in the specimen source of blood, serum, or plasma.

    **Exclusion Criteria:** Excludes concepts that represent laboratory tests for potassium using the specimen source of capillary blood.
    """

    VALUE_SET_NAME = "Potassium Lab Test"
    OID = "2.16.840.1.113762.1.4.1045.117"
    DEFINITION_VERSION = "20230214"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "12812-4",  # Potassium [Moles/volume] in Serum or Plasma --2nd specimen
        "12813-2",  # Potassium [Moles/volume] in Serum or Plasma --3rd specimen
        "2823-3",  # Potassium [Moles/volume] in Serum or Plasma
        "29349-8",  # Potassium [Moles/volume] in Serum or Plasma --post dialysis
        "32713-0",  # Potassium [Moles/volume] in Arterial blood
        "39789-3",  # Potassium [Moles/volume] in Venous blood
        "41656-0",  # Potassium [Moles/volume] in Mixed venous blood
        "51618-7",  # Potassium [Moles/volume] in Serum or Plasma --pre dialysis
        "6298-4",  # Potassium [Moles/volume] in Blood
        "75940-7",  # Potassium [Mass/volume] in Blood
        "77142-8",  # Potassium [Moles/volume] in Serum, Plasma or Blood
    }

class GlucoseLabTestMassPerVolume(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests measuring glucose and reported as Mass Per Volume (mg/dL).

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent a laboratory test measuring glucose in the specimen source of blood, serum, plasma or interstitial fluid, including Point of Care (POC) testing and reported as Mass Per Volume (mg/dL).

    **Exclusion Criteria:** Excludes concepts that represent a laboratory test measuring glucose from a specimen source other than blood, serum, plasma or interstitial fluid. Excludes concepts that represent a laboratory test measuring glucose and reported as Moles Per Volume (mmol/L).
    """

    VALUE_SET_NAME = "Glucose Lab Test Mass Per Volume"
    OID = "2.16.840.1.113762.1.4.1248.34"
    DEFINITION_VERSION = "20230203"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "1547-9",  # Glucose [Mass/volume] in Serum or Plasma --baseline
        "1556-0",  # Fasting glucose [Mass/volume] in Capillary blood
        "1557-8",  # Fasting glucose [Mass/volume] in Venous blood
        "1558-6",  # Fasting glucose [Mass/volume] in Serum or Plasma
        "2339-0",  # Glucose [Mass/volume] in Blood
        "2340-8",  # Glucose [Mass/volume] in Blood by Automated test strip
        "2341-6",  # Glucose [Mass/volume] in Blood by Test strip manual
        "2345-7",  # Glucose [Mass/volume] in Serum or Plasma
        "32016-8",  # Glucose [Mass/volume] in Capillary blood
        "40858-3",  # Glucose [Mass/volume] in Capillary blood --baseline
        "41604-0",  # Fasting glucose [Mass/volume] in Capillary blood by Glucometer
        "41651-1",  # Glucose [Mass/volume] in Arterial blood
        "41652-9",  # Glucose [Mass/volume] in Venous blood
        "41653-7",  # Glucose [Mass/volume] in Capillary blood by Glucometer
        "74774-1",  # Glucose [Mass/volume] in Serum, Plasma or Blood
        "99504-3",  # Glucose [Mass/volume] in Interstitial fluid
    }

class CreatinineMassPerVolume(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for laboratory tests measuring creatinine and reported as Mass Per Volume (mg/dL).

    **Data Element Scope:** This value set may use a model element related to Laboratory Test.

    **Inclusion Criteria:** Includes concepts that represent a laboratory test measuring creatinine in the specimen source of blood, serum, or plasma, and reported as Mass Per Volume (mg/dL).

    **Exclusion Criteria:** Excludes concepts that represent a laboratory test measuring creatinine from a specimen source other than blood, serum, or plasma. Excludes concepts that represent a laboratory test measuring creatinine and reported as Moles Per Volume (mmol/L).
    """

    VALUE_SET_NAME = "Creatinine Mass Per Volume"
    OID = "2.16.840.1.113762.1.4.1248.21"
    DEFINITION_VERSION = "20220415"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "21232-4",  # Creatinine [Mass/volume] in Arterial blood
        "2160-0",  # Creatinine [Mass/volume] in Serum or Plasma
        "38483-4",  # Creatinine [Mass/volume] in Blood
    }

class EstimatedGlomerularFiltrationRate(ValueSet):
    """
    **Clinical Focus:** This value set contains concepts that represent estimated glomerular filtration rate (eGFR) tests.

    **Data Element Scope:** This value set may use Quality Data Model (QDM) category related to Laboratory Test.

    **Inclusion Criteria:** Includes only relevant concepts associated with estimated glomerular filtration rate (eGFR) tests.

    **Exclusion Criteria:** Does not include estimated glomerular filtration rate (eGFR) tests calcuated by Schwartz formula.
    """

    VALUE_SET_NAME = "Estimated Glomerular Filtration Rate"
    OID = "2.16.840.1.113883.3.6929.3.1000"
    DEFINITION_VERSION = "20190531"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "48642-3",  # Glomerular filtration rate/1.73 sq M.predicted among non-blacks [Volume Rate/Area] in Serum, Plasma or Blood by Creatinine-based formula (MDRD)
        "48643-1",  # Glomerular filtration rate/1.73 sq M.predicted among blacks [Volume Rate/Area] in Serum, Plasma or Blood by Creatinine-based formula (MDRD)
        "50044-7",  # Glomerular filtration rate/1.73 sq M.predicted among females [Volume Rate/Area] in Serum, Plasma or Blood by Creatinine-based formula (MDRD)
        "50210-4",  # Glomerular filtration rate/1.73 sq M.predicted [Volume Rate/Area] in Serum, Plasma or Blood by Cystatin C-based formula
        "62238-1",  # Glomerular filtration rate/1.73 sq M.predicted [Volume Rate/Area] in Serum, Plasma or Blood by Creatinine-based formula (CKD-EPI)
        "69405-9",  # Glomerular filtration rate/1.73 sq M.predicted [Volume Rate/Area] in Serum, Plasma or Blood
        "70969-1",  # Glomerular filtration rate/1.73 sq M.predicted among males [Volume Rate/Area] in Serum, Plasma or Blood by Creatinine-based formula (MDRD)
        "77147-7",  # Glomerular filtration rate/1.73 sq M.predicted [Volume Rate/Area] in Serum, Plasma or Blood by Creatinine-based formula (MDRD)
        "88293-6",  # Glomerular filtration rate/1.73 sq M.predicted among blacks [Volume Rate/Area] in Serum, Plasma or Blood by Creatinine-based formula (CKD-EPI)
        "88294-4",  # Glomerular filtration rate/1.73 sq M.predicted among non-blacks [Volume Rate/Area] in Serum, Plasma or Blood by Creatinine-based formula (CKD-EPI)
        "94677-2",  # Glomerular filtration rate/1.73 sq M.predicted [Volume Rate/Area] in Serum, Plasma or Blood by Creatinine and Cystatin C-based formula (CKD-EPI)
        "98979-8",  # Glomerular filtration rate/1.73 sq M.predicted [Volume Rate/Area] in Serum, Plasma or Blood by Creatinine-based formula (CKD-EPI 2021)
        "98980-6",  # Glomerular filtration rate/1.73 sq M.predicted [Volume Rate/Area] in Serum, Plasma or Blood by Creatinine and Cystatin C-based formula (CKD-EPI 2021)
    }

class UrineAlbumin(ValueSet):
    """
    **Clinical Focus:** The value set contains concepts that represent lab tests commonly used for urine albumin and urine microalbumin measurement.

    **Data Element Scope:** This value set may use the Quality Data Model (QDM) category related to Laboratory Test. Codes include tests which measure albumin and microalbumin tests using urine.

    **Inclusion Criteria:** Includes only relevant concepts associated with albumin and microalbumin laboratory tests using urine.

    **Exclusion Criteria:** Excludes concepts associated with urine-based albumin and microalbumin laboratory tests combined with other urine-based tests (e.g., Creatinine).
    """

    VALUE_SET_NAME = "Urine Albumin"
    OID = "2.16.840.1.113762.1.4.1178.88"
    DEFINITION_VERSION = "20231019"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "11218-5",  # Microalbumin [Mass/volume] in Urine by Test strip
        "14956-7",  # Microalbumin [Mass/time] in 24 hour Urine
        "14957-5",  # Microalbumin [Mass/volume] in Urine
        "1754-1",  # Albumin [Mass/volume] in Urine
        "1755-8",  # Albumin [Mass/time] in 24 hour Urine
        "21059-1",  # Albumin [Mass/volume] in 24 hour Urine
        "30003-8",  # Microalbumin [Mass/volume] in 24 hour Urine
        "43605-5",  # Microalbumin [Mass/volume] in 4 hour Urine
        "43606-3",  # Microalbumin [Mass/time] in 4 hour Urine
        "43607-1",  # Microalbumin [Mass/time] in 12 hour Urine
        "49002-9",  # Albumin [Mass/time] in Urine collected for unspecified duration
        "49023-5",  # Microalbumin [Mass/time] in Urine collected for unspecified duration
        "50209-6",  # Albumin [Mass/time] in Urine collected for unspecified duration --supine
        "50949-7",  # Albumin [Presence] in Urine by Test strip
        "51190-7",  # Albumin [Mass/volume] in 24 hour Urine by Electrophoresis
        "53530-2",  # Microalbumin [Mass/volume] in 24 hour Urine by Detection limit <= 1.0 mg/L
        "53531-0",  # Microalbumin [Mass/volume] in Urine by Detection limit <= 1.0 mg/L
        "53532-8",  # Microalbumin [Mass/time] in 24 hour Urine by Detection limit <= 1.0 mg/L
        "56553-1",  # Microalbumin [Mass/time] in 8 hour Urine
        "58448-2",  # Microalbumin ug/min [Mass/time] in 24 hour Urine
        "63474-1",  # Microalbumin [Mass/time] in 18 hour Urine
        "6941-9",  # Albumin [Mass/time] in 24 hour Urine by Electrophoresis
        "6942-7",  # Albumin [Mass/volume] in Urine by Electrophoresis
        "77940-5",  # Albumin [Mass/volume] by Electrophoresis in Urine collected for unspecified duration
    }

class UrineAlbuminCreatinineRatio(ValueSet):
    """
    **Clinical Focus:** This value set contains concepts that represent urine albumin creatinine ratio (uACR) tests.

    **Data Element Scope:** This value set may use Quality Data Model (QDM) category related to Laboratory Test.

    **Inclusion Criteria:** Includes only relevant concepts associated with urine albumin creatinine ratio (uACR) tests. Value set includes contents with mg/mol/creatinine unit of measurement and mg/g/creatinine unit of measurement.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Urine Albumin Creatinine Ratio"
    OID = "2.16.840.1.113883.3.6929.3.1007"
    DEFINITION_VERSION = "20190531"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "13705-9",  # Albumin/Creatinine [Mass Ratio] in 24 hour Urine
        "14585-4",  # Albumin/Creatinine [Molar ratio] in Urine
        "14958-3",  # Microalbumin/Creatinine [Mass Ratio] in 24 hour Urine
        "14959-1",  # Microalbumin/Creatinine [Mass Ratio] in Urine
        "30000-4",  # Microalbumin/Creatinine [Ratio] in Urine
        "30001-2",  # Microalbumin/Creatinine [Ratio] in Urine by Test strip
        "32294-1",  # Albumin/Creatinine [Ratio] in Urine
        "44292-1",  # Microalbumin/Creatinine [Mass Ratio] in 12 hour Urine
        "59159-4",  # Microalbumin/Creatinine [Ratio] in 24 hour Urine
        "76401-9",  # Albumin/Creatinine [Ratio] in 24 hour Urine
        "77253-3",  # Microalbumin/Creatinine [Ratio] in Urine by Detection limit <= 1.0 mg/L
        "77254-1",  # Microalbumin/Creatinine [Ratio] in 24 hour Urine by Detection limit <= 1.0 mg/L
        "9318-7",  # Albumin/Creatinine [Mass Ratio] in Urine
    }

class UrineCreatinine(ValueSet):
    """
    **Clinical Focus:** This value set contains concepts that represent lab tests commonly used for urine creatinine measurement.

    **Data Element Scope:** This value set may use the Quality Data Model (QDM) category related to Laboratory Test. Codes include tests which measure creatinine tests using urine.

    **Inclusion Criteria:** Includes only relevant concepts associated with creatinine laboratory tests using urine.

    **Exclusion Criteria:** Excludes concepts associated with creatinine laboratory combined with other urine-based tests (e.g., urine protein). Excludes urine-based tests combined with serum and and plasma-based creatinine tests.
    """

    VALUE_SET_NAME = "Urine Creatinine"
    OID = "2.16.840.1.113762.1.4.1178.87"
    DEFINITION_VERSION = "20250329"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "14683-7",  # Creatinine [Moles/volume] in Urine
        "20624-3",  # Creatinine [Mass/volume] in 24 hour Urine
        "2149-3",  # Creatine [Mass/volume] in Urine
        "2150-1",  # Creatine [Mass/time] in 24 hour Urine
        "2161-8",  # Creatinine [Mass/volume] in Urine
        "25886-3",  # Creatinine [Moles/volume] in 24 hour Urine
        "30004-6",  # Creatinine [Mass/volume] in Urine by Test strip
        "35674-1",  # Creatinine [Mass/volume] in Urine collected for unspecified duration
        "55593-8",  # Creatinine [Moles/volume] in Urine collected for unspecified duration
        "57346-9",  # Creatinine [Mass/volume] in 12 hour Urine
        "58951-5",  # Creatinine [Mass/volume] in Urine --2nd specimen
    }

__exports__ = (
    "HematocritLabTest",
    "WhiteBloodCellsCountLabTest",
    "Inr",
    "GlycemicScreeningTests",
    "HivViralLoadTests",
    "ChlamydiaScreening",
    "GonorrheaScreening",
    "SyphilisTests",
    "AlbuminLabTest",
    "ArterialBloodPh",
    "AspartateTransaminaseLabTest",
    "BicarbonateLabTest",
    "BilirubinLabTest",
    "BloodUreaNitrogenLabTest",
    "CarbonDioxidePartialPressureInArterialBlood",
    "CreatinineLabTest",
    "HemoglobinLabTest",
    "LeukocyteCountLabTest",
    "OxygenPartialPressureInArterialBlood",
    "PlateletCountLabTest",
    "SodiumLabTest",
    "Hba1cLaboratoryTest",
    "HpvTest",
    "PapTest",
    "ProstateSpecificAntigenTest",
    "FecalOccultBloodTestFobt",
    "SdnaFitTest",
    "GroupAStreptococcusTest",
    "LabTestsDuringPregnancy",
    "LabTestsForSexuallyTransmittedInfections",
    "PregnancyTest",
    "LaboratoryTestsForHypertension",
    "LdlCholesterol",
    "HivLabTests",
    "GlucoseLabTest",
    "PotassiumLabTest",
    "GlucoseLabTestMassPerVolume",
    "CreatinineMassPerVolume",
    "EstimatedGlomerularFiltrationRate",
    "UrineAlbumin",
    "UrineAlbuminCreatinineRatio",
    "UrineCreatinine",
)
