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

class EmergencyDepartmentVisit(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters in the emergency department (ED).

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter ocurring in the emergency department (ED).

    **Exclusion Criteria:** Excludes concepts that represent services not performed in the emergency department, including critical care and observation services.
    """

    VALUE_SET_NAME = "Emergency Department Visit"
    OID = "2.16.840.1.113883.3.117.1.7.1.292"
    DEFINITION_VERSION = "20210611"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "4525004",  # Emergency department patient visit (procedure)
    }

class ObservationServices(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for observation.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for observation in the inpatient or outpatient setting.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Observation Services"
    OID = "2.16.840.1.113762.1.4.1111.143"
    DEFINITION_VERSION = "20210611"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "448951000124107",  # Admission to observation unit (procedure)
    }

class EdVisitAndObTriage(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to group concepts for encounters in the emergency department (ED) or OB triage represented as observation status.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter occurring in the emergency department (ED) or OB triage represented as observation status.

    **Exclusion Criteria:** Excludes concepts that represent services not performed in the emergency department or OB triage represented as observation status.
    """

    VALUE_SET_NAME = "ED Visit and OB Triage"
    OID = "2.16.840.1.113762.1.4.1029.369"
    DEFINITION_VERSION = "20210611"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "42102002",  # Pre-admission observation, undelivered mother (procedure)
        "4525004",  # Emergency department patient visit (procedure)
    }

class NonelectiveInpatientEncounter(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of encounters for non-elective inpatient admission.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for a non-elective inpatient admission.

    **Exclusion Criteria:** Excludes concepts that represent an encounter for an elective inpatient admission.
    """

    VALUE_SET_NAME = "Nonelective Inpatient Encounter"
    OID = "2.16.840.1.113883.3.117.1.7.1.424"
    DEFINITION_VERSION = "20250206"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "183452005",  # Emergency hospital admission (procedure)
        "32485007",  # Hospital admission (procedure)
        "442281000124108",  # Emergency hospital admission from observation unit (procedure)
    }

class OutpatientClinicalEncounters(ValueSet):
    """
    **Clinical Focus:** Office visit outpatient encounters for diabetes screening

    **Data Element Scope:** Allowable outpatient encounters for diabetes screening

    **Inclusion Criteria:** Office visits, outpatient visits, outpatient consultations, and telehealth services

    **Exclusion Criteria:** None
    """

    VALUE_SET_NAME = "Outpatient Clinical Encounters"
    OID = "2.16.840.1.113762.1.4.1160.24"
    DEFINITION_VERSION = "20250301"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "98000",  # Synchronous audio-video visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "98001",  # Synchronous audio-video visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "98002",  # Synchronous audio-video visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate medical decision making. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "98003",  # Synchronous audio-video visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "98004",  # Synchronous audio-video visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 10 minutes must be met or exceeded.
        "98005",  # Synchronous audio-video visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "98006",  # Synchronous audio-video visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "98007",  # Synchronous audio-video visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "98008",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination, straightforward medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "98009",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination, low medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "98010",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination, moderate medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "98011",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination, high medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "98012",  # Synchronous audio-only visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination, straightforward medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 10 minutes must be exceeded.
        "98013",  # Synchronous audio-only visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination, low medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "98014",  # Synchronous audio-only visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination, moderate medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "98015",  # Synchronous audio-only visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination, high medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99202",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "99203",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99204",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "99205",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "99212",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 10 minutes must be met or exceeded.
        "99213",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99214",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99215",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99242",  # Office or other outpatient consultation for a new or established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99243",  # Office or other outpatient consultation for a new or established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99244",  # Office or other outpatient consultation for a new or established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99245",  # Office or other outpatient consultation for a new or established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 55 minutes must be met or exceeded.
        "99341",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "99342",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99344",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "99345",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 75 minutes must be met or exceeded.
        "99347",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99348",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99349",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99350",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
    }

    HCPCSLEVELII = {
        "G0463",  # Hospital outpatient clinic visit for assessment and management of a patient
        "T1015",  # Clinic visit/encounter, all-inclusive
    }

    SNOMEDCT = {
        "11429006",  # Consultation (procedure)
        "185463005",  # Visit out of hours (procedure)
        "185464004",  # Out of hours visit - not night visit (procedure)
        "185465003",  # Weekend visit (procedure)
        "281036007",  # Follow-up consultation (procedure)
        "3391000175108",  # Office visit for pediatric care and assessment (procedure)
        "371883000",  # Outpatient procedure (procedure)
        "439740005",  # Postoperative follow-up visit (procedure)
        "77406008",  # Confirmatory medical consultation (procedure)
    }

class PreventativeClinicalEncounters(ValueSet):
    """
    **Clinical Focus:** Preventative care outpatient encounters for diabetes screening

    **Data Element Scope:** Allowable outpatient encounters for diabetes screening

    **Inclusion Criteria:** Annual wellness visits, outpatient visits, and outpatient preventative care

    **Exclusion Criteria:** None
    """

    VALUE_SET_NAME = "Preventative Clinical Encounters"
    OID = "2.16.840.1.113762.1.4.1160.13"
    DEFINITION_VERSION = "20250301"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99385",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 18-39 years
        "99386",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 40-64 years
        "99387",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 65 years and older
        "99395",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 18-39 years
        "99396",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 40-64 years
        "99397",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 65 years and older
        "99401",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 15 minutes
        "99402",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 30 minutes
        "99403",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 45 minutes
        "99404",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 60 minutes
        "99429",  # Unlisted preventive medicine service
    }

    HCPCSLEVELII = {
        "G0402",  # Initial preventive physical examination; face-to-face visit, services limited to new beneficiary during the first 12 months of medicare enrollment
        "G0438",  # Annual wellness visit; includes a personalized prevention plan of service (pps), initial visit
        "G0439",  # Annual wellness visit, includes a personalized prevention plan of service (pps), subsequent visit
    }

    SNOMEDCT = {
        "108219001",  # Physician visit with evaluation AND/OR management service (procedure)
        "108220007",  # Evaluation AND/OR management - new patient (procedure)
        "108221006",  # Evaluation AND/OR management - established patient (procedure)
        "108224003",  # Preventive patient evaluation (procedure)
        "14736009",  # History and physical examination with evaluation and management of patient (procedure)
        "185349003",  # Encounter for check up (procedure)
        "185389009",  # Follow-up visit (procedure)
        "270427003",  # Patient-initiated encounter (procedure)
        "270430005",  # Provider-initiated encounter (procedure)
        "308335008",  # Patient encounter procedure (procedure)
        "390906007",  # Follow-up encounter (procedure)
        "410187005",  # Physical evaluation management (procedure)
        "444971000124105",  # Annual wellness visit (procedure)
        "456201000124103",  # Medicare annual wellness visit (procedure)
        "78318003",  # History and physical examination, annual for health maintenance (procedure)
        "86013001",  # Periodic reevaluation and management of healthy individual (procedure)
        "90526000",  # Initial evaluation and management of healthy individual (procedure)
    }

class FaceToFaceInteraction(ValueSet):
    """
    **Clinical Focus:** This value set identifies patients who have had a face-to-face interaction with a member of their medical care team.

    **Data Element Scope:** This value set was intended to map to the QDM data type of encounter.

    **Inclusion Criteria:** Includes both initial and follow up visits. Includes home visits, inpatient and outpatient visits, and nursing facility visits.

    **Exclusion Criteria:** Excludes visits that are not performed in-person, including telehealth services.
    """

    VALUE_SET_NAME = "Face to Face Interaction"
    OID = "2.16.840.1.113762.1.4.1248.375"
    DEFINITION_VERSION = "20250325"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "12843005",  # Subsequent hospital visit by physician (procedure)
        "18170008",  # Subsequent nursing facility visit (procedure)
        "185349003",  # Encounter for check up (procedure)
        "185463005",  # Visit out of hours (procedure)
        "185465003",  # Weekend visit (procedure)
        "19681004",  # Nursing evaluation of patient and report (procedure)
        "207195004",  # History and physical examination with evaluation and management of nursing facility patient (procedure)
        "270427003",  # Patient-initiated encounter (procedure)
        "270430005",  # Provider-initiated encounter (procedure)
        "308335008",  # Patient encounter procedure (procedure)
        "390906007",  # Follow-up encounter (procedure)
        "406547006",  # Urgent follow-up (procedure)
        "439708006",  # Home visit (procedure)
        "87790002",  # Follow-up inpatient consultation visit (procedure)
        "90526000",  # Initial evaluation and management of healthy individual (procedure)
    }

class OutpatientConsultation(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for outpatient interactions with a member of the medical care team.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for the comprehensive history, evaluation, and management of a patient presenting with minor to high severity problems.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Outpatient Consultation"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1008"
    DEFINITION_VERSION = "20240110"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99242",  # Office or other outpatient consultation for a new or established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99243",  # Office or other outpatient consultation for a new or established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99244",  # Office or other outpatient consultation for a new or established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99245",  # Office or other outpatient consultation for a new or established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 55 minutes must be met or exceeded.
    }

    SNOMEDCT = {
        "281036007",  # Follow-up consultation (procedure)
        "77406008",  # Confirmatory medical consultation (procedure)
    }

class PreventiveCareServicesInitialOfficeVisit18AndUp(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for preventive care.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for comprehensive preventive medicine reevaluation and management of a new patient 18 years or over.

    **Exclusion Criteria:** Excludes visits for established patients.
    """

    VALUE_SET_NAME = "Preventive Care Services Initial Office Visit, 18 and Up"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1023"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99385",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 18-39 years
        "99386",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 40-64 years
        "99387",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 65 years and older
    }

class PreventiveCareServicesInitialOfficeVisit0To17(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for preventive care.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for comprehensive preventive medicine reevaluation and management of a new patient 0 to 17 years of age.

    **Exclusion Criteria:** Excludes visits for established patients.
    """

    VALUE_SET_NAME = "Preventive Care Services, Initial Office Visit, 0 to 17"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1022"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99381",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; infant (age younger than 1 year)
        "99382",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; early childhood (age 1 through 4 years)
        "99383",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; late childhood (age 5 through 11 years)
        "99384",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; adolescent (age 12 through 17 years)
    }

class PreventiveCareEstablishedOfficeVisit0To17(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for preventative care.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for comprehensive preventive medicine reevaluation and management of an established patient 0 to 17 years of age.

    **Exclusion Criteria:** Excludes initial visits for new patients.
    """

    VALUE_SET_NAME = "Preventive Care, Established Office Visit, 0 to 17"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1024"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99391",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; infant (age younger than 1 year)
        "99392",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; early childhood (age 1 through 4 years)
        "99393",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; late childhood (age 5 through 11 years)
        "99394",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; adolescent (age 12 through 17 years)
    }

class OutpatientEncounter(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for outpatient visits.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for comprehensive history, evaluation, and management of a patient in an outpatient setting.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Outpatient Encounter"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1087"
    DEFINITION_VERSION = "20250328"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99202",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "99203",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99204",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "99205",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "99211",  # Office or other outpatient visit for the evaluation and management of an established patient that may not require the presence of a physician or other qualified health care professional
        "99212",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 10 minutes must be met or exceeded.
        "99213",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99214",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99215",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99242",  # Office or other outpatient consultation for a new or established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99243",  # Office or other outpatient consultation for a new or established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99244",  # Office or other outpatient consultation for a new or established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99245",  # Office or other outpatient consultation for a new or established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 55 minutes must be met or exceeded.
        "99341",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "99342",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99344",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "99345",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 75 minutes must be met or exceeded.
        "99347",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99348",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99349",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99350",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "99381",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; infant (age younger than 1 year)
        "99382",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; early childhood (age 1 through 4 years)
        "99383",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; late childhood (age 5 through 11 years)
        "99384",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; adolescent (age 12 through 17 years)
        "99385",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 18-39 years
        "99386",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 40-64 years
        "99387",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 65 years and older
        "99391",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; infant (age younger than 1 year)
        "99392",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; early childhood (age 1 through 4 years)
        "99393",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; late childhood (age 5 through 11 years)
        "99394",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; adolescent (age 12 through 17 years)
        "99395",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 18-39 years
        "99396",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 40-64 years
        "99397",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 65 years and older
        "99401",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 15 minutes
        "99402",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 30 minutes
        "99403",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 45 minutes
        "99404",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 60 minutes
        "99411",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to individuals in a group setting (separate procedure); approximately 30 minutes
        "99412",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to individuals in a group setting (separate procedure); approximately 60 minutes
        "99429",  # Unlisted preventive medicine service
        "99455",  # Work related or medical disability examination by the treating physician that includes: Completion of a medical history commensurate with the patient's condition; Performance of an examination commensurate with the patient's condition; Formulation of a diagnosis, assessment of capabilities and stability, and calculation of impairment; Development of future medical treatment plan; and Completion of necessary documentation/certificates and report.
        "99456",  # Work related or medical disability examination by other than the treating physician that includes: Completion of a medical history commensurate with the patient's condition; Performance of an examination commensurate with the patient's condition; Formulation of a diagnosis, assessment of capabilities and stability, and calculation of impairment; Development of future medical treatment plan; and Completion of necessary documentation/certificates and report.
        "99483",  # Assessment of and care planning for a patient with cognitive impairment, requiring an independent historian, in the office or other outpatient, home or domiciliary or rest home, with all of the following required elements: Cognition-focused evaluation including a pertinent history and examination, Medical decision making of moderate or high complexity, Functional assessment (eg, basic and instrumental activities of daily living), including decision-making capacity, Use of standardized instruments for staging of dementia (eg, functional assessment staging test [FAST], clinical dementia rating [CDR]), Medication reconciliation and review for high-risk medications, Evaluation for neuropsychiatric and behavioral symptoms, including depression, including use of standardized screening instrument(s), Evaluation of safety (eg, home), including motor vehicle operation, Identification of caregiver(s), caregiver knowledge, caregiver needs, social supports, and the willingness of caregiver to take on caregiving tasks, Development, updating or revision, or review of an Advance Care Plan, Creation of a written care plan, including initial plans to address any neuropsychiatric symptoms, neuro-cognitive symptoms, functional limitations, and referral to community resources as needed (eg, rehabilitation services, adult day programs, support groups) shared with the patient and/or caregiver with initial education and support. Typically, 60 minutes of total time is spent on the date of the encounter.
    }

    HCPCSLEVELII = {
        "G0402",  # Initial preventive physical examination; face-to-face visit, services limited to new beneficiary during the first 12 months of medicare enrollment
        "G0438",  # Annual wellness visit; includes a personalized prevention plan of service (pps), initial visit
        "G0439",  # Annual wellness visit, includes a personalized prevention plan of service (pps), subsequent visit
        "G0463",  # Hospital outpatient clinic visit for assessment and management of a patient
        "T1015",  # Clinic visit/encounter, all-inclusive
    }

    SNOMEDCT = {
        "185463005",  # Visit out of hours (procedure)
        "185464004",  # Out of hours visit - not night visit (procedure)
        "185465003",  # Weekend visit (procedure)
        "281036007",  # Follow-up consultation (procedure)
        "3391000175108",  # Office visit for pediatric care and assessment (procedure)
        "439740005",  # Postoperative follow-up visit (procedure)
        "444971000124105",  # Annual wellness visit (procedure)
        "77406008",  # Confirmatory medical consultation (procedure)
        "84251009",  # Comprehensive consultation (procedure)
    }

class VirtualEncounter(ValueSet):
    """
    **Clinical Focus:** Includes concepts that represent an encounter using online modalities.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter using online modalities.

    **Exclusion Criteria:** Excludes concepts that represent encounters other than online.
    """

    VALUE_SET_NAME = "Virtual Encounter"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1089"
    DEFINITION_VERSION = "20210224"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "98970",  # Nonphysician qualified health care professional online digital assessment and management, for an established patient, for up to 7 days, cumulative time during the 7 days; 5-10 minutes
        "98971",  # Nonphysician qualified health care professional online digital assessment and management, for an established patient, for up to 7 days, cumulative time during the 7 days; 11-20 minutes
        "98972",  # Nonphysician qualified health care professional online digital assessment and management, for an established patient, for up to 7 days, cumulative time during the 7 days; 21 or more minutes
        "98980",  # Remote therapeutic monitoring treatment management services, physician or other qualified health care professional time in a calendar month requiring at least one interactive communication with the patient or caregiver during the calendar month; first 20 minutes
        "98981",  # Remote therapeutic monitoring treatment management services, physician or other qualified health care professional time in a calendar month requiring at least one interactive communication with the patient or caregiver during the calendar month; each additional 20 minutes (List separately in addition to code for primary procedure)
        "99421",  # Online digital evaluation and management service, for an established patient, for up to 7 days, cumulative time during the 7 days; 5-10 minutes
        "99422",  # Online digital evaluation and management service, for an established patient, for up to 7 days, cumulative time during the 7 days; 11-20 minutes
        "99423",  # Online digital evaluation and management service, for an established patient, for up to 7 days, cumulative time during the 7 days; 21 or more minutes
        "99457",  # Remote physiologic monitoring treatment management services, clinical staff/physician/other qualified health care professional time in a calendar month requiring interactive communication with the patient/caregiver during the month; first 20 minutes
        "99458",  # Remote physiologic monitoring treatment management services, clinical staff/physician/other qualified health care professional time in a calendar month requiring interactive communication with the patient/caregiver during the month; each additional 20 minutes (List separately in addition to code for primary procedure)
    }

    HCPCSLEVELII = {
        "G2012",  # Brief communication technology-based service, e.g. virtual check-in, by a physician or other qualified health care professional who can report evaluation and management services, provided to an established patient, not originating from a related e/m service provided within the previous 7 days nor leading to an e/m service or procedure within the next 24 hours or soonest available appointment; 5-10 minutes of medical discussion
        "G0071",  # Payment for communication technology-based services for 5 minutes or more of a virtual (non-face-to-face) communication between an rural health clinic (rhc) or federally qualified health center (fqhc) practitioner and rhc or fqhc patient, or 5 minutes or more of remote evaluation of recorded video and/or images by an rhc or fqhc practitioner, occurring in lieu of an office visit; rhc or fqhc only
        "G2010",  # Remote evaluation of recorded video and/or images submitted by an established patient (e.g., store and forward), including interpretation with follow-up with the patient within 24 business hours, not originating from a related e/m service provided within the previous 7 days nor leading to an e/m service or procedure within the next 24 hours or soonest available appointment
        "G2250",  # Remote assessment of recorded video and/or images submitted by an established patient (e.g., store and forward), including interpretation with follow-up with the patient within 24 business hours, not originating from a related service provided within the previous 7 days nor leading to a service or procedure within the next 24 hours or soonest available appointment
        "G2251",  # Brief communication technology-based service, e.g. virtual check-in, by a qualified health care professional who cannot report evaluation and management services, provided to an established patient, not originating from a related service provided within the previous 7 days nor leading to a service or procedure within the next 24 hours or soonest available appointment; 5-10 minutes of clinical discussion
        "G2252",  # Brief communication technology-based service, e.g. virtual check-in, by a physician or other qualified health care professional who can report evaluation and management services, provided to an established patient, not originating from a related e/m service provided within the previous 7 days nor leading to an e/m service or procedure within the next 24 hours or soonest available appointment; 11-20 minutes of medical discussion
    }

class ElectiveInpatientEncounter(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of elective inpatient encounters

    **Data Element Scope:** Includes concepts that represent inpatient encounters

    **Inclusion Criteria:** This value set may use a model element related to Encounter

    **Exclusion Criteria:** N/A
    """

    VALUE_SET_NAME = "Elective Inpatient Encounter"
    OID = "2.16.840.1.113762.1.4.1248.85"
    DEFINITION_VERSION = "20230518"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "112689000",  # Hospital admission, elective, with complete pre-admission work-up (procedure)
        "15584006",  # Hospital admission, elective, with partial pre-admission work-up (procedure)
        "81672003",  # Hospital admission, elective, without pre-admission work-up (procedure)
        "8715000",  # Hospital admission, elective (procedure)
    }

class OutpatientSurgeryService(ValueSet):
    """
    **Clinical Focus:** This value set contains concepts that are used to identify outpatient surgery encounter types.

    **Data Element Scope:** This value set may use Quality Data Model (QDM) category related to Encounter, Performed. The intent of this data element is to identify patients who have had an outpatient surgery encounter.

    **Inclusion Criteria:** Includes only relevant concepts associated with SNOMED codes identifying outpatient surgery encounters.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Outpatient Surgery Service"
    OID = "2.16.840.1.113762.1.4.1110.38"
    DEFINITION_VERSION = "20190426"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "110468005",  # Ambulatory surgery (procedure)
        "709063003",  # Admission to same day surgery center (procedure)
        "711580002",  # Minor ambulatory surgery (procedure)
    }

class NutritionServices(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for nutrition services.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent nutrition services.

    **Exclusion Criteria:** Excludes concepts for nutrition services limited to a specific diagnosis.
    """

    VALUE_SET_NAME = "Nutrition Services"
    OID = "2.16.840.1.113883.3.464.1003.1006"
    DEFINITION_VERSION = "20210819"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "97802",  # Medical nutrition therapy; initial assessment and intervention, individual, face-to-face with the patient, each 15 minutes
        "97803",  # Medical nutrition therapy; re-assessment and intervention, individual, face-to-face with the patient, each 15 minutes
        "97804",  # Medical nutrition therapy; group (2 or more individual(s)), each 30 minutes
    }

    HCPCSLEVELII = {
        "G0270",  # Medical nutrition therapy; reassessment and subsequent intervention(s) following second referral in same year for change in diagnosis, medical condition or treatment regimen (including additional hours needed for renal disease), individual, face to face with the patient, each 15 minutes
        "G0271",  # Medical nutrition therapy, reassessment and subsequent intervention(s) following second referral in same year for change in diagnosis, medical condition, or treatment regimen (including additional hours needed for renal disease), group (2 or more individuals), each 30 minutes
        "G0447",  # Face-to-face behavioral counseling for obesity, 15 minutes
        "S9449",  # Weight management classes, non-physician provider, per session
        "S9452",  # Nutrition classes, non-physician provider, per session
        "S9470",  # Nutritional counseling, dietitian visit
    }

    SNOMEDCT = {
        "11816003",  # Diet education (procedure)
        "14051000175103",  # Dietary education for cardiovascular disorder (procedure)
        "183059007",  # High fiber diet education (procedure)
        "183060002",  # Low residue diet education (procedure)
        "183061003",  # Low fat diet education (procedure)
        "183062005",  # Low cholesterol diet education (procedure)
        "183063000",  # Low salt diet education (procedure)
        "183065007",  # Low carbohydrate diet education (procedure)
        "183066008",  # Low protein diet education (procedure)
        "183067004",  # High protein diet education (procedure)
        "183070000",  # Vegetarian diet education (procedure)
        "183071001",  # Vegan diet education (procedure)
        "226067002",  # Food hygiene education (procedure)
        "266724001",  # Weight-reducing diet education (procedure)
        "275919002",  # Weight loss advised (situation)
        "281085002",  # Sugar-free diet education (procedure)
        "284352003",  # Obesity diet education (procedure)
        "305849009",  # Seen by dietetics service (finding)
        "305850009",  # Seen by community-based dietetics service (finding)
        "305851008",  # Seen by hospital-based dietetics service (finding)
        "306163007",  # Referral to dietetics service (procedure)
        "306164001",  # Referral to community-based dietetics service (procedure)
        "306165000",  # Referral to hospital-based dietetics service (procedure)
        "306626002",  # Discharge from dietetics service (procedure)
        "306627006",  # Discharge from hospital dietetics service (procedure)
        "306628001",  # Discharge from community dietetics service (procedure)
        "313210009",  # Fluid intake education (procedure)
        "370847001",  # Dietary needs education (procedure)
        "386464006",  # Prescribed diet education (procedure)
        "404923009",  # Weight gain advised (situation)
        "408910007",  # Enteral feeding education (procedure)
        "410171007",  # Nutrition care education (procedure)
        "410177006",  # Special diet education (procedure)
        "410200000",  # Weight control education (procedure)
        "428461000124101",  # Referral to nutrition professional (procedure)
        "428691000124107",  # Vitamin K dietary intake education (procedure)
        "429095004",  # Dietary education for weight gain (procedure)
        "431482008",  # Dietary education for competitive athlete (procedure)
        "441041000124100",  # Counseling about nutrition (regime/therapy)
        "441201000124108",  # Counseling about nutrition using cognitive behavioral theoretical approach (regime/therapy)
        "441231000124100",  # Counseling about nutrition using health belief model (regime/therapy)
        "441241000124105",  # Counseling about nutrition using social learning theory approach (regime/therapy)
        "441251000124107",  # Counseling about nutrition using transtheoretical model and stages of change approach (regime/therapy)
        "441261000124109",  # Counseling about nutrition using motivational interviewing technique (regime/therapy)
        "441271000124102",  # Counseling about nutrition using goal setting strategy (regime/therapy)
        "441281000124104",  # Counseling about nutrition using self-monitoring strategy (regime/therapy)
        "441291000124101",  # Counseling about nutrition using problem solving strategy (regime/therapy)
        "441301000124100",  # Counseling about nutrition using social support strategy (regime/therapy)
        "441311000124102",  # Counseling about nutrition using stress management strategy (regime/therapy)
        "441321000124105",  # Counseling about nutrition using stimulus control strategy (regime/therapy)
        "441331000124108",  # Counseling about nutrition using cognitive restructuring strategy (regime/therapy)
        "441341000124103",  # Counseling about nutrition using relapse prevention strategy (regime/therapy)
        "441351000124101",  # Counseling about nutrition using rewards and contingency management strategy (regime/therapy)
        "443288003",  # Lifestyle education regarding diet (procedure)
        "445291000124103",  # Nutrition-related skill education (procedure)
        "445301000124102",  # Content-related nutrition education (procedure)
        "445331000124105",  # Nutrition-related laboratory result interpretation education (procedure)
        "445641000124105",  # Technical nutrition education (procedure)
        "609104008",  # Educated about weight management (situation)
        "61310001",  # Nutrition education (procedure)
        "698471002",  # Patient advised about weight management (situation)
        "699827002",  # Dietary education about fluid restriction (procedure)
        "699829004",  # High energy diet education (procedure)
        "699830009",  # Food fortification education (procedure)
        "699849008",  # Healthy eating education (procedure)
        "700154005",  # Seen in weight management clinic (finding)
        "700258004",  # Dietary education about vitamin intake (procedure)
        "705060005",  # Diet education about mineral intake (procedure)
        "710881000",  # Education about eating pattern (procedure)
    }

class DecisionToAdmitToHospitalInpatient(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of a decision to admit to hospital inpatient order.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter of a decision to admit a patient to an inpatient hospital.

    **Exclusion Criteria:** No exclusions
    """

    VALUE_SET_NAME = "Decision to Admit to Hospital Inpatient"
    OID = "2.16.840.1.113883.3.117.1.7.1.294"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "10378005",  # Hospital admission, emergency, from emergency room, accidental injury (procedure)
        "19951005",  # Hospital admission, emergency, from emergency room, medical nature (procedure)
        "432661000124104",  # Hospital admission, transfer from emergency department (procedure)
        "73607007",  # Hospital admission, emergency, from emergency room (procedure)
    }

class EmergencyDepartmentEvaluationAndManagementVisit(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters in the emergency department.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for care provided to new and established patients in the emergency department.

    **Exclusion Criteria:** Excludes concepts that represent an encounter not representative of ED visits, including critical care and observation services.
    """

    VALUE_SET_NAME = "Emergency Department Evaluation and Management Visit"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1010"
    DEFINITION_VERSION = "20210928"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99281",  # Emergency department visit for the evaluation and management of a patient that may not require the presence of a physician or other qualified health care professional
        "99282",  # Emergency department visit for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and straightforward medical decision making
        "99283",  # Emergency department visit for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and low level of medical decision making
        "99284",  # Emergency department visit for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making
        "99285",  # Emergency department visit for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and high level of medical decision making
    }

    SNOMEDCT = {
        "4525004",  # Emergency department patient visit (procedure)
    }

class Triage(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for nurse/non-billable encounters.

    **Data Element Scope:** This value set may use the data element Encounter.

    **Inclusion Criteria:** Includes concepts that represent nursing or non-billable encounters in the emergency department.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Triage"
    OID = "2.16.840.1.113762.1.4.1046.279"
    DEFINITION_VERSION = "20250212"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "225390008",  # Triage (procedure)
        "245581009",  # Emergency examination for triage (procedure)
        "273887006",  # Triage index (assessment scale)
        "314850005",  # Seen by triage nurse (finding)
        "386478007",  # Triage: emergency center (procedure)
    }

class DecisionToTransfer(ValueSet):
    """
    **Clinical Focus:** This value set contains concepts that represent procedures used to identify transfer from emergency department (ED) locations.

    **Data Element Scope:** The intent of this data element is to identify patients transferred from emergency department (ED) locations.

    **Inclusion Criteria:** Includes only relevant concepts associated with SNOMED CT codes that identify the environment hierarchy to define an emergency department.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Decision to Transfer"
    OID = "2.16.840.1.113762.1.4.1046.286"
    DEFINITION_VERSION = "20240726"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "19712007",  # Patient transfer, to another health care facility (procedure)
        "448551000124100",  # Patient transfer to another hospital (procedure)
    }

class NursingFacilityVisit(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters in a nursing facility.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter specific to a nursing facility, including skilled, intermediate and long term care facilities.

    **Exclusion Criteria:** Excludes concepts that represent an encounter other than a nursing facility visits.
    """

    VALUE_SET_NAME = "Nursing Facility Visit"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1012"
    DEFINITION_VERSION = "20240110"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99304",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and straightforward or low level of medical decision making. When using total time on the date of the encounter for code selection, 25 minutes must be met or exceeded.
        "99305",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 35 minutes must be met or exceeded.
        "99306",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 50 minutes must be met or exceeded.
        "99307",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 10 minutes must be met or exceeded.
        "99308",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99309",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99310",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "99315",  # Nursing facility discharge management; 30 minutes or less total time on the date of the encounter
        "99316",  # Nursing facility discharge management; more than 30 minutes total time on the date of the encounter
    }

    SNOMEDCT = {
        "18170008",  # Subsequent nursing facility visit (procedure)
        "207195004",  # History and physical examination with evaluation and management of nursing facility patient (procedure)
    }

class PsychVisitDiagnosticEvaluation(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for diagnostic psychiatric evaluations.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for psychiatric diagnostic evaluations.

    **Exclusion Criteria:** Excludes concepts that represent an encounter for group psychotherapy or family psychotherapy visits.
    """

    VALUE_SET_NAME = "Psych Visit Diagnostic Evaluation"
    OID = "2.16.840.1.113883.3.526.3.1492"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "90791",  # Psychiatric diagnostic evaluation
        "90792",  # Psychiatric diagnostic evaluation with medical services
    }

    SNOMEDCT = {
        "10197000",  # Psychiatric interview and evaluation (procedure)
        "165172002",  # Diagnostic psychiatric interview (procedure)
        "68338001",  # Interactive medical psychiatric diagnostic interview (procedure)
        "79094001",  # Initial psychiatric interview with mental status and evaluation (procedure)
    }

class PsychVisitPsychotherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for psychotherapy visits.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for individual psychotherapy services.

    **Exclusion Criteria:** Excludes concepts that represent an encounter for group psychotherapy or family psychotherapy visits.
    """

    VALUE_SET_NAME = "Psych Visit Psychotherapy"
    OID = "2.16.840.1.113883.3.526.3.1496"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "90832",  # Psychotherapy, 30 minutes with patient
        "90834",  # Psychotherapy, 45 minutes with patient
        "90837",  # Psychotherapy, 60 minutes with patient
    }

    SNOMEDCT = {
        "183381005",  # General psychotherapy (regime/therapy)
        "183382003",  # Psychotherapy - behavioral (regime/therapy)
        "183383008",  # Psychotherapy - cognitive (regime/therapy)
        "18512000",  # Individual psychotherapy (regime/therapy)
        "302242004",  # Long-term psychodynamic psychotherapy (regime/therapy)
        "304820009",  # Developmental psychodynamic psychotherapy (regime/therapy)
        "304822001",  # Psychodynamic-interpersonal psychotherapy (regime/therapy)
        "314034001",  # Psychodynamic psychotherapy (regime/therapy)
        "38678006",  # Client-centered psychotherapy (regime/therapy)
        "401157001",  # Brief solution focused psychotherapy (regime/therapy)
        "443730003",  # Interpersonal psychotherapy (regime/therapy)
        "75516001",  # Psychotherapy (regime/therapy)
        "90102008",  # Social psychotherapy (regime/therapy)
    }

class CareServicesInLongTermResidentialFacility(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for patients living in assisted living, domiciliary care or rest homes.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for services provided to new and established patients living in assisted living, domiciliary care or rest home who have had an interaction with a member of their medical team.

    **Exclusion Criteria:** Excludes concepts that represent an encounter for settings other than assisted living, domiciliary care, or rest homes.
    """

    VALUE_SET_NAME = "Care Services in Long Term Residential Facility"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1014"
    DEFINITION_VERSION = "20240203"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "209099002",  # History and physical examination with management of domiciliary or rest home patient (procedure)
        "210098006",  # Domiciliary or rest home patient evaluation and management (procedure)
    }

class PatientProviderInteraction(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters or communications.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter in an office or care setting, as well as interactions that occur via virtual methods, such as telephone calls, emails, and letters.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Patient Provider Interaction"
    OID = "2.16.840.1.113883.3.526.3.1012"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "185316007",  # Indirect encounter (procedure)
        "185317003",  # Telephone encounter (procedure)
        "185318008",  # Third party encounter (procedure)
        "185320006",  # Encounter by computer link (procedure)
        "185321005",  # Letter encounter to patient (procedure)
        "185349003",  # Encounter for check up (procedure)
        "185463005",  # Visit out of hours (procedure)
        "185465003",  # Weekend visit (procedure)
        "270424005",  # Letter encounter from patient (procedure)
        "270427003",  # Patient-initiated encounter (procedure)
        "270430005",  # Provider-initiated encounter (procedure)
        "308335008",  # Patient encounter procedure (procedure)
        "308720009",  # Letter encounter (procedure)
        "386473003",  # Telephone follow-up (procedure)
        "390906007",  # Follow-up encounter (procedure)
        "401267002",  # Telephone triage encounter (procedure)
        "401271004",  # Email sent to patient (procedure)
        "406547006",  # Urgent follow-up (procedure)
        "438515009",  # Email encounter from caregiver (procedure)
        "438516005",  # Email encounter to caregiver (procedure)
        "445450000",  # Encounter by short message service text messaging (procedure)
        "448337001",  # Telemedicine consultation with patient (procedure)
        "87790002",  # Follow-up inpatient consultation visit (procedure)
        "90526000",  # Initial evaluation and management of healthy individual (procedure)
    }

class BehavioralHealthFollowUpVisit(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for a behavioral health follow-up visit.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for education and training for patient self-management by a qualified health care professional.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Behavioral Health Follow up Visit"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1054"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "98960",  # Education and training for patient self-management by a nonphysician qualified health care professional using a standardized curriculum, face-to-face with the patient (could include caregiver/family) each 30 minutes; individual patient
        "98961",  # Education and training for patient self-management by a nonphysician qualified health care professional using a standardized curriculum, face-to-face with the patient (could include caregiver/family) each 30 minutes; 2-4 patients
        "98962",  # Education and training for patient self-management by a nonphysician qualified health care professional using a standardized curriculum, face-to-face with the patient (could include caregiver/family) each 30 minutes; 5-8 patients
        "99078",  # Physician or other qualified health care professional qualified by education, training, licensure/regulation (when applicable) educational services rendered to patients in a group setting (eg, prenatal, obesity, or diabetic instructions)
        "99510",  # Home visit for individual, family, or marriage counseling
    }

class PreventiveCareServicesGroupCounseling(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for group counseling services.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for preventive medicine counseling and/or risk factor reduction intervention(s) in a group setting.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Preventive Care Services Group Counseling"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1027"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99411",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to individuals in a group setting (separate procedure); approximately 30 minutes
        "99412",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to individuals in a group setting (separate procedure); approximately 60 minutes
    }

class PreventiveCareServicesIndividualCounseling(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for individual counseling services.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for counseling, anticipatory guidance, and risk factor reduction interventions.

    **Exclusion Criteria:** Excludes concepts that represent an encounter for services performed in the emergency department, including critical care and observation services.
    """

    VALUE_SET_NAME = "Preventive Care Services Individual Counseling"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1026"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99401",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 15 minutes
        "99402",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 30 minutes
        "99403",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 45 minutes
        "99404",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 60 minutes
    }

class PsychotherapyAndPharmacologicManagement(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for psychotherapy services.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for group or family psychotherapy services or individual psychophysiological therapy.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Psychotherapy and Pharmacologic Management"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1055"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "90845",  # Psychoanalysis
        "90847",  # Family psychotherapy (conjoint psychotherapy) (with patient present), 50 minutes
        "90849",  # Multiple-family group psychotherapy
        "90853",  # Group psychotherapy (other than of a multiple-family group)
        "90875",  # Individual psychophysiological therapy incorporating biofeedback training by any modality (face-to-face with the patient), with psychotherapy (eg, insight oriented, behavior modifying or supportive psychotherapy); 30 minutes
        "90876",  # Individual psychophysiological therapy incorporating biofeedback training by any modality (face-to-face with the patient), with psychotherapy (eg, insight oriented, behavior modifying or supportive psychotherapy); 45 minutes
    }

class DetoxificationVisit(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for detoxification visits.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for alcohol and drug detoxification.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Detoxification Visit"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1059"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "182969009",  # Dependent drug detoxification (regime/therapy)
        "20093000",  # Alcohol rehabilitation and detoxification (regime/therapy)
        "23915005",  # Combined alcohol and drug rehabilitation and detoxification (regime/therapy)
        "414054004",  # Drug dependence home detoxification (regime/therapy)
        "414056002",  # Drug dependence self detoxification (regime/therapy)
        "56876005",  # Drug rehabilitation and detoxification (regime/therapy)
        "61480009",  # Drug detoxification (regime/therapy)
        "64297001",  # Detoxication psychiatric therapy for alcoholism (regime/therapy)
        "67516001",  # Detoxification therapy (regime/therapy)
        "827094004",  # Alcohol detoxification (regime/therapy)
        "87106005",  # Combined alcohol and drug detoxification (regime/therapy)
    }

class DischargeServicesHospitalInpatient(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for inpatient hospital discharge services.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for hospital discharge day management.

    **Exclusion Criteria:** Excludes concepts that represent encounters other than inpatient hospital discharge services.
    """

    VALUE_SET_NAME = "Discharge Services Hospital Inpatient"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1007"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99238",  # Hospital inpatient or observation discharge day management; 30 minutes or less on the date of the encounter
        "99239",  # Hospital inpatient or observation discharge day management; more than 30 minutes on the date of the encounter
    }

class DischargeServicesHospitalInpatientSameDayDischarge(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for same day inpatient hospital discharge services.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for the evaluation and management of a patient that results in discharge on the same date as admission.

    **Exclusion Criteria:** Excludes concepts that represent encounters other than same day inpatient hospital discharge services.
    """

    VALUE_SET_NAME = "Discharge Services Hospital Inpatient Same Day Discharge"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1006"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99234",  # Hospital inpatient or observation care, for the evaluation and management of a patient including admission and discharge on the same date, which requires a medically appropriate history and/or examination and straightforward or low level of medical decision making. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "99235",  # Hospital inpatient or observation care, for the evaluation and management of a patient including admission and discharge on the same date, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 70 minutes must be met or exceeded.
        "99236",  # Hospital inpatient or observation care, for the evaluation and management of a patient including admission and discharge on the same date, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 85 minutes must be met or exceeded.
    }

class InitialHospitalInpatientVisit(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for inpatient hospital care.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for initial hospital care for the evaluation and management of a patient.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Initial Hospital Inpatient Visit"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1004"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99221",  # Initial hospital inpatient or observation care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and straightforward or low level medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99222",  # Initial hospital inpatient or observation care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 55 minutes must be met or exceeded.
        "99223",  # Initial hospital inpatient or observation care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 75 minutes must be met or exceeded.
    }

class OccupationalTherapyEvaluation(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for assessment, management, and evaluation for occupational therapy.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for assessment, management, and evaluation for occupational therapy.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Occupational Therapy Evaluation"
    OID = "2.16.840.1.113883.3.526.3.1011"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "97165",  # Occupational therapy evaluation, low complexity, requiring these components: An occupational profile and medical and therapy history, which includes a brief history including review of medical and/or therapy records relating to the presenting problem; An assessment(s) that identifies 1-3 performance deficits (ie, relating to physical, cognitive, or psychosocial skills) that result in activity limitations and/or participation restrictions; and Clinical decision making of low complexity, which includes an analysis of the occupational profile, analysis of data from problem-focused assessment(s), and consideration of a limited number of treatment options. Patient presents with no comorbidities that affect occupational performance. Modification of tasks or assistance (eg, physical or verbal) with assessment(s) is not necessary to enable completion of evaluation component. Typically, 30 minutes are spent face-to-face with the patient and/or family.
        "97166",  # Occupational therapy evaluation, moderate complexity, requiring these components: An occupational profile and medical and therapy history, which includes an expanded review of medical and/or therapy records and additional review of physical, cognitive, or psychosocial history related to current functional performance; An assessment(s) that identifies 3-5 performance deficits (ie, relating to physical, cognitive, or psychosocial skills) that result in activity limitations and/or participation restrictions; and Clinical decision making of moderate analytic complexity, which includes an analysis of the occupational profile, analysis of data from detailed assessment(s), and consideration of several treatment options. Patient may present with comorbidities that affect occupational performance. Minimal to moderate modification of tasks or assistance (eg, physical or verbal) with assessment(s) is necessary to enable patient to complete evaluation component. Typically, 45 minutes are spent face-to-face with the patient and/or family.
        "97167",  # Occupational therapy evaluation, high complexity, requiring these components: An occupational profile and medical and therapy history, which includes review of medical and/or therapy records and extensive additional review of physical, cognitive, or psychosocial history related to current functional performance; An assessment(s) that identifies 5 or more performance deficits (ie, relating to physical, cognitive, or psychosocial skills) that result in activity limitations and/or participation restrictions; and Clinical decision making of high analytic complexity, which includes an analysis of the patient profile, analysis of data from comprehensive assessment(s), and consideration of multiple treatment options. Patient presents with comorbidities that affect occupational performance. Significant modification of tasks or assistance (eg, physical or verbal) with assessment(s) is necessary to enable patient to complete evaluation component. Typically, 60 minutes are spent face-to-face with the patient and/or family.
        "97168",  # Re-evaluation of occupational therapy established plan of care, requiring these components: An assessment of changes in patient functional or medical status with revised plan of care; An update to the initial occupational profile to reflect changes in condition or environment that affect future interventions and/or goals; and A revised plan of care. A formal reevaluation is performed when there is a documented change in functional status or a significant change to the plan of care is required. Typically, 30 minutes are spent face-to-face with the patient and/or family.
    }

    SNOMEDCT = {
        "228653003",  # Occupational therapy home visit (regime/therapy)
        "410155007",  # Occupational therapy assessment (procedure)
        "410156008",  # Occupational therapy education (procedure)
        "410157004",  # Occupational therapy management (procedure)
        "423602000",  # Occupational therapy surveillance (regime/therapy)
        "424574000",  # Occupational therapy education, guidance, counseling (procedure)
        "59694001",  # Occupational social therapy (regime/therapy)
        "84478008",  # Occupational therapy (regime/therapy)
    }

class PhysicalTherapyEvaluation(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for a physical therapy evaluation.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for a physical therapy evaluation.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Physical Therapy Evaluation"
    OID = "2.16.840.1.113883.3.526.3.1022"
    DEFINITION_VERSION = "20200306"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "97161",  # Physical therapy evaluation: low complexity, requiring these components: A history with no personal factors and/or comorbidities that impact the plan of care; An examination of body system(s) using standardized tests and measures addressing 1-2 elements from any of the following: body structures and functions, activity limitations, and/or participation restrictions; A clinical presentation with stable and/or uncomplicated characteristics; and Clinical decision making of low complexity using standardized patient assessment instrument and/or measurable assessment of functional outcome. Typically, 20 minutes are spent face-to-face with the patient and/or family.
        "97162",  # Physical therapy evaluation: moderate complexity, requiring these components: A history of present problem with 1-2 personal factors and/or comorbidities that impact the plan of care; An examination of body systems using standardized tests and measures in addressing a total of 3 or more elements from any of the following: body structures and functions, activity limitations, and/or participation restrictions; An evolving clinical presentation with changing characteristics; and Clinical decision making of moderate complexity using standardized patient assessment instrument and/or measurable assessment of functional outcome. Typically, 30 minutes are spent face-to-face with the patient and/or family.
        "97163",  # Physical therapy evaluation: high complexity, requiring these components: A history of present problem with 3 or more personal factors and/or comorbidities that impact the plan of care; An examination of body systems using standardized tests and measures addressing a total of 4 or more elements from any of the following: body structures and functions, activity limitations, and/or participation restrictions; A clinical presentation with unstable and unpredictable characteristics; and Clinical decision making of high complexity using standardized patient assessment instrument and/or measurable assessment of functional outcome. Typically, 45 minutes are spent face-to-face with the patient and/or family.
        "97164",  # Re-evaluation of physical therapy established plan of care, requiring these components: An examination including a review of history and use of standardized tests and measures is required; and Revised plan of care using a standardized patient assessment instrument and/or measurable assessment of functional outcome Typically, 20 minutes are spent face-to-face with the patient and/or family.
    }

    SNOMEDCT = {
        "183326003",  # Combined physical therapy (regime/therapy)
        "410158009",  # Physical therapy assessment (procedure)
        "410159001",  # Physical therapy education (procedure)
        "410160006",  # Physical therapy management (procedure)
        "424203006",  # Physical therapy education, guidance and counseling (procedure)
        "424291000",  # Physical therapy surveillance (regime/therapy)
    }

class Psychoanalysis(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for psychoanalysis.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for psychoanalysis.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Psychoanalysis"
    OID = "2.16.840.1.113883.3.526.3.1141"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "90845",  # Psychoanalysis
    }

    SNOMEDCT = {
        "28988002",  # Psychoanalysis in depth (procedure)
        "61436009",  # Psychoanalysis (procedure)
    }

class SpeechAndHearingEvaluation(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for speech or hearing evaluation.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for the evaluation of speech and/or hearing related abilities.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Speech and Hearing Evaluation"
    OID = "2.16.840.1.113883.3.526.3.1530"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "92521",  # Evaluation of speech fluency (eg, stuttering, cluttering)
        "92522",  # Evaluation of speech sound production (eg, articulation, phonological process, apraxia, dysarthria)
        "92523",  # Evaluation of speech sound production (eg, articulation, phonological process, apraxia, dysarthria); with evaluation of language comprehension and expression (eg, receptive and expressive language)
        "92524",  # Behavioral and qualitative analysis of voice and resonance
        "92540",  # Basic vestibular evaluation, includes spontaneous nystagmus test with eccentric gaze fixation nystagmus, with recording, positional nystagmus test, minimum of 4 positions, with recording, optokinetic nystagmus test, bidirectional foveal and peripheral stimulation, with recording, and oscillating tracking test, with recording
        "92557",  # Comprehensive audiometry threshold evaluation and speech recognition (92553 and 92556 combined)
        "92625",  # Assessment of tinnitus (includes pitch, loudness matching, and masking)
    }

    SNOMEDCT = {
        "26342005",  # Medical evaluation for speech, language and/or hearing problems (regime/therapy)
        "41375007",  # Medical evaluation of hearing problem (procedure)
        "77837000",  # Medical evaluation of speech, language and hearing problem (procedure)
        "91515000",  # Special audiologic evaluation for functional hearing loss (procedure)
    }

class AudiologyVisit(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters with nystagmus testing.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for a hearing assessment to quantify hearing such as basic vestibular evaluation, spontaneous and positional nystagmus testing, and computerized dynamic posturography

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Audiology Visit"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1066"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "92540",  # Basic vestibular evaluation, includes spontaneous nystagmus test with eccentric gaze fixation nystagmus, with recording, positional nystagmus test, minimum of 4 positions, with recording, optokinetic nystagmus test, bidirectional foveal and peripheral stimulation, with recording, and oscillating tracking test, with recording
        "92541",  # Spontaneous nystagmus test, including gaze and fixation nystagmus, with recording
        "92542",  # Positional nystagmus test, minimum of 4 positions, with recording
        "92548",  # Computerized dynamic posturography sensory organization test (CDP-SOT), 6 conditions (ie, eyes open, eyes closed, visual sway, platform sway, eyes closed platform sway, platform and visual sway), including interpretation and report
    }

class DischargeServicesNursingFacility(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for discharges from a nursing facility.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for nursing facility discharge.

    **Exclusion Criteria:** Excludes concepts that represent discharges from settings other than a nursing facility.
    """

    VALUE_SET_NAME = "Discharge Services Nursing Facility"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1013"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99315",  # Nursing facility discharge management; 30 minutes or less total time on the date of the encounter
        "99316",  # Nursing facility discharge management; more than 30 minutes total time on the date of the encounter
    }

class MedicalDisabilityExam(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for work related or medical disability examinations

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for work related or medical disability examinations.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Medical Disability Exam"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1073"
    DEFINITION_VERSION = "20210306"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99455",  # Work related or medical disability examination by the treating physician that includes: Completion of a medical history commensurate with the patient's condition; Performance of an examination commensurate with the patient's condition; Formulation of a diagnosis, assessment of capabilities and stability, and calculation of impairment; Development of future medical treatment plan; and Completion of necessary documentation/certificates and report.
        "99456",  # Work related or medical disability examination by other than the treating physician that includes: Completion of a medical history commensurate with the patient's condition; Performance of an examination commensurate with the patient's condition; Formulation of a diagnosis, assessment of capabilities and stability, and calculation of impairment; Development of future medical treatment plan; and Completion of necessary documentation/certificates and report.
    }

class BehavioralOrNeuropsychAssessment(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of encounters for neuropsychological assessments.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that describe an assessment for applicable neuropsychological assessments for behavioral health.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Behavioral or Neuropsych Assessment"
    OID = "2.16.840.1.113883.3.526.3.1023"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "96116",  # Neurobehavioral status exam (clinical assessment of thinking, reasoning and judgment, [eg, acquired knowledge, attention, language, memory, planning and problem solving, and visual spatial abilities]), by physician or other qualified health care professional, both face-to-face time with the patient and time interpreting test results and preparing the report; first hour
    }

    SNOMEDCT = {
        "307808008",  # Neuropsychological testing (procedure)
    }

class AudioVisualTelehealthEncounter(ValueSet):
    """
    **Clinical Focus:** This value set contains concepts that represent telehealth encounters using audio-visual platforms.

    **Data Element Scope:** This value set may use the Quality Data Model (QDM) category related to Encounter.

    **Inclusion Criteria:** Includes only telehealth codes for encounters involving real-time two-way communication using audio-visual platforms.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Audio Visual Telehealth Encounter"
    OID = "2.16.840.1.113883.3.1444.5.215"
    DEFINITION_VERSION = "20250201"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "98000",  # Synchronous audio-video visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "98001",  # Synchronous audio-video visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "98002",  # Synchronous audio-video visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate medical decision making. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "98003",  # Synchronous audio-video visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "98004",  # Synchronous audio-video visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 10 minutes must be met or exceeded.
        "98005",  # Synchronous audio-video visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "98006",  # Synchronous audio-video visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "98007",  # Synchronous audio-video visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
    }

    SNOMEDCT = {
        "448337001",  # Telemedicine consultation with patient (procedure)
        "453131000124105",  # Videotelephony encounter (procedure)
        "763184009",  # Telepractice consultation (procedure)
    }

class RadiationTreatmentManagement(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for the procedure of radiation management.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent a procedure for radiation treatment management.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Radiation Treatment Management"
    OID = "2.16.840.1.113883.3.526.3.1026"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "77427",  # Radiation treatment management, 5 treatments
        "77431",  # Radiation therapy management with complete course of therapy consisting of 1 or 2 fractions only
        "77432",  # Stereotactic radiation treatment management of cranial lesion(s) (complete course of treatment consisting of 1 session)
        "77435",  # Stereotactic body radiation therapy, treatment management, per treatment course, to 1 or more lesions, including image guidance, entire course not to exceed 5 fractions
    }

    SNOMEDCT = {
        "84755001",  # Radiation therapy treatment management (procedure)
    }

class ContactOrOfficeVisit(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for office visits and outpatient contacts to evaluate for depression.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for outpatient contact and office visits in which a patient may be evaluated for depression.

    **Exclusion Criteria:** Excludes concepts that represent an encounter for inpatient visits, except for psychiatry and psychotherapy visits, which are not specific to setting.
    """

    VALUE_SET_NAME = "Contact or Office Visit"
    OID = "2.16.840.1.113762.1.4.1080.5"
    DEFINITION_VERSION = "20220219"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "90791",  # Psychiatric diagnostic evaluation
        "90792",  # Psychiatric diagnostic evaluation with medical services
        "90832",  # Psychotherapy, 30 minutes with patient
        "90834",  # Psychotherapy, 45 minutes with patient
        "90837",  # Psychotherapy, 60 minutes with patient
        "90839",  # Psychotherapy for crisis; first 60 minutes
        "96156",  # Health behavior assessment, or re-assessment (ie, health-focused clinical interview, behavioral observations, clinical decision making)
        "96158",  # Health behavior intervention, individual, face-to-face; initial 30 minutes
        "96159",  # Health behavior intervention, individual, face-to-face; each additional 15 minutes (List separately in addition to code for primary service)
        "98008",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination, straightforward medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "98009",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination, low medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "98010",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination, moderate medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "98011",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination, high medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "98012",  # Synchronous audio-only visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination, straightforward medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 10 minutes must be exceeded.
        "98013",  # Synchronous audio-only visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination, low medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "98014",  # Synchronous audio-only visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination, moderate medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "98015",  # Synchronous audio-only visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination, high medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99202",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "99203",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99204",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "99205",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "99211",  # Office or other outpatient visit for the evaluation and management of an established patient that may not require the presence of a physician or other qualified health care professional
        "99212",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 10 minutes must be met or exceeded.
        "99213",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99214",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99215",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99384",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; adolescent (age 12 through 17 years)
        "99385",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 18-39 years
        "99386",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 40-64 years
        "99387",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 65 years and older
        "99394",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; adolescent (age 12 through 17 years)
        "99395",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 18-39 years
        "99396",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 40-64 years
        "99397",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 65 years and older
        "99421",  # Online digital evaluation and management service, for an established patient, for up to 7 days, cumulative time during the 7 days; 5-10 minutes
        "99422",  # Online digital evaluation and management service, for an established patient, for up to 7 days, cumulative time during the 7 days; 11-20 minutes
        "99423",  # Online digital evaluation and management service, for an established patient, for up to 7 days, cumulative time during the 7 days; 21 or more minutes
    }

    HCPCSLEVELII = {
        "G0402",  # Initial preventive physical examination; face-to-face visit, services limited to new beneficiary during the first 12 months of medicare enrollment
        "G0438",  # Annual wellness visit; includes a personalized prevention plan of service (pps), initial visit
        "G0439",  # Annual wellness visit, includes a personalized prevention plan of service (pps), subsequent visit
    }

class EsrdMonthlyOutpatientServices(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for end-stage renal disease (ESRD) outpatient services.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for ESRD outpatients services.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "ESRD Monthly Outpatient Services"
    OID = "2.16.840.1.113883.3.464.1003.109.12.1014"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

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
        "90989",  # Dialysis training, patient, including helper where applicable, any mode, completed course
        "90993",  # Dialysis training, patient, including helper where applicable, any mode, course not completed, per training session
        "90997",  # Hemoperfusion (eg, with activated charcoal or resin)
        "90999",  # Unlisted dialysis procedure, inpatient or outpatient
        "99512",  # Home visit for hemodialysis
    }

class GroupPsychotherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for group psychotherapy.

    **Data Element Scope:** This value set may use a model element related to Encounter or Procedure.

    **Inclusion Criteria:** Includes concepts that represent group psychotherapy.

    **Exclusion Criteria:** Excludes concepts that represent family psychotherapy or individual psychotherapy.
    """

    VALUE_SET_NAME = "Group Psychotherapy"
    OID = "2.16.840.1.113883.3.526.3.1187"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "90853",  # Group psychotherapy (other than of a multiple-family group)
    }

    SNOMEDCT = {
        "1555005",  # Brief group psychotherapy (regime/therapy)
        "27591006",  # Group analytical psychotherapy (regime/therapy)
        "28868002",  # Interactive group medical psychotherapy (regime/therapy)
        "76168009",  # Group psychotherapy (regime/therapy)
    }

class PsychVisitForFamilyPsychotherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for family psychotherapy.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent family psychotherapy.

    **Exclusion Criteria:** Excludes concepts for group psychotherapy or individual psychotherapy.
    """

    VALUE_SET_NAME = "Psych Visit for Family Psychotherapy"
    OID = "2.16.840.1.113883.3.526.3.1018"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "90846",  # Family psychotherapy (without the patient present), 50 minutes
        "90847",  # Family psychotherapy (conjoint psychotherapy) (with patient present), 50 minutes
    }

    SNOMEDCT = {
        "108313002",  # Family psychotherapy procedure (regime/therapy)
        "302247005",  # Narrative family psychotherapy (regime/therapy)
        "361229007",  # Structural family psychotherapy (regime/therapy)
    }

class EncounterToScreenForBloodPressure(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters where blood pressure would be recorded.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter where blood pressure is recorded.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Encounter to Screen for Blood Pressure"
    OID = "2.16.840.1.113883.3.600.1920"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CDT = {
        "D3921",  # decoronation or submergence of an erupted tooth
        "D7111",  # extraction, coronal remnants - primary tooth
        "D7140",  # extraction, erupted tooth or exposed root (elevation and/or forceps removal)
        "D7210",  # extraction, erupted tooth requiring removal of bone and/or sectioning of tooth, and including elevation of mucoperiosteal flap if indicated
        "D7220",  # removal of impacted tooth - soft tissue
        "D7230",  # removal of impacted tooth - partially bony
        "D7240",  # removal of impacted tooth - completely bony
        "D7241",  # removal of impacted tooth - completely bony, with unusual surgical complications
        "D7250",  # removal of residual tooth roots (cutting procedure)
        "D7251",  # coronectomy - intentional partial tooth removal, impacted teeth only
    }

    CPT = {
        "90791",  # Psychiatric diagnostic evaluation
        "90792",  # Psychiatric diagnostic evaluation with medical services
        "92002",  # Ophthalmological services: medical examination and evaluation with initiation of diagnostic and treatment program; intermediate, new patient
        "92004",  # Ophthalmological services: medical examination and evaluation with initiation of diagnostic and treatment program; comprehensive, new patient, 1 or more visits
        "92012",  # Ophthalmological services: medical examination and evaluation, with initiation or continuation of diagnostic and treatment program; intermediate, established patient
        "92014",  # Ophthalmological services: medical examination and evaluation, with initiation or continuation of diagnostic and treatment program; comprehensive, established patient, 1 or more visits
        "92532",  # Positional nystagmus test
        "92534",  # Optokinetic nystagmus test
        "92537",  # Caloric vestibular test with recording, bilateral; bithermal (ie, one warm and one cool irrigation in each ear for a total of four irrigations)
        "92538",  # Caloric vestibular test with recording, bilateral; monothermal (ie, one irrigation in each ear for a total of two irrigations)
        "92540",  # Basic vestibular evaluation, includes spontaneous nystagmus test with eccentric gaze fixation nystagmus, with recording, positional nystagmus test, minimum of 4 positions, with recording, optokinetic nystagmus test, bidirectional foveal and peripheral stimulation, with recording, and oscillating tracking test, with recording
        "92541",  # Spontaneous nystagmus test, including gaze and fixation nystagmus, with recording
        "92542",  # Positional nystagmus test, minimum of 4 positions, with recording
        "92544",  # Optokinetic nystagmus test, bidirectional, foveal or peripheral stimulation, with recording
        "92545",  # Oscillating tracking test, with recording
        "92546",  # Sinusoidal vertical axis rotational testing
        "92622",  # Diagnostic analysis, programming, and verification of an auditory osseointegrated sound processor, any type; first 60 minutes
        "92625",  # Assessment of tinnitus (includes pitch, loudness matching, and masking)
        "97802",  # Medical nutrition therapy; initial assessment and intervention, individual, face-to-face with the patient, each 15 minutes
        "97803",  # Medical nutrition therapy; re-assessment and intervention, individual, face-to-face with the patient, each 15 minutes
        "99202",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "99203",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99204",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "99205",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "99212",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 10 minutes must be met or exceeded.
        "99213",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99214",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99215",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99236",  # Hospital inpatient or observation care, for the evaluation and management of a patient including admission and discharge on the same date, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 85 minutes must be met or exceeded.
        "99242",  # Office or other outpatient consultation for a new or established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99243",  # Office or other outpatient consultation for a new or established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99244",  # Office or other outpatient consultation for a new or established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99245",  # Office or other outpatient consultation for a new or established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 55 minutes must be met or exceeded.
        "99281",  # Emergency department visit for the evaluation and management of a patient that may not require the presence of a physician or other qualified health care professional
        "99282",  # Emergency department visit for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and straightforward medical decision making
        "99283",  # Emergency department visit for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and low level of medical decision making
        "99284",  # Emergency department visit for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making
        "99285",  # Emergency department visit for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and high level of medical decision making
        "99304",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and straightforward or low level of medical decision making. When using total time on the date of the encounter for code selection, 25 minutes must be met or exceeded.
        "99305",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 35 minutes must be met or exceeded.
        "99306",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 50 minutes must be met or exceeded.
        "99307",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 10 minutes must be met or exceeded.
        "99308",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99309",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99310",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "99315",  # Nursing facility discharge management; 30 minutes or less total time on the date of the encounter
        "99316",  # Nursing facility discharge management; more than 30 minutes total time on the date of the encounter
        "99341",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "99342",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99344",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "99345",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 75 minutes must be met or exceeded.
        "99347",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99348",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99349",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99350",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "99385",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 18-39 years
        "99386",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 40-64 years
        "99387",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 65 years and older
        "99395",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 18-39 years
        "99396",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 40-64 years
        "99397",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 65 years and older
        "99424",  # Principal care management services, for a single high-risk disease, with the following required elements: one complex chronic condition expected to last at least 3 months, and that places the patient at significant risk of hospitalization, acute exacerbation/decompensation, functional decline, or death, the condition requires development, monitoring, or revision of disease-specific care plan, the condition requires frequent adjustments in the medication regimen and/or the management of the condition is unusually complex due to comorbidities, ongoing communication and care coordination between relevant practitioners furnishing care; first 30 minutes provided personally by a physician or other qualified health care professional, per calendar month.
        "99491",  # Chronic care management services with the following required elements: multiple (two or more) chronic conditions expected to last at least 12 months, or until the death of the patient, chronic conditions that place the patient at significant risk of death, acute exacerbation/decompensation, or functional decline, comprehensive care plan established, implemented, revised, or monitored; first 30 minutes provided personally by a physician or other qualified health care professional, per calendar month.
    }

    HCPCSLEVELII = {
        "G0101",  # Cervical or vaginal cancer screening; pelvic and clinical breast examination
        "G0270",  # Medical nutrition therapy; reassessment and subsequent intervention(s) following second referral in same year for change in diagnosis, medical condition or treatment regimen (including additional hours needed for renal disease), individual, face to face with the patient, each 15 minutes
        "G0402",  # Initial preventive physical examination; face-to-face visit, services limited to new beneficiary during the first 12 months of medicare enrollment
        "G0438",  # Annual wellness visit; includes a personalized prevention plan of service (pps), initial visit
        "G0439",  # Annual wellness visit, includes a personalized prevention plan of service (pps), subsequent visit
    }

    SNOMEDCT = {
        "103705002",  # Patient status observation (procedure)
        "108220007",  # Evaluation AND/OR management - new patient (procedure)
        "108221006",  # Evaluation AND/OR management - established patient (procedure)
        "108224003",  # Preventive patient evaluation (procedure)
        "12843005",  # Subsequent hospital visit by physician (procedure)
        "13607009",  # Manual examination of breast (procedure)
        "14736009",  # History and physical examination with evaluation and management of patient (procedure)
        "1759002",  # Assessment of nutritional status (procedure)
        "18170008",  # Subsequent nursing facility visit (procedure)
        "185349003",  # Encounter for check up (procedure)
        "185463005",  # Visit out of hours (procedure)
        "185465003",  # Weekend visit (procedure)
        "207195004",  # History and physical examination with evaluation and management of nursing facility patient (procedure)
        "209099002",  # History and physical examination with management of domiciliary or rest home patient (procedure)
        "210098006",  # Domiciliary or rest home patient evaluation and management (procedure)
        "270427003",  # Patient-initiated encounter (procedure)
        "270430005",  # Provider-initiated encounter (procedure)
        "306677009",  # Discharge from day hospital (procedure)
        "308335008",  # Patient encounter procedure (procedure)
        "310243009",  # Nutritional assessment (procedure)
        "35025007",  # Manual pelvic examination (procedure)
        "390906007",  # Follow-up encounter (procedure)
        "406547006",  # Urgent follow-up (procedure)
        "410172000",  # Nutrition care management (procedure)
        "439708006",  # Home visit (procedure)
        "4525004",  # Emergency department patient visit (procedure)
        "46662001",  # Examination of breast (procedure)
        "50357006",  # Evaluation and management of patient at home (procedure)
        "76464004",  # Hospital admission, for observation (procedure)
        "78318003",  # History and physical examination, annual for health maintenance (procedure)
        "83607001",  # Gynecologic examination (procedure)
        "86013001",  # Periodic reevaluation and management of healthy individual (procedure)
        "90526000",  # Initial evaluation and management of healthy individual (procedure)
    }

class EncounterToScreenForDepression(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of encounters for depression screening.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent wellness visits, annual visits, therapy evaluations, or primary or specialist physician office visits where a depression screen could be conducted.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Encounter to Screen for Depression"
    OID = "2.16.840.1.113883.3.600.1916"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "59400",  # Routine obstetric care including antepartum care, vaginal delivery (with or without episiotomy, and/or forceps) and postpartum care
        "59425",  # Antepartum care only; 4-6 visits
        "59426",  # Antepartum care only; 7 or more visits
        "59510",  # Routine obstetric care including antepartum care, cesarean delivery, and postpartum care
        "59610",  # Routine obstetric care including antepartum care, vaginal delivery (with or without episiotomy, and/or forceps) and postpartum care, after previous cesarean delivery
        "59618",  # Routine obstetric care including antepartum care, cesarean delivery, and postpartum care, following attempted vaginal delivery after previous cesarean delivery
        "90791",  # Psychiatric diagnostic evaluation
        "90792",  # Psychiatric diagnostic evaluation with medical services
        "90832",  # Psychotherapy, 30 minutes with patient
        "90834",  # Psychotherapy, 45 minutes with patient
        "90837",  # Psychotherapy, 60 minutes with patient
        "92622",  # Diagnostic analysis, programming, and verification of an auditory osseointegrated sound processor, any type; first 60 minutes
        "92625",  # Assessment of tinnitus (includes pitch, loudness matching, and masking)
        "96105",  # Assessment of aphasia (includes assessment of expressive and receptive speech and language function, language comprehension, speech production ability, reading, spelling, writing, eg, by Boston Diagnostic Aphasia Examination) with interpretation and report, per hour
        "96110",  # Developmental screening (eg, developmental milestone survey, speech and language delay screen), with scoring and documentation, per standardized instrument
        "96112",  # Developmental test administration (including assessment of fine and/or gross motor, language, cognitive level, social, memory and/or executive functions by standardized developmental instruments when performed), by physician or other qualified health care professional, with interpretation and report; first hour
        "96116",  # Neurobehavioral status exam (clinical assessment of thinking, reasoning and judgment, [eg, acquired knowledge, attention, language, memory, planning and problem solving, and visual spatial abilities]), by physician or other qualified health care professional, both face-to-face time with the patient and time interpreting test results and preparing the report; first hour
        "96125",  # Standardized cognitive performance testing (eg, Ross Information Processing Assessment) per hour of a qualified health care professional's time, both face-to-face time administering tests to the patient and time interpreting these test results and preparing the report
        "96136",  # Psychological or neuropsychological test administration and scoring by physician or other qualified health care professional, two or more tests, any method; first 30 minutes
        "96138",  # Psychological or neuropsychological test administration and scoring by technician, two or more tests, any method; first 30 minutes
        "96156",  # Health behavior assessment, or re-assessment (ie, health-focused clinical interview, behavioral observations, clinical decision making)
        "96158",  # Health behavior intervention, individual, face-to-face; initial 30 minutes
        "97161",  # Physical therapy evaluation: low complexity, requiring these components: A history with no personal factors and/or comorbidities that impact the plan of care; An examination of body system(s) using standardized tests and measures addressing 1-2 elements from any of the following: body structures and functions, activity limitations, and/or participation restrictions; A clinical presentation with stable and/or uncomplicated characteristics; and Clinical decision making of low complexity using standardized patient assessment instrument and/or measurable assessment of functional outcome. Typically, 20 minutes are spent face-to-face with the patient and/or family.
        "97162",  # Physical therapy evaluation: moderate complexity, requiring these components: A history of present problem with 1-2 personal factors and/or comorbidities that impact the plan of care; An examination of body systems using standardized tests and measures in addressing a total of 3 or more elements from any of the following: body structures and functions, activity limitations, and/or participation restrictions; An evolving clinical presentation with changing characteristics; and Clinical decision making of moderate complexity using standardized patient assessment instrument and/or measurable assessment of functional outcome. Typically, 30 minutes are spent face-to-face with the patient and/or family.
        "97163",  # Physical therapy evaluation: high complexity, requiring these components: A history of present problem with 3 or more personal factors and/or comorbidities that impact the plan of care; An examination of body systems using standardized tests and measures addressing a total of 4 or more elements from any of the following: body structures and functions, activity limitations, and/or participation restrictions; A clinical presentation with unstable and unpredictable characteristics; and Clinical decision making of high complexity using standardized patient assessment instrument and/or measurable assessment of functional outcome. Typically, 45 minutes are spent face-to-face with the patient and/or family.
        "97164",  # Re-evaluation of physical therapy established plan of care, requiring these components: An examination including a review of history and use of standardized tests and measures is required; and Revised plan of care using a standardized patient assessment instrument and/or measurable assessment of functional outcome Typically, 20 minutes are spent face-to-face with the patient and/or family.
        "97165",  # Occupational therapy evaluation, low complexity, requiring these components: An occupational profile and medical and therapy history, which includes a brief history including review of medical and/or therapy records relating to the presenting problem; An assessment(s) that identifies 1-3 performance deficits (ie, relating to physical, cognitive, or psychosocial skills) that result in activity limitations and/or participation restrictions; and Clinical decision making of low complexity, which includes an analysis of the occupational profile, analysis of data from problem-focused assessment(s), and consideration of a limited number of treatment options. Patient presents with no comorbidities that affect occupational performance. Modification of tasks or assistance (eg, physical or verbal) with assessment(s) is not necessary to enable completion of evaluation component. Typically, 30 minutes are spent face-to-face with the patient and/or family.
        "97166",  # Occupational therapy evaluation, moderate complexity, requiring these components: An occupational profile and medical and therapy history, which includes an expanded review of medical and/or therapy records and additional review of physical, cognitive, or psychosocial history related to current functional performance; An assessment(s) that identifies 3-5 performance deficits (ie, relating to physical, cognitive, or psychosocial skills) that result in activity limitations and/or participation restrictions; and Clinical decision making of moderate analytic complexity, which includes an analysis of the occupational profile, analysis of data from detailed assessment(s), and consideration of several treatment options. Patient may present with comorbidities that affect occupational performance. Minimal to moderate modification of tasks or assistance (eg, physical or verbal) with assessment(s) is necessary to enable patient to complete evaluation component. Typically, 45 minutes are spent face-to-face with the patient and/or family.
        "97167",  # Occupational therapy evaluation, high complexity, requiring these components: An occupational profile and medical and therapy history, which includes review of medical and/or therapy records and extensive additional review of physical, cognitive, or psychosocial history related to current functional performance; An assessment(s) that identifies 5 or more performance deficits (ie, relating to physical, cognitive, or psychosocial skills) that result in activity limitations and/or participation restrictions; and Clinical decision making of high analytic complexity, which includes an analysis of the patient profile, analysis of data from comprehensive assessment(s), and consideration of multiple treatment options. Patient presents with comorbidities that affect occupational performance. Significant modification of tasks or assistance (eg, physical or verbal) with assessment(s) is necessary to enable patient to complete evaluation component. Typically, 60 minutes are spent face-to-face with the patient and/or family.
        "97802",  # Medical nutrition therapy; initial assessment and intervention, individual, face-to-face with the patient, each 15 minutes
        "97803",  # Medical nutrition therapy; re-assessment and intervention, individual, face-to-face with the patient, each 15 minutes
        "98000",  # Synchronous audio-video visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "98001",  # Synchronous audio-video visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "98002",  # Synchronous audio-video visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate medical decision making. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "98003",  # Synchronous audio-video visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "98004",  # Synchronous audio-video visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 10 minutes must be met or exceeded.
        "98005",  # Synchronous audio-video visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "98006",  # Synchronous audio-video visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "98007",  # Synchronous audio-video visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "98008",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination, straightforward medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "98009",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination, low medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "98010",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination, moderate medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "98011",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination, high medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "98012",  # Synchronous audio-only visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination, straightforward medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 10 minutes must be exceeded.
        "98013",  # Synchronous audio-only visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination, low medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "98014",  # Synchronous audio-only visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination, moderate medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "98015",  # Synchronous audio-only visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination, high medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "98016",  # Brief communication technology-based service (eg, virtual check-in) by a physician or other qualified health care professional who can report evaluation and management services, provided to an established patient, not originating from a related evaluation and management service provided within the previous 7 days nor leading to an evaluation and management service or procedure within the next 24 hours or soonest available appointment, 5-10 minutes of medical discussion
        "98966",  # Telephone assessment and management service provided by a nonphysician qualified health care professional to an established patient, parent, or guardian not originating from a related assessment and management service provided within the previous 7 days nor leading to an assessment and management service or procedure within the next 24 hours or soonest available appointment; 5-10 minutes of medical discussion
        "98967",  # Telephone assessment and management service provided by a nonphysician qualified health care professional to an established patient, parent, or guardian not originating from a related assessment and management service provided within the previous 7 days nor leading to an assessment and management service or procedure within the next 24 hours or soonest available appointment; 11-20 minutes of medical discussion
        "98968",  # Telephone assessment and management service provided by a nonphysician qualified health care professional to an established patient, parent, or guardian not originating from a related assessment and management service provided within the previous 7 days nor leading to an assessment and management service or procedure within the next 24 hours or soonest available appointment; 21-30 minutes of medical discussion
        "99078",  # Physician or other qualified health care professional qualified by education, training, licensure/regulation (when applicable) educational services rendered to patients in a group setting (eg, prenatal, obesity, or diabetic instructions)
        "99202",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "99203",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99204",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "99205",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "99212",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 10 minutes must be met or exceeded.
        "99213",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99214",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99215",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99304",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and straightforward or low level of medical decision making. When using total time on the date of the encounter for code selection, 25 minutes must be met or exceeded.
        "99305",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 35 minutes must be met or exceeded.
        "99306",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 50 minutes must be met or exceeded.
        "99307",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 10 minutes must be met or exceeded.
        "99308",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99309",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99310",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "99315",  # Nursing facility discharge management; 30 minutes or less total time on the date of the encounter
        "99316",  # Nursing facility discharge management; more than 30 minutes total time on the date of the encounter
        "99341",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "99342",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99344",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "99345",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 75 minutes must be met or exceeded.
        "99347",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99348",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99349",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99350",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "99384",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; adolescent (age 12 through 17 years)
        "99385",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 18-39 years
        "99386",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 40-64 years
        "99387",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 65 years and older
        "99394",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; adolescent (age 12 through 17 years)
        "99395",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 18-39 years
        "99396",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 40-64 years
        "99397",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 65 years and older
        "99401",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 15 minutes
        "99402",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 30 minutes
        "99403",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 45 minutes
        "99404",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 60 minutes
        "99424",  # Principal care management services, for a single high-risk disease, with the following required elements: one complex chronic condition expected to last at least 3 months, and that places the patient at significant risk of hospitalization, acute exacerbation/decompensation, functional decline, or death, the condition requires development, monitoring, or revision of disease-specific care plan, the condition requires frequent adjustments in the medication regimen and/or the management of the condition is unusually complex due to comorbidities, ongoing communication and care coordination between relevant practitioners furnishing care; first 30 minutes provided personally by a physician or other qualified health care professional, per calendar month.
        "99483",  # Assessment of and care planning for a patient with cognitive impairment, requiring an independent historian, in the office or other outpatient, home or domiciliary or rest home, with all of the following required elements: Cognition-focused evaluation including a pertinent history and examination, Medical decision making of moderate or high complexity, Functional assessment (eg, basic and instrumental activities of daily living), including decision-making capacity, Use of standardized instruments for staging of dementia (eg, functional assessment staging test [FAST], clinical dementia rating [CDR]), Medication reconciliation and review for high-risk medications, Evaluation for neuropsychiatric and behavioral symptoms, including depression, including use of standardized screening instrument(s), Evaluation of safety (eg, home), including motor vehicle operation, Identification of caregiver(s), caregiver knowledge, caregiver needs, social supports, and the willingness of caregiver to take on caregiving tasks, Development, updating or revision, or review of an Advance Care Plan, Creation of a written care plan, including initial plans to address any neuropsychiatric symptoms, neuro-cognitive symptoms, functional limitations, and referral to community resources as needed (eg, rehabilitation services, adult day programs, support groups) shared with the patient and/or caregiver with initial education and support. Typically, 60 minutes of total time is spent on the date of the encounter.
        "99484",  # Care management services for behavioral health conditions, at least 20 minutes of clinical staff time, directed by a physician or other qualified health care professional, per calendar month, with the following required elements: initial assessment or follow-up monitoring, including the use of applicable validated rating scales, behavioral health care planning in relation to behavioral/psychiatric health problems, including revision for patients who are not progressing or whose status changes, facilitating and coordinating treatment such as psychotherapy, pharmacotherapy, counseling and/or psychiatric consultation, and continuity of care with a designated member of the care team.
        "99491",  # Chronic care management services with the following required elements: multiple (two or more) chronic conditions expected to last at least 12 months, or until the death of the patient, chronic conditions that place the patient at significant risk of death, acute exacerbation/decompensation, or functional decline, comprehensive care plan established, implemented, revised, or monitored; first 30 minutes provided personally by a physician or other qualified health care professional, per calendar month.
        "99492",  # Initial psychiatric collaborative care management, first 70 minutes in the first calendar month of behavioral health care manager activities, in consultation with a psychiatric consultant, and directed by the treating physician or other qualified health care professional, with the following required elements: outreach to and engagement in treatment of a patient directed by the treating physician or other qualified health care professional, initial assessment of the patient, including administration of validated rating scales, with the development of an individualized treatment plan, review by the psychiatric consultant with modifications of the plan if recommended, entering patient in a registry and tracking patient follow-up and progress using the registry, with appropriate documentation, and participation in weekly caseload consultation with the psychiatric consultant, and provision of brief interventions using evidence-based techniques such as behavioral activation, motivational interviewing, and other focused treatment strategies.
        "99493",  # Subsequent psychiatric collaborative care management, first 60 minutes in a subsequent month of behavioral health care manager activities, in consultation with a psychiatric consultant, and directed by the treating physician or other qualified health care professional, with the following required elements: tracking patient follow-up and progress using the registry, with appropriate documentation, participation in weekly caseload consultation with the psychiatric consultant, ongoing collaboration with and coordination of the patient's mental health care with the treating physician or other qualified health care professional and any other treating mental health providers, additional review of progress and recommendations for changes in treatment, as indicated, including medications, based on recommendations provided by the psychiatric consultant, provision of brief interventions using evidence-based techniques such as behavioral activation, motivational interviewing, and other focused treatment strategies, monitoring of patient outcomes using validated rating scales, and relapse prevention planning with patients as they achieve remission of symptoms and/or other treatment goals and are prepared for discharge from active treatment.
    }

    HCPCSLEVELII = {
        "G0101",  # Cervical or vaginal cancer screening; pelvic and clinical breast examination
        "G0270",  # Medical nutrition therapy; reassessment and subsequent intervention(s) following second referral in same year for change in diagnosis, medical condition or treatment regimen (including additional hours needed for renal disease), individual, face to face with the patient, each 15 minutes
        "G0271",  # Medical nutrition therapy, reassessment and subsequent intervention(s) following second referral in same year for change in diagnosis, medical condition, or treatment regimen (including additional hours needed for renal disease), group (2 or more individuals), each 30 minutes
        "G0402",  # Initial preventive physical examination; face-to-face visit, services limited to new beneficiary during the first 12 months of medicare enrollment
        "G0438",  # Annual wellness visit; includes a personalized prevention plan of service (pps), initial visit
        "G0439",  # Annual wellness visit, includes a personalized prevention plan of service (pps), subsequent visit
        "G0444",  # Annual depression screening, 5 to 15 minutes
    }

    SNOMEDCT = {
        "10197000",  # Psychiatric interview and evaluation (procedure)
        "108220007",  # Evaluation AND/OR management - new patient (procedure)
        "108221006",  # Evaluation AND/OR management - established patient (procedure)
        "108224003",  # Preventive patient evaluation (procedure)
        "108311000",  # Psychiatric procedure, interview AND/OR consultation (procedure)
        "13607009",  # Manual examination of breast (procedure)
        "14736009",  # History and physical examination with evaluation and management of patient (procedure)
        "165171009",  # Initial psychiatric evaluation (procedure)
        "171207006",  # Depression screening (procedure)
        "18512000",  # Individual psychotherapy (regime/therapy)
        "185349003",  # Encounter for check up (procedure)
        "185463005",  # Visit out of hours (procedure)
        "185465003",  # Weekend visit (procedure)
        "252603000",  # Tinnitus assessment (procedure)
        "270427003",  # Patient-initiated encounter (procedure)
        "270430005",  # Provider-initiated encounter (procedure)
        "302440009",  # Psychiatric pharmacologic management (procedure)
        "308335008",  # Patient encounter procedure (procedure)
        "35025007",  # Manual pelvic examination (procedure)
        "370803007",  # Evaluation of psychosocial impact on plan of care (procedure)
        "390906007",  # Follow-up encounter (procedure)
        "406547006",  # Urgent follow-up (procedure)
        "410155007",  # Occupational therapy assessment (procedure)
        "410157004",  # Occupational therapy management (procedure)
        "46662001",  # Examination of breast (procedure)
        "53555003",  # Basic comprehensive audiometry testing (procedure)
        "78318003",  # History and physical examination, annual for health maintenance (procedure)
        "83607001",  # Gynecologic examination (procedure)
        "8411005",  # Interactive individual medical psychotherapy (regime/therapy)
        "86013001",  # Periodic reevaluation and management of healthy individual (procedure)
        "90526000",  # Initial evaluation and management of healthy individual (procedure)
    }

class OutpatientEncountersForPreventiveCare(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of an encounter for outpatient visits.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent outpatient encounters for annual visit, preventive evaluation, follow-up, or periodic re-evaluations.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Outpatient Encounters for Preventive Care"
    OID = "2.16.840.1.113883.3.526.3.1576"
    DEFINITION_VERSION = "20200307"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "108219001",  # Physician visit with evaluation AND/OR management service (procedure)
        "108220007",  # Evaluation AND/OR management - new patient (procedure)
        "108221006",  # Evaluation AND/OR management - established patient (procedure)
        "108224003",  # Preventive patient evaluation (procedure)
        "14736009",  # History and physical examination with evaluation and management of patient (procedure)
        "185349003",  # Encounter for check up (procedure)
        "185389009",  # Follow-up visit (procedure)
        "270427003",  # Patient-initiated encounter (procedure)
        "270430005",  # Provider-initiated encounter (procedure)
        "281036007",  # Follow-up consultation (procedure)
        "308335008",  # Patient encounter procedure (procedure)
        "390906007",  # Follow-up encounter (procedure)
        "410187005",  # Physical evaluation management (procedure)
        "78318003",  # History and physical examination, annual for health maintenance (procedure)
        "86013001",  # Periodic reevaluation and management of healthy individual (procedure)
        "90526000",  # Initial evaluation and management of healthy individual (procedure)
    }

class TelemedicineServices(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for telemedicine or virtual encounters.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent a telemedicine or virtual encounter.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Telemedicine Services"
    OID = "2.16.840.1.113762.1.4.1248.276"
    DEFINITION_VERSION = "20250124"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "98000",  # Synchronous audio-video visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "98001",  # Synchronous audio-video visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "98002",  # Synchronous audio-video visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate medical decision making. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "98003",  # Synchronous audio-video visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "98004",  # Synchronous audio-video visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 10 minutes must be met or exceeded.
        "98005",  # Synchronous audio-video visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "98006",  # Synchronous audio-video visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "98007",  # Synchronous audio-video visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "98008",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination, straightforward medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "98009",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination, low medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "98010",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination, moderate medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "98011",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination, high medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "98012",  # Synchronous audio-only visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination, straightforward medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 10 minutes must be exceeded.
        "98013",  # Synchronous audio-only visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination, low medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "98014",  # Synchronous audio-only visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination, moderate medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "98015",  # Synchronous audio-only visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination, high medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "98016",  # Brief communication technology-based service (eg, virtual check-in) by a physician or other qualified health care professional who can report evaluation and management services, provided to an established patient, not originating from a related evaluation and management service provided within the previous 7 days nor leading to an evaluation and management service or procedure within the next 24 hours or soonest available appointment, 5-10 minutes of medical discussion
    }

class EncounterToDocumentMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters that include documentation of current medications.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that identify an encounter that includes documentation of medications reviewed, updated or transcribed as the current medication list.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Encounter to Document Medications"
    OID = "2.16.840.1.113883.3.600.1.1834"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "59400",  # Routine obstetric care including antepartum care, vaginal delivery (with or without episiotomy, and/or forceps) and postpartum care
        "59510",  # Routine obstetric care including antepartum care, cesarean delivery, and postpartum care
        "59610",  # Routine obstetric care including antepartum care, vaginal delivery (with or without episiotomy, and/or forceps) and postpartum care, after previous cesarean delivery
        "59618",  # Routine obstetric care including antepartum care, cesarean delivery, and postpartum care, following attempted vaginal delivery after previous cesarean delivery
        "90791",  # Psychiatric diagnostic evaluation
        "90792",  # Psychiatric diagnostic evaluation with medical services
        "90832",  # Psychotherapy, 30 minutes with patient
        "90834",  # Psychotherapy, 45 minutes with patient
        "90837",  # Psychotherapy, 60 minutes with patient
        "90839",  # Psychotherapy for crisis; first 60 minutes
        "92002",  # Ophthalmological services: medical examination and evaluation with initiation of diagnostic and treatment program; intermediate, new patient
        "92004",  # Ophthalmological services: medical examination and evaluation with initiation of diagnostic and treatment program; comprehensive, new patient, 1 or more visits
        "92012",  # Ophthalmological services: medical examination and evaluation, with initiation or continuation of diagnostic and treatment program; intermediate, established patient
        "92014",  # Ophthalmological services: medical examination and evaluation, with initiation or continuation of diagnostic and treatment program; comprehensive, established patient, 1 or more visits
        "92507",  # Treatment of speech, language, voice, communication, and/or auditory processing disorder; individual
        "92508",  # Treatment of speech, language, voice, communication, and/or auditory processing disorder; group, 2 or more individuals
        "92526",  # Treatment of swallowing dysfunction and/or oral function for feeding
        "92537",  # Caloric vestibular test with recording, bilateral; bithermal (ie, one warm and one cool irrigation in each ear for a total of four irrigations)
        "92538",  # Caloric vestibular test with recording, bilateral; monothermal (ie, one irrigation in each ear for a total of two irrigations)
        "92540",  # Basic vestibular evaluation, includes spontaneous nystagmus test with eccentric gaze fixation nystagmus, with recording, positional nystagmus test, minimum of 4 positions, with recording, optokinetic nystagmus test, bidirectional foveal and peripheral stimulation, with recording, and oscillating tracking test, with recording
        "92541",  # Spontaneous nystagmus test, including gaze and fixation nystagmus, with recording
        "92542",  # Positional nystagmus test, minimum of 4 positions, with recording
        "92544",  # Optokinetic nystagmus test, bidirectional, foveal or peripheral stimulation, with recording
        "92545",  # Oscillating tracking test, with recording
        "92547",  # Use of vertical electrodes (List separately in addition to code for primary procedure)
        "92548",  # Computerized dynamic posturography sensory organization test (CDP-SOT), 6 conditions (ie, eyes open, eyes closed, visual sway, platform sway, eyes closed platform sway, platform and visual sway), including interpretation and report
        "92549",  # Computerized dynamic posturography sensory organization test (CDP-SOT), 6 conditions (ie, eyes open, eyes closed, visual sway, platform sway, eyes closed platform sway, platform and visual sway), including interpretation and report; with motor control test (MCT) and adaptation test (ADT)
        "92550",  # Tympanometry and reflex threshold measurements
        "92557",  # Comprehensive audiometry threshold evaluation and speech recognition (92553 and 92556 combined)
        "92567",  # Tympanometry (impedance testing)
        "92568",  # Acoustic reflex testing, threshold
        "92570",  # Acoustic immittance testing, includes tympanometry (impedance testing), acoustic reflex threshold testing, and acoustic reflex decay testing
        "92588",  # Distortion product evoked otoacoustic emissions; comprehensive diagnostic evaluation (quantitative analysis of outer hair cell function by cochlear mapping, minimum of 12 frequencies), with interpretation and report
        "92626",  # Evaluation of auditory function for surgically implanted device(s) candidacy or postoperative status of a surgically implanted device(s); first hour
        "92650",  # Auditory evoked potentials; screening of auditory potential with broadband stimuli, automated analysis
        "92651",  # Auditory evoked potentials; for hearing status determination, broadband stimuli, with interpretation and report
        "92652",  # Auditory evoked potentials; for threshold estimation at multiple frequencies, with interpretation and report
        "92653",  # Auditory evoked potentials; neurodiagnostic, with interpretation and report
        "96116",  # Neurobehavioral status exam (clinical assessment of thinking, reasoning and judgment, [eg, acquired knowledge, attention, language, memory, planning and problem solving, and visual spatial abilities]), by physician or other qualified health care professional, both face-to-face time with the patient and time interpreting test results and preparing the report; first hour
        "96156",  # Health behavior assessment, or re-assessment (ie, health-focused clinical interview, behavioral observations, clinical decision making)
        "96158",  # Health behavior intervention, individual, face-to-face; initial 30 minutes
        "97129",  # Therapeutic interventions that focus on cognitive function (eg, attention, memory, reasoning, executive function, problem solving, and/or pragmatic functioning) and compensatory strategies to manage the performance of an activity (eg, managing time or schedules, initiating, organizing, and sequencing tasks), direct (one-on-one) patient contact; initial 15 minutes
        "97161",  # Physical therapy evaluation: low complexity, requiring these components: A history with no personal factors and/or comorbidities that impact the plan of care; An examination of body system(s) using standardized tests and measures addressing 1-2 elements from any of the following: body structures and functions, activity limitations, and/or participation restrictions; A clinical presentation with stable and/or uncomplicated characteristics; and Clinical decision making of low complexity using standardized patient assessment instrument and/or measurable assessment of functional outcome. Typically, 20 minutes are spent face-to-face with the patient and/or family.
        "97162",  # Physical therapy evaluation: moderate complexity, requiring these components: A history of present problem with 1-2 personal factors and/or comorbidities that impact the plan of care; An examination of body systems using standardized tests and measures in addressing a total of 3 or more elements from any of the following: body structures and functions, activity limitations, and/or participation restrictions; An evolving clinical presentation with changing characteristics; and Clinical decision making of moderate complexity using standardized patient assessment instrument and/or measurable assessment of functional outcome. Typically, 30 minutes are spent face-to-face with the patient and/or family.
        "97163",  # Physical therapy evaluation: high complexity, requiring these components: A history of present problem with 3 or more personal factors and/or comorbidities that impact the plan of care; An examination of body systems using standardized tests and measures addressing a total of 4 or more elements from any of the following: body structures and functions, activity limitations, and/or participation restrictions; A clinical presentation with unstable and unpredictable characteristics; and Clinical decision making of high complexity using standardized patient assessment instrument and/or measurable assessment of functional outcome. Typically, 45 minutes are spent face-to-face with the patient and/or family.
        "97164",  # Re-evaluation of physical therapy established plan of care, requiring these components: An examination including a review of history and use of standardized tests and measures is required; and Revised plan of care using a standardized patient assessment instrument and/or measurable assessment of functional outcome Typically, 20 minutes are spent face-to-face with the patient and/or family.
        "97165",  # Occupational therapy evaluation, low complexity, requiring these components: An occupational profile and medical and therapy history, which includes a brief history including review of medical and/or therapy records relating to the presenting problem; An assessment(s) that identifies 1-3 performance deficits (ie, relating to physical, cognitive, or psychosocial skills) that result in activity limitations and/or participation restrictions; and Clinical decision making of low complexity, which includes an analysis of the occupational profile, analysis of data from problem-focused assessment(s), and consideration of a limited number of treatment options. Patient presents with no comorbidities that affect occupational performance. Modification of tasks or assistance (eg, physical or verbal) with assessment(s) is not necessary to enable completion of evaluation component. Typically, 30 minutes are spent face-to-face with the patient and/or family.
        "97166",  # Occupational therapy evaluation, moderate complexity, requiring these components: An occupational profile and medical and therapy history, which includes an expanded review of medical and/or therapy records and additional review of physical, cognitive, or psychosocial history related to current functional performance; An assessment(s) that identifies 3-5 performance deficits (ie, relating to physical, cognitive, or psychosocial skills) that result in activity limitations and/or participation restrictions; and Clinical decision making of moderate analytic complexity, which includes an analysis of the occupational profile, analysis of data from detailed assessment(s), and consideration of several treatment options. Patient may present with comorbidities that affect occupational performance. Minimal to moderate modification of tasks or assistance (eg, physical or verbal) with assessment(s) is necessary to enable patient to complete evaluation component. Typically, 45 minutes are spent face-to-face with the patient and/or family.
        "97167",  # Occupational therapy evaluation, high complexity, requiring these components: An occupational profile and medical and therapy history, which includes review of medical and/or therapy records and extensive additional review of physical, cognitive, or psychosocial history related to current functional performance; An assessment(s) that identifies 5 or more performance deficits (ie, relating to physical, cognitive, or psychosocial skills) that result in activity limitations and/or participation restrictions; and Clinical decision making of high analytic complexity, which includes an analysis of the patient profile, analysis of data from comprehensive assessment(s), and consideration of multiple treatment options. Patient presents with comorbidities that affect occupational performance. Significant modification of tasks or assistance (eg, physical or verbal) with assessment(s) is necessary to enable patient to complete evaluation component. Typically, 60 minutes are spent face-to-face with the patient and/or family.
        "97168",  # Re-evaluation of occupational therapy established plan of care, requiring these components: An assessment of changes in patient functional or medical status with revised plan of care; An update to the initial occupational profile to reflect changes in condition or environment that affect future interventions and/or goals; and A revised plan of care. A formal reevaluation is performed when there is a documented change in functional status or a significant change to the plan of care is required. Typically, 30 minutes are spent face-to-face with the patient and/or family.
        "97802",  # Medical nutrition therapy; initial assessment and intervention, individual, face-to-face with the patient, each 15 minutes
        "97803",  # Medical nutrition therapy; re-assessment and intervention, individual, face-to-face with the patient, each 15 minutes
        "97804",  # Medical nutrition therapy; group (2 or more individual(s)), each 30 minutes
        "98000",  # Synchronous audio-video visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "98001",  # Synchronous audio-video visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "98002",  # Synchronous audio-video visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate medical decision making. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "98003",  # Synchronous audio-video visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "98004",  # Synchronous audio-video visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 10 minutes must be met or exceeded.
        "98005",  # Synchronous audio-video visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "98006",  # Synchronous audio-video visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "98007",  # Synchronous audio-video visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "98008",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination, straightforward medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "98009",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination, low medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "98010",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination, moderate medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "98011",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination, high medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "98012",  # Synchronous audio-only visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination, straightforward medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 10 minutes must be exceeded.
        "98013",  # Synchronous audio-only visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination, low medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "98014",  # Synchronous audio-only visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination, moderate medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "98015",  # Synchronous audio-only visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination, high medical decision making, and more than 10 minutes of medical discussion. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "98016",  # Brief communication technology-based service (eg, virtual check-in) by a physician or other qualified health care professional who can report evaluation and management services, provided to an established patient, not originating from a related evaluation and management service provided within the previous 7 days nor leading to an evaluation and management service or procedure within the next 24 hours or soonest available appointment, 5-10 minutes of medical discussion
        "98960",  # Education and training for patient self-management by a nonphysician qualified health care professional using a standardized curriculum, face-to-face with the patient (could include caregiver/family) each 30 minutes; individual patient
        "98961",  # Education and training for patient self-management by a nonphysician qualified health care professional using a standardized curriculum, face-to-face with the patient (could include caregiver/family) each 30 minutes; 2-4 patients
        "98962",  # Education and training for patient self-management by a nonphysician qualified health care professional using a standardized curriculum, face-to-face with the patient (could include caregiver/family) each 30 minutes; 5-8 patients
        "99202",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "99203",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99204",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "99205",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "99211",  # Office or other outpatient visit for the evaluation and management of an established patient that may not require the presence of a physician or other qualified health care professional
        "99212",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 10 minutes must be met or exceeded.
        "99213",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99214",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99215",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99221",  # Initial hospital inpatient or observation care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and straightforward or low level medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99222",  # Initial hospital inpatient or observation care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 55 minutes must be met or exceeded.
        "99223",  # Initial hospital inpatient or observation care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 75 minutes must be met or exceeded.
        "99236",  # Hospital inpatient or observation care, for the evaluation and management of a patient including admission and discharge on the same date, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 85 minutes must be met or exceeded.
        "99281",  # Emergency department visit for the evaluation and management of a patient that may not require the presence of a physician or other qualified health care professional
        "99282",  # Emergency department visit for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and straightforward medical decision making
        "99283",  # Emergency department visit for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and low level of medical decision making
        "99284",  # Emergency department visit for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making
        "99285",  # Emergency department visit for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and high level of medical decision making
        "99304",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and straightforward or low level of medical decision making. When using total time on the date of the encounter for code selection, 25 minutes must be met or exceeded.
        "99305",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 35 minutes must be met or exceeded.
        "99306",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 50 minutes must be met or exceeded.
        "99307",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 10 minutes must be met or exceeded.
        "99308",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99309",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99310",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "99315",  # Nursing facility discharge management; 30 minutes or less total time on the date of the encounter
        "99316",  # Nursing facility discharge management; more than 30 minutes total time on the date of the encounter
        "99341",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "99342",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99344",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "99345",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 75 minutes must be met or exceeded.
        "99347",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99348",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99349",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99350",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "99385",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 18-39 years
        "99386",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 40-64 years
        "99387",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 65 years and older
        "99395",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 18-39 years
        "99396",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 40-64 years
        "99397",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 65 years and older
        "99424",  # Principal care management services, for a single high-risk disease, with the following required elements: one complex chronic condition expected to last at least 3 months, and that places the patient at significant risk of hospitalization, acute exacerbation/decompensation, functional decline, or death, the condition requires development, monitoring, or revision of disease-specific care plan, the condition requires frequent adjustments in the medication regimen and/or the management of the condition is unusually complex due to comorbidities, ongoing communication and care coordination between relevant practitioners furnishing care; first 30 minutes provided personally by a physician or other qualified health care professional, per calendar month.
        "99491",  # Chronic care management services with the following required elements: multiple (two or more) chronic conditions expected to last at least 12 months, or until the death of the patient, chronic conditions that place the patient at significant risk of death, acute exacerbation/decompensation, or functional decline, comprehensive care plan established, implemented, revised, or monitored; first 30 minutes provided personally by a physician or other qualified health care professional, per calendar month.
        "99495",  # Transitional care management services with the following required elements: Communication (direct contact, telephone, electronic) with the patient and/or caregiver within 2 business days of discharge At least moderate level of medical decision making during the service period Face-to-face visit, within 14 calendar days of discharge
        "99496",  # Transitional care management services with the following required elements: Communication (direct contact, telephone, electronic) with the patient and/or caregiver within 2 business days of discharge High level of medical decision making during the service period Face-to-face visit, within 7 calendar days of discharge
    }

    HCPCSLEVELII = {
        "G0101",  # Cervical or vaginal cancer screening; pelvic and clinical breast examination
        "G0108",  # Diabetes outpatient self-management training services, individual, per 30 minutes
        "G0270",  # Medical nutrition therapy; reassessment and subsequent intervention(s) following second referral in same year for change in diagnosis, medical condition or treatment regimen (including additional hours needed for renal disease), individual, face to face with the patient, each 15 minutes
        "G0402",  # Initial preventive physical examination; face-to-face visit, services limited to new beneficiary during the first 12 months of medicare enrollment
        "G0438",  # Annual wellness visit; includes a personalized prevention plan of service (pps), initial visit
        "G0439",  # Annual wellness visit, includes a personalized prevention plan of service (pps), subsequent visit
    }

    SNOMEDCT = {
        "10197000",  # Psychiatric interview and evaluation (procedure)
        "108220007",  # Evaluation AND/OR management - new patient (procedure)
        "108221006",  # Evaluation AND/OR management - established patient (procedure)
        "108224003",  # Preventive patient evaluation (procedure)
        "108311000",  # Psychiatric procedure, interview AND/OR consultation (procedure)
        "13607009",  # Manual examination of breast (procedure)
        "14736009",  # History and physical examination with evaluation and management of patient (procedure)
        "163497009",  # Obstetric examination (procedure)
        "165171009",  # Initial psychiatric evaluation (procedure)
        "169762003",  # Postnatal visit (regime/therapy)
        "18091003",  # Electronystagmography with vertical electrodes (procedure)
        "18114009",  # Prenatal examination and care of mother (procedure)
        "183382003",  # Psychotherapy - behavioral (regime/therapy)
        "183383008",  # Psychotherapy - cognitive (regime/therapy)
        "18512000",  # Individual psychotherapy (regime/therapy)
        "185349003",  # Encounter for check up (procedure)
        "185463005",  # Visit out of hours (procedure)
        "185465003",  # Weekend visit (procedure)
        "209099002",  # History and physical examination with management of domiciliary or rest home patient (procedure)
        "210098006",  # Domiciliary or rest home patient evaluation and management (procedure)
        "225967005",  # Self-care patient education (procedure)
        "252592009",  # Speech audiometry (procedure)
        "252624005",  # Evoked oto-acoustic emission measurement (procedure)
        "270427003",  # Patient-initiated encounter (procedure)
        "270430005",  # Provider-initiated encounter (procedure)
        "274803000",  # Examination of tympanic membrane (procedure)
        "277404009",  # High frequency tympanometry (procedure)
        "284015009",  # Auditory evoked potentials monitoring (regime/therapy)
        "308335008",  # Patient encounter procedure (procedure)
        "34651001",  # Optokinetic nystagmus test, bidirectional, with recording (procedure)
        "35025007",  # Manual pelvic examination (procedure)
        "36228007",  # Ophthalmic examination and evaluation (procedure)
        "370803007",  # Evaluation of psychosocial impact on plan of care (procedure)
        "386372009",  # Nutrition management (regime/therapy)
        "390906007",  # Follow-up encounter (procedure)
        "406547006",  # Urgent follow-up (procedure)
        "408983003",  # Renal care management (procedure)
        "410155007",  # Occupational therapy assessment (procedure)
        "410157004",  # Occupational therapy management (procedure)
        "410158009",  # Physical therapy assessment (procedure)
        "410160006",  # Physical therapy management (procedure)
        "410170008",  # Nutrition care assessment (procedure)
        "439708006",  # Home visit (procedure)
        "439952009",  # Evaluation of auditory rehabilitation (procedure)
        "440524004",  # Oscillating tracking test with recording (procedure)
        "46662001",  # Examination of breast (procedure)
        "48423005",  # Acoustic reflex testing (procedure)
        "50357006",  # Evaluation and management of patient at home (procedure)
        "53555003",  # Basic comprehensive audiometry testing (procedure)
        "54290001",  # Positional nystagmus test with recording (procedure)
        "63547008",  # Caloric vestibular test with recording (procedure)
        "66902005",  # Ophthalmic examination and evaluation, follow-up (procedure)
        "698610002",  # Education about self management of diabetes (procedure)
        "78318003",  # History and physical examination, annual for health maintenance (procedure)
        "83607001",  # Gynecologic examination (procedure)
        "8411005",  # Interactive individual medical psychotherapy (regime/therapy)
        "86013001",  # Periodic reevaluation and management of healthy individual (procedure)
        "870422002",  # Assessment of self management of diabetes mellitus (procedure)
        "90526000",  # Initial evaluation and management of healthy individual (procedure)
        "91573000",  # Tympanometry testing (procedure)
    }

class EncounterToEvaluateBmi(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters where body mass index (BMI) could be assessed.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts for encounters where body mass index (BMI) could be assessed.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Encounter to Evaluate BMI"
    OID = "2.16.840.1.113883.3.600.1.1751"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CDT = {
        "D3921",  # decoronation or submergence of an erupted tooth
        "D7111",  # extraction, coronal remnants - primary tooth
        "D7140",  # extraction, erupted tooth or exposed root (elevation and/or forceps removal)
        "D7210",  # extraction, erupted tooth requiring removal of bone and/or sectioning of tooth, and including elevation of mucoperiosteal flap if indicated
        "D7220",  # removal of impacted tooth - soft tissue
        "D7230",  # removal of impacted tooth - partially bony
        "D7240",  # removal of impacted tooth - completely bony
        "D7241",  # removal of impacted tooth - completely bony, with unusual surgical complications
        "D7250",  # removal of residual tooth roots (cutting procedure)
        "D7251",  # coronectomy - intentional partial tooth removal, impacted teeth only
    }

    CPT = {
        "90791",  # Psychiatric diagnostic evaluation
        "90792",  # Psychiatric diagnostic evaluation with medical services
        "90832",  # Psychotherapy, 30 minutes with patient
        "90834",  # Psychotherapy, 45 minutes with patient
        "90837",  # Psychotherapy, 60 minutes with patient
        "96156",  # Health behavior assessment, or re-assessment (ie, health-focused clinical interview, behavioral observations, clinical decision making)
        "96158",  # Health behavior intervention, individual, face-to-face; initial 30 minutes
        "96159",  # Health behavior intervention, individual, face-to-face; each additional 15 minutes (List separately in addition to code for primary service)
        "97161",  # Physical therapy evaluation: low complexity, requiring these components: A history with no personal factors and/or comorbidities that impact the plan of care; An examination of body system(s) using standardized tests and measures addressing 1-2 elements from any of the following: body structures and functions, activity limitations, and/or participation restrictions; A clinical presentation with stable and/or uncomplicated characteristics; and Clinical decision making of low complexity using standardized patient assessment instrument and/or measurable assessment of functional outcome. Typically, 20 minutes are spent face-to-face with the patient and/or family.
        "97162",  # Physical therapy evaluation: moderate complexity, requiring these components: A history of present problem with 1-2 personal factors and/or comorbidities that impact the plan of care; An examination of body systems using standardized tests and measures in addressing a total of 3 or more elements from any of the following: body structures and functions, activity limitations, and/or participation restrictions; An evolving clinical presentation with changing characteristics; and Clinical decision making of moderate complexity using standardized patient assessment instrument and/or measurable assessment of functional outcome. Typically, 30 minutes are spent face-to-face with the patient and/or family.
        "97163",  # Physical therapy evaluation: high complexity, requiring these components: A history of present problem with 3 or more personal factors and/or comorbidities that impact the plan of care; An examination of body systems using standardized tests and measures addressing a total of 4 or more elements from any of the following: body structures and functions, activity limitations, and/or participation restrictions; A clinical presentation with unstable and unpredictable characteristics; and Clinical decision making of high complexity using standardized patient assessment instrument and/or measurable assessment of functional outcome. Typically, 45 minutes are spent face-to-face with the patient and/or family.
        "97165",  # Occupational therapy evaluation, low complexity, requiring these components: An occupational profile and medical and therapy history, which includes a brief history including review of medical and/or therapy records relating to the presenting problem; An assessment(s) that identifies 1-3 performance deficits (ie, relating to physical, cognitive, or psychosocial skills) that result in activity limitations and/or participation restrictions; and Clinical decision making of low complexity, which includes an analysis of the occupational profile, analysis of data from problem-focused assessment(s), and consideration of a limited number of treatment options. Patient presents with no comorbidities that affect occupational performance. Modification of tasks or assistance (eg, physical or verbal) with assessment(s) is not necessary to enable completion of evaluation component. Typically, 30 minutes are spent face-to-face with the patient and/or family.
        "97166",  # Occupational therapy evaluation, moderate complexity, requiring these components: An occupational profile and medical and therapy history, which includes an expanded review of medical and/or therapy records and additional review of physical, cognitive, or psychosocial history related to current functional performance; An assessment(s) that identifies 3-5 performance deficits (ie, relating to physical, cognitive, or psychosocial skills) that result in activity limitations and/or participation restrictions; and Clinical decision making of moderate analytic complexity, which includes an analysis of the occupational profile, analysis of data from detailed assessment(s), and consideration of several treatment options. Patient may present with comorbidities that affect occupational performance. Minimal to moderate modification of tasks or assistance (eg, physical or verbal) with assessment(s) is necessary to enable patient to complete evaluation component. Typically, 45 minutes are spent face-to-face with the patient and/or family.
        "97167",  # Occupational therapy evaluation, high complexity, requiring these components: An occupational profile and medical and therapy history, which includes review of medical and/or therapy records and extensive additional review of physical, cognitive, or psychosocial history related to current functional performance; An assessment(s) that identifies 5 or more performance deficits (ie, relating to physical, cognitive, or psychosocial skills) that result in activity limitations and/or participation restrictions; and Clinical decision making of high analytic complexity, which includes an analysis of the patient profile, analysis of data from comprehensive assessment(s), and consideration of multiple treatment options. Patient presents with comorbidities that affect occupational performance. Significant modification of tasks or assistance (eg, physical or verbal) with assessment(s) is necessary to enable patient to complete evaluation component. Typically, 60 minutes are spent face-to-face with the patient and/or family.
        "97802",  # Medical nutrition therapy; initial assessment and intervention, individual, face-to-face with the patient, each 15 minutes
        "97803",  # Medical nutrition therapy; re-assessment and intervention, individual, face-to-face with the patient, each 15 minutes
        "99202",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "99203",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99204",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "99205",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "99212",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 10 minutes must be met or exceeded.
        "99213",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99214",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99215",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99242",  # Office or other outpatient consultation for a new or established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99243",  # Office or other outpatient consultation for a new or established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99244",  # Office or other outpatient consultation for a new or established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99245",  # Office or other outpatient consultation for a new or established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 55 minutes must be met or exceeded.
        "99304",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and straightforward or low level of medical decision making. When using total time on the date of the encounter for code selection, 25 minutes must be met or exceeded.
        "99305",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 35 minutes must be met or exceeded.
        "99306",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 50 minutes must be met or exceeded.
        "99307",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 10 minutes must be met or exceeded.
        "99308",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99309",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99310",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "99315",  # Nursing facility discharge management; 30 minutes or less total time on the date of the encounter
        "99316",  # Nursing facility discharge management; more than 30 minutes total time on the date of the encounter
        "99341",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 15 minutes must be met or exceeded.
        "99342",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99344",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "99345",  # Home or residence visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 75 minutes must be met or exceeded.
        "99347",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using total time on the date of the encounter for code selection, 20 minutes must be met or exceeded.
        "99348",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using total time on the date of the encounter for code selection, 30 minutes must be met or exceeded.
        "99349",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99350",  # Home or residence visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 60 minutes must be met or exceeded.
        "99385",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 18-39 years
        "99386",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 40-64 years
        "99387",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 65 years and older
        "99395",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 18-39 years
        "99396",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 40-64 years
        "99397",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 65 years and older
        "99401",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 15 minutes
        "99402",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 30 minutes
        "99491",  # Chronic care management services with the following required elements: multiple (two or more) chronic conditions expected to last at least 12 months, or until the death of the patient, chronic conditions that place the patient at significant risk of death, acute exacerbation/decompensation, or functional decline, comprehensive care plan established, implemented, revised, or monitored; first 30 minutes provided personally by a physician or other qualified health care professional, per calendar month.
    }

    HCPCSLEVELII = {
        "G0101",  # Cervical or vaginal cancer screening; pelvic and clinical breast examination
        "G0108",  # Diabetes outpatient self-management training services, individual, per 30 minutes
        "G0270",  # Medical nutrition therapy; reassessment and subsequent intervention(s) following second referral in same year for change in diagnosis, medical condition or treatment regimen (including additional hours needed for renal disease), individual, face to face with the patient, each 15 minutes
        "G0271",  # Medical nutrition therapy, reassessment and subsequent intervention(s) following second referral in same year for change in diagnosis, medical condition, or treatment regimen (including additional hours needed for renal disease), group (2 or more individuals), each 30 minutes
        "G0402",  # Initial preventive physical examination; face-to-face visit, services limited to new beneficiary during the first 12 months of medicare enrollment
        "G0438",  # Annual wellness visit; includes a personalized prevention plan of service (pps), initial visit
        "G0439",  # Annual wellness visit, includes a personalized prevention plan of service (pps), subsequent visit
        "G0447",  # Face-to-face behavioral counseling for obesity, 15 minutes
        "G0473",  # Face-to-face behavioral counseling for obesity, group (2-10), 30 minutes
    }

    SNOMEDCT = {
        "10197000",  # Psychiatric interview and evaluation (procedure)
        "108220007",  # Evaluation AND/OR management - new patient (procedure)
        "108221006",  # Evaluation AND/OR management - established patient (procedure)
        "108224003",  # Preventive patient evaluation (procedure)
        "108311000",  # Psychiatric procedure, interview AND/OR consultation (procedure)
        "13607009",  # Manual examination of breast (procedure)
        "14736009",  # History and physical examination with evaluation and management of patient (procedure)
        "165171009",  # Initial psychiatric evaluation (procedure)
        "18512000",  # Individual psychotherapy (regime/therapy)
        "185349003",  # Encounter for check up (procedure)
        "185463005",  # Visit out of hours (procedure)
        "185465003",  # Weekend visit (procedure)
        "209099002",  # History and physical examination with management of domiciliary or rest home patient (procedure)
        "210098006",  # Domiciliary or rest home patient evaluation and management (procedure)
        "225967005",  # Self-care patient education (procedure)
        "270427003",  # Patient-initiated encounter (procedure)
        "270430005",  # Provider-initiated encounter (procedure)
        "308335008",  # Patient encounter procedure (procedure)
        "35025007",  # Manual pelvic examination (procedure)
        "386372009",  # Nutrition management (regime/therapy)
        "390906007",  # Follow-up encounter (procedure)
        "406547006",  # Urgent follow-up (procedure)
        "410155007",  # Occupational therapy assessment (procedure)
        "410157004",  # Occupational therapy management (procedure)
        "410158009",  # Physical therapy assessment (procedure)
        "410160006",  # Physical therapy management (procedure)
        "410170008",  # Nutrition care assessment (procedure)
        "410172000",  # Nutrition care management (procedure)
        "46662001",  # Examination of breast (procedure)
        "55162003",  # Tooth extraction (procedure)
        "68381003",  # Surgical removal of erupted tooth requiring elevation of mucoperiosteal flap and removal of bone and/or section of tooth (procedure)
        "78318003",  # History and physical examination, annual for health maintenance (procedure)
        "83607001",  # Gynecologic examination (procedure)
        "8411005",  # Interactive individual medical psychotherapy (regime/therapy)
        "86013001",  # Periodic reevaluation and management of healthy individual (procedure)
        "90526000",  # Initial evaluation and management of healthy individual (procedure)
    }

class ClinicalOralEvaluation(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for clinical oral evaluations.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for periodic or limited (problem focused) or comprehensive oral evaluations and re-evaluations.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Clinical Oral Evaluation"
    OID = "2.16.840.1.113883.3.464.1003.125.12.1003"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CDT = {
        "D0120",  # periodic oral evaluation - established patient
        "D0140",  # limited oral evaluation - problem focused
        "D0145",  # oral evaluation for a patient under three years of age and counseling with primary caregiver
        "D0150",  # comprehensive oral evaluation - new or established patient
        "D0160",  # detailed and extensive oral evaluation - problem focused, by report
        "D0170",  # re-evaluation - limited, problem focused (established patient; not post-operative visit)
        "D0180",  # comprehensive periodontal evaluation - new or established patient
    }

class HospitalServicesForUrologyCare(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of encounters identifying hospital services for urology care.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter specific to hospital services for urology care.

    **Exclusion Criteria:** .No exclusions.
    """

    VALUE_SET_NAME = "Hospital Services for Urology Care"
    OID = "2.16.840.1.113762.1.4.1248.360"
    DEFINITION_VERSION = "20250312"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99221",  # Initial hospital inpatient or observation care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and straightforward or low level medical decision making. When using total time on the date of the encounter for code selection, 40 minutes must be met or exceeded.
        "99222",  # Initial hospital inpatient or observation care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 55 minutes must be met or exceeded.
        "99223",  # Initial hospital inpatient or observation care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 75 minutes must be met or exceeded.
        "99231",  # Subsequent hospital inpatient or observation care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and straightforward or low level of medical decision making. When using total time on the date of the encounter for code selection, 25 minutes must be met or exceeded.
        "99232",  # Subsequent hospital inpatient or observation care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 35 minutes must be met or exceeded.
        "99233",  # Subsequent hospital inpatient or observation care, per day, for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 50 minutes must be met or exceeded.
        "99234",  # Hospital inpatient or observation care, for the evaluation and management of a patient including admission and discharge on the same date, which requires a medically appropriate history and/or examination and straightforward or low level of medical decision making. When using total time on the date of the encounter for code selection, 45 minutes must be met or exceeded.
        "99235",  # Hospital inpatient or observation care, for the evaluation and management of a patient including admission and discharge on the same date, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using total time on the date of the encounter for code selection, 70 minutes must be met or exceeded.
        "99236",  # Hospital inpatient or observation care, for the evaluation and management of a patient including admission and discharge on the same date, which requires a medically appropriate history and/or examination and high level of medical decision making. When using total time on the date of the encounter for code selection, 85 minutes must be met or exceeded.
        "99238",  # Hospital inpatient or observation discharge day management; 30 minutes or less on the date of the encounter
        "99239",  # Hospital inpatient or observation discharge day management; more than 30 minutes on the date of the encounter
        "99281",  # Emergency department visit for the evaluation and management of a patient that may not require the presence of a physician or other qualified health care professional
        "99282",  # Emergency department visit for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and straightforward medical decision making
        "99283",  # Emergency department visit for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and low level of medical decision making
        "99284",  # Emergency department visit for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making
        "99285",  # Emergency department visit for the evaluation and management of a patient, which requires a medically appropriate history and/or examination and high level of medical decision making
    }

__exports__ = (
    "AnnualWellnessVisit",
    "EncounterInpatient",
    "FrailtyEncounter",
    "HomeHealthcareServices",
    "HospiceEncounter",
    "OfficeVisit",
    "PreventiveCareServicesEstablishedOfficeVisit18AndUp",
    "OphthalmologicalServices",
    "PalliativeCareEncounter",
    "TelephoneVisits",
    "EmergencyDepartmentVisit",
    "ObservationServices",
    "EdVisitAndObTriage",
    "NonelectiveInpatientEncounter",
    "OutpatientClinicalEncounters",
    "PreventativeClinicalEncounters",
    "FaceToFaceInteraction",
    "OutpatientConsultation",
    "PreventiveCareServicesInitialOfficeVisit18AndUp",
    "PreventiveCareServicesInitialOfficeVisit0To17",
    "PreventiveCareEstablishedOfficeVisit0To17",
    "OutpatientEncounter",
    "VirtualEncounter",
    "ElectiveInpatientEncounter",
    "OutpatientSurgeryService",
    "NutritionServices",
    "DecisionToAdmitToHospitalInpatient",
    "EmergencyDepartmentEvaluationAndManagementVisit",
    "Triage",
    "DecisionToTransfer",
    "NursingFacilityVisit",
    "PsychVisitDiagnosticEvaluation",
    "PsychVisitPsychotherapy",
    "CareServicesInLongTermResidentialFacility",
    "PatientProviderInteraction",
    "BehavioralHealthFollowUpVisit",
    "PreventiveCareServicesGroupCounseling",
    "PreventiveCareServicesIndividualCounseling",
    "PsychotherapyAndPharmacologicManagement",
    "DetoxificationVisit",
    "DischargeServicesHospitalInpatient",
    "DischargeServicesHospitalInpatientSameDayDischarge",
    "InitialHospitalInpatientVisit",
    "OccupationalTherapyEvaluation",
    "PhysicalTherapyEvaluation",
    "Psychoanalysis",
    "SpeechAndHearingEvaluation",
    "AudiologyVisit",
    "DischargeServicesNursingFacility",
    "MedicalDisabilityExam",
    "BehavioralOrNeuropsychAssessment",
    "AudioVisualTelehealthEncounter",
    "RadiationTreatmentManagement",
    "ContactOrOfficeVisit",
    "EsrdMonthlyOutpatientServices",
    "GroupPsychotherapy",
    "PsychVisitForFamilyPsychotherapy",
    "EncounterToScreenForBloodPressure",
    "EncounterToScreenForDepression",
    "OutpatientEncountersForPreventiveCare",
    "TelemedicineServices",
    "EncounterToDocumentMedications",
    "EncounterToEvaluateBmi",
    "ClinicalOralEvaluation",
    "HospitalServicesForUrologyCare",
)
