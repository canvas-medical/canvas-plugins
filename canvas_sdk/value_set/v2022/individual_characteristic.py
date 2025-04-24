from canvas_sdk.value_set._utilities import get_overrides

from ..value_set import ValueSet


class Ethnicity(ValueSet):
    """Ethnicity value set.

    **Clinical Focus:**

    **Data Element Scope:**

    **Inclusion Criteria:**

    **Exclusion Criteria:**

    ** Used in:** CMS135v10, CMS90v11, CMS249v4, CMS159v10, CMS349v4, CMS69v10, CMS142v10, CMS134v10, CMS177v10, CMS165v10, CMS143v10, CMS146v10, CMS157v10, CMS124v10, CMS2v11, CMS50v10, CMS22v10, CMS68v11, CMS139v10, CMS129v11, CMS154v10, CMS161v10, CMS56v10, CMS74v11, CMS645v5, CMS138v10, CMS75v10, CMS137v10, CMS136v11, CMS128v10, CMS122v10, CMS153v10, CMS144v10, CMS66v10, CMS130v10, CMS646v2, CMS155v10, CMS127v10, CMS771v3, CMS117v10, CMS131v10, CMS149v10, CMS347v5, CMS133v10, CMS156v10, CMS147v11, CMS125v10, CMS145v10
    """

    VALUE_SET_NAME = "Ethnicity"
    OID = "2.16.840.1.114222.4.11.837"
    DEFINITION_VERSION = "20121025"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CDCREC = {
        "2135-2",  # Hispanic or Latino
        "2186-5",  # Not Hispanic or Latino
    }


class OncAdministrativeSex(ValueSet):
    """ONC Administrative Sex value set.

    **Clinical Focus:** Gender identity restricted to only Male and Female used in administrative situations requiring a restriction to these two categories.

    **Data Element Scope:** Gender

    **Inclusion Criteria:** Male and Female only.

    **Exclusion Criteria:** Any gender identity that is not male or female.

    ** Used in:** CMS135v10, CMS90v11, CMS249v4, CMS159v10, CMS349v4, CMS69v10, CMS142v10, CMS134v10, CMS177v10, CMS165v10, CMS143v10, CMS146v10, CMS157v10, CMS124v10, CMS2v11, CMS50v10, CMS22v10, CMS68v11, CMS139v10, CMS129v11, CMS154v10, CMS161v10, CMS56v10, CMS74v11, CMS645v5, CMS138v10, CMS75v10, CMS137v10, CMS136v11, CMS128v10, CMS122v10, CMS153v10, CMS144v10, CMS66v10, CMS130v10, CMS646v2, CMS155v10, CMS127v10, CMS771v3, CMS117v10, CMS131v10, CMS149v10, CMS347v5, CMS133v10, CMS156v10, CMS147v11, CMS125v10, CMS145v10
    """

    VALUE_SET_NAME = "ONC Administrative Sex"
    OID = "2.16.840.1.113762.1.4.1"
    DEFINITION_VERSION = "20150331"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    ADMINISTRATIVEGENDER = {
        "F",  # Female
        "M",  # Male
    }


class Payer(ValueSet):
    """Payer value set.

    **Clinical Focus:** Categories of types of health care payor entities as defined by the US Public Health Data Consortium SOP code system

    **Data Element Scope:** @code in CCDA r2.1 template Planned Coverage [act: identifier urn:oid:2.16.840.1.113883.10.20.22.4.129 (open)] DYNAMIC

    **Inclusion Criteria:** All codes in the code system

    **Exclusion Criteria:** none

    ** Used in:** CMS135v10, CMS90v11, CMS249v4, CMS159v10, CMS349v4, CMS69v10, CMS142v10, CMS134v10, CMS177v10, CMS165v10, CMS143v10, CMS146v10, CMS157v10, CMS124v10, CMS2v11, CMS50v10, CMS22v10, CMS68v11, CMS139v10, CMS129v11, CMS154v10, CMS161v10, CMS56v10, CMS74v11, CMS645v5, CMS138v10, CMS75v10, CMS137v10, CMS136v11, CMS128v10, CMS122v10, CMS153v10, CMS144v10, CMS66v10, CMS130v10, CMS646v2, CMS155v10, CMS127v10, CMS771v3, CMS117v10, CMS131v10, CMS149v10, CMS347v5, CMS133v10, CMS156v10, CMS147v11, CMS125v10, CMS145v10
    """

    VALUE_SET_NAME = "Payer"
    OID = "2.16.840.1.114222.4.11.3591"
    DEFINITION_VERSION = "20180718"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SOP = {
        "1",  # MEDICARE
        "2",  # MEDICAID
        "3",  # OTHER GOVERNMENT (Federal/State/Local) (excluding Department of Corrections)
        "4",  # DEPARTMENTS OF CORRECTIONS
        "5",  # PRIVATE HEALTH INSURANCE
        "6",  # BLUE CROSS/BLUE SHIELD
        "7",  # MANAGED CARE, UNSPECIFIED (to be used only if one can't distinguish public from private)
        "8",  # NO PAYMENT from an Organization/Agency/Program/Private Payer Listed
        "9",  # MISCELLANEOUS/OTHER
        "11",  # Medicare Managed Care (Includes Medicare Advantage Plans)
        "12",  # Medicare (Non-managed Care)
        "13",  # Medicare Hospice
        "14",  # Dual Eligibility Medicare/Medicaid Organization
        "19",  # Medicare Other
        "21",  # Medicaid (Managed Care)
        "22",  # Medicaid (Non-managed Care Plan)
        "23",  # Medicaid/SCHIP
        "25",  # Medicaid - Out of State
        "26",  # Medicaid - Long Term Care
        "29",  # Medicaid Other
        "31",  # Department of Defense
        "32",  # Department of Veterans Affairs
        "33",  # Indian Health Service or Tribe
        "34",  # HRSA Program
        "35",  # Black Lung
        "36",  # State Government
        "37",  # Local Government
        "38",  # Other Government (Federal, State, Local not specified)
        "39",  # Other Federal
        "41",  # Corrections Federal
        "42",  # Corrections State
        "43",  # Corrections Local
        "44",  # Corrections Unknown Level
        "51",  # Managed Care (Private)
        "52",  # Private Health Insurance - Indemnity
        "53",  # Managed Care (private) or private health insurance (indemnity), not otherwise specified
        "54",  # Organized Delivery System
        "55",  # Small Employer Purchasing Group
        "56",  # Specialized Stand-Alone Plan
        "59",  # Other Private Insurance
        "61",  # BC Managed Care
        "62",  # BC Insurance Indemnity
        "71",  # HMO
        "72",  # PPO
        "73",  # POS
        "79",  # Other Managed Care
        "81",  # Self-pay (Includes applicants for insurance and Medicaid applicants)
        "82",  # No Charge
        "83",  # Refusal to Pay/Bad Debt
        "84",  # Hill Burton Free Care
        "85",  # Research/Donor
        "89",  # No Payment, Other
        "91",  # Foreign National
        "92",  # Other (Non-government)
        "93",  # Disability Insurance
        "94",  # Long-term Care Insurance
        "95",  # Worker's Compensation
        "96",  # Auto Insurance (includes no fault)
        "97",  # Legal Liability / Liability Insurance
        "98",  # Other specified but not otherwise classifiable (includes Hospice - Unspecified plan)
        "99",  # No Typology Code available for payment source
        "111",  # Medicare HMO
        "112",  # Medicare PPO
        "113",  # Medicare POS
        "119",  # Medicare Managed Care Other
        "121",  # Medicare FFS
        "122",  # Medicare Drug Benefit
        "123",  # Medicare Medical Savings Account (MSA)
        "129",  # Medicare Non-managed Care Other
        "191",  # Medicare Pharmacy Benefit Manager
        "211",  # Medicaid HMO
        "212",  # Medicaid PPO
        "213",  # Medicaid PCCM (Primary Care Case Management)
        "219",  # Medicaid Managed Care Other
        "291",  # Medicaid Pharmacy Benefit Manager
        "299",  # Medicaid - Dental
        "311",  # TRICARE (CHAMPUS)
        "312",  # Military Treatment Facility
        "313",  # Dental --Stand Alone
        "321",  # Veteran care-Care provided to Veterans
        "322",  # Non-veteran care
        "331",  # Indian Health Service - Regular
        "332",  # Indian Health Service - Contract
        "333",  # Indian Health Service - Managed Care
        "334",  # Indian Tribe - Sponsored Coverage
        "341",  # Title V (MCH Block Grant)
        "342",  # Migrant Health Program
        "343",  # Ryan White Act
        "349",  # Other
        "361",  # State SCHIP program (codes for individual states)
        "362",  # Specific state programs (list/ local code)
        "369",  # State, not otherwise specified (other state)
        "371",  # Local - Managed care
        "372",  # FFS/Indemnity
        "379",  # Local, not otherwise specified (other local, county)
        "381",  # Federal, State, Local not specified managed care
        "382",  # Federal, State, Local not specified - FFS
        "389",  # Federal, State, Local not specified - Other
        "391",  # Federal Employee Health Plan - Use when known
        "511",  # Commercial Managed Care - HMO
        "512",  # Commercial Managed Care - PPO
        "513",  # Commercial Managed Care - POS
        "514",  # Exclusive Provider Organization
        "515",  # Gatekeeper PPO (GPPO)
        "516",  # Commercial Managed Care - Pharmacy Benefit Manager
        "517",  # Commercial Managed Care - Dental
        "519",  # Managed Care, Other (non HMO)
        "521",  # Commercial Indemnity
        "522",  # Self-insured (ERISA) Administrative Services Only (ASO) plan
        "523",  # Medicare supplemental policy (as second payer)
        "524",  # Indemnity Insurance - Dental
        "529",  # Private health insurance--other commercial Indemnity
        "561",  # Dental
        "562",  # Vision
        "611",  # BC Managed Care - HMO
        "612",  # BC Managed Care - PPO
        "613",  # BC Managed Care - POS
        "614",  # BC Managed Care - Dental
        "619",  # BC Managed Care - Other
        "621",  # BC Indemnity
        "622",  # BC Self-insured (ERISA) Administrative Services Only (ASO)Plan
        "623",  # BC Medicare Supplemental Plan
        "629",  # BC Indemnity - Dental
        "821",  # Charity
        "822",  # Professional Courtesy
        "823",  # Research/Clinical Trial
        "951",  # Worker's Comp HMO
        "953",  # Worker's Comp Fee-for-Service
        "954",  # Worker's Comp Other Managed Care
        "959",  # Worker's Comp, Other unspecified
        "3111",  # TRICARE Prime--HMO
        "3112",  # TRICARE Extra--PPO
        "3113",  # TRICARE Standard - Fee For Service
        "3114",  # TRICARE For Life--Medicare Supplement
        "3115",  # TRICARE Reserve Select
        "3116",  # Uniformed Services Family Health Plan (USFHP) -- HMO
        "3119",  # Department of Defense - (other)
        "3121",  # Enrolled Prime--HMO
        "3122",  # Non-enrolled Space Available
        "3123",  # TRICARE For Life (TFL)
        "3211",  # Direct Care-Care provided in VA facilities
        "3212",  # Indirect Care-Care provided outside VA facilities
        "3221",  # Civilian Health and Medical Program for the VA (CHAMPVA)
        "3222",  # Spina Bifida Health Care Program (SB)
        "3223",  # Children of Women Vietnam Veterans (CWVV)
        "3229",  # Other non-veteran care
        "3711",  # HMO
        "3712",  # PPO
        "3713",  # POS
        "3811",  # Federal, State, Local not specified - HMO
        "3812",  # Federal, State, Local not specified - PPO
        "3813",  # Federal, State, Local not specified - POS
        "3819",  # Federal, State, Local not specified - not specified managed care
        "9999",  # Unavailable / No Payer Specified / Blank
        "32121",  # Fee Basis
        "32122",  # Foreign Fee/Foreign Medical Program (FMP)
        "32123",  # Contract Nursing Home/Community Nursing Home
        "32124",  # State Veterans Home
        "32125",  # Sharing Agreements
        "32126",  # Other Federal Agency
        "32127",  # Dental Care
        "32128",  # Vision Care
    }


class Race(ValueSet):
    """Race value set.

    **Clinical Focus:**

    **Data Element Scope:**

    **Inclusion Criteria:**

    **Exclusion Criteria:**

    ** Used in:** CMS135v10, CMS90v11, CMS249v4, CMS159v10, CMS349v4, CMS69v10, CMS142v10, CMS134v10, CMS177v10, CMS165v10, CMS143v10, CMS146v10, CMS157v10, CMS124v10, CMS2v11, CMS50v10, CMS22v10, CMS68v11, CMS139v10, CMS129v11, CMS154v10, CMS161v10, CMS56v10, CMS74v11, CMS645v5, CMS138v10, CMS75v10, CMS137v10, CMS136v11, CMS128v10, CMS122v10, CMS153v10, CMS144v10, CMS66v10, CMS130v10, CMS646v2, CMS155v10, CMS127v10, CMS771v3, CMS117v10, CMS131v10, CMS149v10, CMS347v5, CMS133v10, CMS156v10, CMS147v11, CMS125v10, CMS145v10
    """

    VALUE_SET_NAME = "Race"
    OID = "2.16.840.1.114222.4.11.836"
    DEFINITION_VERSION = "20121025"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CDCREC = {
        "1002-5",  # American Indian or Alaska Native
        "2028-9",  # Asian
        "2054-5",  # Black or African American
        "2076-8",  # Native Hawaiian or Other Pacific Islander
        "2106-3",  # White
        "2131-1",  # Other Race
    }


class Female(ValueSet):
    """Female Gender value set.

    **Clinical Focus:** Concepts that represent Female when assessing quality measures

    **Data Element Scope:** Gender

    **Inclusion Criteria:** Appropriate female gender concepts

    **Exclusion Criteria:** Concepts representing Male gender

    ** Used in:** CMS124v10, CMS153v10, CMS125v10, CMS249v4
    """

    VALUE_SET_NAME = "Female"
    OID = "2.16.840.1.113883.3.560.100.2"
    DEFINITION_VERSION = "20160331"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    ADMINISTRATIVEGENDER = {
        "F",  # Female
    }


class White(ValueSet):
    """White Race value set.

    **Clinical Focus:** The purpose of this value set is to represent concepts for the patient characteristic of white race.

    **Data Element Scope:** This value set may use a model element related to Race.

    **Inclusion Criteria:** Includes concepts that represent a patient characteristic of white race.

    **Exclusion Criteria:** Excludes concepts that represent non-white race.

    ** Used in:** CMS249v4
    """

    VALUE_SET_NAME = "White"
    OID = "2.16.840.1.113883.3.464.1003.123.12.1007"
    DEFINITION_VERSION = "20180321"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CDCREC = {
        "2106-3",  # White
    }


__exports__ = get_overrides(locals().copy())
