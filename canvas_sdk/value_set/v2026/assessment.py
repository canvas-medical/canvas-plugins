from ..value_set import ValueSet

class EstimatedGestationalAgeAtDelivery(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to describe concepts of assessment for estimated gestational age at delivery.

    **Data Element Scope:** This value set may use a model element related to assessment.

    **Inclusion Criteria:** Includes concepts that define an assessment of the estimated gestational age at delivery.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Estimated Gestational Age at Delivery"
    OID = "2.16.840.1.113762.1.4.1045.26"
    DEFINITION_VERSION = "20210611"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "11884-4",  # Gestational age Estimated
        "11885-1",  # Gestational age Estimated from last menstrual period
        "18185-9",  # Gestational age
        "49051-6",  # Gestational age in weeks
    }

class NonInvasiveOxygenTherapy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for oxygen therapies not associated with invasive mechanical ventilation

    **Data Element Scope:** This value set may use a model element related to Assessment

    **Inclusion Criteria:** Includes concepts that represent non invasive oxygen therapies including oxygen masks, nasal cannulas, CPAP, and BPAP which are not associated with invasive mechanical ventilation

    **Exclusion Criteria:** Oxygen therapies and devices associated with invasive mechanical ventilation
    """

    VALUE_SET_NAME = "Non Invasive Oxygen Therapy"
    OID = "2.16.840.1.113762.1.4.1248.213"
    DEFINITION_VERSION = "20230512"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    ICD10PCS = {
        "5A09357",  # Assistance with Respiratory Ventilation, Less than 24 Consecutive Hours, Continuous Positive Airway Pressure
        "5A09358",  # Assistance with Respiratory Ventilation, Less than 24 Consecutive Hours, Intermittent Positive Airway Pressure
        "5A09457",  # Assistance with Respiratory Ventilation, 24-96 Consecutive Hours, Continuous Positive Airway Pressure
        "5A09458",  # Assistance with Respiratory Ventilation, 24-96 Consecutive Hours, Intermittent Positive Airway Pressure
        "5A09557",  # Assistance with Respiratory Ventilation, Greater than 96 Consecutive Hours, Continuous Positive Airway Pressure
        "5A09558",  # Assistance with Respiratory Ventilation, Greater than 96 Consecutive Hours, Intermittent Positive Airway Pressure
    }

    SNOMEDCT = {
        "1186618000",  # Bilevel artificial ventilation (regime/therapy)
        "1186678006",  # Continuous positive airway pressure with an assured constant airway pressure adjunct (regime/therapy)
        "243142003",  # Dual pressure spontaneous ventilation support (regime/therapy)
        "257420000",  # Breathing circuit (physical object)
        "26397000",  # Breathing bag, device (physical object)
        "297120004",  # Anesthetic face mask (physical object)
        "336602003",  # Oxygen mask (physical object)
        "336623009",  # Oxygen nasal cannula (physical object)
        "34281000175105",  # Nocturnal continuous positive airway pressure (regime/therapy)
        "34291000175108",  # Nocturnal dual pressure spontaneous ventilation support (regime/therapy)
        "405642002",  # Anesthesia breathing circuit (physical object)
        "424172009",  # Dual pressure spontaneous ventilation support weaning protocol (regime/therapy)
        "425478008",  # Blow by oxygen mask (physical object)
        "425826004",  # Bilevel positive airway pressure oxygen nasal cannula (physical object)
        "426294006",  # Face tent oxygen delivery device (physical object)
        "426851007",  # Aerosol oxygen mask (physical object)
        "426854004",  # High flow oxygen nasal cannula (physical object)
        "427591007",  # Nonrebreather oxygen mask (physical object)
        "427594004",  # Oxyhood (physical object)
        "428285009",  # Venturi mask (physical object)
        "442398003",  # Nasal mask (physical object)
        "446573003",  # Continuous positive airway pressure titration (procedure)
        "447243000",  # Bilevel positive airway pressure titration (procedure)
        "448134000",  # Continuous positive airway pressure to nonventilated lung (regime/therapy)
        "463587004",  # Rebreathing oxygen face mask (physical object)
        "464225001",  # Oxygen administration nasal catheter (physical object)
        "464233000",  # Partial-rebreathing oxygen face mask (physical object)
        "464428002",  # Moisture chamber face mask (physical object)
        "464578003",  # Oxygen administration face tent (physical object)
        "465256000",  # Tracheostomy mask, aerosol (physical object)
        "465433006",  # Venturi oxygen face mask (physical object)
        "465839001",  # Tracheostomy mask, oxygen (physical object)
        "466713001",  # Basic nasal oxygen cannula (physical object)
        "467645007",  # Continuous positive airway pressure nasal oxygen cannula (physical object)
        "468246003",  # Aerosol face mask, rebreathing (physical object)
        "468414000",  # Aerosol face mask, non-rebreathing (physical object)
        "469956003",  # Anesthesia breathing circuit circulator (physical object)
        "47545007",  # Continuous positive airway pressure ventilation treatment (regime/therapy)
        "701254008",  # Bidirectional-anesthesia breathing circuit (physical object)
        "701582002",  # Vortex oxygen face mask (physical object)
        "704718009",  # CPAP/BPAP oral mask (physical object)
        "706175007",  # Ventilator breathing circuit (physical object)
        "706226000",  # Continuous positive airway pressure/Bilevel positive airway pressure mask (physical object)
        "719705009",  # Capnography oxygen mask (physical object)
        "722742002",  # Breathing room air (finding)
    }

class EmergencyDepartmentEvaluation(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of an assessment performed in the emergency department.

    **Data Element Scope:** This value set may use a model element related to Assessment.

    **Inclusion Criteria:** Includes concepts that represent an assessment that was performed in the emergency department.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Emergency Department Evaluation"
    OID = "2.16.840.1.113762.1.4.1111.163"
    DEFINITION_VERSION = "20200305"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "28568-4",  # Physician Emergency department Note
        "34111-5",  # Emergency department Note
        "34878-9",  # Emergency medicine Note
        "51846-4",  # Emergency department Consult note
        "54094-8",  # Emergency department Triage note
        "68552-9",  # Emergency medicine Emergency department Admission evaluation note
        "74211-4",  # Emergency department+Hospital Summary of episode note
        "78249-0",  # Emergency department Admission history and physical note
        "78307-6",  # Emergency department History and physical note
        "78337-3",  # Emergency department Initial evaluation note
        "78341-5",  # Emergency department Transfer summary note
        "80741-2",  # Emergency medicine Emergency department Plan of care note
        "80746-1",  # Emergency department Plan of care note
        "83818-5",  # Attending Emergency department Note
    }

class TobaccoUseScreening(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for assessments to screen for tobacco use.

    **Data Element Scope:** This value set may use a model element related to Assessment.

    **Inclusion Criteria:** Includes concepts that represent an assessment for tobacco use, including smoking and smoke-less tobacco products.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Tobacco Use Screening"
    OID = "2.16.840.1.113883.3.526.3.1278"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "39240-7",  # Tobacco use status CPHS
        "68535-4",  # Have you used tobacco in the last 30 days [SAMHSA]
        "68536-2",  # Have you used smokeless tobacco product in the last 30 days [SAMHSA]
        "72166-2",  # Tobacco smoking status
    }

class FallsScreening(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for assessments using a falls screening tool.

    **Data Element Scope:** This value set may use a model element related to Assessment.

    **Inclusion Criteria:** Includes concepts that represent an assessment for fall risk.

    **Exclusion Criteria:** Excludes concepts that represent an assessment for falls for children.
    """

    VALUE_SET_NAME = "Falls Screening"
    OID = "2.16.840.1.113883.3.464.1003.118.12.1028"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "52552-7",  # Falls in the past year
        "57254-5",  # Standardized fall risk assessment was conducted during assessment period [CMS Assessment]
        "59454-9",  # History of falling; immediate or within 3 months [Morse Fall Scale]
        "73830-2",  # Fall risk assessment
    }

class StandardizedToolsScoreForAssessmentOfCognition(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to define concepts for assessments representing total score results for standardized tools used for the evaluation of cognition.

    **Data Element Scope:** This value set may use a model element related to Assessment.

    **Inclusion Criteria:** Includes concepts that describe assessments with total score results for the following standardized tools: -Blessed Orientation-Memory-Concentration Test (BOMC) -Montreal Cognitive Assessment (MoCA) -St. Louis University Mental Status Examination (SLUMS) -Mini-Mental State Examination (MMSE) [Note: The MMSE has not been well validated for non-Alzheimer's dementias] -Short Informant Questionnaire on Cognitive Decline in the Elderly (IQCODE) -Ascertain Dementia 8 (AD8) Questionnaire -Minimum Data Set (MDS) Brief Interview of Mental Status (BIMS) [Note: Validated for use with nursing home patients only] -Formal neuropsychological evaluation -Mini-Cog.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Standardized Tools Score for Assessment of Cognition"
    OID = "2.16.840.1.113883.3.526.3.1006"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "58151-2",  # Prior assessment Brief Interview for Mental Status (BIMS) summary score [MDSv3]
        "71492-3",  # Total score [SLUMS]
        "71493-1",  # Total score [IQCODE]
        "71722-3",  # Total score [AD8]
        "72106-8",  # Total score [MMSE]
        "72172-0",  # Total score [MoCA]
        "72173-8",  # Total score [BOMC]
        "72233-0",  # Total score [Mini-Cog]
    }

class StandardizedPainAssessmentTool(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for assessments using pain-focused tools or instruments to quantify pain intensity.

    **Data Element Scope:** This value set may use a model element related to Assessment.

    **Inclusion Criteria:** Includes concepts that represent an assessment of pain intensity.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Standardized Pain Assessment Tool"
    OID = "2.16.840.1.113883.3.526.3.1028"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "38208-5",  # Pain severity - Reported
        "38214-3",  # Pain severity [Score] Visual analog score
        "38221-8",  # Pain severity Wong-Baker FACES pain rating scale
        "72514-3",  # Pain severity - 0-10 verbal numeric rating [Score] - Reported
        "77565-0",  # Pain interference score [BPI Short Form]
    }

class Phq9AndPhq9mTools(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for the assessments of PHQ 9 and PHQ 9M resulting in a completed depression assessment scores for adults and adolescents.

    **Data Element Scope:** This value set may use a model element related to Assessment.

    **Inclusion Criteria:** Includes concepts that represent a completed assessment using PHQ 9 and PHQ 9M depression assessment tools for adults and adolescents with a summary score.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "PHQ 9 and PHQ 9M Tools"
    OID = "2.16.840.1.113883.3.67.1.101.1.263"
    DEFINITION_VERSION = "20220219"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "44261-6",  # Patient Health Questionnaire 9 item (PHQ-9) total score [Reported]
        "89204-2",  # Patient Health Questionnaire-9: Modified for Teens total score [Reported.PHQ.Teen]
    }

class AbnormalPresentation(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to group diagnoses of a fetus in an abnormal position in the uterus at the time of delivery.

    **Data Element Scope:** This value set may use a model element related to diagnosis.

    **Inclusion Criteria:** Includes concepts that identify a diagnosis of a fetus in an abnormal position.

    **Exclusion Criteria:** Excludes concepts that represent a fetus in a vertex presentation.
    """

    VALUE_SET_NAME = "Abnormal Presentation"
    OID = "2.16.840.1.113762.1.4.1045.105"
    DEFINITION_VERSION = "20210611"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    ICD10CM = {
        "O321XX0",  # Maternal care for breech presentation, not applicable or unspecified
        "O321XX1",  # Maternal care for breech presentation, fetus 1
        "O321XX2",  # Maternal care for breech presentation, fetus 2
        "O321XX3",  # Maternal care for breech presentation, fetus 3
        "O321XX4",  # Maternal care for breech presentation, fetus 4
        "O321XX5",  # Maternal care for breech presentation, fetus 5
        "O321XX9",  # Maternal care for breech presentation, other fetus
        "O322XX0",  # Maternal care for transverse and oblique lie, not applicable or unspecified
        "O322XX1",  # Maternal care for transverse and oblique lie, fetus 1
        "O322XX2",  # Maternal care for transverse and oblique lie, fetus 2
        "O322XX3",  # Maternal care for transverse and oblique lie, fetus 3
        "O322XX4",  # Maternal care for transverse and oblique lie, fetus 4
        "O322XX5",  # Maternal care for transverse and oblique lie, fetus 5
        "O322XX9",  # Maternal care for transverse and oblique lie, other fetus
        "O323XX0",  # Maternal care for face, brow and chin presentation, not applicable or unspecified
        "O323XX1",  # Maternal care for face, brow and chin presentation, fetus 1
        "O323XX2",  # Maternal care for face, brow and chin presentation, fetus 2
        "O323XX3",  # Maternal care for face, brow and chin presentation, fetus 3
        "O323XX4",  # Maternal care for face, brow and chin presentation, fetus 4
        "O323XX5",  # Maternal care for face, brow and chin presentation, fetus 5
        "O323XX9",  # Maternal care for face, brow and chin presentation, other fetus
        "O328XX0",  # Maternal care for other malpresentation of fetus, not applicable or unspecified
        "O328XX1",  # Maternal care for other malpresentation of fetus, fetus 1
        "O328XX2",  # Maternal care for other malpresentation of fetus, fetus 2
        "O328XX3",  # Maternal care for other malpresentation of fetus, fetus 3
        "O328XX4",  # Maternal care for other malpresentation of fetus, fetus 4
        "O328XX5",  # Maternal care for other malpresentation of fetus, fetus 5
        "O328XX9",  # Maternal care for other malpresentation of fetus, other fetus
        "O329XX0",  # Maternal care for malpresentation of fetus, unspecified, not applicable or unspecified
        "O329XX1",  # Maternal care for malpresentation of fetus, unspecified, fetus 1
        "O329XX2",  # Maternal care for malpresentation of fetus, unspecified, fetus 2
        "O329XX3",  # Maternal care for malpresentation of fetus, unspecified, fetus 3
        "O329XX4",  # Maternal care for malpresentation of fetus, unspecified, fetus 4
        "O329XX5",  # Maternal care for malpresentation of fetus, unspecified, fetus 5
        "O329XX9",  # Maternal care for malpresentation of fetus, unspecified, other fetus
        "O632",  # Delayed delivery of second twin, triplet, etc.
        "O641XX0",  # Obstructed labor due to breech presentation, not applicable or unspecified
        "O641XX1",  # Obstructed labor due to breech presentation, fetus 1
        "O641XX2",  # Obstructed labor due to breech presentation, fetus 2
        "O641XX3",  # Obstructed labor due to breech presentation, fetus 3
        "O641XX4",  # Obstructed labor due to breech presentation, fetus 4
        "O641XX5",  # Obstructed labor due to breech presentation, fetus 5
        "O641XX9",  # Obstructed labor due to breech presentation, other fetus
        "O642XX0",  # Obstructed labor due to face presentation, not applicable or unspecified
        "O642XX1",  # Obstructed labor due to face presentation, fetus 1
        "O642XX2",  # Obstructed labor due to face presentation, fetus 2
        "O642XX3",  # Obstructed labor due to face presentation, fetus 3
        "O642XX4",  # Obstructed labor due to face presentation, fetus 4
        "O642XX5",  # Obstructed labor due to face presentation, fetus 5
        "O642XX9",  # Obstructed labor due to face presentation, other fetus
        "O643XX0",  # Obstructed labor due to brow presentation, not applicable or unspecified
        "O643XX1",  # Obstructed labor due to brow presentation, fetus 1
        "O643XX2",  # Obstructed labor due to brow presentation, fetus 2
        "O643XX3",  # Obstructed labor due to brow presentation, fetus 3
        "O643XX4",  # Obstructed labor due to brow presentation, fetus 4
        "O643XX5",  # Obstructed labor due to brow presentation, fetus 5
        "O643XX9",  # Obstructed labor due to brow presentation, other fetus
        "O644XX0",  # Obstructed labor due to shoulder presentation, not applicable or unspecified
        "O644XX1",  # Obstructed labor due to shoulder presentation, fetus 1
        "O644XX2",  # Obstructed labor due to shoulder presentation, fetus 2
        "O644XX3",  # Obstructed labor due to shoulder presentation, fetus 3
        "O644XX4",  # Obstructed labor due to shoulder presentation, fetus 4
        "O644XX5",  # Obstructed labor due to shoulder presentation, fetus 5
        "O644XX9",  # Obstructed labor due to shoulder presentation, other fetus
        "O648XX0",  # Obstructed labor due to other malposition and malpresentation, not applicable or unspecified
        "O648XX1",  # Obstructed labor due to other malposition and malpresentation, fetus 1
        "O648XX2",  # Obstructed labor due to other malposition and malpresentation, fetus 2
        "O648XX3",  # Obstructed labor due to other malposition and malpresentation, fetus 3
        "O648XX4",  # Obstructed labor due to other malposition and malpresentation, fetus 4
        "O648XX5",  # Obstructed labor due to other malposition and malpresentation, fetus 5
        "O648XX9",  # Obstructed labor due to other malposition and malpresentation, other fetus
    }

    SNOMEDCT = {
        "11914001",  # Transverse OR oblique presentation of fetus (disorder)
        "1231436008",  # Breech position of fetus in pregnancy (disorder)
        "18559007",  # Frank breech presentation (finding)
        "199355003",  # Breech presentation with antenatal problem (finding)
        "199359009",  # Oblique lie with antenatal problem (disorder)
        "199363002",  # Transverse lie with antenatal problem (disorder)
        "199751005",  # Obstructed labor due to breech presentation (disorder)
        "199752003",  # Obstructed labor due to face presentation (disorder)
        "199753008",  # Obstructed labor due to brow presentation (disorder)
        "199754002",  # Obstructed labor due to shoulder presentation (disorder)
        "200142000",  # Breech extraction - delivered (finding)
        "21882006",  # Face presentation of fetus (disorder)
        "23954006",  # Acromion presentation (finding)
        "249064003",  # Oblique lie, head in iliac fossa (disorder)
        "249065002",  # Oblique lie, breech in iliac fossa (disorder)
        "249089009",  # Fetal mouth presenting (disorder)
        "249090000",  # Fetal ear presenting (disorder)
        "249091001",  # Fetal nose presenting (disorder)
        "249093003",  # Presentation of orbital ridges of fetus (disorder)
        "249097002",  # Footling breech presentation (finding)
        "249098007",  # Knee presentation (disorder)
        "249099004",  # Single knee presentation (disorder)
        "249100007",  # Double knee presentation (disorder)
        "249104003",  # Dorsoanterior shoulder presentation (disorder)
        "249105002",  # Dorsoposterior shoulder presentation (disorder)
        "274128005",  # Brow delivery (finding)
        "274129002",  # Face delivery (finding)
        "289355004",  # Oblique lie head in right iliac fossa (disorder)
        "289356003",  # Oblique lie head in left iliac fossa (disorder)
        "289357007",  # Oblique lie breech in right iliac fossa (disorder)
        "289358002",  # Oblique lie breech in left iliac fossa (disorder)
        "289398000",  # Fetal breech palpable vaginally (finding)
        "38049006",  # Incomplete breech presentation (finding)
        "48906005",  # Breech presentation, double footling (finding)
        "49168004",  # Complete breech presentation (finding)
        "58903006",  # Breech presentation, single footling (finding)
        "6096002",  # Breech presentation (finding)
        "63750008",  # Oblique lie (disorder)
        "73161006",  # Transverse lie (disorder)
        "79255005",  # Mentum presentation of fetus (disorder)
        "8014007",  # Brow presentation of fetus (disorder)
    }

class HistoryOfAtrialAblation(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a situation of a personal history of an atrial ablation.

    **Data Element Scope:** This value set may use a model element related to a diagnosis or assessment.

    **Inclusion Criteria:** Includes concepts that identify a situation for a personal history of an atrial ablation.

    **Exclusion Criteria:** No Exclusions.
    """

    VALUE_SET_NAME = "History of Atrial Ablation"
    OID = "2.16.840.1.113762.1.4.1110.76"
    DEFINITION_VERSION = "20221115"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "427951003",  # History of radiofrequency ablation operation for arrhythmia (situation)
        "429508000",  # History of ablation of atrioventricular node (situation)
        "429756009",  # History of radiofrequency ablation operation on left atrium for arrhythmia (situation)
    }

class MalnutritionRiskScreening(ValueSet):
    """
    **Clinical Focus:** This set of values indicates that a malnutrition screening was done by the health care professional.

    **Data Element Scope:** Data elements included in this set indicate an individual has been screened for malnutrition.

    **Inclusion Criteria:** Malnutrition Risk Screening tools and codes to indicate that a malnutrition risk screening was done.

    **Exclusion Criteria:** Nutrition assessment tools and codes to indicate that a nutrition assessment was done are excluded.
    """

    VALUE_SET_NAME = "Malnutrition Risk Screening"
    OID = "2.16.840.1.113762.1.4.1095.92"
    DEFINITION_VERSION = "20240117"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "101807-6",  # Malnutrition risk screen results indicator
        "98967-3",  # Nutritional Risk Screening 2002 panel
        "98968-1",  # Initial screening NRS_2002
        "98972-3",  # Final screening NRS_2002
    }

class NutritionAssessment(ValueSet):
    """
    **Clinical Focus:** This set of values indicates that a nutrition assessment was completed by a health professional.

    **Data Element Scope:** Completed nutrition assessment by a health professional.

    **Inclusion Criteria:** Nutrition assessment tools and codes to indicate that a nutrition assessment was completed.

    **Exclusion Criteria:** Nutrition screening tools and codes to indicate that a nutrition screening was completed are excluded.
    """

    VALUE_SET_NAME = "Nutrition Assessment"
    OID = "2.16.840.1.113762.1.4.1095.21"
    DEFINITION_VERSION = "20240117"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    LOINC = {
        "101819-1",  # Nutritional assessment for malnutrition status
        "75282-4",  # Nutrition assessment panel
        "75285-7",  # Comparative nutrition assessment standards panel
        "75303-8",  # Nutrition assessment Narrative
        "75304-6",  # Nutrition status observation panel
    }

__exports__ = (
    "EstimatedGestationalAgeAtDelivery",
    "NonInvasiveOxygenTherapy",
    "EmergencyDepartmentEvaluation",
    "TobaccoUseScreening",
    "FallsScreening",
    "StandardizedToolsScoreForAssessmentOfCognition",
    "StandardizedPainAssessmentTool",
    "Phq9AndPhq9mTools",
    "AbnormalPresentation",
    "HistoryOfAtrialAblation",
    "MalnutritionRiskScreening",
    "NutritionAssessment",
)
