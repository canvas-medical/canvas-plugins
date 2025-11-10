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


class EncounterInpatient(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for inpatient hospitalizations encounters.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for inpatient hospitalizations.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS131v14
    """

    VALUE_SET_NAME = "Encounter Inpatient"
    OID = "2.16.840.1.113883.3.666.5.307"
    DEFINITION_VERSION = "20200307"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "183452005",  # Emergency hospital admission (procedure)
        "32485007",  # Hospital admission (procedure)
        "8715000",  # Hospital admission, elective (procedure)
    }


class FrailtyEncounter(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for nursing care services provided to frail patients.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for nursing care and home care services provided to frail patients.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS131v14
    """

    VALUE_SET_NAME = "Frailty Encounter"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1088"
    DEFINITION_VERSION = "20210224"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99504",  # Home visit for mechanical ventilation care
        "99509",  # Home visit for assistance with activities of daily living and personal care
    }
    HCPCSLEVELII = {
        "G0162",  # Skilled services by a registered nurse (rn) for management and evaluation of the plan of care; each 15 minutes (the patient's underlying condition or complication requires an rn to ensure that essential non-skilled care achieves its purpose in the home health or hospice setting)
        "G0299",  # Direct skilled nursing services of a registered nurse (rn) in the home health or hospice setting, each 15 minutes
        "G0300",  # Direct skilled nursing services of a licensed practical nurse (lpn) in the home health or hospice setting, each 15 minutes
        "G0493",  # Skilled services of a registered nurse (rn) for the observation and assessment of the patient's condition, each 15 minutes (the change in the patient's condition requires skilled nursing personnel to identify and evaluate the patient's need for possible modification of treatment in the home health or hospice setting)
        "G0494",  # Skilled services of a licensed practical nurse (lpn) for the observation and assessment of the patient's condition, each 15 minutes (the change in the patient's condition requires skilled nursing personnel to identify and evaluate the patient's need for possible modification of treatment in the home health or hospice setting)
        "S0271",  # Physician management of patient home care, hospice monthly case rate (per 30 days)
        "S0311",  # Comprehensive management and care coordination for advanced illness, per calendar month
        "S9123",  # Nursing care, in the home; by registered nurse, per hour (use for general nursing care only, not to be used when cpt codes 99500-99602 can be used)
        "S9124",  # Nursing care, in the home; by licensed practical nurse, per hour
        "T1000",  # Private duty / independent nursing service(s) - licensed, up to 15 minutes
        "T1001",  # Nursing assessment / evaluation
        "T1002",  # Rn services, up to 15 minutes
        "T1003",  # Lpn/lvn services, up to 15 minutes
        "T1004",  # Services of a qualified nursing aide, up to 15 minutes
        "T1005",  # Respite care services, up to 15 minutes
        "T1019",  # Personal care services, per 15 minutes, not for an inpatient or resident of a hospital, nursing facility, icf/mr or imd, part of the individualized plan of treatment (code may not be used to identify services provided by home health aide or certified nurse assistant)
        "T1020",  # Personal care services, per diem, not for an inpatient or resident of a hospital, nursing facility, icf/mr or imd, part of the individualized plan of treatment (code may not be used to identify services provided by home health aide or certified nurse assistant)
        "T1021",  # Home health aide or certified nurse assistant, per visit
        "T1022",  # Contracted home health agency services, all services provided under contract, per day
        "T1030",  # Nursing care, in the home, by registered nurse, per diem
        "T1031",  # Nursing care, in the home, by licensed practical nurse, per diem
    }


class HomeHealthcareServices(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for home health visits.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for a home health visit for the evaluation and management of a new or established patient.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS131v14
    """

    VALUE_SET_NAME = "Home Healthcare Services"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1016"
    DEFINITION_VERSION = "20240110"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99341",  # Home/residence visit, new patient; straightforward MDM or 15+ minutes total time
        "99342",  # Home/residence visit, new patient; low MDM or 30+ minutes total time
        "99344",  # Home/residence visit, new patient; moderate MDM or 60+ minutes total time
        "99345",  # Home/residence visit, new patient; high MDM or 75+ minutes total time
        "99347",  # Home/residence visit, established patient; straightforward MDM or 20+ minutes total time
        "99348",  # Home/residence visit, established patient; low MDM or 30+ minutes total time
        "99349",  # Home/residence visit, established patient; moderate MDM or 40+ minutes total time
        "99350",  # Home/residence visit, established patient; high MDM or 60+ minutes total time
    }
    SNOMEDCT = {
        "185460008",  # Home visit request by patient (procedure)
        "185462000",  # Home visit request by relative (procedure)
        "185466002",  # Home visit for urgent condition (procedure)
        "185467006",  # Home visit for acute condition (procedure)
        "185468001",  # Home visit for chronic condition (procedure)
        "185470005",  # Home visit elderly assessment (procedure)
        "225929007",  # Joint home visit (procedure)
        "315205008",  # Bank holiday home visit (procedure)
        "439708006",  # Home visit (procedure)
        "698704008",  # Home visit for rheumatology service (procedure)
        "704126008",  # Home visit for anticoagulant drug monitoring (procedure)
    }

    
class HospiceEncounter(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for hospice care services..

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent hospice services in a hospice, home or inpatient setting.

    **Exclusion Criteria:** Excludes concepts that represent palliative care or comfort measures.

    ** Used in:** CMS131v14
    """

    VALUE_SET_NAME = "Hospice Encounter"
    OID = "2.16.840.1.113883.3.464.1003.1003"
    DEFINITION_VERSION = "20210820"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    HCPCSLEVELII = {
        "G9473",  # Services performed by chaplain in the hospice setting, each 15 minutes
        "G9474",  # Services performed by dietary counselor in the hospice setting, each 15 minutes
        "G9475",  # Services performed by other counselor in the hospice setting, each 15 minutes
        "G9476",  # Services performed by volunteer in the hospice setting, each 15 minutes
        "G9477",  # Services performed by care coordinator in the hospice setting, each 15 minutes
        "G9478",  # Services performed by other qualified therapist in the hospice setting, each 15 minutes
        "G9479",  # Services performed by qualified pharmacist in the hospice setting, each 15 minutes
        "Q5003",  # Hospice care provided in nursing long term care facility (ltc) or non-skilled nursing facility (nf)
        "Q5004",  # Hospice care provided in skilled nursing facility (snf)
        "Q5005",  # Hospice care provided in inpatient hospital
        "Q5006",  # Hospice care provided in inpatient hospice facility
        "Q5007",  # Hospice care provided in long term care facility
        "Q5008",  # Hospice care provided in inpatient psychiatric facility
        "Q5010",  # Hospice home care provided in a hospice facility
        "S9126",  # Hospice care, in the home, per diem
        "T2042",  # Hospice routine home care; per diem
        "T2043",  # Hospice continuous home care; per hour
        "T2044",  # Hospice inpatient respite care; per diem
        "T2045",  # Hospice general inpatient care; per diem
        "T2046",  # Hospice long term care, room and board only; per diem
    }

    SNOMEDCT = {
        "183919006",  # Urgent admission to hospice (procedure)
        "183920000",  # Routine admission to hospice (procedure)
        "183921001",  # Admission to hospice for respite (procedure)
        "305336008",  # Admission to hospice (procedure)
        "305911006",  # Seen in hospice (finding)
        "385765002",  # Hospice care management (procedure)
    }


class OfficeVisit(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for an outpatient visit.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for the comprehensive history, evaluation, and management of a patient presenting with minor to high severity problems.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS135v10, CMS90v11, CMS249v4, CMS349v4, CMS142v10, CMS134v10, CMS177v10, CMS165v10, CMS143v10, CMS146v10, CMS157v10, CMS124v10, CMS50v10, CMS139v10, CMS154v10, CMS161v10, CMS56v10, CMS74v11, CMS645v5, CMS138v10, CMS137v10, CMS136v11, CMS128v10, CMS122v10, CMS153v10, CMS144v10, CMS66v10, CMS130v10, CMS646v2, CMS155v10, CMS127v10, CMS771v3, CMS117v10, CMS131v10, CMS149v10, CMS347v5, CMS156v10, CMS147v11, CMS125v10, CMS145v10
    """

    VALUE_SET_NAME = "Office Visit"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1001"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99202",  # Office or other outpatient visit for the evaluation and management of a new patient... 15 minutes or more
        "99203",  # Office or other outpatient visit for the evaluation and management of a new patient... 30 minutes or more
        "99204",  # Office or other outpatient visit for the evaluation and management of a new patient... 45 minutes or more
        "99205",  # Office or other outpatient visit for the evaluation and management of a new patient... 60 minutes or more
        "99212",  # Office or other outpatient visit for the evaluation and management of an established patient... 10 minutes or more
        "99213",  # Office or other outpatient visit for the evaluation and management of an established patient... 20 minutes or more
        "99214",  # Office or other outpatient visit for the evaluation and management of an established patient... 30 minutes or more
        "99215",  # Office or other outpatient visit for the evaluation and management of an established patient... 40 minutes or more
    }

    SNOMEDCT = {
        "185349003",  # Encounter for check up (procedure)
        "185463005",  # Visit out of hours (procedure)
        "185464004",  # Out of hours visit - not night visit (procedure)
        "185465003",  # Weekend visit (procedure)
        "3391000175108",  # Office visit for pediatric care and assessment (procedure)
        "439740005",  # Postoperative follow-up visit (procedure)
    }


class PreventiveCareServicesEstablishedOfficeVisit18AndUp(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for preventive care.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for comprehensive preventive medicine reevaluation and management of an established patient 18 years of age or over.

    **Exclusion Criteria:** Excludes initial visits for new patients.

    ** Used in:**   CMS131v14
    """

    VALUE_SET_NAME = "Preventive Care Services Established Office Visit, 18 and Up"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1025"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"
    
    CPT = {
        "99395",  # Periodic comprehensive preventive medicine reevaluation and management, established patient; 18-39 years
        "99396",  # Periodic comprehensive preventive medicine reevaluation and management, established patient; 40-64 years
        "99397",  # Periodic comprehensive preventive medicine reevaluation and management, established patient; 65 years and older
        "99385",  # Initial comprehensive preventive medicine evaluation and management, new patient; 18-39 years
        "99386",  # Initial comprehensive preventive medicine evaluation and management, new patient; 40-64 years
        "99387",  # Initial comprehensive preventive medicine evaluation and management, new patient; 65 years and older
    }


class OphthalmologicalServices(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of encounters for ophthalmological visits.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for a visit with an eye care professional.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS131v14
    """

    VALUE_SET_NAME = "Ophthalmological Services"
    OID = "2.16.840.1.113883.3.526.3.1285"
    DEFINITION_VERSION = "20210209"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "92002",  # Ophthalmological services: medical examination and evaluation with initiation of diagnostic and treatment program; intermediate, new patient
        "92004",  # Ophthalmological services: medical examination and evaluation with initiation of diagnostic and treatment program; comprehensive, new patient, 1 or more visits
        "92012",  # Ophthalmological services: medical examination and evaluation, with initiation or continuation of diagnostic and treatment program; intermediate, established patient
        "92014",  # Ophthalmological services: medical examination and evaluation, with initiation or continuation of diagnostic and treatment program; comprehensive, established patient, 1 or more visits
    }
    SNOMEDCT = {
        "359960003",  # Ophthalmologic examination and evaluation under general anesthesia, limited (procedure)
        "36228007",  # Ophthalmic examination and evaluation (procedure)
        "66902005",  # Ophthalmic examination and evaluation, follow-up (procedure)
        "78831002",  # Comprehensive eye examination (procedure)
    }


class PalliativeCareEncounter(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for palliative care services.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for admission and management for palliative care services.

    **Exclusion Criteria:** Excludes concepts that represent encounters for hospice and a referral to palliative care.

    ** Used in:** CMS131v14
    """

    VALUE_SET_NAME = "Palliative Care Encounter"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1090"
    DEFINITION_VERSION = "20210224"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    HCPCSLEVELII = {
        "G9054", # Oncology; primary focus of visit; supervising, coordinating or managing care of patient with terminal cancer or for whom other medical illness prevents further cancer treatment; includes symptom management, end-of-life care planning, management of palliative therapies (for use in a medicare-approved demonstration project)
        }

    SNOMEDCT = {
        "305284002",     # Admission by palliative care physician (procedure)
        "305381007",     # Admission to palliative care department (procedure)
        "305686008",     # Seen by palliative care physician (finding)
        "305824005",     # Seen by palliative care medicine service (finding)
        "441874000",     # Seen by palliative care service (finding)
        "4901000124101", # Palliative care education (procedure)
        "713281006",     # Consultation for palliative care (procedure)
    }

    ICD10CM = {
        "Z515",  # Encounter for palliative care
    }


class TelephoneVisits(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for telephone visits.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for assessment, evaluation and management services to a patient by telephone.

    **Exclusion Criteria:** Excludes concepts that represent an encounter for telephone assessment, evaluation and management services that last for less than five minutes.

    ** Used in:** CMS131v14
    """

    VALUE_SET_NAME = "Telephone Visits"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1080"
    DEFINITION_VERSION = "20250205"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99441",  # MD/QHP telephone E/M, established patient; 5–10 minutes of medical discussion
        "99442",  # MD/QHP telephone E/M, established patient; 11–20 minutes of medical discussion
        "99443",  # MD/QHP telephone E/M, established patient; 21–30 minutes of medical discussion
        "98008",  # Audio-only E/M, new patient; straightforward MDM; >10 min, total time ≥15 min
        "98009",  # Audio-only E/M, new patient; low MDM; >10 min, total time ≥30 min
        "98010",  # Audio-only E/M, new patient; moderate MDM; >10 min, total time ≥45 min
        "98011",  # Audio-only E/M, new patient; high MDM; >10 min, total time ≥60 min
        "98012",  # Audio-only E/M, established patient; straightforward MDM; >10 min, time >10 min
        "98013",  # Audio-only E/M, established patient; low MDM; >10 min, total time ≥20 min
        "98014",  # Audio-only E/M, established patient; moderate MDM; >10 min, total time ≥30 min
        "98015",  # Audio-only E/M, established patient; high MDM; >10 min, total time ≥40 min
        "98966",  # Nonphysician telephone assessment/management, established pt; 5–10 min
        "98967",  # Nonphysician telephone assessment/management, established pt; 11–20 min
        "98968",  # Nonphysician telephone assessment/management, established pt; 21–30 min
    }

    SNOMEDCT = {
        "185317003",  # Telephone encounter (procedure)
        "314849005",  # Telephone contact by consultant (procedure)
        "386472008",  # Telephone consultation (procedure)
        "386473003",  # Telephone follow-up (procedure)
        "401267002",  # Telephone triage encounter (procedure)
    }


__exports__ = (AnnualWellnessVisit, EncounterInpatient, FrailtyEncounter, HomeHealthcareServices, HospiceEncounter, OfficeVisit, PreventiveCareServicesEstablishedOfficeVisit18AndUp, OphthalmologicalServices, PalliativeCareEncounter, TelephoneVisits,)