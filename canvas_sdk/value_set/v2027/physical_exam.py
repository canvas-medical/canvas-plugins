from ..value_set import ValueSet


class BestCorrectedVisualAcuityExamUsingSnellenChart(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of a physical exam for visual acuity exams using a Snellen chart.

    **Data Element Scope:** This value set may use a model element related to Physical Exam.

    **Inclusion Criteria:** Includes concepts that represent a physical exam for visual acuity using a Snellen chart.

    **Exclusion Criteria:** No exclusions.

    **Used in:** CMS133v15
    """

    VALUE_SET_NAME = "Best Corrected Visual Acuity Exam Using Snellen Chart"
    OID = "2.16.840.1.113883.3.526.3.1560"
    DEFINITION_VERSION = "20210210"
    EXPANSION_VERSION = "eCQM Update 2026-05-14"

    LOINC = {
        "79880-1",  # Visual acuity best corrected Right eye by Snellen eye chart
        "79881-9",  # Visual acuity best corrected Left eye by Snellen eye chart
    }


class BmiPercentile(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a physical exam where a body mass index (BMI) percentile is calculated.

    **Data Element Scope:** This value set may use a model element related to Physical Exam.

    **Inclusion Criteria:** Includes concepts that represent a physical exam with a BMI percentile measurement.

    **Exclusion Criteria:** No exclusions.

    **Used in:** CMS155v15
    """

    VALUE_SET_NAME = "BMI percentile"
    OID = "2.16.840.1.113883.3.464.1003.121.12.1012"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2026-05-14"

    LOINC = {
        "59574-4",  # Body mass index (BMI) [Percentile]
        "59575-1",  # Body mass index (BMI) [Percentile] Per age
        "59576-9",  # Body mass index (BMI) [Percentile] Per age and sex
    }


class BodyTemperature(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a physical exam with an observation or measurement of a patient's body temperature.

    **Data Element Scope:** This value set may use a model element related to Physical Exam.

    **Inclusion Criteria:** Includes concepts that represent a physical exam during which observation or measurement of a body temperature occurred.

    **Exclusion Criteria:** No exclusions.

    **Used in:** CMS529v7, CMS832v4, CMS844v7
    """

    VALUE_SET_NAME = "Body Temperature"
    OID = "2.16.840.1.113762.1.4.1045.152"
    DEFINITION_VERSION = "20250220"
    EXPANSION_VERSION = "eCQM Update 2026-05-14"

    LOINC = {
        "104063-3",  # Body temperature - Groin
        "11289-6",  # Body temperature at First encounter
        "60830-7",  # Finger temperature
        "60833-1",  # Toe temperature
        "60836-4",  # Esophageal temperature
        "60838-0",  # Nasopharyngeal temperature
        "61008-9",  # Body surface temperature
        "75539-7",  # Body temperature - Temporal artery
        "76010-8",  # Nasal temperature
        "76011-6",  # Ear temperature
        "8310-5",  # Body temperature
        "8328-7",  # Axillary temperature
        "8329-5",  # Body temperature - Core
        "8330-3",  # Body temperature - Intravascular
        "8331-1",  # Oral temperature
        "8332-9",  # Rectal temperature
        "8333-7",  # Tympanic membrane temperature
        "8334-5",  # Body temperature - Urinary bladder
        "91371-5",  # Body temperature - Brain
        "98657-0",  # Body temperature - Hand surface
        "98663-8",  # Body temperature - Foot surface
    }


class BodyWeight(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a physical exam or clinical observation where a person’s body weight is measured, stated, reported, estimated, or calculated, including special contexts such as pre/post dialysis, perioperative, postpartum, dry or lean weight, and attachment-recorded weights.

    **Data Element Scope:** This value set may use a model element related to Physical Exam or other clinical observations where body weight is documented or used for clinical calculations (e.g., drug dosing, ventilator settings).

    **Inclusion Criteria:** Includes concepts representing body weight in any context, including first or usual weight, measurements for calculation, and any observed or estimated weights in the contexts listed above.

    **Exclusion Criteria:** No exclusions.

    **Used in:** CMS529v7
    """

    VALUE_SET_NAME = "Body Weight"
    OID = "2.16.840.1.113762.1.4.1045.159"
    DEFINITION_VERSION = "20230214"
    EXPANSION_VERSION = "eCQM Update 2026-05-14"

    LOINC = {
        "18833-4",  # First Body weight
        "29463-7",  # Body weight
        "3141-9",  # Body weight Measured
        "3142-7",  # Body weight Stated
        "75292-3",  # Body weight - Reported --usual
        "8341-0",  # Dry body weight Measured
        "8344-4",  # Body weight Measured --post dialysis
        "8346-9",  # Body weight Measured --postoperative
        "8347-7",  # Body weight Measured --pre dialysis
        "8349-3",  # Body weight Measured --preoperative
        "8350-1",  # Body weight Measured --with clothes
        "8351-9",  # Body weight Measured --without clothes
    }


class HeartRate(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of a physical exam measuring heart rate.

    **Data Element Scope:** This value set may use a model element related to Physical Exam.

    **Inclusion Criteria:** Includes concepts that represent a physical exam for obtaining heart rate.

    **Exclusion Criteria:** No exclusions.

    **Used in:** CMS144v15
    """

    VALUE_SET_NAME = "Heart Rate"
    OID = "2.16.840.1.113883.3.526.3.1176"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2026-05-14"

    LOINC = {
        "11328-2",  # Heart rate at First encounter
        "68999-2",  # Heart rate --supine
        "69000-8",  # Heart rate --sitting
        "69001-6",  # Heart rate --standing
        "8867-4",  # Heart rate
    }


class HeartRate1341(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of a physical exam measuring heart rate.

    **Data Element Scope:** This value set may use a model element related to Physical Exam.

    **Inclusion Criteria:** Includes concepts that represent a physical exam for obtaining heart rate.

    **Exclusion Criteria:** No exclusions.

    **Used in:** CMS529v7, CMS844v7
    """

    VALUE_SET_NAME = "Heart Rate"
    OID = "2.16.840.1.113883.3.526.2.1341"
    DEFINITION_VERSION = "20240202"
    EXPANSION_VERSION = "eCQM Update 2026-05-14"

    LOINC = {
        "11328-2",  # Heart rate at First encounter
        "68999-2",  # Heart rate --supine
        "69000-8",  # Heart rate --sitting
        "69001-6",  # Heart rate --standing
        "8867-4",  # Heart rate
    }


class Height(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a physical exam with measured height.

    **Data Element Scope:** This value set may use a model element related to Physical Exam.

    **Inclusion Criteria:** Includes concepts that represent a physical exam with a patient height measurement.

    **Exclusion Criteria:** Excludes concepts that represent patient reported height, a percentile for height or an estimated height.

    **Used in:** CMS155v15
    """

    VALUE_SET_NAME = "Height"
    OID = "2.16.840.1.113883.3.464.1003.121.12.1014"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2026-05-14"

    LOINC = {
        "103692-0",  # Body height during assessment period [CMS Assessment]
        "3137-7",  # Body height Measured
        "8302-2",  # Body height
        "8306-3",  # Body height --lying
        "8307-1",  # Body height --preoperative
        "8308-9",  # Body height --standing
    }


class OxygenSaturationByPulseOximetry(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a physical exam or assessment using pulse oximetry to measure a patient’s oxygen saturation.

    **Data Element Scope:** This value set may use a model element related to Physical Exam.

    **Inclusion Criteria:** Includes concepts that represent a patient’s arterial oxygen saturation measured via pulse oximetry during standard physical exam or specific conditions (e.g., resting, exercise, pre-treatment, anesthesia).

    **Exclusion Criteria:** Excludes oxygen saturation values derived from blood specimens, cord or fetal blood, or calculated from laboratory measurements.

    **Used in:** CMS529v7, CMS844v7
    """

    VALUE_SET_NAME = "Oxygen Saturation by Pulse Oximetry"
    OID = "2.16.840.1.113762.1.4.1045.151"
    DEFINITION_VERSION = "20230214"
    EXPANSION_VERSION = "eCQM Update 2026-05-14"

    LOINC = {
        "59408-5",  # Oxygen saturation in Arterial blood by Pulse oximetry
        "59410-1",  # Oxygen saturation in Arterial blood by Pulse oximetry --on room air
        "59414-3",  # Oxygen saturation in Arterial blood by Pulse oximetry --pre bronchodilation
        "59415-0",  # Oxygen saturation in Arterial blood by Pulse oximetry --pre physiotherapy
        "59416-8",  # Oxygen saturation in Arterial blood by Pulse oximetry --pre treatment
        "59417-6",  # Oxygen saturation in Arterial blood by Pulse oximetry --resting
        "89276-0",  # Oxygen saturation in Arterial blood by Pulse oximetry --W exercise
        "89277-8",  # Oxygen saturation in Arterial blood by Pulse oximetry --during anesthesia
    }


class RespiratoryRate(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a physical exam or clinical observation in which a person’s respiratory rate is measured or observed, including spontaneous, mechanical, ventilator-assisted, pulse oximetry, or first encounter measurements.

    **Data Element Scope:** This value set may use a model element related to Physical Exam or clinical observation capturing respiratory rate.

    **Inclusion Criteria:** Includes concepts representing respiratory rate measurement during a physical exam or clinical observation, including mechanical or ventilator-assisted, spontaneous, pulse-ox, and first encounter measurements.

    **Exclusion Criteria:** Excludes device identifiers, ventilator settings, and survey-based respiratory assessments (e.g., PROMIS shortness-of-breath questionnaires).

    **Used in:** CMS529v7
    """

    VALUE_SET_NAME = "Respiratory Rate"
    OID = "2.16.840.1.113762.1.4.1045.130"
    DEFINITION_VERSION = "20230214"
    EXPANSION_VERSION = "eCQM Update 2026-05-14"

    LOINC = {
        "11291-2",  # Respiratory rate at First encounter
        "33438-3",  # Breath rate mechanical --on ventilator
        "76174-2",  # Respiratory rate by Pulse oximetry.plethysmograph
        "76528-9",  # Breath rate spontaneous
        "9279-1",  # Respiratory rate
    }


class RetinalOrDilatedEyeExam(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a physical exam where a retinal or dilated eye exam was performed.

    **Data Element Scope:** This value set may use a model element related to Physical Exam.

    **Inclusion Criteria:** Includes concepts that represent a physical exam during which a retinal or dilated eye exam occurred.

    **Exclusion Criteria:** No exclusions.

    **Used in:** CMS131v15
    """

    VALUE_SET_NAME = "Retinal or Dilated Eye Exam"
    OID = "2.16.840.1.113883.3.464.1003.115.12.1088"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2026-05-14"

    SNOMEDCT = {
        "18188000",  # Ophthalmoscopy under general anesthesia (procedure)
        "20067007",  # Ocular fundus photography (procedure)
        "21593001",  # Ophthalmodynamography (procedure)
        "252779009",  # Single bright white flash electroretinography (procedure)
        "252780007",  # Dark adapted single bright flash electroretinography (procedure)
        "252781006",  # Pre-dark-adapted single bright flash electroretinography (procedure)
        "252782004",  # Photopic electroretinography (procedure)
        "252783009",  # Scotopic rod electroretinography (procedure)
        "252784003",  # Flicker electroretinography (procedure)
        "252788000",  # Chromatic electroretinography (procedure)
        "252789008",  # Early receptor potential electroretinography (procedure)
        "252790004",  # Focal electroretinography (procedure)
        "252846004",  # Scanning laser ophthalmoscopy (procedure)
        "274795007",  # Examination of optic disc (procedure)
        "274798009",  # Examination of retina (procedure)
        "3047001",  # Kowa fundus photography (procedure)
        "308110009",  # Direct fundoscopy following mydriatic (procedure)
        "30842004",  # Ophthalmoscopy with medical evaluation, extended, with fundus photography (procedure)
        "314971001",  # Camera fundoscopy (procedure)
        "314972008",  # Indirect fundoscopy following mydriatic (procedure)
        "36844005",  # Ophthalmoscopy with medical evaluation, extended, with ophthalmodynamometry (procedure)
        "391999003",  # Confocal scanning laser ophthalmoscopy (procedure)
        "392005004",  # Scanning laser polarimetry (procedure)
        "410441007",  # Ophthalmoscopy with medical evaluation, extended, with fluorescein angiography (procedure)
        "410450009",  # Direct ophthalmoscopy (procedure)
        "410451008",  # Indirect ophthalmoscopy (procedure)
        "410452001",  # Monocular indirect ophthalmoscopy (procedure)
        "410453006",  # Binocular indirect ophthalmoscopy (procedure)
        "410455004",  # Slit lamp fundus examination (procedure)
        "416369006",  # Integrated optical coherence tomography and scanning laser ophthalmoscopy (procedure)
        "417587001",  # Integrated ray-trace triangulation acquisition laser scanning with conventional fundus imaging (procedure)
        "420213007",  # Multifocal electroretinography (procedure)
        "425816006",  # Ultrasonic evaluation of retina (procedure)
        "427478009",  # Evaluation of retina (procedure)
        "53524009",  # Ophthalmoscopy (procedure)
        "56072006",  # Ophthalmoscopy with medical evaluation, extended, for retinal detachment mapping (procedure)
        "56204000",  # Ophthalmodynamometry (procedure)
        "6615001",  # Electroretinography (procedure)
        "700070005",  # Optical coherence tomography of retina (procedure)
        "722161008",  # Diabetic retinal eye exam (procedure)
    }


class SystolicBloodPressure(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a physical exam with a standard observation or measurement of systolic blood pressure.

    **Data Element Scope:** This value set may use a model element related to Physical Exam.

    **Inclusion Criteria:** Includes concepts that represent a physical exam during which a person’s systolic blood pressure was measured manually automatically, or in standard body positions (e.g., sitting, standing, supine, lateral).

    **Exclusion Criteria:** Excludes concepts representing invasive, arterial-specific, ultrasound-derived, pediatric percentile, or laboratory-based systolic blood pressure measurements.

    **Used in:** CMS529v7, CMS844v7
    """

    VALUE_SET_NAME = "Systolic Blood Pressure"
    OID = "2.16.840.1.113762.1.4.1045.163"
    DEFINITION_VERSION = "20230214"
    EXPANSION_VERSION = "eCQM Update 2026-05-14"

    LOINC = {
        "11378-7",  # Systolic blood pressure at First encounter
        "8459-0",  # Systolic blood pressure--sitting
        "8460-8",  # Systolic blood pressure--standing
        "8461-6",  # Systolic blood pressure--supine
        "8480-6",  # Systolic blood pressure
        "89268-7",  # Systolic blood pressure--lying in L-lateral position
    }


class Weight(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a physical exam with measured weight.

    **Data Element Scope:** This value set may use a model element related to Physical Exam.

    **Inclusion Criteria:** Includes concepts that represent a physical exam with a patient weight measurement.

    **Exclusion Criteria:** Excludes concepts that represent an ideal body weight, estimated body weight or a body fat measurement.

    **Used in:** CMS155v15
    """

    VALUE_SET_NAME = "Weight"
    OID = "2.16.840.1.113883.3.464.1003.121.12.1015"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2026-05-14"

    LOINC = {
        "18833-4",  # First Body weight
        "29463-7",  # Body weight
        "3141-9",  # Body weight Measured
        "3142-7",  # Body weight Stated
        "8341-0",  # Dry body weight Measured
        "8349-3",  # Body weight Measured --preoperative
        "8350-1",  # Body weight Measured --with clothes
        "8351-9",  # Body weight Measured --without clothes
    }


__exports__ = (
    "BestCorrectedVisualAcuityExamUsingSnellenChart",
    "BmiPercentile",
    "BodyTemperature",
    "BodyWeight",
    "HeartRate",
    "HeartRate1341",
    "Height",
    "OxygenSaturationByPulseOximetry",
    "RespiratoryRate",
    "RetinalOrDilatedEyeExam",
    "SystolicBloodPressure",
    "Weight",
)
