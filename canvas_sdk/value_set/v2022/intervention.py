from canvas_sdk.value_set._utilities import get_overrides

from ..value_set import ValueSet


class PalliativeCareIntervention(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for palliative care interventions.

    **Data Element Scope:** This value set may use a model element related to Intervention.

    **Inclusion Criteria:** Includes concepts that represent palliative care interventions, including procedures and regime/therapy provided as part of palliative care services.

    **Exclusion Criteria:** Excludes concepts that represent an intervention for hospice.

    ** Used in:** CMS134v10, CMS165v10, CMS131v10, CMS122v10, CMS124v10, CMS156v10, CMS125v10, CMS130v10
    """

    VALUE_SET_NAME = "Palliative Care Intervention"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1135"
    DEFINITION_VERSION = "20210224"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "103735009",  # Palliative care (regime/therapy)
        "105402000",  # Visit of patient by chaplain during palliative care (regime/therapy)
        "395669003",  # Specialist palliative care treatment (regime/therapy)
        "395670002",  # Specialist palliative care treatment - inpatient (regime/therapy)
        "395694002",  # Specialist palliative care treatment - daycare (regime/therapy)
        "395695001",  # Specialist palliative care treatment - outpatient (regime/therapy)
        "443761007",  # Anticipatory palliative care (regime/therapy)
        "1841000124106",  # Palliative care medication review (procedure)
        "433181000124107",  # Documentation of palliative care medication action plan (procedure)
    }


class DialysisEducation(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for dialysis education.

    **Data Element Scope:** This value set may use a model element related to Intervention.

    **Inclusion Criteria:** Includes concepts that represent dialysis education.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS134v10
    """

    VALUE_SET_NAME = "Dialysis Education"
    OID = "2.16.840.1.113883.3.464.1003.109.12.1016"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "28812006",  # Hemodialysis education (procedure)
        "59596005",  # Hemodialysis education at home (procedure)
        "66402002",  # Peritoneal dialysis education (procedure)
        "385972005",  # Dialysis care education (procedure)
    }


class OtherServicesRelatedToDialysis(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for services related to dialysis.

    **Data Element Scope:** This value set may use a model element related to Intervention.

    **Inclusion Criteria:** Includes concepts that represent an intervention related to dialysis, including care planning, catheter maintenance and care assessment and management.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS134v10
    """

    VALUE_SET_NAME = "Other Services Related to Dialysis"
    OID = "2.16.840.1.113883.3.464.1003.109.12.1015"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "3257008",  # Empty and measure peritoneal dialysis fluid (procedure)
        "73257006",  # Peritoneal dialysis catheter maintenance (procedure)
        "233591003",  # Hemoperfusion (procedure)
        "385970002",  # Dialysis care assessment (procedure)
        "385971003",  # Dialysis care (regime/therapy)
        "385973000",  # Dialysis care management (procedure)
        "406168002",  # Dialysis access maintenance (regime/therapy)
        "717738008",  # Peritoneal dialysis care assessment (procedure)
        "718019005",  # Hemodialysis care management (procedure)
        "718308002",  # Peritoneal dialysis care (regime/therapy)
        "718330001",  # Hemodialysis care (regime/therapy)
        "718331002",  # Hemodialysis care assessment (procedure)
        "251000124108",  # Dialysis care plan (regime/therapy)
        "311000124103",  # Peritoneal dialysis care plan (regime/therapy)
    }


class AlcoholAndDrugDependenceTreatment(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for alcohol and drug dependence treatment.

    **Data Element Scope:** This value set may use a model element related to Intervention.

    **Inclusion Criteria:** Includes concepts that represent an encounter for alcohol and drug abuse and dependence treatment.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS137v10
    """

    VALUE_SET_NAME = "Alcohol and Drug Dependence Treatment"
    OID = "2.16.840.1.113883.3.464.1003.106.12.1005"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    HCPCSLEVELII = {
        "G2067",  # Medication assisted treatment, methadone; weekly bundle including dispensing and/or administration, substance use counseling, individual and group therapy, and toxicology testing, if performed (provision of the services by a medicare-enrolled opioid treatment program)
        "G2068",  # Medication assisted treatment, buprenorphine (oral); weekly bundle including dispensing and/or administration, substance use counseling, individual and group therapy, and toxicology testing if performed (provision of the services by a medicare-enrolled opioid treatment program)
        "G2069",  # Medication assisted treatment, buprenorphine (injectable); weekly bundle including dispensing and/or administration, substance use counseling, individual and group therapy, and toxicology testing if performed (provision of the services by a medicare-enrolled opioid treatment program)
        "G2070",  # Medication assisted treatment, buprenorphine (implant insertion); weekly bundle including dispensing and/or administration, substance use counseling, individual and group therapy, and toxicology testing if performed (provision of the services by a medicare-enrolled opioid treatment program)
        "G2071",  # Medication assisted treatment, buprenorphine (implant removal); weekly bundle including dispensing and/or administration, substance use counseling, individual and group therapy, and toxicology testing if performed (provision of the services by a medicare-enrolled opioid treatment program)
        "G2072",  # Medication assisted treatment, buprenorphine (implant insertion and removal); weekly bundle including dispensing and/or administration, substance use counseling, individual and group therapy, and toxicology testing if performed (provision of the services by a medicare-enrolled opioid treatment program)
        "G2073",  # Medication assisted treatment, naltrexone; weekly bundle including dispensing and/or administration, substance use counseling, individual and group therapy, and toxicology testing if performed (provision of the services by a medicare-enrolled opioid treatment program)
        "G2074",  # Medication assisted treatment, weekly bundle not including the drug, including substance use counseling, individual and group therapy, and toxicology testing if performed (provision of the services by a medicare-enrolled opioid treatment program)
        "G2075",  # Medication assisted treatment, medication not otherwise specified; weekly bundle including dispensing and/or administration, substance use counseling, individual and group therapy, and toxicology testing, if performed (provision of the services by a medicare-enrolled opioid treatment program)
        "G2076",  # Intake activities, including initial medical examination that is a complete, fully documented physical evaluation and initial assessment by a program physician or a primary care physician, or an authorized healthcare professional under the supervision of a program physician qualified personnel that includes preparation of a treatment plan that includes the patient's short-term goals and the tasks the patient must perform to complete the short-term goals; the patient's requirements for education, vocational rehabilitation, and employment; and the medical, psycho- social, economic, legal, or other supportive services that a patient needs, conducted by qualified personnel (provision of the services by a medicare-enrolled opioid treatment program); list separately in addition to code for primary procedure
        "G2077",  # Periodic assessment; assessing periodically by qualified personnel to determine the most appropriate combination of services and treatment (provision of the services by a medicare-enrolled opioid treatment program); list separately in addition to code for primary procedure
        "G2080",  # Each additional 30 minutes of counseling in a week of medication assisted treatment, (provision of the services by a medicare-enrolled opioid treatment program); list separately in addition to code for primary procedure
        "G2086",  # Office-based treatment for opioid use disorder, including development of the treatment plan, care coordination, individual therapy and group therapy and counseling; at least 70 minutes in the first calendar month
        "G2087",  # Office-based treatment for opioid use disorder, including care coordination, individual therapy and group therapy and counseling; at least 60 minutes in a subsequent calendar month
        "H0020",  # Alcohol and/or drug services; methadone administration and/or service (provision of the drug by a licensed program)
        "H0033",  # Oral medication administration, direct observation
    }
    SNOMEDCT = {
        "20093000",  # Alcohol rehabilitation and detoxification (regime/therapy)
        "23915005",  # Combined alcohol and drug rehabilitation and detoxification (regime/therapy)
        "24165007",  # Alcoholism counseling (procedure)
        "56876005",  # Drug rehabilitation and detoxification (regime/therapy)
        "60112009",  # Drug addiction counseling (procedure)
        "171047005",  # Drugs of addiction education (procedure)
        "266707007",  # Drug addiction therapy (regime/therapy)
        "310653000",  # Drug addiction therapy using methadone (regime/therapy)
        "313071005",  # Counseling for substance abuse (procedure)
        "370881007",  # Abuse prevention assessment (procedure)
        "370884004",  # Abuse prevention management (procedure)
        "385989002",  # Substance use therapy (regime/therapy)
        "386448003",  # Substance use prevention (procedure)
        "386449006",  # Substance use treatment: alcohol withdrawal (regime/therapy)
        "386450006",  # Substance use treatment: drug withdrawal (regime/therapy)
        "386451005",  # Substance use treatment: overdose (regime/therapy)
        "408933008",  # Substance abuse prevention (procedure)
        "408934002",  # Substance abuse prevention assessment (procedure)
        "408935001",  # Substance abuse prevention education (procedure)
        "408936000",  # Substance abuse prevention management (procedure)
        "408941008",  # Drug abuse prevention (procedure)
        "408942001",  # Drug abuse prevention assessment (procedure)
        "408943006",  # Drug abuse prevention education (procedure)
        "408944000",  # Drug abuse prevention management (procedure)
        "408945004",  # Alcohol abuse prevention (procedure)
        "408947007",  # Alcohol abuse prevention education (procedure)
        "408948002",  # Alcohol abuse prevention management (procedure)
        "410419007",  # Substance use surveillance (regime/therapy)
        "413473000",  # Counseling about alcohol consumption (procedure)
        "423416000",  # Substance use cessation case management (procedure)
        "424148004",  # Substance use cessation surveillance (regime/therapy)
        "424407005",  # Substance use cessation education, guidance, and counseling (procedure)
        "424589009",  # Substance use treatment: cessation (regime/therapy)
        "426928008",  # Prevention of opioid abuse (procedure)
        "707166002",  # Alcohol reduction program (regime/therapy)
        "720174008",  # Drug harm reduction program (regime/therapy)
        "720175009",  # Alcohol harm reduction program (regime/therapy)
        "720176005",  # Alcohol relapse prevention program (regime/therapy)
        "720177001",  # Drug relapse prevention program (regime/therapy)
        "737363002",  # Alcohol abuse surveillance (regime/therapy)
        "792901003",  # Drug addiction therapy using buprenorphine (regime/therapy)
        "792902005",  # Drug addiction therapy using buprenorphine and naloxone (regime/therapy)
        "429291000124102",  # Alcohol brief intervention (procedure)
    }


class PsychVisitPsychotherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for encounters for psychotherapy visits.

    **Data Element Scope:** This value set may use a model element related to Encounter.

    **Inclusion Criteria:** Includes concepts that represent an encounter for individual psychotherapy services.

    **Exclusion Criteria:** Excludes concepts that represent an encounter for group psychotherapy or family psychotherapy visits.

    ** Used in:** CMS137v10
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


class TobaccoUseCessationCounseling(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for tobacco cessation counseling.

    **Data Element Scope:** This value set may use a model element related to Intervention.

    **Inclusion Criteria:** Includes concepts that represent an intervention that may include referral to tobacco cessation-related services or providers, education about the benefits of stopping tobacco use, education about the negative side effects of using tobacco, and monitoring for tobacco cessation.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS138v10
    """

    VALUE_SET_NAME = "Tobacco Use Cessation Counseling"
    OID = "2.16.840.1.113883.3.526.3.509"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "99406",  # Smoking and tobacco use cessation counseling visit; intermediate, greater than 3 minutes up to 10 minutes
        "99407",  # Smoking and tobacco use cessation counseling visit; intensive, greater than 10 minutes
    }
    SNOMEDCT = {
        "171055003",  # Pregnancy smoking education (procedure)
        "185795007",  # Stop smoking monitoring verbal invite (procedure)
        "185796008",  # Stop smoking monitoring telephone invite (procedure)
        "225323000",  # Smoking cessation education (procedure)
        "225324006",  # Smoking effects education (procedure)
        "310429001",  # Smoking monitoring invitation (procedure)
        "315232003",  # Referral to stop-smoking clinic (procedure)
        "384742004",  # Smoking cessation assistance (regime/therapy)
        "395700008",  # Referral to smoking cessation advisor (procedure)
        "702388001",  # Tobacco use cessation education (procedure)
        "710081004",  # Smoking cessation therapy (regime/therapy)
        "711028002",  # Counseling about tobacco use (procedure)
        "713700008",  # Smoking cessation drug therapy (regime/therapy)
        "449841000124108",  # Referral to tobacco use cessation clinic (procedure)
        "449851000124105",  # Referral to tobacco use cessation counselor (procedure)
        "449861000124107",  # Referral to tobacco use cessation counseling program (procedure)
        "449871000124100",  # Referral to tobacco use quit line (procedure)
    }


class CognitiveAssessment(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for assessments performed for the evaluation of cognition.

    **Data Element Scope:** This value set may use a model element related to Intervention.

    **Inclusion Criteria:** Includes concepts that describe assessments for evaluation of cognition.

    **Exclusion Criteria:** Excludes concepts that identify specific standardized tools used to evaluate cognition.

    ** Used in:** CMS149v10
    """

    VALUE_SET_NAME = "Cognitive Assessment"
    OID = "2.16.840.1.113883.3.526.3.1332"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "4719001",  # Psychologic cognitive testing and assessment (procedure)
        "113024001",  # Assessment and interpretation of higher cerebral function, cognitive testing (procedure)
    }


class CounselingForNutrition(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for nutrition counseling interventions.

    **Data Element Scope:** This value set may use a model element related to Intervention.

    **Inclusion Criteria:** Includes concepts that represent counseling for nutrition, including medical nutrition therapy, dietetic services, diet education, and weight loss management.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS155v10
    """

    VALUE_SET_NAME = "Counseling for Nutrition"
    OID = "2.16.840.1.113883.3.464.1003.195.12.1003"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "97802",  # Medical nutrition therapy; initial assessment and intervention, individual, face-to-face with the patient, each 15 minutes
        "97803",  # Medical nutrition therapy; re-assessment and intervention, individual, face-to-face with the patient, each 15 minutes
        "97804",  # Medical nutrition therapy; group (2 or more individual(s)), each 30 minutes
    }
    SNOMEDCT = {
        "11816003",  # Diet education (procedure)
        "61310001",  # Nutrition education (procedure)
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
        "429095004",  # Dietary education for weight gain (procedure)
        "431482008",  # Dietary education for competitive athlete (procedure)
        "443288003",  # Lifestyle education regarding diet (procedure)
        "609104008",  # Educated about weight management (situation)
        "698471002",  # Patient advised about weight management (situation)
        "699827002",  # Dietary education about fluid restriction (procedure)
        "699829004",  # High energy diet education (procedure)
        "699830009",  # Food fortification education (procedure)
        "699849008",  # Healthy eating education (procedure)
        "700154005",  # Seen in weight management clinic (finding)
        "700258004",  # Dietary education about vitamin intake (procedure)
        "705060005",  # Diet education about mineral intake (procedure)
        "710881000",  # Education about eating pattern (procedure)
        "428461000124101",  # Referral to nutrition professional (procedure)
        "428691000124107",  # Vitamin K dietary intake education (procedure)
        "441041000124100",  # Counseling about nutrition (procedure)
        "441201000124108",  # Counseling about nutrition using cognitive-behavioral theoretical approach (procedure)
        "441231000124100",  # Counseling about nutrition using health belief model (procedure)
        "441241000124105",  # Counseling about nutrition using social learning theory approach (procedure)
        "441251000124107",  # Counseling about nutrition using transtheoretical model and stages of change approach (procedure)
        "441261000124109",  # Counseling about nutrition using motivational interviewing strategy (procedure)
        "441271000124102",  # Counseling about nutrition using goal setting strategy (procedure)
        "441281000124104",  # Counseling about nutrition using self-monitoring strategy (procedure)
        "441291000124101",  # Counseling about nutrition using problem solving strategy (procedure)
        "441301000124100",  # Counseling about nutrition using social support strategy (procedure)
        "441311000124102",  # Counseling about nutrition using stress management strategy (procedure)
        "441321000124105",  # Counseling about nutrition using stimulus control strategy (procedure)
        "441331000124108",  # Counseling about nutrition using cognitive restructuring strategy (procedure)
        "441341000124103",  # Counseling about nutrition using relapse prevention strategy (procedure)
        "441351000124101",  # Counseling about nutrition using rewards and contingency management strategy (procedure)
        "445291000124103",  # Nutrition-related skills education (procedure)
        "445301000124102",  # Content-related nutrition education (procedure)
        "445331000124105",  # Nutrition-related laboratory result interpretation education (procedure)
        "445641000124105",  # Technical nutrition education (procedure)
    }


class CounselingForPhysicalActivity(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for physical activity counseling.

    **Data Element Scope:** This value set may use a model element related to Intervention.

    **Inclusion Criteria:** Includes concepts that represent counseling or referrals for physical activity, including weight management services.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS155v10
    """

    VALUE_SET_NAME = "Counseling for Physical Activity"
    OID = "2.16.840.1.113883.3.464.1003.118.12.1035"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "103736005",  # History and physical examination, sports participation (procedure)
        "183073003",  # Patient advised about exercise (situation)
        "281090004",  # Recommendation to exercise (procedure)
        "304507003",  # Exercise education (procedure)
        "304549008",  # Giving encouragement to exercise (procedure)
        "304558001",  # Reassuring about exercise (procedure)
        "310882002",  # Exercise on prescription (regime/therapy)
        "386291006",  # Exercise promotion: strength training (procedure)
        "386292004",  # Exercise promotion: stretching (procedure)
        "386463000",  # Prescribed activity/exercise education (procedure)
        "390864007",  # Referral for exercise therapy (procedure)
        "390893007",  # Referral to physical activity program (procedure)
        "398636004",  # Physical activity assessment (procedure)
        "398752005",  # Referral to weight maintenance regimen service (procedure)
        "408289007",  # Refer to weight management program (procedure)
        "410200000",  # Weight control education (procedure)
        "410289001",  # Exercises education, guidance, and counseling (procedure)
        "410335001",  # Exercises case management (procedure)
        "429778002",  # Patient given written advice on benefits of physical activity (situation)
        "710849009",  # Assessment of exercise behavior (procedure)
        "435551000124105",  # Counseling about physical activity (procedure)
    }


class PalliativeOrHospiceCare(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of an intervention or procedure to identify patients receiving palliative, comfort or hospice care.

    **Data Element Scope:** This value set may use a model element related to Intervention or Procedure.

    **Inclusion Criteria:** Includes concepts that identify an intervention or procedure for palliative, comfort or hospice care.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS347v5, CMS159v10, CMS69v10
    """

    VALUE_SET_NAME = "Palliative or Hospice Care"
    OID = "2.16.840.1.113883.3.600.1.1579"
    DEFINITION_VERSION = "20210224"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "103735009",  # Palliative care (regime/therapy)
        "133918004",  # Comfort measures (regime/therapy)
        "182964004",  # Terminal care (regime/therapy)
        "305284002",  # Admission by palliative care physician (procedure)
        "305381007",  # Admission to palliative care department (procedure)
        "305981001",  # Referral by palliative care physician (procedure)
        "306237005",  # Referral to palliative care service (procedure)
        "306288008",  # Referral to palliative care physician (procedure)
        "385736008",  # Dying care (regime/therapy)
        "385763009",  # Hospice care (regime/therapy)
    }


class DietaryRecommendations(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for recommendations and education for diet and nutrition.

    **Data Element Scope:** This value set may use a model element related to Intervention or Procedure.

    **Inclusion Criteria:** This value set may use a model element related to Intervention or Procedure.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS22v10
    """

    VALUE_SET_NAME = "Dietary Recommendations"
    OID = "2.16.840.1.113883.3.600.1515"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    HCPCSLEVELII = {
        "S9452",  # Nutrition classes, non-physician provider, per session
        "S9470",  # Nutritional counseling, dietitian visit
    }
    ICD10CM = {
        "Z713",  # Dietary counseling and surveillance
    }
    SNOMEDCT = {
        "11816003",  # Diet education (procedure)
        "61310001",  # Nutrition education (procedure)
        "103699006",  # Patient referral to dietitian (procedure)
        "182922004",  # Dietary regime (regime/therapy)
        "182954008",  # Dietary prophylaxis (regime/therapy)
        "182955009",  # Low carbohydrate diet - prophylaxis (regime/therapy)
        "182956005",  # Low calorie diet - prophylaxis (regime/therapy)
        "182960008",  # Unsaturated fat diet - prophylaxis (regime/therapy)
        "183061003",  # Low fat diet education (procedure)
        "183065007",  # Low carbohydrate diet education (procedure)
        "183070000",  # Vegetarian diet education (procedure)
        "183071001",  # Vegan diet education (procedure)
        "281085002",  # Sugar-free diet education (procedure)
        "284071006",  # Dietary treatment for disorder (regime/therapy)
        "284352003",  # Obesity diet education (procedure)
        "285383009",  # Recommendation to change fruit and nut intake (procedure)
        "289176001",  # Recommendation to change sodium intake (procedure)
        "304491008",  # Dietary education for disorder (procedure)
        "306163007",  # Referral to dietetics service (procedure)
        "361231003",  # Prescribed dietary intake (regime/therapy)
        "370847001",  # Dietary needs education (procedure)
        "386464006",  # Prescribed diet education (procedure)
        "410114009",  # Dietary compliance education (procedure)
        "410171007",  # Nutrition care education (procedure)
        "410177006",  # Special diet education (procedure)
        "410270001",  # Nutritionist education, guidance, and counseling (procedure)
        "413315001",  # Nutrition / feeding management (regime/therapy)
        "418995006",  # Feeding regime (regime/therapy)
        "424753004",  # Dietary management education, guidance, and counseling (procedure)
        "443288003",  # Lifestyle education regarding diet (procedure)
        "699849008",  # Healthy eating education (procedure)
        "715282001",  # Combined healthy eating and physical education program (regime/therapy)
        "770749002",  # Referral for combined healthy eating and physical education program (procedure)
        "1151000175103",  # Dietary Approaches to Stop Hypertension diet (regime/therapy)
        "435771000124106",  # General healthful diet (regime/therapy)
        "437231000124109",  # Sodium modified diet (regime/therapy)
        "437421000124105",  # Decreased sodium diet (regime/therapy)
    }


class FollowUpWithin4Weeks(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for follow-up timing.

    **Data Element Scope:** This value set may use a model element related to Intervention.

    **Inclusion Criteria:** Includes concepts that represent follow-up timing from one day to one month.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS22v10
    """

    VALUE_SET_NAME = "Follow Up Within 4 Weeks"
    OID = "2.16.840.1.113883.3.526.3.1578"
    DEFINITION_VERSION = "20200307"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "183617005",  # Follow-up 1 day (finding)
        "183618000",  # Follow-up 2-3 days (finding)
        "183619008",  # Follow-up 4-6 days (finding)
        "183620002",  # Follow-up 1 week (finding)
        "183621003",  # Follow-up 2 weeks (finding)
        "183622005",  # Follow-up 3 weeks (finding)
        "183623000",  # Follow-up 1 month (finding)
    }


class LifestyleRecommendation(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for  lifestyle needs and education related to hypertension.

    **Data Element Scope:** This value set may use a model element related to Procedure or Intervention.

    **Inclusion Criteria:** Includes concepts that represent a procedure or intervention for lifestyle education focused on hypertension.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS22v10
    """

    VALUE_SET_NAME = "Lifestyle Recommendation"
    OID = "2.16.840.1.113883.3.526.3.1581"
    DEFINITION_VERSION = "20200307"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "39155009",  # Hypertension education (procedure)
        "313204009",  # Lifestyle education (procedure)
        "443402002",  # Lifestyle education regarding hypertension (procedure)
    }


class RecommendationToIncreasePhysicalActivity(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for recommendations for exercise and nutrition education.

    **Data Element Scope:** This value set may use a model element related to Intervention or Procedure.

    **Inclusion Criteria:** Includes concepts that represent an intervention or procedure for promoting exercise and nutrition regimens.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS22v10
    """

    VALUE_SET_NAME = "Recommendation to Increase Physical Activity"
    OID = "2.16.840.1.113883.3.600.1518"
    DEFINITION_VERSION = "20190313"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    HCPCSLEVELII = {
        "S9451",  # Exercise classes, non-physician provider, per session
    }
    SNOMEDCT = {
        "281090004",  # Recommendation to exercise (procedure)
        "304507003",  # Exercise education (procedure)
        "304549008",  # Giving encouragement to exercise (procedure)
        "386291006",  # Exercise promotion: strength training (procedure)
        "386292004",  # Exercise promotion: stretching (procedure)
        "386373004",  # Nutrition therapy (regime/therapy)
        "386463000",  # Prescribed activity/exercise education (procedure)
        "410289001",  # Exercises education, guidance, and counseling (procedure)
    }


class ReferralOrCounselingForAlcoholConsumption(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for interventions relevant to alcohol use.

    **Data Element Scope:** This value set may use a model element related to Procedure or Intervention.

    **Inclusion Criteria:** Includes concepts that indicate an intervention for the type of education provided, referral to community service, or rehabilitation center for alcohol use.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS22v10
    """

    VALUE_SET_NAME = "Referral or Counseling for Alcohol Consumption"
    OID = "2.16.840.1.113883.3.526.3.1583"
    DEFINITION_VERSION = "20200307"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "24165007",  # Alcoholism counseling (procedure)
        "38670004",  # Referral to alcoholism rehabilitation service (procedure)
        "390857005",  # Referral to community alcohol team (procedure)
        "408947007",  # Alcohol abuse prevention education (procedure)
        "413473000",  # Counseling about alcohol consumption (procedure)
        "417096006",  # Referral to community drug and alcohol team (procedure)
        "431260004",  # Referral to specialist alcohol treatment service (procedure)
    }


class ReferralToPrimaryCareOrAlternateProvider(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for referrals to an alternate or primary care provider.

    **Data Element Scope:** This value set may use a model element related to Intervention.

    **Inclusion Criteria:** Includes concepts that describe an intervention of a referral to an alternate or primary care provider.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS22v10
    """

    VALUE_SET_NAME = "Referral to Primary Care or Alternate Provider"
    OID = "2.16.840.1.113883.3.526.3.1580"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "134403003",  # Urgent referral (procedure)
        "183516009",  # Referral to general medical service (procedure)
        "183561008",  # Referral to general practitioner (procedure)
        "183856001",  # Referral to hypertension clinic (procedure)
        "306206005",  # Referral to service (procedure)
        "306253008",  # Referral to doctor (procedure)
        "306362008",  # Referral to pharmacist (procedure)
        "308470006",  # Referral to general physician (procedure)
        "453641000124107",  # Referral to specialist pharmacist (procedure)
    }


class WeightReductionRecommended(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for discussion, education and  management of weight reduction.

    **Data Element Scope:** This value set may use a model element related to Intervention or Procedure.

    **Inclusion Criteria:** Includes concepts that represent discussion, education and  management of weight reduction.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS22v10
    """

    VALUE_SET_NAME = "Weight Reduction Recommended"
    OID = "2.16.840.1.113883.3.600.1510"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    HCPCSLEVELII = {
        "S9449",  # Weight management classes, non-physician provider, per session
    }
    SNOMEDCT = {
        "170795002",  # Follow-up obesity assessment (regime/therapy)
        "266724001",  # Weight-reducing diet education (procedure)
        "268523001",  # Target weight discussed (regime/therapy)
        "284352003",  # Obesity diet education (procedure)
        "388975008",  # Weight reduction consultation (procedure)
        "398752005",  # Referral to weight maintenance regimen service (procedure)
        "408289007",  # Refer to weight management program (procedure)
        "410200000",  # Weight control education (procedure)
        "410201001",  # Weight maintenance regimen management (procedure)
        "445033007",  # Discussion about ideal body weight (procedure)
        "1181000175107",  # Recommendation to lose weight (procedure)
    }


class FollowUpForAdolescentDepression(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for follow-up plans used to document a plan is in place for the treatment of depression that specifically pertains to the adolescent population.

    **Data Element Scope:** This value set may use a model element related to Intervention.

    **Inclusion Criteria:** Includes concepts that represent emotional and coping support as well as mental health management in an attempt to follow up on previously evaluated and diagnosed depression or depressive disorder in adolescents.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS2v11
    """

    VALUE_SET_NAME = "Follow Up for Adolescent Depression"
    OID = "2.16.840.1.113883.3.526.3.1569"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "1555005",  # Brief group psychotherapy (regime/therapy)
        "5694008",  # Crisis intervention with follow-up (regime/therapy)
        "15558000",  # Expressive psychotherapy (regime/therapy)
        "18512000",  # Individual psychotherapy (regime/therapy)
        "28868002",  # Interactive group medical psychotherapy (regime/therapy)
        "75516001",  # Psychotherapy (regime/therapy)
        "76168009",  # Group psychotherapy (regime/therapy)
        "76740001",  # Psychiatric telephone consultation or therapy with patient (procedure)
        "81294000",  # Patient referral for psychotherapy (procedure)
        "88848003",  # Psychiatric follow-up (procedure)
        "91310009",  # Patient follow-up to return when and if necessary (procedure)
        "108313002",  # Family psychotherapy procedure (regime/therapy)
        "228557008",  # Cognitive and behavioral therapy (regime/therapy)
        "229065009",  # Exercise therapy (regime/therapy)
        "372067001",  # Implementation of measures to provide psychological support (regime/therapy)
        "385721005",  # Coping support assessment (procedure)
        "385724002",  # Coping support management (procedure)
        "385725001",  # Emotional support assessment (procedure)
        "385726000",  # Emotional support education (procedure)
        "385727009",  # Emotional support management (procedure)
        "385887004",  # Mental health history taking assessment (procedure)
        "385889001",  # Mental health history taking education (procedure)
        "385890005",  # Mental health history taking management (procedure)
        "386472008",  # Telephone consultation (procedure)
        "401277000",  # Completion of mental health crisis plan (procedure)
        "405780009",  # Dialectical behavior therapy (regime/therapy)
        "410223002",  # Mental health care assessment (procedure)
        "410224008",  # Mental health care education (procedure)
        "410225009",  # Mental health care management (procedure)
        "410226005",  # Mental health promotion assessment (procedure)
        "410227001",  # Mental health promotion education (procedure)
        "410228006",  # Mental health promotion management (procedure)
        "410229003",  # Mental health screening assessment (procedure)
        "410230008",  # Mental health screening education (procedure)
        "410231007",  # Mental health screening management (procedure)
        "410232000",  # Mental health treatment assessment (procedure)
        "410233005",  # Mental health treatment education (procedure)
        "410234004",  # Management of mental health treatment (procedure)
        "425604002",  # Case management follow up (procedure)
        "439141002",  # Discharge by mental health primary care worker (procedure)
    }


class FollowUpForAdultDepression(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for follow-up plans used to document a plan is in place for the treatment of depression specifically pertaining to the adult population.

    **Data Element Scope:** This value set may use a model element related to Intervention.

    **Inclusion Criteria:** Includes concepts that represent emotional and coping support as well as mental health management in an attempt to follow up on previously evaluated and diagnosed depression or depressive disorder in the adults.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS2v11
    """

    VALUE_SET_NAME = "Follow Up for Adult Depression"
    OID = "2.16.840.1.113883.3.526.3.1568"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "1555005",  # Brief group psychotherapy (regime/therapy)
        "5694008",  # Crisis intervention with follow-up (regime/therapy)
        "15558000",  # Expressive psychotherapy (regime/therapy)
        "18512000",  # Individual psychotherapy (regime/therapy)
        "28868002",  # Interactive group medical psychotherapy (regime/therapy)
        "75516001",  # Psychotherapy (regime/therapy)
        "76168009",  # Group psychotherapy (regime/therapy)
        "76740001",  # Psychiatric telephone consultation or therapy with patient (procedure)
        "81294000",  # Patient referral for psychotherapy (procedure)
        "88848003",  # Psychiatric follow-up (procedure)
        "91310009",  # Patient follow-up to return when and if necessary (procedure)
        "108313002",  # Family psychotherapy procedure (regime/therapy)
        "228557008",  # Cognitive and behavioral therapy (regime/therapy)
        "229065009",  # Exercise therapy (regime/therapy)
        "372067001",  # Implementation of measures to provide psychological support (regime/therapy)
        "385721005",  # Coping support assessment (procedure)
        "385724002",  # Coping support management (procedure)
        "385725001",  # Emotional support assessment (procedure)
        "385726000",  # Emotional support education (procedure)
        "385727009",  # Emotional support management (procedure)
        "385887004",  # Mental health history taking assessment (procedure)
        "385889001",  # Mental health history taking education (procedure)
        "385890005",  # Mental health history taking management (procedure)
        "386472008",  # Telephone consultation (procedure)
        "401277000",  # Completion of mental health crisis plan (procedure)
        "405780009",  # Dialectical behavior therapy (regime/therapy)
        "410223002",  # Mental health care assessment (procedure)
        "410224008",  # Mental health care education (procedure)
        "410225009",  # Mental health care management (procedure)
        "410226005",  # Mental health promotion assessment (procedure)
        "410227001",  # Mental health promotion education (procedure)
        "410228006",  # Mental health promotion management (procedure)
        "410229003",  # Mental health screening assessment (procedure)
        "410230008",  # Mental health screening education (procedure)
        "410231007",  # Mental health screening management (procedure)
        "410232000",  # Mental health treatment assessment (procedure)
        "410233005",  # Mental health treatment education (procedure)
        "410234004",  # Management of mental health treatment (procedure)
        "425604002",  # Case management follow up (procedure)
        "439141002",  # Discharge by mental health primary care worker (procedure)
    }


class ReferralForAdolescentDepression(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for referrals for depression management for the child and adolescent population.

    **Data Element Scope:** This value set may use a model element related to Intervention.

    **Inclusion Criteria:** Includes concepts that represent referrals for depression management in the child and adolescent population.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS2v11
    """

    VALUE_SET_NAME = "Referral for Adolescent Depression"
    OID = "2.16.840.1.113883.3.526.3.1570"
    DEFINITION_VERSION = "20200307"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "183524004",  # Referral to psychiatry service (procedure)
        "183583007",  # Refer to mental health worker (procedure)
        "183851006",  # Referral to clinic (procedure)
        "183866009",  # Referral to emergency clinic (procedure)
        "306136006",  # Referral to liaison psychiatry service (procedure)
        "306137002",  # Referral to mental handicap psychiatry service (procedure)
        "306226009",  # Referral to mental health counseling service (procedure)
        "306227000",  # Referral for mental health counseling (procedure)
        "306252003",  # Referral to mental health counselor (procedure)
        "306291008",  # Referral to child and adolescent psychiatrist (procedure)
        "306294000",  # Referral to psychiatrist for mental handicap (procedure)
        "308459004",  # Referral to psychologist (procedure)
        "308477009",  # Referral to psychiatrist (procedure)
        "309627007",  # Child referral - clinical psychologist (procedure)
        "390866009",  # Referral to mental health team (procedure)
        "703978000",  # Referral to primary care service (procedure)
        "710914003",  # Referral to family therapy (procedure)
        "711281004",  # Referral to support group (procedure)
    }


class ReferralForAdultDepression(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for referrals for depression management for the adult population.

    **Data Element Scope:** This value set may use a model element related to Intervention.

    **Inclusion Criteria:** Includes concepts that represent referrals for depression management in the adult population.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS2v11
    """

    VALUE_SET_NAME = "Referral for Adult Depression"
    OID = "2.16.840.1.113883.3.526.3.1571"
    DEFINITION_VERSION = "20200307"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "183524004",  # Referral to psychiatry service (procedure)
        "183528001",  # Referral to psychiatrist for the elderly mentally ill (procedure)
        "183583007",  # Refer to mental health worker (procedure)
        "183866009",  # Referral to emergency clinic (procedure)
        "305922005",  # Referral by mental health counselor (procedure)
        "306136006",  # Referral to liaison psychiatry service (procedure)
        "306137002",  # Referral to mental handicap psychiatry service (procedure)
        "306138007",  # Referral to psychogeriatric service (procedure)
        "306204008",  # Referral to psychogeriatric day hospital (procedure)
        "306226009",  # Referral to mental health counseling service (procedure)
        "306227000",  # Referral for mental health counseling (procedure)
        "306252003",  # Referral to mental health counselor (procedure)
        "306294000",  # Referral to psychiatrist for mental handicap (procedure)
        "308459004",  # Referral to psychologist (procedure)
        "308477009",  # Referral to psychiatrist (procedure)
        "390866009",  # Referral to mental health team (procedure)
        "703978000",  # Referral to primary care service (procedure)
        "710914003",  # Referral to family therapy (procedure)
        "711281004",  # Referral to support group (procedure)
    }


class HospiceCareAmbulatory(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of interventions to identify patients receiving hospice care outside of a hospital or long term care facility.

    **Data Element Scope:** This value set may use a model element related to Procedure or Intervention.

    **Inclusion Criteria:** Includes concepts that represent a procedure or intervention for hospice care.

    **Exclusion Criteria:** Excludes concepts that represent palliative care or comfort measures.

    ** Used in:** CMS347v5, CMS69v10
    """

    VALUE_SET_NAME = "Hospice Care Ambulatory"
    OID = "2.16.840.1.113883.3.526.3.1584"
    DEFINITION_VERSION = "20200307"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "385763009",  # Hospice care (regime/therapy)
        "385765002",  # Hospice care management (procedure)
    }


class Referral(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of an encounter for a referral of a patient to a practitioner for evaluation, treatment or co-management of a patient's condition.

    **Data Element Scope:** This value set may use a model element related to Intervention.

    **Inclusion Criteria:** Includes concepts that represent an intervention for referrals and consultations.

    **Exclusion Criteria:** Excludes concepts that represent self-referrals.

    ** Used in:** CMS50v10
    """

    VALUE_SET_NAME = "Referral"
    OID = "2.16.840.1.113883.3.464.1003.101.12.1046"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "54395008",  # Patient referral for medical consultation (procedure)
        "103696004",  # Patient referral to specialist (procedure)
        "103697008",  # Patient referral for dental care (procedure)
        "103698003",  # Patient referral to non-physician provider (procedure)
        "103699006",  # Patient referral to dietitian (procedure)
        "103704003",  # Patient referral to sex therapist (procedure)
        "183515008",  # Referral to physician (procedure)
        "183517000",  # Referral to pediatrician (procedure)
        "183528001",  # Referral to psychiatrist for the elderly mentally ill (procedure)
        "183529009",  # Referral to oncologist (procedure)
        "183530004",  # Referral to diabetologist (procedure)
        "183541002",  # Referral to surgeon (procedure)
        "183555005",  # Burns referral (procedure)
        "183557002",  # Referral to cardiothoracic surgeon (procedure)
        "183561008",  # Referral to general practitioner (procedure)
        "183567007",  # Referral to hematologist (procedure)
        "183569005",  # Refer to terminal care consult (procedure)
        "183583007",  # Refer to mental health worker (procedure)
        "183591003",  # Refer to partner (procedure)
        "183878008",  # Private referral to general surgeon (procedure)
        "183879000",  # Private referral to ophthalmologist (procedure)
        "183880002",  # Private referral to ear, nose and throat surgeon (procedure)
        "183881003",  # Private referral to orthopedic surgeon (procedure)
        "183882005",  # Private referral to neurosurgeon (procedure)
        "183884006",  # Private referral to pediatric surgeon (procedure)
        "183885007",  # Private referral to obstetrician (procedure)
        "183886008",  # Private referral to gynecologist (procedure)
        "183887004",  # Private referral to plastic surgeon (procedure)
        "183888009",  # Private referral to oral surgeon (procedure)
        "183889001",  # Private referral to urologist (procedure)
        "183890005",  # Private referral to thoracic surgeon (procedure)
        "183891009",  # Private referral to vascular surgeon (procedure)
        "183892002",  # Private referral to maxillofacial surgeon (procedure)
        "183893007",  # Private referral cardiothoracic surgeon (procedure)
        "183894001",  # Private referral to physician (procedure)
        "183895000",  # Private referral to general physician (procedure)
        "183896004",  # Private referral to pediatrician (procedure)
        "183897008",  # Private referral to dermatologist (procedure)
        "183899006",  # Private referral to cardiologist (procedure)
        "183900001",  # Private referral to immunologist (procedure)
        "183901002",  # Private referral to neurologist (procedure)
        "183902009",  # Private referral to geriatrician (procedure)
        "183903004",  # Private referral to gastroenterologist (procedure)
        "183904005",  # Private referral to psychiatrist (procedure)
        "183905006",  # Private referral to venereologist (procedure)
        "183906007",  # Private referral to rheumatologist (procedure)
        "183907003",  # Private referral to chest physician (procedure)
        "183908008",  # Private referral to psychogeriatrician (procedure)
        "183909000",  # Private referral to oncologist (procedure)
        "183910005",  # Private referral to diabetologist (procedure)
        "183911009",  # Private referral to radiotherapist (procedure)
        "183913007",  # Private referral to geneticist (procedure)
        "183914001",  # Private referral to anesthetist (procedure)
        "183915000",  # Private referral to endocrinologist (procedure)
        "183916004",  # Private referral to nephrologist (procedure)
        "266747000",  # Referral to private doctor (procedure)
        "274410002",  # Dental referral - child (procedure)
        "306241009",  # Referral to audiological physician (procedure)
        "306242002",  # Referral to audiological scientist (procedure)
        "306243007",  # Referral to community doctor in audiology (procedure)
        "306245000",  # Referral to hearing therapist (procedure)
        "306247008",  # Referral to pediatric audiologist (procedure)
        "306250006",  # Referral to genetic counselor (procedure)
        "306252003",  # Referral to mental health counselor (procedure)
        "306253008",  # Referral to doctor (procedure)
        "306254002",  # Referral to Accident and Emergency doctor (procedure)
        "306255001",  # Referral to anesthetist (procedure)
        "306256000",  # Referral to radiotherapist (procedure)
        "306257009",  # Referral to family planning doctor (procedure)
        "306258004",  # Referral to intensive care specialist (procedure)
        "306259007",  # Referral to adult intensive care specialist (procedure)
        "306260002",  # Referral to pediatric intensive care specialist (procedure)
        "306261003",  # Referral to community pediatrician (procedure)
        "306262005",  # Referral to neonatologist (procedure)
        "306263000",  # Referral to pediatric neurologist (procedure)
        "306264006",  # Referral to pediatric oncologist (procedure)
        "306265007",  # Referral to pain management specialist (procedure)
        "306266008",  # Referral to pathologist (procedure)
        "306267004",  # Referral to blood transfusion doctor (procedure)
        "306268009",  # Referral to chemical pathologist (procedure)
        "306269001",  # Referral to general pathologist (procedure)
        "306270000",  # Referral to medical microbiologist (procedure)
        "306271001",  # Referral to neuropathologist (procedure)
        "306272008",  # Referral to clinical allergist (procedure)
        "306273003",  # Referral to chest physician (procedure)
        "306275005",  # Referral to respiratory physician (procedure)
        "306276006",  # Referral to clinical neurophysiologist (procedure)
        "306277002",  # Referral to clinical physiologist (procedure)
        "306278007",  # Referral to endocrinologist (procedure)
        "306279004",  # Referral to clinical geneticist (procedure)
        "306280001",  # Referral to clinical cytogeneticist (procedure)
        "306281002",  # Referral to clinical molecular geneticist (procedure)
        "306282009",  # Referral to genitourinary physician (procedure)
        "306284005",  # Referral to infectious diseases physician (procedure)
        "306285006",  # Referral to medical ophthalmologist (procedure)
        "306286007",  # Referral to nephrologist (procedure)
        "306287003",  # Referral to nuclear medicine physician (procedure)
        "306288008",  # Referral to palliative care physician (procedure)
        "306289000",  # Referral to rehabilitation physician (procedure)
        "306290009",  # Referral to rheumatologist (procedure)
        "306291008",  # Referral to child and adolescent psychiatrist (procedure)
        "306293006",  # Referral to liaison psychiatrist (procedure)
        "306294000",  # Referral to psychiatrist for mental handicap (procedure)
        "306295004",  # Referral to rehabilitation psychiatrist (procedure)
        "306296003",  # Referral to public health physician (procedure)
        "306297007",  # Referral to obstetrician and gynecologist (procedure)
        "306298002",  # Referral to occupational health physician (procedure)
        "306299005",  # Referral to radiologist (procedure)
        "306300002",  # Referral to breast surgeon (procedure)
        "306301003",  # Referral to thoracic surgeon (procedure)
        "306302005",  # Referral to cardiac surgeon (procedure)
        "306303000",  # Referral to dental surgeon (procedure)
        "306304006",  # Referral to orthodontist (procedure)
        "306305007",  # Referral to pediatric dentist (procedure)
        "306306008",  # Referral to restorative dentist (procedure)
        "306307004",  # Referral to endocrine surgeon (procedure)
        "306308009",  # Referral to gastrointestinal surgeon (procedure)
        "306309001",  # Referral to general gastrointestinal surgeon (procedure)
        "306310006",  # Referral to upper gastrointestinal surgeon (procedure)
        "306311005",  # Referral to colorectal surgeon (procedure)
        "306312003",  # Referral to hand surgeon (procedure)
        "306313008",  # Referral to hepatobiliary surgeon (procedure)
        "306314002",  # Referral to pancreatic surgeon (procedure)
        "306315001",  # Referral to plastic surgeon (procedure)
        "306316000",  # Referral to transplant surgeon (procedure)
        "306317009",  # Referral to trauma surgeon (procedure)
        "306318004",  # Referral to urologist (procedure)
        "306320001",  # Referral to clinical nurse specialist (procedure)
        "306338003",  # Referral to nurse practitioner (procedure)
        "306341007",  # Referral to community-based midwife (procedure)
        "306342000",  # Referral to hospital-based midwife (procedure)
        "306343005",  # Referral to psychotherapist (procedure)
        "306351008",  # Referral to community-based podiatrist (procedure)
        "306352001",  # Referral to hospital-based podiatrist (procedure)
        "306353006",  # Referral to community-based dietitian (procedure)
        "306354000",  # Referral to hospital-based dietitian (procedure)
        "306355004",  # Referral to community-based occupational therapist (procedure)
        "306356003",  # Referral to social services department occupational therapist (procedure)
        "306357007",  # Referral to hospital-based occupational therapist (procedure)
        "306358002",  # Referral to community-based physiotherapist (procedure)
        "306359005",  # Referral to hospital-based physiotherapist (procedure)
        "306360000",  # Referral to community-based speech and language therapist (procedure)
        "306361001",  # Referral to hospital-based speech and language therapist (procedure)
        "306736002",  # Referral to general dental surgeon (procedure)
        "307063001",  # Referral to clinical hematologist (procedure)
        "307777008",  # Referral to vascular surgeon (procedure)
        "308439003",  # Referral to midwife (procedure)
        "308447003",  # Referral to physiotherapist (procedure)
        "308449000",  # Referral to chiropractor (procedure)
        "308450000",  # Referral to osteopath (procedure)
        "308451001",  # Referral to podiatrist (procedure)
        "308452008",  # Referral to speech and language therapist (procedure)
        "308453003",  # Referral to occupational therapist (procedure)
        "308454009",  # Referral to orthoptist (procedure)
        "308455005",  # Referral to orthotist (procedure)
        "308456006",  # Referral to audiologist (procedure)
        "308459004",  # Referral to psychologist (procedure)
        "308465004",  # Referral to optometrist (procedure)
        "308469005",  # Referral to geneticist (procedure)
        "308470006",  # Referral to general physician (procedure)
        "308471005",  # Referral to cardiologist (procedure)
        "308472003",  # Referral to dermatologist (procedure)
        "308473008",  # Referral to clinical immunologist (procedure)
        "308474002",  # Referral to neurologist (procedure)
        "308475001",  # Referral to care of the elderly physician (procedure)
        "308476000",  # Referral to gastroenterologist (procedure)
        "308477009",  # Referral to psychiatrist (procedure)
        "308478004",  # Referral to general surgeon (procedure)
        "308479007",  # Referral to ophthalmologist (procedure)
        "308480005",  # Referral to ear, nose and throat surgeon (procedure)
        "308481009",  # Referral to orthopedic surgeon (procedure)
        "308482002",  # Referral to neurosurgeon (procedure)
        "308483007",  # Referral to pediatric surgeon (procedure)
        "308484001",  # Referral to obstetrician (procedure)
        "308485000",  # Referral to gynecologist (procedure)
        "309046007",  # Private referral to surgeon (procedure)
        "309623006",  # Child referral to optician (procedure)
        "309626003",  # Child referral - school psychologist (procedure)
        "309627007",  # Child referral - clinical psychologist (procedure)
        "309629005",  # Child referral - community dentist (procedure)
        "310515004",  # Referral to medical oncologist (procedure)
        "312487009",  # Referral to pediatric cardiologist (procedure)
        "312488004",  # Referral to community child health doctor (procedure)
        "390866009",  # Referral to mental health team (procedure)
        "401266006",  # Referral to drug abuse counselor (procedure)
        "406158007",  # Referral to oral surgeon (procedure)
        "406159004",  # Referral to maxillofacial surgeon (procedure)
        "408285001",  # Referral to pediatric dietitian (procedure)
        "415277000",  # Referral to pediatric endocrinologist (procedure)
        "416116000",  # Referral to home registered dietitian (procedure)
        "416999007",  # Private referral to physiotherapist (procedure)
        "425971006",  # Referral to pediatric pulmonologist (procedure)
        "429365000",  # Referral to pediatric gastroenterologist (procedure)
        "433151006",  # Referral to educational psychologist (procedure)
        "698563003",  # Referral to bariatric surgeon (procedure)
        "698599008",  # Private referral to breast surgeon (procedure)
        "703974003",  # Private referral to colorectal surgeon (procedure)
        "703975002",  # Private referral to podiatrist (procedure)
        "703976001",  # Private referral to radiologist (procedure)
        "716634006",  # Referral to neurological physiotherapist (procedure)
        "428441000124100",  # Referral to nurse anesthetist (procedure)
        "428451000124103",  # Referral to physician assistant (procedure)
        "428461000124101",  # Referral to nutrition professional (procedure)
        "428471000124108",  # Referral to clinical psychologist (procedure)
        "428481000124106",  # Referral to clinical social worker (procedure)
        "428491000124109",  # Referral to anesthesiologist assistant (procedure)
        "428541000124104",  # Referral to nurse midwife (procedure)
        "448761000124106",  # Referral to endovascular specialist (procedure)
        "448771000124104",  # Referral to prosthetist (procedure)
    }


class FollowUpForAboveNormalBmi(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a follow-up for a body mass index (BMI) above normal measurement.

    **Data Element Scope:** This value set may use a model element related to Intervention or Procedure.

    **Inclusion Criteria:** Includes concepts that represent a follow-up for above normal body mass index (BMI).

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS69v10
    """

    VALUE_SET_NAME = "Follow Up for Above Normal BMI"
    OID = "2.16.840.1.113883.3.600.1.1525"
    DEFINITION_VERSION = "20190314"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "43644",  # Laparoscopy, surgical, gastric restrictive procedure; with gastric bypass and Roux-en-Y gastroenterostomy (roux limb 150 cm or less)
        "43645",  # Laparoscopy, surgical, gastric restrictive procedure; with gastric bypass and small intestine reconstruction to limit absorption
        "43659",  # Unlisted laparoscopy procedure, stomach
        "43770",  # Laparoscopy, surgical, gastric restrictive procedure; placement of adjustable gastric restrictive device (eg, gastric band and subcutaneous port components)
        "43771",  # Laparoscopy, surgical, gastric restrictive procedure; revision of adjustable gastric restrictive device component only
        "43772",  # Laparoscopy, surgical, gastric restrictive procedure; removal of adjustable gastric restrictive device component only
        "43773",  # Laparoscopy, surgical, gastric restrictive procedure; removal and replacement of adjustable gastric restrictive device component only
        "43774",  # Laparoscopy, surgical, gastric restrictive procedure; removal of adjustable gastric restrictive device and subcutaneous port components
        "43842",  # Gastric restrictive procedure, without gastric bypass, for morbid obesity; vertical-banded gastroplasty
        "43843",  # Gastric restrictive procedure, without gastric bypass, for morbid obesity; other than vertical-banded gastroplasty
        "43845",  # Gastric restrictive procedure with partial gastrectomy, pylorus-preserving duodenoileostomy and ileoileostomy (50 to 100 cm common channel) to limit absorption (biliopancreatic diversion with duodenal switch)
        "43846",  # Gastric restrictive procedure, with gastric bypass for morbid obesity; with short limb (150 cm or less) Roux-en-Y gastroenterostomy
        "43847",  # Gastric restrictive procedure, with gastric bypass for morbid obesity; with small intestine reconstruction to limit absorption
        "43848",  # Revision, open, of gastric restrictive procedure for morbid obesity, other than adjustable gastric restrictive device (separate procedure)
        "43886",  # Gastric restrictive procedure, open; revision of subcutaneous port component only
        "43888",  # Gastric restrictive procedure, open; removal and replacement of subcutaneous port component only
        "97802",  # Medical nutrition therapy; initial assessment and intervention, individual, face-to-face with the patient, each 15 minutes
        "97803",  # Medical nutrition therapy; re-assessment and intervention, individual, face-to-face with the patient, each 15 minutes
        "97804",  # Medical nutrition therapy; group (2 or more individual(s)), each 30 minutes
        "98960",  # Education and training for patient self-management by a qualified, nonphysician health care professional using a standardized curriculum, face-to-face with the patient (could include caregiver/family) each 30 minutes; individual patient
        "99078",  # Physician or other qualified health care professional qualified by education, training, licensure/regulation (when applicable) educational services rendered to patients in a group setting (eg, prenatal, obesity, or diabetic instructions)
        "99401",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 15 minutes
        "99402",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 30 minutes
    }
    HCPCSLEVELII = {
        "G0270",  # Medical nutrition therapy; reassessment and subsequent intervention(s) following second referral in same year for change in diagnosis, medical condition or treatment regimen (including additional hours needed for renal disease), individual, face to face with the patient, each 15 minutes
        "G0271",  # Medical nutrition therapy, reassessment and subsequent intervention(s) following second referral in same year for change in diagnosis, medical condition, or treatment regimen (including additional hours needed for renal disease), group (2 or more individuals), each 30 minutes
        "G0447",  # Face-to-face behavioral counseling for obesity, 15 minutes
        "G0473",  # Face-to-face behavioral counseling for obesity, group (2-10), 30 minutes
        "S9449",  # Weight management classes, non-physician provider, per session
        "S9451",  # Exercise classes, non-physician provider, per session
        "S9452",  # Nutrition classes, non-physician provider, per session
        "S9470",  # Nutritional counseling, dietitian visit
    }
    ICD10CM = {
        "Z713",  # Dietary counseling and surveillance
        "Z7182",  # Exercise counseling
    }
    SNOMEDCT = {
        "304549008",  # Giving encouragement to exercise (procedure)
        "307818003",  # Weight monitoring (regime/therapy)
        "361231003",  # Prescribed dietary intake (regime/therapy)
        "370847001",  # Dietary needs education (procedure)
        "386291006",  # Exercise promotion: strength training (procedure)
        "386292004",  # Exercise promotion: stretching (procedure)
        "386373004",  # Nutrition therapy (regime/therapy)
        "386463000",  # Prescribed activity/exercise education (procedure)
        "386464006",  # Prescribed diet education (procedure)
        "410177006",  # Special diet education (procedure)
        "413315001",  # Nutrition / feeding management (regime/therapy)
        "418995006",  # Feeding regime (regime/therapy)
        "424753004",  # Dietary management education, guidance, and counseling (procedure)
        "443288003",  # Lifestyle education regarding diet (procedure)
    }


class FollowUpForBelowNormalBmi(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for follow-up with a body mass index (BMI) below normal measurement.

    **Data Element Scope:** This value set may use a model element related to Intervention or Procedure.

    **Inclusion Criteria:** Includes concepts that represent a follow-up for below normal body mass index (BMI).

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS69v10
    """

    VALUE_SET_NAME = "Follow Up for Below Normal BMI"
    OID = "2.16.840.1.113883.3.600.1.1528"
    DEFINITION_VERSION = "20200307"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    CPT = {
        "97802",  # Medical nutrition therapy; initial assessment and intervention, individual, face-to-face with the patient, each 15 minutes
        "97803",  # Medical nutrition therapy; re-assessment and intervention, individual, face-to-face with the patient, each 15 minutes
        "97804",  # Medical nutrition therapy; group (2 or more individual(s)), each 30 minutes
        "98960",  # Education and training for patient self-management by a qualified, nonphysician health care professional using a standardized curriculum, face-to-face with the patient (could include caregiver/family) each 30 minutes; individual patient
        "99078",  # Physician or other qualified health care professional qualified by education, training, licensure/regulation (when applicable) educational services rendered to patients in a group setting (eg, prenatal, obesity, or diabetic instructions)
        "99401",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 15 minutes
        "99402",  # Preventive medicine counseling and/or risk factor reduction intervention(s) provided to an individual (separate procedure); approximately 30 minutes
    }
    HCPCSLEVELII = {
        "G0270",  # Medical nutrition therapy; reassessment and subsequent intervention(s) following second referral in same year for change in diagnosis, medical condition or treatment regimen (including additional hours needed for renal disease), individual, face to face with the patient, each 15 minutes
        "G0271",  # Medical nutrition therapy, reassessment and subsequent intervention(s) following second referral in same year for change in diagnosis, medical condition, or treatment regimen (including additional hours needed for renal disease), group (2 or more individuals), each 30 minutes
        "S9449",  # Weight management classes, non-physician provider, per session
        "S9452",  # Nutrition classes, non-physician provider, per session
        "S9470",  # Nutritional counseling, dietitian visit
    }
    ICD10CM = {
        "Z713",  # Dietary counseling and surveillance
    }
    SNOMEDCT = {
        "386464006",  # Prescribed diet education (procedure)
        "410177006",  # Special diet education (procedure)
        "413315001",  # Nutrition / feeding management (regime/therapy)
        "418995006",  # Feeding regime (regime/therapy)
        "424753004",  # Dietary management education, guidance, and counseling (procedure)
        "429095004",  # Dietary education for weight gain (procedure)
        "443288003",  # Lifestyle education regarding diet (procedure)
    }


class ReferralsWhereWeightAssessmentMayOccur(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a referral to multiple types of providers and settings for weight assessment.

    **Data Element Scope:** This value set may use a model element related to Intervention or Procedure.

    **Inclusion Criteria:** Includes concepts that represent a referral to multiple types of providers and settings for weight assessment.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS69v10
    """

    VALUE_SET_NAME = "Referrals Where Weight Assessment May Occur"
    OID = "2.16.840.1.113883.3.600.1.1527"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "183515008",  # Referral to physician (procedure)
        "183524004",  # Referral to psychiatry service (procedure)
        "183583007",  # Refer to mental health worker (procedure)
        "306136006",  # Referral to liaison psychiatry service (procedure)
        "306163007",  # Referral to dietetics service (procedure)
        "306164001",  # Referral to community-based dietetics service (procedure)
        "306165000",  # Referral to hospital-based dietetics service (procedure)
        "306166004",  # Referral to occupational therapy service (procedure)
        "306167008",  # Referral to community-based occupational therapy service (procedure)
        "306168003",  # Referral to hospital-based occupational therapy service (procedure)
        "306226009",  # Referral to mental health counseling service (procedure)
        "306227000",  # Referral for mental health counseling (procedure)
        "306252003",  # Referral to mental health counselor (procedure)
        "306344004",  # Referral to professional allied to medicine (procedure)
        "306353006",  # Referral to community-based dietitian (procedure)
        "306354000",  # Referral to hospital-based dietitian (procedure)
        "308459004",  # Referral to psychologist (procedure)
        "308470006",  # Referral to general physician (procedure)
        "308477009",  # Referral to psychiatrist (procedure)
        "390864007",  # Referral for exercise therapy (procedure)
        "390866009",  # Referral to mental health team (procedure)
        "390893007",  # Referral to physical activity program (procedure)
        "408289007",  # Refer to weight management program (procedure)
        "416790000",  # Referral for home physical therapy (procedure)
    }


__exports__ = get_overrides(locals().copy())
