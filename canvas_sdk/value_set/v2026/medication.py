from ..value_set import ValueSet


class DementiaMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for dementia medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable dementia medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS131v14
    """

    VALUE_SET_NAME = "Dementia Medications"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1510"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1100184",  # donepezil hydrochloride 23 MG Oral Tablet
        "1308569",  # 24 HR rivastigmine 0.554 MG/HR Transdermal System
        "1599803",  # 24 HR donepezil hydrochloride 10 MG / memantine hydrochloride 28 MG Extended Release Oral Capsule
        "1599805",  # 24 HR donepezil hydrochloride 10 MG / memantine hydrochloride 14 MG Extended Release Oral Capsule
        "1805420",  # 24 HR donepezil hydrochloride 10 MG / memantine hydrochloride 21 MG Extended Release Oral Capsule
        "1805425",  # 24 HR donepezil hydrochloride 10 MG / memantine hydrochloride 7 MG Extended Release Oral Capsule
        "1858970",  # {7 (24 HR donepezil hydrochloride 10 MG / memantine hydrochloride 14 MG Extended Release Oral Capsule) / 7 (24 HR donepezil hydrochloride 10 MG / memantine hydrochloride 21 MG Extended Release Oral Capsule) / 7 (24 HR donepezil hydrochloride 10 MG / memantine hydrochloride 28 MG Extended Release Oral Capsule) / 7 (24 HR donepezil hydrochloride 10 MG / memantine hydrochloride 7 MG Extended Release Oral Capsule)} Pack
        "310436",  # galantamine 4 MG Oral Tablet
        "310437",  # galantamine 8 MG Oral Tablet
        "312835",  # rivastigmine 3 MG Oral Capsule
        "312836",  # rivastigmine 6 MG Oral Capsule
        "314214",  # rivastigmine 1.5 MG Oral Capsule
        "314215",  # rivastigmine 4.5 MG Oral Capsule
        "579148",  # galantamine 12 MG Oral Tablet
        "725021",  # 24 HR rivastigmine 0.192 MG/HR Transdermal System
        "725023",  # 24 HR rivastigmine 0.396 MG/HR Transdermal System
        "860695",  # 24 HR galantamine hydrobromide 16 MG Extended Release Oral Capsule
        "860707",  # 24 HR galantamine hydrobromide 24 MG Extended Release Oral Capsule
        "860715",  # 24 HR galantamine hydrobromide 8 MG Extended Release Oral Capsule
        "860901",  # galantamine hydrobromide 4 MG/ML Oral Solution
        "996561",  # memantine hydrochloride 10 MG Oral Tablet
        "996571",  # memantine hydrochloride 5 MG Oral Tablet
        "996572",  # {21 (memantine hydrochloride 10 MG Oral Tablet) / 28 (memantine hydrochloride 5 MG Oral Tablet)} Pack
        "996594",  # 24 HR memantine hydrochloride 14 MG Extended Release Oral Capsule
        "996603",  # 24 HR memantine hydrochloride 21 MG Extended Release Oral Capsule
        "996609",  # 24 HR memantine hydrochloride 28 MG Extended Release Oral Capsule
        "996615",  # 24 HR memantine hydrochloride 7 MG Extended Release Oral Capsule
        "996624",  # {7 (24 HR memantine hydrochloride 14 MG Extended Release Oral Capsule) / 7 (24 HR memantine hydrochloride 21 MG Extended Release Oral Capsule) / 7 (24 HR memantine hydrochloride 28 MG Extended Release Oral Capsule) / 7 (24 HR memantine hydrochloride 7 MG Extended Release Oral Capsule)} Pack
        "996740",  # memantine hydrochloride 2 MG/ML Oral Solution
        "997220",  # donepezil hydrochloride 10 MG Disintegrating Oral Tablet
        "997223",  # donepezil hydrochloride 10 MG Oral Tablet
        "997226",  # donepezil hydrochloride 5 MG Disintegrating Oral Tablet
        "997229",  # donepezil hydrochloride 5 MG Oral Tablet
    }


__exports__ = (DementiaMedications,)