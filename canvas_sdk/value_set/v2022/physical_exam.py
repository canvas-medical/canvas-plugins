from canvas_sdk.value_set._utilities import get_overrides

from ..value_set import ValueSet


class RetinalOrDilatedEyeExam(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a physical exam where a retinal or dilated eye exam was performed.

    **Data Element Scope:** This value set may use a model element related to Physical Exam.

    **Inclusion Criteria:** Includes concepts that represent a physical exam during which a retinal or dilated eye exam occurred.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS131v10
    """

    VALUE_SET_NAME = "Retinal or Dilated Eye Exam"
    OID = "2.16.840.1.113883.3.464.1003.115.12.1088"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "6615001",  # Electroretinography (procedure)
        "252779009",  # Single bright white flash electroretinography (procedure)
        "252780007",  # Dark adapted single bright flash electroretinography (procedure)
        "252781006",  # Pre-dark-adapted single bright flash electroretinography (procedure)
        "252782004",  # Photopic electroretinography (procedure)
        "252783009",  # Scotopic rod electroretinography (procedure)
        "252784003",  # Flicker electroretinography (procedure)
        "252788000",  # Chromatic electroretinography (procedure)
        "252789008",  # Early receptor potential electroretinography (procedure)
        "252790004",  # Focal electroretinography (procedure)
        "274795007",  # Examination of optic disc (procedure)
        "274798009",  # Examination of retina (procedure)
        "308110009",  # Direct fundoscopy following mydriatic (procedure)
        "314971001",  # Camera fundoscopy (procedure)
        "314972008",  # Indirect fundoscopy following mydriatic (procedure)
        "410451008",  # Indirect ophthalmoscopy (procedure)
        "410452001",  # Monocular indirect ophthalmoscopy (procedure)
        "410453006",  # Binocular indirect ophthalmoscopy (procedure)
        "410455004",  # Slit lamp fundus examination (procedure)
        "420213007",  # Multifocal electroretinography (procedure)
        "425816006",  # Ultrasonic evaluation of retina (procedure)
        "427478009",  # Evaluation of retina (procedure)
        "722161008",  # Diabetic retinal eye exam (procedure)
    }


class BestCorrectedVisualAcuityExamUsingSnellenChart(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of a physical exam for visual acuity exams using a Snellen chart.

    **Data Element Scope:** This value set may use a model element related to Physical Exam.

    **Inclusion Criteria:** Includes concepts that represent a physical exam for visual acuity using a Snellen chart.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS133v10
    """

    VALUE_SET_NAME = "Best Corrected Visual Acuity Exam Using Snellen Chart"
    OID = "2.16.840.1.113883.3.526.3.1560"
    DEFINITION_VERSION = "20210210"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "79880-1",  # Visual acuity best corrected Right eye by Snellen eye chart
        "79881-9",  # Visual acuity best corrected Left eye by Snellen eye chart
    }


class HeartRate(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of a physical exam measuring heart rate.

    **Data Element Scope:** This value set may use a model element related to Physical Exam.

    **Inclusion Criteria:** Includes concepts that represent a physical exam for obtaining heart rate.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS144v10, CMS145v10
    """

    VALUE_SET_NAME = "Heart Rate"
    OID = "2.16.840.1.113883.3.526.3.1176"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "68999-2",  # Heart rate --supine
        "69000-8",  # Heart rate --sitting
        "69001-6",  # Heart rate --standing
        "8867-4",  # Heart rate
    }


class BmiPercentile(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a physical exam where a body mass index (BMI) percentile is calculated.

    **Data Element Scope:** This value set may use a model element related to Physical Exam.

    **Inclusion Criteria:** Includes concepts that represent a physical exam with a BMI percentile measurement.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS155v10
    """

    VALUE_SET_NAME = "BMI percentile"
    OID = "2.16.840.1.113883.3.464.1003.121.12.1012"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "59574-4",  # Body mass index (BMI) [Percentile]
        "59575-1",  # Body mass index (BMI) [Percentile] Per age
        "59576-9",  # Body mass index (BMI) [Percentile] Per age and sex
    }


class Height(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a physical exam with measured height.

    **Data Element Scope:** This value set may use a model element related to Physical Exam.

    **Inclusion Criteria:** Includes concepts that represent a physical exam with a patient height measurement.

    **Exclusion Criteria:** Excludes concepts that represent patient reported height, a percentile for height or an estimated height.

    ** Used in:** CMS155v10
    """

    VALUE_SET_NAME = "Height"
    OID = "2.16.840.1.113883.3.464.1003.121.12.1014"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "3137-7",  # Body height Measured
        "8302-2",  # Body height
        "8306-3",  # Body height --lying
        "8307-1",  # Body height --preoperative
        "8308-9",  # Body height --standing
    }


class Weight(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a physical exam with measured weight.

    **Data Element Scope:** This value set may use a model element related to Physical Exam.

    **Inclusion Criteria:** Includes concepts that represent a physical exam with a patient weight measurement.

    **Exclusion Criteria:** Excludes concepts that represent an ideal body weight, estimated body weight or a body fat measurement.

    ** Used in:** CMS155v10
    """

    VALUE_SET_NAME = "Weight"
    OID = "2.16.840.1.113883.3.464.1003.121.12.1015"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

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


class BmiRatio(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a physical exam where a body mass index (BMI) ratio is calculated.

    **Data Element Scope:** This value set may use a model element related to Physical Exam.

    **Inclusion Criteria:** Includes concepts that represent a physical exam with a body mass index (BMI) ratio measurement.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS249v4
    """

    VALUE_SET_NAME = "BMI Ratio"
    OID = "2.16.840.1.113883.3.600.1.1490"
    DEFINITION_VERSION = "20140502"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "39156-5",  # Body mass index (BMI) [Ratio]
    }


__exports__ = get_overrides(locals().copy())
