from canvas_sdk.value_set._utilities import get_overrides

from ..value_set import ValueSet


class EncounterInpatient(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of  inpatient hospitalization encounters.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for inpatient hospitalizations.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS90v11, CMS134v10, CMS165v10, CMS146v10, CMS124v10, CMS139v10, CMS154v10, CMS56v10, CMS74v11, CMS75v10, CMS137v10, CMS136v11, CMS128v10, CMS122v10, CMS153v10, CMS66v10, CMS130v10, CMS155v10, CMS127v10, CMS117v10, CMS131v10, CMS156v10, CMS125v10
    """

    VALUE_SET_NAME = "Encounter Inpatient"
    OID = "2.16.840.1.113883.3.666.5.307"
    DEFINITION_VERSION = "20200307"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "8715000",  # Hospital admission, elective (procedure)
        "32485007",  # Hospital admission (procedure)
        "183452005",  # Emergency hospital admission (procedure)
    }


class HomeHealthcareServices(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for home health visits.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for a home health visit for the evaluation and management of a new or established patient.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS135v10, CMS134v10, CMS165v10, CMS146v10, CMS124v10, CMS139v10, CMS154v10, CMS138v10, CMS136v11, CMS128v10, CMS122v10, CMS153v10, CMS144v10, CMS130v10, CMS155v10, CMS127v10, CMS117v10, CMS131v10, CMS149v10, CMS156v10, CMS147v11, CMS125v10, CMS145v10
    """

    VALUE_SET_NAME = "Home Healthcare Services"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1016"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99341",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: A problem focused history; A problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low severity. Typically, 20 minutes are spent face-to-face with the patient and/or family.
        "99342",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate severity. Typically, 30 minutes are spent face-to-face with the patient and/or family.
        "99343",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: A detailed history; A detailed examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 45 minutes are spent face-to-face with the patient and/or family.
        "99344",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of high severity. Typically, 60 minutes are spent face-to-face with the patient and/or family.
        "99345",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is unstable or has developed a significant new problem requiring immediate physician attention. Typically, 75 minutes are spent face-to-face with the patient and/or family.
        "99347",  # Home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self limited or minor. Typically, 15 minutes are spent face-to-face with the patient and/or family.
        "99348",  # Home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low to moderate severity. Typically, 25 minutes are spent face-to-face with the patient and/or family.
        "99349",  # Home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A detailed interval history; A detailed examination; Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are moderate to high severity. Typically, 40 minutes are spent face-to-face with the patient and/or family.
        "99350",  # Home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A comprehensive interval history; A comprehensive examination; Medical decision making of moderate to high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. The patient may be unstable or may have developed a significant new problem requiring immediate physician attention. Typically, 60 minutes are spent face-to-face with the patient and/or family.
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
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99201",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires these 3 key components: A problem focused history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self limited or minor. Typically, 10 minutes are spent face-to-face with the patient and/or family.
        "99202",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using time for code selection, 15-29 minutes of total time is spent on the date of the encounter.
        "99203",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using time for code selection, 30-44 minutes of total time is spent on the date of the encounter.
        "99204",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using time for code selection, 45-59 minutes of total time is spent on the date of the encounter.
        "99205",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using time for code selection, 60-74 minutes of total time is spent on the date of the encounter.
        "99212",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using time for code selection, 10-19 minutes of total time is spent on the date of the encounter.
        "99213",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using time for code selection, 20-29 minutes of total time is spent on the date of the encounter.
        "99214",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using time for code selection, 30-39 minutes of total time is spent on the date of the encounter.
        "99215",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using time for code selection, 40-54 minutes of total time is spent on the date of the encounter.
    }
    SNOMEDCT = {
        "30346009",  # Evaluation and management of established outpatient in office or other outpatient facility (procedure)
        "37894004",  # Evaluation and management of new outpatient in office or other outpatient facility (procedure)
        "185463005",  # Visit out of hours (procedure)
        "185464004",  # Out of hours visit - not night visit (procedure)
        "185465003",  # Weekend visit (procedure)
        "439740005",  # Postoperative follow-up visit (procedure)
        "3391000175108",  # Office visit for pediatric care and assessment (procedure)
    }


class OnlineAssessments(ValueSet):
    """
    **Clinical Focus:** Includes concepts that represent an encounter using online modalities.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter using online modalities.

    **Exclusion Criteria:** Excludes concepts that represent encounters other than online.

    ** Used in:** CMS90v11, CMS249v4, CMS165v10, CMS146v10, CMS124v10, CMS139v10, CMS154v10, CMS56v10, CMS74v11, CMS138v10, CMS137v10, CMS136v11, CMS128v10, CMS153v10, CMS66v10, CMS130v10, CMS127v10, CMS117v10, CMS156v10, CMS147v11, CMS125v10
    """

    VALUE_SET_NAME = "Online Assessments"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1089"
    DEFINITION_VERSION = "20210224"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "98969",  # Online assessment and management service provided by a qualified nonphysician health care professional to an established patient or guardian, not originating from a related assessment and management service provided within the previous 7 days, using the Internet or similar electronic communications network
        "98970",  # Qualified nonphysician health care professional online digital assessment and management, for an established patient, for up to 7 days, cumulative time during the 7 days; 5-10 minutes
        "98971",  # Qualified nonphysician health care professional online digital assessment and management, for an established patient, for up to 7 days, cumulative time during the 7 days; 11-20 minutes
        "98972",  # Qualified nonphysician health care professional online digital assessment and management, for an established patient, for up to 7 days, cumulative time during the 7 days; 21 or more minutes
        "99421",  # Online digital evaluation and management service, for an established patient, for up to 7 days, cumulative time during the 7 days; 5-10 minutes
        "99422",  # Online digital evaluation and management service, for an established patient, for up to 7 days, cumulative time during the 7 days; 11-20 minutes
        "99423",  # Online digital evaluation and management service, for an established patient, for up to 7 days, cumulative time during the 7 days; 21 or more minutes
        "99458",  # Remote physiologic monitoring treatment management services, clinical staff/physician/other qualified health care professional time in a calendar month requiring interactive communication with the patient/caregiver during the month; each additional 20 minutes (List separately in addition to code for primary procedure)
    }
    HCPCSLEVELII = {
        "G0071",  # Payment for communication technology-based services for 5 minutes or more of a virtual (non-face-to-face) communication between an rural health clinic (rhc) or federally qualified health center (fqhc) practitioner and rhc or fqhc patient, or 5 minutes or more of remote evaluation of recorded video and/or images by an rhc or fqhc practitioner, occurring in lieu of an office visit; rhc or fqhc only
        "G2010",  # Remote evaluation of recorded video and/or images submitted by an established patient (e.g., store and forward), including interpretation with follow-up with the patient within 24 business hours, not originating from a related e/m service provided within the previous 7 days nor leading to an e/m service or procedure within the next 24 hours or soonest available appointment
        "G2012",  # Brief communication technology-based service, e.g. virtual check-in, by a physician or other qualified health care professional who can report evaluation and management services, provided to an established patient, not originating from a related e/m service provided within the previous 7 days nor leading to an e/m service or procedure within the next 24 hours or soonest available appointment; 5-10 minutes of medical discussion
        "G2061",  # Qualified nonphysician healthcare professional online assessment and management service, for an established patient, for up to seven days, cumulative time during the 7 days; 5-10 minutes
        "G2062",  # Qualified nonphysician healthcare professional online assessment and management service, for an established patient, for up to seven days, cumulative time during the 7 days; 11-20 minutes
        "G2063",  # Qualified nonphysician healthcare professional online assessment and management service, for an established patient, for up to seven days, cumulative time during the 7 days; 21 or more minutes
    }


class PreventiveCareServices_InitialOfficeVisit_0To17(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for preventive care.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an  encounter for comprehensive preventive medicine reevaluation and management of a patient 0 to 17 years of age.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS155v10, CMS74v11, CMS136v11, CMS117v10, CMS146v10, CMS153v10, CMS50v10, CMS349v4, CMS147v11, CMS154v10
    """

    VALUE_SET_NAME = "Preventive Care Services, Initial Office Visit, 0 to 17"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1022"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99381",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; infant (age younger than 1 year)
        "99382",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; early childhood (age 1 through 4 years)
        "99383",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; late childhood (age 5 through 11 years)
        "99384",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; adolescent (age 12 through 17 years)
    }


class PreventiveCare_EstablishedOfficeVisit_0To17(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for preventative care.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for comprehensive preventive medicine reevaluation and management of an individual 0 to 17 years of age.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS155v10, CMS74v11, CMS136v11, CMS117v10, CMS146v10, CMS153v10, CMS50v10, CMS349v4, CMS147v11, CMS154v10
    """

    VALUE_SET_NAME = "Preventive Care, Established Office Visit, 0 to 17"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1024"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99391",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; infant (age younger than 1 year)
        "99392",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; early childhood (age 1 through 4 years)
        "99393",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; late childhood (age 5 through 11 years)
        "99394",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; adolescent (age 12 through 17 years)
    }


class TelephoneVisits(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for telephone visits.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for assessment, evaluation and management services to a patient by telephone.

    **Exclusion Criteria:** Excludes concepts that represent an encounter for telephone assessment, evaluation and management services that last for less than five minutes.

    ** Used in:** CMS90v11, CMS249v4, CMS134v10, CMS165v10, CMS146v10, CMS124v10, CMS139v10, CMS154v10, CMS56v10, CMS74v11, CMS138v10, CMS137v10, CMS136v11, CMS128v10, CMS122v10, CMS153v10, CMS66v10, CMS130v10, CMS155v10, CMS127v10, CMS117v10, CMS131v10, CMS156v10, CMS147v11, CMS125v10
    """

    VALUE_SET_NAME = "Telephone Visits"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1080"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "98966",  # Telephone assessment and management service provided by a qualified nonphysician health care professional to an established patient, parent, or guardian not originating from a related assessment and management service provided within the previous 7 days nor leading to an assessment and management service or procedure within the next 24 hours or soonest available appointment; 5-10 minutes of medical discussion
        "98967",  # Telephone assessment and management service provided by a qualified nonphysician health care professional to an established patient, parent, or guardian not originating from a related assessment and management service provided within the previous 7 days nor leading to an assessment and management service or procedure within the next 24 hours or soonest available appointment; 11-20 minutes of medical discussion
        "98968",  # Telephone assessment and management service provided by a qualified nonphysician health care professional to an established patient, parent, or guardian not originating from a related assessment and management service provided within the previous 7 days nor leading to an assessment and management service or procedure within the next 24 hours or soonest available appointment; 21-30 minutes of medical discussion
        "99441",  # Telephone evaluation and management service by a physician or other qualified health care professional who may report evaluation and management services provided to an established patient, parent, or guardian not originating from a related E/M service provided within the previous 7 days nor leading to an E/M service or procedure within the next 24 hours or soonest available appointment; 5-10 minutes of medical discussion
        "99442",  # Telephone evaluation and management service by a physician or other qualified health care professional who may report evaluation and management services provided to an established patient, parent, or guardian not originating from a related E/M service provided within the previous 7 days nor leading to an E/M service or procedure within the next 24 hours or soonest available appointment; 11-20 minutes of medical discussion
        "99443",  # Telephone evaluation and management service by a physician or other qualified health care professional who may report evaluation and management services provided to an established patient, parent, or guardian not originating from a related E/M service provided within the previous 7 days nor leading to an E/M service or procedure within the next 24 hours or soonest available appointment; 21-30 minutes of medical discussion
    }
    SNOMEDCT = {
        "185317003",  # Telephone encounter (procedure)
        "314849005",  # Telephone contact by consultant (procedure)
        "386472008",  # Telephone consultation (procedure)
        "386473003",  # Telephone follow-up (procedure)
        "401267002",  # Telephone triage encounter (procedure)
    }


class AcuteInpatient(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for acute inpatient visits.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for comprehensive history, evaluation, and management of a patient in an acute inpatient setting.

    **Exclusion Criteria:** Excludes concepts that represent encounters other than an acute inpatient visit.

    ** Used in:** CMS134v10, CMS165v10, CMS131v10, CMS122v10, CMS125v10, CMS130v10
    """

    VALUE_SET_NAME = "Acute Inpatient"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1083"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99221",  # Initial hospital care, per day, for the evaluation and management of a patient, which requires these 3 key components: A detailed or comprehensive history; A detailed or comprehensive examination; and Medical decision making that is straightforward or of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of low severity. Typically, 30 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99222",  # Initial hospital care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of moderate severity. Typically, 50 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99223",  # Initial hospital care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of high severity. Typically, 70 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99231",  # Subsequent hospital care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Medical decision making that is straightforward or of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is stable, recovering or improving. Typically, 15 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99232",  # Subsequent hospital care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is responding inadequately to therapy or has developed a minor complication. Typically, 25 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99233",  # Subsequent hospital care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A detailed interval history; A detailed examination; Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is unstable or has developed a significant complication or a significant new problem. Typically, 35 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99238",  # Hospital discharge day management; 30 minutes or less
        "99239",  # Hospital discharge day management; more than 30 minutes
        "99251",  # Inpatient consultation for a new or established patient, which requires these 3 key components: A problem focused history; A problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self limited or minor. Typically, 20 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99252",  # Inpatient consultation for a new or established patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low severity. Typically, 40 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99253",  # Inpatient consultation for a new or established patient, which requires these 3 key components: A detailed history; A detailed examination; and Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate severity. Typically, 55 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99254",  # Inpatient consultation for a new or established patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 80 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99255",  # Inpatient consultation for a new or established patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 110 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99291",  # Critical care, evaluation and management of the critically ill or critically injured patient; first 30-74 minutes
    }
    SNOMEDCT = {
        "417005",  # Hospital re-admission (procedure)
        "1505002",  # Hospital admission for isolation (procedure)
        "2252009",  # Hospital admission, urgent, 48 hours (procedure)
        "4563007",  # Hospital admission, transfer from other hospital or health care facility (procedure)
        "5161006",  # Specialty clinic admission (procedure)
        "8715000",  # Hospital admission, elective (procedure)
        "10378005",  # Hospital admission, emergency, from emergency room, accidental injury (procedure)
        "15584006",  # Hospital admission, elective, with partial pre-admission work-up (procedure)
        "18083007",  # Hospital admission, emergency, indirect (procedure)
        "19951005",  # Hospital admission, emergency, from emergency room, medical nature (procedure)
        "25986004",  # Hospital admission, under police custody (procedure)
        "32485007",  # Hospital admission (procedure)
        "45702004",  # Hospital admission, precertified by medical audit action (procedure)
        "47348005",  # Hospital admission, mother, for observation, delivered outside of hospital (procedure)
        "48183000",  # Hospital admission, special (procedure)
        "50699000",  # Hospital admission, short-term (procedure)
        "51032003",  # Hospital admission, donor for transplant organ (procedure)
        "51501005",  # Hospital admission, parent, for in-hospital child care (procedure)
        "52748007",  # Hospital admission, involuntary (procedure)
        "60059000",  # Hospital admission, infant, for observation, delivered outside of hospital (procedure)
        "63551005",  # Hospital admission, from remote area, by means of special transportation (procedure)
        "70755000",  # Hospital admission, by legal authority (commitment) (procedure)
        "71290004",  # Hospital admission, limited to designated procedures (procedure)
        "73607007",  # Hospital admission, emergency, from emergency room (procedure)
        "74857009",  # Hospital admission, short-term, 24 hours (procedure)
        "76193006",  # Routinely scheduled operation (procedure)
        "76464004",  # Hospital admission, for observation (procedure)
        "78680009",  # Hospital admission, emergency, direct (procedure)
        "81672003",  # Hospital admission, elective, without pre-admission work-up (procedure)
        "82942009",  # Hospital admission, blood donor (procedure)
        "112689000",  # Hospital admission, elective, with complete pre-admission work-up (procedure)
        "183450002",  # Admission to burn unit (procedure)
        "183452005",  # Emergency hospital admission (procedure)
        "183481006",  # Non-urgent hospital admission (procedure)
        "183487005",  # Non-urgent medical admission (procedure)
        "183488000",  # Non-urgent surgical admission (procedure)
        "183489008",  # Non-urgent psychiatric admission (procedure)
        "183491000",  # Non-urgent geriatric admission (procedure)
        "183492007",  # Non-urgent pediatric admission (procedure)
        "183493002",  # Non-urgent gynecological admission (procedure)
        "183494008",  # Non-urgent obstetric admission (procedure)
        "183495009",  # Non-urgent orthopedic admission (procedure)
        "183496005",  # Non-urgent ear, nose and throat admission (procedure)
        "183497001",  # Non-urgent trauma admission (procedure)
        "183498006",  # Non-urgent ophthalmological admission (procedure)
        "183499003",  # Non-urgent rheumatology admission (procedure)
        "183500007",  # Non-urgent dermatology admission (procedure)
        "183501006",  # Non-urgent neurology admission (procedure)
        "183502004",  # Non-urgent urology admission (procedure)
        "183503009",  # Non-urgent radiotherapy admission (procedure)
        "183504003",  # Non-urgent hematology admission (procedure)
        "183505002",  # Non-urgent plastic surgery admission (procedure)
        "183506001",  # Non-urgent diabetic admission (procedure)
        "183507005",  # Non-urgent respiratory admission (procedure)
        "183508000",  # Non-urgent psychogeriatric admission (procedure)
        "183509008",  # Non-urgent renal medicine admission (procedure)
        "183510003",  # Non-urgent neurosurgical admission (procedure)
        "183511004",  # Non-urgent cardiothoracic admission (procedure)
        "183512006",  # Non-urgent oral surgical admission (procedure)
        "235313004",  # Non-emergency appendectomy (procedure)
        "287927002",  # Dilatation and curettage: routine (procedure)
        "304566005",  # Admission for treatment (procedure)
        "305337004",  # Admission to community hospital (procedure)
        "305338009",  # Admission to general practice hospital (procedure)
        "305339001",  # Admission to private hospital (procedure)
        "305341000",  # Admission to tertiary referral hospital (procedure)
        "305342007",  # Admission to ward (procedure)
        "305350003",  # Admission to anesthetic department (procedure)
        "305354007",  # Admission to medical department (procedure)
        "305355008",  # Admission to clinical allergy department (procedure)
        "305356009",  # Admission to audiology department (procedure)
        "305357000",  # Admission to cardiology department (procedure)
        "305358005",  # Admission to chest medicine department (procedure)
        "305359002",  # Admission to thoracic medicine department (procedure)
        "305360007",  # Admission to respiratory medicine department (procedure)
        "305361006",  # Admission to clinical immunology department (procedure)
        "305362004",  # Admission to clinical neurophysiology department (procedure)
        "305363009",  # Admission to clinical pharmacology department (procedure)
        "305364003",  # Admission to clinical physiology department (procedure)
        "305365002",  # Admission to dermatology department (procedure)
        "305366001",  # Admission to endocrinology department (procedure)
        "305367005",  # Admission to gastroenterology department (procedure)
        "305368000",  # Admission to general medical department (procedure)
        "305369008",  # Admission to genetics department (procedure)
        "305370009",  # Admission to clinical genetics department (procedure)
        "305371008",  # Admission to clinical cytogenetics department (procedure)
        "305372001",  # Admission to clinical molecular genetics department (procedure)
        "305374000",  # Admission to genitourinary medicine department (procedure)
        "305375004",  # Admission to care of the elderly department (procedure)
        "305376003",  # Admission to infectious diseases department (procedure)
        "305377007",  # Admission to medical ophthalmology department (procedure)
        "305378002",  # Admission to nephrology department (procedure)
        "305379005",  # Admission to neurology department (procedure)
        "305380008",  # Admission to nuclear medicine department (procedure)
        "305382000",  # Admission to rehabilitation department (procedure)
        "305383005",  # Admission to rheumatology department (procedure)
        "305384004",  # Admission to obstetrics and gynecology department (procedure)
        "305385003",  # Admission to gynecology department (procedure)
        "305386002",  # Admission to obstetrics department (procedure)
        "305387006",  # Admission to pediatric department (procedure)
        "305388001",  # Admission to special care baby unit (procedure)
        "305389009",  # Admission to pediatric neurology department (procedure)
        "305390000",  # Admission to pediatric oncology department (procedure)
        "305391001",  # Admission to pain management department (procedure)
        "305392008",  # Admission to pathology department (procedure)
        "305393003",  # Admission to blood transfusion department (procedure)
        "305394009",  # Admission to chemical pathology department (procedure)
        "305395005",  # Admission to general pathology department (procedure)
        "305396006",  # Admission to hematology department (procedure)
        "305397002",  # Admission to medical microbiology department (procedure)
        "305399004",  # Admission to neuropathology department (procedure)
        "305400006",  # Admission to psychiatry department (procedure)
        "305401005",  # Admission to child and adolescent psychiatry department (procedure)
        "305402003",  # Admission to forensic psychiatry department (procedure)
        "305403008",  # Admission to psychogeriatric department (procedure)
        "305404002",  # Admission to mental handicap psychiatry department (procedure)
        "305405001",  # Admission to rehabilitation psychiatry department (procedure)
        "305406000",  # Admission to radiology department (procedure)
        "305407009",  # Admission to occupational health department (procedure)
        "305408004",  # Admission to surgical department (procedure)
        "305409007",  # Admission to breast surgery department (procedure)
        "305410002",  # Admission to cardiothoracic surgery department (procedure)
        "305411003",  # Admission to thoracic surgery department (procedure)
        "305412005",  # Admission to cardiac surgery department (procedure)
        "305413000",  # Admission to dental surgery department (procedure)
        "305414006",  # Admission to orthodontics department (procedure)
        "305415007",  # Admission to pediatric dentistry department (procedure)
        "305416008",  # Admission to restorative dentistry department (procedure)
        "305417004",  # Admission to ear, nose and throat department (procedure)
        "305418009",  # Admission to endocrine surgery department (procedure)
        "305419001",  # Admission to gastrointestinal surgery department (procedure)
        "305420007",  # Admission to general gastrointestinal surgery department (procedure)
        "305421006",  # Admission to upper gastrointestinal surgery department (procedure)
        "305422004",  # Admission to colorectal surgery department (procedure)
        "305423009",  # Admission to general surgical department (procedure)
        "305424003",  # Admission to hepatobiliary surgical department (procedure)
        "305425002",  # Admission to neurosurgical department (procedure)
        "305426001",  # Admission to ophthalmology department (procedure)
        "305427005",  # Admission to oral surgery department (procedure)
        "305428000",  # Admission to orthopedic department (procedure)
        "305429008",  # Admission to pancreatic surgery department (procedure)
        "305430003",  # Admission to pediatric surgical department (procedure)
        "305431004",  # Admission to plastic surgery department (procedure)
        "305432006",  # Admission to surgical transplant department (procedure)
        "305433001",  # Admission to trauma surgery department (procedure)
        "305434007",  # Admission to urology department (procedure)
        "305435008",  # Admission to vascular surgery department (procedure)
        "306732000",  # Admission to general dental surgery department (procedure)
        "306803007",  # Admission to stroke unit (procedure)
        "306967009",  # Admission to hand surgery department (procedure)
        "308251003",  # Admission to clinical oncology department (procedure)
        "308252005",  # Admission to radiotherapy department (procedure)
        "308253000",  # Admission to diabetic department (procedure)
        "310361003",  # Non-urgent cardiological admission (procedure)
        "373113001",  # Routine procedure (procedure)
        "397769005",  # Unexpected admission to high dependency unit (procedure)
        "398162007",  # Admission to high dependency unit (procedure)
        "405614004",  # Unexpected hospital admission (procedure)
        "699124006",  # Admission to substance misuse detoxification center (procedure)
        "3241000175106",  # Hospital admission from non-health care facility (procedure)
        "432621000124105",  # Hospital admission from dialysis facility (procedure)
        "442281000124108",  # Emergency hospital admission from observation unit (procedure)
        "447941000124106",  # Hospital admission of newborn (procedure)
        "448421000124105",  # Hospital admission, transfer from physician office (procedure)
        "448431000124108",  # Hospital admission, transfer from assisted living facility (procedure)
        "448441000124103",  # Hospital admission, transfer from intermediate care facility (procedure)
        "448851000124103",  # Hospital admission from observation unit (procedure)
    }


class AnnualWellnessVisit(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for annual wellness visits.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for a Medicare annual wellness visit.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS134v10, CMS127v10, CMS138v10, CMS165v10, CMS128v10, CMS122v10, CMS131v10, CMS347v5, CMS156v10, CMS147v11, CMS139v10, CMS125v10, CMS130v10
    """

    VALUE_SET_NAME = "Annual Wellness Visit"
    OID = "2.16.840.1.113883.3.526.3.1240"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    HCPCSLEVELII = {
        "G0438",  # Annual wellness visit; includes a personalized prevention plan of service (pps), initial visit
        "G0439",  # Annual wellness visit, includes a personalized prevention plan of service (pps), subsequent visit
    }
    SNOMEDCT = {
        "444971000124105",  # Annual wellness visit (procedure)
        "456201000124103",  # Medicare Annual Wellness Visit (procedure)
    }


class CareServicesInLongTermResidentialFacility(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for patients living in assisted living, domiciliary care or rest homes.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for services provided to new and established patients living in assisted living, domiciliary care or rest home who have had an interaction with a member of their medical team.

    **Exclusion Criteria:** Excludes concepts that represent an encounter for settings other than assisted living, domiciliary care, or rest homes.

    ** Used in:** CMS135v10, CMS147v11, CMS134v10, CMS127v10, CMS165v10, CMS143v10, CMS131v10, CMS122v10, CMS149v10, CMS144v10, CMS156v10, CMS159v10, CMS142v10, CMS139v10, CMS125v10, CMS130v10, CMS145v10
    """

    VALUE_SET_NAME = "Care Services in Long-Term Residential Facility"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1014"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99324",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A problem focused history; A problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low severity. Typically, 20 minutes are spent with the patient and/or family or caregiver.
        "99325",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate severity. Typically, 30 minutes are spent with the patient and/or family or caregiver.
        "99326",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A detailed history; A detailed examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 45 minutes are spent with the patient and/or family or caregiver.
        "99327",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of high severity. Typically, 60 minutes are spent with the patient and/or family or caregiver.
        "99328",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is unstable or has developed a significant new problem requiring immediate physician attention. Typically, 75 minutes are spent with the patient and/or family or caregiver.
        "99334",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self-limited or minor. Typically, 15 minutes are spent with the patient and/or family or caregiver.
        "99335",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low to moderate severity. Typically, 25 minutes are spent with the patient and/or family or caregiver.
        "99336",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A detailed interval history; A detailed examination; Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 40 minutes are spent with the patient and/or family or caregiver.
        "99337",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A comprehensive interval history; A comprehensive examination; Medical decision making of moderate to high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. The patient may be unstable or may have developed a significant new problem requiring immediate physician attention. Typically, 60 minutes are spent with the patient and/or family or caregiver.
    }
    SNOMEDCT = {
        "209099002",  # History and physical examination with management of domiciliary or rest home patient (procedure)
        "210098006",  # Domiciliary or rest home patient evaluation and management (procedure)
    }


class EmergencyDepartmentVisit(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters in the emergency department.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for care provided to new and established patients in the emergency department.

    **Exclusion Criteria:** Excludes concepts that represent an encounter not representative of ED visits, including critical care and observation services.

    ** Used in:** CMS134v10, CMS137v10, CMS165v10, CMS146v10, CMS131v10, CMS122v10, CMS154v10, CMS125v10, CMS130v10, CMS161v10
    """

    VALUE_SET_NAME = "Emergency Department Visit"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1010"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99281",  # Emergency department visit for the evaluation and management of a patient, which requires these 3 key components: A problem focused history; A problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self limited or minor.
        "99282",  # Emergency department visit for the evaluation and management of a patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low to moderate severity.
        "99283",  # Emergency department visit for the evaluation and management of a patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate severity.
        "99284",  # Emergency department visit for the evaluation and management of a patient, which requires these 3 key components: A detailed history; A detailed examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of high severity, and require urgent evaluation by the physician, or other qualified health care professionals but do not pose an immediate significant threat to life or physiologic function.
        "99285",  # Emergency department visit for the evaluation and management of a patient, which requires these 3 key components within the constraints imposed by the urgency of the patient's clinical condition and/or mental status: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of high severity and pose an immediate significant threat to life or physiologic function.
    }
    SNOMEDCT = {
        "4525004",  # Emergency department patient visit (procedure)
    }


class FrailtyEncounter(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for nursing care services provided to frail patients.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for nursing care and home care services provided to frail patients.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS134v10, CMS165v10, CMS131v10, CMS122v10, CMS125v10, CMS130v10
    """

    VALUE_SET_NAME = "Frailty Encounter"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1088"
    DEFINITION_VERSION = "20210224"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

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


class NonacuteInpatient(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for nonacute inpatient visits.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for comprehensive history, evaluation, and management of a patient in a nonacute inpatient setting.

    **Exclusion Criteria:** Excludes concepts that represent an encounter other than nonacute inpatient visits.

    ** Used in:** CMS134v10, CMS165v10, CMS131v10, CMS122v10, CMS125v10, CMS130v10
    """

    VALUE_SET_NAME = "Nonacute Inpatient"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1084"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99304",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires these 3 key components: A detailed or comprehensive history; A detailed or comprehensive examination; and Medical decision making that is straightforward or of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of low severity. Typically, 25 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99305",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of moderate severity. Typically, 35 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99306",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of high severity. Typically, 45 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99307",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is stable, recovering, or improving. Typically, 10 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99308",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is responding inadequately to therapy or has developed a minor complication. Typically, 15 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99309",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A detailed interval history; A detailed examination; Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient has developed a significant complication or a significant new problem. Typically, 25 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99310",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A comprehensive interval history; A comprehensive examination; Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. The patient may be unstable or may have developed a significant new problem requiring immediate physician attention. Typically, 35 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99315",  # Nursing facility discharge day management; 30 minutes or less
        "99316",  # Nursing facility discharge day management; more than 30 minutes
        "99318",  # Evaluation and management of a patient involving an annual nursing facility assessment, which requires these 3 key components: A detailed interval history; A comprehensive examination; and Medical decision making that is of low to moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is stable, recovering, or improving. Typically, 30 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99324",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A problem focused history; A problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low severity. Typically, 20 minutes are spent with the patient and/or family or caregiver.
        "99325",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate severity. Typically, 30 minutes are spent with the patient and/or family or caregiver.
        "99326",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A detailed history; A detailed examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 45 minutes are spent with the patient and/or family or caregiver.
        "99327",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of high severity. Typically, 60 minutes are spent with the patient and/or family or caregiver.
        "99328",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is unstable or has developed a significant new problem requiring immediate physician attention. Typically, 75 minutes are spent with the patient and/or family or caregiver.
        "99334",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self-limited or minor. Typically, 15 minutes are spent with the patient and/or family or caregiver.
        "99335",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low to moderate severity. Typically, 25 minutes are spent with the patient and/or family or caregiver.
        "99336",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A detailed interval history; A detailed examination; Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 40 minutes are spent with the patient and/or family or caregiver.
        "99337",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A comprehensive interval history; A comprehensive examination; Medical decision making of moderate to high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. The patient may be unstable or may have developed a significant new problem requiring immediate physician attention. Typically, 60 minutes are spent with the patient and/or family or caregiver.
    }
    SNOMEDCT = {
        "36723004",  # Hospital admission, pre-nursing home placement (procedure)
        "112690009",  # Hospital admission, boarder, for social reasons (procedure)
        "183430001",  # Holiday relief admission (procedure)
        "183921001",  # Admission to hospice for respite (procedure)
        "304567001",  # Admission for long-term care (procedure)
        "304568006",  # Admission for respite care (procedure)
        "305336008",  # Admission to hospice (procedure)
        "305340004",  # Admission to long stay hospital (procedure)
        "305381007",  # Admission to palliative care department (procedure)
        "306804001",  # Admission to young disabled unit (procedure)
        "449411000124106",  # Admission to skilled nursing facility (procedure)
        "449421000124103",  # Admission to nursing home (procedure)
        "449431000124100",  # Admission to inpatient rehabilitation facility (procedure)
    }


class NursingFacilityVisit(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters in a nursing facility.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter specific to a nursing facility, including skilled, intermediate and long term care facilities.

    **Exclusion Criteria:** Excludes concepts that represent an encounter other than a nursing facility visits.

    ** Used in:** CMS135v10, CMS147v11, CMS134v10, CMS127v10, CMS165v10, CMS143v10, CMS128v10, CMS122v10, CMS131v10, CMS149v10, CMS144v10, CMS156v10, CMS142v10, CMS139v10, CMS125v10, CMS130v10, CMS145v10
    """

    VALUE_SET_NAME = "Nursing Facility Visit"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1012"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99304",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires these 3 key components: A detailed or comprehensive history; A detailed or comprehensive examination; and Medical decision making that is straightforward or of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of low severity. Typically, 25 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99305",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of moderate severity. Typically, 35 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99306",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of high severity. Typically, 45 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99307",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is stable, recovering, or improving. Typically, 10 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99308",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is responding inadequately to therapy or has developed a minor complication. Typically, 15 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99309",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A detailed interval history; A detailed examination; Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient has developed a significant complication or a significant new problem. Typically, 25 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99310",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A comprehensive interval history; A comprehensive examination; Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. The patient may be unstable or may have developed a significant new problem requiring immediate physician attention. Typically, 35 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99315",  # Nursing facility discharge day management; 30 minutes or less
        "99316",  # Nursing facility discharge day management; more than 30 minutes
        "99318",  # Evaluation and management of a patient involving an annual nursing facility assessment, which requires these 3 key components: A detailed interval history; A comprehensive examination; and Medical decision making that is of low to moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is stable, recovering, or improving. Typically, 30 minutes are spent at the bedside and on the patient's facility floor or unit.
    }
    SNOMEDCT = {
        "18170008",  # Subsequent nursing facility visit (procedure)
        "207195004",  # History and physical examination with evaluation and management of nursing facility patient (procedure)
    }


class Observation(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for observation stays.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for comprehensive history, evaluation, and management of a patient in an observation care setting.

    **Exclusion Criteria:** Excludes concepts that represent an encounter not representative of observation care, including critical care and ED visits.

    ** Used in:** CMS134v10, CMS165v10, CMS146v10, CMS131v10, CMS122v10, CMS154v10, CMS125v10, CMS130v10
    """

    VALUE_SET_NAME = "Observation"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1086"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99217",  # Observation care discharge day management (This code is to be utilized to report all services provided to a patient on discharge from outpatient hospital "observation status" if the discharge is on other than the initial date of "observation status." To report services to a patient designated as "observation status" or "inpatient status" and discharged on the same date, use the codes for Observation or Inpatient Care Services [including Admission and Discharge Services, 99234-99236 as appropriate.])
        "99218",  # Initial observation care, per day, for the evaluation and management of a patient which requires these 3 key components: A detailed or comprehensive history; A detailed or comprehensive examination; and Medical decision making that is straightforward or of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission to outpatient hospital "observation status" are of low severity. Typically, 30 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99219",  # Initial observation care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission to outpatient hospital "observation status" are of moderate severity. Typically, 50 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99220",  # Initial observation care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission to outpatient hospital "observation status" are of high severity. Typically, 70 minutes are spent at the bedside and on the patient's hospital floor or unit.
    }


class Outpatient(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for outpatient visits.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for comprehensive history, evaluation, and management of a patient in an outpatient setting.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS134v10, CMS165v10, CMS131v10, CMS122v10, CMS125v10, CMS130v10
    """

    VALUE_SET_NAME = "Outpatient"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1087"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99201",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires these 3 key components: A problem focused history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self limited or minor. Typically, 10 minutes are spent face-to-face with the patient and/or family.
        "99202",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using time for code selection, 15-29 minutes of total time is spent on the date of the encounter.
        "99203",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using time for code selection, 30-44 minutes of total time is spent on the date of the encounter.
        "99204",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using time for code selection, 45-59 minutes of total time is spent on the date of the encounter.
        "99205",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using time for code selection, 60-74 minutes of total time is spent on the date of the encounter.
        "99211",  # Office or other outpatient visit for the evaluation and management of an established patient, that may not require the presence of a physician or other qualified health care professional. Usually, the presenting problem(s) are minimal.
        "99212",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using time for code selection, 10-19 minutes of total time is spent on the date of the encounter.
        "99213",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using time for code selection, 20-29 minutes of total time is spent on the date of the encounter.
        "99214",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using time for code selection, 30-39 minutes of total time is spent on the date of the encounter.
        "99215",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using time for code selection, 40-54 minutes of total time is spent on the date of the encounter.
        "99241",  # Office consultation for a new or established patient, which requires these 3 key components: A problem focused history; A problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self limited or minor. Typically, 15 minutes are spent face-to-face with the patient and/or family.
        "99242",  # Office consultation for a new or established patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low severity. Typically, 30 minutes are spent face-to-face with the patient and/or family.
        "99243",  # Office consultation for a new or established patient, which requires these 3 key components: A detailed history; A detailed examination; and Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate severity. Typically, 40 minutes are spent face-to-face with the patient and/or family.
        "99244",  # Office consultation for a new or established patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 60 minutes are spent face-to-face with the patient and/or family.
        "99245",  # Office consultation for a new or established patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 80 minutes are spent face-to-face with the patient and/or family.
        "99341",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: A problem focused history; A problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low severity. Typically, 20 minutes are spent face-to-face with the patient and/or family.
        "99342",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate severity. Typically, 30 minutes are spent face-to-face with the patient and/or family.
        "99343",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: A detailed history; A detailed examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 45 minutes are spent face-to-face with the patient and/or family.
        "99344",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of high severity. Typically, 60 minutes are spent face-to-face with the patient and/or family.
        "99345",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is unstable or has developed a significant new problem requiring immediate physician attention. Typically, 75 minutes are spent face-to-face with the patient and/or family.
        "99347",  # Home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self limited or minor. Typically, 15 minutes are spent face-to-face with the patient and/or family.
        "99348",  # Home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low to moderate severity. Typically, 25 minutes are spent face-to-face with the patient and/or family.
        "99349",  # Home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A detailed interval history; A detailed examination; Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are moderate to high severity. Typically, 40 minutes are spent face-to-face with the patient and/or family.
        "99350",  # Home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A comprehensive interval history; A comprehensive examination; Medical decision making of moderate to high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. The patient may be unstable or may have developed a significant new problem requiring immediate physician attention. Typically, 60 minutes are spent face-to-face with the patient and/or family.
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
        "99483",  # Assessment of and care planning for a patient with cognitive impairment, requiring an independent historian, in the office or other outpatient, home or domiciliary or rest home, with all of the following required elements: Cognition-focused evaluation including a pertinent history and examination; Medical decision making of moderate or high complexity; Functional assessment (eg, basic and instrumental activities of daily living), including decision-making capacity; Use of standardized instruments for staging of dementia (eg, functional assessment staging test [FAST], clinical dementia rating [CDR]); Medication reconciliation and review for high-risk medications; Evaluation for neuropsychiatric and behavioral symptoms, including depression, including use of standardized screening instrument(s); Evaluation of safety (eg, home), including motor vehicle operation; Identification of caregiver(s), caregiver knowledge, caregiver needs, social supports, and the willingness of caregiver to take on caregiving tasks; Development, updating or revision, or review of an Advance Care Plan; Creation of a written care plan, including initial plans to address any neuropsychiatric symptoms, neuro-cognitive symptoms, functional limitations, and referral to community resources as needed (eg, rehabilitation services, adult day programs, support groups) shared with the patient and/or caregiver with initial education and support. Typically, 50 minutes are spent face-to-face with the patient and/or family or caregiver.
    }
    HCPCSLEVELII = {
        "G0402",  # Initial preventive physical examination; face-to-face visit, services limited to new beneficiary during the first 12 months of medicare enrollment
        "G0438",  # Annual wellness visit; includes a personalized prevention plan of service (pps), initial visit
        "G0439",  # Annual wellness visit, includes a personalized prevention plan of service (pps), subsequent visit
        "G0463",  # Hospital outpatient clinic visit for assessment and management of a patient
        "T1015",  # Clinic visit/encounter, all-inclusive
    }
    SNOMEDCT = {
        "30346009",  # Evaluation and management of established outpatient in office or other outpatient facility (procedure)
        "37894004",  # Evaluation and management of new outpatient in office or other outpatient facility (procedure)
        "77406008",  # Confirmatory medical consultation (procedure)
        "84251009",  # Comprehensive consultation (procedure)
        "185463005",  # Visit out of hours (procedure)
        "185464004",  # Out of hours visit - not night visit (procedure)
        "185465003",  # Weekend visit (procedure)
        "281036007",  # Follow-up consultation (procedure)
        "439740005",  # Postoperative follow-up visit (procedure)
        "3391000175108",  # Office visit for pediatric care and assessment (procedure)
        "444971000124105",  # Annual wellness visit (procedure)
    }


class PalliativeCareEncounter(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for palliative care services.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for admission and management for palliative care services.

    **Exclusion Criteria:** Excludes concepts that represent encounters for hospice and a referral to palliative care.

    ** Used in:** CMS134v10, CMS165v10, CMS131v10, CMS122v10, CMS124v10, CMS156v10, CMS159v10, CMS125v10, CMS130v10
    """

    VALUE_SET_NAME = "Palliative Care Encounter"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1090"
    DEFINITION_VERSION = "20210224"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    HCPCSLEVELII = {
        "G9054",  # Oncology; primary focus of visit; supervising, coordinating or managing care of patient with terminal cancer or for whom other medical illness prevents further cancer treatment; includes symptom management, end-of-life care planning, management of palliative therapies (for use in a medicare-approved demonstration project)
        "M1017",  # Patient admitted to palliative care services
    }
    SNOMEDCT = {
        "305284002",  # Admission by palliative care physician (procedure)
        "305381007",  # Admission to palliative care department (procedure)
        "713281006",  # Consultation for palliative care (procedure)
        "4901000124101",  # Palliative care education (procedure)
    }
    ICD10CM = {
        "Z515",  # Encounter for palliative care
    }


class PreventiveCareServicesEstablishedOfficeVisit_18AndUp(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for preventive care.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for comprehensive preventive medicine reevaluation and management of an individual 18 years of age or over.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS249v4, CMS349v4, CMS134v10, CMS165v10, CMS146v10, CMS124v10, CMS50v10, CMS139v10, CMS154v10, CMS74v11, CMS138v10, CMS128v10, CMS122v10, CMS153v10, CMS130v10, CMS127v10, CMS131v10, CMS347v5, CMS156v10, CMS147v11, CMS125v10
    """

    VALUE_SET_NAME = "Preventive Care Services - Established Office Visit, 18 and Up"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1025"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99395",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 18-39 years
        "99396",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 40-64 years
        "99397",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 65 years and older
    }


class PreventiveCareServicesInitialOfficeVisit_18AndUp(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for  preventive care.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an  encounter for comprehensive preventive medicine reevaluation and management of a patient 18 years or over.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS249v4, CMS349v4, CMS134v10, CMS165v10, CMS146v10, CMS124v10, CMS50v10, CMS139v10, CMS154v10, CMS74v11, CMS138v10, CMS128v10, CMS122v10, CMS153v10, CMS130v10, CMS127v10, CMS131v10, CMS347v5, CMS156v10, CMS147v11, CMS125v10
    """

    VALUE_SET_NAME = "Preventive Care Services-Initial Office Visit, 18 and Up"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1023"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99385",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 18-39 years
        "99386",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 40-64 years
        "99387",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 65 years and older
    }


class DischargeServicesNursingFacility(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for discharges from a nursing facility.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for nursing facility discharge.

    **Exclusion Criteria:** Excludes concepts that represent discharges from settings other than a nursing facility.

    ** Used in:** CMS147v11, CMS139v10, CMS127v10, CMS156v10
    """

    VALUE_SET_NAME = "Discharge Services - Nursing Facility"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1013"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99315",  # Nursing facility discharge day management; 30 minutes or less
        "99316",  # Nursing facility discharge day management; more than 30 minutes
    }


class PsychVisitDiagnosticEvaluation(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for diagnostic psychiatric evaluations.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for psychiatric diagnostic evaluations.

    **Exclusion Criteria:** Excludes concepts that represent an encounter for group psychotherapy or family psychotherapy visits.

    ** Used in:** CMS138v10, CMS177v10, CMS136v11, CMS149v10, CMS128v10, CMS161v10
    """

    VALUE_SET_NAME = "Psych Visit - Diagnostic Evaluation"
    OID = "2.16.840.1.113883.3.526.3.1492"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90791",  # Psychiatric diagnostic evaluation
        "90792",  # Psychiatric diagnostic evaluation with medical services
    }
    SNOMEDCT = {
        "10197000",  # Psychiatric interview and evaluation (procedure)
        "68338001",  # Interactive medical psychiatric diagnostic interview (procedure)
        "79094001",  # Initial psychiatric interview with mental status and evaluation (procedure)
        "165172002",  # Diagnostic psychiatric interview (procedure)
    }


class PsychVisitPsychotherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for psychotherapy visits.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for individual psychotherapy services.

    **Exclusion Criteria:** Excludes concepts that represent an encounter for group psychotherapy or family psychotherapy visits.

    ** Used in:** CMS138v10, CMS177v10, CMS136v11, CMS149v10, CMS128v10, CMS161v10
    """

    VALUE_SET_NAME = "Psych Visit - Psychotherapy"
    OID = "2.16.840.1.113883.3.526.3.1496"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90832",  # Psychotherapy, 30 minutes with patient
        "90834",  # Psychotherapy, 45 minutes with patient
        "90837",  # Psychotherapy, 60 minutes with patient
    }
    SNOMEDCT = {
        "18512000",  # Individual psychotherapy (regime/therapy)
        "38678006",  # Client-centered psychotherapy (regime/therapy)
        "75516001",  # Psychotherapy (regime/therapy)
        "90102008",  # Social psychotherapy (regime/therapy)
        "183381005",  # General psychotherapy (regime/therapy)
        "183382003",  # Psychotherapy - behavioral (regime/therapy)
        "183383008",  # Psychotherapy - cognitive (regime/therapy)
        "302242004",  # Long-term psychodynamic psychotherapy (regime/therapy)
        "304820009",  # Developmental psychodynamic psychotherapy (regime/therapy)
        "304822001",  # Psychodynamic-interpersonal psychotherapy (regime/therapy)
        "314034001",  # Psychodynamic psychotherapy (regime/therapy)
        "401157001",  # Brief solution focused psychotherapy (regime/therapy)
        "443730003",  # Interpersonal psychotherapy (regime/therapy)
    }


class OphthalmologicalServices(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of encounters for ophthalmological visits.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for a visit with an eye care professional.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS138v10, CMS143v10, CMS131v10, CMS50v10, CMS142v10, CMS139v10
    """

    VALUE_SET_NAME = "Ophthalmological Services"
    OID = "2.16.840.1.113883.3.526.3.1285"
    DEFINITION_VERSION = "20210209"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "92002",  # Ophthalmological services: medical examination and evaluation with initiation of diagnostic and treatment program; intermediate, new patient
        "92004",  # Ophthalmological services: medical examination and evaluation with initiation of diagnostic and treatment program; comprehensive, new patient, 1 or more visits
        "92012",  # Ophthalmological services: medical examination and evaluation, with initiation or continuation of diagnostic and treatment program; intermediate, established patient
        "92014",  # Ophthalmological services: medical examination and evaluation, with initiation or continuation of diagnostic and treatment program; comprehensive, established patient, 1 or more visits
    }
    SNOMEDCT = {
        "36228007",  # Ophthalmic examination and evaluation (procedure)
        "66902005",  # Ophthalmic examination and evaluation, follow-up (procedure)
        "78831002",  # Comprehensive eye examination (procedure)
        "359960003",  # Ophthalmologic examination and evaluation under general anesthesia, limited (procedure)
    }


class EsrdMonthlyOutpatientServices(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for end-stage renal disease (ESRD) outpatient services.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for ESRD outpatients services.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS165v10, CMS134v10
    """

    VALUE_SET_NAME = "ESRD Monthly Outpatient Services"
    OID = "2.16.840.1.113883.3.464.1003.109.12.1014"
    DEFINITION_VERSION = "20170504"
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
        "90989",  # Dialysis training, patient, including helper where applicable, any mode, completed course
        "90993",  # Dialysis training, patient, including helper where applicable, any mode, course not completed, per training session
        "90997",  # Hemoperfusion (eg, with activated charcoal or resin)
        "90999",  # Unlisted dialysis procedure, inpatient or outpatient
        "99512",  # Home visit for hemodialysis
    }


class DischargeServicesHospitalInpatient(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for inpatient hospital discharge services.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for hospital discharge day management.

    **Exclusion Criteria:** Excludes concepts that represent encounters other than inpatient hospital discharge services.

    ** Used in:** CMS135v10, CMS144v10, CMS137v10
    """

    VALUE_SET_NAME = "Discharge Services - Hospital Inpatient"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1007"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99238",  # Hospital discharge day management; 30 minutes or less
        "99239",  # Hospital discharge day management; more than 30 minutes
    }


class OutpatientConsultation(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for outpatient interactions with a member of the medical care team.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for the comprehensive history, evaluation, and management of a patient presenting with minor to high severity problems.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS135v10, CMS147v11, CMS56v10, CMS177v10, CMS136v11, CMS143v10, CMS146v10, CMS149v10, CMS249v4, CMS347v5, CMS144v10, CMS66v10, CMS142v10, CMS154v10, CMS145v10, CMS161v10
    """

    VALUE_SET_NAME = "Outpatient Consultation"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1008"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99241",  # Office consultation for a new or established patient, which requires these 3 key components: A problem focused history; A problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self limited or minor. Typically, 15 minutes are spent face-to-face with the patient and/or family.
        "99242",  # Office consultation for a new or established patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low severity. Typically, 30 minutes are spent face-to-face with the patient and/or family.
        "99243",  # Office consultation for a new or established patient, which requires these 3 key components: A detailed history; A detailed examination; and Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate severity. Typically, 40 minutes are spent face-to-face with the patient and/or family.
        "99244",  # Office consultation for a new or established patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 60 minutes are spent face-to-face with the patient and/or family.
        "99245",  # Office consultation for a new or established patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 80 minutes are spent face-to-face with the patient and/or family.
    }
    SNOMEDCT = {
        "77406008",  # Confirmatory medical consultation (procedure)
        "281036007",  # Follow-up consultation (procedure)
    }


class PatientProviderInteraction(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters or communications.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter in an office or care setting, as well as interactions that occur via virtual methods, such as telephone calls, emails, and letters.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS135v10, CMS149v10, CMS144v10, CMS147v11, CMS145v10
    """

    VALUE_SET_NAME = "Patient Provider Interaction"
    OID = "2.16.840.1.113883.3.526.3.1012"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "87790002",  # Follow-up inpatient consultation visit (procedure)
        "90526000",  # Initial evaluation and management of healthy individual (procedure)
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
        "401271004",  # E-mail sent to patient (procedure)
        "406547006",  # Urgent follow-up (procedure)
        "438515009",  # E-mail encounter from caregiver (procedure)
        "438516005",  # E-mail encounter to caregiver (procedure)
        "445450000",  # Encounter by short message service text messaging (procedure)
        "448337001",  # Telemedicine consultation with patient (procedure)
    }


class BehavioralHealthFollowUpVisit(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for a behavioral health follow-up visit.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for education and training for patient self-management by a qualified health care professional.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS136v11
    """

    VALUE_SET_NAME = "Behavioral Health Follow-up Visit"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1054"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "98960",  # Education and training for patient self-management by a qualified, nonphysician health care professional using a standardized curriculum, face-to-face with the patient (could include caregiver/family) each 30 minutes; individual patient
        "98961",  # Education and training for patient self-management by a qualified, nonphysician health care professional using a standardized curriculum, face-to-face with the patient (could include caregiver/family) each 30 minutes; 2-4 patients
        "98962",  # Education and training for patient self-management by a qualified, nonphysician health care professional using a standardized curriculum, face-to-face with the patient (could include caregiver/family) each 30 minutes; 5-8 patients
        "99078",  # Physician or other qualified health care professional qualified by education, training, licensure/regulation (when applicable) educational services rendered to patients in a group setting (eg, prenatal, obesity, or diabetic instructions)
        "99510",  # Home visit for individual, family, or marriage counseling
    }


class HospitalObservationCareInitial(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for initial hospital observation care.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for initial observation care for the evaluation and management of a patient.

    **Exclusion Criteria:** Excludes concepts that represent an encounter not representative of observation care, including critical care and ED visits.

    ** Used in:** CMS136v11, CMS154v10, CMS146v10, CMS137v10
    """

    VALUE_SET_NAME = "Hospital Observation Care - Initial"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1002"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99218",  # Initial observation care, per day, for the evaluation and management of a patient which requires these 3 key components: A detailed or comprehensive history; A detailed or comprehensive examination; and Medical decision making that is straightforward or of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission to outpatient hospital "observation status" are of low severity. Typically, 30 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99219",  # Initial observation care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission to outpatient hospital "observation status" are of moderate severity. Typically, 50 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99220",  # Initial observation care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission to outpatient hospital "observation status" are of high severity. Typically, 70 minutes are spent at the bedside and on the patient's hospital floor or unit.
    }


class PreventiveCareServicesGroupCounseling(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for group counseling services.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for preventive medicine counseling and/or risk factor reduction intervention(s) in a group setting.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS155v10, CMS138v10, CMS136v11, CMS146v10, CMS147v11, CMS154v10
    """

    VALUE_SET_NAME = "Preventive Care Services - Group Counseling"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1027"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

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

    ** Used in:** CMS155v10, CMS138v10, CMS136v11, CMS146v10, CMS347v5, CMS147v11, CMS139v10, CMS154v10
    """

    VALUE_SET_NAME = "Preventive Care Services-Individual Counseling"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1026"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

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

    ** Used in:** CMS136v11
    """

    VALUE_SET_NAME = "Psychotherapy and Pharmacologic Management"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1055"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90845",  # Psychoanalysis
        "90847",  # Family psychotherapy (conjoint psychotherapy) (with patient present), 50 minutes
        "90849",  # Multiple-family group psychotherapy
        "90853",  # Group psychotherapy (other than of a multiple-family group)
        "90875",  # Individual psychophysiological therapy incorporating biofeedback training by any modality (face-to-face with the patient), with psychotherapy (eg, insight oriented, behavior modifying or supportive psychotherapy); 30 minutes
        "90876",  # Individual psychophysiological therapy incorporating biofeedback training by any modality (face-to-face with the patient), with psychotherapy (eg, insight oriented, behavior modifying or supportive psychotherapy); 45 minutes
    }


class TelehealthServices(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters delivered via telehealth.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for services delivered via telehealth, including telephone and online evaluation and management services.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS136v11, CMS177v10, CMS161v10
    """

    VALUE_SET_NAME = "Telehealth Services"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1031"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "98966",  # Telephone assessment and management service provided by a qualified nonphysician health care professional to an established patient, parent, or guardian not originating from a related assessment and management service provided within the previous 7 days nor leading to an assessment and management service or procedure within the next 24 hours or soonest available appointment; 5-10 minutes of medical discussion
        "98967",  # Telephone assessment and management service provided by a qualified nonphysician health care professional to an established patient, parent, or guardian not originating from a related assessment and management service provided within the previous 7 days nor leading to an assessment and management service or procedure within the next 24 hours or soonest available appointment; 11-20 minutes of medical discussion
        "98968",  # Telephone assessment and management service provided by a qualified nonphysician health care professional to an established patient, parent, or guardian not originating from a related assessment and management service provided within the previous 7 days nor leading to an assessment and management service or procedure within the next 24 hours or soonest available appointment; 21-30 minutes of medical discussion
        "99441",  # Telephone evaluation and management service by a physician or other qualified health care professional who may report evaluation and management services provided to an established patient, parent, or guardian not originating from a related E/M service provided within the previous 7 days nor leading to an E/M service or procedure within the next 24 hours or soonest available appointment; 5-10 minutes of medical discussion
        "99442",  # Telephone evaluation and management service by a physician or other qualified health care professional who may report evaluation and management services provided to an established patient, parent, or guardian not originating from a related E/M service provided within the previous 7 days nor leading to an E/M service or procedure within the next 24 hours or soonest available appointment; 11-20 minutes of medical discussion
        "99443",  # Telephone evaluation and management service by a physician or other qualified health care professional who may report evaluation and management services provided to an established patient, parent, or guardian not originating from a related E/M service provided within the previous 7 days nor leading to an E/M service or procedure within the next 24 hours or soonest available appointment; 21-30 minutes of medical discussion
    }


class DetoxificationVisit(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for detoxification visits.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for alcohol and drug detoxification.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS137v10
    """

    VALUE_SET_NAME = "Detoxification Visit"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1059"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "20093000",  # Alcohol rehabilitation and detoxification (regime/therapy)
        "23915005",  # Combined alcohol and drug rehabilitation and detoxification (regime/therapy)
        "56876005",  # Drug rehabilitation and detoxification (regime/therapy)
        "61480009",  # Drug detoxification (regime/therapy)
        "64297001",  # Detoxication psychiatric therapy for alcoholism (regime/therapy)
        "67516001",  # Detoxification therapy (regime/therapy)
        "87106005",  # Combined alcohol and drug detoxification (regime/therapy)
        "182969009",  # Dependent drug detoxification (regime/therapy)
        "414054004",  # Drug dependence home detoxification (regime/therapy)
        "414056002",  # Drug dependence self detoxification (regime/therapy)
        "827094004",  # Alcohol detoxification (regime/therapy)
    }


class DischargeServicesHospitalInpatientSameDayDischarge(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for same day inpatient hospital discharge services.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for the evaluation and management of a patient that results in discharge on the same date as admission.

    **Exclusion Criteria:** Excludes concepts that represent encounters other than same day inpatient hospital discharge services.

    ** Used in:** CMS137v10
    """

    VALUE_SET_NAME = "Discharge Services - Hospital Inpatient Same Day Discharge"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1006"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99234",  # Observation or inpatient hospital care, for the evaluation and management of a patient including admission and discharge on the same date, which requires these 3 key components: A detailed or comprehensive history; A detailed or comprehensive examination; and Medical decision making that is straightforward or of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually the presenting problem(s) requiring admission are of low severity. Typically, 40 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99235",  # Observation or inpatient hospital care, for the evaluation and management of a patient including admission and discharge on the same date, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually the presenting problem(s) requiring admission are of moderate severity. Typically, 50 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99236",  # Observation or inpatient hospital care, for the evaluation and management of a patient including admission and discharge on the same date, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually the presenting problem(s) requiring admission are of high severity. Typically, 55 minutes are spent at the bedside and on the patient's hospital floor or unit.
    }


class HospitalInpatientVisitInitial(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for inpatient hospital care.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for initial hospital care for the evaluation and management of a patient.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS137v10
    """

    VALUE_SET_NAME = "Hospital Inpatient Visit - Initial"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1004"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99221",  # Initial hospital care, per day, for the evaluation and management of a patient, which requires these 3 key components: A detailed or comprehensive history; A detailed or comprehensive examination; and Medical decision making that is straightforward or of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of low severity. Typically, 30 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99222",  # Initial hospital care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of moderate severity. Typically, 50 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99223",  # Initial hospital care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of high severity. Typically, 70 minutes are spent at the bedside and on the patient's hospital floor or unit.
    }


class OccupationalTherapyEvaluation(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for assessment, management, and evaluation for occupational therapy.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for assessment, management, and evaluation for occupational therapy.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS138v10, CMS149v10
    """

    VALUE_SET_NAME = "Occupational Therapy Evaluation"
    OID = "2.16.840.1.113883.3.526.3.1011"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "97165",  # Occupational therapy evaluation, low complexity, requiring these components: An occupational profile and medical and therapy history, which includes a brief history including review of medical and/or therapy records relating to the presenting problem; An assessment(s) that identifies 1-3 performance deficits (ie, relating to physical, cognitive, or psychosocial skills) that result in activity limitations and/or participation restrictions; and Clinical decision making of low complexity, which includes an analysis of the occupational profile, analysis of data from problem-focused assessment(s), and consideration of a limited number of treatment options. Patient presents with no comorbidities that affect occupational performance. Modification of tasks or assistance (eg, physical or verbal) with assessment(s) is not necessary to enable completion of evaluation component. Typically, 30 minutes are spent face-to-face with the patient and/or family.
        "97166",  # Occupational therapy evaluation, moderate complexity, requiring these components: An occupational profile and medical and therapy history, which includes an expanded review of medical and/or therapy records and additional review of physical, cognitive, or psychosocial history related to current functional performance; An assessment(s) that identifies 3-5 performance deficits (ie, relating to physical, cognitive, or psychosocial skills) that result in activity limitations and/or participation restrictions; and Clinical decision making of moderate analytic complexity, which includes an analysis of the occupational profile, analysis of data from detailed assessment(s), and consideration of several treatment options. Patient may present with comorbidities that affect occupational performance. Minimal to moderate modification of tasks or assistance (eg, physical or verbal) with assessment(s) is necessary to enable patient to complete evaluation component. Typically, 45 minutes are spent face-to-face with the patient and/or family.
        "97167",  # Occupational therapy evaluation, high complexity, requiring these components: An occupational profile and medical and therapy history, which includes review of medical and/or therapy records and extensive additional review of physical, cognitive, or psychosocial history related to current functional performance; An assessment(s) that identifies 5 or more performance deficits (ie, relating to physical, cognitive, or psychosocial skills) that result in activity limitations and/or participation restrictions; and Clinical decision making of high analytic complexity, which includes an analysis of the patient profile, analysis of data from comprehensive assessment(s), and consideration of multiple treatment options. Patient presents with comorbidities that affect occupational performance. Significant modification of tasks or assistance (eg, physical or verbal) with assessment(s) is necessary to enable patient to complete evaluation component. Typically, 60 minutes are spent face-to-face with the patient and/or family.
        "97168",  # Re-evaluation of occupational therapy established plan of care, requiring these components: An assessment of changes in patient functional or medical status with revised plan of care; An update to the initial occupational profile to reflect changes in condition or environment that affect future interventions and/or goals; and A revised plan of care. A formal reevaluation is performed when there is a documented change in functional status or a significant change to the plan of care is required. Typically, 30 minutes are spent face-to-face with the patient and/or family.
    }
    SNOMEDCT = {
        "410155007",  # Occupational therapy assessment (procedure)
        "410157004",  # Occupational therapy management (procedure)
    }


class PhysicalTherapyEvaluation(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for a physical therapy evaluation.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for a physical therapy evaluation.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS2v11, CMS138v10
    """

    VALUE_SET_NAME = "Physical Therapy Evaluation"
    OID = "2.16.840.1.113883.3.526.3.1022"
    DEFINITION_VERSION = "20200306"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "97161",  # Physical therapy evaluation: low complexity, requiring these components: A history with no personal factors and/or comorbidities that impact the plan of care; An examination of body system(s) using standardized tests and measures addressing 1-2 elements from any of the following: body structures and functions, activity limitations, and/or participation restrictions; A clinical presentation with stable and/or uncomplicated characteristics; and Clinical decision making of low complexity using standardized patient assessment instrument and/or measurable assessment of functional outcome. Typically, 20 minutes are spent face-to-face with the patient and/or family.
        "97162",  # Physical therapy evaluation: moderate complexity, requiring these components: A history of present problem with 1-2 personal factors and/or comorbidities that impact the plan of care; An examination of body systems using standardized tests and measures in addressing a total of 3 or more elements from any of the following: body structures and functions, activity limitations, and/or participation restrictions; An evolving clinical presentation with changing characteristics; and Clinical decision making of moderate complexity using standardized patient assessment instrument and/or measurable assessment of functional outcome. Typically, 30 minutes are spent face-to-face with the patient and/or family.
        "97163",  # Physical therapy evaluation: high complexity, requiring these components: A history of present problem with 3 or more personal factors and/or comorbidities that impact the plan of care; An examination of body systems using standardized tests and measures addressing a total of 4 or more elements from any of the following: body structures and functions, activity limitations, and/or participation restrictions; A clinical presentation with unstable and unpredictable characteristics; and Clinical decision making of high complexity using standardized patient assessment instrument and/or measurable assessment of functional outcome. Typically, 45 minutes are spent face-to-face with the patient and/or family.
    }
    SNOMEDCT = {
        "33849009",  # Diagnostic physical therapy procedure (regime/therapy)
    }


class PreventiveCareServicesOther(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for unlisted preventive medicine services.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for unlisted preventive medicine services.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS138v10, CMS146v10, CMS249v4, CMS347v5, CMS147v11, CMS154v10
    """

    VALUE_SET_NAME = "Preventive Care Services - Other"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1030"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99429",  # Unlisted preventive medicine service
    }


class Psychoanalysis(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for psychoanalysis.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for psychoanalysis.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS138v10, CMS177v10, CMS161v10
    """

    VALUE_SET_NAME = "Psychoanalysis"
    OID = "2.16.840.1.113883.3.526.3.1141"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

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

    ** Used in:** CMS138v10
    """

    VALUE_SET_NAME = "Speech and Hearing Evaluation"
    OID = "2.16.840.1.113883.3.526.3.1530"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

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

    ** Used in:** CMS139v10
    """

    VALUE_SET_NAME = "Audiology Visit"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1066"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "92540",  # Basic vestibular evaluation, includes spontaneous nystagmus test with eccentric gaze fixation nystagmus, with recording, positional nystagmus test, minimum of 4 positions, with recording, optokinetic nystagmus test, bidirectional foveal and peripheral stimulation, with recording, and oscillating tracking test, with recording
        "92541",  # Spontaneous nystagmus test, including gaze and fixation nystagmus, with recording
        "92542",  # Positional nystagmus test, minimum of 4 positions, with recording
        "92548",  # Computerized dynamic posturography sensory organization test (CDP-SOT), 6 conditions (ie, eyes open, eyes closed, visual sway, platform sway, eyes closed platform sway, platform and visual sway), including interpretation and report
    }


class MedicalDisabilityExam(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for work related or medical disability examinations.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for work related or medical disability examinations.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS154v10, CMS146v10
    """

    VALUE_SET_NAME = "Medical Disability Exam"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1073"
    DEFINITION_VERSION = "20210306"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99455",  # Work related or medical disability examination by the treating physician that includes: Completion of a medical history commensurate with the patient's condition; Performance of an examination commensurate with the patient's condition; Formulation of a diagnosis, assessment of capabilities and stability, and calculation of impairment; Development of future medical treatment plan; and Completion of necessary documentation/certificates and report.
        "99456",  # Work related or medical disability examination by other than the treating physician that includes: Completion of a medical history commensurate with the patient's condition; Performance of an examination commensurate with the patient's condition; Formulation of a diagnosis, assessment of capabilities and stability, and calculation of impairment; Development of future medical treatment plan; and Completion of necessary documentation/certificates and report.
    }


class EncounterInfluenza(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters where an influenza vaccine may be administered.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter  where an influenza vaccine may be administered.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS147v11
    """

    VALUE_SET_NAME = "Encounter-Influenza"
    OID = "2.16.840.1.113883.3.526.3.1252"
    DEFINITION_VERSION = "20180407"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99201",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires these 3 key components: A problem focused history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self limited or minor. Typically, 10 minutes are spent face-to-face with the patient and/or family.
        "99202",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using time for code selection, 15-29 minutes of total time is spent on the date of the encounter.
        "99203",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using time for code selection, 30-44 minutes of total time is spent on the date of the encounter.
        "99204",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using time for code selection, 45-59 minutes of total time is spent on the date of the encounter.
        "99205",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using time for code selection, 60-74 minutes of total time is spent on the date of the encounter.
        "99212",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using time for code selection, 10-19 minutes of total time is spent on the date of the encounter.
        "99213",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using time for code selection, 20-29 minutes of total time is spent on the date of the encounter.
        "99214",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using time for code selection, 30-39 minutes of total time is spent on the date of the encounter.
        "99215",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using time for code selection, 40-54 minutes of total time is spent on the date of the encounter.
        "99241",  # Office consultation for a new or established patient, which requires these 3 key components: A problem focused history; A problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self limited or minor. Typically, 15 minutes are spent face-to-face with the patient and/or family.
        "99242",  # Office consultation for a new or established patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low severity. Typically, 30 minutes are spent face-to-face with the patient and/or family.
        "99243",  # Office consultation for a new or established patient, which requires these 3 key components: A detailed history; A detailed examination; and Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate severity. Typically, 40 minutes are spent face-to-face with the patient and/or family.
        "99244",  # Office consultation for a new or established patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 60 minutes are spent face-to-face with the patient and/or family.
        "99245",  # Office consultation for a new or established patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 80 minutes are spent face-to-face with the patient and/or family.
        "99304",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires these 3 key components: A detailed or comprehensive history; A detailed or comprehensive examination; and Medical decision making that is straightforward or of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of low severity. Typically, 25 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99305",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of moderate severity. Typically, 35 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99306",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of high severity. Typically, 45 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99307",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is stable, recovering, or improving. Typically, 10 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99308",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is responding inadequately to therapy or has developed a minor complication. Typically, 15 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99309",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A detailed interval history; A detailed examination; Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient has developed a significant complication or a significant new problem. Typically, 25 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99310",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A comprehensive interval history; A comprehensive examination; Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. The patient may be unstable or may have developed a significant new problem requiring immediate physician attention. Typically, 35 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99315",  # Nursing facility discharge day management; 30 minutes or less
        "99316",  # Nursing facility discharge day management; more than 30 minutes
        "99318",  # Evaluation and management of a patient involving an annual nursing facility assessment, which requires these 3 key components: A detailed interval history; A comprehensive examination; and Medical decision making that is of low to moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is stable, recovering, or improving. Typically, 30 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99324",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A problem focused history; A problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low severity. Typically, 20 minutes are spent with the patient and/or family or caregiver.
        "99325",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate severity. Typically, 30 minutes are spent with the patient and/or family or caregiver.
        "99326",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A detailed history; A detailed examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 45 minutes are spent with the patient and/or family or caregiver.
        "99327",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of high severity. Typically, 60 minutes are spent with the patient and/or family or caregiver.
        "99328",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is unstable or has developed a significant new problem requiring immediate physician attention. Typically, 75 minutes are spent with the patient and/or family or caregiver.
        "99334",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self-limited or minor. Typically, 15 minutes are spent with the patient and/or family or caregiver.
        "99335",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low to moderate severity. Typically, 25 minutes are spent with the patient and/or family or caregiver.
        "99336",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A detailed interval history; A detailed examination; Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 40 minutes are spent with the patient and/or family or caregiver.
        "99337",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A comprehensive interval history; A comprehensive examination; Medical decision making of moderate to high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. The patient may be unstable or may have developed a significant new problem requiring immediate physician attention. Typically, 60 minutes are spent with the patient and/or family or caregiver.
        "99341",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: A problem focused history; A problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low severity. Typically, 20 minutes are spent face-to-face with the patient and/or family.
        "99342",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate severity. Typically, 30 minutes are spent face-to-face with the patient and/or family.
        "99343",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: A detailed history; A detailed examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 45 minutes are spent face-to-face with the patient and/or family.
        "99344",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of high severity. Typically, 60 minutes are spent face-to-face with the patient and/or family.
        "99345",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is unstable or has developed a significant new problem requiring immediate physician attention. Typically, 75 minutes are spent face-to-face with the patient and/or family.
        "99347",  # Home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self limited or minor. Typically, 15 minutes are spent face-to-face with the patient and/or family.
        "99348",  # Home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low to moderate severity. Typically, 25 minutes are spent face-to-face with the patient and/or family.
        "99349",  # Home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A detailed interval history; A detailed examination; Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are moderate to high severity. Typically, 40 minutes are spent face-to-face with the patient and/or family.
        "99350",  # Home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A comprehensive interval history; A comprehensive examination; Medical decision making of moderate to high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. The patient may be unstable or may have developed a significant new problem requiring immediate physician attention. Typically, 60 minutes are spent face-to-face with the patient and/or family.
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
    }
    HCPCSLEVELII = {
        "G0438",  # Annual wellness visit; includes a personalized prevention plan of service (pps), initial visit
        "G0439",  # Annual wellness visit, includes a personalized prevention plan of service (pps), subsequent visit
    }
    SNOMEDCT = {
        "18170008",  # Subsequent nursing facility visit (procedure)
        "30346009",  # Evaluation and management of established outpatient in office or other outpatient facility (procedure)
        "37894004",  # Evaluation and management of new outpatient in office or other outpatient facility (procedure)
        "77406008",  # Confirmatory medical consultation (procedure)
        "185460008",  # Home visit request by patient (procedure)
        "185462000",  # Home visit request by relative (procedure)
        "185463005",  # Visit out of hours (procedure)
        "185464004",  # Out of hours visit - not night visit (procedure)
        "185465003",  # Weekend visit (procedure)
        "185466002",  # Home visit for urgent condition (procedure)
        "185467006",  # Home visit for acute condition (procedure)
        "185468001",  # Home visit for chronic condition (procedure)
        "185470005",  # Home visit elderly assessment (procedure)
        "207195004",  # History and physical examination with evaluation and management of nursing facility patient (procedure)
        "209099002",  # History and physical examination with management of domiciliary or rest home patient (procedure)
        "210098006",  # Domiciliary or rest home patient evaluation and management (procedure)
        "225929007",  # Joint home visit (procedure)
        "281036007",  # Follow-up consultation (procedure)
        "315205008",  # Bank holiday home visit (procedure)
        "439708006",  # Home visit (procedure)
        "439740005",  # Postoperative follow-up visit (procedure)
        "698704008",  # Home visit for rheumatology service (procedure)
        "704126008",  # Home visit for anticoagulant drug monitoring (procedure)
        "3391000175108",  # Office visit for pediatric care and assessment (procedure)
    }


class BehavioralNeuropsychAssessment(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of encounters for neuropsychological assessments.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that describe an assessment for applicable neuropsychological assessments for behavioral health.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS149v10
    """

    VALUE_SET_NAME = "Behavioral/Neuropsych Assessment"
    OID = "2.16.840.1.113883.3.526.3.1023"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "96116",  # Neurobehavioral status exam (clinical assessment of thinking, reasoning and judgment, [eg, acquired knowledge, attention, language, memory, planning and problem solving, and visual spatial abilities]), by physician or other qualified health care professional, both face-to-face time with the patient and time interpreting test results and preparing the report; first hour
    }
    SNOMEDCT = {
        "307808008",  # Neuropsychological testing (procedure)
    }


class OphthalmologicServices(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for ophthalmological visits.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter with an eye care professional.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Ophthalmologic Services"
    OID = "2.16.840.1.113883.3.464.1003.101.11.1206"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "92002",  # Ophthalmological services: medical examination and evaluation with initiation of diagnostic and treatment program; intermediate, new patient
        "92004",  # Ophthalmological services: medical examination and evaluation with initiation of diagnostic and treatment program; comprehensive, new patient, 1 or more visits
        "92012",  # Ophthalmological services: medical examination and evaluation, with initiation or continuation of diagnostic and treatment program; intermediate, established patient
        "92014",  # Ophthalmological services: medical examination and evaluation, with initiation or continuation of diagnostic and treatment program; comprehensive, established patient, 1 or more visits
    }


class ContactOrOfficeVisit(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for office visits and outpatient contacts to evaluate for depression.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for outpatient contact and office visits in which a patient may be evaluated for depression.

    **Exclusion Criteria:** Excludes concepts that represent an encounter for inpatient visits, except for psychiatry and psychotherapy visits, which are not specific to setting.

    ** Used in:** CMS159v10
    """

    VALUE_SET_NAME = "Contact or Office Visit"
    OID = "2.16.840.1.113762.1.4.1080.5"
    DEFINITION_VERSION = "20210219"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90791",  # Psychiatric diagnostic evaluation
        "90792",  # Psychiatric diagnostic evaluation with medical services
        "90832",  # Psychotherapy, 30 minutes with patient
        "90833",  # Psychotherapy, 30 minutes with patient when performed with an evaluation and management service (List separately in addition to the code for primary procedure)
        "90834",  # Psychotherapy, 45 minutes with patient
        "90836",  # Psychotherapy, 45 minutes with patient when performed with an evaluation and management service (List separately in addition to the code for primary procedure)
        "90837",  # Psychotherapy, 60 minutes with patient
        "90838",  # Psychotherapy, 60 minutes with patient when performed with an evaluation and management service (List separately in addition to the code for primary procedure)
        "90839",  # Psychotherapy for crisis; first 60 minutes
        "90840",  # Psychotherapy for crisis; each additional 30 minutes (List separately in addition to code for primary service)
        "96156",  # Health behavior assessment, or re-assessment (ie, health-focused clinical interview, behavioral observations, clinical decision making)
        "96158",  # Health behavior intervention, individual, face-to-face; initial 30 minutes
        "96159",  # Health behavior intervention, individual, face-to-face; each additional 15 minutes (List separately in addition to code for primary service)
        "99201",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires these 3 key components: A problem focused history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self limited or minor. Typically, 10 minutes are spent face-to-face with the patient and/or family.
        "99202",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using time for code selection, 15-29 minutes of total time is spent on the date of the encounter.
        "99203",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using time for code selection, 30-44 minutes of total time is spent on the date of the encounter.
        "99204",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using time for code selection, 45-59 minutes of total time is spent on the date of the encounter.
        "99205",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using time for code selection, 60-74 minutes of total time is spent on the date of the encounter.
        "99211",  # Office or other outpatient visit for the evaluation and management of an established patient, that may not require the presence of a physician or other qualified health care professional. Usually, the presenting problem(s) are minimal.
        "99212",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using time for code selection, 10-19 minutes of total time is spent on the date of the encounter.
        "99213",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using time for code selection, 20-29 minutes of total time is spent on the date of the encounter.
        "99214",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using time for code selection, 30-39 minutes of total time is spent on the date of the encounter.
        "99215",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using time for code selection, 40-54 minutes of total time is spent on the date of the encounter.
        "99421",  # Online digital evaluation and management service, for an established patient, for up to 7 days, cumulative time during the 7 days; 5-10 minutes
        "99422",  # Online digital evaluation and management service, for an established patient, for up to 7 days, cumulative time during the 7 days; 11-20 minutes
        "99423",  # Online digital evaluation and management service, for an established patient, for up to 7 days, cumulative time during the 7 days; 21 or more minutes
        "99441",  # Telephone evaluation and management service by a physician or other qualified health care professional who may report evaluation and management services provided to an established patient, parent, or guardian not originating from a related E/M service provided within the previous 7 days nor leading to an E/M service or procedure within the next 24 hours or soonest available appointment; 5-10 minutes of medical discussion
        "99442",  # Telephone evaluation and management service by a physician or other qualified health care professional who may report evaluation and management services provided to an established patient, parent, or guardian not originating from a related E/M service provided within the previous 7 days nor leading to an E/M service or procedure within the next 24 hours or soonest available appointment; 11-20 minutes of medical discussion
        "99443",  # Telephone evaluation and management service by a physician or other qualified health care professional who may report evaluation and management services provided to an established patient, parent, or guardian not originating from a related E/M service provided within the previous 7 days nor leading to an E/M service or procedure within the next 24 hours or soonest available appointment; 21-30 minutes of medical discussion
    }
    HCPCSLEVELII = {
        "G0402",  # Initial preventive physical examination; face-to-face visit, services limited to new beneficiary during the first 12 months of medicare enrollment
        "G0438",  # Annual wellness visit; includes a personalized prevention plan of service (pps), initial visit
        "G0439",  # Annual wellness visit, includes a personalized prevention plan of service (pps), subsequent visit
    }


class GroupPsychotherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for group psychotherapy.

    **Data Element Scope:** This value set may use a model element related to Encounter or Procedure.

    **Inclusion Criteria:** Includes concepts that represent group psychotherapy.

    **Exclusion Criteria:** Excludes concepts that represent family psychotherapy or individual psychotherapy.

    ** Used in:** CMS177v10
    """

    VALUE_SET_NAME = "Group Psychotherapy"
    OID = "2.16.840.1.113883.3.526.3.1187"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "90853",  # Group psychotherapy (other than of a multiple-family group)
    }
    SNOMEDCT = {
        "1555005",  # Brief group psychotherapy (regime/therapy)
        "27591006",  # Group analytical psychotherapy (regime/therapy)
        "28868002",  # Interactive group medical psychotherapy (regime/therapy)
        "76168009",  # Group psychotherapy (regime/therapy)
    }


class PsychVisitFamilyPsychotherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for family psychotherapy.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent family psychotherapy.

    **Exclusion Criteria:** Excludes concepts for group psychotherapy or individual psychotherapy.

    ** Used in:** CMS177v10
    """

    VALUE_SET_NAME = "Psych Visit - Family Psychotherapy"
    OID = "2.16.840.1.113883.3.526.3.1018"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

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

    ** Used in:** CMS22v10
    """

    VALUE_SET_NAME = "Encounter to Screen for Blood Pressure"
    OID = "2.16.840.1.113883.3.600.1920"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CDT = {
        "D7111",  # extraction, coronal remnants - primary tooth
        "D7140",  # extraction, erupted tooth or exposed root (elevation and/or forceps removal)
        "D7210",  # extraction, erupted tooth requiring removal of bone and/or sectioning of tooth, and including elevation of mucoperiosteal flap if indicated
        "D7220",  # removal of impacted tooth - soft tissue
        "D7230",  # removal of impacted tooth - partially bony
        "D7240",  # removal of impacted tooth - completely bony
        "D7241",  # removal of impacted tooth - completely bony, with unusual surgical complications
        "D7250",  # removal of residual tooth roots (cutting procedure)
        "D7251",  # coronectomy - intentional partial tooth removal
    }
    CPT = {
        "90791",  # Psychiatric diagnostic evaluation
        "90792",  # Psychiatric diagnostic evaluation with medical services
        "92002",  # Ophthalmological services: medical examination and evaluation with initiation of diagnostic and treatment program; intermediate, new patient
        "92004",  # Ophthalmological services: medical examination and evaluation with initiation of diagnostic and treatment program; comprehensive, new patient, 1 or more visits
        "92012",  # Ophthalmological services: medical examination and evaluation, with initiation or continuation of diagnostic and treatment program; intermediate, established patient
        "92014",  # Ophthalmological services: medical examination and evaluation, with initiation or continuation of diagnostic and treatment program; comprehensive, established patient, 1 or more visits
        "99202",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using time for code selection, 15-29 minutes of total time is spent on the date of the encounter.
        "99203",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using time for code selection, 30-44 minutes of total time is spent on the date of the encounter.
        "99204",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using time for code selection, 45-59 minutes of total time is spent on the date of the encounter.
        "99205",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using time for code selection, 60-74 minutes of total time is spent on the date of the encounter.
        "99212",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using time for code selection, 10-19 minutes of total time is spent on the date of the encounter.
        "99213",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using time for code selection, 20-29 minutes of total time is spent on the date of the encounter.
        "99214",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using time for code selection, 30-39 minutes of total time is spent on the date of the encounter.
        "99215",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using time for code selection, 40-54 minutes of total time is spent on the date of the encounter.
        "99236",  # Observation or inpatient hospital care, for the evaluation and management of a patient including admission and discharge on the same date, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually the presenting problem(s) requiring admission are of high severity. Typically, 55 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99281",  # Emergency department visit for the evaluation and management of a patient, which requires these 3 key components: A problem focused history; A problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self limited or minor.
        "99282",  # Emergency department visit for the evaluation and management of a patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low to moderate severity.
        "99283",  # Emergency department visit for the evaluation and management of a patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate severity.
        "99284",  # Emergency department visit for the evaluation and management of a patient, which requires these 3 key components: A detailed history; A detailed examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of high severity, and require urgent evaluation by the physician, or other qualified health care professionals but do not pose an immediate significant threat to life or physiologic function.
        "99285",  # Emergency department visit for the evaluation and management of a patient, which requires these 3 key components within the constraints imposed by the urgency of the patient's clinical condition and/or mental status: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of high severity and pose an immediate significant threat to life or physiologic function.
        "99304",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires these 3 key components: A detailed or comprehensive history; A detailed or comprehensive examination; and Medical decision making that is straightforward or of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of low severity. Typically, 25 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99305",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of moderate severity. Typically, 35 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99306",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of high severity. Typically, 45 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99307",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is stable, recovering, or improving. Typically, 10 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99308",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is responding inadequately to therapy or has developed a minor complication. Typically, 15 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99309",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A detailed interval history; A detailed examination; Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient has developed a significant complication or a significant new problem. Typically, 25 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99310",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A comprehensive interval history; A comprehensive examination; Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. The patient may be unstable or may have developed a significant new problem requiring immediate physician attention. Typically, 35 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99315",  # Nursing facility discharge day management; 30 minutes or less
        "99316",  # Nursing facility discharge day management; more than 30 minutes
        "99318",  # Evaluation and management of a patient involving an annual nursing facility assessment, which requires these 3 key components: A detailed interval history; A comprehensive examination; and Medical decision making that is of low to moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is stable, recovering, or improving. Typically, 30 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99324",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A problem focused history; A problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low severity. Typically, 20 minutes are spent with the patient and/or family or caregiver.
        "99325",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate severity. Typically, 30 minutes are spent with the patient and/or family or caregiver.
        "99326",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A detailed history; A detailed examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 45 minutes are spent with the patient and/or family or caregiver.
        "99327",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of high severity. Typically, 60 minutes are spent with the patient and/or family or caregiver.
        "99328",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is unstable or has developed a significant new problem requiring immediate physician attention. Typically, 75 minutes are spent with the patient and/or family or caregiver.
        "99334",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self-limited or minor. Typically, 15 minutes are spent with the patient and/or family or caregiver.
        "99335",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low to moderate severity. Typically, 25 minutes are spent with the patient and/or family or caregiver.
        "99336",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A detailed interval history; A detailed examination; Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 40 minutes are spent with the patient and/or family or caregiver.
        "99337",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A comprehensive interval history; A comprehensive examination; Medical decision making of moderate to high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. The patient may be unstable or may have developed a significant new problem requiring immediate physician attention. Typically, 60 minutes are spent with the patient and/or family or caregiver.
        "99339",  # Individual physician supervision of a patient (patient not present) in home, domiciliary or rest home (eg, assisted living facility) requiring complex and multidisciplinary care modalities involving regular physician development and/or revision of care plans, review of subsequent reports of patient status, review of related laboratory and other studies, communication (including telephone calls) for purposes of assessment or care decisions with health care professional(s), family member(s), surrogate decision maker(s) (eg, legal guardian) and/or key caregiver(s) involved in patient's care, integration of new information into the medical treatment plan and/or adjustment of medical therapy, within a calendar month; 15-29 minutes
        "99340",  # Individual physician supervision of a patient (patient not present) in home, domiciliary or rest home (eg, assisted living facility) requiring complex and multidisciplinary care modalities involving regular physician development and/or revision of care plans, review of subsequent reports of patient status, review of related laboratory and other studies, communication (including telephone calls) for purposes of assessment or care decisions with health care professional(s), family member(s), surrogate decision maker(s) (eg, legal guardian) and/or key caregiver(s) involved in patient's care, integration of new information into the medical treatment plan and/or adjustment of medical therapy, within a calendar month; 30 minutes or more
        "99341",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: A problem focused history; A problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low severity. Typically, 20 minutes are spent face-to-face with the patient and/or family.
        "99342",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate severity. Typically, 30 minutes are spent face-to-face with the patient and/or family.
        "99343",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: A detailed history; A detailed examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 45 minutes are spent face-to-face with the patient and/or family.
        "99344",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of high severity. Typically, 60 minutes are spent face-to-face with the patient and/or family.
        "99345",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is unstable or has developed a significant new problem requiring immediate physician attention. Typically, 75 minutes are spent face-to-face with the patient and/or family.
        "99347",  # Home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self limited or minor. Typically, 15 minutes are spent face-to-face with the patient and/or family.
        "99348",  # Home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low to moderate severity. Typically, 25 minutes are spent face-to-face with the patient and/or family.
        "99349",  # Home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A detailed interval history; A detailed examination; Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are moderate to high severity. Typically, 40 minutes are spent face-to-face with the patient and/or family.
        "99350",  # Home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A comprehensive interval history; A comprehensive examination; Medical decision making of moderate to high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. The patient may be unstable or may have developed a significant new problem requiring immediate physician attention. Typically, 60 minutes are spent face-to-face with the patient and/or family.
        "99385",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 18-39 years
        "99386",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 40-64 years
        "99387",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 65 years and older
        "99395",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 18-39 years
        "99396",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 40-64 years
        "99397",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 65 years and older
    }
    HCPCSLEVELII = {
        "G0101",  # Cervical or vaginal cancer screening; pelvic and clinical breast examination
        "G0402",  # Initial preventive physical examination; face-to-face visit, services limited to new beneficiary during the first 12 months of medicare enrollment
        "G0438",  # Annual wellness visit; includes a personalized prevention plan of service (pps), initial visit
        "G0439",  # Annual wellness visit, includes a personalized prevention plan of service (pps), subsequent visit
    }
    SNOMEDCT = {
        "4525004",  # Emergency department patient visit (procedure)
        "12843005",  # Subsequent hospital visit by physician (procedure)
        "13607009",  # Manual examination of breast (procedure)
        "14736009",  # History and physical examination with evaluation and management of patient (procedure)
        "18170008",  # Subsequent nursing facility visit (procedure)
        "35025007",  # Manual pelvic examination (procedure)
        "46662001",  # Examination of breast (procedure)
        "50357006",  # Evaluation and management of patient at home (procedure)
        "76464004",  # Hospital admission, for observation (procedure)
        "78318003",  # History and physical examination, annual for health maintenance (procedure)
        "83607001",  # Gynecologic examination (procedure)
        "86013001",  # Periodic reevaluation and management of healthy individual (procedure)
        "90526000",  # Initial evaluation and management of healthy individual (procedure)
        "103705002",  # Patient status observation (procedure)
        "108220007",  # Evaluation AND/OR management - new patient (procedure)
        "108221006",  # Evaluation AND/OR management - established patient (procedure)
        "108224003",  # Preventive patient evaluation (procedure)
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
        "390906007",  # Follow-up encounter (procedure)
        "406547006",  # Urgent follow-up (procedure)
        "439708006",  # Home visit (procedure)
    }


class EncounterToScreenForDepression(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of encounters for depression screening.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent wellness visits, annual visits, therapy evaluations, or primary or specialist physician office visits where a depression screen could be conducted.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS2v11
    """

    VALUE_SET_NAME = "Encounter to Screen for Depression"
    OID = "2.16.840.1.113883.3.600.1916"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

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
        "97165",  # Occupational therapy evaluation, low complexity, requiring these components: An occupational profile and medical and therapy history, which includes a brief history including review of medical and/or therapy records relating to the presenting problem; An assessment(s) that identifies 1-3 performance deficits (ie, relating to physical, cognitive, or psychosocial skills) that result in activity limitations and/or participation restrictions; and Clinical decision making of low complexity, which includes an analysis of the occupational profile, analysis of data from problem-focused assessment(s), and consideration of a limited number of treatment options. Patient presents with no comorbidities that affect occupational performance. Modification of tasks or assistance (eg, physical or verbal) with assessment(s) is not necessary to enable completion of evaluation component. Typically, 30 minutes are spent face-to-face with the patient and/or family.
        "97166",  # Occupational therapy evaluation, moderate complexity, requiring these components: An occupational profile and medical and therapy history, which includes an expanded review of medical and/or therapy records and additional review of physical, cognitive, or psychosocial history related to current functional performance; An assessment(s) that identifies 3-5 performance deficits (ie, relating to physical, cognitive, or psychosocial skills) that result in activity limitations and/or participation restrictions; and Clinical decision making of moderate analytic complexity, which includes an analysis of the occupational profile, analysis of data from detailed assessment(s), and consideration of several treatment options. Patient may present with comorbidities that affect occupational performance. Minimal to moderate modification of tasks or assistance (eg, physical or verbal) with assessment(s) is necessary to enable patient to complete evaluation component. Typically, 45 minutes are spent face-to-face with the patient and/or family.
        "97167",  # Occupational therapy evaluation, high complexity, requiring these components: An occupational profile and medical and therapy history, which includes review of medical and/or therapy records and extensive additional review of physical, cognitive, or psychosocial history related to current functional performance; An assessment(s) that identifies 5 or more performance deficits (ie, relating to physical, cognitive, or psychosocial skills) that result in activity limitations and/or participation restrictions; and Clinical decision making of high analytic complexity, which includes an analysis of the patient profile, analysis of data from comprehensive assessment(s), and consideration of multiple treatment options. Patient presents with comorbidities that affect occupational performance. Significant modification of tasks or assistance (eg, physical or verbal) with assessment(s) is necessary to enable patient to complete evaluation component. Typically, 60 minutes are spent face-to-face with the patient and/or family.
        "99078",  # Physician or other qualified health care professional qualified by education, training, licensure/regulation (when applicable) educational services rendered to patients in a group setting (eg, prenatal, obesity, or diabetic instructions)
        "99202",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using time for code selection, 15-29 minutes of total time is spent on the date of the encounter.
        "99203",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using time for code selection, 30-44 minutes of total time is spent on the date of the encounter.
        "99204",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using time for code selection, 45-59 minutes of total time is spent on the date of the encounter.
        "99205",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using time for code selection, 60-74 minutes of total time is spent on the date of the encounter.
        "99212",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using time for code selection, 10-19 minutes of total time is spent on the date of the encounter.
        "99213",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using time for code selection, 20-29 minutes of total time is spent on the date of the encounter.
        "99214",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using time for code selection, 30-39 minutes of total time is spent on the date of the encounter.
        "99215",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using time for code selection, 40-54 minutes of total time is spent on the date of the encounter.
        "99304",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires these 3 key components: A detailed or comprehensive history; A detailed or comprehensive examination; and Medical decision making that is straightforward or of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of low severity. Typically, 25 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99305",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of moderate severity. Typically, 35 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99306",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of high severity. Typically, 45 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99307",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is stable, recovering, or improving. Typically, 10 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99308",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is responding inadequately to therapy or has developed a minor complication. Typically, 15 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99309",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A detailed interval history; A detailed examination; Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient has developed a significant complication or a significant new problem. Typically, 25 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99310",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A comprehensive interval history; A comprehensive examination; Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. The patient may be unstable or may have developed a significant new problem requiring immediate physician attention. Typically, 35 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99315",  # Nursing facility discharge day management; 30 minutes or less
        "99316",  # Nursing facility discharge day management; more than 30 minutes
        "99318",  # Evaluation and management of a patient involving an annual nursing facility assessment, which requires these 3 key components: A detailed interval history; A comprehensive examination; and Medical decision making that is of low to moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is stable, recovering, or improving. Typically, 30 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99324",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A problem focused history; A problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low severity. Typically, 20 minutes are spent with the patient and/or family or caregiver.
        "99325",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate severity. Typically, 30 minutes are spent with the patient and/or family or caregiver.
        "99326",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A detailed history; A detailed examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 45 minutes are spent with the patient and/or family or caregiver.
        "99327",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of high severity. Typically, 60 minutes are spent with the patient and/or family or caregiver.
        "99328",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is unstable or has developed a significant new problem requiring immediate physician attention. Typically, 75 minutes are spent with the patient and/or family or caregiver.
        "99334",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self-limited or minor. Typically, 15 minutes are spent with the patient and/or family or caregiver.
        "99335",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low to moderate severity. Typically, 25 minutes are spent with the patient and/or family or caregiver.
        "99336",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A detailed interval history; A detailed examination; Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 40 minutes are spent with the patient and/or family or caregiver.
        "99337",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A comprehensive interval history; A comprehensive examination; Medical decision making of moderate to high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. The patient may be unstable or may have developed a significant new problem requiring immediate physician attention. Typically, 60 minutes are spent with the patient and/or family or caregiver.
        "99339",  # Individual physician supervision of a patient (patient not present) in home, domiciliary or rest home (eg, assisted living facility) requiring complex and multidisciplinary care modalities involving regular physician development and/or revision of care plans, review of subsequent reports of patient status, review of related laboratory and other studies, communication (including telephone calls) for purposes of assessment or care decisions with health care professional(s), family member(s), surrogate decision maker(s) (eg, legal guardian) and/or key caregiver(s) involved in patient's care, integration of new information into the medical treatment plan and/or adjustment of medical therapy, within a calendar month; 15-29 minutes
        "99340",  # Individual physician supervision of a patient (patient not present) in home, domiciliary or rest home (eg, assisted living facility) requiring complex and multidisciplinary care modalities involving regular physician development and/or revision of care plans, review of subsequent reports of patient status, review of related laboratory and other studies, communication (including telephone calls) for purposes of assessment or care decisions with health care professional(s), family member(s), surrogate decision maker(s) (eg, legal guardian) and/or key caregiver(s) involved in patient's care, integration of new information into the medical treatment plan and/or adjustment of medical therapy, within a calendar month; 30 minutes or more
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
        "99483",  # Assessment of and care planning for a patient with cognitive impairment, requiring an independent historian, in the office or other outpatient, home or domiciliary or rest home, with all of the following required elements: Cognition-focused evaluation including a pertinent history and examination; Medical decision making of moderate or high complexity; Functional assessment (eg, basic and instrumental activities of daily living), including decision-making capacity; Use of standardized instruments for staging of dementia (eg, functional assessment staging test [FAST], clinical dementia rating [CDR]); Medication reconciliation and review for high-risk medications; Evaluation for neuropsychiatric and behavioral symptoms, including depression, including use of standardized screening instrument(s); Evaluation of safety (eg, home), including motor vehicle operation; Identification of caregiver(s), caregiver knowledge, caregiver needs, social supports, and the willingness of caregiver to take on caregiving tasks; Development, updating or revision, or review of an Advance Care Plan; Creation of a written care plan, including initial plans to address any neuropsychiatric symptoms, neuro-cognitive symptoms, functional limitations, and referral to community resources as needed (eg, rehabilitation services, adult day programs, support groups) shared with the patient and/or caregiver with initial education and support. Typically, 50 minutes are spent face-to-face with the patient and/or family or caregiver.
        "99484",  # Care management services for behavioral health conditions, at least 20 minutes of clinical staff time, directed by a physician or other qualified health care professional, per calendar month, with the following required elements: initial assessment or follow-up monitoring, including the use of applicable validated rating scales; behavioral health care planning in relation to behavioral/psychiatric health problems, including revision for patients who are not progressing or whose status changes; facilitating and coordinating treatment such as psychotherapy, pharmacotherapy, counseling and/or psychiatric consultation; and continuity of care with a designated member of the care team.
        "99492",  # Initial psychiatric collaborative care management, first 70 minutes in the first calendar month of behavioral health care manager activities, in consultation with a psychiatric consultant, and directed by the treating physician or other qualified health care professional, with the following required elements: outreach to and engagement in treatment of a patient directed by the treating physician or other qualified health care professional; initial assessment of the patient, including administration of validated rating scales, with the development of an individualized treatment plan; review by the psychiatric consultant with modifications of the plan if recommended; entering patient in a registry and tracking patient follow-up and progress using the registry, with appropriate documentation, and participation in weekly caseload consultation with the psychiatric consultant; and provision of brief interventions using evidence-based techniques such as behavioral activation, motivational interviewing, and other focused treatment strategies.
        "99493",  # Subsequent psychiatric collaborative care management, first 60 minutes in a subsequent month of behavioral health care manager activities, in consultation with a psychiatric consultant, and directed by the treating physician or other qualified health care professional, with the following required elements: tracking patient follow-up and progress using the registry, with appropriate documentation; participation in weekly caseload consultation with the psychiatric consultant; ongoing collaboration with and coordination of the patient's mental health care with the treating physician or other qualified health care professional and any other treating mental health providers; additional review of progress and recommendations for changes in treatment, as indicated, including medications, based on recommendations provided by the psychiatric consultant; provision of brief interventions using evidence-based techniques such as behavioral activation, motivational interviewing, and other focused treatment strategies; monitoring of patient outcomes using validated rating scales; and relapse prevention planning with patients as they achieve remission of symptoms and/or other treatment goals and are prepared for discharge from active treatment.
    }
    HCPCSLEVELII = {
        "G0101",  # Cervical or vaginal cancer screening; pelvic and clinical breast examination
        "G0402",  # Initial preventive physical examination; face-to-face visit, services limited to new beneficiary during the first 12 months of medicare enrollment
        "G0438",  # Annual wellness visit; includes a personalized prevention plan of service (pps), initial visit
        "G0439",  # Annual wellness visit, includes a personalized prevention plan of service (pps), subsequent visit
        "G0444",  # Annual depression screening, 15 minutes
    }
    SNOMEDCT = {
        "8411005",  # Interactive individual medical psychotherapy (regime/therapy)
        "10197000",  # Psychiatric interview and evaluation (procedure)
        "13607009",  # Manual examination of breast (procedure)
        "14736009",  # History and physical examination with evaluation and management of patient (procedure)
        "18512000",  # Individual psychotherapy (regime/therapy)
        "35025007",  # Manual pelvic examination (procedure)
        "46662001",  # Examination of breast (procedure)
        "53555003",  # Basic comprehensive audiometry testing (procedure)
        "78318003",  # History and physical examination, annual for health maintenance (procedure)
        "83607001",  # Gynecologic examination (procedure)
        "86013001",  # Periodic reevaluation and management of healthy individual (procedure)
        "90526000",  # Initial evaluation and management of healthy individual (procedure)
        "108220007",  # Evaluation AND/OR management - new patient (procedure)
        "108221006",  # Evaluation AND/OR management - established patient (procedure)
        "108224003",  # Preventive patient evaluation (procedure)
        "108311000",  # Psychiatric procedure, interview AND/OR consultation (procedure)
        "165171009",  # Initial psychiatric evaluation (procedure)
        "171207006",  # Depression screening (procedure)
        "185349003",  # Encounter for check up (procedure)
        "185463005",  # Visit out of hours (procedure)
        "185465003",  # Weekend visit (procedure)
        "252603000",  # Tinnitus assessment (procedure)
        "270427003",  # Patient-initiated encounter (procedure)
        "270430005",  # Provider-initiated encounter (procedure)
        "302440009",  # Psychiatric pharmacologic management (procedure)
        "308335008",  # Patient encounter procedure (procedure)
        "370803007",  # Evaluation of psychosocial impact on plan of care (procedure)
        "390906007",  # Follow-up encounter (procedure)
        "406547006",  # Urgent follow-up (procedure)
        "410155007",  # Occupational therapy assessment (procedure)
        "410157004",  # Occupational therapy management (procedure)
    }


class OutpatientEncountersForPreventiveCare(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of an encounter for outpatient visits.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent outpatient encounters for annual visit, preventive evaluation, follow-up, or periodic re-evaluations.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS347v5
    """

    VALUE_SET_NAME = "Outpatient Encounters for Preventive Care"
    OID = "2.16.840.1.113883.3.526.3.1576"
    DEFINITION_VERSION = "20200307"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "14736009",  # History and physical examination with evaluation and management of patient (procedure)
        "78318003",  # History and physical examination, annual for health maintenance (procedure)
        "86013001",  # Periodic reevaluation and management of healthy individual (procedure)
        "90526000",  # Initial evaluation and management of healthy individual (procedure)
        "108219001",  # Physician visit with evaluation AND/OR management service (procedure)
        "108220007",  # Evaluation AND/OR management - new patient (procedure)
        "108221006",  # Evaluation AND/OR management - established patient (procedure)
        "108224003",  # Preventive patient evaluation (procedure)
        "185349003",  # Encounter for check up (procedure)
        "185389009",  # Follow-up visit (procedure)
        "270427003",  # Patient-initiated encounter (procedure)
        "270430005",  # Provider-initiated encounter (procedure)
        "281036007",  # Follow-up consultation (procedure)
        "308335008",  # Patient encounter procedure (procedure)
        "390906007",  # Follow-up encounter (procedure)
        "410187005",  # Physical evaluation management (procedure)
    }


class EncounterToDocumentMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters that include documentation of current medications.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that identify an encounter that includes documentation of medications reviewed, updated or transcribed as the current medication list.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS68v11
    """

    VALUE_SET_NAME = "Encounter to Document Medications"
    OID = "2.16.840.1.113883.3.600.1.1834"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

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
        "98960",  # Education and training for patient self-management by a qualified, nonphysician health care professional using a standardized curriculum, face-to-face with the patient (could include caregiver/family) each 30 minutes; individual patient
        "98961",  # Education and training for patient self-management by a qualified, nonphysician health care professional using a standardized curriculum, face-to-face with the patient (could include caregiver/family) each 30 minutes; 2-4 patients
        "98962",  # Education and training for patient self-management by a qualified, nonphysician health care professional using a standardized curriculum, face-to-face with the patient (could include caregiver/family) each 30 minutes; 5-8 patients
        "99202",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using time for code selection, 15-29 minutes of total time is spent on the date of the encounter.
        "99203",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using time for code selection, 30-44 minutes of total time is spent on the date of the encounter.
        "99204",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using time for code selection, 45-59 minutes of total time is spent on the date of the encounter.
        "99205",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using time for code selection, 60-74 minutes of total time is spent on the date of the encounter.
        "99211",  # Office or other outpatient visit for the evaluation and management of an established patient, that may not require the presence of a physician or other qualified health care professional. Usually, the presenting problem(s) are minimal.
        "99212",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using time for code selection, 10-19 minutes of total time is spent on the date of the encounter.
        "99213",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using time for code selection, 20-29 minutes of total time is spent on the date of the encounter.
        "99214",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using time for code selection, 30-39 minutes of total time is spent on the date of the encounter.
        "99215",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using time for code selection, 40-54 minutes of total time is spent on the date of the encounter.
        "99221",  # Initial hospital care, per day, for the evaluation and management of a patient, which requires these 3 key components: A detailed or comprehensive history; A detailed or comprehensive examination; and Medical decision making that is straightforward or of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of low severity. Typically, 30 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99222",  # Initial hospital care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of moderate severity. Typically, 50 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99223",  # Initial hospital care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of high severity. Typically, 70 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99236",  # Observation or inpatient hospital care, for the evaluation and management of a patient including admission and discharge on the same date, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually the presenting problem(s) requiring admission are of high severity. Typically, 55 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99281",  # Emergency department visit for the evaluation and management of a patient, which requires these 3 key components: A problem focused history; A problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self limited or minor.
        "99282",  # Emergency department visit for the evaluation and management of a patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low to moderate severity.
        "99283",  # Emergency department visit for the evaluation and management of a patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate severity.
        "99284",  # Emergency department visit for the evaluation and management of a patient, which requires these 3 key components: A detailed history; A detailed examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of high severity, and require urgent evaluation by the physician, or other qualified health care professionals but do not pose an immediate significant threat to life or physiologic function.
        "99285",  # Emergency department visit for the evaluation and management of a patient, which requires these 3 key components within the constraints imposed by the urgency of the patient's clinical condition and/or mental status: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of high severity and pose an immediate significant threat to life or physiologic function.
        "99304",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires these 3 key components: A detailed or comprehensive history; A detailed or comprehensive examination; and Medical decision making that is straightforward or of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of low severity. Typically, 25 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99305",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of moderate severity. Typically, 35 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99306",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of high severity. Typically, 45 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99307",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is stable, recovering, or improving. Typically, 10 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99308",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is responding inadequately to therapy or has developed a minor complication. Typically, 15 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99309",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A detailed interval history; A detailed examination; Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient has developed a significant complication or a significant new problem. Typically, 25 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99310",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A comprehensive interval history; A comprehensive examination; Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. The patient may be unstable or may have developed a significant new problem requiring immediate physician attention. Typically, 35 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99315",  # Nursing facility discharge day management; 30 minutes or less
        "99316",  # Nursing facility discharge day management; more than 30 minutes
        "99318",  # Evaluation and management of a patient involving an annual nursing facility assessment, which requires these 3 key components: A detailed interval history; A comprehensive examination; and Medical decision making that is of low to moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is stable, recovering, or improving. Typically, 30 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99324",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A problem focused history; A problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low severity. Typically, 20 minutes are spent with the patient and/or family or caregiver.
        "99325",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate severity. Typically, 30 minutes are spent with the patient and/or family or caregiver.
        "99326",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A detailed history; A detailed examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 45 minutes are spent with the patient and/or family or caregiver.
        "99327",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of high severity. Typically, 60 minutes are spent with the patient and/or family or caregiver.
        "99328",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is unstable or has developed a significant new problem requiring immediate physician attention. Typically, 75 minutes are spent with the patient and/or family or caregiver.
        "99334",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self-limited or minor. Typically, 15 minutes are spent with the patient and/or family or caregiver.
        "99335",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low to moderate severity. Typically, 25 minutes are spent with the patient and/or family or caregiver.
        "99336",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A detailed interval history; A detailed examination; Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 40 minutes are spent with the patient and/or family or caregiver.
        "99337",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A comprehensive interval history; A comprehensive examination; Medical decision making of moderate to high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. The patient may be unstable or may have developed a significant new problem requiring immediate physician attention. Typically, 60 minutes are spent with the patient and/or family or caregiver.
        "99339",  # Individual physician supervision of a patient (patient not present) in home, domiciliary or rest home (eg, assisted living facility) requiring complex and multidisciplinary care modalities involving regular physician development and/or revision of care plans, review of subsequent reports of patient status, review of related laboratory and other studies, communication (including telephone calls) for purposes of assessment or care decisions with health care professional(s), family member(s), surrogate decision maker(s) (eg, legal guardian) and/or key caregiver(s) involved in patient's care, integration of new information into the medical treatment plan and/or adjustment of medical therapy, within a calendar month; 15-29 minutes
        "99340",  # Individual physician supervision of a patient (patient not present) in home, domiciliary or rest home (eg, assisted living facility) requiring complex and multidisciplinary care modalities involving regular physician development and/or revision of care plans, review of subsequent reports of patient status, review of related laboratory and other studies, communication (including telephone calls) for purposes of assessment or care decisions with health care professional(s), family member(s), surrogate decision maker(s) (eg, legal guardian) and/or key caregiver(s) involved in patient's care, integration of new information into the medical treatment plan and/or adjustment of medical therapy, within a calendar month; 30 minutes or more
        "99341",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: A problem focused history; A problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low severity. Typically, 20 minutes are spent face-to-face with the patient and/or family.
        "99342",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate severity. Typically, 30 minutes are spent face-to-face with the patient and/or family.
        "99343",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: A detailed history; A detailed examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 45 minutes are spent face-to-face with the patient and/or family.
        "99344",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of high severity. Typically, 60 minutes are spent face-to-face with the patient and/or family.
        "99345",  # Home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is unstable or has developed a significant new problem requiring immediate physician attention. Typically, 75 minutes are spent face-to-face with the patient and/or family.
        "99347",  # Home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self limited or minor. Typically, 15 minutes are spent face-to-face with the patient and/or family.
        "99348",  # Home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low to moderate severity. Typically, 25 minutes are spent face-to-face with the patient and/or family.
        "99349",  # Home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A detailed interval history; A detailed examination; Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are moderate to high severity. Typically, 40 minutes are spent face-to-face with the patient and/or family.
        "99350",  # Home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A comprehensive interval history; A comprehensive examination; Medical decision making of moderate to high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. The patient may be unstable or may have developed a significant new problem requiring immediate physician attention. Typically, 60 minutes are spent face-to-face with the patient and/or family.
        "99385",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 18-39 years
        "99386",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 40-64 years
        "99387",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 65 years and older
        "99395",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 18-39 years
        "99396",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 40-64 years
        "99397",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 65 years and older
        "99495",  # Transitional Care Management Services with the following required elements: Communication (direct contact, telephone, electronic) with the patient and/or caregiver within 2 business days of discharge Medical decision making of at least moderate complexity during the service period Face-to-face visit, within 14 calendar days of discharge
        "99496",  # Transitional Care Management Services with the following required elements: Communication (direct contact, telephone, electronic) with the patient and/or caregiver within 2 business days of discharge Medical decision making of high complexity during the service period Face-to-face visit, within 7 calendar days of discharge
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
        "8411005",  # Interactive individual medical psychotherapy (regime/therapy)
        "10197000",  # Psychiatric interview and evaluation (procedure)
        "13607009",  # Manual examination of breast (procedure)
        "14736009",  # History and physical examination with evaluation and management of patient (procedure)
        "18091003",  # Electronystagmography with vertical electrodes (procedure)
        "18114009",  # Prenatal examination and care of mother (procedure)
        "18512000",  # Individual psychotherapy (regime/therapy)
        "34651001",  # Optokinetic nystagmus test, bidirectional, with recording (procedure)
        "35025007",  # Manual pelvic examination (procedure)
        "36228007",  # Ophthalmic examination and evaluation (procedure)
        "46662001",  # Examination of breast (procedure)
        "48423005",  # Acoustic reflex testing (procedure)
        "50357006",  # Evaluation and management of patient at home (procedure)
        "53555003",  # Basic comprehensive audiometry testing (procedure)
        "54290001",  # Positional nystagmus test with recording (procedure)
        "63547008",  # Caloric vestibular test with recording (procedure)
        "66902005",  # Ophthalmic examination and evaluation, follow-up (procedure)
        "78318003",  # History and physical examination, annual for health maintenance (procedure)
        "83607001",  # Gynecologic examination (procedure)
        "86013001",  # Periodic reevaluation and management of healthy individual (procedure)
        "90526000",  # Initial evaluation and management of healthy individual (procedure)
        "91573000",  # Tympanometry testing (procedure)
        "108220007",  # Evaluation AND/OR management - new patient (procedure)
        "108221006",  # Evaluation AND/OR management - established patient (procedure)
        "108224003",  # Preventive patient evaluation (procedure)
        "108311000",  # Psychiatric procedure, interview AND/OR consultation (procedure)
        "163497009",  # Obstetric examination (procedure)
        "165171009",  # Initial psychiatric evaluation (procedure)
        "169762003",  # Postnatal visit (regime/therapy)
        "183382003",  # Psychotherapy - behavioral (regime/therapy)
        "183383008",  # Psychotherapy - cognitive (regime/therapy)
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
        "698610002",  # Education about self management of diabetes (procedure)
        "870422002",  # Assessment of self management of diabetes mellitus (procedure)
    }


class EncounterToEvaluateBmi(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters where body mass index (BMI) could be assessed.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts for encounters where body mass index (BMI) could be assessed.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS69v10
    """

    VALUE_SET_NAME = "Encounter to Evaluate BMI"
    OID = "2.16.840.1.113883.3.600.1.1751"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CDT = {
        "D7111",  # extraction, coronal remnants - primary tooth
        "D7140",  # extraction, erupted tooth or exposed root (elevation and/or forceps removal)
        "D7210",  # extraction, erupted tooth requiring removal of bone and/or sectioning of tooth, and including elevation of mucoperiosteal flap if indicated
        "D7220",  # removal of impacted tooth - soft tissue
        "D7230",  # removal of impacted tooth - partially bony
        "D7240",  # removal of impacted tooth - completely bony
        "D7241",  # removal of impacted tooth - completely bony, with unusual surgical complications
        "D7250",  # removal of residual tooth roots (cutting procedure)
        "D7251",  # coronectomy - intentional partial tooth removal
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
        "99202",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using time for code selection, 15-29 minutes of total time is spent on the date of the encounter.
        "99203",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using time for code selection, 30-44 minutes of total time is spent on the date of the encounter.
        "99204",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using time for code selection, 45-59 minutes of total time is spent on the date of the encounter.
        "99205",  # Office or other outpatient visit for the evaluation and management of a new patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using time for code selection, 60-74 minutes of total time is spent on the date of the encounter.
        "99212",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and straightforward medical decision making. When using time for code selection, 10-19 minutes of total time is spent on the date of the encounter.
        "99213",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and low level of medical decision making. When using time for code selection, 20-29 minutes of total time is spent on the date of the encounter.
        "99214",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and moderate level of medical decision making. When using time for code selection, 30-39 minutes of total time is spent on the date of the encounter.
        "99215",  # Office or other outpatient visit for the evaluation and management of an established patient, which requires a medically appropriate history and/or examination and high level of medical decision making. When using time for code selection, 40-54 minutes of total time is spent on the date of the encounter.
        "99236",  # Observation or inpatient hospital care, for the evaluation and management of a patient including admission and discharge on the same date, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually the presenting problem(s) requiring admission are of high severity. Typically, 55 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99304",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires these 3 key components: A detailed or comprehensive history; A detailed or comprehensive examination; and Medical decision making that is straightforward or of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of low severity. Typically, 25 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99305",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of moderate severity. Typically, 35 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99306",  # Initial nursing facility care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of high severity. Typically, 45 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99307",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is stable, recovering, or improving. Typically, 10 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99308",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is responding inadequately to therapy or has developed a minor complication. Typically, 15 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99309",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A detailed interval history; A detailed examination; Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient has developed a significant complication or a significant new problem. Typically, 25 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99310",  # Subsequent nursing facility care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A comprehensive interval history; A comprehensive examination; Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. The patient may be unstable or may have developed a significant new problem requiring immediate physician attention. Typically, 35 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99315",  # Nursing facility discharge day management; 30 minutes or less
        "99316",  # Nursing facility discharge day management; more than 30 minutes
        "99318",  # Evaluation and management of a patient involving an annual nursing facility assessment, which requires these 3 key components: A detailed interval history; A comprehensive examination; and Medical decision making that is of low to moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is stable, recovering, or improving. Typically, 30 minutes are spent at the bedside and on the patient's facility floor or unit.
        "99324",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A problem focused history; A problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low severity. Typically, 20 minutes are spent with the patient and/or family or caregiver.
        "99325",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate severity. Typically, 30 minutes are spent with the patient and/or family or caregiver.
        "99326",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A detailed history; A detailed examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 45 minutes are spent with the patient and/or family or caregiver.
        "99327",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of high severity. Typically, 60 minutes are spent with the patient and/or family or caregiver.
        "99328",  # Domiciliary or rest home visit for the evaluation and management of a new patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is unstable or has developed a significant new problem requiring immediate physician attention. Typically, 75 minutes are spent with the patient and/or family or caregiver.
        "99334",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self-limited or minor. Typically, 15 minutes are spent with the patient and/or family or caregiver.
        "99335",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low to moderate severity. Typically, 25 minutes are spent with the patient and/or family or caregiver.
        "99336",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A detailed interval history; A detailed examination; Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. Typically, 40 minutes are spent with the patient and/or family or caregiver.
        "99337",  # Domiciliary or rest home visit for the evaluation and management of an established patient, which requires at least 2 of these 3 key components: A comprehensive interval history; A comprehensive examination; Medical decision making of moderate to high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate to high severity. The patient may be unstable or may have developed a significant new problem requiring immediate physician attention. Typically, 60 minutes are spent with the patient and/or family or caregiver.
        "99339",  # Individual physician supervision of a patient (patient not present) in home, domiciliary or rest home (eg, assisted living facility) requiring complex and multidisciplinary care modalities involving regular physician development and/or revision of care plans, review of subsequent reports of patient status, review of related laboratory and other studies, communication (including telephone calls) for purposes of assessment or care decisions with health care professional(s), family member(s), surrogate decision maker(s) (eg, legal guardian) and/or key caregiver(s) involved in patient's care, integration of new information into the medical treatment plan and/or adjustment of medical therapy, within a calendar month; 15-29 minutes
        "99340",  # Individual physician supervision of a patient (patient not present) in home, domiciliary or rest home (eg, assisted living facility) requiring complex and multidisciplinary care modalities involving regular physician development and/or revision of care plans, review of subsequent reports of patient status, review of related laboratory and other studies, communication (including telephone calls) for purposes of assessment or care decisions with health care professional(s), family member(s), surrogate decision maker(s) (eg, legal guardian) and/or key caregiver(s) involved in patient's care, integration of new information into the medical treatment plan and/or adjustment of medical therapy, within a calendar month; 30 minutes or more
        "99385",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 18-39 years
        "99386",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 40-64 years
        "99387",  # Initial comprehensive preventive medicine evaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, new patient; 65 years and older
        "99395",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 18-39 years
        "99396",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 40-64 years
        "99397",  # Periodic comprehensive preventive medicine reevaluation and management of an individual including an age and gender appropriate history, examination, counseling/anticipatory guidance/risk factor reduction interventions, and the ordering of laboratory/diagnostic procedures, established patient; 65 years and older
        "99401",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 15 minutes
        "99402",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 30 minutes
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
        "8411005",  # Interactive individual medical psychotherapy (regime/therapy)
        "10197000",  # Psychiatric interview and evaluation (procedure)
        "13607009",  # Manual examination of breast (procedure)
        "14736009",  # History and physical examination with evaluation and management of patient (procedure)
        "18512000",  # Individual psychotherapy (regime/therapy)
        "35025007",  # Manual pelvic examination (procedure)
        "46662001",  # Examination of breast (procedure)
        "55162003",  # Tooth extraction (procedure)
        "68381003",  # Surgical removal of erupted tooth requiring elevation of mucoperiosteal flap and removal of bone and/or section of tooth (procedure)
        "78318003",  # History and physical examination, annual for health maintenance (procedure)
        "83607001",  # Gynecologic examination (procedure)
        "86013001",  # Periodic reevaluation and management of healthy individual (procedure)
        "90526000",  # Initial evaluation and management of healthy individual (procedure)
        "108220007",  # Evaluation AND/OR management - new patient (procedure)
        "108221006",  # Evaluation AND/OR management - established patient (procedure)
        "108224003",  # Preventive patient evaluation (procedure)
        "108311000",  # Psychiatric procedure, interview AND/OR consultation (procedure)
        "165171009",  # Initial psychiatric evaluation (procedure)
        "185349003",  # Encounter for check up (procedure)
        "185463005",  # Visit out of hours (procedure)
        "185465003",  # Weekend visit (procedure)
        "225967005",  # Self-care patient education (procedure)
        "270427003",  # Patient-initiated encounter (procedure)
        "270430005",  # Provider-initiated encounter (procedure)
        "308335008",  # Patient encounter procedure (procedure)
        "386372009",  # Nutrition management (regime/therapy)
        "390906007",  # Follow-up encounter (procedure)
        "406547006",  # Urgent follow-up (procedure)
        "410155007",  # Occupational therapy assessment (procedure)
        "410157004",  # Occupational therapy management (procedure)
        "410158009",  # Physical therapy assessment (procedure)
        "410160006",  # Physical therapy management (procedure)
        "410170008",  # Nutrition care assessment (procedure)
        "410172000",  # Nutrition care management (procedure)
    }


class ClinicalOralEvaluation(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for clinical oral evaluations.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for periodic or limited (problem focused) or comprehensive oral evaluations and re-evaluations.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS74v11, CMS75v10
    """

    VALUE_SET_NAME = "Clinical Oral Evaluation"
    OID = "2.16.840.1.113883.3.464.1003.125.12.1003"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

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

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS771v3
    """

    VALUE_SET_NAME = "Hospital Services for urology care"
    OID = "2.16.840.1.113762.1.4.1164.64"
    DEFINITION_VERSION = "20171025"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99217",  # Observation care discharge day management (This code is to be utilized to report all services provided to a patient on discharge from outpatient hospital "observation status" if the discharge is on other than the initial date of "observation status." To report services to a patient designated as "observation status" or "inpatient status" and discharged on the same date, use the codes for Observation or Inpatient Care Services [including Admission and Discharge Services, 99234-99236 as appropriate.])
        "99218",  # Initial observation care, per day, for the evaluation and management of a patient which requires these 3 key components: A detailed or comprehensive history; A detailed or comprehensive examination; and Medical decision making that is straightforward or of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission to outpatient hospital "observation status" are of low severity. Typically, 30 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99219",  # Initial observation care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission to outpatient hospital "observation status" are of moderate severity. Typically, 50 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99220",  # Initial observation care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission to outpatient hospital "observation status" are of high severity. Typically, 70 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99221",  # Initial hospital care, per day, for the evaluation and management of a patient, which requires these 3 key components: A detailed or comprehensive history; A detailed or comprehensive examination; and Medical decision making that is straightforward or of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of low severity. Typically, 30 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99222",  # Initial hospital care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of moderate severity. Typically, 50 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99223",  # Initial hospital care, per day, for the evaluation and management of a patient, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the problem(s) requiring admission are of high severity. Typically, 70 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99231",  # Subsequent hospital care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A problem focused interval history; A problem focused examination; Medical decision making that is straightforward or of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is stable, recovering or improving. Typically, 15 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99232",  # Subsequent hospital care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: An expanded problem focused interval history; An expanded problem focused examination; Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is responding inadequately to therapy or has developed a minor complication. Typically, 25 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99233",  # Subsequent hospital care, per day, for the evaluation and management of a patient, which requires at least 2 of these 3 key components: A detailed interval history; A detailed examination; Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the patient is unstable or has developed a significant complication or a significant new problem. Typically, 35 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99234",  # Observation or inpatient hospital care, for the evaluation and management of a patient including admission and discharge on the same date, which requires these 3 key components: A detailed or comprehensive history; A detailed or comprehensive examination; and Medical decision making that is straightforward or of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually the presenting problem(s) requiring admission are of low severity. Typically, 40 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99235",  # Observation or inpatient hospital care, for the evaluation and management of a patient including admission and discharge on the same date, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually the presenting problem(s) requiring admission are of moderate severity. Typically, 50 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99236",  # Observation or inpatient hospital care, for the evaluation and management of a patient including admission and discharge on the same date, which requires these 3 key components: A comprehensive history; A comprehensive examination; and Medical decision making of high complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually the presenting problem(s) requiring admission are of high severity. Typically, 55 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99238",  # Hospital discharge day management; 30 minutes or less
        "99239",  # Hospital discharge day management; more than 30 minutes
        "99251",  # Inpatient consultation for a new or established patient, which requires these 3 key components: A problem focused history; A problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self limited or minor. Typically, 20 minutes are spent at the bedside and on the patient's hospital floor or unit.
        "99281",  # Emergency department visit for the evaluation and management of a patient, which requires these 3 key components: A problem focused history; A problem focused examination; and Straightforward medical decision making. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are self limited or minor.
        "99282",  # Emergency department visit for the evaluation and management of a patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Medical decision making of low complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of low to moderate severity.
        "99283",  # Emergency department visit for the evaluation and management of a patient, which requires these 3 key components: An expanded problem focused history; An expanded problem focused examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of moderate severity.
        "99284",  # Emergency department visit for the evaluation and management of a patient, which requires these 3 key components: A detailed history; A detailed examination; and Medical decision making of moderate complexity. Counseling and/or coordination of care with other physicians, other qualified health care professionals, or agencies are provided consistent with the nature of the problem(s) and the patient's and/or family's needs. Usually, the presenting problem(s) are of high severity, and require urgent evaluation by the physician, or other qualified health care professionals but do not pose an immediate significant threat to life or physiologic function.
    }


__exports__ = get_overrides(locals().copy())
