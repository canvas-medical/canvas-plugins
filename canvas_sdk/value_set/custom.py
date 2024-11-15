from canvas_sdk.value_set.v2022.condition import KidneyFailure as v2022KidneyFailure
from canvas_sdk.value_set.value_set import ValueSet


class Hcc005v1AnnualWellnessVisit(ValueSet):
    """Hcc005v1AnnualWellnessVisit."""

    VALUE_SET_NAME = "Annual Wellness Visit"

    HCPCS = {
        "G0438",
        "G0439",
        "G0402",
        "99387",
        "99397",
    }


class DysrhythmiaClassConditionSuspect(ValueSet):
    """Dysrhythmia Class Condition suspect."""

    VALUE_SET_NAME = "Dysrhythmia Class Condition suspect"
    EXPANSION_VERSION = "CanvasHCC Update 2024-11-04"

    ICD10CM = {
        "I420",
        "I421",
        "I422",
        "I423",
        "I424",
        "I425",
        "I426",
        "I427",
        "I428",
        "I429",
        "I470",
        "I471",
        "I4710",
        "I4711",
        "I4719",
        "I472",
        "I4720",
        "I4721",
        "I4729",
        "I479",
        "I480",
        "I481",
        "I4811",
        "I4819",
        "I482",
        "I4820",
        "I4821",
        "I483",
        "I484",
        "I4891",
        "I4892",
        "I4901",
        "I4902",
        "I491",
        "I492",
        "I493",
        "I4940",
        "I4949",
        "I495",
        "I498",
        "I499",
    }


class Antiarrhythmics(ValueSet):
    """Antiarrhythmic medications."""

    VALUE_SET_NAME = "Antiarrhythmics"
    EXPANSION_VERSION = "ClassPath Update 18-10-15"

    FDB = {
        "150358",
        "151807",
        "152779",
        "155773",
        "157601",
        "160121",
        "165621",
        "166591",
        "169107",
        "169508",
        "170461",
        "174429",
        "175363",
        "175494",
        "178251",
        "183239",
        "184929",
        "185830",
        "189377",
        "189730",
        "190878",
        "193821",
        "194412",
        "195187",
        "196380",
        "198310",
        "199400",
        "203114",
        "205183",
        "206598",
        "208686",
        "210260",
        "210732",
        "212898",
        "221901",
        "222092",
        "223459",
        "224332",
        "228864",
        "230155",
        "237183",
        "243776",
        "243776",
        "248491",
        "248829",
        "250272",
        "251530",
        "251766",
        "260972",
        "261266",
        "261929",
        "262594",
        "265464",
        "265785",
        "274471",
        "278255",
        "278255",
        "278255",
        "278255",
        "280333",
        "281153",
        "283306",
        "288964",
        "291187",
        "296991",
        "444249",
        "444249",
        "444944",
        "444944",
        "449494",
        "449496",
        "451558",
        "451559",
        "451560",
        "453457",
        "453462",
        "454178",
        "454180",
        "454181",
        "454205",
        "454206",
        "454207",
        "454371",
        "545231",
        "545231",
        "545232",
        "545233",
        "545238",
        "545239",
        "545239",
        "558741",
        "558745",
        "559416",
        "560050",
        "563304",
        "563305",
        "563306",
        "563310",
        "564459",
        "564460",
        "565068",
        "565069",
        "573523",
        "583982",
        "583982",
        "583985",
        "583985",
        "590326",
        "590375",
        "590376",
        "591479",
        "592349",
        "592421",
        "594710",
        "594714",
    }


class LabReportCreatinine(ValueSet):
    """LabReportCreatinine."""

    VALUE_SET_NAME = "Lab Report Creatinine"
    EXPANSION_VERSION = "CanvasHCC Update 2018-10-04"

    LOINC = {
        "2160-0",
    }


class HypertensiveChronicKidneyDisease(ValueSet):
    """
    **Clinical Focus:** This value set contains concepts that represent hypertensive kidney disease.

    **Data Element Scope:** This value set may use the Quality Data Model (QDM) category related to Diagnosis.

    **Inclusion Criteria:** Includes only relevant concepts associated with hypertensive kidney disease.

    **Exclusion Criteria:** No exclusions.
    """

    OID = "2.16.840.1.113883.3.464.1003.109.12.1017"
    VALUE_SET_NAME = "Hypertensive Chronic Kidney Disease"
    EXPANSION_VERSION = "eCQM Update 2020-05-07"

    ICD10CM = {"I120", "I129", "I130", "I1310", "I1311", "I132", "I150", "I151"}

    ICD9CM = {
        "40301",
        "40310",
        "40311",
        "40390",
        "40391",
        "40400",
        "40401",
        "40402",
        "40403",
        "40410",
        "40411",
        "40412",
        "40413",
        "40490",
        "40491",
        "40492",
        "40493",
    }

    SNOMEDCT = {
        "111438007",
        "123799005",
        "123800009",
        "14973001",
        "193003",
        "194774006",
        "194783001",
        "19769006",
        "23130000",
        "28119000",
        "285831000119108",
        "285841000119104",
        "286371000119107",
        "32916005",
        "38481006",
        "39018007",
        "397748008",
        "427889009",
        "428575007",
        "473392002",
        "49220004",
        "57684003",
        "62240004",
        "65443008",
        "66052004",
        "66610008",
        "73410007",
        "78544004",
        "81363003",
        "86234004",
        "90493000",
    }


class KidneyFailure(v2022KidneyFailure):
    """Added N1830-N1832 per MRHS request."""

    OID = "2.16.840.1.113883.3.464.1003.109.12.1028"
    VALUE_SET_NAME = "Kidney Failure"
    EXPANSION_VERSION = "eCQM Update 2019-05-10 with a few additions"

    ICD10CM = {
        "N170",
        "N171",
        "N172",
        "N178",
        "N179",
        "N181",
        "N182",
        "N183",
        "N184",
        "N185",
        "N186",
        "N189",
        "N19",
        "N1830",
        "N1831",
        "N1832",
    }
