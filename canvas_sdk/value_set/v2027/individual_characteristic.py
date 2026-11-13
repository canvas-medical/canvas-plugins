from ..value_set import ValueSet


class Ethnicity(ValueSet):
    """
    **Clinical Focus:** 

    **Data Element Scope:** 

    **Inclusion Criteria:** 

    **Exclusion Criteria:** 

    **Used in:** CMS2v16, CMS22v15, CMS50v15, CMS56v15, CMS68v16, CMS69v15, CMS71v16, CMS72v15, CMS74v16, CMS75v15, CMS90v16, CMS104v15, CMS108v15, CMS117v15, CMS122v15, CMS124v15, CMS125v15, CMS128v15, CMS129v16, CMS130v15, CMS131v15, CMS133v15, CMS135v15, CMS136v16, CMS137v15, CMS138v15, CMS139v15, CMS142v15, CMS143v15, CMS144v15, CMS146v15, CMS149v15, CMS153v15, CMS154v15, CMS155v15, CMS156v15, CMS157v15, CMS159v15, CMS165v15, CMS177v15, CMS190v15, CMS314v4, CMS334v8, CMS347v10, CMS349v9, CMS506v9, CMS529v7, CMS645v10, CMS646v7, CMS771v8, CMS816v6, CMS819v5, CMS826v4, CMS832v4, CMS844v7, CMS871v6, CMS951v5, CMS986v6, CMS996v7, CMS1017v3, CMS1028v5, CMS1056v4, CMS1061v1, CMS1074v4, CMS1154v2, CMS1157v3, CMS1173v2, CMS1188v4, CMS1206v4, CMS1218v3, CMS1244v2, CMS1264v2, CMS1317v1
    """

    VALUE_SET_NAME = "Ethnicity"
    OID = "2.16.840.1.114222.4.11.837"
    DEFINITION_VERSION = "20121025"
    EXPANSION_VERSION = "eCQM Update 2026-05-14"

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

    **Used in:** CMS2v16, CMS22v15, CMS50v15, CMS56v15, CMS68v16, CMS69v15, CMS71v16, CMS72v15, CMS74v16, CMS75v15, CMS90v16, CMS104v15, CMS108v15, CMS117v15, CMS122v15, CMS124v15, CMS125v15, CMS128v15, CMS129v16, CMS130v15, CMS131v15, CMS133v15, CMS135v15, CMS136v16, CMS137v15, CMS138v15, CMS139v15, CMS142v15, CMS143v15, CMS144v15, CMS146v15, CMS149v15, CMS153v15, CMS154v15, CMS155v15, CMS156v15, CMS157v15, CMS159v15, CMS165v15, CMS177v15, CMS190v15, CMS314v4, CMS334v8, CMS347v10, CMS349v9, CMS506v9, CMS529v7, CMS645v10, CMS646v7, CMS771v8, CMS816v6, CMS819v5, CMS826v4, CMS832v4, CMS844v7, CMS871v6, CMS951v5, CMS986v6, CMS996v7, CMS1017v3, CMS1028v5, CMS1056v4, CMS1061v1, CMS1074v4, CMS1154v2, CMS1157v3, CMS1173v2, CMS1188v4, CMS1206v4, CMS1218v3, CMS1244v2, CMS1264v2, CMS1317v1
    """

    VALUE_SET_NAME = "Federal Administrative Sex"
    OID = "2.16.840.1.113762.1.4.1021.121"
    DEFINITION_VERSION = "20250228"
    EXPANSION_VERSION = "eCQM Update 2026-05-14"

    SNOMEDCT = {
        "248152002",  # Female (finding)
        "248153007",  # Male (finding)
    }


class MedicareAdvantagePayer(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to identify concepts for Medicare Advantage payer types.

    **Data Element Scope:** This value set may use a model element related to Patient Characteristic.

    **Inclusion Criteria:** Includes concepts that identify a patient with Medicare Advantage as a payer source.

    **Exclusion Criteria:** Excludes concepts that represent Medicare Fee-For-Service as a payer source.

    **Used in:** CMS529v7, CMS844v7
    """

    VALUE_SET_NAME = "Medicare Advantage Payer"
    OID = "2.16.840.1.113762.1.4.1104.12"
    DEFINITION_VERSION = "20230214"
    EXPANSION_VERSION = "eCQM Update 2026-05-14"

    SOPT = {
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

    **Used in:** CMS529v7, CMS844v7
    """

    VALUE_SET_NAME = "Medicare FFS Payer"
    OID = "2.16.840.1.113762.1.4.1104.10"
    DEFINITION_VERSION = "20230214"
    EXPANSION_VERSION = "eCQM Update 2026-05-14"

    SOPT = {
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


class PayerType(ValueSet):
    """
    **Clinical Focus:** Categories of types of health care payer entities as defined by the Centers for Disease Control and Prevention National Center for Health Statistics Source of Payment Codes.

    **Data Element Scope:** Concepts intended to represent categories of insurance (payer) types.

    **Inclusion Criteria:** Codes representing high level categories of insurance (payer) types

    **Exclusion Criteria:** Codes representing, subdivisions of insurance categories and or specific private insurance companies

    **Used in:** CMS2v16, CMS22v15, CMS50v15, CMS56v15, CMS68v16, CMS69v15, CMS71v16, CMS72v15, CMS74v16, CMS75v15, CMS90v16, CMS104v15, CMS108v15, CMS117v15, CMS122v15, CMS124v15, CMS125v15, CMS128v15, CMS129v16, CMS130v15, CMS131v15, CMS133v15, CMS135v15, CMS136v16, CMS137v15, CMS138v15, CMS139v15, CMS142v15, CMS143v15, CMS144v15, CMS146v15, CMS149v15, CMS153v15, CMS154v15, CMS155v15, CMS156v15, CMS157v15, CMS159v15, CMS165v15, CMS177v15, CMS190v15, CMS314v4, CMS334v8, CMS347v10, CMS349v9, CMS506v9, CMS529v7, CMS645v10, CMS646v7, CMS771v8, CMS816v6, CMS819v5, CMS826v4, CMS832v4, CMS844v7, CMS871v6, CMS951v5, CMS986v6, CMS996v7, CMS1017v3, CMS1028v5, CMS1056v4, CMS1061v1, CMS1074v4, CMS1154v2, CMS1157v3, CMS1173v2, CMS1188v4, CMS1206v4, CMS1218v3, CMS1244v2, CMS1264v2, CMS1317v1
    """

    VALUE_SET_NAME = "Payer Type"
    OID = "2.16.840.1.114222.4.11.3591"
    DEFINITION_VERSION = "20250419"
    EXPANSION_VERSION = "eCQM Update 2026-05-14"

    SOPT = {
        "1",  # MEDICARE
        "11",  # Medicare Managed Care (Includes Medicare Advantage Plans)
        "1111",  # Medicare Chronic Condition Special Needs Plan (C-SNP)
        "112",  # Medicare PPO
        "113",  # Medicare POS
        "119",  # Medicare Managed Care Other
        "12",  # Medicare (Non-managed Care)
        "121",  # Medicare FFS
        "122",  # Medicare Drug Benefit
        "123",  # Medicare Medical Savings Account (MSA)
        "129",  # Medicare Non-managed Care Other
        "13",  # Medicare Hospice
        "14",  # Dual Eligibility Medicare/Medicaid Organization
        "141",  # Dual Eligible Special Needs Plan (D-SNP)
        "142",  # Fully Integrated Dual Eligible Special Needs Plan (FIDE-SNP)
        "19",  # Medicare Other
        "191",  # Medicare Pharmacy Benefit Manager
        "2",  # MEDICAID
        "21",  # Medicaid (Managed Care)
        "211",  # Medicaid HMO
        "212",  # Medicaid PPO
        "213",  # Medicaid PCCM (Primary Care Case Management)
        "219",  # Medicaid Managed Care Other
        "22",  # Medicaid (Non-managed Care Plan)
        "23",  # Medicaid/SCHIP
        "25",  # Medicaid - Out of State
        "26",  # Medicaid - Long Term Care
        "29",  # Medicaid Other
        "291",  # Medicaid Pharmacy Benefit Manager
        "299",  # Medicaid - Dental
        "3",  # OTHER GOVERNMENT (Federal/State/Local) (excluding Department of Corrections)
        "31",  # Department of Defense
        "311",  # TRICARE (CHAMPUS)
        "3113",  # TRICARE Standard - Fee For Service
        "312",  # Military Treatment Facility
        "3123",  # TRICARE For Life (TFL)
        "313",  # Dental --Stand Alone
        "32",  # Department of Veterans Affairs
        "321",  # Veteran care-Care provided to Veterans
        "322",  # Non-veteran care
        "3221",  # Civilian Health and Medical Program for the VA (CHAMPVA)
        "33",  # Indian Health Service or Tribe
        "331",  # Indian Health Service - Regular
        "332",  # Indian Health Service - Contract
        "333",  # Indian Health Service - Managed Care
        "334",  # Indian Tribe - Sponsored Coverage
        "34",  # HRSA Program
        "341",  # Title V (MCH Block Grant)
        "342",  # Migrant Health Program
        "343",  # Ryan White Act
        "344",  # Disaster-related (includes Covid-19)
        "349",  # Other
        "35",  # Black Lung
        "36",  # State Government
        "361",  # State SCHIP program (codes for individual states)
        "362",  # Specific state programs (list/ local code)
        "369",  # State, not otherwise specified (other state)
        "37",  # Local Government
        "371",  # Local - Managed care
        "372",  # FFS/Indemnity
        "379",  # Local, not otherwise specified (other local, county)
        "38",  # Other Government (Federal, State, Local not specified)
        "381",  # Federal, State, Local not specified managed care
        "382",  # Federal, State, Local not specified - FFS
        "389",  # Federal, State, Local not specified - Other
        "39",  # Other Federal
        "391",  # Federal Employee Health Plan - Use when known
        "4",  # DEPARTMENTS OF CORRECTIONS
        "41",  # Corrections Federal
        "42",  # Corrections State
        "43",  # Corrections Local
        "44",  # Corrections Unknown Level
        "5",  # PRIVATE HEALTH INSURANCE
        "51",  # Managed Care (Private)
        "511",  # Commercial Managed Care - HMO
        "512",  # Commercial Managed Care - PPO
        "513",  # Commercial Managed Care - POS
        "514",  # Exclusive Provider Organization
        "515",  # Gatekeeper PPO (GPPO)
        "516",  # Commercial Managed Care - Pharmacy Benefit Manager
        "517",  # Commercial Managed Care - Dental
        "519",  # Managed Care, Other (non HMO)
        "52",  # Private Health Insurance - Indemnity
        "521",  # Commercial Indemnity
        "522",  # Self-insured (ERISA) Administrative Services Only (ASO) plan
        "523",  # Medicare supplemental policy (as second payer)
        "524",  # Indemnity Insurance - Dental
        "529",  # Private health insurance--other commercial Indemnity
        "53",  # Managed Care (private) or private health insurance (indemnity), not otherwise specified
        "54",  # Organized Delivery System
        "55",  # Small Employer Purchasing Group
        "56",  # Specialized Stand-Alone Plan
        "561",  # Dental
        "562",  # Vision
        "59",  # Other Private Insurance
        "7",  # MANAGED CARE, UNSPECIFIED (to be used only if one can't distinguish public from private)
        "71",  # HMO
        "72",  # PPO
        "73",  # POS
        "79",  # Other Managed Care
        "8",  # NO PAYMENT from an Organization/Agency/Program/Private Payer Listed
        "81",  # Self-pay (Includes applicants for insurance and Medicaid applicants)
        "82",  # No Charge
        "821",  # Charity
        "822",  # Professional Courtesy
        "823",  # Research/Clinical Trial
        "83",  # Refusal to Pay/Bad Debt
        "84",  # Hill Burton Free Care
        "85",  # Research/Donor
        "89",  # No Payment, Other
        "9",  # MISCELLANEOUS/OTHER
        "91",  # Foreign National
        "92",  # Other (Non-government)
        "93",  # Disability Insurance
        "94",  # Long-term Care Insurance
        "95",  # Worker's Compensation
        "951",  # Worker's Comp HMO
        "953",  # Worker's Comp Fee-for-Service
        "954",  # Worker's Comp Other Managed Care
        "959",  # Worker's Comp, Other unspecified
        "96",  # Auto Insurance (includes no fault)
        "97",  # Legal Liability / Liability Insurance
        "98",  # Other specified but not otherwise classifiable (includes Hospice - Unspecified plan)
        "99",  # No Typology Code available for payment source
        "9999",  # Unavailable / No Payer Specified / Blank
    }


class Race(ValueSet):
    """
    **Clinical Focus:** 

    **Data Element Scope:** 

    **Inclusion Criteria:** 

    **Exclusion Criteria:** 

    **Used in:** CMS2v16, CMS22v15, CMS50v15, CMS56v15, CMS68v16, CMS69v15, CMS71v16, CMS72v15, CMS74v16, CMS75v15, CMS90v16, CMS104v15, CMS108v15, CMS117v15, CMS122v15, CMS124v15, CMS125v15, CMS128v15, CMS129v16, CMS130v15, CMS131v15, CMS133v15, CMS135v15, CMS136v16, CMS137v15, CMS138v15, CMS139v15, CMS142v15, CMS143v15, CMS144v15, CMS146v15, CMS149v15, CMS153v15, CMS154v15, CMS155v15, CMS156v15, CMS157v15, CMS159v15, CMS165v15, CMS177v15, CMS190v15, CMS314v4, CMS334v8, CMS347v10, CMS349v9, CMS506v9, CMS529v7, CMS645v10, CMS646v7, CMS771v8, CMS816v6, CMS819v5, CMS826v4, CMS832v4, CMS844v7, CMS871v6, CMS951v5, CMS986v6, CMS996v7, CMS1017v3, CMS1028v5, CMS1056v4, CMS1061v1, CMS1074v4, CMS1154v2, CMS1157v3, CMS1173v2, CMS1188v4, CMS1206v4, CMS1218v3, CMS1244v2, CMS1264v2, CMS1317v1
    """

    VALUE_SET_NAME = "Race"
    OID = "2.16.840.1.114222.4.11.836"
    DEFINITION_VERSION = "20121025"
    EXPANSION_VERSION = "eCQM Update 2026-05-14"

    CDCREC = {
        "1002-5",  # AMERICAN INDIAN OR ALASKA NATIVE
        "2028-9",  # Asian
        "2054-5",  # Black or African American
        "2076-8",  # Native Hawaiian or Other Pacific Islander
        "2106-3",  # White
        "2131-1",  # Other Race
    }


__exports__ = (
    "Ethnicity",
    "FederalAdministrativeSex",
    "MedicareAdvantagePayer",
    "MedicareFfsPayer",
    "PayerType",
    "Race",
)
