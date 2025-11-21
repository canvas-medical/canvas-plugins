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

class AnticoagulantsForAllIndications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for anticoagulant medications

    **Data Element Scope:** This value set may use a model element related to Medication

    **Inclusion Criteria:** Includes concepts that represent anticoagulant medications

    **Exclusion Criteria:** None
    """

    VALUE_SET_NAME = "Anticoagulants for All Indications"
    OID = "2.16.840.1.113762.1.4.1248.22"
    DEFINITION_VERSION = "20220608"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1037045",  # dabigatran etexilate 150 MG Oral Capsule
        "1037179",  # dabigatran etexilate 75 MG Oral Capsule
        "1114198",  # rivaroxaban 10 MG Oral Tablet
        "1232082",  # rivaroxaban 15 MG Oral Tablet
        "1232086",  # rivaroxaban 20 MG Oral Tablet
        "1361574",  # heparin sodium, porcine 20000 UNT/ML Injectable Solution
        "1361615",  # heparin sodium, porcine 5000 UNT/ML Injectable Solution
        "1361853",  # 0.5 ML heparin sodium, porcine 10000 UNT/ML Cartridge
        "1362831",  # heparin sodium, porcine 10000 UNT/ML Injectable Solution
        "1364435",  # apixaban 2.5 MG Oral Tablet
        "1364445",  # apixaban 5 MG Oral Tablet
        "1549682",  # {42 (rivaroxaban 15 MG Oral Tablet) / 9 (rivaroxaban 20 MG Oral Tablet) } Pack
        "1599543",  # edoxaban 15 MG Oral Tablet
        "1599551",  # edoxaban 30 MG Oral Tablet
        "1599555",  # edoxaban 60 MG Oral Tablet
        "1658634",  # 0.5 ML heparin sodium, porcine 10000 UNT/ML Injection
        "1658637",  # 1 ML heparin sodium, porcine 10000 UNT/ML Injection
        "1658647",  # 2 ML heparin sodium, porcine 1000 UNT/ML Injection
        "1658690",  # 1000 ML heparin sodium, porcine 2 UNT/ML Injection
        "1658692",  # 500 ML heparin sodium, porcine 2 UNT/ML Injection
        "1658717",  # 250 ML heparin sodium, porcine 100 UNT/ML Injection
        "1659195",  # 500 ML heparin sodium, porcine 50 UNT/ML Injection
        "1659197",  # 250 ML heparin sodium, porcine 50 UNT/ML Injection
        "1659260",  # 1 ML heparin sodium, porcine 5000 UNT/ML Cartridge
        "1659263",  # 1 ML heparin sodium, porcine 5000 UNT/ML Injection
        "1723476",  # dabigatran etexilate 110 MG Oral Capsule
        "1798389",  # 1 ML heparin sodium, porcine 5000 UNT/ML Prefilled Syringe
        "1992427",  # {74 (apixaban 5 MG Oral Tablet) } Pack
        "1997015",  # 50 ML bivalirudin 5 MG/ML Injection
        "1997017",  # 100 ML bivalirudin 5 MG/ML Injection
        "2121591",  # 0.5 ML heparin sodium, porcine 10000 UNT/ML Prefilled Syringe
        "308351",  # 2.5 ML argatroban 100 MG/ML Injection
        "308769",  # bivalirudin 250 MG Injection
        "402248",  # desirudin 15 MG Injection
        "854228",  # 0.3 ML enoxaparin sodium 100 MG/ML Prefilled Syringe
        "854235",  # 0.4 ML enoxaparin sodium 100 MG/ML Prefilled Syringe
        "854238",  # 0.6 ML enoxaparin sodium 100 MG/ML Prefilled Syringe
        "854241",  # 0.8 ML enoxaparin sodium 100 MG/ML Prefilled Syringe
        "854245",  # 0.8 ML enoxaparin sodium 150 MG/ML Prefilled Syringe
        "854248",  # 1 ML enoxaparin sodium 100 MG/ML Prefilled Syringe
        "854252",  # 1 ML enoxaparin sodium 150 MG/ML Prefilled Syringe
        "854255",  # enoxaparin sodium 100 MG/ML Injectable Solution
        "855288",  # warfarin sodium 1 MG Oral Tablet
        "855296",  # warfarin sodium 10 MG Oral Tablet
        "855302",  # warfarin sodium 2 MG Oral Tablet
        "855312",  # warfarin sodium 2.5 MG Oral Tablet
        "855318",  # warfarin sodium 3 MG Oral Tablet
        "855324",  # warfarin sodium 4 MG Oral Tablet
        "855332",  # warfarin sodium 5 MG Oral Tablet
        "855338",  # warfarin sodium 6 MG Oral Tablet
        "855344",  # warfarin sodium 7.5 MG Oral Tablet
        "861356",  # 0.8 ML fondaparinux sodium 12.5 MG/ML Prefilled Syringe
        "861360",  # 0.5 ML fondaparinux sodium 5 MG/ML Prefilled Syringe
        "861363",  # 0.4 ML fondaparinux sodium 12.5 MG/ML Prefilled Syringe
        "861365",  # 0.6 ML fondaparinux sodium 12.5 MG/ML Prefilled Syringe
        "978725",  # 0.2 ML dalteparin sodium 12500 UNT/ML Prefilled Syringe
        "978733",  # 0.2 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978736",  # 0.3 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978740",  # 0.5 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978744",  # 0.6 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978746",  # 0.72 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978755",  # 1 ML dalteparin sodium 10000 UNT/ML Prefilled Syringe
        "978759",  # dalteparin sodium 10000 UNT/ML Injectable Solution
        "978777",  # dalteparin sodium 25000 UNT/ML Injectable Solution
    }

class Antidepressants(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for antidepressants

    **Data Element Scope:** This value set may use a model element related to Medication

    **Inclusion Criteria:** Includes concepts that represent antidepressant medications including tricyclics, tetracyclics, SNRIs, and SSRAs in generic, prescribable forms.

    **Exclusion Criteria:** N/A
    """

    VALUE_SET_NAME = "Antidepressants"
    OID = "2.16.840.1.113762.1.4.1248.163"
    DEFINITION_VERSION = "20240119"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1000048",  # doxepin 10 MG Oral Capsule
        "1000054",  # doxepin 10 MG/ML Oral Solution
        "1000058",  # doxepin 100 MG Oral Capsule
        "1000064",  # doxepin 150 MG Oral Capsule
        "1000070",  # doxepin 25 MG Oral Capsule
        "1000076",  # doxepin 50 MG Oral Capsule
        "1000097",  # doxepin 75 MG Oral Capsule
        "1086772",  # vilazodone hydrochloride 10 MG Oral Tablet
        "1086778",  # vilazodone hydrochloride 20 MG Oral Tablet
        "1086784",  # vilazodone hydrochloride 40 MG Oral Tablet
        "1099288",  # desipramine hydrochloride 10 MG Oral Tablet
        "1099292",  # desipramine hydrochloride 100 MG Oral Tablet
        "1099296",  # desipramine hydrochloride 150 MG Oral Tablet
        "1099300",  # desipramine hydrochloride 25 MG Oral Tablet
        "1099304",  # desipramine hydrochloride 50 MG Oral Tablet
        "1099316",  # desipramine hydrochloride 75 MG Oral Tablet
        "1190110",  # fluoxetine 60 MG Oral Tablet
        "1298861",  # maprotiline hydrochloride 50 MG Oral Tablet
        "1298870",  # maprotiline hydrochloride 75 MG Oral Tablet
        "1430122",  # paroxetine mesylate 7.5 MG Oral Capsule
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
        "1874553",  # 24 HR desvenlafaxine succinate 100 MG Extended Release Oral Tablet
        "1874559",  # 24 HR desvenlafaxine succinate 50 MG Extended Release Oral Tablet
        "197363",  # amoxapine 100 MG Oral Tablet
        "197364",  # amoxapine 150 MG Oral Tablet
        "197365",  # amoxapine 25 MG Oral Tablet
        "197366",  # amoxapine 50 MG Oral Tablet
        "198045",  # nortriptyline 10 MG Oral Capsule
        "198046",  # nortriptyline 50 MG Oral Capsule
        "198047",  # nortriptyline 75 MG Oral Capsule
        "200371",  # citalopram 20 MG Oral Tablet
        "2200168",  # Sprinkle duloxetine 20 MG Delayed Release Oral Capsule
        "2200175",  # Sprinkle duloxetine 30 MG Delayed Release Oral Capsule
        "2200178",  # Sprinkle duloxetine 40 MG Delayed Release Oral Capsule
        "2200181",  # Sprinkle duloxetine 60 MG Delayed Release Oral Capsule
        "248642",  # fluoxetine 20 MG Oral Tablet
        "251201",  # sertraline 200 MG Oral Capsule
        "2532159",  # PMDD fluoxetine 10 MG Oral Tablet
        "2532163",  # PMDD fluoxetine 20 MG Oral Tablet
        "2591786",  # citalopram 30 MG Oral Capsule
        "283672",  # citalopram 10 MG Oral Tablet
        "309313",  # citalopram 2 MG/ML Oral Solution
        "309314",  # citalopram 40 MG Oral Tablet
        "310384",  # fluoxetine 10 MG Oral Capsule
        "310385",  # fluoxetine 20 MG Oral Capsule
        "310386",  # fluoxetine 4 MG/ML Oral Solution
        "312036",  # nortriptyline 2 MG/ML Oral Solution
        "312242",  # paroxetine hydrochloride 2 MG/ML Oral Suspension
        "312938",  # sertraline 100 MG Oral Tablet
        "312940",  # sertraline 25 MG Oral Tablet
        "312941",  # sertraline 50 MG Oral Tablet
        "313496",  # trimipramine 100 MG Oral Capsule
        "313498",  # trimipramine 25 MG Oral Capsule
        "313499",  # trimipramine 50 MG Oral Capsule
        "313989",  # fluoxetine 40 MG Oral Capsule
        "313990",  # fluoxetine 10 MG Oral Tablet
        "313995",  # fluoxetine 90 MG Delayed Release Oral Capsule
        "317136",  # nortriptyline 25 MG Oral Capsule
        "349332",  # escitalopram 10 MG Oral Tablet
        "351249",  # escitalopram 5 MG Oral Tablet
        "351250",  # escitalopram 20 MG Oral Tablet
        "351285",  # escitalopram 1 MG/ML Oral Solution
        "403969",  # fluoxetine 25 MG / olanzapine 6 MG Oral Capsule
        "403970",  # fluoxetine 25 MG / olanzapine 12 MG Oral Capsule
        "403971",  # fluoxetine 50 MG / olanzapine 12 MG Oral Capsule
        "403972",  # fluoxetine 50 MG / olanzapine 6 MG Oral Capsule
        "410584",  # sertraline 150 MG Oral Capsule
        "596926",  # duloxetine 20 MG Delayed Release Oral Capsule
        "596930",  # duloxetine 30 MG Delayed Release Oral Capsule
        "596934",  # duloxetine 60 MG Delayed Release Oral Capsule
        "616402",  # duloxetine 40 MG Delayed Release Oral Capsule
        "721787",  # fluoxetine 25 MG / olanzapine 3 MG Oral Capsule
        "790264",  # 24 HR desvenlafaxine 100 MG Extended Release Oral Tablet
        "790288",  # 24 HR desvenlafaxine 50 MG Extended Release Oral Tablet
        "833135",  # milnacipran hydrochloride 100 MG Oral Tablet
        "833141",  # milnacipran hydrochloride 12.5 MG Oral Tablet
        "833144",  # milnacipran hydrochloride 50 MG Oral Tablet
        "833147",  # milnacipran hydrochloride 25 MG Oral Tablet
        "835564",  # imipramine hydrochloride 25 MG Oral Tablet
        "835568",  # imipramine hydrochloride 50 MG Oral Tablet
        "835572",  # imipramine pamoate 75 MG Oral Capsule
        "835577",  # imipramine pamoate 150 MG Oral Capsule
        "835589",  # imipramine pamoate 125 MG Oral Capsule
        "835591",  # imipramine pamoate 100 MG Oral Capsule
        "835593",  # imipramine hydrochloride 10 MG Oral Tablet
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
        "861064",  # sertraline 20 MG/ML Oral Solution
        "903873",  # 24 HR fluvoxamine maleate 100 MG Extended Release Oral Capsule
        "903879",  # 24 HR fluvoxamine maleate 150 MG Extended Release Oral Capsule
        "903884",  # fluvoxamine maleate 100 MG Oral Tablet
        "903887",  # fluvoxamine maleate 25 MG Oral Tablet
        "903891",  # fluvoxamine maleate 50 MG Oral Tablet
        "905168",  # protriptyline hydrochloride 10 MG Oral Tablet
        "905172",  # protriptyline hydrochloride 5 MG Oral Tablet
        "966787",  # doxepin 3 MG Oral Tablet
        "966793",  # doxepin 6 MG Oral Tablet
    }

class Antihypertensives(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for antihypertensives

    **Data Element Scope:** This value set may use a model element related to Medication

    **Inclusion Criteria:** Includes concepts that represent antihypertensive medications including ace inhibitors, ARBs, aldosterone antagonists, alpha agonists, alpha blockers, beta blockers, calcium channel blockers, renin inhibitors, and vasodilators in generic, prescribable forms

    **Exclusion Criteria:** N/A
    """

    VALUE_SET_NAME = "Antihypertensives"
    OID = "2.16.840.1.113762.1.4.1248.164"
    DEFINITION_VERSION = "20240120"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1000001",  # amlodipine 5 MG / hydrochlorothiazide 25 MG / olmesartan medoxomil 40 MG Oral Tablet
        "1011710",  # aliskiren 150 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "1011713",  # aliskiren 150 MG / hydrochlorothiazide 25 MG Oral Tablet
        "1011736",  # aliskiren 150 MG Oral Tablet
        "1011739",  # aliskiren 300 MG Oral Tablet
        "1011750",  # aliskiren 300 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "1011753",  # aliskiren 300 MG / hydrochlorothiazide 25 MG Oral Tablet
        "104232",  # spironolactone 5 MG/ML Oral Suspension
        "1091646",  # azilsartan medoxomil 40 MG Oral Tablet
        "1091652",  # azilsartan medoxomil 80 MG Oral Tablet
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
        "153822",  # candesartan cilexetil 4 MG Oral Tablet
        "153823",  # candesartan cilexetil 8 MG Oral Tablet
        "1600716",  # amlodipine 10 MG / perindopril arginine 14 MG Oral Tablet
        "1600724",  # amlodipine 2.5 MG / perindopril arginine 3.5 MG Oral Tablet
        "1600728",  # amlodipine 5 MG / perindopril arginine 7 MG Oral Tablet
        "1606347",  # metoprolol tartrate 37.5 MG Oral Tablet
        "1606349",  # metoprolol tartrate 75 MG Oral Tablet
        "1656340",  # sacubitril 24 MG / valsartan 26 MG Oral Tablet
        "1656349",  # sacubitril 49 MG / valsartan 51 MG Oral Tablet
        "1656354",  # sacubitril 97 MG / valsartan 103 MG Oral Tablet
        "1798281",  # nebivolol 5 MG / valsartan 80 MG Oral Tablet
        "1806884",  # lisinopril 1 MG/ML Oral Solution
        "1812011",  # Osmotic 24 HR nifedipine 30 MG Extended Release Oral Tablet
        "1812013",  # Osmotic 24 HR nifedipine 60 MG Extended Release Oral Tablet
        "1812015",  # Osmotic 24 HR nifedipine 90 MG Extended Release Oral Tablet
        "197361",  # amlodipine 5 MG Oral Tablet
        "197379",  # atenolol 100 MG Oral Tablet
        "197380",  # atenolol 25 MG Oral Tablet
        "197381",  # atenolol 50 MG Oral Tablet
        "197382",  # atenolol 100 MG / chlorthalidone 25 MG Oral Tablet
        "197383",  # atenolol 50 MG / chlorthalidone 25 MG Oral Tablet
        "197436",  # captopril 25 MG / hydrochlorothiazide 15 MG Oral Tablet
        "197437",  # captopril 25 MG / hydrochlorothiazide 25 MG Oral Tablet
        "197438",  # captopril 50 MG / hydrochlorothiazide 15 MG Oral Tablet
        "197439",  # captopril 50 MG / hydrochlorothiazide 25 MG Oral Tablet
        "197625",  # doxazosin 1 MG Oral Tablet
        "197626",  # doxazosin 2 MG Oral Tablet
        "197627",  # doxazosin 4 MG Oral Tablet
        "197628",  # doxazosin 8 MG Oral Tablet
        "197745",  # guanfacine 1 MG Oral Tablet
        "197746",  # guanfacine 2 MG Oral Tablet
        "197770",  # hydrochlorothiazide 50 MG Oral Tablet
        "197848",  # isradipine 2.5 MG Oral Capsule
        "197849",  # isradipine 5 MG Oral Capsule
        "197884",  # lisinopril 40 MG Oral Tablet
        "197885",  # hydrochlorothiazide 12.5 MG / lisinopril 10 MG Oral Tablet
        "197886",  # hydrochlorothiazide 12.5 MG / lisinopril 20 MG Oral Tablet
        "197887",  # hydrochlorothiazide 25 MG / lisinopril 20 MG Oral Tablet
        "197956",  # methyldopa 250 MG Oral Tablet
        "197958",  # methyldopa 500 MG Oral Tablet
        "197960",  # hydrochlorothiazide 25 MG / methyldopa 250 MG Oral Tablet
        "197963",  # hydrochlorothiazide 15 MG / methyldopa 250 MG Oral Tablet
        "197986",  # minoxidil 10 MG Oral Tablet
        "197987",  # minoxidil 2.5 MG Oral Tablet
        "198000",  # bendroflumethiazide 5 MG / nadolol 40 MG Oral Tablet
        "198001",  # bendroflumethiazide 5 MG / nadolol 80 MG Oral Tablet
        "198032",  # nifedipine 10 MG Oral Capsule
        "198033",  # nifedipine 20 MG Oral Capsule
        "198034",  # 24 HR nifedipine 30 MG Extended Release Oral Tablet
        "198035",  # 24 HR nifedipine 60 MG Extended Release Oral Tablet
        "198036",  # 24 HR nifedipine 90 MG Extended Release Oral Tablet
        "198037",  # nimodipine 30 MG Oral Capsule
        "198141",  # prazosin 5 MG Oral Capsule
        "198188",  # ramipril 2.5 MG Oral Capsule
        "198189",  # ramipril 5 MG Oral Capsule
        "198222",  # spironolactone 100 MG Oral Tablet
        "198223",  # spironolactone 50 MG Oral Tablet
        "198224",  # hydrochlorothiazide 25 MG / spironolactone 25 MG Oral Tablet
        "198225",  # hydrochlorothiazide 50 MG / spironolactone 50 MG Oral Tablet
        "198314",  # hydrochlorothiazide 25 MG / triamterene 50 MG Oral Capsule
        "198316",  # hydrochlorothiazide 25 MG / triamterene 37.5 MG Oral Capsule
        "199351",  # trandolapril 2 MG Oral Tablet
        "199352",  # trandolapril 4 MG Oral Tablet
        "199353",  # trandolapril 1 MG Oral Tablet
        "1996254",  # valsartan 4 MG/ML Oral Solution
        "199903",  # hydrochlorothiazide 12.5 MG Oral Capsule
        "1999031",  # 24 HR metoprolol succinate 100 MG Extended Release Oral Capsule
        "1999033",  # 24 HR metoprolol succinate 200 MG Extended Release Oral Capsule
        "1999035",  # 24 HR metoprolol succinate 25 MG Extended Release Oral Capsule
        "1999037",  # 24 HR metoprolol succinate 50 MG Extended Release Oral Capsule
        "200031",  # carvedilol 6.25 MG Oral Tablet
        "200032",  # carvedilol 12.5 MG Oral Tablet
        "200033",  # carvedilol 25 MG Oral Tablet
        "200094",  # irbesartan 75 MG Oral Tablet
        "200095",  # irbesartan 150 MG Oral Tablet
        "200096",  # irbesartan 300 MG Oral Tablet
        "200284",  # hydrochlorothiazide 12.5 MG / valsartan 80 MG Oral Tablet
        "200285",  # hydrochlorothiazide 12.5 MG / valsartan 160 MG Oral Tablet
        "2047715",  # amlodipine 2.5 MG / celecoxib 200 MG Oral Tablet
        "2047716",  # amlodipine 5 MG / celecoxib 200 MG Oral Tablet
        "2047717",  # amlodipine 10 MG / celecoxib 200 MG Oral Tablet
        "205304",  # telmisartan 40 MG Oral Tablet
        "205305",  # telmisartan 80 MG Oral Tablet
        "205326",  # lisinopril 30 MG Oral Tablet
        "2184120",  # amlodipine 1 MG/ML Oral Suspension
        "2361311",  # nimodipine 6 MG/ML Oral Solution
        "251856",  # ramipril 2.5 MG Oral Tablet
        "251857",  # ramipril 5 MG Oral Tablet
        "2562816",  # finerenone 10 MG Oral Tablet
        "2562824",  # finerenone 20 MG Oral Tablet
        "2599173",  # amlodipine 1 MG/ML Oral Solution
        "260376",  # terazosin 10 MG Oral Capsule
        "261962",  # ramipril 10 MG Oral Capsule
        "282755",  # telmisartan 20 MG Oral Tablet
        "283316",  # hydrochlorothiazide 12.5 MG / telmisartan 40 MG Oral Tablet
        "283317",  # hydrochlorothiazide 12.5 MG / telmisartan 80 MG Oral Tablet
        "308135",  # amlodipine 10 MG Oral Tablet
        "308136",  # amlodipine 2.5 MG Oral Tablet
        "308962",  # captopril 100 MG Oral Tablet
        "308963",  # captopril 12.5 MG Oral Tablet
        "308964",  # captopril 50 MG Oral Tablet
        "310140",  # eprosartan 600 MG Oral Tablet
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
        "351256",  # eplerenone 25 MG Oral Tablet
        "351257",  # eplerenone 50 MG Oral Tablet
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
        "905199",  # hydralazine hydrochloride 10 MG Oral Tablet
        "905222",  # hydralazine hydrochloride 100 MG Oral Tablet
        "905225",  # hydralazine hydrochloride 25 MG Oral Tablet
        "905377",  # hydralazine hydrochloride 37.5 MG / isosorbide dinitrate 20 MG Oral Tablet
        "905395",  # hydralazine hydrochloride 50 MG Oral Tablet
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
    }

class CentralNervousSystemDepressants(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for prescription central nervous system (CNS) medications capable of slowing brain activity

    **Data Element Scope:** This value set may use a model element related to Medication

    **Inclusion Criteria:** Includes concepts that represent generic and prescription central nervous system (CNS) medications capable of slowing brain activity such as antiepileptics, antipsychotics, barbiturates, benzodiazepines, and hypnotics

    **Exclusion Criteria:** Excludes non-prescription CNS depressant medications
    """

    VALUE_SET_NAME = "Central Nervous System Depressants"
    OID = "2.16.840.1.113762.1.4.1248.134"
    DEFINITION_VERSION = "20250211"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1000048",  # doxepin 10 MG Oral Capsule
        "1000054",  # doxepin 10 MG/ML Oral Solution
        "1000058",  # doxepin 100 MG Oral Capsule
        "1000064",  # doxepin 150 MG Oral Capsule
        "1000070",  # doxepin 25 MG Oral Capsule
        "1000076",  # doxepin 50 MG Oral Capsule
        "1000091",  # doxepin hydrochloride 50 MG/ML Topical Cream
        "1000097",  # doxepin 75 MG Oral Capsule
        "1006801",  # clozapine 150 MG Disintegrating Oral Tablet
        "103968",  # lamotrigine 100 MG Disintegrating Oral Tablet
        "1040031",  # lurasidone hydrochloride 40 MG Oral Tablet
        "1040041",  # lurasidone hydrochloride 80 MG Oral Tablet
        "1046787",  # atropine sulfate 0.00388 MG/ML / hyoscyamine sulfate 0.0207 MG/ML / phenobarbital 3.24 MG/ML / scopolamine hydrobromide 0.0013 MG/ML Oral Solution
        "1046815",  # atropine sulfate 0.0194 MG / hyoscyamine sulfate 0.1037 MG / phenobarbital 16.2 MG / scopolamine hydrobromide 0.0065 MG Oral Tablet
        "1046997",  # atropine sulfate 0.0582 MG / hyoscyamine sulfate 0.311 MG / phenobarbital 48.6 MG / scopolamine hydrobromide 0.0195 MG Extended Release Oral Tablet
        "1092357",  # rufinamide 40 MG/ML Oral Suspension
        "1098608",  # 24 HR lamotrigine 300 MG Extended Release Oral Tablet
        "1099563",  # 24 HR divalproex sodium 250 MG Extended Release Oral Tablet
        "1099569",  # 24 HR divalproex sodium 500 MG Extended Release Oral Tablet
        "1099596",  # divalproex sodium 125 MG Delayed Release Oral Capsule
        "1099625",  # divalproex sodium 125 MG Delayed Release Oral Tablet
        "1099678",  # divalproex sodium 250 MG Delayed Release Oral Tablet
        "1099681",  # valproic acid 250 MG Oral Capsule
        "1099687",  # valproic acid 50 MG/ML Oral Solution
        "1099870",  # divalproex sodium 500 MG Delayed Release Oral Tablet
        "1101338",  # gabapentin enacarbil 600 MG Extended Release Oral Tablet
        "1146690",  # 24 HR lamotrigine 250 MG Extended Release Oral Tablet
        "1232194",  # zolpidem tartrate 1.75 MG Sublingual Tablet
        "1232202",  # zolpidem tartrate 3.5 MG Sublingual Tablet
        "1235247",  # lurasidone hydrochloride 20 MG Oral Tablet
        "1249617",  # acetaminophen 300 MG / butalbital 50 MG Oral Tablet
        "1251614",  # butabarbital sodium 30 MG Oral Tablet
        "1297278",  # lurasidone hydrochloride 120 MG Oral Tablet
        "1298088",  # flurazepam hydrochloride 15 MG Oral Capsule
        "1298091",  # flurazepam hydrochloride 30 MG Oral Capsule
        "1298816",  # molindone hydrochloride 10 MG Oral Tablet
        "1298906",  # molindone hydrochloride 25 MG Oral Tablet
        "1298910",  # molindone hydrochloride 5 MG Oral Tablet
        "1299903",  # tiagabine hydrochloride 12 MG Oral Tablet
        "1299909",  # tiagabine hydrochloride 16 MG Oral Tablet
        "1299911",  # tiagabine hydrochloride 2 MG Oral Tablet
        "1299914",  # tiagabine hydrochloride 20 MG Oral Tablet
        "1299917",  # tiagabine hydrochloride 4 MG Oral Tablet
        "1302827",  # 24 HR phentermine 7.5 MG / topiramate 46 MG Extended Release Oral Capsule
        "1302839",  # 24 HR phentermine 3.75 MG / topiramate 23 MG Extended Release Oral Capsule
        "1302850",  # 24 HR phentermine 15 MG / topiramate 92 MG Extended Release Oral Capsule
        "1313059",  # 24 HR phentermine 11.25 MG / topiramate 69 MG Extended Release Oral Capsule
        "1313112",  # phenytoin 25 MG/ML Oral Suspension
        "1313885",  # phenytoin 50 MG Chewable Tablet
        "1356557",  # perampanel 2 MG Oral Tablet
        "1356570",  # perampanel 4 MG Oral Tablet
        "1356574",  # perampanel 6 MG Oral Tablet
        "1356578",  # perampanel 8 MG Oral Tablet
        "1356582",  # perampanel 10 MG Oral Tablet
        "1356586",  # perampanel 12 MG Oral Tablet
        "1359010",  # {7 (perampanel 2 MG Oral Tablet) / 7 (perampanel 4 MG Oral Tablet) } Pack
        "1365653",  # 24 HR oxcarbazepine 150 MG Extended Release Oral Tablet
        "1365842",  # 24 HR oxcarbazepine 300 MG Extended Release Oral Tablet
        "1365844",  # 24 HR oxcarbazepine 600 MG Extended Release Oral Tablet
        "1366192",  # clobazam 2.5 MG/ML Oral Suspension
        "1367518",  # 1 ACTUAT loxapine 10 MG/ACTUAT Dry Powder Inhaler
        "1369825",  # clozapine 50 MG/ML Oral Suspension
        "141935",  # haloperidol 2 MG/ML Oral Solution
        "1431235",  # lurasidone hydrochloride 60 MG Oral Tablet
        "1431286",  # acetaminophen 300 MG / butalbital 50 MG / caffeine 40 MG / codeine phosphate 30 MG Oral Capsule
        "1436239",  # 24 HR topiramate 50 MG Extended Release Oral Capsule
        "1437278",  # 24 HR topiramate 25 MG Extended Release Oral Capsule
        "1437283",  # 24 HR topiramate 100 MG Extended Release Oral Capsule
        "1437288",  # 24 HR topiramate 200 MG Extended Release Oral Capsule
        "1482507",  # eslicarbazepine acetate 200 MG Oral Tablet
        "1482515",  # eslicarbazepine acetate 400 MG Oral Tablet
        "1482521",  # eslicarbazepine acetate 600 MG Oral Tablet
        "1482525",  # eslicarbazepine acetate 800 MG Oral Tablet
        "1482820",  # gabapentin enacarbil 300 MG Extended Release Oral Tablet
        "1490473",  # tasimelteon 20 MG Oral Capsule
        "1491642",  # {7 (eslicarbazepine acetate 400 MG Oral Tablet) / 7 (eslicarbazepine acetate 800 MG Oral Tablet) } Pack
        "1494769",  # Sprinkle 24 HR topiramate 150 MG Extended Release Oral Capsule
        "151226",  # topiramate 50 MG Oral Tablet
        "1547104",  # suvorexant 10 MG Oral Tablet
        "1547112",  # suvorexant 15 MG Oral Tablet
        "1547116",  # suvorexant 20 MG Oral Tablet
        "1547573",  # suvorexant 5 MG Oral Tablet
        "1605362",  # 24 HR levetiracetam 1000 MG Extended Release Oral Tablet
        "1605372",  # 24 HR levetiracetam 1500 MG Extended Release Oral Tablet
        "1606337",  # asenapine 2.5 MG Sublingual Tablet
        "1648646",  # {1 (24 HR quetiapine 200 MG Extended Release Oral Tablet) / 11 (24 HR quetiapine 300 MG Extended Release Oral Tablet) / 3 (24 HR quetiapine 50 MG Extended Release Oral Tablet) } Pack
        "1658319",  # brexpiprazole 0.25 MG Oral Tablet
        "1658327",  # brexpiprazole 0.5 MG Oral Tablet
        "1658331",  # brexpiprazole 1 MG Oral Tablet
        "1658335",  # brexpiprazole 2 MG Oral Tablet
        "1658339",  # brexpiprazole 3 MG Oral Tablet
        "1658343",  # brexpiprazole 4 MG Oral Tablet
        "1667660",  # cariprazine 1.5 MG Oral Capsule
        "1667668",  # cariprazine 3 MG Oral Capsule
        "1667672",  # cariprazine 4.5 MG Oral Capsule
        "1667676",  # cariprazine 6 MG Oral Capsule
        "1721312",  # {7 (perampanel 4 MG Oral Tablet) / 7 (perampanel 6 MG Oral Tablet) } Pack
        "1724446",  # acetaminophen 325 MG / butalbital 25 MG Oral Tablet
        "1736037",  # levetiracetam 1000 MG Tablet for Oral Suspension
        "1736045",  # levetiracetam 250 MG Tablet for Oral Suspension
        "1736048",  # levetiracetam 500 MG Tablet for Oral Suspension
        "1736051",  # levetiracetam 750 MG Tablet for Oral Suspension
        "1739761",  # brivaracetam 10 MG Oral Tablet
        "1739768",  # brivaracetam 100 MG Oral Tablet
        "1739772",  # brivaracetam 25 MG Oral Tablet
        "1739776",  # brivaracetam 50 MG Oral Tablet
        "1739780",  # brivaracetam 75 MG Oral Tablet
        "1739785",  # brivaracetam 10 MG/ML Oral Solution
        "1741746",  # {1 (cariprazine 1.5 MG Oral Capsule) / 6 (cariprazine 3 MG Oral Capsule) } Pack
        "1790122",  # perampanel 0.5 MG/ML Oral Suspension
        "1806380",  # Once-Daily gabapentin 300 MG Oral Tablet
        "1806382",  # Once-Daily gabapentin 600 MG Oral Tablet
        "1812419",  # Sprinkle 24 HR topiramate 200 MG Extended Release Oral Capsule
        "1812421",  # Sprinkle 24 HR topiramate 25 MG Extended Release Oral Capsule
        "1812425",  # Sprinkle 24 HR topiramate 50 MG Extended Release Oral Capsule
        "1812427",  # Sprinkle 24 HR topiramate 100 MG Extended Release Oral Capsule
        "197303",  # acetazolamide 125 MG Oral Tablet
        "197304",  # acetazolamide 250 MG Oral Tablet
        "197321",  # alprazolam 1 MG Oral Tablet
        "197322",  # alprazolam 2 MG Oral Tablet
        "197426",  # acetaminophen 325 MG / butalbital 50 MG Oral Tablet
        "197441",  # carbamazepine 100 MG Oral Tablet
        "197464",  # clorazepate dipotassium 15 MG Oral Tablet
        "197465",  # clorazepate dipotassium 3.75 MG Oral Tablet
        "197466",  # clorazepate dipotassium 7.5 MG Oral Tablet
        "197527",  # clonazepam 0.5 MG Oral Tablet
        "197528",  # clonazepam 1 MG Oral Tablet
        "197529",  # clonazepam 2 MG Oral Tablet
        "197535",  # clozapine 100 MG Oral Tablet
        "197536",  # clozapine 25 MG Oral Tablet
        "197589",  # diazepam 10 MG Oral Tablet
        "197590",  # diazepam 2 MG Oral Tablet
        "197591",  # diazepam 5 MG Oral Tablet
        "197653",  # estazolam 1 MG Oral Tablet
        "197654",  # estazolam 2 MG Oral Tablet
        "197682",  # ethosuximide 250 MG Oral Capsule
        "197754",  # haloperidol 20 MG Oral Tablet
        "197900",  # lorazepam 0.5 MG Oral Tablet
        "197901",  # lorazepam 1 MG Oral Tablet
        "197902",  # lorazepam 2 MG Oral Tablet
        "197949",  # methsuximide 300 MG Oral Capsule
        "198057",  # oxazepam 10 MG Oral Capsule
        "198059",  # oxazepam 30 MG Oral Capsule
        "198075",  # perphenazine 16 MG Oral Tablet
        "198076",  # perphenazine 2 MG Oral Tablet
        "198077",  # perphenazine 4 MG Oral Tablet
        "198078",  # perphenazine 8 MG Oral Tablet
        "198083",  # phenobarbital 100 MG Oral Tablet
        "198085",  # phenobarbital 16 MG Oral Tablet
        "198086",  # phenobarbital 16.2 MG Oral Tablet
        "198089",  # phenobarbital 60 MG Oral Tablet
        "198103",  # pimozide 2 MG Oral Tablet
        "198150",  # primidone 50 MG Oral Tablet
        "198159",  # prochlorperazine 25 MG Rectal Suppository
        "198183",  # quazepam 15 MG Oral Tablet
        "198241",  # temazepam 15 MG Oral Capsule
        "198242",  # temazepam 30 MG Oral Capsule
        "198243",  # temazepam 7.5 MG Oral Capsule
        "198270",  # thioridazine 100 MG Oral Tablet
        "198274",  # thioridazine 25 MG Oral Tablet
        "198275",  # thioridazine 50 MG Oral Tablet
        "198317",  # triazolam 0.125 MG Oral Tablet
        "198318",  # triazolam 0.25 MG Oral Tablet
        "198322",  # trifluoperazine 1 MG Oral Tablet
        "198323",  # trifluoperazine 10 MG Oral Tablet
        "198324",  # trifluoperazine 2 MG Oral Tablet
        "198325",  # trifluoperazine 5 MG Oral Tablet
        "198358",  # felbamate 400 MG Oral Tablet
        "198359",  # felbamate 600 MG Oral Tablet
        "198365",  # prochlorperazine 10 MG Oral Tablet
        "198427",  # lamotrigine 100 MG Oral Tablet
        "198428",  # lamotrigine 150 MG Oral Tablet
        "198429",  # lamotrigine 200 MG Oral Tablet
        "198430",  # lamotrigine 25 MG Disintegrating Oral Tablet
        "1988974",  # 24 HR pregabalin 165 MG Extended Release Oral Tablet
        "1988977",  # 24 HR pregabalin 330 MG Extended Release Oral Tablet
        "1988980",  # 24 HR pregabalin 82.5 MG Extended Release Oral Tablet
        "199164",  # phenobarbital 97.2 MG Oral Tablet
        "199167",  # phenobarbital 32.4 MG Oral Tablet
        "199168",  # phenobarbital 64.8 MG Oral Tablet
        "199322",  # lamotrigine 50 MG Oral Tablet
        "199378",  # 12 HR carbamazepine 100 MG Extended Release Oral Tablet
        "199387",  # risperidone 1 MG/ML Oral Solution
        "199450",  # clobazam 10 MG Oral Tablet
        "1995136",  # acetaminophen 300 MG / butalbital 50 MG Oral Capsule
        "199521",  # vigabatrin 500 MG Oral Tablet
        "1998451",  # Sensor aripiprazole 10 MG Oral Tablet
        "1998454",  # Sensor aripiprazole 15 MG Oral Tablet
        "1998456",  # Sensor aripiprazole 2 MG Oral Tablet
        "1998458",  # Sensor aripiprazole 20 MG Oral Tablet
        "1998460",  # Sensor aripiprazole 30 MG Oral Tablet
        "1998462",  # Sensor aripiprazole 5 MG Oral Tablet
        "199888",  # topiramate 25 MG Oral Tablet
        "199889",  # topiramate 100 MG Oral Tablet
        "199890",  # topiramate 200 MG Oral Tablet
        "200034",  # olanzapine 2.5 MG Oral Tablet
        "200131",  # 12 HR carbamazepine 300 MG Extended Release Oral Capsule
        "2049269",  # pimavanserin 10 MG Oral Tablet
        "2049275",  # pimavanserin 34 MG Oral Capsule
        "205315",  # topiramate 25 MG Oral Capsule
        "205316",  # topiramate 15 MG Oral Capsule
        "2054973",  # stiripentol 250 MG Oral Capsule
        "2054981",  # stiripentol 500 MG Oral Capsule
        "2055011",  # stiripentol 500 MG Powder for Oral Suspension
        "2055015",  # stiripentol 250 MG Powder for Oral Suspension
        "2058253",  # clobazam 10 MG Oral Film
        "2058254",  # clobazam 20 MG Oral Film
        "2058255",  # clobazam 5 MG Oral Film
        "2058900",  # cannabidiol 100 MG/ML Oral Solution
        "2173494",  # midazolam 50 MG/ML Nasal Spray
        "2261741",  # 24 HR asenapine 0.158 MG/HR Transdermal System
        "2261750",  # 24 HR asenapine 0.238 MG/HR Transdermal System
        "2261758",  # 24 HR asenapine 0.317 MG/HR Transdermal System
        "2265695",  # cenobamate 50 MG Oral Tablet
        "2272613",  # diazepam 100 MG/ML Nasal Spray
        "2272626",  # diazepam 50 MG/ML Nasal Spray
        "2272632",  # diazepam 75 MG/ML Nasal Spray
        "2275607",  # lumateperone 42 MG Oral Capsule
        "2283503",  # cenobamate 100 MG Oral Tablet
        "2283507",  # cenobamate 150 MG Oral Tablet
        "2283511",  # cenobamate 200 MG Oral Tablet
        "2283517",  # {28 (cenobamate 150 MG Oral Tablet) / 28 (cenobamate 200 MG Oral Tablet) } Pack
        "2283520",  # cenobamate 12.5 MG Oral Tablet
        "2283522",  # cenobamate 25 MG Oral Tablet
        "2283523",  # {14 (cenobamate 12.5 MG Oral Tablet) / 14 (cenobamate 25 MG Oral Tablet) } Pack
        "2283535",  # {14 (cenobamate 100 MG Oral Tablet) / 14 (cenobamate 50 MG Oral Tablet) } Pack
        "2283539",  # {14 (cenobamate 150 MG Oral Tablet) / 14 (cenobamate 200 MG Oral Tablet) } Pack
        "2381138",  # fenfluramine 2.2 MG/ML Oral Solution
        "238134",  # aspirin 325 MG / butalbital 50 MG / caffeine 40 MG Oral Capsule
        "238135",  # aspirin 325 MG / butalbital 50 MG / caffeine 40 MG Oral Tablet
        "238153",  # acetaminophen 325 MG / butalbital 50 MG / caffeine 40 MG Oral Capsule
        "238154",  # acetaminophen 325 MG / butalbital 50 MG / caffeine 40 MG Oral Tablet
        "2398511",  # {9 (Once-Daily gabapentin 300 MG Oral Tablet) / 24 (Once-Daily gabapentin 600 MG Oral Tablet) } Pack
        "246172",  # clobazam 20 MG Oral Tablet
        "2468312",  # tasimelteon 4 MG/ML Oral Suspension
        "249329",  # lamotrigine 250 MG Oral Tablet
        "250820",  # vigabatrin 500 MG Powder for Oral Solution
        "251322",  # ethosuximide 50 MG/ML Oral Solution
        "252478",  # lamotrigine 50 MG Disintegrating Oral Tablet
        "252479",  # lamotrigine 200 MG Disintegrating Oral Tablet
        "2540431",  # {28 (cenobamate 100 MG Oral Tablet) / 28 (cenobamate 150 MG Oral Tablet) } Pack
        "2569564",  # 24 HR lorazepam 1 MG Extended Release Oral Capsule
        "2569573",  # 24 HR lorazepam 2 MG Extended Release Oral Capsule
        "2569577",  # 24 HR lorazepam 3 MG Extended Release Oral Capsule
        "2570392",  # olanzapine 5 MG / samidorphan 10 MG Oral Tablet
        "2570399",  # olanzapine 10 MG / samidorphan 10 MG Oral Tablet
        "2570402",  # olanzapine 15 MG / samidorphan 10 MG Oral Tablet
        "2570405",  # olanzapine 20 MG / samidorphan 10 MG Oral Tablet
        "2583731",  # aspirin 500 MG / butalbital 50 MG / caffeine 40 MG Oral Capsule
        "2586427",  # topiramate 25 MG/ML Oral Solution
        "2607529",  # lumateperone 10.5 MG Oral Capsule
        "2607533",  # lumateperone 21 MG Oral Capsule
        "2634743",  # Once-Daily gabapentin 900 MG Oral Tablet
        "2634747",  # Once-Daily gabapentin 450 MG Oral Tablet
        "2634751",  # Once-Daily gabapentin 750 MG Oral Tablet
        "2637018",  # 24 HR lacosamide 100 MG Extended Release Oral Capsule
        "2637027",  # 24 HR lacosamide 150 MG Extended Release Oral Capsule
        "2637032",  # 24 HR lacosamide 200 MG Extended Release Oral Capsule
        "2637353",  # zolpidem tartrate 7.5 MG Oral Capsule
        "2641918",  # {14 (perampanel 2 MG Oral Tablet) } Pack
        "282401",  # lamotrigine 25 MG Oral Tablet
        "283523",  # gabapentin 50 MG/ML Oral Solution
        "283536",  # oxcarbazepine 60 MG/ML Oral Suspension
        "283639",  # olanzapine 20 MG Oral Tablet
        "308047",  # alprazolam 0.25 MG Oral Tablet
        "308048",  # alprazolam 0.5 MG Oral Tablet
        "308050",  # alprazolam 1 MG/ML Oral Solution
        "309374",  # clozapine 200 MG Oral Tablet
        "309843",  # diazepam 1 MG/ML Oral Solution
        "309844",  # diazepam 5 MG/ML Oral Solution
        "310285",  # felbamate 120 MG/ML Oral Suspension
        "310430",  # gabapentin 100 MG Oral Capsule
        "310431",  # gabapentin 300 MG Oral Capsule
        "310432",  # gabapentin 400 MG Oral Capsule
        "310433",  # gabapentin 600 MG Oral Tablet
        "310434",  # gabapentin 800 MG Oral Tablet
        "310670",  # haloperidol 0.5 MG Oral Tablet
        "310671",  # haloperidol 1 MG Oral Tablet
        "310672",  # haloperidol 5 MG Oral Tablet
        "311264",  # lamotrigine 25 MG Tablet for Oral Suspension
        "311265",  # lamotrigine 5 MG Tablet for Oral Suspension
        "311288",  # levetiracetam 250 MG Oral Tablet
        "311289",  # levetiracetam 500 MG Oral Tablet
        "311290",  # levetiracetam 750 MG Oral Tablet
        "311376",  # lorazepam 2 MG/ML Oral Solution
        "311385",  # loxapine 25 MG Oral Capsule
        "311386",  # loxapine 5 MG Oral Capsule
        "312076",  # olanzapine 10 MG Disintegrating Oral Tablet
        "312077",  # olanzapine 15 MG Oral Tablet
        "312078",  # olanzapine 5 MG Oral Tablet
        "312079",  # olanzapine 7.5 MG Oral Tablet
        "312134",  # oxazepam 15 MG Oral Capsule
        "312136",  # oxcarbazepine 150 MG Oral Tablet
        "312137",  # oxcarbazepine 300 MG Oral Tablet
        "312138",  # oxcarbazepine 600 MG Oral Tablet
        "312357",  # phenobarbital 15 MG Oral Tablet
        "312362",  # phenobarbital 30 MG Oral Tablet
        "312439",  # pimozide 1 MG Oral Tablet
        "312635",  # prochlorperazine 5 MG Oral Tablet
        "312743",  # quetiapine 100 MG Oral Tablet
        "312744",  # quetiapine 25 MG Oral Tablet
        "312745",  # quetiapine 300 MG Oral Tablet
        "312828",  # risperidone 0.25 MG Oral Tablet
        "312829",  # risperidone 0.5 MG Oral Tablet
        "312830",  # risperidone 1 MG Oral Tablet
        "312831",  # risperidone 2 MG Oral Tablet
        "312832",  # risperidone 3 MG Oral Tablet
        "312914",  # secobarbital sodium 100 MG Oral Capsule
        "313354",  # thioridazine 10 MG Oral Tablet
        "313361",  # thiothixene 10 MG Oral Capsule
        "313362",  # thiothixene 1 MG Oral Capsule
        "313364",  # thiothixene 2 MG Oral Capsule
        "313366",  # thiothixene 5 MG Oral Capsule
        "313761",  # zaleplon 10 MG Oral Capsule
        "313762",  # zaleplon 5 MG Oral Capsule
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
        "314285",  # zonisamide 100 MG Oral Capsule
        "314286",  # ziprasidone 20 MG Oral Capsule
        "317174",  # quetiapine 200 MG Oral Tablet
        "349010",  # lamotrigine 2 MG Tablet for Oral Suspension
        "349194",  # clonazepam 0.125 MG Disintegrating Oral Tablet
        "349195",  # clonazepam 0.25 MG Disintegrating Oral Tablet
        "349196",  # clonazepam 1 MG Disintegrating Oral Tablet
        "349197",  # clonazepam 2 MG Disintegrating Oral Tablet
        "349198",  # clonazepam 0.5 MG Disintegrating Oral Tablet
        "349490",  # aripiprazole 15 MG Oral Tablet
        "349545",  # aripiprazole 10 MG Oral Tablet
        "349547",  # aripiprazole 30 MG Oral Tablet
        "349553",  # aripiprazole 20 MG Oral Tablet
        "351107",  # olanzapine 15 MG Disintegrating Oral Tablet
        "351108",  # olanzapine 20 MG Disintegrating Oral Tablet
        "387003",  # levetiracetam 1000 MG Oral Tablet
        "389201",  # quetiapine 150 MG Oral Tablet
        "401953",  # risperidone 1 MG Disintegrating Oral Tablet
        "401954",  # risperidone 2 MG Disintegrating Oral Tablet
        "402131",  # aripiprazole 5 MG Oral Tablet
        "403825",  # risperidone 0.5 MG Disintegrating Oral Tablet
        "403884",  # levetiracetam 100 MG/ML Oral Solution
        "403966",  # zonisamide 25 MG Oral Capsule
        "403967",  # zonisamide 50 MG Oral Capsule
        "403969",  # fluoxetine 25 MG / olanzapine 6 MG Oral Capsule
        "403970",  # fluoxetine 25 MG / olanzapine 12 MG Oral Capsule
        "403971",  # fluoxetine 50 MG / olanzapine 12 MG Oral Capsule
        "403972",  # fluoxetine 50 MG / olanzapine 6 MG Oral Capsule
        "422410",  # midazolam 2 MG/ML Oral Solution
        "427538",  # clobazam 5 MG Oral Tablet
        "429212",  # clozapine 50 MG Oral Tablet
        "433798",  # 24 HR alprazolam 0.5 MG Extended Release Oral Tablet
        "433799",  # 24 HR alprazolam 2 MG Extended Release Oral Tablet
        "433800",  # 24 HR alprazolam 1 MG Extended Release Oral Tablet
        "433801",  # 24 HR alprazolam 3 MG Extended Release Oral Tablet
        "476177",  # clozapine 100 MG Disintegrating Oral Tablet
        "476179",  # clozapine 25 MG Disintegrating Oral Tablet
        "483438",  # pregabalin 100 MG Oral Capsule
        "483440",  # pregabalin 150 MG Oral Capsule
        "483442",  # pregabalin 25 MG Oral Capsule
        "483444",  # pregabalin 300 MG Oral Capsule
        "483446",  # pregabalin 200 MG Oral Capsule
        "483448",  # pregabalin 50 MG Oral Capsule
        "483450",  # pregabalin 75 MG Oral Capsule
        "485413",  # alprazolam 0.25 MG Disintegrating Oral Tablet
        "485414",  # alprazolam 1 MG Disintegrating Oral Tablet
        "485415",  # alprazolam 0.5 MG Disintegrating Oral Tablet
        "485416",  # alprazolam 2 MG Disintegrating Oral Tablet
        "485440",  # eszopiclone 1 MG Oral Tablet
        "485442",  # eszopiclone 2 MG Oral Tablet
        "485465",  # eszopiclone 3 MG Oral Tablet
        "485489",  # temazepam 22.5 MG Oral Capsule
        "485496",  # aripiprazole 1 MG/ML Oral Solution
        "562524",  # 12 HR acetazolamide 500 MG Extended Release Oral Capsule
        "577127",  # pregabalin 225 MG Oral Capsule
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
        "702519",  # phenobarbital 4 MG/ML Oral Solution
        "721773",  # clozapine 12.5 MG Disintegrating Oral Tablet
        "721787",  # fluoxetine 25 MG / olanzapine 3 MG Oral Capsule
        "721791",  # 24 HR quetiapine 200 MG Extended Release Oral Tablet
        "721794",  # 24 HR quetiapine 300 MG Extended Release Oral Tablet
        "721796",  # 24 HR quetiapine 400 MG Extended Release Oral Tablet
        "751139",  # {35 (lamotrigine 25 MG Oral Tablet) } Pack
        "751563",  # {7 (lamotrigine 100 MG Oral Tablet) / 42 (lamotrigine 25 MG Oral Tablet) } Pack
        "753451",  # {14 (lamotrigine 100 MG Oral Tablet) / 84 (lamotrigine 25 MG Oral Tablet) } Pack
        "756245",  # acetaminophen 21.7 MG/ML / butalbital 3.33 MG/ML / caffeine 2.67 MG/ML Oral Solution
        "801957",  # 0.5 ML diazepam 5 MG/ML Rectal Gel
        "801961",  # 2 ML diazepam 5 MG/ML Rectal Gel
        "801966",  # 4 ML diazepam 5 MG/ML Rectal Gel
        "807832",  # 24 HR levetiracetam 500 MG Extended Release Oral Tablet
        "809987",  # lacosamide 100 MG Oral Tablet
        "809992",  # lacosamide 150 MG Oral Tablet
        "809996",  # lacosamide 200 MG Oral Tablet
        "810000",  # lacosamide 50 MG Oral Tablet
        "824295",  # rufinamide 200 MG Oral Tablet
        "824301",  # rufinamide 400 MG Oral Tablet
        "828692",  # zolpidem tartrate 5 MG/ACTUAT Oral Spray
        "835726",  # acamprosate calcium 333 MG Delayed Release Oral Tablet
        "836641",  # zolpidem tartrate 10 MG Sublingual Tablet
        "836647",  # zolpidem tartrate 5 MG Sublingual Tablet
        "846378",  # 24 HR levetiracetam 750 MG Extended Release Oral Tablet
        "848722",  # iloperidone 1 MG Oral Tablet
        "848728",  # iloperidone 10 MG Oral Tablet
        "848732",  # iloperidone 12 MG Oral Tablet
        "848736",  # iloperidone 2 MG Oral Tablet
        "848740",  # iloperidone 4 MG Oral Tablet
        "848744",  # iloperidone 6 MG Oral Tablet
        "848748",  # iloperidone 8 MG Oral Tablet
        "848751",  # {2 (iloperidone 1 MG Oral Tablet) / 2 (iloperidone 2 MG Oral Tablet) / 2 (iloperidone 4 MG Oral Tablet) / 2 (iloperidone 6 MG Oral Tablet) } Pack
        "850087",  # 24 HR lamotrigine 100 MG Extended Release Oral Tablet
        "850091",  # 24 HR lamotrigine 50 MG Extended Release Oral Tablet
        "851748",  # {21 (lamotrigine 25 MG Disintegrating Oral Tablet) / 7 (lamotrigine 50 MG Disintegrating Oral Tablet) } Pack
        "851750",  # {7 (lamotrigine 100 MG Disintegrating Oral Tablet) / 14 (lamotrigine 25 MG Disintegrating Oral Tablet) / 14 (lamotrigine 50 MG Disintegrating Oral Tablet) } Pack
        "851752",  # {14 (lamotrigine 100 MG Disintegrating Oral Tablet) / 42 (lamotrigine 50 MG Disintegrating Oral Tablet) } Pack
        "853201",  # 24 HR quetiapine 50 MG Extended Release Oral Tablet
        "854873",  # zolpidem tartrate 10 MG Oral Tablet
        "854876",  # zolpidem tartrate 5 MG Oral Tablet
        "854880",  # zolpidem tartrate 12.5 MG Extended Release Oral Tablet
        "854894",  # zolpidem tartrate 6.25 MG Extended Release Oral Tablet
        "855671",  # phenytoin sodium 100 MG Extended Release Oral Capsule
        "855861",  # phenytoin sodium 200 MG Extended Release Oral Capsule
        "855869",  # phenytoin sodium 30 MG Extended Release Oral Capsule
        "855873",  # phenytoin sodium 300 MG Extended Release Oral Capsule
        "856706",  # amitriptyline hydrochloride 10 MG / perphenazine 2 MG Oral Tablet
        "856720",  # amitriptyline hydrochloride 10 MG / perphenazine 4 MG Oral Tablet
        "856769",  # amitriptyline hydrochloride 12.5 MG / chlordiazepoxide 5 MG Oral Tablet
        "856792",  # amitriptyline hydrochloride 25 MG / chlordiazepoxide 10 MG Oral Tablet
        "856797",  # amitriptyline hydrochloride 25 MG / perphenazine 2 MG Oral Tablet
        "856825",  # amitriptyline hydrochloride 25 MG / perphenazine 4 MG Oral Tablet
        "856840",  # amitriptyline hydrochloride 50 MG / perphenazine 4 MG Oral Tablet
        "859835",  # fluphenazine hydrochloride 0.5 MG/ML Oral Solution
        "859841",  # fluphenazine hydrochloride 10 MG Oral Tablet
        "859975",  # asenapine 10 MG Sublingual Tablet
        "859981",  # asenapine 5 MG Sublingual Tablet
        "860918",  # fluphenazine hydrochloride 5 MG Oral Tablet
        "861848",  # fluphenazine hydrochloride 5 MG/ML Oral Solution
        "865117",  # fluphenazine hydrochloride 1 MG Oral Tablet
        "865123",  # fluphenazine hydrochloride 2.5 MG Oral Tablet
        "866103",  # 24 HR paliperidone 1.5 MG Extended Release Oral Tablet
        "881271",  # {14 (lacosamide 100 MG Oral Tablet) / 14 (lacosamide 50 MG Oral Tablet) } Pack
        "889520",  # acetaminophen 300 MG / butalbital 50 MG / caffeine 40 MG Oral Capsule
        "889614",  # chlordiazepoxide hydrochloride 5 MG / clidinium bromide 2.5 MG Oral Capsule
        "895670",  # 24 HR quetiapine 150 MG Extended Release Oral Tablet
        "898715",  # pregabalin 20 MG/ML Oral Solution
        "900156",  # 24 HR lamotrigine 200 MG Extended Release Oral Tablet
        "900164",  # 24 HR lamotrigine 25 MG Extended Release Oral Tablet
        "900865",  # {14 (24 HR lamotrigine 100 MG Extended Release Oral Tablet) / 7 (24 HR lamotrigine 200 MG Extended Release Oral Tablet) / 14 (24 HR lamotrigine 50 MG Extended Release Oral Tablet) } Pack
        "900890",  # {7 (24 HR lamotrigine 100 MG Extended Release Oral Tablet) / 14 (24 HR lamotrigine 25 MG Extended Release Oral Tablet) / 14 (24 HR lamotrigine 50 MG Extended Release Oral Tablet) } Pack
        "900983",  # {21 (24 HR lamotrigine 25 MG Extended Release Oral Tablet) / 7 (24 HR lamotrigine 50 MG Extended Release Oral Tablet) } Pack
        "905369",  # chlordiazepoxide hydrochloride 10 MG Oral Capsule
        "905495",  # chlordiazepoxide hydrochloride 25 MG Oral Capsule
        "905516",  # chlordiazepoxide hydrochloride 5 MG Oral Capsule
        "96304",  # primidone 250 MG Oral Tablet
        "966787",  # doxepin 3 MG Oral Tablet
        "966793",  # doxepin 6 MG Oral Tablet
        "991039",  # chlorpromazine hydrochloride 10 MG Oral Tablet
        "991044",  # chlorpromazine hydrochloride 100 MG Oral Tablet
        "991053",  # chlorpromazine hydrochloride 100 MG/ML Oral Solution
        "991188",  # chlorpromazine hydrochloride 200 MG Oral Tablet
        "991194",  # chlorpromazine hydrochloride 25 MG Oral Tablet
        "991332",  # chlorpromazine hydrochloride 30 MG/ML Oral Solution
        "991336",  # chlorpromazine hydrochloride 50 MG Oral Tablet
        "993856",  # lacosamide 10 MG/ML Oral Solution
        "993943",  # acetaminophen 325 MG / butalbital 50 MG / caffeine 40 MG / codeine phosphate 30 MG Oral Capsule
        "994237",  # aspirin 325 MG / butalbital 50 MG / caffeine 40 MG / codeine phosphate 30 MG Oral Capsule
        "996921",  # clozapine 200 MG Disintegrating Oral Tablet
    }

class Diuretics(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for diuretics

    **Data Element Scope:** This value set may use a model element related to Medication

    **Inclusion Criteria:** Includes concepts that represent diuretics including loop diuretics, thiazide, and potassium sparing diuretics in generic, prescribable forms

    **Exclusion Criteria:** N/A
    """

    VALUE_SET_NAME = "Diuretics"
    OID = "2.16.840.1.113762.1.4.1248.170"
    DEFINITION_VERSION = "20240118"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "104232",  # spironolactone 5 MG/ML Oral Suspension
        "1235144",  # azilsartan medoxomil 40 MG / chlorthalidone 12.5 MG Oral Tablet
        "1235151",  # azilsartan medoxomil 40 MG / chlorthalidone 25 MG Oral Tablet
        "1251903",  # ethacrynic acid 25 MG Oral Tablet
        "197382",  # atenolol 100 MG / chlorthalidone 25 MG Oral Tablet
        "197383",  # atenolol 50 MG / chlorthalidone 25 MG Oral Tablet
        "197417",  # bumetanide 0.5 MG Oral Tablet
        "197418",  # bumetanide 1 MG Oral Tablet
        "197419",  # bumetanide 2 MG Oral Tablet
        "197475",  # chlorothiazide 250 MG Oral Tablet
        "197476",  # chlorothiazide 500 MG Oral Tablet
        "197498",  # chlorthalidone 15 MG Oral Tablet
        "197499",  # chlorthalidone 25 MG Oral Tablet
        "197500",  # chlorthalidone 50 MG Oral Tablet
        "197730",  # furosemide 10 MG/ML Oral Solution
        "197731",  # furosemide 8 MG/ML Oral Solution
        "197732",  # furosemide 80 MG Oral Tablet
        "197770",  # hydrochlorothiazide 50 MG Oral Tablet
        "197960",  # hydrochlorothiazide 25 MG / methyldopa 250 MG Oral Tablet
        "197963",  # hydrochlorothiazide 15 MG / methyldopa 250 MG Oral Tablet
        "198222",  # spironolactone 100 MG Oral Tablet
        "198223",  # spironolactone 50 MG Oral Tablet
        "198224",  # hydrochlorothiazide 25 MG / spironolactone 25 MG Oral Tablet
        "198225",  # hydrochlorothiazide 50 MG / spironolactone 50 MG Oral Tablet
        "198312",  # triamterene 100 MG Oral Capsule
        "198313",  # triamterene 50 MG Oral Capsule
        "198314",  # hydrochlorothiazide 25 MG / triamterene 50 MG Oral Capsule
        "198316",  # hydrochlorothiazide 25 MG / triamterene 37.5 MG Oral Capsule
        "198369",  # torsemide 10 MG Oral Tablet
        "198370",  # torsemide 100 MG Oral Tablet
        "198371",  # torsemide 20 MG Oral Tablet
        "198372",  # torsemide 5 MG Oral Tablet
        "199903",  # hydrochlorothiazide 12.5 MG Oral Capsule
        "2589881",  # torsemide 40 MG Oral Tablet
        "2589885",  # torsemide 60 MG Oral Tablet
        "309198",  # chlorothiazide 50 MG/ML Oral Suspension
        "310429",  # furosemide 20 MG Oral Tablet
        "310796",  # hydrochlorothiazide 12.5 MG / quinapril 10 MG Oral Tablet
        "310797",  # hydrochlorothiazide 12.5 MG / quinapril 20 MG Oral Tablet
        "310798",  # hydrochlorothiazide 25 MG Oral Tablet
        "310809",  # hydrochlorothiazide 25 MG / quinapril 20 MG Oral Tablet
        "310812",  # hydrochlorothiazide 25 MG / triamterene 37.5 MG Oral Tablet
        "310818",  # hydrochlorothiazide 50 MG / triamterene 75 MG Oral Tablet
        "313096",  # spironolactone 25 MG Oral Tablet
        "313988",  # furosemide 40 MG Oral Tablet
        "351256",  # eplerenone 25 MG Oral Tablet
        "351257",  # eplerenone 50 MG Oral Tablet
        "429503",  # hydrochlorothiazide 12.5 MG Oral Tablet
        "884192",  # chlorthalidone 15 MG / clonidine hydrochloride 0.1 MG Oral Tablet
        "884198",  # chlorthalidone 15 MG / clonidine hydrochloride 0.2 MG Oral Tablet
        "884203",  # chlorthalidone 15 MG / clonidine hydrochloride 0.3 MG Oral Tablet
        "977880",  # amiloride hydrochloride 5 MG Oral Tablet
        "977883",  # amiloride hydrochloride 5 MG / hydrochlorothiazide 50 MG Oral Tablet
    }

class Opioids(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for opioid medications.

    **Data Element Scope:** This value set may use a model element related to Medication

    **Inclusion Criteria:** Includes concepts that represent all formulations of opioids that may be administered in a home setting regardless of intended use. Includes combination medications that contain both an opioid and naloxone, an opioid antagonist.

    **Exclusion Criteria:** Excludes concepts for opioid medications that can only be administered in a clinical setting.
    """

    VALUE_SET_NAME = "Opioids"
    OID = "2.16.840.1.113762.1.4.1248.120"
    DEFINITION_VERSION = "20250206"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1010600",  # buprenorphine 2 MG / naloxone 0.5 MG Sublingual Film
        "1010604",  # buprenorphine 8 MG / naloxone 2 MG Sublingual Film
        "1014599",  # acetaminophen 300 MG / oxycodone hydrochloride 10 MG Oral Tablet
        "1014615",  # acetaminophen 300 MG / oxycodone hydrochloride 5 MG Oral Tablet
        "1014632",  # acetaminophen 300 MG / oxycodone hydrochloride 7.5 MG Oral Tablet
        "1037259",  # acetaminophen 300 MG / oxycodone hydrochloride 2.5 MG Oral Tablet
        "1042693",  # chlorpheniramine maleate 0.4 MG/ML / codeine phosphate 2 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "1044427",  # acetaminophen 20 MG/ML / hydrocodone bitartrate 0.667 MG/ML Oral Solution
        "1049214",  # acetaminophen 325 MG / oxycodone hydrochloride 10 MG Oral Tablet
        "1049221",  # acetaminophen 325 MG / oxycodone hydrochloride 5 MG Oral Tablet
        "1049225",  # acetaminophen 325 MG / oxycodone hydrochloride 7.5 MG Oral Tablet
        "1049251",  # acetaminophen 400 MG / oxycodone hydrochloride 10 MG Oral Tablet
        "1049260",  # acetaminophen 400 MG / oxycodone hydrochloride 5 MG Oral Tablet
        "1049502",  # 12 HR oxycodone hydrochloride 10 MG Extended Release Oral Tablet
        "1049543",  # 12 HR oxycodone hydrochloride 15 MG Extended Release Oral Tablet
        "1049574",  # 12 HR oxycodone hydrochloride 30 MG Extended Release Oral Tablet
        "1049580",  # acetaminophen 65 MG/ML / oxycodone hydrochloride 1 MG/ML Oral Solution
        "1049589",  # ibuprofen 400 MG / oxycodone hydrochloride 5 MG Oral Tablet
        "1049593",  # 12 HR oxycodone hydrochloride 60 MG Extended Release Oral Tablet
        "1049604",  # oxycodone hydrochloride 1 MG/ML Oral Solution
        "1049611",  # oxycodone hydrochloride 15 MG Oral Tablet
        "1049615",  # oxycodone hydrochloride 20 MG/ML Oral Solution
        "1049618",  # oxycodone hydrochloride 30 MG Oral Tablet
        "1049621",  # oxycodone hydrochloride 5 MG Oral Tablet
        "1049635",  # acetaminophen 325 MG / oxycodone hydrochloride 2.5 MG Oral Tablet
        "1049683",  # oxycodone hydrochloride 10 MG Oral Tablet
        "1049686",  # oxycodone hydrochloride 20 MG Oral Tablet
        "1049696",  # oxycodone hydrochloride 5 MG Oral Capsule
        "1053647",  # fentanyl 0.1 MG Sublingual Tablet
        "1053652",  # fentanyl 0.2 MG Sublingual Tablet
        "1053655",  # fentanyl 0.3 MG Sublingual Tablet
        "1053658",  # fentanyl 0.4 MG Sublingual Tablet
        "1053661",  # fentanyl 0.6 MG Sublingual Tablet
        "1053664",  # fentanyl 0.8 MG Sublingual Tablet
        "1087459",  # 12 HR chlorpheniramine polistirex 1.6 MG/ML / hydrocodone polistirex 2 MG/ML Extended Release Suspension
        "1089055",  # codeine phosphate 10 MG / guaifenesin 400 MG / pseudoephedrine hydrochloride 20 MG Oral Tablet
        "1089058",  # codeine phosphate 10 MG / guaifenesin 400 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet
        "1112220",  # chlorpheniramine maleate 0.8 MG/ML / hydrocodone bitartrate 1 MG/ML / pseudoephedrine hydrochloride 12 MG/ML Oral Solution
        "1113314",  # oxycodone hydrochloride 7.5 MG Oral Tablet
        "1114026",  # codeine phosphate 1.6 MG/ML / guaifenesin 40 MG/ML Oral Solution
        "1115573",  # fentanyl 0.1 MG/ACTUAT Metered Dose Nasal Spray
        "1115577",  # fentanyl 0.4 MG/ACTUAT Metered Dose Nasal Spray
        "1148478",  # 24 HR tramadol hydrochloride 100 MG Extended Release Oral Capsule
        "1148485",  # 24 HR tramadol hydrochloride 200 MG Extended Release Oral Capsule
        "1148489",  # 24 HR tramadol hydrochloride 300 MG Extended Release Oral Capsule
        "1148797",  # 12 HR tapentadol 100 MG Extended Release Oral Tablet
        "1148800",  # 12 HR tapentadol 150 MG Extended Release Oral Tablet
        "1148803",  # 12 HR tapentadol 200 MG Extended Release Oral Tablet
        "1148807",  # 12 HR tapentadol 250 MG Extended Release Oral Tablet
        "1148809",  # 12 HR tapentadol 50 MG Extended Release Oral Tablet
        "1190580",  # codeine phosphate 1.2 MG/ML / dexbrompheniramine maleate 0.133 MG/ML / pseudoephedrine hydrochloride 4 MG/ML Oral Solution
        "1235862",  # chlorcyclizine hydrochloride 2.5 MG/ML / codeine phosphate 1.8 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1237050",  # fentanyl 0.1 MG/ACTUAT Mucosal Spray
        "1237057",  # fentanyl 0.2 MG/ACTUAT Mucosal Spray
        "1237060",  # fentanyl 0.4 MG/ACTUAT Mucosal Spray
        "1237064",  # fentanyl 0.6 MG/ACTUAT Mucosal Spray
        "1237068",  # fentanyl 0.8 MG/ACTUAT Mucosal Spray
        "1248115",  # 24 HR tramadol hydrochloride 150 MG Extended Release Oral Capsule
        "1303736",  # morphine sulfate 40 MG Extended Release Oral Capsule
        "1306898",  # 24 HR hydromorphone hydrochloride 32 MG Extended Release Oral Tablet
        "1307056",  # buprenorphine 4 MG / naloxone 1 MG Sublingual Film
        "1307061",  # buprenorphine 12 MG / naloxone 3 MG Sublingual Film
        "1356797",  # brompheniramine maleate 4 MG / codeine phosphate 10 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1356800",  # brompheniramine maleate 4 MG / codeine phosphate 10 MG Oral Tablet
        "1356804",  # brompheniramine maleate 4 MG / codeine phosphate 20 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1356807",  # brompheniramine maleate 4 MG / codeine phosphate 20 MG Oral Tablet
        "1366873",  # hydrocodone bitartrate 5 MG / pseudoephedrine hydrochloride 60 MG Oral Tablet
        "1431076",  # buprenorphine 1.4 MG / naloxone 0.36 MG Sublingual Tablet
        "1431102",  # buprenorphine 5.7 MG / naloxone 1.4 MG Sublingual Tablet
        "1431286",  # acetaminophen 300 MG / butalbital 50 MG / caffeine 40 MG / codeine phosphate 30 MG Oral Capsule
        "1432969",  # 168 HR buprenorphine 0.015 MG/HR Transdermal System
        "1440003",  # codeine phosphate 1.8 MG/ML / dexchlorpheniramine maleate 0.2 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "1541630",  # brompheniramine maleate 0.8 MG/ML / codeine phosphate 2 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "1542390",  # buprenorphine 2.1 MG / naloxone 0.3 MG Buccal Film
        "1542997",  # 168 HR buprenorphine 0.0075 MG/HR Transdermal System
        "1544851",  # buprenorphine 4.2 MG / naloxone 0.7 MG Buccal Film
        "1544854",  # buprenorphine 6.3 MG / naloxone 1 MG Buccal Film
        "1595730",  # Abuse-Deterrent 24 HR hydrocodone bitartrate 20 MG Extended Release Oral Tablet
        "1595740",  # Abuse-Deterrent 24 HR hydrocodone bitartrate 30 MG Extended Release Oral Tablet
        "1595746",  # Abuse-Deterrent 24 HR hydrocodone bitartrate 40 MG Extended Release Oral Tablet
        "1595752",  # Abuse-Deterrent 24 HR hydrocodone bitartrate 60 MG Extended Release Oral Tablet
        "1595758",  # Abuse-Deterrent 24 HR hydrocodone bitartrate 80 MG Extended Release Oral Tablet
        "1595764",  # Abuse-Deterrent 24 HR hydrocodone bitartrate 100 MG Extended Release Oral Tablet
        "1595770",  # Abuse-Deterrent 24 HR hydrocodone bitartrate 120 MG Extended Release Oral Tablet
        "1596108",  # acetaminophen 320.5 MG / caffeine 30 MG / dihydrocodeine bitartrate 16 MG Oral Capsule
        "1597568",  # buprenorphine 11.4 MG / naloxone 2.9 MG Sublingual Tablet
        "1597573",  # buprenorphine 8.6 MG / naloxone 2.1 MG Sublingual Tablet
        "1603495",  # 72 HR fentanyl 0.0375 MG/HR Transdermal System
        "1603498",  # 72 HR fentanyl 0.0625 MG/HR Transdermal System
        "1603501",  # 72 HR fentanyl 0.0875 MG/HR Transdermal System
        "1651558",  # guaifenesin 40 MG/ML / hydrocodone bitartrate 0.5 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1652087",  # 12 HR chlorpheniramine polistirex 0.8 MG/ML / codeine polistirex 4 MG/ML Extended Release Suspension
        "1661319",  # codeine phosphate 2 MG/ML / phenylephrine hydrochloride 2 MG/ML / triprolidine hydrochloride 0.5 MG/ML Oral Solution
        "1664543",  # 12 HR chlorpheniramine maleate 8 MG / codeine phosphate 54.3 MG Extended Release Oral Tablet
        "1666338",  # buprenorphine 2.9 MG / naloxone 0.71 MG Sublingual Tablet
        "1666831",  # 80 ACTUAT fentanyl 0.04 MG/ACTUAT Transdermal System
        "1716057",  # buprenorphine 0.15 MG Buccal Film
        "1716065",  # buprenorphine 0.3 MG Buccal Film
        "1716069",  # buprenorphine 0.45 MG Buccal Film
        "1716073",  # buprenorphine 0.6 MG Buccal Film
        "1716077",  # buprenorphine 0.075 MG Buccal Film
        "1716081",  # buprenorphine 0.75 MG Buccal Film
        "1716086",  # buprenorphine 0.9 MG Buccal Film
        "1729320",  # fentanyl 0.3 MG/ACTUAT Metered Dose Nasal Spray
        "1740007",  # {2 (fentanyl 0.6 MG/ACTUAT Mucosal Spray) } Pack
        "1740009",  # {2 (fentanyl 0.8 MG/ACTUAT Mucosal Spray) } Pack
        "1790527",  # Abuse-Deterrent 12 HR oxycodone 9 MG Extended Release Oral Capsule
        "1791558",  # Abuse-Deterrent 12 HR oxycodone 13.5 MG Extended Release Oral Capsule
        "1791567",  # Abuse-Deterrent 12 HR oxycodone 18 MG Extended Release Oral Capsule
        "1791574",  # Abuse-Deterrent 12 HR oxycodone 27 MG Extended Release Oral Capsule
        "1791580",  # Abuse-Deterrent 12 HR oxycodone 36 MG Extended Release Oral Capsule
        "1792707",  # codeine phosphate 2 MG/ML / guaifenesin 40 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1797650",  # buprenorphine 74.2 MG Drug Implant
        "1812164",  # acetaminophen 325 MG / caffeine 30 MG / dihydrocodeine bitartrate 16 MG Oral Tablet
        "1860127",  # Abuse-Deterrent 12 HR oxycodone hydrochloride 60 MG Extended Release Oral Tablet
        "1860129",  # Abuse-Deterrent 12 HR oxycodone hydrochloride 20 MG Extended Release Oral Tablet
        "1860137",  # Abuse-Deterrent 12 HR oxycodone hydrochloride 40 MG Extended Release Oral Tablet
        "1860148",  # Abuse-Deterrent 12 HR oxycodone hydrochloride 80 MG Extended Release Oral Tablet
        "1860151",  # Abuse-Deterrent 12 HR oxycodone hydrochloride 30 MG Extended Release Oral Tablet
        "1860154",  # Abuse-Deterrent 12 HR oxycodone hydrochloride 15 MG Extended Release Oral Tablet
        "1860157",  # Abuse-Deterrent 12 HR oxycodone hydrochloride 10 MG Extended Release Oral Tablet
        "1860491",  # 12 HR hydrocodone bitartrate 10 MG Extended Release Oral Capsule
        "1860493",  # 12 HR hydrocodone bitartrate 15 MG Extended Release Oral Capsule
        "1860495",  # 12 HR hydrocodone bitartrate 20 MG Extended Release Oral Capsule
        "1860497",  # 12 HR hydrocodone bitartrate 30 MG Extended Release Oral Capsule
        "1860499",  # 12 HR hydrocodone bitartrate 40 MG Extended Release Oral Capsule
        "1860501",  # 12 HR hydrocodone bitartrate 50 MG Extended Release Oral Capsule
        "1864412",  # buprenorphine 0.7 MG / naloxone 0.18 MG Sublingual Tablet
        "1871434",  # Abuse-Deterrent 12 HR morphine sulfate 15 MG Extended Release Oral Tablet
        "1871441",  # Abuse-Deterrent 12 HR morphine sulfate 30 MG Extended Release Oral Tablet
        "1871444",  # Abuse-Deterrent 12 HR morphine sulfate 60 MG Extended Release Oral Tablet
        "1944529",  # Abuse-Deterrent oxycodone hydrochloride 15 MG Oral Tablet
        "1944538",  # Abuse-Deterrent oxycodone hydrochloride 30 MG Oral Tablet
        "1944541",  # Abuse-Deterrent oxycodone hydrochloride 5 MG Oral Tablet
        "1946525",  # Matrix Delivery 24 HR tramadol hydrochloride 300 MG Extended Release Oral Tablet
        "1946527",  # Matrix Delivery 24 HR tramadol hydrochloride 200 MG Extended Release Oral Tablet
        "1946529",  # Matrix Delivery 24 HR tramadol hydrochloride 100 MG Extended Release Oral Tablet
        "197696",  # 72 HR fentanyl 0.075 MG/HR Transdermal System
        "197873",  # levorphanol tartrate 2 MG Oral Tablet
        "2001358",  # acetaminophen 325 MG / benzhydrocodone 6.12 MG Oral Tablet
        "2056893",  # chlorpheniramine maleate 0.8 MG/ML / codeine phosphate 2 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "2058845",  # levorphanol tartrate 3 MG Oral Tablet
        "2103192",  # sufentanil 0.03 MG Sublingual Tablet
        "2105822",  # acetaminophen 60 MG/ML / oxycodone hydrochloride 2 MG/ML Oral Solution
        "2118728",  # acetaminophen 325 MG / benzhydrocodone 4.08 MG Oral Tablet
        "2118732",  # acetaminophen 325 MG / benzhydrocodone 8.16 MG Oral Tablet
        "2179635",  # tramadol hydrochloride 100 MG Oral Tablet
        "2395808",  # tramadol hydrochloride 5 MG/ML Oral Solution
        "245134",  # 72 HR fentanyl 0.025 MG/HR Transdermal System
        "245135",  # 72 HR fentanyl 0.05 MG/HR Transdermal System
        "245136",  # 72 HR fentanyl 0.1 MG/HR Transdermal System
        "2588478",  # celecoxib 56 MG / tramadol hydrochloride 44 MG Oral Tablet
        "2670390",  # tramadol hydrochloride 25 MG Oral Tablet
        "310293",  # fentanyl 1.2 MG Oral Lozenge
        "310294",  # fentanyl 1.6 MG Oral Lozenge
        "310295",  # fentanyl 0.2 MG Oral Lozenge
        "310297",  # fentanyl 0.4 MG Oral Lozenge
        "312104",  # belladonna alkaloids 16.2 MG / opium 30 MG Rectal Suppository
        "312107",  # belladonna alkaloids 16.2 MG / opium 60 MG Rectal Suppository
        "312289",  # naloxone 0.5 MG / pentazocine 50 MG Oral Tablet
        "313992",  # fentanyl 0.6 MG Oral Lozenge
        "313993",  # fentanyl 0.8 MG Oral Lozenge
        "351264",  # buprenorphine 2 MG Sublingual Tablet
        "351265",  # buprenorphine 8 MG Sublingual Tablet
        "351266",  # buprenorphine 2 MG / naloxone 0.5 MG Sublingual Tablet
        "351267",  # buprenorphine 8 MG / naloxone 2 MG Sublingual Tablet
        "577057",  # 72 HR fentanyl 0.012 MG/HR Transdermal System
        "637540",  # aspirin 325 MG / oxycodone hydrochloride 4.5 MG / oxycodone terephthalate 0.38 MG Oral Tablet
        "668363",  # fentanyl 0.1 MG Buccal Tablet
        "668364",  # fentanyl 0.2 MG Buccal Tablet
        "668365",  # fentanyl 0.4 MG Buccal Tablet
        "668366",  # fentanyl 0.6 MG Buccal Tablet
        "668367",  # fentanyl 0.8 MG Buccal Tablet
        "825409",  # tapentadol 100 MG Oral Tablet
        "825411",  # tapentadol 50 MG Oral Tablet
        "825413",  # tapentadol 75 MG Oral Tablet
        "830196",  # opium tincture 100 MG/ML Oral Solution
        "833709",  # 24 HR tramadol hydrochloride 100 MG Extended Release Oral Tablet
        "833711",  # 24 HR tramadol hydrochloride 200 MG Extended Release Oral Tablet
        "833713",  # 24 HR tramadol hydrochloride 300 MG Extended Release Oral Tablet
        "835603",  # tramadol hydrochloride 50 MG Oral Tablet
        "836395",  # acetaminophen 325 MG / tramadol hydrochloride 37.5 MG Oral Tablet
        "848768",  # aspirin 325 MG / oxycodone hydrochloride 4.84 MG Oral Tablet
        "856940",  # acetaminophen 21.7 MG/ML / hydrocodone bitartrate 0.5 MG/ML Oral Solution
        "856944",  # acetaminophen 21.7 MG/ML / hydrocodone bitartrate 0.67 MG/ML Oral Solution
        "856980",  # acetaminophen 300 MG / hydrocodone bitartrate 10 MG Oral Tablet
        "856987",  # acetaminophen 300 MG / hydrocodone bitartrate 5 MG Oral Tablet
        "856992",  # acetaminophen 300 MG / hydrocodone bitartrate 7.5 MG Oral Tablet
        "856999",  # acetaminophen 325 MG / hydrocodone bitartrate 10 MG Oral Tablet
        "857002",  # acetaminophen 325 MG / hydrocodone bitartrate 5 MG Oral Tablet
        "857005",  # acetaminophen 325 MG / hydrocodone bitartrate 7.5 MG Oral Tablet
        "857099",  # acetaminophen 33.3 MG/ML / hydrocodone bitartrate 0.5 MG/ML Oral Solution
        "857121",  # aspirin 500 MG / hydrocodone bitartrate 5 MG Oral Tablet
        "857131",  # acetaminophen 400 MG / hydrocodone bitartrate 5 MG Oral Tablet
        "857391",  # acetaminophen 325 MG / hydrocodone bitartrate 2.5 MG Oral Tablet
        "857512",  # 12 HR chlorpheniramine polistirex 8 MG / hydrocodone polistirex 10 MG Extended Release Oral Capsule
        "858770",  # hydrocodone bitartrate 2.5 MG / ibuprofen 200 MG Oral Tablet
        "858778",  # hydrocodone bitartrate 5 MG / ibuprofen 200 MG Oral Tablet
        "858798",  # hydrocodone bitartrate 7.5 MG / ibuprofen 200 MG Oral Tablet
        "859315",  # hydrocodone bitartrate 10 MG / ibuprofen 200 MG Oral Tablet
        "859383",  # guaifenesin 40 MG/ML / hydrocodone bitartrate 0.5 MG/ML Oral Solution
        "861455",  # meperidine hydrochloride 100 MG Oral Tablet
        "861467",  # meperidine hydrochloride 50 MG Oral Tablet
        "861479",  # meperidine hydrochloride 10 MG/ML Oral Solution
        "863845",  # Abuse-Deterrent morphine sulfate 100 MG / naltrexone hydrochloride 4 MG Extended Release Oral Capsule
        "863848",  # Abuse-Deterrent morphine sulfate 20 MG / naltrexone hydrochloride 0.8 MG Extended Release Oral Capsule
        "863850",  # Abuse-Deterrent morphine sulfate 30 MG / naltrexone hydrochloride 1.2 MG Extended Release Oral Capsule
        "863852",  # Abuse-Deterrent morphine sulfate 50 MG / naltrexone hydrochloride 2 MG Extended Release Oral Capsule
        "863854",  # Abuse-Deterrent morphine sulfate 60 MG / naltrexone hydrochloride 2.4 MG Extended Release Oral Capsule
        "863856",  # Abuse-Deterrent morphine sulfate 80 MG / naltrexone hydrochloride 3.2 MG Extended Release Oral Capsule
        "864706",  # methadone hydrochloride 10 MG Oral Tablet
        "864718",  # methadone hydrochloride 5 MG Oral Tablet
        "864761",  # methadone hydrochloride 1 MG/ML Oral Solution
        "864769",  # methadone hydrochloride 2 MG/ML Oral Solution
        "864978",  # methadone hydrochloride 40 MG Tablet for Oral Suspension
        "886634",  # butorphanol tartrate 1 MG/ACTUAT Metered Dose Nasal Spray
        "891874",  # morphine sulfate 100 MG Extended Release Oral Tablet
        "891881",  # morphine sulfate 15 MG Extended Release Oral Tablet
        "891888",  # morphine sulfate 30 MG Extended Release Oral Tablet
        "891893",  # morphine sulfate 60 MG Extended Release Oral Tablet
        "892297",  # 24 HR morphine sulfate 120 MG Extended Release Oral Capsule
        "892342",  # 24 HR morphine sulfate 30 MG Extended Release Oral Capsule
        "892345",  # morphine sulfate 30 MG Extended Release Oral Capsule
        "892349",  # 24 HR morphine sulfate 60 MG Extended Release Oral Capsule
        "892352",  # morphine sulfate 60 MG Extended Release Oral Capsule
        "892355",  # 24 HR morphine sulfate 90 MG Extended Release Oral Capsule
        "892494",  # morphine sulfate 10 MG Extended Release Oral Capsule
        "892516",  # morphine sulfate 10 MG Rectal Suppository
        "892554",  # morphine sulfate 100 MG Extended Release Oral Capsule
        "892582",  # morphine sulfate 15 MG Oral Tablet
        "892589",  # morphine sulfate 2 MG/ML Oral Solution
        "892596",  # morphine sulfate 20 MG Extended Release Oral Capsule
        "892603",  # morphine sulfate 20 MG Rectal Suppository
        "892625",  # morphine sulfate 20 MG/ML Oral Solution
        "892643",  # morphine sulfate 200 MG Extended Release Oral Capsule
        "892646",  # morphine sulfate 200 MG Extended Release Oral Tablet
        "892672",  # morphine sulfate 30 MG Oral Tablet
        "892678",  # morphine sulfate 30 MG Rectal Suppository
        "894780",  # morphine sulfate 4 MG/ML Oral Solution
        "894801",  # morphine sulfate 50 MG Extended Release Oral Capsule
        "894807",  # morphine sulfate 5 MG Rectal Suppository
        "894814",  # morphine sulfate 80 MG Extended Release Oral Capsule
        "894942",  # 24 HR morphine sulfate 45 MG Extended Release Oral Capsule
        "894970",  # 24 HR morphine sulfate 75 MG Extended Release Oral Capsule
        "897657",  # hydromorphone hydrochloride 1 MG/ML Oral Solution
        "897696",  # hydromorphone hydrochloride 2 MG Oral Tablet
        "897702",  # hydromorphone hydrochloride 4 MG Oral Tablet
        "897710",  # hydromorphone hydrochloride 8 MG Oral Tablet
        "897749",  # hydromorphone hydrochloride 3 MG Rectal Suppository
        "902729",  # 24 HR hydromorphone hydrochloride 12 MG Extended Release Oral Tablet
        "902736",  # 24 HR hydromorphone hydrochloride 16 MG Extended Release Oral Tablet
        "902741",  # 24 HR hydromorphone hydrochloride 8 MG Extended Release Oral Tablet
        "904870",  # 168 HR buprenorphine 0.01 MG/HR Transdermal System
        "904876",  # 168 HR buprenorphine 0.02 MG/HR Transdermal System
        "904880",  # 168 HR buprenorphine 0.005 MG/HR Transdermal System
        "977874",  # 12 HR oxymorphone hydrochloride 10 MG Extended Release Oral Tablet
        "977894",  # 12 HR oxymorphone hydrochloride 15 MG Extended Release Oral Tablet
        "977902",  # 12 HR oxymorphone hydrochloride 20 MG Extended Release Oral Tablet
        "977909",  # 12 HR oxymorphone hydrochloride 30 MG Extended Release Oral Tablet
        "977915",  # 12 HR oxymorphone hydrochloride 40 MG Extended Release Oral Tablet
        "977923",  # 12 HR oxymorphone hydrochloride 5 MG Extended Release Oral Tablet
        "977929",  # 12 HR oxymorphone hydrochloride 7.5 MG Extended Release Oral Tablet
        "977939",  # oxymorphone hydrochloride 5 MG Oral Tablet
        "977942",  # oxymorphone hydrochloride 10 MG Oral Tablet
        "991147",  # methadone hydrochloride 10 MG/ML Oral Solution
        "991486",  # codeine phosphate 2 MG/ML / promethazine hydrochloride 1.25 MG/ML Oral Solution
        "992656",  # homatropine methylbromide 1.5 MG / hydrocodone bitartrate 5 MG Oral Tablet
        "992668",  # homatropine methylbromide 0.3 MG/ML / hydrocodone bitartrate 1 MG/ML Oral Solution
        "993755",  # acetaminophen 24 MG/ML / codeine phosphate 2.4 MG/ML Oral Solution
        "993770",  # acetaminophen 300 MG / codeine phosphate 15 MG Oral Tablet
        "993781",  # acetaminophen 300 MG / codeine phosphate 30 MG Oral Tablet
        "993890",  # acetaminophen 300 MG / codeine phosphate 60 MG Oral Tablet
        "993943",  # acetaminophen 325 MG / butalbital 50 MG / caffeine 40 MG / codeine phosphate 30 MG Oral Capsule
        "994226",  # aspirin 325 MG / carisoprodol 200 MG / codeine phosphate 16 MG Oral Tablet
        "994237",  # aspirin 325 MG / butalbital 50 MG / caffeine 40 MG / codeine phosphate 30 MG Oral Capsule
        "994289",  # brompheniramine maleate 0.27 MG/ML / codeine phosphate 1.27 MG/ML / pseudoephedrine hydrochloride 2 MG/ML Oral Solution
        "994402",  # brompheniramine maleate 0.4 MG/ML / codeine phosphate 1.5 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
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
        "995226",  # codeine phosphate 0.5 MG/ML / guaifenesin 15 MG/ML Oral Solution
        "995438",  # codeine phosphate 1.26 MG/ML / guaifenesin 20 MG/ML Oral Solution
        "995441",  # codeine phosphate 1.5 MG/ML / guaifenesin 45 MG/ML Oral Solution
        "995450",  # codeine phosphate 10 MG / guaifenesin 300 MG Oral Tablet
        "995483",  # codeine phosphate 2 MG/ML / guaifenesin 40 MG/ML Oral Solution
        "995868",  # codeine phosphate 2 MG/ML / guaifenesin 20 MG/ML Oral Solution
        "995983",  # codeine phosphate 2 MG/ML / guaifenesin 20 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "996580",  # codeine phosphate 2 MG/ML / phenylephrine hydrochloride 1 MG/ML / pyrilamine maleate 1 MG/ML Oral Solution
        "996655",  # codeine phosphate 2 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "996706",  # codeine phosphate 20 MG / guaifenesin 400 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "996710",  # codeine phosphate 20 MG / guaifenesin 400 MG / pseudoephedrine hydrochloride 20 MG Oral Tablet
        "996714",  # codeine phosphate 20 MG / guaifenesin 400 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet
        "996725",  # codeine phosphate 20 MG / guaifenesin 400 MG Oral Tablet
        "996728",  # codeine phosphate 20 MG / pseudoephedrine hydrochloride 60 MG Oral Capsule
        "996736",  # codeine phosphate 9 MG / guaifenesin 200 MG Oral Capsule
        "996757",  # codeine phosphate 2 MG/ML / phenylephrine hydrochloride 1 MG/ML / promethazine hydrochloride 1.25 MG/ML Oral Solution
        "996998",  # brompheniramine maleate 0.266 MG/ML / codeine phosphate 1.27 MG/ML / phenylephrine hydrochloride 0.666 MG/ML Oral Solution
        "997170",  # codeine sulfate 15 MG Oral Tablet
        "997287",  # codeine sulfate 30 MG Oral Tablet
        "997296",  # codeine sulfate 60 MG Oral Tablet
    }

class AntithromboticTherapyForIschemicStroke(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of medications that are anticoagulant and antiplatelet medications used to reduce stroke mortality and morbidity.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication that is an antithrombotic medication, including oral, rectal, and injectable dose forms.

    **Exclusion Criteria:** Excludes concepts that represent enoxaparin and heparin generally given for VTE prophylaxis.
    """

    VALUE_SET_NAME = "Antithrombotic Therapy for Ischemic Stroke"
    OID = "2.16.840.1.113762.1.4.1110.62"
    DEFINITION_VERSION = "20210409"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1037045",  # dabigatran etexilate 150 MG Oral Capsule
        "1037179",  # dabigatran etexilate 75 MG Oral Capsule
        "1092398",  # aspirin 500 MG / diphenhydramine hydrochloride 25 MG Oral Tablet
        "1114198",  # rivaroxaban 10 MG Oral Tablet
        "1116635",  # ticagrelor 90 MG Oral Tablet
        "1232082",  # rivaroxaban 15 MG Oral Tablet
        "1232086",  # rivaroxaban 20 MG Oral Tablet
        "1250907",  # aspirin 500 MG / diphenhydramine citrate 38.3 MG Oral Tablet
        "1361574",  # heparin sodium, porcine 20000 UNT/ML Injectable Solution
        "1364435",  # apixaban 2.5 MG Oral Tablet
        "1364445",  # apixaban 5 MG Oral Tablet
        "1536467",  # aspirin 325 MG / citric acid 1000 MG / sodium bicarbonate 1700 MG Effervescent Oral Tablet
        "1536498",  # aspirin 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet
        "1536503",  # aspirin 500 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet
        "1536675",  # aspirin 325 MG / citric acid 1000 MG / sodium bicarbonate 1916 MG Effervescent Oral Tablet
        "1536815",  # aspirin 500 MG / caffeine 65 MG Effervescent Oral Tablet
        "1536833",  # aspirin 500 MG / citric acid 1000 MG / sodium bicarbonate 1985 MG Effervescent Oral Tablet
        "1536840",  # aspirin 325 MG / chlorpheniramine maleate 2 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet
        "1537029",  # aspirin 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet
        "1549682",  # {42 (rivaroxaban 15 MG Oral Tablet) / 9 (rivaroxaban 20 MG Oral Tablet) } Pack
        "1593110",  # acetaminophen 250 MG / aspirin 250 MG / diphenhydramine citrate 38 MG Oral Tablet
        "1599543",  # edoxaban 15 MG Oral Tablet
        "1599551",  # edoxaban 30 MG Oral Tablet
        "1599555",  # edoxaban 60 MG Oral Tablet
        "1658717",  # 250 ML heparin sodium, porcine 100 UNT/ML Injection
        "1659195",  # 500 ML heparin sodium, porcine 50 UNT/ML Injection
        "1659197",  # 250 ML heparin sodium, porcine 50 UNT/ML Injection
        "1665356",  # 24 HR aspirin 162.5 MG Extended Release Oral Capsule
        "1666332",  # ticagrelor 60 MG Oral Tablet
        "1722689",  # aspirin 81 MG / calcium carbonate 777 MG Oral Tablet
        "1723476",  # dabigatran etexilate 110 MG Oral Capsule
        "1730187",  # {1 (aspirin 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet) / 1 (aspirin 500 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet) } Pack
        "1804735",  # 50 ML argatroban 1 MG/ML Injection
        "1804737",  # 125 ML argatroban 1 MG/ML Injection
        "1811631",  # aspirin 81 MG / omeprazole 40 MG Delayed Release Oral Tablet
        "1811632",  # aspirin 325 MG / omeprazole 40 MG Delayed Release Oral Tablet
        "197447",  # aspirin 325 MG / carisoprodol 200 MG Oral Tablet
        "197945",  # aspirin 325 MG / methocarbamol 400 MG Oral Tablet
        "198464",  # aspirin 300 MG Rectal Suppository
        "198466",  # aspirin 325 MG Oral Capsule
        "198467",  # aspirin 325 MG Delayed Release Oral Tablet
        "198471",  # aspirin 500 MG Oral Tablet
        "198475",  # aspirin 650 MG Oral Tablet
        "198479",  # aspirin 400 MG / caffeine 32 MG Oral Tablet
        "198480",  # aspirin 500 MG / caffeine 32 MG Oral Tablet
        "1992427",  # {74 (apixaban 5 MG Oral Tablet) } Pack
        "2059015",  # rivaroxaban 2.5 MG Oral Tablet
        "212033",  # aspirin 325 MG Oral Tablet
        "2267026",  # aspirin 1000 MG / caffeine 150 MG Oral Powder
        "2360605",  # acetaminophen 500 MG / aspirin 500 MG / caffeine 65 MG Oral Powder
        "238134",  # aspirin 325 MG / butalbital 50 MG / caffeine 40 MG Oral Capsule
        "238135",  # aspirin 325 MG / butalbital 50 MG / caffeine 40 MG Oral Tablet
        "243670",  # aspirin 81 MG Oral Tablet
        "243694",  # acetaminophen 194 MG / aspirin 227 MG / caffeine 33 MG Oral Tablet
        "252857",  # aspirin 81 MG Oral Capsule
        "2565491",  # aspirin 325 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet
        "2565492",  # {1 (aspirin 325 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet) / 1 (aspirin 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet) } Pack
        "2583731",  # aspirin 500 MG / butalbital 50 MG / caffeine 40 MG Oral Capsule
        "2588062",  # rivaroxaban 1 MG/ML Oral Suspension
        "2590616",  # dabigatran etexilate 110 MG Oral Pellet
        "2590620",  # dabigatran etexilate 150 MG Oral Pellet
        "2590623",  # dabigatran etexilate 20 MG Oral Pellet
        "2590627",  # dabigatran etexilate 30 MG Oral Pellet
        "2590631",  # dabigatran etexilate 40 MG Oral Pellet
        "2590635",  # dabigatran etexilate 50 MG Oral Pellet
        "259081",  # 12 HR aspirin 25 MG / dipyridamole 200 MG Extended Release Oral Capsule
        "2618839",  # 4 ML dalteparin sodium 2500 UNT/ML Injection
        "2626726",  # aspirin 650 MG / caffeine 65 MG Oral Powder
        "308278",  # acetaminophen 115 MG / aspirin 210 MG / caffeine 16 MG / salicylamide 65 MG Oral Tablet
        "308297",  # acetaminophen 250 MG / aspirin 250 MG / caffeine 65 MG Oral Tablet
        "308351",  # 2.5 ML argatroban 100 MG/ML Injection
        "308363",  # aspirin 325 MG / caffeine 16 MG / salicylamide 95 MG Oral Tablet
        "308409",  # aspirin 500 MG Delayed Release Oral Tablet
        "308411",  # aspirin 650 MG Delayed Release Oral Tablet
        "308416",  # aspirin 81 MG Delayed Release Oral Tablet
        "309362",  # clopidogrel 75 MG Oral Tablet
        "313406",  # ticlopidine hydrochloride 250 MG Oral Tablet
        "318272",  # aspirin 81 MG Chewable Tablet
        "359221",  # acetaminophen 110 MG / aspirin 162 MG / caffeine 32.4 MG / salicylamide 152 MG Oral Tablet
        "432638",  # acetaminophen 250 MG / aspirin 250 MG Oral Tablet
        "637540",  # aspirin 325 MG / oxycodone hydrochloride 4.5 MG / oxycodone terephthalate 0.38 MG Oral Tablet
        "692836",  # acetaminophen 325 MG / aspirin 500 MG / caffeine 65 MG Oral Powder
        "702316",  # aspirin 500 MG / caffeine 32.5 MG Oral Tablet
        "749196",  # clopidogrel 300 MG Oral Tablet
        "763111",  # acetaminophen 325 MG / aspirin 500 MG Oral Powder
        "763116",  # acetaminophen 260 MG / aspirin 520 MG / caffeine 32.5 MG Oral Powder
        "806446",  # aspirin 500 MG / caffeine 65 MG Oral Tablet
        "827318",  # acetaminophen 250 MG / aspirin 250 MG / caffeine 65 MG Oral Capsule
        "848768",  # aspirin 325 MG / oxycodone hydrochloride 4.84 MG Oral Tablet
        "854238",  # 0.6 ML enoxaparin sodium 100 MG/ML Prefilled Syringe
        "854241",  # 0.8 ML enoxaparin sodium 100 MG/ML Prefilled Syringe
        "854245",  # 0.8 ML enoxaparin sodium 150 MG/ML Prefilled Syringe
        "854248",  # 1 ML enoxaparin sodium 100 MG/ML Prefilled Syringe
        "854252",  # 1 ML enoxaparin sodium 150 MG/ML Prefilled Syringe
        "854255",  # enoxaparin sodium 100 MG/ML Injectable Solution
        "855288",  # warfarin sodium 1 MG Oral Tablet
        "855296",  # warfarin sodium 10 MG Oral Tablet
        "855302",  # warfarin sodium 2 MG Oral Tablet
        "855312",  # warfarin sodium 2.5 MG Oral Tablet
        "855318",  # warfarin sodium 3 MG Oral Tablet
        "855324",  # warfarin sodium 4 MG Oral Tablet
        "855332",  # warfarin sodium 5 MG Oral Tablet
        "855338",  # warfarin sodium 6 MG Oral Tablet
        "855344",  # warfarin sodium 7.5 MG Oral Tablet
        "857121",  # aspirin 500 MG / hydrocodone bitartrate 5 MG Oral Tablet
        "861356",  # 0.8 ML fondaparinux sodium 12.5 MG/ML Prefilled Syringe
        "861360",  # 0.5 ML fondaparinux sodium 5 MG/ML Prefilled Syringe
        "861363",  # 0.4 ML fondaparinux sodium 12.5 MG/ML Prefilled Syringe
        "861365",  # 0.6 ML fondaparinux sodium 12.5 MG/ML Prefilled Syringe
        "900528",  # aspirin 850 MG / caffeine 65 MG Oral Powder
        "978725",  # 0.2 ML dalteparin sodium 12500 UNT/ML Prefilled Syringe
        "978733",  # 0.2 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978736",  # 0.3 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978740",  # 0.5 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978744",  # 0.6 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978746",  # 0.72 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978755",  # 1 ML dalteparin sodium 10000 UNT/ML Prefilled Syringe
        "978759",  # dalteparin sodium 10000 UNT/ML Injectable Solution
        "978777",  # dalteparin sodium 25000 UNT/ML Injectable Solution
        "994226",  # aspirin 325 MG / carisoprodol 200 MG / codeine phosphate 16 MG Oral Tablet
        "994237",  # aspirin 325 MG / butalbital 50 MG / caffeine 40 MG / codeine phosphate 30 MG Oral Capsule
        "994430",  # aspirin 1000 MG / caffeine 65 MG Oral Powder
        "994435",  # aspirin 845 MG / caffeine 65 MG Oral Powder
        "994528",  # aspirin 385 MG / caffeine 30 MG / orphenadrine citrate 25 MG Oral Tablet
        "994535",  # aspirin 770 MG / caffeine 60 MG / orphenadrine citrate 50 MG Oral Tablet
    }

class PharmacologicalContraindicationsForAntithromboticTherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications indicating pharmacological contraindications for antithrombotic therapy.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for pharmacological contraindications for antithrombotic therapy.

    **Exclusion Criteria:** Excludes concepts that are not for human use and that are not prescribable in the US.
    """

    VALUE_SET_NAME = "Pharmacological Contraindications For Antithrombotic Therapy"
    OID = "2.16.840.1.113762.1.4.1110.52"
    DEFINITION_VERSION = "20220219"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "855812",  # prasugrel 10 MG Oral Tablet
        "855818",  # prasugrel 5 MG Oral Tablet
    }

class DirectThrombinInhibitor(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications that are direct thrombin inhibitors.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication that is a direct thrombin inhibitors.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Direct Thrombin Inhibitor"
    OID = "2.16.840.1.113883.3.117.1.7.1.205"
    DEFINITION_VERSION = "20240203"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1037045",  # dabigatran etexilate 150 MG Oral Capsule
        "1037179",  # dabigatran etexilate 75 MG Oral Capsule
        "1723476",  # dabigatran etexilate 110 MG Oral Capsule
        "1804735",  # 50 ML argatroban 1 MG/ML Injection
        "1804737",  # 125 ML argatroban 1 MG/ML Injection
        "1997015",  # 50 ML bivalirudin 5 MG/ML Injection
        "1997017",  # 100 ML bivalirudin 5 MG/ML Injection
        "2590616",  # dabigatran etexilate 110 MG Oral Pellet
        "2590620",  # dabigatran etexilate 150 MG Oral Pellet
        "2590623",  # dabigatran etexilate 20 MG Oral Pellet
        "2590627",  # dabigatran etexilate 30 MG Oral Pellet
        "2590631",  # dabigatran etexilate 40 MG Oral Pellet
        "2590635",  # dabigatran etexilate 50 MG Oral Pellet
        "308351",  # 2.5 ML argatroban 100 MG/ML Injection
        "308769",  # bivalirudin 250 MG Injection
    }

class GlycoproteinIibIiiaInhibitors(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications to identify glycoprotein IIb/IIIa inhibitors.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication that is a glycoprotein IIb/IIIa inhibitor.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Glycoprotein IIb IIIa Inhibitors"
    OID = "2.16.840.1.113762.1.4.1045.41"
    DEFINITION_VERSION = "20230117"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1736470",  # 10 ML eptifibatide 2 MG/ML Injection
        "1736477",  # 100 ML eptifibatide 2 MG/ML Injection
        "1737466",  # 100 ML tirofiban 0.05 MG/ML Injection
        "1737471",  # 250 ML tirofiban 0.05 MG/ML Injection
        "1813035",  # 15 ML tirofiban 0.25 MG/ML Injection
        "200349",  # 100 ML eptifibatide 0.75 MG/ML Injection
    }

class InjectableFactorXaInhibitorForVteProphylaxis(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications of injectable factor Xa inhibitors used for venous thromboembolism (VTE) prophylaxis.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication that is an injectable factor Xa inhibitor.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Injectable Factor Xa Inhibitor for VTE Prophylaxis"
    OID = "2.16.840.1.113883.3.117.1.7.1.211"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "861356",  # 0.8 ML fondaparinux sodium 12.5 MG/ML Prefilled Syringe
        "861360",  # 0.5 ML fondaparinux sodium 5 MG/ML Prefilled Syringe
        "861363",  # 0.4 ML fondaparinux sodium 12.5 MG/ML Prefilled Syringe
        "861365",  # 0.6 ML fondaparinux sodium 12.5 MG/ML Prefilled Syringe
    }

class LowDoseUnfractionatedHeparinForVteProphylaxis(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications of unfractionated heparin with strengths that could be used for venous thromboembolism (VTE) prophylaxis.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication that could reasonably be used to achieve a dose of at least 5000 units when administered subcutaneously.

    **Exclusion Criteria:** Excludes concepts that represent concentrations less than 250 units/mL.
    """

    VALUE_SET_NAME = "Low Dose Unfractionated Heparin for VTE Prophylaxis"
    OID = "2.16.840.1.113762.1.4.1045.39"
    DEFINITION_VERSION = "20240203"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1361226",  # heparin sodium, porcine 1000 UNT/ML Injectable Solution
        "1361574",  # heparin sodium, porcine 20000 UNT/ML Injectable Solution
        "1361615",  # heparin sodium, porcine 5000 UNT/ML Injectable Solution
        "1361853",  # 0.5 ML heparin sodium, porcine 10000 UNT/ML Cartridge
        "1362831",  # heparin sodium, porcine 10000 UNT/ML Injectable Solution
        "1658634",  # 0.5 ML heparin sodium, porcine 10000 UNT/ML Injection
        "1658637",  # 1 ML heparin sodium, porcine 10000 UNT/ML Injection
        "1658647",  # 2 ML heparin sodium, porcine 1000 UNT/ML Injection
        "1658659",  # 1 ML heparin sodium, porcine 1000 UNT/ML Injection
        "1659260",  # 1 ML heparin sodium, porcine 5000 UNT/ML Cartridge
        "1659263",  # 1 ML heparin sodium, porcine 5000 UNT/ML Injection
        "1798389",  # 1 ML heparin sodium, porcine 5000 UNT/ML Prefilled Syringe
        "2121591",  # 0.5 ML heparin sodium, porcine 10000 UNT/ML Prefilled Syringe
    }

class LowMolecularWeightHeparinForVteProphylaxis(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of medication for parenteral administration of low molecular weight heparin medications used for venous thromboembolism (VTE) prophylaxis.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for parenteral administration of low molecular weight heparin.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Low Molecular Weight Heparin for VTE Prophylaxis"
    OID = "2.16.840.1.113883.3.117.1.7.1.219"
    DEFINITION_VERSION = "20230117"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "2618839",  # 4 ML dalteparin sodium 2500 UNT/ML Injection
        "854228",  # 0.3 ML enoxaparin sodium 100 MG/ML Prefilled Syringe
        "854235",  # 0.4 ML enoxaparin sodium 100 MG/ML Prefilled Syringe
        "854238",  # 0.6 ML enoxaparin sodium 100 MG/ML Prefilled Syringe
        "854241",  # 0.8 ML enoxaparin sodium 100 MG/ML Prefilled Syringe
        "854245",  # 0.8 ML enoxaparin sodium 150 MG/ML Prefilled Syringe
        "854248",  # 1 ML enoxaparin sodium 100 MG/ML Prefilled Syringe
        "854252",  # 1 ML enoxaparin sodium 150 MG/ML Prefilled Syringe
        "854255",  # enoxaparin sodium 100 MG/ML Injectable Solution
        "978725",  # 0.2 ML dalteparin sodium 12500 UNT/ML Prefilled Syringe
        "978733",  # 0.2 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978736",  # 0.3 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978740",  # 0.5 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978744",  # 0.6 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978746",  # 0.72 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978755",  # 1 ML dalteparin sodium 10000 UNT/ML Prefilled Syringe
        "978759",  # dalteparin sodium 10000 UNT/ML Injectable Solution
        "978777",  # dalteparin sodium 25000 UNT/ML Injectable Solution
    }

class OralFactorXaInhibitorForVteProphylaxisOrVteTreatment(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications of oral factor Xa inhibitors indicated for venous thromboembolism (VTE) prophylaxis and treatment.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for oral forms of factor Xa inhibitors.

    **Exclusion Criteria:** Excludes concepts that represent dose forms of factor Xa inhibitors other than oral.
    """

    VALUE_SET_NAME = "Oral Factor Xa Inhibitor for VTE Prophylaxis or VTE Treatment"
    OID = "2.16.840.1.113883.3.117.1.7.1.134"
    DEFINITION_VERSION = "20220212"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1364435",  # apixaban 2.5 MG Oral Tablet
        "1364445",  # apixaban 5 MG Oral Tablet
        "1599543",  # edoxaban 15 MG Oral Tablet
        "1599551",  # edoxaban 30 MG Oral Tablet
        "1599555",  # edoxaban 60 MG Oral Tablet
        "1992427",  # {74 (apixaban 5 MG Oral Tablet) } Pack
    }

class RivaroxabanForVteProphylaxis(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications of rivaroxaban indicated for venous thromboembolism (VTE) prophylaxis and treatment.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for oral forms of rivaroxaban.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Rivaroxaban for VTE Prophylaxis"
    OID = "2.16.840.1.113762.1.4.1110.50"
    DEFINITION_VERSION = "20220219"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1114198",  # rivaroxaban 10 MG Oral Tablet
        "1232082",  # rivaroxaban 15 MG Oral Tablet
        "1232086",  # rivaroxaban 20 MG Oral Tablet
        "1549682",  # {42 (rivaroxaban 15 MG Oral Tablet) / 9 (rivaroxaban 20 MG Oral Tablet) } Pack
        "2059015",  # rivaroxaban 2.5 MG Oral Tablet
        "2588062",  # rivaroxaban 1 MG/ML Oral Suspension
    }

class UnfractionatedHeparin(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of medication for continuous infusion of heparin formulations to treat venous thromboembolism (VTE).

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication that could be used for continuous infusion of heparin and achieve therapeutic levels.

    **Exclusion Criteria:** Excludes concepts that describe concentrations < 250 UNT/ML (except those representing premixed heparin infusion bags, per inclusion criteria).
    """

    VALUE_SET_NAME = "Unfractionated Heparin"
    OID = "2.16.840.1.113883.3.117.1.7.1.218"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1361607",  # 500 ML heparin sodium, porcine 40 UNT/ML Injection
        "1658717",  # 250 ML heparin sodium, porcine 100 UNT/ML Injection
        "1659195",  # 500 ML heparin sodium, porcine 50 UNT/ML Injection
        "1659197",  # 250 ML heparin sodium, porcine 50 UNT/ML Injection
    }

class Warfarin(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications of warfarin administered to patients to reduce the risk of blood clot formation.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for single ingredient drug forms consistent with oral administration.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Warfarin"
    OID = "2.16.840.1.113883.3.117.1.7.1.232"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "855288",  # warfarin sodium 1 MG Oral Tablet
        "855296",  # warfarin sodium 10 MG Oral Tablet
        "855302",  # warfarin sodium 2 MG Oral Tablet
        "855312",  # warfarin sodium 2.5 MG Oral Tablet
        "855318",  # warfarin sodium 3 MG Oral Tablet
        "855324",  # warfarin sodium 4 MG Oral Tablet
        "855332",  # warfarin sodium 5 MG Oral Tablet
        "855338",  # warfarin sodium 6 MG Oral Tablet
        "855344",  # warfarin sodium 7.5 MG Oral Tablet
    }

class AnticoagulantMedications(ValueSet):
    """
    **Clinical Focus:** Commonly prescribed anticoagulants

    **Data Element Scope:** Anticoagulant medications active during measurement year

    **Inclusion Criteria:** Anticoagulant medications consist of: Apixaban, Argatroban, Bivalirudin, clopidogrel,Dabigatran, Dalteparin, Desirudin, Edoxaban, Enoxaparin, Fondaparinux, Heparin, Lepirudin, prasugrel, Rivaroxaban, Tinzaparin, or Warfarin.

    **Exclusion Criteria:** N/A
    """

    VALUE_SET_NAME = "Anticoagulant Medications"
    OID = "2.16.840.1.113762.1.4.1206.19"
    DEFINITION_VERSION = "20250205"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1037041",  # dabigatran etexilate mesylate
        "1037042",  # dabigatran etexilate
        "1037045",  # dabigatran etexilate 150 MG Oral Capsule
        "1037046",  # Pradaxa
        "1037049",  # dabigatran etexilate 150 MG Oral Capsule [Pradaxa]
        "1037179",  # dabigatran etexilate 75 MG Oral Capsule
        "1037181",  # dabigatran etexilate 75 MG Oral Capsule [Pradaxa]
        "105899",  # naproxen 500 MG Oral Tablet [Naprosyn]
        "10594",  # ticlopidine
        "1114195",  # rivaroxaban
        "1114199",  # Xarelto
        "11289",  # warfarin
        "114194",  # warfarin sodium
        "114934",  # desirudin
        "1361226",  # heparin sodium, porcine 1000 UNT/ML Injectable Solution
        "1361574",  # heparin sodium, porcine 20000 UNT/ML Injectable Solution
        "1361615",  # heparin sodium, porcine 5000 UNT/ML Injectable Solution
        "1362060",  # 2 ML heparin sodium, porcine 100 UNT/ML Prefilled Syringe
        "1362062",  # 3 ML heparin sodium, porcine 100 UNT/ML Prefilled Syringe
        "1362831",  # heparin sodium, porcine 10000 UNT/ML Injectable Solution
        "1364430",  # apixaban
        "1364436",  # Eliquis
        "1364445",  # apixaban 5 MG Oral Tablet
        "1364447",  # apixaban 5 MG Oral Tablet [Eliquis]
        "15202",  # argatroban
        "1599538",  # edoxaban
        "1599543",  # edoxaban 15 MG Oral Tablet
        "1599544",  # Savaysa
        "1599549",  # edoxaban 15 MG Oral Tablet [Savaysa]
        "1599551",  # edoxaban 30 MG Oral Tablet
        "1599553",  # edoxaban 30 MG Oral Tablet [Savaysa]
        "1599555",  # edoxaban 60 MG Oral Tablet
        "1599557",  # edoxaban 60 MG Oral Tablet [Savaysa]
        "1599564",  # edoxaban tosylate
        "1658634",  # 0.5 ML heparin sodium, porcine 10000 UNT/ML Injection
        "1658637",  # 1 ML heparin sodium, porcine 10000 UNT/ML Injection
        "1658647",  # 2 ML heparin sodium, porcine 1000 UNT/ML Injection
        "1658659",  # 1 ML heparin sodium, porcine 1000 UNT/ML Injection
        "1658690",  # 1000 ML heparin sodium, porcine 2 UNT/ML Injection
        "1658692",  # 500 ML heparin sodium, porcine 2 UNT/ML Injection
        "1658717",  # 250 ML heparin sodium, porcine 100 UNT/ML Injection
        "1659195",  # 500 ML heparin sodium, porcine 50 UNT/ML Injection
        "1659197",  # 250 ML heparin sodium, porcine 50 UNT/ML Injection
        "1659260",  # 1 ML heparin sodium, porcine 5000 UNT/ML Cartridge
        "1659263",  # 1 ML heparin sodium, porcine 5000 UNT/ML Injection
        "1723476",  # dabigatran etexilate 110 MG Oral Capsule
        "1723478",  # dabigatran etexilate 110 MG Oral Capsule [Pradaxa]
        "174742",  # Plavix
        "1798389",  # 1 ML heparin sodium, porcine 5000 UNT/ML Prefilled Syringe
        "1804735",  # 50 ML argatroban 1 MG/ML Injection
        "1804737",  # 125 ML argatroban 1 MG/ML Injection
        "1992427",  # {74 (apixaban 5 MG Oral Tablet) } Pack
        "1992428",  # {74 (apixaban 5 MG Oral Tablet [Eliquis]) } Pack [Eliquis 30-Day Starter Pack]
        "2059015",  # rivaroxaban 2.5 MG Oral Tablet
        "2059017",  # rivaroxaban 2.5 MG Oral Tablet [Xarelto]
        "21107",  # cilostazol
        "2121591",  # 0.5 ML heparin sodium, porcine 10000 UNT/ML Prefilled Syringe
        "213169",  # clopidogrel 75 MG Oral Tablet [Plavix]
        "221095",  # enoxaparin sodium
        "225036",  # Lovenox
        "236991",  # clopidogrel bisulfate
        "242461",  # cilostazol 100 MG Oral Tablet
        "242462",  # cilostazol 50 MG Oral Tablet
        "281554",  # Fragmin
        "284534",  # bivalirudin 250 MG Injection [Angiomax]
        "285044",  # Angiomax
        "308351",  # 2.5 ML argatroban 100 MG/ML Injection
        "308769",  # bivalirudin 250 MG Injection
        "309362",  # clopidogrel 75 MG Oral Tablet
        "313406",  # ticlopidine hydrochloride 250 MG Oral Tablet
        "314659",  # heparin sodium, porcine
        "321208",  # fondaparinux
        "322154",  # fondaparinux sodium
        "322155",  # Arixtra
        "32968",  # clopidogrel
        "402248",  # desirudin 15 MG Injection
        "405155",  # Jantoven
        "5224",  # heparin
        "60819",  # bivalirudin
        "613391",  # prasugrel
        "67108",  # enoxaparin
        "67109",  # dalteparin
        "749196",  # clopidogrel 300 MG Oral Tablet
        "749198",  # clopidogrel 300 MG Oral Tablet [Plavix]
        "82137",  # dalteparin sodium
        "847020",  # prasugrel hydrochloride
        "854228",  # 0.3 ML enoxaparin sodium 100 MG/ML Prefilled Syringe
        "854232",  # 0.3 ML enoxaparin sodium 100 MG/ML Prefilled Syringe [Lovenox]
        "854235",  # 0.4 ML enoxaparin sodium 100 MG/ML Prefilled Syringe
        "854236",  # 0.4 ML enoxaparin sodium 100 MG/ML Prefilled Syringe [Lovenox]
        "854238",  # 0.6 ML enoxaparin sodium 100 MG/ML Prefilled Syringe
        "854239",  # 0.6 ML enoxaparin sodium 100 MG/ML Prefilled Syringe [Lovenox]
        "854241",  # 0.8 ML enoxaparin sodium 100 MG/ML Prefilled Syringe
        "854242",  # 0.8 ML enoxaparin sodium 100 MG/ML Prefilled Syringe [Lovenox]
        "854245",  # 0.8 ML enoxaparin sodium 150 MG/ML Prefilled Syringe
        "854247",  # 0.8 ML enoxaparin sodium 150 MG/ML Prefilled Syringe [Lovenox]
        "854248",  # 1 ML enoxaparin sodium 100 MG/ML Prefilled Syringe
        "854249",  # 1 ML enoxaparin sodium 100 MG/ML Prefilled Syringe [Lovenox]
        "854252",  # 1 ML enoxaparin sodium 150 MG/ML Prefilled Syringe
        "854253",  # 1 ML enoxaparin sodium 150 MG/ML Prefilled Syringe [Lovenox]
        "854255",  # enoxaparin sodium 100 MG/ML Injectable Solution
        "854256",  # enoxaparin sodium 100 MG/ML Injectable Solution [Lovenox]
        "855288",  # warfarin sodium 1 MG Oral Tablet
        "855292",  # warfarin sodium 1 MG Oral Tablet [Jantoven]
        "855296",  # warfarin sodium 10 MG Oral Tablet
        "855300",  # warfarin sodium 10 MG Oral Tablet [Jantoven]
        "855302",  # warfarin sodium 2 MG Oral Tablet
        "855306",  # warfarin sodium 2 MG Oral Tablet [Jantoven]
        "855312",  # warfarin sodium 2.5 MG Oral Tablet
        "855316",  # warfarin sodium 2.5 MG Oral Tablet [Jantoven]
        "855318",  # warfarin sodium 3 MG Oral Tablet
        "855322",  # warfarin sodium 3 MG Oral Tablet [Jantoven]
        "855324",  # warfarin sodium 4 MG Oral Tablet
        "855328",  # warfarin sodium 4 MG Oral Tablet [Jantoven]
        "855332",  # warfarin sodium 5 MG Oral Tablet
        "855336",  # warfarin sodium 5 MG Oral Tablet [Jantoven]
        "855338",  # warfarin sodium 6 MG Oral Tablet
        "855342",  # warfarin sodium 6 MG Oral Tablet [Jantoven]
        "855344",  # warfarin sodium 7.5 MG Oral Tablet
        "855348",  # warfarin sodium 7.5 MG Oral Tablet [Jantoven]
        "855812",  # prasugrel 10 MG Oral Tablet
        "855813",  # Effient
        "855816",  # prasugrel 10 MG Oral Tablet [Effient]
        "855818",  # prasugrel 5 MG Oral Tablet
        "855820",  # prasugrel 5 MG Oral Tablet [Effient]
        "861356",  # 0.8 ML fondaparinux sodium 12.5 MG/ML Prefilled Syringe
        "861360",  # 0.5 ML fondaparinux sodium 5 MG/ML Prefilled Syringe
        "861362",  # 0.5 ML fondaparinux sodium 5 MG/ML Prefilled Syringe [Arixtra]
        "861363",  # 0.4 ML fondaparinux sodium 12.5 MG/ML Prefilled Syringe
        "861364",  # 0.4 ML fondaparinux sodium 12.5 MG/ML Prefilled Syringe [Arixtra]
        "861365",  # 0.6 ML fondaparinux sodium 12.5 MG/ML Prefilled Syringe
        "861366",  # 0.6 ML fondaparinux sodium 12.5 MG/ML Prefilled Syringe [Arixtra]
        "97",  # ticlopidine hydrochloride
        "978725",  # 0.2 ML dalteparin sodium 12500 UNT/ML Prefilled Syringe
        "978727",  # 0.2 ML dalteparin sodium 12500 UNT/ML Prefilled Syringe [Fragmin]
        "978733",  # 0.2 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978735",  # 0.2 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe [Fragmin]
        "978736",  # 0.3 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978737",  # 0.3 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe [Fragmin]
        "978740",  # 0.5 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978741",  # 0.5 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe [Fragmin]
        "978744",  # 0.6 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978745",  # 0.6 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe [Fragmin]
        "978746",  # 0.72 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978747",  # 0.72 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe [Fragmin]
        "978755",  # 1 ML dalteparin sodium 10000 UNT/ML Prefilled Syringe
        "978757",  # 1 ML dalteparin sodium 10000 UNT/ML Prefilled Syringe [Fragmin]
        "978759",  # dalteparin sodium 10000 UNT/ML Injectable Solution
        "978777",  # dalteparin sodium 25000 UNT/ML Injectable Solution
        "978778",  # dalteparin sodium 25000 UNT/ML Injectable Solution [Fragmin]
    }

class AntidepressantMedication(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for antidepressant medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable antidepressant medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Antidepressant Medication"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1213"
    DEFINITION_VERSION = "20210306"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1000048",  # doxepin 10 MG Oral Capsule
        "1000054",  # doxepin 10 MG/ML Oral Solution
        "1000058",  # doxepin 100 MG Oral Capsule
        "1000064",  # doxepin 150 MG Oral Capsule
        "1000070",  # doxepin 25 MG Oral Capsule
        "1000076",  # doxepin 50 MG Oral Capsule
        "1000097",  # doxepin 75 MG Oral Capsule
        "104837",  # isocarboxazid 10 MG Oral Tablet
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
        "1298861",  # maprotiline hydrochloride 50 MG Oral Tablet
        "1298870",  # maprotiline hydrochloride 75 MG Oral Tablet
        "1430122",  # paroxetine mesylate 7.5 MG Oral Capsule
        "1433217",  # 24 HR levomilnacipran 120 MG Extended Release Oral Capsule
        "1433227",  # 24 HR levomilnacipran 20 MG Extended Release Oral Capsule
        "1433233",  # 24 HR levomilnacipran 40 MG Extended Release Oral Capsule
        "1433239",  # 24 HR levomilnacipran 80 MG Extended Release Oral Capsule
        "1433249",  # {2 (24 HR levomilnacipran 20 MG Extended Release Oral Capsule) / 26 (24 HR levomilnacipran 40 MG Extended Release Oral Capsule) } Pack
        "1439808",  # vortioxetine 10 MG Oral Tablet
        "1439810",  # vortioxetine 20 MG Oral Tablet
        "1439812",  # vortioxetine 5 MG Oral Tablet
        "1607617",  # 24 HR desvenlafaxine succinate 25 MG Extended Release Oral Tablet
        "1653469",  # {7 (vilazodone hydrochloride 10 MG Oral Tablet) / 23 (vilazodone hydrochloride 20 MG Oral Tablet) } Pack
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
        "197363",  # amoxapine 100 MG Oral Tablet
        "197364",  # amoxapine 150 MG Oral Tablet
        "197365",  # amoxapine 25 MG Oral Tablet
        "197366",  # amoxapine 50 MG Oral Tablet
        "198045",  # nortriptyline 10 MG Oral Capsule
        "198046",  # nortriptyline 50 MG Oral Capsule
        "198047",  # nortriptyline 75 MG Oral Capsule
        "200371",  # citalopram 20 MG Oral Tablet
        "2200168",  # Sprinkle duloxetine 20 MG Delayed Release Oral Capsule
        "2200175",  # Sprinkle duloxetine 30 MG Delayed Release Oral Capsule
        "2200178",  # Sprinkle duloxetine 40 MG Delayed Release Oral Capsule
        "2200181",  # Sprinkle duloxetine 60 MG Delayed Release Oral Capsule
        "248642",  # fluoxetine 20 MG Oral Tablet
        "251201",  # sertraline 200 MG Oral Capsule
        "2532159",  # PMDD fluoxetine 10 MG Oral Tablet
        "2532163",  # PMDD fluoxetine 20 MG Oral Tablet
        "2591786",  # citalopram 30 MG Oral Capsule
        "2605950",  # 24 HR venlafaxine 112.5 MG Extended Release Oral Tablet
        "2636817",  # {2 (24 HR levomilnacipran 20 MG Extended Release Oral Capsule) / 5 (24 HR levomilnacipran 40 MG Extended Release Oral Capsule) } Pack
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
        "410584",  # sertraline 150 MG Oral Capsule
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
    }

class AceInhibitorOrArbOrArni(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of medications of angiotensin-converting enzyme (ACE) inhibitor, angiotensin-receptor blocker (ARB), and angiotensin receptor-neprilysin inhibitor (ARNI) therapies.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for angiotensin-converting enzyme (ACE) inhibitor, angiotensin-receptor blocker (ARB), and angiotensin receptor-neprilysin inhibitor (ARNI) therapies.s diuretic, ACEI plus calcium channel blocker, ARB plus calcium channel blocker, or ARB plus calcium channel blocker plus diuretic.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable branded drugs, components or ingredients.
    """

    VALUE_SET_NAME = "ACE Inhibitor or ARB or ARNI"
    OID = "2.16.840.1.113883.3.526.3.1139"
    DEFINITION_VERSION = "20210218"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
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
        "153822",  # candesartan cilexetil 4 MG Oral Tablet
        "153823",  # candesartan cilexetil 8 MG Oral Tablet
        "1600716",  # amlodipine 10 MG / perindopril arginine 14 MG Oral Tablet
        "1600724",  # amlodipine 2.5 MG / perindopril arginine 3.5 MG Oral Tablet
        "1600728",  # amlodipine 5 MG / perindopril arginine 7 MG Oral Tablet
        "1656340",  # sacubitril 24 MG / valsartan 26 MG Oral Tablet
        "1656349",  # sacubitril 49 MG / valsartan 51 MG Oral Tablet
        "1656354",  # sacubitril 97 MG / valsartan 103 MG Oral Tablet
        "1798281",  # nebivolol 5 MG / valsartan 80 MG Oral Tablet
        "1806884",  # lisinopril 1 MG/ML Oral Solution
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
        "1996254",  # valsartan 4 MG/ML Oral Solution
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
        "401965",  # ramipril 1.25 MG Oral Tablet
        "401968",  # ramipril 10 MG Oral Tablet
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
    }

class Atomoxetine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for atomoxetine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable atomoxetine and atomoxetine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Atomoxetine"
    OID = "2.16.840.1.113883.3.464.1003.1170"
    DEFINITION_VERSION = "20220902"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "349591",  # atomoxetine 10 MG Oral Capsule
        "349592",  # atomoxetine 18 MG Oral Capsule
        "349593",  # atomoxetine 25 MG Oral Capsule
        "349594",  # atomoxetine 40 MG Oral Capsule
        "349595",  # atomoxetine 60 MG Oral Capsule
        "608139",  # atomoxetine 100 MG Oral Capsule
        "608143",  # atomoxetine 80 MG Oral Capsule
    }

class Clonidine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for clonidine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable clonidine and clonidine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Clonidine"
    OID = "2.16.840.1.113883.3.464.1003.1171"
    DEFINITION_VERSION = "20240119"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1013930",  # 12 HR clonidine hydrochloride 0.1 MG Extended Release Oral Tablet
        "884173",  # clonidine hydrochloride 0.1 MG Oral Tablet
        "884185",  # clonidine hydrochloride 0.2 MG Oral Tablet
        "884189",  # clonidine hydrochloride 0.3 MG Oral Tablet
        "884221",  # 10 ML clonidine hydrochloride 0.1 MG/ML Injection
        "884225",  # 10 ML clonidine hydrochloride 0.5 MG/ML Injection
        "885880",  # 24 HR clonidine 0.17 MG Extended Release Oral Tablet
        "998671",  # 168 HR clonidine 0.00417 MG/HR Transdermal System
        "998675",  # 168 HR clonidine 0.00833 MG/HR Transdermal System
        "998679",  # 168 HR clonidine 0.0125 MG/HR Transdermal System
    }

class Dexmethylphenidate(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for dexmethylphenidate medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable dexmethylphenidate and dexmethylphenidate in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Dexmethylphenidate"
    OID = "2.16.840.1.113883.3.464.1003.1172"
    DEFINITION_VERSION = "20250109"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1006608",  # 24 HR dexmethylphenidate hydrochloride 40 MG Extended Release Oral Capsule
        "1101926",  # 24 HR dexmethylphenidate hydrochloride 25 MG Extended Release Oral Capsule
        "1101932",  # 24 HR dexmethylphenidate hydrochloride 35 MG Extended Release Oral Capsule
        "2562187",  # dexmethylphenidate 5.2 MG / serdexmethylphenidate 26.1 MG Oral Capsule
        "2562191",  # dexmethylphenidate 7.8 MG / serdexmethylphenidate 39.2 MG Oral Capsule
        "2562194",  # dexmethylphenidate 10.4 MG / serdexmethylphenidate 52.3 MG Oral Capsule
        "899439",  # 24 HR dexmethylphenidate hydrochloride 10 MG Extended Release Oral Capsule
        "899461",  # 24 HR dexmethylphenidate hydrochloride 15 MG Extended Release Oral Capsule
        "899485",  # 24 HR dexmethylphenidate hydrochloride 20 MG Extended Release Oral Capsule
        "899495",  # 24 HR dexmethylphenidate hydrochloride 30 MG Extended Release Oral Capsule
        "899511",  # 24 HR dexmethylphenidate hydrochloride 5 MG Extended Release Oral Capsule
        "899518",  # dexmethylphenidate hydrochloride 5 MG Oral Tablet
        "899548",  # dexmethylphenidate hydrochloride 10 MG Oral Tablet
        "899557",  # dexmethylphenidate hydrochloride 2.5 MG Oral Tablet
    }

class Dextroamphetamine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for dextroamphetamine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable dextroamphetamine and dextroamphetamine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Dextroamphetamine"
    OID = "2.16.840.1.113883.3.464.1003.1173"
    DEFINITION_VERSION = "20220902"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1009145",  # amphetamine aspartate 1.875 MG / amphetamine sulfate 1.875 MG / dextroamphetamine saccharate 1.875 MG / dextroamphetamine sulfate 1.875 MG Oral Tablet
        "1425847",  # dextroamphetamine sulfate 2.5 MG Oral Tablet
        "1425854",  # dextroamphetamine sulfate 7.5 MG Oral Tablet
        "1535454",  # dextroamphetamine sulfate 20 MG Oral Tablet
        "1535470",  # dextroamphetamine sulfate 30 MG Oral Tablet
        "1927610",  # 3-Bead 24 HR amphetamine aspartate 12.5 MG / amphetamine sulfate 12.5 MG / dextroamphetamine saccharate 12.5 MG / dextroamphetamine sulfate 12.5 MG Extended Release Oral Capsule
        "1927617",  # 3-Bead 24 HR amphetamine aspartate 6.25 MG / amphetamine sulfate 6.25 MG / dextroamphetamine saccharate 6.25 MG / dextroamphetamine sulfate 6.25 MG Extended Release Oral Capsule
        "1927630",  # 3-Bead 24 HR amphetamine aspartate 3.125 MG / amphetamine sulfate 3.125 MG / dextroamphetamine saccharate 3.125 MG / dextroamphetamine sulfate 3.125 MG Extended Release Oral Capsule
        "1927637",  # 3-Bead 24 HR amphetamine aspartate 9.375 MG / amphetamine sulfate 9.375 MG / dextroamphetamine saccharate 9.375 MG / dextroamphetamine sulfate 9.375 MG Extended Release Oral Capsule
        "541363",  # amphetamine aspartate 7.5 MG / amphetamine sulfate 7.5 MG / dextroamphetamine saccharate 7.5 MG / dextroamphetamine sulfate 7.5 MG Oral Tablet
        "541878",  # amphetamine aspartate 1.25 MG / amphetamine sulfate 1.25 MG / dextroamphetamine saccharate 1.25 MG / dextroamphetamine sulfate 1.25 MG Oral Tablet
        "541892",  # amphetamine aspartate 2.5 MG / amphetamine sulfate 2.5 MG / dextroamphetamine saccharate 2.5 MG / dextroamphetamine sulfate 2.5 MG Oral Tablet
        "577957",  # amphetamine aspartate 3.75 MG / amphetamine sulfate 3.75 MG / dextroamphetamine saccharate 3.75 MG / dextroamphetamine sulfate 3.75 MG Oral Tablet
        "577961",  # amphetamine aspartate 5 MG / amphetamine sulfate 5 MG / dextroamphetamine saccharate 5 MG / dextroamphetamine sulfate 5 MG Oral Tablet
        "687043",  # amphetamine aspartate 3.125 MG / amphetamine sulfate 3.125 MG / dextroamphetamine saccharate 3.125 MG / dextroamphetamine sulfate 3.125 MG Oral Tablet
        "861221",  # 24 HR amphetamine aspartate 2.5 MG / amphetamine sulfate 2.5 MG / dextroamphetamine saccharate 2.5 MG / dextroamphetamine sulfate 2.5 MG Extended Release Oral Capsule
        "861223",  # 24 HR amphetamine aspartate 3.75 MG / amphetamine sulfate 3.75 MG / dextroamphetamine saccharate 3.75 MG / dextroamphetamine sulfate 3.75 MG Extended Release Oral Capsule
        "861225",  # 24 HR amphetamine aspartate 5 MG / amphetamine sulfate 5 MG / dextroamphetamine saccharate 5 MG / dextroamphetamine sulfate 5 MG Extended Release Oral Capsule
        "861227",  # 24 HR amphetamine aspartate 6.25 MG / amphetamine sulfate 6.25 MG / dextroamphetamine saccharate 6.25 MG / dextroamphetamine sulfate 6.25 MG Extended Release Oral Capsule
        "861232",  # 24 HR amphetamine aspartate 7.5 MG / amphetamine sulfate 7.5 MG / dextroamphetamine saccharate 7.5 MG / dextroamphetamine sulfate 7.5 MG Extended Release Oral Capsule
        "861237",  # 24 HR amphetamine aspartate 1.25 MG / amphetamine sulfate 1.25 MG / dextroamphetamine saccharate 1.25 MG / dextroamphetamine sulfate 1.25 MG Extended Release Oral Capsule
        "884385",  # dextroamphetamine sulfate 10 MG Oral Tablet
        "884386",  # dextroamphetamine sulfate 5 MG Oral Tablet
        "884520",  # dextroamphetamine sulfate 10 MG Extended Release Oral Capsule
        "884522",  # dextroamphetamine sulfate 1 MG/ML Oral Solution
        "884532",  # dextroamphetamine sulfate 15 MG Extended Release Oral Capsule
        "884535",  # dextroamphetamine sulfate 5 MG Extended Release Oral Capsule
        "884684",  # dextroamphetamine sulfate 15 MG Oral Tablet
    }

class GuanfacineMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for guanfacine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable guanfacine and guanfacine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Guanfacine Medications"
    OID = "2.16.840.1.113883.3.464.1003.196.11.1252"
    DEFINITION_VERSION = "20240123"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "197745",  # guanfacine 1 MG Oral Tablet
        "197746",  # guanfacine 2 MG Oral Tablet
        "862006",  # 24 HR guanfacine 1 MG Extended Release Oral Tablet
        "862013",  # 24 HR guanfacine 2 MG Extended Release Oral Tablet
        "862019",  # 24 HR guanfacine 3 MG Extended Release Oral Tablet
        "862025",  # 24 HR guanfacine 4 MG Extended Release Oral Tablet
    }

class Lisdexamfetamine(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for lisdexamfetamine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable lisdexamfetamine and lisdexamfetamine in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Lisdexamfetamine"
    OID = "2.16.840.1.113883.3.464.1003.1174"
    DEFINITION_VERSION = "20220902"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1593856",  # lisdexamfetamine dimesylate 10 MG Oral Capsule
        "1871456",  # lisdexamfetamine dimesylate 40 MG Chewable Tablet
        "1871460",  # lisdexamfetamine dimesylate 30 MG Chewable Tablet
        "1871462",  # lisdexamfetamine dimesylate 20 MG Chewable Tablet
        "1871464",  # lisdexamfetamine dimesylate 10 MG Chewable Tablet
        "1871466",  # lisdexamfetamine dimesylate 60 MG Chewable Tablet
        "1871468",  # lisdexamfetamine dimesylate 50 MG Chewable Tablet
        "854830",  # lisdexamfetamine dimesylate 20 MG Oral Capsule
        "854834",  # lisdexamfetamine dimesylate 30 MG Oral Capsule
        "854838",  # lisdexamfetamine dimesylate 40 MG Oral Capsule
        "854842",  # lisdexamfetamine dimesylate 70 MG Oral Capsule
        "854846",  # lisdexamfetamine dimesylate 60 MG Oral Capsule
        "854850",  # lisdexamfetamine dimesylate 50 MG Oral Capsule
    }

class Methylphenidate(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for Methylphenidate medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable Methylphenidate and Methylphenidate in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Methylphenidate"
    OID = "2.16.840.1.113883.3.464.1003.1176"
    DEFINITION_VERSION = "20240123"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
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
        "1312583",  # 24 HR methylphenidate hydrochloride 5 MG/ML Extended Release Suspension
        "1648183",  # 40/60 Release 24 HR methylphenidate hydrochloride 15 MG Extended Release Oral Capsule
        "1727443",  # 24 HR methylphenidate hydrochloride 20 MG Chewable Extended Release Oral Tablet
        "1734928",  # 24 HR methylphenidate hydrochloride 30 MG Chewable Extended Release Oral Tablet
        "1734951",  # 24 HR methylphenidate hydrochloride 40 MG Chewable Extended Release Oral Tablet
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
        "1926840",  # methylphenidate 17.3 MG Disintegrating Oral Tablet
        "1926849",  # methylphenidate 25.9 MG Disintegrating Oral Tablet
        "1926853",  # methylphenidate 8.6 MG Disintegrating Oral Tablet
        "1995461",  # 24 HR methylphenidate hydrochloride 72 MG Extended Release Oral Tablet
        "2001564",  # BX Rating 24 HR methylphenidate hydrochloride 18 MG Extended Release Oral Tablet
        "2001565",  # BX Rating 24 HR methylphenidate hydrochloride 27 MG Extended Release Oral Tablet
        "2001566",  # BX Rating 24 HR methylphenidate hydrochloride 36 MG Extended Release Oral Tablet
        "2001568",  # BX Rating 24 HR methylphenidate hydrochloride 54 MG Extended Release Oral Tablet
        "2119559",  # 20/80 Release 24 HR methylphenidate hydrochloride 25 MG Extended Release Oral Capsule
        "2119563",  # 20/80 Release 24 HR methylphenidate hydrochloride 35 MG Extended Release Oral Capsule
        "2119567",  # 20/80 Release 24 HR methylphenidate hydrochloride 45 MG Extended Release Oral Capsule
        "2119571",  # 20/80 Release 24 HR methylphenidate hydrochloride 55 MG Extended Release Oral Capsule
        "2119574",  # 20/80 Release 24 HR methylphenidate hydrochloride 85 MG Extended Release Oral Capsule
        "2119577",  # 20/80 Release 24 HR methylphenidate hydrochloride 70 MG Extended Release Oral Capsule
        "2168857",  # Evening Dosing 24 HR methylphenidate hydrochloride 60 MG Extended Release Oral Capsule
        "2168861",  # Evening Dosing 24 HR methylphenidate hydrochloride 80 MG Extended Release Oral Capsule
        "2168864",  # Evening Dosing 24 HR methylphenidate hydrochloride 100 MG Extended Release Oral Capsule
        "2168866",  # Evening Dosing 24 HR methylphenidate hydrochloride 20 MG Extended Release Oral Capsule
        "2168868",  # Evening Dosing 24 HR methylphenidate hydrochloride 40 MG Extended Release Oral Capsule
        "2605796",  # 24 HR methylphenidate hydrochloride 63 MG Extended Release Oral Tablet
        "2605798",  # 24 HR methylphenidate hydrochloride 45 MG Extended Release Oral Tablet
        "753436",  # 9 HR methylphenidate 1.11 MG/HR Transdermal System
        "753438",  # 9 HR methylphenidate 1.67 MG/HR Transdermal System
        "753440",  # 9 HR methylphenidate 2.22 MG/HR Transdermal System
        "753441",  # 9 HR methylphenidate 3.33 MG/HR Transdermal System
    }

class Viloxazine(ValueSet):
    """
    **Clinical Focus:** N/A

    **Data Element Scope:** N/A

    **Inclusion Criteria:** N/A

    **Exclusion Criteria:** N/A
    """

    VALUE_SET_NAME = "Viloxazine"
    OID = "2.16.840.1.113883.3.464.1003.1260"
    DEFINITION_VERSION = "20250109"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "2536548",  # 24 HR viloxazine 100 MG Extended Release Oral Capsule
        "2536750",  # 24 HR viloxazine 150 MG Extended Release Oral Capsule
        "2536756",  # 24 HR viloxazine 200 MG Extended Release Oral Capsule
    }

class SubstanceUseDisorderLongActingMedication(ValueSet):
    """
    **Clinical Focus:** The purpose of this Grouping value set is to represent concepts for long acting substance use disorder medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable buprenorphine implant, buprenorphine injection and naltrexone injection medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients. Excludes short acting oral and sublingual medications.
    """

    VALUE_SET_NAME = "Substance Use Disorder Long Acting Medication"
    OID = "2.16.840.1.113883.3.464.1003.1149"
    DEFINITION_VERSION = "20240124"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1655032",  # 1 ML buprenorphine 0.3 MG/ML Cartridge
        "1797650",  # buprenorphine 74.2 MG Drug Implant
        "1996184",  # 0.5 ML buprenorphine 200 MG/ML Prefilled Syringe
        "1996192",  # 1.5 ML buprenorphine 200 MG/ML Prefilled Syringe
        "238129",  # 1 ML buprenorphine 0.3 MG/ML Injection
        "2639021",  # 0.16 ML buprenorphine 50 MG/ML Prefilled Syringe
        "2639029",  # 0.32 ML buprenorphine 50 MG/ML Prefilled Syringe
        "2639031",  # 0.48 ML buprenorphine 50 MG/ML Prefilled Syringe
        "2639033",  # 0.64 ML buprenorphine 50 MG/ML Prefilled Syringe
        "2639036",  # 0.18 ML buprenorphine 356 MG/ML Prefilled Syringe
        "2639041",  # 0.27 ML buprenorphine 356 MG/ML Prefilled Syringe
        "2639043",  # 0.36 ML buprenorphine 356 MG/ML Prefilled Syringe
        "637213",  # naltrexone 380 MG Injection
    }

class SubstanceUseDisorderShortActingMedication(ValueSet):
    """
    **Clinical Focus:** The purpose of this Grouping value set is to represent concepts for short acting substance use disorder medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable Acamprosate, Disulfiram, Naltrexone Oral, Buprenorphine Naloxone and Buprenorphine (oral, sublingual) medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients. Excludes long acting implant and injection medications.
    """

    VALUE_SET_NAME = "Substance Use Disorder Short Acting Medication"
    OID = "2.16.840.1.113883.3.464.1003.1150"
    DEFINITION_VERSION = "20240124"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
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
        "1597568",  # buprenorphine 11.4 MG / naloxone 2.9 MG Sublingual Tablet
        "1597573",  # buprenorphine 8.6 MG / naloxone 2.1 MG Sublingual Tablet
        "1666338",  # buprenorphine 2.9 MG / naloxone 0.71 MG Sublingual Tablet
        "1864412",  # buprenorphine 0.7 MG / naloxone 0.18 MG Sublingual Tablet
        "197623",  # disulfiram 250 MG Oral Tablet
        "197624",  # disulfiram 500 MG Oral Tablet
        "351264",  # buprenorphine 2 MG Sublingual Tablet
        "351265",  # buprenorphine 8 MG Sublingual Tablet
        "351266",  # buprenorphine 2 MG / naloxone 0.5 MG Sublingual Tablet
        "351267",  # buprenorphine 8 MG / naloxone 2 MG Sublingual Tablet
        "835726",  # acamprosate calcium 333 MG Delayed Release Oral Tablet
    }

class TobaccoUseCessationPharmacotherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for tobacco use cessation medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable tobacco use cessation medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Tobacco Use Cessation Pharmacotherapy"
    OID = "2.16.840.1.113883.3.526.3.1190"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1232585",  # 24 HR bupropion hydrochloride 450 MG Extended Release Oral Tablet
        "1551468",  # 12 HR bupropion hydrochloride 90 MG / naltrexone hydrochloride 8 MG Extended Release Oral Tablet
        "1797886",  # nicotine 0.5 MG/ACTUAT Metered Dose Nasal Spray
        "1801289",  # Smoking Cessation 12 HR bupropion hydrochloride 150 MG Extended Release Oral Tablet
        "198029",  # 24 HR nicotine 0.583 MG/HR Transdermal System
        "198030",  # 24 HR nicotine 0.875 MG/HR Transdermal System
        "198031",  # 24 HR nicotine 0.292 MG/HR Transdermal System
        "250983",  # nicotine 4 MG Inhalation Solution
        "2572365",  # varenicline 0.03 MG/ACTUAT Nasal Spray
        "2611260",  # bupropion hydrochloride 105 MG / dextromethorphan hydrobromide 45 MG Extended Release Oral Tablet
        "311975",  # nicotine 4 MG Chewing Gum
        "314119",  # nicotine 2 MG Chewing Gum
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
        "993550",  # 24 HR bupropion hydrobromide 174 MG Extended Release Oral Tablet
        "993557",  # 24 HR bupropion hydrochloride 300 MG Extended Release Oral Tablet
        "993567",  # 24 HR bupropion hydrobromide 348 MG Extended Release Oral Tablet
        "993681",  # 24 HR bupropion hydrobromide 522 MG Extended Release Oral Tablet
        "993687",  # bupropion hydrochloride 100 MG Oral Tablet
        "993691",  # bupropion hydrochloride 75 MG Oral Tablet
    }

class BetaBlockerTherapyForLvsd(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of medications for beta blocker therapy for left ventricular systolic dysfunction (LVSD).

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for generic and prescribable bisoprolol, carvedilol, or sustained release metoprolol succinate.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable branded drugs, components or ingredients.
    """

    VALUE_SET_NAME = "Beta Blocker Therapy for LVSD"
    OID = "2.16.840.1.113883.3.526.3.1184"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1999031",  # 24 HR metoprolol succinate 100 MG Extended Release Oral Capsule
        "1999033",  # 24 HR metoprolol succinate 200 MG Extended Release Oral Capsule
        "1999035",  # 24 HR metoprolol succinate 25 MG Extended Release Oral Capsule
        "1999037",  # 24 HR metoprolol succinate 50 MG Extended Release Oral Capsule
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
    """

    VALUE_SET_NAME = "Beta Blocker Therapy"
    OID = "2.16.840.1.113883.3.526.3.1174"
    DEFINITION_VERSION = "20210303"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1234256",  # 4 ML labetalol hydrochloride 5 MG/ML Cartridge
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
        "1999031",  # 24 HR metoprolol succinate 100 MG Extended Release Oral Capsule
        "1999033",  # 24 HR metoprolol succinate 200 MG Extended Release Oral Capsule
        "1999035",  # 24 HR metoprolol succinate 25 MG Extended Release Oral Capsule
        "1999037",  # 24 HR metoprolol succinate 50 MG Extended Release Oral Capsule
        "200031",  # carvedilol 6.25 MG Oral Tablet
        "200032",  # carvedilol 12.5 MG Oral Tablet
        "200033",  # carvedilol 25 MG Oral Tablet
        "2477889",  # 4 ML labetalol hydrochloride 5 MG/ML Injection
        "2479564",  # 200 ML labetalol hydrochloride 1 MG/ML Injection
        "2479566",  # 100 ML labetalol hydrochloride 1 MG/ML Injection
        "2479567",  # 300 ML labetalol hydrochloride 1 MG/ML Injection
        "2598343",  # 2 ML labetalol hydrochloride 5 MG/ML Prefilled Syringe
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
        "896771",  # labetalol hydrochloride 5 MG/ML Injectable Solution
        "904589",  # sotalol hydrochloride 240 MG Oral Tablet
        "904630",  # 10 ML sotalol hydrochloride 15 MG/ML Injection
        "998685",  # acebutolol 400 MG Oral Capsule
        "998689",  # acebutolol 200 MG Oral Capsule
    }

class AntibioticMedicationsForPharyngitis(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for antibiotic medications used to treat pharyngitis.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable antibiotics for pharyngitis.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Antibiotic Medications for Pharyngitis"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1001"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1013659",  # 24 HR minocycline 105 MG Extended Release Oral Tablet
        "1013662",  # 24 HR minocycline 55 MG Extended Release Oral Tablet
        "1013665",  # 24 HR minocycline 80 MG Extended Release Oral Tablet
        "1043022",  # cefixime 100 MG Chewable Tablet
        "1043030",  # cefixime 200 MG Chewable Tablet
        "105171",  # cefadroxil 100 MG/ML Oral Suspension
        "1291986",  # {4 (amoxicillin 500 MG Oral Capsule) / 2 (clarithromycin 500 MG Oral Tablet) / 2 (omeprazole 20 MG Delayed Release Oral Capsule) } Pack
        "1302650",  # 24 HR minocycline 45 MG Extended Release Oral Capsule
        "1302664",  # 24 HR minocycline 90 MG Extended Release Oral Capsule
        "1302674",  # 24 HR minocycline 135 MG Extended Release Oral Capsule
        "1373014",  # cefixime 100 MG/ML Oral Suspension
        "141963",  # azithromycin 40 MG/ML Oral Suspension
        "1423080",  # doxycycline hyclate 200 MG Delayed Release Oral Tablet
        "1649401",  # doxycycline monohydrate 50 MG Oral Capsule
        "1649405",  # doxycycline hyclate 50 MG Oral Capsule
        "1649425",  # doxycycline hyclate 75 MG Oral Tablet
        "1649429",  # doxycycline monohydrate 75 MG Oral Tablet
        "1649988",  # doxycycline hyclate 100 MG Oral Capsule
        "1649990",  # doxycycline monohydrate 100 MG Oral Capsule
        "1650030",  # doxycycline monohydrate 5 MG/ML Oral Suspension
        "1650142",  # doxycycline monohydrate 100 MG Oral Tablet
        "1650143",  # doxycycline hyclate 100 MG Oral Tablet
        "1650198",  # {150 (doxycycline monohydrate 100 MG Oral Tablet) / 1 (118 ML) (salicylic acid 20 MG/ML Medicated Liquid Soap) } Pack
        "1650444",  # doxycycline monohydrate 150 MG Oral Tablet
        "1650446",  # doxycycline hyclate 150 MG Oral Tablet
        "1652673",  # doxycycline monohydrate 50 MG Oral Tablet
        "1652674",  # doxycycline hyclate 50 MG Oral Tablet
        "1653433",  # doxycycline hyclate 50 MG Delayed Release Oral Tablet
        "1665005",  # ceftriaxone 500 MG Injection
        "1665021",  # ceftriaxone 1000 MG Injection
        "1665046",  # ceftriaxone 2000 MG Injection
        "1665050",  # cefazolin 1000 MG Injection
        "1665052",  # cefazolin 500 MG Injection
        "1665060",  # cefazolin 2000 MG Injection
        "1665210",  # 100 ML ciprofloxacin 2 MG/ML Injection
        "1665212",  # 200 ML ciprofloxacin 2 MG/ML Injection
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
        "1721473",  # ampicillin 250 MG Injection
        "1721474",  # ampicillin 500 MG Injection
        "1721475",  # ampicillin 1000 MG Injection
        "1721476",  # ampicillin 2000 MG Injection
        "1737244",  # 2 ML clindamycin 150 MG/ML Injection
        "1737578",  # 4 ML clindamycin 150 MG/ML Injection
        "1737581",  # 6 ML clindamycin 150 MG/ML Injection
        "1801138",  # doxycycline hyclate 120 MG Delayed Release Oral Tablet
        "1801142",  # doxycycline hyclate 60 MG Delayed Release Oral Tablet
        "1809083",  # 5 ML sulfamethoxazole 80 MG/ML / trimethoprim 16 MG/ML Injection
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
        "197650",  # erythromycin 500 MG Oral Tablet
        "197984",  # minocycline 100 MG Oral Capsule
        "197985",  # minocycline 50 MG Oral Capsule
        "198048",  # ofloxacin 200 MG Oral Tablet
        "198049",  # ofloxacin 300 MG Oral Tablet
        "198050",  # ofloxacin 400 MG Oral Tablet
        "198250",  # tetracycline hydrochloride 250 MG Oral Capsule
        "198252",  # tetracycline hydrochloride 500 MG Oral Capsule
        "198332",  # trimethoprim 100 MG Oral Tablet
        "198334",  # sulfamethoxazole 400 MG / trimethoprim 80 MG Oral Tablet
        "198335",  # sulfamethoxazole 800 MG / trimethoprim 160 MG Oral Tablet
        "199370",  # ciprofloxacin 100 MG Oral Tablet
        "1998483",  # doxycycline hyclate 200 MG Injection
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
        "2099768",  # {42 (doxycycline hyclate 100 MG Oral Tablet) } Pack
        "2122343",  # doxycycline hyclate 80 MG Delayed Release Oral Tablet
        "239191",  # amoxicillin 50 MG/ML Oral Suspension
        "240741",  # clarithromycin 25 MG/ML Oral Suspension
        "242807",  # minocycline 10 MG/ML Oral Suspension
        "248656",  # azithromycin 500 MG Oral Tablet
        "2604801",  # {84 (amoxicillin 500 MG Oral Capsule) / 28 (vonoprazan 20 MG Oral Tablet) } Pack
        "2604803",  # {56 (amoxicillin 500 MG Oral Capsule) / 28 (clarithromycin 500 MG Oral Tablet) / 28 (vonoprazan 20 MG Oral Tablet) } Pack
        "2630753",  # cefazolin 3000 MG Injection
        "2671687",  # penicillin G benzathine 1200000 UNT Injection
        "2671695",  # penicillin G benzathine 2400000 UNT Injection
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
        "308212",  # ampicillin 500 MG Oral Capsule
        "308459",  # azithromycin 20 MG/ML Oral Suspension
        "308460",  # azithromycin 250 MG Oral Tablet
        "309042",  # cefaclor 75 MG/ML Oral Suspension
        "309043",  # 12 HR cefaclor 500 MG Extended Release Oral Tablet
        "309044",  # cefaclor 25 MG/ML Oral Suspension
        "309045",  # cefaclor 250 MG Oral Capsule
        "309047",  # cefadroxil 1000 MG Oral Tablet
        "309048",  # cefadroxil 50 MG/ML Oral Suspension
        "309049",  # cefadroxil 500 MG Oral Capsule
        "309054",  # cefdinir 25 MG/ML Oral Suspension
        "309058",  # cefixime 20 MG/ML Oral Suspension
        "309076",  # cefpodoxime 100 MG Oral Tablet
        "309077",  # cefpodoxime 20 MG/ML Oral Suspension
        "309078",  # cefpodoxime 200 MG Oral Tablet
        "309079",  # cefpodoxime 10 MG/ML Oral Suspension
        "309080",  # cefprozil 25 MG/ML Oral Suspension
        "309081",  # cefprozil 50 MG/ML Oral Suspension
        "309090",  # ceftriaxone 100 MG/ML Injectable Solution
        "309092",  # ceftriaxone 250 MG Injection
        "309095",  # cefuroxime 125 MG Oral Tablet
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
        "311787",  # moxifloxacin 400 MG Oral Tablet
        "313134",  # sulfamethoxazole 40 MG/ML / trimethoprim 8 MG/ML Oral Suspension
        "313137",  # sulfamethoxazole 80 MG/ML / trimethoprim 16 MG/ML Injectable Solution
        "313252",  # tetracycline hydrochloride 250 MG Oral Tablet
        "313254",  # tetracycline hydrochloride 500 MG Oral Tablet
        "313797",  # amoxicillin 25 MG/ML Oral Suspension
        "313800",  # ampicillin 250 MG Oral Capsule
        "313850",  # amoxicillin 40 MG/ML Oral Suspension
        "313888",  # cefaclor 50 MG/ML Oral Suspension
        "313920",  # cefazolin 200 MG/ML Injectable Solution
        "314108",  # minocycline 75 MG Oral Capsule
        "315090",  # erythromycin 333 MG Delayed Release Oral Tablet
        "317127",  # minocycline 100 MG Injection
        "348869",  # doxycycline hyclate 100 MG Delayed Release Oral Capsule
        "351121",  # minocycline 1 MG Oral Powder
        "351156",  # 250 ML moxifloxacin 1.6 MG/ML Injection
        "359383",  # 24 HR ciprofloxacin 500 MG Extended Release Oral Tablet
        "359385",  # 24 HR clarithromycin 500 MG Extended Release Oral Tablet
        "403840",  # minocycline 75 MG Oral Tablet
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
        "637173",  # cephalexin 750 MG Oral Capsule
        "645617",  # cephalexin 333 MG Oral Capsule
        "686355",  # erythromycin stearate 250 MG Oral Tablet
        "686400",  # erythromycin ethylsuccinate 40 MG/ML Oral Suspension
        "686405",  # erythromycin ethylsuccinate 400 MG Oral Tablet
        "686406",  # erythromycin stearate 500 MG Oral Tablet
        "686418",  # erythromycin ethylsuccinate 80 MG/ML Oral Suspension
        "700408",  # doxycycline monohydrate 75 MG Oral Capsule
        "728207",  # doxycycline monohydrate 150 MG Oral Capsule
        "731567",  # 2 ML penicillin G benzathine 600000 UNT/ML Prefilled Syringe
        "731570",  # 4 ML penicillin G benzathine 600000 UNT/ML Prefilled Syringe
        "745302",  # penicillin G sodium 100000 UNT/ML Injectable Solution
        "749780",  # {3 (azithromycin 500 MG Oral Tablet) } Pack
        "749783",  # {6 (azithromycin 250 MG Oral Tablet) } Pack
        "757968",  # {4 (amoxicillin 500 MG Oral Capsule) / 2 (clarithromycin 500 MG Oral Tablet) / 2 (lansoprazole 30 MG Delayed Release Oral Capsule) } Pack
        "758019",  # {112 (bismuth subsalicylate 262 MG Chewable Tablet) / 56 (metronidazole 250 MG Oral Tablet) / 56 (tetracycline hydrochloride 500 MG Oral Capsule) } Pack
        "789980",  # ampicillin 100 MG/ML Injectable Solution
        "799048",  # doxycycline hyclate 150 MG Delayed Release Oral Tablet
        "802550",  # amoxicillin 775 MG Extended Release Oral Tablet
        "834040",  # penicillin V potassium 50 MG/ML Oral Solution
        "834046",  # penicillin V potassium 25 MG/ML Oral Solution
        "834061",  # penicillin V potassium 250 MG Oral Tablet
        "834102",  # penicillin V potassium 500 MG Oral Tablet
        "835700",  # {30 (doxycycline monohydrate 150 MG Oral Tablet) } Pack
        "853019",  # clindamycin 25 MG Oral Capsule
        "858062",  # 24 HR minocycline 115 MG Extended Release Oral Tablet
        "858372",  # 24 HR minocycline 65 MG Extended Release Oral Tablet
        "861416",  # azithromycin 1000 MG Powder for Oral Suspension
        "863538",  # penicillin G potassium 1000000 UNT/ML Injectable Solution
        "901399",  # doxycycline anhydrous 40 MG Delayed Release Oral Capsule
    }

class ContraceptiveMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for contraceptive medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable contraceptive medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Contraceptive Medications"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1080"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1000126",  # 1 ML medroxyprogesterone acetate 150 MG/ML Injection
        "1000153",  # 1 ML medroxyprogesterone acetate 150 MG/ML Prefilled Syringe
        "1000156",  # 0.65 ML medroxyprogesterone acetate 160 MG/ML Prefilled Syringe
        "1000405",  # norethindrone acetate 5 MG Oral Tablet
        "1013626",  # drospirenone 3 MG / ethinyl estradiol 0.02 MG / levomefolate calcium 0.451 MG Oral Tablet
        "1013629",  # {24 (drospirenone 3 MG / ethinyl estradiol 0.02 MG / levomefolate calcium 0.451 MG Oral Tablet) / 4 (levomefolate calcium 0.451 MG Oral Tablet) } Pack
        "1037183",  # ethinyl estradiol 0.01 MG / norethindrone acetate 1 MG Oral Tablet
        "1037184",  # {24 (ethinyl estradiol 0.01 MG / norethindrone acetate 1 MG Oral Tablet) / 2 (ethinyl estradiol 0.01 MG Oral Tablet) / 2 (ferrous fumarate 75 MG Oral Tablet) } Pack
        "1090992",  # ethinyl estradiol 0.005 MG / norethindrone acetate 1 MG Oral Tablet
        "1095224",  # {21 (ethinyl estradiol 0.035 MG / norethindrone 0.4 MG Chewable Tablet) / 7 (ferrous fumarate 75 MG Chewable Tablet) } Pack
        "1099638",  # ethinyl estradiol 0.025 MG / norethindrone 0.8 MG Chewable Tablet
        "1251323",  # ethinyl estradiol 0.0025 MG / norethindrone acetate 0.5 MG Oral Tablet
        "1251334",  # {28 (ethinyl estradiol 0.0025 MG / norethindrone acetate 0.5 MG Oral Tablet) } Pack
        "1251336",  # {28 (ethinyl estradiol 0.005 MG / norethindrone acetate 1 MG Oral Tablet) } Pack
        "1301016",  # drospirenone 0.25 MG / ethinyl estradiol 0.5 MG Oral Tablet
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
        "1366334",  # levonorgestrel 0.000583 MG/HR Intrauterine System
        "1367436",  # 21 DAY ethinyl estradiol 0.000625 MG/HR / etonogestrel 0.005 MG/HR Vaginal System
        "1373501",  # ethinyl estradiol 0.02 MG / levonorgestrel 0.15 MG Oral Tablet
        "1373502",  # ethinyl estradiol 0.025 MG / levonorgestrel 0.15 MG Oral Tablet
        "1373503",  # {7 (ethinyl estradiol 0.01 MG Oral Tablet) / 42 (ethinyl estradiol 0.02 MG / levonorgestrel 0.15 MG Oral Tablet) / 21 (ethinyl estradiol 0.025 MG / levonorgestrel 0.15 MG Oral Tablet) / 21 (ethinyl estradiol 0.03 MG / levonorgestrel 0.15 MG Oral Tablet) } Pack
        "1421459",  # ethinyl estradiol 0.02 MG / norethindrone acetate 1 MG Oral Capsule
        "1421461",  # {24 (ethinyl estradiol 0.02 MG / norethindrone acetate 1 MG Oral Capsule) / 4 (ferrous fumarate 75 MG Oral Capsule) } Pack
        "1426288",  # ethinyl estradiol 0.02 MG / norethindrone acetate 1 MG Chewable Tablet
        "1426600",  # {24 (ethinyl estradiol 0.02 MG / norethindrone acetate 1 MG Chewable Tablet) / 4 (ferrous fumarate 75 MG Oral Tablet) } Pack
        "1534809",  # 168 HR ethinyl estradiol 0.00146 MG/HR / norelgestromin 0.00625 MG/HR Transdermal System
        "1605252",  # levonorgestrel 0.000813 MG/HR Intrauterine System
        "1607990",  # {24 (ethinyl estradiol 0.025 MG / norethindrone 0.8 MG Chewable Tablet) / 4 (ferrous fumarate 75 MG Chewable Tablet) } Pack
        "1811886",  # levonorgestrel 0.000729 MG/HR Intrauterine System
        "198042",  # norethindrone 0.35 MG Oral Tablet
        "238015",  # ethinyl estradiol 0.035 MG / norethindrone 0.4 MG Oral Tablet
        "238019",  # ethinyl estradiol 0.03 MG / levonorgestrel 0.15 MG Oral Tablet
        "240128",  # ethinyl estradiol 0.035 MG / norgestimate 0.25 MG Oral Tablet
        "240707",  # desogestrel 0.15 MG / ethinyl estradiol 0.03 MG Oral Tablet
        "242297",  # ethinyl estradiol 0.02 MG / levonorgestrel 0.1 MG Oral Tablet
        "249357",  # desogestrel 0.15 MG / ethinyl estradiol 0.02 MG Oral Tablet
        "2539224",  # ethinyl estradiol 0.02 MG / levonorgestrel 0.1 MG Chewable Tablet
        "2539228",  # {21 (ethinyl estradiol 0.02 MG / levonorgestrel 0.1 MG Chewable Tablet) / 7 (inert ingredients 1 MG Chewable Tablet) } Pack
        "259218",  # levonorgestrel 0.75 MG Oral Tablet
        "2672923",  # {21 (ethinyl estradiol 0.02 MG / levonorgestrel 0.1 MG Oral Tablet) / 7 (ferrous bisglycinate 36.5 MG Oral Tablet) } Pack
        "2696883",  # ethinyl estradiol 0.02 MG / norethindrone acetate 1 MG Disintegrating Oral Tablet
        "2696887",  # {24 (ethinyl estradiol 0.02 MG / norethindrone acetate 1 MG Disintegrating Oral Tablet) / 4 (inert ingredients 1 MG Disintegrating Oral Tablet) } Pack
        "284207",  # drospirenone 3 MG / ethinyl estradiol 0.03 MG Oral Tablet
        "310228",  # ethinyl estradiol 0.035 MG / ethynodiol diacetate 1 MG Oral Tablet
        "310230",  # ethinyl estradiol 0.03 MG / levonorgestrel 0.05 MG Oral Tablet
        "310463",  # ethinyl estradiol 0.035 MG / norethindrone 0.5 MG Oral Tablet
        "311359",  # ethinyl estradiol 0.03 MG / norgestrel 0.3 MG Oral Tablet
        "312033",  # ethinyl estradiol 0.035 MG / norethindrone 1 MG Oral Tablet
        "314146",  # ethinyl estradiol 0.05 MG / norgestrel 0.5 MG Oral Tablet
        "315096",  # ethinyl estradiol 0.05 MG / ethynodiol diacetate 1 MG Oral Tablet
        "348804",  # ethinyl estradiol 0.03 MG / levonorgestrel 0.125 MG Oral Tablet
        "348805",  # ethinyl estradiol 0.04 MG / levonorgestrel 0.075 MG Oral Tablet
        "389221",  # etonogestrel 68 MG Drug Implant
        "392662",  # ethinyl estradiol 0.035 MG / norethindrone 0.75 MG Oral Tablet
        "406396",  # ethinyl estradiol 0.035 MG / norgestimate 0.18 MG Oral Tablet
        "433718",  # ethinyl estradiol 0.035 MG / norethindrone 0.4 MG Chewable Tablet
        "483325",  # levonorgestrel 1.5 MG Oral Tablet
        "578732",  # ethinyl estradiol 0.025 MG / norgestimate 0.18 MG Oral Tablet
        "602598",  # drospirenone 0.5 MG / ethinyl estradiol 1 MG Oral Tablet
        "630734",  # drospirenone 3 MG / ethinyl estradiol 0.02 MG Oral Tablet
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
        "759741",  # desogestrel 0.125 MG / ethinyl estradiol 0.025 MG Oral Tablet
        "759742",  # {7 (desogestrel 0.1 MG / ethinyl estradiol 0.025 MG Oral Tablet) / 7 (desogestrel 0.125 MG / ethinyl estradiol 0.025 MG Oral Tablet) / 7 (desogestrel 0.15 MG / ethinyl estradiol 0.025 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "759743",  # {21 (desogestrel 0.15 MG / ethinyl estradiol 0.02 MG Oral Tablet) / 5 (ethinyl estradiol 0.01 MG Oral Tablet) / 2 (inert ingredients 1 MG Oral Tablet) } Pack
        "763088",  # {2 (levonorgestrel 0.75 MG Oral Tablet) } Pack
        "804156",  # levonorgestrel 0.000833 MG/HR Intrauterine System
        "810096",  # {7 (ethinyl estradiol 0.01 MG Oral Tablet) / 84 (ethinyl estradiol 0.02 MG / levonorgestrel 0.1 MG Oral Tablet) } Pack
        "823777",  # {12 (ethinyl estradiol 0.035 MG / norethindrone 0.5 MG Oral Tablet) / 9 (ethinyl estradiol 0.035 MG / norethindrone 1 MG Oral Tablet) / 7 (inert ingredients 1 MG Oral Tablet) } Pack
        "978949",  # {5 (dienogest 2 MG / estradiol valerate 2 MG Oral Tablet) / 17 (dienogest 3 MG / estradiol valerate 2 MG Oral Tablet) / 2 (estradiol valerate 1 MG Oral Tablet) / 2 (estradiol valerate 3 MG Oral Tablet) / 2 (inert ingredients 1 MG Oral Tablet) } Pack
    }

class Isotretinoin(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for isotretinoin medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable isotretinoin and isotretinoin in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Isotretinoin"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1143"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1547561",  # isotretinoin 25 MG Oral Capsule
        "1547565",  # isotretinoin 35 MG Oral Capsule
        "197843",  # isotretinoin 10 MG Oral Capsule
        "197844",  # isotretinoin 20 MG Oral Capsule
        "197845",  # isotretinoin 40 MG Oral Capsule
        "2262711",  # Micronized isotretinoin 16 MG Oral Capsule
        "2262717",  # Micronized isotretinoin 24 MG Oral Capsule
        "2262725",  # Micronized isotretinoin 32 MG Oral Capsule
        "2262729",  # Micronized isotretinoin 8 MG Oral Capsule
        "403930",  # isotretinoin 30 MG Oral Capsule
    }

class AntibioticMedicationsForUpperRespiratoryInfection(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for antibiotic medications used to treat upper respiratory infection.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable antibiotics for upper respiratory infection.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Antibiotic Medications for Upper Respiratory Infection"
    OID = "2.16.840.1.113883.3.464.1003.1190"
    DEFINITION_VERSION = "20250114"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1013659",  # 24 HR minocycline 105 MG Extended Release Oral Tablet
        "1013662",  # 24 HR minocycline 55 MG Extended Release Oral Tablet
        "1013665",  # 24 HR minocycline 80 MG Extended Release Oral Tablet
        "1043022",  # cefixime 100 MG Chewable Tablet
        "1043030",  # cefixime 200 MG Chewable Tablet
        "105171",  # cefadroxil 100 MG/ML Oral Suspension
        "1291986",  # {4 (amoxicillin 500 MG Oral Capsule) / 2 (clarithromycin 500 MG Oral Tablet) / 2 (omeprazole 20 MG Delayed Release Oral Capsule) } Pack
        "1302650",  # 24 HR minocycline 45 MG Extended Release Oral Capsule
        "1302664",  # 24 HR minocycline 90 MG Extended Release Oral Capsule
        "1302674",  # 24 HR minocycline 135 MG Extended Release Oral Capsule
        "1314763",  # tobramycin 75 MG/ML Inhalation Solution
        "1373014",  # cefixime 100 MG/ML Oral Suspension
        "1374569",  # tobramycin 28 MG Inhalation Powder
        "1374570",  # {224 (tobramycin 28 MG Inhalation Powder) } Pack
        "141963",  # azithromycin 40 MG/ML Oral Suspension
        "1423080",  # doxycycline hyclate 200 MG Delayed Release Oral Tablet
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
        "1650198",  # {150 (doxycycline monohydrate 100 MG Oral Tablet) / 1 (118 ML) (salicylic acid 20 MG/ML Medicated Liquid Soap) } Pack
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
        "1661466",  # {8 (tobramycin 28 MG Inhalation Powder) } Pack
        "1661559",  # {56 (tobramycin 28 MG Inhalation Powder) } Pack
        "1662278",  # 100 ML linezolid 2 MG/ML Injection
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
        "1737244",  # 2 ML clindamycin 150 MG/ML Injection
        "1737578",  # 4 ML clindamycin 150 MG/ML Injection
        "1737581",  # 6 ML clindamycin 150 MG/ML Injection
        "1739890",  # cefoxitin 100 MG/ML Injectable Solution
        "1743547",  # oxacillin 1000 MG Injection
        "1743549",  # oxacillin 2000 MG Injection
        "1801138",  # doxycycline hyclate 120 MG Delayed Release Oral Tablet
        "1801142",  # doxycycline hyclate 60 MG Delayed Release Oral Tablet
        "1807508",  # 200 ML vancomycin 5 MG/ML Injection
        "1807510",  # 150 ML vancomycin 5 MG/ML Injection
        "1807511",  # 100 ML vancomycin 5 MG/ML Injection
        "1807513",  # vancomycin 1000 MG Injection
        "1807516",  # vancomycin 500 MG Injection
        "1807518",  # vancomycin 750 MG Injection
        "1809083",  # 5 ML sulfamethoxazole 80 MG/ML / trimethoprim 16 MG/ML Injection
        "1870631",  # 100 ML gentamicin 1.2 MG/ML Injection
        "1870633",  # 50 ML gentamicin 1.2 MG/ML Injection
        "1870650",  # 2 ML gentamicin 40 MG/ML Injection
        "1870676",  # 2 ML gentamicin 10 MG/ML Injection
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
        "197736",  # 50 ML gentamicin 2 MG/ML Injection
        "197984",  # minocycline 100 MG Oral Capsule
        "197985",  # minocycline 50 MG Oral Capsule
        "198048",  # ofloxacin 200 MG Oral Tablet
        "198049",  # ofloxacin 300 MG Oral Tablet
        "198050",  # ofloxacin 400 MG Oral Tablet
        "198201",  # rifampin 150 MG Oral Capsule
        "198202",  # rifampin 300 MG Oral Capsule
        "198228",  # sulfadiazine 500 MG Oral Tablet
        "198250",  # tetracycline hydrochloride 250 MG Oral Capsule
        "198252",  # tetracycline hydrochloride 500 MG Oral Capsule
        "198332",  # trimethoprim 100 MG Oral Tablet
        "198334",  # sulfamethoxazole 400 MG / trimethoprim 80 MG Oral Tablet
        "198335",  # sulfamethoxazole 800 MG / trimethoprim 160 MG Oral Tablet
        "199055",  # metronidazole 375 MG Oral Capsule
        "199370",  # ciprofloxacin 100 MG Oral Tablet
        "1996246",  # daptomycin 350 MG Injection
        "1998483",  # doxycycline hyclate 200 MG Injection
        "199884",  # levofloxacin 250 MG Oral Tablet
        "199885",  # levofloxacin 500 MG Oral Tablet
        "2000127",  # vancomycin 25 MG/ML Oral Solution
        "2000134",  # vancomycin 50 MG/ML Oral Solution
        "200346",  # cefdinir 300 MG Oral Capsule
        "204466",  # 50 ML penicillin G potassium 40000 UNT/ML Injection
        "204844",  # azithromycin 600 MG Oral Tablet
        "2049888",  # vancomycin 1250 MG Injection
        "2049890",  # vancomycin 1500 MG Injection
        "2049891",  # vancomycin 250 MG Injection
        "2058953",  # cefepime 100 MG/ML Injectable Solution
        "205964",  # clindamycin 150 MG/ML Injectable Solution
        "207362",  # minocycline 50 MG Oral Tablet
        "207364",  # minocycline 100 MG Oral Tablet
        "207390",  # 50 ML penicillin G potassium 20000 UNT/ML Injection
        "207391",  # 50 ML penicillin G potassium 60000 UNT/ML Injection
        "2099768",  # {42 (doxycycline hyclate 100 MG Oral Tablet) } Pack
        "2118448",  # 300 ML vancomycin 5 MG/ML Injection
        "2118449",  # 400 ML vancomycin 5 MG/ML Injection
        "2122343",  # doxycycline hyclate 80 MG Delayed Release Oral Tablet
        "2387078",  # 250 ML vancomycin 5 MG/ML Injection
        "2387079",  # 350 ML vancomycin 5 MG/ML Injection
        "239189",  # nafcillin 100 MG/ML Injectable Solution
        "239191",  # amoxicillin 50 MG/ML Oral Suspension
        "239200",  # chloramphenicol 100 MG/ML Injectable Solution
        "239204",  # gentamicin 10 MG/ML Injectable Solution
        "239209",  # vancomycin 100 MG/ML Injectable Solution
        "239212",  # lincomycin 300 MG/ML Injectable Solution
        "240637",  # 50 ML oxacillin 40 MG/ML Injection
        "240741",  # clarithromycin 25 MG/ML Oral Suspension
        "240984",  # ampicillin 100 MG/ML / sulbactam 50 MG/ML Injectable Solution
        "242800",  # ceftazidime 200 MG/ML Injectable Solution
        "242807",  # minocycline 10 MG/ML Oral Suspension
        "242816",  # 100 ML gentamicin 1 MG/ML Injection
        "248656",  # azithromycin 500 MG Oral Tablet
        "259290",  # dalfopristin 350 MG / quinupristin 150 MG Injection
        "2604801",  # {84 (amoxicillin 500 MG Oral Capsule) / 28 (vonoprazan 20 MG Oral Tablet) } Pack
        "2604803",  # {56 (amoxicillin 500 MG Oral Capsule) / 28 (clarithromycin 500 MG Oral Tablet) / 28 (vonoprazan 20 MG Oral Tablet) } Pack
        "2630753",  # cefazolin 3000 MG Injection
        "2632127",  # 100 ML daptomycin 10 MG/ML Injection
        "2632130",  # 50 ML daptomycin 7 MG/ML Injection
        "2632132",  # 50 ML daptomycin 10 MG/ML Injection
        "2632133",  # 100 ML daptomycin 7 MG/ML Injection
        "2667642",  # metronidazole 100 MG/ML Oral Suspension
        "2671687",  # penicillin G benzathine 1200000 UNT Injection
        "2671695",  # penicillin G benzathine 2400000 UNT Injection
        "2688632",  # vancomycin 1750 MG Injection
        "2688634",  # vancomycin 2000 MG Injection
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
        "308212",  # ampicillin 500 MG Oral Capsule
        "308459",  # azithromycin 20 MG/ML Oral Suspension
        "308460",  # azithromycin 250 MG Oral Tablet
        "309042",  # cefaclor 75 MG/ML Oral Suspension
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
        "310473",  # 100 ML gentamicin 0.8 MG/ML Injection
        "310477",  # 50 ML gentamicin 1.6 MG/ML Injection
        "311296",  # levofloxacin 750 MG Oral Tablet
        "311345",  # linezolid 20 MG/ML Oral Suspension
        "311347",  # linezolid 600 MG Oral Tablet
        "311681",  # metronidazole 500 MG Oral Tablet
        "311683",  # 100 ML metronidazole 5 MG/ML Injection
        "311787",  # moxifloxacin 400 MG Oral Tablet
        "311989",  # nitrofurantoin 5 MG/ML Oral Suspension
        "311994",  # nitrofurantoin, macrocrystals 25 MG Oral Capsule
        "311995",  # nitrofurantoin, macrocrystals 50 MG Oral Capsule
        "312127",  # oxacillin 100 MG/ML Injectable Solution
        "312128",  # 50 ML oxacillin 20 MG/ML Injection
        "312447",  # piperacillin 200 MG/ML / tazobactam 25 MG/ML Injectable Solution
        "312821",  # rifampin 600 MG Injection
        "313115",  # streptomycin 1000 MG Injection
        "313134",  # sulfamethoxazole 40 MG/ML / trimethoprim 8 MG/ML Oral Suspension
        "313137",  # sulfamethoxazole 80 MG/ML / trimethoprim 16 MG/ML Injectable Solution
        "313252",  # tetracycline hydrochloride 250 MG Oral Tablet
        "313254",  # tetracycline hydrochloride 500 MG Oral Tablet
        "313416",  # tobramycin 10 MG/ML Injectable Solution
        "313570",  # vancomycin 125 MG Oral Capsule
        "313571",  # vancomycin 250 MG Oral Capsule
        "313572",  # vancomycin 50 MG/ML Injectable Solution
        "313797",  # amoxicillin 25 MG/ML Oral Suspension
        "313800",  # ampicillin 250 MG Oral Capsule
        "313850",  # amoxicillin 40 MG/ML Oral Suspension
        "313888",  # cefaclor 50 MG/ML Oral Suspension
        "313920",  # cefazolin 200 MG/ML Injectable Solution
        "313996",  # gentamicin 40 MG/ML Injectable Solution
        "314106",  # metronidazole 250 MG Oral Tablet
        "314108",  # minocycline 75 MG Oral Capsule
        "315090",  # erythromycin 333 MG Delayed Release Oral Tablet
        "317127",  # minocycline 100 MG Injection
        "348719",  # tobramycin 60 MG/ML Inhalation Solution
        "348869",  # doxycycline hyclate 100 MG Delayed Release Oral Capsule
        "351121",  # minocycline 1 MG Oral Powder
        "351156",  # 250 ML moxifloxacin 1.6 MG/ML Injection
        "359383",  # 24 HR ciprofloxacin 500 MG Extended Release Oral Tablet
        "359385",  # 24 HR clarithromycin 500 MG Extended Release Oral Tablet
        "403840",  # minocycline 75 MG Oral Tablet
        "403920",  # daptomycin 500 MG Injection
        "403921",  # 24 HR ciprofloxacin 1000 MG Extended Release Oral Tablet
        "406524",  # doxycycline hyclate 75 MG Delayed Release Oral Tablet
        "409823",  # cefixime 400 MG Oral Capsule
        "419849",  # cefixime 40 MG/ML Oral Suspension
        "422434",  # nitrofurantoin 10 MG/ML Oral Suspension
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
        "731567",  # 2 ML penicillin G benzathine 600000 UNT/ML Prefilled Syringe
        "731570",  # 4 ML penicillin G benzathine 600000 UNT/ML Prefilled Syringe
        "745302",  # penicillin G sodium 100000 UNT/ML Injectable Solution
        "745462",  # 2 ML penicillin G procaine 600000 UNT/ML Prefilled Syringe
        "745560",  # 1 ML penicillin G procaine 600000 UNT/ML Prefilled Syringe
        "749780",  # {3 (azithromycin 500 MG Oral Tablet) } Pack
        "749783",  # {6 (azithromycin 250 MG Oral Tablet) } Pack
        "757460",  # {31 (doxycycline monohydrate 100 MG Oral Tablet) } Pack
        "757466",  # {60 (doxycycline monohydrate 100 MG Oral Tablet) } Pack
        "757968",  # {4 (amoxicillin 500 MG Oral Capsule) / 2 (clarithromycin 500 MG Oral Tablet) / 2 (lansoprazole 30 MG Delayed Release Oral Capsule) } Pack
        "758019",  # {112 (bismuth subsalicylate 262 MG Chewable Tablet) / 56 (metronidazole 250 MG Oral Tablet) / 56 (tetracycline hydrochloride 500 MG Oral Capsule) } Pack
        "789980",  # ampicillin 100 MG/ML Injectable Solution
        "799048",  # doxycycline hyclate 150 MG Delayed Release Oral Tablet
        "802550",  # amoxicillin 775 MG Extended Release Oral Tablet
        "808917",  # fosfomycin 3000 MG Granules for Oral Solution
        "834040",  # penicillin V potassium 50 MG/ML Oral Solution
        "834046",  # penicillin V potassium 25 MG/ML Oral Solution
        "834061",  # penicillin V potassium 250 MG Oral Tablet
        "834102",  # penicillin V potassium 500 MG Oral Tablet
        "835700",  # {30 (doxycycline monohydrate 150 MG Oral Tablet) } Pack
        "836306",  # 2 ML penicillin G benzathine 450000 UNT/ML / penicillin G procaine 150000 UNT/ML Prefilled Syringe
        "853019",  # clindamycin 25 MG Oral Capsule
        "858062",  # 24 HR minocycline 115 MG Extended Release Oral Tablet
        "858372",  # 24 HR minocycline 65 MG Extended Release Oral Tablet
        "861416",  # azithromycin 1000 MG Powder for Oral Suspension
        "863538",  # penicillin G potassium 1000000 UNT/ML Injectable Solution
        "901399",  # doxycycline anhydrous 40 MG Delayed Release Oral Capsule
        "901610",  # aztreonam 75 MG/ML Inhalation Solution
    }

class DesiccatedThyroidMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for desiccated thyroid medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Desiccated Thyroid Medications"
    OID = "2.16.840.1.113883.3.464.1003.1060"
    DEFINITION_VERSION = "20240117"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1041814",  # thyroid (USP) 97.5 MG Oral Tablet
        "1099948",  # thyroid (USP) 48.75 MG Oral Tablet
        "1537767",  # thyroid (USP) 162.5 MG Oral Tablet
        "1537803",  # thyroid (USP) 113.75 MG Oral Tablet
        "1537807",  # thyroid (USP) 146.25 MG Oral Tablet
        "1537811",  # thyroid (USP) 81.25 MG Oral Tablet
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
    }

class DigoxinMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for digoxin medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Digoxin Medications"
    OID = "2.16.840.1.113883.3.464.1003.1065"
    DEFINITION_VERSION = "20210910"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "104208",  # 2 ML digoxin 0.25 MG/ML Injection
        "197604",  # digoxin 0.125 MG Oral Tablet
        "197606",  # digoxin 0.25 MG Oral Tablet
        "204504",  # 1 ML digoxin 0.1 MG/ML Injection
        "245273",  # digoxin 0.0625 MG Oral Tablet
        "393245",  # digoxin 0.05 MG/ML Oral Solution
    }

class DipyridamoleMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for antithrombotic medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes dipyridamole (oral, excluding extended release). Includes concepts that represent generic, human use and prescribable medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Dipyridamole Medications"
    OID = "2.16.840.1.113883.3.464.1003.1051"
    DEFINITION_VERSION = "20210909"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "197622",  # dipyridamole 50 MG Oral Tablet
        "309952",  # dipyridamole 25 MG Oral Tablet
        "309955",  # dipyridamole 75 MG Oral Tablet
    }

class DoxepinMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for doxepin medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Doxepin Medications"
    OID = "2.16.840.1.113883.3.464.1003.1067"
    DEFINITION_VERSION = "20210910"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1000048",  # doxepin 10 MG Oral Capsule
        "1000054",  # doxepin 10 MG/ML Oral Solution
        "1000058",  # doxepin 100 MG Oral Capsule
        "1000064",  # doxepin 150 MG Oral Capsule
        "1000070",  # doxepin 25 MG Oral Capsule
        "1000076",  # doxepin 50 MG Oral Capsule
        "1000097",  # doxepin 75 MG Oral Capsule
        "966787",  # doxepin 3 MG Oral Tablet
        "966793",  # doxepin 6 MG Oral Tablet
    }

class MegestrolMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for megestrol medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable megestrol and megestrol in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Megestrol Medications"
    OID = "2.16.840.1.113883.3.464.1003.1247"
    DEFINITION_VERSION = "20240110"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "577154",  # megestrol acetate 125 MG/ML Oral Suspension
        "860215",  # megestrol acetate 20 MG Oral Tablet
        "860221",  # megestrol acetate 40 MG Oral Tablet
        "860225",  # megestrol acetate 40 MG/ML Oral Suspension
    }

class MeperidineMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for meperidine medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable nonbenzodiazepine hypnotic medication.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Meperidine Medications"
    OID = "2.16.840.1.113883.3.464.1003.1248"
    DEFINITION_VERSION = "20240110"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1665685",  # 1 ML meperidine hydrochloride 100 MG/ML Injection
        "1665697",  # 1 ML meperidine hydrochloride 50 MG/ML Injection
        "1665699",  # 0.5 ML meperidine hydrochloride 50 MG/ML Injection
        "1665701",  # 2 ML meperidine hydrochloride 50 MG/ML Injection
        "2539186",  # 1 ML meperidine hydrochloride 50 MG/ML Prefilled Syringe
        "2539191",  # 1 ML meperidine hydrochloride 25 MG/ML Prefilled Syringe
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
    }

class MeprobamateMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for meprobamate medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Meprobamate Medications"
    OID = "2.16.840.1.113883.3.464.1003.1057"
    DEFINITION_VERSION = "20210909"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "197928",  # meprobamate 200 MG Oral Tablet
        "197929",  # meprobamate 400 MG Oral Tablet
    }

class NifedipineMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for disopyramide and nifedipine (excluding extended release) medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Nifedipine Medications"
    OID = "2.16.840.1.113883.3.464.1003.1053"
    DEFINITION_VERSION = "20240117"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "198032",  # nifedipine 10 MG Oral Capsule
        "198033",  # nifedipine 20 MG Oral Capsule
    }

class PotentiallyHarmfulAntidepressantsForOlderAdults(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for potentially harmful antidepressants for older adults as described in the 2023 American Geriatrics Society BEERS criteria

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes Amoxapine, Amitriptyline Hydrochloride, Desipramine, Nortriptyline, Clomipramine, Paroxetine, Imipramine. Includes concepts that represent generic, human use and prescribable medications. Imipramine

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Potentially Harmful Antidepressants for Older Adults"
    OID = "2.16.840.1.113883.3.464.1003.1054"
    DEFINITION_VERSION = "20240120"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1099288",  # desipramine hydrochloride 10 MG Oral Tablet
        "1099292",  # desipramine hydrochloride 100 MG Oral Tablet
        "1099296",  # desipramine hydrochloride 150 MG Oral Tablet
        "1099300",  # desipramine hydrochloride 25 MG Oral Tablet
        "1099304",  # desipramine hydrochloride 50 MG Oral Tablet
        "1099316",  # desipramine hydrochloride 75 MG Oral Tablet
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
        "197363",  # amoxapine 100 MG Oral Tablet
        "197364",  # amoxapine 150 MG Oral Tablet
        "197365",  # amoxapine 25 MG Oral Tablet
        "197366",  # amoxapine 50 MG Oral Tablet
        "198045",  # nortriptyline 10 MG Oral Capsule
        "198046",  # nortriptyline 50 MG Oral Capsule
        "198047",  # nortriptyline 75 MG Oral Capsule
        "312036",  # nortriptyline 2 MG/ML Oral Solution
        "312242",  # paroxetine hydrochloride 2 MG/ML Oral Suspension
        "317136",  # nortriptyline 25 MG Oral Capsule
        "835564",  # imipramine hydrochloride 25 MG Oral Tablet
        "835568",  # imipramine hydrochloride 50 MG Oral Tablet
        "835572",  # imipramine pamoate 75 MG Oral Capsule
        "835577",  # imipramine pamoate 150 MG Oral Capsule
        "835589",  # imipramine pamoate 125 MG Oral Capsule
        "835591",  # imipramine pamoate 100 MG Oral Capsule
        "835593",  # imipramine hydrochloride 10 MG Oral Tablet
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
    }

class PotentiallyHarmfulAntihistaminesForOlderAdults(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for potentially harmful antihistamines for older adults as described in the 2023 American Geriatrics Society BEERS criteria

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable medications. Includes Diphenhydramine, Hydroxyzine, Chlorpheniramine, Promethazine, Triprolidine, Cyproheptadine, Dimenhydrinate, Meclizine, Brompheniramine, Doxylamine.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Potentially Harmful Antihistamines for Older Adults"
    OID = "2.16.840.1.113883.3.464.1003.1043"
    DEFINITION_VERSION = "20240120"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1013619",  # chlorpheniramine maleate 3 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1014331",  # brompheniramine maleate 0.4 MG/ML / chlophedianol hydrochloride 2.5 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1020477",  # diphenhydramine hydrochloride 50 MG Oral Capsule
        "1042675",  # acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 0.667 MG/ML / doxylamine succinate 0.417 MG/ML Oral Solution
        "1042684",  # acetaminophen 33.3 MG/ML / dextromethorphan hydrobromide 1 MG/ML / doxylamine succinate 0.417 MG/ML Oral Solution
        "1042688",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Capsule
        "1042693",  # chlorpheniramine maleate 0.4 MG/ML / codeine phosphate 2 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "1043400",  # acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 1 MG/ML / doxylamine succinate 0.417 MG/ML Oral Solution
        "1046384",  # acetaminophen 21.7 MG/ML / chlorpheniramine maleate 0.133 MG/ML / dextromethorphan hydrobromide 1 MG/ML Oral Solution
        "1046751",  # acetaminophen 325 MG / diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 5 MG Oral Tablet
        "1046781",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG / phenylephrine hydrochloride 5 MG Oral Tablet
        "1048124",  # 12 HR atropine sulfate 0.04 MG / chlorpheniramine maleate 8 MG / hyoscyamine sulfate 0.19 MG / pseudoephedrine hydrochloride 90 MG / scopolamine hydrobromide 0.01 MG Extended Release Oral Tablet
        "1049630",  # diphenhydramine hydrochloride 25 MG Oral Tablet
        "1049884",  # diphenhydramine hydrochloride 1.25 MG/ML Oral Solution
        "1049900",  # diphenhydramine hydrochloride 12.5 MG Chewable Tablet
        "1049906",  # diphenhydramine hydrochloride 2.5 MG/ML Oral Solution
        "1049909",  # diphenhydramine hydrochloride 25 MG Oral Capsule
        "1050385",  # acetaminophen 32 MG/ML / diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution
        "1052462",  # acetaminophen 325 MG / diphenhydramine hydrochloride 12.5 MG Oral Tablet
        "1052467",  # acetaminophen 500 MG / diphenhydramine hydrochloride 12.5 MG Oral Tablet
        "1052647",  # acetaminophen 325 MG / doxylamine succinate 6.25 MG / phenylephrine hydrochloride 5 MG Oral Capsule
        "1052679",  # acetaminophen 500 MG / chlorpheniramine maleate 2 MG / phenylephrine hydrochloride 5 MG Oral Tablet
        "1052928",  # diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1053258",  # brompheniramine maleate 0.2 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution
        "1053618",  # chlorpheniramine maleate 0.4 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1053624",  # chlorpheniramine maleate 1 MG / pseudoephedrine hydrochloride 15 MG Chewable Tablet
        "1085945",  # diphenhydramine hydrochloride 50 MG Oral Tablet
        "1086443",  # chlorpheniramine maleate 0.8 MG/ML / dextromethorphan hydrobromide 3 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "1086463",  # chlorpheniramine maleate 0.8 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "1086720",  # diphenhydramine hydrochloride 2.5 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "1086750",  # acetaminophen 32 MG/ML / chlorpheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1 MG/ML Oral Suspension
        "1086991",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Tablet
        "1087459",  # 12 HR chlorpheniramine polistirex 1.6 MG/ML / hydrocodone polistirex 2 MG/ML Extended Release Suspension
        "1087607",  # acetaminophen 500 MG / diphenhydramine hydrochloride 50 MG Oral Tablet
        "1089822",  # acetaminophen 325 MG / dextromethorphan hydrobromide 15 MG / doxylamine succinate 6.25 MG / pseudoephedrine hydrochloride 30 MG Oral Capsule
        "1089968",  # acetaminophen 500 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 15 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet
        "1090443",  # chlorpheniramine maleate 4 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1090463",  # brompheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution
        "1090699",  # chlorpheniramine maleate 2 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet
        "1092189",  # acetaminophen 500 MG / diphenhydramine hydrochloride 25 MG Oral Tablet
        "1092373",  # acetaminophen 33.3 MG/ML / diphenhydramine hydrochloride 1.67 MG/ML Oral Solution
        "1092398",  # aspirin 500 MG / diphenhydramine hydrochloride 25 MG Oral Tablet
        "1093075",  # acetaminophen 325 MG / diphenhydramine hydrochloride 50 MG Oral Tablet
        "1093098",  # diphenhydramine hydrochloride 25 MG Disintegrating Oral Tablet
        "1094131",  # acetaminophen 65 MG/ML / dextromethorphan hydrobromide 2 MG/ML / diphenhydramine hydrochloride 2.5 MG/ML Oral Solution
        "1094350",  # dextromethorphan hydrobromide 3 MG/ML / doxylamine succinate 1.25 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1094355",  # doxylamine succinate 1.25 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1094434",  # phenylephrine hydrochloride 2 MG/ML / triprolidine hydrochloride 0.5 MG/ML Oral Solution
        "1094549",  # acetaminophen 325 MG / dextromethorphan hydrobromide 15 MG / doxylamine succinate 6.25 MG Oral Capsule
        "1098496",  # acetaminophen 500 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 15 MG Oral Tablet
        "1098497",  # brompheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1 MG/ML / pseudoephedrine hydrochloride 3 MG/ML Oral Solution
        "1098498",  # brompheniramine maleate 0.2 MG/ML / pseudoephedrine hydrochloride 3 MG/ML Oral Solution
        "1099308",  # pseudoephedrine hydrochloride 6 MG/ML / triprolidine hydrochloride 0.25 MG/ML Oral Solution
        "1099446",  # pseudoephedrine hydrochloride 60 MG / triprolidine hydrochloride 2.5 MG Oral Tablet
        "1099653",  # dextromethorphan hydrobromide 4 MG/ML / pseudoephedrine hydrochloride 10 MG/ML / triprolidine hydrochloride 0.938 MG/ML Oral Suspension
        "1099659",  # phenylephrine hydrochloride 10 MG / triprolidine hydrochloride 2.5 MG Oral Tablet
        "1099668",  # pseudoephedrine hydrochloride 10 MG/ML / triprolidine hydrochloride 0.938 MG/ML Oral Solution
        "1099684",  # triprolidine hydrochloride 0.25 MG/ML Oral Solution
        "1099694",  # triprolidine hydrochloride 2.5 MG Oral Tablet
        "1099719",  # pseudoephedrine hydrochloride 30 MG / triprolidine hydrochloride 1.25 MG Oral Tablet
        "1099872",  # acetaminophen 500 MG / diphenhydramine citrate 38 MG Oral Tablet
        "1101439",  # doxylamine succinate 5 MG Chewable Tablet
        "1101446",  # doxylamine succinate 25 MG Oral Tablet
        "1101457",  # doxylamine succinate 1 MG/ML Oral Solution
        "1101555",  # {1 (acetaminophen 500 MG / chlorpheniramine maleate 2 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 1 (acetaminophen 500 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1111065",  # brompheniramine maleate 0.8 MG/ML / chlophedianol hydrochloride 5 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "1111440",  # chlorpheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1.5 MG/ML Oral Solution
        "1112220",  # chlorpheniramine maleate 0.8 MG/ML / hydrocodone bitartrate 1 MG/ML / pseudoephedrine hydrochloride 12 MG/ML Oral Solution
        "1112489",  # chlorpheniramine maleate 1 MG/ML / phenylephrine hydrochloride 2.5 MG/ML Oral Solution
        "1112864",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG Oral Tablet
        "1113397",  # acetaminophen 32 MG/ML / chlorpheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Suspension
        "1113522",  # acetaminophen 32 MG/ML / chlorpheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1.5 MG/ML Oral Solution
        "1114361",  # chlorpheniramine maleate 0.133 MG/ML / dextromethorphan hydrobromide 1 MG/ML Oral Solution
        "1114838",  # chlorpheniramine maleate 2 MG/ML / phenylephrine hydrochloride 5 MG/ML Oral Solution
        "1115329",  # dextromethorphan hydrobromide 1.5 MG/ML / doxylamine succinate 0.625 MG/ML Oral Solution
        "1117245",  # acetaminophen 500 MG / diphenhydramine hydrochloride 25 MG Oral Capsule
        "1117392",  # chlorpheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1 MG/ML / pseudoephedrine hydrochloride 3 MG/ML Oral Solution
        "1147795",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet
        "1148155",  # brompheniramine maleate 0.8 MG/ML / dextromethorphan hydrobromide 4 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "1190174",  # chlorpheniramine maleate 0.4 MG/ML / dextromethorphan hydrobromide 3 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "1190448",  # 12 HR diphenhydramine hydrochloride 100 MG / pseudoephedrine hydrochloride 120 MG Extended Release Oral Tablet
        "1193293",  # acetaminophen 325 MG / chlorpheniramine maleate 4 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1233575",  # acetaminophen 325 MG / diphenhydramine hydrochloride 12.5 MG / phenylephrine hydrochloride 5 MG Oral Tablet
        "1234386",  # dextromethorphan hydrobromide 1 MG/ML / doxylamine succinate 0.417 MG/ML Oral Solution
        "1236048",  # diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution
        "1237110",  # acetaminophen 33.3 MG/ML / dextromethorphan hydrobromide 1 MG/ML / doxylamine succinate 0.417 MG/ML / pseudoephedrine hydrochloride 2 MG/ML Oral Solution
        "1242240",  # chlorpheniramine maleate 2 MG / phenylephrine hydrochloride 5 MG Oral Tablet
        "1242618",  # acetaminophen 250 MG / doxylamine succinate 25 MG / salicylamide 150 MG Oral Tablet
        "1244523",  # brompheniramine maleate 1.2 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Suspension
        "1245184",  # dimenhydrinate 25 MG Chewable Tablet
        "1245291",  # chlorpheniramine maleate 1 MG / dextromethorphan hydrobromide 5 MG / pseudoephedrine hydrochloride 15 MG Chewable Tablet
        "1245706",  # chlophedianol hydrochloride 4.8 MG/ML / chlorpheniramine maleate 0.8 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Suspension
        "1245722",  # brompheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 4 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1248057",  # phenylephrine hydrochloride 1 MG/ML / promethazine hydrochloride 1.25 MG/ML Oral Solution
        "1248354",  # diphenhydramine hydrochloride 1.67 MG/ML Oral Solution
        "1250907",  # aspirin 500 MG / diphenhydramine citrate 38.3 MG Oral Tablet
        "1250983",  # {1 (acetaminophen 500 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 15 MG Oral Tablet) / 1 (dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG Oral Capsule) } Pack
        "1251802",  # brompheniramine maleate 1 MG / phenylephrine hydrochloride 2.5 MG Chewable Tablet
        "1251811",  # chlorpheniramine maleate 1 MG / dextromethorphan hydrobromide 5 MG Chewable Tablet
        "1251928",  # acetaminophen 500 MG / chlorpheniramine maleate 2 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet
        "1291266",  # chlorpheniramine maleate 0.8 MG/ML / dextromethorphan hydrobromide 2 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "1292342",  # acetaminophen 43.3 MG/ML / chlorpheniramine maleate 0.267 MG/ML / dextromethorphan hydrobromide 2 MG/ML Oral Solution
        "1293344",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet
        "1294201",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG / pseudoephedrine hydrochloride 30 MG Oral Capsule
        "1294348",  # diphenhydramine hydrochloride 12.5 MG / phenylephrine hydrochloride 5 MG Chewable Tablet
        "1294567",  # acetaminophen 500 MG / diphenhydramine hydrochloride 12.5 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet
        "1294607",  # acetaminophen 21.7 MG/ML / diphenhydramine hydrochloride 0.833 MG/ML Oral Solution
        "1297288",  # acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine hydrochloride 5 MG Oral Capsule
        "1297390",  # chlorpheniramine maleate 2 MG / ibuprofen 200 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet
        "1297517",  # diphenhydramine hydrochloride 25 MG / magnesium salicylate 580 MG Oral Tablet
        "1297947",  # acetaminophen 500 MG / diphenhydramine citrate 38 MG Oral Powder
        "1298348",  # acetaminophen 21.7 MG/ML / diphenhydramine hydrochloride 0.833 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution
        "1299646",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 15 MG / pseudoephedrine hydrochloride 30 MG Oral Capsule
        "1299662",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / pseudoephedrine hydrochloride 30 MG Oral Capsule
        "1304105",  # brompheniramine maleate 4 MG / dextromethorphan hydrobromide 20 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1310503",  # chlorpheniramine maleate 4 MG / ibuprofen 200 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1313969",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG / phenylephrine hydrochloride 5 MG Oral Capsule
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
        "1357553",  # acetaminophen 32 MG/ML / chlorpheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution
        "1357883",  # 12 HR brompheniramine maleate 6 MG / phenylephrine hydrochloride 30 MG Extended Release Oral Tablet
        "1357894",  # 12 HR chlorpheniramine maleate 8 MG / dextromethorphan hydrobromide 30 MG / phenylephrine hydrochloride 20 MG Extended Release Oral Tablet
        "1359114",  # chlorpheniramine maleate 4 MG / dextromethorphan hydrobromide 20 MG / pseudoephedrine hydrochloride 60 MG Oral Tablet
        "1360638",  # {1 (dextromethorphan hydrobromide 1 MG/ML / doxylamine succinate 0.417 MG/ML Oral Solution) / 1 (dextromethorphan hydrobromide 1 MG/ML Oral Solution) } Pack
        "1363288",  # 12 HR chlorpheniramine maleate 12 MG Extended Release Oral Tablet
        "1363306",  # chlorpheniramine maleate 0.4 MG/ML Oral Solution
        "1363309",  # chlorpheniramine maleate 4 MG Oral Tablet
        "1363752",  # chlorpheniramine maleate 0.4 MG/ML / dextromethorphan hydrobromide 2 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "1363780",  # 12 HR chlorpheniramine maleate 12 MG / pseudoephedrine hydrochloride 120 MG Extended Release Oral Tablet
        "1366825",  # acetaminophen 80 MG / chlorpheniramine maleate 0.5 MG / dextromethorphan hydrobromide 2.5 MG / pseudoephedrine hydrochloride 7.5 MG Chewable Tablet
        "1366948",  # chlorpheniramine tannate 8 MG / phenylephrine tannate 25 MG Oral Tablet
        "1367219",  # brompheniramine tannate 2.2 MG / phenylephrine tannate 1.58 MG Chewable Tablet
        "1367225",  # chlorpheniramine maleate 2 MG / guaifenesin 100 MG / phenylephrine hydrochloride 5 MG Oral Tablet
        "1367227",  # chlorpheniramine maleate 3.5 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1368963",  # chlophedianol hydrochloride 25 MG / chlorpheniramine maleate 4 MG / phenylephrine hydrochloride 15 MG Oral Tablet
        "1370125",  # chlorpheniramine maleate 0.4 MG/ML / dextromethorphan hydrobromide 3 MG/ML Oral Solution
        "1371196",  # dextromethorphan hydrobromide 3 MG/ML / doxylamine succinate 1.25 MG/ML Oral Solution
        "1372312",  # acetaminophen 32 MG/ML / chlorpheniramine maleate 0.2 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Suspension
        "1375932",  # acetaminophen 32.5 MG/ML / diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution
        "1375948",  # doxylamine succinate 10 MG / pyridoxine hydrochloride 10 MG Delayed Release Oral Tablet
        "1421985",  # chlorpheniramine maleate 4 MG / dextromethorphan hydrobromide 30 MG Oral Tablet
        "1423702",  # brompheniramine maleate 0.4 MG/ML / dextromethorphan hydrobromide 2 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "1423711",  # chlorpheniramine maleate 0.4 MG/ML / dextromethorphan hydrobromide 2 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1424551",  # {1 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 1 (acetaminophen 325 MG / diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1424850",  # {1 (acetaminophen 32.5 MG/ML / dextromethorphan hydrobromide 1 MG/ML / guaifenesin 20 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) / 1 (acetaminophen 32.5 MG/ML / diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) } Pack
        "1424872",  # chlophedianol hydrochloride 24 MG / chlorpheniramine maleate 3.5 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1428880",  # {1 (acetaminophen 650 MG / dextromethorphan hydrobromide 20 MG / phenylephrine hydrochloride 10 MG Granules for Oral Solution) / 1 (acetaminophen 650 MG / diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 10 MG Granules for Oral Solution) } Pack
        "1428927",  # triprolidine hydrochloride 0.625 MG/ML Oral Solution
        "1429345",  # chlorpheniramine maleate 0.2 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution
        "1430522",  # 12 HR brompheniramine maleate 6 MG / pseudoephedrine hydrochloride 45 MG Extended Release Oral Tablet
        "1431245",  # acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 0.667 MG/ML / doxylamine succinate 0.417 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution
        "1441831",  # doxylamine succinate 7.5 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1486964",  # brompheniramine maleate 0.8 MG/ML / dextromethorphan hydrobromide 3 MG/ML / phenylephrine hydrochloride 1.5 MG/ML Oral Solution
        "1489310",  # chlorpheniramine maleate 0.8 MG/ML / dextromethorphan hydrobromide 4 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "1490671",  # triprolidine hydrochloride 0.5 MG/ML Oral Solution
        "1491649",  # triprolidine hydrochloride 0.938 MG/ML Oral Solution
        "1492052",  # dextromethorphan hydrobromide 4 MG/ML / phenylephrine hydrochloride 2 MG/ML / triprolidine hydrochloride 0.5 MG/ML Oral Solution
        "1534835",  # acetaminophen 650 MG / dextromethorphan hydrobromide 20 MG / doxylamine succinate 12.5 MG / phenylephrine hydrochloride 10 MG Powder for Oral Solution
        "1535609",  # {1 (acetaminophen 325 MG / diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 1 (dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1535702",  # diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Suspension
        "1535923",  # chlorpheniramine maleate 1 MG/ML / dextromethorphan hydrobromide 3 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "1536477",  # acetaminophen 250 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Effervescent Oral Tablet
        "1536503",  # aspirin 500 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet
        "1536840",  # aspirin 325 MG / chlorpheniramine maleate 2 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet
        "1536862",  # chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Effervescent Oral Tablet
        "1536999",  # acetaminophen 250 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine hydrochloride 5 MG Effervescent Oral Tablet
        "1537029",  # aspirin 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet
        "1541630",  # brompheniramine maleate 0.8 MG/ML / codeine phosphate 2 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "1546881",  # acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine hydrochloride 5 MG Oral Tablet
        "1550957",  # diphenhydramine hydrochloride 25 MG / naproxen sodium 220 MG Oral Tablet
        "1593105",  # chlorpheniramine maleate 4 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1593110",  # acetaminophen 250 MG / aspirin 250 MG / diphenhydramine citrate 38 MG Oral Tablet
        "1595631",  # acetaminophen 250 MG / brompheniramine maleate 2 MG Oral Tablet
        "1652087",  # 12 HR chlorpheniramine polistirex 0.8 MG/ML / codeine polistirex 4 MG/ML Extended Release Suspension
        "1659175",  # acetaminophen 500 MG / diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 10 MG Powder for Oral Solution
        "1659960",  # acetaminophen 650 MG / diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 10 MG Granules for Oral Solution
        "1661319",  # codeine phosphate 2 MG/ML / phenylephrine hydrochloride 2 MG/ML / triprolidine hydrochloride 0.5 MG/ML Oral Solution
        "1663612",  # brompheniramine maleate 0.2 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Suspension
        "1663815",  # meclizine hydrochloride 25 MG Disintegrating Oral Tablet
        "1664543",  # 12 HR chlorpheniramine maleate 8 MG / codeine phosphate 54.3 MG Extended Release Oral Tablet
        "1666116",  # {1 (brompheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) / 1 (diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) } Pack
        "1730187",  # {1 (aspirin 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet) / 1 (aspirin 500 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet) } Pack
        "1730190",  # {1 (dextromethorphan hydrobromide 1 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) / 1 (diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) } Pack
        "1741529",  # acetaminophen 650 MG / chlorpheniramine maleate 4 MG / phenylephrine hydrochloride 10 MG Oral Powder
        "1789508",  # triprolidine hydrochloride 0.313 MG/ML Oral Solution
        "1789740",  # diphenhydramine hydrochloride 6.25 MG/ML Oral Solution
        "1794552",  # 2 ML hydroxyzine hydrochloride 50 MG/ML Injection
        "1794554",  # 1 ML hydroxyzine hydrochloride 50 MG/ML Injection
        "1795585",  # {1 (dextromethorphan hydrobromide 2 MG/ML / guaifenesin 40 MG/ML Oral Solution) / 1 (dextromethorphan hydrobromide 3 MG/ML / doxylamine succinate 1.25 MG/ML Oral Solution) } Pack
        "1799180",  # {1 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 1 (acetaminophen 325 MG / diphenhydramine hydrochloride 12.5 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "1803669",  # {1 (acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 0.667 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution) / 1 (acetaminophen 21.7 MG/ML / diphenhydramine hydrochloride 0.833 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution) } Pack
        "1804384",  # {1 (acetaminophen 500 MG / dextromethorphan hydrobromide 20 MG / guaifenesin 400 MG / phenylephrine hydrochloride 10 MG Powder for Oral Solution) / 1 (acetaminophen 650 MG / dextromethorphan hydrobromide 20 MG / doxylamine succinate 12.5 MG / phenylephrine hydrochloride 10 MG Powder for Oral Solution) } Pack
        "1876117",  # chlorpheniramine maleate 0.4 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "1926926",  # triprolidine hydrochloride 1.25 MG/ML Oral Solution
        "1927849",  # {1 (acetaminophen 250 MG / dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Capsule) / 1 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine hydrochloride 5 MG Oral Capsule) } Pack
        "1939354",  # triprolidine hydrochloride 1.25 MG Chewable Tablet
        "198602",  # dimenhydrinate 25 MG Oral Tablet
        "198603",  # dimenhydrinate 50 MG Oral Tablet
        "1996098",  # acetaminophen 32.5 MG/ML / dextromethorphan hydrobromide 1 MG/ML / diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution
        "1999651",  # 12 HR doxylamine succinate 20 MG / pyridoxine hydrochloride 20 MG Extended Release Oral Tablet
        "2003130",  # chlorpheniramine maleate 4 MG / dextromethorphan hydrobromide 18 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "2003179",  # chlorpheniramine maleate 0.8 MG/ML / dextromethorphan hydrobromide 3.6 MG/ML Oral Solution
        "2046528",  # diphenhydramine hydrochloride 25 MG Chewable Tablet
        "2047427",  # {100 (acetaminophen 250 MG / aspirin 250 MG / caffeine 65 MG Oral Tablet) / 24 (acetaminophen 250 MG / aspirin 250 MG / diphenhydramine citrate 38 MG Oral Tablet) } Pack
        "2049283",  # acetaminophen 33.3 MG/ML / chlorpheniramine maleate 0.133 MG/ML / dextromethorphan hydrobromide 1 MG/ML / pseudoephedrine hydrochloride 2 MG/ML Oral Solution
        "2049841",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG Oral Tablet
        "2056073",  # {1 (dextromethorphan hydrobromide 1 MG/ML / guaifenesin 20 MG/ML Oral Solution) / 1 (dextromethorphan hydrobromide 1.5 MG/ML / doxylamine succinate 0.625 MG/ML Oral Solution) } Pack
        "2056893",  # chlorpheniramine maleate 0.8 MG/ML / codeine phosphate 2 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "2119625",  # {1 (chlorpheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1.5 MG/ML Oral Solution) / 1 (dextromethorphan hydrobromide 1 MG/ML / guaifenesin 20 MG/ML Oral Solution) } Pack
        "2121065",  # acetaminophen 65 MG/ML / chlorpheniramine maleate 0.4 MG/ML / dextromethorphan hydrobromide 1.3 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "2166129",  # diphenhydramine hydrochloride 0.833 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution
        "2167740",  # chlorpheniramine maleate 0.133 MG/ML / dextromethorphan hydrobromide 0.333 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution
        "2167750",  # chlorpheniramine maleate 0.8 MG/ML / dextromethorphan hydrobromide 6 MG/ML / phenylephrine hydrochloride 1.5 MG/ML Oral Solution
        "2167752",  # chlorpheniramine maleate 4 MG / dextromethorphan hydrobromide 20 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "2172491",  # doxylamine succinate 10.5 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "2173662",  # acetaminophen 32.5 MG/ML / dextromethorphan hydrobromide 1 MG/ML / phenylephrine hydrochloride 0.5 MG/ML / triprolidine hydrochloride 0.125 MG/ML Oral Solution
        "2173667",  # acetaminophen 32.5 MG/ML / dextromethorphan hydrobromide 1 MG/ML / triprolidine hydrochloride 0.125 MG/ML Oral Solution
        "2176488",  # chlorpheniramine maleate 0.133 MG/ML / dextromethorphan hydrobromide 0.333 MG/ML / pseudoephedrine hydrochloride 0.333 MG/ML Oral Solution
        "2181307",  # acetaminophen 325 MG / caffeine 45 MG / chlorpheniramine maleate 2 MG / phenylephrine hydrochloride 5 MG Oral Tablet
        "2183701",  # chlorpheniramine maleate 8 MG Extended Release Oral Capsule
        "2268058",  # dextromethorphan hydrobromide 3 MG/ML / phenylephrine hydrochloride 1 MG/ML / triprolidine hydrochloride 0.25 MG/ML Oral Solution
        "2287760",  # {1 (acetaminophen 32.5 MG/ML / dextromethorphan hydrobromide 1 MG/ML / triprolidine hydrochloride 0.125 MG/ML Oral Solution) / 1 (dextromethorphan hydrobromide 1 MG/ML / guaifenesin 20 MG/ML Oral Solution) } Pack
        "2288826",  # {1 (acetaminophen 32.5 MG/ML / dextromethorphan hydrobromide 1 MG/ML / phenylephrine hydrochloride 0.5 MG/ML / triprolidine hydrochloride 0.125 MG/ML Oral Solution) / 1 (dextromethorphan hydrobromide 1 MG/ML / guaifenesin 20 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) } Pack
        "2362250",  # {1 (chlorpheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1.5 MG/ML Oral Solution) / 1 (dextromethorphan hydrobromide 1 MG/ML / guaifenesin 10 MG/ML Oral Solution) } Pack
        "2374554",  # acetaminophen 32.5 MG/ML / diphenhydramine hydrochloride 1.25 MG/ML Oral Solution
        "2390630",  # {1 (acetaminophen 32.5 MG/ML / dextromethorphan hydrobromide 1 MG/ML / triprolidine hydrochloride 0.125 MG/ML Oral Solution) / 1 (dextromethorphan hydrobromide 1 MG/ML / guaifenesin 20 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) } Pack
        "2397132",  # {1 (acetaminophen 32.5 MG/ML / dextromethorphan hydrobromide 1 MG/ML / phenylephrine hydrochloride 0.5 MG/ML / triprolidine hydrochloride 0.125 MG/ML Oral Solution) / 1 (acetaminophen 32.5 MG/ML / guaifenesin 20 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) } Pack
        "2549034",  # acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / triprolidine hydrochloride 1.25 MG Oral Tablet
        "2549037",  # acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG / triprolidine hydrochloride 1.25 MG Oral Tablet
        "2557336",  # acetaminophen 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Effervescent Oral Tablet
        "2558505",  # {1 (acetaminophen 500 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 15 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet) / 1 (acetaminophen 500 MG / dextromethorphan hydrobromide 15 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet) } Pack
        "2560237",  # {1 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 1 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG / triprolidine hydrochloride 1.25 MG Oral Tablet) } Pack
        "2560238",  # {1 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / triprolidine hydrochloride 1.25 MG Oral Tablet) / 1 (dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "2565491",  # aspirin 325 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet
        "2565492",  # {1 (aspirin 325 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet) / 1 (aspirin 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet) } Pack
        "2603661",  # chlorpheniramine maleate 3.5 MG / dextromethorphan hydrobromide 29 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "2604562",  # acetaminophen 33.3 MG/ML / chlorpheniramine maleate 0.133 MG/ML / dextromethorphan hydrobromide 1 MG/ML Oral Solution
        "2604579",  # {1 (acetaminophen 500 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 15 MG Oral Tablet) / 1 (acetaminophen 500 MG / dextromethorphan hydrobromide 15 MG Oral Tablet) } Pack
        "2604635",  # {1 (acetaminophen 33.3 MG/ML / chlorpheniramine maleate 0.133 MG/ML / dextromethorphan hydrobromide 1 MG/ML Oral Solution) / 1 (acetaminophen 33.3 MG/ML / dextromethorphan hydrobromide 1 MG/ML Oral Solution) } Pack
        "2608082",  # acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG / triprolidine hydrochloride 1.25 MG Oral Capsule
        "2626497",  # {1 (dextromethorphan hydrobromide 0.667 MG/ML / guaifenesin 13.33 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution) / 1 (diphenhydramine hydrochloride 0.833 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution) } Pack
        "2632643",  # meclizine hydrochloride 50 MG Chewable Tablet
        "2634363",  # {1 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine hydrochloride 5 MG Oral Capsule) / 1 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Capsule) } Pack
        "2634364",  # {1 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine hydrochloride 5 MG Oral Capsule) / 1 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Capsule) } Pack
        "2634398",  # {1 (acetaminophen 325 MG / diphenhydramine hydrochloride 12.5 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 1 (acetaminophen 325 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "2634560",  # {1 (acetaminophen 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 1 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "2634561",  # {1 (acetaminophen 325 MG / chlorpheniramine maleate 2 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 1 (acetaminophen 325 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "2634562",  # {1 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / guaifenesin 100 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 1 (acetaminophen 325 MG / diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "2634564",  # {1 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Capsule) / 1 (acetaminophen 325 MG / dextromethorphan hydrobromide 15 MG / doxylamine succinate 6.25 MG Oral Capsule) } Pack
        "2634815",  # {1 (acetaminophen 325 MG / diphenhydramine hydrochloride 12.5 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 1 (dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "2634816",  # {1 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 1 (acetaminophen 325 MG / diphenhydramine hydrochloride 12.5 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "2634817",  # {1 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 1 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "2634818",  # {1 (acetaminophen 325 MG / diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 1 (acetaminophen 325 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "2634819",  # {1 (acetaminophen 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / phenylephrine hydrochloride 5 MG Oral Tablet) / 1 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG / guaifenesin 200 MG / phenylephrine hydrochloride 5 MG Oral Tablet) } Pack
        "2634822",  # {1 (acetaminophen 325 MG / doxylamine succinate 6.25 MG / phenylephrine hydrochloride 5 MG Oral Capsule) / 1 (acetaminophen 325 MG / phenylephrine hydrochloride 5 MG Oral Capsule) } Pack
        "2637485",  # dextromethorphan hydrobromide 2 MG/ML / triprolidine hydrochloride 0.25 MG/ML Oral Solution
        "2637726",  # {1 (acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 0.667 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution) / 1 (acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 1 MG/ML / doxylamine succinate 0.417 MG/ML Oral Solution) } Pack
        "2637727",  # {1 (acetaminophen 32.5 MG/ML / dextromethorphan hydrobromide 1 MG/ML / guaifenesin 20 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) / 1 (acetaminophen 32.5 MG/ML / dextromethorphan hydrobromide 1 MG/ML / phenylephrine hydrochloride 0.5 MG/ML / triprolidine hydrochloride 0.125 MG/ML Oral Solution) } Pack
        "2637728",  # {1 (acetaminophen 32.5 MG/ML / diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) / 1 (dextromethorphan hydrobromide 1 MG/ML / guaifenesin 20 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) } Pack
        "2637729",  # {1 (acetaminophen 32.5 MG/ML / dextromethorphan hydrobromide 1 MG/ML / guaifenesin 20 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) / 1 (acetaminophen 32.5 MG/ML / dextromethorphan hydrobromide 1 MG/ML / triprolidine hydrochloride 0.125 MG/ML Oral Solution) } Pack
        "2637730",  # {1 (acetaminophen 32.5 MG/ML / diphenhydramine hydrochloride 1.25 MG/ML / phenylephrine hydrochloride 0.5 MG/ML Oral Solution) / 1 (dextromethorphan hydrobromide 1 MG/ML / guaifenesin 20 MG/ML Oral Solution) } Pack
        "2637731",  # {1 (acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 0.667 MG/ML / doxylamine succinate 0.417 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution) / 1 (acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 0.667 MG/ML / guaifenesin 13.3 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution) } Pack
        "2637756",  # {1 (acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 0.667 MG/ML Oral Solution) / 1 (acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 1 MG/ML / doxylamine succinate 0.417 MG/ML Oral Solution) } Pack
        "2639176",  # {1 (diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 10 MG Oral Tablet) / 1 (phenylephrine hydrochloride 10 MG Oral Tablet) } Pack
        "2640034",  # {1 (acetaminophen 500 MG / dextromethorphan hydrobromide 20 MG / phenylephrine hydrochloride 10 MG Granules for Oral Solution) / 1 (acetaminophen 650 MG / diphenhydramine hydrochloride 25 MG / phenylephrine hydrochloride 10 MG Granules for Oral Solution) } Pack
        "2644878",  # {1 (chlorpheniramine maleate 0.133 MG/ML / dextromethorphan hydrobromide 1 MG/ML Oral Solution) / 1 (dextromethorphan hydrobromide 0.667 MG/ML / guaifenesin 6.667 MG/ML / phenylephrine hydrochloride 0.333 MG/ML Oral Solution) } Pack
        "2664074",  # {1 (aspirin 325 MG / chlorpheniramine maleate 2 MG / dextromethorphan hydrobromide 10 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet) / 1 (aspirin 325 MG / dextromethorphan hydrobromide 10 MG / phenylephrine bitartrate 7.8 MG Effervescent Oral Tablet) } Pack
        "2670677",  # acetaminophen 650 MG / diphenhydramine hydrochloride 25 MG Powder for Oral Solution
        "2676954",  # {1 (acetaminophen 325 MG / dextromethorphan hydrobromide 10 MG Oral Capsule) / 1 (acetaminophen 325 MG / dextromethorphan hydrobromide 15 MG / doxylamine succinate 6.25 MG Oral Capsule) } Pack
        "2681010",  # {1 (acetaminophen 33.3 MG/ML / diphenhydramine hydrochloride 1.67 MG/ML Oral Solution) / 1 (acetaminophen 33.3 MG/ML Oral Solution) } Pack
        "2683226",  # {1 (dextromethorphan hydrobromide 1 MG/ML / guaifenesin 20 MG/ML Oral Solution) / 1 (diphenhydramine hydrochloride 2.5 MG/ML Oral Solution) } Pack
        "2683422",  # {1 (brompheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1 MG/ML Oral Solution) / 1 (diphenhydramine hydrochloride 1.25 MG/ML Oral Solution) } Pack
        "2683423",  # dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG Chewable Tablet
        "2683425",  # {1 (dextromethorphan hydrobromide 10 MG / doxylamine succinate 6.25 MG Chewable Tablet) / 1 (dextromethorphan hydrobromide 10 MG Chewable Tablet) } Pack
        "2687211",  # {1 (acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 0.667 MG/ML / doxylamine succinate 0.417 MG/ML Oral Solution) / 1 (acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 0.667 MG/ML Oral Solution) } Pack
        "2695452",  # {1 (acetaminophen 21.7 MG/ML / dextromethorphan hydrobromide 0.667 MG/ML / guaifenesin 13.3 MG/ML Oral Solution) / 1 (acetaminophen 21.7 MG/ML / diphenhydramine hydrochloride 0.833 MG/ML Oral Solution) } Pack
        "309913",  # dimenhydrinate 50 MG Chewable Tablet
        "309914",  # dimenhydrinate 50 MG/ML Injectable Solution
        "359281",  # 12 HR brompheniramine maleate 6 MG Extended Release Oral Tablet
        "477045",  # chlorpheniramine maleate 2 MG/ML Oral Solution
        "604664",  # chlorpheniramine maleate 0.4 MG/ML / phenylephrine hydrochloride 1.5 MG/ML / pyrilamine maleate 2.5 MG/ML Oral Solution
        "636568",  # chlorpheniramine maleate 0.2 MG/ML / dextromethorphan hydrobromide 1 MG/ML Oral Solution
        "700851",  # brompheniramine maleate 1 MG/ML Oral Solution
        "700949",  # chlorpheniramine maleate 0.6 MG/ML / dextromethorphan hydrobromide 2.75 MG/ML / phenylephrine hydrochloride 1.5 MG/ML Oral Solution
        "731032",  # 12 HR brompheniramine maleate 11 MG Extended Release Oral Tablet
        "759494",  # {14 (12 HR brompheniramine maleate 6 MG / pseudoephedrine hydrochloride 45 MG Extended Release Oral Tablet) / 14 (12 HR chlorpheniramine maleate 8 MG / methscopolamine nitrate 2.5 MG / phenylephrine hydrochloride 25 MG Extended Release Oral Tablet) } Pack
        "857512",  # 12 HR chlorpheniramine polistirex 8 MG / hydrocodone polistirex 10 MG Extended Release Oral Capsule
        "866021",  # cyproheptadine hydrochloride 0.4 MG/ML Oral Solution
        "866144",  # cyproheptadine hydrochloride 4 MG Oral Tablet
        "882504",  # diphenhydramine hydrochloride 12.5 MG Disintegrating Oral Tablet
        "895664",  # diphenhydramine citrate 38 MG / ibuprofen 200 MG Oral Tablet
        "901814",  # diphenhydramine hydrochloride 25 MG / ibuprofen 200 MG Oral Capsule
        "991486",  # codeine phosphate 2 MG/ML / promethazine hydrochloride 1.25 MG/ML Oral Solution
        "991528",  # dextromethorphan hydrobromide 3 MG/ML / promethazine hydrochloride 1.25 MG/ML Oral Solution
        "992432",  # promethazine hydrochloride 1.25 MG/ML Oral Solution
        "992438",  # promethazine hydrochloride 12.5 MG Oral Tablet
        "992447",  # promethazine hydrochloride 25 MG Oral Tablet
        "992460",  # 1 ML promethazine hydrochloride 25 MG/ML Injection
        "992475",  # promethazine hydrochloride 50 MG Oral Tablet
        "992858",  # 1 ML promethazine hydrochloride 50 MG/ML Injection
        "994289",  # brompheniramine maleate 0.27 MG/ML / codeine phosphate 1.27 MG/ML / pseudoephedrine hydrochloride 2 MG/ML Oral Solution
        "994402",  # brompheniramine maleate 0.4 MG/ML / codeine phosphate 1.5 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
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
        "995218",  # hydroxyzine hydrochloride 10 MG Oral Tablet
        "995232",  # hydroxyzine pamoate 100 MG Oral Capsule
        "995241",  # hydroxyzine hydrochloride 2 MG/ML Oral Solution
        "995253",  # hydroxyzine pamoate 25 MG Oral Capsule
        "995258",  # hydroxyzine hydrochloride 25 MG Oral Tablet
        "995270",  # 1 ML hydroxyzine hydrochloride 25 MG/ML Injection
        "995278",  # hydroxyzine pamoate 50 MG Oral Capsule
        "995281",  # hydroxyzine hydrochloride 50 MG Oral Tablet
        "995285",  # hydroxyzine hydrochloride 50 MG/ML Injectable Solution
        "995624",  # meclizine hydrochloride 12.5 MG Oral Tablet
        "995632",  # meclizine hydrochloride 25 MG Chewable Tablet
        "995666",  # meclizine hydrochloride 25 MG Oral Tablet
        "995686",  # meclizine hydrochloride 50 MG Oral Tablet
        "996757",  # codeine phosphate 2 MG/ML / phenylephrine hydrochloride 1 MG/ML / promethazine hydrochloride 1.25 MG/ML Oral Solution
        "996998",  # brompheniramine maleate 0.266 MG/ML / codeine phosphate 1.27 MG/ML / phenylephrine hydrochloride 0.666 MG/ML Oral Solution
        "998254",  # chlorpheniramine maleate 4 MG / pseudoephedrine hydrochloride 60 MG Oral Tablet
    }

class PotentiallyHarmfulAntiinfectivesForOlderAdults(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for potentially harmful ant infectives for older adults as described in the 2023 American Geriatrics Society BEERS criteria.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use, prescribable nitrofurantoin and nitrofurantoin in combination with other medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable, branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Potentially Harmful Antiinfectives for Older Adults"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1481"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1648759",  # nitrofurantoin, macrocrystals 100 MG Oral Capsule
        "311989",  # nitrofurantoin 5 MG/ML Oral Suspension
        "311994",  # nitrofurantoin, macrocrystals 25 MG Oral Capsule
        "311995",  # nitrofurantoin, macrocrystals 50 MG Oral Capsule
        "422434",  # nitrofurantoin 10 MG/ML Oral Suspension
    }

class PotentiallyHarmfulAntiparkinsonianAgentsForOlderAdults(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for potentially harmful antiparkinsonian agents for older adults as described in the 2023 American Geriatrics Society BEERS criteria

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable medications. Includes Benztripine and Trihexyphenidyl medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Potentially Harmful Antiparkinsonian Agents for Older Adults"
    OID = "2.16.840.1.113883.3.464.1003.1049"
    DEFINITION_VERSION = "20240123"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "885209",  # benztropine mesylate 2 MG Oral Tablet
        "885213",  # benztropine mesylate 1 MG Oral Tablet
        "885219",  # benztropine mesylate 0.5 MG Oral Tablet
        "905269",  # trihexyphenidyl hydrochloride 2 MG Oral Tablet
        "905273",  # trihexyphenidyl hydrochloride 0.4 MG/ML Oral Solution
        "905283",  # trihexyphenidyl hydrochloride 5 MG Oral Tablet
    }

class PotentiallyHarmfulAntipsychoticsForOlderAdults(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for potentially harmful antipsychotics for older adults as described in the 2023 American Geriatrics Society BEERS criteria.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable antipsychotic medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Potentially Harmful Antipsychotics for Older Adults"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1523"
    DEFINITION_VERSION = "20220213"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
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
        "141935",  # haloperidol 2 MG/ML Oral Solution
        "1431235",  # lurasidone hydrochloride 60 MG Oral Tablet
        "1602163",  # 1.5 ML aripiprazole 200 MG/ML Prefilled Syringe
        "1602171",  # 2 ML aripiprazole 200 MG/ML Prefilled Syringe
        "1606337",  # asenapine 2.5 MG Sublingual Tablet
        "1648646",  # {1 (24 HR quetiapine 200 MG Extended Release Oral Tablet) / 11 (24 HR quetiapine 300 MG Extended Release Oral Tablet) / 3 (24 HR quetiapine 50 MG Extended Release Oral Tablet) } Pack
        "1650966",  # 0.88 ML paliperidone palmitate 310 MG/ML Prefilled Syringe
        "1650971",  # 1.32 ML paliperidone palmitate 311 MG/ML Prefilled Syringe
        "1650973",  # 1.75 ML paliperidone palmitate 312 MG/ML Prefilled Syringe
        "1650975",  # 2.63 ML paliperidone palmitate 311 MG/ML Prefilled Syringe
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
        "1876502",  # 1 ML haloperidol 5 MG/ML Prefilled Syringe
        "1925262",  # 3.9 ML aripiprazole lauroxil 273 MG/ML Prefilled Syringe
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
        "1998451",  # Sensor aripiprazole 10 MG Oral Tablet
        "1998454",  # Sensor aripiprazole 15 MG Oral Tablet
        "1998456",  # Sensor aripiprazole 2 MG Oral Tablet
        "1998458",  # Sensor aripiprazole 20 MG Oral Tablet
        "1998460",  # Sensor aripiprazole 30 MG Oral Tablet
        "1998462",  # Sensor aripiprazole 5 MG Oral Tablet
        "200034",  # olanzapine 2.5 MG Oral Tablet
        "204416",  # haloperidol 5 MG/ML Injectable Solution
        "2049269",  # pimavanserin 10 MG Oral Tablet
        "2049275",  # pimavanserin 34 MG Oral Capsule
        "2049341",  # 2.4 ML aripiprazole lauroxil 281.3 MG/ML Prefilled Syringe
        "2055667",  # 0.8 ML risperidone 150 MG/ML Prefilled Syringe
        "2055675",  # 0.6 ML risperidone 150 MG/ML Prefilled Syringe
        "2570392",  # olanzapine 5 MG / samidorphan 10 MG Oral Tablet
        "2570399",  # olanzapine 10 MG / samidorphan 10 MG Oral Tablet
        "2570402",  # olanzapine 15 MG / samidorphan 10 MG Oral Tablet
        "2570405",  # olanzapine 20 MG / samidorphan 10 MG Oral Tablet
        "2570418",  # 3.5 ML paliperidone palmitate 312 MG/ML Prefilled Syringe
        "2570420",  # 5 ML paliperidone palmitate 312 MG/ML Prefilled Syringe
        "2636033",  # 0.28 ML risperidone 357 MG/ML Prefilled Syringe
        "2636041",  # 0.35 ML risperidone 357 MG/ML Prefilled Syringe
        "2636043",  # 0.42 ML risperidone 357 MG/ML Prefilled Syringe
        "2636045",  # 0.56 ML risperidone 357 MG/ML Prefilled Syringe
        "2636047",  # 0.7 ML risperidone 357 MG/ML Prefilled Syringe
        "2636049",  # 0.14 ML risperidone 357 MG/ML Prefilled Syringe
        "2636051",  # 0.21 ML risperidone 357 MG/ML Prefilled Syringe
        "2636637",  # 2.4 ML aripiprazole 300 MG/ML Prefilled Syringe
        "2636645",  # 3.2 ML aripiprazole 300 MG/ML Prefilled Syringe
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
        "991053",  # chlorpromazine hydrochloride 100 MG/ML Oral Solution
        "991188",  # chlorpromazine hydrochloride 200 MG Oral Tablet
        "991194",  # chlorpromazine hydrochloride 25 MG Oral Tablet
        "991332",  # chlorpromazine hydrochloride 30 MG/ML Oral Solution
        "991336",  # chlorpromazine hydrochloride 50 MG Oral Tablet
        "996921",  # clozapine 200 MG Disintegrating Oral Tablet
    }

class PotentiallyHarmfulBarbituratesForOlderAdults(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for potentially harmful barbituates for older adults as described in the 2023 American Geriatrics Society BEERS criteria.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes butalbital, phenobarbital and Primidone. Includes concepts that represent generic, human use and prescribable medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Potentially Harmful Barbiturates for Older Adults"
    OID = "2.16.840.1.113883.3.464.1003.1055"
    DEFINITION_VERSION = "20240123"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1046787",  # atropine sulfate 0.00388 MG/ML / hyoscyamine sulfate 0.0207 MG/ML / phenobarbital 3.24 MG/ML / scopolamine hydrobromide 0.0013 MG/ML Oral Solution
        "1046815",  # atropine sulfate 0.0194 MG / hyoscyamine sulfate 0.1037 MG / phenobarbital 16.2 MG / scopolamine hydrobromide 0.0065 MG Oral Tablet
        "1046997",  # atropine sulfate 0.0582 MG / hyoscyamine sulfate 0.311 MG / phenobarbital 48.6 MG / scopolamine hydrobromide 0.0195 MG Extended Release Oral Tablet
        "1249617",  # acetaminophen 300 MG / butalbital 50 MG Oral Tablet
        "1431286",  # acetaminophen 300 MG / butalbital 50 MG / caffeine 40 MG / codeine phosphate 30 MG Oral Capsule
        "1724446",  # acetaminophen 325 MG / butalbital 25 MG Oral Tablet
        "197426",  # acetaminophen 325 MG / butalbital 50 MG Oral Tablet
        "198083",  # phenobarbital 100 MG Oral Tablet
        "198085",  # phenobarbital 16 MG Oral Tablet
        "198086",  # phenobarbital 16.2 MG Oral Tablet
        "198089",  # phenobarbital 60 MG Oral Tablet
        "198150",  # primidone 50 MG Oral Tablet
        "198368",  # phenobarbital 65 MG/ML Injectable Solution
        "199164",  # phenobarbital 97.2 MG Oral Tablet
        "199167",  # phenobarbital 32.4 MG Oral Tablet
        "199168",  # phenobarbital 64.8 MG Oral Tablet
        "1995136",  # acetaminophen 300 MG / butalbital 50 MG Oral Capsule
        "238134",  # aspirin 325 MG / butalbital 50 MG / caffeine 40 MG Oral Capsule
        "238135",  # aspirin 325 MG / butalbital 50 MG / caffeine 40 MG Oral Tablet
        "238153",  # acetaminophen 325 MG / butalbital 50 MG / caffeine 40 MG Oral Capsule
        "238154",  # acetaminophen 325 MG / butalbital 50 MG / caffeine 40 MG Oral Tablet
        "2583731",  # aspirin 500 MG / butalbital 50 MG / caffeine 40 MG Oral Capsule
        "2624719",  # phenobarbital sodium 100 MG Injection
        "2671204",  # 1 ML phenobarbital sodium 130 MG/ML Injection
        "2671207",  # 1 ML phenobarbital sodium 65 MG/ML Injection
        "312357",  # phenobarbital 15 MG Oral Tablet
        "312362",  # phenobarbital 30 MG Oral Tablet
        "312370",  # phenobarbital 130 MG/ML Injectable Solution
        "328176",  # primidone 125 MG Oral Tablet
        "702519",  # phenobarbital 4 MG/ML Oral Solution
        "756245",  # acetaminophen 21.7 MG/ML / butalbital 3.33 MG/ML / caffeine 2.67 MG/ML Oral Solution
        "889520",  # acetaminophen 300 MG / butalbital 50 MG / caffeine 40 MG Oral Capsule
        "96304",  # primidone 250 MG Oral Tablet
        "993943",  # acetaminophen 325 MG / butalbital 50 MG / caffeine 40 MG / codeine phosphate 30 MG Oral Capsule
        "994237",  # aspirin 325 MG / butalbital 50 MG / caffeine 40 MG / codeine phosphate 30 MG Oral Capsule
    }

class PotentiallyHarmfulBenzodiazepinesForOlderAdults(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for potentially harmful benzodiazepines for older adults as described in the 2023 American Geriatrics Society BEERS criteria.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable benzodiazepine medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Potentially Harmful Benzodiazepines for Older Adults"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1522"
    DEFINITION_VERSION = "20220212"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1366192",  # clobazam 2.5 MG/ML Oral Suspension
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
        "197653",  # estazolam 1 MG Oral Tablet
        "197654",  # estazolam 2 MG Oral Tablet
        "197900",  # lorazepam 0.5 MG Oral Tablet
        "197901",  # lorazepam 1 MG Oral Tablet
        "197902",  # lorazepam 2 MG Oral Tablet
        "198057",  # oxazepam 10 MG Oral Capsule
        "198059",  # oxazepam 30 MG Oral Capsule
        "198241",  # temazepam 15 MG Oral Capsule
        "198242",  # temazepam 30 MG Oral Capsule
        "198243",  # temazepam 7.5 MG Oral Capsule
        "198317",  # triazolam 0.125 MG Oral Tablet
        "198318",  # triazolam 0.25 MG Oral Tablet
        "199450",  # clobazam 10 MG Oral Tablet
        "2120550",  # 2 ML diazepam 5 MG/ML Prefilled Syringe
        "238100",  # lorazepam 2 MG/ML Injectable Solution
        "238101",  # lorazepam 4 MG/ML Injectable Solution
        "246172",  # clobazam 20 MG Oral Tablet
        "2541170",  # 50 ML midazolam 1 MG/ML Injection
        "2541171",  # 100 ML midazolam 1 MG/ML Injection
        "2569564",  # 24 HR lorazepam 1 MG Extended Release Oral Capsule
        "2569573",  # 24 HR lorazepam 2 MG Extended Release Oral Capsule
        "2569577",  # 24 HR lorazepam 3 MG Extended Release Oral Capsule
        "2594600",  # 24 HR lorazepam 1.5 MG Extended Release Oral Capsule
        "2608698",  # 0.7 ML midazolam 14.3 MG/ML Auto-Injector
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
        "427538",  # clobazam 5 MG Oral Tablet
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
    }

class PotentiallyHarmfulEstrogensForOlderAdults(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for potentially harmful estrogens for older adults as described in the 2023 American Geriatrics Society BEERS criteria.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable medications. Includes only oral and topical patch products. Includes Esterified Estrogens, Estradiol, Estropipate and Conjugated Estrogens

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients. Excludes implant and injection medications.
    """

    VALUE_SET_NAME = "Potentially Harmful Estrogens for Older Adults"
    OID = "2.16.840.1.113883.3.464.1003.1058"
    DEFINITION_VERSION = "20240123"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1000351",  # estrogens, conjugated (USP) 0.3 MG / medroxyprogesterone acetate 1.5 MG Oral Tablet
        "1000352",  # estrogens, conjugated (USP) 0.45 MG / medroxyprogesterone acetate 1.5 MG Oral Tablet
        "1000355",  # estrogens, conjugated (USP) 0.625 MG / medroxyprogesterone acetate 2.5 MG Oral Tablet
        "1000356",  # estrogens, conjugated (USP) 0.625 MG / medroxyprogesterone acetate 5 MG Oral Tablet
        "1000395",  # {28 (estrogens, conjugated (USP) 0.625 MG / medroxyprogesterone acetate 2.5 MG Oral Tablet) } Pack
        "1000398",  # {28 (estrogens, conjugated (USP) 0.625 MG / medroxyprogesterone acetate 5 MG Oral Tablet) } Pack
        "1000486",  # {14 (estrogens, conjugated (USP) 0.625 MG / medroxyprogesterone acetate 5 MG Oral Tablet) / 14 (estrogens, conjugated (USP) 0.625 MG Oral Tablet) } Pack
        "1000490",  # {28 (estrogens, conjugated (USP) 0.3 MG / medroxyprogesterone acetate 1.5 MG Oral Tablet) } Pack
        "1000496",  # {28 (estrogens, conjugated (USP) 0.45 MG / medroxyprogesterone acetate 1.5 MG Oral Tablet) } Pack
        "1149632",  # 84 HR estradiol 0.00313 MG/HR Transdermal System
        "1251493",  # 84 HR estradiol 0.00208 MG/HR / norethindrone acetate 0.00583 MG/HR Transdermal System
        "1251499",  # 84 HR estradiol 0.00208 MG/HR / norethindrone acetate 0.0104 MG/HR Transdermal System
        "1359123",  # estradiol 0.5 MG / norethindrone acetate 0.1 MG Oral Tablet
        "1359124",  # {28 (estradiol 0.5 MG / norethindrone acetate 0.1 MG Oral Tablet) } Pack
        "1359126",  # estradiol 1 MG / norethindrone acetate 0.5 MG Oral Tablet
        "1359127",  # {28 (estradiol 1 MG / norethindrone acetate 0.5 MG Oral Tablet) } Pack
        "1441392",  # bazedoxifene 20 MG / estrogens, conjugated (USP) 0.45 MG Oral Tablet
        "1483549",  # drospirenone 0.25 MG / estradiol 0.5 MG Oral Tablet
        "1483550",  # {28 (drospirenone 0.25 MG / estradiol 0.5 MG Oral Tablet) } Pack
        "1483552",  # drospirenone 0.5 MG / estradiol 1 MG Oral Tablet
        "1483553",  # {28 (drospirenone 0.5 MG / estradiol 1 MG Oral Tablet) } Pack
        "197657",  # estradiol 0.5 MG Oral Tablet
        "197658",  # estradiol 1 MG Oral Tablet
        "197659",  # estradiol 2 MG Oral Tablet
        "197660",  # estrogens, conjugated (USP) 0.3 MG Oral Tablet
        "197661",  # estrogens, conjugated (USP) 0.9 MG Oral Tablet
        "197662",  # estrogens, conjugated (USP) 1.25 MG Oral Tablet
        "197666",  # estrogens, esterified (USP) 0.3 MG Oral Tablet
        "197667",  # estrogens, esterified (USP) 0.625 MG Oral Tablet
        "197668",  # estrogens, esterified (USP) 1.25 MG Oral Tablet
        "197669",  # estrogens, esterified (USP) 2.5 MG Oral Tablet
        "197670",  # estrogens, esterified (USP) 1.25 MG / methyltestosterone 2.5 MG Oral Tablet
        "2108924",  # estradiol 1 MG / progesterone 100 MG Oral Capsule
        "2371764",  # elagolix 300 MG / estradiol 1 MG / norethindrone 0.5 MG Oral Capsule
        "2371767",  # {28 (elagolix 300 MG / estradiol 1 MG / norethindrone 0.5 MG Oral Capsule) / 28 (elagolix 300 MG Oral Capsule) } Pack
        "238003",  # 168 HR estradiol 0.00208 MG/HR Transdermal System
        "238004",  # 168 HR estradiol 0.00417 MG/HR Transdermal System
        "238006",  # estrogens, esterified (USP) 0.625 MG / methyltestosterone 1.25 MG Oral Tablet
        "241527",  # 168 HR estradiol 0.00312 MG/HR Transdermal System
        "241946",  # 84 HR estradiol 0.00156 MG/HR Transdermal System
        "242333",  # 168 HR estradiol 0.00104 MG/HR Transdermal System
        "242891",  # 84 HR estradiol 0.00208 MG/HR Transdermal System
        "242892",  # 84 HR estradiol 0.00417 MG/HR Transdermal System
        "248478",  # 84 HR estradiol 0.00104 MG/HR Transdermal System
        "2556799",  # estradiol 1 MG / norethindrone acetate 0.5 MG / relugolix 40 MG Oral Tablet
        "2632844",  # estradiol 0.5 MG / progesterone 100 MG Oral Capsule
        "310197",  # estrogens, conjugated (USP) 0.625 MG Oral Tablet
        "310212",  # estropipate 0.75 MG Oral Tablet
        "310213",  # estropipate 1.5 MG Oral Tablet
        "348906",  # estradiol 1 MG / norgestimate 0.09 MG Oral Tablet
        "402250",  # 168 HR estradiol 0.00188 MG/HR / levonorgestrel 0.000625 MG/HR Transdermal System
        "403849",  # estrogens, conjugated (USP) 0.45 MG Oral Tablet
        "403922",  # 168 HR estradiol 0.00156 MG/HR Transdermal System
        "403923",  # 168 HR estradiol 0.0025 MG/HR Transdermal System
        "476545",  # 168 HR estradiol 0.000583 MG/HR Transdermal System
        "577027",  # estradiol 0.45 MG Oral Tablet
        "577029",  # estradiol 1.8 MG Oral Tablet
        "749850",  # {15 (estradiol 1 MG / norgestimate 0.09 MG Oral Tablet) / 15 (estradiol 1 MG Oral Tablet) } Pack
        "978941",  # estradiol valerate 3 MG Oral Tablet
        "978944",  # dienogest 2 MG / estradiol valerate 2 MG Oral Tablet
        "978946",  # dienogest 3 MG / estradiol valerate 2 MG Oral Tablet
        "978948",  # estradiol valerate 1 MG Oral Tablet
        "978949",  # {5 (dienogest 2 MG / estradiol valerate 2 MG Oral Tablet) / 17 (dienogest 3 MG / estradiol valerate 2 MG Oral Tablet) / 2 (estradiol valerate 1 MG Oral Tablet) / 2 (estradiol valerate 3 MG Oral Tablet) / 2 (inert ingredients 1 MG Oral Tablet) } Pack
    }

class PotentiallyHarmfulGastrointestinalAntispasmodicsForOlderAdults(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for potentially harmful Gastrointestinal Antispasmodics for older adults as described in the 2023 American Geriatrics Society BEERS criteria.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes atropine, chlordiazepoxide-clidinium, dicyclomine, hyoscyamine, and scopolamine. Includes concepts that represent generic, human use and prescribable medications.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients. Excludes ophthalmic routes.
    """

    VALUE_SET_NAME = "Potentially Harmful Gastrointestinal Antispasmodics for Older Adults"
    OID = "2.16.840.1.113883.3.464.1003.1050"
    DEFINITION_VERSION = "20240123"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
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
        "1048307",  # hyoscyamine sulfate 0.12 MG / methenamine 120 MG / methylene blue 10 MG / phenyl salicylate 36 MG / sodium phosphate, monobasic 40.8 MG Oral Capsule
        "1048336",  # hyoscyamine sulfate 0.12 MG / methenamine 81 MG / methylene blue 10.8 MG / phenyl salicylate 32.4 MG / sodium phosphate, monobasic 40.8 MG Oral Tablet
        "1050325",  # hyoscyamine sulfate 0.12 MG / methenamine 81.6 MG / methylene blue 10.8 MG / sodium phosphate, monobasic 40.8 MG Oral Tablet
        "1087365",  # hyoscyamine sulfate 0.12 MG / methenamine 118 MG / methylene blue 10 MG / phenyl salicylate 36 MG / sodium phosphate, monobasic 40.8 MG Oral Capsule
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
        "1190795",  # 1 ML atropine sulfate 1 MG/ML Injection
        "1440869",  # hyoscyamine sulfate 0.12 MG / methenamine 120 MG / methylene blue 10.8 MG / phenyl salicylate 36.2 MG / sodium phosphate, monobasic 40.8 MG Oral Tablet
        "1666781",  # 1 ML atropine sulfate 0.4 MG/ML Injection
        "1807886",  # Biphasic 12 HR hyoscyamine sulfate 0.375 MG Extended Release Oral Tablet
        "226552",  # 72 HR scopolamine 0.0139 MG/HR Transdermal System
        "2637557",  # hyoscyamine sulfate 0.12 MG / methenamine 120 MG / methylene blue 10.8 MG / phenyl salicylate 36.2 MG / sodium phosphate, monobasic 40.8 MG Oral Capsule
        "727415",  # 2.7 ML atropine 0.778 MG/ML / pralidoxime chloride 222 MG/ML Auto-Injector
        "889614",  # chlordiazepoxide hydrochloride 5 MG / clidinium bromide 2.5 MG Oral Capsule
        "991061",  # dicyclomine hydrochloride 10 MG Oral Capsule
        "991065",  # 2 ML dicyclomine hydrochloride 10 MG/ML Injection
        "991082",  # dicyclomine hydrochloride 2 MG/ML Oral Solution
        "991086",  # dicyclomine hydrochloride 20 MG Oral Tablet
        "998726",  # hyoscyamine sulfate 0.0625 MG / phenyltoloxamine citrate 15 MG Oral Capsule
    }

class PotentiallyHarmfulNonbenzodiazepineHypnoticsForOlderAdults(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for potentially harmful Nonbenzodiazepine Hypnotics for older adults as described in the 2023 American Geriatrics Society BEERS criteria.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable nonbenzodiazepine hypnotic medication.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Potentially Harmful Nonbenzodiazepine Hypnotics for Older Adults"
    OID = "2.16.840.1.113883.3.464.1003.196.12.1480"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1232194",  # zolpidem tartrate 1.75 MG Sublingual Tablet
        "1232202",  # zolpidem tartrate 3.5 MG Sublingual Tablet
        "2637353",  # zolpidem tartrate 7.5 MG Oral Capsule
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
    }

class PotentiallyHarmfulPainMedicationsForOlderAdults(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for potentially harmful pain medications for older adults as described in the 2023 American Geriatrics Society BEERS criteria.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable medications. Includes Indomethacin and Ketorolac Tromethamine.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Potentially Harmful Pain Medications for Older Adults"
    OID = "2.16.840.1.113883.3.464.1003.1063"
    DEFINITION_VERSION = "20240123"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1490727",  # indomethacin 20 MG Oral Capsule
        "1491529",  # indomethacin 40 MG Oral Capsule
        "1665459",  # 2 ML ketorolac tromethamine 30 MG/ML Injection
        "1665461",  # 1 ML ketorolac tromethamine 30 MG/ML Injection
        "1797855",  # ketorolac tromethamine 15.8 MG/ACTUAT Metered Dose Nasal Spray
        "197817",  # indomethacin 25 MG Oral Capsule
        "197818",  # indomethacin 50 MG Oral Capsule
        "310991",  # indomethacin 5 MG/ML Oral Suspension
        "310992",  # indomethacin 75 MG Extended Release Oral Capsule
        "834022",  # ketorolac tromethamine 10 MG Oral Tablet
        "860092",  # 1 ML ketorolac tromethamine 15 MG/ML Injection
        "860096",  # ketorolac tromethamine 30 MG/ML Injectable Solution
        "860113",  # 1 ML ketorolac tromethamine 15 MG/ML Prefilled Syringe
        "860114",  # 1 ML ketorolac tromethamine 30 MG/ML Prefilled Syringe
        "860115",  # 2 ML ketorolac tromethamine 30 MG/ML Prefilled Syringe
    }

class PotentiallyHarmfulSkeletalMuscleRelaxantsForOlderAdults(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for potentially harmful Skeletal Muscle Relaxants for older adults as described in the 2023 American Geriatrics Society BEERS criteria.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable medications. Includes Carisoprodol, Metaxalone, Chlorzoxazone , Cyclobenzaprine Hydrochloride, Methocarbamol and Orphenadrine.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Potentially Harmful Skeletal Muscle Relaxants for Older Adults"
    OID = "2.16.840.1.113883.3.464.1003.1062"
    DEFINITION_VERSION = "20240123"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1088934",  # chlorzoxazone 375 MG Oral Tablet
        "1088936",  # chlorzoxazone 750 MG Oral Tablet
        "197446",  # carisoprodol 350 MG Oral Tablet
        "197447",  # aspirin 325 MG / carisoprodol 200 MG Oral Tablet
        "197501",  # chlorzoxazone 250 MG Oral Tablet
        "197502",  # chlorzoxazone 500 MG Oral Tablet
        "197935",  # metaxalone 400 MG Oral Tablet
        "197943",  # methocarbamol 500 MG Oral Tablet
        "197944",  # methocarbamol 750 MG Oral Tablet
        "197945",  # aspirin 325 MG / methocarbamol 400 MG Oral Tablet
        "2611794",  # methocarbamol 1000 MG Oral Tablet
        "2627781",  # metaxalone 640 MG Oral Tablet
        "351254",  # metaxalone 800 MG Oral Tablet
        "730794",  # carisoprodol 250 MG Oral Tablet
        "828299",  # cyclobenzaprine hydrochloride 7.5 MG Oral Tablet
        "828320",  # cyclobenzaprine hydrochloride 5 MG Oral Tablet
        "828348",  # cyclobenzaprine hydrochloride 10 MG Oral Tablet
        "828353",  # 24 HR cyclobenzaprine hydrochloride 30 MG Extended Release Oral Capsule
        "828358",  # 24 HR cyclobenzaprine hydrochloride 15 MG Extended Release Oral Capsule
        "994226",  # aspirin 325 MG / carisoprodol 200 MG / codeine phosphate 16 MG Oral Tablet
        "994521",  # 12 HR orphenadrine citrate 100 MG Extended Release Oral Tablet
        "994528",  # aspirin 385 MG / caffeine 30 MG / orphenadrine citrate 25 MG Oral Tablet
        "994535",  # aspirin 770 MG / caffeine 60 MG / orphenadrine citrate 50 MG Oral Tablet
    }

class PotentiallyHarmfulSulfonylureasForOlderAdults(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for potentially harmful Sulfonylureas for older adults as described in the 2023 American Geriatrics Society BEERS criteria.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent generic, human use and prescribable medications. Includes glimepiride and glyburide.

    **Exclusion Criteria:** Excludes concepts that represent non-prescribable or branded drugs and excludes concepts that represent components or ingredients.
    """

    VALUE_SET_NAME = "Potentially Harmful Sulfonylureas for Older Adults"
    OID = "2.16.840.1.113883.3.464.1003.1059"
    DEFINITION_VERSION = "20240123"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1361493",  # glimepiride 6 MG Oral Tablet
        "1361495",  # glimepiride 8 MG Oral Tablet
        "153842",  # glimepiride 3 MG Oral Tablet
        "197737",  # glyburide 1.25 MG Oral Tablet
        "199245",  # glimepiride 1 MG Oral Tablet
        "199246",  # glimepiride 2 MG Oral Tablet
        "199247",  # glimepiride 4 MG Oral Tablet
        "310534",  # glyburide 2.5 MG Oral Tablet
        "310536",  # glyburide 3 MG Oral Tablet
        "310537",  # glyburide 5 MG Oral Tablet
        "310539",  # glyburide 6 MG Oral Tablet
        "314000",  # glyburide 1.5 MG Oral Tablet
        "647237",  # glimepiride 2 MG / pioglitazone 30 MG Oral Tablet
        "647239",  # glimepiride 4 MG / pioglitazone 30 MG Oral Tablet
        "861743",  # glyburide 1.25 MG / metformin hydrochloride 250 MG Oral Tablet
        "861748",  # glyburide 2.5 MG / metformin hydrochloride 500 MG Oral Tablet
        "861753",  # glyburide 5 MG / metformin hydrochloride 500 MG Oral Tablet
    }

class PharmacologicTherapyForHypertension(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent medications prescribed for the treatment of hypertension.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that describe a medication for treatment of hypertension.

    **Exclusion Criteria:** Excludes concepts that represent branded and non-prescribable drugs.
    """

    VALUE_SET_NAME = "Pharmacologic Therapy for Hypertension"
    OID = "2.16.840.1.113883.3.526.1577"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1000001",  # amlodipine 5 MG / hydrochlorothiazide 25 MG / olmesartan medoxomil 40 MG Oral Tablet
        "1011710",  # aliskiren 150 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "1011713",  # aliskiren 150 MG / hydrochlorothiazide 25 MG Oral Tablet
        "1011736",  # aliskiren 150 MG Oral Tablet
        "1011739",  # aliskiren 300 MG Oral Tablet
        "1011750",  # aliskiren 300 MG / hydrochlorothiazide 12.5 MG Oral Tablet
        "1011753",  # aliskiren 300 MG / hydrochlorothiazide 25 MG Oral Tablet
        "1013930",  # 12 HR clonidine hydrochloride 0.1 MG Extended Release Oral Tablet
        "104232",  # spironolactone 5 MG/ML Oral Suspension
        "1091646",  # azilsartan medoxomil 40 MG Oral Tablet
        "1091652",  # azilsartan medoxomil 80 MG Oral Tablet
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
        "1435624",  # enalapril maleate 1 MG/ML Oral Solution
        "1495058",  # propranolol hydrochloride 4.28 MG/ML Oral Solution
        "153822",  # candesartan cilexetil 4 MG Oral Tablet
        "153823",  # candesartan cilexetil 8 MG Oral Tablet
        "1600716",  # amlodipine 10 MG / perindopril arginine 14 MG Oral Tablet
        "1600724",  # amlodipine 2.5 MG / perindopril arginine 3.5 MG Oral Tablet
        "1600728",  # amlodipine 5 MG / perindopril arginine 7 MG Oral Tablet
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
        "1727569",  # 4 ML bumetanide 0.25 MG/ML Injection
        "1727572",  # 2 ML bumetanide 0.25 MG/ML Injection
        "1729200",  # 1 ML enalaprilat 1.25 MG/ML Injection
        "1729205",  # 2 ML enalaprilat 1.25 MG/ML Injection
        "1790239",  # 50 ML clevidipine 0.5 MG/ML Injection
        "1790245",  # 100 ML clevidipine 0.5 MG/ML Injection
        "1790247",  # 250 ML clevidipine 0.5 MG/ML Injection
        "1791229",  # 5 ML diltiazem hydrochloride 5 MG/ML Injection
        "1791232",  # 10 ML diltiazem hydrochloride 5 MG/ML Injection
        "1791233",  # 25 ML diltiazem hydrochloride 5 MG/ML Injection
        "1791240",  # diltiazem hydrochloride 100 MG Injection
        "1798281",  # nebivolol 5 MG / valsartan 80 MG Oral Tablet
        "1806884",  # lisinopril 1 MG/ML Oral Solution
        "1812011",  # Osmotic 24 HR nifedipine 30 MG Extended Release Oral Tablet
        "1812013",  # Osmotic 24 HR nifedipine 60 MG Extended Release Oral Tablet
        "1812015",  # Osmotic 24 HR nifedipine 90 MG Extended Release Oral Tablet
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
        "1996254",  # valsartan 4 MG/ML Oral Solution
        "199903",  # hydrochlorothiazide 12.5 MG Oral Capsule
        "1999031",  # 24 HR metoprolol succinate 100 MG Extended Release Oral Capsule
        "1999033",  # 24 HR metoprolol succinate 200 MG Extended Release Oral Capsule
        "1999035",  # 24 HR metoprolol succinate 25 MG Extended Release Oral Capsule
        "1999037",  # 24 HR metoprolol succinate 50 MG Extended Release Oral Capsule
        "200031",  # carvedilol 6.25 MG Oral Tablet
        "200032",  # carvedilol 12.5 MG Oral Tablet
        "200033",  # carvedilol 25 MG Oral Tablet
        "200094",  # irbesartan 75 MG Oral Tablet
        "200095",  # irbesartan 150 MG Oral Tablet
        "200096",  # irbesartan 300 MG Oral Tablet
        "200284",  # hydrochlorothiazide 12.5 MG / valsartan 80 MG Oral Tablet
        "200285",  # hydrochlorothiazide 12.5 MG / valsartan 160 MG Oral Tablet
        "2047715",  # amlodipine 2.5 MG / celecoxib 200 MG Oral Tablet
        "2047716",  # amlodipine 5 MG / celecoxib 200 MG Oral Tablet
        "2047717",  # amlodipine 10 MG / celecoxib 200 MG Oral Tablet
        "205304",  # telmisartan 40 MG Oral Tablet
        "205305",  # telmisartan 80 MG Oral Tablet
        "205326",  # lisinopril 30 MG Oral Tablet
        "2184120",  # amlodipine 1 MG/ML Oral Suspension
        "2477889",  # 4 ML labetalol hydrochloride 5 MG/ML Injection
        "2479564",  # 200 ML labetalol hydrochloride 1 MG/ML Injection
        "2479566",  # 100 ML labetalol hydrochloride 1 MG/ML Injection
        "2479567",  # 300 ML labetalol hydrochloride 1 MG/ML Injection
        "251856",  # ramipril 2.5 MG Oral Tablet
        "251857",  # ramipril 5 MG Oral Tablet
        "2586034",  # 125 ML diltiazem hydrochloride 1 MG/ML Injection
        "2586036",  # 250 ML diltiazem hydrochloride 1 MG/ML Injection
        "2589881",  # torsemide 40 MG Oral Tablet
        "2589885",  # torsemide 60 MG Oral Tablet
        "2598343",  # 2 ML labetalol hydrochloride 5 MG/ML Prefilled Syringe
        "2599173",  # amlodipine 1 MG/ML Oral Solution
        "260376",  # terazosin 10 MG Oral Capsule
        "261962",  # ramipril 10 MG Oral Capsule
        "2621022",  # 10 ML furosemide 8 MG/ML Cartridge
        "2683305",  # 50 ML furosemide 10 MG/ML Injection
        "2683306",  # 100 ML furosemide 10 MG/ML Injection
        "2690727",  # 24 HR clonidine hydrochloride 0.1 MG/ML Extended Release Suspension
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
        "351256",  # eplerenone 25 MG Oral Tablet
        "351257",  # eplerenone 50 MG Oral Tablet
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
        "885880",  # 24 HR clonidine 0.17 MG Extended Release Oral Tablet
        "896758",  # labetalol hydrochloride 100 MG Oral Tablet
        "896762",  # labetalol hydrochloride 200 MG Oral Tablet
        "896766",  # labetalol hydrochloride 300 MG Oral Tablet
        "896771",  # labetalol hydrochloride 5 MG/ML Injectable Solution
        "896983",  # labetalol hydrochloride 400 MG Oral Tablet
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
        "905199",  # hydralazine hydrochloride 10 MG Oral Tablet
        "905222",  # hydralazine hydrochloride 100 MG Oral Tablet
        "905225",  # hydralazine hydrochloride 25 MG Oral Tablet
        "905377",  # hydralazine hydrochloride 37.5 MG / isosorbide dinitrate 20 MG Oral Tablet
        "905395",  # hydralazine hydrochloride 50 MG Oral Tablet
        "966571",  # 1 ML hydralazine hydrochloride 20 MG/ML Injection
        "977880",  # amiloride hydrochloride 5 MG Oral Tablet
        "977883",  # amiloride hydrochloride 5 MG / hydrochlorothiazide 50 MG Oral Tablet
        "979464",  # hydrochlorothiazide 12.5 MG / losartan potassium 100 MG Oral Tablet
        "979468",  # hydrochlorothiazide 12.5 MG / losartan potassium 50 MG Oral Tablet
        "979471",  # hydrochlorothiazide 25 MG / losartan potassium 100 MG Oral Tablet
        "979480",  # losartan potassium 100 MG Oral Tablet
        "979485",  # losartan potassium 25 MG Oral Tablet
        "979492",  # losartan potassium 50 MG Oral Tablet
        "998671",  # 168 HR clonidine 0.00417 MG/HR Transdermal System
        "998675",  # 168 HR clonidine 0.00833 MG/HR Transdermal System
        "998679",  # 168 HR clonidine 0.0125 MG/HR Transdermal System
        "998685",  # acebutolol 400 MG Oral Capsule
        "998689",  # acebutolol 200 MG Oral Capsule
        "999967",  # amlodipine 5 MG / hydrochlorothiazide 12.5 MG / olmesartan medoxomil 20 MG Oral Tablet
        "999986",  # amlodipine 10 MG / hydrochlorothiazide 12.5 MG / olmesartan medoxomil 40 MG Oral Tablet
        "999991",  # amlodipine 10 MG / hydrochlorothiazide 25 MG / olmesartan medoxomil 40 MG Oral Tablet
        "999996",  # amlodipine 5 MG / hydrochlorothiazide 12.5 MG / olmesartan medoxomil 40 MG Oral Tablet
    }

class AdolescentDepressionMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent medications used to treat depression in the child and adolescent population.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts for medications used for treatment and management of depression in children and adolescents.

    **Exclusion Criteria:** Excludes concepts that represent medications that are not recommended for children and adolescents and are solely used in the adult population.
    """

    VALUE_SET_NAME = "Adolescent Depression Medications"
    OID = "2.16.840.1.113883.3.526.3.1567"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1190110",  # fluoxetine 60 MG Oral Tablet
        "200371",  # citalopram 20 MG Oral Tablet
        "248642",  # fluoxetine 20 MG Oral Tablet
        "251201",  # sertraline 200 MG Oral Capsule
        "2591786",  # citalopram 30 MG Oral Capsule
        "2605950",  # 24 HR venlafaxine 112.5 MG Extended Release Oral Tablet
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
        "403969",  # fluoxetine 25 MG / olanzapine 6 MG Oral Capsule
        "403970",  # fluoxetine 25 MG / olanzapine 12 MG Oral Capsule
        "403971",  # fluoxetine 50 MG / olanzapine 12 MG Oral Capsule
        "403972",  # fluoxetine 50 MG / olanzapine 6 MG Oral Capsule
        "410584",  # sertraline 150 MG Oral Capsule
        "476809",  # mirtazapine 7.5 MG Oral Tablet
        "596926",  # duloxetine 20 MG Delayed Release Oral Capsule
        "596930",  # duloxetine 30 MG Delayed Release Oral Capsule
        "596934",  # duloxetine 60 MG Delayed Release Oral Capsule
        "616402",  # duloxetine 40 MG Delayed Release Oral Capsule
        "721787",  # fluoxetine 25 MG / olanzapine 3 MG Oral Capsule
        "808744",  # 24 HR venlafaxine 150 MG Extended Release Oral Tablet
        "808748",  # 24 HR venlafaxine 225 MG Extended Release Oral Tablet
        "808751",  # 24 HR venlafaxine 37.5 MG Extended Release Oral Tablet
        "808753",  # 24 HR venlafaxine 75 MG Extended Release Oral Tablet
        "861064",  # sertraline 20 MG/ML Oral Solution
        "903873",  # 24 HR fluvoxamine maleate 100 MG Extended Release Oral Capsule
        "903879",  # 24 HR fluvoxamine maleate 150 MG Extended Release Oral Capsule
        "903884",  # fluvoxamine maleate 100 MG Oral Tablet
        "903887",  # fluvoxamine maleate 25 MG Oral Tablet
        "903891",  # fluvoxamine maleate 50 MG Oral Tablet
    }

class AdultDepressionMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent medications used to treat depression in the adult population.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts for medications used for treatment and management of depression in adults.

    **Exclusion Criteria:** Excludes concepts that represent medications that are not recommended for children and adolescents and are solely used in the adult population.
    """

    VALUE_SET_NAME = "Adult Depression Medications"
    OID = "2.16.840.1.113883.3.526.3.1566"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1000048",  # doxepin 10 MG Oral Capsule
        "1000054",  # doxepin 10 MG/ML Oral Solution
        "1000058",  # doxepin 100 MG Oral Capsule
        "1000064",  # doxepin 150 MG Oral Capsule
        "1000070",  # doxepin 25 MG Oral Capsule
        "1000076",  # doxepin 50 MG Oral Capsule
        "1000097",  # doxepin 75 MG Oral Capsule
        "103968",  # lamotrigine 100 MG Disintegrating Oral Tablet
        "1086772",  # vilazodone hydrochloride 10 MG Oral Tablet
        "1086778",  # vilazodone hydrochloride 20 MG Oral Tablet
        "1086784",  # vilazodone hydrochloride 40 MG Oral Tablet
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
        "1298861",  # maprotiline hydrochloride 50 MG Oral Tablet
        "1298870",  # maprotiline hydrochloride 75 MG Oral Tablet
        "1424836",  # 5-hydroxytryptophan 200 MG Oral Capsule
        "1430122",  # paroxetine mesylate 7.5 MG Oral Capsule
        "1607617",  # 24 HR desvenlafaxine succinate 25 MG Extended Release Oral Tablet
        "1653469",  # {7 (vilazodone hydrochloride 10 MG Oral Tablet) / 23 (vilazodone hydrochloride 20 MG Oral Tablet) } Pack
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
        "1874553",  # 24 HR desvenlafaxine succinate 100 MG Extended Release Oral Tablet
        "1874559",  # 24 HR desvenlafaxine succinate 50 MG Extended Release Oral Tablet
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
        "199322",  # lamotrigine 50 MG Oral Tablet
        "200371",  # citalopram 20 MG Oral Tablet
        "2200168",  # Sprinkle duloxetine 20 MG Delayed Release Oral Capsule
        "2200175",  # Sprinkle duloxetine 30 MG Delayed Release Oral Capsule
        "2200178",  # Sprinkle duloxetine 40 MG Delayed Release Oral Capsule
        "2200181",  # Sprinkle duloxetine 60 MG Delayed Release Oral Capsule
        "248642",  # fluoxetine 20 MG Oral Tablet
        "249329",  # lamotrigine 250 MG Oral Tablet
        "251201",  # sertraline 200 MG Oral Capsule
        "252478",  # lamotrigine 50 MG Disintegrating Oral Tablet
        "252479",  # lamotrigine 200 MG Disintegrating Oral Tablet
        "2591786",  # citalopram 30 MG Oral Capsule
        "2605720",  # 5-hydroxytryptophan 100 MG Extended Release Oral Tablet
        "2605950",  # 24 HR venlafaxine 112.5 MG Extended Release Oral Tablet
        "2611260",  # bupropion hydrochloride 105 MG / dextromethorphan hydrobromide 45 MG Extended Release Oral Tablet
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
        "311264",  # lamotrigine 25 MG Tablet for Oral Suspension
        "311265",  # lamotrigine 5 MG Tablet for Oral Suspension
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
        "349010",  # lamotrigine 2 MG Tablet for Oral Suspension
        "349332",  # escitalopram 10 MG Oral Tablet
        "351249",  # escitalopram 5 MG Oral Tablet
        "351250",  # escitalopram 20 MG Oral Tablet
        "351285",  # escitalopram 1 MG/ML Oral Solution
        "403969",  # fluoxetine 25 MG / olanzapine 6 MG Oral Capsule
        "403970",  # fluoxetine 25 MG / olanzapine 12 MG Oral Capsule
        "403971",  # fluoxetine 50 MG / olanzapine 12 MG Oral Capsule
        "403972",  # fluoxetine 50 MG / olanzapine 6 MG Oral Capsule
        "410503",  # 5-hydroxytryptophan 100 MG Oral Capsule
        "410584",  # sertraline 150 MG Oral Capsule
        "476809",  # mirtazapine 7.5 MG Oral Tablet
        "485514",  # 5-hydroxytryptophan 50 MG Oral Capsule
        "596926",  # duloxetine 20 MG Delayed Release Oral Capsule
        "596930",  # duloxetine 30 MG Delayed Release Oral Capsule
        "596934",  # duloxetine 60 MG Delayed Release Oral Capsule
        "616402",  # duloxetine 40 MG Delayed Release Oral Capsule
        "721787",  # fluoxetine 25 MG / olanzapine 3 MG Oral Capsule
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
    }

class HighIntensityStatinTherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications that are high intensity statins as defined by the 2013 American College of Cardiology (ACC) and the American Heart Association (AHA) guideline.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for high intensity statin therapy as defined by the 2013 American College of Cardiology (ACC) and the American Heart Association (AHA) guideline.

    **Exclusion Criteria:** Excludes concepts that represent any other intensity of statin therapy.
    """

    VALUE_SET_NAME = "High Intensity Statin Therapy"
    OID = "2.16.840.1.113883.3.526.3.1572"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1422096",  # atorvastatin 40 MG / ezetimibe 10 MG Oral Tablet
        "1422099",  # atorvastatin 80 MG / ezetimibe 10 MG Oral Tablet
        "200345",  # simvastatin 80 MG Oral Tablet
        "2167565",  # rosuvastatin 20 MG Oral Capsule
        "2167569",  # rosuvastatin 40 MG Oral Capsule
        "2535745",  # ezetimibe 10 MG / rosuvastatin 20 MG Oral Tablet
        "2535749",  # ezetimibe 10 MG / rosuvastatin 40 MG Oral Tablet
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
    }

class LowIntensityStatinTherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of low intensity statin medications as defined by the 2013 American College of Cardiology (ACC) and the American Heart Association (AHA) guideline.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for low intensity statin therapy as defined by the 2013 American College of Cardiology (ACC) and the American Heart Association (AHA) guideline.

    **Exclusion Criteria:** Excludes concepts that represent any other intensity of statin therapy.
    """

    VALUE_SET_NAME = "Low Intensity Statin Therapy"
    OID = "2.16.840.1.113883.3.526.3.1574"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1790679",  # simvastatin 4 MG/ML Oral Suspension
        "197903",  # lovastatin 10 MG Oral Tablet
        "197904",  # lovastatin 20 MG Oral Tablet
        "310404",  # fluvastatin 20 MG Oral Capsule
        "312962",  # simvastatin 5 MG Oral Tablet
        "314231",  # simvastatin 10 MG Oral Tablet
        "433849",  # 24 HR lovastatin 20 MG Extended Release Oral Tablet
        "476345",  # ezetimibe 10 MG / simvastatin 10 MG Oral Tablet
        "904458",  # pravastatin sodium 10 MG Oral Tablet
        "904467",  # pravastatin sodium 20 MG Oral Tablet
    }

class ModerateIntensityStatinTherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent moderate intensity statin medications as defined by the 2013 American College of Cardiology (ACC) and the American Heart Association (AHA) guideline.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for moderate intensity statin therapy as defined by the 2013 American College of Cardiology (ACC) and the American Heart Association (AHA) guideline.

    **Exclusion Criteria:** Excludes concepts that represent any other intensity of statin therapy.
    """

    VALUE_SET_NAME = "Moderate Intensity Statin Therapy"
    OID = "2.16.840.1.113883.3.526.3.1575"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1422086",  # atorvastatin 10 MG / ezetimibe 10 MG Oral Tablet
        "1422093",  # atorvastatin 20 MG / ezetimibe 10 MG Oral Tablet
        "1944264",  # simvastatin 8 MG/ML Oral Suspension
        "197905",  # lovastatin 40 MG Oral Tablet
        "198211",  # simvastatin 40 MG Oral Tablet
        "2001254",  # pitavastatin magnesium 1 MG Oral Tablet
        "2001262",  # pitavastatin magnesium 2 MG Oral Tablet
        "2001266",  # pitavastatin magnesium 4 MG Oral Tablet
        "2167557",  # rosuvastatin 10 MG Oral Capsule
        "2167573",  # rosuvastatin 5 MG Oral Capsule
        "2535747",  # ezetimibe 10 MG / rosuvastatin 5 MG Oral Tablet
        "2535750",  # ezetimibe 10 MG / rosuvastatin 10 MG Oral Tablet
        "2689112",  # pitavastatin sodium 1 MG Oral Tablet
        "2689121",  # pitavastatin sodium 2 MG Oral Tablet
        "2689125",  # pitavastatin sodium 4 MG Oral Tablet
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
        "861643",  # pitavastatin calcium 1 MG Oral Tablet
        "861648",  # pitavastatin calcium 2 MG Oral Tablet
        "861652",  # pitavastatin calcium 4 MG Oral Tablet
        "904475",  # pravastatin sodium 40 MG Oral Tablet
        "904481",  # pravastatin sodium 80 MG Oral Tablet
    }

class MedicationsForOpioidUseDisorderMoud(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to group concepts that represent medications for opioid use disorders.

    **Data Element Scope:** This value set may use a model element related to medication.

    **Inclusion Criteria:** Includes concepts that represent medications used for opioid use disorders.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Medications for Opioid Use Disorder (MOUD)"
    OID = "2.16.840.1.113762.1.4.1046.269"
    DEFINITION_VERSION = "20240215"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1010600",  # buprenorphine 2 MG / naloxone 0.5 MG Sublingual Film
        "1010604",  # buprenorphine 8 MG / naloxone 2 MG Sublingual Film
        "1307056",  # buprenorphine 4 MG / naloxone 1 MG Sublingual Film
        "1307061",  # buprenorphine 12 MG / naloxone 3 MG Sublingual Film
        "1431076",  # buprenorphine 1.4 MG / naloxone 0.36 MG Sublingual Tablet
        "1431102",  # buprenorphine 5.7 MG / naloxone 1.4 MG Sublingual Tablet
        "1432969",  # 168 HR buprenorphine 0.015 MG/HR Transdermal System
        "1542390",  # buprenorphine 2.1 MG / naloxone 0.3 MG Buccal Film
        "1542997",  # 168 HR buprenorphine 0.0075 MG/HR Transdermal System
        "1544851",  # buprenorphine 4.2 MG / naloxone 0.7 MG Buccal Film
        "1544854",  # buprenorphine 6.3 MG / naloxone 1 MG Buccal Film
        "1597568",  # buprenorphine 11.4 MG / naloxone 2.9 MG Sublingual Tablet
        "1597573",  # buprenorphine 8.6 MG / naloxone 2.1 MG Sublingual Tablet
        "1666338",  # buprenorphine 2.9 MG / naloxone 0.71 MG Sublingual Tablet
        "238129",  # 1 ML buprenorphine 0.3 MG/ML Injection
        "351264",  # buprenorphine 2 MG Sublingual Tablet
        "351265",  # buprenorphine 8 MG Sublingual Tablet
        "351266",  # buprenorphine 2 MG / naloxone 0.5 MG Sublingual Tablet
        "351267",  # buprenorphine 8 MG / naloxone 2 MG Sublingual Tablet
        "637213",  # naltrexone 380 MG Injection
        "864706",  # methadone hydrochloride 10 MG Oral Tablet
        "864714",  # methadone hydrochloride 10 MG/ML Injectable Solution
        "864718",  # methadone hydrochloride 5 MG Oral Tablet
        "864761",  # methadone hydrochloride 1 MG/ML Oral Solution
        "864769",  # methadone hydrochloride 2 MG/ML Oral Solution
        "864978",  # methadone hydrochloride 40 MG Tablet for Oral Suspension
        "904870",  # 168 HR buprenorphine 0.01 MG/HR Transdermal System
        "904876",  # 168 HR buprenorphine 0.02 MG/HR Transdermal System
        "904880",  # 168 HR buprenorphine 0.005 MG/HR Transdermal System
        "991147",  # methadone hydrochloride 10 MG/ML Oral Solution
    }

class ScheduleIiIiiAndIvOpioidMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to group Schedules II, III and IV opioid medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that identify medications of Schedules II, III and IV opioid medications.

    **Exclusion Criteria:** Excludes concepts that represent schedule I and V, unscheduled, nonprescribable, non-human, and inactive opioid medications.
    """

    VALUE_SET_NAME = "Schedule II, III and IV Opioid Medications"
    OID = "2.16.840.1.113762.1.4.1046.241"
    DEFINITION_VERSION = "20240215"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1014599",  # acetaminophen 300 MG / oxycodone hydrochloride 10 MG Oral Tablet
        "1014615",  # acetaminophen 300 MG / oxycodone hydrochloride 5 MG Oral Tablet
        "1014632",  # acetaminophen 300 MG / oxycodone hydrochloride 7.5 MG Oral Tablet
        "1037259",  # acetaminophen 300 MG / oxycodone hydrochloride 2.5 MG Oral Tablet
        "1042693",  # chlorpheniramine maleate 0.4 MG/ML / codeine phosphate 2 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "1044427",  # acetaminophen 20 MG/ML / hydrocodone bitartrate 0.667 MG/ML Oral Solution
        "1049214",  # acetaminophen 325 MG / oxycodone hydrochloride 10 MG Oral Tablet
        "1049221",  # acetaminophen 325 MG / oxycodone hydrochloride 5 MG Oral Tablet
        "1049225",  # acetaminophen 325 MG / oxycodone hydrochloride 7.5 MG Oral Tablet
        "1049251",  # acetaminophen 400 MG / oxycodone hydrochloride 10 MG Oral Tablet
        "1049260",  # acetaminophen 400 MG / oxycodone hydrochloride 5 MG Oral Tablet
        "1049502",  # 12 HR oxycodone hydrochloride 10 MG Extended Release Oral Tablet
        "1049543",  # 12 HR oxycodone hydrochloride 15 MG Extended Release Oral Tablet
        "1049574",  # 12 HR oxycodone hydrochloride 30 MG Extended Release Oral Tablet
        "1049580",  # acetaminophen 65 MG/ML / oxycodone hydrochloride 1 MG/ML Oral Solution
        "1049589",  # ibuprofen 400 MG / oxycodone hydrochloride 5 MG Oral Tablet
        "1049593",  # 12 HR oxycodone hydrochloride 60 MG Extended Release Oral Tablet
        "1049604",  # oxycodone hydrochloride 1 MG/ML Oral Solution
        "1049611",  # oxycodone hydrochloride 15 MG Oral Tablet
        "1049615",  # oxycodone hydrochloride 20 MG/ML Oral Solution
        "1049618",  # oxycodone hydrochloride 30 MG Oral Tablet
        "1049621",  # oxycodone hydrochloride 5 MG Oral Tablet
        "1049635",  # acetaminophen 325 MG / oxycodone hydrochloride 2.5 MG Oral Tablet
        "1049683",  # oxycodone hydrochloride 10 MG Oral Tablet
        "1049686",  # oxycodone hydrochloride 20 MG Oral Tablet
        "1049696",  # oxycodone hydrochloride 5 MG Oral Capsule
        "1053647",  # fentanyl 0.1 MG Sublingual Tablet
        "1053652",  # fentanyl 0.2 MG Sublingual Tablet
        "1053655",  # fentanyl 0.3 MG Sublingual Tablet
        "1053658",  # fentanyl 0.4 MG Sublingual Tablet
        "1053661",  # fentanyl 0.6 MG Sublingual Tablet
        "1053664",  # fentanyl 0.8 MG Sublingual Tablet
        "1087459",  # 12 HR chlorpheniramine polistirex 1.6 MG/ML / hydrocodone polistirex 2 MG/ML Extended Release Suspension
        "1089055",  # codeine phosphate 10 MG / guaifenesin 400 MG / pseudoephedrine hydrochloride 20 MG Oral Tablet
        "1089058",  # codeine phosphate 10 MG / guaifenesin 400 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet
        "1112220",  # chlorpheniramine maleate 0.8 MG/ML / hydrocodone bitartrate 1 MG/ML / pseudoephedrine hydrochloride 12 MG/ML Oral Solution
        "1113314",  # oxycodone hydrochloride 7.5 MG Oral Tablet
        "1114026",  # codeine phosphate 1.6 MG/ML / guaifenesin 40 MG/ML Oral Solution
        "1115573",  # fentanyl 0.1 MG/ACTUAT Metered Dose Nasal Spray
        "1115577",  # fentanyl 0.4 MG/ACTUAT Metered Dose Nasal Spray
        "1148478",  # 24 HR tramadol hydrochloride 100 MG Extended Release Oral Capsule
        "1148485",  # 24 HR tramadol hydrochloride 200 MG Extended Release Oral Capsule
        "1148489",  # 24 HR tramadol hydrochloride 300 MG Extended Release Oral Capsule
        "1148797",  # 12 HR tapentadol 100 MG Extended Release Oral Tablet
        "1148800",  # 12 HR tapentadol 150 MG Extended Release Oral Tablet
        "1148803",  # 12 HR tapentadol 200 MG Extended Release Oral Tablet
        "1148807",  # 12 HR tapentadol 250 MG Extended Release Oral Tablet
        "1148809",  # 12 HR tapentadol 50 MG Extended Release Oral Tablet
        "1190580",  # codeine phosphate 1.2 MG/ML / dexbrompheniramine maleate 0.133 MG/ML / pseudoephedrine hydrochloride 4 MG/ML Oral Solution
        "1235862",  # chlorcyclizine hydrochloride 2.5 MG/ML / codeine phosphate 1.8 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1237050",  # fentanyl 0.1 MG/ACTUAT Mucosal Spray
        "1237057",  # fentanyl 0.2 MG/ACTUAT Mucosal Spray
        "1237060",  # fentanyl 0.4 MG/ACTUAT Mucosal Spray
        "1237064",  # fentanyl 0.6 MG/ACTUAT Mucosal Spray
        "1237068",  # fentanyl 0.8 MG/ACTUAT Mucosal Spray
        "1248115",  # 24 HR tramadol hydrochloride 150 MG Extended Release Oral Capsule
        "1303736",  # morphine sulfate 40 MG Extended Release Oral Capsule
        "1306898",  # 24 HR hydromorphone hydrochloride 32 MG Extended Release Oral Tablet
        "1356797",  # brompheniramine maleate 4 MG / codeine phosphate 10 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1356800",  # brompheniramine maleate 4 MG / codeine phosphate 10 MG Oral Tablet
        "1356804",  # brompheniramine maleate 4 MG / codeine phosphate 20 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1356807",  # brompheniramine maleate 4 MG / codeine phosphate 20 MG Oral Tablet
        "1366873",  # hydrocodone bitartrate 5 MG / pseudoephedrine hydrochloride 60 MG Oral Tablet
        "1431286",  # acetaminophen 300 MG / butalbital 50 MG / caffeine 40 MG / codeine phosphate 30 MG Oral Capsule
        "1432969",  # 168 HR buprenorphine 0.015 MG/HR Transdermal System
        "1433251",  # 0.5 ML hydromorphone hydrochloride 1 MG/ML Prefilled Syringe
        "1440003",  # codeine phosphate 1.8 MG/ML / dexchlorpheniramine maleate 0.2 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "1442790",  # 1 ML morphine sulfate 5 MG/ML Prefilled Syringe
        "1541630",  # brompheniramine maleate 0.8 MG/ML / codeine phosphate 2 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "1542997",  # 168 HR buprenorphine 0.0075 MG/HR Transdermal System
        "1595730",  # Abuse-Deterrent 24 HR hydrocodone bitartrate 20 MG Extended Release Oral Tablet
        "1595740",  # Abuse-Deterrent 24 HR hydrocodone bitartrate 30 MG Extended Release Oral Tablet
        "1595746",  # Abuse-Deterrent 24 HR hydrocodone bitartrate 40 MG Extended Release Oral Tablet
        "1595752",  # Abuse-Deterrent 24 HR hydrocodone bitartrate 60 MG Extended Release Oral Tablet
        "1595758",  # Abuse-Deterrent 24 HR hydrocodone bitartrate 80 MG Extended Release Oral Tablet
        "1595764",  # Abuse-Deterrent 24 HR hydrocodone bitartrate 100 MG Extended Release Oral Tablet
        "1595770",  # Abuse-Deterrent 24 HR hydrocodone bitartrate 120 MG Extended Release Oral Tablet
        "1596108",  # acetaminophen 320.5 MG / caffeine 30 MG / dihydrocodeine bitartrate 16 MG Oral Capsule
        "1603495",  # 72 HR fentanyl 0.0375 MG/HR Transdermal System
        "1603498",  # 72 HR fentanyl 0.0625 MG/HR Transdermal System
        "1603501",  # 72 HR fentanyl 0.0875 MG/HR Transdermal System
        "1651558",  # guaifenesin 40 MG/ML / hydrocodone bitartrate 0.5 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1652087",  # 12 HR chlorpheniramine polistirex 0.8 MG/ML / codeine polistirex 4 MG/ML Extended Release Suspension
        "1655032",  # 1 ML buprenorphine 0.3 MG/ML Cartridge
        "1661319",  # codeine phosphate 2 MG/ML / phenylephrine hydrochloride 2 MG/ML / triprolidine hydrochloride 0.5 MG/ML Oral Solution
        "1664543",  # 12 HR chlorpheniramine maleate 8 MG / codeine phosphate 54.3 MG Extended Release Oral Tablet
        "1665685",  # 1 ML meperidine hydrochloride 100 MG/ML Injection
        "1665697",  # 1 ML meperidine hydrochloride 50 MG/ML Injection
        "1665699",  # 0.5 ML meperidine hydrochloride 50 MG/ML Injection
        "1665701",  # 2 ML meperidine hydrochloride 50 MG/ML Injection
        "1666831",  # 80 ACTUAT fentanyl 0.04 MG/ACTUAT Transdermal System
        "1716057",  # buprenorphine 0.15 MG Buccal Film
        "1716065",  # buprenorphine 0.3 MG Buccal Film
        "1716069",  # buprenorphine 0.45 MG Buccal Film
        "1716073",  # buprenorphine 0.6 MG Buccal Film
        "1716077",  # buprenorphine 0.075 MG Buccal Film
        "1716081",  # buprenorphine 0.75 MG Buccal Film
        "1716086",  # buprenorphine 0.9 MG Buccal Film
        "1723206",  # 2 ML alfentanil 0.5 MG/ML Injection
        "1723208",  # 10 ML alfentanil 0.5 MG/ML Injection
        "1723209",  # 20 ML alfentanil 0.5 MG/ML Injection
        "1723210",  # 5 ML alfentanil 0.5 MG/ML Injection
        "1724276",  # 1 ML hydromorphone hydrochloride 2 MG/ML Injection
        "1724338",  # 1 ML hydromorphone hydrochloride 10 MG/ML Injection
        "1724340",  # 5 ML hydromorphone hydrochloride 10 MG/ML Injection
        "1724341",  # 50 ML hydromorphone hydrochloride 10 MG/ML Injection
        "1724383",  # 1 ML hydromorphone hydrochloride 1 MG/ML Cartridge
        "1724644",  # 1 ML hydromorphone hydrochloride 2 MG/ML Cartridge
        "1728351",  # 1 ML butorphanol tartrate 2 MG/ML Injection
        "1728355",  # 2 ML butorphanol tartrate 2 MG/ML Injection
        "1728783",  # 10 ML morphine sulfate 0.5 MG/ML Injection
        "1728791",  # 2 ML morphine sulfate 0.5 MG/ML Injection
        "1728800",  # 10 ML morphine sulfate 1 MG/ML Injection
        "1728999",  # 30 ML morphine sulfate 1 MG/ML Injection
        "1729197",  # 1 ML morphine sulfate 2 MG/ML Cartridge
        "1729320",  # fentanyl 0.3 MG/ACTUAT Metered Dose Nasal Spray
        "1729578",  # remifentanil 1 MG Injection
        "1729584",  # remifentanil 2 MG Injection
        "1729710",  # remifentanil 5 MG Injection
        "1731520",  # 4 ML morphine sulfate 25 MG/ML Injection
        "1731522",  # 20 ML morphine sulfate 25 MG/ML Injection
        "1731537",  # 20 ML morphine sulfate 50 MG/ML Injection
        "1731545",  # 50 ML morphine sulfate 50 MG/ML Injection
        "1731990",  # 1.5 ML morphine sulfate liposomal 10 MG/ML Injection
        "1731993",  # 1 ML morphine sulfate 10 MG/ML Injection
        "1731995",  # 1 ML morphine sulfate 10 MG/ML Cartridge
        "1731998",  # 20 ML morphine sulfate 10 MG/ML Injection
        "1732003",  # 1 ML morphine sulfate 8 MG/ML Cartridge
        "1732006",  # 1 ML morphine sulfate 4 MG/ML Injection
        "1732011",  # 1 ML morphine sulfate 8 MG/ML Injection
        "1732014",  # 1 ML morphine sulfate 4 MG/ML Cartridge
        "1732136",  # 1 ML morphine sulfate 5 MG/ML Injection
        "1733080",  # 1 ML morphine sulfate 15 MG/ML Cartridge
        "1735003",  # 2 ML fentanyl 0.05 MG/ML Injection
        "1735006",  # 10 ML fentanyl 0.05 MG/ML Injection
        "1735007",  # 5 ML fentanyl 0.05 MG/ML Injection
        "1735008",  # 20 ML fentanyl 0.05 MG/ML Injection
        "1735013",  # 50 ML fentanyl 0.05 MG/ML Injection
        "1740007",  # {2 (fentanyl 0.6 MG/ACTUAT Mucosal Spray) } Pack
        "1740009",  # {2 (fentanyl 0.8 MG/ACTUAT Mucosal Spray) } Pack
        "1790527",  # Abuse-Deterrent 12 HR oxycodone 9 MG Extended Release Oral Capsule
        "1791558",  # Abuse-Deterrent 12 HR oxycodone 13.5 MG Extended Release Oral Capsule
        "1791567",  # Abuse-Deterrent 12 HR oxycodone 18 MG Extended Release Oral Capsule
        "1791574",  # Abuse-Deterrent 12 HR oxycodone 27 MG Extended Release Oral Capsule
        "1791580",  # Abuse-Deterrent 12 HR oxycodone 36 MG Extended Release Oral Capsule
        "1792707",  # codeine phosphate 2 MG/ML / guaifenesin 40 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1797650",  # buprenorphine 74.2 MG Drug Implant
        "1809097",  # 1 ML sufentanil 0.05 MG/ML Injection
        "1809102",  # 2 ML sufentanil 0.05 MG/ML Injection
        "1809104",  # 5 ML sufentanil 0.05 MG/ML Injection
        "1812164",  # acetaminophen 325 MG / caffeine 30 MG / dihydrocodeine bitartrate 16 MG Oral Tablet
        "1860127",  # Abuse-Deterrent 12 HR oxycodone hydrochloride 60 MG Extended Release Oral Tablet
        "1860129",  # Abuse-Deterrent 12 HR oxycodone hydrochloride 20 MG Extended Release Oral Tablet
        "1860137",  # Abuse-Deterrent 12 HR oxycodone hydrochloride 40 MG Extended Release Oral Tablet
        "1860148",  # Abuse-Deterrent 12 HR oxycodone hydrochloride 80 MG Extended Release Oral Tablet
        "1860151",  # Abuse-Deterrent 12 HR oxycodone hydrochloride 30 MG Extended Release Oral Tablet
        "1860154",  # Abuse-Deterrent 12 HR oxycodone hydrochloride 15 MG Extended Release Oral Tablet
        "1860157",  # Abuse-Deterrent 12 HR oxycodone hydrochloride 10 MG Extended Release Oral Tablet
        "1860491",  # 12 HR hydrocodone bitartrate 10 MG Extended Release Oral Capsule
        "1860493",  # 12 HR hydrocodone bitartrate 15 MG Extended Release Oral Capsule
        "1860495",  # 12 HR hydrocodone bitartrate 20 MG Extended Release Oral Capsule
        "1860497",  # 12 HR hydrocodone bitartrate 30 MG Extended Release Oral Capsule
        "1860499",  # 12 HR hydrocodone bitartrate 40 MG Extended Release Oral Capsule
        "1860501",  # 12 HR hydrocodone bitartrate 50 MG Extended Release Oral Capsule
        "1866543",  # 1 ML nalbuphine hydrochloride 10 MG/ML Injection
        "1866551",  # 1 ML nalbuphine hydrochloride 20 MG/ML Injection
        "1871434",  # Abuse-Deterrent 12 HR morphine sulfate 15 MG Extended Release Oral Tablet
        "1871441",  # Abuse-Deterrent 12 HR morphine sulfate 30 MG Extended Release Oral Tablet
        "1871444",  # Abuse-Deterrent 12 HR morphine sulfate 60 MG Extended Release Oral Tablet
        "1872271",  # 1 ML hydromorphone hydrochloride 4 MG/ML Prefilled Syringe
        "1944529",  # Abuse-Deterrent oxycodone hydrochloride 15 MG Oral Tablet
        "1944538",  # Abuse-Deterrent oxycodone hydrochloride 30 MG Oral Tablet
        "1944541",  # Abuse-Deterrent oxycodone hydrochloride 5 MG Oral Tablet
        "1946525",  # Matrix Delivery 24 HR tramadol hydrochloride 300 MG Extended Release Oral Tablet
        "1946527",  # Matrix Delivery 24 HR tramadol hydrochloride 200 MG Extended Release Oral Tablet
        "1946529",  # Matrix Delivery 24 HR tramadol hydrochloride 100 MG Extended Release Oral Tablet
        "197696",  # 72 HR fentanyl 0.075 MG/HR Transdermal System
        "197873",  # levorphanol tartrate 2 MG Oral Tablet
        "1996184",  # 0.5 ML buprenorphine 200 MG/ML Prefilled Syringe
        "1996192",  # 1.5 ML buprenorphine 200 MG/ML Prefilled Syringe
        "2003714",  # 1 ML morphine sulfate 2 MG/ML Injection
        "2056893",  # chlorpheniramine maleate 0.8 MG/ML / codeine phosphate 2 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "2058845",  # levorphanol tartrate 3 MG Oral Tablet
        "2103192",  # sufentanil 0.03 MG Sublingual Tablet
        "2105822",  # acetaminophen 60 MG/ML / oxycodone hydrochloride 2 MG/ML Oral Solution
        "2168270",  # 1 ML fentanyl 0.05 MG/ML Injection
        "2179635",  # tramadol hydrochloride 100 MG Oral Tablet
        "2277368",  # 1 ML hydromorphone hydrochloride 0.2 MG/ML Prefilled Syringe
        "238129",  # 1 ML buprenorphine 0.3 MG/ML Injection
        "238133",  # pentazocine 30 MG/ML Injectable Solution
        "2395808",  # tramadol hydrochloride 5 MG/ML Oral Solution
        "245134",  # 72 HR fentanyl 0.025 MG/HR Transdermal System
        "245135",  # 72 HR fentanyl 0.05 MG/HR Transdermal System
        "245136",  # 72 HR fentanyl 0.1 MG/HR Transdermal System
        "2474267",  # 2 ML fentanyl 0.05 MG/ML Prefilled Syringe
        "2474269",  # 1 ML fentanyl 0.05 MG/ML Prefilled Syringe
        "2539186",  # 1 ML meperidine hydrochloride 50 MG/ML Prefilled Syringe
        "2539191",  # 1 ML meperidine hydrochloride 25 MG/ML Prefilled Syringe
        "2629337",  # 0.5 ML fentanyl 0.05 MG/ML Prefilled Syringe
        "2635081",  # 100 ML fentanyl 0.05 MG/ML Injection
        "2670390",  # tramadol hydrochloride 25 MG Oral Tablet
        "310293",  # fentanyl 1.2 MG Oral Lozenge
        "310294",  # fentanyl 1.6 MG Oral Lozenge
        "310295",  # fentanyl 0.2 MG Oral Lozenge
        "310297",  # fentanyl 0.4 MG Oral Lozenge
        "312104",  # belladonna alkaloids 16.2 MG / opium 30 MG Rectal Suppository
        "312107",  # belladonna alkaloids 16.2 MG / opium 60 MG Rectal Suppository
        "313992",  # fentanyl 0.6 MG Oral Lozenge
        "313993",  # fentanyl 0.8 MG Oral Lozenge
        "351264",  # buprenorphine 2 MG Sublingual Tablet
        "351265",  # buprenorphine 8 MG Sublingual Tablet
        "577057",  # 72 HR fentanyl 0.012 MG/HR Transdermal System
        "637540",  # aspirin 325 MG / oxycodone hydrochloride 4.5 MG / oxycodone terephthalate 0.38 MG Oral Tablet
        "668363",  # fentanyl 0.1 MG Buccal Tablet
        "668364",  # fentanyl 0.2 MG Buccal Tablet
        "668365",  # fentanyl 0.4 MG Buccal Tablet
        "668366",  # fentanyl 0.6 MG Buccal Tablet
        "668367",  # fentanyl 0.8 MG Buccal Tablet
        "727759",  # 2 ML fentanyl 0.05 MG/ML Cartridge
        "825409",  # tapentadol 100 MG Oral Tablet
        "825411",  # tapentadol 50 MG Oral Tablet
        "825413",  # tapentadol 75 MG Oral Tablet
        "830196",  # opium tincture 100 MG/ML Oral Solution
        "833709",  # 24 HR tramadol hydrochloride 100 MG Extended Release Oral Tablet
        "833711",  # 24 HR tramadol hydrochloride 200 MG Extended Release Oral Tablet
        "833713",  # 24 HR tramadol hydrochloride 300 MG Extended Release Oral Tablet
        "835603",  # tramadol hydrochloride 50 MG Oral Tablet
        "836395",  # acetaminophen 325 MG / tramadol hydrochloride 37.5 MG Oral Tablet
        "848768",  # aspirin 325 MG / oxycodone hydrochloride 4.84 MG Oral Tablet
        "856940",  # acetaminophen 21.7 MG/ML / hydrocodone bitartrate 0.5 MG/ML Oral Solution
        "856944",  # acetaminophen 21.7 MG/ML / hydrocodone bitartrate 0.67 MG/ML Oral Solution
        "856980",  # acetaminophen 300 MG / hydrocodone bitartrate 10 MG Oral Tablet
        "856987",  # acetaminophen 300 MG / hydrocodone bitartrate 5 MG Oral Tablet
        "856992",  # acetaminophen 300 MG / hydrocodone bitartrate 7.5 MG Oral Tablet
        "856999",  # acetaminophen 325 MG / hydrocodone bitartrate 10 MG Oral Tablet
        "857002",  # acetaminophen 325 MG / hydrocodone bitartrate 5 MG Oral Tablet
        "857005",  # acetaminophen 325 MG / hydrocodone bitartrate 7.5 MG Oral Tablet
        "857099",  # acetaminophen 33.3 MG/ML / hydrocodone bitartrate 0.5 MG/ML Oral Solution
        "857121",  # aspirin 500 MG / hydrocodone bitartrate 5 MG Oral Tablet
        "857131",  # acetaminophen 400 MG / hydrocodone bitartrate 5 MG Oral Tablet
        "857391",  # acetaminophen 325 MG / hydrocodone bitartrate 2.5 MG Oral Tablet
        "857512",  # 12 HR chlorpheniramine polistirex 8 MG / hydrocodone polistirex 10 MG Extended Release Oral Capsule
        "858770",  # hydrocodone bitartrate 2.5 MG / ibuprofen 200 MG Oral Tablet
        "858778",  # hydrocodone bitartrate 5 MG / ibuprofen 200 MG Oral Tablet
        "858798",  # hydrocodone bitartrate 7.5 MG / ibuprofen 200 MG Oral Tablet
        "859315",  # hydrocodone bitartrate 10 MG / ibuprofen 200 MG Oral Tablet
        "859383",  # guaifenesin 40 MG/ML / hydrocodone bitartrate 0.5 MG/ML Oral Solution
        "860792",  # 1 ML meperidine hydrochloride 75 MG/ML Cartridge
        "861455",  # meperidine hydrochloride 100 MG Oral Tablet
        "861463",  # meperidine hydrochloride 50 MG/ML Injectable Solution
        "861467",  # meperidine hydrochloride 50 MG Oral Tablet
        "861473",  # 1 ML meperidine hydrochloride 50 MG/ML Cartridge
        "861476",  # 1 ML meperidine hydrochloride 25 MG/ML Injection
        "861479",  # meperidine hydrochloride 10 MG/ML Oral Solution
        "861493",  # 1 ML meperidine hydrochloride 100 MG/ML Cartridge
        "861494",  # 1 ML meperidine hydrochloride 25 MG/ML Cartridge
        "863845",  # Abuse-Deterrent morphine sulfate 100 MG / naltrexone hydrochloride 4 MG Extended Release Oral Capsule
        "863848",  # Abuse-Deterrent morphine sulfate 20 MG / naltrexone hydrochloride 0.8 MG Extended Release Oral Capsule
        "863850",  # Abuse-Deterrent morphine sulfate 30 MG / naltrexone hydrochloride 1.2 MG Extended Release Oral Capsule
        "863852",  # Abuse-Deterrent morphine sulfate 50 MG / naltrexone hydrochloride 2 MG Extended Release Oral Capsule
        "863854",  # Abuse-Deterrent morphine sulfate 60 MG / naltrexone hydrochloride 2.4 MG Extended Release Oral Capsule
        "863856",  # Abuse-Deterrent morphine sulfate 80 MG / naltrexone hydrochloride 3.2 MG Extended Release Oral Capsule
        "864706",  # methadone hydrochloride 10 MG Oral Tablet
        "864714",  # methadone hydrochloride 10 MG/ML Injectable Solution
        "864718",  # methadone hydrochloride 5 MG Oral Tablet
        "864761",  # methadone hydrochloride 1 MG/ML Oral Solution
        "864769",  # methadone hydrochloride 2 MG/ML Oral Solution
        "864978",  # methadone hydrochloride 40 MG Tablet for Oral Suspension
        "886622",  # butorphanol tartrate 2 MG/ML Injectable Solution
        "886627",  # 1 ML butorphanol tartrate 1 MG/ML Injection
        "886634",  # butorphanol tartrate 1 MG/ACTUAT Metered Dose Nasal Spray
        "891874",  # morphine sulfate 100 MG Extended Release Oral Tablet
        "891881",  # morphine sulfate 15 MG Extended Release Oral Tablet
        "891888",  # morphine sulfate 30 MG Extended Release Oral Tablet
        "891893",  # morphine sulfate 60 MG Extended Release Oral Tablet
        "892297",  # 24 HR morphine sulfate 120 MG Extended Release Oral Capsule
        "892342",  # 24 HR morphine sulfate 30 MG Extended Release Oral Capsule
        "892345",  # morphine sulfate 30 MG Extended Release Oral Capsule
        "892349",  # 24 HR morphine sulfate 60 MG Extended Release Oral Capsule
        "892352",  # morphine sulfate 60 MG Extended Release Oral Capsule
        "892355",  # 24 HR morphine sulfate 90 MG Extended Release Oral Capsule
        "892494",  # morphine sulfate 10 MG Extended Release Oral Capsule
        "892516",  # morphine sulfate 10 MG Rectal Suppository
        "892554",  # morphine sulfate 100 MG Extended Release Oral Capsule
        "892582",  # morphine sulfate 15 MG Oral Tablet
        "892589",  # morphine sulfate 2 MG/ML Oral Solution
        "892596",  # morphine sulfate 20 MG Extended Release Oral Capsule
        "892603",  # morphine sulfate 20 MG Rectal Suppository
        "892625",  # morphine sulfate 20 MG/ML Oral Solution
        "892643",  # morphine sulfate 200 MG Extended Release Oral Capsule
        "892646",  # morphine sulfate 200 MG Extended Release Oral Tablet
        "892672",  # morphine sulfate 30 MG Oral Tablet
        "892678",  # morphine sulfate 30 MG Rectal Suppository
        "894780",  # morphine sulfate 4 MG/ML Oral Solution
        "894801",  # morphine sulfate 50 MG Extended Release Oral Capsule
        "894807",  # morphine sulfate 5 MG Rectal Suppository
        "894814",  # morphine sulfate 80 MG Extended Release Oral Capsule
        "894911",  # 0.7 ML morphine sulfate 14.3 MG/ML Auto-Injector
        "894912",  # 1 ML morphine sulfate 10 MG/ML Prefilled Syringe
        "894914",  # 1 ML morphine sulfate 8 MG/ML Prefilled Syringe
        "894942",  # 24 HR morphine sulfate 45 MG Extended Release Oral Capsule
        "894970",  # 24 HR morphine sulfate 75 MG Extended Release Oral Capsule
        "897653",  # 1 ML hydromorphone hydrochloride 1 MG/ML Injection
        "897657",  # hydromorphone hydrochloride 1 MG/ML Oral Solution
        "897696",  # hydromorphone hydrochloride 2 MG Oral Tablet
        "897702",  # hydromorphone hydrochloride 4 MG Oral Tablet
        "897710",  # hydromorphone hydrochloride 8 MG Oral Tablet
        "897745",  # hydromorphone hydrochloride 2 MG/ML Injectable Solution
        "897749",  # hydromorphone hydrochloride 3 MG Rectal Suppository
        "897753",  # 1 ML hydromorphone hydrochloride 4 MG/ML Injection
        "897756",  # 1 ML hydromorphone hydrochloride 1 MG/ML Prefilled Syringe
        "897757",  # 1 ML hydromorphone hydrochloride 2 MG/ML Prefilled Syringe
        "897758",  # 1 ML hydromorphone hydrochloride 4 MG/ML Cartridge
        "902729",  # 24 HR hydromorphone hydrochloride 12 MG Extended Release Oral Tablet
        "902736",  # 24 HR hydromorphone hydrochloride 16 MG Extended Release Oral Tablet
        "902741",  # 24 HR hydromorphone hydrochloride 8 MG Extended Release Oral Tablet
        "904415",  # nalbuphine hydrochloride 10 MG/ML Injectable Solution
        "904440",  # nalbuphine hydrochloride 20 MG/ML Injectable Solution
        "904870",  # 168 HR buprenorphine 0.01 MG/HR Transdermal System
        "904876",  # 168 HR buprenorphine 0.02 MG/HR Transdermal System
        "904880",  # 168 HR buprenorphine 0.005 MG/HR Transdermal System
        "977874",  # 12 HR oxymorphone hydrochloride 10 MG Extended Release Oral Tablet
        "977894",  # 12 HR oxymorphone hydrochloride 15 MG Extended Release Oral Tablet
        "977902",  # 12 HR oxymorphone hydrochloride 20 MG Extended Release Oral Tablet
        "977909",  # 12 HR oxymorphone hydrochloride 30 MG Extended Release Oral Tablet
        "977915",  # 12 HR oxymorphone hydrochloride 40 MG Extended Release Oral Tablet
        "977923",  # 12 HR oxymorphone hydrochloride 5 MG Extended Release Oral Tablet
        "977929",  # 12 HR oxymorphone hydrochloride 7.5 MG Extended Release Oral Tablet
        "977939",  # oxymorphone hydrochloride 5 MG Oral Tablet
        "977942",  # oxymorphone hydrochloride 10 MG Oral Tablet
        "991147",  # methadone hydrochloride 10 MG/ML Oral Solution
        "991486",  # codeine phosphate 2 MG/ML / promethazine hydrochloride 1.25 MG/ML Oral Solution
        "992656",  # homatropine methylbromide 1.5 MG / hydrocodone bitartrate 5 MG Oral Tablet
        "992668",  # homatropine methylbromide 0.3 MG/ML / hydrocodone bitartrate 1 MG/ML Oral Solution
        "993755",  # acetaminophen 24 MG/ML / codeine phosphate 2.4 MG/ML Oral Solution
        "993770",  # acetaminophen 300 MG / codeine phosphate 15 MG Oral Tablet
        "993781",  # acetaminophen 300 MG / codeine phosphate 30 MG Oral Tablet
        "993890",  # acetaminophen 300 MG / codeine phosphate 60 MG Oral Tablet
        "993943",  # acetaminophen 325 MG / butalbital 50 MG / caffeine 40 MG / codeine phosphate 30 MG Oral Capsule
        "994226",  # aspirin 325 MG / carisoprodol 200 MG / codeine phosphate 16 MG Oral Tablet
        "994237",  # aspirin 325 MG / butalbital 50 MG / caffeine 40 MG / codeine phosphate 30 MG Oral Capsule
        "994289",  # brompheniramine maleate 0.27 MG/ML / codeine phosphate 1.27 MG/ML / pseudoephedrine hydrochloride 2 MG/ML Oral Solution
        "994402",  # brompheniramine maleate 0.4 MG/ML / codeine phosphate 1.5 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
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
        "995226",  # codeine phosphate 0.5 MG/ML / guaifenesin 15 MG/ML Oral Solution
        "995438",  # codeine phosphate 1.26 MG/ML / guaifenesin 20 MG/ML Oral Solution
        "995441",  # codeine phosphate 1.5 MG/ML / guaifenesin 45 MG/ML Oral Solution
        "995450",  # codeine phosphate 10 MG / guaifenesin 300 MG Oral Tablet
        "995483",  # codeine phosphate 2 MG/ML / guaifenesin 40 MG/ML Oral Solution
        "995868",  # codeine phosphate 2 MG/ML / guaifenesin 20 MG/ML Oral Solution
        "995983",  # codeine phosphate 2 MG/ML / guaifenesin 20 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "996580",  # codeine phosphate 2 MG/ML / phenylephrine hydrochloride 1 MG/ML / pyrilamine maleate 1 MG/ML Oral Solution
        "996655",  # codeine phosphate 2 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "996706",  # codeine phosphate 20 MG / guaifenesin 400 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "996710",  # codeine phosphate 20 MG / guaifenesin 400 MG / pseudoephedrine hydrochloride 20 MG Oral Tablet
        "996714",  # codeine phosphate 20 MG / guaifenesin 400 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet
        "996725",  # codeine phosphate 20 MG / guaifenesin 400 MG Oral Tablet
        "996728",  # codeine phosphate 20 MG / pseudoephedrine hydrochloride 60 MG Oral Capsule
        "996736",  # codeine phosphate 9 MG / guaifenesin 200 MG Oral Capsule
        "996757",  # codeine phosphate 2 MG/ML / phenylephrine hydrochloride 1 MG/ML / promethazine hydrochloride 1.25 MG/ML Oral Solution
        "996998",  # brompheniramine maleate 0.266 MG/ML / codeine phosphate 1.27 MG/ML / phenylephrine hydrochloride 0.666 MG/ML Oral Solution
        "997170",  # codeine sulfate 15 MG Oral Tablet
        "997287",  # codeine sulfate 30 MG Oral Tablet
        "997296",  # codeine sulfate 60 MG Oral Tablet
        "998212",  # 1 ML morphine sulfate 2 MG/ML Prefilled Syringe
        "998213",  # 1 ML morphine sulfate 4 MG/ML Prefilled Syringe
    }

class ScheduleIvBenzodiazepines(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications that are Schedule IV benzodiazepine medication.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that identify a medication for benzodiazepines.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Schedule IV Benzodiazepines"
    OID = "2.16.840.1.113762.1.4.1125.1"
    DEFINITION_VERSION = "20250211"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1298088",  # flurazepam hydrochloride 15 MG Oral Capsule
        "1298091",  # flurazepam hydrochloride 30 MG Oral Capsule
        "1366192",  # clobazam 2.5 MG/ML Oral Suspension
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
        "197653",  # estazolam 1 MG Oral Tablet
        "197654",  # estazolam 2 MG Oral Tablet
        "197900",  # lorazepam 0.5 MG Oral Tablet
        "197901",  # lorazepam 1 MG Oral Tablet
        "197902",  # lorazepam 2 MG Oral Tablet
        "198057",  # oxazepam 10 MG Oral Capsule
        "198059",  # oxazepam 30 MG Oral Capsule
        "198183",  # quazepam 15 MG Oral Tablet
        "198241",  # temazepam 15 MG Oral Capsule
        "198242",  # temazepam 30 MG Oral Capsule
        "198243",  # temazepam 7.5 MG Oral Capsule
        "198317",  # triazolam 0.125 MG Oral Tablet
        "198318",  # triazolam 0.25 MG Oral Tablet
        "199450",  # clobazam 10 MG Oral Tablet
        "2058253",  # clobazam 10 MG Oral Film
        "2058254",  # clobazam 20 MG Oral Film
        "2058255",  # clobazam 5 MG Oral Film
        "2120550",  # 2 ML diazepam 5 MG/ML Prefilled Syringe
        "2173494",  # midazolam 50 MG/ML Nasal Spray
        "2272613",  # diazepam 100 MG/ML Nasal Spray
        "2272626",  # diazepam 50 MG/ML Nasal Spray
        "2272632",  # diazepam 75 MG/ML Nasal Spray
        "238100",  # lorazepam 2 MG/ML Injectable Solution
        "238101",  # lorazepam 4 MG/ML Injectable Solution
        "2383946",  # remimazolam 20 MG Injection
        "246172",  # clobazam 20 MG Oral Tablet
        "2541170",  # 50 ML midazolam 1 MG/ML Injection
        "2541171",  # 100 ML midazolam 1 MG/ML Injection
        "2569564",  # 24 HR lorazepam 1 MG Extended Release Oral Capsule
        "2569573",  # 24 HR lorazepam 2 MG Extended Release Oral Capsule
        "2569577",  # 24 HR lorazepam 3 MG Extended Release Oral Capsule
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
        "317408",  # lorazepam 4 MG/ML
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
    }

class AndrogenDeprivationTherapyForUrologyCare(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications for androgen deprivation therapy as identified for urology care.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication that is an androgen deprivation therapy medication.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Androgen Deprivation Therapy for Urology Care"
    OID = "2.16.840.1.113762.1.4.1248.352"
    DEFINITION_VERSION = "20250312"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1115257",  # 1.5 ML leuprolide acetate 30 MG/ML Prefilled Syringe
        "1115447",  # 1 ML leuprolide acetate 11.25 MG/ML Prefilled Syringe
        "1115454",  # 1 ML leuprolide acetate 15 MG/ML Prefilled Syringe
        "1115457",  # 1 ML leuprolide acetate 3.75 MG/ML Prefilled Syringe
        "1115462",  # 1 ML leuprolide acetate 7.5 MG/ML Prefilled Syringe
        "1115467",  # 1.5 ML leuprolide acetate 15 MG/ML Prefilled Syringe
        "1115472",  # 1.5 ML leuprolide acetate 7.5 MG/ML Prefilled Syringe
        "1946519",  # 3-Month 1.5 ML leuprolide acetate 20 MG/ML Prefilled Syringe
        "1946521",  # 4-Month 1.5 ML leuprolide acetate 20 MG/ML Prefilled Syringe
        "2606516",  # leuprolide acetate 22.5 MG Injection
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
    }

class BacillusCalmetteGuerinForUrologyCare(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of medications of Bacillus Calmette Guerin (BCG) .

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that identify a medication of Bacillus Calmette Guerin (BCG) for intravesical use.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Bacillus Calmette Guerin for Urology Care"
    OID = "2.16.840.1.113762.1.4.1248.353"
    DEFINITION_VERSION = "20250312"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1653484",  # BCG, live, Tice strain 50 MG/ML Topical Suspension
        "1653579",  # BCG, live, Tice strain 50 MG Injection
    }

class ChemotherapyAgentsForAdvancedCancer(ValueSet):
    """
    **Clinical Focus:** This value set contains RxNORM codes associated with chemotherapy agents commonly used to treat patients with advanced stages of cancer.

    **Data Element Scope:** This would use the Medication QDM category.

    **Inclusion Criteria:** Inclusion Criteria Inclusion Criteria.The following generic, prescribable chemotherapy agents are included in this value set: altretamine, arsenic trioxide, asparaginase, azacytidine, belinostat, bendamustine, bexarotene, bleomycin, busulfan, cabazitaxel, capecitabine, carboplatin, carmustine, chlorambucil, cisplatin, cladribine, clofarabine, cyclophosphamide, cytarabine, cytarabine liposome, dacarbazine, dactinomycin, daunorubicin, decitabine, docetaxel, doxorubicin, epirubicin, eribulin, estramustine, etoposide, floxuridine, fludarabine, fluorouracil, gemcitabine, hydroxyurea, idarubicin, ifosfamide, irinotecan, ixabepilone, lomustine, mechlorethamine, melphalan, mercaptopurine, methotrexate, mitomycin, mitotane, mitoxantrone, nelarabine, omacetaxine, oxaliplatin, paclitaxel, pegaspargase, pemetrexed, pentostatin, pralatrexate, procarbazine, ruxolitinib, streptozocin, temozolomide, teniposide, thioguanine, thiotepa, topotecan, trabectedin, vinblastine, vincristine.

    **Exclusion Criteria:** Chemotherapy agents not listed above are excluded from this value set, including brand name drugs or brand name drug packs.
    """

    VALUE_SET_NAME = "Chemotherapy Agents for Advanced Cancer"
    OID = "2.16.840.1.113762.1.4.1248.355"
    DEFINITION_VERSION = "20250312"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1001405",  # docetaxel 20 MG/ML Injectable Solution
        "1001433",  # 1.5 ML cabazitaxel 40 MG/ML Injection
        "1045456",  # 2 ML eribulin mesylate 0.5 MG/ML Injection
        "105585",  # methotrexate 2.5 MG Oral Tablet
        "105586",  # methotrexate 10 MG Oral Tablet
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
        "1543547",  # belinostat 500 MG Injection
        "1544378",  # 0.2 ML methotrexate 50 MG/ML Auto-Injector
        "1544385",  # 0.25 ML methotrexate 50 MG/ML Auto-Injector
        "1544387",  # 0.3 ML methotrexate 50 MG/ML Auto-Injector
        "1544389",  # 0.35 ML methotrexate 50 MG/ML Auto-Injector
        "1544395",  # 0.45 ML methotrexate 50 MG/ML Auto-Injector
        "1544397",  # 0.5 ML methotrexate 50 MG/ML Auto-Injector
        "1544401",  # 0.6 ML methotrexate 50 MG/ML Auto-Injector
        "1544403",  # 0.15 ML methotrexate 50 MG/ML Auto-Injector
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
        "1872062",  # doxorubicin hydrochloride 20 MG Injection
        "1921592",  # methotrexate 2.5 MG/ML Oral Solution
        "1942743",  # cytarabine liposome 100 MG / daunorubicin liposomal 44 MG Injection
        "1946772",  # methotrexate 25 MG/ML Injectable Solution
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
        "1992545",  # 6 ML arsenic trioxide 2 MG/ML Injection
        "1998783",  # gemcitabine 100 MG/ML Injectable Solution
        "1999308",  # hydroxyurea 100 MG Oral Tablet
        "2002002",  # 10 ML daunorubicin 5 MG/ML Injection
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
        "829926",  # 10 ML arsenic trioxide 1 MG/ML Injection
    }

class ImmunosuppressiveDrugsForUrologyCare(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is represent concepts of medications for immunosuppressive drugs .

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that identify a medication for immunosuppressive drug therapy.

    **Exclusion Criteria:** Excludes concepts that identify a medication not used for immunosuppression.
    """

    VALUE_SET_NAME = "Immunosuppressive Drugs for Urology Care"
    OID = "2.16.840.1.113762.1.4.1248.364"
    DEFINITION_VERSION = "20250312"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
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
        "2048566",  # tofacitinib 10 MG Oral Tablet
        "205175",  # 5 ML cyclosporine 50 MG/ML Injection
        "2052605",  # tacrolimus 0.2 MG Granules for Oral Suspension
        "2052703",  # tacrolimus 1 MG Granules for Oral Suspension
        "205284",  # leflunomide 10 MG Oral Tablet
        "205285",  # leflunomide 20 MG Oral Tablet
        "205286",  # leflunomide 100 MG Oral Tablet
        "205301",  # prednisone 5 MG/ML Oral Solution
        "2056895",  # everolimus 1 MG Oral Tablet
        "2105834",  # 50 ML rituximab-abbs 10 MG/ML Injection
        "2182338",  # 1 ML etanercept 50 MG/ML Cartridge
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
    }

class MedicationsForAboveNormalBmi(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications prescribed for weight loss to patients with an above normal body mass index (BMI) measurement.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for weight loss in patients with an above normal body mass index (BMI) measurement.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Medications for Above Normal BMI"
    OID = "2.16.840.1.113883.3.526.3.1561"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1112982",  # phentermine hydrochloride 15 MG Disintegrating Oral Tablet
        "1112987",  # phentermine hydrochloride 30 MG Disintegrating Oral Tablet
        "1232585",  # 24 HR bupropion hydrochloride 450 MG Extended Release Oral Tablet
        "1249083",  # phentermine hydrochloride 37.5 MG Disintegrating Oral Tablet
        "1302827",  # 24 HR phentermine 7.5 MG / topiramate 46 MG Extended Release Oral Capsule
        "1302839",  # 24 HR phentermine 3.75 MG / topiramate 23 MG Extended Release Oral Capsule
        "1302850",  # 24 HR phentermine 15 MG / topiramate 92 MG Extended Release Oral Capsule
        "1313059",  # 24 HR phentermine 11.25 MG / topiramate 69 MG Extended Release Oral Capsule
        "1551468",  # 12 HR bupropion hydrochloride 90 MG / naltrexone hydrochloride 8 MG Extended Release Oral Tablet
        "1991306",  # 0.25 MG, 0.5 MG Dose 1.5 ML semaglutide 1.34 MG/ML Pen Injector
        "1991316",  # 1 MG Dose 1.5 ML semaglutide 1.34 MG/ML Pen Injector
        "2200644",  # semaglutide 14 MG Oral Tablet
        "2200652",  # semaglutide 3 MG Oral Tablet
        "2200656",  # semaglutide 7 MG Oral Tablet
        "2398841",  # 3 ML semaglutide 1.34 MG/ML Pen Injector
        "2469346",  # setmelanotide 10 MG/ML Injectable Solution
        "2553501",  # 0.5 ML semaglutide 0.5 MG/ML Auto-Injector
        "2553601",  # 0.5 ML semaglutide 1 MG/ML Auto-Injector
        "2553802",  # 0.5 ML semaglutide 2 MG/ML Auto-Injector
        "2553901",  # 0.75 ML semaglutide 2.27 MG/ML Auto-Injector
        "2554102",  # 0.75 ML semaglutide 3.2 MG/ML Auto-Injector
        "2599362",  # 3 ML semaglutide 2.68 MG/ML Pen Injector
        "2601743",  # 0.5 ML tirzepatide 10 MG/ML Auto-Injector
        "2601755",  # 0.5 ML tirzepatide 30 MG/ML Auto-Injector
        "2601761",  # 0.5 ML tirzepatide 5 MG/ML Auto-Injector
        "2601767",  # 0.5 ML tirzepatide 20 MG/ML Auto-Injector
        "2601773",  # 0.5 ML tirzepatide 25 MG/ML Auto-Injector
        "2601784",  # 0.5 ML tirzepatide 15 MG/ML Auto-Injector
        "2611260",  # bupropion hydrochloride 105 MG / dextromethorphan hydrobromide 45 MG Extended Release Oral Tablet
        "2619152",  # 0.25 MG, 0.5 MG Dose 3 ML semaglutide 0.68 MG/ML Pen Injector
        "2644396",  # 0.5 ML tirzepatide 15 MG/ML Injection
        "2644401",  # 0.5 ML tirzepatide 10 MG/ML Injection
        "2644405",  # 0.5 ML tirzepatide 5 MG/ML Injection
        "2644409",  # 0.5 ML tirzepatide 30 MG/ML Injection
        "2644413",  # 0.5 ML tirzepatide 25 MG/ML Injection
        "2644417",  # 0.5 ML tirzepatide 20 MG/ML Injection
        "314153",  # orlistat 120 MG Oral Capsule
        "692876",  # orlistat 60 MG Oral Capsule
        "803348",  # phentermine hydrochloride 37.5 MG Oral Capsule
        "803353",  # phentermine hydrochloride 37.5 MG Oral Tablet
        "826131",  # phentermine hydrochloride 18.8 MG Oral Capsule
        "826586",  # phentermine resin 15 MG Extended Release Oral Capsule
        "826832",  # phentermine resin 30 MG Extended Release Oral Capsule
        "826919",  # phentermine hydrochloride 8 MG Oral Tablet
        "897122",  # 3 ML liraglutide 6 MG/ML Pen Injector
        "900038",  # phentermine hydrochloride 30 MG Oral Capsule
        "904368",  # benzphetamine hydrochloride 50 MG Oral Tablet
        "904372",  # benzphetamine hydrochloride 25 MG Oral Tablet
        "968766",  # phentermine hydrochloride 15 MG Oral Capsule
        "978654",  # diethylpropion hydrochloride 25 MG Oral Tablet
        "978668",  # 24 HR diethylpropion hydrochloride 75 MG Extended Release Oral Tablet
        "979543",  # 24 HR phendimetrazine tartrate 105 MG Extended Release Oral Capsule
        "979549",  # phendimetrazine tartrate 35 MG Oral Tablet
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
    }

class MedicationsForBelowNormalBmi(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications prescribed for weight gain to patients with a below normal body mass index (BMI) measurement.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for weight gain in patients with a below normal body mass index (BMI) measurement.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Medications for Below Normal BMI"
    OID = "2.16.840.1.113883.3.526.3.1562"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1928948",  # dronabinol 5 MG/ML Oral Solution
        "197634",  # dronabinol 10 MG Oral Capsule
        "197635",  # dronabinol 2.5 MG Oral Capsule
        "197636",  # dronabinol 5 MG Oral Capsule
        "577154",  # megestrol acetate 125 MG/ML Oral Suspension
        "860215",  # megestrol acetate 20 MG Oral Tablet
        "860221",  # megestrol acetate 40 MG Oral Tablet
        "860225",  # megestrol acetate 40 MG/ML Oral Suspension
    }

class AnticoagulantTherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications prescribed at hospital discharge for anticoagulant therapy for patients following acute ischemic stroke.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for oral and injectable drug forms of anticoagulants.

    **Exclusion Criteria:** Excludes concepts that represent enoxaparin and heparin generally given for VTE prophylaxis.
    """

    VALUE_SET_NAME = "Anticoagulant Therapy"
    OID = "2.16.840.1.113883.3.117.1.7.1.200"
    DEFINITION_VERSION = "20250206"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1037045",  # dabigatran etexilate 150 MG Oral Capsule
        "1037179",  # dabigatran etexilate 75 MG Oral Capsule
        "1114198",  # rivaroxaban 10 MG Oral Tablet
        "1232082",  # rivaroxaban 15 MG Oral Tablet
        "1232086",  # rivaroxaban 20 MG Oral Tablet
        "1361574",  # heparin sodium, porcine 20000 UNT/ML Injectable Solution
        "1364435",  # apixaban 2.5 MG Oral Tablet
        "1364445",  # apixaban 5 MG Oral Tablet
        "1549682",  # {42 (rivaroxaban 15 MG Oral Tablet) / 9 (rivaroxaban 20 MG Oral Tablet) } Pack
        "1599543",  # edoxaban 15 MG Oral Tablet
        "1599551",  # edoxaban 30 MG Oral Tablet
        "1599555",  # edoxaban 60 MG Oral Tablet
        "1658717",  # 250 ML heparin sodium, porcine 100 UNT/ML Injection
        "1659195",  # 500 ML heparin sodium, porcine 50 UNT/ML Injection
        "1659197",  # 250 ML heparin sodium, porcine 50 UNT/ML Injection
        "1723476",  # dabigatran etexilate 110 MG Oral Capsule
        "1804735",  # 50 ML argatroban 1 MG/ML Injection
        "1804737",  # 125 ML argatroban 1 MG/ML Injection
        "1992427",  # {74 (apixaban 5 MG Oral Tablet) } Pack
        "2059015",  # rivaroxaban 2.5 MG Oral Tablet
        "2588062",  # rivaroxaban 1 MG/ML Oral Suspension
        "2590616",  # dabigatran etexilate 110 MG Oral Pellet
        "2590620",  # dabigatran etexilate 150 MG Oral Pellet
        "2590623",  # dabigatran etexilate 20 MG Oral Pellet
        "2590627",  # dabigatran etexilate 30 MG Oral Pellet
        "2590631",  # dabigatran etexilate 40 MG Oral Pellet
        "2590635",  # dabigatran etexilate 50 MG Oral Pellet
        "2618839",  # 4 ML dalteparin sodium 2500 UNT/ML Injection
        "308351",  # 2.5 ML argatroban 100 MG/ML Injection
        "854238",  # 0.6 ML enoxaparin sodium 100 MG/ML Prefilled Syringe
        "854241",  # 0.8 ML enoxaparin sodium 100 MG/ML Prefilled Syringe
        "854245",  # 0.8 ML enoxaparin sodium 150 MG/ML Prefilled Syringe
        "854248",  # 1 ML enoxaparin sodium 100 MG/ML Prefilled Syringe
        "854252",  # 1 ML enoxaparin sodium 150 MG/ML Prefilled Syringe
        "854255",  # enoxaparin sodium 100 MG/ML Injectable Solution
        "855288",  # warfarin sodium 1 MG Oral Tablet
        "855296",  # warfarin sodium 10 MG Oral Tablet
        "855302",  # warfarin sodium 2 MG Oral Tablet
        "855312",  # warfarin sodium 2.5 MG Oral Tablet
        "855318",  # warfarin sodium 3 MG Oral Tablet
        "855324",  # warfarin sodium 4 MG Oral Tablet
        "855332",  # warfarin sodium 5 MG Oral Tablet
        "855338",  # warfarin sodium 6 MG Oral Tablet
        "855344",  # warfarin sodium 7.5 MG Oral Tablet
        "861356",  # 0.8 ML fondaparinux sodium 12.5 MG/ML Prefilled Syringe
        "861360",  # 0.5 ML fondaparinux sodium 5 MG/ML Prefilled Syringe
        "861363",  # 0.4 ML fondaparinux sodium 12.5 MG/ML Prefilled Syringe
        "861365",  # 0.6 ML fondaparinux sodium 12.5 MG/ML Prefilled Syringe
        "978725",  # 0.2 ML dalteparin sodium 12500 UNT/ML Prefilled Syringe
        "978733",  # 0.2 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978736",  # 0.3 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978740",  # 0.5 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978744",  # 0.6 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978746",  # 0.72 ML dalteparin sodium 25000 UNT/ML Prefilled Syringe
        "978755",  # 1 ML dalteparin sodium 10000 UNT/ML Prefilled Syringe
        "978759",  # dalteparin sodium 10000 UNT/ML Injectable Solution
        "978777",  # dalteparin sodium 25000 UNT/ML Injectable Solution
    }

class ThrombolyticTpaTherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications prescribed for thrombolytic (t-PA) therapy for treatment of ischemic stroke.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent a medication for stroke treatment consistent with administration by intravenous (IV) route.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Thrombolytic tPA Therapy"
    OID = "2.16.840.1.113883.3.117.1.7.1.226"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1804799",  # alteplase 100 MG Injection
        "1804804",  # alteplase 50 MG Injection
        "313212",  # tenecteplase 50 MG Injection
    }

class HypoglycemicsSevereHypoglycemia(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for medications capable of causing severe hypoglycemia.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent insulin, non-insulin injectable antidiabetics, and oral antidiabetic medication.

    **Exclusion Criteria:** Excludes concepts that represent medications used to treat diabetes mellitus but are not commonly associated with severe hypoglycemia.
    """

    VALUE_SET_NAME = "Hypoglycemics Severe Hypoglycemia"
    OID = "2.16.840.1.113762.1.4.1196.393"
    DEFINITION_VERSION = "20240117"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1361493",  # glimepiride 6 MG Oral Tablet
        "1361495",  # glimepiride 8 MG Oral Tablet
        "153842",  # glimepiride 3 MG Oral Tablet
        "1543202",  # insulin, regular, human 4 UNT Inhalation Powder
        "1544488",  # insulin, regular, human 8 UNT Inhalation Powder
        "1551295",  # 0.5 ML dulaglutide 1.5 MG/ML Auto-Injector
        "1551304",  # 0.5 ML dulaglutide 3 MG/ML Auto-Injector
        "1604539",  # 1.5 ML insulin glargine 300 UNT/ML Pen Injector
        "1652239",  # 3 ML insulin lispro 200 UNT/ML Pen Injector
        "1652639",  # 3 ML insulin lispro 100 UNT/ML Pen Injector
        "1652644",  # 3 ML insulin lispro 100 UNT/ML Cartridge
        "1653196",  # 3 ML insulin aspart, human 100 UNT/ML Cartridge
        "1653202",  # 3 ML insulin aspart, human 100 UNT/ML Pen Injector
        "1654862",  # 3 ML insulin isophane, human 100 UNT/ML Pen Injector
        "1654910",  # insulin, regular, human 12 UNT Inhalation Powder
        "1670011",  # 3 ML insulin degludec 100 UNT/ML Pen Injector
        "1670021",  # 3 ML insulin degludec 200 UNT/ML Pen Injector
        "1731315",  # 3 ML insulin, regular, human 500 UNT/ML Pen Injector
        "1798387",  # {90 (insulin, regular, human 4 UNT Inhalation Powder) / 90 (insulin, regular, human 8 UNT Inhalation Powder) } Pack
        "1860167",  # 3 ML insulin degludec 100 UNT/ML / liraglutide 3.6 MG/ML Pen Injector
        "1862101",  # {60 (insulin, regular, human 12 UNT Inhalation Powder) / 60 (insulin, regular, human 4 UNT Inhalation Powder) / 60 (insulin, regular, human 8 UNT Inhalation Powder) } Pack
        "1926331",  # 0.5 UNT Doses 3 ML insulin lispro 100 UNT/ML Pen Injector
        "197495",  # chlorpropamide 100 MG Oral Tablet
        "197496",  # chlorpropamide 250 MG Oral Tablet
        "197737",  # glyburide 1.25 MG Oral Tablet
        "198292",  # tolazamide 250 MG Oral Tablet
        "198293",  # tolazamide 500 MG Oral Tablet
        "198294",  # tolbutamide 500 MG Oral Tablet
        "199245",  # glimepiride 1 MG Oral Tablet
        "199246",  # glimepiride 2 MG Oral Tablet
        "199247",  # glimepiride 4 MG Oral Tablet
        "2002419",  # 3 ML insulin glargine 300 UNT/ML Pen Injector
        "200256",  # repaglinide 1 MG Oral Tablet
        "200257",  # repaglinide 0.5 MG Oral Tablet
        "200258",  # repaglinide 2 MG Oral Tablet
        "2100028",  # {90 (insulin, regular, human 12 UNT Inhalation Powder) / 90 (insulin, regular, human 8 UNT Inhalation Powder) } Pack
        "2107520",  # insulin degludec 100 UNT/ML Injectable Solution
        "2179744",  # 100 ML insulin, regular, human 1 UNT/ML Injection
        "2206090",  # 3 ML insulin, regular, human 100 UNT/ML Pen Injector
        "2268064",  # Sensor 3 ML insulin glargine 100 UNT/ML Pen Injector
        "2380231",  # insulin lispro-aabc 100 UNT/ML Injectable Solution
        "2380254",  # 3 ML insulin lispro-aabc 200 UNT/ML Pen Injector
        "2380259",  # 3 ML insulin lispro-aabc 100 UNT/ML Pen Injector
        "2380267",  # Sensor 3 ML insulin lispro-aabc 100 UNT/ML Pen Injector
        "2395777",  # 0.5 ML dulaglutide 6 MG/ML Auto-Injector
        "2395783",  # 0.5 ML dulaglutide 9 MG/ML Auto-Injector
        "242120",  # insulin lispro 100 UNT/ML Injectable Solution
        "249220",  # insulin, regular, human 500 UNT/ML Injectable Solution
        "2563971",  # 3 ML insulin glargine-yfgn 100 UNT/ML Pen Injector
        "2563976",  # insulin glargine-yfgn 100 UNT/ML Injectable Solution
        "2589008",  # 3 ML insulin glargine-aglr 100 UNT/ML Pen Injector
        "259111",  # insulin lispro 25 UNT/ML / insulin lispro protamine, human 75 UNT/ML Injectable Suspension
        "260265",  # insulin lispro 50 UNT/ML / insulin lispro protamine, human 50 UNT/ML Injectable Suspension
        "2621571",  # Sensor 3 ML insulin lispro 100 UNT/ML Pen Injector
        "2642808",  # 1.6 ML insulin aspart, human 100 UNT/ML Cartridge
        "2644768",  # {9 (insulin, regular, human 12 UNT Inhalation Powder) / 9 (insulin, regular, human 4 UNT Inhalation Powder) / 9 (insulin, regular, human 8 UNT Inhalation Powder) } Pack
        "310488",  # glipizide 10 MG Oral Tablet
        "310489",  # 24 HR glipizide 2.5 MG Extended Release Oral Tablet
        "310490",  # glipizide 5 MG Oral Tablet
        "310534",  # glyburide 2.5 MG Oral Tablet
        "310536",  # glyburide 3 MG Oral Tablet
        "310537",  # glyburide 5 MG Oral Tablet
        "310539",  # glyburide 6 MG Oral Tablet
        "311028",  # insulin isophane, human 100 UNT/ML Injectable Suspension
        "311034",  # insulin, regular, human 100 UNT/ML Injectable Solution
        "311040",  # insulin aspart, human 100 UNT/ML Injectable Solution
        "311041",  # insulin glargine 100 UNT/ML Injectable Solution
        "311048",  # insulin isophane, human 70 UNT/ML / insulin, regular, human 30 UNT/ML Injectable Suspension
        "311919",  # nateglinide 120 MG Oral Tablet
        "314000",  # glyburide 1.5 MG Oral Tablet
        "314006",  # 24 HR glipizide 5 MG Extended Release Oral Tablet
        "314142",  # nateglinide 60 MG Oral Tablet
        "315107",  # 24 HR glipizide 10 MG Extended Release Oral Tablet
        "351297",  # insulin aspart protamine, human 70 UNT/ML / insulin aspart, human 30 UNT/ML Injectable Suspension
        "379804",  # glipizide 2.5 MG Oral Tablet
        "484322",  # insulin detemir 100 UNT/ML Injectable Solution
        "485210",  # insulin glulisine, human 100 UNT/ML Injectable Solution
        "647237",  # glimepiride 2 MG / pioglitazone 30 MG Oral Tablet
        "647239",  # glimepiride 4 MG / pioglitazone 30 MG Oral Tablet
        "847187",  # 3 ML insulin isophane, human 70 UNT/ML / insulin, regular, human 30 UNT/ML Pen Injector
        "847191",  # 3 ML insulin aspart protamine, human 70 UNT/ML / insulin aspart, human 30 UNT/ML Pen Injector
        "847211",  # 3 ML insulin lispro 50 UNT/ML / insulin lispro protamine, human 50 UNT/ML Pen Injector
        "847230",  # 3 ML insulin glargine 100 UNT/ML Pen Injector
        "847239",  # 3 ML insulin detemir 100 UNT/ML Pen Injector
        "847252",  # 3 ML insulin lispro 25 UNT/ML / insulin lispro protamine, human 75 UNT/ML Pen Injector
        "847259",  # 3 ML insulin glulisine, human 100 UNT/ML Pen Injector
        "861731",  # glipizide 2.5 MG / metformin hydrochloride 250 MG Oral Tablet
        "861736",  # glipizide 2.5 MG / metformin hydrochloride 500 MG Oral Tablet
        "861740",  # glipizide 5 MG / metformin hydrochloride 500 MG Oral Tablet
        "861743",  # glyburide 1.25 MG / metformin hydrochloride 250 MG Oral Tablet
        "861748",  # glyburide 2.5 MG / metformin hydrochloride 500 MG Oral Tablet
        "861753",  # glyburide 5 MG / metformin hydrochloride 500 MG Oral Tablet
    }

class OpioidAntagonist(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for the opioid antagonist medications naloxone and nalmefine administered to reverse over-administration of opioids in the hospital setting

    **Data Element Scope:** This value set may use a model element related to Medication

    **Inclusion Criteria:** Includes concepts that represent non-enteral (intranasal, intramuscular, intravenous, subcutaneous, inhalation) forms of naloxone and nalmefene medications

    **Exclusion Criteria:** Excludes all other types of opioid antagonists such as naltrexone. Excludes combination medications that contain both an opioid antagonist and an opioid. Excludes concepts that represent enteral (e.g., oral, gastrointestinal) forms of naloxone and nalmefene medications.
    """

    VALUE_SET_NAME = "Opioid Antagonist"
    OID = "2.16.840.1.113762.1.4.1248.119"
    DEFINITION_VERSION = "20250211"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1191222",  # naloxone hydrochloride 0.4 MG/ML Injectable Solution
        "1191234",  # 1 ML naloxone hydrochloride 0.4 MG/ML Cartridge
        "1191250",  # 2 ML naloxone hydrochloride 1 MG/ML Prefilled Syringe
        "1659929",  # 1 ML naloxone hydrochloride 0.4 MG/ML Injection
        "1725059",  # naloxone hydrochloride 40 MG/ML Nasal Spray
        "1870933",  # naloxone hydrochloride 20 MG/ML Nasal Spray
        "199059",  # nalmefene 1 MG/ML Injectable Solution
        "2540703",  # naloxone hydrochloride 80 MG/ML Nasal Spray
        "2589612",  # 0.5 ML naloxone hydrochloride 10 MG/ML Prefilled Syringe
        "2592953",  # 2 ML nalmefene 1 MG/ML Injection
        "2596175",  # 0.4 ML naloxone hydrochloride 25 MG/ML Auto-Injector
        "2639721",  # nalmefene 27 MG/ML Nasal Spray
    }

class OpioidsAll(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for opioid medications.

    **Data Element Scope:** This value set may use a model element related to Medication

    **Inclusion Criteria:** Includes concepts that represent all formulations of opioids that may be administered in an inpatient or outpatient setting regardless of intended use. Includes combination medications that contain both an opioid and naloxone or nalmefene which are opioid antagonists.

    **Exclusion Criteria:** Excludes concepts that represent medications used as opiate antagonists.
    """

    VALUE_SET_NAME = "Opioids, All"
    OID = "2.16.840.1.113762.1.4.1196.226"
    DEFINITION_VERSION = "20240124"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1372265",  # chlorpheniramine maleate 0.8 MG/ML / hydrocodone bitartrate 1 MG/ML Oral Solution
        "1010600",  # buprenorphine 2 MG / naloxone 0.5 MG Sublingual Film
        "1010604",  # buprenorphine 8 MG / naloxone 2 MG Sublingual Film
        "1014599",  # acetaminophen 300 MG / oxycodone hydrochloride 10 MG Oral Tablet
        "1014615",  # acetaminophen 300 MG / oxycodone hydrochloride 5 MG Oral Tablet
        "1014632",  # acetaminophen 300 MG / oxycodone hydrochloride 7.5 MG Oral Tablet
        "1037259",  # acetaminophen 300 MG / oxycodone hydrochloride 2.5 MG Oral Tablet
        "1042693",  # chlorpheniramine maleate 0.4 MG/ML / codeine phosphate 2 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "1044427",  # acetaminophen 20 MG/ML / hydrocodone bitartrate 0.667 MG/ML Oral Solution
        "1049214",  # acetaminophen 325 MG / oxycodone hydrochloride 10 MG Oral Tablet
        "1049221",  # acetaminophen 325 MG / oxycodone hydrochloride 5 MG Oral Tablet
        "1049225",  # acetaminophen 325 MG / oxycodone hydrochloride 7.5 MG Oral Tablet
        "1049251",  # acetaminophen 400 MG / oxycodone hydrochloride 10 MG Oral Tablet
        "1049260",  # acetaminophen 400 MG / oxycodone hydrochloride 5 MG Oral Tablet
        "1049502",  # 12 HR oxycodone hydrochloride 10 MG Extended Release Oral Tablet
        "1049543",  # 12 HR oxycodone hydrochloride 15 MG Extended Release Oral Tablet
        "1049574",  # 12 HR oxycodone hydrochloride 30 MG Extended Release Oral Tablet
        "1049580",  # acetaminophen 65 MG/ML / oxycodone hydrochloride 1 MG/ML Oral Solution
        "1049589",  # ibuprofen 400 MG / oxycodone hydrochloride 5 MG Oral Tablet
        "1049593",  # 12 HR oxycodone hydrochloride 60 MG Extended Release Oral Tablet
        "1049604",  # oxycodone hydrochloride 1 MG/ML Oral Solution
        "1049611",  # oxycodone hydrochloride 15 MG Oral Tablet
        "1049615",  # oxycodone hydrochloride 20 MG/ML Oral Solution
        "1049618",  # oxycodone hydrochloride 30 MG Oral Tablet
        "1049621",  # oxycodone hydrochloride 5 MG Oral Tablet
        "1049635",  # acetaminophen 325 MG / oxycodone hydrochloride 2.5 MG Oral Tablet
        "1049683",  # oxycodone hydrochloride 10 MG Oral Tablet
        "1049686",  # oxycodone hydrochloride 20 MG Oral Tablet
        "1049696",  # oxycodone hydrochloride 5 MG Oral Capsule
        "1053647",  # fentanyl 0.1 MG Sublingual Tablet
        "1053652",  # fentanyl 0.2 MG Sublingual Tablet
        "1053655",  # fentanyl 0.3 MG Sublingual Tablet
        "1053658",  # fentanyl 0.4 MG Sublingual Tablet
        "1053661",  # fentanyl 0.6 MG Sublingual Tablet
        "1053664",  # fentanyl 0.8 MG Sublingual Tablet
        "1087459",  # 12 HR chlorpheniramine polistirex 1.6 MG/ML / hydrocodone polistirex 2 MG/ML Extended Release Suspension
        "1089055",  # codeine phosphate 10 MG / guaifenesin 400 MG / pseudoephedrine hydrochloride 20 MG Oral Tablet
        "1089058",  # codeine phosphate 10 MG / guaifenesin 400 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet
        "1112220",  # chlorpheniramine maleate 0.8 MG/ML / hydrocodone bitartrate 1 MG/ML / pseudoephedrine hydrochloride 12 MG/ML Oral Solution
        "1113314",  # oxycodone hydrochloride 7.5 MG Oral Tablet
        "1114026",  # codeine phosphate 1.6 MG/ML / guaifenesin 40 MG/ML Oral Solution
        "1115573",  # fentanyl 0.1 MG/ACTUAT Metered Dose Nasal Spray
        "1115577",  # fentanyl 0.4 MG/ACTUAT Metered Dose Nasal Spray
        "1148478",  # 24 HR tramadol hydrochloride 100 MG Extended Release Oral Capsule
        "1148485",  # 24 HR tramadol hydrochloride 200 MG Extended Release Oral Capsule
        "1148489",  # 24 HR tramadol hydrochloride 300 MG Extended Release Oral Capsule
        "1148797",  # 12 HR tapentadol 100 MG Extended Release Oral Tablet
        "1148800",  # 12 HR tapentadol 150 MG Extended Release Oral Tablet
        "1148803",  # 12 HR tapentadol 200 MG Extended Release Oral Tablet
        "1148807",  # 12 HR tapentadol 250 MG Extended Release Oral Tablet
        "1148809",  # 12 HR tapentadol 50 MG Extended Release Oral Tablet
        "1190580",  # codeine phosphate 1.2 MG/ML / dexbrompheniramine maleate 0.133 MG/ML / pseudoephedrine hydrochloride 4 MG/ML Oral Solution
        "1235862",  # chlorcyclizine hydrochloride 2.5 MG/ML / codeine phosphate 1.8 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1237050",  # fentanyl 0.1 MG/ACTUAT Mucosal Spray
        "1237057",  # fentanyl 0.2 MG/ACTUAT Mucosal Spray
        "1237060",  # fentanyl 0.4 MG/ACTUAT Mucosal Spray
        "1237064",  # fentanyl 0.6 MG/ACTUAT Mucosal Spray
        "1237068",  # fentanyl 0.8 MG/ACTUAT Mucosal Spray
        "1248115",  # 24 HR tramadol hydrochloride 150 MG Extended Release Oral Capsule
        "1303736",  # morphine sulfate 40 MG Extended Release Oral Capsule
        "1306898",  # 24 HR hydromorphone hydrochloride 32 MG Extended Release Oral Tablet
        "1307056",  # buprenorphine 4 MG / naloxone 1 MG Sublingual Film
        "1307061",  # buprenorphine 12 MG / naloxone 3 MG Sublingual Film
        "1356797",  # brompheniramine maleate 4 MG / codeine phosphate 10 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1356800",  # brompheniramine maleate 4 MG / codeine phosphate 10 MG Oral Tablet
        "1356804",  # brompheniramine maleate 4 MG / codeine phosphate 20 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "1356807",  # brompheniramine maleate 4 MG / codeine phosphate 20 MG Oral Tablet
        "1366873",  # hydrocodone bitartrate 5 MG / pseudoephedrine hydrochloride 60 MG Oral Tablet
        "1431076",  # buprenorphine 1.4 MG / naloxone 0.36 MG Sublingual Tablet
        "1431102",  # buprenorphine 5.7 MG / naloxone 1.4 MG Sublingual Tablet
        "1431286",  # acetaminophen 300 MG / butalbital 50 MG / caffeine 40 MG / codeine phosphate 30 MG Oral Capsule
        "1432969",  # 168 HR buprenorphine 0.015 MG/HR Transdermal System
        "1433251",  # 0.5 ML hydromorphone hydrochloride 1 MG/ML Prefilled Syringe
        "1440003",  # codeine phosphate 1.8 MG/ML / dexchlorpheniramine maleate 0.2 MG/ML / phenylephrine hydrochloride 1 MG/ML Oral Solution
        "1442790",  # 1 ML morphine sulfate 5 MG/ML Prefilled Syringe
        "1541630",  # brompheniramine maleate 0.8 MG/ML / codeine phosphate 2 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "1542390",  # buprenorphine 2.1 MG / naloxone 0.3 MG Buccal Film
        "1542997",  # 168 HR buprenorphine 0.0075 MG/HR Transdermal System
        "1544851",  # buprenorphine 4.2 MG / naloxone 0.7 MG Buccal Film
        "1544854",  # buprenorphine 6.3 MG / naloxone 1 MG Buccal Film
        "1595730",  # Abuse-Deterrent 24 HR hydrocodone bitartrate 20 MG Extended Release Oral Tablet
        "1595740",  # Abuse-Deterrent 24 HR hydrocodone bitartrate 30 MG Extended Release Oral Tablet
        "1595746",  # Abuse-Deterrent 24 HR hydrocodone bitartrate 40 MG Extended Release Oral Tablet
        "1595752",  # Abuse-Deterrent 24 HR hydrocodone bitartrate 60 MG Extended Release Oral Tablet
        "1595758",  # Abuse-Deterrent 24 HR hydrocodone bitartrate 80 MG Extended Release Oral Tablet
        "1595764",  # Abuse-Deterrent 24 HR hydrocodone bitartrate 100 MG Extended Release Oral Tablet
        "1595770",  # Abuse-Deterrent 24 HR hydrocodone bitartrate 120 MG Extended Release Oral Tablet
        "1596108",  # acetaminophen 320.5 MG / caffeine 30 MG / dihydrocodeine bitartrate 16 MG Oral Capsule
        "1597568",  # buprenorphine 11.4 MG / naloxone 2.9 MG Sublingual Tablet
        "1597573",  # buprenorphine 8.6 MG / naloxone 2.1 MG Sublingual Tablet
        "1603495",  # 72 HR fentanyl 0.0375 MG/HR Transdermal System
        "1603498",  # 72 HR fentanyl 0.0625 MG/HR Transdermal System
        "1603501",  # 72 HR fentanyl 0.0875 MG/HR Transdermal System
        "1651558",  # guaifenesin 40 MG/ML / hydrocodone bitartrate 0.5 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1652087",  # 12 HR chlorpheniramine polistirex 0.8 MG/ML / codeine polistirex 4 MG/ML Extended Release Suspension
        "1655032",  # 1 ML buprenorphine 0.3 MG/ML Cartridge
        "1661319",  # codeine phosphate 2 MG/ML / phenylephrine hydrochloride 2 MG/ML / triprolidine hydrochloride 0.5 MG/ML Oral Solution
        "1664543",  # 12 HR chlorpheniramine maleate 8 MG / codeine phosphate 54.3 MG Extended Release Oral Tablet
        "1665685",  # 1 ML meperidine hydrochloride 100 MG/ML Injection
        "1665697",  # 1 ML meperidine hydrochloride 50 MG/ML Injection
        "1665699",  # 0.5 ML meperidine hydrochloride 50 MG/ML Injection
        "1665701",  # 2 ML meperidine hydrochloride 50 MG/ML Injection
        "1666338",  # buprenorphine 2.9 MG / naloxone 0.71 MG Sublingual Tablet
        "1666831",  # 80 ACTUAT fentanyl 0.04 MG/ACTUAT Transdermal System
        "1716057",  # buprenorphine 0.15 MG Buccal Film
        "1716065",  # buprenorphine 0.3 MG Buccal Film
        "1716069",  # buprenorphine 0.45 MG Buccal Film
        "1716073",  # buprenorphine 0.6 MG Buccal Film
        "1716077",  # buprenorphine 0.075 MG Buccal Film
        "1716081",  # buprenorphine 0.75 MG Buccal Film
        "1716086",  # buprenorphine 0.9 MG Buccal Film
        "1723206",  # 2 ML alfentanil 0.5 MG/ML Injection
        "1723208",  # 10 ML alfentanil 0.5 MG/ML Injection
        "1723209",  # 20 ML alfentanil 0.5 MG/ML Injection
        "1723210",  # 5 ML alfentanil 0.5 MG/ML Injection
        "1724276",  # 1 ML hydromorphone hydrochloride 2 MG/ML Injection
        "1724338",  # 1 ML hydromorphone hydrochloride 10 MG/ML Injection
        "1724340",  # 5 ML hydromorphone hydrochloride 10 MG/ML Injection
        "1724341",  # 50 ML hydromorphone hydrochloride 10 MG/ML Injection
        "1724383",  # 1 ML hydromorphone hydrochloride 1 MG/ML Cartridge
        "1724644",  # 1 ML hydromorphone hydrochloride 2 MG/ML Cartridge
        "1728351",  # 1 ML butorphanol tartrate 2 MG/ML Injection
        "1728355",  # 2 ML butorphanol tartrate 2 MG/ML Injection
        "1728783",  # 10 ML morphine sulfate 0.5 MG/ML Injection
        "1728791",  # 2 ML morphine sulfate 0.5 MG/ML Injection
        "1728800",  # 10 ML morphine sulfate 1 MG/ML Injection
        "1728999",  # 30 ML morphine sulfate 1 MG/ML Injection
        "1729197",  # 1 ML morphine sulfate 2 MG/ML Cartridge
        "1729320",  # fentanyl 0.3 MG/ACTUAT Metered Dose Nasal Spray
        "1729578",  # remifentanil 1 MG Injection
        "1729584",  # remifentanil 2 MG Injection
        "1729710",  # remifentanil 5 MG Injection
        "1731520",  # 4 ML morphine sulfate 25 MG/ML Injection
        "1731522",  # 20 ML morphine sulfate 25 MG/ML Injection
        "1731537",  # 20 ML morphine sulfate 50 MG/ML Injection
        "1731545",  # 50 ML morphine sulfate 50 MG/ML Injection
        "1731990",  # 1.5 ML morphine sulfate liposomal 10 MG/ML Injection
        "1731993",  # 1 ML morphine sulfate 10 MG/ML Injection
        "1731995",  # 1 ML morphine sulfate 10 MG/ML Cartridge
        "1731998",  # 20 ML morphine sulfate 10 MG/ML Injection
        "1732003",  # 1 ML morphine sulfate 8 MG/ML Cartridge
        "1732006",  # 1 ML morphine sulfate 4 MG/ML Injection
        "1732011",  # 1 ML morphine sulfate 8 MG/ML Injection
        "1732014",  # 1 ML morphine sulfate 4 MG/ML Cartridge
        "1732136",  # 1 ML morphine sulfate 5 MG/ML Injection
        "1733080",  # 1 ML morphine sulfate 15 MG/ML Cartridge
        "1735003",  # 2 ML fentanyl 0.05 MG/ML Injection
        "1735006",  # 10 ML fentanyl 0.05 MG/ML Injection
        "1735007",  # 5 ML fentanyl 0.05 MG/ML Injection
        "1735008",  # 20 ML fentanyl 0.05 MG/ML Injection
        "1735013",  # 50 ML fentanyl 0.05 MG/ML Injection
        "1740007",  # {2 (fentanyl 0.6 MG/ACTUAT Mucosal Spray) } Pack
        "1740009",  # {2 (fentanyl 0.8 MG/ACTUAT Mucosal Spray) } Pack
        "1790527",  # Abuse-Deterrent 12 HR oxycodone 9 MG Extended Release Oral Capsule
        "1791558",  # Abuse-Deterrent 12 HR oxycodone 13.5 MG Extended Release Oral Capsule
        "1791567",  # Abuse-Deterrent 12 HR oxycodone 18 MG Extended Release Oral Capsule
        "1791574",  # Abuse-Deterrent 12 HR oxycodone 27 MG Extended Release Oral Capsule
        "1791580",  # Abuse-Deterrent 12 HR oxycodone 36 MG Extended Release Oral Capsule
        "1792707",  # codeine phosphate 2 MG/ML / guaifenesin 40 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "1797650",  # buprenorphine 74.2 MG Drug Implant
        "1809097",  # 1 ML sufentanil 0.05 MG/ML Injection
        "1809102",  # 2 ML sufentanil 0.05 MG/ML Injection
        "1809104",  # 5 ML sufentanil 0.05 MG/ML Injection
        "1812164",  # acetaminophen 325 MG / caffeine 30 MG / dihydrocodeine bitartrate 16 MG Oral Tablet
        "1860127",  # Abuse-Deterrent 12 HR oxycodone hydrochloride 60 MG Extended Release Oral Tablet
        "1860129",  # Abuse-Deterrent 12 HR oxycodone hydrochloride 20 MG Extended Release Oral Tablet
        "1860137",  # Abuse-Deterrent 12 HR oxycodone hydrochloride 40 MG Extended Release Oral Tablet
        "1860148",  # Abuse-Deterrent 12 HR oxycodone hydrochloride 80 MG Extended Release Oral Tablet
        "1860151",  # Abuse-Deterrent 12 HR oxycodone hydrochloride 30 MG Extended Release Oral Tablet
        "1860154",  # Abuse-Deterrent 12 HR oxycodone hydrochloride 15 MG Extended Release Oral Tablet
        "1860157",  # Abuse-Deterrent 12 HR oxycodone hydrochloride 10 MG Extended Release Oral Tablet
        "1860491",  # 12 HR hydrocodone bitartrate 10 MG Extended Release Oral Capsule
        "1860493",  # 12 HR hydrocodone bitartrate 15 MG Extended Release Oral Capsule
        "1860495",  # 12 HR hydrocodone bitartrate 20 MG Extended Release Oral Capsule
        "1860497",  # 12 HR hydrocodone bitartrate 30 MG Extended Release Oral Capsule
        "1860499",  # 12 HR hydrocodone bitartrate 40 MG Extended Release Oral Capsule
        "1860501",  # 12 HR hydrocodone bitartrate 50 MG Extended Release Oral Capsule
        "1864412",  # buprenorphine 0.7 MG / naloxone 0.18 MG Sublingual Tablet
        "1866543",  # 1 ML nalbuphine hydrochloride 10 MG/ML Injection
        "1866551",  # 1 ML nalbuphine hydrochloride 20 MG/ML Injection
        "1871434",  # Abuse-Deterrent 12 HR morphine sulfate 15 MG Extended Release Oral Tablet
        "1871441",  # Abuse-Deterrent 12 HR morphine sulfate 30 MG Extended Release Oral Tablet
        "1871444",  # Abuse-Deterrent 12 HR morphine sulfate 60 MG Extended Release Oral Tablet
        "1872271",  # 1 ML hydromorphone hydrochloride 4 MG/ML Prefilled Syringe
        "1944529",  # Abuse-Deterrent oxycodone hydrochloride 15 MG Oral Tablet
        "1944538",  # Abuse-Deterrent oxycodone hydrochloride 30 MG Oral Tablet
        "1944541",  # Abuse-Deterrent oxycodone hydrochloride 5 MG Oral Tablet
        "1946525",  # Matrix Delivery 24 HR tramadol hydrochloride 300 MG Extended Release Oral Tablet
        "1946527",  # Matrix Delivery 24 HR tramadol hydrochloride 200 MG Extended Release Oral Tablet
        "1946529",  # Matrix Delivery 24 HR tramadol hydrochloride 100 MG Extended Release Oral Tablet
        "197696",  # 72 HR fentanyl 0.075 MG/HR Transdermal System
        "197873",  # levorphanol tartrate 2 MG Oral Tablet
        "1996184",  # 0.5 ML buprenorphine 200 MG/ML Prefilled Syringe
        "1996192",  # 1.5 ML buprenorphine 200 MG/ML Prefilled Syringe
        "2001358",  # acetaminophen 325 MG / benzhydrocodone 6.12 MG Oral Tablet
        "2003714",  # 1 ML morphine sulfate 2 MG/ML Injection
        "2056893",  # chlorpheniramine maleate 0.8 MG/ML / codeine phosphate 2 MG/ML / phenylephrine hydrochloride 2 MG/ML Oral Solution
        "2058845",  # levorphanol tartrate 3 MG Oral Tablet
        "2103192",  # sufentanil 0.03 MG Sublingual Tablet
        "2105822",  # acetaminophen 60 MG/ML / oxycodone hydrochloride 2 MG/ML Oral Solution
        "2118728",  # acetaminophen 325 MG / benzhydrocodone 4.08 MG Oral Tablet
        "2118732",  # acetaminophen 325 MG / benzhydrocodone 8.16 MG Oral Tablet
        "2168270",  # 1 ML fentanyl 0.05 MG/ML Injection
        "2179635",  # tramadol hydrochloride 100 MG Oral Tablet
        "2277368",  # 1 ML hydromorphone hydrochloride 0.2 MG/ML Prefilled Syringe
        "238129",  # 1 ML buprenorphine 0.3 MG/ML Injection
        "238133",  # pentazocine 30 MG/ML Injectable Solution
        "2392234",  # 1 ML oliceridine 1 MG/ML Injection
        "2392242",  # 2 ML oliceridine 1 MG/ML Injection
        "2392244",  # 30 ML oliceridine 1 MG/ML Injection
        "2395808",  # tramadol hydrochloride 5 MG/ML Oral Solution
        "245134",  # 72 HR fentanyl 0.025 MG/HR Transdermal System
        "245135",  # 72 HR fentanyl 0.05 MG/HR Transdermal System
        "245136",  # 72 HR fentanyl 0.1 MG/HR Transdermal System
        "2474267",  # 2 ML fentanyl 0.05 MG/ML Prefilled Syringe
        "2474269",  # 1 ML fentanyl 0.05 MG/ML Prefilled Syringe
        "2539186",  # 1 ML meperidine hydrochloride 50 MG/ML Prefilled Syringe
        "2539191",  # 1 ML meperidine hydrochloride 25 MG/ML Prefilled Syringe
        "2588478",  # celecoxib 56 MG / tramadol hydrochloride 44 MG Oral Tablet
        "2629337",  # 0.5 ML fentanyl 0.05 MG/ML Prefilled Syringe
        "2635081",  # 100 ML fentanyl 0.05 MG/ML Injection
        "2639021",  # 0.16 ML buprenorphine 50 MG/ML Prefilled Syringe
        "2639029",  # 0.32 ML buprenorphine 50 MG/ML Prefilled Syringe
        "2639031",  # 0.48 ML buprenorphine 50 MG/ML Prefilled Syringe
        "2639033",  # 0.64 ML buprenorphine 50 MG/ML Prefilled Syringe
        "2639036",  # 0.18 ML buprenorphine 356 MG/ML Prefilled Syringe
        "2639041",  # 0.27 ML buprenorphine 356 MG/ML Prefilled Syringe
        "2639043",  # 0.36 ML buprenorphine 356 MG/ML Prefilled Syringe
        "2670390",  # tramadol hydrochloride 25 MG Oral Tablet
        "310293",  # fentanyl 1.2 MG Oral Lozenge
        "310294",  # fentanyl 1.6 MG Oral Lozenge
        "310295",  # fentanyl 0.2 MG Oral Lozenge
        "310297",  # fentanyl 0.4 MG Oral Lozenge
        "312104",  # belladonna alkaloids 16.2 MG / opium 30 MG Rectal Suppository
        "312107",  # belladonna alkaloids 16.2 MG / opium 60 MG Rectal Suppository
        "312289",  # naloxone 0.5 MG / pentazocine 50 MG Oral Tablet
        "313992",  # fentanyl 0.6 MG Oral Lozenge
        "313993",  # fentanyl 0.8 MG Oral Lozenge
        "351264",  # buprenorphine 2 MG Sublingual Tablet
        "351265",  # buprenorphine 8 MG Sublingual Tablet
        "351266",  # buprenorphine 2 MG / naloxone 0.5 MG Sublingual Tablet
        "351267",  # buprenorphine 8 MG / naloxone 2 MG Sublingual Tablet
        "577057",  # 72 HR fentanyl 0.012 MG/HR Transdermal System
        "637540",  # aspirin 325 MG / oxycodone hydrochloride 4.5 MG / oxycodone terephthalate 0.38 MG Oral Tablet
        "668363",  # fentanyl 0.1 MG Buccal Tablet
        "668364",  # fentanyl 0.2 MG Buccal Tablet
        "668365",  # fentanyl 0.4 MG Buccal Tablet
        "668366",  # fentanyl 0.6 MG Buccal Tablet
        "668367",  # fentanyl 0.8 MG Buccal Tablet
        "727759",  # 2 ML fentanyl 0.05 MG/ML Cartridge
        "825409",  # tapentadol 100 MG Oral Tablet
        "825411",  # tapentadol 50 MG Oral Tablet
        "825413",  # tapentadol 75 MG Oral Tablet
        "830196",  # opium tincture 100 MG/ML Oral Solution
        "833709",  # 24 HR tramadol hydrochloride 100 MG Extended Release Oral Tablet
        "833711",  # 24 HR tramadol hydrochloride 200 MG Extended Release Oral Tablet
        "833713",  # 24 HR tramadol hydrochloride 300 MG Extended Release Oral Tablet
        "835603",  # tramadol hydrochloride 50 MG Oral Tablet
        "836395",  # acetaminophen 325 MG / tramadol hydrochloride 37.5 MG Oral Tablet
        "848768",  # aspirin 325 MG / oxycodone hydrochloride 4.84 MG Oral Tablet
        "856940",  # acetaminophen 21.7 MG/ML / hydrocodone bitartrate 0.5 MG/ML Oral Solution
        "856944",  # acetaminophen 21.7 MG/ML / hydrocodone bitartrate 0.67 MG/ML Oral Solution
        "856980",  # acetaminophen 300 MG / hydrocodone bitartrate 10 MG Oral Tablet
        "856987",  # acetaminophen 300 MG / hydrocodone bitartrate 5 MG Oral Tablet
        "856992",  # acetaminophen 300 MG / hydrocodone bitartrate 7.5 MG Oral Tablet
        "856999",  # acetaminophen 325 MG / hydrocodone bitartrate 10 MG Oral Tablet
        "857002",  # acetaminophen 325 MG / hydrocodone bitartrate 5 MG Oral Tablet
        "857005",  # acetaminophen 325 MG / hydrocodone bitartrate 7.5 MG Oral Tablet
        "857099",  # acetaminophen 33.3 MG/ML / hydrocodone bitartrate 0.5 MG/ML Oral Solution
        "857121",  # aspirin 500 MG / hydrocodone bitartrate 5 MG Oral Tablet
        "857131",  # acetaminophen 400 MG / hydrocodone bitartrate 5 MG Oral Tablet
        "857391",  # acetaminophen 325 MG / hydrocodone bitartrate 2.5 MG Oral Tablet
        "857512",  # 12 HR chlorpheniramine polistirex 8 MG / hydrocodone polistirex 10 MG Extended Release Oral Capsule
        "858770",  # hydrocodone bitartrate 2.5 MG / ibuprofen 200 MG Oral Tablet
        "858778",  # hydrocodone bitartrate 5 MG / ibuprofen 200 MG Oral Tablet
        "858798",  # hydrocodone bitartrate 7.5 MG / ibuprofen 200 MG Oral Tablet
        "859315",  # hydrocodone bitartrate 10 MG / ibuprofen 200 MG Oral Tablet
        "859383",  # guaifenesin 40 MG/ML / hydrocodone bitartrate 0.5 MG/ML Oral Solution
        "860792",  # 1 ML meperidine hydrochloride 75 MG/ML Cartridge
        "861455",  # meperidine hydrochloride 100 MG Oral Tablet
        "861463",  # meperidine hydrochloride 50 MG/ML Injectable Solution
        "861467",  # meperidine hydrochloride 50 MG Oral Tablet
        "861473",  # 1 ML meperidine hydrochloride 50 MG/ML Cartridge
        "861476",  # 1 ML meperidine hydrochloride 25 MG/ML Injection
        "861479",  # meperidine hydrochloride 10 MG/ML Oral Solution
        "861493",  # 1 ML meperidine hydrochloride 100 MG/ML Cartridge
        "861494",  # 1 ML meperidine hydrochloride 25 MG/ML Cartridge
        "863845",  # Abuse-Deterrent morphine sulfate 100 MG / naltrexone hydrochloride 4 MG Extended Release Oral Capsule
        "863848",  # Abuse-Deterrent morphine sulfate 20 MG / naltrexone hydrochloride 0.8 MG Extended Release Oral Capsule
        "863850",  # Abuse-Deterrent morphine sulfate 30 MG / naltrexone hydrochloride 1.2 MG Extended Release Oral Capsule
        "863852",  # Abuse-Deterrent morphine sulfate 50 MG / naltrexone hydrochloride 2 MG Extended Release Oral Capsule
        "863854",  # Abuse-Deterrent morphine sulfate 60 MG / naltrexone hydrochloride 2.4 MG Extended Release Oral Capsule
        "863856",  # Abuse-Deterrent morphine sulfate 80 MG / naltrexone hydrochloride 3.2 MG Extended Release Oral Capsule
        "864706",  # methadone hydrochloride 10 MG Oral Tablet
        "864714",  # methadone hydrochloride 10 MG/ML Injectable Solution
        "864718",  # methadone hydrochloride 5 MG Oral Tablet
        "864761",  # methadone hydrochloride 1 MG/ML Oral Solution
        "864769",  # methadone hydrochloride 2 MG/ML Oral Solution
        "864978",  # methadone hydrochloride 40 MG Tablet for Oral Suspension
        "886622",  # butorphanol tartrate 2 MG/ML Injectable Solution
        "886627",  # 1 ML butorphanol tartrate 1 MG/ML Injection
        "886634",  # butorphanol tartrate 1 MG/ACTUAT Metered Dose Nasal Spray
        "891874",  # morphine sulfate 100 MG Extended Release Oral Tablet
        "891881",  # morphine sulfate 15 MG Extended Release Oral Tablet
        "891888",  # morphine sulfate 30 MG Extended Release Oral Tablet
        "891893",  # morphine sulfate 60 MG Extended Release Oral Tablet
        "892297",  # 24 HR morphine sulfate 120 MG Extended Release Oral Capsule
        "892342",  # 24 HR morphine sulfate 30 MG Extended Release Oral Capsule
        "892345",  # morphine sulfate 30 MG Extended Release Oral Capsule
        "892349",  # 24 HR morphine sulfate 60 MG Extended Release Oral Capsule
        "892352",  # morphine sulfate 60 MG Extended Release Oral Capsule
        "892355",  # 24 HR morphine sulfate 90 MG Extended Release Oral Capsule
        "892494",  # morphine sulfate 10 MG Extended Release Oral Capsule
        "892516",  # morphine sulfate 10 MG Rectal Suppository
        "892554",  # morphine sulfate 100 MG Extended Release Oral Capsule
        "892582",  # morphine sulfate 15 MG Oral Tablet
        "892589",  # morphine sulfate 2 MG/ML Oral Solution
        "892596",  # morphine sulfate 20 MG Extended Release Oral Capsule
        "892603",  # morphine sulfate 20 MG Rectal Suppository
        "892625",  # morphine sulfate 20 MG/ML Oral Solution
        "892643",  # morphine sulfate 200 MG Extended Release Oral Capsule
        "892646",  # morphine sulfate 200 MG Extended Release Oral Tablet
        "892672",  # morphine sulfate 30 MG Oral Tablet
        "892678",  # morphine sulfate 30 MG Rectal Suppository
        "894780",  # morphine sulfate 4 MG/ML Oral Solution
        "894801",  # morphine sulfate 50 MG Extended Release Oral Capsule
        "894807",  # morphine sulfate 5 MG Rectal Suppository
        "894814",  # morphine sulfate 80 MG Extended Release Oral Capsule
        "894911",  # 0.7 ML morphine sulfate 14.3 MG/ML Auto-Injector
        "894912",  # 1 ML morphine sulfate 10 MG/ML Prefilled Syringe
        "894914",  # 1 ML morphine sulfate 8 MG/ML Prefilled Syringe
        "894942",  # 24 HR morphine sulfate 45 MG Extended Release Oral Capsule
        "894970",  # 24 HR morphine sulfate 75 MG Extended Release Oral Capsule
        "897653",  # 1 ML hydromorphone hydrochloride 1 MG/ML Injection
        "897657",  # hydromorphone hydrochloride 1 MG/ML Oral Solution
        "897696",  # hydromorphone hydrochloride 2 MG Oral Tablet
        "897702",  # hydromorphone hydrochloride 4 MG Oral Tablet
        "897710",  # hydromorphone hydrochloride 8 MG Oral Tablet
        "897745",  # hydromorphone hydrochloride 2 MG/ML Injectable Solution
        "897749",  # hydromorphone hydrochloride 3 MG Rectal Suppository
        "897753",  # 1 ML hydromorphone hydrochloride 4 MG/ML Injection
        "897756",  # 1 ML hydromorphone hydrochloride 1 MG/ML Prefilled Syringe
        "897757",  # 1 ML hydromorphone hydrochloride 2 MG/ML Prefilled Syringe
        "897758",  # 1 ML hydromorphone hydrochloride 4 MG/ML Cartridge
        "902729",  # 24 HR hydromorphone hydrochloride 12 MG Extended Release Oral Tablet
        "902736",  # 24 HR hydromorphone hydrochloride 16 MG Extended Release Oral Tablet
        "902741",  # 24 HR hydromorphone hydrochloride 8 MG Extended Release Oral Tablet
        "904415",  # nalbuphine hydrochloride 10 MG/ML Injectable Solution
        "904440",  # nalbuphine hydrochloride 20 MG/ML Injectable Solution
        "904870",  # 168 HR buprenorphine 0.01 MG/HR Transdermal System
        "904876",  # 168 HR buprenorphine 0.02 MG/HR Transdermal System
        "904880",  # 168 HR buprenorphine 0.005 MG/HR Transdermal System
        "977874",  # 12 HR oxymorphone hydrochloride 10 MG Extended Release Oral Tablet
        "977894",  # 12 HR oxymorphone hydrochloride 15 MG Extended Release Oral Tablet
        "977902",  # 12 HR oxymorphone hydrochloride 20 MG Extended Release Oral Tablet
        "977909",  # 12 HR oxymorphone hydrochloride 30 MG Extended Release Oral Tablet
        "977915",  # 12 HR oxymorphone hydrochloride 40 MG Extended Release Oral Tablet
        "977923",  # 12 HR oxymorphone hydrochloride 5 MG Extended Release Oral Tablet
        "977929",  # 12 HR oxymorphone hydrochloride 7.5 MG Extended Release Oral Tablet
        "977939",  # oxymorphone hydrochloride 5 MG Oral Tablet
        "977942",  # oxymorphone hydrochloride 10 MG Oral Tablet
        "991147",  # methadone hydrochloride 10 MG/ML Oral Solution
        "991486",  # codeine phosphate 2 MG/ML / promethazine hydrochloride 1.25 MG/ML Oral Solution
        "992656",  # homatropine methylbromide 1.5 MG / hydrocodone bitartrate 5 MG Oral Tablet
        "992668",  # homatropine methylbromide 0.3 MG/ML / hydrocodone bitartrate 1 MG/ML Oral Solution
        "993755",  # acetaminophen 24 MG/ML / codeine phosphate 2.4 MG/ML Oral Solution
        "993770",  # acetaminophen 300 MG / codeine phosphate 15 MG Oral Tablet
        "993781",  # acetaminophen 300 MG / codeine phosphate 30 MG Oral Tablet
        "993890",  # acetaminophen 300 MG / codeine phosphate 60 MG Oral Tablet
        "993943",  # acetaminophen 325 MG / butalbital 50 MG / caffeine 40 MG / codeine phosphate 30 MG Oral Capsule
        "994226",  # aspirin 325 MG / carisoprodol 200 MG / codeine phosphate 16 MG Oral Tablet
        "994237",  # aspirin 325 MG / butalbital 50 MG / caffeine 40 MG / codeine phosphate 30 MG Oral Capsule
        "994289",  # brompheniramine maleate 0.27 MG/ML / codeine phosphate 1.27 MG/ML / pseudoephedrine hydrochloride 2 MG/ML Oral Solution
        "994402",  # brompheniramine maleate 0.4 MG/ML / codeine phosphate 1.5 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
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
        "995226",  # codeine phosphate 0.5 MG/ML / guaifenesin 15 MG/ML Oral Solution
        "995438",  # codeine phosphate 1.26 MG/ML / guaifenesin 20 MG/ML Oral Solution
        "995441",  # codeine phosphate 1.5 MG/ML / guaifenesin 45 MG/ML Oral Solution
        "995450",  # codeine phosphate 10 MG / guaifenesin 300 MG Oral Tablet
        "995483",  # codeine phosphate 2 MG/ML / guaifenesin 40 MG/ML Oral Solution
        "995868",  # codeine phosphate 2 MG/ML / guaifenesin 20 MG/ML Oral Solution
        "995983",  # codeine phosphate 2 MG/ML / guaifenesin 20 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "996580",  # codeine phosphate 2 MG/ML / phenylephrine hydrochloride 1 MG/ML / pyrilamine maleate 1 MG/ML Oral Solution
        "996655",  # codeine phosphate 2 MG/ML / pseudoephedrine hydrochloride 6 MG/ML Oral Solution
        "996706",  # codeine phosphate 20 MG / guaifenesin 400 MG / phenylephrine hydrochloride 10 MG Oral Tablet
        "996710",  # codeine phosphate 20 MG / guaifenesin 400 MG / pseudoephedrine hydrochloride 20 MG Oral Tablet
        "996714",  # codeine phosphate 20 MG / guaifenesin 400 MG / pseudoephedrine hydrochloride 30 MG Oral Tablet
        "996725",  # codeine phosphate 20 MG / guaifenesin 400 MG Oral Tablet
        "996728",  # codeine phosphate 20 MG / pseudoephedrine hydrochloride 60 MG Oral Capsule
        "996736",  # codeine phosphate 9 MG / guaifenesin 200 MG Oral Capsule
        "996757",  # codeine phosphate 2 MG/ML / phenylephrine hydrochloride 1 MG/ML / promethazine hydrochloride 1.25 MG/ML Oral Solution
        "996998",  # brompheniramine maleate 0.266 MG/ML / codeine phosphate 1.27 MG/ML / phenylephrine hydrochloride 0.666 MG/ML Oral Solution
        "997170",  # codeine sulfate 15 MG Oral Tablet
        "997287",  # codeine sulfate 30 MG Oral Tablet
        "997296",  # codeine sulfate 60 MG Oral Tablet
        "998212",  # 1 ML morphine sulfate 2 MG/ML Prefilled Syringe
        "998213",  # 1 ML morphine sulfate 4 MG/ML Prefilled Syringe
    }

class HypoglycemicsTreatmentMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for insulin and non-insulin injectable and oral antidiabetic medications capable of causing hypoglycemia.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes concepts that represent insulin and non-insulin injectable and oral antidiabetic medications.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Hypoglycemics Treatment Medications"
    OID = "2.16.840.1.113762.1.4.1196.394"
    DEFINITION_VERSION = "20250227"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1043563",  # 24 HR metformin hydrochloride 1000 MG / saxagliptin 2.5 MG Extended Release Oral Tablet
        "1043570",  # 24 HR metformin hydrochloride 1000 MG / saxagliptin 5 MG Extended Release Oral Tablet
        "1043578",  # 24 HR metformin hydrochloride 500 MG / saxagliptin 5 MG Extended Release Oral Tablet
        "1100702",  # linagliptin 5 MG Oral Tablet
        "1242963",  # exenatide 2 MG Injection
        "1243020",  # linagliptin 2.5 MG / metformin hydrochloride 1000 MG Oral Tablet
        "1243027",  # linagliptin 2.5 MG / metformin hydrochloride 500 MG Oral Tablet
        "1243034",  # linagliptin 2.5 MG / metformin hydrochloride 850 MG Oral Tablet
        "1243827",  # 24 HR metformin hydrochloride 1000 MG / sitagliptin 100 MG Extended Release Oral Tablet
        "1243842",  # 24 HR metformin hydrochloride 1000 MG / sitagliptin 50 MG Extended Release Oral Tablet
        "1243846",  # 24 HR metformin hydrochloride 500 MG / sitagliptin 50 MG Extended Release Oral Tablet
        "1245262",  # mifepristone 300 MG Oral Tablet
        "1361493",  # glimepiride 6 MG Oral Tablet
        "1361495",  # glimepiride 8 MG Oral Tablet
        "1368006",  # alogliptin 25 MG Oral Tablet
        "1368018",  # alogliptin 6.25 MG Oral Tablet
        "1368034",  # alogliptin 12.5 MG Oral Tablet
        "1368385",  # alogliptin 12.5 MG / metformin hydrochloride 1000 MG Oral Tablet
        "1368392",  # alogliptin 12.5 MG / metformin hydrochloride 500 MG Oral Tablet
        "1368403",  # alogliptin 12.5 MG / pioglitazone 15 MG Oral Tablet
        "1368410",  # alogliptin 12.5 MG / pioglitazone 30 MG Oral Tablet
        "1368417",  # alogliptin 12.5 MG / pioglitazone 45 MG Oral Tablet
        "1368424",  # alogliptin 25 MG / pioglitazone 15 MG Oral Tablet
        "1368431",  # alogliptin 25 MG / pioglitazone 30 MG Oral Tablet
        "1368438",  # alogliptin 25 MG / pioglitazone 45 MG Oral Tablet
        "1373463",  # canagliflozin 100 MG Oral Tablet
        "1373471",  # canagliflozin 300 MG Oral Tablet
        "1488569",  # dapagliflozin 10 MG Oral Tablet
        "1488574",  # dapagliflozin 5 MG Oral Tablet
        "1534800",  # 0.5 ML albiglutide 60 MG/ML Pen Injector
        "1534820",  # 0.5 ML albiglutide 100 MG/ML Pen Injector
        "153842",  # glimepiride 3 MG Oral Tablet
        "1543202",  # insulin, regular, human 4 UNT Inhalation Powder
        "1544488",  # insulin, regular, human 8 UNT Inhalation Powder
        "1545150",  # canagliflozin 150 MG / metformin hydrochloride 1000 MG Oral Tablet
        "1545157",  # canagliflozin 150 MG / metformin hydrochloride 500 MG Oral Tablet
        "1545161",  # canagliflozin 50 MG / metformin hydrochloride 1000 MG Oral Tablet
        "1545164",  # canagliflozin 50 MG / metformin hydrochloride 500 MG Oral Tablet
        "1545658",  # empagliflozin 10 MG Oral Tablet
        "1545666",  # empagliflozin 25 MG Oral Tablet
        "1551295",  # 0.5 ML dulaglutide 1.5 MG/ML Auto-Injector
        "1551304",  # 0.5 ML dulaglutide 3 MG/ML Auto-Injector
        "1593058",  # 24 HR dapagliflozin 10 MG / metformin hydrochloride 1000 MG Extended Release Oral Tablet
        "1593068",  # 24 HR dapagliflozin 10 MG / metformin hydrochloride 500 MG Extended Release Oral Tablet
        "1593070",  # 24 HR dapagliflozin 5 MG / metformin hydrochloride 1000 MG Extended Release Oral Tablet
        "1593072",  # 24 HR dapagliflozin 5 MG / metformin hydrochloride 500 MG Extended Release Oral Tablet
        "1602109",  # empagliflozin 10 MG / linagliptin 5 MG Oral Tablet
        "1602118",  # empagliflozin 25 MG / linagliptin 5 MG Oral Tablet
        "1604539",  # 1.5 ML insulin glargine 300 UNT/ML Pen Injector
        "1652239",  # 3 ML insulin lispro 200 UNT/ML Pen Injector
        "1652639",  # 3 ML insulin lispro 100 UNT/ML Pen Injector
        "1652644",  # 3 ML insulin lispro 100 UNT/ML Cartridge
        "1653196",  # 3 ML insulin aspart, human 100 UNT/ML Cartridge
        "1653202",  # 3 ML insulin aspart, human 100 UNT/ML Pen Injector
        "1654862",  # 3 ML insulin isophane, human 100 UNT/ML Pen Injector
        "1654910",  # insulin, regular, human 12 UNT Inhalation Powder
        "1664315",  # empagliflozin 5 MG / metformin hydrochloride 500 MG Oral Tablet
        "1664323",  # empagliflozin 12.5 MG / metformin hydrochloride 500 MG Oral Tablet
        "1664326",  # empagliflozin 5 MG / metformin hydrochloride 1000 MG Oral Tablet
        "1665367",  # empagliflozin 12.5 MG / metformin hydrochloride 1000 MG Oral Tablet
        "1670011",  # 3 ML insulin degludec 100 UNT/ML Pen Injector
        "1670021",  # 3 ML insulin degludec 200 UNT/ML Pen Injector
        "1731315",  # 3 ML insulin, regular, human 500 UNT/ML Pen Injector
        "1796089",  # 24 HR linagliptin 2.5 MG / metformin hydrochloride 1000 MG Extended Release Oral Tablet
        "1796094",  # 24 HR linagliptin 5 MG / metformin hydrochloride 1000 MG Extended Release Oral Tablet
        "1798387",  # {90 (insulin, regular, human 4 UNT Inhalation Powder) / 90 (insulin, regular, human 8 UNT Inhalation Powder) } Pack
        "1803892",  # 3 ML lixisenatide 0.05 MG/ML Pen Injector
        "1803894",  # 3 ML lixisenatide 0.1 MG/ML Pen Injector
        "1803902",  # {1 (3 ML lixisenatide 0.05 MG/ML Pen Injector) / 1 (3 ML lixisenatide 0.1 MG/ML Pen Injector) } Pack
        "1807888",  # Modified 24 HR metformin hydrochloride 1000 MG Extended Release Oral Tablet
        "1807894",  # Osmotic 24 HR metformin hydrochloride 1000 MG Extended Release Oral Tablet
        "1807915",  # Modified 24 HR metformin hydrochloride 500 MG Extended Release Oral Tablet
        "1807917",  # Osmotic 24 HR metformin hydrochloride 500 MG Extended Release Oral Tablet
        "1810997",  # 24 HR canagliflozin 150 MG / metformin hydrochloride 1000 MG Extended Release Oral Tablet
        "1811002",  # 24 HR canagliflozin 150 MG / metformin hydrochloride 500 MG Extended Release Oral Tablet
        "1811006",  # 24 HR canagliflozin 50 MG / metformin hydrochloride 1000 MG Extended Release Oral Tablet
        "1811010",  # 24 HR canagliflozin 50 MG / metformin hydrochloride 500 MG Extended Release Oral Tablet
        "1858995",  # 3 ML insulin glargine 100 UNT/ML / lixisenatide 0.033 MG/ML Pen Injector
        "1860167",  # 3 ML insulin degludec 100 UNT/ML / liraglutide 3.6 MG/ML Pen Injector
        "1862101",  # {60 (insulin, regular, human 12 UNT Inhalation Powder) / 60 (insulin, regular, human 4 UNT Inhalation Powder) / 60 (insulin, regular, human 8 UNT Inhalation Powder) } Pack
        "1862685",  # 24 HR empagliflozin 10 MG / metformin hydrochloride 1000 MG Extended Release Oral Tablet
        "1862691",  # 24 HR empagliflozin 12.5 MG / metformin hydrochloride 1000 MG Extended Release Oral Tablet
        "1862695",  # 24 HR empagliflozin 25 MG / metformin hydrochloride 1000 MG Extended Release Oral Tablet
        "1862700",  # 24 HR empagliflozin 5 MG / metformin hydrochloride 1000 MG Extended Release Oral Tablet
        "1925498",  # dapagliflozin 10 MG / saxagliptin 5 MG Oral Tablet
        "1926331",  # 0.5 UNT Doses 3 ML insulin lispro 100 UNT/ML Pen Injector
        "1940496",  # 24 HR dapagliflozin 2.5 MG / metformin hydrochloride 1000 MG Extended Release Oral Tablet
        "197411",  # bromocriptine 2.5 MG Oral Tablet
        "197412",  # bromocriptine 5 MG Oral Capsule
        "197495",  # chlorpropamide 100 MG Oral Tablet
        "197496",  # chlorpropamide 250 MG Oral Tablet
        "197737",  # glyburide 1.25 MG Oral Tablet
        "198292",  # tolazamide 250 MG Oral Tablet
        "198293",  # tolazamide 500 MG Oral Tablet
        "1990866",  # 0.85 ML exenatide 2.35 MG/ML Auto-Injector
        "1991306",  # 0.25 MG, 0.5 MG Dose 1.5 ML semaglutide 1.34 MG/ML Pen Injector
        "1991316",  # 1 MG Dose 1.5 ML semaglutide 1.34 MG/ML Pen Injector
        "199149",  # acarbose 50 MG Oral Tablet
        "199150",  # acarbose 100 MG Oral Tablet
        "199245",  # glimepiride 1 MG Oral Tablet
        "199246",  # glimepiride 2 MG Oral Tablet
        "199247",  # glimepiride 4 MG Oral Tablet
        "1992685",  # ertugliflozin 2.5 MG / metformin hydrochloride 1000 MG Oral Tablet
        "1992693",  # ertugliflozin 2.5 MG / metformin hydrochloride 500 MG Oral Tablet
        "1992698",  # ertugliflozin 7.5 MG / metformin hydrochloride 1000 MG Oral Tablet
        "1992701",  # ertugliflozin 7.5 MG / metformin hydrochloride 500 MG Oral Tablet
        "1992810",  # ertugliflozin 5 MG Oral Tablet
        "1992819",  # ertugliflozin 15 MG Oral Tablet
        "1992826",  # ertugliflozin 15 MG / sitagliptin 100 MG Oral Tablet
        "1992835",  # ertugliflozin 5 MG / sitagliptin 100 MG Oral Tablet
        "200132",  # acarbose 25 MG Oral Tablet
        "2002419",  # 3 ML insulin glargine 300 UNT/ML Pen Injector
        "200256",  # repaglinide 1 MG Oral Tablet
        "200257",  # repaglinide 0.5 MG Oral Tablet
        "200258",  # repaglinide 2 MG Oral Tablet
        "205329",  # miglitol 25 MG Oral Tablet
        "205330",  # miglitol 50 MG Oral Tablet
        "205331",  # miglitol 100 MG Oral Tablet
        "2100028",  # {90 (insulin, regular, human 12 UNT Inhalation Powder) / 90 (insulin, regular, human 8 UNT Inhalation Powder) } Pack
        "2107520",  # insulin degludec 100 UNT/ML Injectable Solution
        "2169274",  # dapagliflozin 5 MG / saxagliptin 5 MG Oral Tablet
        "2179744",  # 100 ML insulin, regular, human 1 UNT/ML Injection
        "2200518",  # metformin hydrochloride 100 MG/ML Extended Release Suspension
        "2200644",  # semaglutide 14 MG Oral Tablet
        "2200652",  # semaglutide 3 MG Oral Tablet
        "2200656",  # semaglutide 7 MG Oral Tablet
        "2206090",  # 3 ML insulin, regular, human 100 UNT/ML Pen Injector
        "2268064",  # Sensor 3 ML insulin glargine 100 UNT/ML Pen Injector
        "2359279",  # 24 HR empagliflozin 10 MG / linagliptin 5 MG / metformin hydrochloride 1000 MG Extended Release Oral Tablet
        "2359288",  # 24 HR empagliflozin 12.5 MG / linagliptin 2.5 MG / metformin hydrochloride 1000 MG Extended Release Oral Tablet
        "2359351",  # 24 HR empagliflozin 25 MG / linagliptin 5 MG / metformin hydrochloride 1000 MG Extended Release Oral Tablet
        "2359356",  # 24 HR empagliflozin 5 MG / linagliptin 2.5 MG / metformin hydrochloride 1000 MG Extended Release Oral Tablet
        "2380231",  # insulin lispro-aabc 100 UNT/ML Injectable Solution
        "2380254",  # 3 ML insulin lispro-aabc 200 UNT/ML Pen Injector
        "2380259",  # 3 ML insulin lispro-aabc 100 UNT/ML Pen Injector
        "2380267",  # Sensor 3 ML insulin lispro-aabc 100 UNT/ML Pen Injector
        "2395777",  # 0.5 ML dulaglutide 6 MG/ML Auto-Injector
        "2395783",  # 0.5 ML dulaglutide 9 MG/ML Auto-Injector
        "2398841",  # 3 ML semaglutide 1.34 MG/ML Pen Injector
        "242120",  # insulin lispro 100 UNT/ML Injectable Solution
        "249220",  # insulin, regular, human 500 UNT/ML Injectable Solution
        "2553501",  # 0.5 ML semaglutide 0.5 MG/ML Auto-Injector
        "2553601",  # 0.5 ML semaglutide 1 MG/ML Auto-Injector
        "2553802",  # 0.5 ML semaglutide 2 MG/ML Auto-Injector
        "2553901",  # 0.75 ML semaglutide 2.27 MG/ML Auto-Injector
        "2554102",  # 0.75 ML semaglutide 3.2 MG/ML Auto-Injector
        "2563971",  # 3 ML insulin glargine-yfgn 100 UNT/ML Pen Injector
        "2563976",  # insulin glargine-yfgn 100 UNT/ML Injectable Solution
        "2589008",  # 3 ML insulin glargine-aglr 100 UNT/ML Pen Injector
        "259111",  # insulin lispro 25 UNT/ML / insulin lispro protamine, human 75 UNT/ML Injectable Suspension
        "2599362",  # 3 ML semaglutide 2.68 MG/ML Pen Injector
        "2601743",  # 0.5 ML tirzepatide 10 MG/ML Auto-Injector
        "2601755",  # 0.5 ML tirzepatide 30 MG/ML Auto-Injector
        "2601761",  # 0.5 ML tirzepatide 5 MG/ML Auto-Injector
        "2601767",  # 0.5 ML tirzepatide 20 MG/ML Auto-Injector
        "2601773",  # 0.5 ML tirzepatide 25 MG/ML Auto-Injector
        "2601784",  # 0.5 ML tirzepatide 15 MG/ML Auto-Injector
        "260265",  # insulin lispro 50 UNT/ML / insulin lispro protamine, human 50 UNT/ML Injectable Suspension
        "2619152",  # 0.25 MG, 0.5 MG Dose 3 ML semaglutide 0.68 MG/ML Pen Injector
        "2621571",  # Sensor 3 ML insulin lispro 100 UNT/ML Pen Injector
        "2637859",  # bexagliflozin 20 MG Oral Tablet
        "2638683",  # sotagliflozin 200 MG Oral Tablet
        "2638691",  # sotagliflozin 400 MG Oral Tablet
        "2642808",  # 1.6 ML insulin aspart, human 100 UNT/ML Cartridge
        "2644396",  # 0.5 ML tirzepatide 15 MG/ML Injection
        "2644401",  # 0.5 ML tirzepatide 10 MG/ML Injection
        "2644405",  # 0.5 ML tirzepatide 5 MG/ML Injection
        "2644409",  # 0.5 ML tirzepatide 30 MG/ML Injection
        "2644413",  # 0.5 ML tirzepatide 25 MG/ML Injection
        "2644417",  # 0.5 ML tirzepatide 20 MG/ML Injection
        "2644768",  # {9 (insulin, regular, human 12 UNT Inhalation Powder) / 9 (insulin, regular, human 4 UNT Inhalation Powder) / 9 (insulin, regular, human 8 UNT Inhalation Powder) } Pack
        "310488",  # glipizide 10 MG Oral Tablet
        "310489",  # 24 HR glipizide 2.5 MG Extended Release Oral Tablet
        "310490",  # glipizide 5 MG Oral Tablet
        "310534",  # glyburide 2.5 MG Oral Tablet
        "310536",  # glyburide 3 MG Oral Tablet
        "310537",  # glyburide 5 MG Oral Tablet
        "310539",  # glyburide 6 MG Oral Tablet
        "311028",  # insulin isophane, human 100 UNT/ML Injectable Suspension
        "311034",  # insulin, regular, human 100 UNT/ML Injectable Solution
        "311040",  # insulin aspart, human 100 UNT/ML Injectable Solution
        "311041",  # insulin glargine 100 UNT/ML Injectable Solution
        "311048",  # insulin isophane, human 70 UNT/ML / insulin, regular, human 30 UNT/ML Injectable Suspension
        "311704",  # mifepristone 200 MG Oral Tablet
        "311919",  # nateglinide 120 MG Oral Tablet
        "312440",  # pioglitazone 30 MG Oral Tablet
        "312441",  # pioglitazone 45 MG Oral Tablet
        "312859",  # rosiglitazone 2 MG Oral Tablet
        "314000",  # glyburide 1.5 MG Oral Tablet
        "314006",  # 24 HR glipizide 5 MG Extended Release Oral Tablet
        "314142",  # nateglinide 60 MG Oral Tablet
        "315107",  # 24 HR glipizide 10 MG Extended Release Oral Tablet
        "317573",  # pioglitazone 15 MG Oral Tablet
        "351297",  # insulin aspart protamine, human 70 UNT/ML / insulin aspart, human 30 UNT/ML Injectable Suspension
        "379804",  # glipizide 2.5 MG Oral Tablet
        "484322",  # insulin detemir 100 UNT/ML Injectable Solution
        "485210",  # insulin glulisine, human 100 UNT/ML Injectable Solution
        "647237",  # glimepiride 2 MG / pioglitazone 30 MG Oral Tablet
        "647239",  # glimepiride 4 MG / pioglitazone 30 MG Oral Tablet
        "665033",  # sitagliptin 100 MG Oral Tablet
        "665038",  # sitagliptin 25 MG Oral Tablet
        "665042",  # sitagliptin 50 MG Oral Tablet
        "847187",  # 3 ML insulin isophane, human 70 UNT/ML / insulin, regular, human 30 UNT/ML Pen Injector
        "847191",  # 3 ML insulin aspart protamine, human 70 UNT/ML / insulin aspart, human 30 UNT/ML Pen Injector
        "847211",  # 3 ML insulin lispro 50 UNT/ML / insulin lispro protamine, human 50 UNT/ML Pen Injector
        "847230",  # 3 ML insulin glargine 100 UNT/ML Pen Injector
        "847239",  # 3 ML insulin detemir 100 UNT/ML Pen Injector
        "847252",  # 3 ML insulin lispro 25 UNT/ML / insulin lispro protamine, human 75 UNT/ML Pen Injector
        "847259",  # 3 ML insulin glulisine, human 100 UNT/ML Pen Injector
        "847910",  # 60 ACTUAT exenatide 0.01 MG/ACTUAT Pen Injector
        "847915",  # 60 ACTUAT exenatide 0.005 MG/ACTUAT Pen Injector
        "858036",  # saxagliptin 5 MG Oral Tablet
        "858042",  # saxagliptin 2.5 MG Oral Tablet
        "859077",  # bromocriptine 0.8 MG Oral Tablet
        "860975",  # 24 HR metformin hydrochloride 500 MG Extended Release Oral Tablet
        "860981",  # 24 HR metformin hydrochloride 750 MG Extended Release Oral Tablet
        "861004",  # metformin hydrochloride 1000 MG Oral Tablet
        "861007",  # metformin hydrochloride 500 MG Oral Tablet
        "861010",  # metformin hydrochloride 850 MG Oral Tablet
        "861021",  # metformin hydrochloride 625 MG Oral Tablet
        "861025",  # metformin hydrochloride 100 MG/ML Oral Solution
        "861042",  # 2.7 ML pramlintide acetate 1 MG/ML Pen Injector
        "861044",  # 1.5 ML pramlintide acetate 1 MG/ML Pen Injector
        "861731",  # glipizide 2.5 MG / metformin hydrochloride 250 MG Oral Tablet
        "861736",  # glipizide 2.5 MG / metformin hydrochloride 500 MG Oral Tablet
        "861740",  # glipizide 5 MG / metformin hydrochloride 500 MG Oral Tablet
        "861743",  # glyburide 1.25 MG / metformin hydrochloride 250 MG Oral Tablet
        "861748",  # glyburide 2.5 MG / metformin hydrochloride 500 MG Oral Tablet
        "861753",  # glyburide 5 MG / metformin hydrochloride 500 MG Oral Tablet
        "861760",  # metformin hydrochloride 1000 MG / rosiglitazone 2 MG Oral Tablet
        "861763",  # metformin hydrochloride 1000 MG / rosiglitazone 4 MG Oral Tablet
        "861769",  # metformin hydrochloride 1000 MG / sitagliptin 50 MG Oral Tablet
        "861783",  # metformin hydrochloride 500 MG / pioglitazone 15 MG Oral Tablet
        "861806",  # metformin hydrochloride 500 MG / rosiglitazone 2 MG Oral Tablet
        "861816",  # metformin hydrochloride 500 MG / rosiglitazone 4 MG Oral Tablet
        "861819",  # metformin hydrochloride 500 MG / sitagliptin 50 MG Oral Tablet
        "861822",  # metformin hydrochloride 850 MG / pioglitazone 15 MG Oral Tablet
        "897122",  # 3 ML liraglutide 6 MG/ML Pen Injector
    }

class FibrinolyticTherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for fibrinolytic therapy used in the treatment of ST-segment elevation myocardial infarction (STEMI).

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes RXNORM codes that represent medications used in STEMI treatment.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Fibrinolytic Therapy"
    OID = "2.16.840.1.113883.3.3157.4019"
    DEFINITION_VERSION = "20230218"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1804799",  # alteplase 100 MG Injection
        "1804804",  # alteplase 50 MG Injection
        "313212",  # tenecteplase 50 MG Injection
        "763138",  # reteplase 10 UNT Injection
    }

class OralAnticoagulantMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for oral anticoagulant medications.

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes RXNORM codes that represent medications used to treat blood clots.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Oral Anticoagulant Medications"
    OID = "2.16.840.1.113883.3.3157.4045"
    DEFINITION_VERSION = "20230218"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "1037045",  # dabigatran etexilate 150 MG Oral Capsule
        "1037179",  # dabigatran etexilate 75 MG Oral Capsule
        "1114198",  # rivaroxaban 10 MG Oral Tablet
        "1232082",  # rivaroxaban 15 MG Oral Tablet
        "1232086",  # rivaroxaban 20 MG Oral Tablet
        "1364435",  # apixaban 2.5 MG Oral Tablet
        "1364445",  # apixaban 5 MG Oral Tablet
        "1549682",  # {42 (rivaroxaban 15 MG Oral Tablet) / 9 (rivaroxaban 20 MG Oral Tablet) } Pack
        "1599543",  # edoxaban 15 MG Oral Tablet
        "1599551",  # edoxaban 30 MG Oral Tablet
        "1599555",  # edoxaban 60 MG Oral Tablet
        "1723476",  # dabigatran etexilate 110 MG Oral Capsule
        "1992427",  # {74 (apixaban 5 MG Oral Tablet) } Pack
        "2059015",  # rivaroxaban 2.5 MG Oral Tablet
        "2588062",  # rivaroxaban 1 MG/ML Oral Suspension
        "2590616",  # dabigatran etexilate 110 MG Oral Pellet
        "2590620",  # dabigatran etexilate 150 MG Oral Pellet
        "2590623",  # dabigatran etexilate 20 MG Oral Pellet
        "2590627",  # dabigatran etexilate 30 MG Oral Pellet
        "2590631",  # dabigatran etexilate 40 MG Oral Pellet
        "2590635",  # dabigatran etexilate 50 MG Oral Pellet
        "855288",  # warfarin sodium 1 MG Oral Tablet
        "855296",  # warfarin sodium 10 MG Oral Tablet
        "855302",  # warfarin sodium 2 MG Oral Tablet
        "855312",  # warfarin sodium 2.5 MG Oral Tablet
        "855318",  # warfarin sodium 3 MG Oral Tablet
        "855324",  # warfarin sodium 4 MG Oral Tablet
        "855332",  # warfarin sodium 5 MG Oral Tablet
        "855338",  # warfarin sodium 6 MG Oral Tablet
        "855344",  # warfarin sodium 7.5 MG Oral Tablet
    }

__exports__ = (
    "DementiaMedications",
    "AnticoagulantsForAllIndications",
    "Antidepressants",
    "Antihypertensives",
    "CentralNervousSystemDepressants",
    "Diuretics",
    "Opioids",
    "AntithromboticTherapyForIschemicStroke",
    "PharmacologicalContraindicationsForAntithromboticTherapy",
    "DirectThrombinInhibitor",
    "GlycoproteinIibIiiaInhibitors",
    "InjectableFactorXaInhibitorForVteProphylaxis",
    "LowDoseUnfractionatedHeparinForVteProphylaxis",
    "LowMolecularWeightHeparinForVteProphylaxis",
    "OralFactorXaInhibitorForVteProphylaxisOrVteTreatment",
    "RivaroxabanForVteProphylaxis",
    "UnfractionatedHeparin",
    "Warfarin",
    "AnticoagulantMedications",
    "AntidepressantMedication",
    "AceInhibitorOrArbOrArni",
    "Atomoxetine",
    "Clonidine",
    "Dexmethylphenidate",
    "Dextroamphetamine",
    "GuanfacineMedications",
    "Lisdexamfetamine",
    "Methylphenidate",
    "Viloxazine",
    "SubstanceUseDisorderLongActingMedication",
    "SubstanceUseDisorderShortActingMedication",
    "TobaccoUseCessationPharmacotherapy",
    "BetaBlockerTherapyForLvsd",
    "BetaBlockerTherapy",
    "AntibioticMedicationsForPharyngitis",
    "ContraceptiveMedications",
    "Isotretinoin",
    "AntibioticMedicationsForUpperRespiratoryInfection",
    "DesiccatedThyroidMedications",
    "DigoxinMedications",
    "DipyridamoleMedications",
    "DoxepinMedications",
    "MegestrolMedications",
    "MeperidineMedications",
    "MeprobamateMedications",
    "NifedipineMedications",
    "PotentiallyHarmfulAntidepressantsForOlderAdults",
    "PotentiallyHarmfulAntihistaminesForOlderAdults",
    "PotentiallyHarmfulAntiinfectivesForOlderAdults",
    "PotentiallyHarmfulAntiparkinsonianAgentsForOlderAdults",
    "PotentiallyHarmfulAntipsychoticsForOlderAdults",
    "PotentiallyHarmfulBarbituratesForOlderAdults",
    "PotentiallyHarmfulBenzodiazepinesForOlderAdults",
    "PotentiallyHarmfulEstrogensForOlderAdults",
    "PotentiallyHarmfulGastrointestinalAntispasmodicsForOlderAdults",
    "PotentiallyHarmfulNonbenzodiazepineHypnoticsForOlderAdults",
    "PotentiallyHarmfulPainMedicationsForOlderAdults",
    "PotentiallyHarmfulSkeletalMuscleRelaxantsForOlderAdults",
    "PotentiallyHarmfulSulfonylureasForOlderAdults",
    "PharmacologicTherapyForHypertension",
    "AdolescentDepressionMedications",
    "AdultDepressionMedications",
    "HighIntensityStatinTherapy",
    "LowIntensityStatinTherapy",
    "ModerateIntensityStatinTherapy",
    "MedicationsForOpioidUseDisorderMoud",
    "ScheduleIiIiiAndIvOpioidMedications",
    "ScheduleIvBenzodiazepines",
    "AndrogenDeprivationTherapyForUrologyCare",
    "BacillusCalmetteGuerinForUrologyCare",
    "ChemotherapyAgentsForAdvancedCancer",
    "ImmunosuppressiveDrugsForUrologyCare",
    "MedicationsForAboveNormalBmi",
    "MedicationsForBelowNormalBmi",
    "AnticoagulantTherapy",
    "ThrombolyticTpaTherapy",
    "HypoglycemicsSevereHypoglycemia",
    "OpioidAntagonist",
    "OpioidsAll",
    "HypoglycemicsTreatmentMedications",
    "FibrinolyticTherapy",
    "OralAnticoagulantMedications",
)
