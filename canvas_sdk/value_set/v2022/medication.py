from canvas_sdk.value_set._utilities import get_overrides

from ..value_set import ValueSet


class DementiaMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for dementia medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable dementia medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS134v10, CMS165v10, CMS131v10, CMS122v10, CMS125v10, CMS130v10
    """

    VALUE_SET_NAME = "Dementia Medications"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1510"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
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
        "996594",  # 24 HR memantine hydrochloride 14 MG Extended Release Oral Capsule
        "996603",  # 24 HR memantine hydrochloride 21 MG Extended Release Oral Capsule
        "996609",  # 24 HR memantine hydrochloride 28 MG Extended Release Oral Capsule
        "996615",  # 24 HR memantine hydrochloride 7 MG Extended Release Oral Capsule
        "996740",  # memantine hydrochloride 2 MG/ML Oral Solution
        "997220",  # donepezil hydrochloride 10 MG Disintegrating Oral Tablet
        "997223",  # donepezil hydrochloride 10 MG Oral Tablet
        "997226",  # donepezil hydrochloride 5 MG Disintegrating Oral Tablet
        "997229",  # donepezil hydrochloride 5 MG Oral Tablet
        "1100184",  # donepezil hydrochloride 23 MG Oral Tablet
        "1308569",  # 24 HR rivastigmine 0.554 MG/HR Transdermal System
        "1599803",  # 24 HR donepezil hydrochloride 10 MG / memantine hydrochloride 28 MG Extended Release Oral Capsule
        "1599805",  # 24 HR donepezil hydrochloride 10 MG / memantine hydrochloride 14 MG Extended Release Oral Capsule
        "1805420",  # 24 HR donepezil hydrochloride 10 MG / memantine hydrochloride 21 MG Extended Release Oral Capsule
        "1805425",  # 24 HR donepezil hydrochloride 10 MG / memantine hydrochloride 7 MG Extended Release Oral Capsule
    }


class AntidepressantMedication(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for antidepressant medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable antidepressant medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS128v10
    """

    VALUE_SET_NAME = "Antidepressant Medication"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1213"
    DEFINITION_VERSION = "20210306"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "104837",  # isocarboxazid 10 MG Oral Tablet
        "197363",  # amoxapine 100 MG Oral Tablet
        "197364",  # amoxapine 150 MG Oral Tablet
        "197365",  # amoxapine 25 MG Oral Tablet
        "197366",  # amoxapine 50 MG Oral Tablet
        "198045",  # nortriptyline 10 MG Oral Capsule
        "198046",  # nortriptyline 50 MG Oral Capsule
        "198047",  # nortriptyline 75 MG Oral Capsule
        "200371",  # citalopram 20 MG Oral Tablet
        "248642",  # fluoxetine 20 MG Oral Tablet
        "283406",  # mirtazapine 15 MG Disintegrating Oral Tablet
        "283407",  # mirtazapine 30 MG Disintegrating Oral Tablet
        "283485",  # mirtazapine 45 MG Disintegrating Oral Tablet
        "283672",  # citalopram 10 MG Oral Tablet
        "309313",  # citalopram 2 MG/ML Oral Solution
        "309314",  # citalopram 40 MG Oral Tablet
        "310384",  # fluoxetine 10 MG Oral Capsule
        "310385",  # fluoxetine 20 MG Oral Capsule
        "310386",  # fluoxetine 4 MG/ML Oral Solution
        "311725",  # mirtazapine 15 MG Oral Tablet
        "311726",  # mirtazapine 45 MG Oral Tablet
        "312036",  # nortriptyline 2 MG/ML Oral Solution
        "312242",  # paroxetine hydrochloride 2 MG/ML Oral Suspension
        "312347",  # phenelzine 15 MG Oral Tablet
        "312938",  # sertraline 100 MG Oral Tablet
        "312940",  # sertraline 25 MG Oral Tablet
        "312941",  # sertraline 50 MG Oral Tablet
        "313447",  # tranylcypromine 10 MG Oral Tablet
        "313496",  # trimipramine 100 MG Oral Capsule
        "313498",  # trimipramine 25 MG Oral Capsule
        "313499",  # trimipramine 50 MG Oral Capsule
        "313580",  # venlafaxine 100 MG Oral Tablet
        "313581",  # 24 HR venlafaxine 150 MG Extended Release Oral Capsule
        "313582",  # venlafaxine 25 MG Oral Tablet
        "313583",  # 24 HR venlafaxine 37.5 MG Extended Release Oral Capsule
        "313584",  # venlafaxine 37.5 MG Oral Tablet
        "313585",  # 24 HR venlafaxine 75 MG Extended Release Oral Capsule
        "313586",  # venlafaxine 75 MG Oral Tablet
        "313989",  # fluoxetine 40 MG Oral Capsule
        "313990",  # fluoxetine 10 MG Oral Tablet
        "313995",  # fluoxetine 90 MG Delayed Release Oral Capsule
        "314111",  # mirtazapine 30 MG Oral Tablet
        "314277",  # venlafaxine 50 MG Oral Tablet
        "317136",  # nortriptyline 25 MG Oral Capsule
        "349332",  # escitalopram 10 MG Oral Tablet
        "351249",  # escitalopram 5 MG Oral Tablet
        "351250",  # escitalopram 20 MG Oral Tablet
        "351285",  # escitalopram 1 MG/ML Oral Solution
        "403969",  # fluoxetine 25 MG / olanzapine 6 MG Oral Capsule
        "403970",  # fluoxetine 25 MG / olanzapine 12 MG Oral Capsule
        "403971",  # fluoxetine 50 MG / olanzapine 12 MG Oral Capsule
        "403972",  # fluoxetine 50 MG / olanzapine 6 MG Oral Capsule
        "476809",  # mirtazapine 7.5 MG Oral Tablet
        "596926",  # duloxetine 20 MG Delayed Release Oral Capsule
        "596930",  # duloxetine 30 MG Delayed Release Oral Capsule
        "596934",  # duloxetine 60 MG Delayed Release Oral Capsule
        "616402",  # duloxetine 40 MG Delayed Release Oral Capsule
        "721787",  # fluoxetine 25 MG / olanzapine 3 MG Oral Capsule
        "790264",  # 24 HR desvenlafaxine 100 MG Extended Release Oral Tablet
        "790288",  # 24 HR desvenlafaxine 50 MG Extended Release Oral Tablet
        "808744",  # 24 HR venlafaxine 150 MG Extended Release Oral Tablet
        "808748",  # 24 HR venlafaxine 225 MG Extended Release Oral Tablet
        "808751",  # 24 HR venlafaxine 37.5 MG Extended Release Oral Tablet
        "808753",  # 24 HR venlafaxine 75 MG Extended Release Oral Tablet
        "835564",  # imipramine hydrochloride 25 MG Oral Tablet
        "835568",  # imipramine hydrochloride 50 MG Oral Tablet
        "835572",  # imipramine pamoate 75 MG Oral Capsule
        "835577",  # imipramine pamoate 150 MG Oral Capsule
        "835589",  # imipramine pamoate 125 MG Oral Capsule
        "835591",  # imipramine pamoate 100 MG Oral Capsule
        "835593",  # imipramine hydrochloride 10 MG Oral Tablet
        "856364",  # trazodone hydrochloride 150 MG Oral Tablet
        "856369",  # trazodone hydrochloride 300 MG Oral Tablet
        "856373",  # trazodone hydrochloride 100 MG Oral Tablet
        "856377",  # trazodone hydrochloride 50 MG Oral Tablet
        "856706",  # amitriptyline hydrochloride 10 MG / perphenazine 2 MG Oral Tablet
        "856720",  # amitriptyline hydrochloride 10 MG / perphenazine 4 MG Oral Tablet
        "856762",  # amitriptyline hydrochloride 100 MG Oral Tablet
        "856769",  # amitriptyline hydrochloride 12.5 MG / chlordiazepoxide 5 MG Oral Tablet
        "856773",  # amitriptyline hydrochloride 150 MG Oral Tablet
        "856783",  # amitriptyline hydrochloride 10 MG Oral Tablet
        "856792",  # amitriptyline hydrochloride 25 MG / chlordiazepoxide 10 MG Oral Tablet
        "856797",  # amitriptyline hydrochloride 25 MG / perphenazine 2 MG Oral Tablet
        "856825",  # amitriptyline hydrochloride 25 MG / perphenazine 4 MG Oral Tablet
        "856834",  # amitriptyline hydrochloride 25 MG Oral Tablet
        "856840",  # amitriptyline hydrochloride 50 MG / perphenazine 4 MG Oral Tablet
        "856845",  # amitriptyline hydrochloride 50 MG Oral Tablet
        "856853",  # amitriptyline hydrochloride 75 MG Oral Tablet
        "857297",  # clomipramine hydrochloride 25 MG Oral Capsule
        "857301",  # clomipramine hydrochloride 50 MG Oral Capsule
        "857305",  # clomipramine hydrochloride 75 MG Oral Capsule
        "859186",  # selegiline hydrochloride 5 MG Oral Capsule
        "859190",  # selegiline hydrochloride 1.25 MG Disintegrating Oral Tablet
        "859193",  # selegiline hydrochloride 5 MG Oral Tablet
        "861064",  # sertraline 20 MG/ML Oral Solution
        "865206",  # 24 HR selegiline 0.25 MG/HR Transdermal System
        "865210",  # 24 HR selegiline 0.375 MG/HR Transdermal System
        "865214",  # 24 HR selegiline 0.5 MG/HR Transdermal System
        "898697",  # 24 HR trazodone hydrochloride 150 MG Extended Release Oral Tablet
        "898704",  # 24 HR trazodone hydrochloride 300 MG Extended Release Oral Tablet
        "903873",  # 24 HR fluvoxamine maleate 100 MG Extended Release Oral Capsule
        "903879",  # 24 HR fluvoxamine maleate 150 MG Extended Release Oral Capsule
        "903884",  # fluvoxamine maleate 100 MG Oral Tablet
        "903887",  # fluvoxamine maleate 25 MG Oral Tablet
        "903891",  # fluvoxamine maleate 50 MG Oral Tablet
        "905168",  # protriptyline hydrochloride 10 MG Oral Tablet
        "905172",  # protriptyline hydrochloride 5 MG Oral Tablet
        "993503",  # 12 HR bupropion hydrochloride 100 MG Extended Release Oral Tablet
        "993518",  # 12 HR bupropion hydrochloride 150 MG Extended Release Oral Tablet
        "993536",  # 12 HR bupropion hydrochloride 200 MG Extended Release Oral Tablet
        "993541",  # 24 HR bupropion hydrochloride 150 MG Extended Release Oral Tablet
        "993550",  # 24 HR bupropion hydrobromide 174 MG Extended Release Oral Tablet
        "993557",  # 24 HR bupropion hydrochloride 300 MG Extended Release Oral Tablet
        "993567",  # 24 HR bupropion hydrobromide 348 MG Extended Release Oral Tablet
        "993681",  # 24 HR bupropion hydrobromide 522 MG Extended Release Oral Tablet
        "993687",  # bupropion hydrochloride 100 MG Oral Tablet
        "993691",  # bupropion hydrochloride 75 MG Oral Tablet
        "1000048",  # doxepin hydrochloride 10 MG Oral Capsule
        "1000054",  # doxepin hydrochloride 10 MG/ML Oral Solution
        "1000058",  # doxepin hydrochloride 100 MG Oral Capsule
        "1000064",  # doxepin hydrochloride 150 MG Oral Capsule
        "1000070",  # doxepin hydrochloride 25 MG Oral Capsule
        "1000076",  # doxepin hydrochloride 50 MG Oral Capsule
        "1000097",  # doxepin hydrochloride 75 MG Oral Capsule
        "1086772",  # vilazodone hydrochloride 10 MG Oral Tablet
        "1086778",  # vilazodone hydrochloride 20 MG Oral Tablet
        "1086784",  # vilazodone hydrochloride 40 MG Oral Tablet
        "1098649",  # nefazodone hydrochloride 100 MG Oral Tablet
        "1098666",  # nefazodone hydrochloride 150 MG Oral Tablet
        "1098670",  # nefazodone hydrochloride 200 MG Oral Tablet
        "1098674",  # nefazodone hydrochloride 250 MG Oral Tablet
        "1098678",  # nefazodone hydrochloride 50 MG Oral Tablet
        "1099288",  # desipramine hydrochloride 10 MG Oral Tablet
        "1099292",  # desipramine hydrochloride 100 MG Oral Tablet
        "1099296",  # desipramine hydrochloride 150 MG Oral Tablet
        "1099300",  # desipramine hydrochloride 25 MG Oral Tablet
        "1099304",  # desipramine hydrochloride 50 MG Oral Tablet
        "1099316",  # desipramine hydrochloride 75 MG Oral Tablet
        "1190110",  # fluoxetine 60 MG Oral Tablet
        "1232585",  # 24 HR bupropion hydrochloride 450 MG Extended Release Oral Tablet
        "1298857",  # maprotiline hydrochloride 25 MG Oral Tablet
        "1298861",  # maprotiline hydrochloride 50 MG Oral Tablet
        "1298870",  # maprotiline hydrochloride 75 MG Oral Tablet
        "1430122",  # paroxetine mesylate 7.5 MG Oral Capsule
        "1433217",  # 24 HR levomilnacipran 120 MG Extended Release Oral Capsule
        "1433227",  # 24 HR levomilnacipran 20 MG Extended Release Oral Capsule
        "1433233",  # 24 HR levomilnacipran 40 MG Extended Release Oral Capsule
        "1433239",  # 24 HR levomilnacipran 80 MG Extended Release Oral Capsule
        "1439808",  # vortioxetine 10 MG Oral Tablet
        "1439810",  # vortioxetine 20 MG Oral Tablet
        "1439812",  # vortioxetine 5 MG Oral Tablet
        "1607617",  # 24 HR desvenlafaxine succinate 25 MG Extended Release Oral Tablet
        "1738483",  # paroxetine hydrochloride 10 MG Oral Tablet
        "1738495",  # paroxetine hydrochloride 20 MG Oral Tablet
        "1738503",  # paroxetine hydrochloride 30 MG Oral Tablet
        "1738511",  # paroxetine hydrochloride 40 MG Oral Tablet
        "1738515",  # paroxetine mesylate 10 MG Oral Tablet
        "1738519",  # paroxetine mesylate 20 MG Oral Tablet
        "1738523",  # paroxetine mesylate 30 MG Oral Tablet
        "1738527",  # paroxetine mesylate 40 MG Oral Tablet
        "1738803",  # 24 HR paroxetine hydrochloride 12.5 MG Extended Release Oral Tablet
        "1738805",  # 24 HR paroxetine hydrochloride 25 MG Extended Release Oral Tablet
        "1738807",  # 24 HR paroxetine hydrochloride 37.5 MG Extended Release Oral Tablet
        "1801289",  # Smoking Cessation 12 HR bupropion hydrochloride 150 MG Extended Release Oral Tablet
        "1874553",  # 24 HR desvenlafaxine succinate 100 MG Extended Release Oral Tablet
        "1874559",  # 24 HR desvenlafaxine succinate 50 MG Extended Release Oral Tablet
    }


class AceInhibitorOrArbOrArni(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of medications of angiotensin-converting enzyme (ACE) inhibitor, angiotensin-receptor blocker (ARB), and angiotensin receptor-neprilysin inhibitor (ARNI) therapies.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for angiotensin-converting enzyme (ACE) inhibitor, angiotensin-receptor blocker (ARB), and angiotensin receptor-neprilysin inhibitor (ARNI) therapies.s diuretic, ACEI plus calcium channel blocker, ARB plus calcium channel blocker, or ARB plus calcium channel blocker plus diuretic.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable branded drugs, components or ingredients.

    ** Used in:** CMS135v10, CMS134v10
    """

    VALUE_SET_NAME = "ACE Inhibitor or ARB or ARNI"
    OID = "2.16.840.1.113883.3.526.3.1139"
    DEFINITION_VERSION = "20210218"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "153822",  # candesartan cilexetil 4 MG Oral Tablet
        "153823",  # candesartan cilexetil 8 MG Oral Tablet
        "197436",  # captopril 25 MG / hydrochlorothiazide 15 MG Oral Tablet
        "197437",  # captopril 25 MG / hydrochlorothiazide 25 MG Oral Tablet
        "197438",  # captopril 50 MG / hydrochlorothiazide 15 MG Oral Tablet
        "197439",  # captopril 50 MG / hydrochlorothiazide 25 MG Oral Tablet
        "197884",  # lisinopril 40 MG Oral Tablet
        "197885",  # hydrochlorothiazide 12.5 MG / lisinopril 10 MG Oral Tablet
        "197886",  # hydrochlorothiazide 12.5 MG / lisinopril 20 MG Oral Tablet
        "197887",  # hydrochlorothiazide 25 MG / lisinopril 20 MG Oral Tablet
        "198188",  # ramipril 2.5 MG Oral Capsule
        "198189",  # ramipril 5 MG Oral Capsule
        "199351",  # trandolapril 2 MG Oral Tablet
        "199352",  # trandolapril 4 MG Oral Tablet
        "199353",  # trandolapril 1 MG Oral Tablet
        "200094",  # irbesartan 75 MG Oral Tablet
        "200095",  # irbesartan 150 MG Oral Tablet
        "200096",  # irbesartan 300 MG Oral Tablet
        "200284",  # hydrochlorothiazide 12.5 MG / valsartan 80 MG Oral Tablet
        "200285",  # hydrochlorothiazide 12.5 MG / valsartan 160 MG Oral Tablet
        "205304",  # telmisartan 40 MG Oral Tablet
        "205305",  # telmisartan 80 MG Oral Tablet
        "205326",  # lisinopril 30 MG Oral Tablet
        "261962",  # ramipril 10 MG Oral Capsule
        "282755",  # telmisartan 20 MG Oral Tablet
        "283316",  # hydrochlorothiazide 12.5 MG / telmisartan 40 MG Oral Tablet
        "283317",  # hydrochlorothiazide 12.5 MG / telmisartan 80 MG Oral Tablet
        "308962",  # captopril 100 MG Oral Tablet
        "308963",  # captopril 12.5 MG Oral Tablet
        "308964",  # captopril 50 MG Oral Tablet
        "310140",  # eprosartan 600 MG Oral Tablet
        "310792",  # hydrochlorothiazide 12.5 MG / irbesartan 150 MG Oral Tablet
        "310793",  # hydrochlorothiazide 12.5 MG / irbesartan 300 MG Oral Tablet
        "310796",  # hydrochlorothiazide 12.5 MG / quinapril 10 MG Oral Tablet
        "310797",  # hydrochlorothiazide 12.5 MG / quinapril 20 MG Oral Tablet
        "310809",  # hydrochlorothiazide 25 MG / quinapril 20 MG Oral Tablet
        "311353",  # lisinopril 2.5 MG Oral Tablet
        "311354",  # lisinopril 5 MG Oral Tablet
        "312748",  # quinapril 10 MG Oral Tablet
        "312749",  # quinapril 20 MG Oral Tablet
        "312750",  # quinapril 5 MG Oral Tablet
        "314076",  # lisinopril 10 MG Oral Tablet
        "314077",  # lisinopril 20 MG Oral Tablet
        "314203",  # quinapril 40 MG Oral Tablet
        "317173",  # captopril 25 MG Oral Tablet
        "349199",  # valsartan 80 MG Oral Tablet
        "349200",  # valsartan 320 MG Oral Tablet
        "349201",  # valsartan 160 MG Oral Tablet
        "349353",  # hydrochlorothiazide 25 MG / valsartan 160 MG Oral Tablet
        "349373",  # olmesartan medoxomil 5 MG Oral Tablet
        "349401",  # olmesartan medoxomil 20 MG Oral Tablet
        "349405",  # olmesartan medoxomil 40 MG Oral Tablet
        "349483",  # valsartan 40 MG Oral Tablet
        "351292",  # eprosartan 600 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "351293",  # eprosartan 600 MG / hydrochlorothiazide 25 MG Oral Tablet
        "403853",  # hydrochlorothiazide 12.5 MG / olmesartan medoxomil 20 MG Oral Tablet
        "403854",  # hydrochlorothiazide 12.5 MG / olmesartan medoxomil 40 MG Oral Tablet
        "403855",  # hydrochlorothiazide 25 MG / olmesartan medoxomil 40 MG Oral Tablet
        "477130",  # hydrochlorothiazide 25 MG / telmisartan 80 MG Oral Tablet
        "485471",  # hydrochlorothiazide 25 MG / irbesartan 300 MG Oral Tablet
        "577776",  # candesartan cilexetil 16 MG Oral Tablet
        "578325",  # candesartan cilexetil 16 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "578330",  # candesartan cilexetil 32 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "636042",  # hydrochlorothiazide 12.5 MG / valsartan 320 MG Oral Tablet
        "636045",  # hydrochlorothiazide 25 MG / valsartan 320 MG Oral Tablet
        "639537",  # candesartan cilexetil 32 MG Oral Tablet
        "722126",  # amlodipine 10 MG / valsartan 160 MG Oral Tablet
        "722131",  # amlodipine 10 MG / valsartan 320 MG Oral Tablet
        "722134",  # amlodipine 5 MG / valsartan 160 MG Oral Tablet
        "722137",  # amlodipine 5 MG / valsartan 320 MG Oral Tablet
        "730861",  # amlodipine 10 MG / olmesartan medoxomil 20 MG Oral Tablet
        "730866",  # amlodipine 10 MG / olmesartan medoxomil 40 MG Oral Tablet
        "730869",  # amlodipine 5 MG / olmesartan medoxomil 20 MG Oral Tablet
        "730872",  # amlodipine 5 MG / olmesartan medoxomil 40 MG Oral Tablet
        "802749",  # candesartan cilexetil 32 MG / hydrochlorothiazide 25 MG Oral Tablet
        "845488",  # ramipril 1.25 MG Oral Capsule
        "848131",  # amlodipine 10 MG / hydrochlorothiazide 12.5 MG / valsartan 160 MG Oral Tablet
        "848135",  # amlodipine 10 MG / hydrochlorothiazide 25 MG / valsartan 320 MG Oral Tablet
        "848140",  # amlodipine 5 MG / hydrochlorothiazide 12.5 MG / valsartan 160 MG Oral Tablet
        "848145",  # amlodipine 5 MG / hydrochlorothiazide 25 MG / valsartan 160 MG Oral Tablet
        "848151",  # amlodipine 10 MG / hydrochlorothiazide 25 MG / valsartan 160 MG Oral Tablet
        "854925",  # perindopril erbumine 8 MG Oral Tablet
        "854984",  # perindopril erbumine 2 MG Oral Tablet
        "854988",  # perindopril erbumine 4 MG Oral Tablet
        "857166",  # fosinopril sodium 10 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "857169",  # fosinopril sodium 10 MG Oral Tablet
        "857174",  # fosinopril sodium 20 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "857183",  # fosinopril sodium 20 MG Oral Tablet
        "857187",  # fosinopril sodium 40 MG Oral Tablet
        "858804",  # enalapril maleate 2.5 MG Oral Tablet
        "858810",  # enalapril maleate 20 MG Oral Tablet
        "858813",  # enalapril maleate 5 MG Oral Tablet
        "858817",  # enalapril maleate 10 MG Oral Tablet
        "858824",  # enalapril maleate 5 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "858828",  # enalapril maleate 10 MG / hydrochlorothiazide 25 MG Oral Tablet
        "876514",  # amlodipine 10 MG / telmisartan 40 MG Oral Tablet
        "876519",  # amlodipine 10 MG / telmisartan 80 MG Oral Tablet
        "876524",  # amlodipine 5 MG / telmisartan 40 MG Oral Tablet
        "876529",  # amlodipine 5 MG / telmisartan 80 MG Oral Tablet
        "897781",  # 24 HR trandolapril 1 MG / verapamil hydrochloride 240 MG Extended Release Oral Tablet
        "897783",  # 24 HR trandolapril 2 MG / verapamil hydrochloride 180 MG Extended Release Oral Tablet
        "897844",  # 24 HR trandolapril 2 MG / verapamil hydrochloride 240 MG Extended Release Oral Tablet
        "897853",  # 24 HR trandolapril 4 MG / verapamil hydrochloride 240 MG Extended Release Oral Tablet
        "898342",  # amlodipine 10 MG / benazepril hydrochloride 20 MG Oral Capsule
        "898346",  # amlodipine 10 MG / benazepril hydrochloride 40 MG Oral Capsule
        "898350",  # amlodipine 2.5 MG / benazepril hydrochloride 10 MG Oral Capsule
        "898353",  # amlodipine 5 MG / benazepril hydrochloride 10 MG Oral Capsule
        "898356",  # amlodipine 5 MG / benazepril hydrochloride 20 MG Oral Capsule
        "898359",  # amlodipine 5 MG / benazepril hydrochloride 40 MG Oral Capsule
        "898362",  # benazepril hydrochloride 10 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "898367",  # benazepril hydrochloride 20 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "898372",  # benazepril hydrochloride 20 MG / hydrochlorothiazide 25 MG Oral Tablet
        "898378",  # benazepril hydrochloride 5 MG / hydrochlorothiazide 6.25 MG Oral Tablet
        "898687",  # benazepril hydrochloride 10 MG Oral Tablet
        "898690",  # benazepril hydrochloride 20 MG Oral Tablet
        "898719",  # benazepril hydrochloride 40 MG Oral Tablet
        "898723",  # benazepril hydrochloride 5 MG Oral Tablet
        "979464",  # hydrochlorothiazide 12.5 MG / losartan potassium 100 MG Oral Tablet
        "979468",  # hydrochlorothiazide 12.5 MG / losartan potassium 50 MG Oral Tablet
        "979471",  # hydrochlorothiazide 25 MG / losartan potassium 100 MG Oral Tablet
        "979480",  # losartan potassium 100 MG Oral Tablet
        "979485",  # losartan potassium 25 MG Oral Tablet
        "979492",  # losartan potassium 50 MG Oral Tablet
        "999967",  # amlodipine 5 MG / hydrochlorothiazide 12.5 MG / olmesartan medoxomil 20 MG Oral Tablet
        "999986",  # amlodipine 10 MG / hydrochlorothiazide 12.5 MG / olmesartan medoxomil 40 MG Oral Tablet
        "999991",  # amlodipine 10 MG / hydrochlorothiazide 25 MG / olmesartan medoxomil 40 MG Oral Tablet
        "999996",  # amlodipine 5 MG / hydrochlorothiazide 12.5 MG / olmesartan medoxomil 40 MG Oral Tablet
        "1000001",  # amlodipine 5 MG / hydrochlorothiazide 25 MG / olmesartan medoxomil 40 MG Oral Tablet
        "1091646",  # azilsartan medoxomil 40 MG Oral Tablet
        "1091652",  # azilsartan medoxomil 80 MG Oral Tablet
        "1235144",  # azilsartan medoxomil 40 MG / chlorthalidone 12.5 MG Oral Tablet
        "1235151",  # azilsartan medoxomil 40 MG / chlorthalidone 25 MG Oral Tablet
        "1299859",  # hydrochlorothiazide 12.5 MG / moexipril hydrochloride 15 MG Oral Tablet
        "1299871",  # hydrochlorothiazide 12.5 MG / moexipril hydrochloride 7.5 MG Oral Tablet
        "1299890",  # hydrochlorothiazide 25 MG / moexipril hydrochloride 15 MG Oral Tablet
        "1299896",  # moexipril hydrochloride 15 MG Oral Tablet
        "1299897",  # moexipril hydrochloride 7.5 MG Oral Tablet
        "1435624",  # enalapril maleate 1 MG/ML Oral Solution
        "1600716",  # amlodipine 10 MG / perindopril arginine 14 MG Oral Tablet
        "1600724",  # amlodipine 2.5 MG / perindopril arginine 3.5 MG Oral Tablet
        "1600728",  # amlodipine 5 MG / perindopril arginine 7 MG Oral Tablet
        "1656340",  # sacubitril 24 MG / valsartan 26 MG Oral Tablet
        "1656349",  # sacubitril 49 MG / valsartan 51 MG Oral Tablet
        "1656354",  # sacubitril 97 MG / valsartan 103 MG Oral Tablet
    }


class AdhdMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for attention deficit hyperactivity disorder (ADHD) medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable ADHD medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS136v11
    """

    VALUE_SET_NAME = "ADHD Medications"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1171"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197745",  # guanfacine 1 MG Oral Tablet
        "197746",  # guanfacine 2 MG Oral Tablet
        "349591",  # atomoxetine 10 MG Oral Capsule
        "349592",  # atomoxetine 18 MG Oral Capsule
        "349593",  # atomoxetine 25 MG Oral Capsule
        "349594",  # atomoxetine 40 MG Oral Capsule
        "349595",  # atomoxetine 60 MG Oral Capsule
        "541363",  # amphetamine aspartate 7.5 MG / amphetamine sulfate 7.5 MG / dextroamphetamine saccharate 7.5 MG / dextroamphetamine sulfate 7.5 MG Oral Tablet
        "541878",  # amphetamine aspartate 1.25 MG / amphetamine sulfate 1.25 MG / dextroamphetamine saccharate 1.25 MG / dextroamphetamine sulfate 1.25 MG Oral Tablet
        "541892",  # amphetamine aspartate 2.5 MG / amphetamine sulfate 2.5 MG / dextroamphetamine saccharate 2.5 MG / dextroamphetamine sulfate 2.5 MG Oral Tablet
        "577957",  # amphetamine aspartate 3.75 MG / amphetamine sulfate 3.75 MG / dextroamphetamine saccharate 3.75 MG / dextroamphetamine sulfate 3.75 MG Oral Tablet
        "577961",  # amphetamine aspartate 5 MG / amphetamine sulfate 5 MG / dextroamphetamine saccharate 5 MG / dextroamphetamine sulfate 5 MG Oral Tablet
        "608139",  # atomoxetine 100 MG Oral Capsule
        "608143",  # atomoxetine 80 MG Oral Capsule
        "687043",  # amphetamine aspartate 3.125 MG / amphetamine sulfate 3.125 MG / dextroamphetamine saccharate 3.125 MG / dextroamphetamine sulfate 3.125 MG Oral Tablet
        "753436",  # 9 HR methylphenidate 1.11 MG/HR Transdermal System
        "753438",  # 9 HR methylphenidate 1.67 MG/HR Transdermal System
        "753440",  # 9 HR methylphenidate 2.22 MG/HR Transdermal System
        "753441",  # 9 HR methylphenidate 3.33 MG/HR Transdermal System
        "854830",  # lisdexamfetamine dimesylate 20 MG Oral Capsule
        "854834",  # lisdexamfetamine dimesylate 30 MG Oral Capsule
        "854838",  # lisdexamfetamine dimesylate 40 MG Oral Capsule
        "854842",  # lisdexamfetamine dimesylate 70 MG Oral Capsule
        "854846",  # lisdexamfetamine dimesylate 60 MG Oral Capsule
        "854850",  # lisdexamfetamine dimesylate 50 MG Oral Capsule
        "861221",  # 24 HR amphetamine aspartate 2.5 MG / amphetamine sulfate 2.5 MG / dextroamphetamine saccharate 2.5 MG / dextroamphetamine sulfate 2.5 MG Extended Release Oral Capsule
        "861223",  # 24 HR amphetamine aspartate 3.75 MG / amphetamine sulfate 3.75 MG / dextroamphetamine saccharate 3.75 MG / dextroamphetamine sulfate 3.75 MG Extended Release Oral Capsule
        "861225",  # 24 HR amphetamine aspartate 5 MG / amphetamine sulfate 5 MG / dextroamphetamine saccharate 5 MG / dextroamphetamine sulfate 5 MG Extended Release Oral Capsule
        "861227",  # 24 HR amphetamine aspartate 6.25 MG / amphetamine sulfate 6.25 MG / dextroamphetamine saccharate 6.25 MG / dextroamphetamine sulfate 6.25 MG Extended Release Oral Capsule
        "861232",  # 24 HR amphetamine aspartate 7.5 MG / amphetamine sulfate 7.5 MG / dextroamphetamine saccharate 7.5 MG / dextroamphetamine sulfate 7.5 MG Extended Release Oral Capsule
        "861237",  # 24 HR amphetamine aspartate 1.25 MG / amphetamine sulfate 1.25 MG / dextroamphetamine saccharate 1.25 MG / dextroamphetamine sulfate 1.25 MG Extended Release Oral Capsule
        "862006",  # 24 HR guanfacine 1 MG Extended Release Oral Tablet
        "862013",  # 24 HR guanfacine 2 MG Extended Release Oral Tablet
        "862019",  # 24 HR guanfacine 3 MG Extended Release Oral Tablet
        "862025",  # 24 HR guanfacine 4 MG Extended Release Oral Tablet
        "884173",  # clonidine hydrochloride 0.1 MG Oral Tablet
        "884185",  # clonidine hydrochloride 0.2 MG Oral Tablet
        "884189",  # clonidine hydrochloride 0.3 MG Oral Tablet
        "884221",  # 10 ML clonidine hydrochloride 0.1 MG/ML Injection
        "884225",  # 10 ML clonidine hydrochloride 0.5 MG/ML Injection
        "884385",  # dextroamphetamine sulfate 10 MG Oral Tablet
        "884386",  # dextroamphetamine sulfate 5 MG Oral Tablet
        "884520",  # dextroamphetamine sulfate 10 MG Extended Release Oral Capsule
        "884522",  # dextroamphetamine sulfate 1 MG/ML Oral Solution
        "884532",  # dextroamphetamine sulfate 15 MG Extended Release Oral Capsule
        "884535",  # dextroamphetamine sulfate 5 MG Extended Release Oral Capsule
        "884684",  # dextroamphetamine sulfate 15 MG Oral Tablet
        "899439",  # 24 HR dexmethylphenidate hydrochloride 10 MG Extended Release Oral Capsule
        "899461",  # 24 HR dexmethylphenidate hydrochloride 15 MG Extended Release Oral Capsule
        "899485",  # 24 HR dexmethylphenidate hydrochloride 20 MG Extended Release Oral Capsule
        "899495",  # 24 HR dexmethylphenidate hydrochloride 30 MG Extended Release Oral Capsule
        "899511",  # 24 HR dexmethylphenidate hydrochloride 5 MG Extended Release Oral Capsule
        "899518",  # dexmethylphenidate hydrochloride 5 MG Oral Tablet
        "899548",  # dexmethylphenidate hydrochloride 10 MG Oral Tablet
        "899557",  # dexmethylphenidate hydrochloride 2.5 MG Oral Tablet
        "977860",  # methamphetamine hydrochloride 5 MG Oral Tablet
        "998671",  # 168 HR clonidine 0.00417 MG/HR Transdermal System
        "998675",  # 168 HR clonidine 0.00833 MG/HR Transdermal System
        "998679",  # 168 HR clonidine 0.0125 MG/HR Transdermal System
        "1006608",  # 24 HR dexmethylphenidate hydrochloride 40 MG Extended Release Oral Capsule
        "1009145",  # amphetamine aspartate 1.875 MG / amphetamine sulfate 1.875 MG / dextroamphetamine saccharate 1.875 MG / dextroamphetamine sulfate 1.875 MG Oral Tablet
        "1013930",  # 12 HR clonidine hydrochloride 0.1 MG Extended Release Oral Tablet
        "1013937",  # 12 HR clonidine hydrochloride 0.2 MG Extended Release Oral Tablet
        "1091133",  # methylphenidate hydrochloride 2 MG/ML Oral Solution
        "1091145",  # 8 HR methylphenidate hydrochloride 10 MG Extended Release Oral Tablet
        "1091150",  # methylphenidate hydrochloride 10 MG Oral Tablet
        "1091152",  # methylphenidate hydrochloride 10 MG Chewable Tablet
        "1091155",  # 24 HR methylphenidate hydrochloride 18 MG Extended Release Oral Tablet
        "1091170",  # 24 HR methylphenidate hydrochloride 27 MG Extended Release Oral Tablet
        "1091185",  # 24 HR methylphenidate hydrochloride 36 MG Extended Release Oral Tablet
        "1091210",  # 24 HR methylphenidate hydrochloride 54 MG Extended Release Oral Tablet
        "1091225",  # 8 HR methylphenidate hydrochloride 20 MG Extended Release Oral Tablet
        "1091322",  # methylphenidate hydrochloride 5 MG Chewable Tablet
        "1091341",  # methylphenidate hydrochloride 1 MG/ML Oral Solution
        "1091389",  # methylphenidate hydrochloride 2.5 MG Chewable Tablet
        "1091392",  # methylphenidate hydrochloride 20 MG Oral Tablet
        "1091497",  # methylphenidate hydrochloride 5 MG Oral Tablet
        "1092566",  # {7 (24 HR guanfacine 1 MG Extended Release Oral Tablet) / 7 (24 HR guanfacine 2 MG Extended Release Oral Tablet) } Pack
        "1101926",  # 24 HR dexmethylphenidate hydrochloride 25 MG Extended Release Oral Capsule
        "1101932",  # 24 HR dexmethylphenidate hydrochloride 35 MG Extended Release Oral Capsule
        "1312583",  # 24 HR methylphenidate hydrochloride 5 MG/ML Extended Release Suspension
        "1425847",  # dextroamphetamine sulfate 2.5 MG Oral Tablet
        "1425854",  # dextroamphetamine sulfate 7.5 MG Oral Tablet
        "1535454",  # dextroamphetamine sulfate 20 MG Oral Tablet
        "1535470",  # dextroamphetamine sulfate 30 MG Oral Tablet
        "1593856",  # lisdexamfetamine dimesylate 10 MG Oral Capsule
        "1648183",  # 40/60 Release 24 HR methylphenidate hydrochloride 15 MG Extended Release Oral Capsule
        "1727443",  # 24 HR methylphenidate hydrochloride 20 MG Chewable Extended Release Oral Tablet
        "1734928",  # 24 HR methylphenidate hydrochloride 30 MG Chewable Extended Release Oral Tablet
        "1734951",  # 24 HR methylphenidate 40 MG Chewable Extended Release Oral Tablet
        "1806177",  # 50/50 Release 24 HR methylphenidate hydrochloride 20 MG Extended Release Oral Capsule
        "1806179",  # 50/50 Release 24 HR methylphenidate hydrochloride 30 MG Extended Release Oral Capsule
        "1806181",  # 30/70 Release 24 HR methylphenidate hydrochloride 10 MG Extended Release Oral Capsule
        "1806183",  # 50/50 Release 24 HR methylphenidate hydrochloride 40 MG Extended Release Oral Capsule
        "1806185",  # 50/50 Release 24 HR methylphenidate hydrochloride 60 MG Extended Release Oral Capsule
        "1806187",  # 30/70 Release 24 HR methylphenidate hydrochloride 20 MG Extended Release Oral Capsule
        "1806189",  # 30/70 Release 24 HR methylphenidate hydrochloride 30 MG Extended Release Oral Capsule
        "1806191",  # 30/70 Release 24 HR methylphenidate hydrochloride 40 MG Extended Release Oral Capsule
        "1806193",  # 30/70 Release 24 HR methylphenidate hydrochloride 50 MG Extended Release Oral Capsule
        "1806195",  # 50/50 Release 24 HR methylphenidate hydrochloride 10 MG Extended Release Oral Capsule
        "1806197",  # 30/70 Release 24 HR methylphenidate hydrochloride 60 MG Extended Release Oral Capsule
        "1806200",  # 40/60 Release 24 HR methylphenidate hydrochloride 10 MG Extended Release Oral Capsule
        "1806202",  # 40/60 Release 24 HR methylphenidate hydrochloride 20 MG Extended Release Oral Capsule
        "1806204",  # 40/60 Release 24 HR methylphenidate hydrochloride 50 MG Extended Release Oral Capsule
        "1806206",  # 40/60 Release 24 HR methylphenidate hydrochloride 30 MG Extended Release Oral Capsule
        "1806208",  # 40/60 Release 24 HR methylphenidate hydrochloride 60 MG Extended Release Oral Capsule
        "1806210",  # 40/60 Release 24 HR methylphenidate hydrochloride 40 MG Extended Release Oral Capsule
        "1871456",  # lisdexamfetamine dimesylate 40 MG Chewable Tablet
        "1871460",  # lisdexamfetamine dimesylate 30 MG Chewable Tablet
        "1871462",  # lisdexamfetamine dimesylate 20 MG Chewable Tablet
        "1871464",  # lisdexamfetamine dimesylate 10 MG Chewable Tablet
        "1871466",  # lisdexamfetamine dimesylate 60 MG Chewable Tablet
        "1871468",  # lisdexamfetamine dimesylate 50 MG Chewable Tablet
        "1926840",  # methylphenidate 17.3 MG Disintegrating Oral Tablet
        "1926849",  # methylphenidate 25.9 MG Disintegrating Oral Tablet
        "1926853",  # methylphenidate 8.6 MG Disintegrating Oral Tablet
        "1927610",  # 3-Bead 24 HR amphetamine aspartate 12.5 MG / amphetamine sulfate 12.5 MG / dextroamphetamine saccharate 12.5 MG / dextroamphetamine sulfate 12.5 MG Extended Release Oral Capsule
        "1927617",  # 3-Bead 24 HR amphetamine aspartate 6.25 MG / amphetamine sulfate 6.25 MG / dextroamphetamine saccharate 6.25 MG / dextroamphetamine sulfate 6.25 MG Extended Release Oral Capsule
        "1927630",  # 3-Bead 24 HR amphetamine aspartate 3.125 MG / amphetamine sulfate 3.125 MG / dextroamphetamine saccharate 3.125 MG / dextroamphetamine sulfate 3.125 MG Extended Release Oral Capsule
        "1927637",  # 3-Bead 24 HR amphetamine aspartate 9.375 MG / amphetamine sulfate 9.375 MG / dextroamphetamine saccharate 9.375 MG / dextroamphetamine sulfate 9.375 MG Extended Release Oral Capsule
        "1995461",  # 24 HR methylphenidate hydrochloride 72 MG Extended Release Oral Tablet
        "2001564",  # BX Rating 24 HR methylphenidate hydrochloride 18 MG Extended Release Oral Tablet
        "2001565",  # BX Rating 24 HR methylphenidate hydrochloride 27 MG Extended Release Oral Tablet
        "2001566",  # BX Rating 24 HR methylphenidate hydrochloride 36 MG Extended Release Oral Tablet
        "2001568",  # BX Rating 24 HR methylphenidate hydrochloride 54 MG Extended Release Oral Tablet
    }


class OpiateAntagonists(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for opiate antagonist medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable opiate antagonist medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and concepts that represent components or ingredients.

    ** Used in:** CMS137v10
    """

    VALUE_SET_NAME = "Opiate Antagonists"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1132"
    DEFINITION_VERSION = "20200310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197623",  # disulfiram 250 MG Oral Tablet
        "197624",  # disulfiram 500 MG Oral Tablet
        "238129",  # 1 ML buprenorphine 0.3 MG/ML Injection
        "351264",  # buprenorphine 2 MG Sublingual Tablet
        "351265",  # buprenorphine 8 MG Sublingual Tablet
        "351266",  # buprenorphine 2 MG / naloxone 0.5 MG Sublingual Tablet
        "351267",  # buprenorphine 8 MG / naloxone 2 MG Sublingual Tablet
        "637213",  # naltrexone 380 MG Injection
        "835726",  # acamprosate calcium 333 MG Delayed Release Oral Tablet
        "1010600",  # buprenorphine 2 MG / naloxone 0.5 MG Sublingual Film
        "1010604",  # buprenorphine 8 MG / naloxone 2 MG Sublingual Film
        "1307056",  # buprenorphine 4 MG / naloxone 1 MG Sublingual Film
        "1307061",  # buprenorphine 12 MG / naloxone 3 MG Sublingual Film
        "1431076",  # buprenorphine 1.4 MG / naloxone 0.36 MG Sublingual Tablet
        "1431102",  # buprenorphine 5.7 MG / naloxone 1.4 MG Sublingual Tablet
        "1483744",  # naltrexone hydrochloride 50 MG Oral Tablet
        "1542390",  # buprenorphine 2.1 MG / naloxone 0.3 MG Buccal Film
        "1544851",  # buprenorphine 4.2 MG / naloxone 0.7 MG Buccal Film
        "1544854",  # buprenorphine 6.3 MG / naloxone 1 MG Buccal Film
        "1551468",  # 12 HR bupropion hydrochloride 90 MG / naltrexone hydrochloride 8 MG Extended Release Oral Tablet
        "1597568",  # buprenorphine 11.4 MG / naloxone 2.9 MG Sublingual Tablet
        "1597573",  # buprenorphine 8.6 MG / naloxone 2.1 MG Sublingual Tablet
        "1655032",  # 1 ML buprenorphine 0.3 MG/ML Cartridge
        "1666338",  # buprenorphine 2.9 MG / naloxone 0.71 MG Sublingual Tablet
        "1797650",  # buprenorphine 74.2 MG Drug Implant
        "1864412",  # buprenorphine 0.7 MG / naloxone 0.18 MG Sublingual Tablet
        "1996184",  # 0.5 ML buprenorphine 200 MG/ML Prefilled Syringe
        "1996192",  # 1.5 ML buprenorphine 200 MG/ML Prefilled Syringe
    }


class TobaccoUseCessationPharmacotherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for tobacco use cessation medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable tobacco use cessation medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS138v10
    """

    VALUE_SET_NAME = "Tobacco Use Cessation Pharmacotherapy"
    OID = "2.16.840.1.113883.3.526.3.1190"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "151226",  # topiramate 50 MG Oral Tablet
        "198029",  # 24 HR nicotine 0.583 MG/HR Transdermal System
        "198030",  # 24 HR nicotine 0.875 MG/HR Transdermal System
        "198031",  # 24 HR nicotine 0.292 MG/HR Transdermal System
        "198045",  # nortriptyline 10 MG Oral Capsule
        "198046",  # nortriptyline 50 MG Oral Capsule
        "198047",  # nortriptyline 75 MG Oral Capsule
        "199888",  # topiramate 25 MG Oral Tablet
        "199889",  # topiramate 100 MG Oral Tablet
        "199890",  # topiramate 200 MG Oral Tablet
        "205315",  # topiramate 25 MG Oral Capsule
        "205316",  # topiramate 15 MG Oral Capsule
        "250983",  # nicotine 4 MG Inhalation Solution
        "311975",  # nicotine 4 MG Chewing Gum
        "312036",  # nortriptyline 2 MG/ML Oral Solution
        "314119",  # nicotine 2 MG Chewing Gum
        "317136",  # nortriptyline 25 MG Oral Capsule
        "359817",  # nicotine 2 MG Oral Lozenge
        "359818",  # nicotine 4 MG Oral Lozenge
        "636671",  # varenicline 0.5 MG Oral Tablet
        "636676",  # varenicline 1 MG Oral Tablet
        "749289",  # {11 (varenicline 0.5 MG Oral Tablet) / 42 (varenicline 1 MG Oral Tablet) } Pack
        "749788",  # {56 (varenicline 1 MG Oral Tablet) } Pack
        "892244",  # {14 (24 HR nicotine 0.292 MG/HR Transdermal System) / 14 (24 HR nicotine 0.583 MG/HR Transdermal System) / 28 (24 HR nicotine 0.875 MG/HR Transdermal System) } Pack
        "993503",  # 12 HR bupropion hydrochloride 100 MG Extended Release Oral Tablet
        "993518",  # 12 HR bupropion hydrochloride 150 MG Extended Release Oral Tablet
        "993536",  # 12 HR bupropion hydrochloride 200 MG Extended Release Oral Tablet
        "993541",  # 24 HR bupropion hydrochloride 150 MG Extended Release Oral Tablet
        "993557",  # 24 HR bupropion hydrochloride 300 MG Extended Release Oral Tablet
        "993687",  # bupropion hydrochloride 100 MG Oral Tablet
        "993691",  # bupropion hydrochloride 75 MG Oral Tablet
        "998671",  # 168 HR clonidine 0.00417 MG/HR Transdermal System
        "998675",  # 168 HR clonidine 0.00833 MG/HR Transdermal System
        "998679",  # 168 HR clonidine 0.0125 MG/HR Transdermal System
        "1232585",  # 24 HR bupropion hydrochloride 450 MG Extended Release Oral Tablet
        "1302827",  # 24 HR phentermine 7.5 MG / topiramate 46 MG Extended Release Oral Capsule
        "1302839",  # 24 HR phentermine 3.75 MG / topiramate 23 MG Extended Release Oral Capsule
        "1302850",  # 24 HR phentermine 15 MG / topiramate 92 MG Extended Release Oral Capsule
        "1436239",  # 24 HR topiramate 50 MG Extended Release Oral Capsule
        "1437278",  # 24 HR topiramate 25 MG Extended Release Oral Capsule
        "1437283",  # 24 HR topiramate 100 MG Extended Release Oral Capsule
        "1437288",  # 24 HR topiramate 200 MG Extended Release Oral Capsule
        "1494769",  # Sprinkle 24 HR topiramate 150 MG Extended Release Oral Capsule
        "1551468",  # 12 HR bupropion hydrochloride 90 MG / naltrexone hydrochloride 8 MG Extended Release Oral Tablet
        "1797886",  # nicotine 0.5 MG/ACTUAT Metered Dose Nasal Spray
        "1801289",  # Smoking Cessation 12 HR bupropion hydrochloride 150 MG Extended Release Oral Tablet
        "1812419",  # Sprinkle 24 HR topiramate 200 MG Extended Release Oral Capsule
        "1812421",  # Sprinkle 24 HR topiramate 25 MG Extended Release Oral Capsule
        "1812425",  # Sprinkle 24 HR topiramate 50 MG Extended Release Oral Capsule
        "1812427",  # Sprinkle 24 HR topiramate 100 MG Extended Release Oral Capsule
    }


class BetaBlockerTherapyForLvsd(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of medications for beta blocker therapy for left ventricular systolic dysfunction (LVSD).

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for generic and prescribable bisoprolol, carvedilol, or sustained release metoprolol succinate.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable branded drugs, components or ingredients.

    ** Used in:** CMS144v10, CMS145v10
    """

    VALUE_SET_NAME = "Beta Blocker Therapy for LVSD"
    OID = "2.16.840.1.113883.3.526.3.1184"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "200031",  # carvedilol 6.25 MG Oral Tablet
        "200032",  # carvedilol 12.5 MG Oral Tablet
        "200033",  # carvedilol 25 MG Oral Tablet
        "686924",  # carvedilol 3.125 MG Oral Tablet
        "854901",  # bisoprolol fumarate 10 MG Oral Tablet
        "854905",  # bisoprolol fumarate 5 MG Oral Tablet
        "854908",  # bisoprolol fumarate 10 MG / hydrochlorothiazide 6.25 MG Oral Tablet
        "854916",  # bisoprolol fumarate 2.5 MG / hydrochlorothiazide 6.25 MG Oral Tablet
        "854919",  # bisoprolol fumarate 5 MG / hydrochlorothiazide 6.25 MG Oral Tablet
        "860510",  # 24 HR carvedilol phosphate 10 MG Extended Release Oral Capsule
        "860516",  # 24 HR carvedilol phosphate 20 MG Extended Release Oral Capsule
        "860522",  # 24 HR carvedilol phosphate 40 MG Extended Release Oral Capsule
        "860532",  # 24 HR carvedilol phosphate 80 MG Extended Release Oral Capsule
        "866412",  # 24 HR metoprolol succinate 100 MG Extended Release Oral Tablet
        "866419",  # 24 HR metoprolol succinate 200 MG Extended Release Oral Tablet
        "866427",  # 24 HR metoprolol succinate 25 MG Extended Release Oral Tablet
        "866436",  # 24 HR metoprolol succinate 50 MG Extended Release Oral Tablet
        "866452",  # 24 HR hydrochlorothiazide 12.5 MG / metoprolol succinate 100 MG Extended Release Oral Tablet
        "866461",  # 24 HR hydrochlorothiazide 12.5 MG / metoprolol succinate 25 MG Extended Release Oral Tablet
        "866472",  # 24 HR hydrochlorothiazide 12.5 MG / metoprolol succinate 50 MG Extended Release Oral Tablet
    }


class BetaBlockerTherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of medications for beta blocker therapy.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for beta blockers.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable branded drugs, components or ingredients.

    ** Used in:** CMS145v10
    """

    VALUE_SET_NAME = "Beta Blocker Therapy"
    OID = "2.16.840.1.113883.3.526.3.1174"
    DEFINITION_VERSION = "20210303"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197379",  # atenolol 100 MG Oral Tablet
        "197380",  # atenolol 25 MG Oral Tablet
        "197381",  # atenolol 50 MG Oral Tablet
        "197382",  # atenolol 100 MG / chlorthalidone 25 MG Oral Tablet
        "197383",  # atenolol 50 MG / chlorthalidone 25 MG Oral Tablet
        "198000",  # bendroflumethiazide 5 MG / nadolol 40 MG Oral Tablet
        "198001",  # bendroflumethiazide 5 MG / nadolol 80 MG Oral Tablet
        "198006",  # nadolol 20 MG Oral Tablet
        "198007",  # nadolol 40 MG Oral Tablet
        "198008",  # nadolol 80 MG Oral Tablet
        "198104",  # pindolol 10 MG Oral Tablet
        "198105",  # pindolol 5 MG Oral Tablet
        "198284",  # timolol 10 MG Oral Tablet
        "198285",  # timolol 20 MG Oral Tablet
        "198286",  # timolol 5 MG Oral Tablet
        "200031",  # carvedilol 6.25 MG Oral Tablet
        "200032",  # carvedilol 12.5 MG Oral Tablet
        "200033",  # carvedilol 25 MG Oral Tablet
        "387013",  # nebivolol 5 MG Oral Tablet
        "686924",  # carvedilol 3.125 MG Oral Tablet
        "751612",  # nebivolol 10 MG Oral Tablet
        "751618",  # nebivolol 2.5 MG Oral Tablet
        "827073",  # nebivolol 20 MG Oral Tablet
        "854901",  # bisoprolol fumarate 10 MG Oral Tablet
        "854905",  # bisoprolol fumarate 5 MG Oral Tablet
        "854908",  # bisoprolol fumarate 10 MG / hydrochlorothiazide 6.25 MG Oral Tablet
        "854916",  # bisoprolol fumarate 2.5 MG / hydrochlorothiazide 6.25 MG Oral Tablet
        "854919",  # bisoprolol fumarate 5 MG / hydrochlorothiazide 6.25 MG Oral Tablet
        "856422",  # hydrochlorothiazide 25 MG / propranolol hydrochloride 40 MG Oral Tablet
        "856429",  # hydrochlorothiazide 25 MG / propranolol hydrochloride 80 MG Oral Tablet
        "856448",  # propranolol hydrochloride 10 MG Oral Tablet
        "856457",  # propranolol hydrochloride 20 MG Oral Tablet
        "856460",  # 24 HR propranolol hydrochloride 120 MG Extended Release Oral Capsule
        "856481",  # 24 HR propranolol hydrochloride 160 MG Extended Release Oral Capsule
        "856519",  # propranolol hydrochloride 40 MG Oral Tablet
        "856535",  # 24 HR propranolol hydrochloride 60 MG Extended Release Oral Capsule
        "856556",  # propranolol hydrochloride 60 MG Oral Tablet
        "856569",  # 24 HR propranolol hydrochloride 80 MG Extended Release Oral Capsule
        "856578",  # propranolol hydrochloride 80 MG Oral Tablet
        "856724",  # propranolol hydrochloride 4 MG/ML Oral Solution
        "856733",  # propranolol hydrochloride 8 MG/ML Oral Solution
        "860510",  # 24 HR carvedilol phosphate 10 MG Extended Release Oral Capsule
        "860516",  # 24 HR carvedilol phosphate 20 MG Extended Release Oral Capsule
        "860522",  # 24 HR carvedilol phosphate 40 MG Extended Release Oral Capsule
        "860532",  # 24 HR carvedilol phosphate 80 MG Extended Release Oral Capsule
        "866412",  # 24 HR metoprolol succinate 100 MG Extended Release Oral Tablet
        "866419",  # 24 HR metoprolol succinate 200 MG Extended Release Oral Tablet
        "866427",  # 24 HR metoprolol succinate 25 MG Extended Release Oral Tablet
        "866436",  # 24 HR metoprolol succinate 50 MG Extended Release Oral Tablet
        "866452",  # 24 HR hydrochlorothiazide 12.5 MG / metoprolol succinate 100 MG Extended Release Oral Tablet
        "866461",  # 24 HR hydrochlorothiazide 12.5 MG / metoprolol succinate 25 MG Extended Release Oral Tablet
        "866472",  # 24 HR hydrochlorothiazide 12.5 MG / metoprolol succinate 50 MG Extended Release Oral Tablet
        "866479",  # hydrochlorothiazide 25 MG / metoprolol tartrate 100 MG Oral Tablet
        "866482",  # hydrochlorothiazide 25 MG / metoprolol tartrate 50 MG Oral Tablet
        "866491",  # hydrochlorothiazide 50 MG / metoprolol tartrate 100 MG Oral Tablet
        "866511",  # metoprolol tartrate 100 MG Oral Tablet
        "866514",  # metoprolol tartrate 50 MG Oral Tablet
        "866924",  # metoprolol tartrate 25 MG Oral Tablet
        "896758",  # labetalol hydrochloride 100 MG Oral Tablet
        "896762",  # labetalol hydrochloride 200 MG Oral Tablet
        "896766",  # labetalol hydrochloride 300 MG Oral Tablet
        "904589",  # sotalol hydrochloride 240 MG Oral Tablet
        "998685",  # acebutolol 400 MG Oral Capsule
        "998689",  # acebutolol 200 MG Oral Capsule
        "1191185",  # penbutolol sulfate 20 MG Oral Tablet
        "1297753",  # betaxolol hydrochloride 10 MG Oral Tablet
        "1297757",  # betaxolol hydrochloride 20 MG Oral Tablet
        "1495058",  # propranolol hydrochloride 4.28 MG/ML Oral Solution
        "1593725",  # sotalol hydrochloride 5 MG/ML Oral Solution
        "1606347",  # metoprolol tartrate 37.5 MG Oral Tablet
        "1606349",  # metoprolol tartrate 75 MG Oral Tablet
        "1798281",  # nebivolol 5 MG / valsartan 80 MG Oral Tablet
        "1923422",  # sotalol hydrochloride 120 MG Oral Tablet
        "1923424",  # sotalol hydrochloride 160 MG Oral Tablet
        "1923426",  # sotalol hydrochloride 80 MG Oral Tablet
    }


class AntibioticMedicationsForPharyngitis(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for antibiotic medications used to treat pharyngitis.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable antibiotics for pharyngitis.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and concepts that represent components or ingredients.

    ** Used in:** CMS154v10, CMS146v10
    """

    VALUE_SET_NAME = "Antibiotic Medications for Pharyngitis"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1001"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "105171",  # cefadroxil 100 MG/ML Oral Suspension
        "141963",  # azithromycin 40 MG/ML Oral Suspension
        "197449",  # cefaclor 500 MG Oral Capsule
        "197451",  # cefixime 400 MG Oral Tablet
        "197452",  # cefprozil 250 MG Oral Tablet
        "197453",  # cefprozil 500 MG Oral Tablet
        "197454",  # cephalexin 500 MG Oral Tablet
        "197511",  # ciprofloxacin 250 MG Oral Tablet
        "197512",  # ciprofloxacin 750 MG Oral Tablet
        "197516",  # clarithromycin 250 MG Oral Tablet
        "197517",  # clarithromycin 500 MG Oral Tablet
        "197518",  # clindamycin 150 MG Oral Capsule
        "197595",  # dicloxacillin 250 MG Oral Capsule
        "197596",  # dicloxacillin 500 MG Oral Capsule
        "197650",  # erythromycin 500 MG Oral Tablet
        "197984",  # minocycline 100 MG Oral Capsule
        "197985",  # minocycline 50 MG Oral Capsule
        "198044",  # norfloxacin 400 MG Oral Tablet
        "198048",  # ofloxacin 200 MG Oral Tablet
        "198049",  # ofloxacin 300 MG Oral Tablet
        "198050",  # ofloxacin 400 MG Oral Tablet
        "198201",  # rifampin 150 MG Oral Capsule
        "198202",  # rifampin 300 MG Oral Capsule
        "198250",  # tetracycline hydrochloride 250 MG Oral Capsule
        "198252",  # tetracycline hydrochloride 500 MG Oral Capsule
        "198332",  # trimethoprim 100 MG Oral Tablet
        "198334",  # sulfamethoxazole 400 MG / trimethoprim 80 MG Oral Tablet
        "198335",  # sulfamethoxazole 800 MG / trimethoprim 160 MG Oral Tablet
        "199055",  # metronidazole 375 MG Oral Capsule
        "199370",  # ciprofloxacin 100 MG Oral Tablet
        "199884",  # levofloxacin 250 MG Oral Tablet
        "199885",  # levofloxacin 500 MG Oral Tablet
        "200346",  # cefdinir 300 MG Oral Capsule
        "204466",  # 50 ML penicillin G potassium 40000 UNT/ML Injection
        "204844",  # azithromycin 600 MG Oral Tablet
        "205964",  # clindamycin 150 MG/ML Injectable Solution
        "207362",  # minocycline 50 MG Oral Tablet
        "207364",  # minocycline 100 MG Oral Tablet
        "207390",  # 50 ML penicillin G potassium 20000 UNT/ML Injection
        "207391",  # 50 ML penicillin G potassium 60000 UNT/ML Injection
        "239189",  # nafcillin 100 MG/ML Injectable Solution
        "239191",  # amoxicillin 50 MG/ML Oral Suspension
        "239204",  # gentamicin 10 MG/ML Injectable Solution
        "239209",  # vancomycin 100 MG/ML Injectable Solution
        "240637",  # 50 ML oxacillin 40 MG/ML Injection
        "240741",  # clarithromycin 25 MG/ML Oral Suspension
        "240984",  # ampicillin 100 MG/ML / sulbactam 50 MG/ML Injectable Solution
        "242800",  # ceftazidime 200 MG/ML Injectable Solution
        "242825",  # 50 ML tobramycin 1.2 MG/ML Injection
        "248656",  # azithromycin 500 MG Oral Tablet
        "259290",  # dalfopristin 350 MG / quinupristin 150 MG Injection
        "283535",  # doxycycline hyclate 20 MG Oral Tablet
        "284215",  # clindamycin 300 MG Oral Capsule
        "308177",  # amoxicillin 125 MG Chewable Tablet
        "308182",  # amoxicillin 250 MG Oral Capsule
        "308188",  # amoxicillin 400 MG Chewable Tablet
        "308189",  # amoxicillin 80 MG/ML Oral Suspension
        "308191",  # amoxicillin 500 MG Oral Capsule
        "308192",  # amoxicillin 500 MG Oral Tablet
        "308194",  # amoxicillin 875 MG Oral Tablet
        "308207",  # ampicillin 125 MG Injection
        "308210",  # ampicillin 50 MG/ML Oral Suspension
        "308212",  # ampicillin 500 MG Oral Capsule
        "308459",  # azithromycin 20 MG/ML Oral Suspension
        "308460",  # azithromycin 250 MG Oral Tablet
        "309043",  # 12 HR cefaclor 500 MG Extended Release Oral Tablet
        "309044",  # cefaclor 25 MG/ML Oral Suspension
        "309045",  # cefaclor 250 MG Oral Capsule
        "309047",  # cefadroxil 1000 MG Oral Tablet
        "309048",  # cefadroxil 50 MG/ML Oral Suspension
        "309049",  # cefadroxil 500 MG Oral Capsule
        "309054",  # cefdinir 25 MG/ML Oral Suspension
        "309058",  # cefixime 20 MG/ML Oral Suspension
        "309065",  # cefotaxime 200 MG/ML Injectable Solution
        "309068",  # cefotaxime 500 MG Injection
        "309072",  # cefoxitin 200 MG/ML Injectable Solution
        "309076",  # cefpodoxime 100 MG Oral Tablet
        "309077",  # cefpodoxime 20 MG/ML Oral Suspension
        "309078",  # cefpodoxime 200 MG Oral Tablet
        "309079",  # cefpodoxime 10 MG/ML Oral Suspension
        "309080",  # cefprozil 25 MG/ML Oral Suspension
        "309081",  # cefprozil 50 MG/ML Oral Suspension
        "309090",  # ceftriaxone 100 MG/ML Injectable Solution
        "309092",  # ceftriaxone 250 MG Injection
        "309095",  # cefuroxime 125 MG Oral Tablet
        "309096",  # cefuroxime 25 MG/ML Oral Suspension
        "309097",  # cefuroxime 250 MG Oral Tablet
        "309098",  # cefuroxime 500 MG Oral Tablet
        "309101",  # cefuroxime 95 MG/ML Injectable Solution
        "309110",  # cephalexin 25 MG/ML Oral Suspension
        "309112",  # cephalexin 250 MG Oral Capsule
        "309113",  # cephalexin 50 MG/ML Oral Suspension
        "309114",  # cephalexin 500 MG Oral Capsule
        "309115",  # cephalexin 250 MG Oral Tablet
        "309308",  # ciprofloxacin 50 MG/ML Oral Suspension
        "309309",  # ciprofloxacin 500 MG Oral Tablet
        "309310",  # ciprofloxacin 100 MG/ML Oral Suspension
        "309322",  # clarithromycin 50 MG/ML Oral Suspension
        "309329",  # clindamycin 75 MG Oral Capsule
        "309335",  # 50 ML clindamycin 12 MG/ML Injection
        "309336",  # 50 ML clindamycin 18 MG/ML Injection
        "309339",  # 50 ML clindamycin 6 MG/ML Injection
        "310026",  # doxycycline calcium 10 MG/ML Oral Suspension
        "310027",  # doxycycline hyclate 100 MG Injection
        "310028",  # doxycycline hyclate 20 MG Oral Capsule
        "310154",  # erythromycin 250 MG Delayed Release Oral Capsule
        "310155",  # erythromycin 250 MG Delayed Release Oral Tablet
        "310157",  # erythromycin 500 MG Delayed Release Oral Tablet
        "311296",  # levofloxacin 750 MG Oral Tablet
        "311681",  # metronidazole 500 MG Oral Tablet
        "311787",  # moxifloxacin 400 MG Oral Tablet
        "311989",  # nitrofurantoin 5 MG/ML Oral Suspension
        "311994",  # nitrofurantoin, macrocrystals 25 MG Oral Capsule
        "311995",  # nitrofurantoin, macrocrystals 50 MG Oral Capsule
        "312127",  # oxacillin 100 MG/ML Injectable Solution
        "312128",  # 50 ML oxacillin 20 MG/ML Injection
        "312447",  # piperacillin 200 MG/ML / tazobactam 25 MG/ML Injectable Solution
        "313115",  # streptomycin 1000 MG Injection
        "313134",  # sulfamethoxazole 40 MG/ML / trimethoprim 8 MG/ML Oral Suspension
        "313137",  # sulfamethoxazole 80 MG/ML / trimethoprim 16 MG/ML Injectable Solution
        "313416",  # tobramycin 10 MG/ML Injectable Solution
        "313570",  # vancomycin 125 MG Oral Capsule
        "313571",  # vancomycin 250 MG Oral Capsule
        "313572",  # vancomycin 50 MG/ML Injectable Solution
        "313797",  # amoxicillin 25 MG/ML Oral Suspension
        "313800",  # ampicillin 250 MG Oral Capsule
        "313850",  # amoxicillin 40 MG/ML Oral Suspension
        "313888",  # cefaclor 50 MG/ML Oral Suspension
        "313920",  # cefazolin 200 MG/ML Injectable Solution
        "313926",  # cefuroxime 50 MG/ML Oral Suspension
        "313996",  # gentamicin 40 MG/ML Injectable Solution
        "314106",  # metronidazole 250 MG Oral Tablet
        "314108",  # minocycline 75 MG Oral Capsule
        "315090",  # erythromycin 333 MG Delayed Release Oral Tablet
        "317127",  # minocycline 100 MG Injection
        "348869",  # doxycycline hyclate 100 MG Delayed Release Oral Capsule
        "351156",  # 250 ML moxifloxacin 1.6 MG/ML Injection
        "359383",  # 24 HR ciprofloxacin 500 MG Extended Release Oral Tablet
        "359385",  # 24 HR clarithromycin 500 MG Extended Release Oral Tablet
        "403840",  # minocycline 75 MG Oral Tablet
        "403920",  # daptomycin 500 MG Injection
        "403921",  # 24 HR ciprofloxacin 1000 MG Extended Release Oral Tablet
        "406524",  # doxycycline hyclate 75 MG Delayed Release Oral Tablet
        "409823",  # cefixime 400 MG Oral Capsule
        "419849",  # cefixime 40 MG/ML Oral Suspension
        "434018",  # doxycycline hyclate 100 MG Delayed Release Oral Tablet
        "476576",  # cefdinir 50 MG/ML Oral Suspension
        "477391",  # levofloxacin 25 MG/ML Oral Solution
        "562251",  # amoxicillin 250 MG / clavulanate 125 MG Oral Tablet
        "562266",  # clindamycin 15 MG/ML Oral Solution
        "562508",  # amoxicillin 875 MG / clavulanate 125 MG Oral Tablet
        "562707",  # trimethoprim 10 MG/ML Oral Solution
        "577378",  # azithromycin 33.3 MG/ML Extended Release Suspension
        "597823",  # tobramycin 40 MG/ML Injectable Solution
        "598006",  # erythromycin 250 MG Oral Tablet
        "598025",  # amoxicillin 250 MG Chewable Tablet
        "617296",  # amoxicillin 500 MG / clavulanate 125 MG Oral Tablet
        "617302",  # amoxicillin 25 MG/ML / clavulanate 6.25 MG/ML Oral Suspension
        "617309",  # amoxicillin 200 MG / clavulanate 28.5 MG Chewable Tablet
        "617316",  # amoxicillin 400 MG / clavulanate 57 MG Chewable Tablet
        "617322",  # amoxicillin 50 MG/ML / clavulanate 12.5 MG/ML Oral Suspension
        "617423",  # amoxicillin 40 MG/ML / clavulanate 5.7 MG/ML Oral Suspension
        "617430",  # amoxicillin 80 MG/ML / clavulanate 11.4 MG/ML Oral Suspension
        "617993",  # amoxicillin 120 MG/ML / clavulanate 8.58 MG/ML Oral Suspension
        "617995",  # 12 HR amoxicillin 1000 MG / clavulanate 62.5 MG Extended Release Oral Tablet
        "629695",  # 24 HR minocycline 135 MG Extended Release Oral Tablet
        "629697",  # 24 HR minocycline 45 MG Extended Release Oral Tablet
        "629699",  # 24 HR minocycline 90 MG Extended Release Oral Tablet
        "636559",  # 24 HR metronidazole 750 MG Extended Release Oral Tablet
        "637173",  # cephalexin 750 MG Oral Capsule
        "637560",  # gemifloxacin 320 MG Oral Tablet
        "645617",  # cephalexin 333 MG Oral Capsule
        "686355",  # erythromycin stearate 250 MG Oral Tablet
        "686400",  # erythromycin ethylsuccinate 40 MG/ML Oral Suspension
        "686405",  # erythromycin ethylsuccinate 400 MG Oral Tablet
        "686406",  # erythromycin stearate 500 MG Oral Tablet
        "686418",  # erythromycin ethylsuccinate 80 MG/ML Oral Suspension
        "700408",  # doxycycline monohydrate 75 MG Oral Capsule
        "728207",  # doxycycline monohydrate 150 MG Oral Capsule
        "731538",  # 2 ML penicillin G benzathine 300000 UNT/ML / penicillin G procaine 300000 UNT/ML Prefilled Syringe
        "731564",  # 1 ML penicillin G benzathine 600000 UNT/ML Prefilled Syringe
        "731567",  # 2 ML penicillin G benzathine 600000 UNT/ML Prefilled Syringe
        "731570",  # 4 ML penicillin G benzathine 600000 UNT/ML Prefilled Syringe
        "745302",  # penicillin G sodium 100000 UNT/ML Injectable Solution
        "745462",  # 2 ML penicillin G procaine 600000 UNT/ML Prefilled Syringe
        "745560",  # 1 ML penicillin G procaine 600000 UNT/ML Prefilled Syringe
        "749780",  # {3 (azithromycin 500 MG Oral Tablet) } Pack
        "749783",  # {6 (azithromycin 250 MG Oral Tablet) } Pack
        "757460",  # {31 (doxycycline monohydrate 100 MG Oral Tablet) } Pack
        "757464",  # {31 (doxycycline monohydrate 75 MG Oral Tablet) } Pack
        "757466",  # {60 (doxycycline monohydrate 100 MG Oral Tablet) } Pack
        "789980",  # ampicillin 100 MG/ML Injectable Solution
        "799048",  # doxycycline hyclate 150 MG Delayed Release Oral Tablet
        "802550",  # amoxicillin 775 MG Extended Release Oral Tablet
        "834040",  # penicillin V potassium 50 MG/ML Oral Solution
        "834046",  # penicillin V potassium 25 MG/ML Oral Solution
        "834061",  # penicillin V potassium 250 MG Oral Tablet
        "834102",  # penicillin V potassium 500 MG Oral Tablet
        "835700",  # {30 (doxycycline monohydrate 150 MG Oral Tablet) } Pack
        "836306",  # 2 ML penicillin G benzathine 450000 UNT/ML / penicillin G procaine 150000 UNT/ML Prefilled Syringe
        "858062",  # 24 HR minocycline 115 MG Extended Release Oral Tablet
        "858372",  # 24 HR minocycline 65 MG Extended Release Oral Tablet
        "863538",  # penicillin G potassium 1000000 UNT/ML Injectable Solution
        "901399",  # doxycycline anhydrous 40 MG Delayed Release Oral Capsule
        "1013659",  # 24 HR minocycline 105 MG Extended Release Oral Tablet
        "1013662",  # 24 HR minocycline 55 MG Extended Release Oral Tablet
        "1013665",  # 24 HR minocycline 80 MG Extended Release Oral Tablet
        "1043022",  # cefixime 100 MG Chewable Tablet
        "1043030",  # cefixime 200 MG Chewable Tablet
        "1302650",  # 24 HR minocycline 45 MG Extended Release Oral Capsule
        "1302664",  # 24 HR minocycline 90 MG Extended Release Oral Capsule
        "1302674",  # 24 HR minocycline 135 MG Extended Release Oral Capsule
        "1373014",  # cefixime 100 MG/ML Oral Suspension
        "1423080",  # doxycycline hyclate 200 MG Delayed Release Oral Tablet
        "1648755",  # nitrofurantoin, macrocrystals 25 MG / nitrofurantoin, monohydrate 75 MG Oral Capsule
        "1648759",  # nitrofurantoin, macrocrystals 100 MG Oral Capsule
        "1649401",  # doxycycline monohydrate 50 MG Oral Capsule
        "1649405",  # doxycycline hyclate 50 MG Oral Capsule
        "1649425",  # doxycycline hyclate 75 MG Oral Tablet
        "1649429",  # doxycycline monohydrate 75 MG Oral Tablet
        "1649988",  # doxycycline hyclate 100 MG Oral Capsule
        "1649990",  # doxycycline monohydrate 100 MG Oral Capsule
        "1650030",  # doxycycline monohydrate 5 MG/ML Oral Suspension
        "1650142",  # doxycycline monohydrate 100 MG Oral Tablet
        "1650143",  # doxycycline hyclate 100 MG Oral Tablet
        "1650444",  # doxycycline monohydrate 150 MG Oral Tablet
        "1650446",  # doxycycline hyclate 150 MG Oral Tablet
        "1652673",  # doxycycline monohydrate 50 MG Oral Tablet
        "1652674",  # doxycycline hyclate 50 MG Oral Tablet
        "1653433",  # doxycycline hyclate 50 MG Delayed Release Oral Tablet
        "1656313",  # cefotaxime 1000 MG Injection
        "1656318",  # cefotaxime 2000 MG Injection
        "1659131",  # piperacillin 2000 MG / tazobactam 250 MG Injection
        "1659137",  # piperacillin 3000 MG / tazobactam 375 MG Injection
        "1659149",  # piperacillin 4000 MG / tazobactam 500 MG Injection
        "1659278",  # ceftazidime 500 MG Injection
        "1659283",  # ceftazidime 1000 MG Injection
        "1659287",  # ceftazidime 2000 MG Injection
        "1659592",  # ampicillin 1000 MG / sulbactam 500 MG Injection
        "1659598",  # ampicillin 2000 MG / sulbactam 1000 MG Injection
        "1662285",  # 300 ML linezolid 2 MG/ML Injection
        "1664981",  # aztreonam 1000 MG Injection
        "1664986",  # aztreonam 2000 MG Injection
        "1665005",  # ceftriaxone 500 MG Injection
        "1665021",  # ceftriaxone 1000 MG Injection
        "1665046",  # ceftriaxone 2000 MG Injection
        "1665050",  # cefazolin 1000 MG Injection
        "1665052",  # cefazolin 500 MG Injection
        "1665060",  # cefazolin 2000 MG Injection
        "1665088",  # cefepime 2000 MG Injection
        "1665093",  # cefepime 1000 MG Injection
        "1665097",  # cefepime 500 MG Injection
        "1665102",  # cefoxitin 1000 MG Injection
        "1665107",  # cefoxitin 2000 MG Injection
        "1665210",  # 100 ML ciprofloxacin 2 MG/ML Injection
        "1665212",  # 200 ML ciprofloxacin 2 MG/ML Injection
        "1665227",  # 20 ML ciprofloxacin 10 MG/ML Injection
        "1665229",  # 40 ML ciprofloxacin 10 MG/ML Injection
        "1665444",  # cefuroxime 1500 MG Injection
        "1665449",  # cefuroxime 750 MG Injection
        "1665497",  # 50 ML levofloxacin 5 MG/ML Injection
        "1665507",  # 100 ML levofloxacin 5 MG/ML Injection
        "1665515",  # 150 ML levofloxacin 5 MG/ML Injection
        "1665517",  # 20 ML levofloxacin 25 MG/ML Injection
        "1665519",  # 30 ML levofloxacin 25 MG/ML Injection
        "1668238",  # azithromycin 500 MG Injection
        "1668264",  # erythromycin lactobionate 500 MG Injection
        "1721458",  # nafcillin 1000 MG Injection
        "1721460",  # nafcillin 2000 MG Injection
        "1721473",  # ampicillin 250 MG Injection
        "1721474",  # ampicillin 500 MG Injection
        "1721475",  # ampicillin 1000 MG Injection
        "1721476",  # ampicillin 2000 MG Injection
        "1722916",  # cefotetan 180 MG/ML Injectable Solution
        "1722919",  # cefotetan 1000 MG Injection
        "1722921",  # cefotetan 2000 MG Injection
        "1723156",  # 2 ML amikacin 250 MG/ML Injection
        "1723160",  # 4 ML amikacin 250 MG/ML Injection
        "1728082",  # telavancin 750 MG Injection
        "1737244",  # 2 ML clindamycin 150 MG/ML Injection
        "1737578",  # 4 ML clindamycin 150 MG/ML Injection
        "1737581",  # 6 ML clindamycin 150 MG/ML Injection
        "1739890",  # cefoxitin 100 MG/ML Injectable Solution
        "1743547",  # oxacillin 1000 MG Injection
        "1743549",  # oxacillin 2000 MG Injection
        "1791505",  # doxycycline hyclate 75 MG Oral Capsule
        "1801138",  # doxycycline hyclate 120 MG Delayed Release Oral Tablet
        "1807508",  # 200 ML vancomycin 5 MG/ML Injection
        "1807510",  # 150 ML vancomycin 5 MG/ML Injection
        "1807511",  # 100 ML vancomycin 5 MG/ML Injection
        "1807513",  # vancomycin 1000 MG Injection
        "1807516",  # vancomycin 500 MG Injection
        "1807518",  # vancomycin 750 MG Injection
        "1870631",  # 100 ML gentamicin 1.2 MG/ML Injection
        "1870633",  # 50 ML gentamicin 1.2 MG/ML Injection
        "1870650",  # 2 ML gentamicin 40 MG/ML Injection
        "1870676",  # 2 ML gentamicin 10 MG/ML Injection
        "1870681",  # 6 ML gentamicin 10 MG/ML Injection
        "1870685",  # 8 ML gentamicin 10 MG/ML Injection
        "1870686",  # 10 ML gentamicin 10 MG/ML Injection
        "1996246",  # daptomycin 350 MG Injection
        "1998483",  # doxycycline hyclate 200 MG Injection
        "2000127",  # vancomycin 25 MG/ML Oral Solution
        "2000134",  # vancomycin 50 MG/ML Oral Solution
        "2387078",  # 250 ML vancomycin 5 MG/ML Injection
        "2387079",  # 350 ML vancomycin 5 MG/ML Injection
    }


class ContraceptiveMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for contraceptive medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable contraceptive medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS153v10
    """

    VALUE_SET_NAME = "Contraceptive Medications"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1080"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "198042",  # norethindrone 0.35 MG Oral Tablet
        "238015",  # ethinyl estradiol 0.035 MG / norethindrone 0.4 MG Oral Tablet
        "238019",  # ethinyl estradiol 0.03 MG / levonorgestrel 0.15 MG Oral Tablet
        "240128",  # ethinyl estradiol 0.035 MG / norgestimate 0.25 MG Oral Tablet
        "240707",  # desogestrel 0.15 MG / ethinyl estradiol 0.03 MG Oral Tablet
        "242297",  # ethinyl estradiol 0.02 MG / levonorgestrel 0.1 MG Oral Tablet
        "248310",  # ethinyl estradiol 0.01 MG Oral Tablet
        "249357",  # desogestrel 0.15 MG / ethinyl estradiol 0.02 MG Oral Tablet
        "259218",  # levonorgestrel 0.75 MG Oral Tablet
        "310228",  # ethinyl estradiol 0.035 MG / ethynodiol diacetate 1 MG Oral Tablet
        "310230",  # ethinyl estradiol 0.03 MG / levonorgestrel 0.05 MG Oral Tablet
        "310463",  # ethinyl estradiol 0.035 MG / norethindrone 0.5 MG Oral Tablet
        "311359",  # ethinyl estradiol 0.03 MG / norgestrel 0.3 MG Oral Tablet
        "312033",  # ethinyl estradiol 0.035 MG / norethindrone 1 MG Oral Tablet
        "312124",  # ethinyl estradiol 0.05 MG / norethindrone 1 MG Oral Tablet
        "314146",  # ethinyl estradiol 0.05 MG / norgestrel 0.5 MG Oral Tablet
        "315096",  # ethinyl estradiol 0.05 MG / ethynodiol diacetate 1 MG Oral Tablet
        "348804",  # ethinyl estradiol 0.03 MG / levonorgestrel 0.125 MG Oral Tablet
        "348805",  # ethinyl estradiol 0.04 MG / levonorgestrel 0.075 MG Oral Tablet
        "389221",  # etonogestrel 68 MG Drug Implant
        "392662",  # ethinyl estradiol 0.035 MG / norethindrone 0.75 MG Oral Tablet
        "402250",  # 168 HR estradiol 0.00188 MG/HR / levonorgestrel 0.000625 MG/HR Transdermal System
        "406396",  # ethinyl estradiol 0.035 MG / norgestimate 0.18 MG Oral Tablet
        "433718",  # ethinyl estradiol 0.035 MG / norethindrone 0.4 MG Chewable Tablet
        "483325",  # levonorgestrel 1.5 MG Oral Tablet
        "578732",  # ethinyl estradiol 0.025 MG / norgestimate 0.18 MG Oral Tablet
        "654353",  # desogestrel 0.1 MG / ethinyl estradiol 0.025 MG Oral Tablet
        "687424",  # ethinyl estradiol 0.035 MG / norgestimate 0.215 MG Oral Tablet
        "722152",  # ethinyl estradiol 0.02 MG / levonorgestrel 0.09 MG Oral Tablet
        "729534",  # desogestrel 0.15 MG / ethinyl estradiol 0.025 MG Oral Tablet
        "748798",  # {24 (drospirenone 3 MG / ethinyl estradiol 0.02 MG Oral Tablet) / 4 (inert ingredients 1 MG Oral Tablet) } Pack
        "748800",  # {21 (drospirenone 3 MG / ethinyl estradiol 0.03 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "748804",  # {21 (ethinyl estradiol 0.035 MG / ethynodiol diacetate 1 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "748806",  # {21 (ethinyl estradiol 0.05 MG / ethynodiol diacetate 1 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "748832",  # {6 (ethinyl estradiol 0.03 MG / levonorgestrel 0.05 MG Oral Tablet) / 10 (ethinyl estradiol 0.03 MG / levonorgestrel 0.125 MG Oral Tablet) / 5 (ethinyl estradiol 0.04 MG / levonorgestrel 0.075 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "748868",  # {21 (ethinyl estradiol 0.02 MG / levonorgestrel 0.1 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "748878",  # {21 (ethinyl estradiol 0.03 MG / levonorgestrel 0.15 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "748961",  # {28 (norethindrone 0.35 MG Oral Tablet) } Pack
        "749155",  # ethinyl estradiol 0.025 MG / norgestimate 0.215 MG Oral Tablet
        "749156",  # ethinyl estradiol 0.025 MG / norgestimate 0.25 MG Oral Tablet
        "749157",  # {7 (ethinyl estradiol 0.025 MG / norgestimate 0.18 MG Oral Tablet) / 7 (ethinyl estradiol 0.025 MG / norgestimate 0.215 MG Oral Tablet) / 7 (ethinyl estradiol 0.025 MG / norgestimate 0.25 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "749736",  # {21 (ethinyl estradiol 0.035 MG / norethindrone 0.4 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "749761",  # {7 (ethinyl estradiol 0.01 MG Oral Tablet) / 84 (ethinyl estradiol 0.03 MG / levonorgestrel 0.15 MG Oral Tablet) } Pack
        "749784",  # {7 (ethinyl estradiol 0.035 MG / norgestimate 0.18 MG Oral Tablet) / 7 (ethinyl estradiol 0.035 MG / norgestimate 0.215 MG Oral Tablet) / 7 (ethinyl estradiol 0.035 MG / norgestimate 0.25 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "749786",  # {21 (ethinyl estradiol 0.03 MG / norgestrel 0.3 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "749848",  # {21 (desogestrel 0.15 MG / ethinyl estradiol 0.03 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "749852",  # {7 (ethinyl estradiol 0.035 MG / norethindrone 0.5 MG Oral Tablet) / 7 (ethinyl estradiol 0.035 MG / norethindrone 0.75 MG Oral Tablet) / 7 (ethinyl estradiol 0.035 MG / norethindrone 1 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "749858",  # {21 (ethinyl estradiol 0.035 MG / norethindrone 1 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "749860",  # {21 (ethinyl estradiol 0.035 MG / norgestimate 0.25 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "749869",  # {21 (ethinyl estradiol 0.035 MG / norethindrone 1 MG Oral Tablet) } Pack
        "749879",  # {21 (ethinyl estradiol 0.035 MG / norethindrone 0.5 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "750242",  # {21 (ethinyl estradiol 0.05 MG / norgestrel 0.5 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "751553",  # {28 (ethinyl estradiol 0.02 MG / levonorgestrel 0.09 MG Oral Tablet) } Pack
        "751901",  # {84 (ethinyl estradiol 0.03 MG / levonorgestrel 0.15 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "753476",  # {21 (ethinyl estradiol 0.05 MG / norethindrone 1 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "759741",  # desogestrel 0.125 MG / ethinyl estradiol 0.025 MG Oral Tablet
        "759742",  # {7 (desogestrel 0.1 MG / ethinyl estradiol 0.025 MG Oral Tablet) / 7 (desogestrel 0.125 MG / ethinyl estradiol 0.025 MG Oral Tablet) / 7 (desogestrel 0.15 MG / ethinyl estradiol 0.025 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "759743",  # {21 (desogestrel 0.15 MG / ethinyl estradiol 0.02 MG Oral Tablet) / 5 (ethinyl estradiol 0.01 MG Oral Tablet) / 2 (inert ingredients 1 MG Oral Tablet) } Pack
        "763088",  # {2 (levonorgestrel 0.75 MG Oral Tablet) } Pack
        "810096",  # {7 (ethinyl estradiol 0.01 MG Oral Tablet) / 84 (ethinyl estradiol 0.02 MG / levonorgestrel 0.1 MG Oral Tablet) } Pack
        "823777",  # {12 (ethinyl estradiol 0.035 MG / norethindrone 0.5 MG Oral Tablet) / 9 (ethinyl estradiol 0.035 MG / norethindrone 1 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "978949",  # {5 (dienogest 2 MG / estradiol valerate 2 MG Oral Tablet) / 17 (dienogest 3 MG / estradiol valerate 2 MG Oral Tablet) / 2 (estradiol valerate 1 MG Oral Tablet) / 2 (estradiol valerate 3 MG Oral Tablet) / 2 (inert ingredients 1 MG Oral Tablet) } Pack
        "1000126",  # 1 ML medroxyprogesterone acetate 150 MG/ML Injection
        "1000131",  # medroxyprogesterone acetate 400 MG/ML Injectable Suspension
        "1000153",  # 1 ML medroxyprogesterone acetate 150 MG/ML Prefilled Syringe
        "1000156",  # 0.65 ML medroxyprogesterone acetate 160 MG/ML Prefilled Syringe
        "1013629",  # {24 (drospirenone 3 MG / ethinyl estradiol 0.02 MG / levomefolate calcium 0.451 MG Oral Tablet) / 4 (levomefolate calcium 0.451 MG Oral Tablet) } Pack
        "1037183",  # ethinyl estradiol 0.01 MG / norethindrone acetate 1 MG Oral Tablet
        "1037184",  # {24 (ethinyl estradiol 0.01 MG / norethindrone acetate 1 MG Oral Tablet) / 2 (ethinyl estradiol 0.01 MG Oral Tablet) / 2 (ferrous fumarate 75 MG Oral Tablet) } Pack
        "1050493",  # {21 (drospirenone 3 MG / ethinyl estradiol 0.03 MG / levomefolate calcium 0.451 MG Oral Tablet) / 7 (levomefolate calcium 0.451 MG Oral Tablet) } Pack
        "1090992",  # ethinyl estradiol 0.005 MG / norethindrone acetate 1 MG Oral Tablet
        "1095224",  # {21 (ethinyl estradiol 0.035 MG / norethindrone 0.4 MG Chewable Tablet) / 7 (ferrous fumarate 75 MG Chewable Tablet) } Pack
        "1099638",  # ethinyl estradiol 0.025 MG / norethindrone 0.8 MG Chewable Tablet
        "1251323",  # ethinyl estradiol 0.0025 MG / norethindrone acetate 0.5 MG Oral Tablet
        "1251334",  # {28 (ethinyl estradiol 0.0025 MG / norethindrone acetate 0.5 MG Oral Tablet) } Pack
        "1251336",  # {28 (ethinyl estradiol 0.005 MG / norethindrone acetate 1 MG Oral Tablet) } Pack
        "1358762",  # ethinyl estradiol 0.02 MG / norethindrone acetate 1 MG Oral Tablet
        "1358763",  # {21 (ethinyl estradiol 0.02 MG / norethindrone acetate 1 MG Oral Tablet) / 7 (ferrous fumarate 75 MG Oral Tablet) } Pack
        "1358776",  # {21 (ethinyl estradiol 0.02 MG / norethindrone acetate 1 MG Oral Tablet) } Pack
        "1359022",  # ethinyl estradiol 0.03 MG / norethindrone acetate 1.5 MG Oral Tablet
        "1359023",  # {21 (ethinyl estradiol 0.03 MG / norethindrone acetate 1.5 MG Oral Tablet) / 7 (ferrous fumarate 75 MG Oral Tablet) } Pack
        "1359028",  # {21 (ethinyl estradiol 0.03 MG / norethindrone acetate 1.5 MG Oral Tablet) } Pack
        "1359117",  # {24 (ethinyl estradiol 0.02 MG / norethindrone acetate 1 MG Oral Tablet) / 4 (ferrous fumarate 75 MG Oral Tablet) } Pack
        "1359130",  # ethinyl estradiol 0.03 MG / norethindrone acetate 1 MG Oral Tablet
        "1359131",  # ethinyl estradiol 0.035 MG / norethindrone acetate 1 MG Oral Tablet
        "1359132",  # {5 (ethinyl estradiol 0.02 MG / norethindrone acetate 1 MG Oral Tablet) / 7 (ethinyl estradiol 0.03 MG / norethindrone acetate 1 MG Oral Tablet) / 9 (ethinyl estradiol 0.035 MG / norethindrone acetate 1 MG Oral Tablet) / 7 (ferrous fumarate 75 MG Oral Tablet) } Pack
        "1367436",  # 21 DAY ethinyl estradiol 0.000625 MG/HR / etonogestrel 0.005 MG/HR Vaginal System
        "1373501",  # ethinyl estradiol 0.02 MG / levonorgestrel 0.15 MG Oral Tablet
        "1373502",  # ethinyl estradiol 0.025 MG / levonorgestrel 0.15 MG Oral Tablet
        "1373503",  # {7 (ethinyl estradiol 0.01 MG Oral Tablet) / 42 (ethinyl estradiol 0.02 MG / levonorgestrel 0.15 MG Oral Tablet) / 21 (ethinyl estradiol 0.025 MG / levonorgestrel 0.15 MG Oral Tablet) / 21 (ethinyl estradiol 0.03 MG / levonorgestrel 0.15 MG Oral Tablet) } Pack
        "1421459",  # ethinyl estradiol 0.02 MG / norethindrone acetate 1 MG Oral Capsule
        "1426288",  # ethinyl estradiol 0.02 MG / norethindrone acetate 1 MG Chewable Tablet
        "2396242",  # 168 HR ethinyl estradiol 0.00125 MG/HR / levonorgestrel 0.005 MG/HR Transdermal System
        "2396253",  # {3 (168 HR ethinyl estradiol 0.00125 MG/HR / levonorgestrel 0.005 MG/HR Transdermal System) } Pack
    }


class Isotretinoin(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for isotretinoin medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable isotretinoin and isotretinoin in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS153v10
    """

    VALUE_SET_NAME = "Isotretinoin"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1143"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197843",  # isotretinoin 10 MG Oral Capsule
        "197844",  # isotretinoin 20 MG Oral Capsule
        "197845",  # isotretinoin 40 MG Oral Capsule
        "403930",  # isotretinoin 30 MG Oral Capsule
        "1547561",  # isotretinoin 25 MG Oral Capsule
        "1547565",  # isotretinoin 35 MG Oral Capsule
    }


class AmitriptylineHydrochloride(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for amitriptyline hydrochloride.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable amitriptyline hydrochloride and amitriptyline hydrochloride in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Amitriptyline Hydrochloride"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1373"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "856706",  # amitriptyline hydrochloride 10 MG / perphenazine 2 MG Oral Tablet
        "856720",  # amitriptyline hydrochloride 10 MG / perphenazine 4 MG Oral Tablet
        "856762",  # amitriptyline hydrochloride 100 MG Oral Tablet
        "856769",  # amitriptyline hydrochloride 12.5 MG / chlordiazepoxide 5 MG Oral Tablet
        "856773",  # amitriptyline hydrochloride 150 MG Oral Tablet
        "856783",  # amitriptyline hydrochloride 10 MG Oral Tablet
        "856792",  # amitriptyline hydrochloride 25 MG / chlordiazepoxide 10 MG Oral Tablet
        "856797",  # amitriptyline hydrochloride 25 MG / perphenazine 2 MG Oral Tablet
        "856825",  # amitriptyline hydrochloride 25 MG / perphenazine 4 MG Oral Tablet
        "856834",  # amitriptyline hydrochloride 25 MG Oral Tablet
        "856840",  # amitriptyline hydrochloride 50 MG / perphenazine 4 MG Oral Tablet
        "856845",  # amitriptyline hydrochloride 50 MG Oral Tablet
        "856853",  # amitriptyline hydrochloride 75 MG Oral Tablet
    }


class Amoxapine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for amoxapine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable amoxapine and amoxapine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Amoxapine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1273"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197363",  # amoxapine 100 MG Oral Tablet
        "197364",  # amoxapine 150 MG Oral Tablet
        "197365",  # amoxapine 25 MG Oral Tablet
        "197366",  # amoxapine 50 MG Oral Tablet
    }


class AntiInfectives_Other(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for nitrofurantoin medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable nitrofurantoin and nitrofurantoin in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Anti Infectives, other"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1481"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "311989",  # nitrofurantoin 5 MG/ML Oral Suspension
        "311994",  # nitrofurantoin, macrocrystals 25 MG Oral Capsule
        "311995",  # nitrofurantoin, macrocrystals 50 MG Oral Capsule
        "1648755",  # nitrofurantoin, macrocrystals 25 MG / nitrofurantoin, monohydrate 75 MG Oral Capsule
        "1648759",  # nitrofurantoin, macrocrystals 100 MG Oral Capsule
    }


class Antipsychotic(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for antipsychotic medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable antipsychotic medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Antipsychotic"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1523"
    DEFINITION_VERSION = "20210224"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "141935",  # haloperidol 2 MG/ML Oral Solution
        "197535",  # clozapine 100 MG Oral Tablet
        "197536",  # clozapine 25 MG Oral Tablet
        "197754",  # haloperidol 20 MG Oral Tablet
        "198075",  # perphenazine 16 MG Oral Tablet
        "198076",  # perphenazine 2 MG Oral Tablet
        "198077",  # perphenazine 4 MG Oral Tablet
        "198078",  # perphenazine 8 MG Oral Tablet
        "198103",  # pimozide 2 MG Oral Tablet
        "198270",  # thioridazine 100 MG Oral Tablet
        "198274",  # thioridazine 25 MG Oral Tablet
        "198275",  # thioridazine 50 MG Oral Tablet
        "198322",  # trifluoperazine 1 MG Oral Tablet
        "198323",  # trifluoperazine 10 MG Oral Tablet
        "198324",  # trifluoperazine 2 MG Oral Tablet
        "198325",  # trifluoperazine 5 MG Oral Tablet
        "199387",  # risperidone 1 MG/ML Oral Solution
        "200034",  # olanzapine 2.5 MG Oral Tablet
        "204416",  # haloperidol 5 MG/ML Injectable Solution
        "283639",  # olanzapine 20 MG Oral Tablet
        "309374",  # clozapine 200 MG Oral Tablet
        "310670",  # haloperidol 0.5 MG Oral Tablet
        "310671",  # haloperidol 1 MG Oral Tablet
        "310672",  # haloperidol 5 MG Oral Tablet
        "311385",  # loxapine 25 MG Oral Capsule
        "311386",  # loxapine 5 MG Oral Capsule
        "312076",  # olanzapine 10 MG Disintegrating Oral Tablet
        "312077",  # olanzapine 15 MG Oral Tablet
        "312078",  # olanzapine 5 MG Oral Tablet
        "312079",  # olanzapine 7.5 MG Oral Tablet
        "312439",  # pimozide 1 MG Oral Tablet
        "312743",  # quetiapine 100 MG Oral Tablet
        "312744",  # quetiapine 25 MG Oral Tablet
        "312745",  # quetiapine 300 MG Oral Tablet
        "312828",  # risperidone 0.25 MG Oral Tablet
        "312829",  # risperidone 0.5 MG Oral Tablet
        "312830",  # risperidone 1 MG Oral Tablet
        "312831",  # risperidone 2 MG Oral Tablet
        "312832",  # risperidone 3 MG Oral Tablet
        "313354",  # thioridazine 10 MG Oral Tablet
        "313361",  # thiothixene 10 MG Oral Capsule
        "313362",  # thiothixene 1 MG Oral Capsule
        "313364",  # thiothixene 2 MG Oral Capsule
        "313366",  # thiothixene 5 MG Oral Capsule
        "313776",  # ziprasidone 40 MG Oral Capsule
        "313777",  # ziprasidone 60 MG Oral Capsule
        "313778",  # ziprasidone 80 MG Oral Capsule
        "314034",  # haloperidol 2 MG Oral Tablet
        "314035",  # haloperidol 10 MG Oral Tablet
        "314075",  # loxapine 50 MG Oral Capsule
        "314078",  # loxapine 10 MG Oral Capsule
        "314154",  # olanzapine 10 MG Oral Tablet
        "314155",  # olanzapine 5 MG Disintegrating Oral Tablet
        "314211",  # risperidone 4 MG Oral Tablet
        "314286",  # ziprasidone 20 MG Oral Capsule
        "317174",  # quetiapine 200 MG Oral Tablet
        "349490",  # aripiprazole 15 MG Oral Tablet
        "349545",  # aripiprazole 10 MG Oral Tablet
        "349547",  # aripiprazole 30 MG Oral Tablet
        "349553",  # aripiprazole 20 MG Oral Tablet
        "351107",  # olanzapine 15 MG Disintegrating Oral Tablet
        "351108",  # olanzapine 20 MG Disintegrating Oral Tablet
        "351223",  # ziprasidone 20 MG Injection
        "389201",  # quetiapine 150 MG Oral Tablet
        "401953",  # risperidone 1 MG Disintegrating Oral Tablet
        "401954",  # risperidone 2 MG Disintegrating Oral Tablet
        "402010",  # risperidone 25 MG Injection
        "402011",  # risperidone 37.5 MG Injection
        "402012",  # risperidone 50 MG Injection
        "402131",  # aripiprazole 5 MG Oral Tablet
        "403825",  # risperidone 0.5 MG Disintegrating Oral Tablet
        "403969",  # fluoxetine 25 MG / olanzapine 6 MG Oral Capsule
        "403970",  # fluoxetine 25 MG / olanzapine 12 MG Oral Capsule
        "403971",  # fluoxetine 50 MG / olanzapine 12 MG Oral Capsule
        "403972",  # fluoxetine 50 MG / olanzapine 6 MG Oral Capsule
        "429212",  # clozapine 50 MG Oral Tablet
        "476177",  # clozapine 100 MG Disintegrating Oral Tablet
        "476179",  # clozapine 25 MG Disintegrating Oral Tablet
        "485496",  # aripiprazole 1 MG/ML Oral Solution
        "485968",  # olanzapine 10 MG Injection
        "602964",  # aripiprazole 2 MG Oral Tablet
        "616483",  # quetiapine 400 MG Oral Tablet
        "616487",  # quetiapine 50 MG Oral Tablet
        "616698",  # risperidone 3 MG Disintegrating Oral Tablet
        "616705",  # risperidone 4 MG Disintegrating Oral Tablet
        "643019",  # aripiprazole 10 MG Disintegrating Oral Tablet
        "643022",  # aripiprazole 15 MG Disintegrating Oral Tablet
        "643027",  # aripiprazole 20 MG Disintegrating Oral Tablet
        "643058",  # aripiprazole 30 MG Disintegrating Oral Tablet
        "645037",  # risperidone 0.25 MG Disintegrating Oral Tablet
        "672567",  # 24 HR paliperidone 3 MG Extended Release Oral Tablet
        "672569",  # 24 HR paliperidone 6 MG Extended Release Oral Tablet
        "672571",  # 24 HR paliperidone 9 MG Extended Release Oral Tablet
        "706822",  # risperidone 12.5 MG Injection
        "721773",  # clozapine 12.5 MG Disintegrating Oral Tablet
        "721787",  # fluoxetine 25 MG / olanzapine 3 MG Oral Capsule
        "721791",  # 24 HR quetiapine 200 MG Extended Release Oral Tablet
        "721794",  # 24 HR quetiapine 300 MG Extended Release Oral Tablet
        "721796",  # 24 HR quetiapine 400 MG Extended Release Oral Tablet
        "848722",  # iloperidone 1 MG Oral Tablet
        "848728",  # iloperidone 10 MG Oral Tablet
        "848732",  # iloperidone 12 MG Oral Tablet
        "848736",  # iloperidone 2 MG Oral Tablet
        "848740",  # iloperidone 4 MG Oral Tablet
        "848744",  # iloperidone 6 MG Oral Tablet
        "848748",  # iloperidone 8 MG Oral Tablet
        "848751",  # {2 (iloperidone 1 MG Oral Tablet) / 2 (iloperidone 2 MG Oral Tablet) / 2 (iloperidone 4 MG Oral Tablet) / 2 (iloperidone 6 MG Oral Tablet) } Pack
        "853201",  # 24 HR quetiapine 50 MG Extended Release Oral Tablet
        "856706",  # amitriptyline hydrochloride 10 MG / perphenazine 2 MG Oral Tablet
        "856720",  # amitriptyline hydrochloride 10 MG / perphenazine 4 MG Oral Tablet
        "856797",  # amitriptyline hydrochloride 25 MG / perphenazine 2 MG Oral Tablet
        "856825",  # amitriptyline hydrochloride 25 MG / perphenazine 4 MG Oral Tablet
        "856840",  # amitriptyline hydrochloride 50 MG / perphenazine 4 MG Oral Tablet
        "858048",  # 0.5 ML paliperidone palmitate 156 MG/ML Prefilled Syringe
        "858052",  # 1.5 ML paliperidone palmitate 156 MG/ML Prefilled Syringe
        "858054",  # 1 ML paliperidone palmitate 156 MG/ML Prefilled Syringe
        "858056",  # 0.75 ML paliperidone palmitate 156 MG/ML Prefilled Syringe
        "858073",  # 0.25 ML paliperidone palmitate 156 MG/ML Prefilled Syringe
        "859824",  # fluphenazine decanoate 25 MG/ML Injectable Solution
        "859835",  # fluphenazine hydrochloride 0.5 MG/ML Oral Solution
        "859841",  # fluphenazine hydrochloride 10 MG Oral Tablet
        "859867",  # haloperidol decanoate 50 MG/ML Injectable Solution
        "859871",  # haloperidol decanoate 100 MG/ML Injectable Solution
        "859975",  # asenapine 10 MG Sublingual Tablet
        "859981",  # asenapine 5 MG Sublingual Tablet
        "860918",  # fluphenazine hydrochloride 5 MG Oral Tablet
        "861848",  # fluphenazine hydrochloride 5 MG/ML Oral Solution
        "865117",  # fluphenazine hydrochloride 1 MG Oral Tablet
        "865123",  # fluphenazine hydrochloride 2.5 MG Oral Tablet
        "865129",  # fluphenazine hydrochloride 2.5 MG/ML Injectable Solution
        "866103",  # 24 HR paliperidone 1.5 MG Extended Release Oral Tablet
        "895670",  # 24 HR quetiapine 150 MG Extended Release Oral Tablet
        "991039",  # chlorpromazine hydrochloride 10 MG Oral Tablet
        "991044",  # chlorpromazine hydrochloride 100 MG Oral Tablet
        "991188",  # chlorpromazine hydrochloride 200 MG Oral Tablet
        "991194",  # chlorpromazine hydrochloride 25 MG Oral Tablet
        "991336",  # chlorpromazine hydrochloride 50 MG Oral Tablet
        "996921",  # clozapine 200 MG Disintegrating Oral Tablet
        "1006801",  # clozapine 150 MG Disintegrating Oral Tablet
        "1040031",  # lurasidone hydrochloride 40 MG Oral Tablet
        "1040041",  # lurasidone hydrochloride 80 MG Oral Tablet
        "1235247",  # lurasidone hydrochloride 20 MG Oral Tablet
        "1297278",  # lurasidone hydrochloride 120 MG Oral Tablet
        "1298816",  # molindone hydrochloride 10 MG Oral Tablet
        "1298906",  # molindone hydrochloride 25 MG Oral Tablet
        "1298910",  # molindone hydrochloride 5 MG Oral Tablet
        "1367518",  # 1 ACTUAT loxapine 10 MG/ACTUAT Dry Powder Inhaler
        "1369825",  # clozapine 50 MG/ML Oral Suspension
        "1431235",  # lurasidone hydrochloride 60 MG Oral Tablet
        "1602163",  # 1.5 ML aripiprazole 200 MG/ML Prefilled Syringe
        "1602171",  # 2 ML aripiprazole 200 MG/ML Prefilled Syringe
        "1606337",  # asenapine 2.5 MG Sublingual Tablet
        "1648646",  # {1 (24 HR quetiapine 200 MG Extended Release Oral Tablet) / 11 (24 HR quetiapine 300 MG Extended Release Oral Tablet) / 3 (24 HR quetiapine 50 MG Extended Release Oral Tablet) } Pack
        "1650966",  # 0.875 ML paliperidone palmitate 312 MG/ML Prefilled Syringe
        "1650971",  # 1.315 ML paliperidone palmitate 312 MG/ML Prefilled Syringe
        "1650973",  # 1.75 ML paliperidone palmitate 312 MG/ML Prefilled Syringe
        "1650975",  # 2.625 ML paliperidone palmitate 312 MG/ML Prefilled Syringe
        "1658319",  # brexpiprazole 0.25 MG Oral Tablet
        "1658327",  # brexpiprazole 0.5 MG Oral Tablet
        "1658331",  # brexpiprazole 1 MG Oral Tablet
        "1658335",  # brexpiprazole 2 MG Oral Tablet
        "1658339",  # brexpiprazole 3 MG Oral Tablet
        "1658343",  # brexpiprazole 4 MG Oral Tablet
        "1659812",  # aripiprazole 400 MG Injection
        "1659816",  # aripiprazole 300 MG Injection
        "1667660",  # cariprazine 1.5 MG Oral Capsule
        "1667668",  # cariprazine 3 MG Oral Capsule
        "1667672",  # cariprazine 4.5 MG Oral Capsule
        "1667676",  # cariprazine 6 MG Oral Capsule
        "1673269",  # 1.6 ML aripiprazole lauroxil 276 MG/ML Prefilled Syringe
        "1673277",  # 2.4 ML aripiprazole lauroxil 276 MG/ML Prefilled Syringe
        "1673279",  # 3.2 ML aripiprazole lauroxil 276 MG/ML Prefilled Syringe
        "1718925",  # olanzapine 405 MG Injection
        "1718930",  # olanzapine 300 MG Injection
        "1718934",  # olanzapine 210 MG Injection
        "1719646",  # 1 ML haloperidol 5 MG/ML Injection
        "1719803",  # 1 ML haloperidol decanoate 100 MG/ML Injection
        "1719862",  # 1 ML haloperidol decanoate 50 MG/ML Injection
        "1730076",  # 1 ML chlorpromazine hydrochloride 25 MG/ML Injection
        "1730078",  # 2 ML chlorpromazine hydrochloride 25 MG/ML Injection
        "1741746",  # {1 (cariprazine 1.5 MG Oral Capsule) / 6 (cariprazine 3 MG Oral Capsule) } Pack
        "1791691",  # pimavanserin 17 MG Oral Tablet
        "1876502",  # 1 ML haloperidol 5 MG/ML Prefilled Syringe
        "1925262",  # 3.9 ML aripiprazole lauroxil 273 MG/ML Prefilled Syringe
        "1998451",  # Sensor aripiprazole 10 MG Oral Tablet
        "1998454",  # Sensor aripiprazole 15 MG Oral Tablet
        "1998456",  # Sensor aripiprazole 2 MG Oral Tablet
        "1998458",  # Sensor aripiprazole 20 MG Oral Tablet
        "1998460",  # Sensor aripiprazole 30 MG Oral Tablet
        "1998462",  # Sensor aripiprazole 5 MG Oral Tablet
        "2049269",  # pimavanserin 10 MG Oral Tablet
        "2049275",  # pimavanserin 34 MG Oral Capsule
        "2049341",  # 2.4 ML aripiprazole lauroxil 281.3 MG/ML Prefilled Syringe
        "2055667",  # 0.8 ML risperidone 150 MG/ML Prefilled Syringe
        "2055675",  # 0.6 ML risperidone 150 MG/ML Prefilled Syringe
    }


class Atropine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for atropine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable atropine and atropine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Atropine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1274"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "727415",  # 2.7 ML atropine 0.778 MG/ML / pralidoxime chloride 222 MG/ML Auto-Injector
        "1046787",  # atropine sulfate 0.00388 MG/ML / hyoscyamine sulfate 0.0207 MG/ML / phenobarbital 3.24 MG/ML / scopolamine hydrobromide 0.0013 MG/ML Oral Solution
        "1046815",  # atropine sulfate 0.0194 MG / hyoscyamine sulfate 0.1037 MG / phenobarbital 16.2 MG / scopolamine hydrobromide 0.0065 MG Oral Tablet
        "1046997",  # atropine sulfate 0.0582 MG / hyoscyamine sulfate 0.311 MG / phenobarbital 48.6 MG / scopolamine hydrobromide 0.0195 MG Extended Release Oral Tablet
        "1048124",  # 12 HR atropine sulfate 0.04 MG / chlorpheniramine maleate 8 MG / hyoscyamine sulfate 0.19 MG / pseudoephedrine hydrochloride 90 MG / scopolamine hydrobromide 0.01 MG Extended Release Oral Tablet
        "1048147",  # atropine sulfate 0.0582 MG / hyoscyamine sulfate 0.3111 MG / phenobarbital 48.6 MG / scopolamine hydrobromide 0.0195 MG Extended Release Oral Tablet
        "1190538",  # 0.7 ML atropine sulfate 0.714 MG/ML Auto-Injector
        "1190540",  # 0.7 ML atropine sulfate 1.43 MG/ML Auto-Injector
        "1190542",  # 0.7 ML atropine sulfate 2.86 MG/ML Auto-Injector
        "1190546",  # 10 ML atropine sulfate 0.1 MG/ML Prefilled Syringe
        "1190551",  # 5 ML atropine sulfate 0.05 MG/ML Prefilled Syringe
        "1190552",  # 5 ML atropine sulfate 0.1 MG/ML Prefilled Syringe
        "1190568",  # atropine sulfate 0.005 MG/ML / diphenoxylate hydrochloride 0.5 MG/ML Oral Solution
        "1190572",  # atropine sulfate 0.025 MG / diphenoxylate hydrochloride 2.5 MG Oral Tablet
        "1190738",  # atropine sulfate 0.025 MG / difenoxin hydrochloride 1 MG Oral Tablet
        "1190748",  # 5 ML atropine sulfate 0.14 MG/ML / edrophonium chloride 10 MG/ML Injection
        "1190776",  # atropine sulfate 0.4 MG/ML Injectable Solution
        "1190793",  # 0.5 ML atropine sulfate 0.8 MG/ML Injection
        "1190795",  # 1 ML atropine sulfate 1 MG/ML Injection
        "1666781",  # 1 ML atropine sulfate 0.4 MG/ML Injection
    }


class Benzodiazepine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for benzodiazepine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable benzodiazepine medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Benzodiazepine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1522"
    DEFINITION_VERSION = "20210224"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197321",  # alprazolam 1 MG Oral Tablet
        "197322",  # alprazolam 2 MG Oral Tablet
        "197464",  # clorazepate dipotassium 15 MG Oral Tablet
        "197465",  # clorazepate dipotassium 3.75 MG Oral Tablet
        "197466",  # clorazepate dipotassium 7.5 MG Oral Tablet
        "197527",  # clonazepam 0.5 MG Oral Tablet
        "197528",  # clonazepam 1 MG Oral Tablet
        "197529",  # clonazepam 2 MG Oral Tablet
        "197589",  # diazepam 10 MG Oral Tablet
        "197590",  # diazepam 2 MG Oral Tablet
        "197591",  # diazepam 5 MG Oral Tablet
        "197900",  # lorazepam 0.5 MG Oral Tablet
        "197901",  # lorazepam 1 MG Oral Tablet
        "197902",  # lorazepam 2 MG Oral Tablet
        "198057",  # oxazepam 10 MG Oral Capsule
        "198059",  # oxazepam 30 MG Oral Capsule
        "198241",  # temazepam 15 MG Oral Capsule
        "198242",  # temazepam 30 MG Oral Capsule
        "198243",  # temazepam 7.5 MG Oral Capsule
        "238100",  # lorazepam 2 MG/ML Injectable Solution
        "238101",  # lorazepam 4 MG/ML Injectable Solution
        "308047",  # alprazolam 0.25 MG Oral Tablet
        "308048",  # alprazolam 0.5 MG Oral Tablet
        "308050",  # alprazolam 1 MG/ML Oral Solution
        "309843",  # diazepam 1 MG/ML Oral Solution
        "309844",  # diazepam 5 MG/ML Oral Solution
        "309845",  # diazepam 5 MG/ML Injectable Solution
        "311376",  # lorazepam 2 MG/ML Oral Solution
        "311700",  # midazolam 1 MG/ML Injectable Solution
        "311702",  # midazolam 5 MG/ML Injectable Solution
        "312134",  # oxazepam 15 MG Oral Capsule
        "349194",  # clonazepam 0.125 MG Disintegrating Oral Tablet
        "349195",  # clonazepam 0.25 MG Disintegrating Oral Tablet
        "349196",  # clonazepam 1 MG Disintegrating Oral Tablet
        "349197",  # clonazepam 2 MG Disintegrating Oral Tablet
        "349198",  # clonazepam 0.5 MG Disintegrating Oral Tablet
        "422410",  # midazolam 2 MG/ML Oral Solution
        "433798",  # 24 HR alprazolam 0.5 MG Extended Release Oral Tablet
        "433799",  # 24 HR alprazolam 2 MG Extended Release Oral Tablet
        "433800",  # 24 HR alprazolam 1 MG Extended Release Oral Tablet
        "433801",  # 24 HR alprazolam 3 MG Extended Release Oral Tablet
        "485413",  # alprazolam 0.25 MG Disintegrating Oral Tablet
        "485414",  # alprazolam 1 MG Disintegrating Oral Tablet
        "485415",  # alprazolam 0.5 MG Disintegrating Oral Tablet
        "485416",  # alprazolam 2 MG Disintegrating Oral Tablet
        "485489",  # temazepam 22.5 MG Oral Capsule
        "763028",  # 1 ML lorazepam 2 MG/ML Cartridge
        "763029",  # 1 ML lorazepam 4 MG/ML Cartridge
        "801957",  # 0.5 ML diazepam 5 MG/ML Rectal Gel
        "801961",  # 2 ML diazepam 5 MG/ML Rectal Gel
        "801966",  # 4 ML diazepam 5 MG/ML Rectal Gel
        "856769",  # amitriptyline hydrochloride 12.5 MG / chlordiazepoxide 5 MG Oral Tablet
        "856792",  # amitriptyline hydrochloride 25 MG / chlordiazepoxide 10 MG Oral Tablet
        "889614",  # chlordiazepoxide hydrochloride 5 MG / clidinium bromide 2.5 MG Oral Capsule
        "905369",  # chlordiazepoxide hydrochloride 10 MG Oral Capsule
        "905495",  # chlordiazepoxide hydrochloride 25 MG Oral Capsule
        "905516",  # chlordiazepoxide hydrochloride 5 MG Oral Capsule
        "998211",  # 2 ML midazolam 1 MG/ML Prefilled Syringe
        "1298088",  # flurazepam hydrochloride 15 MG Oral Capsule
        "1298091",  # flurazepam hydrochloride 30 MG Oral Capsule
        "1551393",  # 2 ML midazolam 5 MG/ML Prefilled Syringe
        "1551395",  # 1 ML midazolam 5 MG/ML Prefilled Syringe
        "1665188",  # 1 ML lorazepam 2 MG/ML Injection
        "1665326",  # 1 ML lorazepam 4 MG/ML Injection
        "1666777",  # 2 ML midazolam 1 MG/ML Cartridge
        "1666798",  # 2 ML midazolam 1 MG/ML Injection
        "1666800",  # 5 ML midazolam 1 MG/ML Injection
        "1666814",  # 1 ML midazolam 5 MG/ML Injection
        "1666821",  # 1 ML midazolam 5 MG/ML Cartridge
        "1666823",  # 2 ML midazolam 5 MG/ML Injection
        "1807452",  # 2 ML diazepam 5 MG/ML Auto-Injector
        "1807459",  # 2 ML diazepam 5 MG/ML Cartridge
        "2120550",  # 2 ML diazepam 5 MG/ML Prefilled Syringe
    }


class Benztropine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for benztropine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable benztropine and benztropine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Benztropine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1361"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "885209",  # benztropine mesylate 2 MG Oral Tablet
        "885213",  # benztropine mesylate 1 MG Oral Tablet
        "885219",  # benztropine mesylate 0.5 MG Oral Tablet
    }


class Brompheniramine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for brompheniramine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable brompheniramine and brompheniramine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Brompheniramine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1427"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "359281",  # 12 HR brompheniramine maleate 6 MG Extended Release Oral Tablet
        "700851",  # brompheniramine maleate 1 MG/ML Oral Solution
        "731032",  # 12 HR brompheniramine maleate 11 MG Extended Release Oral Tablet
        "994289",  # brompheniramine maleate 0.27 MG/ML / codeine phosphate 1.27 MG/ML / pseudoephedrine hydrochloride 2 MG/ML Oral Solution
        "994402",  # brompheniramine maleate 0.4 MG/ML / codeine phosphate 1.5 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "996998",  # brompheniramine maleate 0.266 MG/ML / codeine phosphate 1.27 MG/ML / phenylephrine hydrochloride 0.666 MG/ML Oral Solution
        "1014331",  # brompheniramine maleate 0.4 MG/ML / chlophedianol hydrochloride 2.5 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1053258",  # brompheniramine maleate 0.2 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution
        "1090463",  # brompheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution
        "1098497",  # brompheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1 MG/ML / pseudoephedrine hydrochloride 3 MG/ML Oral Solution
        "1098498",  # brompheniramine maleate 0.2 MG/ML / pseudoephedrine hydrochloride 3 MG/ML Oral Solution
        "1111065",  # brompheniramine maleate 0.8 MG/ML / chlophedianol hydrochloride 5 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "1148155",  # brompheniramine maleate 0.8 MG/ML / dextromethorphan hydrobromide 4 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "1192477",  # brompheniramine maleate 4 MG / pseudoephedrine hydrochloride 60 MG Oral Capsule
        "1244523",  # brompheniramine maleate 1.2 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Suspension
        "1245722",  # brompheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 4 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1251802",  # brompheniramine maleate 1 MG / phenylephrine hydrochloride 2.5 MG Chewable Tablet
        "1304105",  # brompheniramine maleate 4 MG / dextromethorphan hydrobromide 20 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1356797",  # brompheniramine maleate 4 MG / codeine phosphate 10 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1356800",  # brompheniramine maleate 4 MG / codeine phosphate 10 MG Oral Tablet
        "1356804",  # brompheniramine maleate 4 MG / codeine phosphate 20 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1356807",  # brompheniramine maleate 4 MG / codeine phosphate 20 MG Oral Tablet
        "1356812",  # brompheniramine maleate 4 MG / dextromethorphan hydrobromide 20 MG / pseudoephedrine hydrochloride 40 MG Oral Tablet
        "1356815",  # brompheniramine maleate 4 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1356838",  # brompheniramine maleate 0.8 MG/ML / dextromethorphan hydrobromide 4 MG/ML / pseudoephedrine hydrochloride 4 MG/ML Oral Solution
        "1356841",  # brompheniramine maleate 0.8 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "1356848",  # brompheniramine tannate 12 MG Chewable Tablet
        "1357010",  # brompheniramine maleate 0.4 MG/ML / dextromethorphan hydrobromide 2 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1357013",  # brompheniramine maleate 0.4 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "1357883",  # 12 HR brompheniramine maleate 6 MG / phenylephrine hydrochloride 30 MG Extended Release Oral Tablet
        "1367219",  # brompheniramine tannate 2.2 MG / phenylephrine tannate 1.58 MG Chewable Tablet
        "1423702",  # brompheniramine maleate 0.4 MG/ML / dextromethorphan hydrobromide 2 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "1430522",  # 12 HR brompheniramine maleate 6 MG / pseudoephedrine hydrochloride 45 MG Extended Release Oral Tablet
        "1486964",  # brompheniramine maleate 0.8 MG/ML / dextromethorphan hydrobromide 3 MG/ML / phenylephrine hydrochloride 1.5 MG/ML Oral Solution
        "1541630",  # brompheniramine maleate 0.8 MG/ML / codeine phosphate 2 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "1595631",  # acetaminophen 250 MG / brompheniramine maleate 2 MG Oral Tablet
        "1666116",  # {1 (120 ML) (brompheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) / 1 (120 ML) (diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) } Pack
    }


class Butabarbital(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for butabarbital medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable butabarbital and butabarbital in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Butabarbital"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1402"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "1251614",  # butabarbital sodium 30 MG Oral Tablet
    }


class Butalbital(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for butalbital medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable butalbital, and bubtalbital in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Butalbital"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1514"
    DEFINITION_VERSION = "20200310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197426",  # acetaminophen 325 MG / butalbital 50 MG Oral Tablet
        "238134",  # aspirin 325 MG / butalbital 50 MG / caffeine 40 MG Oral Capsule
        "238135",  # aspirin 325 MG / butalbital 50 MG / caffeine 40 MG Oral Tablet
        "238153",  # acetaminophen 325 MG / butalbital 50 MG / caffeine 40 MG Oral Capsule
        "238154",  # acetaminophen 325 MG / butalbital 50 MG / caffeine 40 MG Oral Tablet
        "756245",  # acetaminophen 21.7 MG/ML / butalbital 3.33 MG/ML / caffeine 2.67 MG/ML Oral Solution
        "889520",  # acetaminophen 300 MG / butalbital 50 MG / caffeine 40 MG Oral Capsule
        "993943",  # acetaminophen 325 MG / butalbital 50 MG / caffeine 40 MG / codeine phosphate 30 MG Oral Capsule
        "994237",  # aspirin 325 MG / butalbital 50 MG / caffeine 40 MG / codeine phosphate 30 MG Oral Capsule
        "1249617",  # acetaminophen 300 MG / butalbital 50 MG Oral Tablet
        "1431286",  # acetaminophen 300 MG / butalbital 50 MG / caffeine 40 MG / codeine phosphate 30 MG Oral Capsule
        "1724446",  # acetaminophen 325 MG / butalbital 25 MG Oral Tablet
        "1995136",  # acetaminophen 300 MG / butalbital 50 MG Oral Capsule
    }


class Carbinoxamine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for carbinoxamine.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable carbinoxamine.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients and carbinoxamine in combination with other medications.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Carbinoxamine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1306"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "359329",  # carbetapentane citrate 4 MG/ML / guaifenesin 20 MG/ML Oral Solution
        "1010696",  # carbinoxamine maleate 0.8 MG/ML Oral Solution
        "1012904",  # carbinoxamine maleate 4 MG Oral Tablet
        "1374770",  # 12 HR carbinoxamine maleate 0.8 MG/ML Extended Release Suspension
        "1795581",  # carbinoxamine maleate 6 MG Oral Tablet
    }


class Carisoprodol(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for carisoprodol.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable carisoprodol.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients and carisoprodol in combination with other medications.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Carisoprodol"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1369"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197446",  # carisoprodol 350 MG Oral Tablet
        "197447",  # aspirin 325 MG / carisoprodol 200 MG Oral Tablet
        "730794",  # carisoprodol 250 MG Oral Tablet
        "994226",  # aspirin 325 MG / carisoprodol 200 MG / codeine phosphate 16 MG Oral Tablet
    }


class Chlorpheniramine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for chlorpheniramine.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable chlorpheniramine.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients and chlorpheniramine in combination with other medications.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Chlorpheniramine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1352"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "477045",  # chlorpheniramine maleate 2 MG/ML Oral Solution
        "604664",  # chlorpheniramine maleate 0.4 MG/ML / phenylephrine hydrochloride 1.5 MG/ML / pyrilamine maleate 2.5 MG/ML Oral Solution
        "636568",  # chlorpheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1 MG/ML Oral Solution
        "700949",  # chlorpheniramine maleate 0.6 MG/ML / dextromethorphan hydrobromide 2.75 MG/ML / phenylephrine hydrochloride 1.5 MG/ML Oral Solution
        "857510",  # 12 HR chlorpheniramine polistirex 4 MG / hydrocodone polistirex 5 MG Extended Release Oral Capsule
        "857512",  # 12 HR chlorpheniramine polistirex 8 MG / hydrocodone polistirex 10 MG Extended Release Oral Capsule
        "995041",  # chlorpheniramine maleate 0.2 MG/ML / codeine phosphate 1 MG/ML / pseudoephedrine hydrochloride 3 MG/ML Oral Suspension
        "995065",  # chlorpheniramine maleate 0.222 MG/ML / codeine phosphate 1 MG/ML / pseudoephedrine hydrochloride 3.33 MG/ML Oral Suspension
        "995068",  # chlorpheniramine maleate 0.222 MG/ML / codeine phosphate 1 MG/ML Oral Suspension
        "995071",  # chlorpheniramine maleate 0.25 MG/ML / codeine phosphate 1 MG/ML Oral Suspension
        "995075",  # chlorpheniramine maleate 0.25 MG/ML / codeine phosphate 1 MG/ML / pseudoephedrine hydrochloride 0.375 MG/ML Oral Suspension
        "995079",  # chlorpheniramine maleate 0.266 MG/ML / codeine phosphate 1 MG/ML / pseudoephedrine hydrochloride 4 MG/ML Oral Suspension
        "995082",  # chlorpheniramine maleate 0.267 MG/ML / codeine phosphate 1 MG/ML Oral Suspension
        "995086",  # chlorpheniramine maleate 0.286 MG/ML / codeine phosphate 1 MG/ML / pseudoephedrine hydrochloride 4.29 MG/ML Oral Suspension
        "995093",  # chlorpheniramine maleate 0.286 MG/ML / codeine phosphate 1 MG/ML Oral Suspension
        "995108",  # chlorpheniramine maleate 0.333 MG/ML / codeine phosphate 1 MG/ML / pseudoephedrine hydrochloride 5 MG/ML Oral Suspension
        "995116",  # chlorpheniramine maleate 0.333 MG/ML / codeine phosphate 1 MG/ML Oral Suspension
        "995120",  # chlorpheniramine maleate 0.4 MG/ML / codeine phosphate 1 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Suspension
        "995123",  # chlorpheniramine maleate 0.4 MG/ML / codeine phosphate 1 MG/ML Oral Suspension
        "995128",  # chlorpheniramine maleate 0.4 MG/ML / codeine phosphate 1.8 MG/ML Oral Solution
        "998254",  # chlorpheniramine maleate 4 MG / pseudoephedrine hydrochloride 60 MG Oral Tablet
        "1013619",  # chlorpheniramine maleate 3 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1042688",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Capsule
        "1042693",  # chlorpheniramine maleate 0.4 MG/ML / codeine phosphate 2 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "1046384",  # acetaminophen 21.7 MG/ML / chlorpheniramine maleate 0.133 MG/ML / dextromethorphan hydrobromide 1 MG/ML Oral Solution
        "1046781",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG / phenylephrine hydrochloride 5 MG Oral Tablet
        "1046799",  # {12 (acetaminophen 325 MG / chlorpheniramine maleate 2 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 12 (acetaminophen 325 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1048124",  # 12 HR atropine sulfate 0.04 MG / chlorpheniramine maleate 8 MG / hyoscyamine sulfate 0.19 MG / pseudoephedrine hydrochloride 90 MG / scopolamine hydrobromide 0.01 MG Extended Release Oral Tablet
        "1052679",  # acetaminophen 500 MG / chlorpheniramine maleate 2 MG / phenylephrine hydrochloride 5 MG Oral Tablet
        "1053618",  # chlorpheniramine maleate 0.4 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1053624",  # chlorpheniramine maleate 1 MG / pseudoephedrine hydrochloride 15 MG Chewable Tablet
        "1086443",  # chlorpheniramine maleate 0.8 MG/ML / dextromethorphan hydrobromide 3 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "1086463",  # chlorpheniramine maleate 0.8 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "1086750",  # acetaminophen 32 MG/ML / chlorpheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1 MG/ML Oral Suspension
        "1086991",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Tablet
        "1087459",  # 12 HR chlorpheniramine polistirex 1.6 MG/ML / hydrocodone polistirex 2 MG/ML Extended Release Suspension
        "1089968",  # acetaminophen 500 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 15 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet
        "1090443",  # chlorpheniramine maleate 4 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1090699",  # chlorpheniramine maleate 2 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet
        "1098496",  # acetaminophen 500 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 15 MG Oral Tablet
        "1101555",  # {12 (acetaminophen 500 MG / chlorpheniramine maleate 2 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 16 (acetaminophen 500 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1111171",  # 12 HR belladonna alkaloids 0.24 MG / chlorpheniramine maleate 8 MG / pseudoephedrine hydrochloride 90 MG Extended Release Oral Tablet
        "1111440",  # chlorpheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1.5 MG/ML Oral Solution
        "1112220",  # chlorpheniramine maleate 0.8 MG/ML / hydrocodone bitartrate 1 MG/ML / pseudoephedrine hydrochloride 12 MG/ML Oral Solution
        "1112489",  # chlorpheniramine maleate 1 MG/ML / phenylephrine hydrochloride 2.5 MG/ML Oral Solution
        "1112864",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG Oral Tablet
        "1112906",  # {10 (acetaminophen 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 10 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1112908",  # {12 (acetaminophen 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 12 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1113397",  # acetaminophen 32 MG/ML / chlorpheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Suspension
        "1113522",  # acetaminophen 32 MG/ML / chlorpheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1.5 MG/ML Oral Solution
        "1113998",  # chlorpheniramine maleate 0.4 MG/ML / codeine phosphate 1.6 MG/ML Oral Solution
        "1114361",  # chlorpheniramine maleate 0.133 MG/ML / dextromethorphan hydrobromide 1 MG/ML Oral Solution
        "1114838",  # chlorpheniramine maleate 2 MG/ML / phenylephrine hydrochloride 5 MG/ML Oral Solution
        "1116173",  # carbetapentane tannate 60 MG / chlorpheniramine tannate 5 MG / ephedrine tannate 10 MG / phenylephrine tannate 10 MG Oral Tablet
        "1117392",  # chlorpheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1 MG/ML / pseudoephedrine hydrochloride 3 MG/ML Oral Solution
        "1147795",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet
        "1190174",  # chlorpheniramine maleate 0.4 MG/ML / dextromethorphan hydrobromide 3 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "1193293",  # acetaminophen 325 MG / chlorpheniramine maleate 4 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1234941",  # chlorpheniramine maleate 0.4 MG/ML / dihydrocodeine bitartrate 0.6 MG/ML / phenylephrine hydrochloride 1.5 MG/ML Oral Solution
        "1242240",  # chlorpheniramine maleate 2 MG / phenylephrine hydrochloride 5 MG Oral Tablet
        "1244951",  # {10 (acetaminophen 325 MG / chlorpheniramine maleate 2 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 10 (acetaminophen 325 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1245291",  # chlorpheniramine maleate 1 MG / dextromethorphan hydrobromide 5 MG / pseudoephedrine hydrochloride 15 MG Chewable Tablet
        "1245706",  # chlophedianol hydrochloride 4.8 MG/ML / chlorpheniramine maleate 0.8 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Suspension
        "1250983",  # {8 (acetaminophen 500 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 15 MG Oral Tablet) / 16 (dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG Oral Capsule) } Pack
        "1251811",  # chlorpheniramine maleate 1 MG / dextromethorphan hydrobromide 5 MG Chewable Tablet
        "1251928",  # acetaminophen 500 MG / chlorpheniramine maleate 2 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet
        "1292342",  # acetaminophen 43.3 MG/ML / chlorpheniramine maleate 0.267 MG/ML / dextromethorphan hydrobromide 2 MG/ML Oral Solution
        "1293344",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet
        "1294201",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG / pseudoephedrine hydrochloride 30 MG Oral Capsule
        "1297390",  # chlorpheniramine maleate 2 MG / ibuprofen 200 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet
        "1299646",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 15 MG / pseudoephedrine hydrochloride 30 MG Oral Capsule
        "1299662",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / pseudoephedrine hydrochloride 30 MG Oral Capsule
        "1310503",  # chlorpheniramine maleate 4 MG / ibuprofen 200 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1313969",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG / phenylephrine hydrochloride 5 MG Oral Capsule
        "1357553",  # acetaminophen 32 MG/ML / chlorpheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution
        "1357894",  # 12 HR chlorpheniramine maleate 8 MG / dextromethorphan hydrobromide 30 MG / phenylephrine hydrochloride 20 MG Extended Release Oral Tablet
        "1359114",  # chlorpheniramine maleate 4 MG / dextromethorphan hydrobromide 20 MG / pseudoephedrine hydrochloride 60 MG Oral Tablet
        "1363288",  # 12 HR chlorpheniramine maleate 12 MG Extended Release Oral Tablet
        "1363306",  # chlorpheniramine maleate 0.4 MG/ML Oral Solution
        "1363309",  # chlorpheniramine maleate 4 MG Oral Tablet
        "1363752",  # chlorpheniramine maleate 0.4 MG/ML / dextromethorphan hydrobromide 2 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "1363780",  # 12 HR chlorpheniramine maleate 12 MG / pseudoephedrine hydrochloride 120 MG Extended Release Oral Tablet
        "1366022",  # {8 (acetaminophen 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 12 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1366653",  # {8 (acetaminophen 325 MG / chlorpheniramine maleate 2 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 12 (acetaminophen 325 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1366825",  # acetaminophen 80 MG / chlorpheniramine maleate 0.5 MG / dextromethorphan hydrobromide 2.5 MG / pseudoephedrine hydrochloride 7.5 MG Chewable Tablet
        "1366948",  # chlorpheniramine tannate 8 MG / phenylephrine tannate 25 MG Oral Tablet
        "1367225",  # chlorpheniramine maleate 2 MG / guaifenesin 100 MG / phenylephrine hydrochloride 5 MG Oral Tablet
        "1367227",  # chlorpheniramine maleate 3.5 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1368963",  # chlophedianol hydrochloride 25 MG / chlorpheniramine maleate 4 MG / phenylephrine hydrochloride 15 MG Oral Tablet
        "1370125",  # chlorpheniramine maleate 0.4 MG/ML / dextromethorphan hydrobromide 3 MG/ML Oral Solution
        "1372265",  # chlorpheniramine maleate 0.8 MG/ML / hydrocodone bitartrate 1 MG/ML Oral Solution
        "1372312",  # acetaminophen 32 MG/ML / chlorpheniramine maleate 0.2 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Suspension
        "1421985",  # chlorpheniramine maleate 4 MG / dextromethorphan hydrobromide 30 MG Oral Tablet
        "1423711",  # chlorpheniramine maleate 0.4 MG/ML / dextromethorphan hydrobromide 2 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1424872",  # chlophedianol hydrochloride 24 MG / chlorpheniramine maleate 3.5 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1429345",  # chlorpheniramine maleate 0.2 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution
        "1489310",  # chlorpheniramine maleate 0.8 MG/ML / dextromethorphan hydrobromide 4 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "1535923",  # chlorpheniramine maleate 1 MG/ML / dextromethorphan hydrobromide 3 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "1536477",  # acetaminophen 250 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Effervescent Oral Tablet
        "1536840",  # aspirin 325 MG / chlorpheniramine maleate 2 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet
        "1536862",  # chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Effervescent Oral Tablet
        "1536931",  # acetaminophen 250 MG / chlorpheniramine maleate 2 MG / phenylephrine hydrochloride 5 MG Effervescent Oral Tablet
        "1537029",  # aspirin 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet
        "1593105",  # chlorpheniramine maleate 4 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1652087",  # 12 HR chlorpheniramine polistirex 0.8 MG/ML / codeine polistirex 4 MG/ML Extended Release Suspension
        "1664543",  # 12 HR chlorpheniramine maleate 8 MG / codeine phosphate 54.3 MG Extended Release Oral Tablet
        "1741529",  # acetaminophen 650 MG / chlorpheniramine maleate 4 MG / phenylephrine hydrochloride 10 MG Oral Powder
        "1800670",  # {48 (acetaminophen 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 120 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1801964",  # {8 (acetaminophen 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 16 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1876117",  # chlorpheniramine maleate 0.4 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "2003130",  # chlorpheniramine maleate 4 MG / dextromethorphan hydrobromide 18 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "2003179",  # chlorpheniramine maleate 0.8 MG/ML / dextromethorphan hydrobromide 3.6 MG/ML Oral Solution
        "2049841",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG Oral Tablet
        "2056893",  # chlorpheniramine maleate 0.8 MG/ML / codeine phosphate 2 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "2121065",  # acetaminophen 65 MG/ML / chlorpheniramine maleate 0.4 MG/ML / dextromethorphan hydrobromide 1.3 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "2167740",  # chlorpheniramine maleate 0.133 MG/ML / dextromethorphan hydrobromide 0.333 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution
        "2181307",  # acetaminophen 325 MG / caffeine 45 MG / chlorpheniramine maleate 2 MG / phenylephrine hydrochloride 5 MG Oral Tablet
        "2183687",  # chlorpheniramine tannate 1.6 MG/ML Extended Release Suspension
        "2183697",  # chlorpheniramine maleate 2 MG Chewable Tablet
        "2183701",  # chlorpheniramine maleate 8 MG Extended Release Oral Capsule
        "2383312",  # {56 (acetaminophen 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 112 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
    }


class Chlorpropamide(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for chlorpropamide medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable chlorpropamide and chlorpropamide in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Chlorpropamide"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1303"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197495",  # chlorpropamide 100 MG Oral Tablet
        "197496",  # chlorpropamide 250 MG Oral Tablet
    }


class Chlorzoxazone(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for chlorzoxazone medicaitons.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable chlorzoxazone and chlorzoxazone in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Chlorzoxazone"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1362"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197501",  # chlorzoxazone 250 MG Oral Tablet
        "197502",  # chlorzoxazone 500 MG Oral Tablet
        "1088934",  # chlorzoxazone 375 MG Oral Tablet
        "1088936",  # chlorzoxazone 750 MG Oral Tablet
    }


class Clemastine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for clemastine.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable clemastine.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients and clemastine in combination with other medications.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Clemastine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1308"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "857416",  # clemastine fumarate 1.34 MG Oral Tablet
        "857420",  # 12 HR clemastine fumarate 1.34 MG Extended Release Oral Tablet
        "857430",  # clemastine fumarate 0.134 MG/ML Oral Solution
        "857461",  # clemastine fumarate 2.68 MG Oral Tablet
    }


class Clomipramine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for clomipramine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable clomipramine and clomipramine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Clomipramine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1336"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "857297",  # clomipramine hydrochloride 25 MG Oral Capsule
        "857301",  # clomipramine hydrochloride 50 MG Oral Capsule
        "857305",  # clomipramine hydrochloride 75 MG Oral Capsule
    }


class ConjugatedEstrogens(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for conjugated estrogens.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable conjugated estrogens and conjugated estrogens in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Conjugated Estrogens"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1357"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197660",  # estrogens, conjugated (USP) 0.3 MG Oral Tablet
        "197661",  # estrogens, conjugated (USP) 0.9 MG Oral Tablet
        "197662",  # estrogens, conjugated (USP) 1.25 MG Oral Tablet
        "310197",  # estrogens, conjugated (USP) 0.625 MG Oral Tablet
        "403849",  # estrogens, conjugated (USP) 0.45 MG Oral Tablet
        "1000351",  # estrogens, conjugated (USP) 0.3 MG / medroxyprogesterone acetate 1.5 MG Oral Tablet
        "1000352",  # estrogens, conjugated (USP) 0.45 MG / medroxyprogesterone acetate 1.5 MG Oral Tablet
        "1000355",  # estrogens, conjugated (USP) 0.625 MG / medroxyprogesterone acetate 2.5 MG Oral Tablet
        "1000356",  # estrogens, conjugated (USP) 0.625 MG / medroxyprogesterone acetate 5 MG Oral Tablet
        "1000395",  # {28 (estrogens, conjugated (USP) 0.625 MG / medroxyprogesterone acetate 2.5 MG Oral Tablet) } Pack
        "1000398",  # {28 (estrogens, conjugated (USP) 0.625 MG / medroxyprogesterone acetate 5 MG Oral Tablet) } Pack
        "1000486",  # {14 (estrogens, conjugated (USP) 0.625 MG / medroxyprogesterone acetate 5 MG Oral Tablet) / 14 (estrogens, conjugated (USP) 0.625 MG Oral Tablet) } Pack
        "1000490",  # {28 (estrogens, conjugated (USP) 0.3 MG / medroxyprogesterone acetate 1.5 MG Oral Tablet) } Pack
        "1000496",  # {28 (estrogens, conjugated (USP) 0.45 MG / medroxyprogesterone acetate 1.5 MG Oral Tablet) } Pack
        "1441392",  # bazedoxifene 20 MG / estrogens, conjugated (USP) 0.45 MG Oral Tablet
    }


class CyclobenzaprineHydrochloride(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for cyclobenzaprine hydrochloride medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable cyclobenzaprine hydrochloride and cyclobenzaprine hydrochloride in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Cyclobenzaprine Hydrochloride"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1372"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "828299",  # cyclobenzaprine hydrochloride 7.5 MG Oral Tablet
        "828320",  # cyclobenzaprine hydrochloride 5 MG Oral Tablet
        "828348",  # cyclobenzaprine hydrochloride 10 MG Oral Tablet
        "828353",  # 24 HR cyclobenzaprine hydrochloride 30 MG Extended Release Oral Capsule
        "828358",  # 24 HR cyclobenzaprine hydrochloride 15 MG Extended Release Oral Capsule
    }


class Cyproheptadine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for cyproheptadine medications..

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable cyproheptadine and cyproheptadine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Cyproheptadine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1277"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "866021",  # cyproheptadine hydrochloride 0.4 MG/ML Oral Solution
        "866144",  # cyproheptadine hydrochloride 4 MG Oral Tablet
    }


class DesiccatedThyroid(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for desiccated thyroid medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable desiccated thyroid and desiccated thyroid in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Desiccated Thyroid"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1354"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "198277",  # thyroid (USP) 130 MG Oral Tablet
        "198278",  # thyroid (USP) 180 MG Oral Tablet
        "208545",  # thyroid (USP) 120 MG Oral Tablet
        "313385",  # thyroid (USP) 240 MG Oral Tablet
        "313386",  # thyroid (USP) 260 MG Oral Tablet
        "313387",  # thyroid (USP) 30 MG Oral Tablet
        "313389",  # thyroid (USP) 325 MG Oral Tablet
        "313391",  # thyroid (USP) 60 MG Oral Tablet
        "313393",  # thyroid (USP) 90 MG Oral Tablet
        "313396",  # thyroid (USP) 65 MG Oral Tablet
        "314267",  # thyroid (USP) 15 MG Oral Tablet
        "315234",  # thyroid (USP) 195 MG Oral Tablet
        "315235",  # thyroid (USP) 300 MG Oral Tablet
        "347151",  # thyroid (USP) 32.5 MG Oral Tablet
        "728581",  # thyroid (USP) 16.25 MG Oral Tablet
        "1041814",  # thyroid (USP) 97.5 MG Oral Tablet
        "1099948",  # thyroid (USP) 48.75 MG Oral Tablet
        "1537767",  # thyroid (USP) 162.5 MG Oral Tablet
        "1537803",  # thyroid (USP) 113.75 MG Oral Tablet
        "1537807",  # thyroid (USP) 146.25 MG Oral Tablet
        "1537811",  # thyroid (USP) 81.25 MG Oral Tablet
    }


class Desipramine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for desipramine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable desipramine and desipramine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Desipramine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1278"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "1099288",  # desipramine hydrochloride 10 MG Oral Tablet
        "1099292",  # desipramine hydrochloride 100 MG Oral Tablet
        "1099296",  # desipramine hydrochloride 150 MG Oral Tablet
        "1099300",  # desipramine hydrochloride 25 MG Oral Tablet
        "1099304",  # desipramine hydrochloride 50 MG Oral Tablet
        "1099316",  # desipramine hydrochloride 75 MG Oral Tablet
    }


class Dexbrompheniramine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for dexbrompheniramine.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable dexbrompheniramine.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients and dexbrompheniramine in combination with other medications.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Dexbrompheniramine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1375"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "1190580",  # codeine phosphate 1.2 MG/ML / dexbrompheniramine maleate 0.133 MG/ML / pseudoephedrine hydrochloride 4 MG/ML Oral Solution
        "1190600",  # dexbrompheniramine maleate 0.133 MG/ML / dextromethorphan hydrobromide 2 MG/ML / pseudoephedrine hydrochloride 4 MG/ML Oral Solution
        "1369403",  # chlophedianol hydrochloride 2.5 MG/ML / dexbrompheniramine maleate 0.2 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "1441376",  # chlophedianol hydrochloride 2.5 MG/ML / dexbrompheniramine maleate 0.2 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1491637",  # dexbrompheniramine maleate 1 MG / phenylephrine hydrochloride 5 MG Oral Tablet
        "1539185",  # dexbrompheniramine maleate 0.2 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "1545306",  # dexbrompheniramine maleate 1 MG Chewable Tablet
        "1545309",  # dexbrompheniramine maleate 0.4 MG/ML Oral Solution
        "1551286",  # chlophedianol hydrochloride 2.5 MG/ML / dexbrompheniramine maleate 0.2 MG/ML Oral Solution
        "1798453",  # acetaminophen 500 MG / dexbrompheniramine maleate 1 MG Oral Tablet
        "2391334",  # dexbrompheniramine maleate 2 MG / phenylephrine hydrochloride 7.5 MG Oral Tablet
    }


class Dexchlorpheniramine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for dexchlorpheniramine.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable dexchlorpheniramine and dexchlorpheniramine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Dexchlorpheniramine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1300"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "1293239",  # dexchlorpheniramine maleate 2 MG / pseudoephedrine hydrochloride 60 MG Oral Tablet
        "1298226",  # dexchlorpheniramine maleate 0.2 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1298433",  # dexchlorpheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 3 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1369424",  # chlophedianol hydrochloride 2.5 MG/ML / dexchlorpheniramine maleate 0.2 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1369971",  # chlophedianol hydrochloride 6.25 MG/ML / dexchlorpheniramine maleate 0.5 MG/ML / pseudoephedrine hydrochloride 15 MG/ML Oral Solution
        "1369972",  # chlophedianol hydrochloride 5 MG/ML / dexchlorpheniramine maleate 0.4 MG/ML / pseudoephedrine hydrochloride 12 MG/ML Oral Solution
        "1440003",  # codeine phosphate 1.8 MG/ML / dexchlorpheniramine maleate 0.2 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "1990881",  # dexchlorpheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 2 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "2181304",  # 12 HR dexchlorpheniramine maleate 6 MG / phenylephrine hydrochloride 40 MG Extended Release Oral Tablet
        "2183907",  # dexchlorpheniramine maleate 0.4 MG/ML Oral Solution
        "2184108",  # dexchlorpheniramine maleate 2 MG / phenylephrine hydrochloride 10 MG Oral Tablet
    }


class Dicyclomine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for dicyclomine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use,  prescribable dicyclomine and dicyclomine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Dicyclomine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1279"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "991061",  # dicyclomine hydrochloride 10 MG Oral Capsule
        "991065",  # 2 ML dicyclomine hydrochloride 10 MG/ML Injection
        "991082",  # dicyclomine hydrochloride 2 MG/ML Oral Solution
        "991086",  # dicyclomine hydrochloride 20 MG Oral Tablet
    }


class Dimenhydrinate(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for dimenhydrinate medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable dimenhydrinate and dimenhydrinate in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Dimenhydrinate"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1500"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "198602",  # dimenhydrinate 25 MG Oral Tablet
        "198603",  # dimenhydrinate 50 MG Oral Tablet
        "309913",  # dimenhydrinate 50 MG Chewable Tablet
        "309914",  # dimenhydrinate 50 MG/ML Injectable Solution
        "1245184",  # dimenhydrinate 25 MG Chewable Tablet
    }


class Diphenhydramine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for diphenhydramine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable diphenhydramine, and diphenhydramine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Diphenhydramine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1293"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "882504",  # diphenhydramine hydrochloride 12.5 MG Disintegrating Oral Tablet
        "895664",  # diphenhydramine citrate 38 MG / ibuprofen 200 MG Oral Tablet
        "901814",  # diphenhydramine hydrochloride 25 MG / ibuprofen 200 MG Oral Capsule
        "1020477",  # diphenhydramine hydrochloride 50 MG Oral Capsule
        "1046751",  # acetaminophen 325 MG / diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 5 MG Oral Tablet
        "1049630",  # diphenhydramine hydrochloride 25 MG Oral Tablet
        "1049900",  # diphenhydramine hydrochloride 12.5 MG Chewable Tablet
        "1049906",  # diphenhydramine hydrochloride 2.5 MG/ML Oral Solution
        "1049909",  # diphenhydramine hydrochloride 25 MG Oral Capsule
        "1050385",  # acetaminophen 32 MG/ML / diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution
        "1052462",  # acetaminophen 325 MG / diphenhydramine hydrochloride 12.5 MG Oral Tablet
        "1052467",  # acetaminophen 500 MG / diphenhydramine hydrochloride 12.5 MG Oral Tablet
        "1052928",  # diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1085945",  # diphenhydramine hydrochloride 50 MG Oral Tablet
        "1086720",  # diphenhydramine hydrochloride 2.5 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "1087607",  # acetaminophen 500 MG / diphenhydramine hydrochloride 50 MG Oral Tablet
        "1092189",  # acetaminophen 500 MG / diphenhydramine hydrochloride 25 MG Oral Tablet
        "1092373",  # acetaminophen 33.3 MG/ML / diphenhydramine hydrochloride 1.67 MG/ML Oral Solution
        "1092398",  # aspirin 500 MG / diphenhydramine hydrochloride 25 MG Oral Tablet
        "1093098",  # diphenhydramine hydrochloride 25 MG Disintegrating Oral Tablet
        "1094131",  # acetaminophen 65 MG/ML / dextromethorphan hydrobromide 2 MG/ML / diphenhydramine hydrochloride 2.5 MG/ML Oral Solution
        "1098443",  # {10 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / guaifenesin 100 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 10 (acetaminophen 325 MG / diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1099872",  # acetaminophen 500 MG / diphenhydramine citrate 38 MG Oral Tablet
        "1117245",  # acetaminophen 500 MG / diphenhydramine hydrochloride 25 MG Oral Capsule
        "1190448",  # 12 HR diphenhydramine hydrochloride 100 MG / pseudoephedrine hydrochloride 120 MG Extended Release Oral Tablet
        "1233575",  # acetaminophen 325 MG / diphenhydramine hydrochloride 12.5 MG / phenylephrine hydrochloride 5 MG Oral Tablet
        "1236048",  # diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution
        "1248354",  # diphenhydramine hydrochloride 1.67 MG/ML Oral Solution
        "1250907",  # aspirin 500 MG / diphenhydramine citrate 38.3 MG Oral Tablet
        "1294348",  # diphenhydramine hydrochloride 12.5 MG / phenylephrine hydrochloride 5 MG Chewable Tablet
        "1294567",  # acetaminophen 500 MG / diphenhydramine hydrochloride 12.5 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet
        "1297517",  # diphenhydramine hydrochloride 25 MG / magnesium salicylate 580 MG Oral Tablet
        "1297947",  # acetaminophen 500 MG / diphenhydramine citrate 38 MG Oral Powder
        "1298348",  # acetaminophen 21.7 MG/ML / diphenhydramine hydrochloride 0.833 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution
        "1356113",  # {10 (acetaminophen 325 MG / diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 10 (acetaminophen 325 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1375932",  # acetaminophen 32.5 MG/ML / diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution
        "1424551",  # {20 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 10 (acetaminophen 325 MG / diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1424850",  # {1 (180 ML) (acetaminophen 32.5 MG/ML / dextromethorphan hydrobromide 1 MG/ML / guaifenesin 20 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) / 1 (180 ML) (acetaminophen 32.5 MG/ML / diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) } Pack
        "1428880",  # {6 (acetaminophen 650 MG / dextromethorphan hydrobromide 20 MG / phenylephrine hydrochloride 10 MG Granules for Oral Solution) / 6 (acetaminophen 650 MG / diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 10 MG Granules for Oral Solution) } Pack
        "1535609",  # {10 (acetaminophen 325 MG / diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 20 (dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1537095",  # {1 (180 ML) (acetaminophen 32.5 MG/ML / diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) / 1 (180 ML) (acetaminophen 32.5 MG/ML / guaifenesin 20 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) } Pack
        "1550957",  # diphenhydramine hydrochloride 25 MG / naproxen sodium 220 MG Oral Tablet
        "1593110",  # acetaminophen 250 MG / aspirin 250 MG / diphenhydramine citrate 38 MG Oral Tablet
        "1606291",  # {1 (118 ML) (acetaminophen 32.5 MG/ML / diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) / 1 (118 ML) (dextromethorphan hydrobromide 1 MG/ML / guaifenesin 20 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) } Pack
        "1659175",  # acetaminophen 500 MG / diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 10 MG Powder for Oral Solution
        "1659960",  # acetaminophen 650 MG / diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 10 MG Granules for Oral Solution
        "1666116",  # {1 (120 ML) (brompheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) / 1 (120 ML) (diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) } Pack
        "1727571",  # {10 (acetaminophen 325 MG / diphenhydramine hydrochloride 12.5 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 20 (dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1730190",  # {1 (118 ML) (dextromethorphan hydrobromide 1 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) / 1 (118 ML) (diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) } Pack
        "1730192",  # {1 (180 ML) (acetaminophen 32.5 MG/ML / diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) / 1 (180 ML) (dextromethorphan hydrobromide 1 MG/ML / guaifenesin 20 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) } Pack
        "1789740",  # diphenhydramine hydrochloride 6.25 MG/ML Oral Solution
        "1799180",  # {20 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 20 (acetaminophen 325 MG / diphenhydramine hydrochloride 12.5 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1803669",  # {1 (245 ML) (acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 0.667 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution) / 1 (245 ML) (acetaminophen 21.7 MG/ML / diphenhydramine hydrochloride 0.833 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution) } Pack
        "1804449",  # {6 (acetaminophen 500 MG / dextromethorphan hydrobromide 20 MG / phenylephrine hydrochloride 10 MG Granules for Oral Solution) / 6 (acetaminophen 650 MG / diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 10 MG Granules for Oral Solution) } Pack
        "1855193",  # {12 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / guaifenesin 100 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 12 (acetaminophen 325 MG / diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1926601",  # {8 (diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 10 MG Oral Tablet) / 12 (phenylephrine hydrochloride 10 MG Oral Tablet) } Pack
        "1939343",  # {8 (acetaminophen 325 MG / diphenhydramine hydrochloride 12.5 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 12 (acetaminophen 325 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1944254",  # {20 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 10 (acetaminophen 325 MG / diphenhydramine hydrochloride 12.5 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1993219",  # {118 (acetaminophen 32.5 MG/ML / diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) / 118 (dextromethorphan hydrobromide 1 MG/ML / guaifenesin 20 MG/ML Oral Solution) } Pack
        "1993220",  # {1 (180 ML) (acetaminophen 32.5 MG/ML / diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) / 1 (180 ML) (dextromethorphan hydrobromide 1 MG/ML / guaifenesin 20 MG/ML Oral Solution) } Pack
        "1996098",  # acetaminophen 32.5 MG/ML / dextromethorphan hydrobromide 1 MG/ML / diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution
    }


class Dipyridamole(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for dipyridamole medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable dipyridamole and dipyridamole in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Dipyridamole"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1349"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197622",  # dipyridamole 50 MG Oral Tablet
        "309952",  # dipyridamole 25 MG Oral Tablet
        "309955",  # dipyridamole 75 MG Oral Tablet
    }


class Disopyramide(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for disopyramide medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable disopyramide and disopyramide in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Disopyramide"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1311"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "309958",  # disopyramide 100 MG Oral Capsule
        "309960",  # disopyramide 150 MG Oral Capsule
        "636793",  # 12 HR disopyramide 100 MG Extended Release Oral Capsule
        "636794",  # 12 HR disopyramide 150 MG Extended Release Oral Capsule
    }


class Doxylamine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for doxylamine.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable doxylamine.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients and doxylamine in combination with other medications.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Doxylamine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1515"
    DEFINITION_VERSION = "20200310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "1042684",  # acetaminophen 33.3 MG/ML / dextromethorphan hydrobromide 1 MG/ML / doxylamine succinate 0.417 MG/ML Oral Solution
        "1043400",  # acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 1 MG/ML / doxylamine succinate 0.417 MG/ML Oral Solution
        "1052647",  # acetaminophen 325 MG / doxylamine succinate 6.25 MG / phenylephrine hydrochloride 5 MG Oral Capsule
        "1089822",  # acetaminophen 325 MG / dextromethorphan hydrobromide 15 MG / doxylamine succinate 6.25 MG / pseudoephedrine hydrochloride 30 MG Oral Capsule
        "1094350",  # dextromethorphan hydrobromide 3 MG/ML / doxylamine succinate 1.25 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1094355",  # doxylamine succinate 1.25 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1094549",  # acetaminophen 325 MG / dextromethorphan hydrobromide 15 MG / doxylamine succinate 6.25 MG Oral Capsule
        "1101439",  # doxylamine succinate 5 MG Chewable Tablet
        "1101446",  # doxylamine succinate 25 MG Oral Tablet
        "1101457",  # doxylamine succinate 1 MG/ML Oral Solution
        "1115329",  # dextromethorphan hydrobromide 1.5 MG/ML / doxylamine succinate 0.625 MG/ML Oral Solution
        "1233546",  # {20 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Capsule) / 20 (acetaminophen 325 MG / dextromethorphan hydrobromide 15 MG / doxylamine succinate 6.25 MG Oral Capsule) } Pack
        "1234386",  # dextromethorphan hydrobromide 1 MG/ML / doxylamine succinate 0.417 MG/ML Oral Solution
        "1237110",  # acetaminophen 33.3 MG/ML / dextromethorphan hydrobromide 1 MG/ML / doxylamine succinate 0.417 MG/ML / pseudoephedrine hydrochloride 2 MG/ML Oral Solution
        "1242618",  # acetaminophen 250 MG / doxylamine succinate 25 MG / salicylamide 150 MG Oral Tablet
        "1245233",  # {20 (acetaminophen 325 MG / doxylamine succinate 6.25 MG / phenylephrine hydrochloride 5 MG Oral Capsule) / 20 (acetaminophen 325 MG / phenylephrine hydrochloride 5 MG Oral Capsule) } Pack
        "1297288",  # acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine hydrochloride 5 MG Oral Capsule
        "1297404",  # {8 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine hydrochloride 5 MG Oral Capsule) / 12 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Capsule) } Pack
        "1311150",  # {32 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Capsule) / 16 (acetaminophen 325 MG / dextromethorphan hydrobromide 15 MG / doxylamine succinate 6.25 MG Oral Capsule) } Pack
        "1360638",  # {1 (355 ML) (dextromethorphan hydrobromide 1 MG/ML / doxylamine succinate 0.417 MG/ML Oral Solution) / 1 (355 ML) (dextromethorphan hydrobromide 1 MG/ML Oral Solution) } Pack
        "1366502",  # {16 (acetaminophen 325 MG / doxylamine succinate 6.25 MG / phenylephrine hydrochloride 5 MG Oral Capsule) / 32 (acetaminophen 325 MG / phenylephrine hydrochloride 5 MG Oral Capsule) } Pack
        "1371196",  # dextromethorphan hydrobromide 3 MG/ML / doxylamine succinate 1.25 MG/ML Oral Solution
        "1375948",  # doxylamine succinate 10 MG / pyridoxine hydrochloride 10 MG Delayed Release Oral Tablet
        "1431245",  # acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 0.667 MG/ML / doxylamine succinate 0.417 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution
        "1441831",  # doxylamine succinate 7.5 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1484901",  # {1 (355 ML) (acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 0.667 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution) / 1 (355 ML) (acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 1 MG/ML / doxylamine succinate 0.417 MG/ML Oral Solution) } Pack
        "1492380",  # {16 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Capsule) / 8 (acetaminophen 325 MG / dextromethorphan hydrobromide 15 MG / doxylamine succinate 6.25 MG Oral Capsule) } Pack
        "1534835",  # acetaminophen 650 MG / dextromethorphan hydrobromide 20 MG / doxylamine succinate 12.5 MG / phenylephrine hydrochloride 10 MG Powder for Oral Solution
        "1536503",  # aspirin 500 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet
        "1536999",  # acetaminophen 250 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine hydrochloride 5 MG Effervescent Oral Tablet
        "1544175",  # {1 (355 ML) (acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 0.667 MG/ML / doxylamine succinate 0.417 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution) / 1 (355 ML) (acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 0.667 MG/ML / guaifenesin 13.3 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution) } Pack
        "1546881",  # acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine hydrochloride 5 MG Oral Tablet
        "1657147",  # {8 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine hydrochloride 5 MG Oral Capsule) / 16 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Capsule) } Pack
        "1730187",  # {12 (aspirin 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet) / 8 (aspirin 500 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet) } Pack
        "1730211",  # {8 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 16 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1730213",  # {8 (acetaminophen 325 MG / doxylamine succinate 6.25 MG / phenylephrine hydrochloride 5 MG Oral Capsule) / 16 (acetaminophen 325 MG / phenylephrine hydrochloride 5 MG Oral Capsule) } Pack
        "1795585",  # {1 (118 ML) (dextromethorphan hydrobromide 2 MG/ML / guaifenesin 40 MG/ML Oral Solution) / 1 (118 ML) (dextromethorphan hydrobromide 3 MG/ML / doxylamine succinate 1.25 MG/ML Oral Solution) } Pack
        "1804384",  # {6 (acetaminophen 500 MG / dextromethorphan hydrobromide 20 MG / guaifenesin 400 MG / phenylephrine hydrochloride 10 MG Powder for Oral Solution) / 6 (acetaminophen 650 MG / dextromethorphan hydrobromide 20 MG / doxylamine succinate 12.5 MG / phenylephrine hydrochloride 10 MG Powder for Oral Solution) } Pack
        "1860085",  # {1 (240 ML) (acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 0.667 MG/ML / doxylamine succinate 0.417 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution) / 1 (240 ML) (acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 0.667 MG/ML / guaifenesin 13.3 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution) } Pack
        "1927849",  # {12 (acetaminophen 250 MG / dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Capsule) / 8 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine hydrochloride 5 MG Oral Capsule) } Pack
        "1999651",  # 12 HR doxylamine succinate 20 MG / pyridoxine hydrochloride 20 MG Extended Release Oral Tablet
        "2056073",  # {1 (118 ML) (dextromethorphan hydrobromide 1 MG/ML / guaifenesin 20 MG/ML Oral Solution) / 1 (118 ML) (dextromethorphan hydrobromide 1.5 MG/ML / doxylamine succinate 0.625 MG/ML Oral Solution) } Pack
        "2172491",  # doxylamine succinate 10.5 MG / phenylephrine hydrochloride 10 MG Oral Tablet
    }


class EsterifiedEstrogens(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for esterified estrogen medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable esterified estrogen and esterified estrogen in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Esterified Estrogens"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1419"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197666",  # estrogens, esterified (USP) 0.3 MG Oral Tablet
        "197667",  # estrogens, esterified (USP) 0.625 MG Oral Tablet
        "197668",  # estrogens, esterified (USP) 1.25 MG Oral Tablet
        "197669",  # estrogens, esterified (USP) 2.5 MG Oral Tablet
        "197670",  # estrogens, esterified (USP) 1.25 MG / methyltestosterone 2.5 MG Oral Tablet
        "238006",  # estrogens, esterified (USP) 0.625 MG / methyltestosterone 1.25 MG Oral Tablet
    }


class Estradiol(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for estradiol.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable estradiol.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients and estradiol in combination with other medications.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Estradiol"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1365"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197657",  # estradiol 0.5 MG Oral Tablet
        "197658",  # estradiol 1 MG Oral Tablet
        "197659",  # estradiol 2 MG Oral Tablet
        "205333",  # estradiol 1.5 MG Oral Tablet
        "238003",  # 168 HR estradiol 0.00208 MG/HR Transdermal System
        "238004",  # 168 HR estradiol 0.00417 MG/HR Transdermal System
        "241527",  # 168 HR estradiol 0.00312 MG/HR Transdermal System
        "241946",  # 84 HR estradiol 0.00156 MG/HR Transdermal System
        "242333",  # 168 HR estradiol 0.00104 MG/HR Transdermal System
        "242891",  # 84 HR estradiol 0.00208 MG/HR Transdermal System
        "242892",  # 84 HR estradiol 0.00417 MG/HR Transdermal System
        "248478",  # 84 HR estradiol 0.00104 MG/HR Transdermal System
        "348906",  # estradiol 1 MG / norgestimate 0.09 MG Oral Tablet
        "402250",  # 168 HR estradiol 0.00188 MG/HR / levonorgestrel 0.000625 MG/HR Transdermal System
        "403922",  # 168 HR estradiol 0.00156 MG/HR Transdermal System
        "403923",  # 168 HR estradiol 0.0025 MG/HR Transdermal System
        "476545",  # 168 HR estradiol 0.000583 MG/HR Transdermal System
        "577027",  # estradiol 0.45 MG Oral Tablet
        "577029",  # estradiol 1.8 MG Oral Tablet
        "728118",  # estradiol 1.53 MG/ACTUAT Topical Spray
        "749850",  # {15 (estradiol 1 MG / norgestimate 0.09 MG Oral Tablet) / 15 (estradiol 1 MG Oral Tablet) } Pack
        "978941",  # estradiol valerate 3 MG Oral Tablet
        "978944",  # dienogest 2 MG / estradiol valerate 2 MG Oral Tablet
        "978946",  # dienogest 3 MG / estradiol valerate 2 MG Oral Tablet
        "978948",  # estradiol valerate 1 MG Oral Tablet
        "978949",  # {5 (dienogest 2 MG / estradiol valerate 2 MG Oral Tablet) / 17 (dienogest 3 MG / estradiol valerate 2 MG Oral Tablet) / 2 (estradiol valerate 1 MG Oral Tablet) / 2 (estradiol valerate 3 MG Oral Tablet) / 2 (inert ingredients 1 MG Oral Tablet) } Pack
        "1149632",  # 84 HR estradiol 0.00313 MG/HR Transdermal System
        "1251493",  # 84 HR estradiol 0.00208 MG/HR / norethindrone acetate 0.00583 MG/HR Transdermal System
        "1251499",  # 84 HR estradiol 0.00208 MG/HR / norethindrone acetate 0.0104 MG/HR Transdermal System
        "1359123",  # estradiol 0.5 MG / norethindrone acetate 0.1 MG Oral Tablet
        "1359124",  # {28 (estradiol 0.5 MG / norethindrone acetate 0.1 MG Oral Tablet) } Pack
        "1359126",  # estradiol 1 MG / norethindrone acetate 0.5 MG Oral Tablet
        "1359127",  # {28 (estradiol 1 MG / norethindrone acetate 0.5 MG Oral Tablet) } Pack
        "1483549",  # drospirenone 0.25 MG / estradiol 0.5 MG Oral Tablet
        "1483550",  # {28 (drospirenone 0.25 MG / estradiol 0.5 MG Oral Tablet) } Pack
        "1483552",  # drospirenone 0.5 MG / estradiol 1 MG Oral Tablet
        "1483553",  # {28 (drospirenone 0.5 MG / estradiol 1 MG Oral Tablet) } Pack
        "2108924",  # estradiol 1 MG / progesterone 100 MG Oral Capsule
        "2371764",  # elagolix 300 MG / estradiol 1 MG / norethindrone 0.5 MG Oral Capsule
        "2371767",  # {28 (elagolix 300 MG / estradiol 1 MG / norethindrone 0.5 MG Oral Capsule) / 28 (elagolix 300 MG Oral Capsule) } Pack
    }


class Estropipate(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for estropipate medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable estropipate and estropipate in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Estropipate"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1319"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "310212",  # estropipate 0.75 MG Oral Tablet
        "310213",  # estropipate 1.5 MG Oral Tablet
        "310215",  # estropipate 3 MG Oral Tablet
    }


class Glyburide(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for glyburide.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable glyburide.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients and glyburide in combination with other medications.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Glyburide"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1368"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197737",  # glyburide 1.25 MG Oral Tablet
        "310534",  # glyburide 2.5 MG Oral Tablet
        "310536",  # glyburide 3 MG Oral Tablet
        "310537",  # glyburide 5 MG Oral Tablet
        "310539",  # glyburide 6 MG Oral Tablet
        "314000",  # glyburide 1.5 MG Oral Tablet
        "861743",  # glyburide 1.25 MG / metformin hydrochloride 250 MG Oral Tablet
        "861748",  # glyburide 2.5 MG / metformin hydrochloride 500 MG Oral Tablet
        "861753",  # glyburide 5 MG / metformin hydrochloride 500 MG Oral Tablet
    }


class Guanfacine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for guanfacine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable guanfacine and guanfacine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Guanfacine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1341"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197745",  # guanfacine 1 MG Oral Tablet
        "197746",  # guanfacine 2 MG Oral Tablet
        "862006",  # 24 HR guanfacine 1 MG Extended Release Oral Tablet
        "862013",  # 24 HR guanfacine 2 MG Extended Release Oral Tablet
        "862019",  # 24 HR guanfacine 3 MG Extended Release Oral Tablet
        "862025",  # 24 HR guanfacine 4 MG Extended Release Oral Tablet
        "1092566",  # {7 (24 HR guanfacine 1 MG Extended Release Oral Tablet) / 7 (24 HR guanfacine 2 MG Extended Release Oral Tablet) } Pack
    }


class Hydroxyzine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for hydroxyzine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable hydroxyzine and hydroxyzine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Hydroxyzine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1374"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "995218",  # hydroxyzine hydrochloride 10 MG Oral Tablet
        "995232",  # hydroxyzine pamoate 100 MG Oral Capsule
        "995241",  # hydroxyzine hydrochloride 2 MG/ML Oral Solution
        "995258",  # hydroxyzine hydrochloride 25 MG Oral Tablet
        "995270",  # 1 ML hydroxyzine hydrochloride 25 MG/ML Injection
        "995278",  # hydroxyzine pamoate 50 MG Oral Capsule
        "995281",  # hydroxyzine hydrochloride 50 MG Oral Tablet
        "995285",  # hydroxyzine hydrochloride 50 MG/ML Injectable Solution
        "1794552",  # 2 ML hydroxyzine hydrochloride 50 MG/ML Injection
        "1794554",  # 1 ML hydroxyzine hydrochloride 50 MG/ML Injection
    }


class Hyoscyamine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for hyoscyamine.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable hyoscyamine.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients and hyoscyamine in combination with other medications.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Hyoscyamine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1501"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "998726",  # hyoscyamine sulfate 0.0625 MG / phenyltoloxamine citrate 15 MG Oral Capsule
        "1037234",  # benzoic acid 9 MG / hyoscyamine sulfate 0.12 MG / methenamine 81.6 MG / methylene blue 10.8 MG / phenyl salicylate 36.2 MG Oral Tablet
        "1046770",  # 12 HR hyoscyamine sulfate 0.375 MG Extended Release Oral Tablet
        "1046787",  # atropine sulfate 0.00388 MG/ML / hyoscyamine sulfate 0.0207 MG/ML / phenobarbital 3.24 MG/ML / scopolamine hydrobromide 0.0013 MG/ML Oral Solution
        "1046815",  # atropine sulfate 0.0194 MG / hyoscyamine sulfate 0.1037 MG / phenobarbital 16.2 MG / scopolamine hydrobromide 0.0065 MG Oral Tablet
        "1046982",  # hyoscyamine sulfate 0.125 MG Sublingual Tablet
        "1046985",  # hyoscyamine sulfate 0.125 MG Disintegrating Oral Tablet
        "1046997",  # atropine sulfate 0.0582 MG / hyoscyamine sulfate 0.311 MG / phenobarbital 48.6 MG / scopolamine hydrobromide 0.0195 MG Extended Release Oral Tablet
        "1047786",  # hyoscyamine sulfate 0.12 MG / methenamine 81.6 MG / methylene blue 10.8 MG / phenyl salicylate 36.2 MG / sodium phosphate, monobasic 40.8 MG Oral Tablet
        "1047881",  # hyoscyamine sulfate 0.025 MG/ML Oral Solution
        "1047895",  # hyoscyamine sulfate 0.125 MG/ML Oral Solution
        "1047905",  # hyoscyamine sulfate 0.125 MG Oral Tablet
        "1047916",  # 1 ML hyoscyamine sulfate 0.5 MG/ML Injection
        "1048124",  # 12 HR atropine sulfate 0.04 MG / chlorpheniramine maleate 8 MG / hyoscyamine sulfate 0.19 MG / pseudoephedrine hydrochloride 90 MG / scopolamine hydrobromide 0.01 MG Extended Release Oral Tablet
        "1048147",  # atropine sulfate 0.0582 MG / hyoscyamine sulfate 0.3111 MG / phenobarbital 48.6 MG / scopolamine hydrobromide 0.0195 MG Extended Release Oral Tablet
        "1048307",  # hyoscyamine sulfate 0.12 MG / methenamine 120 MG / methylene blue 10 MG / phenyl salicylate 36 MG / sodium phosphate, monobasic 40.8 MG Oral Capsule
        "1048336",  # hyoscyamine sulfate 0.12 MG / methenamine 81 MG / methylene blue 10.8 MG / phenyl salicylate 32.4 MG / sodium phosphate, monobasic 40.8 MG Oral Tablet
        "1050325",  # hyoscyamine sulfate 0.12 MG / methenamine 81.6 MG / methylene blue 10.8 MG / sodium phosphate, monobasic 40.8 MG Oral Tablet
        "1087365",  # hyoscyamine sulfate 0.12 MG / methenamine 118 MG / methylene blue 10 MG / phenyl salicylate 36 MG / sodium phosphate, monobasic 40.8 MG Oral Capsule
        "1440869",  # hyoscyamine sulfate 0.12 MG / methenamine 120 MG / methylene blue 10.8 MG / phenyl salicylate 36.2 MG / sodium phosphate, monobasic 40.8 MG Oral Tablet
        "1598634",  # hyoscyamine sulfate 0.12 MG / methenamine 120 MG / methylene blue 10 MG / sodium phosphate, monobasic 40.8 MG Oral Capsule
        "1807886",  # Biphasic 12 HR hyoscyamine sulfate 0.375 MG Extended Release Oral Tablet
    }


class Imipramine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for imipramine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable imipramine and imipramine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Imipramine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1359"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "835564",  # imipramine hydrochloride 25 MG Oral Tablet
        "835568",  # imipramine hydrochloride 50 MG Oral Tablet
        "835572",  # imipramine pamoate 75 MG Oral Capsule
        "835577",  # imipramine pamoate 150 MG Oral Capsule
        "835589",  # imipramine pamoate 125 MG Oral Capsule
        "835591",  # imipramine pamoate 100 MG Oral Capsule
        "835593",  # imipramine hydrochloride 10 MG Oral Tablet
    }


class Indomethacin(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for indomethacine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable indomethacin and indomethacin in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Indomethacin"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1366"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197817",  # indomethacin 25 MG Oral Capsule
        "197818",  # indomethacin 50 MG Oral Capsule
        "310991",  # indomethacin 5 MG/ML Oral Suspension
        "310992",  # indomethacin 75 MG Extended Release Oral Capsule
        "1490727",  # indomethacin 20 MG Oral Capsule
        "1491529",  # indomethacin 40 MG Oral Capsule
    }


class Isoxsuprine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for isoxsuprine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable isoxsuprine and isoxsuprine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Isoxsuprine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1422"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "1298799",  # isoxsuprine hydrochloride 20 MG Oral Tablet
        "1298834",  # isoxsuprine hydrochloride 10 MG Oral Tablet
    }


class KetorolacTromethamine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for ketorolac tromethamine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable ketorolac tromethamine and ketorolac tromethamine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Ketorolac Tromethamine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1364"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "834022",  # ketorolac tromethamine 10 MG Oral Tablet
        "860092",  # 1 ML ketorolac tromethamine 15 MG/ML Injection
        "860096",  # ketorolac tromethamine 30 MG/ML Injectable Solution
        "860113",  # 1 ML ketorolac tromethamine 15 MG/ML Prefilled Syringe
        "860114",  # 1 ML ketorolac tromethamine 30 MG/ML Prefilled Syringe
        "860115",  # 2 ML ketorolac tromethamine 30 MG/ML Prefilled Syringe
        "1665459",  # 2 ML ketorolac tromethamine 30 MG/ML Injection
        "1665461",  # 1 ML ketorolac tromethamine 30 MG/ML Injection
        "1665675",  # 1 ML ketorolac tromethamine 15 MG/ML Cartridge
        "1665679",  # 1 ML ketorolac tromethamine 30 MG/ML Cartridge
        "1665682",  # 2 ML ketorolac tromethamine 30 MG/ML Cartridge
        "1797855",  # ketorolac tromethamine 15.8 MG/ACTUAT Metered Dose Nasal Spray
    }


class ListOfSingleRxnormCodeConceptsForHighRiskDrugsForTheElderly(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for high risk medications for the elderly.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable medications considered high risk for the elderly.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "List of Single RxNorm Code Concepts for High Risk Drugs for the Elderly"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1272"
    DEFINITION_VERSION = "20210406"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "238133",  # pentazocine 30 MG/ML Injectable Solution
        "308170",  # amobarbital sodium 500 MG Injection
        "312289",  # naloxone 0.5 MG / pentazocine 50 MG Oral Tablet
        "313406",  # ticlopidine hydrochloride 250 MG Oral Tablet
        "318179",  # ergoloid mesylates, USP 1 MG Oral Tablet
    }


class Meclizine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for meclizine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable meclizine and meclizine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Meclizine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1506"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "995624",  # meclizine hydrochloride 12.5 MG Oral Tablet
        "995632",  # meclizine hydrochloride 25 MG Chewable Tablet
        "995666",  # meclizine hydrochloride 25 MG Oral Tablet
        "995686",  # meclizine hydrochloride 50 MG Oral Tablet
        "1663815",  # meclizine hydrochloride 25 MG Disintegrating Oral Tablet
    }


class Megestrol(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for megestrol medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable megestrol and megestrol in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Megestrol"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1342"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "577154",  # megestrol acetate 125 MG/ML Oral Suspension
        "860215",  # megestrol acetate 20 MG Oral Tablet
        "860221",  # megestrol acetate 40 MG Oral Tablet
        "860225",  # megestrol acetate 40 MG/ML Oral Suspension
    }


class Meperidine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for meperidine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable meperidine and meperidine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Meperidine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1351"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "860792",  # 1 ML meperidine hydrochloride 75 MG/ML Cartridge
        "861447",  # meperidine hydrochloride 10 MG/ML Injectable Solution
        "861455",  # meperidine hydrochloride 100 MG Oral Tablet
        "861459",  # meperidine hydrochloride 100 MG/ML Injectable Solution
        "861463",  # meperidine hydrochloride 50 MG/ML Injectable Solution
        "861467",  # meperidine hydrochloride 50 MG Oral Tablet
        "861473",  # 1 ML meperidine hydrochloride 50 MG/ML Cartridge
        "861476",  # 1 ML meperidine hydrochloride 25 MG/ML Injection
        "861479",  # meperidine hydrochloride 10 MG/ML Oral Solution
        "861493",  # 1 ML meperidine hydrochloride 100 MG/ML Cartridge
        "861494",  # 1 ML meperidine hydrochloride 25 MG/ML Cartridge
        "1655058",  # meperidine hydrochloride 150 MG Oral Tablet
        "1655060",  # meperidine hydrochloride 75 MG Oral Tablet
        "1665685",  # 1 ML meperidine hydrochloride 100 MG/ML Injection
        "1665690",  # 1.5 ML meperidine hydrochloride 50 MG/ML Injection
        "1665697",  # 1 ML meperidine hydrochloride 50 MG/ML Injection
        "1665699",  # 0.5 ML meperidine hydrochloride 50 MG/ML Injection
        "1665701",  # 2 ML meperidine hydrochloride 50 MG/ML Injection
    }


class Meprobamate(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for meprobamate.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable meprobamate.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients and meprobamate in combination with other medications.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Meprobamate"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1284"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197928",  # meprobamate 200 MG Oral Tablet
        "197929",  # meprobamate 400 MG Oral Tablet
    }


class Metaxalone(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for metaxalone medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable metaxalone and metaxalone in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Metaxalone"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1358"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197935",  # metaxalone 400 MG Oral Tablet
        "351254",  # metaxalone 800 MG Oral Tablet
    }


class Methocarbamol(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for methocarbamol.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable methocarbamol.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients and methocarbamol in combination with other medications.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Methocarbamol"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1370"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197943",  # methocarbamol 500 MG Oral Tablet
        "197944",  # methocarbamol 750 MG Oral Tablet
    }


class Methscopolamine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for methscopolamine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable methscopolamine medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Methscopolamine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1525"
    DEFINITION_VERSION = "20210224"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "314088",  # methscopolamine bromide 2.5 MG Oral Tablet
        "403914",  # methscopolamine bromide 5 MG Oral Tablet
    }


class Methyldopa(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for methyldopa.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable methyldopa.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients and methyldopa in combination with other medications.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Methyldopa"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1331"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197956",  # methyldopa 250 MG Oral Tablet
        "197958",  # methyldopa 500 MG Oral Tablet
        "197960",  # hydrochlorothiazide 25 MG / methyldopa 250 MG Oral Tablet
        "197963",  # hydrochlorothiazide 15 MG / methyldopa 250 MG Oral Tablet
    }


class Nifedipine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for nifedipine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable nifedipine and nifedipine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Nifedipine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1353"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "198032",  # nifedipine 10 MG Oral Capsule
        "198033",  # nifedipine 20 MG Oral Capsule
    }


class NonbenzodiazepineHypnotics(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for nonbenzodiazepine hypnotic medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable nonbenzodiazepine hypnotic medication.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Nonbenzodiazepine hypnotics"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1480"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "313761",  # zaleplon 10 MG Oral Capsule
        "313762",  # zaleplon 5 MG Oral Capsule
        "485440",  # eszopiclone 1 MG Oral Tablet
        "485442",  # eszopiclone 2 MG Oral Tablet
        "485465",  # eszopiclone 3 MG Oral Tablet
        "828692",  # zolpidem tartrate 5 MG/ACTUAT Oral Spray
        "836641",  # zolpidem tartrate 10 MG Sublingual Tablet
        "836647",  # zolpidem tartrate 5 MG Sublingual Tablet
        "854873",  # zolpidem tartrate 10 MG Oral Tablet
        "854876",  # zolpidem tartrate 5 MG Oral Tablet
        "854880",  # zolpidem tartrate 12.5 MG Extended Release Oral Tablet
        "854894",  # zolpidem tartrate 6.25 MG Extended Release Oral Tablet
        "1232194",  # zolpidem tartrate 1.75 MG Sublingual Tablet
        "1232202",  # zolpidem tartrate 3.5 MG Sublingual Tablet
    }


class Nortriptyline(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for nortriptyline.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable nortriptyline.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients and nortriptyline in combination with other medications.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Nortriptyline"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1507"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "198045",  # nortriptyline 10 MG Oral Capsule
        "198046",  # nortriptyline 50 MG Oral Capsule
        "198047",  # nortriptyline 75 MG Oral Capsule
        "312036",  # nortriptyline 2 MG/ML Oral Solution
        "317136",  # nortriptyline 25 MG Oral Capsule
    }


class Orphenadrine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for orphenadrine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable orphenadrine and orphenadrine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Orphenadrine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1302"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "994521",  # 12 HR orphenadrine citrate 100 MG Extended Release Oral Tablet
        "994528",  # aspirin 385 MG / caffeine 30 MG / orphenadrine citrate 25 MG Oral Tablet
        "994535",  # aspirin 770 MG / caffeine 60 MG / orphenadrine citrate 50 MG Oral Tablet
    }


class Paroxetine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for paroxetine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable paroxetine and paroxetine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Paroxetine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1508"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "312242",  # paroxetine hydrochloride 2 MG/ML Oral Suspension
        "1430122",  # paroxetine mesylate 7.5 MG Oral Capsule
        "1738483",  # paroxetine hydrochloride 10 MG Oral Tablet
        "1738495",  # paroxetine hydrochloride 20 MG Oral Tablet
        "1738503",  # paroxetine hydrochloride 30 MG Oral Tablet
        "1738511",  # paroxetine hydrochloride 40 MG Oral Tablet
        "1738515",  # paroxetine mesylate 10 MG Oral Tablet
        "1738519",  # paroxetine mesylate 20 MG Oral Tablet
        "1738523",  # paroxetine mesylate 30 MG Oral Tablet
        "1738527",  # paroxetine mesylate 40 MG Oral Tablet
        "1738803",  # 24 HR paroxetine hydrochloride 12.5 MG Extended Release Oral Tablet
        "1738805",  # 24 HR paroxetine hydrochloride 25 MG Extended Release Oral Tablet
        "1738807",  # 24 HR paroxetine hydrochloride 37.5 MG Extended Release Oral Tablet
    }


class Pentobarbital(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for pentobarbital medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable pentobarbital and penobarbital in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Pentobarbital"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1518"
    DEFINITION_VERSION = "20200310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "238090",  # pentobarbital sodium 50 MG/ML Injectable Solution
    }


class Phenobarbital(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for pentobarbital.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable phentobarbital.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients and phenobarbital in combination with other medications.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Phenobarbital"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1348"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "198083",  # phenobarbital 100 MG Oral Tablet
        "198085",  # phenobarbital 16 MG Oral Tablet
        "198086",  # phenobarbital 16.2 MG Oral Tablet
        "198089",  # phenobarbital 60 MG Oral Tablet
        "198368",  # phenobarbital 65 MG/ML Injectable Solution
        "199164",  # phenobarbital 97.2 MG Oral Tablet
        "199167",  # phenobarbital 32.4 MG Oral Tablet
        "199168",  # phenobarbital 64.8 MG Oral Tablet
        "312357",  # phenobarbital 15 MG Oral Tablet
        "312362",  # phenobarbital 30 MG Oral Tablet
        "312370",  # phenobarbital 130 MG/ML Injectable Solution
        "702519",  # phenobarbital 4 MG/ML Oral Solution
        "1046787",  # atropine sulfate 0.00388 MG/ML / hyoscyamine sulfate 0.0207 MG/ML / phenobarbital 3.24 MG/ML / scopolamine hydrobromide 0.0013 MG/ML Oral Solution
        "1046815",  # atropine sulfate 0.0194 MG / hyoscyamine sulfate 0.1037 MG / phenobarbital 16.2 MG / scopolamine hydrobromide 0.0065 MG Oral Tablet
        "1046997",  # atropine sulfate 0.0582 MG / hyoscyamine sulfate 0.311 MG / phenobarbital 48.6 MG / scopolamine hydrobromide 0.0195 MG Extended Release Oral Tablet
        "1048147",  # atropine sulfate 0.0582 MG / hyoscyamine sulfate 0.3111 MG / phenobarbital 48.6 MG / scopolamine hydrobromide 0.0195 MG Extended Release Oral Tablet
    }


class PromethazineHydrochloride(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for promethazine hydrochloride.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable promethazine hydrochloride.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients and promethazine hydrochloride in combination with other medications.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Promethazine Hydrochloride"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1367"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "991486",  # codeine phosphate 2 MG/ML / promethazine hydrochloride 1.25 MG/ML Oral Solution
        "991528",  # dextromethorphan hydrobromide 3 MG/ML / promethazine hydrochloride 1.25 MG/ML Oral Solution
        "992432",  # promethazine hydrochloride 1.25 MG/ML Oral Solution
        "992438",  # promethazine hydrochloride 12.5 MG Oral Tablet
        "992447",  # promethazine hydrochloride 25 MG Oral Tablet
        "992460",  # 1 ML promethazine hydrochloride 25 MG/ML Injection
        "992475",  # promethazine hydrochloride 50 MG Oral Tablet
        "992858",  # 1 ML promethazine hydrochloride 50 MG/ML Injection
        "996757",  # codeine phosphate 2 MG/ML / phenylephrine hydrochloride 1 MG/ML / promethazine hydrochloride 1.25 MG/ML Oral Solution
        "1248057",  # phenylephrine hydrochloride 1 MG/ML / promethazine hydrochloride 1.25 MG/ML Oral Solution
    }


class Propantheline(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for propantheline.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable propantheline and propantheline in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Propantheline"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1519"
    DEFINITION_VERSION = "20200310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "198165",  # propantheline 15 MG Oral Tablet
    }


class Protriptyline(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for protriptyline medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable protriptyline and protriptyline in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Protriptyline"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1509"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "905168",  # protriptyline hydrochloride 10 MG Oral Tablet
        "905172",  # protriptyline hydrochloride 5 MG Oral Tablet
    }


class Pyrilamine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for pyrilamine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable pyrilamine and pyrilamine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Pyrilamine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1524"
    DEFINITION_VERSION = "20210224"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "604664",  # chlorpheniramine maleate 0.4 MG/ML / phenylephrine hydrochloride 1.5 MG/ML / pyrilamine maleate 2.5 MG/ML Oral Solution
        "701913",  # acetaminophen 500 MG / caffeine 60 MG / pyrilamine maleate 15 MG Oral Capsule
        "860151",  # hydrocodone bitartrate 1 MG/ML / phenylephrine hydrochloride 1 MG/ML / pyrilamine maleate 1 MG/ML Oral Solution
        "1013731",  # phenylephrine hydrochloride 10 MG / pyrilamine maleate 25 MG Oral Tablet
        "1052637",  # acetaminophen 500 MG / pamabrom 25 MG / pyrilamine maleate 15 MG Oral Tablet
        "1241829",  # acetaminophen 325 MG / phenylephrine hydrochloride 5 MG / pyrilamine maleate 25 MG Oral Tablet
        "1363733",  # dextromethorphan tannate 25 MG / phenylephrine tannate 25 MG / pyrilamine tannate 30 MG Chewable Tablet
        "1423307",  # dextromethorphan hydrobromide 1.5 MG/ML / pyrilamine maleate 1.5 MG/ML Oral Solution
        "1538456",  # acetaminophen 325 MG / pyrilamine maleate 25 MG Oral Tablet
        "1593749",  # chlophedianol hydrochloride 2.5 MG/ML / pyrilamine maleate 2.5 MG/ML Oral Solution
        "1593765",  # acetaminophen 32 MG/ML / chlophedianol hydrochloride 2.5 MG/ML / pyrilamine maleate 2.5 MG/ML Oral Solution
        "1597298",  # acetaminophen 500 MG / caffeine 60 MG / pyrilamine maleate 15 MG Oral Tablet
        "1735487",  # chlophedianol hydrochloride 25 MG / pyrilamine maleate 50 MG Oral Tablet
        "1808189",  # chlophedianol hydrochloride 0.417 MG/ML / pyrilamine maleate 0.833 MG/ML Oral Solution
        "1858383",  # phenylephrine hydrochloride 1 MG/ML / pyrilamine maleate 3.2 MG/ML Oral Solution
        "1874721",  # chlophedianol hydrochloride 12.5 MG / pyrilamine maleate 25 MG Oral Tablet
        "1923362",  # dextromethorphan hydrobromide 30 MG / pyrilamine maleate 30 MG Oral Tablet
        "1943497",  # chlophedianol hydrochloride 2.5 MG/ML / pseudoephedrine hydrochloride 6 MG/ML / pyrilamine maleate 2.5 MG/ML Oral Solution
        "2178279",  # pyrilamine maleate 0.833 MG/ML Oral Solution
        "2268057",  # chlophedianol hydrochloride 12.5 MG / pyrilamine maleate 12.5 MG Chewable Tablet
    }


class Scopolamine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for scopolamine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable scopolamine and scopolamine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Scopolamine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1520"
    DEFINITION_VERSION = "20200310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "198207",  # scopolamine 0.4 MG/ML Injectable Solution
        "226552",  # 72 HR scopolamine 0.0139 MG/HR Transdermal System
        "1046787",  # atropine sulfate 0.00388 MG/ML / hyoscyamine sulfate 0.0207 MG/ML / phenobarbital 3.24 MG/ML / scopolamine hydrobromide 0.0013 MG/ML Oral Solution
        "1046815",  # atropine sulfate 0.0194 MG / hyoscyamine sulfate 0.1037 MG / phenobarbital 16.2 MG / scopolamine hydrobromide 0.0065 MG Oral Tablet
        "1046997",  # atropine sulfate 0.0582 MG / hyoscyamine sulfate 0.311 MG / phenobarbital 48.6 MG / scopolamine hydrobromide 0.0195 MG Extended Release Oral Tablet
        "1048124",  # 12 HR atropine sulfate 0.04 MG / chlorpheniramine maleate 8 MG / hyoscyamine sulfate 0.19 MG / pseudoephedrine hydrochloride 90 MG / scopolamine hydrobromide 0.01 MG Extended Release Oral Tablet
        "1048147",  # atropine sulfate 0.0582 MG / hyoscyamine sulfate 0.3111 MG / phenobarbital 48.6 MG / scopolamine hydrobromide 0.0195 MG Extended Release Oral Tablet
    }


class Secobarbital(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for secobarbital medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable secobarbital and secobarbital in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Secobarbital"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1521"
    DEFINITION_VERSION = "20200310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "312914",  # secobarbital sodium 100 MG Oral Capsule
    }


class Trihexyphenidyl(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for trihexyphenidyl medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable trihexyphenidyl and trihexyphenidyl in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Trihexyphenidyl"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1334"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "905269",  # trihexyphenidyl hydrochloride 2 MG Oral Tablet
        "905273",  # trihexyphenidyl hydrochloride 0.4 MG/ML Oral Solution
        "905283",  # trihexyphenidyl hydrochloride 5 MG Oral Tablet
    }


class Trimipramine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for trimipramine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable trimipramine and trimipramine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Trimipramine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1285"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "313496",  # trimipramine 100 MG Oral Capsule
        "313498",  # trimipramine 25 MG Oral Capsule
        "313499",  # trimipramine 50 MG Oral Capsule
    }


class Triprolidine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for triprolidine.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable triprolidine.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients and triprolidine in combination with other medications.

    ** Used in:** CMS156v10
    """

    VALUE_SET_NAME = "Triprolidine"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1408"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "1094434",  # phenylephrine hydrochloride 2 MG/ML / triprolidine hydrochloride 0.5 MG/ML Oral Solution
        "1099308",  # pseudoephedrine hydrochloride 6 MG/ML / triprolidine hydrochloride 0.25 MG/ML Oral Solution
        "1099446",  # pseudoephedrine hydrochloride 60 MG / triprolidine hydrochloride 2.5 MG Oral Tablet
        "1099653",  # dextromethorphan hydrobromide 4 MG/ML / pseudoephedrine hydrochloride 10 MG/ML / triprolidine hydrochloride 0.938 MG/ML Oral Suspension
        "1099668",  # pseudoephedrine hydrochloride 10 MG/ML / triprolidine hydrochloride 0.938 MG/ML Oral Solution
        "1428927",  # triprolidine hydrochloride 0.625 MG/ML Oral Solution
        "1490671",  # triprolidine hydrochloride 0.5 MG/ML Oral Solution
        "1491649",  # triprolidine hydrochloride 0.938 MG/ML Oral Solution
        "1492052",  # dextromethorphan hydrobromide 4 MG/ML / phenylephrine hydrochloride 2 MG/ML / triprolidine hydrochloride 0.5 MG/ML Oral Solution
        "1661319",  # codeine phosphate 2 MG/ML / phenylephrine hydrochloride 2 MG/ML / triprolidine hydrochloride 0.5 MG/ML Oral Solution
        "1789508",  # triprolidine hydrochloride 0.313 MG/ML Oral Solution
        "1926926",  # triprolidine hydrochloride 1.25 MG/ML Oral Solution
        "1939354",  # triprolidine hydrochloride 1.25 MG Chewable Tablet
        "2173662",  # acetaminophen 32.5 MG/ML / dextromethorphan hydrobromide 1 MG/ML / phenylephrine hydrochloride 0.5 MG/ML / triprolidine hydrochloride 0.125 MG/ML Oral Solution
        "2173667",  # acetaminophen 32.5 MG/ML / dextromethorphan hydrobromide 1 MG/ML / triprolidine hydrochloride 0.125 MG/ML Oral Solution
    }


class PharmacologicTherapyForHypertension(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent medications  prescribed for the treatment of hypertension.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that describe a medication for treatment of hypertension.

    **Exclusion Criteria:** Excludes concepts that represent  branded and non-prescribable drugs.

    ** Used in:** CMS22v10
    """

    VALUE_SET_NAME = "Pharmacologic Therapy for Hypertension"
    OID = "2.16.840.1.113883.3.526.1577"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "153822",  # candesartan cilexetil 4 MG Oral Tablet
        "153823",  # candesartan cilexetil 8 MG Oral Tablet
        "197361",  # amlodipine 5 MG Oral Tablet
        "197379",  # atenolol 100 MG Oral Tablet
        "197380",  # atenolol 25 MG Oral Tablet
        "197381",  # atenolol 50 MG Oral Tablet
        "197382",  # atenolol 100 MG / chlorthalidone 25 MG Oral Tablet
        "197383",  # atenolol 50 MG / chlorthalidone 25 MG Oral Tablet
        "197417",  # bumetanide 0.5 MG Oral Tablet
        "197418",  # bumetanide 1 MG Oral Tablet
        "197419",  # bumetanide 2 MG Oral Tablet
        "197436",  # captopril 25 MG / hydrochlorothiazide 15 MG Oral Tablet
        "197437",  # captopril 25 MG / hydrochlorothiazide 25 MG Oral Tablet
        "197438",  # captopril 50 MG / hydrochlorothiazide 15 MG Oral Tablet
        "197439",  # captopril 50 MG / hydrochlorothiazide 25 MG Oral Tablet
        "197475",  # chlorothiazide 250 MG Oral Tablet
        "197476",  # chlorothiazide 500 MG Oral Tablet
        "197499",  # chlorthalidone 25 MG Oral Tablet
        "197500",  # chlorthalidone 50 MG Oral Tablet
        "197625",  # doxazosin 1 MG Oral Tablet
        "197626",  # doxazosin 2 MG Oral Tablet
        "197627",  # doxazosin 4 MG Oral Tablet
        "197628",  # doxazosin 8 MG Oral Tablet
        "197730",  # furosemide 10 MG/ML Oral Solution
        "197731",  # furosemide 8 MG/ML Oral Solution
        "197732",  # furosemide 80 MG Oral Tablet
        "197745",  # guanfacine 1 MG Oral Tablet
        "197746",  # guanfacine 2 MG Oral Tablet
        "197770",  # hydrochlorothiazide 50 MG Oral Tablet
        "197815",  # indapamide 1.25 MG Oral Tablet
        "197816",  # indapamide 2.5 MG Oral Tablet
        "197848",  # isradipine 2.5 MG Oral Capsule
        "197849",  # isradipine 5 MG Oral Capsule
        "197884",  # lisinopril 40 MG Oral Tablet
        "197885",  # hydrochlorothiazide 12.5 MG / lisinopril 10 MG Oral Tablet
        "197886",  # hydrochlorothiazide 12.5 MG / lisinopril 20 MG Oral Tablet
        "197887",  # hydrochlorothiazide 25 MG / lisinopril 20 MG Oral Tablet
        "197951",  # methyclothiazide 5 MG Oral Tablet
        "197956",  # methyldopa 250 MG Oral Tablet
        "197958",  # methyldopa 500 MG Oral Tablet
        "197960",  # hydrochlorothiazide 25 MG / methyldopa 250 MG Oral Tablet
        "197963",  # hydrochlorothiazide 15 MG / methyldopa 250 MG Oral Tablet
        "197978",  # metolazone 10 MG Oral Tablet
        "197979",  # metolazone 2.5 MG Oral Tablet
        "197986",  # minoxidil 10 MG Oral Tablet
        "197987",  # minoxidil 2.5 MG Oral Tablet
        "198000",  # bendroflumethiazide 5 MG / nadolol 40 MG Oral Tablet
        "198001",  # bendroflumethiazide 5 MG / nadolol 80 MG Oral Tablet
        "198006",  # nadolol 20 MG Oral Tablet
        "198007",  # nadolol 40 MG Oral Tablet
        "198008",  # nadolol 80 MG Oral Tablet
        "198032",  # nifedipine 10 MG Oral Capsule
        "198033",  # nifedipine 20 MG Oral Capsule
        "198034",  # 24 HR nifedipine 30 MG Extended Release Oral Tablet
        "198035",  # 24 HR nifedipine 60 MG Extended Release Oral Tablet
        "198036",  # 24 HR nifedipine 90 MG Extended Release Oral Tablet
        "198037",  # nimodipine 30 MG Oral Capsule
        "198104",  # pindolol 10 MG Oral Tablet
        "198105",  # pindolol 5 MG Oral Tablet
        "198141",  # prazosin 5 MG Oral Capsule
        "198188",  # ramipril 2.5 MG Oral Capsule
        "198189",  # ramipril 5 MG Oral Capsule
        "198222",  # spironolactone 100 MG Oral Tablet
        "198223",  # spironolactone 50 MG Oral Tablet
        "198224",  # hydrochlorothiazide 25 MG / spironolactone 25 MG Oral Tablet
        "198225",  # hydrochlorothiazide 50 MG / spironolactone 50 MG Oral Tablet
        "198284",  # timolol 10 MG Oral Tablet
        "198285",  # timolol 20 MG Oral Tablet
        "198286",  # timolol 5 MG Oral Tablet
        "198312",  # triamterene 100 MG Oral Capsule
        "198313",  # triamterene 50 MG Oral Capsule
        "198314",  # hydrochlorothiazide 25 MG / triamterene 50 MG Oral Capsule
        "198316",  # hydrochlorothiazide 25 MG / triamterene 37.5 MG Oral Capsule
        "198369",  # torsemide 10 MG Oral Tablet
        "198370",  # torsemide 100 MG Oral Tablet
        "198371",  # torsemide 20 MG Oral Tablet
        "198372",  # torsemide 5 MG Oral Tablet
        "199351",  # trandolapril 2 MG Oral Tablet
        "199352",  # trandolapril 4 MG Oral Tablet
        "199353",  # trandolapril 1 MG Oral Tablet
        "199903",  # hydrochlorothiazide 12.5 MG Oral Capsule
        "200031",  # carvedilol 6.25 MG Oral Tablet
        "200032",  # carvedilol 12.5 MG Oral Tablet
        "200033",  # carvedilol 25 MG Oral Tablet
        "200094",  # irbesartan 75 MG Oral Tablet
        "200095",  # irbesartan 150 MG Oral Tablet
        "200096",  # irbesartan 300 MG Oral Tablet
        "200284",  # hydrochlorothiazide 12.5 MG / valsartan 80 MG Oral Tablet
        "200285",  # hydrochlorothiazide 12.5 MG / valsartan 160 MG Oral Tablet
        "205304",  # telmisartan 40 MG Oral Tablet
        "205305",  # telmisartan 80 MG Oral Tablet
        "205326",  # lisinopril 30 MG Oral Tablet
        "251856",  # ramipril 2.5 MG Oral Tablet
        "251857",  # ramipril 5 MG Oral Tablet
        "260376",  # terazosin 10 MG Oral Capsule
        "261962",  # ramipril 10 MG Oral Capsule
        "282486",  # bumetanide 0.25 MG/ML Injectable Solution
        "282755",  # telmisartan 20 MG Oral Tablet
        "283316",  # hydrochlorothiazide 12.5 MG / telmisartan 40 MG Oral Tablet
        "283317",  # hydrochlorothiazide 12.5 MG / telmisartan 80 MG Oral Tablet
        "308135",  # amlodipine 10 MG Oral Tablet
        "308136",  # amlodipine 2.5 MG Oral Tablet
        "308962",  # captopril 100 MG Oral Tablet
        "308963",  # captopril 12.5 MG Oral Tablet
        "308964",  # captopril 50 MG Oral Tablet
        "309198",  # chlorothiazide 50 MG/ML Oral Suspension
        "310140",  # eprosartan 600 MG Oral Tablet
        "310429",  # furosemide 20 MG Oral Tablet
        "310792",  # hydrochlorothiazide 12.5 MG / irbesartan 150 MG Oral Tablet
        "310793",  # hydrochlorothiazide 12.5 MG / irbesartan 300 MG Oral Tablet
        "310796",  # hydrochlorothiazide 12.5 MG / quinapril 10 MG Oral Tablet
        "310797",  # hydrochlorothiazide 12.5 MG / quinapril 20 MG Oral Tablet
        "310798",  # hydrochlorothiazide 25 MG Oral Tablet
        "310809",  # hydrochlorothiazide 25 MG / quinapril 20 MG Oral Tablet
        "310812",  # hydrochlorothiazide 25 MG / triamterene 37.5 MG Oral Tablet
        "310818",  # hydrochlorothiazide 50 MG / triamterene 75 MG Oral Tablet
        "311353",  # lisinopril 2.5 MG Oral Tablet
        "311354",  # lisinopril 5 MG Oral Tablet
        "311671",  # metolazone 5 MG Oral Tablet
        "311984",  # 24 HR nisoldipine 20 MG Extended Release Oral Tablet
        "311985",  # 24 HR nisoldipine 30 MG Extended Release Oral Tablet
        "312593",  # prazosin 1 MG Oral Capsule
        "312594",  # prazosin 2 MG Oral Capsule
        "312748",  # quinapril 10 MG Oral Tablet
        "312749",  # quinapril 20 MG Oral Tablet
        "312750",  # quinapril 5 MG Oral Tablet
        "313096",  # spironolactone 25 MG Oral Tablet
        "313215",  # terazosin 1 MG Oral Capsule
        "313217",  # terazosin 2 MG Oral Capsule
        "313219",  # terazosin 5 MG Oral Capsule
        "313988",  # furosemide 40 MG Oral Tablet
        "314076",  # lisinopril 10 MG Oral Tablet
        "314077",  # lisinopril 20 MG Oral Tablet
        "314203",  # quinapril 40 MG Oral Tablet
        "317173",  # captopril 25 MG Oral Tablet
        "349199",  # valsartan 80 MG Oral Tablet
        "349200",  # valsartan 320 MG Oral Tablet
        "349201",  # valsartan 160 MG Oral Tablet
        "349353",  # hydrochlorothiazide 25 MG / valsartan 160 MG Oral Tablet
        "349373",  # olmesartan medoxomil 5 MG Oral Tablet
        "349401",  # olmesartan medoxomil 20 MG Oral Tablet
        "349405",  # olmesartan medoxomil 40 MG Oral Tablet
        "349483",  # valsartan 40 MG Oral Tablet
        "351292",  # eprosartan 600 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "351293",  # eprosartan 600 MG / hydrochlorothiazide 25 MG Oral Tablet
        "360344",  # 24 HR nisoldipine 40 MG Extended Release Oral Tablet
        "387013",  # nebivolol 5 MG Oral Tablet
        "401965",  # ramipril 1.25 MG Oral Tablet
        "401968",  # ramipril 10 MG Oral Tablet
        "402695",  # 24 HR felodipine 10 MG Extended Release Oral Tablet
        "402696",  # 24 HR felodipine 5 MG Extended Release Oral Tablet
        "402698",  # 24 HR felodipine 2.5 MG Extended Release Oral Tablet
        "403853",  # hydrochlorothiazide 12.5 MG / olmesartan medoxomil 20 MG Oral Tablet
        "403854",  # hydrochlorothiazide 12.5 MG / olmesartan medoxomil 40 MG Oral Tablet
        "403855",  # hydrochlorothiazide 25 MG / olmesartan medoxomil 40 MG Oral Tablet
        "404011",  # amlodipine 5 MG / atorvastatin 80 MG Oral Tablet
        "404013",  # amlodipine 10 MG / atorvastatin 80 MG Oral Tablet
        "429503",  # hydrochlorothiazide 12.5 MG Oral Tablet
        "477130",  # hydrochlorothiazide 25 MG / telmisartan 80 MG Oral Tablet
        "484152",  # chlorothiazide 500 MG Injection
        "485471",  # hydrochlorothiazide 25 MG / irbesartan 300 MG Oral Tablet
        "562518",  # 24 HR isradipine 10 MG Extended Release Oral Tablet
        "562520",  # 24 HR isradipine 5 MG Extended Release Oral Tablet
        "577776",  # candesartan cilexetil 16 MG Oral Tablet
        "578325",  # candesartan cilexetil 16 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "578330",  # candesartan cilexetil 32 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "597967",  # amlodipine 10 MG / atorvastatin 20 MG Oral Tablet
        "597971",  # amlodipine 2.5 MG / atorvastatin 10 MG Oral Tablet
        "597974",  # amlodipine 2.5 MG / atorvastatin 20 MG Oral Tablet
        "597977",  # amlodipine 5 MG / atorvastatin 10 MG Oral Tablet
        "597980",  # amlodipine 5 MG / atorvastatin 20 MG Oral Tablet
        "597984",  # amlodipine 5 MG / atorvastatin 40 MG Oral Tablet
        "597987",  # amlodipine 10 MG / atorvastatin 10 MG Oral Tablet
        "597990",  # amlodipine 10 MG / atorvastatin 40 MG Oral Tablet
        "597993",  # amlodipine 2.5 MG / atorvastatin 40 MG Oral Tablet
        "636042",  # hydrochlorothiazide 12.5 MG / valsartan 320 MG Oral Tablet
        "636045",  # hydrochlorothiazide 25 MG / valsartan 320 MG Oral Tablet
        "636360",  # 24 HR doxazosin 4 MG Extended Release Oral Tablet
        "636361",  # 24 HR doxazosin 8 MG Extended Release Oral Tablet
        "639537",  # candesartan cilexetil 32 MG Oral Tablet
        "686924",  # carvedilol 3.125 MG Oral Tablet
        "722126",  # amlodipine 10 MG / valsartan 160 MG Oral Tablet
        "722131",  # amlodipine 10 MG / valsartan 320 MG Oral Tablet
        "722134",  # amlodipine 5 MG / valsartan 160 MG Oral Tablet
        "722137",  # amlodipine 5 MG / valsartan 320 MG Oral Tablet
        "727574",  # 10 ML furosemide 10 MG/ML Prefilled Syringe
        "727575",  # 4 ML furosemide 10 MG/ML Prefilled Syringe
        "730861",  # amlodipine 10 MG / olmesartan medoxomil 20 MG Oral Tablet
        "730866",  # amlodipine 10 MG / olmesartan medoxomil 40 MG Oral Tablet
        "730869",  # amlodipine 5 MG / olmesartan medoxomil 20 MG Oral Tablet
        "730872",  # amlodipine 5 MG / olmesartan medoxomil 40 MG Oral Tablet
        "751612",  # nebivolol 10 MG Oral Tablet
        "751618",  # nebivolol 2.5 MG Oral Tablet
        "763519",  # 24 HR nisoldipine 17 MG Extended Release Oral Tablet
        "763574",  # 24 HR nisoldipine 25.5 MG Extended Release Oral Tablet
        "763589",  # 24 HR nisoldipine 34 MG Extended Release Oral Tablet
        "790489",  # 24 HR nisoldipine 8.5 MG Extended Release Oral Tablet
        "802749",  # candesartan cilexetil 32 MG / hydrochlorothiazide 25 MG Oral Tablet
        "827073",  # nebivolol 20 MG Oral Tablet
        "830795",  # 24 HR diltiazem hydrochloride 360 MG Extended Release Oral Capsule
        "830801",  # 24 HR diltiazem hydrochloride 300 MG Extended Release Oral Capsule
        "830837",  # 24 HR diltiazem hydrochloride 240 MG Extended Release Oral Capsule
        "830845",  # 24 HR diltiazem hydrochloride 180 MG Extended Release Oral Capsule
        "830861",  # 24 HR diltiazem hydrochloride 120 MG Extended Release Oral Capsule
        "830865",  # 12 HR diltiazem hydrochloride 60 MG Extended Release Oral Capsule
        "830869",  # 12 HR diltiazem hydrochloride 90 MG Extended Release Oral Capsule
        "830872",  # 12 HR diltiazem hydrochloride 120 MG Extended Release Oral Capsule
        "830874",  # 24 HR diltiazem hydrochloride 120 MG Extended Release Oral Tablet
        "830877",  # 24 HR diltiazem hydrochloride 180 MG Extended Release Oral Tablet
        "830879",  # 24 HR diltiazem hydrochloride 240 MG Extended Release Oral Tablet
        "830882",  # 24 HR diltiazem hydrochloride 300 MG Extended Release Oral Tablet
        "830897",  # 24 HR diltiazem hydrochloride 360 MG Extended Release Oral Tablet
        "830900",  # 24 HR diltiazem hydrochloride 420 MG Extended Release Oral Tablet
        "831054",  # diltiazem hydrochloride 120 MG Oral Tablet
        "831102",  # diltiazem hydrochloride 90 MG Oral Tablet
        "831103",  # diltiazem hydrochloride 60 MG Oral Tablet
        "831359",  # 24 HR diltiazem hydrochloride 420 MG Extended Release Oral Capsule
        "833217",  # diltiazem hydrochloride 30 MG Oral Tablet
        "845488",  # ramipril 1.25 MG Oral Capsule
        "848131",  # amlodipine 10 MG / hydrochlorothiazide 12.5 MG / valsartan 160 MG Oral Tablet
        "848135",  # amlodipine 10 MG / hydrochlorothiazide 25 MG / valsartan 320 MG Oral Tablet
        "848140",  # amlodipine 5 MG / hydrochlorothiazide 12.5 MG / valsartan 160 MG Oral Tablet
        "848145",  # amlodipine 5 MG / hydrochlorothiazide 25 MG / valsartan 160 MG Oral Tablet
        "848151",  # amlodipine 10 MG / hydrochlorothiazide 25 MG / valsartan 160 MG Oral Tablet
        "854901",  # bisoprolol fumarate 10 MG Oral Tablet
        "854905",  # bisoprolol fumarate 5 MG Oral Tablet
        "854908",  # bisoprolol fumarate 10 MG / hydrochlorothiazide 6.25 MG Oral Tablet
        "854916",  # bisoprolol fumarate 2.5 MG / hydrochlorothiazide 6.25 MG Oral Tablet
        "854919",  # bisoprolol fumarate 5 MG / hydrochlorothiazide 6.25 MG Oral Tablet
        "854925",  # perindopril erbumine 8 MG Oral Tablet
        "854984",  # perindopril erbumine 2 MG Oral Tablet
        "854988",  # perindopril erbumine 4 MG Oral Tablet
        "856422",  # hydrochlorothiazide 25 MG / propranolol hydrochloride 40 MG Oral Tablet
        "856429",  # hydrochlorothiazide 25 MG / propranolol hydrochloride 80 MG Oral Tablet
        "856443",  # 1 ML propranolol hydrochloride 1 MG/ML Injection
        "856448",  # propranolol hydrochloride 10 MG Oral Tablet
        "856457",  # propranolol hydrochloride 20 MG Oral Tablet
        "856460",  # 24 HR propranolol hydrochloride 120 MG Extended Release Oral Capsule
        "856481",  # 24 HR propranolol hydrochloride 160 MG Extended Release Oral Capsule
        "856519",  # propranolol hydrochloride 40 MG Oral Tablet
        "856535",  # 24 HR propranolol hydrochloride 60 MG Extended Release Oral Capsule
        "856556",  # propranolol hydrochloride 60 MG Oral Tablet
        "856569",  # 24 HR propranolol hydrochloride 80 MG Extended Release Oral Capsule
        "856578",  # propranolol hydrochloride 80 MG Oral Tablet
        "856724",  # propranolol hydrochloride 4 MG/ML Oral Solution
        "856733",  # propranolol hydrochloride 8 MG/ML Oral Solution
        "857166",  # fosinopril sodium 10 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "857169",  # fosinopril sodium 10 MG Oral Tablet
        "857174",  # fosinopril sodium 20 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "857183",  # fosinopril sodium 20 MG Oral Tablet
        "857187",  # fosinopril sodium 40 MG Oral Tablet
        "858580",  # 12 HR nicardipine hydrochloride 45 MG Extended Release Oral Capsule
        "858587",  # 12 HR nicardipine hydrochloride 30 MG Extended Release Oral Capsule
        "858599",  # 200 ML nicardipine hydrochloride 0.1 MG/ML Injection
        "858603",  # 200 ML nicardipine hydrochloride 0.2 MG/ML Injection
        "858607",  # 10 ML nicardipine hydrochloride 2.5 MG/ML Injection
        "858613",  # nicardipine hydrochloride 20 MG Oral Capsule
        "858616",  # nicardipine hydrochloride 30 MG Oral Capsule
        "858804",  # enalapril maleate 2.5 MG Oral Tablet
        "858810",  # enalapril maleate 20 MG Oral Tablet
        "858813",  # enalapril maleate 5 MG Oral Tablet
        "858817",  # enalapril maleate 10 MG Oral Tablet
        "858824",  # enalapril maleate 5 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "858828",  # enalapril maleate 10 MG / hydrochlorothiazide 25 MG Oral Tablet
        "860510",  # 24 HR carvedilol phosphate 10 MG Extended Release Oral Capsule
        "860516",  # 24 HR carvedilol phosphate 20 MG Extended Release Oral Capsule
        "860522",  # 24 HR carvedilol phosphate 40 MG Extended Release Oral Capsule
        "860532",  # 24 HR carvedilol phosphate 80 MG Extended Release Oral Capsule
        "861402",  # phenoxybenzamine hydrochloride 10 MG Oral Capsule
        "862006",  # 24 HR guanfacine 1 MG Extended Release Oral Tablet
        "862013",  # 24 HR guanfacine 2 MG Extended Release Oral Tablet
        "862019",  # 24 HR guanfacine 3 MG Extended Release Oral Tablet
        "862025",  # 24 HR guanfacine 4 MG Extended Release Oral Tablet
        "866412",  # 24 HR metoprolol succinate 100 MG Extended Release Oral Tablet
        "866419",  # 24 HR metoprolol succinate 200 MG Extended Release Oral Tablet
        "866427",  # 24 HR metoprolol succinate 25 MG Extended Release Oral Tablet
        "866436",  # 24 HR metoprolol succinate 50 MG Extended Release Oral Tablet
        "866452",  # 24 HR hydrochlorothiazide 12.5 MG / metoprolol succinate 100 MG Extended Release Oral Tablet
        "866461",  # 24 HR hydrochlorothiazide 12.5 MG / metoprolol succinate 25 MG Extended Release Oral Tablet
        "866472",  # 24 HR hydrochlorothiazide 12.5 MG / metoprolol succinate 50 MG Extended Release Oral Tablet
        "866479",  # hydrochlorothiazide 25 MG / metoprolol tartrate 100 MG Oral Tablet
        "866482",  # hydrochlorothiazide 25 MG / metoprolol tartrate 50 MG Oral Tablet
        "866491",  # hydrochlorothiazide 50 MG / metoprolol tartrate 100 MG Oral Tablet
        "866508",  # 5 ML metoprolol tartrate 1 MG/ML Injection
        "866511",  # metoprolol tartrate 100 MG Oral Tablet
        "866514",  # metoprolol tartrate 50 MG Oral Tablet
        "866924",  # metoprolol tartrate 25 MG Oral Tablet
        "876514",  # amlodipine 10 MG / telmisartan 40 MG Oral Tablet
        "876519",  # amlodipine 10 MG / telmisartan 80 MG Oral Tablet
        "876524",  # amlodipine 5 MG / telmisartan 40 MG Oral Tablet
        "876529",  # amlodipine 5 MG / telmisartan 80 MG Oral Tablet
        "884173",  # clonidine hydrochloride 0.1 MG Oral Tablet
        "884185",  # clonidine hydrochloride 0.2 MG Oral Tablet
        "884189",  # clonidine hydrochloride 0.3 MG Oral Tablet
        "884192",  # chlorthalidone 15 MG / clonidine hydrochloride 0.1 MG Oral Tablet
        "884198",  # chlorthalidone 15 MG / clonidine hydrochloride 0.2 MG Oral Tablet
        "884203",  # chlorthalidone 15 MG / clonidine hydrochloride 0.3 MG Oral Tablet
        "884221",  # 10 ML clonidine hydrochloride 0.1 MG/ML Injection
        "884225",  # 10 ML clonidine hydrochloride 0.5 MG/ML Injection
        "896758",  # labetalol hydrochloride 100 MG Oral Tablet
        "896762",  # labetalol hydrochloride 200 MG Oral Tablet
        "896766",  # labetalol hydrochloride 300 MG Oral Tablet
        "896771",  # labetalol hydrochloride 5 MG/ML Injectable Solution
        "897584",  # 24 HR verapamil hydrochloride 100 MG Extended Release Oral Capsule
        "897590",  # 24 HR verapamil hydrochloride 200 MG Extended Release Oral Capsule
        "897596",  # 24 HR verapamil hydrochloride 300 MG Extended Release Oral Capsule
        "897612",  # 24 HR verapamil hydrochloride 120 MG Extended Release Oral Capsule
        "897618",  # 24 HR verapamil hydrochloride 180 MG Extended Release Oral Capsule
        "897624",  # 24 HR verapamil hydrochloride 240 MG Extended Release Oral Capsule
        "897630",  # 24 HR verapamil hydrochloride 360 MG Extended Release Oral Capsule
        "897640",  # verapamil hydrochloride 180 MG Extended Release Oral Tablet
        "897649",  # verapamil hydrochloride 240 MG Extended Release Oral Tablet
        "897659",  # verapamil hydrochloride 120 MG Extended Release Oral Tablet
        "897666",  # verapamil hydrochloride 120 MG Oral Tablet
        "897683",  # verapamil hydrochloride 80 MG Oral Tablet
        "897722",  # verapamil hydrochloride 40 MG Oral Tablet
        "897781",  # 24 HR trandolapril 1 MG / verapamil hydrochloride 240 MG Extended Release Oral Tablet
        "897783",  # 24 HR trandolapril 2 MG / verapamil hydrochloride 180 MG Extended Release Oral Tablet
        "897844",  # 24 HR trandolapril 2 MG / verapamil hydrochloride 240 MG Extended Release Oral Tablet
        "897853",  # 24 HR trandolapril 4 MG / verapamil hydrochloride 240 MG Extended Release Oral Tablet
        "898316",  # 4 ML verapamil hydrochloride 2.5 MG/ML Prefilled Syringe
        "898342",  # amlodipine 10 MG / benazepril hydrochloride 20 MG Oral Capsule
        "898346",  # amlodipine 10 MG / benazepril hydrochloride 40 MG Oral Capsule
        "898350",  # amlodipine 2.5 MG / benazepril hydrochloride 10 MG Oral Capsule
        "898353",  # amlodipine 5 MG / benazepril hydrochloride 10 MG Oral Capsule
        "898356",  # amlodipine 5 MG / benazepril hydrochloride 20 MG Oral Capsule
        "898359",  # amlodipine 5 MG / benazepril hydrochloride 40 MG Oral Capsule
        "898362",  # benazepril hydrochloride 10 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "898367",  # benazepril hydrochloride 20 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "898372",  # benazepril hydrochloride 20 MG / hydrochlorothiazide 25 MG Oral Tablet
        "898378",  # benazepril hydrochloride 5 MG / hydrochlorothiazide 6.25 MG Oral Tablet
        "898687",  # benazepril hydrochloride 10 MG Oral Tablet
        "898690",  # benazepril hydrochloride 20 MG Oral Tablet
        "898719",  # benazepril hydrochloride 40 MG Oral Tablet
        "898723",  # benazepril hydrochloride 5 MG Oral Tablet
        "904589",  # sotalol hydrochloride 240 MG Oral Tablet
        "904630",  # 10 ML sotalol hydrochloride 15 MG/ML Injection
        "905199",  # hydralazine hydrochloride 10 MG Oral Tablet
        "905222",  # hydralazine hydrochloride 100 MG Oral Tablet
        "905225",  # hydralazine hydrochloride 25 MG Oral Tablet
        "905377",  # hydralazine hydrochloride 37.5 MG / isosorbide dinitrate 20 MG Oral Tablet
        "905395",  # hydralazine hydrochloride 50 MG Oral Tablet
        "966571",  # 1 ML hydralazine hydrochloride 20 MG/ML Injection
        "977880",  # amiloride hydrochloride 5 MG Oral Tablet
        "977883",  # amiloride hydrochloride 5 MG / hydrochlorothiazide 50 MG Oral Tablet
        "979432",  # 100 ML esmolol hydrochloride 20 MG/ML Injection
        "979464",  # hydrochlorothiazide 12.5 MG / losartan potassium 100 MG Oral Tablet
        "979468",  # hydrochlorothiazide 12.5 MG / losartan potassium 50 MG Oral Tablet
        "979471",  # hydrochlorothiazide 25 MG / losartan potassium 100 MG Oral Tablet
        "979480",  # losartan potassium 100 MG Oral Tablet
        "979485",  # losartan potassium 25 MG Oral Tablet
        "979492",  # losartan potassium 50 MG Oral Tablet
        "998685",  # acebutolol 400 MG Oral Capsule
        "998689",  # acebutolol 200 MG Oral Capsule
        "999967",  # amlodipine 5 MG / hydrochlorothiazide 12.5 MG / olmesartan medoxomil 20 MG Oral Tablet
        "999986",  # amlodipine 10 MG / hydrochlorothiazide 12.5 MG / olmesartan medoxomil 40 MG Oral Tablet
        "999991",  # amlodipine 10 MG / hydrochlorothiazide 25 MG / olmesartan medoxomil 40 MG Oral Tablet
        "999996",  # amlodipine 5 MG / hydrochlorothiazide 12.5 MG / olmesartan medoxomil 40 MG Oral Tablet
        "1000001",  # amlodipine 5 MG / hydrochlorothiazide 25 MG / olmesartan medoxomil 40 MG Oral Tablet
        "1011710",  # aliskiren 150 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "1011713",  # aliskiren 150 MG / hydrochlorothiazide 25 MG Oral Tablet
        "1011736",  # aliskiren 150 MG Oral Tablet
        "1011739",  # aliskiren 300 MG Oral Tablet
        "1011750",  # aliskiren 300 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "1011753",  # aliskiren 300 MG / hydrochlorothiazide 25 MG Oral Tablet
        "1013930",  # 12 HR clonidine hydrochloride 0.1 MG Extended Release Oral Tablet
        "1013937",  # 12 HR clonidine hydrochloride 0.2 MG Extended Release Oral Tablet
        "1091646",  # azilsartan medoxomil 40 MG Oral Tablet
        "1091652",  # azilsartan medoxomil 80 MG Oral Tablet
        "1092566",  # {7 (24 HR guanfacine 1 MG Extended Release Oral Tablet) / 7 (24 HR guanfacine 2 MG Extended Release Oral Tablet) } Pack
        "1191185",  # penbutolol sulfate 20 MG Oral Tablet
        "1234256",  # 4 ML labetalol hydrochloride 5 MG/ML Cartridge
        "1235144",  # azilsartan medoxomil 40 MG / chlorthalidone 12.5 MG Oral Tablet
        "1235151",  # azilsartan medoxomil 40 MG / chlorthalidone 25 MG Oral Tablet
        "1297753",  # betaxolol hydrochloride 10 MG Oral Tablet
        "1297757",  # betaxolol hydrochloride 20 MG Oral Tablet
        "1299859",  # hydrochlorothiazide 12.5 MG / moexipril hydrochloride 15 MG Oral Tablet
        "1299871",  # hydrochlorothiazide 12.5 MG / moexipril hydrochloride 7.5 MG Oral Tablet
        "1299890",  # hydrochlorothiazide 25 MG / moexipril hydrochloride 15 MG Oral Tablet
        "1299896",  # moexipril hydrochloride 15 MG Oral Tablet
        "1299897",  # moexipril hydrochloride 7.5 MG Oral Tablet
        "1423767",  # nimodipine 3 MG/ML Oral Solution
        "1435624",  # enalapril maleate 1 MG/ML Oral Solution
        "1495058",  # propranolol hydrochloride 4.28 MG/ML Oral Solution
        "1593725",  # sotalol hydrochloride 5 MG/ML Oral Solution
        "1606347",  # metoprolol tartrate 37.5 MG Oral Tablet
        "1606349",  # metoprolol tartrate 75 MG Oral Tablet
        "1656340",  # sacubitril 24 MG / valsartan 26 MG Oral Tablet
        "1656349",  # sacubitril 49 MG / valsartan 51 MG Oral Tablet
        "1656354",  # sacubitril 97 MG / valsartan 103 MG Oral Tablet
        "1665057",  # 2 ML verapamil hydrochloride 2.5 MG/ML Injection
        "1665061",  # 4 ML verapamil hydrochloride 2.5 MG/ML Injection
        "1719286",  # 10 ML furosemide 10 MG/ML Injection
        "1719290",  # 2 ML furosemide 10 MG/ML Injection
        "1719291",  # 4 ML furosemide 10 MG/ML Injection
        "1729200",  # 1 ML enalaprilat 1.25 MG/ML Injection
        "1729205",  # 2 ML enalaprilat 1.25 MG/ML Injection
        "1736541",  # 250 ML esmolol hydrochloride 10 MG/ML Injection
        "1736546",  # 10 ML esmolol hydrochloride 10 MG/ML Injection
        "1790239",  # 50 ML clevidipine 0.5 MG/ML Injection
        "1790245",  # 100 ML clevidipine 0.5 MG/ML Injection
        "1790247",  # 250 ML clevidipine 0.5 MG/ML Injection
        "1791229",  # 5 ML diltiazem hydrochloride 5 MG/ML Injection
        "1791232",  # 10 ML diltiazem hydrochloride 5 MG/ML Injection
        "1791233",  # 25 ML diltiazem hydrochloride 5 MG/ML Injection
        "1791240",  # diltiazem hydrochloride 100 MG Injection
        "1798281",  # nebivolol 5 MG / valsartan 80 MG Oral Tablet
        "1806884",  # lisinopril 1 MG/ML Oral Solution
        "1923422",  # sotalol hydrochloride 120 MG Oral Tablet
        "1923424",  # sotalol hydrochloride 160 MG Oral Tablet
        "1923426",  # sotalol hydrochloride 80 MG Oral Tablet
        "1999031",  # 24 HR metoprolol succinate 100 MG Extended Release Oral Capsule
        "1999033",  # 24 HR metoprolol succinate 200 MG Extended Release Oral Capsule
        "1999035",  # 24 HR metoprolol succinate 25 MG Extended Release Oral Capsule
        "1999037",  # 24 HR metoprolol succinate 50 MG Extended Release Oral Capsule
    }


class AromataseInhibitors(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for aromatase inhibitors.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable aromatase inhibitors.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.

    ** Used in:** CMS249v4
    """

    VALUE_SET_NAME = "Aromatase Inhibitors"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1265"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "199224",  # anastrozole 1 MG Oral Tablet
        "200064",  # letrozole 2.5 MG Oral Tablet
        "310261",  # exemestane 25 MG Oral Tablet
    }


class GlucocorticoidsOralOnly(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for glucocorticoids.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable oral glucocorticoids.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and concepts that represent components, ingredients or non-oral medications.

    ** Used in:** CMS249v4
    """

    VALUE_SET_NAME = "Glucocorticoids (oral only)"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1266"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197577",  # dexamethasone 0.5 MG Oral Tablet
        "197579",  # dexamethasone 1 MG Oral Tablet
        "197580",  # dexamethasone 1.5 MG Oral Tablet
        "197581",  # dexamethasone 2 MG Oral Tablet
        "197582",  # dexamethasone 4 MG Oral Tablet
        "197583",  # dexamethasone 6 MG Oral Tablet
        "197783",  # hydrocortisone 20 MG Oral Tablet
        "197787",  # hydrocortisone 5 MG Oral Tablet
        "197969",  # methylprednisolone 2 MG Oral Tablet
        "197971",  # methylprednisolone 32 MG Oral Tablet
        "197973",  # methylprednisolone 8 MG Oral Tablet
        "198142",  # prednisolone 5 MG Oral Tablet
        "198144",  # prednisone 1 MG Oral Tablet
        "198145",  # prednisone 10 MG Oral Tablet
        "198146",  # prednisone 2.5 MG Oral Tablet
        "198148",  # prednisone 50 MG Oral Tablet
        "205301",  # prednisone 5 MG/ML Oral Solution
        "249066",  # prednisolone 5 MG/ML Oral Solution
        "259966",  # methylprednisolone 4 MG Oral Tablet
        "283077",  # prednisolone 3 MG/ML Oral Solution
        "309684",  # dexamethasone 1 MG/ML Oral Solution
        "309686",  # dexamethasone 0.1 MG/ML Oral Solution
        "312614",  # prednisolone 1 MG/ML Oral Solution
        "312615",  # prednisone 20 MG Oral Tablet
        "312617",  # prednisone 5 MG Oral Tablet
        "313979",  # fludrocortisone acetate 0.1 MG Oral Tablet
        "315187",  # prednisone 1 MG/ML Oral Solution
        "328161",  # methylprednisolone 16 MG Oral Tablet
        "343033",  # dexamethasone 0.75 MG Oral Tablet
        "429199",  # prednisolone 20 MG Oral Tablet
        "643123",  # prednisolone 10 MG Disintegrating Oral Tablet
        "643127",  # prednisolone 30 MG Disintegrating Oral Tablet
        "702306",  # prednisolone 4 MG/ML Oral Solution
        "759481",  # {51 (dexamethasone 1.5 MG Oral Tablet) } Pack
        "759697",  # {35 (dexamethasone 1.5 MG Oral Tablet) } Pack
        "762675",  # {21 (methylprednisolone 4 MG Oral Tablet) } Pack
        "763179",  # {48 (prednisone 5 MG Oral Tablet) } Pack
        "763181",  # {21 (prednisone 5 MG Oral Tablet) } Pack
        "763183",  # {48 (prednisone 10 MG Oral Tablet) } Pack
        "763185",  # {21 (prednisone 10 MG Oral Tablet) } Pack
        "793099",  # prednisolone 3 MG/ML Oral Suspension
        "794979",  # prednisolone 2 MG/ML Oral Solution
        "828248",  # cortisone acetate 25 MG Oral Tablet
        "846192",  # {21 (dexamethasone 1.5 MG Oral Tablet) } Pack
        "1005830",  # {48 (prednisolone 5 MG Oral Tablet) } Pack
        "1013114",  # {21 (prednisolone 5 MG Oral Tablet) } Pack
        "1085728",  # triamcinolone acetonide 0.001 MG/MG Oral Paste
        "1303125",  # prednisone 1 MG Delayed Release Oral Tablet
        "1303132",  # prednisone 2 MG Delayed Release Oral Tablet
        "1303135",  # prednisone 5 MG Delayed Release Oral Tablet
        "2121587",  # {39 (dexamethasone 1.5 MG Oral Tablet) } Pack
        "2261802",  # dexamethasone 20 MG Oral Tablet
    }


class AdolescentDepressionMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent medications used to treat depression in the child and adolescent population.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts for medications used for treatment and management of depression in children and adolescents.

    **Exclusion Criteria:** Excludes concepts that represent medications that are not recommended for children and adolescents and are solely used in the adult population.

    ** Used in:** CMS2v11
    """

    VALUE_SET_NAME = "Adolescent Depression Medications"
    OID = "2.16.840.1.113883.3.526.3.1567"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "200371",  # citalopram 20 MG Oral Tablet
        "248642",  # fluoxetine 20 MG Oral Tablet
        "283406",  # mirtazapine 15 MG Disintegrating Oral Tablet
        "283407",  # mirtazapine 30 MG Disintegrating Oral Tablet
        "283485",  # mirtazapine 45 MG Disintegrating Oral Tablet
        "283672",  # citalopram 10 MG Oral Tablet
        "309313",  # citalopram 2 MG/ML Oral Solution
        "309314",  # citalopram 40 MG Oral Tablet
        "310384",  # fluoxetine 10 MG Oral Capsule
        "310385",  # fluoxetine 20 MG Oral Capsule
        "310386",  # fluoxetine 4 MG/ML Oral Solution
        "311725",  # mirtazapine 15 MG Oral Tablet
        "311726",  # mirtazapine 45 MG Oral Tablet
        "312938",  # sertraline 100 MG Oral Tablet
        "312940",  # sertraline 25 MG Oral Tablet
        "312941",  # sertraline 50 MG Oral Tablet
        "313580",  # venlafaxine 100 MG Oral Tablet
        "313581",  # 24 HR venlafaxine 150 MG Extended Release Oral Capsule
        "313582",  # venlafaxine 25 MG Oral Tablet
        "313583",  # 24 HR venlafaxine 37.5 MG Extended Release Oral Capsule
        "313584",  # venlafaxine 37.5 MG Oral Tablet
        "313585",  # 24 HR venlafaxine 75 MG Extended Release Oral Capsule
        "313586",  # venlafaxine 75 MG Oral Tablet
        "313989",  # fluoxetine 40 MG Oral Capsule
        "313990",  # fluoxetine 10 MG Oral Tablet
        "313995",  # fluoxetine 90 MG Delayed Release Oral Capsule
        "314111",  # mirtazapine 30 MG Oral Tablet
        "314277",  # venlafaxine 50 MG Oral Tablet
        "349332",  # escitalopram 10 MG Oral Tablet
        "351249",  # escitalopram 5 MG Oral Tablet
        "351250",  # escitalopram 20 MG Oral Tablet
        "351285",  # escitalopram 1 MG/ML Oral Solution
        "476809",  # mirtazapine 7.5 MG Oral Tablet
        "596926",  # duloxetine 20 MG Delayed Release Oral Capsule
        "596930",  # duloxetine 30 MG Delayed Release Oral Capsule
        "596934",  # duloxetine 60 MG Delayed Release Oral Capsule
        "616402",  # duloxetine 40 MG Delayed Release Oral Capsule
        "808744",  # 24 HR venlafaxine 150 MG Extended Release Oral Tablet
        "808748",  # 24 HR venlafaxine 225 MG Extended Release Oral Tablet
        "808751",  # 24 HR venlafaxine 37.5 MG Extended Release Oral Tablet
        "808753",  # 24 HR venlafaxine 75 MG Extended Release Oral Tablet
        "861064",  # sertraline 20 MG/ML Oral Solution
        "1190110",  # fluoxetine 60 MG Oral Tablet
    }


class AdultDepressionMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent medications used to treat depression in the adult population.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts for medications used for treatment and management of depression in adults.

    **Exclusion Criteria:** Excludes concepts that represent medications that are not recommended for children and adolescents and are solely used in the adult population.

    ** Used in:** CMS2v11
    """

    VALUE_SET_NAME = "Adult Depression Medications"
    OID = "2.16.840.1.113883.3.526.3.1566"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "103968",  # lamotrigine 100 MG Disintegrating Oral Tablet
        "197363",  # amoxapine 100 MG Oral Tablet
        "197364",  # amoxapine 150 MG Oral Tablet
        "197365",  # amoxapine 25 MG Oral Tablet
        "197366",  # amoxapine 50 MG Oral Tablet
        "198045",  # nortriptyline 10 MG Oral Capsule
        "198046",  # nortriptyline 50 MG Oral Capsule
        "198047",  # nortriptyline 75 MG Oral Capsule
        "198427",  # lamotrigine 100 MG Oral Tablet
        "198428",  # lamotrigine 150 MG Oral Tablet
        "198429",  # lamotrigine 200 MG Oral Tablet
        "198430",  # lamotrigine 25 MG Disintegrating Oral Tablet
        "200371",  # citalopram 20 MG Oral Tablet
        "248642",  # fluoxetine 20 MG Oral Tablet
        "252478",  # lamotrigine 50 MG Disintegrating Oral Tablet
        "252479",  # lamotrigine 200 MG Disintegrating Oral Tablet
        "282401",  # lamotrigine 25 MG Oral Tablet
        "283406",  # mirtazapine 15 MG Disintegrating Oral Tablet
        "283407",  # mirtazapine 30 MG Disintegrating Oral Tablet
        "283485",  # mirtazapine 45 MG Disintegrating Oral Tablet
        "283672",  # citalopram 10 MG Oral Tablet
        "309313",  # citalopram 2 MG/ML Oral Solution
        "309314",  # citalopram 40 MG Oral Tablet
        "310384",  # fluoxetine 10 MG Oral Capsule
        "310385",  # fluoxetine 20 MG Oral Capsule
        "310386",  # fluoxetine 4 MG/ML Oral Solution
        "311264",  # lamotrigine 25 MG Chewable Tablet
        "311265",  # lamotrigine 5 MG Chewable Tablet
        "311725",  # mirtazapine 15 MG Oral Tablet
        "311726",  # mirtazapine 45 MG Oral Tablet
        "312036",  # nortriptyline 2 MG/ML Oral Solution
        "312242",  # paroxetine hydrochloride 2 MG/ML Oral Suspension
        "312347",  # phenelzine 15 MG Oral Tablet
        "312938",  # sertraline 100 MG Oral Tablet
        "312940",  # sertraline 25 MG Oral Tablet
        "312941",  # sertraline 50 MG Oral Tablet
        "313447",  # tranylcypromine 10 MG Oral Tablet
        "313496",  # trimipramine 100 MG Oral Capsule
        "313498",  # trimipramine 25 MG Oral Capsule
        "313499",  # trimipramine 50 MG Oral Capsule
        "313580",  # venlafaxine 100 MG Oral Tablet
        "313581",  # 24 HR venlafaxine 150 MG Extended Release Oral Capsule
        "313582",  # venlafaxine 25 MG Oral Tablet
        "313583",  # 24 HR venlafaxine 37.5 MG Extended Release Oral Capsule
        "313584",  # venlafaxine 37.5 MG Oral Tablet
        "313585",  # 24 HR venlafaxine 75 MG Extended Release Oral Capsule
        "313586",  # venlafaxine 75 MG Oral Tablet
        "313989",  # fluoxetine 40 MG Oral Capsule
        "313990",  # fluoxetine 10 MG Oral Tablet
        "313995",  # fluoxetine 90 MG Delayed Release Oral Capsule
        "314111",  # mirtazapine 30 MG Oral Tablet
        "314277",  # venlafaxine 50 MG Oral Tablet
        "317136",  # nortriptyline 25 MG Oral Capsule
        "349010",  # lamotrigine 2 MG Chewable Tablet
        "349332",  # escitalopram 10 MG Oral Tablet
        "351249",  # escitalopram 5 MG Oral Tablet
        "351250",  # escitalopram 20 MG Oral Tablet
        "351285",  # escitalopram 1 MG/ML Oral Solution
        "410503",  # 5-hydroxytryptophan 100 MG Oral Capsule
        "476809",  # mirtazapine 7.5 MG Oral Tablet
        "485514",  # 5-hydroxytryptophan 50 MG Oral Capsule
        "596926",  # duloxetine 20 MG Delayed Release Oral Capsule
        "596930",  # duloxetine 30 MG Delayed Release Oral Capsule
        "596934",  # duloxetine 60 MG Delayed Release Oral Capsule
        "616402",  # duloxetine 40 MG Delayed Release Oral Capsule
        "751139",  # {35 (lamotrigine 25 MG Oral Tablet) } Pack
        "751563",  # {7 (lamotrigine 100 MG Oral Tablet) / 42 (lamotrigine 25 MG Oral Tablet) } Pack
        "753451",  # {14 (lamotrigine 100 MG Oral Tablet) / 84 (lamotrigine 25 MG Oral Tablet) } Pack
        "790264",  # 24 HR desvenlafaxine 100 MG Extended Release Oral Tablet
        "790288",  # 24 HR desvenlafaxine 50 MG Extended Release Oral Tablet
        "808744",  # 24 HR venlafaxine 150 MG Extended Release Oral Tablet
        "808748",  # 24 HR venlafaxine 225 MG Extended Release Oral Tablet
        "808751",  # 24 HR venlafaxine 37.5 MG Extended Release Oral Tablet
        "808753",  # 24 HR venlafaxine 75 MG Extended Release Oral Tablet
        "835564",  # imipramine hydrochloride 25 MG Oral Tablet
        "835568",  # imipramine hydrochloride 50 MG Oral Tablet
        "835572",  # imipramine pamoate 75 MG Oral Capsule
        "835577",  # imipramine pamoate 150 MG Oral Capsule
        "835589",  # imipramine pamoate 125 MG Oral Capsule
        "835591",  # imipramine pamoate 100 MG Oral Capsule
        "835593",  # imipramine hydrochloride 10 MG Oral Tablet
        "850087",  # 24 HR lamotrigine 100 MG Extended Release Oral Tablet
        "850091",  # 24 HR lamotrigine 50 MG Extended Release Oral Tablet
        "851748",  # {21 (lamotrigine 25 MG Disintegrating Oral Tablet) / 7 (lamotrigine 50 MG Disintegrating Oral Tablet) } Pack
        "851750",  # {7 (lamotrigine 100 MG Disintegrating Oral Tablet) / 14 (lamotrigine 25 MG Disintegrating Oral Tablet) / 14 (lamotrigine 50 MG Disintegrating Oral Tablet) } Pack
        "851752",  # {14 (lamotrigine 100 MG Disintegrating Oral Tablet) / 42 (lamotrigine 50 MG Disintegrating Oral Tablet) } Pack
        "856364",  # trazodone hydrochloride 150 MG Oral Tablet
        "856369",  # trazodone hydrochloride 300 MG Oral Tablet
        "856373",  # trazodone hydrochloride 100 MG Oral Tablet
        "856377",  # trazodone hydrochloride 50 MG Oral Tablet
        "856706",  # amitriptyline hydrochloride 10 MG / perphenazine 2 MG Oral Tablet
        "856720",  # amitriptyline hydrochloride 10 MG / perphenazine 4 MG Oral Tablet
        "856762",  # amitriptyline hydrochloride 100 MG Oral Tablet
        "856769",  # amitriptyline hydrochloride 12.5 MG / chlordiazepoxide 5 MG Oral Tablet
        "856773",  # amitriptyline hydrochloride 150 MG Oral Tablet
        "856783",  # amitriptyline hydrochloride 10 MG Oral Tablet
        "856792",  # amitriptyline hydrochloride 25 MG / chlordiazepoxide 10 MG Oral Tablet
        "856797",  # amitriptyline hydrochloride 25 MG / perphenazine 2 MG Oral Tablet
        "856825",  # amitriptyline hydrochloride 25 MG / perphenazine 4 MG Oral Tablet
        "856834",  # amitriptyline hydrochloride 25 MG Oral Tablet
        "856840",  # amitriptyline hydrochloride 50 MG / perphenazine 4 MG Oral Tablet
        "856845",  # amitriptyline hydrochloride 50 MG Oral Tablet
        "856853",  # amitriptyline hydrochloride 75 MG Oral Tablet
        "857297",  # clomipramine hydrochloride 25 MG Oral Capsule
        "857301",  # clomipramine hydrochloride 50 MG Oral Capsule
        "857305",  # clomipramine hydrochloride 75 MG Oral Capsule
        "859186",  # selegiline hydrochloride 5 MG Oral Capsule
        "859190",  # selegiline hydrochloride 1.25 MG Disintegrating Oral Tablet
        "859193",  # selegiline hydrochloride 5 MG Oral Tablet
        "861064",  # sertraline 20 MG/ML Oral Solution
        "865206",  # 24 HR selegiline 0.25 MG/HR Transdermal System
        "865210",  # 24 HR selegiline 0.375 MG/HR Transdermal System
        "865214",  # 24 HR selegiline 0.5 MG/HR Transdermal System
        "898697",  # 24 HR trazodone hydrochloride 150 MG Extended Release Oral Tablet
        "898704",  # 24 HR trazodone hydrochloride 300 MG Extended Release Oral Tablet
        "900156",  # 24 HR lamotrigine 200 MG Extended Release Oral Tablet
        "900164",  # 24 HR lamotrigine 25 MG Extended Release Oral Tablet
        "900865",  # {14 (24 HR lamotrigine 100 MG Extended Release Oral Tablet) / 7 (24 HR lamotrigine 200 MG Extended Release Oral Tablet) / 14 (24 HR lamotrigine 50 MG Extended Release Oral Tablet) } Pack
        "900890",  # {7 (24 HR lamotrigine 100 MG Extended Release Oral Tablet) / 14 (24 HR lamotrigine 25 MG Extended Release Oral Tablet) / 14 (24 HR lamotrigine 50 MG Extended Release Oral Tablet) } Pack
        "900983",  # {21 (24 HR lamotrigine 25 MG Extended Release Oral Tablet) / 7 (24 HR lamotrigine 50 MG Extended Release Oral Tablet) } Pack
        "903873",  # 24 HR fluvoxamine maleate 100 MG Extended Release Oral Capsule
        "903879",  # 24 HR fluvoxamine maleate 150 MG Extended Release Oral Capsule
        "903884",  # fluvoxamine maleate 100 MG Oral Tablet
        "903887",  # fluvoxamine maleate 25 MG Oral Tablet
        "903891",  # fluvoxamine maleate 50 MG Oral Tablet
        "905168",  # protriptyline hydrochloride 10 MG Oral Tablet
        "905172",  # protriptyline hydrochloride 5 MG Oral Tablet
        "966787",  # doxepin 3 MG Oral Tablet
        "966793",  # doxepin 6 MG Oral Tablet
        "993503",  # 12 HR bupropion hydrochloride 100 MG Extended Release Oral Tablet
        "993518",  # 12 HR bupropion hydrochloride 150 MG Extended Release Oral Tablet
        "993536",  # 12 HR bupropion hydrochloride 200 MG Extended Release Oral Tablet
        "993541",  # 24 HR bupropion hydrochloride 150 MG Extended Release Oral Tablet
        "993550",  # 24 HR bupropion hydrobromide 174 MG Extended Release Oral Tablet
        "993557",  # 24 HR bupropion hydrochloride 300 MG Extended Release Oral Tablet
        "993567",  # 24 HR bupropion hydrobromide 348 MG Extended Release Oral Tablet
        "993681",  # 24 HR bupropion hydrobromide 522 MG Extended Release Oral Tablet
        "993687",  # bupropion hydrochloride 100 MG Oral Tablet
        "993691",  # bupropion hydrochloride 75 MG Oral Tablet
        "1000048",  # doxepin hydrochloride 10 MG Oral Capsule
        "1000054",  # doxepin hydrochloride 10 MG/ML Oral Solution
        "1000058",  # doxepin hydrochloride 100 MG Oral Capsule
        "1000064",  # doxepin hydrochloride 150 MG Oral Capsule
        "1000070",  # doxepin hydrochloride 25 MG Oral Capsule
        "1000076",  # doxepin hydrochloride 50 MG Oral Capsule
        "1000097",  # doxepin hydrochloride 75 MG Oral Capsule
        "1086772",  # vilazodone hydrochloride 10 MG Oral Tablet
        "1086778",  # vilazodone hydrochloride 20 MG Oral Tablet
        "1086784",  # vilazodone hydrochloride 40 MG Oral Tablet
        "1086789",  # {7 (vilazodone hydrochloride 10 MG Oral Tablet) / 7 (vilazodone hydrochloride 20 MG Oral Tablet) / 16 (vilazodone hydrochloride 40 MG Oral Tablet) } Pack
        "1098608",  # 24 HR lamotrigine 300 MG Extended Release Oral Tablet
        "1098649",  # nefazodone hydrochloride 100 MG Oral Tablet
        "1098666",  # nefazodone hydrochloride 150 MG Oral Tablet
        "1098670",  # nefazodone hydrochloride 200 MG Oral Tablet
        "1098674",  # nefazodone hydrochloride 250 MG Oral Tablet
        "1098678",  # nefazodone hydrochloride 50 MG Oral Tablet
        "1099288",  # desipramine hydrochloride 10 MG Oral Tablet
        "1099292",  # desipramine hydrochloride 100 MG Oral Tablet
        "1099296",  # desipramine hydrochloride 150 MG Oral Tablet
        "1099300",  # desipramine hydrochloride 25 MG Oral Tablet
        "1099304",  # desipramine hydrochloride 50 MG Oral Tablet
        "1099316",  # desipramine hydrochloride 75 MG Oral Tablet
        "1146690",  # 24 HR lamotrigine 250 MG Extended Release Oral Tablet
        "1190110",  # fluoxetine 60 MG Oral Tablet
        "1232585",  # 24 HR bupropion hydrochloride 450 MG Extended Release Oral Tablet
        "1298857",  # maprotiline hydrochloride 25 MG Oral Tablet
        "1298861",  # maprotiline hydrochloride 50 MG Oral Tablet
        "1298870",  # maprotiline hydrochloride 75 MG Oral Tablet
        "1738483",  # paroxetine hydrochloride 10 MG Oral Tablet
        "1738495",  # paroxetine hydrochloride 20 MG Oral Tablet
        "1738503",  # paroxetine hydrochloride 30 MG Oral Tablet
        "1738511",  # paroxetine hydrochloride 40 MG Oral Tablet
        "1738515",  # paroxetine mesylate 10 MG Oral Tablet
        "1738519",  # paroxetine mesylate 20 MG Oral Tablet
        "1738523",  # paroxetine mesylate 30 MG Oral Tablet
        "1738527",  # paroxetine mesylate 40 MG Oral Tablet
        "1738803",  # 24 HR paroxetine hydrochloride 12.5 MG Extended Release Oral Tablet
        "1738805",  # 24 HR paroxetine hydrochloride 25 MG Extended Release Oral Tablet
        "1738807",  # 24 HR paroxetine hydrochloride 37.5 MG Extended Release Oral Tablet
    }


class HighIntensityStatinTherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications that are high intensity statins as defined by the 2013 American College of Cardiology (ACC) and the American Heart Association (AHA) guideline.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for high intensity statin therapy as defined by the 2013 American College of Cardiology (ACC) and the American Heart Association (AHA) guideline.

    **Exclusion Criteria:** Excludes concepts that represent any other intensity of statin therapy.

    ** Used in:** CMS347v5
    """

    VALUE_SET_NAME = "High Intensity Statin Therapy"
    OID = "2.16.840.1.113883.3.526.3.1572"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "259255",  # atorvastatin 80 MG Oral Tablet
        "404011",  # amlodipine 5 MG / atorvastatin 80 MG Oral Tablet
        "404013",  # amlodipine 10 MG / atorvastatin 80 MG Oral Tablet
        "476351",  # ezetimibe 10 MG / simvastatin 80 MG Oral Tablet
        "597984",  # amlodipine 5 MG / atorvastatin 40 MG Oral Tablet
        "597990",  # amlodipine 10 MG / atorvastatin 40 MG Oral Tablet
        "597993",  # amlodipine 2.5 MG / atorvastatin 40 MG Oral Tablet
        "617311",  # atorvastatin 40 MG Oral Tablet
        "859419",  # rosuvastatin calcium 40 MG Oral Tablet
        "859751",  # rosuvastatin calcium 20 MG Oral Tablet
        "2167565",  # rosuvastatin 20 MG Oral Capsule
        "2167569",  # rosuvastatin 40 MG Oral Capsule
    }


class LowIntensityStatinTherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of low intensity statin medications as defined by the 2013 American College of Cardiology (ACC) and the American Heart Association (AHA) guideline.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for low intensity statin therapy as defined by the 2013 American College of Cardiology (ACC) and the American Heart Association (AHA) guideline.

    **Exclusion Criteria:** Excludes concepts that represent any other intensity of statin therapy.

    ** Used in:** CMS347v5
    """

    VALUE_SET_NAME = "Low Intensity Statin Therapy"
    OID = "2.16.840.1.113883.3.526.3.1574"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197903",  # lovastatin 10 MG Oral Tablet
        "197904",  # lovastatin 20 MG Oral Tablet
        "310404",  # fluvastatin 20 MG Oral Capsule
        "310405",  # fluvastatin 40 MG Oral Capsule
        "312962",  # simvastatin 5 MG Oral Tablet
        "314231",  # simvastatin 10 MG Oral Tablet
        "433849",  # 24 HR lovastatin 20 MG Extended Release Oral Tablet
        "476345",  # ezetimibe 10 MG / simvastatin 10 MG Oral Tablet
        "861643",  # pitavastatin calcium 1 MG Oral Tablet
        "904458",  # pravastatin sodium 10 MG Oral Tablet
        "904467",  # pravastatin sodium 20 MG Oral Tablet
        "1790679",  # simvastatin 4 MG/ML Oral Suspension
        "1944264",  # simvastatin 8 MG/ML Oral Suspension
        "2001254",  # pitavastatin magnesium 1 MG Oral Tablet
    }


class ModerateIntensityStatinTherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent moderate intensity statin medications as defined by the 2013 American College of Cardiology (ACC) and the American Heart Association (AHA) guideline.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for moderate intensity statin therapy as defined by the 2013 American College of Cardiology (ACC) and the American Heart Association (AHA) guideline.

    **Exclusion Criteria:** Excludes concepts that represent any other intensity of statin therapy.

    ** Used in:** CMS347v5
    """

    VALUE_SET_NAME = "Moderate Intensity Statin Therapy"
    OID = "2.16.840.1.113883.3.526.3.1575"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197905",  # lovastatin 40 MG Oral Tablet
        "198211",  # simvastatin 40 MG Oral Tablet
        "200345",  # simvastatin 80 MG Oral Tablet
        "310405",  # fluvastatin 40 MG Oral Capsule
        "312961",  # simvastatin 20 MG Oral Tablet
        "359731",  # 24 HR lovastatin 40 MG Extended Release Oral Tablet
        "359732",  # 24 HR lovastatin 60 MG Extended Release Oral Tablet
        "360507",  # 24 HR fluvastatin 80 MG Extended Release Oral Tablet
        "476349",  # ezetimibe 10 MG / simvastatin 20 MG Oral Tablet
        "476350",  # ezetimibe 10 MG / simvastatin 40 MG Oral Tablet
        "597967",  # amlodipine 10 MG / atorvastatin 20 MG Oral Tablet
        "597971",  # amlodipine 2.5 MG / atorvastatin 10 MG Oral Tablet
        "597974",  # amlodipine 2.5 MG / atorvastatin 20 MG Oral Tablet
        "597977",  # amlodipine 5 MG / atorvastatin 10 MG Oral Tablet
        "597980",  # amlodipine 5 MG / atorvastatin 20 MG Oral Tablet
        "597987",  # amlodipine 10 MG / atorvastatin 10 MG Oral Tablet
        "617310",  # atorvastatin 20 MG Oral Tablet
        "617312",  # atorvastatin 10 MG Oral Tablet
        "859424",  # rosuvastatin calcium 5 MG Oral Tablet
        "859747",  # rosuvastatin calcium 10 MG Oral Tablet
        "861648",  # pitavastatin calcium 2 MG Oral Tablet
        "861652",  # pitavastatin calcium 4 MG Oral Tablet
        "904475",  # pravastatin sodium 40 MG Oral Tablet
        "904481",  # pravastatin sodium 80 MG Oral Tablet
        "1790679",  # simvastatin 4 MG/ML Oral Suspension
        "1944264",  # simvastatin 8 MG/ML Oral Suspension
        "2001262",  # pitavastatin magnesium 2 MG Oral Tablet
        "2001266",  # pitavastatin magnesium 4 MG Oral Tablet
        "2167557",  # rosuvastatin 10 MG Oral Capsule
        "2167573",  # rosuvastatin 5 MG Oral Capsule
    }


class AndrogenDeprivationTherapyForUrologyCare(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications for androgen deprivation therapy as identified for urology care.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication that is an androgen deprivation therapy medication.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS645v5
    """

    VALUE_SET_NAME = "Androgen deprivation therapy for Urology Care"
    OID = "2.16.840.1.113762.1.4.1151.48"
    DEFINITION_VERSION = "20210202"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "310592",  # goserelin 3.6 MG Drug Implant
        "314008",  # goserelin 10.8 MG Drug Implant
        "545835",  # leuprolide acetate 5 MG/ML Injectable Solution
        "752884",  # 0.375 ML leuprolide acetate 120 MG/ML Prefilled Syringe
        "752889",  # 0.5 ML leuprolide acetate 60 MG/ML Prefilled Syringe
        "752894",  # 0.375 ML leuprolide acetate 60 MG/ML Prefilled Syringe
        "752899",  # 0.25 ML leuprolide acetate 30 MG/ML Prefilled Syringe
        "828749",  # degarelix 80 MG Injection
        "828751",  # degarelix 120 MG Injection
        "905053",  # triptorelin 22.5 MG Injection
        "905062",  # triptorelin 11.25 MG Injection
        "1115257",  # 1.5 ML leuprolide acetate 30 MG/ML Prefilled Syringe
        "1115447",  # 1 ML leuprolide acetate 11.25 MG/ML Prefilled Syringe
        "1115454",  # 1 ML leuprolide acetate 15 MG/ML Prefilled Syringe
        "1115457",  # 1 ML leuprolide acetate 3.75 MG/ML Prefilled Syringe
        "1115462",  # 1 ML leuprolide acetate 7.5 MG/ML Prefilled Syringe
        "1115467",  # 1.5 ML leuprolide acetate 15 MG/ML Prefilled Syringe
        "1115472",  # 1.5 ML leuprolide acetate 7.5 MG/ML Prefilled Syringe
        "1946519",  # 3-Month 1.5 ML leuprolide acetate 20 MG/ML Prefilled Syringe
        "1946521",  # 4-Month 1.5 ML leuprolide acetate 20 MG/ML Prefilled Syringe
    }


class BcgBacillusCalmetteGuerinForUrologyCare(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of medications of Bacillus Calmette Guerin (BCG) .

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that identify a medication of Bacillus Calmette Guerin (BCG) for intravesical use.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS646v2
    """

    VALUE_SET_NAME = "BCG Bacillus Calmette Guerin for Urology Care"
    OID = "2.16.840.1.113762.1.4.1151.52"
    DEFINITION_VERSION = "20200207"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "1653484",  # BCG, live, Tice strain 50 MG/ML Topical Suspension
        "1653579",  # BCG, live, Tice strain 50 MG Injection
    }


class ChemotherapyForAdvancedCancer(ValueSet):
    """
        **Clinical Focus:** This value set contains RxNORM codes associated with chemotherapy agents commonly used to treat patients with advanced stages of cancer.

        **Data Element Scope:** This would use the Medication QDM category.

        **Inclusion Criteria:** The following generic, prescribable chemotherapy agents are included in this value set:
    altretamine, arsenic trioxide, asparaginase, azacytidine, belinostat, bendamustine, bexarotene, bleomycin, busulfan, cabazitaxel, capecitabine, carboplatin, carmustine, chlorambucil, cisplatin, cladribine, clofarabine, cyclophosphamide, cytarabine, cytarabine liposome, dacarbazine, dactinomycin, daunorubicin, decitabine, docetaxel, doxorubicin, epirubicin, eribulin, estramustine, etoposide, floxuridine, fludarabine, fluorouracil, gemcitabine, hydroxyurea, idarubicin, ifosfamide, irinotecan, ixabepilone, lomustine, mechlorethamine, melphalan, mercaptopurine, methotrexate, mitomycin, mitotane, mitoxantrone, nelarabine, omacetaxine, oxaliplatin, paclitaxel, pegaspargase, pemetrexed, pentostatin, pralatrexate, procarbazine, ruxolitinib, streptozocin, temozolomide, teniposide, thioguanine, thiotepa, topotecan, trabectedin, vinblastine, vincristine.

        **Exclusion Criteria:** Chemotherapy agents not listed above are excluded from this value set, including brand name drugs or brand name drug packs.

        ** Used in:** CMS646v2
    """

    VALUE_SET_NAME = "Chemotherapy for Advanced Cancer"
    OID = "2.16.840.1.113883.3.7643.3.1048"
    DEFINITION_VERSION = "20190108"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "105585",  # methotrexate 2.5 MG Oral Tablet
        "105586",  # methotrexate 10 MG Oral Tablet
        "197323",  # altretamine 50 MG Oral Capsule
        "197422",  # busulfan 2 MG Oral Tablet
        "197462",  # chlorambucil 2 MG Oral Tablet
        "197687",  # etoposide 50 MG Oral Capsule
        "197797",  # hydroxyurea 500 MG Oral Capsule
        "197894",  # lomustine 10 MG Oral Capsule
        "197895",  # lomustine 100 MG Oral Capsule
        "197896",  # lomustine 40 MG Oral Capsule
        "197919",  # melphalan 2 MG Oral Tablet
        "197931",  # mercaptopurine 50 MG Oral Tablet
        "197988",  # mitotane 500 MG Oral Tablet
        "197989",  # mitoxantrone 2 MG/ML Injectable Solution
        "198269",  # thioguanine 40 MG Oral Tablet
        "199315",  # etoposide 100 MG Oral Capsule
        "200327",  # capecitabine 150 MG Oral Tablet
        "200328",  # capecitabine 500 MG Oral Tablet
        "200342",  # hydroxyurea 200 MG Oral Capsule
        "200343",  # hydroxyurea 300 MG Oral Capsule
        "200344",  # hydroxyurea 400 MG Oral Capsule
        "239177",  # fluorouracil 50 MG/ML Injectable Solution
        "239178",  # vinblastine sulfate 1 MG/ML Injectable Solution
        "239179",  # dactinomycin 0.5 MG Injection
        "239180",  # streptozocin 1000 MG Injection
        "240416",  # cytarabine 20 MG/ML Injectable Solution
        "240573",  # pentostatin 10 MG Injection
        "240754",  # 10 ML cladribine 1 MG/ML Injection
        "240906",  # 5 ML pegaspargase 750 UNT/ML Injection
        "249364",  # 20 ML cytarabine 100 MG/ML Injection
        "253113",  # 10 ML busulfan 6 MG/ML Injection
        "283475",  # hydroxyurea 1000 MG Oral Tablet
        "283510",  # methotrexate 15 MG Oral Tablet
        "283511",  # methotrexate 5 MG Oral Tablet
        "283671",  # methotrexate 7.5 MG Oral Tablet
        "308725",  # bexarotene 75 MG Oral Capsule
        "309012",  # carmustine 100 MG Injection
        "309013",  # carmustine 7.7 MG Drug Implant
        "309311",  # cisplatin 1 MG/ML Injectable Solution
        "309650",  # 4 ML daunorubicin 5 MG/ML Injection
        "310194",  # estramustine 140 MG Oral Capsule
        "310248",  # etoposide 20 MG/ML Injectable Solution
        "310351",  # floxuridine 500 MG Injection
        "311487",  # melphalan 50 MG Injection
        "311625",  # methotrexate 1000 MG Injection
        "312199",  # paclitaxel 6 MG/ML Injectable Solution
        "313209",  # temozolomide 20 MG Oral Capsule
        "313210",  # temozolomide 250 MG Oral Capsule
        "313211",  # temozolomide 5 MG Oral Capsule
        "313213",  # 5 ML teniposide 10 MG/ML Injection
        "314167",  # procarbazine 50 MG Oral Capsule
        "317160",  # temozolomide 100 MG Oral Capsule
        "485246",  # azacitidine 100 MG Injection
        "486419",  # 20 ML clofarabine 1 MG/ML Injection
        "583214",  # paclitaxel 100 MG Injection
        "597195",  # carboplatin 10 MG/ML Injectable Solution
        "603566",  # 50 ML nelarabine 5 MG/ML Injection
        "636631",  # decitabine 50 MG Injection
        "700883",  # temozolomide 140 MG Oral Capsule
        "700885",  # temozolomide 180 MG Oral Capsule
        "747193",  # topotecan 1 MG Oral Capsule
        "747195",  # topotecan 0.25 MG Oral Capsule
        "828706",  # fludarabine phosphate 10 MG Oral Tablet
        "829926",  # 10 ML arsenic trioxide 1 MG/ML Injection
        "968807",  # 5 ML cytarabine liposome 10 MG/ML Injection
        "992166",  # mechlorethamine hydrochloride 10 MG Injection
        "1001405",  # docetaxel 20 MG/ML Injectable Solution
        "1001433",  # 1.5 ML cabazitaxel 40 MG/ML Injection
        "1045456",  # 2 ML eribulin mesylate 0.5 MG/ML Injection
        "1093280",  # docetaxel 10 MG/ML Injectable Solution
        "1191138",  # doxorubicin hydrochloride 2 MG/ML Injectable Solution
        "1193331",  # ruxolitinib 10 MG Oral Tablet
        "1193339",  # ruxolitinib 5 MG Oral Tablet
        "1193343",  # ruxolitinib 15 MG Oral Tablet
        "1193347",  # ruxolitinib 20 MG Oral Tablet
        "1193351",  # ruxolitinib 25 MG Oral Tablet
        "1437968",  # cyclophosphamide 25 MG Oral Capsule
        "1437969",  # cyclophosphamide 50 MG Oral Capsule
        "1441402",  # 0.4 ML methotrexate 25 MG/ML Auto-Injector
        "1441411",  # 0.4 ML methotrexate 37.5 MG/ML Auto-Injector
        "1441416",  # 0.4 ML methotrexate 50 MG/ML Auto-Injector
        "1441422",  # 0.4 ML methotrexate 62.5 MG/ML Auto-Injector
        "1536484",  # mercaptopurine 20 MG/ML Oral Suspension
        "1541222",  # {24 (Methotrexate 2.5 MG Oral Tablet) } Pack
        "1543547",  # belinostat 500 MG Injection
        "1544378",  # 0.2 ML methotrexate 50 MG/ML Auto-Injector
        "1544385",  # 0.25 ML methotrexate 50 MG/ML Auto-Injector
        "1544387",  # 0.3 ML methotrexate 50 MG/ML Auto-Injector
        "1544389",  # 0.35 ML methotrexate 50 MG/ML Auto-Injector
        "1544395",  # 0.45 ML methotrexate 50 MG/ML Auto-Injector
        "1544397",  # 0.5 ML methotrexate 50 MG/ML Auto-Injector
        "1544399",  # 0.55 ML methotrexate 50 MG/ML Auto-Injector
        "1544401",  # 0.6 ML methotrexate 50 MG/ML Auto-Injector
        "1544403",  # 0.15 ML methotrexate 50 MG/ML Auto-Injector
        "1594757",  # 0.4 ML Methotrexate 18.8 MG/ML Auto-Injector
        "1655956",  # 40 ML methotrexate 25 MG/ML Injection
        "1655959",  # 10 ML methotrexate 25 MG/ML Injection
        "1655960",  # 2 ML methotrexate 25 MG/ML Injection
        "1655967",  # 4 ML methotrexate 25 MG/ML Injection
        "1655968",  # 8 ML methotrexate 25 MG/ML Injection
        "1660004",  # thiotepa 100 MG Injection
        "1660009",  # thiotepa 15 MG Injection
        "1718589",  # trabectedin 1 MG Injection
        "1719000",  # gemcitabine 200 MG Injection
        "1719003",  # gemcitabine 1000 MG Injection
        "1719005",  # gemcitabine 2000 MG Injection
        "1720735",  # lomustine 5 MG Oral Capsule
        "1720960",  # 26.3 ML gemcitabine 38 MG/ML Injection
        "1720975",  # 52.6 ML gemcitabine 38 MG/ML Injection
        "1720977",  # 5.26 ML gemcitabine 38 MG/ML Injection
        "1726097",  # bendamustine hydrochloride 25 MG/ML Injectable Solution
        "1726271",  # ixabepilone 45 MG Injection
        "1726276",  # ixabepilone 15 MG Injection
        "1726319",  # 2 ML irinotecan hydrochloride 20 MG/ML Injection
        "1726324",  # 5 ML irinotecan hydrochloride 20 MG/ML Injection
        "1726333",  # 15 ML irinotecan hydrochloride 20 MG/ML Injection
        "1726492",  # 25 ML irinotecan hydrochloride 20 MG/ML Injection
        "1726673",  # bleomycin 15 UNT Injection
        "1726676",  # bleomycin 30 UNT Injection
        "1728072",  # pemetrexed 500 MG Injection
        "1728077",  # pemetrexed 100 MG Injection
        "1731338",  # dacarbazine 200 MG Injection
        "1731340",  # dacarbazine 100 MG Injection
        "1731355",  # 5 ML cytarabine 20 MG/ML Injection
        "1732182",  # 25 ML epirubicin hydrochloride 2 MG/ML Injection
        "1732186",  # 100 ML epirubicin hydrochloride 2 MG/ML Injection
        "1734340",  # etoposide 100 MG Injection
        "1734917",  # cyclophosphamide 500 MG Injection
        "1734919",  # cyclophosphamide 1000 MG Injection
        "1734921",  # cyclophosphamide 2000 MG Injection
        "1736776",  # 10 ML oxaliplatin 5 MG/ML Injection
        "1736781",  # 20 ML oxaliplatin 5 MG/ML Injection
        "1736784",  # oxaliplatin 50 MG Injection
        "1736786",  # oxaliplatin 100 MG Injection
        "1736854",  # cisplatin 50 MG Injection
        "1740864",  # fludarabine phosphate 50 MG Injection
        "1740865",  # 2 ML fludarabine phosphate 25 MG/ML Injection
        "1740894",  # mitomycin 5 MG Injection
        "1740898",  # mitomycin 40 MG Injection
        "1740900",  # mitomycin 20 MG Injection
        "1747179",  # 0.4 ML methotrexate 31.3 MG/ML Auto-Injector
        "1747185",  # 0.4 ML methotrexate 43.8 MG/ML Auto-Injector
        "1747192",  # 0.4 ML methotrexate 56.3 MG/ML Auto-Injector
        "1790095",  # doxorubicin hydrochloride 50 MG Injection
        "1790097",  # 5 ML doxorubicin hydrochloride 2 MG/ML Injection
        "1790099",  # 10 ML doxorubicin hydrochloride 2 MG/ML Injection
        "1790100",  # 25 ML doxorubicin hydrochloride 2 MG/ML Injection
        "1790103",  # doxorubicin hydrochloride 10 MG Injection
        "1791493",  # 20 ML idarubicin hydrochloride 1 MG/ML Injection
        "1791498",  # 10 ML idarubicin hydrochloride 1 MG/ML Injection
        "1791500",  # 5 ML idarubicin hydrochloride 1 MG/ML Injection
        "1791588",  # ifosfamide 3000 MG Injection
        "1791593",  # ifosfamide 1000 MG Injection
        "1791597",  # 60 ML ifosfamide 50 MG/ML Injection
        "1791599",  # 20 ML ifosfamide 50 MG/ML Injection
        "1791701",  # 10 ML fluorouracil 50 MG/ML Injection
        "1791736",  # 20 ML fluorouracil 50 MG/ML Injection
        "1796419",  # 1 ML pralatrexate 20 MG/ML Injection
        "1796424",  # 2 ML pralatrexate 20 MG/ML Injection
        "1797528",  # 40 ML oxaliplatin 5 MG/ML Injection
        "1799416",  # topotecan 4 MG Injection
        "1799424",  # 4 ML topotecan 1 MG/ML Injection
        "1805001",  # bendamustine hydrochloride 100 MG Injection
        "1805007",  # bendamustine hydrochloride 25 MG Injection
        "1860480",  # 1 ML docetaxel 20 MG/ML Injection
        "1860485",  # 4 ML docetaxel 20 MG/ML Injection
        "1860619",  # 2 ML docetaxel 10 MG/ML Injection
        "1861411",  # 8 ML docetaxel 20 MG/ML Injection
        "1863343",  # 1 ML vincristine sulfate 1 MG/ML Injection
        "1863354",  # 2 ML vincristine sulfate 1 MG/ML Injection
        "1870937",  # 0.5 ML docetaxel 40 MG/ML Injection
        "1872062",  # doxorubicin hydrochloride 20 MG Injection
        "1918045",  # 10 ML docetaxel 20 MG/ML Injection
        "1921592",  # methotrexate 2.5 MG/ML Oral Solution
        "1942743",  # cytarabine liposome 100 MG / daunorubicin liposomal 44 MG Injection
        "1946772",  # methotrexate 25 MG/ML Injectable Solution
        "1992545",  # 6 ML arsenic trioxide 2 MG/ML Injection
        "1998783",  # gemcitabine 100 MG/ML Injectable Solution
        "1999308",  # hydroxyurea 100 MG Oral Tablet
        "2002002",  # 10 ML daunorubicin 5 MG/ML Injection
    }


class ImmunosuppressiveDrugsForUrologyCare(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is represent concepts of medications for immunosuppressive drugs .

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that identify a medication for immunosuppressive drug therapy.

    **Exclusion Criteria:** Excludes concepts that identify a medication not used for immunosuppression.

    ** Used in:** CMS646v2
    """

    VALUE_SET_NAME = "Immunosuppressive Drugs for Urology Care"
    OID = "2.16.840.1.113762.1.4.1151.32"
    DEFINITION_VERSION = "20210202"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197388",  # azathioprine 50 MG Oral Tablet
        "197553",  # cyclosporine 25 MG Oral Capsule
        "198142",  # prednisolone 5 MG Oral Tablet
        "198144",  # prednisone 1 MG Oral Tablet
        "198145",  # prednisone 10 MG Oral Tablet
        "198146",  # prednisone 2.5 MG Oral Tablet
        "198148",  # prednisone 50 MG Oral Tablet
        "198377",  # tacrolimus 1 MG Oral Capsule
        "198378",  # tacrolimus 5 MG Oral Capsule
        "198379",  # 1 ML tacrolimus 5 MG/ML Injection
        "199058",  # mycophenolate mofetil 250 MG Oral Capsule
        "199310",  # azathioprine 25 MG Oral Tablet
        "200060",  # mycophenolate mofetil 500 MG Oral Tablet
        "205175",  # 5 ML cyclosporine 50 MG/ML Injection
        "205284",  # leflunomide 10 MG Oral Tablet
        "205285",  # leflunomide 20 MG Oral Tablet
        "205286",  # leflunomide 100 MG Oral Tablet
        "205301",  # prednisone 5 MG/ML Oral Solution
        "239983",  # azathioprine 100 MG Injection
        "241834",  # cyclosporine, modified 100 MG Oral Capsule
        "249066",  # prednisolone 5 MG/ML Oral Solution
        "253014",  # etanercept 25 MG/ML Injectable Solution
        "283077",  # prednisolone 3 MG/ML Oral Solution
        "309632",  # cyclosporine 100 MG/ML Oral Solution
        "310994",  # infliximab 100 MG Injection
        "311880",  # mycophenolate mofetil 200 MG/ML Oral Suspension
        "312614",  # prednisolone 1 MG/ML Oral Solution
        "312615",  # prednisone 20 MG Oral Tablet
        "312617",  # prednisone 5 MG Oral Tablet
        "314230",  # sirolimus 1 MG/ML Oral Solution
        "315187",  # prednisone 1 MG/ML Oral Solution
        "328160",  # cyclosporine 100 MG Oral Capsule
        "342977",  # etanercept 25 MG/ML
        "349208",  # sirolimus 1 MG Oral Tablet
        "359228",  # azathioprine 100 MG Oral Tablet
        "359229",  # azathioprine 75 MG Oral Tablet
        "360110",  # sirolimus 2 MG Oral Tablet
        "429199",  # prednisolone 20 MG Oral Tablet
        "477484",  # 15 ML natalizumab 20 MG/ML Injection
        "485020",  # mycophenolic acid 180 MG Delayed Release Oral Tablet
        "485023",  # mycophenolic acid 360 MG Delayed Release Oral Tablet
        "582670",  # etanercept 50 MG/ML
        "616015",  # abatacept 250 MG Injection
        "643123",  # prednisolone 10 MG Disintegrating Oral Tablet
        "643125",  # prednisolone 15 MG Disintegrating Oral Tablet
        "643127",  # prednisolone 30 MG Disintegrating Oral Tablet
        "702306",  # prednisolone 4 MG/ML Oral Solution
        "727703",  # 0.8 ML adalimumab 50 MG/ML Prefilled Syringe
        "727711",  # 0.67 ML anakinra 149 MG/ML Prefilled Syringe
        "727757",  # 1 ML etanercept 50 MG/ML Prefilled Syringe
        "763564",  # 0.4 ML adalimumab 50 MG/ML Prefilled Syringe
        "793099",  # prednisolone 3 MG/ML Oral Suspension
        "794979",  # prednisolone 2 MG/ML Oral Solution
        "795081",  # certolizumab pegol 200 MG Injection
        "809158",  # 0.5 ML etanercept 50 MG/ML Prefilled Syringe
        "835886",  # cyclosporine, modified 100 MG/ML Oral Solution
        "835894",  # cyclosporine, modified 25 MG Oral Capsule
        "835925",  # cyclosporine, modified 50 MG Oral Capsule
        "845507",  # everolimus 10 MG Oral Tablet
        "845515",  # everolimus 5 MG Oral Tablet
        "848160",  # 0.5 ML golimumab 100 MG/ML Prefilled Syringe
        "849597",  # 1 ML certolizumab pegol 200 MG/ML Prefilled Syringe
        "853350",  # 0.5 ML ustekinumab 90 MG/ML Prefilled Syringe
        "853355",  # 1 ML ustekinumab 90 MG/ML Prefilled Syringe
        "905158",  # sirolimus 0.5 MG Oral Tablet
        "977427",  # everolimus 0.25 MG Oral Tablet
        "977434",  # everolimus 0.5 MG Oral Tablet
        "977438",  # everolimus 0.75 MG Oral Tablet
        "998189",  # everolimus 2.5 MG Oral Tablet
        "1119400",  # everolimus 7.5 MG Oral Tablet
        "1145929",  # 1 ML abatacept 125 MG/ML Prefilled Syringe
        "1244214",  # budesonide 3 MG Delayed Release Oral Capsule
        "1303125",  # prednisone 1 MG Delayed Release Oral Tablet
        "1303132",  # prednisone 2 MG Delayed Release Oral Tablet
        "1303135",  # prednisone 5 MG Delayed Release Oral Tablet
        "1308428",  # everolimus 2 MG Tablet for Oral Suspension
        "1308430",  # everolimus 3 MG Tablet for Oral Suspension
        "1308432",  # everolimus 5 MG Tablet for Oral Suspension
        "1366550",  # 24 HR budesonide 9 MG Extended Release Oral Tablet
        "1431642",  # 4 ML golimumab 12.5 MG/ML Injection
        "1431971",  # 24 HR tacrolimus 0.5 MG Extended Release Oral Capsule
        "1431980",  # 24 HR tacrolimus 1 MG Extended Release Oral Capsule
        "1431985",  # 24 HR tacrolimus 5 MG Extended Release Oral Capsule
        "1441527",  # 0.9 ML tocilizumab 180 MG/ML Prefilled Syringe
        "1482813",  # 1 ML golimumab 100 MG/ML Prefilled Syringe
        "1538137",  # vedolizumab 300 MG Injection
        "1551887",  # 0.2 ML adalimumab 50 MG/ML Prefilled Syringe
        "1599792",  # 1 ML secukinumab 150 MG/ML Prefilled Syringe
        "1653142",  # 0.5 ML golimumab 100 MG/ML Auto-Injector
        "1653165",  # 1 ML golimumab 100 MG/ML Auto-Injector
        "1653223",  # 1 ML etanercept 50 MG/ML Auto-Injector
        "1653241",  # 1 ML secukinumab 150 MG/ML Auto-Injector
        "1654077",  # 0.5 ML ustekinumab 90 MG/ML Injection
        "1655726",  # 0.8 ML adalimumab 50 MG/ML Auto-Injector
        "1656643",  # basiliximab 10 MG Injection
        "1656648",  # basiliximab 20 MG Injection
        "1657862",  # 10 ML rituximab 10 MG/ML Injection
        "1657867",  # 50 ML rituximab 10 MG/ML Injection
        "1657974",  # 4 ML tocilizumab 20 MG/ML Injection
        "1657979",  # 10 ML tocilizumab 20 MG/ML Injection
        "1657981",  # 20 ML tocilizumab 20 MG/ML Injection
        "1664434",  # 24 HR tacrolimus 4 MG Extended Release Oral Tablet
        "1664456",  # 24 HR tacrolimus 0.75 MG Extended Release Oral Tablet
        "1664461",  # 24 HR tacrolimus 1 MG Extended Release Oral Tablet
        "1726844",  # 0.4 ML adalimumab 100 MG/ML Prefilled Syringe
        "1741046",  # 24 HR tofacitinib 11 MG Extended Release Oral Tablet
        "1745103",  # 1 ML ixekizumab 80 MG/ML Auto-Injector
        "1745112",  # 1 ML ixekizumab 80 MG/ML Prefilled Syringe
        "1790541",  # infliximab-dyyb 100 MG Injection
        "1799228",  # 1 ML abatacept 125 MG/ML Auto-Injector
        "1811255",  # 26 ML ustekinumab 5 MG/ML Injection
        "1855523",  # 0.8 ML adalimumab 100 MG/ML Prefilled Syringe
        "1872979",  # 0.4 ML adalimumab 100 MG/ML Auto-Injector
        "1921009",  # 0.1 ML adalimumab 100 MG/ML Prefilled Syringe
        "1921016",  # 0.2 ML adalimumab 100 MG/ML Prefilled Syringe
        "1921238",  # 0.8 ML adalimumab 100 MG/ML Auto-Injector
        "1925254",  # 0.4 ML abatacept 125 MG/ML Prefilled Syringe
        "1925256",  # 0.7 ML abatacept 125 MG/ML Prefilled Syringe
        "1927285",  # infliximab-abda 100 MG Injection
        "1927893",  # 13.4 ML hyaluronidase, human recombinant 2000 UNT/ML / rituximab 120 MG/ML Injection
        "2048566",  # tofacitinib 10 MG Oral Tablet
        "2052605",  # tacrolimus 0.2 MG Granules for Oral Suspension
        "2052703",  # tacrolimus 1 MG Granules for Oral Suspension
        "2056895",  # everolimus 1 MG Oral Tablet
        "2105834",  # 50 ML rituximab-abbs 10 MG/ML Injection
        "2182338",  # 1 ML etanercept 50 MG/ML Cartridge
    }


class MedicationsForAboveNormalBmi(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications prescribed for weight loss to patients with an above normal body mass index (BMI) measurement.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for weight loss in patients with an above normal body mass index (BMI) measurement.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS69v10
    """

    VALUE_SET_NAME = "Medications for Above Normal BMI"
    OID = "2.16.840.1.113883.3.526.3.1561"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "314153",  # orlistat 120 MG Oral Capsule
        "692876",  # orlistat 60 MG Oral Capsule
        "803348",  # phentermine hydrochloride 37.5 MG Oral Capsule
        "803353",  # phentermine hydrochloride 37.5 MG Oral Tablet
        "826131",  # phentermine hydrochloride 18.8 MG Oral Capsule
        "826919",  # phentermine hydrochloride 8 MG Oral Tablet
        "900038",  # phentermine hydrochloride 30 MG Oral Capsule
        "968766",  # phentermine hydrochloride 15 MG Oral Capsule
        "978654",  # diethylpropion hydrochloride 25 MG Oral Tablet
        "978668",  # 24 HR diethylpropion hydrochloride 75 MG Extended Release Oral Tablet
        "1112982",  # phentermine hydrochloride 15 MG Disintegrating Oral Tablet
        "1112987",  # phentermine hydrochloride 30 MG Disintegrating Oral Tablet
        "1249083",  # phentermine hydrochloride 37.5 MG Disintegrating Oral Tablet
        "1302827",  # 24 HR phentermine 7.5 MG / topiramate 46 MG Extended Release Oral Capsule
        "1302839",  # 24 HR phentermine 3.75 MG / topiramate 23 MG Extended Release Oral Capsule
        "1302850",  # 24 HR phentermine 15 MG / topiramate 92 MG Extended Release Oral Capsule
        "1313059",  # 24 HR phentermine 11.25 MG / topiramate 69 MG Extended Release Oral Capsule
    }


class MedicationsForBelowNormalBmi(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications prescribed for weight gain to patients with a below normal body mass index (BMI) measurement.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for weight gain in patients with a below normal body mass index (BMI) measurement.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS69v10
    """

    VALUE_SET_NAME = "Medications for Below Normal BMI"
    OID = "2.16.840.1.113883.3.526.3.1562"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    RXNORM = {
        "197634",  # dronabinol 10 MG Oral Capsule
        "197635",  # dronabinol 2.5 MG Oral Capsule
        "197636",  # dronabinol 5 MG Oral Capsule
        "577154",  # megestrol acetate 125 MG/ML Oral Suspension
        "860215",  # megestrol acetate 20 MG Oral Tablet
        "860221",  # megestrol acetate 40 MG Oral Tablet
        "860225",  # megestrol acetate 40 MG/ML Oral Suspension
    }


__exports__ = get_overrides(locals().copy())
