from ..value_set import ValueSet


class AnnualWellnessVisit(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for annual wellness visits.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for a Medicare annual wellness visit.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS130v14
    """

    VALUE_SET_NAME = "Annual Wellness Visit"
    OID = "2.16.840.1.113883.3.526.3.1240"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    HCPCSLEVELII = {
        "G0402",  # Initial preventive physical examination; face-to-face visit, services limited to new beneficiary ...
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
    **Clinical Focus:** The purpose of this value set is to represent concepts of  inpatient hospitalization encounters.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for inpatient hospitalizations.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS130v14
    """

    VALUE_SET_NAME = "Encounter Inpatient"
    OID = "2.16.840.1.113883.3.666.5.307"
    DEFINITION_VERSION = "20200307"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

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

    ** Used in:** CMS130v14
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
        "G0162",  # Skilled services by a registered nurse (rn) for management and evaluation of the plan of care; ea...
        "G0299",  # Direct skilled nursing services of a registered nurse (rn) in the home health or hospice setting,...
        "G0300",  # Direct skilled nursing services of a licensed practical nurse (lpn) in the home health or hospice...
        "G0493",  # Skilled services of a registered nurse (rn) for the observation and assessment of the patient\'s ...
        "G0494",  # Skilled services of a licensed practical nurse (lpn) for the observation and assessment of the pa...
        "S0271",  # Physician management of patient home care, hospice monthly case rate (per 30 days)
        "S0311",  # Comprehensive management and care coordination for advanced illness, per calendar month
        "S9123",  # Nursing care, in the home; by registered nurse, per hour (use for general nursing care only, not ...
        "S9124",  # Nursing care, in the home; by licensed practical nurse, per hour
        "T1000",  # Private duty / independent nursing service(s) - licensed, up to 15 minutes
        "T1001",  # Nursing assessment / evaluation
        "T1002",  # Rn services, up to 15 minutes
        "T1003",  # Lpn/lvn services, up to 15 minutes
        "T1004",  # Services of a qualified nursing aide, up to 15 minutes
        "T1005",  # Respite care services, up to 15 minutes
        "T1019",  # Personal care services, per 15 minutes, not for an inpatient or resident of a hospital, nursing f...
        "T1020",  # Personal care services, per diem, not for an inpatient or resident of a hospital, nursing facilit...
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

    ** Used in:** CMS130v14
    """

    VALUE_SET_NAME = "Home Healthcare Services"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1016"
    DEFINITION_VERSION = "20240110"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99341",  # Home or residence visit for the evaluation and management of a new patient, which requires a medi...
        "99342",  # Home or residence visit for the evaluation and management of a new patient, which requires a medi...
        "99344",  # Home or residence visit for the evaluation and management of a new patient, which requires a medi...
        "99345",  # Home or residence visit for the evaluation and management of a new patient, which requires a medi...
        "99347",  # Home or residence visit for the evaluation and management of an established patient, which requir...
        "99348",  # Home or residence visit for the evaluation and management of an established patient, which requir...
        "99349",  # Home or residence visit for the evaluation and management of an established patient, which requir...
        "99350",  # Home or residence visit for the evaluation and management of an established patient, which requir...
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
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for hospice care services.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent hospice services in a hospice, home or inpatient setting.

    **Exclusion Criteria:** Excludes concepts that represent palliative care or comfort measures.

    ** Used in:** CMS130v14
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

    ** Used in:** CMS130v14
    """

    VALUE_SET_NAME = "Office Visit"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1001"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99202",  # Office or other outpatient visit for the evaluation and management of a new patient, which requir...
        "99203",  # Office or other outpatient visit for the evaluation and management of a new patient, which requir...
        "99204",  # Office or other outpatient visit for the evaluation and management of a new patient, which requir...
        "99205",  # Office or other outpatient visit for the evaluation and management of a new patient, which requir...
        "99212",  # Office or other outpatient visit for the evaluation and management of an established patient, whi...
        "99213",  # Office or other outpatient visit for the evaluation and management of an established patient, whi...
        "99214",  # Office or other outpatient visit for the evaluation and management of an established patient, whi...
        "99215",  # Office or other outpatient visit for the evaluation and management of an established patient, whi...
    }

    SNOMEDCT = {
        "185349003",  # Encounter for check up (procedure)
        "185463005",  # Visit out of hours (procedure)
        "185464004",  # Out of hours visit - not night visit (procedure)
        "185465003",  # Weekend visit (procedure)
        "3391000175108",  # Office visit for pediatric care and assessment (procedure)
        "439740005",  # Postoperative follow-up visit (procedure)
    }

class PalliativeCareEncounter(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for palliative care services.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for admission and management for palliative care services.

    **Exclusion Criteria:** Excludes concepts that represent encounters for hospice and a referral to palliative care.

    ** Used in:** CMS130v14
    """

    VALUE_SET_NAME = "Palliative Care Encounter"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1090"
    DEFINITION_VERSION = "20210224"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    HCPCSLEVELII = {
        "G9054",  # Oncology; primary focus of visit; supervising, coordinating or managing care of patient with term...
    }

    SNOMEDCT = {
        "305284002",  # Admission by palliative care physician (procedure)
        "305381007",  # Admission to palliative care department (procedure)
        "305686008",  # Seen by palliative care physician (finding)
        "305824005",  # Seen by palliative care medicine service (finding)
        "441874000",  # Seen by palliative care service (finding)
        "4901000124101",  # Palliative care education (procedure)
        "713281006",  # Consultation for palliative care (procedure)
    }

class PreventiveCareServicesEstablishedOfficeVisit18AndUp(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for preventive care.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for comprehensive preventive medicine reevaluation and management of an established patient 18 years of age or over.

    **Exclusion Criteria:** Excludes initial visits for new patients.

    ** Used in:** CMS130v14
    """

    VALUE_SET_NAME = "Preventive Care Services Established Office Visit, 18 and Up"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1025"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99395",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including...
        "99396",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including...
        "99397",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including...
    }

class PreventiveCareServicesInitialOfficeVisit18AndUp(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for  preventive care.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an  encounter for comprehensive preventive medicine reevaluation and management of a new patient 18 years or over.

    **Exclusion Criteria:** Excludes visits for established patients.

    ** Used in:** CMS130v14
    """

    VALUE_SET_NAME = "Preventive Care Services Initial Office Visit, 18 and Up"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1023"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99385",  # Initial comprehensive preventive medicine evaluation and management of an individual including an...
        "99386",  # Initial comprehensive preventive medicine evaluation and management of an individual including an...
        "99387",  # Initial comprehensive preventive medicine evaluation and management of an individual including an...
    }

class TelephoneVisits(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for telephone visits.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for assessment, evaluation and management services to a patient by telephone.

    **Exclusion Criteria:** Excludes concepts that represent an encounter for telephone assessment, evaluation and management services that last for less than five minutes.

    ** Used in:** CMS130v14
    """

    VALUE_SET_NAME = "Telephone Visits"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1080"
    DEFINITION_VERSION = "20250205"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "98008",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a...
        "98009",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a...
        "98010",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a...
        "98011",  # Synchronous audio-only visit for the evaluation and management of a new patient, which requires a...
        "98012",  # Synchronous audio-only visit for the evaluation and management of an established patient, which r...
        "98013",  # Synchronous audio-only visit for the evaluation and management of an established patient, which r...
        "98014",  # Synchronous audio-only visit for the evaluation and management of an established patient, which r...
        "98015",  # Synchronous audio-only visit for the evaluation and management of an established patient, which r...
        "98966",  # Telephone assessment and management service provided by a nonphysician qualified health care prof...
        "98967",  # Telephone assessment and management service provided by a nonphysician qualified health care prof...
        "98968",  # Telephone assessment and management service provided by a nonphysician qualified health care prof...
        "99441",  # Telephone evaluation and management service by a physician or other qualified health care profess...
        "99442",  # Telephone evaluation and management service by a physician or other qualified health care profess...
        "99443",  # Telephone evaluation and management service by a physician or other qualified health care profess...
    }

    SNOMEDCT = {
        "185317003",  # Telephone encounter (procedure)
        "314849005",  # Telephone contact by consultant (procedure)
        "386472008",  # Telephone consultation (procedure)
        "386473003",  # Telephone follow-up (procedure)
        "401267002",  # Telephone triage encounter (procedure)
    }

class VirtualEncounter(ValueSet):
    """
    **Clinical Focus:** Includes concepts that represent an encounter using online modalities.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter using online modalities.

    **Exclusion Criteria:** Excludes concepts that represent encounters other than online.

    ** Used in:** CMS130v14
    """

    VALUE_SET_NAME = "Virtual Encounter"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1089"
    DEFINITION_VERSION = "20210224"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "98970",  # Nonphysician qualified health care professional online digital assessment and management, for an ...
        "98971",  # Nonphysician qualified health care professional online digital assessment and management, for an ...
        "98972",  # Nonphysician qualified health care professional online digital assessment and management, for an ...
        "98980",  # Remote therapeutic monitoring treatment management services, physician or other qualified health ...
        "98981",  # Remote therapeutic monitoring treatment management services, physician or other qualified health ...
        "99421",  # Online digital evaluation and management service, for an established patient, for up to 7 days, c...
        "99422",  # Online digital evaluation and management service, for an established patient, for up to 7 days, c...
        "99423",  # Online digital evaluation and management service, for an established patient, for up to 7 days, c...
        "99457",  # Remote physiologic monitoring treatment management services, clinical staff/physician/other quali...
        "99458",  # Remote physiologic monitoring treatment management services, clinical staff/physician/other quali...
    }

    HCPCSLEVELII = {
        "G0071",  # Payment for communication technology-based services for 5 minutes or more of a virtual (non-face-...
        "G2010",  # Remote evaluation of recorded video and/or images submitted by an established patient (e.g., stor...
        "G2012",  # Brief communication technology-based service, e.g. virtual check-in, by a physician or other qual...
        "G2250",  # Remote assessment of recorded video and/or images submitted by an established patient (e.g., stor...
        "G2251",  # Brief communication technology-based service, e.g. virtual check-in, by a qualified health care p...
        "G2252",  # Brief communication technology-based service, e.g. virtual check-in, by a physician or other qual...
    }



__exports__ = (
    "AnnualWellnessVisit",
    "EncounterInpatient",
    "FrailtyEncounter",
    "HomeHealthcareServices",
    "HospiceEncounter",
    "OfficeVisit",
    "PalliativeCareEncounter",
    "PreventiveCareServicesEstablishedOfficeVisit18AndUp",
    "PreventiveCareServicesInitialOfficeVisit18AndUp",
    "TelephoneVisits",
    "VirtualEncounter",
)