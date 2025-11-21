from ..value_set import ValueSet


class Ethnicity(ValueSet):
    """

    **Clinical Focus:**

    **Data Element Scope:**

    **Inclusion Criteria:**

    **Exclusion Criteria:**

    ** Used in:** CMS131v14
    """

    VALUE_SET_NAME = "Ethnicity"
    OID = "2.16.840.1.114222.4.11.837"
    DEFINITION_VERSION = "20121025"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CDCREC = {
        "2135-2",  # Hispanic or Latino
        "2186-5",  # Not Hispanic or Latino
    }


class FederalAdministrativeSex(ValueSet):
    """

    **Clinical Focus:** SNOMED CT representations of sex values aligned with US federal administrative requirements across all systems, including quality measure use

    **Data Element Scope:** Patient characteristics

    **Inclusion Criteria:** Limited set of SNOMED CT representations of sex values.

    **Exclusion Criteria:** 

    ** Used in:** CMS131v14
    """

    VALUE_SET_NAME = "Federal Administrative Sex"
    OID = "2.16.840.1.113762.1.4.1021.121"
    DEFINITION_VERSION = "20250228"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "248152002",  # Female (finding)
        "248153007",  # Male (finding)
    }


class PayerType(ValueSet):
    """
    **Clinical Focus:** Categories of types of health care payer entities as defined by the US Public Health Data Consortium SOP code system

    **Data Element Scope:** @code in CCDA r2.1 template Planned Coverage [act: identifier urn:oid:2.16.840.1.113883.10.20.22.4.129 (open)] DYNAMIC

    **Inclusion Criteria:** All codes in the code system

    **Exclusion Criteria:** None

    ** Used in:** CMS131v14
    """

    VALUE_SET_NAME = "Payer Type"
    OID = "2.16.840.1.114222.4.11.3591"
    DEFINITION_VERSION = "20221118"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SOP = {
        "1",      # MEDICARE
        "2",      # MEDICAID
        "3",      # OTHER GOVERNMENT (Federal/State/Local) (excluding Department of Corrections)
        "4",      # DEPARTMENTS OF CORRECTIONS
        "5",      # PRIVATE HEALTH INSURANCE
        "6",      # BLUE CROSS/BLUE SHIELD
        "7",      # MANAGED CARE, UNSPECIFIED (cannot distinguish public from private)
        "8",      # NO PAYMENT from an Organization/Agency/Program/Private Payer Listed
        "9",      # MISCELLANEOUS/OTHER
        "11",     # Medicare Managed Care (Includes Medicare Advantage Plans)
        "12",     # Medicare (Non-managed Care)
        "13",     # Medicare Hospice
        "14",     # Dual Eligibility Medicare/Medicaid Organization
        "19",     # Medicare Other
        "21",     # Medicaid (Managed Care)
        "22",     # Medicaid (Non-managed Care Plan)
        "23",     # Medicaid/SCHIP
        "25",     # Medicaid - Out of State
        "26",     # Medicaid - Long Term Care
        "29",     # Medicaid Other
        "31",     # Department of Defense
        "32",     # Department of Veterans Affairs
        "33",     # Indian Health Service or Tribe
        "34",     # HRSA Program
        "35",     # Black Lung
        "36",     # State Government
        "37",     # Local Government
        "38",     # Other Government (Federal, State, Local not specified)
        "39",     # Other Federal
        "41",     # Corrections Federal
        "42",     # Corrections State
        "43",     # Corrections Local
        "44",     # Corrections Unknown Level
        "51",     # Managed Care (Private)
        "52",     # Private Health Insurance - Indemnity
        "53",     # Managed Care (private) or private health insurance (indemnity), not otherwise specified
        "54",     # Organized Delivery System
        "55",     # Small Employer Purchasing Group
        "56",     # Specialized Stand-Alone Plan
        "59",     # Other Private Insurance
        "61",     # BC Managed Care
        "62",     # BC Insurance Indemnity
        "71",     # HMO (Managed Care, Unspecified)
        "72",     # PPO (Managed Care, Unspecified)
        "73",     # POS (Managed Care, Unspecified)
        "79",     # Other Managed Care
        "81",     # Self-pay (includes applicants for insurance and Medicaid applicants)
        "82",     # No Charge
        "83",     # Refusal to Pay/Bad Debt
        "84",     # Hill Burton Free Care
        "85",     # Research/Donor
        "89",     # No Payment, Other
        "91",     # Foreign National
        "92",     # Other (Non-government)
        "93",     # Disability Insurance
        "94",     # Long-term Care Insurance
        "95",     # Worker's Compensation
        "96",     # Auto Insurance (includes no fault)
        "97",     # Legal Liability / Liability Insurance
        "98",     # Other specified but not otherwise classifiable (includes Hospice - Unspecified plan)
        "99",     # No Typology Code available for payment source
        "111",    # Medicare HMO
        "112",    # Medicare PPO
        "113",    # Medicare POS
        "119",    # Medicare Managed Care Other
        "121",    # Medicare FFS
        "122",    # Medicare Drug Benefit
        "123",    # Medicare Medical Savings Account (MSA)
        "129",    # Medicare Non-managed Care Other
        "141",    # Dual Eligible Special Needs Plan (D-SNP)
        "142",    # Fully Integrated Dual Eligible Special Needs Plan (FIDE-SNP)
        "191",    # Medicare Pharmacy Benefit Manager
        "211",    # Medicaid HMO
        "212",    # Medicaid PPO
        "213",    # Medicaid PCCM (Primary Care Case Management)
        "219",    # Medicaid Managed Care Other
        "291",    # Medicaid Pharmacy Benefit Manager
        "299",    # Medicaid - Dental
        "311",    # TRICARE (CHAMPUS)
        "312",    # Military Treatment Facility
        "313",    # Dental -- Stand Alone
        "321",    # Veteran care - Care provided to Veterans
        "322",    # Non-veteran care
        "331",    # Indian Health Service - Regular
        "332",    # Indian Health Service - Contract
        "333",    # Indian Health Service - Managed Care
        "334",    # Indian Tribe - Sponsored Coverage
        "341",    # Title V (MCH Block Grant)
        "342",    # Migrant Health Program
        "343",    # Ryan White Act
        "344",    # Disaster-related (includes Covid-19)
        "349",    # Other (HRSA Program subcategory)
        "361",    # State SCHIP program (codes for individual states)
        "362",    # Specific state programs (list/local code)
        "369",    # State, not otherwise specified (other state)
        "371",    # Local - Managed care
        "372",    # FFS/Indemnity (Local Government)
        "379",    # Local, not otherwise specified (other local, county)
        "381",    # Federal, State, Local not specified - managed care
        "382",    # Federal, State, Local not specified - FFS
        "389",    # Federal, State, Local not specified - Other
        "391",    # Federal Employee Health Plan - use when known
        "511",    # Commercial Managed Care - HMO
        "512",    # Commercial Managed Care - PPO
        "513",    # Commercial Managed Care - POS
        "514",    # Exclusive Provider Organization
        "515",    # Gatekeeper PPO (GPPO)
        "516",    # Commercial Managed Care - Pharmacy Benefit Manager
        "517",    # Commercial Managed Care - Dental
        "519",    # Managed Care, Other (non HMO)
        "521",    # Commercial Indemnity
        "522",    # Self-insured (ERISA) Administrative Services Only (ASO) plan
        "523",    # Medicare supplemental policy (as second payer)
        "524",    # Indemnity Insurance - Dental
        "529",    # Private health insurance -- other commercial indemnity
        "561",    # Dental (specialized stand-alone plan)
        "562",    # Vision (specialized stand-alone plan)
        "611",    # BC Managed Care - HMO
        "612",    # BC Managed Care - PPO
        "613",    # BC Managed Care - POS
        "614",    # BC Managed Care - Dental
        "619",    # BC Managed Care - Other
        "621",    # BC Indemnity
        "622",    # BC Self-insured (ERISA) Administrative Services Only (ASO) plan
        "623",    # BC Medicare Supplemental Plan
        "821",    # Charity
        "822",    # Professional Courtesy
        "823",    # Research/Clinical Trial
        "951",    # Worker's Comp HMO
        "953",    # Worker's Comp Fee-for-Service
        "954",    # Worker's Comp Other Managed Care
        "959",    # Worker's Comp, Other unspecified
        "1111",   # Medicare Chronic Condition Special Needs Plan (C-SNP)
        "1112",   # Medicare Institutional Special Needs Plan (I-SNP)
        "3111",   # TRICARE Prime -- HMO
        "3112",   # TRICARE Extra -- PPO
        "3113",   # TRICARE Standard - Fee For Service
        "3114",   # TRICARE For Life -- Medicare Supplement
        "3115",   # TRICARE Reserve Select
        "3116",   # Uniformed Services Family Health Plan (USFHP) -- HMO
        "3119",   # Department of Defense - (other)
        "3121",   # Enrolled Prime -- HMO
        "3122",   # Non-enrolled Space Available
        "3123",   # TRICARE For Life (TFL)
        "3211",   # Direct Care - Care provided in VA facilities
        "3212",   # Indirect Care - Care provided outside VA facilities
        "3221",   # Civilian Health and Medical Program for the VA (CHAMPVA)
        "3222",   # Spina Bifida Health Care Program (SB)
        "3223",   # Children of Women Vietnam Veterans (CWVV)
        "3229",   # Other non-veteran care
        "3711",   # HMO (Local - Managed care)
        "3712",   # PPO (Local - Managed care)
        "3713",   # POS (Local - Managed care)
        "3811",   # Federal/State/Local not specified - HMO
        "3812",   # Federal/State/Local not specified - PPO
        "3813",   # Federal/State/Local not specified - POS
        "3819",   # Federal/State/Local not specified - not specified managed care
        "9999",   # Unavailable / No Payer Specified / Blank
        "32121",  # Fee Basis (VA indirect care)
        "32122",  # Foreign Fee/Foreign Medical Program (FMP)
        "32123",  # Contract Nursing Home/Community Nursing Home
        "32124",  # State Veterans Home
        "32125",  # Sharing Agreements
        "32126",  # Other Federal Agency
        "32127",  # Dental Care (VA)
        "32128",  # Vision Care (VA)
    }


class Race(ValueSet):
    """
    **Clinical Focus:** 

    **Data Element Scope:** 

    **Inclusion Criteria:** 

    **Exclusion Criteria:** 

    ** Used in:** CMS131v14
    """

    VALUE_SET_NAME = "Race"
    OID = "2.16.840.1.114222.4.11.836"
    DEFINITION_VERSION = "20121025"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CDCREC = {
        "10025",  # American Indian or Alaska Native
        "20289",  # Asian
        "20545",  # Black or African American
        "20768",  # Native Hawaiian or Other Pacific Islander
        "21063",  # White
        "21311",  # Other Race
    }

class MedicareAdvantagePayer(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to identify concepts for Medicare Advantage payer types.

    **Data Element Scope:** This value set may use a model element related to Patient Characteristic.

    **Inclusion Criteria:** Includes concepts that identify a patient with Medicare Advantage as a payer source.

    **Exclusion Criteria:** Excludes concepts that represent Medicare Fee-For-Service as a payer source.
    """

    VALUE_SET_NAME = "Medicare Advantage Payer"
    OID = "2.16.840.1.113762.1.4.1104.12"
    DEFINITION_VERSION = "20230214"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SOP = {
        "11",  # Medicare Managed Care (Includes Medicare Advantage Plans)
        "111",  # Medicare HMO
        "1111",  # Medicare Chronic Condition Special Needs Plan (C-SNP)
        "1112",  # Medicare Institutional Special Needs Plan (I-SNP)
        "112",  # Medicare PPO
        "113",  # Medicare POS
        "119",  # Medicare Managed Care Other
        "123",  # Medicare Medical Savings Account (MSA)
        "13",  # Medicare Hospice
        "14",  # Dual Eligibility Medicare/Medicaid Organization
        "141",  # Dual Eligible Special Needs Plan (D-SNP)
        "142",  # Fully Integrated Dual Eligible Special Needs Plan (FIDE-SNP)
        "19",  # Medicare Other
        "191",  # Medicare Pharmacy Benefit Manager
    }

class MedicareFfsPayer(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to identify concepts for Medicare Fee-For-Service payer types.

    **Data Element Scope:** This value set may use a model element related to Patient Characteristic.

    **Inclusion Criteria:** Includes concepts that identify a patient with Medicare Fee-For-Service as a payer source.

    **Exclusion Criteria:** Excludes concepts that represent non-Medicare Fee-For-Service as a payer source.
    """

    VALUE_SET_NAME = "Medicare FFS Payer"
    OID = "2.16.840.1.113762.1.4.1104.10"
    DEFINITION_VERSION = "20230214"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SOP = {
        "1",  # MEDICARE
        "12",  # Medicare (Non-managed Care)
        "121",  # Medicare FFS
        "122",  # Medicare Drug Benefit
        "129",  # Medicare Non-managed Care Other
        "13",  # Medicare Hospice
        "14",  # Dual Eligibility Medicare/Medicaid Organization
        "141",  # Dual Eligible Special Needs Plan (D-SNP)
        "142",  # Fully Integrated Dual Eligible Special Needs Plan (FIDE-SNP)
        "19",  # Medicare Other
        "191",  # Medicare Pharmacy Benefit Manager
    }

__exports__ = (
    "Ethnicity",
    "FederalAdministrativeSex",
    "PayerType",
    "Race",
    "MedicareAdvantagePayer",
    "MedicareFfsPayer",
)
