from canvas_sdk.value_set._utilities import get_overrides

from ..value_set import ValueSet


class Mammography(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a mammogram.

    **Data Element Scope:** This value set may use a model element related to Diagnostic Study.

    **Inclusion Criteria:** Includes concepts that represent a diagnostic study for a mammogram or mammography exam.

    **Exclusion Criteria:** Excludes order only codes.

    ** Used in:** CMS125v10
    """

    VALUE_SET_NAME = "Mammography"
    OID = "2.16.840.1.113883.3.464.1003.108.12.1018"
    DEFINITION_VERSION = "20210304"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "24604-1",  # MG Breast Diagnostic Limited Views
        "24605-8",  # MG Breast Diagnostic
        "24606-6",  # MG Breast Screening
        "24610-8",  # MG Breast Limited Views
        "26175-0",  # MG Breast - bilateral Screening
        "26176-8",  # MG Breast - left Screening
        "26177-6",  # MG Breast - right Screening
        "26287-3",  # MG Breast - bilateral Limited Views
        "26289-9",  # MG Breast - left Limited Views
        "26291-5",  # MG Breast - right Limited Views
        "26346-7",  # MG Breast - bilateral Diagnostic
        "26347-5",  # MG Breast - left Diagnostic
        "26348-3",  # MG Breast - right Diagnostic
        "26349-1",  # MG Breast - bilateral Diagnostic Limited Views
        "26350-9",  # MG Breast - left Diagnostic Limited Views
        "26351-7",  # MG Breast - right Diagnostic Limited Views
        "36319-2",  # MG Breast 4 Views
        "36625-2",  # MG Breast Views
        "36626-0",  # MG Breast - bilateral Views
        "36627-8",  # MG Breast - left Views
        "36642-7",  # MG Breast - left 2 Views
        "36962-9",  # MG Breast Axillary
        "37005-6",  # MG Breast - left Magnification
        "37006-4",  # MG Breast - bilateral MLO
        "37016-3",  # MG Breast - bilateral Rolled Views
        "37017-1",  # MG Breast - left Rolled Views
        "37028-8",  # MG Breast Tangential
        "37029-6",  # MG Breast - bilateral Tangential
        "37030-4",  # MG Breast - left Tangential
        "37037-9",  # MG Breast True lateral
        "37038-7",  # MG Breast - bilateral True lateral
        "37052-8",  # MG Breast - bilateral XCCL
        "37053-6",  # MG Breast - left XCCL
        "37539-4",  # MG Breast Grid Views
        "37542-8",  # MG Breast Magnification Views
        "37543-6",  # MG Breast - bilateral Magnification Views
        "37551-9",  # MG Breast Spot Views
        "37552-7",  # MG Breast - bilateral Spot Views
        "37553-5",  # MG Breast - left Spot Views compression
        "37554-3",  # MG Breast - bilateral Magnification and Spot
        "37768-9",  # MG Breast - right 2 Views
        "37769-7",  # MG Breast - right Magnification and Spot
        "37770-5",  # MG Breast - right Tangential
        "37771-3",  # MG Breast - right True lateral
        "37772-1",  # MG Breast - right XCCL
        "37773-9",  # MG Breast - right Magnification
        "37774-7",  # MG Breast - right Views
        "37775-4",  # MG Breast - right Rolled Views
        "38070-9",  # MG Breast Views for implant
        "38071-7",  # MG Breast - bilateral Views for implant
        "38072-5",  # MG Breast - left Views for implant
        "38090-7",  # MG Breast - bilateral Air gap Views
        "38091-5",  # MG Breast - left Air gap Views
        "38807-4",  # MG Breast - right Spot Views
        "38820-7",  # MG Breast - right Views for implant
        "38854-6",  # MG Breast - left Magnification and Spot
        "38855-3",  # MG Breast - left True lateral
        "39150-8",  # FFD mammogram Breast Views Post Localization
        "39152-4",  # FFD mammogram Breast Diagnostic
        "39153-2",  # FFD mammogram Breast Screening
        "39154-0",  # FFD mammogram Breast - bilateral Diagnostic
        "42168-5",  # FFD mammogram Breast - right Diagnostic
        "42169-3",  # FFD mammogram Breast - left Diagnostic
        "42174-3",  # FFD mammogram Breast - bilateral Screening
        "42415-0",  # MG Breast - bilateral Views Post Wire Placement
        "42416-8",  # MG Breast - left Views Post Wire Placement
        "46335-6",  # MG Breast - bilateral Single view
        "46336-4",  # MG Breast - left Single view
        "46337-2",  # MG Breast - right Single view
        "46338-0",  # MG Breast - unilateral Single view
        "46339-8",  # MG Breast - unilateral Views
        "46342-2",  # FFD mammogram Breast Views
        "46350-5",  # MG Breast - unilateral Diagnostic
        "46351-3",  # MG Breast - bilateral Displacement Views for Implant
        "46354-7",  # FFD mammogram Breast - right Screening
        "46355-4",  # FFD mammogram Breast - left Screening
        "46356-2",  # MG Breast - unilateral Screening
        "46380-2",  # MG Breast - unilateral Views for implant
        "48475-8",  # MG Breast - bilateral Diagnostic for implant
        "48492-3",  # MG Breast - bilateral Screening for implant
        "69150-1",  # MG Breast - left Diagnostic for implant
        "69251-7",  # MG Breast Views Post Wire Placement
        "69259-0",  # MG Breast - right Diagnostic for implant
        "72137-3",  # DBT Breast - right diagnostic
        "72138-1",  # DBT Breast - left diagnostic
        "72139-9",  # DBT Breast - bilateral diagnostic
        "72140-7",  # DBT Breast - right screening
        "72141-5",  # DBT Breast - left screening
        "72142-3",  # DBT Breast - bilateral screening
        "86462-9",  # DBT Breast - unilateral
        "86463-7",  # DBT Breast - bilateral
    }


class BoneScan(ValueSet):
    """
    **Clinical Focus:** This value set contains concepts that represent bone scan diagnostic imaging.

    **Data Element Scope:** This value set may use Quality Data Model (QDM) category related to Diagnostic Study.

    **Inclusion Criteria:** Includes only relevant concepts associated with conventional technetium-99m-MDP bone scan as well as 18F-NaF PET (or PET/CT) scan.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS129v11
    """

    VALUE_SET_NAME = "Bone Scan"
    OID = "2.16.840.1.113883.3.526.3.320"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "25031-6",  # NM Bone Views
        "25032-4",  # NM Bone Views W In-111 tagged WBC IV
        "39627-5",  # NM Bone Limited Views
        "39812-3",  # NM Bone Views W Tc-99m HMPAO IV
        "39813-1",  # SPECT Bone limited
        "39816-4",  # SPECT Whole body Bone
        "39818-0",  # NM Whole body Bone Views
        "39819-8",  # NM Bone Delayed Views
        "39820-6",  # NM Bone Views W Sm-153 IV
        "39858-6",  # NM Bone Views for blood flow
        "39879-2",  # SPECT Bone
        "39880-0",  # NM Bone 2 Phase Views
        "39881-8",  # SPECT Whole body Bone 3 phase
        "39882-6",  # NM Whole body Bone 3 Phase Views
        "39883-4",  # NM Bone 3 Phase Views
        "39884-2",  # NM Bone Blood pool
        "39901-4",  # NM Bone 3 Phase Views multiple areas
        "39902-2",  # NM Bone 3 Phase Views single area
        "39904-8",  # NM Bone Multiple area Views
        "39905-5",  # SPECT Bone multiple areas
        "41772-5",  # SPECT Bone W In-111 tagged WBC IV
        "41836-8",  # NM Bone Limited Views W In-111 tagged WBC IV
        "42700-5",  # NM Bone Views W Tc-99m tagged WBC IV
        "44142-8",  # NM Bone Views W Tc-99m medronate IV
        "81551-4",  # PET+CT Bone from skull base to mid-thigh W 18F-NaF IV
        "81552-2",  # PET+CT Whole body Bone W 18F-NaF IV
    }


class CtColonography(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for computed tomographic (CT) colonography.

    **Data Element Scope:** This value set may use a model element related to Procedure.

    **Inclusion Criteria:** Includes concepts that represent computed tomographic (CT) colonography.

    **Exclusion Criteria:** Excludes concepts that represent order only codes.

    ** Used in:** CMS130v10
    """

    VALUE_SET_NAME = "CT Colonography"
    OID = "2.16.840.1.113883.3.464.1003.108.12.1038"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "60515-4",  # CT Colon and Rectum W air contrast PR
        "72531-7",  # CT Colon and Rectum W contrast IV and W air contrast PR
        "79069-1",  # CT Colon and Rectum for screening WO contrast IV and W air contrast PR
        "79071-7",  # CT Colon and Rectum WO contrast IV and W air contrast PR
        "79101-2",  # CT Colon and Rectum for screening W air contrast PR
        "82688-3",  # CT Colon and Rectum WO and W contrast IV and W air contrast PR
    }


class EjectionFraction(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of diagnostic studies for ejection fraction.

    **Data Element Scope:** This value set may use a model element related to Diagnostic Study.

    **Inclusion Criteria:** Includes concepts that represent a diagnostic study for obtaining left ventricular ejection fraction.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS135v10, CMS144v10, CMS145v10
    """

    VALUE_SET_NAME = "Ejection Fraction"
    OID = "2.16.840.1.113883.3.526.3.1134"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "10230-1",  # Left ventricular Ejection fraction
        "18043-0",  # Left ventricular Ejection fraction by US
        "18044-8",  # Left ventricular Ejection fraction by US.2D+Calculated by single-plane ellipse method
        "18045-5",  # Left ventricular Ejection fraction by US.2D+Calculated by biplane ellipse method
        "18046-3",  # Left ventricular Ejection fraction by US 2D modified
        "18047-1",  # Left ventricular Ejection fraction by US 2D modified biplane
        "18048-9",  # Left ventricular Ejection fraction by US 2D modified single-plane
        "18049-7",  # Left ventricular Ejection fraction by US.M-mode+Calculated by Teichholz method
        "77889-4",  # Left ventricular Ejection fraction by US.M-mode+Calculated by cube method
        "77890-2",  # Left ventricular Ejection fraction by US.2D+Calculated by cube method
        "77891-0",  # Left ventricular Ejection fraction by US.2D+Calculated by Teichholz method
        "77892-8",  # Left ventricular Ejection fraction by US.2D+Calculated by modified Simpson method
        "79990-8",  # Left ventricular Ejection fraction by US.3D.segmentation
        "79991-6",  # Left ventricular Ejection fraction by US.2D+Calculated by biplane method of disks
        "79992-4",  # Left ventricular Ejection fraction by US.2D.A2C+Calculated by single plane method of disks
        "79993-2",  # Left ventricular Ejection fraction by US.2D.A4C+Calculated by single plane method of disks
        "8806-2",  # Left ventricular Ejection fraction by 2D echo
        "8807-0",  # Left ventricular Ejection fraction by 2D echo.visual estimate
        "8808-8",  # Left ventricular Ejection fraction by Cardiac angiogram
        "8809-6",  # Left ventricular Ejection fraction by Cardiac angiogram.visual estimate
        "8810-4",  # Left ventricular Ejection fraction by Spiral CT
        "8811-2",  # Left ventricular Ejection fraction by MR
        "8812-0",  # Left ventricular Ejection fraction by Nuclear blood pool
    }


class MacularExam(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a diagnostic study of a macular exam of the eye.

    **Data Element Scope:** This value set may use a model element related to Diagnostic Study.

    **Inclusion Criteria:** Includes concepts that represent a diagnostic study of macular exams, where laterality is specified or not.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS142v10
    """

    VALUE_SET_NAME = "Macular Exam"
    OID = "2.16.840.1.113883.3.526.3.1251"
    DEFINITION_VERSION = "20210209"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "32451-7",  # Physical findings of Macula
        "71488-1",  # Left eye Macular edema by Ophthalmoscopy
        "71489-9",  # Right eye Macular edema by Ophthalmoscopy
        "79820-7",  # Physical findings of Right macula by Ophthalmoscopy
        "79821-5",  # Physical findings of Left macula by Ophthalmoscopy
    }


class CupToDiscRatio(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of diagnostic studies specific to obtaining cup to disc ratio by ophthalmoscopy.

    **Data Element Scope:** This value set may use a model element related to Diagnostic Study.

    **Inclusion Criteria:** Includes concepts that represent a diagnostic study using ophthalmoscopy.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS143v10
    """

    VALUE_SET_NAME = "Cup to Disc Ratio"
    OID = "2.16.840.1.113883.3.526.3.1333"
    DEFINITION_VERSION = "20210209"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "71484-0",  # Left optic nerve Cup-disc ratio by Ophthalmoscopy
        "71485-7",  # Right optic nerve Cup-disc ratio by Ophthalmoscopy
    }


class OpticDiscExamForStructuralAbnormalities(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of diagnostic studies specific to obtaining cup to disc ratio by ophthalmoscopy.

    **Data Element Scope:** This value set may use a model element related to Diagnostic Study.

    **Inclusion Criteria:** Includes concepts that represent a diagnostic study using ophthalmoscopy.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS143v10
    """

    VALUE_SET_NAME = "Optic Disc Exam for Structural Abnormalities"
    OID = "2.16.840.1.113883.3.526.3.1334"
    DEFINITION_VERSION = "20210209"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "71486-5",  # Left eye Optic disc or retinal nerve fiber layer structural abnormalities by Ophthalmoscopy
        "71487-3",  # Right eye Optic disc or retinal nerve fiber layer structural abnormalities by Ophthalmoscopy
    }


class DiagnosticStudiesDuringPregnancy(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for diagnostic studies performed on a fetus during pregnancy.

    **Data Element Scope:** This value set may use a model element related to Diagnostic Study.

    **Inclusion Criteria:** Includes concepts that represent a diagnostic study conducted on a fetus.

    **Exclusion Criteria:** Excludes order only codes.

    ** Used in:** CMS153v10
    """

    VALUE_SET_NAME = "Diagnostic Studies During Pregnancy"
    OID = "2.16.840.1.113883.3.464.1003.111.12.1008"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "11615-2",  # Fetal Heart Activity US
        "11616-0",  # Fetal Heart Narrative Activity US
        "11617-8",  # Fetal Limbs Activity US
        "11618-6",  # Fetal Limbs Narrative Activity US
        "11619-4",  # Fetal Respiratory Activity US
        "11620-2",  # Fetal Respiratory Narrative Activity US
        "11621-0",  # Fetal Trunk Activity US
        "11622-8",  # Fetal Trunk Narrative Activity US
        "11623-6",  # Fetal Quadrant four Amniotic fluid index derived by US
        "11624-4",  # Fetal Quadrant four one Amniotic fluid index derived by US
        "11625-1",  # Fetal Quadrant three Amniotic fluid index derived by US
        "11626-9",  # Fetal Quadrant two Amniotic fluid index derived by US
        "11627-7",  # Fetal Amniotic fluid index.sum derived by US
        "11628-5",  # Fetal Head Binocular distance estimated from Biparietal diameter on US
        "11629-3",  # Fetal Head Binocular distance US
        "11630-1",  # Fetal Biophysical profile.amniotic fluid volume US
        "11631-9",  # Fetal Biophysical profile.body movement US
        "11632-7",  # Fetal Biophysical profile.breathing movement US
        "11633-5",  # Fetal Biophysical profile.heart rate reactivity US
        "11634-3",  # Fetal Biophysical profile.sum Derived
        "11635-0",  # Fetal Biophysical profile.tone US
        "11641-8",  # Fetal Mitral valve Peak A wave US.doppler
        "11643-4",  # Fetal Tricuspid valve Peak A wave US.doppler
        "11645-9",  # Fetal Mitral valve Peak E wave US.doppler
        "11647-5",  # Fetal Tricuspid valve Peak E wave US.doppler
        "11649-1",  # Fetal Mitral valve E-wave/A-wave US.doppler
        "11651-7",  # Fetal Tricuspid valve E-wave/A-wave US.doppler
        "11654-1",  # Fetal Cerebral artery anterior Minimal flow velocity US.doppler
        "11656-6",  # Fetal Cerebral artery middle Minimal flow velocity US.doppler
        "11660-8",  # Fetal Umbilical artery at fetus Minimal flow velocity US.doppler
        "11661-6",  # Fetal Umbilical artery at placenta Minimal flow velocity US.doppler
        "11662-4",  # Fetal Umbilical artery between fetus and placenta Minimal flow velocity US.doppler
        "11666-5",  # Fetal Aorta ascending Mean blood flow velocity US.doppler
        "11668-1",  # Fetal Aorta descending Mean blood flow velocity US.doppler
        "11670-7",  # Fetal Aortic arch Mean blood flow velocity US.doppler
        "11672-3",  # Fetal Cerebral artery anterior Mean blood flow velocity US.doppler
        "11675-6",  # Fetal Ductus arteriosus Mean blood flow velocity US.doppler
        "11677-2",  # Fetal Pulmonic valve Mean blood flow velocity US.doppler
        "11679-8",  # Fetal Left ventricular outflow tract Mean blood flow velocity US.doppler
        "11681-4",  # Fetal Right ventricular outflow tract Mean blood flow velocity US.doppler
        "11685-5",  # Fetal Main pulmonary artery Mean blood flow velocity US.doppler
        "11687-1",  # Fetal Umbilical artery at fetus Mean blood flow velocity US.doppler
        "11688-9",  # Fetal Umbilical artery at placenta Mean blood flow US.doppler
        "11689-7",  # Fetal Umbilical artery between fetus and placenta Mean blood flow US.doppler
        "11693-9",  # Fetal Aorta ascending Peak systolic flow velocity US.doppler
        "11695-4",  # Fetal Aorta descending Peak systolic flow velocity US.doppler
        "11697-0",  # Fetal Aortic arch Peak systolic flow velocity US.doppler
        "11699-6",  # Fetal Cerebral artery anterior Peak systolic flow velocity US.doppler
        "11701-0",  # Fetal Cerebral artery middle Peak systolic flow velocity US.doppler
        "11703-6",  # Fetal Ductus arteriosus Peak systolic flow velocity US.doppler
        "11705-1",  # Fetal Aortic valve Peak systolic flow velocity US.doppler
        "11707-7",  # Fetal Mitral valve Peak systolic flow velocity US.doppler
        "11709-3",  # Fetal Pulmonic valve Peak systolic flow velocity US.doppler
        "11711-9",  # Fetal Tricuspid valve Peak systolic flow velocity US.doppler
        "11713-5",  # Fetal Left ventricular outflow tract Peak systolic flow velocity US.doppler
        "11715-0",  # Fetal Right ventricular outflow tract Peak systolic flow velocity US.doppler
        "11719-2",  # Fetal Main pulmonary artery Peak systolic flow velocity US.doppler
        "11721-8",  # Fetal Umbilical artery at fetus Peak systolic flow velocity US.doppler
        "11722-6",  # Fetal Umbilical artery at placenta Peak systolic flow velocity US.doppler
        "11723-4",  # Fetal Umbilical artery between fetus and placenta Peak systolic flow velocity US.doppler
        "11727-5",  # Fetal Body weight estimated by US
        "11728-3",  # Fetal Body weight estimated from Abdominal circumference on US
        "11729-1",  # Fetal Body weight estimated from Abdominal circumference and Biparietal diameter on US
        "11730-9",  # Fetal Body weight estimated from Abdominal circumference and Biparietal diameter and Femur length on US
        "11731-7",  # Fetal Body weight estimated from Abdominal circumference and Biparietal diameter and Femur length and Head circumference on US
        "11732-5",  # Fetal Body weight estimated from Abdominal circumference and Biparietal diameter and Femur length and Head circumference on US by Hadlock 1985 method
        "11733-3",  # Fetal Body weight estimated from Abdominal circumference and Biparietal diameter and Femur length and Head circumference on US by Roberts 1985 method
        "11734-1",  # Fetal Body weight estimated from Abdominal circumference and Biparietal diameter and Femur length on US by Hadlock 1984 method
        "11735-8",  # Fetal Body weight estimated from Abdominal circumference and Biparietal diameter and Femur length on US by Hadlock 1985 method
        "11736-6",  # Fetal Body weight estimated from Abdominal circumference and Biparietal diameter and Femur length on US by Woo 1985 method
        "11737-4",  # Fetal Body weight estimated from Abdominal circumference and Biparietal diameter on US by Eik-Nes 1982 method
        "11738-2",  # Fetal Body weight estimated from Abdominal circumference and Biparietal diameter on US by Hadlock 1984 method
        "11739-0",  # Fetal Body weight estimated from Abdominal circumference and Biparietal diameter on US by Shepard 1982 method
        "11740-8",  # Fetal Body weight estimated from Abdominal circumference and Biparietal diameter on US by Thurnau 1983 method
        "11741-6",  # Fetal Body weight estimated from Abdominal circumference and Biparietal diameter on US by Warsof 1977 method
        "11742-4",  # Fetal Body weight estimated from Abdominal circumference and Biparietal diameter on US by Weinberger 1984 method
        "11743-2",  # Fetal Body weight estimated from Abdominal circumference and Femur length on US
        "11744-0",  # Fetal Body weight estimated from Abdominal circumference and Femur length and Head circumference on US
        "11745-7",  # Fetal Body weight estimated from Abdominal circumference and Femur length and Head circumference on US by Hadlock 1984 method
        "11746-5",  # Fetal Body weight estimated from Abdominal circumference and Femur length and Head circumference on US by Hadlock 1985 method
        "11747-3",  # Fetal Body weight estimated from Abdominal circumference and Femur length and Head circumference on US by Ott 1986 method
        "11748-1",  # Fetal Body weight estimated from Abdominal circumference and Femur length and Head circumference on US by Vintzileos 1987 method
        "11749-9",  # Fetal Body weight estimated from Abdominal circumference and Femur length and Head circumference on US by Weiner 1985 method
        "11750-7",  # Fetal Body weight estimated from Abdominal circumference and Femur length on US by Hadlock 1984 method
        "11751-5",  # Fetal Body weight estimated from Abdominal circumference and Femur length on US by Hadlock 1985 method
        "11752-3",  # Fetal Body weight estimated from Abdominal circumference and Femur length on US by Woo 1985 method
        "11753-1",  # Fetal Body weight estimated from Abdominal circumference and Head circumference on US
        "11754-9",  # Fetal Body weight estimated from Abdominal circumference and Head circumference on US by Hadlock 1984 method
        "11755-6",  # Fetal Body weight estimated from Abdominal circumference and Head circumference on US by Jordaan 1983 method
        "11756-4",  # Fetal Body weight estimated from Abdominal circumference on US by Campbell 1975 method
        "11757-2",  # Fetal Body weight estimated from Abdominal circumference on US by Vintzileos 1987 method
        "11758-0",  # Fetal Body weight estimated from Abdominal circumference on US by Warsof 1977 method
        "11759-8",  # Fetal Body weight estimated from Abdominal diameter and Biparietal diameter on US
        "11760-6",  # Fetal Body weight estimated from Abdominal diameter and Biparietal diameter and Femur length on US
        "11761-4",  # Fetal Body weight estimated from Abdominal diameter and Biparietal diameter and Femur length on US by Rose 1987 method
        "11762-2",  # Fetal Body weight estimated from Abdominal diameter and Biparietal diameter on US by Rose 1987 method
        "11763-0",  # Fetal Body weight estimated from Abdominal diameter and Biparietal diameter on US by Vintzileos 1987 method
        "11764-8",  # Fetal Body weight estimated from Abdominal diameter and Femur length on US
        "11765-5",  # Fetal Body weight estimated from Abdominal diameter and Femur length on US by Rose 1987 method
        "11766-3",  # Fetal Body weight percentile Per estimated gestational age
        "11767-1",  # Body weight percentile Comparison of estimated fetal weight with standard population distribution at same estimated gestational age
        "11768-9",  # Fetal Body weight percentile range Categorization by comparison with standards
        "11775-4",  # Fetal body weight estimation formula Narrative [Bibliographic Citation] Citation
        "11776-2",  # Gestational age estimation formula Narrative [Bibliographic Citation] Citation
        "11777-0",  # Fetal Abdomen [Area] Cross section derived by US
        "11782-0",  # Fetal Bowel Diameter US
        "11790-3",  # Fetal Colon lumen Diameter US
        "11792-9",  # Fetal Eye Diameter US
        "11794-5",  # Fetal Aortic valve Diameter US
        "11796-0",  # Fetal Mitral valve Diameter US
        "11798-6",  # Fetal Pulmonic valve Diameter US
        "11800-0",  # Fetal Tricuspid valve Diameter US
        "11802-6",  # Fetal Left ventricular outflow tract Diameter US.doppler
        "11804-2",  # Fetal Right ventricular outflow tract Diameter US
        "11806-7",  # Fetal Pulmonary artery Diameter US
        "11808-3",  # Fetal Renal pelvis - left Diameter US
        "11810-9",  # Fetal Renal pelvis - right Diameter US
        "11812-5",  # Fetal Small bowel Diameter US
        "11814-1",  # Fetal Umbilical vein Diameter US
        "11815-8",  # Fetal Urinary bladder Diameter US
        "11816-6",  # Fetal Yolk sac Diameter US
        "11817-4",  # Fetal Amniotic fluid space Diameter largest pocket US
        "11818-2",  # Fetal Abdomen Diameter.anterior-posterior US
        "11819-0",  # Fetal Thorax Diameter.anterior-posterior US
        "11820-8",  # Fetal Head Diameter.biparietal US
        "11821-6",  # Fetal Head Mean biparietal diameter Estimated from gestational age
        "11822-4",  # Fetal Head Mean biparietal diameter estimated from Cerebellar diameter (US)
        "11823-2",  # Fetal Head Diameter.biparietal/Diameter.occipital derived by US
        "11824-0",  # Fetal Head Diameter.BPD.area-corrected derived by US
        "11825-7",  # Fetal Kidney - left Hilum-cortex diameter US
        "11827-3",  # Fetal Kidney - right Hilum-cortex diameter US
        "11831-5",  # Fetal Kidney Mean width Estimated from gestational age
        "11832-3",  # Fetal Amniotic fluid space Maximum diameter largest pocket US
        "11833-1",  # Fetal Amniotic fluid space Mean diameter largest pocket US
        "11834-9",  # Fetal Kidney - left Longitudinal diameter US
        "11836-4",  # Fetal Kidney - right Longitudinal diameter US
        "11838-0",  # Fetal Liver Longitudinal diameter US
        "11843-0",  # Fetal Kidney Mean longitudinal diameter Estimated from gestational age
        "11844-8",  # Fetal Liver Mean longitudinal diameter Estimated from abdominal circumference
        "11845-5",  # Fetal Liver Mean longitudinal diameter Estimated from gestational age
        "11849-7",  # Fetal Abdomen Mean diameter Estimated from gestational age
        "11851-3",  # Fetal Head Diameter.occipito-frontal US
        "11852-1",  # Fetal Head Diameter.outer to outer US
        "11853-9",  # Fetal Kidney - left Thickeness US
        "11855-4",  # Fetal Kidney - right Thickeness US
        "11860-4",  # Fetal Cisterna magna Diameter.sagittal US
        "11861-2",  # Fetal Cisterna magna Mean sagittal diameter Estimated from gestational age
        "11862-0",  # Fetal Abdomen Diameter transverse US
        "11863-8",  # Fetal Cerebellum Diameter transverse US
        "11864-6",  # Fetal Thorax Diameter transverse US
        "11866-1",  # Fetal Cerebellum Mean transverse diameter Estimated from gestational age
        "11868-7",  # Fetal body weight estimation formula Narrative [Equation] Equation
        "11869-5",  # Gestational age estimation formula Narrative [Equation] Equation
        "11871-1",  # Fetal Femur length/Abdominal circumference derived by US
        "11872-9",  # Fetal Femur length/Biparietal diameter derived by US
        "11873-7",  # Fetal Femur length/Head circumference derived by US
        "11874-5",  # Fetal position palpation
        "11875-2",  # Fetal position US
        "11876-0",  # Fetal presentation palpation
        "11877-8",  # Fetal presentation US
        "11878-6",  # Number of fetuses by US
        "11882-8",  # Fetal Sex US
        "11883-6",  # Fetal Narrative Sex US
        "11884-4",  # Gestational age Estimated
        "11885-1",  # Gestational age Estimated from last menstrual period
        "11886-9",  # Gestational age Estimated from ovulation date
        "11887-7",  # Gestational age Estimated from selected delivery date
        "11888-5",  # Gestational age US composite estimate
        "11889-3",  # Gestational age estimated from Abdominal circumference on US
        "11890-1",  # Gestational age estimated from Abdominal circumference on US by Campbell 1975 method
        "11891-9",  # Gestational age estimated from Abdominal circumference on US by Hadlock 1982 method
        "11892-7",  # Gestational age estimated from Abdominal circumference on US by Hadlock 1984 method
        "11893-5",  # Gestational age estimated from Abdominal circumference on US by Jeanty 1984 method
        "11894-3",  # Gestational age estimated from area corrected Biparietal circumference (US)
        "11895-0",  # Gestational age estimated from Binocular distance on US
        "11896-8",  # Gestational age estimated from Binocular distance on US by Jeanty 1984 method
        "11897-6",  # Gestational age estimated from Biparietal circumference (US)
        "11898-4",  # Gestational age estimated from Biparietal diameter on US
        "11899-2",  # Gestational age estimated from Biparietal diameter on US by Campbell 1975 method
        "11900-8",  # Gestational age estimated from Biparietal diameter on US by Doubilet 1993 method
        "11901-6",  # Gestational age estimated from Biparietal diameter on US by Hadlock 1982 method
        "11902-4",  # Gestational age estimated from Biparietal diameter on US by Hadlock 1984 method
        "11903-2",  # Gestational age estimated from Biparietal diameter on US by Hansmann 1985 method
        "11904-0",  # Gestational age estimated from Biparietal diameter on US by Hobbins 1983 method
        "11905-7",  # Gestational age estimated from Biparietal diameter on US by Jeanty 1984 method
        "11906-5",  # Gestational age estimated from Biparietal diameter on US by Kurtz 1980 method
        "11907-3",  # Gestational age estimated from Biparietal diameter on US by Sabbagha 1978 method
        "11908-1",  # Gestational age estimated from Cerebellar diameter by method of Goldstein 1987 (US)
        "11909-9",  # Gestational age estimated from Crown rump length on US
        "11910-7",  # Gestational age estimated from Crown rump length on US by Hadlock 1992 method
        "11911-5",  # Gestational age estimated from Crown rump length on US by Hansmann 1985 method
        "11912-3",  # Gestational age estimated from Crown rump length on US by Jeanty 1984 method
        "11913-1",  # Gestational age estimated from Crown rump length on US by Nelson 1981 method
        "11914-9",  # Gestational age estimated from Crown rump length on US by Robinson 1975 method
        "11915-6",  # Gestational age estimated from Crown rump length on US by Yeh 1988 method
        "11916-4",  # Gestational age estimated from Fibula length (US)
        "11917-2",  # Gestational age estimated from Fibula length by method of Jeanty 1984 (US)
        "11918-0",  # Gestational age estimated from Fibula length by method of Merz 1987 (US)
        "11919-8",  # Gestational age estimated from Femur length on US
        "11920-6",  # Gestational age estimated from Femur length on US by Hadlock 1984 method
        "11921-4",  # Gestational age estimated from Femur length on US by Hansmann 1985 method
        "11922-2",  # Gestational age estimated from Femur length on US by Hohler 1982 method
        "11923-0",  # Gestational age estimated from Femur length on US by Jeanty 1984 method
        "11924-8",  # Gestational age estimated from Femur length on US by Merz 1987 method
        "11925-5",  # Gestational age estimated from Femur length on US by Obrien 1982 method
        "11926-3",  # Gestational age estimated from Foot length on US by Mercer 1987 method
        "11927-1",  # Gestational age estimated from Gestational sac diameter on US
        "11928-9",  # Gestational age estimated from Gestational sac diameter on US by Hellman 1969 method
        "11929-7",  # Gestational age estimated from Gestational sac diameter on US by Rempen 1991 method
        "11930-5",  # Gestational age estimated from Head circumference on US
        "11931-3",  # Gestational age estimated from Head circumference on US by Hadlock 1982 method
        "11932-1",  # Gestational age estimated from Head circumference on US by Hadlock 1984 method
        "11933-9",  # Gestational age estimated from Head circumference on US by Hoffbauer 1979 method
        "11934-7",  # Gestational age estimated from Head circumference on US by Jeanty 1984 method
        "11935-4",  # Gestational age estimated from Humerus length on US
        "11936-2",  # Gestational age estimated from Humerus length on US by Jeanty 1984 method
        "11937-0",  # Gestational age estimated from Humerus length on US by Merz 1987 method
        "11938-8",  # Gestational age estimated from Radius length (US)
        "11939-6",  # Gestational age estimated from Radius length by method of Merz 1987 (US)
        "11940-4",  # Gestational age estimated from Tibia length on US
        "11941-2",  # Gestational age estimated from Tibia length on US by Jeanty 1984 method
        "11942-0",  # Gestational age estimated from Tibia length on US by Merz 1987 method
        "11943-8",  # Gestational age estimated from Ulna length (US)
        "11944-6",  # Gestational age estimated from Ulna length by method of Jeanty 1984 (US)
        "11945-3",  # Gestational age estimated from Ulna length by method of Merz 1987 (US)
        "11946-1",  # Fetal Placenta Grade US
        "11947-9",  # Head circumference/Abdominal circumference derived by US
        "11948-7",  # Fetal Heart rate US
        "11949-5",  # Fetal Identification criteria US
        "11950-3",  # Fetal Narrative Identification criteria US
        "11951-1",  # Fetal [Identifier] Identifier
        "11952-9",  # Fetal Umbilical cord.placenta Narrative Insertion site US
        "11954-5",  # Fetal Kidney length/Abdominal circumference derived by US
        "11956-0",  # Fetal Head Lateral ventricular body width/Hemispheric width derived by US
        "11957-8",  # Fetal Crown Rump length US
        "11962-8",  # Fetal Clavicle diaphysis [Length] US
        "11963-6",  # Fetal Femur diaphysis [Length] US
        "11964-4",  # Fetal Fibula diaphysis [Length] US
        "11965-1",  # Fetal Foot [Length] US
        "11966-9",  # Fetal Humerus diaphysis [Length] US
        "11967-7",  # Fetal Radius diaphysis [Length] US
        "11968-5",  # Fetal Tibia diaphysis [Length] US
        "11969-3",  # Fetal Ulna diaphysis [Length] US
        "11970-1",  # Fetal Femur diaphysis [Length] mean Estimated from gestational age.Merz. 1987
        "11971-9",  # Fetal Fibula diaphysis [Length] mean Estimated from gestational age.Merz. 1987
        "11972-7",  # Fetal Humerus diaphysis [Length] mean Estimated from gestational age.Merz. 1987
        "11973-5",  # Fetal Radius diaphysis [Length] mean Estimated from gestational age.Merz. 1987
        "11974-3",  # Fetal Tibia diaphysis [Length] mean Estimated from gestational age.Merz. 1987
        "11975-0",  # Fetal Ulna diaphysis [Length] mean Estimated from gestational age.Merz. 1987
        "11978-4",  # Fetal Abdomen Circumference derived by US
        "11979-2",  # Fetal Abdomen Circumference US
        "11980-0",  # Fetal Abdomen Circumference measured by ellipse overlay (US)
        "11981-8",  # Fetal Abdomen Circumference US.traced
        "11982-6",  # Fetal Head Circumference derived from occipital-frontal diameter and outer-outer transaxial diameter (US)
        "11983-4",  # Fetal Head Circumference derived from occipital-frontal diameter and outer-inner biparietal diameter (US)
        "11984-2",  # Fetal Head Circumference US
        "11985-9",  # Fetal Head Circumference measured by ellipse overlay (US)
        "11986-7",  # Fetal Head Circumference US.traced
        "11987-5",  # Fetal Thorax Circumference derived by US
        "11988-3",  # Fetal Thorax Circumference US
        "11989-1",  # Fetal Thorax Circumference measured by ellipse overlay (US)
        "11990-9",  # Fetal Thorax Circumference US.traced
        "11991-7",  # Fetal Abdomen Mean perimeter Estimated from gestational age
        "11992-5",  # Fetal Heart position US
        "11993-3",  # Fetal Narrative Heart position US
        "11997-4",  # Fetal Cerebral artery anterior Pulsatility index US.doppler
        "11999-0",  # Fetal Cerebral artery middle Pulsatility index US.doppler
        "12003-0",  # Fetal Umbilical artery at fetus Pulsatility index US.doppler
        "12004-8",  # Fetal Umbilical artery at placenta Pulsatility index US.doppler
        "12005-5",  # Fetal Umbilical artery between fetus and placenta Pulsatility index US.doppler
        "12009-7",  # Fetal Heart R-R duration US
        "12012-1",  # Fetal Cerebral artery anterior Resistivity index US.doppler
        "12018-8",  # Fetal Umbilical artery at fetus Resistivity index US.doppler
        "12019-6",  # Fetal Umbilical artery at placenta Resistivity index US.doppler
        "12020-4",  # Fetal Umbilical artery between fetus and placenta Resistivity index US.doppler
        "12028-7",  # Fetal Abdomen Study observation US
        "12029-5",  # Fetal Abdomen Narrative Study observation US
        "12030-3",  # Fetal Abdominal wall Study observation US
        "12031-1",  # Fetal Abdominal wall Narrative Study observation US
        "12032-9",  # Fetal Aorta ascending Study observation US
        "12033-7",  # Fetal Aorta ascending Narrative Study observation US
        "12034-5",  # Fetal Aorta descending Study observation US
        "12035-2",  # Fetal Aorta descending Narrative Study observation US
        "12036-0",  # Fetal Aorta Study observation US
        "12037-8",  # Fetal Aorta Narrative Study observation US
        "12038-6",  # Fetal Aortic arch Study observation US
        "12039-4",  # Fetal Aortic arch Narrative Study observation US
        "12040-2",  # Fetal Cerebellum Study observation US
        "12041-0",  # Fetal Cerebellum Narrative Study observation US
        "12042-8",  # Fetal Cerebrum Study observation US
        "12043-6",  # Fetal Cerebrum Narrative Study observation US
        "12047-7",  # Fetal Colon Study observation US
        "12048-5",  # Fetal Colon Narrative Study observation US
        "12049-3",  # Fetal Cranium Study observation US
        "12050-1",  # Fetal Cranium Narrative Study observation US
        "12051-9",  # Fetal Diaphragm Study observation US
        "12052-7",  # Fetal Diaphragm Narrative Study observation US
        "12053-5",  # Fetal ductal arch Study observation US
        "12054-3",  # Fetal ductal arch Narrative Study observation US
        "12055-0",  # Fetal Face Study observation US
        "12056-8",  # Fetal Face Narrative Study observation US
        "12057-6",  # Fetal Choroid plexus Study observation US
        "12058-4",  # Fetal Choroid plexus Narrative Study observation US
        "12059-2",  # Fetal Fourth ventricle Study observation US
        "12060-0",  # Fetal Fourth ventricle Narrative Study observation US
        "12061-8",  # Fetal Intracranial anatomy Study observation US
        "12062-6",  # Fetal Intracranial anatomy Narrative Study observation US
        "12063-4",  # Fetal Lateral cerebral ventricles Study observation US
        "12064-2",  # Fetal Lateral cerebral ventricles Narrative Study observation US
        "12065-9",  # Fetal Posterior fossa Study observation US
        "12066-7",  # Fetal Posterior fossa Narrative Study observation US
        "12067-5",  # Fetal Head Third Ventricle Study observation US
        "12068-3",  # Fetal Head Third Ventricle Narrative Study observation US
        "12069-1",  # Fetal Head Study observation US
        "12070-9",  # Fetal Head Narrative Study observation US
        "12071-7",  # Fetal Aortic valve Study observation US
        "12072-5",  # Fetal Aortic valve Narrative Study observation US
        "12073-3",  # Fetal Atrium Study observation US
        "12074-1",  # Fetal Atrium Narrative Study observation US
        "12075-8",  # Fetal Heart chambers Study observation US
        "12076-6",  # Fetal Heart chambers Narrative Study observation US
        "12077-4",  # Fetal Heart great vessels Study observation US
        "12078-2",  # Fetal Heart great vessels Narrative Study observation US
        "12079-0",  # Fetal Interventricular septum Study observation US
        "12080-8",  # Fetal Interventricular septum Narrative Study observation US
        "12081-6",  # Fetal Mitral valve Study observation US
        "12082-4",  # Fetal Mitral valve Narrative Study observation US
        "12083-2",  # Fetal Pulmonic valve Study observation US
        "12084-0",  # Fetal Tricuspid valve Study observation US
        "12085-7",  # Fetal Tricuspid valve Narrative Study observation US
        "12086-5",  # Fetal Heart valves Study observation US
        "12087-3",  # Fetal Heart valves Narrative Study observation US
        "12088-1",  # Fetal Left ventricular outflow tract Study observation US
        "12089-9",  # Fetal Left ventricular outflow tract Narrative Study observation US
        "12090-7",  # Fetal Right ventricular outflow tract Study observation US
        "12091-5",  # Fetal Right ventricular outflow tract Narrative Study observation US
        "12092-3",  # Fetal Intestine Study observation US
        "12093-1",  # Fetal Intestine Narrative Study observation US
        "12094-9",  # Fetal Kidney - left Study observation US
        "12095-6",  # Fetal Kidney - left Narrative Study observation US
        "12096-4",  # Fetal Kidney - right Study observation US
        "12097-2",  # Fetal Kidney - right Narrative Study observation US
        "12098-0",  # Fetal Kidney Study observation US
        "12099-8",  # Fetal Kidney Narrative Study observation US
        "12100-4",  # Fetal Limbs Study observation US
        "12101-2",  # Fetal Limbs Narrative Study observation US
        "12102-0",  # Fetal Nuchal fold Study observation US
        "12103-8",  # Fetal Nuchal fold Narrative Study observation US
        "12104-6",  # Fetal Pulmonary artery Study observation US
        "12105-3",  # Fetal Pulmonary artery Narrative Study observation US
        "12106-1",  # Fetal Pulmonary vein Study observation US
        "12107-9",  # Fetal Pulmonary vein Narrative Study observation US
        "12108-7",  # Fetal Small bowel Study observation US
        "12109-5",  # Fetal Small bowel Narrative Study observation US
        "12110-3",  # Fetal Spine Study observation US
        "12111-1",  # Fetal Spine Narrative Study observation US
        "12112-9",  # Fetal Stomach Study observation US
        "12113-7",  # Fetal Stomach Narrative Study observation US
        "12114-5",  # Fetal Thorax Study observation US
        "12115-2",  # Fetal Thorax Narrative Study observation US
        "12116-0",  # Fetal Umbilical cord Study observation US
        "12117-8",  # Fetal Umbilical cord Narrative Study observation US
        "12118-6",  # Fetal Urinary bladder Study observation US
        "12119-4",  # Fetal Urinary bladder Narrative Study observation US
        "12120-2",  # Fetal Inferior vena cava Study observation US
        "12121-0",  # Fetal Inferior vena cava Narrative Study observation US
        "12122-8",  # Fetal Superior vena cava Study observation US
        "12123-6",  # Fetal Superior vena cava Narrative Study observation US
        "12124-4",  # Fetal Vena cava Study observation US
        "12125-1",  # Fetal Vena cava Narrative Study observation US
        "12128-5",  # Fetal Yolk sac Narrative Study observation US
        "12129-3",  # Fetal [Interpretation] Study observation general US
        "12130-1",  # Fetal Narrative [Interpretation] Study observation general US
        "12133-5",  # Fetal Cerebral artery anterior Systolic flow/Diastolic flow US.doppler
        "12135-0",  # Fetal Cerebral artery middle Systolic flow/Diastolic flow US.doppler
        "12139-2",  # Fetal Umbilical artery at fetus Systolic flow/Diastolic flow US.doppler
        "12140-0",  # Fetal Umbilical artery at placenta Systolic flow/Diastolic flow US.doppler
        "12141-8",  # Fetal Umbilical artery between fetus and placenta Systolic flow/Diastolic flow US.doppler
        "12146-7",  # Fetal Nuchal fold Thickness US
        "12147-5",  # Fetal Placenta Thickness US
        "12148-3",  # Fetal Interventricular septum Thickness diastolic US.M-mode+Measured
        "12149-1",  # Fetal Interventricular septum Thickness diastolic Measured by real time two dimension US
        "12150-9",  # Fetal Left ventricular posterior wall Thickness diastolic US.M-mode+Measured
        "12151-7",  # Fetal Left ventricular posterior wall Thickness diastolic Measured by real time two dimension US
        "12152-5",  # Fetal Interventricular septum Thickness.systolic US.M-mode+Measured
        "12153-3",  # Fetal Interventricular septum Thickness.systolic Measured by real time two dimension US
        "12154-1",  # Fetal Left ventricular posterior wall Thickness.systolic US.M-mode+Measured
        "12155-8",  # Fetal Left ventricular posterior wall Thickness.systolic Measured by real time two dimension US
        "12162-4",  # Fetal Kidney - left Volume derived by US
        "12163-2",  # Fetal Kidney - right Volume derived by US
        "12166-5",  # Fetal Yolk sac Volume US
        "12167-3",  # Fetal Amniotic fluid space [Interpretation] Volume.amniotic fluid US
        "12168-1",  # Fetal Urinary bladder Volume post void US
        "12169-9",  # Fetal Urinary bladder Volume.pre void US
        "12170-7",  # Fetal Head Hemisphere width US
        "12171-5",  # Fetal Lateral cerebral ventricles Transverse width US
        "18185-9",  # Gestational age
        "18847-4",  # Narrative Fetal position palpation
        "18848-2",  # Narrative Fetal position US
        "18849-0",  # Narrative Fetal presentation palpation
        "18850-8",  # Narrative Fetal presentation US
        "18851-6",  # Fetal Placenta Grade US (narrative)
        "21299-3",  # Gestational age method
        "24537-3",  # US Guidance for aspiration of amniotic fluid of Uterus
        "30707-4",  # Fetal Narrative [Interpretation] Study observation.general.follow-up US
        "30708-2",  # Fetal Narrative [Interpretation] Study observation.general.limited US
        "33068-8",  # Fetal Thoracic area US
        "33069-6",  # Fetal nuchal translucency measured by US
        "33070-4",  # Fetal Orbit - bilateral Diameter.inner orbital US
        "33071-2",  # Fetal Spine Length from T6 to L3 US
        "33072-0",  # Gestational age estimated from Abdominal circumference on US by Australian Society of Ultrasound Medicine 2000 method
        "33073-8",  # Gestational age estimated from Abdominal circumference on US by Hansmann 1985 method
        "33074-6",  # Gestational age estimated from Abdominal circumference on US by Lessoway 1998 method
        "33075-3",  # Gestational age estimated from Abdominal circumference on US by Merz 1988 method
        "33076-1",  # Gestational age estimated from Abdominal circumference on US by Shinozuka 1996 method
        "33077-9",  # Gestational age estimated from Anterior-posterior diameter of the abdomen by method of Lessoway 1998 (US)
        "33078-7",  # Gestational age estimated from AXT by method of Shinozuka 1996 (US)
        "33079-5",  # Gestational age estimated from Biparietal diameter on US by Australian Society of Ultrasound Medicine 1989 method
        "33080-3",  # Gestational age estimated from Biparietal diameter on US by Lessoway 1998 method
        "33081-1",  # Gestational age estimated from Biparietal diameter on US by Merz 1988 method
        "33082-9",  # Gestational age estimated from Biparietal diameter on US by Osaka 1989 method
        "33083-7",  # Gestational age estimated from Biparietal diameter on US by Rempen 1991 method
        "33084-5",  # Gestational age estimated from Biparietal diameter on US by Shinozuka 1996 method
        "33085-2",  # Gestational age estimated from Biparietal diameter on US by Tokyo 1986 method
        "33086-0",  # Gestational age estimated from Outer-Inner Biparietal diameter on US by Chitty 1997 method
        "33087-8",  # Gestational age estimated from Outer-Outer Biparietal diameter on US by Chitty 1997 method
        "33088-6",  # Gestational age estimated from clavicle length by method of Yarkoni 1985 (US)
        "33089-4",  # Gestational age estimated from Crown rump length on US by Australian Society of Ultrasound Medicine 1991 method
        "33090-2",  # Gestational age estimated from Crown rump length on US by Australian Society of Ultrasound Medicine 2000 method
        "33091-0",  # Gestational age estimated from Crown rump length on US by Daya 1993 method
        "33092-8",  # Gestational age estimated from Crown rump length on US by Jeanty 1982 method
        "33093-6",  # Gestational age estimated from Crown rump length on US by Osaka 1989 method
        "33094-4",  # Gestational age estimated from Crown rump length on US by Rempen 1991 method
        "33095-1",  # Gestational age estimated from Crown rump length on US by Shinozuka 1996 method
        "33096-9",  # Gestational age estimated from Crown rump length on US by Tokyo 1986 method
        "33097-7",  # Gestational age estimated from Fibula length by method of Jeanty 1983 (US)
        "33098-5",  # Gestational age estimated from Femur length on US by Chitty 1997 method
        "33099-3",  # Gestational age estimated from Femur length on US by Jeanty 1982 method
        "33100-9",  # Gestational age estimated from Femur length on US by Lessoway 1998 method
        "33101-7",  # Gestational age estimated from Femur length on US by Osaka 1989 method
        "33102-5",  # Gestational age estimated from Femur length on US by Shinozuka 1996 method
        "33103-3",  # Gestational age estimated from Femur length on US by Tokyo 1986 method
        "33104-1",  # Gestational age estimated from Gestational sac diameter on US by Daya 1991 method
        "33105-8",  # Gestational age estimated from Gestational sac length on US by Hansmann 1979 method
        "33106-6",  # Gestational age estimated from Gestational sac diameter on US by Hansmann 1982 method
        "33107-4",  # Gestational age estimated from Gestational sac length on US by Nyberg 1992 method
        "33108-2",  # Gestational age estimated from Gestational sac diameter on US by Tokyo 1986 method
        "33109-0",  # Gestational age estimated from Head circumference on US by Australian Society of Ultrasound Medicine 2000 method
        "33110-8",  # Gestational age estimated from Head circumference measured on US by Chitty 1997 method
        "33111-6",  # Gestational age estimated from Head circumference derived on US by Chitty 1997 method
        "33112-4",  # Gestational age estimated from Head circumference on US by Hansmann 1985 method
        "33113-2",  # Gestational age estimated from Head circumference on US by Jeanty 1982 method
        "33114-0",  # Gestational age estimated from Head circumference on US by Lessoway 1998 method
        "33115-7",  # Gestational age estimated from Head circumference on US by Merz 1988 method
        "33116-5",  # Gestational age estimated from Humerus length on US by Australian Society of Ultrasound Medicine 2000 method
        "33117-3",  # Gestational age estimated from Humerus length on US by Osaka 1989 method
        "33118-1",  # Gestational age estimated from length of vertebra by method of Tokyo 1986 (US)
        "33119-9",  # Gestational age estimated from Occipital-frontal diameter on US by Australian Society of Ultrasound Medicine 2000 method
        "33120-7",  # Gestational age estimated from Occipital-frontal diameter on US by Hansmann 1986 method
        "33121-5",  # Gestational age estimated from Occipital-frontal diameter on US by Lessoway 1998 method
        "33122-3",  # Gestational age estimated from Inter ocular distance on US by Mayden 1982 method
        "33123-1",  # Gestational age estimated from Inter ocular distance on US by Trout 1994 method
        "33124-9",  # Gestational age estimated from Outer orbital distance on US by Mayden 1982 method
        "33125-6",  # Gestational age estimated from Outer orbital distance on US by Trout 1994 method
        "33126-4",  # Gestational age estimated from Radius length by method of Jeanty 1983 (US)
        "33127-2",  # Gestational age estimated from Spine length by method of Tokyo 1989 (US)
        "33128-0",  # Gestational age estimated from Transverse abdominal diameter on US by Eriksen 1985 method
        "33129-8",  # Gestational age estimated from Transverse abdominal diameter on US by Hansmann 1979 method
        "33130-6",  # Gestational age estimated from Transverse abdominal diameter on US by Tokyo 1986 method
        "33131-4",  # Gestational age estimated from Thoracic circumference on US by Chitkara 1987 method
        "33132-2",  # Gestational age estimated from Transverse cerebral diameter on US by Chitty 1994 method
        "33133-0",  # Gestational age estimated from Transverse cerebral diameter on US by Goldstein 1987 method
        "33134-8",  # Gestational age estimated from Transverse cerebral diameter on US by Hill 1990 method
        "33135-5",  # Gestational age estimated from Thoracic circumference on US by Nimrod 1986 method
        "33136-3",  # Gestational age estimated from Transverse abdominal diameter on US by Hansmann 1985 method
        "33137-1",  # Gestational age estimated from Transverse abdominal diameter on US by Lessoway 1998 method
        "33138-9",  # Gestational age estimated from Fetal trunk area by method of Osaka 1989 (US)
        "33139-7",  # Fetal Body weight estimated from Biparietal diameter and Transverse thoracic diameter on US by Hansmann 1986 method
        "33140-5",  # Fetal Body weight estimated from Biparietal diameter and Fetal trunk area and Femur length on US by Osaka 1990 method
        "33141-3",  # Fetal weight estimated by method of Shinozuka formula 1 1996 (US)
        "33142-1",  # Fetal weight estimated by method of Shinozuka formula 2 1996 (US)
        "33143-9",  # Fetal weight estimated by method of Shinozuka formula 3 1996 (US)
        "33144-7",  # Fetal Body weight estimated on US by Tokyo 1987 method
        "33145-4",  # Fetal Abdomen Circumference estimated from gestational age by method of Australian Society of Ultrasound Medicine 2000 (US)
        "33146-2",  # Fetal Abdomen Circumference estimated from gestational age by method of Hadlock 1984 (US)
        "33147-0",  # Fetal Abdomen Circumference measured by method of Chitty 1994 (US)
        "33148-8",  # Fetal Abdomen Circumference estimated from gestational age by method of Merz 1988 (US)
        "33149-6",  # Fetal Abdomen Circumference estimated from gestational age by method of Shinozuka 1996 (US)
        "33150-4",  # Fetal Abdomen Diameter product estimated from gestational age by method of Shinozuka 1996 (US)
        "33151-2",  # Fetal Head Diameter.biparietal estimated from gestational age by method of Australian Society of Ultrasound Medicine 2000 (US)
        "33152-0",  # Fetal Head Diameter.biparietal outer to outer estimated from gestational age by method of Chitty 1994 (US)
        "33153-8",  # Fetal Head Diameter.biparietal estimated from gestational age by method of Jeanty 1982 (US)
        "33154-6",  # Fetal Head Diameter.biparietal estimated from gestational age by method of Merz 1988 (US)
        "33155-3",  # Fetal Head Diameter.biparietal estimated from gestational age by method of Rempen 1991 (US)
        "33156-1",  # Fetal Head Diameter.biparietal estimated from gestational age by method of Shinozuka 1996 (US)
        "33157-9",  # Fetal Head Diameter.biparietal/Diameter.occipital estimated from gestational age by method of Chitty 1994 (US)
        "33158-7",  # Fetal Head Diameter.biparietal/Diameter.occipital estimated from gestational age by method of Hadlock 1981 (US)
        "33159-5",  # Fetal Crown Rump length estimated from gestational age by method of Australian Society of Ultrasound Medicine 2000 (US)
        "33160-3",  # Fetal Crown Rump length estimated from gestational age by method of Rempen 1991 (US)
        "33161-1",  # Fetal Crown Rump length estimated from gestational age by method of Shinozuka 1996 (US)
        "33162-9",  # Fetal Body weight US+Estimated from Hadlock 1991
        "33163-7",  # Fetal weight estimated from gestational age by method of Hansmann 1986 (US)
        "33164-5",  # Fetal Fibula diaphysis [Length] estimated from gestational age by method of Jeanty 1983 (US)
        "33165-2",  # Fetal Femur diaphysis [Length] estimated from gestational age by method of Australian Society of Ultrasound Medicine 2000 (US)
        "33166-0",  # Fetal Femur diaphysis [Length] estimated from gestational age by method of Hadlock 1984 (US)
        "33167-8",  # Fetal Femur diaphysis [Length] estimated from gestational age by method of Chitty 1994 (US)
        "33168-6",  # Fetal Femur diaphysis [Length] estimated from gestational age by method of Jeanty 1982 (US)
        "33169-4",  # Fetal Femur diaphysis [Length] estimated from gestational age by method of Merz 1988 (US)
        "33170-2",  # Fetal Femur diaphysis [Length] estimated from gestational age by method of Shinozuka 1996 (US)
        "33172-8",  # Fetal Head Circumference estimated from gestational age by method of Australian Society of Ultrasound Medicine 2000 (US)
        "33173-6",  # Fetal Head Circumference estimated from gestational age by method of Hadlock 1984 (US)
        "33174-4",  # Fetal Head Circumference estimated from gestational age by method of Chitty 1994 (US)
        "33175-1",  # Fetal Head Circumference estimated from gestational age by method of Jeanty 1982 (US)
        "33176-9",  # Fetal Head Circumference estimated from gestational age by method of Merz 1988 (US)
        "33177-7",  # Fetal Humerus diaphysis [Length] estimated from gestational age by method of Australian Society of Ultrasound Medicine 2000 (US)
        "33178-5",  # Occipital frontal diameter estimated from gestational age by method of Australian Society of Ultrasound Medicine 2000 (US)
        "33179-3",  # Occipital frontal diameter estimated from gestational age by method of Chitty 1994 (US)
        "33180-1",  # Fetal Radius diaphysis [Length] estimated from gestational age by method of Jeanty 1983 (US)
        "33181-9",  # Fetal Cerebellum Diameter transverse estimated from gestational age by method of Goldstein 1987 (US)
        "33184-3",  # Fetal body weight growth percentile estimated from gestational age by method of Williams 1982 (US)
        "33185-0",  # Fetal body weight growth percentile estimated from gestational age by method of Alexander 1996 (US)
        "33186-8",  # Fetal body weight growth percentile by method of Arbuckle 1993 male singleton (US)
        "33187-6",  # Fetal body weight growth percentile by method of Arbuckle 1993 female singleton (US)
        "33188-4",  # Fetal body weight growth percentile by method of Arbuckle 1993 female twins (US)
        "33189-2",  # Fetal body weight growth percentile estimated from gestational age by method of Brenner 1976 (US)
        "33190-0",  # Fetal body weight growth percentile estimated from gestational age by method of Hadlock 1985 (US)
        "33191-8",  # Fetal Thorax Diameter product derived by US
        "33196-7",  # Fetal Lateral cerebral ventricles Posterior horn width US
        "33197-5",  # Fetal Lateral cerebral ventricles Anterior horn width US
        "33198-3",  # Fetal Head Diameter.biparietal estimated from gestational age by method of Hadlock 1984 (US)
        "33199-1",  # Fetal body weight growth percentile by method of Arbuckle 1993 male twins (US)
        "33537-2",  # Gestational age estimated from Abdominal circumference on US by Jeanty 1982 method
        "33538-0",  # Gestational age estimated from Biparietal diameter on US by Hansmann 1986 method
        "33539-8",  # Gestational age estimated from Biparietal diameter on US by Jeanty 1982 method
        "33540-6",  # Gestational age estimated from Crown rump length on US by Hansmann 1986 method
        "33541-4",  # Gestational age estimated from Femur length on US by Hansmann 1986 method
        "33542-2",  # Gestational age Estimated from FL.Merz 1988
        "33543-0",  # Gestational age estimated from Head circumference on US by Hansmann 1986 method
        "33544-8",  # Gestational age estimated from Occipital-frontal diameter on US by Hansmann 1985 method
        "33545-5",  # Gestational age estimated from Binocular distance on US by Jeanty 1982 method
        "33546-3",  # Fetal Abdomen Circumference derived by method of Chitty 1994 (US)
        "33556-2",  # Fetal Head Diameter.biparietal outer to inner estimated from gestational age by method of Chitty 1994 (US)
        "42138-8",  # US Guidance for localization of placenta
        "42451-5",  # Fetal Narrative [Interpretation] Study observation.general transvaginal 1st trimester US
        "42452-3",  # Fetal Narrative [Interpretation] Study observation.general 1st trimester US
        "42453-1",  # Fetal Narrative [Interpretation] Study observation.general 2nd trimester US
        "42454-9",  # Fetal Narrative [Interpretation] Study observation.general 3rd trimester US
        "42464-8",  # Fetal Narrative [Interpretation] Study observation.general 1st trimester, multiple fetuses US
        "42465-5",  # Fetal Narrative [Interpretation] Study observation.general 2nd trimester, multiple fetuses US
        "42466-3",  # Fetal Narrative [Interpretation] Study observation.general 3rd trimester, multiple fetuses US
        "42467-1",  # Fetal Narrative [Interpretation] Study observation.general.limited, multiple fetuses US
        "42479-6",  # Fetal Narrative [Interpretation] Study observation general, multiple fetuses US
        "49035-9",  # Fetal Nuchal fold [Multiple of the median] Thickness US
        "49051-6",  # Gestational age in weeks
        "49052-4",  # Gestational age in days
        "49508-5",  # Fetal Narrative [Interpretation] Study observation general US.doppler
        "49513-5",  # Fetal Abdomen Narrative Study observation, multiple fetuses US
        "53655-7",  # Fetal Heart Diameter transverse US
        "53656-5",  # Fetal Heart Diameter.anterior-posterior US
        "53657-3",  # Fetal Heart Circumference US
        "53658-1",  # Fetal Aorta Diameter US
        "53659-9",  # Fetal Cerebral artery middle Mean blood flow velocity US.doppler
        "53660-7",  # Fetal Heart Narrative Study observation US
        "53667-2",  # Method of best overall fetal weight estimate
        "53668-0",  # Fetal Ear - right Maximum length US
        "53669-8",  # Fetal Right eye Diameter US
        "53670-6",  # Fetal Mandible Maximum length US
        "53671-4",  # Fetal Lung - left Diameter US
        "53672-2",  # Fetal Lung - right Diameter US
        "53673-0",  # Fetal Right ventricle Diameter during diastole US
        "53674-8",  # Fetal Finger fifth - right Length US
        "53675-5",  # Fetal Scapula - left Maximum length US
        "53676-3",  # Fetal Scapula - right Maximum length US
        "53677-1",  # Fetal Clavicle.diaphysis - right [Length] US
        "53678-9",  # Fetal Tibia diaphysis - right [Length] US
        "53679-7",  # Fetal Fibula.diaphysis - right [Length] US
        "53680-5",  # Fetal Lateral cerebral ventricle - right Transverse width US
        "53681-3",  # Fetal Foot - right [Length] US
        "53682-1",  # Fetal Third cerebral ventricle Diameter transverse US
        "53683-9",  # Fetal Head.fourth cerebral ventricle Diameter.anterior-posterior US
        "53684-7",  # Fetal Ear - left Maximum length US
        "53685-4",  # Fetal Left ventricle Diameter during diastole US
        "53686-2",  # Fetal Neck Narrative Study observation US
        "53687-0",  # Fetal Gastrointestinal tract Narrative Study observation US
        "53688-8",  # Fetal Genitalia Narrative Study observation US
        "53689-6",  # Fetal Extremities Narrative Study observation US
        "53690-4",  # Fetal Skeletal system Narrative Study observation US
        "53691-2",  # Gestational age Estimated from patient reported estimated date of conception
        "53693-8",  # Gestational age Estimated from conception date
        "53695-3",  # Gestational age Estimated from prior assessment
        "53696-1",  # Fetal Femur.diaphysis - right [Length] US
        "53697-9",  # Fetal Nasal bone diaphysis [Length] US
        "53698-7",  # Fetal Humerus diaphysis - right [Length] US
        "53699-5",  # Fetal Radius.diaphysis - right [Length] US
        "53700-1",  # Fetal Ulna diaphysis - right [Length] US
        "53701-9",  # Fetal Finger fifth - left Length US
        "57067-1",  # Fetal Body weight Estimated by palpation
        "60477-7",  # Fetal Nuchal fold [Multiple of the median] Thickness adjusted for maternal weight
        "69391-1",  # US Guidance for cordocentesis
        "69400-0",  # US Guidance for chorionic villus sampling
        "72221-5",  # Fetal Yolk sac Study observation US
        "76514-9",  # Fetal Narrative Study observation general Diagnostic imaging
        "80414-6",  # Head circumference/Abdominal circumference US+Estimated from Campbell 1991
        "80416-1",  # Head circumference/Abdominal circumference US+Estimated from Campbell 1977
    }


class XRayStudyAllInclusive(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a radiology study involving x-rays.

    **Data Element Scope:** This value set may use a model element related to Diagnostic Study.

    **Inclusion Criteria:** Includes concepts that describe a diagnostic study involving x-rays.

    **Exclusion Criteria:** Excludes order only codes.

    ** Used in:** CMS153v10
    """

    VALUE_SET_NAME = "X-Ray Study (all inclusive)"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1034"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "24533-2",  # MRA Abdominal vessels W contrast IV
        "24535-7",  # XR Acetabulum Views
        "24536-5",  # XR Acromioclavicular Joint Views
        "24538-1",  # MR Ankle
        "24539-9",  # MR Ankle WO and W contrast IV
        "24540-7",  # XR Ankle 2 Views
        "24541-5",  # XR Ankle Views
        "24544-9",  # CT Thoracic Aorta
        "24545-6",  # CT Thoracic Aorta W contrast IV
        "24549-8",  # MRA Upper extremity vessels W contrast IV
        "24552-2",  # RF Stent Views W contrast intra stent
        "24556-3",  # MR Abdomen
        "24557-1",  # MR Abdomen WO and W contrast IV
        "24561-3",  # XR Abdomen AP left lateral-decubitus
        "24562-1",  # XR Abdomen Left lateral-decubitus and Right lateral-decubitus
        "24563-9",  # XR Abdomen AP right lateral-decubitus
        "24566-2",  # CT Retroperitoneum
        "24570-4",  # RF Guidance for removal of calculus from Biliary duct common-- W contrast retrograde intra biliary
        "24573-8",  # XR Biliary ducts and Gallbladder Views W contrast IV
        "24574-6",  # RF Biliary ducts and Gallbladder Views during surgery W contrast biliary duct
        "24575-3",  # RF Biliary ducts and Gallbladder Views W contrast percutaneous transhepatic
        "24577-9",  # XR Bone Views during surgery
        "24579-5",  # XR Long bones Survey Views
        "24582-9",  # MR Brachial plexus
        "24583-7",  # MR Brachial plexus WO and W contrast IV
        "24584-5",  # MRA Thoracic inlet vessels W contrast IV
        "24585-2",  # CT Guidance for stereotactic biopsy of Head-- W contrast IV
        "24586-0",  # MR Brain W anesthesia
        "24587-8",  # MR Brain WO and W contrast IV
        "24588-6",  # MR Brain WO and W contrast IV and W anesthesia
        "24589-4",  # MR Brain W contrast IV
        "24590-2",  # MR Brain
        "24593-6",  # MRA Head vessels W contrast IV
        "24612-4",  # XR Calcaneus Views
        "24619-9",  # XR Wrist Views
        "24620-7",  # RF Catheter Views for patency check W contrast via catheter
        "24621-5",  # RF Guidance for percutaneous drainage and placement of drainage catheter of Unspecified body region
        "24623-1",  # CT Guidance for nerve block of Celiac plexus
        "24627-2",  # CT Chest
        "24628-0",  # CT Chest W contrast IV
        "24629-8",  # MR Chest
        "24631-4",  # RF Unspecified body region Views for central venous catheter placement check
        "24635-5",  # XR Chest PA upright Views W inspiration and expiration
        "24637-1",  # XR Chest AP left lateral-decubitus
        "24639-7",  # XR Chest Left lateral upright
        "24640-5",  # XR Chest Apical lordotic
        "24642-1",  # XR Chest AP and PA upright
        "24643-9",  # XR Chest PA and Lateral and Oblique upright
        "24646-2",  # XR Chest PA and Right lateral and Right oblique and Left oblique upright
        "24647-0",  # XR Chest PA and Lateral upright
        "24648-8",  # XR Chest PA upright
        "24650-4",  # XR Chest Right lateral-decubitus and Left lateral-decubitus
        "24651-2",  # XR Chest Right oblique and Left oblique upright
        "24653-8",  # XR Chest AP and AP right lateral-decubitus
        "24655-3",  # RF Chest Image intensifier during surgery
        "24656-1",  # RF Chest Single view during surgery
        "24659-5",  # MRA Chest vessels W contrast IV
        "24660-3",  # MRA Thoracic Aorta
        "24661-1",  # RF Pleural space Views W contrast intra pleural space
        "24664-5",  # XR Clavicle Views
        "24665-2",  # XR Sacrum and Coccyx Views
        "24666-0",  # RF Colon Views W air and barium contrast PR
        "24667-8",  # RF Colon Views W contrast PR
        "24668-6",  # RF Colon Single view for transit Post solid contrast
        "24669-4",  # RF Colon Views W water soluble contrast PR
        "24671-0",  # RF Guidance for aspiration of cyst of Unspecified body region
        "24674-4",  # MR Elbow
        "24675-1",  # MR Elbow WO and W contrast IV
        "24676-9",  # XR Elbow Views
        "24678-5",  # RF Esophagus Views W contrast PO
        "24679-3",  # RF Esophagus Views W gastrografin PO
        "24680-1",  # RF Guidance for dilation of Esophagus
        "24686-8",  # XR Lower extremity Views
        "24687-6",  # MR Lower Extremity Joint
        "24688-4",  # MR Upper extremity
        "24689-2",  # XR Upper extremity Views
        "24690-0",  # CT Extremity
        "24691-8",  # CT Extremity W contrast IV
        "24694-2",  # MR Face WO and W contrast IV
        "24695-9",  # XR Facial bones Views
        "24696-7",  # CT Facial bones
        "24697-5",  # CT Facial bones W contrast IV
        "24700-7",  # XR Femur and Tibia Views for leg length
        "24702-3",  # MR Thigh
        "24703-1",  # MR Thigh WO and W contrast IV
        "24704-9",  # XR Femur Views
        "24705-6",  # MR Finger
        "24706-4",  # XR Finger Views
        "24707-2",  # MR Foot
        "24708-0",  # XR Foot Views W standing
        "24709-8",  # XR Foot Views
        "24710-6",  # MR Forearm
        "24712-2",  # XR Gallbladder Views W contrast PO
        "24713-0",  # XR Gallbladder Views 48H post contrast PO
        "24715-5",  # RF Gastrointestinal tract upper Single view W contrast PO
        "24716-3",  # RF Guidance for placement of decompression tube in Gastrointestinal tract
        "24718-9",  # RF Guidance for transjugular biopsy of Liver-- W contrast IV
        "24720-5",  # MR Hand
        "24721-3",  # XR Hand 2 Views
        "24722-1",  # XR Hand 3 Views
        "24723-9",  # XR Hand Arthritis
        "24724-7",  # XR Wrist and Hand Bone age Views
        "24725-4",  # CT Head
        "24726-2",  # CT Head WO and W contrast IV
        "24727-0",  # CT Head W contrast IV
        "24734-6",  # CT Cerebral cisterns W contrast IT
        "24735-3",  # MR Internal auditory canal and Posterior fossa
        "24740-3",  # MR Internal auditory canal and Posterior fossa WO and W contrast IV
        "24745-2",  # XR Petrous part of temporal bone Views
        "24748-6",  # MR Heart
        "24753-6",  # CT Unspecified body region W contrast IV
        "24761-9",  # XR Hip Single view
        "24762-7",  # XR Hip Views
        "24764-3",  # RF Hip Arthrogram
        "24765-0",  # XR Humerus 2 Views
        "24769-2",  # CT Guidance for injection of Joint space
        "24771-8",  # RF Guidance for arthrocentesis of Joint space
        "24778-3",  # XR Kidney - bilateral 3 Serial Views WO and W contrast IV
        "24779-1",  # RF Guidance for percutaneous placement of nephrostomy tube of Kidney - bilateral-- W contrast via tube
        "24780-9",  # RF Kidney - bilateral Views W contrast via nephrostomy tube
        "24781-7",  # RF Guidance for exchange of nephrostomy tube of Kidney - bilateral-- W contrast
        "24782-5",  # RF Guidance for percutaneous placement of nephroureteral stent of Kidney - bilateral-- W contrast via stent
        "24783-3",  # RF Kidney - bilateral Views for urodynamics
        "24788-2",  # XR Kidney - bilateral Views W contrast IV
        "24794-0",  # XR Abdomen AP and Lateral
        "24796-5",  # XR Abdomen AP and AP left lateral-decubitus
        "24797-3",  # XR Abdomen AP and Oblique prone
        "24798-1",  # XR Abdomen Supine and Upright
        "24799-9",  # XR Abdomen AP
        "24800-5",  # RF Knee Arthrogram
        "24801-3",  # XR Knee Merchants
        "24802-1",  # MR Knee
        "24803-9",  # MR Knee WO and W contrast IV
        "24805-4",  # XR Knee AP and Lateral W standing
        "24806-2",  # XR Knee 2 Views
        "24807-0",  # XR Knee AP W standing
        "24808-8",  # XR Knee AP and PA W standing
        "24809-6",  # XR Knee Views W standing
        "24811-2",  # CT Guidance for fluid aspiration of Liver
        "24812-0",  # CT Guidance for biopsy of Liver
        "24813-8",  # CT Guidance for core needle biopsy of Liver
        "24814-6",  # CT Liver
        "24815-3",  # CT Liver W contrast IV
        "24820-3",  # MRA Lower leg vessels W contrast IV
        "24821-1",  # MR Lower leg
        "24822-9",  # CT Guidance for fluid aspiration of Lung
        "24823-7",  # CT Guidance for biopsy of Lung
        "24825-2",  # XR Lung Views W contrast intrabronchial
        "24829-4",  # XR Mandible Views
        "24830-2",  # XR Mastoid Views
        "24834-4",  # XR Nasal bones Views
        "24835-1",  # CT Nasopharynx and Neck
        "24836-9",  # CT Nasopharynx and Neck W contrast IV
        "24837-7",  # CT Guidance for fluid aspiration of Neck
        "24838-5",  # CT Guidance for biopsy of Neck
        "24839-3",  # MR Neck
        "24840-1",  # MR Neck WO and W contrast IV
        "24841-9",  # MR Neck W contrast IV
        "24843-5",  # XR Neck Lateral
        "24844-3",  # MRA Neck vessels W contrast IV
        "24845-0",  # RF Neck Views W contrast intra larynx
        "24846-8",  # XR Optic foramen Views
        "24848-4",  # CT Orbit - bilateral
        "24849-2",  # CT Orbit - bilateral WO and W contrast IV
        "24850-0",  # CT Orbit - bilateral W contrast IV
        "24851-8",  # MR Orbit - bilateral WO and W contrast IV
        "24852-6",  # MR Orbit - bilateral W contrast IV
        "24854-2",  # XR Orbit - bilateral Views
        "24856-7",  # CT Guidance for fluid aspiration of Pancreas
        "24857-5",  # CT Pancreas
        "24858-3",  # CT Pancreas W contrast IV
        "24861-7",  # XR Patella 2 Views
        "24863-3",  # CT Guidance for fluid aspiration of Pelvis
        "24864-1",  # CT Guidance for biopsy of Pelvis
        "24865-8",  # CT Pelvis
        "24866-6",  # CT Pelvis W contrast IV
        "24867-4",  # MR Pelvis
        "24871-6",  # XR Pelvis Pelvimetry
        "24872-4",  # MR Pelvis and Hip
        "24873-2",  # MRA Pelvis vessels W contrast IV
        "24877-3",  # CT Petrous part of temporal bone
        "24878-1",  # CT Petrous part of temporal bone W contrast IV
        "24879-9",  # MR Pituitary and Sella turcica WO and W contrast IV
        "24880-7",  # MR Pituitary and Sella turcica
        "24891-4",  # XR Radius and Ulna Views
        "24893-0",  # RF Rectum Single view post contrast PR during defecation
        "24894-8",  # RF Rectum and Urinary bladder Views W contrast PR and intra bladder during defecation and voiding
        "24899-7",  # XR Ribs Views
        "24900-3",  # XR Sacroiliac Joint Views
        "24901-1",  # CT Guidance for injection of Sacroiliac Joint
        "24902-9",  # RF Salivary gland Views W contrast intra salivary duct
        "24903-7",  # XR Scapula Views
        "24904-5",  # CT Pituitary and Sella turcica WO and W contrast IV
        "24905-2",  # MR Shoulder
        "24906-0",  # MR Shoulder WO and W contrast IV
        "24908-6",  # XR Shoulder 3 Views
        "24909-4",  # XR Shoulder Views
        "24910-2",  # RF Shoulder Arthrogram
        "24911-0",  # RF Shunt Views
        "24912-8",  # RF Sinus tract Views W contrast intra sinus tract
        "24913-6",  # CT Sinuses limited
        "24914-4",  # MR Sinuses
        "24915-1",  # MR Sinuses W contrast IV
        "24916-9",  # XR Sinuses Views
        "24917-7",  # XR Skull Single view
        "24918-5",  # XR Skull 3 Views
        "24919-3",  # XR Skull AP and Lateral
        "24920-1",  # XR Skull Lateral
        "24921-9",  # XR Skull Waters
        "24922-7",  # XR Skull 5 Views
        "24923-5",  # RF Small bowel Views W positive contrast via enteroclysis tube
        "24924-3",  # RF Small bowel Views W contrast PO
        "24927-6",  # RF Spine Views W contrast intradisc
        "24928-4",  # XR Spine AP and Lateral
        "24929-2",  # XR Thoracic and lumbar spine Views for scoliosis W flexion and W extension
        "24930-0",  # XR Thoracic and lumbar spine Views for scoliosis
        "24931-8",  # RF Guidance for injection of Spine facet joint
        "24932-6",  # CT Cervical spine
        "24933-4",  # CT Cervical spine W contrast IV
        "24934-2",  # CT Cervical spine W contrast IT
        "24935-9",  # MR Cervical spine
        "24936-7",  # MR Cervical spine W anesthesia
        "24937-5",  # MR Cervical spine WO and W contrast IV
        "24938-3",  # MR Cervical spine W contrast IV
        "24939-1",  # XR Cervical spine 5 Views
        "24940-9",  # XR Cervical spine Single view
        "24941-7",  # XR Cervical spine 3 Views
        "24942-5",  # XR Cervical spine AP and Lateral
        "24943-3",  # XR Cervical spine Lateral
        "24944-1",  # XR Cervical spine Swimmers
        "24945-8",  # XR Cervical spine Views W flexion and W extension
        "24946-6",  # XR Cervical spine Views
        "24947-4",  # RF Cervical spine Views W contrast IT
        "24948-2",  # XR Spine Cervical Odontoid and Cervical axis AP
        "24963-1",  # CT Lumbar spine
        "24964-9",  # CT Lumbar spine W contrast IV
        "24965-6",  # CT Lumbar spine W contrast IT
        "24967-2",  # MR Lumbar spine WO and W contrast IV
        "24968-0",  # MR Lumbar spine
        "24969-8",  # XR Lumbar spine Lateral
        "24970-6",  # XR Lumbar spine AP and Lateral
        "24971-4",  # XR Lumbar spine Views W flexion and W extension
        "24972-2",  # XR Lumbar spine Views
        "24973-0",  # RF Guidance for fluid aspiration of Lumbar spine space
        "24974-8",  # RF Lumbar spine Views W contrast IT
        "24975-5",  # XR Spine.lumbar and Sacroiliac joint - bilateral Views
        "24977-1",  # MR Lumbar spine W anesthesia
        "24978-9",  # CT Thoracic spine
        "24979-7",  # CT Thoracic spine W contrast IV
        "24980-5",  # MR Thoracic spine
        "24981-3",  # MR Thoracic spine WO and W contrast IV
        "24982-1",  # MR Thoracic spine W contrast IV
        "24983-9",  # XR Thoracic spine Views
        "24984-7",  # XR Thoracic and lumbar spine 2 Views
        "24985-4",  # RF Thoracic spine Views W contrast IT
        "24986-2",  # CT Guidance for biopsy of Spine
        "24987-0",  # CT Spine W contrast IV
        "24988-8",  # CT Spleen
        "24989-6",  # CT Spleen WO and W contrast IV
        "24994-6",  # XR Sternum Views
        "24995-3",  # RF Guidance for placement of tube in Stomach
        "24996-1",  # RF Guidance for percutaneous replacement of gastrostomy of Stomach
        "24998-7",  # RF Placement check of gastrostomy tube W contrast via GI tube
        "24999-5",  # MR Temporomandibular joint
        "25003-5",  # MRA Thigh vessels W contrast IV
        "25006-8",  # XR Thumb Views
        "25011-8",  # XR Tibia and Fibula Views
        "25013-4",  # XR Toes Views
        "25016-7",  # RF Urethra Views W contrast intra urethra
        "25017-5",  # RF Urinary bladder and Urethra Views W contrast intra bladder
        "25020-9",  # RF Urinary bladder and Urethra Views W contrast retrograde via urethra
        "25022-5",  # RF Uterus and Fallopian tubes Views W contrast IU
        "25033-2",  # MR Wrist
        "25034-0",  # RF Wrist Arthrogram
        "25035-7",  # MR Wrist WO and W contrast IV
        "25039-9",  # CT Unspecified body region limited
        "25041-5",  # CT Guidance for aspiration or biopsy of Unspecified body region-- W contrast IV
        "25042-3",  # CT Guidance for aspiration or biopsy of Unspecified body region
        "25043-1",  # CT Guidance for fluid aspiration of Unspecified body region
        "25044-9",  # CT Guidance for biopsy of Unspecified body region
        "25045-6",  # CT Unspecified body region
        "25046-4",  # CT Unspecified body region W anesthesia
        "25047-2",  # CT Unspecified body region W conscious sedation
        "25053-0",  # CT Guidance for radiosurgery of Unspecified body region
        "25054-8",  # CT Guidance for radiosurgery of Unspecified body region-- W contrast IV
        "25056-3",  # MR Unspecified body region
        "25057-1",  # MR Unspecified body region W conscious sedation
        "25058-9",  # MRA Unspecified body region W contrast IV
        "25062-1",  # XR Unspecified body region Comparison view
        "25065-4",  # RF 15 minutes
        "25066-2",  # RF 30 minutes
        "25067-0",  # RF 45 minutes
        "25068-8",  # RF 1 hour
        "25069-6",  # RF Guidance for biopsy of Unspecified body region
        "25070-4",  # RF Unspecified body region Views during surgery
        "25074-6",  # XR Zygomatic arch Views
        "25078-7",  # RF Guidance for placement of stent in Intrahepatic portal system
        "26067-9",  # RF Salivary gland - bilateral Views W contrast intra salivary duct
        "26068-7",  # RF Salivary gland - left Views W contrast intra salivary duct
        "26069-5",  # RF Salivary gland - right Views W contrast intra salivary duct
        "26070-3",  # RF Hip - bilateral Arthrogram
        "26071-1",  # RF Hip - left Arthrogram
        "26072-9",  # RF Hip - right Arthrogram
        "26073-7",  # RF Knee - bilateral Arthrogram
        "26074-5",  # RF Knee - left Arthrogram
        "26075-2",  # RF Knee - right Arthrogram
        "26076-0",  # RF Shoulder - bilateral Arthrogram
        "26077-8",  # RF Shoulder - left Arthrogram
        "26078-6",  # RF Shoulder - right Arthrogram
        "26085-1",  # XR Knee - bilateral Views W standing
        "26086-9",  # XR Knee - left Views W standing
        "26087-7",  # XR Knee - right Views W standing
        "26094-3",  # XR Foot - bilateral Views W standing
        "26095-0",  # XR Foot - left Views W standing
        "26096-8",  # XR Foot - right Views W standing
        "26097-6",  # XR Ankle - bilateral Views
        "26098-4",  # XR Ankle - left Views
        "26099-2",  # XR Ankle - right Views
        "26100-8",  # XR Calcaneus - bilateral Views
        "26101-6",  # XR Calcaneus - left Views
        "26102-4",  # XR Calcaneus - right Views
        "26106-5",  # XR Clavicle - bilateral Views
        "26107-3",  # XR Clavicle - left Views
        "26108-1",  # XR Clavicle - right Views
        "26109-9",  # XR Elbow - bilateral Views
        "26110-7",  # XR Elbow - left Views
        "26111-5",  # XR Elbow - right Views
        "26112-3",  # XR Lower extremity - bilateral Views
        "26113-1",  # XR Lower extremity - left Views
        "26114-9",  # XR Lower extremity - right Views
        "26115-6",  # XR Upper extremity - bilateral Views
        "26116-4",  # XR Upper extremity - left Views
        "26117-2",  # XR Upper extremity - right Views
        "26118-0",  # XR Femur - bilateral Views
        "26120-6",  # XR Femur - left Views
        "26122-2",  # XR Femur - right Views
        "26124-8",  # XR Finger - bilateral Views
        "26125-5",  # XR Finger - left Views
        "26126-3",  # XR Finger - right Views
        "26127-1",  # XR Foot - bilateral Views
        "26128-9",  # XR Foot - left Views
        "26129-7",  # XR Foot - right Views
        "26130-5",  # XR Hip - bilateral Views
        "26131-3",  # XR Hip - left Views
        "26132-1",  # XR Hip - right Views
        "26133-9",  # XR Acetabulum - bilateral Views
        "26134-7",  # XR Acetabulum - left Views
        "26135-4",  # XR Acetabulum - right Views
        "26136-2",  # XR Acromioclavicular joint - bilateral Views
        "26137-0",  # XR Acromioclavicular joint - left Views
        "26138-8",  # XR Acromioclavicular joint - right Views
        "26139-6",  # XR Mastoid - bilateral Views
        "26140-4",  # XR Mastoid - left Views
        "26141-2",  # XR Mastoid - right Views
        "26142-0",  # XR Optic foramen - bilateral Views
        "26143-8",  # XR Optic foramen - left Views
        "26144-6",  # XR Optic foramen - right Views
        "26146-1",  # XR Radius and Ulna - bilateral Views
        "26148-7",  # XR Radius and Ulna - left Views
        "26150-3",  # XR Radius and Ulna - right Views
        "26151-1",  # XR Ribs - bilateral Views
        "26152-9",  # XR Ribs - left Views
        "26153-7",  # XR Ribs - right Views
        "26154-5",  # XR Scapula - bilateral Views
        "26155-2",  # XR Scapula - left Views
        "26156-0",  # XR Scapula - right Views
        "26157-8",  # XR Shoulder - bilateral Views
        "26158-6",  # XR Shoulder - left Views
        "26159-4",  # XR Shoulder - right Views
        "26160-2",  # XR Thumb - bilateral Views
        "26161-0",  # XR Thumb - left Views
        "26162-8",  # XR Thumb - right Views
        "26163-6",  # XR Tibia and Fibula - bilateral Views
        "26164-4",  # XR Tibia and Fibula - left Views
        "26165-1",  # XR Tibia and Fibula - right Views
        "26166-9",  # XR Toes - bilateral Views
        "26167-7",  # XR Toes - left Views
        "26168-5",  # XR Toes - right Views
        "26169-3",  # XR Wrist - bilateral Views
        "26170-1",  # XR Wrist - left Views
        "26171-9",  # XR Wrist - right Views
        "26172-7",  # XR Zygomatic arch - bilateral Views
        "26173-5",  # XR Zygomatic arch - left Views
        "26174-3",  # XR Zygomatic arch - right Views
        "26181-8",  # MRA Thoracic inlet vessels - bilateral W contrast IV
        "26182-6",  # MRA Thoracic inlet vessels - left W contrast IV
        "26183-4",  # MRA Thoracic inlet vessels - right W contrast IV
        "26184-2",  # CT Extremity - bilateral W contrast IV
        "26185-9",  # CT Extremity - left W contrast IV
        "26186-7",  # CT Extremity - right W contrast IV
        "26187-5",  # MR Ankle - bilateral WO and W contrast IV
        "26188-3",  # MR Ankle - left WO and W contrast IV
        "26189-1",  # MR Ankle - right WO and W contrast IV
        "26190-9",  # MR Brachial plexus - bilateral WO and W contrast IV
        "26191-7",  # MR Brachial plexus - left WO and W contrast IV
        "26192-5",  # MR Brachial plexus - right WO and W contrast IV
        "26193-3",  # MR Elbow - bilateral WO and W contrast IV
        "26194-1",  # MR Elbow - left WO and W contrast IV
        "26195-8",  # MR Elbow - right WO and W contrast IV
        "26196-6",  # MR Thigh - bilateral WO and W contrast IV
        "26197-4",  # MR Thigh - left WO and W contrast IV
        "26198-2",  # MR Thigh - right WO and W contrast IV
        "26199-0",  # MR Knee - bilateral WO and W contrast IV
        "26200-6",  # MR Knee - left WO and W contrast IV
        "26201-4",  # MR Knee - right WO and W contrast IV
        "26202-2",  # MR Shoulder - bilateral WO and W contrast IV
        "26203-0",  # MR Shoulder - left WO and W contrast IV
        "26204-8",  # MR Shoulder - right WO and W contrast IV
        "26205-5",  # MR Wrist - bilateral WO and W contrast IV
        "26206-3",  # MR Wrist - left WO and W contrast IV
        "26207-1",  # MR Wrist - right WO and W contrast IV
        "26208-9",  # MR Ankle - bilateral
        "26209-7",  # MR Ankle - left
        "26210-5",  # MR Ankle - right
        "26211-3",  # MR Brachial plexus - bilateral
        "26212-1",  # MR Brachial plexus - left
        "26213-9",  # MR Brachial plexus - right
        "26220-4",  # MR Elbow - bilateral
        "26221-2",  # MR Elbow - left
        "26222-0",  # MR Elbow - right
        "26224-6",  # CT Extremity - bilateral
        "26226-1",  # CT Extremity - left
        "26227-9",  # MR Lower extremity joint - bilateral
        "26228-7",  # MR Lower extremity joint - left
        "26229-5",  # MR Lower extremity joint - right
        "26231-1",  # CT Extremity - right
        "26232-9",  # MR Upper extremity - bilateral
        "26233-7",  # MR Upper extremity - left
        "26234-5",  # MR Upper extremity - right
        "26235-2",  # MR Thigh - bilateral
        "26236-0",  # MR Thigh - left
        "26237-8",  # MR Thigh - right
        "26238-6",  # MR Finger - bilateral
        "26239-4",  # MR Finger - left
        "26240-2",  # MR Finger - right
        "26241-0",  # MR Foot - bilateral
        "26242-8",  # MR Foot - left
        "26243-6",  # MR Foot - right
        "26244-4",  # MR Forearm - bilateral
        "26245-1",  # MR Forearm - left
        "26246-9",  # MR Forearm - right
        "26247-7",  # MR Hand - bilateral
        "26248-5",  # MR Hand - left
        "26249-3",  # MR Hand - right
        "26256-8",  # MR Knee - bilateral
        "26257-6",  # MR Knee - left
        "26258-4",  # MR Knee - right
        "26259-2",  # MR Pelvis and Hip - bilateral
        "26260-0",  # MR Pelvis and Hip - left
        "26261-8",  # MR Pelvis and Hip - right
        "26266-7",  # MR Shoulder - bilateral
        "26268-3",  # MR Shoulder - left
        "26270-9",  # MR Shoulder - right
        "26277-4",  # MR Wrist - bilateral
        "26279-0",  # MR Wrist - left
        "26281-6",  # MR Wrist - right
        "26283-2",  # XR Knee - bilateral Merchants
        "26284-0",  # XR Knee - left Merchants
        "26285-7",  # XR Knee - right Merchants
        "26319-4",  # CT Guidance for injection of Sacroiliac joint - bilateral
        "26320-2",  # CT Guidance for injection of Sacroiliac joint - left
        "26321-0",  # CT Guidance for injection of Sacroiliac joint - right
        "26322-8",  # RF Guidance for injection of Spine facet joint - bilateral
        "26323-6",  # RF Guidance for injection of Spine facet joint - left
        "26324-4",  # RF Guidance for injection of Spine facet joint - right
        "26352-5",  # XR Wrist - bilateral and Hand - bilateral Bone age Views
        "26353-3",  # XR Wrist - left and Hand - left Bone age Views
        "26354-1",  # XR Wrist - right and Hand - right Bone age Views
        "26355-8",  # XR Hand - bilateral Arthritis
        "26356-6",  # XR Hand - left Arthritis
        "26357-4",  # XR Hand - right Arthritis
        "26358-2",  # XR Knee - bilateral AP W standing
        "26359-0",  # XR Knee - left AP W standing
        "26360-8",  # XR Knee - right AP W standing
        "26361-6",  # XR Knee - bilateral AP and PA W standing
        "26362-4",  # XR Knee - left AP and PA W standing
        "26363-2",  # XR Knee - right AP and PA W standing
        "26364-0",  # XR Knee - bilateral AP and Lateral W standing
        "26365-7",  # XR Knee - left AP and Lateral W standing
        "26366-5",  # XR Knee - right AP and Lateral W standing
        "26379-8",  # XR Hand - bilateral 3 Views
        "26380-6",  # XR Hand - left 3 Views
        "26381-4",  # XR Hand - right 3 Views
        "26382-2",  # XR Shoulder - bilateral 3 Views
        "26383-0",  # XR Shoulder - left 3 Views
        "26384-8",  # XR Shoulder - right 3 Views
        "26385-5",  # XR Ankle - bilateral 2 Views
        "26386-3",  # XR Ankle - left 2 Views
        "26387-1",  # XR Ankle - right 2 Views
        "26388-9",  # XR Hand - bilateral 2 Views
        "26389-7",  # XR Hand - left 2 Views
        "26390-5",  # XR Hand - right 2 Views
        "26391-3",  # XR Humerus - bilateral 2 Views
        "26392-1",  # XR Humerus - left 2 Views
        "26393-9",  # XR Humerus - right 2 Views
        "26394-7",  # XR Knee - bilateral 2 Views
        "26395-4",  # XR Knee - left 2 Views
        "26396-2",  # XR Knee - right 2 Views
        "26397-0",  # XR Patella - bilateral 2 Views
        "26398-8",  # XR Patella - left 2 Views
        "26399-6",  # XR Patella - right 2 Views
        "26400-2",  # XR Hip - bilateral Single view
        "26401-0",  # XR Hip - left Single view
        "26402-8",  # XR Hip - right Single view
        "28561-9",  # XR Pelvis Views
        "28564-3",  # XR Skull Views
        "28565-0",  # XR Knee Views
        "28566-8",  # CT Spine
        "28567-6",  # XR Humerus Views
        "28576-7",  # MR Joint
        "28582-5",  # XR Hand Views
        "28613-8",  # XR Spine Views
        "29252-4",  # CT Chest WO contrast
        "30578-9",  # CT Guidance for drainage of abscess and placement of drainage catheter of Unspecified body region
        "30579-7",  # CT Guidance for injection of Spine facet joint
        "30580-5",  # CT Guidance for fine needle aspiration of Unspecified body region
        "30581-3",  # CT Guidance for radiation treatment of Unspecified body region-- W contrast IV
        "30582-1",  # CT Guidance for radiation treatment of Unspecified body region-- WO contrast
        "30583-9",  # CT Internal auditory canal W contrast IV
        "30584-7",  # CT Internal auditory canal WO contrast
        "30585-4",  # CT Nasopharynx and Neck WO contrast
        "30586-2",  # CT Neck WO and W contrast IV
        "30587-0",  # CT Orbit - bilateral WO contrast
        "30588-8",  # CT Sinuses
        "30589-6",  # CT Petrous part of temporal bone WO contrast
        "30590-4",  # CT Pituitary and Sella turcica W contrast IV
        "30591-2",  # CT Pituitary and Sella turcica WO contrast
        "30592-0",  # CT Cervical spine WO contrast
        "30595-3",  # CT Guidance for fine needle aspiration of Lung
        "30596-1",  # CT Thoracic spine W contrast IT
        "30597-9",  # CT Thoracic spine WO contrast
        "30598-7",  # CT Chest WO and W contrast IV
        "30600-1",  # CT Small bowel W positive contrast via enteroclysis tube
        "30601-9",  # CT Guidance for biopsy of Abdomen
        "30602-7",  # CT Guidance for fine needle aspiration of Abdomen
        "30603-5",  # CT Guidance for fine needle aspiration of Liver
        "30604-3",  # CT Guidance for biopsy of Pancreas
        "30605-0",  # CT Guidance for fine needle aspiration of Pancreas
        "30606-8",  # CT Guidance for fine needle aspiration of Pelvis
        "30607-6",  # CT Guidance for biopsy of Kidney - bilateral
        "30608-4",  # CT Guidance for fine needle aspiration of Kidney - bilateral
        "30609-2",  # CT Guidance for biopsy of Spleen
        "30610-0",  # CT Guidance for fine needle aspiration of Spleen
        "30611-8",  # CT Liver WO contrast
        "30612-6",  # CT Liver WO and W contrast IV
        "30613-4",  # CT Pancreas WO contrast
        "30614-2",  # CT Pancreas WO and W contrast IV
        "30615-9",  # CT Pelvis WO contrast
        "30616-7",  # CT Pelvis WO and W contrast IV
        "30619-1",  # CT Sacroiliac Joint
        "30620-9",  # CT Lumbar spine WO contrast
        "30621-7",  # CT Spleen WO contrast
        "30622-5",  # CT Spleen W contrast IV
        "30624-1",  # CT Lower extremity W contrast IV
        "30625-8",  # CT Lower extremity WO contrast
        "30626-6",  # CT Upper extremity W contrast IV
        "30627-4",  # CT Upper extremity WO contrast
        "30628-2",  # RF Guidance for removal of foreign body of Unspecified body region
        "30629-0",  # RF Guidance for procedure of Unspecified body region
        "30631-6",  # RF Chest Views
        "30632-4",  # RF Diaphragm for motion
        "30633-2",  # RF Esophagus Views W barium contrast PO
        "30634-0",  # RF Guidance for biopsy of Lung
        "30636-5",  # RF Colon Views for reduction W contrast PR
        "30637-3",  # RF Guidance for placement of tube in Gastrointestinal tract
        "30638-1",  # RF Guidance for injection of Hip
        "30642-3",  # RF Unspecified body region Single view
        "30646-4",  # RF Guidance for change of tube in Sinus tract-- W contrast
        "30647-2",  # RF Biliary ducts and Gallbladder Views W contrast via T-tube
        "30650-6",  # RF Unspecified body region Views for shunt
        "30654-8",  # MR Brachial plexus WO contrast
        "30655-5",  # MR Cerebral cisterns
        "30656-3",  # MR Guidance for stereotactic localization of Brain-- W contrast IV
        "30657-1",  # MR Brain WO contrast
        "30658-9",  # MR Internal auditory canal WO contrast
        "30659-7",  # MR Internal auditory canal WO and W contrast IV
        "30660-5",  # MR Neck WO contrast
        "30661-3",  # MR Orbit - bilateral WO contrast
        "30662-1",  # MR Sinuses WO contrast
        "30663-9",  # MR Sinuses WO and W contrast IV
        "30664-7",  # MR Guidance for radiation treatment of Unspecified body region-- W contrast IV
        "30665-4",  # MR Guidance for radiation treatment of Unspecified body region-- WO contrast
        "30666-2",  # MR Pituitary and Sella turcica WO contrast
        "30667-0",  # MR Cervical spine WO contrast
        "30668-8",  # MR Abdomen WO contrast
        "30669-6",  # MR Liver WO contrast
        "30670-4",  # MR Liver WO and W contrast IV
        "30671-2",  # MR Pelvis and Hip WO contrast
        "30672-0",  # MR Pelvis and Hip WO and W contrast IV
        "30673-8",  # MR Pelvis WO contrast
        "30674-6",  # MR Pelvis WO and W contrast IV
        "30675-3",  # MR Prostate
        "30678-7",  # MR Lumbar spine W contrast IV
        "30679-5",  # MR Lumbar spine WO contrast
        "30680-3",  # MR Ankle WO contrast
        "30681-1",  # MR Foot WO contrast
        "30682-9",  # MR Foot WO and W contrast IV
        "30683-7",  # MR Forearm WO contrast
        "30684-5",  # MR Forearm WO and W contrast IV
        "30685-2",  # MR Hand WO contrast
        "30686-0",  # MR Hand WO and W contrast IV
        "30687-8",  # MR Hip WO contrast
        "30688-6",  # MR Hip WO and W contrast IV
        "30689-4",  # MR Upper arm WO contrast
        "30690-2",  # MR Upper arm WO and W contrast IV
        "30691-0",  # MR Knee WO contrast
        "30692-8",  # MR Lower extremity
        "30693-6",  # MR Shoulder WO contrast
        "30713-2",  # XR Spine Views W right bending and W left bending
        "30714-0",  # XR Thoracic and lumbar spine AP for scoliosis
        "30715-7",  # XR Thoracic and lumbar spine AP and lateral for scoliosis
        "30716-5",  # XR Thoracic and lumbar spine Lateral Views for scoliosis
        "30717-3",  # XR Thoracic and lumbar spine Views for scoliosis W standing
        "30720-7",  # XR Orbit - bilateral Views for foreign body
        "30721-5",  # XR Sinuses PA and Lateral
        "30725-6",  # XR Cervical spine AP
        "30734-8",  # XR Chest AP lateral-decubitus
        "30736-3",  # XR Chest Views W inspiration and expiration
        "30737-1",  # XR Chest Left lateral
        "30740-5",  # XR Chest Oblique
        "30741-3",  # XR Chest PA and Lateral and Lordotic upright
        "30742-1",  # XR Chest PA and Lateral and Right oblique and Left oblique
        "30744-7",  # XR Chest PA and Lateral and Oblique
        "30745-4",  # XR Chest Views
        "30748-8",  # XR Shoulder Single view
        "30750-4",  # XR Shoulder 5 Views
        "30751-2",  # XR Shoulder West Point
        "30752-0",  # XR Thoracic spine AP
        "30753-8",  # XR Thoracic spine AP and Lateral
        "30756-1",  # XR Thoracic spine Lateral
        "30758-7",  # XR Thoracic spine Oblique
        "30766-0",  # XR Pelvis 3 Views
        "30767-8",  # XR Pelvis and Hip Views
        "30768-6",  # XR Pelvis and Hip - bilateral Views
        "30769-4",  # XR Pelvis and Hip - bilateral Maximum abduction Views
        "30770-2",  # XR Pelvis and Hip AP and Lateral frog
        "30771-0",  # XR Pelvis Inlet and Outlet
        "30773-6",  # XR Lumbar spine Single view
        "30775-1",  # XR Lumbar spine 3 Views
        "30777-7",  # XR Lumbar spine AP
        "30778-5",  # XR Lumbar spine Oblique
        "30779-3",  # XR Ankle AP and Lateral
        "30780-1",  # XR Finger second Views
        "30781-9",  # XR Finger third Views
        "30782-7",  # XR Finger fourth Views
        "30783-5",  # XR Finger fifth Views
        "30784-3",  # XR Foot 2 Views
        "30785-0",  # XR Foot Views W forced dorsiflexion
        "30786-8",  # XR Hip Lateral frog
        "30787-6",  # XR Joint Single view
        "30788-4",  # XR Knee 3 Views
        "30789-2",  # XR Knee 4 Views
        "30790-0",  # XR Knee Tunnel
        "30791-8",  # XR Patella Views
        "30793-4",  # XR Wrist AP and Lateral
        "30794-2",  # MR Breast
        "30795-9",  # MR Breast - bilateral
        "30796-7",  # MR Elbow WO contrast
        "30797-5",  # XR Lumbar spine 5 Views
        "30799-1",  # CT Head WO contrast
        "30800-7",  # MR Guidance for stereotactic localization of Brain-- WO contrast
        "30801-5",  # CT Maxillofacial region W contrast IV
        "30802-3",  # CT Maxillofacial region WO contrast
        "30803-1",  # CT Maxillofacial region WO and W contrast IV
        "30808-0",  # RF Cervical and thoracic and lumbar spine Views W contrast IT
        "30809-8",  # RF Upper gastrointestinal tract and Small bowel Single view W contrast PO
        "30810-6",  # RF Lacrimal duct Views W contrast intra lacrimal duct
        "30811-4",  # RF Posterior fossa Views W contrast IT
        "30812-2",  # RF Guidance for injection of Spine Cervical Facet Joint
        "30813-0",  # XR Lung - bilateral Views W contrast intrabronchial
        "30814-8",  # RF Guidance for injection of Spine Thoracic Facet Joint
        "30815-5",  # RF Guidance for endoscopy of Biliary ducts and Pancreatic duct-- W contrast retrograde
        "30817-1",  # RF Guidance for injection of Lumbar Spine Facet Joint
        "30818-9",  # RF Guidance for placement of catheter in Fallopian tubes-- transcervical
        "30854-4",  # MR Cervical and thoracic and lumbar spine WO contrast
        "30855-1",  # MR Cervical and thoracic and lumbar spine WO and W contrast IV
        "30856-9",  # MRA Head vessels
        "30857-7",  # MR Nerves cranial
        "30858-5",  # MRA Head veins
        "30859-3",  # MRA Carotid vessels and Neck vessels
        "30860-1",  # MR Nasopharynx
        "30861-9",  # MRA Aortic arch and Neck vessels
        "30862-7",  # MRA Chest vessels
        "30864-3",  # MRA Abdominal veins and IVC
        "30865-0",  # MRA Celiac vessels and Superior mesenteric Vessels
        "30866-8",  # MR Lumbosacral plexus
        "30867-6",  # MRA Pelvis vessels
        "30868-4",  # MRA Renal vessels
        "30869-2",  # MR Lower leg WO contrast
        "30870-0",  # MR Lower leg WO and W contrast IV
        "30871-8",  # MRA Femoral vessels
        "30872-6",  # MRA Foot vessels
        "30873-4",  # MRA Forearm vessels
        "30874-2",  # MRA Lower extremity vessels
        "30875-9",  # MR Upper extremity.joint
        "30876-7",  # MRA Extremity veins
        "30883-3",  # XR Coccyx Views
        "30884-1",  # XR Sacrum Views
        "30885-8",  # XR Pelvis symphysis pubis Views
        "30887-4",  # MRA Renal vessels W contrast IV
        "30888-2",  # MRA Tibioperoneal vessels
        "30889-0",  # XR Temporomandibular joint - left Views
        "30890-8",  # XR Temporomandibular joint - right Views
        "30892-4",  # RF Guidance for placement of catheter in Biliary ducts and Pancreatic duct-- W contrast retrograde
        "35884-6",  # CT Guidance for drainage of abscess and placement of drainage catheter of Abdomen
        "35885-3",  # RF Guidance for drainage of abscess and placement of drainage catheter of Unspecified body region
        "35886-1",  # CT Guidance for fluid aspiration of Breast
        "35887-9",  # CT Guidance for aspiration of cyst of Unspecified body region
        "35888-7",  # RF Guidance for arthrocentesis of Hip
        "35889-5",  # RF Guidance for bronchoscopy of Chest
        "35890-3",  # RF Guidance for biopsy of Abdomen
        "35891-1",  # CT guidance for percutaneous biopsy of Bone
        "35892-9",  # CT Guidance for biopsy of Head
        "35893-7",  # CT Guidance for biopsy of Breast
        "35894-5",  # RF Guidance for biopsy of Chest
        "35895-2",  # CT Guidance for biopsy of Chest
        "35896-0",  # CT Guidance for biopsy of Lower extremity
        "35897-8",  # CT Guidance for biopsy of Upper extremity
        "35898-6",  # CT Guidance for biopsy of Salivary gland
        "35899-4",  # RF Guidance for biopsy of Kidney
        "35900-0",  # RF Guidance for percutaneous biopsy of Liver
        "35901-8",  # CT Guidance for biopsy of Lymph node
        "35902-6",  # RF Guidance for biopsy of Pancreas
        "35903-4",  # CT Guidance for biopsy of Prostate
        "35904-2",  # CT Guidance for biopsy of Cervical spine
        "35905-9",  # CT Guidance for biopsy of Lumbar spine
        "35906-7",  # CT Guidance for biopsy of Thoracic spine
        "35907-5",  # RF Guidance for biopsy of Spleen
        "35908-3",  # CT Guidance for biopsy of Thyroid gland
        "35909-1",  # CT Guidance for biopsy of Chest-- W contrast IV
        "35910-9",  # CT Guidance for biopsy of Chest-- WO and W contrast IV
        "35911-7",  # CT Guidance for biopsy of Chest-- WO contrast
        "35912-5",  # RF Guidance for placement of catheter in Unspecified body region
        "35913-3",  # CT Guidance for drainage and placement of drainage catheter of Abdomen
        "35914-1",  # CT Guidance for drainage and placement of drainage catheter of Anus
        "35915-8",  # CT Guidance for drainage and placement of drainage catheter of Appendix
        "35916-6",  # CT Guidance for drainage and placement of drainage catheter of Chest
        "35917-4",  # CT Guidance for drainage and placement of drainage catheter of Gallbladder
        "35918-2",  # CT Guidance for drainage and placement of drainage catheter of Kidney
        "35919-0",  # CT Guidance for drainage and placement of drainage catheter of Liver
        "35920-8",  # CT Guidance for drainage of Lymph node
        "35921-6",  # CT Guidance for drainage and placement of drainage catheter of Pelvis
        "35922-4",  # CT Guidance for drainage and placement of drainage catheter of Unspecified body region
        "35923-2",  # CT Guidance for drainage and placement of drainage catheter of Chest-- W contrast IV
        "35924-0",  # CT Guidance for drainage and placement of drainage catheter of Chest-- WO contrast
        "35925-7",  # RF Guidance for endoscopy of Stomach
        "35926-5",  # RF Guidance for gastrostomy of Stomach
        "35927-3",  # RF Guidance for injection of Sacroiliac Joint
        "35928-1",  # CT Guidance for localization of Breast - left
        "35929-9",  # CT Guidance for localization of Breast - right
        "35930-7",  # CT Guidance for nerve block of Abdomen
        "35931-5",  # CT Guidance for nerve block of Pelvis
        "35932-3",  # CT Guidance for nerve block of Lumbar spine
        "35933-1",  # CT Guidance for percutaneous vertebroplasty of Spine
        "35934-9",  # CT Guidance for percutaneous vertebroplasty of Lumbar spine
        "35935-6",  # CT Guidance for percutaneous vertebroplasty of Thoracic spine
        "35936-4",  # RF Guidance for percutaneous vertebroplasty of Spine
        "35937-2",  # CT Guidance for placement of radiation therapy fields in Unspecified body region
        "35938-0",  # CT Guidance for placement of tube in Chest
        "35940-6",  # CT Ankle
        "35941-4",  # CT Ankle - bilateral
        "35942-2",  # CT Ankle - left
        "35944-8",  # CT Ankle - right
        "35945-5",  # CT Thoracic and abdominal aorta
        "35946-3",  # MRA Thoracic and abdominal aorta
        "35947-1",  # MR Thoracic and abdominal aorta
        "35948-9",  # CT Abdominal Aorta
        "35949-7",  # MR Abdominal Aorta
        "35950-5",  # MR Thoracic Aorta
        "35951-3",  # MRA Aortic arch
        "35952-1",  # CT Appendix
        "35953-9",  # MR Face
        "35954-7",  # MR Breast - left
        "35955-4",  # MR Breast - right
        "35956-2",  # MR Internal auditory canal
        "35957-0",  # CT Internal auditory canal - left
        "35958-8",  # CT Internal auditory canal
        "35960-4",  # CT Clavicle
        "35961-2",  # MR Clavicle
        "35962-0",  # CT Elbow
        "35965-3",  # CT Elbow - bilateral
        "35966-1",  # CT Elbow - left
        "35968-7",  # CT Elbow - right
        "35969-5",  # CT Esophagus
        "35971-1",  # CT Lower extremity
        "35973-7",  # CT Lower extremity - bilateral
        "35974-5",  # MRA Lower extremity vessels - bilateral
        "35975-2",  # MR Lower extremity - bilateral
        "35976-0",  # CT Lower extremity - left
        "35978-6",  # MR Lower extremity - left
        "35979-4",  # CT Lower extremity - right
        "35980-2",  # MR Lower extremity - right
        "35981-0",  # CT Upper extremity
        "35982-8",  # CT Upper extremity - left
        "35983-6",  # CT Upper extremity - right
        "35984-4",  # CT Thigh
        "35987-7",  # CT Thigh - left
        "35989-3",  # CT Thigh - right
        "35990-1",  # MR Fetal
        "35991-9",  # CT Foot
        "35993-5",  # CT Foot - bilateral
        "35994-3",  # CT Foot - left
        "35996-8",  # CT Foot - right
        "35997-6",  # CT Forearm
        "35998-4",  # CT Forearm - bilateral
        "35999-2",  # CT Forearm - left
        "36000-8",  # CT Forearm - right
        "36002-4",  # CT Hand
        "36004-0",  # CT Hand - bilateral
        "36005-7",  # CT Hand - left
        "36007-3",  # CT Hand - right
        "36008-1",  # MR Wrist and Hand
        "36009-9",  # MRA Heart
        "36013-1",  # MR Hip
        "36014-9",  # CT Hip
        "36016-4",  # CT Hip - bilateral
        "36017-2",  # MR Hip - bilateral
        "36018-0",  # CT Hip - left
        "36020-6",  # MR Hip - left
        "36021-4",  # CT Hip - right
        "36022-2",  # MR Hip - right
        "36023-0",  # CT Upper arm
        "36025-5",  # MR Upper arm
        "36026-3",  # CT Upper arm - bilateral
        "36027-1",  # CT Upper arm - left
        "36028-9",  # MR Upper arm - left
        "36029-7",  # CT Upper arm - right
        "36030-5",  # MR Upper arm - right
        "36031-3",  # MR Sacroiliac Joint
        "36033-9",  # MR Kidney
        "36034-7",  # MR Kidney - bilateral
        "36035-4",  # MR Kidney - left
        "36036-2",  # MR Kidney - right
        "36037-0",  # CT Knee
        "36040-4",  # CT Knee - bilateral
        "36041-2",  # CT Knee - left
        "36043-8",  # CT Knee - right
        "36045-3",  # MR Larynx
        "36046-1",  # MR Liver
        "36047-9",  # CT Mandible
        "36049-5",  # CT Maxilla and Mandible
        "36050-3",  # CT Maxilla
        "36051-1",  # CT Neck
        "36052-9",  # MR Pancreas
        "36053-7",  # MR Parathyroid gland
        "36054-5",  # CT Brachial plexus
        "36055-2",  # CT Posterior fossa
        "36056-0",  # MR Posterior fossa
        "36057-8",  # CT Prostate
        "36058-6",  # CT Sacrum
        "36059-4",  # MR Sacrum
        "36060-2",  # MR Sacrum and Coccyx
        "36061-0",  # MR Scapula
        "36062-8",  # CT Shoulder
        "36063-6",  # CT Shoulder - bilateral
        "36064-4",  # CT Shoulder - left
        "36066-9",  # CT Shoulder - right
        "36067-7",  # MR Spine
        "36070-1",  # MR Spleen
        "36071-9",  # CT Sternum
        "36072-7",  # MR Sternum
        "36073-5",  # MR Scrotum and testicle
        "36074-3",  # CT Lower leg
        "36075-0",  # MR Lower leg - left
        "36076-8",  # MR Lower leg - right
        "36077-6",  # MRA Portal vein
        "36078-4",  # MRA Renal vein
        "36079-2",  # MRA Lower extremity veins
        "36080-0",  # MRA Upper extremity veins
        "36081-8",  # MRA Vena cava
        "36082-6",  # MRA Inferior vena cava
        "36083-4",  # MR Inferior vena cava
        "36084-2",  # MRA Upper extremity vessels
        "36085-9",  # MRA Neck vessels
        "36086-7",  # CT Abdomen limited
        "36087-5",  # CT Head limited
        "36088-3",  # MR Internal auditory canal limited
        "36089-1",  # CT Chest limited
        "36090-9",  # CT Extremity limited
        "36091-7",  # MR Heart limited
        "36092-5",  # CT Hip limited
        "36093-3",  # MR Lower Extremity Joint limited
        "36094-1",  # MR Upper extremity.joint limited
        "36095-8",  # CT Abdomen limited W contrast IV
        "36096-6",  # MR Brain limited W contrast IV
        "36097-4",  # CT Upper extremity limited W contrast IV
        "36098-2",  # CT Pelvis limited W contrast IV
        "36099-0",  # CT Cervical spine limited W contrast IV
        "36100-6",  # MR Lumbar spine limited W contrast IV
        "36101-4",  # MR Thoracic spine limited W contrast IV
        "36102-2",  # CT Abdomen limited WO and W contrast IV
        "36103-0",  # CT Abdomen limited WO contrast
        "36104-8",  # CT Head limited WO contrast
        "36105-5",  # MR Brain limited WO contrast
        "36106-3",  # CT Lower extremity limited WO contrast
        "36107-1",  # MR Lower extremity joint - left limited WO contrast
        "36108-9",  # CT Pelvis limited WO contrast
        "36109-7",  # CT Cervical spine limited WO contrast
        "36110-5",  # CT Lumbar spine limited WO contrast
        "36111-3",  # MR Lumbar spine limited WO contrast
        "36112-1",  # MR Thoracic spine limited WO contrast
        "36113-9",  # MR Kidney W contrast IV
        "36114-7",  # MR Breast - bilateral dynamic W contrast IV
        "36115-4",  # MR Ankle Arthrogram
        "36116-2",  # MR Ankle - left Arthrogram
        "36117-0",  # MR Ankle - right Arthrogram
        "36118-8",  # MR Elbow - left Arthrogram
        "36119-6",  # MR Elbow - right Arthrogram
        "36120-4",  # MR Hip Arthrogram
        "36121-2",  # MR Hip - left Arthrogram
        "36122-0",  # MR Hip - right Arthrogram
        "36123-8",  # CT Sacroiliac Joint Arthrogram
        "36124-6",  # CT Knee Arthrogram
        "36125-3",  # MR Knee Arthrogram
        "36126-1",  # MR Knee - left Arthrogram
        "36127-9",  # MR Knee - right Arthrogram
        "36128-7",  # CT Shoulder Arthrogram
        "36129-5",  # MR Shoulder Arthrogram
        "36130-3",  # MR Shoulder - left Arthrogram
        "36131-1",  # CT Shoulder - right Arthrogram
        "36132-9",  # MR Shoulder - right Arthrogram
        "36134-5",  # MR Abdomen W contrast IV
        "36135-2",  # CT Ankle W contrast IV
        "36136-0",  # MR Ankle W contrast IV
        "36137-8",  # CT Ankle - left W contrast IV
        "36138-6",  # MR Ankle - left W contrast IV
        "36139-4",  # CT Ankle - right W contrast IV
        "36140-2",  # MR Ankle - right W contrast IV
        "36142-8",  # CT Thoracic and abdominal aorta W contrast IV
        "36143-6",  # CT Abdominal Aorta W contrast IV
        "36145-1",  # CT Appendix W contrast IV
        "36148-5",  # MR Face W contrast IV
        "36149-3",  # MR Breast W contrast IV
        "36150-1",  # MR Breast - bilateral W contrast IV
        "36151-9",  # MR Breast - left W contrast IV
        "36152-7",  # MR Breast - right W contrast IV
        "36155-0",  # MR Internal auditory canal W contrast IV
        "36156-8",  # MR Chest W contrast IV
        "36157-6",  # CT Elbow W contrast IV
        "36158-4",  # MR Elbow W contrast IV
        "36159-2",  # CT Elbow - left W contrast IV
        "36160-0",  # MR Elbow - left W contrast IV
        "36161-8",  # CT Elbow - right W contrast IV
        "36162-6",  # MR Elbow - right W contrast IV
        "36163-4",  # MR Lower extremity - bilateral W contrast IV
        "36164-2",  # CT Lower extremity - left W contrast IV
        "36165-9",  # MR Lower extremity - left W contrast IV
        "36166-7",  # CT Lower extremity - right W contrast IV
        "36167-5",  # MR Lower extremity - right W contrast IV
        "36168-3",  # CT Upper extremity - bilateral W contrast IV
        "36169-1",  # CT Upper extremity - left W contrast IV
        "36170-9",  # CT Upper extremity - right W contrast IV
        "36171-7",  # MR Upper extremity - right W contrast IV
        "36172-5",  # CT Thigh W contrast IV
        "36173-3",  # MR Thigh W contrast IV
        "36174-1",  # CT Thigh - left W contrast IV
        "36175-8",  # MR Thigh - left W contrast IV
        "36176-6",  # CT Thigh - right W contrast IV
        "36177-4",  # MR Thigh - right W contrast IV
        "36178-2",  # CT Foot W contrast IV
        "36179-0",  # MR Foot W contrast IV
        "36180-8",  # MR Foot - bilateral W contrast IV
        "36181-6",  # CT Foot - left W contrast IV
        "36182-4",  # MR Foot - left W contrast IV
        "36183-2",  # CT Foot - right W contrast IV
        "36184-0",  # MR Foot - right W contrast IV
        "36185-7",  # CT Forearm W contrast IV
        "36186-5",  # MR Forearm W contrast IV
        "36187-3",  # CT Forearm - left W contrast IV
        "36188-1",  # MR Forearm - left W contrast IV
        "36189-9",  # CT Forearm - right W contrast IV
        "36190-7",  # MR Forearm - right W contrast IV
        "36191-5",  # CT Hand W contrast IV
        "36192-3",  # MR Hand W contrast IV
        "36193-1",  # CT Hand - left W contrast IV
        "36194-9",  # MR Hand - left W contrast IV
        "36195-6",  # CT Hand - right W contrast IV
        "36196-4",  # MR Hand - right W contrast IV
        "36197-2",  # MR Heart W contrast IV
        "36199-8",  # MR Hip W contrast IV
        "36200-4",  # CT Hip W contrast IV
        "36201-2",  # CT Hip - bilateral W contrast IV
        "36202-0",  # MR Hip - bilateral W contrast IV
        "36203-8",  # CT Hip - left W contrast IV
        "36204-6",  # MR Hip - left W contrast IV
        "36205-3",  # CT Hip - right W contrast IV
        "36206-1",  # MR Hip - right W contrast IV
        "36207-9",  # CT Upper arm W contrast IV
        "36208-7",  # MR Upper arm W contrast IV
        "36209-5",  # CT Upper arm - left W contrast IV
        "36210-3",  # MR Upper arm - left W contrast IV
        "36211-1",  # CT Upper arm - right W contrast IV
        "36212-9",  # MR Upper arm - right W contrast IV
        "36213-7",  # MR Lower Extremity Joint W contrast IV
        "36214-5",  # MR Lower extremity joint - left W contrast IV
        "36215-2",  # MR Lower extremity joint - right W contrast IV
        "36216-0",  # MR Upper extremity.joint W contrast IV
        "36217-8",  # CT Sacroiliac Joint W contrast IV
        "36218-6",  # MR Sacroiliac Joint W contrast IV
        "36219-4",  # MR Kidney - bilateral W contrast IV
        "36220-2",  # MR Kidney - left W contrast IV
        "36221-0",  # MR Kidney - right W contrast IV
        "36222-8",  # CT Knee W contrast IV
        "36223-6",  # MR Knee W contrast IV
        "36224-4",  # MR Knee - bilateral W contrast IV
        "36225-1",  # CT Knee - left W contrast IV
        "36226-9",  # MR Knee - left W contrast IV
        "36227-7",  # CT Knee - right W contrast IV
        "36228-5",  # MR Knee - right W contrast IV
        "36229-3",  # CT Larynx W contrast IV
        "36230-1",  # MR Larynx W contrast IV
        "36231-9",  # MR Liver W contrast IV
        "36232-7",  # CT Mandible W contrast IV
        "36233-5",  # MR Nasopharynx W contrast IV
        "36235-0",  # CT Neck W contrast IV
        "36236-8",  # MR Pancreas W contrast IV
        "36237-6",  # MR Pelvis W contrast IV
        "36238-4",  # MR Pituitary and Sella turcica W contrast IV
        "36239-2",  # MR Brachial plexus W contrast IV
        "36240-0",  # MR Brachial plexus - left W contrast IV
        "36241-8",  # MR Brachial plexus - right W contrast IV
        "36242-6",  # CT Posterior fossa W contrast IV
        "36243-4",  # MR Posterior fossa W contrast IV
        "36244-2",  # MR Prostate W contrast IV
        "36245-9",  # CT Sacrum W contrast IV
        "36246-7",  # MR Sacrum W contrast IV
        "36247-5",  # MR Sacrum and Coccyx W contrast IV
        "36248-3",  # MR Scapula - left W contrast IV
        "36249-1",  # MR Scapula - right W contrast IV
        "36250-9",  # CT Shoulder W contrast IV
        "36251-7",  # MR Shoulder W contrast IV
        "36252-5",  # CT Shoulder - left W contrast IV
        "36253-3",  # CT Shoulder - right W contrast IV
        "36254-1",  # MR Shoulder - right W contrast IV
        "36255-8",  # CT Sinuses W contrast IV
        "36256-6",  # MR Spine W contrast IV
        "36257-4",  # CT Sternum W contrast IV
        "36258-2",  # CT Lower leg W contrast IV
        "36259-0",  # MR Lower leg W contrast IV
        "36260-8",  # CT Lower leg - left W contrast IV
        "36261-6",  # MR Lower leg - left W contrast IV
        "36262-4",  # CT Lower leg - right W contrast IV
        "36263-2",  # MR Lower leg - right W contrast IV
        "36264-0",  # CT Uterus W contrast IV
        "36265-7",  # MR Uterus W contrast IV
        "36267-3",  # CT Abdomen WO and W contrast IV
        "36268-1",  # CT Ankle WO and W contrast IV
        "36269-9",  # CT Ankle - left WO and W contrast IV
        "36270-7",  # CT Ankle - right WO and W contrast IV
        "36271-5",  # CT Abdominal Aorta WO and W contrast IV
        "36272-3",  # MRA Abdominal Aorta WO and W contrast IV
        "36273-1",  # MR Abdominal Aorta WO and W contrast IV
        "36274-9",  # MRA Thoracic Aorta WO and W contrast IV
        "36275-6",  # MRA Renal artery WO and W contrast IV
        "36276-4",  # MR Breast WO and W contrast IV
        "36277-2",  # MR Breast - bilateral WO and W contrast IV
        "36278-0",  # MR Breast - left WO and W contrast IV
        "36279-8",  # MR Breast - right WO and W contrast IV
        "36282-2",  # CT Internal auditory canal WO and W contrast IV
        "36283-0",  # MR Chest WO and W contrast IV
        "36284-8",  # MR Chest and Abdomen WO and W contrast IV
        "36285-5",  # CT Elbow WO and W contrast IV
        "36286-3",  # CT Elbow - left WO and W contrast IV
        "36287-1",  # CT Elbow - right WO and W contrast IV
        "36288-9",  # CT Lower extremity WO and W contrast IV
        "36289-7",  # MR Lower extremity - bilateral WO and W contrast IV
        "36290-5",  # CT Lower extremity - left WO and W contrast IV
        "36291-3",  # MR Lower extremity - left WO and W contrast IV
        "36292-1",  # CT Lower extremity - right WO and W contrast IV
        "36293-9",  # XR Abdomen 3 Views
        "36294-7",  # XR Ankle 3 Views
        "36295-4",  # XR Ankle - bilateral 3 Views
        "36296-2",  # XR Ankle - left 3 Views
        "36297-0",  # XR Facial bones 3 Views
        "36298-8",  # XR Chest 3 Views
        "36299-6",  # XR Elbow 3 Views
        "36300-2",  # XR Elbow - bilateral 3 Views
        "36301-0",  # XR Elbow - left 3 Views
        "36302-8",  # XR Femur 3 Views
        "36303-6",  # XR Finger 3 Views
        "36304-4",  # XR Finger - left 3 Views
        "36305-1",  # XR Foot 3 Views
        "36306-9",  # XR Foot - bilateral 3 Views
        "36307-7",  # XR Foot - left 3 Views
        "36308-5",  # XR Hip - bilateral 3 Views
        "36309-3",  # XR Hip - left 3 Views
        "36310-1",  # XR Knee - bilateral 3 Views
        "36311-9",  # XR Knee - left 3 Views
        "36312-7",  # XR Mandible 3 Views
        "36313-5",  # XR Ribs - bilateral 3 Views
        "36314-3",  # XR Ribs - left 3 Views
        "36315-0",  # XR Thumb - left 3 Views
        "36316-8",  # XR Toes - left 3 Views
        "36317-6",  # XR Ankle 4 Views
        "36318-4",  # XR Facial bones 4 Views
        "36320-0",  # XR Chest 4 Views
        "36322-6",  # XR Elbow - bilateral 4 Views
        "36323-4",  # XR Elbow - left 4 Views
        "36324-2",  # XR Femur - left 4 Views
        "36325-9",  # XR Knee - bilateral 4 Views
        "36326-7",  # XR Knee - left 4 Views
        "36327-5",  # XR Mandible 4 Views
        "36328-3",  # XR Ribs - bilateral 4 Views
        "36329-1",  # XR Shoulder - bilateral 4 Views
        "36330-9",  # XR Shoulder - left 4 Views
        "36331-7",  # XR Cervical spine 4 Views
        "36332-5",  # XR Lumbar spine 4 Views
        "36333-3",  # MR Lower extremity - right WO and W contrast IV
        "36334-1",  # CT Upper extremity WO and W contrast IV
        "36335-8",  # CT Upper extremity - left WO and W contrast IV
        "36336-6",  # CT Upper extremity - right WO and W contrast IV
        "36337-4",  # MR Upper extremity - right WO and W contrast IV
        "36338-2",  # CT Thigh WO and W contrast IV
        "36339-0",  # CT Thigh - left WO and W contrast IV
        "36340-8",  # CT Thigh - right WO and W contrast IV
        "36341-6",  # CT Foot WO and W contrast IV
        "36342-4",  # MR Foot - bilateral WO and W contrast IV
        "36343-2",  # CT Foot - left WO and W contrast IV
        "36344-0",  # MR Foot - left WO and W contrast IV
        "36345-7",  # CT Foot - right WO and W contrast IV
        "36346-5",  # MR Foot - right WO and W contrast IV
        "36347-3",  # CT Forearm WO and W contrast IV
        "36348-1",  # CT Forearm - left WO and W contrast IV
        "36349-9",  # MR Forearm - left WO and W contrast IV
        "36350-7",  # CT Forearm - right WO and W contrast IV
        "36351-5",  # MR Forearm - right WO and W contrast IV
        "36352-3",  # CT Hand WO and W contrast IV
        "36353-1",  # CT Hand - left WO and W contrast IV
        "36354-9",  # MR Hand - left WO and W contrast IV
        "36355-6",  # CT Hand - right WO and W contrast IV
        "36356-4",  # MR Hand - right WO and W contrast IV
        "36357-2",  # MR Heart WO and W contrast IV
        "36359-8",  # CT Hip WO and W contrast IV
        "36360-6",  # CT Hip - bilateral WO and W contrast IV
        "36361-4",  # MR Hip - bilateral WO and W contrast IV
        "36362-2",  # CT Hip - left WO and W contrast IV
        "36363-0",  # MR Hip - left WO and W contrast IV
        "36364-8",  # CT Hip - right WO and W contrast IV
        "36365-5",  # MR Hip - right WO and W contrast IV
        "36366-3",  # CT Upper arm WO and W contrast IV
        "36367-1",  # CT Upper arm - left WO and W contrast IV
        "36368-9",  # MR Upper arm - left WO and W contrast IV
        "36369-7",  # CT Upper arm - right WO and W contrast IV
        "36370-5",  # MR Upper arm - right WO and W contrast IV
        "36371-3",  # MR Lower Extremity Joint WO and W contrast IV
        "36372-1",  # MR Lower extremity joint - left WO and W contrast IV
        "36373-9",  # MR Lower extremity joint - right WO and W contrast IV
        "36374-7",  # MR Upper extremity.joint WO and W contrast IV
        "36375-4",  # CT Sacroiliac Joint WO and W contrast IV
        "36376-2",  # MR Sacroiliac Joint WO and W contrast IV
        "36377-0",  # CT Kidney - bilateral WO and W contrast IV
        "36378-8",  # MR Kidney - bilateral WO and W contrast IV
        "36379-6",  # CT Knee WO and W contrast IV
        "36380-4",  # CT Knee - left WO and W contrast IV
        "36381-2",  # CT Knee - right WO and W contrast IV
        "36382-0",  # MR Larynx WO and W contrast IV
        "36383-8",  # CT Mandible WO and W contrast IV
        "36384-6",  # MR Nasopharynx WO and W contrast IV
        "36385-3",  # MR Pancreas WO and W contrast IV
        "36387-9",  # CT Posterior fossa WO and W contrast IV
        "36388-7",  # MR Posterior fossa WO and W contrast IV
        "36389-5",  # MR Prostate WO and W contrast IV
        "36390-3",  # CT Sacrum WO and W contrast IV
        "36391-1",  # MR Sacrum WO and W contrast IV
        "36392-9",  # MR Sacrum and Coccyx WO and W contrast IV
        "36393-7",  # MR Scapula - left WO and W contrast IV
        "36394-5",  # MR Scapula - right WO and W contrast IV
        "36395-2",  # CT Shoulder WO and W contrast IV
        "36396-0",  # CT Shoulder - left WO and W contrast IV
        "36397-8",  # CT Shoulder - right WO and W contrast IV
        "36398-6",  # CT Sinuses WO and W contrast IV
        "36399-4",  # CT Spine WO and W contrast IV
        "36400-0",  # MR Spine WO and W contrast IV
        "36401-8",  # CT Cervical spine WO and W contrast IV
        "36402-6",  # CT Lumbar spine WO and W contrast IV
        "36403-4",  # CT Thoracic spine WO and W contrast IV
        "36404-2",  # MR Spleen WO and W contrast IV
        "36405-9",  # CT Sternum WO and W contrast IV
        "36406-7",  # MR Scrotum and testicle WO and W contrast IV
        "36407-5",  # MR Thyroid gland WO and W contrast IV
        "36408-3",  # CT Lower leg WO and W contrast IV
        "36409-1",  # CT Lower leg - left WO and W contrast IV
        "36410-9",  # MR Lower leg - left WO and W contrast IV
        "36411-7",  # CT Lower leg - right WO and W contrast IV
        "36412-5",  # MR Lower leg - right WO and W contrast IV
        "36413-3",  # MR Uterus WO and W contrast IV
        "36414-1",  # MRA Portal vein WO and W contrast IV
        "36415-8",  # MRA Renal vein WO and W contrast IV
        "36416-6",  # MRA Lower extremity veins WO and W contrast IV
        "36417-4",  # MRA Upper extremity veins WO and W contrast IV
        "36418-2",  # MR Inferior vena cava WO and W contrast IV
        "36419-0",  # MR Superior vena cava WO and W contrast IV
        "36420-8",  # MRA Chest vessels WO and W contrast IV
        "36422-4",  # MRA Upper extremity vessels WO and W contrast IV
        "36423-2",  # MRA Neck vessels WO and W contrast IV
        "36424-0",  # CT Abdomen WO contrast
        "36425-7",  # CT Ankle WO contrast
        "36426-5",  # CT Ankle - left WO contrast
        "36427-3",  # MR Ankle - left WO contrast
        "36428-1",  # CT Ankle - right WO contrast
        "36429-9",  # MR Ankle - right WO contrast
        "36430-7",  # CT Thoracic and abdominal aorta WO contrast
        "36431-5",  # CT Abdominal Aorta WO contrast
        "36432-3",  # MRA Abdominal Aorta WO contrast
        "36433-1",  # MRA Thoracic Aorta WO contrast
        "36434-9",  # CT Appendix WO contrast
        "36435-6",  # MR Face WO contrast
        "36436-4",  # MR Breast WO contrast
        "36437-2",  # MR Breast - bilateral WO contrast
        "36438-0",  # MR Breast - left WO contrast
        "36439-8",  # MR Breast - right WO contrast
        "36442-2",  # MR Chest WO contrast
        "36443-0",  # CT Elbow WO contrast
        "36444-8",  # CT Elbow - bilateral WO contrast
        "36445-5",  # CT Elbow - left WO contrast
        "36446-3",  # MR Elbow - left WO contrast
        "36447-1",  # CT Elbow - right WO contrast
        "36448-9",  # MR Elbow - right WO contrast
        "36449-7",  # CT Lower extremity - bilateral WO contrast
        "36450-5",  # MRA Lower extremity vessels - bilateral WO contrast
        "36451-3",  # MR Lower extremity - bilateral WO contrast
        "36452-1",  # CT Lower extremity - left WO contrast
        "36453-9",  # MR Lower extremity - left WO contrast
        "36454-7",  # CT Lower extremity - right WO contrast
        "36455-4",  # MR Lower extremity - right WO contrast
        "36456-2",  # CT Upper extremity - bilateral WO contrast
        "36457-0",  # CT Upper extremity - left WO contrast
        "36458-8",  # CT Upper extremity - right WO contrast
        "36459-6",  # MR Upper extremity - right WO contrast
        "36460-4",  # CT Thigh WO contrast
        "36461-2",  # MR Thigh WO contrast
        "36462-0",  # CT Thigh - left WO contrast
        "36463-8",  # MR Thigh - left WO contrast
        "36464-6",  # CT Thigh - right WO contrast
        "36465-3",  # MR Thigh - right WO contrast
        "36466-1",  # CT Foot WO contrast
        "36467-9",  # MR Foot - bilateral WO contrast
        "36468-7",  # CT Foot - left WO contrast
        "36469-5",  # MR Foot - left WO contrast
        "36470-3",  # CT Foot - right WO contrast
        "36471-1",  # MR Foot - right WO contrast
        "36472-9",  # CT Forearm WO contrast
        "36473-7",  # CT Forearm - left WO contrast
        "36474-5",  # MR Forearm - left WO contrast
        "36475-2",  # CT Forearm - right WO contrast
        "36476-0",  # MR Forearm - right WO contrast
        "36477-8",  # CT Hand WO contrast
        "36478-6",  # CT Hand - left WO contrast
        "36479-4",  # MR Hand - left WO contrast
        "36480-2",  # CT Hand - right WO contrast
        "36481-0",  # MR Hand - right WO contrast
        "36482-8",  # MR Heart WO contrast
        "36484-4",  # CT Hip WO contrast
        "36485-1",  # CT Hip - bilateral WO contrast
        "36486-9",  # MR Hip - bilateral WO contrast
        "36487-7",  # CT Hip - left WO contrast
        "36488-5",  # MR Hip - left WO contrast
        "36489-3",  # CT Hip - right WO contrast
        "36490-1",  # MR Hip - right WO contrast
        "36491-9",  # CT Upper arm WO contrast
        "36492-7",  # CT Upper arm - left WO contrast
        "36493-5",  # MR Upper arm - left WO contrast
        "36494-3",  # CT Upper arm - right WO contrast
        "36495-0",  # MR Upper arm - right WO contrast
        "36496-8",  # MR Acromioclavicular Joint WO contrast
        "36497-6",  # MR Lower Extremity Joint WO contrast
        "36498-4",  # MR Lower extremity joint - left WO contrast
        "36499-2",  # MR Lower extremity joint - right WO contrast
        "36500-7",  # MR Upper extremity.joint WO contrast
        "36501-5",  # CT Sacroiliac Joint WO contrast
        "36502-3",  # MR Sacroiliac Joint WO contrast
        "36503-1",  # CT Kidney - bilateral WO contrast
        "36504-9",  # MR Kidney - bilateral WO contrast
        "36505-6",  # CT Knee WO contrast
        "36506-4",  # MR Knee - bilateral WO contrast
        "36507-2",  # CT Knee - left WO contrast
        "36508-0",  # MR Knee - left WO contrast
        "36509-8",  # CT Knee - right WO contrast
        "36510-6",  # MR Knee - right WO contrast
        "36511-4",  # CT Larynx WO contrast
        "36512-2",  # CT Mandible WO contrast
        "36513-0",  # MR Nasopharynx WO contrast
        "36514-8",  # CT Neck WO contrast
        "36515-5",  # MR Pancreas WO contrast
        "36516-3",  # MR Brachial plexus - right WO contrast
        "36517-1",  # CT Posterior fossa WO contrast
        "36518-9",  # MR Posterior fossa WO contrast
        "36519-7",  # MR Prostate WO contrast
        "36520-5",  # CT Sacrum WO contrast
        "36521-3",  # MR Sacrum WO contrast
        "36522-1",  # MR Sacrum and Coccyx WO contrast
        "36523-9",  # MR Scapula - left WO contrast
        "36524-7",  # CT Shoulder WO contrast
        "36525-4",  # MR Shoulder - bilateral WO contrast
        "36526-2",  # CT Shoulder - left WO contrast
        "36527-0",  # CT Shoulder - right WO contrast
        "36528-8",  # MR Shoulder - right WO contrast
        "36529-6",  # CT Sinuses WO contrast
        "36530-4",  # CT Spine WO contrast
        "36531-2",  # MR Spine WO contrast
        "36532-0",  # MR Thoracic spine WO contrast
        "36533-8",  # MR Spleen WO contrast
        "36534-6",  # CT Sternum WO contrast
        "36535-3",  # MR Scrotum and testicle WO contrast
        "36536-1",  # MR Thyroid gland WO contrast
        "36537-9",  # CT Lower leg WO contrast
        "36538-7",  # CT Lower leg - left WO contrast
        "36539-5",  # MR Lower leg - left WO contrast
        "36540-3",  # CT Lower leg - right WO contrast
        "36541-1",  # MR Lower leg - right WO contrast
        "36542-9",  # MR Uterus WO contrast
        "36543-7",  # MRA Portal vein WO contrast
        "36544-5",  # MRA Renal vein WO contrast
        "36545-2",  # MR Inferior vena cava WO contrast
        "36546-0",  # MR Superior vena cava WO contrast
        "36547-8",  # MRA Chest vessels WO contrast
        "36548-6",  # MRA Upper extremity vessels WO contrast
        "36549-4",  # MRA Neck vessels WO contrast
        "36550-2",  # XR Abdomen Single view
        "36551-0",  # XR Ankle Single view
        "36554-4",  # XR Chest Single view
        "36555-1",  # XR Clavicle Single view
        "36556-9",  # XR Elbow Single view
        "36557-7",  # XR Lower extremity - bilateral Single view
        "36558-5",  # XR Lower extremity - left Single view
        "36559-3",  # XR Femur Single view
        "36560-1",  # XR Femur - left Single view
        "36561-9",  # XR Foot Single view
        "36563-5",  # XR Hand Single view
        "36564-3",  # XR Calcaneus Single view
        "36565-0",  # XR Humerus Single view
        "36566-8",  # XR Knee - bilateral Single view
        "36567-6",  # XR Knee - left Single view
        "36568-4",  # XR Shoulder - bilateral Single view
        "36569-2",  # XR Shoulder - left Single view
        "36570-0",  # XR Wrist - left Single view
        "36571-8",  # XR Ankle AP
        "36572-6",  # XR Chest AP
        "36573-4",  # XR Clavicle AP
        "36574-2",  # XR Lower extremity AP
        "36575-9",  # XR Femur AP
        "36576-7",  # XR Finger fifth AP
        "36577-5",  # XR Finger fourth AP
        "36578-3",  # XR Finger third AP
        "36579-1",  # XR Foot AP
        "36580-9",  # XR Foot - bilateral AP
        "36581-7",  # XR Hip AP
        "36582-5",  # XR Hip - left AP
        "36583-3",  # XR Acromioclavicular joint - left AP
        "36584-1",  # XR Knee AP
        "36585-8",  # XR Knee - bilateral AP
        "36586-6",  # XR Shoulder - bilateral AP
        "36587-4",  # XR Shoulder - left AP
        "36590-8",  # XR Knee - bilateral AP and Lateral
        "36591-6",  # XR Abdomen Lateral
        "36592-4",  # XR Ankle Lateral
        "36593-2",  # XR Femur Lateral
        "36594-0",  # XR Finger fifth Lateral
        "36595-7",  # XR Finger fourth Lateral
        "36596-5",  # XR Finger second Lateral
        "36597-3",  # XR Finger third Lateral
        "36598-1",  # XR Foot - left Lateral
        "36599-9",  # XR Hand Lateral
        "36600-5",  # XR Hand - bilateral Lateral
        "36601-3",  # XR Hand - left Lateral
        "36602-1",  # XR Hip Lateral
        "36603-9",  # XR Hip - left Lateral
        "36604-7",  # XR Knee Lateral
        "36605-4",  # XR Knee - bilateral Lateral
        "36606-2",  # XR Knee - left Lateral
        "36607-0",  # XR Abdomen Oblique
        "36608-8",  # XR Elbow Oblique Views
        "36609-6",  # XR Femur Oblique
        "36610-4",  # XR Finger fifth Oblique
        "36611-2",  # XR Finger fourth Oblique
        "36612-0",  # XR Finger second Oblique
        "36613-8",  # XR Finger third Oblique
        "36614-6",  # XR Foot Oblique
        "36615-3",  # XR Foot - left Oblique
        "36616-1",  # XR Hand Oblique
        "36617-9",  # XR Hip Oblique
        "36618-7",  # XR Hip - bilateral Oblique
        "36619-5",  # XR Knee Oblique Views
        "36620-3",  # XR Chest Left anterior oblique
        "36621-1",  # XR Hand PA
        "36622-9",  # XR Hand - bilateral PA
        "36623-7",  # XR Hand - left PA
        "36624-5",  # XR Wrist - bilateral PA
        "36628-6",  # XR Internal auditory canal Views
        "36629-4",  # XR Hand - bilateral Views
        "36630-2",  # XR Hand - left Views
        "36631-0",  # XR Pelvis and Hip - left Views
        "36632-8",  # XR Humerus - left Views
        "36633-6",  # XR Sacroiliac joint - bilateral Views
        "36634-4",  # XR Sacroiliac joint - left Views
        "36635-1",  # XR Knee - bilateral Views
        "36636-9",  # XR Knee - left Views
        "36637-7",  # XR Maxilla Views
        "36638-5",  # XR Patella - bilateral Views
        "36639-3",  # XR Patella - left Views
        "36640-1",  # RF Cervical spine Views
        "36641-9",  # XR Abdomen 2 Views
        "36643-5",  # XR Chest 2 Views
        "36645-0",  # XR Clavicle 2 Views
        "36646-8",  # XR Clavicle - left 2 Views
        "36647-6",  # XR Coccyx 2 Views
        "36648-4",  # XR Elbow 2 Views
        "36649-2",  # XR Elbow - bilateral 2 Views
        "36650-0",  # XR Elbow - left 2 Views
        "36651-8",  # XR Lower extremity 2 Views
        "36652-6",  # XR Femur 2 Views
        "36653-4",  # XR Femur - bilateral 2 Views
        "36654-2",  # XR Femur - left 2 Views
        "36655-9",  # XR Finger 2 Views
        "36656-7",  # XR Finger - left 2 Views
        "36657-5",  # XR Foot - bilateral 2 Views
        "36658-3",  # XR Radius and Ulna 2 Views
        "36659-1",  # XR Radius and Ulna - bilateral 2 Views
        "36660-9",  # XR Radius and Ulna - left 2 Views
        "36661-7",  # XR Calcaneus 2 Views
        "36662-5",  # XR Calcaneus - left 2 Views
        "36663-3",  # XR Hip 2 Views
        "36664-1",  # XR Hip - left 2 Views
        "36665-8",  # XR Acromioclavicular joint - left 2 Views
        "36666-6",  # XR Scapula - left 2 Views
        "36667-4",  # XR Shoulder - bilateral 2 Views
        "36668-2",  # XR Shoulder - left 2 Views
        "36669-0",  # XR Cervical spine 2 Views
        "36670-8",  # XR Lumbar spine 2 Views
        "36671-6",  # XR Tibia and Fibula - bilateral 2 Views
        "36672-4",  # XR Tibia and Fibula - left 2 Views
        "36673-2",  # XR Toes - left 2 Views
        "36675-7",  # XR Facial bones 5 Views
        "36676-5",  # XR Knee - left 5 Views
        "36677-3",  # XR Shoulder - left 5 Views
        "36678-1",  # XR Knee - bilateral 6 Views
        "36679-9",  # XR Shoulder - left 6 Views
        "36680-7",  # XR Cervical spine 7 Views
        "36681-5",  # XR Lumbar spine 7 Views
        "36682-3",  # XR Knee - bilateral 8 Views
        "36683-1",  # XR Wrist - left 8 Views
        "36684-9",  # XR Ankle - bilateral AP and Lateral
        "36685-6",  # XR Ankle - left AP and Lateral
        "36686-4",  # XR Calcaneus - bilateral AP and Lateral
        "36687-2",  # XR Chest AP and Lateral
        "36688-0",  # XR Coccyx AP and Lateral
        "36689-8",  # XR Elbow AP and Lateral
        "36690-6",  # XR Elbow - bilateral AP and Lateral
        "36691-4",  # XR Elbow - left AP and Lateral
        "36692-2",  # XR Lower extremity AP and Lateral
        "36693-0",  # XR Femur AP and Lateral
        "36694-8",  # XR Femur - bilateral AP and Lateral
        "36695-5",  # XR Femur - left AP and Lateral
        "36696-3",  # XR Foot - bilateral AP and Lateral
        "36697-1",  # XR Foot - left AP and Lateral
        "36698-9",  # XR Radius and Ulna AP and Lateral
        "36699-7",  # XR Radius and Ulna - bilateral AP and Lateral
        "36700-3",  # XR Radius and Ulna - left AP and Lateral
        "36701-1",  # XR Calcaneus - left AP and Lateral
        "36702-9",  # XR Hip AP and Lateral
        "36703-7",  # XR Hip - bilateral AP and Lateral
        "36704-5",  # XR Hip - left AP and Lateral
        "36705-2",  # XR Pelvis and Hip AP and Lateral
        "36706-0",  # XR Humerus AP and Lateral
        "36707-8",  # XR Humerus - bilateral AP and Lateral
        "36708-6",  # XR Humerus - left AP and Lateral
        "36709-4",  # XR Knee AP and Lateral
        "36710-2",  # XR Knee - left AP and Lateral
        "36711-0",  # XR Mandible AP and Lateral
        "36712-8",  # XR Patella - bilateral AP and Lateral
        "36713-6",  # XR Patella - left AP and Lateral
        "36714-4",  # XR Scapula - bilateral AP and Lateral
        "36715-1",  # XR Scapula - left AP and Lateral
        "36716-9",  # XR Shoulder - bilateral AP and Lateral
        "36717-7",  # XR Tibia and Fibula - bilateral AP and Lateral
        "36718-5",  # XR Tibia and Fibula - left AP and Lateral
        "36719-3",  # XR Toes - left AP and Lateral
        "36720-1",  # XR Ankle - bilateral AP and Lateral and oblique
        "36721-9",  # XR Ankle - left AP and Lateral and oblique
        "36722-7",  # XR Elbow AP and Lateral and oblique
        "36723-5",  # XR Elbow - bilateral AP and Lateral and oblique
        "36724-3",  # XR Elbow - left AP and Lateral and oblique
        "36725-0",  # XR Finger AP and Lateral and oblique
        "36726-8",  # XR Finger - bilateral AP and Lateral and oblique
        "36727-6",  # XR Finger - left AP and Lateral and oblique
        "36728-4",  # XR Foot AP and Lateral and oblique
        "36729-2",  # XR Foot - bilateral AP and Lateral and oblique
        "36730-0",  # XR Foot - left AP and Lateral and oblique
        "36731-8",  # XR Calcaneus AP and Lateral and oblique
        "36732-6",  # XR Knee - bilateral AP and Lateral and oblique
        "36733-4",  # XR Knee - left AP and Lateral and oblique
        "36734-2",  # XR Cervical spine AP and Lateral and oblique
        "36735-9",  # XR Lumbar spine AP and Lateral and oblique
        "36736-7",  # XR Thumb - left AP and Lateral and oblique
        "36737-5",  # XR Facial bones Limited Views
        "36738-3",  # XR Mandible Limited Views
        "36739-1",  # XR Wrist - bilateral Limited Views
        "36740-9",  # XR Elbow - bilateral Oblique Views
        "36741-7",  # XR Elbow - left Oblique Views
        "36742-5",  # XR Radius and Ulna - bilateral Oblique Views
        "36743-3",  # XR Radius and Ulna - left Oblique Views
        "36744-1",  # XR Humerus - left Oblique Views
        "36745-8",  # XR Knee - bilateral Oblique Views
        "36746-6",  # XR Knee - left Oblique Views
        "36747-4",  # XR Mandible Oblique Views
        "36748-2",  # XR Cervical spine Oblique Views
        "36749-0",  # XR Tibia and Fibula - left Oblique Views
        "36750-8",  # XR Chest PA and AP lateral-decubitus
        "36752-4",  # XR Hand - bilateral PA and Lateral
        "36753-2",  # XR Hand - left PA and Lateral
        "36754-0",  # XR Mandible PA and Lateral
        "36755-7",  # XR Hand PA and Lateral and Oblique
        "36756-5",  # XR Hand - bilateral PA and Lateral and Oblique
        "36757-3",  # XR Hand - left PA and Lateral and Oblique
        "36758-1",  # XR Chest PA and Lateral and Oblique and Apical lordotic
        "36759-9",  # XR Chest PA and Apical lordotic
        "36761-5",  # RF Guidance for balloon dilatation of Biliary ducts-- W contrast
        "36767-2",  # CT Guidance for biopsy of Adrenal gland
        "36768-0",  # CT Guidance for percutaneous biopsy of Muscle
        "36769-8",  # CT Guidance for exchange of nephrostomy tube of Kidney
        "36770-6",  # CT Guidance for drainage and placement of drainage catheter of Biliary ducts and Gallbladder
        "36771-4",  # RF Guidance for injection of Joint
        "36772-2",  # CT Guidance for placement of nephrostomy tube in Kidney
        "36773-0",  # CT Temporal bone
        "36774-8",  # MR Upper extremity joint - left
        "36775-5",  # MR Upper extremity joint - right
        "36777-1",  # MR Orbit
        "36778-9",  # MR Orbit - right
        "36779-7",  # MR Ovary
        "36780-5",  # MR Toe
        "36781-3",  # MRA Abdominal veins
        "36782-1",  # MRA Subclavian artery
        "36783-9",  # MRA Veins
        "36784-7",  # MRA Lower extremity veins - left
        "36785-4",  # MRA Lower extremity veins - right
        "36786-2",  # MRA Upper extremity veins - left
        "36787-0",  # MRA Upper extremity veins - right
        "36788-8",  # MRA Neck veins
        "36789-6",  # MRA Pelvis veins
        "36790-4",  # MRA Inferior vena cava + tributaries
        "36791-2",  # MRA Abdominal vessels
        "36792-0",  # MRA Adrenal vessels
        "36794-6",  # MRA Extremity vessels
        "36795-3",  # MRA Lower extremity vessels - left
        "36796-1",  # MRA Lower extremity vessels - right
        "36797-9",  # MRA Upper extremity vessels - left
        "36798-7",  # MRA Upper extremity vessels - right
        "36799-5",  # MRA Knee vessels
        "36800-1",  # MRA Knee vessels - left
        "36801-9",  # MRA Knee vessels - right
        "36802-7",  # MRA Orbit vessels
        "36803-5",  # MRA Pulmonary vessels
        "36804-3",  # MRA Renal vessels - bilateral
        "36805-0",  # MRA Shoulder vessels
        "36806-8",  # MRA Shoulder vessels - left
        "36807-6",  # MRA Shoulder vessels - right
        "36808-4",  # MRA Head vessels limited
        "36811-8",  # CT Joint Arthrogram
        "36812-6",  # MR Joint Arthrogram
        "36813-4",  # CT Abdomen and Pelvis W contrast IV
        "36815-9",  # CT Temporal bone W contrast IV
        "36816-7",  # CT Temporal bone - right W contrast IV
        "36817-5",  # MR Upper extremity joint - bilateral W contrast IV
        "36818-3",  # MR Upper extremity joint - left W contrast IV
        "36819-1",  # MR Upper extremity joint - right W contrast IV
        "36820-9",  # MR Orbit W contrast IV
        "36821-7",  # MR Orbit - left W contrast IV
        "36822-5",  # MR Orbit - right W contrast IV
        "36823-3",  # MR Ovary W contrast IV
        "36826-6",  # MRA Head veins W contrast IV
        "36827-4",  # MRA Neck veins W contrast IV
        "36832-4",  # MRA Orbit vessels W contrast IV
        "36835-7",  # CT Petrous part of temporal bone WO and W contrast IV
        "36837-3",  # CT Temporal bone WO and W contrast IV
        "36838-1",  # XR Mastoid 3 Views
        "36839-9",  # XR Mastoid 4 Views
        "36840-7",  # MR Upper extremity joint - left WO and W contrast IV
        "36841-5",  # MR Upper extremity joint - right WO and W contrast IV
        "36842-3",  # MR Orbit WO and W contrast IV
        "36843-1",  # MR Orbit - left WO and W contrast IV
        "36844-9",  # MR Orbit - right WO and W contrast IV
        "36845-6",  # MR Ovary WO and W contrast IV
        "36846-4",  # MRA Abdominal veins WO and W contrast IV
        "36847-2",  # MRA Head veins WO and W contrast IV
        "36848-0",  # MRA Chest veins WO and W contrast IV
        "36849-8",  # MRA Lower extremity veins - left WO and W contrast IV
        "36850-6",  # MRA Lower extremity veins - right WO and W contrast IV
        "36851-4",  # MRA Upper extremity veins - left WO and W contrast IV
        "36852-2",  # MRA Upper extremity veins - right WO and W contrast IV
        "36853-0",  # MRA Neck veins WO and W contrast IV
        "36854-8",  # MRA Pelvis veins WO and W contrast IV
        "36855-5",  # MRA Abdominal vessels WO and W contrast IV
        "36857-1",  # MRA Head vessels WO and W contrast IV
        "36858-9",  # MRA Lower extremity vessels - left WO and W contrast IV
        "36859-7",  # MRA Lower extremity vessels - right WO and W contrast IV
        "36860-5",  # MRA Upper extremity vessels - left WO and W contrast IV
        "36861-3",  # MRA Upper extremity vessels - right WO and W contrast IV
        "36862-1",  # MRA Knee vessels - right WO and W contrast IV
        "36863-9",  # MRA Pelvis vessels WO and W contrast IV
        "36864-7",  # MRA Shoulder vessels - left WO and W contrast IV
        "36865-4",  # MRA Shoulder vessels - right WO and W contrast IV
        "36866-2",  # CT Temporal bone WO contrast
        "36867-0",  # CT Temporal bone - left WO contrast
        "36868-8",  # CT Temporal bone - right WO contrast
        "36869-6",  # MR Upper extremity joint - left WO contrast
        "36870-4",  # MR Upper extremity joint - right WO contrast
        "36871-2",  # MR Joint WO contrast
        "36872-0",  # MR Orbit WO contrast
        "36873-8",  # MR Orbit - left WO contrast
        "36874-6",  # MR Orbit - right WO contrast
        "36875-3",  # MR Ovary WO contrast
        "36876-1",  # MRA Head veins WO contrast
        "36877-9",  # MRA Neck veins WO contrast
        "36878-7",  # MRA Abdominal vessels WO contrast
        "36879-5",  # MRA Ankle vessels WO contrast
        "36881-1",  # MRA Head vessels WO contrast
        "36882-9",  # MRA Lower extremity vessels - left WO contrast
        "36883-7",  # MRA Pelvis vessels WO contrast
        "36886-0",  # XR Orbit Views
        "36887-8",  # XR Orbit - left Views
        "36890-2",  # XR Mastoid 5 Views
        "36893-6",  # XR Mastoid Limited Views
        "36894-4",  # XR Tibia and Fibula Oblique Views
        "36927-2",  # CT Guidance for biopsy of Maxillofacial region
        "36928-0",  # CT Guidance for stereotactic biopsy of Head
        "36929-8",  # CT Guidance for stereotactic biopsy of Head-- WO contrast
        "36930-6",  # CT Adrenal gland
        "36931-4",  # MR Adrenal gland
        "36932-2",  # CT Pituitary and Sella turcica
        "36933-0",  # MR Salivary gland
        "36934-8",  # CT Heart for calcium scoring
        "36935-5",  # CT Heart for calcium scoring W contrast IV
        "36936-3",  # MR Guidance for stereotactic biopsy of Brain
        "36937-1",  # CT Maxillofacial region limited
        "36938-9",  # CT Maxillofacial region limited WO contrast
        "36941-3",  # CT Salivary gland W contrast intra salivary duct
        "36942-1",  # MR Chest and Abdomen W contrast IV
        "36943-9",  # CT Adrenal gland W contrast IV
        "36944-7",  # MR Biliary ducts and Pancreatic duct WO and W contrast IV
        "36945-4",  # XR Knee - bilateral 2 Views W standing
        "36946-2",  # XR Lumbar spine 2 Views W standing
        "36947-0",  # XR Foot - bilateral 3 Views W standing
        "36948-8",  # XR Foot - left 3 Views W standing
        "36949-6",  # XR Lumbar spine 3 Views W standing
        "36950-4",  # CT Adrenal gland WO and W contrast IV
        "36951-2",  # MR Adrenal gland WO and W contrast IV
        "36952-0",  # CT Abdomen and Pelvis WO contrast
        "36953-8",  # CT Adrenal gland WO contrast
        "36954-6",  # MR Adrenal gland WO contrast
        "36955-3",  # CT Thyroid gland WO contrast
        "36956-1",  # MR Orbit and Face WO contrast
        "36958-7",  # XR Ribs - bilateral AP
        "36959-5",  # XR Ribs - left AP
        "36961-1",  # XR Shoulder - left AP and West Point and Outlet
        "36963-7",  # XR Shoulder - bilateral Axillary
        "36964-5",  # XR Shoulder - left Axillary
        "36965-2",  # XR Hand Ball Catcher
        "36966-0",  # XR Hand - bilateral Brewerton
        "36967-8",  # XR Hand - left Brewerton
        "36968-6",  # XR Wrist - bilateral Single view W clenched fist
        "36971-0",  # XR Wrist - left Lateral W extension
        "36972-8",  # XR Wrist - left Lateral W flexion
        "36973-6",  # XR Hip Friedman
        "36974-4",  # XR Shoulder - left Garth
        "36975-1",  # XR Calcaneus - bilateral Harris
        "36976-9",  # XR Foot Harris
        "36977-7",  # XR Calcaneus - left Harris
        "36978-5",  # XR Knee Holmblad
        "36979-3",  # XR Elbow Jones
        "36980-1",  # XR Elbow - left Jones
        "36981-9",  # XR Hip Judet
        "36982-7",  # XR Hip - bilateral Judet
        "36983-5",  # XR Hip - left Judet
        "36984-3",  # XR Abdomen Lateral crosstable
        "36985-0",  # XR Hip Lateral crosstable
        "36986-8",  # XR Hip - bilateral Lateral crosstable
        "36987-6",  # XR Hip - left Lateral crosstable
        "36988-4",  # XR Knee Lateral crosstable
        "36989-2",  # XR Cervical spine Lateral crosstable
        "36990-0",  # XR Lumbar spine Lateral crosstable
        "36993-4",  # XR Hip - bilateral Lateral frog
        "36994-2",  # XR Hip - left Lateral frog
        "36995-9",  # XR Abdomen Left lateral
        "36996-7",  # XR Abdomen Right lateral
        "36997-5",  # XR Cervical spine Lateral W extension
        "36998-3",  # XR Cervical spine Lateral W flexion
        "36999-1",  # XR Knee - bilateral Lateral W extension
        "37000-7",  # XR Knee - left Lateral W extension
        "37001-5",  # XR Foot Lateral W standing
        "37002-3",  # XR Knee - left Lateral W standing
        "37003-1",  # XR Lumbar spine Lateral W standing
        "37004-9",  # XR Knee Laurin
        "37007-2",  # XR Ankle Mortise
        "37008-0",  # XR Chest Left oblique
        "37009-8",  # XR Lumbar spine Left oblique
        "37010-6",  # XR Chest Right oblique
        "37011-4",  # XR Lumbar spine Right oblique
        "37012-2",  # XR Shoulder - bilateral Outlet
        "37013-0",  # XR Shoulder - left Outlet
        "37014-8",  # XR Knee - left PA W standing
        "37015-5",  # XR Abdomen PA prone
        "37018-9",  # XR Knee Rosenberg W standing
        "37019-7",  # XR Knee - left Rosenberg W standing
        "37020-5",  # XR Knee - bilateral Rosenberg W standing
        "37021-3",  # XR Calcaneus - bilateral Ski jump Views
        "37022-1",  # XR Calcaneus Ski jump Views
        "37023-9",  # XR Calcaneus - left Ski jump Views
        "37024-7",  # XR Shoulder - bilateral Stryker Notch
        "37025-4",  # XR Shoulder - left Stryker Notch
        "37026-2",  # XR Skull Submentovertex
        "37027-0",  # XR Knee - bilateral Sunrise
        "37031-2",  # XR Humerus Transthoracic
        "37032-0",  # XR Humerus - bilateral Transthoracic
        "37033-8",  # XR Humerus - left Transthoracic
        "37034-6",  # XR Shoulder - left Transthoracic
        "37035-3",  # XR Shoulder - bilateral Grashey
        "37039-5",  # XR Hip True lateral
        "37040-3",  # XR Hip - left True lateral
        "37041-1",  # XR Knee - bilateral Tunnel
        "37042-9",  # XR Knee - left Tunnel
        "37043-7",  # XR Knee - left Tunnel W standing
        "37044-5",  # XR Wrist - left Ulnar deviation
        "37045-2",  # XR Wrist - bilateral Ulnar deviation
        "37046-0",  # XR Abdomen Upright
        "37047-8",  # XR Shoulder - bilateral Velpeau axillary
        "37048-6",  # XR Shoulder - left Velpeau axillary
        "37049-4",  # XR Hip Von Rosen
        "37050-2",  # XR Shoulder - bilateral West Point
        "37051-0",  # XR Shoulder - left West Point
        "37054-4",  # XR Scapula - left Y
        "37055-1",  # XR Scapula - bilateral Y
        "37056-9",  # XR Acromioclavicular joint - bilateral Zanca
        "37057-7",  # XR Acromioclavicular joint - left Zanca
        "37058-5",  # XR Calcaneus - bilateral Single view W standing
        "37059-3",  # XR Hip - bilateral Single view W standing
        "37060-1",  # XR Fetal Views
        "37062-7",  # XR Humerus - bilateral Views
        "37063-5",  # RF Unspecified body region Views for foreign body
        "37064-3",  # XR Acetabulum - left 2 Views
        "37066-8",  # XR Ribs - left 2 Views
        "37067-6",  # XR Chest 2 Views W nipple markers
        "37068-4",  # XR Foot - bilateral 2 Views W standing
        "37069-2",  # XR Foot - left 2 Views W standing
        "37070-0",  # XR Wrist - bilateral 4 Views
        "37071-8",  # XR Wrist - left 4 Views
        "37072-6",  # XR Wrist - left 5 Views
        "37073-4",  # XR Lumbar spine 5 Views W standing
        "37074-2",  # XR Wrist - left 6 Views
        "37080-9",  # XR Shoulder - bilateral AP and Axillary
        "37081-7",  # XR Shoulder - bilateral AP and Axillary and Outlet
        "37082-5",  # XR Shoulder - left AP and Axillary and Outlet
        "37083-3",  # XR Shoulder - left AP and Axillary and Outlet and Zanca
        "37084-1",  # XR Shoulder - left AP and Axillary and Y
        "37085-8",  # XR Abdomen Supine and Lateral-decubitus
        "37086-6",  # XR Hip AP and Lateral crosstable
        "37087-4",  # XR Hip - left AP and Lateral crosstable
        "37088-2",  # XR Pelvis and Hip - left AP and Lateral crosstable
        "37089-0",  # XR Pelvis and Hip AP and Lateral crosstable
        "37090-8",  # XR Knee AP and Lateral crosstable
        "37091-6",  # XR Hip AP and Lateral frog
        "37092-4",  # XR Hip - bilateral AP and Lateral frog
        "37093-2",  # XR Hip - left AP and Lateral frog
        "37094-0",  # XR Pelvis and Hip - left AP and Lateral frog
        "37095-7",  # XR Ankle AP and Lateral and Mortise
        "37096-5",  # XR Ankle - bilateral AP and Lateral and Mortise
        "37097-3",  # XR Ankle - left AP and Lateral and Mortise
        "37098-1",  # XR Cervical spine AP and Oblique and (Lateral W flexion and W extension)
        "37099-9",  # XR Cervical spine AP and Lateral and Oblique and Odontoid
        "37100-5",  # XR Cervical spine AP and Oblique and Odontoid and (Lateral W flexion and W extension)
        "37101-3",  # XR Lumbar spine AP and Lateral and Oblique and Spot
        "37102-1",  # XR Knee - bilateral AP and Lateral and Oblique and Sunrise
        "37103-9",  # XR Cervical spine AP and Lateral and Odontoid
        "37104-7",  # XR Cervical spine AP and Odontoid and (Lateral W flexion and W extension)
        "37105-4",  # XR Lumbar spine AP and Lateral and Spot
        "37106-2",  # XR Knee AP and Lateral and Sunrise
        "37107-0",  # XR Knee - bilateral AP and Lateral and Sunrise
        "37108-8",  # XR Knee - left AP and Lateral and Sunrise
        "37109-6",  # XR Patella - bilateral AP and Lateral and Sunrise
        "37110-4",  # XR Patella - left AP and Lateral and Sunrise
        "37111-2",  # XR Knee AP and Lateral and Sunrise and tunnel
        "37112-0",  # XR Knee AP and Lateral and Tunnel
        "37113-8",  # XR Knee - bilateral AP and Lateral and Tunnel
        "37114-6",  # XR Knee - left AP and Lateral and Tunnel
        "37115-3",  # XR Knee AP and Lateral and Oblique and Tunnel
        "37116-1",  # XR Knee - bilateral AP and Lateral and Sunrise and tunnel
        "37117-9",  # XR Knee - left AP and Lateral and Sunrise and tunnel
        "37118-7",  # XR Knee - bilateral AP and Lateral and Oblique and Sunrise and Tunnel
        "37119-5",  # XR Abdomen AP and Oblique
        "37120-3",  # XR Cervical spine AP and Odontoid and Lateral crosstable
        "37121-1",  # XR Clavicle - left AP and Serendipity
        "37122-9",  # XR Shoulder - left AP and Stryker Notch
        "37123-7",  # XR Shoulder - left AP and West Point
        "37124-5",  # XR Scapula - left AP and Y
        "37125-2",  # XR Shoulder - left AP and Y
        "37126-0",  # XR Shoulder - bilateral AP and Axillary and Y
        "37127-8",  # XR Shoulder - bilateral Axillary and Y
        "37128-6",  # XR Shoulder - left Axillary and Y
        "37131-0",  # XR Abdomen Right lateral and Left lateral
        "37132-8",  # XR Lumbar spine Lateral Views W flexion and W extension
        "37133-6",  # XR Cervical spine Lateral Views W flexion and W extension
        "37134-4",  # XR Ankle - bilateral Lateral and Mortise
        "37135-1",  # XR Ankle - left Lateral and Mortise
        "37136-9",  # XR Shoulder - left Lateral and Y
        "37137-7",  # XR Kidney Limited Views W contrast IV
        "37138-5",  # XR Abdomen Right oblique and Left oblique
        "37139-3",  # XR Cervical spine Oblique and (Lateral W flexion and W extension)
        "37140-1",  # XR Shoulder - left Outlet and Y
        "37141-9",  # XR Chest PA and Right lateral
        "37142-7",  # XR Hand - bilateral PA and Lateral and Ball Catcher
        "37143-5",  # XR Chest PA and Lateral and AP lateral-decubitus
        "37144-3",  # XR Chest PA and Lateral and AP left lateral-decubitus
        "37145-0",  # XR Chest PA and Lateral and AP right lateral-decubitus
        "37146-8",  # XR Chest PA and Lateral and Left oblique
        "37147-6",  # XR Chest PA and Lateral and Right oblique
        "37148-4",  # XR Mandible PA and Lateral and Oblique and Towne
        "37149-2",  # XR Patella - left PA and Lateral and Sunrise
        "37150-0",  # XR Chest PA and Right oblique and Left oblique
        "37152-6",  # XR Shoulder - bilateral Outlet and Y
        "37153-4",  # XR Mastoid Stenver and Arcelin
        "37154-2",  # XR Knee Oblique and Sunrise
        "37155-9",  # XR Knee Oblique and Sunrise and Tunnel
        "37156-7",  # XR Knee - left Sunrise and Tunnel
        "37157-5",  # XR Shoulder - left Grashey and Outlet
        "37158-3",  # XR Shoulder - left Grashey and Axillary and Outlet
        "37160-9",  # XR Shoulder - left Grashey and Axillary
        "37161-7",  # XR Shoulder - bilateral Grashey and Axillary and Outlet and Zanca
        "37162-5",  # XR Shoulder - left Grashey and Outlet and Serendipity
        "37163-3",  # XR Knee - bilateral Sunrise and Tunnel
        "37164-1",  # XR Facial bones Lateral and Caldwell and Waters
        "37165-8",  # XR Facial bones Lateral and Caldwell and Waters and Submentovertex
        "37166-6",  # XR Facial bones Lateral and Caldwell and Waters and Submentovertex and Towne
        "37167-4",  # XR Shoulder - left Grashey and West Point
        "37183-1",  # RF Ankle Arthrogram
        "37184-9",  # RF Ankle - bilateral Arthrogram
        "37185-6",  # RF Ankle - left Arthrogram
        "37186-4",  # RF Elbow Arthrogram
        "37187-2",  # RF Elbow - bilateral Arthrogram
        "37188-0",  # RF Elbow - left Arthrogram
        "37189-8",  # RF Sacroiliac joint - bilateral Arthrogram
        "37190-6",  # RF Sacroiliac joint - left Arthrogram
        "37191-4",  # RF Joint Arthrogram
        "37192-2",  # RF Cervical spine Views W contrast intradisc
        "37193-0",  # RF Lumbar spine Views W contrast intradisc
        "37198-9",  # XR Esophagus Views W contrast PO
        "37199-7",  # RF Chest Views W contrast PO
        "37200-3",  # XR Chest Views W contrast PO
        "37201-1",  # XR Ankle Views W standing
        "37202-9",  # XR Ankle - bilateral Views W standing
        "37203-7",  # XR Ankle - left Views W standing
        "37204-5",  # XR Lower extremity Views W standing
        "37205-2",  # XR Calcaneus Views W standing
        "37206-0",  # XR Calcaneus - left Views W standing
        "37207-8",  # XR Hip - left Single view W standing
        "37208-6",  # XR Lumbar spine Views W standing
        "37209-4",  # XR Toes - left Views W standing
        "37210-2",  # CT Guidance for aspiration of cyst of Abdomen
        "37211-0",  # CT Guidance for biopsy of Bone marrow
        "37212-8",  # CT Guidance for biopsy of Epididymis
        "37213-6",  # CT Guidance for biopsy of Mediastinum
        "37214-4",  # CT Guidance for superficial biopsy of Tissue
        "37215-1",  # MR Brain and Larynx W contrast IV
        "37217-7",  # MR Brain stem and Cranial nerves
        "37218-5",  # MR Brain.temporal
        "37219-3",  # MR Biliary ducts
        "37220-1",  # MR Biliary ducts and Pancreatic duct
        "37221-9",  # CT Unspecified body region for fistula
        "37222-7",  # MR Ankle and Foot
        "37223-5",  # CT Parotid gland
        "37224-3",  # MR Parotid gland
        "37225-0",  # CT Sternoclavicular Joint
        "37226-8",  # CT Temporomandibular joint
        "37228-4",  # MR Temporomandibular joint - bilateral
        "37230-0",  # MR Temporomandibular joint - left
        "37231-8",  # MR Temporomandibular joint - right
        "37232-6",  # CT Spine lumbosacral junction
        "37234-2",  # MR Mediastinum
        "37235-9",  # MRA Circle of Willis
        "37237-5",  # CT Sinus tract W contrast intra sinus tract
        "37238-3",  # CT Lower Extremity Joint Arthrogram
        "37239-1",  # MR Brain and Internal auditory canal W contrast IV
        "37240-9",  # CT Parotid gland W contrast IV
        "37241-7",  # MR Parotid gland W contrast IV
        "37242-5",  # CT Sternoclavicular Joint W contrast IV
        "37243-3",  # CT Temporomandibular joint W contrast IV
        "37244-1",  # MR Temporomandibular joint W contrast IV
        "37245-8",  # MR Temporomandibular joint - bilateral W contrast IV
        "37246-6",  # CT Temporomandibular joint - left W contrast IV
        "37247-4",  # MR Temporomandibular joint - left W contrast IV
        "37248-2",  # CT Temporomandibular joint - right W contrast IV
        "37249-0",  # MR Temporomandibular joint - right W contrast IV
        "37253-2",  # MR Soft tissue W contrast IV
        "37254-0",  # MRA Circle of Willis W contrast IV
        "37256-5",  # XR Pelvis and Spine Lumbar 3 Views
        "37257-3",  # XR Spine Lumbar and Sacroiliac Joint 3 Views
        "37259-9",  # XR Spine Lumbar and Sacrum 3 Views
        "37260-7",  # XR Spine Lumbar and Sacrum and Coccyx 3 Views
        "37261-5",  # XR Lumbar spine and Sacrum and SI joint and Coccyx 3 Views
        "37265-6",  # MR Parotid gland WO and W contrast IV
        "37266-4",  # CT Sternoclavicular Joint WO and W contrast IV
        "37267-2",  # CT Temporomandibular joint WO and W contrast IV
        "37268-0",  # MR Temporomandibular joint WO and W contrast IV
        "37269-8",  # MR Temporomandibular joint - bilateral WO and W contrast IV
        "37270-6",  # MR Temporomandibular joint - left WO and W contrast IV
        "37271-4",  # MR Temporomandibular joint - right WO and W contrast IV
        "37272-2",  # MR Mediastinum WO and W contrast IV
        "37277-1",  # MRA Spinal veins WO and W contrast IV
        "37278-9",  # MR Brain and Internal auditory canal WO contrast
        "37279-7",  # MR Brain and Larynx WO contrast
        "37280-5",  # CT Parotid gland WO contrast
        "37281-3",  # MR Parotid gland WO contrast
        "37282-1",  # CT Sternoclavicular Joint WO contrast
        "37283-9",  # CT Temporomandibular joint WO contrast
        "37284-7",  # MR Temporomandibular joint WO contrast
        "37285-4",  # MR Temporomandibular joint - bilateral WO contrast
        "37286-2",  # MR Temporomandibular joint - left WO contrast
        "37287-0",  # MR Temporomandibular joint - right WO contrast
        "37288-8",  # CT Spine lumbosacral junction WO contrast
        "37293-8",  # MR Soft tissue WO contrast
        "37297-9",  # XR Abdomen and Fetal Single view for fetal age
        "37298-7",  # XR Sternoclavicular joint - bilateral Serendipity
        "37299-5",  # XR Sternoclavicular joint - left Serendipity
        "37300-1",  # XR Spine lumbosacral junction True AP
        "37302-7",  # XR Wrist - left Scaphoid Views
        "37303-5",  # XR Facial bones and Zygomatic arch Views
        "37304-3",  # XR Wrist - bilateral Scaphoid Views
        "37319-1",  # XR Humerus bicipital groove Views
        "37320-9",  # XR Humerus bicipital groove - left Views
        "37321-7",  # XR Humerus bicipital groove - bilateral Views
        "37323-3",  # XR Sternoclavicular joint - bilateral Views
        "37324-1",  # XR Sternoclavicular joint - left Views
        "37325-8",  # XR Temporomandibular joint - bilateral Views
        "37332-4",  # XR Olecranon - left Views
        "37338-1",  # XR Skull and Facial bones and Mandible Views
        "37340-7",  # XR Spine Lumbar and Sacrum Views
        "37341-5",  # XR Spine Lumbar and Sacrum and Coccyx Views
        "37342-3",  # XR Lumbar spine and Sacrum and SI joint and Coccyx Views
        "37348-0",  # XR Toes - bilateral 2 Views
        "37350-6",  # XR Temporomandibular joint - bilateral 5 Views
        "37351-4",  # XR Pelvis and Spine Lumbar 5 Views
        "37353-0",  # XR Spine Lumbar and Sacroiliac Joint 5 Views
        "37355-5",  # XR Spine Lumbar and Sacrum 5 Views
        "37356-3",  # XR Spine Lumbar and Sacrum and Coccyx 5 Views
        "37357-1",  # XR Lumbar spine and Sacrum and SI joint and Coccyx 5 Views
        "37361-3",  # XR Cervical and thoracic spine AP and Lateral
        "37362-1",  # XR Bones Bone age Views
        "37365-4",  # XR Bones Survey Views for metastasis
        "37409-0",  # RF Temporomandibular joint - bilateral Arthrogram
        "37410-8",  # RF Temporomandibular joint - left Arthrogram
        "37427-2",  # RF Guidance for injection of Spine
        "37428-0",  # CT Wrist
        "37430-6",  # CT Wrist - bilateral
        "37431-4",  # CT Wrist - left
        "37433-0",  # CT Wrist - right
        "37434-8",  # MR Heart cine for function
        "37435-5",  # MR Temporomandibular joint cine
        "37437-1",  # MR Breast dynamic W contrast IV
        "37439-7",  # CT Lung parenchyma
        "37440-5",  # CT Lung parenchyma W contrast IV
        "37441-3",  # CT Lung parenchyma WO contrast
        "37442-1",  # MR spectroscopy Brain
        "37443-9",  # MR spectroscopy Unspecified body region
        "37444-7",  # MR Wrist Arthrogram
        "37445-4",  # MR Wrist - left Arthrogram
        "37446-2",  # MR Wrist - right Arthrogram
        "37447-0",  # CT Wrist W contrast IV
        "37448-8",  # MR Wrist W contrast IV
        "37449-6",  # MR Wrist - bilateral W contrast IV
        "37450-4",  # CT Wrist - left W contrast IV
        "37451-2",  # MR Wrist - left W contrast IV
        "37452-0",  # CT Wrist - right W contrast IV
        "37453-8",  # MR Wrist - right W contrast IV
        "37454-6",  # XR Wrist - bilateral 3 Views
        "37455-3",  # XR Wrist - left 3 Views
        "37457-9",  # CT Wrist WO and W contrast IV
        "37458-7",  # CT Wrist - left WO and W contrast IV
        "37459-5",  # CT Wrist WO contrast
        "37460-3",  # MR Wrist WO contrast
        "37461-1",  # CT Wrist - bilateral WO contrast
        "37462-9",  # MR Wrist - bilateral WO contrast
        "37463-7",  # CT Wrist - left WO contrast
        "37464-5",  # MR Wrist - left WO contrast
        "37465-2",  # CT Wrist - right WO contrast
        "37466-0",  # MR Wrist - right WO contrast
        "37467-8",  # XR Acromioclavicular Joint 10 degree cephalic angle
        "37468-6",  # XR Shoulder - bilateral 30 degree caudal angle
        "37469-4",  # XR Clavicle - bilateral 45 degree cephalic angle
        "37470-2",  # XR Clavicle - left 45 degree cephalic angle
        "37471-0",  # XR Hand - bilateral Bora
        "37472-8",  # XR Hand - left Bora
        "37473-6",  # XR Shoulder - left Grashey
        "37474-4",  # XR Ankle - left Lateral Views W manual stress
        "37475-1",  # XR Ankle - left Mortise W manual stress
        "37476-9",  # XR Knee PA 45 degree flexion
        "37477-7",  # XR Knee PA 45 degree flexion W standing
        "37481-9",  # XR Cervical and thoracic spine Views
        "37482-7",  # XR Wrist - bilateral 2 Views
        "37483-5",  # XR Wrist - left 2 Views
        "37484-3",  # XR Knee - left Views AP W manual stress
        "37485-0",  # XR Humerus AP and Transthoracic
        "37486-8",  # XR Ankle Broden Views W manual stress
        "37491-8",  # CT Guidance for fluid aspiration of Pleural space
        "37492-6",  # CT Guidance for biopsy of Chest Pleura
        "37493-4",  # CT Guidance for injection of Cervical spine Intervertebral disc
        "37494-2",  # RF Guidance for injection of Tendon
        "37495-9",  # CT Skull base
        "37496-7",  # CT Cervical spine W contrast intradisc
        "37497-5",  # MRA Spine vessels
        "37500-6",  # MRA Spine vessels W contrast IV
        "37501-4",  # MRA Cervical spine vessels W contrast IV
        "37502-2",  # MRA Lumbar spine vessels W contrast IV
        "37503-0",  # MRA Thoracic spine vessels W contrast IV
        "37505-5",  # MRA Spine vessels WO and W contrast IV
        "37506-3",  # MRA Cervical spine vessels WO and W contrast IV
        "37507-1",  # MRA Lumbar spine vessels WO and W contrast IV
        "37508-9",  # MRA Thoracic spine vessels WO and W contrast IV
        "37509-7",  # CT Lumbar spine W contrast intradisc
        "37510-5",  # MRA Spine vessels WO contrast
        "37511-3",  # MRA Cervical spine vessels WO contrast
        "37512-1",  # MRA Thoracic spine vessels WO contrast
        "37513-9",  # XR Tibia - bilateral 10 degree caudal angle
        "37514-7",  # XR Tibia - left 10 degree caudal angle
        "37515-4",  # XR Spine lumbosacral junction Lateral spot
        "37516-2",  # XR Spine lumbosacral junction Lateral spot W standing
        "37517-0",  # XR Finger fifth - bilateral Views
        "37518-8",  # XR Finger fifth - left Views
        "37519-6",  # XR Finger fourth - bilateral Views
        "37520-4",  # XR Finger fourth - left Views
        "37521-2",  # XR Finger second - bilateral Views
        "37522-0",  # XR Finger second - left Views
        "37523-8",  # XR Finger third - bilateral Views
        "37524-6",  # XR Finger third - left Views
        "37530-3",  # XR Toe fifth - left Views
        "37531-1",  # XR Toe fourth - left Views
        "37532-9",  # XR Great toe - bilateral Views
        "37533-7",  # XR Great toe - left Views
        "37534-5",  # XR Toe second - left Views
        "37535-2",  # XR Toe third - left Views
        "37538-6",  # XR Shoulder - left Grashey and Axillary and Y
        "37540-2",  # XR Knee - bilateral Holmblad Views W standing
        "37541-0",  # XR Mastoid - bilateral Law and Mayer and Stenver and Towne
        "37544-4",  # XR Wrist - bilateral Oblique Views
        "37545-1",  # XR Hip - left Oblique crosstable
        "37546-9",  # XR Temporomandibular joint - bilateral Open and Closed mouth
        "37547-7",  # XR Wrist - bilateral PA and Lateral
        "37548-5",  # XR Wrist - left PA and Lateral
        "37549-3",  # XR Wrist - bilateral PA and Lateral and Oblique
        "37550-1",  # XR Wrist - left PA and Lateral and Oblique
        "37555-0",  # XR Wrist - left Ulnar deviation and Radial deviation
        "37556-8",  # XR Ankle Views W manual stress
        "37557-6",  # XR Ankle - bilateral Views W manual stress
        "37558-4",  # XR Ankle - left Views W manual stress
        "37559-2",  # XR Foot - left Views W manual stress
        "37560-0",  # XR Knee Views W manual stress
        "37561-8",  # XR Knee - bilateral Views W manual stress
        "37562-6",  # XR Knee - left Views W manual stress
        "37563-4",  # XR Thumb - bilateral Views W manual stress
        "37564-2",  # XR Thumb - left Views W manual stress
        "37565-9",  # RF Unspecified body region Views W barium contrast via fistula
        "37566-7",  # RF Unspecified body region Views W contrast via catheter
        "37567-5",  # RF Colon Views W contrast via colostomy
        "37568-3",  # RF Unspecified body region Views W contrast via fistula
        "37569-1",  # RF Urinary bladder Views W contrast via suprapubic tube
        "37570-9",  # RF Wrist - bilateral Arthrogram
        "37571-7",  # RF Wrist - left Arthrogram
        "37572-5",  # RF Spine Views W contrast IT
        "37575-8",  # XR Gallbladder Views W contrast and fatty meal PO
        "37576-6",  # RF Unspecified body region Views W gastrografin via fistula
        "37577-4",  # XR Acromioclavicular Joint Views W weight
        "37578-2",  # XR Acromioclavicular joint - bilateral Views W weight
        "37579-0",  # XR Acromioclavicular Joint Views WO and W weight
        "37580-8",  # XR Acromioclavicular joint - bilateral Views WO and W weight
        "37581-6",  # XR Acromioclavicular joint - left Views WO and W weight
        "37582-4",  # XR Acromioclavicular Joint Views WO weight
        "37583-2",  # XR Pelvis and Hip - bilateral Views and Lateral frog
        "37584-0",  # XR Great toe - left Views W standing
        "37585-7",  # RF Jejunum Views W contrast
        "37586-5",  # RF Penis Views W contrast intra corpus cavernosum
        "37604-6",  # XR Nasal bones 3 Views
        "37605-3",  # XR Nasal bones Lateral and Waters
        "37607-9",  # XR Kidney Views W contrast IV
        "37609-5",  # XR Optic foramen 4 Views
        "37612-9",  # XR Orbit - bilateral 4 Views
        "37613-7",  # XR Orbit - bilateral Waters
        "37614-5",  # XR Patella Single view
        "37616-0",  # XR Pelvis Single view
        "37617-8",  # XR Pelvis 2 Views
        "37618-6",  # XR Pelvis AP and Inlet
        "37619-4",  # XR Pelvis AP and Judet
        "37620-2",  # XR Pelvis AP and Lateral
        "37621-0",  # XR Pelvis AP and Oblique
        "37622-8",  # XR Pelvis AP
        "37623-6",  # XR Pelvis AP and Inlet and Outlet
        "37624-4",  # XR Pelvis AP and Lateral and oblique
        "37625-1",  # XR Pelvis Ferguson
        "37626-9",  # XR Pelvis Lateral frog
        "37627-7",  # XR Pelvis Inlet and Outlet and Oblique
        "37628-5",  # XR Pelvis Inlet
        "37629-3",  # XR Pelvis Lateral
        "37630-1",  # XR Pelvis Oblique Views
        "37631-9",  # XR Pelvis Outlet
        "37633-5",  # XR Pelvis Single view W standing
        "37634-3",  # XR Pelvis AP 20 degree cephalic angle
        "37635-0",  # XR Acetabulum 3 Views
        "37636-8",  # XR Abdomen Views
        "37637-6",  # XR Extremity Views
        "37639-2",  # XR Neck Views
        "37641-8",  # RF Wrist - right Arthrogram
        "37642-6",  # XR Wrist - right Limited Views
        "37643-4",  # XR Wrist - right Oblique Views
        "37645-9",  # XR Wrist - right Ulnar deviation
        "37646-7",  # XR Sacroiliac Joint Limited Views
        "37647-5",  # RF Sacroiliac Joint Arthrogram
        "37648-3",  # XR Sacroiliac Joint 3 Views
        "37649-1",  # XR Sacroiliac Joint AP and Oblique
        "37650-9",  # XR Sacroiliac Joint Ferguson
        "37651-7",  # XR Sacrum 2 Views
        "37652-5",  # XR Sacrum AP and Lateral
        "37654-1",  # XR Scapula Single view
        "37655-8",  # XR Scapula 2 Views
        "37656-6",  # XR Scapula Y
        "37658-2",  # XR Thoracic and lumbar spine 2 Views for scoliosis
        "37659-0",  # XR Thoracic and lumbar spine AP for scoliosis W standing
        "37660-8",  # XR Thoracic and lumbar spine Lateral for scoliosis W standing
        "37661-6",  # XR Acromioclavicular joint - right 2 Views
        "37662-4",  # XR Acromioclavicular joint - right AP
        "37663-2",  # XR Acromioclavicular joint - right Views WO and W weight
        "37664-0",  # XR Acetabulum - right 2 Views
        "37665-7",  # XR Ankle - right 3 Views
        "37666-5",  # XR Ankle - right AP and Lateral and Mortise
        "37667-3",  # XR Ankle - right AP and Lateral
        "37668-1",  # XR Ankle - right AP and Lateral and oblique
        "37669-9",  # XR Ankle - right Lateral Views W manual stress
        "37670-7",  # XR Ankle - right Lateral and Mortise
        "37671-5",  # XR Ankle - right Mortise W manual stress
        "37672-3",  # XR Ankle - right 2 Views W manual stress
        "37673-1",  # XR Ankle - right Views W manual stress
        "37675-6",  # XR Ankle - right 2 Views W standing
        "37676-4",  # XR Ankle - right Views W standing
        "37677-2",  # XR Wrist - right Carpal tunnel
        "37678-0",  # XR Wrist - right 2 Carpal tunnel Views
        "37679-8",  # XR Clavicle - right 2 Views
        "37680-6",  # XR Clavicle - right AP and Serendipity
        "37681-4",  # XR Elbow - right 2 Views
        "37682-2",  # XR Elbow - right 3 Views
        "37683-0",  # XR Elbow - right 4 Views
        "37684-8",  # XR Elbow - right AP and Lateral
        "37685-5",  # XR Elbow - right AP and Lateral and oblique
        "37686-3",  # XR Elbow - right 2 Oblique Views
        "37687-1",  # XR Elbow - right Oblique Views
        "37689-7",  # XR Femur - right Single view
        "37690-5",  # XR Femur - right 2 Views
        "37691-3",  # XR Femur - right 4 Views
        "37692-1",  # XR Femur - right AP and Lateral
        "37693-9",  # XR Femur - right Views W standing
        "37694-7",  # XR Finger - right 2 Views
        "37695-4",  # XR Finger - right 3 Views
        "37696-2",  # XR Finger - right AP and Lateral and oblique
        "37697-0",  # XR Foot - right 2 Views
        "37698-8",  # XR Foot - right 2 Views W standing
        "37699-6",  # XR Foot - right 3 Views
        "37700-2",  # XR Foot - right 3 Views W standing
        "37701-0",  # XR Foot - right AP and Lateral
        "37702-8",  # XR Foot - right AP and Lateral and oblique
        "37703-6",  # XR Foot - right Lateral
        "37704-4",  # XR Foot - right Oblique
        "37705-1",  # XR Foot - right Views W manual stress
        "37707-7",  # XR Radius and Ulna - right 2 Views
        "37708-5",  # XR Radius and Ulna - right AP and Lateral
        "37709-3",  # XR Radius and Ulna - right Oblique Views
        "37710-1",  # XR Hand - right AP and Lateral
        "37711-9",  # XR Hand - right AP and Lateral and oblique
        "37712-7",  # XR Hand - right Lateral
        "37713-5",  # XR Hand - right PA and Lateral
        "37714-3",  # XR Hand - right PA
        "37715-0",  # XR Hand - right PA and Lateral and Oblique
        "37716-8",  # XR Hand - right Views
        "37718-4",  # XR Calcaneus - right 2 Views
        "37719-2",  # XR Calcaneus - right AP and Lateral
        "37720-0",  # XR Calcaneus - right Views W standing
        "37721-8",  # XR Hip - right 2 Views
        "37722-6",  # XR Hip - right 3 Views
        "37723-4",  # XR Hip - right AP and Lateral crosstable
        "37724-2",  # XR Hip - right AP and Lateral frog
        "37725-9",  # XR Hip - right AP and Lateral
        "37726-7",  # XR Hip - right AP
        "37727-5",  # XR Hip - right Lateral crosstable
        "37728-3",  # XR Hip - right Oblique crosstable
        "37729-1",  # XR Hip - right Lateral frog
        "37730-9",  # XR Hip - right Lateral
        "37731-7",  # XR Hip - right Single view W standing
        "37732-5",  # XR Hip - right Judet
        "37733-3",  # XR Lower extremity - right AP W standing
        "37734-1",  # XR Lower extremity - right Single view W standing
        "37736-6",  # XR Humerus - right AP and Lateral
        "37737-4",  # XR Humerus - right Oblique Views
        "37738-2",  # XR Humerus - right Views
        "37740-8",  # XR Knee - right AP and Lateral and Sunrise and tunnel
        "37741-6",  # XR Knee - right Single view
        "37742-4",  # XR Knee - right 3 Views
        "37743-2",  # XR Knee - right 4 Views
        "37744-0",  # XR Knee - right 5 Views
        "37745-7",  # XR Knee - right AP and Lateral
        "37746-5",  # XR Knee - right Views AP W manual stress
        "37747-3",  # XR Knee - right AP and Lateral and Tunnel
        "37748-1",  # XR Knee - right AP and Lateral and oblique
        "37749-9",  # XR Knee - right AP and Lateral and Sunrise
        "37750-7",  # XR Knee - right Lateral W extension
        "37751-5",  # XR Knee - right Lateral
        "37752-3",  # XR Knee - right Rosenberg W standing
        "37753-1",  # XR Knee - right Views W manual stress
        "37754-9",  # XR Knee - right Lateral W standing
        "37755-6",  # XR Knee - right PA W standing
        "37756-4",  # XR Knee - right Tunnel W standing
        "37757-2",  # XR Knee - right Oblique Views
        "37758-0",  # XR Knee - right Views
        "37759-8",  # XR Knee - right Sunrise and Tunnel
        "37761-4",  # XR Knee - right Tunnel
        "37762-2",  # XR Knee - right 2 Views W standing
        "37763-0",  # XR Knee - right 4 Views W standing
        "37764-8",  # XR Lower extremity - right Single view
        "37776-2",  # XR Patella - right AP and Lateral
        "37777-0",  # XR Patella - right Views
        "37780-4",  # XR Ribs - right 2 Views
        "37781-2",  # XR Ribs - right 3 Views
        "37782-0",  # XR Ribs - right Anterior and Lateral
        "37783-8",  # XR Ribs - right AP
        "37784-6",  # XR Ribs - right Lateral
        "37785-3",  # RF Sacroiliac joint - right Arthrogram
        "37786-1",  # XR Sacroiliac joint - right Views
        "37787-9",  # XR Scapula - right 2 Views
        "37788-7",  # XR Scapula - right AP and Lateral
        "37789-5",  # XR Scapula - right AP and Y
        "37790-3",  # XR Scapula - right Y
        "37791-1",  # XR Shoulder - right Stryker Notch
        "37792-9",  # XR Shoulder - right Single view
        "37793-7",  # XR Shoulder - right 2 Views
        "37794-5",  # XR Shoulder - right 4 Views
        "37795-2",  # XR Shoulder - right 5 Views
        "37796-0",  # XR Shoulder - right 6 Views
        "37797-8",  # XR Shoulder - right AP and Stryker Notch
        "37798-6",  # XR Shoulder - right AP
        "37799-4",  # XR Shoulder - right AP and West Point and Outlet
        "37800-0",  # XR Shoulder - right Axillary
        "37801-8",  # XR Shoulder - right Garth
        "37802-6",  # XR Shoulder - right Outlet
        "37803-4",  # XR Shoulder - right Lateral and Y
        "37804-2",  # XR Shoulder - right Outlet and Y
        "37805-9",  # XR Shoulder - right Y
        "37806-7",  # XR Shoulder - right Grashey and Axillary and Outlet
        "37807-5",  # XR Shoulder - right Axillary and Y
        "37808-3",  # XR Sternoclavicular joint - right Serendipity
        "37809-1",  # XR Shoulder - right West Point
        "37810-9",  # XR Acromioclavicular joint - right Zanca
        "37812-5",  # XR Thumb - right 3 Views
        "37813-3",  # XR Thumb - right AP and Lateral and oblique
        "37814-1",  # XR Thumb - right Views W manual stress
        "37815-8",  # XR Tibia and Fibula - right 2 Views
        "37816-6",  # XR Tibia and Fibula - right AP and Lateral
        "37817-4",  # XR Tibia and Fibula - right Oblique Views
        "37818-2",  # RF Temporomandibular joint - right Arthrogram
        "37820-8",  # XR Toes - right 3 Views
        "37821-6",  # XR Toes - right 2 Views
        "37822-4",  # XR Toes - right AP and Lateral
        "37823-2",  # XR Toes - right Views W standing
        "37825-7",  # XR Wrist - right Single view
        "37826-5",  # XR Wrist - right 2 Views
        "37827-3",  # XR Wrist - right 3 Views
        "37828-1",  # XR Wrist - right 4 Views
        "37829-9",  # XR Wrist - right 5 Views
        "37830-7",  # XR Wrist - right 6 Views
        "37831-5",  # XR Wrist - right 8 Views
        "37832-3",  # XR Wrist - right AP and Lateral
        "37833-1",  # XR Wrist - right Lateral W extension
        "37834-9",  # XR Wrist - right Lateral W flexion
        "37835-6",  # XR Wrist - right PA and Lateral
        "37836-4",  # XR Wrist - right PA and Lateral and Oblique
        "37839-8",  # XR Shoulder AP and Lateral and Axillary
        "37840-6",  # XR Shoulder 2 Views
        "37841-4",  # XR Shoulder AP and Lateral
        "37842-2",  # XR Shoulder AP
        "37843-0",  # XR Shoulder Garth
        "37844-8",  # XR Shoulder Grashey
        "37845-5",  # XR Shoulder Outlet
        "37846-3",  # XR Sternoclavicular Joint Serendipity
        "37847-1",  # XR Shoulder Y
        "37848-9",  # XR Acromioclavicular Joint Zanca
        "37849-7",  # XR Shoulder Axillary
        "37851-3",  # XR Sinuses Single view
        "37852-1",  # XR Sinuses Caldwell and Waters
        "37853-9",  # XR Sinuses 2 Views
        "37854-7",  # XR Sinuses 3 Views
        "37855-4",  # XR Sinuses 4 Views
        "37856-2",  # XR Sinuses 5 Views
        "37857-0",  # XR Sinuses Caldwell
        "37858-8",  # XR Sinuses Lateral
        "37859-6",  # XR Sinuses PA and Lateral and Waters
        "37860-4",  # XR Sinuses PA and Lateral and Caldwell and Waters
        "37861-2",  # XR Sinuses Submentovertex
        "37862-0",  # XR Sinuses Lateral and Waters
        "37863-8",  # XR Sinuses Waters
        "37864-6",  # XR Sinuses Lateral and Caldwell and Waters
        "37867-9",  # XR Skull 2 Views
        "37868-7",  # XR Skull 4 Views
        "37869-5",  # XR Skull Lateral and Towne
        "37870-3",  # XR Skull Towne
        "37871-1",  # XR Skull Lateral and Caldwell and Waters and Towne
        "37872-9",  # XR Skull Lateral crosstable
        "37875-2",  # XR Spine Single view
        "37876-0",  # XR Spine 4 Views
        "37877-8",  # XR Spine AP
        "37878-6",  # XR Spine Lateral crosstable
        "37879-4",  # XR Spine 2 Views
        "37880-2",  # XR Sternoclavicular Joint AP
        "37881-0",  # XR Sternoclavicular Joint 3 Views
        "37882-8",  # XR Sternoclavicular Joint 4 Views
        "37883-6",  # XR Sternum 2 Views
        "37884-4",  # XR Sternum PA and Lateral and Oblique
        "37887-7",  # RF Guidance for fluid aspiration of Pleural space
        "37888-5",  # XR Thumb 3 Views
        "37889-3",  # XR Thumb AP and Lateral
        "37890-1",  # XR Thumb AP
        "37891-9",  # XR Thumb Lateral
        "37892-7",  # XR Thumb Oblique
        "37893-5",  # XR Tibia and Fibula Lateral
        "37894-3",  # XR Tibia and Fibula Single view
        "37895-0",  # XR Tibia and Fibula 2 Views
        "37896-8",  # XR Tibia and Fibula AP and Lateral
        "37897-6",  # XR Tibia and Fibula AP
        "37899-2",  # XR Tibia and Fibula Views W standing
        "37901-6",  # RF Temporomandibular joint Arthrogram
        "37902-4",  # XR Toes 2 Views
        "37903-2",  # XR Thoracic spine Lateral crosstable
        "37904-0",  # XR Thoracic spine Single view
        "37905-7",  # XR Thoracic spine 2 Views
        "37906-5",  # XR Thoracic spine 3 Views
        "37907-3",  # XR Thoracic spine 4 Views
        "37908-1",  # XR Thoracic spine AP and Lateral and oblique
        "37909-9",  # XR Thoracic spine Lateral W hyperextension
        "37910-7",  # XR Thoracic spine Lateral W standing
        "37922-2",  # XR Upper extremity 2 Views
        "37924-8",  # XR Wrist Single view
        "37925-5",  # XR Wrist 2 Views
        "37926-3",  # XR Wrist 3 Views
        "37927-1",  # XR Wrist AP and Lateral and oblique
        "37928-9",  # XR Wrist Brewerton
        "37929-7",  # XR Wrist Lateral Views W flexion and W extension
        "37930-5",  # XR Wrist Lateral
        "37931-3",  # XR Wrist PA
        "37933-9",  # XR Zygomatic arch 3 Views
        "37934-7",  # XR Zygomatic arch 4 Views
        "37937-0",  # XR Ribs anterior Views
        "37938-8",  # XR Ribs posterior Views
        "37942-0",  # RF Ankle - right Arthrogram
        "37947-9",  # RF Elbow - right Arthrogram
        "37960-2",  # XR Ribs lower - right Views
        "37961-0",  # XR Ribs upper - right Views
        "37962-8",  # XR Ribs anterior and posterior - right Views
        "37963-6",  # XR Ribs anterior - right Views
        "37964-4",  # XR Ribs posterior - right Views
        "37965-1",  # XR Sternoclavicular joint - right Views
        "37973-5",  # RF Testicular vessels Views W contrast
        "37974-3",  # XR Spine thoracolumbar junction AP and Lateral
        "37975-0",  # XR Spine thoracolumbar junction Views
        "37994-1",  # MRA Lumbar spine vessels WO contrast
        "37995-8",  # XR Calcaneus - bilateral Broden Views
        "37996-6",  # XR Calcaneus Broden Views
        "37997-4",  # XR Calcaneus - left Broden Views
        "37998-2",  # XR Elbow Radial head capitellar
        "37999-0",  # XR Elbow - bilateral Radial head capitellar
        "38000-6",  # XR Elbow - left Radial head capitellar
        "38001-4",  # XR Chest Single view W expiration
        "38002-2",  # XR Chest Single view W inspiration
        "38003-0",  # XR Foot - left Views AP W standing
        "38004-8",  # XR Shoulder - left Grashey Views WO and W weight
        "38006-3",  # XR Elbow - right Radial head capitellar
        "38007-1",  # XR Humerus - right Transthoracic
        "38008-9",  # XR Cervical and thoracic and lumbar spine Views
        "38009-7",  # XR Thoracic spine AP and Lateral and Swimmers
        "38010-5",  # XR Thoracic spine Lateral Views W flexion and W extension
        "38057-6",  # MR Breast - left for implant
        "38058-4",  # MR Breast - right for implant
        "38061-8",  # MR Spine Cervical and Spine Thoracic and Spine Lumbar and Sacrum W contrast IV
        "38062-6",  # MR Breast - right for implant WO and W contrast IV
        "38064-2",  # MR Breast - left for implant WO contrast
        "38065-9",  # XR Hip - left Single view during surgery
        "38066-7",  # XR Hip - left Lateral during surgery
        "38068-3",  # XR Chest Right anterior oblique
        "38069-1",  # XR Abdomen Left posterior oblique
        "38073-3",  # XR Ribs anterior - bilateral Views
        "38074-1",  # XR Ribs anterior - left Views
        "38082-4",  # XR Shoulder - left AP and Transthoracic
        "38083-2",  # XR Cervical spine AP and Lateral and Oblique and Odontoid and Swimmers
        "38084-0",  # XR Abdomen AP and Left posterior oblique
        "38086-5",  # XR Knee Merchants 30 and 45 and 60 degrees
        "38087-3",  # XR Knee - left Sunrise 20 and 40 and 60 degrees
        "38088-1",  # XR Knee - bilateral Sunrise 20 and 40 and 60 degrees
        "38089-9",  # XR Bones Limited Survey Views for metastasis
        "38092-3",  # RF Urinary bladder Views W chain and contrast intra bladder
        "38093-1",  # XR Chest Views W nipple markers
        "38094-9",  # RF Spinal cavity Views W contrast
        "38097-2",  # RF Parotid gland - left Views W contrast intra salivary duct
        "38098-0",  # RF Lacrimal duct - bilateral Views W contrast intra lacrimal duct
        "38099-8",  # RF Lacrimal duct - left Views W contrast intra lacrimal duct
        "38100-4",  # RF Urinary bladder and Urethra Views W contrast antegrade
        "38101-2",  # XR Kidney Views W contrast antegrade
        "38102-0",  # XR Kidney Views W contrast antegrade via pyelostomy
        "38103-8",  # RF Spine Cervical and Spine Lumbar Views W contrast IT
        "38104-6",  # RF Spine epidural space Views W contrast IT
        "38105-3",  # XR Kidney Views W contrast retrograde
        "38107-9",  # XR Wrist Scaphoid Views
        "38108-7",  # XR Knee - right 2 Oblique Views
        "38112-9",  # RF Kidney - right Views W contrast via nephrostomy tube
        "38114-5",  # XR Tibia and Fibula - right 2 Oblique Views
        "38115-2",  # XR Wrist - right Scaphoid Views
        "38116-0",  # RF Parotid gland Views W contrast intra salivary duct
        "38117-8",  # XR Sinuses Waters upright
        "38118-6",  # XR Neck 2 Lateral Views
        "38120-2",  # RF Thoracic spine Limited Views W contrast IT
        "38121-0",  # XR Thoracic and lumbar spine Single view
        "38123-6",  # XR Thoracic and lumbar spine AP and Lateral
        "38124-4",  # XR Thoracic and lumbar spine Views W standing
        "38125-1",  # RF Cervical and thoracic and lumbar spine Limited Views W contrast IT
        "38144-2",  # XR Finger second - right Views
        "38145-9",  # XR Finger third - right Views
        "38146-7",  # XR Finger fourth - right Views
        "38147-5",  # XR Finger fifth - right Views
        "38148-3",  # XR Toe second - right Views
        "38149-1",  # XR Toe third - right Views
        "38150-9",  # XR Toe fourth - right Views
        "38151-7",  # XR Toe fifth - right Views
        "38152-5",  # XR Great toe - right Views
        "38153-3",  # RF Submandibular gland Views W contrast intra salivary duct
        "38154-1",  # RF Guidance for superficial biopsy of Bone
        "38155-8",  # XR Wrist 4 Views
        "38156-6",  # XR Wrist 6 Views
        "38181-4",  # XR Chest Diameter.lateral
        "38767-0",  # CT Internal auditory canal - right
        "38769-6",  # MR Lower extremity joint - right limited WO contrast
        "38770-4",  # MR Scapula - right WO contrast
        "38771-2",  # XR Pelvis and Hip - right Views
        "38772-0",  # XR Hip - right True lateral
        "38773-8",  # MRA Lower extremity vessels - right WO contrast
        "38774-6",  # XR Orbit - right Views
        "38775-3",  # XR Hand - right Brewerton
        "38776-1",  # XR Calcaneus - right Harris
        "38777-9",  # XR Elbow - right Jones
        "38778-7",  # XR Calcaneus - right Ski jump Views
        "38779-5",  # XR Shoulder - right Transthoracic
        "38780-3",  # XR Shoulder - right Velpeau axillary
        "38781-1",  # XR Shoulder - right AP and Axillary and Outlet
        "38782-9",  # XR Shoulder - right AP and Axillary and Outlet and Zanca
        "38783-7",  # XR Shoulder - right AP and Axillary and Y
        "38784-5",  # XR Pelvis and Hip - right AP and Lateral crosstable
        "38785-2",  # XR Pelvis and Hip - right AP and Lateral frog
        "38786-0",  # XR Patella - right AP and Lateral and Sunrise
        "38787-8",  # XR Shoulder - right AP and West Point
        "38788-6",  # XR Shoulder - right AP and Y
        "38789-4",  # XR Shoulder - right Grashey and Axillary and Y
        "38790-2",  # XR Patella - right PA and Lateral and Sunrise
        "38791-0",  # XR Shoulder - right Grashey and Outlet
        "38793-6",  # XR Shoulder - right Grashey and Axillary
        "38794-4",  # XR Shoulder - right Grashey and Outlet and Serendipity
        "38795-1",  # XR Shoulder - right Grashey and West Point
        "38797-7",  # XR Humerus bicipital groove - right Views
        "38798-5",  # XR Olecranon - right Views
        "38802-5",  # CT Wrist - right WO and W contrast IV
        "38803-3",  # XR Clavicle - right 45 degree cephalic angle
        "38804-1",  # XR Hand - right Bora
        "38805-8",  # XR Shoulder - right Grashey
        "38806-6",  # XR Tibia - right 10 degree caudal angle
        "38808-2",  # XR Wrist - right Ulnar deviation and Radial deviation
        "38810-8",  # XR Great toe - right Views W standing
        "38814-0",  # XR Calcaneus - right Broden Views
        "38815-7",  # XR Foot - right Views AP W standing
        "38816-5",  # XR Shoulder - right Grashey Views WO and W weight
        "38817-3",  # MR Breast - right for implant WO contrast
        "38818-1",  # XR Hip - right Single view during surgery
        "38819-9",  # XR Hip - right Lateral during surgery
        "38822-3",  # XR Shoulder - right AP and Transthoracic
        "38824-9",  # XR Knee - right Sunrise 20 and 40 and 60 degrees
        "38826-4",  # RF Parotid gland - right Views W contrast intra salivary duct
        "38827-2",  # RF Lacrimal duct - right Views W contrast intra lacrimal duct
        "38828-0",  # CT Shoulder - left Arthrogram
        "38829-8",  # MR Upper extremity - left W contrast IV
        "38830-6",  # MR Shoulder - left W contrast IV
        "38831-4",  # MR Upper extremity - left WO and W contrast IV
        "38832-2",  # MR Upper extremity - left WO contrast
        "38833-0",  # MR Brachial plexus - left WO contrast
        "38834-8",  # MR Shoulder - left WO contrast
        "38835-5",  # CT Temporal bone - left W contrast IV
        "38836-3",  # MR Orbit - left
        "38837-1",  # MRA Knee vessels - left WO and W contrast IV
        "38838-9",  # XR Wrist - left Limited Views
        "38839-7",  # XR Wrist - left Oblique Views
        "38840-5",  # XR Ankle - left 2 Views W manual stress
        "38841-3",  # XR Ankle - left 2 Views W standing
        "38842-1",  # XR Wrist - left Carpal tunnel
        "38843-9",  # XR Wrist - left 2 Carpal tunnel Views
        "38844-7",  # XR Elbow - left 2 Oblique Views
        "38845-4",  # XR Femur - left Views W standing
        "38846-2",  # XR Foot - left 2 Views
        "38847-0",  # XR Hand - left AP and Lateral
        "38848-8",  # XR Hand - left AP and Lateral and oblique
        "38849-6",  # XR Lower extremity - left AP W standing
        "38850-4",  # XR Lower extremity - left Single view W standing
        "38851-2",  # XR Knee - left 2 Views W standing
        "38852-0",  # XR Knee - left 4 Views W standing
        "38856-1",  # XR Ribs - left Anterior and Lateral
        "38857-9",  # XR Ribs - left Lateral
        "38858-7",  # XR Shoulder - left Y
        "38860-3",  # XR Wrist - left AP and Lateral
        "38866-0",  # XR Ribs lower - left Views
        "38867-8",  # XR Ribs upper - left Views
        "38868-6",  # XR Ribs anterior and posterior - left Views
        "38869-4",  # XR Ribs posterior - left Views
        "38870-2",  # MR Breast - left for implant WO and W contrast IV
        "38871-0",  # XR Knee - left 2 Oblique Views
        "38872-8",  # RF Kidney - left Views W contrast via nephrostomy tube
        "38874-4",  # XR Tibia and Fibula - left 2 Oblique Views
        "39026-0",  # CT Guidance for needle localization of Unspecified body region
        "39027-8",  # RF Guidance for needle localization of Unspecified body region
        "39028-6",  # MR Guidance for needle localization of Unspecified body region
        "39029-4",  # MR Orbit and Face WO and W contrast IV
        "39033-6",  # MR Upper extremity WO contrast
        "39034-4",  # MR Upper extremity WO and W contrast IV
        "39037-7",  # MR Upper extremity W contrast IV
        "39038-5",  # MR Orbit and Face W contrast IV
        "39046-8",  # CT Pelvis limited for pelvimetry WO contrast
        "39047-6",  # RF Hip Single view during surgery
        "39048-4",  # XR Scapula AP
        "39049-2",  # XR Thoracic and lumbar spine AP
        "39050-0",  # XR Ribs AP
        "39051-8",  # XR Chest Lateral
        "39052-6",  # XR Spine Lateral
        "39053-4",  # XR Ribs Lateral
        "39056-7",  # XR Unspecified body region Views W manual stress
        "39058-3",  # XR Salivary gland Views
        "39060-9",  # XR Ribs 2 Views
        "39061-7",  # XR Sacrum and Coccyx 3 Views
        "39062-5",  # XR Ribs 3 Views
        "39063-3",  # XR Lumbar spine 5 Views W flexion and W extension
        "39064-1",  # XR Ribs Anterior and Lateral
        "39065-8",  # XR Pelvis AP and Inlet and Outlet and Oblique
        "39067-4",  # XR Cervical and thoracic and lumbar spine AP and Lateral
        "39068-2",  # XR Foot AP and Lateral W standing
        "39069-0",  # XR Foot AP and Lateral
        "39070-8",  # XR Chest AP and Lateral and Apical lordotic
        "39071-6",  # XR Knee AP and Lateral and Merchants
        "39072-4",  # XR Ankle AP and Lateral and oblique
        "39073-2",  # XR Knee AP and Lateral and Right oblique and Left oblique
        "39074-0",  # XR Chest AP and Lateral and Right oblique and Left oblique
        "39075-7",  # XR Toes AP and Oblique
        "39076-5",  # XR Foot AP and Oblique
        "39077-3",  # XR Shoulder AP and Transthoracic
        "39078-1",  # XR Finger PA and Lateral and Oblique
        "39079-9",  # XR Hand PA and Oblique
        "39099-7",  # XR Ribs - bilateral 4 Views and Chest PA
        "39140-9",  # MR Heart cine for blood flow velocity mapping
        "39141-7",  # MR Bone marrow
        "39144-1",  # RF Gastrointestinal tract upper Single view W air contrast PO
        "39149-0",  # XR Gastrointestinal tract and Pulmonary system Single view for foreign body
        "39151-6",  # RF Vas deferens Views W contrast intra vas deferens
        "39291-0",  # MR Lower extremity WO and W contrast IV
        "39292-8",  # MR Lower extremity WO contrast
        "39293-6",  # MR Lower extremity W contrast IV
        "39321-5",  # XR Shoulder AP internal rotation and AP external rotation and Axillary
        "39322-3",  # CT Spine W contrast intradisc
        "39323-1",  # XR Abdomen Right posterior oblique
        "39324-9",  # XR Wrist - left PA W clenched fist
        "39325-6",  # XR Shoulder - left AP internal rotation and Grashey and Axillary and Outlet
        "39326-4",  # XR Ribs - left and Chest Views
        "39327-2",  # XR Abdomen and Fetal Views for fetal age
        "39328-0",  # XR Shoulder - left AP internal rotation and AP external rotation
        "39329-8",  # XR Shoulder - bilateral AP internal rotation and AP external rotation
        "39330-6",  # XR Ankle - bilateral AP and Lateral W standing
        "39331-4",  # XR Foot - bilateral AP and Lateral W standing
        "39332-2",  # XR Foot - left AP and Lateral W standing
        "39333-0",  # XR Lumbar spine AP and Lateral W standing
        "39334-8",  # XR Foot - left AP and Lateral and oblique W standing
        "39335-5",  # XR Shoulder - left AP internal rotation and AP external rotation and Axillary
        "39336-3",  # XR Shoulder - bilateral AP internal rotation and AP external rotation and Axillary
        "39337-1",  # XR Shoulder - bilateral AP internal rotation and AP external rotation and Axillary and Outlet
        "39338-9",  # XR Shoulder - left AP internal rotation and AP external rotation and Axillary and Y
        "39339-7",  # XR Shoulder - bilateral AP and Axillary and Outlet and 30 degree caudal angle
        "39340-5",  # XR Lumbar spine Lateral Views W standing and W flexion and W extension
        "39341-3",  # XR Chest Lateral and PA W inspiration and expiration
        "39343-9",  # XR Shoulder - bilateral AP internal rotation and AP external rotation and Y
        "39344-7",  # XR Shoulder - bilateral AP internal rotation and AP external rotation and Axillary and Y
        "39345-4",  # XR Knee - left Sunrise and (Tunnel W standing)
        "39346-2",  # XR Shoulder - bilateral AP internal rotation and West Point
        "39347-0",  # XR Shoulder - left AP internal rotation and West Point
        "39348-8",  # XR Shoulder - left AP internal rotation and AP external rotation and Y
        "39349-6",  # RF Kidney - bilateral Views W contrast retrograde
        "39350-4",  # XR Shoulder - bilateral Grashey and Outlet and Serendipity
        "39351-2",  # XR Ribs upper anterior and posterior - left Views
        "39352-0",  # XR Ribs posterior - bilateral Views
        "39353-8",  # XR Ribs upper posterior - left Views
        "39360-3",  # XR Pelvis Views and Inlet and Outlet
        "39361-1",  # RF Guidance for drainage of abscess and placement of drainage catheter of Liver
        "39362-9",  # RF Guidance for placement of tube in Chest
        "39364-5",  # XR Wrist - right 3 Views and Radial deviation
        "39365-2",  # XR Wrist - right 3 Views and Ulnar deviation
        "39366-0",  # XR Scapula Lateral and outlet
        "39367-8",  # XR Thoracic and lumbar spine AP and lateral for scoliosis W standing
        "39368-6",  # XR Ankle - right AP and Lateral W standing
        "39369-4",  # XR Ankle - right AP and Lateral and Oblique and (View W manual stress)
        "39370-2",  # XR Ankle - right Views and (View W manual stress)
        "39371-0",  # XR Ankle - right AP and Lateral and oblique W standing
        "39372-8",  # XR Ankle - right Views and Mortise
        "39373-6",  # XR Elbow - right Views and Oblique
        "39374-4",  # XR Foot - right AP and Lateral W standing
        "39375-1",  # XR Foot - right AP and Lateral and oblique W standing
        "39376-9",  # XR Radius and Ulna - right Views and Oblique
        "39377-7",  # XR Hip - right Views and Lateral crosstable
        "39378-5",  # XR Knee - right 2 Views and Oblique
        "39379-3",  # XR Knee - right 2 Views and Sunrise
        "39380-1",  # XR Knee - right 2 Views and Sunrise and Tunnel
        "39381-9",  # XR Knee - right 2 Views and Tunnel
        "39382-7",  # XR Knee - right 2 views and (Tunnel W standing)
        "39383-5",  # XR Knee - right 3 Views and Sunrise
        "39384-3",  # XR Knee - right 4 views and (AP W standing)
        "39385-0",  # XR Knee - right 4 Views and Oblique
        "39386-8",  # XR Knee - right 4 views and Tunnel
        "39387-6",  # XR Knee - right 4 Views and Sunrise and Tunnel
        "39388-4",  # XR Knee - right AP and Lateral and Right oblique and Left oblique
        "39389-2",  # XR Knee - right Views and Tunnel
        "39390-0",  # XR Knee - right Views and Oblique
        "39391-8",  # XR Knee - right Views and Sunrise
        "39392-6",  # XR Shoulder - right Internal rotation and External rotation and Axillary
        "39393-4",  # XR Shoulder - right 3 Views and Axillary
        "39394-2",  # XR Shoulder - right 3 Views and Y
        "39395-9",  # XR Shoulder - right AP internal rotation and AP external rotation
        "39396-7",  # XR Shoulder - right AP internal rotation and West Point
        "39397-5",  # XR Shoulder - right AP internal rotation and AP external rotation and West Point
        "39398-3",  # XR Tibia and Fibula - right Views and Oblique
        "39399-1",  # XR Wrist - right 3 Views and Carpal tunnel
        "39400-7",  # XR Wrist - right Views and Carpal tunnel
        "39401-5",  # XR Shoulder AP and Grashey and Axillary
        "39402-3",  # XR Shoulder AP internal rotation and AP external rotation
        "39403-1",  # XR Shoulder Axillary and Transcapular
        "39404-9",  # XR Sinuses 3 Views and Submentovertex
        "39405-6",  # XR Sternum Lateral and right oblique and left oblique
        "39406-4",  # XR Sternum Lateral and right anterior oblique
        "39407-2",  # XR Thoracic spine 5 Views and Oblique
        "39410-6",  # XR Thoracic spine AP W left bending
        "39411-4",  # XR Thoracic spine AP W right bending
        "39412-2",  # XR Thoracic spine Views and Swimmers
        "39413-0",  # XR Thoracic spine 4 Views and Oblique
        "39414-8",  # XR Thoracic spine Views and Oblique
        "39489-0",  # XR Ribs lower posterior Views
        "39490-8",  # XR Femur and Tibia - right Views for leg length
        "39491-6",  # XR Ribs upper anterior and posterior - right Views
        "39492-4",  # XR Ribs upper posterior - right Views
        "39493-2",  # XR Ribs lower posterior - right Views
        "39511-1",  # XR Pelvis Views and Oblique
        "39512-9",  # XR Hip - right AP and Danelius Miller
        "39513-7",  # XR Hip - right Views and Danelius Miller
        "39514-5",  # XR Hip - right Danelius Miller
        "39515-2",  # XR Wrist - right Lateral Views W flexion and W extension
        "39516-0",  # XR Shoulder Stryker Notch
        "39517-8",  # XR Shoulder Stryker Notch and West Point
        "39518-6",  # XR Long bones Limited Survey Views
        "39519-4",  # XR Skull PA and Right lateral and Left lateral
        "39520-2",  # XR Skull PA and Right lateral and Left lateral and Towne
        "39521-0",  # XR Skull PA and Right lateral and Left lateral and Caldwell and Towne
        "41785-7",  # XR Elbow - right Limited Views
        "41789-9",  # XR Hand - right Limited Views
        "41790-7",  # XR Chest Single view during surgery
        "41792-3",  # XR Chest Right oblique and Left oblique
        "41793-1",  # XR Abdomen Single view during surgery
        "41795-6",  # RF Upper gastrointestinal tract and Small bowel Single view W air contrast PO
        "41797-2",  # RF Colon Limited Views W air and barium contrast PR
        "41799-8",  # RF Guidance for placement of tube in Liver
        "41800-4",  # RF Guidance for drainage and placement of drainage catheter of Pharynx
        "41802-0",  # RF Guidance for biopsy of Prostate
        "41803-8",  # RF Guidance for biopsy of Breast
        "41806-1",  # CT Abdomen
        "41807-9",  # CT Orbit
        "41808-7",  # CT Maxillofacial region
        "41811-1",  # XR Ribs - bilateral Views and Chest PA
        "41819-4",  # XR Knee - left 2 Views and Tunnel
        "41826-9",  # XR Elbow - left Limited Views
        "41830-1",  # XR Hand - left Limited Views
        "41832-7",  # XR Ribs - left Views and Chest PA
        "42007-5",  # XR Mastoid - bilateral Limited Views
        "42008-3",  # XR Humerus Single view during surgery
        "42009-1",  # XR Chest 2 Views and Apical lordotic
        "42010-9",  # XR Ribs - right Views and Chest PA
        "42011-7",  # XR Chest PA and Abdomen AP
        "42012-5",  # RF Gastrointestinal tract upper Views W water soluble contrast PO
        "42014-1",  # RF Urinary bladder and Urethra Views W contrast
        "42017-4",  # RF Guidance for percutaneous replacement of cholecystostomy of Abdomen
        "42019-0",  # XR Abdomen upright and left lateral decubitus
        "42020-8",  # CT Guidance for needle localization of Lumbar spine
        "42021-6",  # CT Guidance for needle localization of Cervical spine
        "42136-2",  # CT Guidance for biopsy of Heart
        "42153-7",  # XR Extremity Single view
        "42159-4",  # XR Sella turcica Views
        "42160-2",  # XR Unspecified body region Views for shunt patency
        "42163-6",  # XR Lumbar spine Views and Oblique
        "42164-4",  # XR Cervical spine Views and Oblique
        "42165-1",  # XR Ribs Views and Chest PA
        "42167-7",  # XR Pelvis and Hip - bilateral AP and Lateral frog
        "42260-0",  # CT Guidance for biopsy of Unspecified body region-- W contrast IV
        "42265-9",  # CT Guidance for superficial biopsy of Bone
        "42268-3",  # CT Extremity WO and W contrast IV
        "42269-1",  # XR Chest and Abdomen Views
        "42270-9",  # MR Cervical spine W flexion and W extension
        "42272-5",  # XR Chest PA and Lateral
        "42273-3",  # XR Ankle - bilateral 6 Views
        "42274-1",  # CT Abdomen and Pelvis WO and W contrast IV
        "42275-8",  # CT Chest and Abdomen W contrast IV
        "42276-6",  # CT Chest and Abdomen WO contrast
        "42277-4",  # CT Chest and Abdomen WO and W contrast IV
        "42278-2",  # CT Extremity WO contrast
        "42279-0",  # CT Guidance for biopsy of Kidney
        "42280-8",  # CT Guidance for drainage of abscess and placement of drainage catheter of Appendix
        "42281-6",  # CT Guidance for drainage of abscess and placement of drainage catheter of Chest
        "42282-4",  # CT Guidance for drainage of abscess and placement of drainage catheter of Liver
        "42283-2",  # CT Guidance for drainage and placement of drainage catheter of Pancreas
        "42284-0",  # CT Guidance for drainage of abscess and placement of chest tube of Pleural space
        "42285-7",  # CT Guidance for drainage of abscess and placement of drainage catheter of Kidney
        "42286-5",  # CT Guidance for drainage of abscess and placement of drainage catheter of Pelvis
        "42287-3",  # CT Guidance for drainage and placement of drainage catheter of Retroperitoneum
        "42291-5",  # CT Retroperitoneum WO contrast
        "42298-0",  # MR Unspecified body region WO and W contrast IV
        "42299-8",  # MR Clavicle WO and W contrast IV
        "42300-4",  # MR Thyroid gland
        "42301-2",  # MR Uterus
        "42302-0",  # MR Clavicle WO contrast
        "42303-8",  # MR Orbit and Face
        "42304-6",  # MRA Head vessels and Neck vessels
        "42311-1",  # XR Orbit - left Views for foreign body
        "42312-9",  # XR Orbit - right Views for foreign body
        "42313-7",  # XR Ribs - left Single view
        "42314-5",  # XR Ribs - right Single view
        "42335-0",  # RF Cervical spine Limited Views W contrast IT
        "42378-0",  # XR Lumbar spine AP W left bending
        "42379-8",  # XR Lumbar spine AP W right bending
        "42380-6",  # XR Ankle - left AP and Lateral W standing
        "42381-4",  # XR Ribs lower posterior - left Views
        "42382-2",  # XR Ankle - left Lateral and Mortise and Broden W manual stress
        "42383-0",  # XR Gallbladder Views W contrast PO and W contrast PO
        "42385-5",  # MR Brain and Pituitary and Sella turcica
        "42386-3",  # MR Brain cine for CSF flow
        "42387-1",  # MR Unspecified body region cine for CSF flow
        "42388-9",  # MR Prostate Endorectal
        "42389-7",  # MR Pelvis Endorectal
        "42390-5",  # MR Endovaginal
        "42391-3",  # MR Brain and Pituitary and Sella turcica W contrast IV
        "42392-1",  # MR Brain and Pituitary and Sella turcica WO and W contrast IV
        "42393-9",  # MR Brain and Pituitary and Sella turcica WO contrast
        "42394-7",  # CT Pulmonary system W Xe-133 IH
        "42395-4",  # XR Foot sesamoid bones - bilateral Axial
        "42396-2",  # XR Foot sesamoid bones - left Axial
        "42398-8",  # XR Foot Oblique and (AP and Lateral W standing)
        "42399-6",  # XR Foot sesamoid bones Views
        "42400-2",  # XR Foot sesamoid bones - bilateral Views
        "42401-0",  # XR Lumbar spine Lumbar (AP W R-bending and W L-bending and WO bending) and Lateral
        "42402-8",  # XR Unspecified body region Post morten Views
        "42403-6",  # XR Lumbar spine Views AP W right bending and W left bending
        "42404-4",  # XR Hip - left AP and Lateral Views for measurement
        "42405-1",  # XR Knee (AP W standing) and (Lateral W extension)
        "42406-9",  # XR Lumbar spine Views AP W and WO left bending
        "42407-7",  # XR Lumbar spine Views AP W and WO right bending
        "42408-5",  # XR Lumbar spine Views AP W right bending and W left bending and WO bending
        "42409-3",  # XR Foot sesamoid bones AP and Lateral
        "42410-1",  # XR Lumbar spine AP and Lateral and Oblique and Spot W standing
        "42411-9",  # XR Lumbar spine (AP^W R-bending and W L-bending) and (Lateral^W flexion and W extension)
        "42412-7",  # XR Shoulder - left 90 degree abduction Views
        "42413-5",  # XR Lumbar spine Views W right bending and W left bending
        "42414-3",  # XR Chest Right oblique and Left oblique W nipple markers
        "42417-6",  # XR Ankle - bilateral AP and Lateral and Oblique and (View W manual stress)
        "42418-4",  # XR Ankle - left AP and Lateral and Oblique and (View W manual stress)
        "42419-2",  # XR Wrist - bilateral Single view
        "42420-0",  # XR Pelvis AP W standing
        "42421-8",  # RF Guidance for percutaneous drainage of abscess and placement of drainage catheter of Unspecified body region
        "42422-6",  # RF Guidance for percutaneous drainage of abscess and placement of drainage catheter of Breast
        "42423-4",  # RF Guidance for percutaneous drainage of abscess and placement of drainage catheter of Chest
        "42424-2",  # XR Thoracic and lumbar spine AP and lateral for scoliosis W sitting
        "42425-9",  # XR Thoracic and lumbar spine AP Views for scoliosis W standing and W right bending and W left bending and WO bending
        "42426-7",  # XR Thoracic and lumbar spine AP for scoliosis W sitting
        "42427-5",  # XR Thoracic and lumbar spine Lateral for scoliosis W sitting
        "42428-3",  # XR Thoracic and lumbar spine AP for scoliosis W standing in brace
        "42429-1",  # XR Thoracic and lumbar spine AP for scoliosis W standing and W right bending
        "42430-9",  # XR Knee - right 2 views and (Views W standing)
        "42431-7",  # XR Knee - right PA 30 degree flexion W standing
        "42432-5",  # XR Knee - right Sunrise and (Views W standing)
        "42434-1",  # XR Foot sesamoid bones - right Views
        "42435-8",  # XR Sella turcica 2 Views
        "42436-6",  # XR Sella turcica Lateral and Towne
        "42438-2",  # XR Neck AP and Lateral
        "42439-0",  # XR Neck AP
        "42441-6",  # XR Neck Magnification
        "42442-4",  # XR Spine Lateral W standing
        "42443-2",  # XR Thoracic spine 3 Views W standing
        "42444-0",  # XR Thoracic spine Views AP W right bending and W left bending and WO bending
        "42445-7",  # XR Thoracic spine Views AP W left bending and WO bending
        "42446-5",  # XR Thoracic spine Views AP W right bending and WO bending
        "42459-8",  # RF Gastrointestinal tract upper Views W contrast PO
        "42460-6",  # RF Submandibular gland - left Views W contrast intra salivary duct
        "42469-7",  # RF Gastrointestinal tract upper and Small bowel and Gallbladder Single view W contrast PO
        "42470-5",  # RF Gastrointestinal tract upper and Gallbladder Single view W contrast PO
        "42472-1",  # XR Thoracic and lumbar spine AP Views for scoliosis in traction
        "42681-7",  # RF Colon Views W gastrografin PR
        "42684-1",  # RF Gastrointestinal tract upper Views W gastrografin PO
        "42685-8",  # XR Pelvis and Hip - left 2 Views
        "42686-6",  # XR Pelvis and Hip - right 2 Views
        "42687-4",  # XR Ribs - bilateral 2 Views
        "42688-2",  # CT Guidance for nerve block of Spine
        "42689-0",  # XR Spine Oblique
        "42690-8",  # XR Spine Views W flexion and W extension
        "42691-6",  # XR Cervical spine 6 Views
        "42692-4",  # XR Thoracic and lumbar spine Views
        "42693-2",  # MR Urinary bladder and Urethra cine
        "42694-0",  # MR Clavicle W contrast IV
        "42695-7",  # MR Lower leg - bilateral W contrast IV
        "42696-5",  # MR Lower leg - bilateral
        "42697-3",  # MR Lower leg - bilateral WO and W contrast IV
        "42698-1",  # MR Cervical and thoracic and lumbar spine
        "42699-9",  # XR Chest and Abdomen Single view
        "42701-3",  # CT Guidance for localization of placenta of Uterus
        "42702-1",  # RF Greater than 1 hour
        "42703-9",  # RF Less than 1 hour
        "42710-4",  # XR Cervical spine Limited Views
        "42811-0",  # XR Wrist - right scaphoid single view
        "42812-8",  # XR Wrist scaphoid single view
        "42813-6",  # XR Wrist - bilateral scaphoid single view
        "42814-4",  # XR Wrist - left scaphoid single view
        "43444-9",  # CT Guidance for percutaneous drainage of abscess and placement of drainage catheter of Unspecified body region
        "43445-6",  # CT Pulmonary system
        "43448-0",  # MR Liver WO and W ferumoxides IV
        "43449-8",  # MR Ankle - right dynamic W contrast IV
        "43450-6",  # MR Elbow - left dynamic W contrast IV
        "43451-4",  # MR Elbow - right dynamic W contrast IV
        "43452-2",  # MR Knee - left dynamic W contrast IV
        "43453-0",  # MR Knee - right dynamic W contrast IV
        "43454-8",  # MR Pulmonary system
        "43455-5",  # MR Oropharynx
        "43456-3",  # MR Cervical and thoracic spine WO and W contrast IV
        "43457-1",  # MR Cervical and thoracic spine
        "43458-9",  # MRA Orbit vessels WO and W contrast IV
        "43463-9",  # XR Chest PA and Abdomen Supine and Upright
        "43466-2",  # XR Chest AP right lateral-decubitus
        "43467-0",  # XR Chest 2 Views and Right oblique and Left oblique
        "43468-8",  # XR Unspecified body region Views
        "43469-6",  # XR Unspecified body region Views for foreign body
        "43470-4",  # XR Skull LE 3 Views
        "43471-2",  # RF 2 hour
        "43472-0",  # RF 90 minutes
        "43473-8",  # RF Guidance for endoscopy of Biliary ducts and Pancreatic duct-- 2H post contrast retrograde intrabiliary
        "43474-6",  # RF Guidance for endoscopy of Biliary ducts and Pancreatic duct-- 15m post contrast retrograde intrabiliary
        "43475-3",  # RF Guidance for endoscopy of Biliary ducts and Pancreatic duct-- 30M post contrast retrograde intrabiliary
        "43476-1",  # RF Guidance for endoscopy of Biliary ducts and Pancreatic duct-- 45M post contrast retrograde intrabiliary
        "43477-9",  # RF Guidance for endoscopy of Biliary ducts and Pancreatic duct-- 1H post contrast retrograde intrabiliary
        "43478-7",  # RF Guidance for endoscopy of Biliary ducts and Pancreatic duct-- 1.5 hours post contrast retrograde intrabiliary
        "43480-3",  # XR Joint Lateral Views W manual stress
        "43481-1",  # XR Joint Views W flexion and W extension
        "43482-9",  # XR Knee - right GE 3 Views
        "43483-7",  # XR Foot - right 3 or 4 Views
        "43485-2",  # XR Kidney Views during surgery W contrast retrograde
        "43486-0",  # XR Sinuses GE 3 Views
        "43488-6",  # XR Thumb - left GE 3 Views
        "43489-4",  # XR Finger second - left GE 3 Views
        "43490-2",  # XR Finger third - left GE 3 Views
        "43491-0",  # XR Finger fourth - left GE 3 Views
        "43492-8",  # XR Finger fifth - left GE 3 Views
        "43493-6",  # XR Thumb - right GE 3 Views
        "43494-4",  # XR Finger second - right GE 3 Views
        "43495-1",  # XR Finger third - right GE 3 Views
        "43496-9",  # XR Finger fourth - right GE 3 Views
        "43497-7",  # XR Finger fifth - right GE 3 Views
        "43498-5",  # XR Knee - left GE 3 Views
        "43499-3",  # XR Foot - left 3 or 4 Views
        "43502-4",  # CT Guidance for drainage of abscess and placement of drainage catheter of Subphrenic space
        "43504-0",  # MR Axilla - left W contrast IV
        "43505-7",  # MR Axilla - right W contrast IV
        "43506-5",  # MR Ovary - bilateral
        "43507-3",  # MR Thymus gland
        "43508-1",  # MR Axilla - left
        "43509-9",  # MR Axilla - left WO and W contrast IV
        "43510-7",  # MR Axilla - right
        "43511-5",  # MR Axilla - right WO and W contrast IV
        "43512-3",  # MRA Lower leg vessels - bilateral W contrast IV
        "43513-1",  # MRA Lower leg vessels - left
        "43514-9",  # MRA Thigh vessels - left WO contrast
        "43515-6",  # MRA Thigh vessels - right WO contrast
        "43516-4",  # MRA Wrist vessels - left WO contrast
        "43517-2",  # MRA Wrist vessels - right WO contrast
        "43518-0",  # XR Bones Survey Views
        "43519-8",  # XR Bones Limited Survey Views
        "43521-4",  # XR Mandible 1 or 2 Views
        "43522-2",  # XR Pelvis 1 or 2 Views
        "43523-0",  # XR Sinuses 1 or 2 Views
        "43524-8",  # XR Skull GE 5 Views
        "43525-5",  # CT Unspecified body region WO contrast
        "43528-9",  # MR Breast - unilateral WO and W contrast IV
        "43529-7",  # XR Orbit and Facial bones Views
        "43530-5",  # MR Orbit and Face and Neck
        "43532-1",  # XR Chest PA and Abdomen Upright
        "43537-0",  # RF Guidance for drainage and placement of drainage catheter of Unspecified body region
        "43539-6",  # XR Cervical spine 2 or 3 Views
        "43543-8",  # XR Pelvis GE 3 Views
        "43555-2",  # MR Ankle - left dynamic W contrast IV
        "43556-0",  # MRA Lower leg vessels - right
        "43558-6",  # RF Guidance for change of dialysis catheter in Unspecified body region-- W contrast IV
        "43559-4",  # RF Urinary bladder and Urethra Views W contrast intra bladder during voiding
        "43561-0",  # XR Chest AP and Abdomen Upright
        "43567-7",  # CT Guidance for deep biopsy of Bone
        "43569-3",  # XR Thoracic and lumbar spine AP Views for scoliosis upright and supine
        "43574-3",  # RF Upper gastrointestinal tract and Small bowel Views W barium contrast PO
        "43641-0",  # XR Foot sesamoid bones - left Views
        "43757-4",  # CT Guidance for fine needle aspiration of Kidney
        "43766-5",  # CT Kidney - bilateral W contrast IV
        "43767-3",  # CT Kidney - bilateral
        "43768-1",  # CT Kidney WO and W contrast IV
        "43769-9",  # MR Brain and Internal auditory canal WO and W contrast IV
        "43770-7",  # CT Kidney WO contrast
        "43772-3",  # MR Brain and Internal auditory canal
        "43773-1",  # MR Kidney WO contrast
        "43775-6",  # MR Kidney WO and W contrast IV
        "43779-8",  # XR Knee - left Sunrise
        "43780-6",  # XR Knee Sunrise
        "43781-4",  # XR Spine cervicothoracic junction Views
        "43784-8",  # XR Cervical and thoracic and lumbar spine 2 Views
        "43785-5",  # XR Spine cervicothoracic junction AP and Lateral
        "43787-1",  # XR Skull and Facial bones and Mandible Views for dental measurement
        "43788-9",  # RF Tube Views for patency W contrast via tube
        "43790-5",  # XR Shoulder - right Grashey and Y
        "43791-3",  # XR Lumbar spine Oblique Views
        "43796-2",  # XR Wrist - bilateral Carpal tunnel Views
        "44101-4",  # CT Guidance for ablation of tissue of Liver
        "44102-2",  # CT Guidance for procedure of Joint space
        "44103-0",  # CT Guidance for fine needle aspiration of Lymph node
        "44104-8",  # CT Guidance for fine needle aspiration of Mediastinum
        "44105-5",  # CT Guidance for fine needle aspiration of Muscle
        "44106-3",  # CT Guidance for FNA of Prostate
        "44107-1",  # CT Guidance for fine needle aspiration of Retroperitoneum
        "44108-9",  # CT Guidance for fine needle aspiration of Adrenal gland
        "44109-7",  # CT Guidance for deep biopsy of Muscle
        "44110-5",  # CT Guidance for needle localization of Breast
        "44111-3",  # CT Skull base WO and W contrast IV
        "44112-1",  # CT Skull base WO contrast
        "44113-9",  # CT Thoracic spine WO and W contrast IT
        "44114-7",  # CT Lumbar spine WO and W contrast IT
        "44115-4",  # CT Abdomen and Pelvis
        "44116-2",  # CT Mandible limited
        "44117-0",  # CT Guidance for biopsy of Retroperitoneum
        "44118-8",  # CT Guidance for needle localization of Breast-- WO and W contrast IV
        "44119-6",  # CT Breast - bilateral WO contrast
        "44122-0",  # MR Guidance for stereotactic localization of Brain-- WO and W contrast IV
        "44123-8",  # MR Biliary ducts and Pancreatic duct WO contrast
        "44124-6",  # MR Adrenal gland W contrast IV
        "44125-3",  # MR Biliary ducts and Pancreatic duct W contrast IV
        "44126-1",  # MR Heart cine for blood flow velocity mapping W contrast IV
        "44127-9",  # MR Heart limited cine for function
        "44128-7",  # MRA Lower extremity vessels WO and W contrast IV
        "44129-5",  # MRA Lower extremity vessels WO contrast
        "44130-3",  # MRA Aortic arch WO contrast
        "44131-1",  # MRA Thoracic and abdominal aorta WO and W contrast IV
        "44132-9",  # MRA Thoracic and abdominal aorta WO contrast
        "44133-7",  # MRA Renal vessels WO contrast
        "44134-5",  # MRA Renal vessels WO and W contrast IV
        "44135-2",  # MRA Lower extremity vessels - bilateral W contrast IV
        "44177-4",  # XR Lower extremity - bilateral AP W standing
        "44178-2",  # XR Lumbar spine oblique and (views W right bending and W left bending)
        "44179-0",  # XR Sacrum and Coccyx 2 Views
        "44181-6",  # XR Sacroiliac Joint 2 or 3 Views
        "44188-1",  # XR Foot GE 3 Views
        "44189-9",  # XR Sacroiliac Joint GE 3 Views
        "44190-7",  # XR Wrist GE 3 Views
        "44191-5",  # XR Ribs GE 3 Views and Chest PA
        "44194-9",  # XR Spine GE 4 Views W right bending and W left bending
        "44195-6",  # XR Knee GE 5 Views
        "44196-4",  # XR Lumbar spine GE 5 Views W right bending and W left bending
        "44197-2",  # XR Knee - bilateral GE 5 Views W standing
        "44198-0",  # XR Knee 1 or 2 Views
        "44199-8",  # XR Facial bones 1 or 2 Views
        "44205-3",  # XR Lower extremity - bilateral Single view W standing
        "44206-1",  # XR Thoracic and lumbar spine for scoliosis single view
        "44208-7",  # XR Orbit Views for foreign body
        "44209-5",  # XR Sinuses Limited Views
        "44210-3",  # XR Ankle GE 3 Views
        "44211-1",  # XR Chest GE 4 Views
        "44212-9",  # XR Cervical spine GE 4 Views
        "44213-7",  # RF Guidance for endoscopy of Pancreatic duct-- W contrast retrograde
        "44214-5",  # RF Guidance for endoscopy of Biliary ducts-- W contrast retrograde
        "44215-2",  # RF Guidance for fine needle aspiration of Unspecified body region
        "44216-0",  # RF Guidance for fine needle aspiration of Thyroid gland
        "44217-8",  # RF Guidance for fine needle aspiration of Kidney
        "44218-6",  # RF Guidance for fine needle aspiration of Pancreas
        "44220-2",  # RF Guidance for fine needle aspiration of Liver
        "44221-0",  # RF Guidance for deep aspiration.fine needle of Tissue
        "44222-8",  # RF Guidance for procedure of Joint space
        "44223-6",  # RF Guidance for percutaneous drainage of abscess and placement of drainage catheter of Ovary
        "44224-4",  # RF Guidance for placement of tube in Unspecified body region
        "44225-1",  # RF Guidance for biopsy of Liver-- W contrast IV
        "44226-9",  # RF Colon Views for reduction W barium contrast PR
        "44227-7",  # RF Colon Views W barium contrast PR
        "44228-5",  # CT Guidance for ablation of tissue of Kidney
        "44229-3",  # CT Bone
        "44230-1",  # MRA Superior mesenteric vessels WO contrast
        "44231-9",  # MRA Superior mesenteric vessels WO and W contrast IV
        "44238-4",  # XR Trachea Views
        "46281-2",  # CT Guidance for aspiration or injection of cyst of Unspecified body region
        "46289-5",  # CT Guidance for biopsy of Unspecified body region-- WO and W contrast IV
        "46290-3",  # CT Guidance for biopsy of Unspecified body region-- WO contrast
        "46291-1",  # CT Guidance for drainage and placement of drainage catheter of Unspecified body region-- WO and W contrast IV
        "46292-9",  # CT Guidance for drainage and placement of drainage catheter of Unspecified body region-- W contrast IV
        "46293-7",  # CT Guidance for drainage and placement of drainage catheter of Unspecified body region-- WO contrast
        "46298-6",  # CT Mastoid - bilateral
        "46299-4",  # MR Breast - unilateral
        "46304-2",  # CT Sinuses limited WO contrast
        "46305-9",  # CT Whole body
        "46306-7",  # CT Whole body W contrast IV
        "46310-9",  # MR Orbit and Face and Neck WO and W contrast IV
        "46311-7",  # CT Parotid gland WO and W contrast IV
        "46313-3",  # CT Pelvis WO and W reduced contrast volume IV
        "46314-1",  # CT Internal auditory canal WO and W reduced contrast volume IV
        "46315-8",  # CT Maxillofacial region WO and W reduced contrast volume IV
        "46316-6",  # CT Head WO and W reduced contrast volume IV
        "46317-4",  # CT Chest WO and W reduced contrast volume IV
        "46318-2",  # CT Abdomen WO and W reduced contrast volume IV
        "46319-0",  # MR Elbow Arthrogram
        "46320-8",  # CT Orbit and Face W contrast IV
        "46321-6",  # MR Orbit and Face and Neck W contrast IV
        "46322-4",  # CT Kidney W contrast IV
        "46323-2",  # MR Breast - unilateral W contrast IV
        "46324-0",  # MRA Lower extremity vessels W contrast IV
        "46325-7",  # CT Internal auditory canal W reduced contrast volume IV
        "46326-5",  # CT Maxillofacial region W reduced contrast volume IV
        "46327-3",  # CT Chest W reduced contrast volume IV
        "46328-1",  # CT Head W reduced contrast volume IV
        "46329-9",  # CT Pelvis W reduced contrast volume IV
        "46330-7",  # CT Abdomen W reduced contrast volume IV
        "46331-5",  # CT Orbit WO contrast
        "46332-3",  # MR Orbit and Face and Neck WO contrast
        "46333-1",  # MR Breast - unilateral WO contrast
        "46340-6",  # XR Spine lumbosacral junction Views
        "46341-4",  # RF Abdomen Views
        "46343-0",  # XR Wrist - right GE 3 Views
        "46344-8",  # XR Elbow - left GE 3 Views
        "46345-5",  # XR Elbow - right GE 3 Views
        "46346-3",  # XR Wrist - left GE 3 Views
        "46347-1",  # XR Ankle - right GE 3 Views
        "46348-9",  # XR Chest GE 2 and PA and Lateral
        "46349-7",  # XR Shoulder - bilateral AP and Transthoracic
        "46357-0",  # RF Colon Views W air contrast PR
        "46358-8",  # MR Whole body
        "46359-6",  # MRA Superior mesenteric vessels
        "46360-4",  # MRA Aortic arch WO and W contrast IV
        "46365-3",  # CT Guidance for ablation of tissue of Celiac plexus
        "46371-1",  # XR Guidance for change of percutaneous tube in Unspecified body region-- W contrast
        "46372-9",  # RF Guidance for percutaneous drainage and placement of drainage catheter of Biliary ducts
        "46376-0",  # RF Kidney - bilateral Views W contrast antegrade
        "46377-8",  # XR Skull GE 3 Views
        "46378-6",  # XR Knee - bilateral PA Views W standing and W flexion
        "46381-0",  # XR Elbow and Radius and Ulna Views
        "46386-9",  # XR Teeth Bitewing Views
        "46389-3",  # XR Elbow - bilateral Views and Radial head capitellar
        "46390-1",  # XR Ankle - left GE 3 Views
        "46392-7",  # RF Guidance for injection of Sinuses
        "46393-5",  # CT Liver W Xe-133 IH
        "47366-0",  # CT Chest limited WO contrast
        "47368-6",  # XR Chest GE 4 and PA and Lateral
        "47370-2",  # XR Hand - left GE 3 Views
        "47371-0",  # XR Hand - right GE 3 Views
        "47372-8",  # XR Hip Views during surgery
        "47373-6",  # XR Knee - left 1 or 2 Views
        "47374-4",  # XR Knee - left GE 4 Views
        "47375-1",  # XR Knee - right 1 or 2 Views
        "47376-9",  # XR Knee - right GE 4 Views
        "47377-7",  # XR Knee - right LE 4 Views
        "47379-3",  # XR Mandible GE 4 Views
        "47380-1",  # XR Mandible LE 3 Views
        "47381-9",  # XR Mastoid GE 3 Views
        "47382-7",  # XR Lumbar spine GE 4 Views
        "47983-2",  # XR Mastoid - bilateral 1 or 2 Views
        "47984-0",  # XR Pelvis and Spine Lumbar Views
        "47985-7",  # CT Spine W contrast IT
        "48433-7",  # XR Calcaneus - bilateral 2 Views
        "48435-2",  # RF Guidance for injection of Salivary gland - bilateral
        "48436-0",  # MR Lumbar spine W contrast IT
        "48439-4",  # MR Thoracic spine W contrast IT
        "48440-2",  # MR Skull base W contrast IV
        "48441-0",  # MR Thoracic spine WO and W contrast IT
        "48442-8",  # CT Spine WO and W contrast IT
        "48443-6",  # CT Nasopharynx WO and W contrast IV
        "48444-4",  # MR Brain.temporal W contrast IV
        "48445-1",  # MR Larynx WO contrast
        "48446-9",  # CT Nasopharynx W contrast IV
        "48447-7",  # MR Cervical spine W contrast IT
        "48449-3",  # CT Orbit W contrast IV
        "48450-1",  # MR Cervical spine WO and W contrast IT
        "48451-9",  # CT Orbit WO and W contrast IV
        "48452-7",  # MR Lumbar spine WO and W contrast IT
        "48453-5",  # MR Brain.temporal WO contrast
        "48454-3",  # MR Clavicle - right WO and W contrast IV
        "48455-0",  # MR Clavicle - left WO and W contrast IV
        "48456-8",  # MR Clavicle - right W contrast IV
        "48457-6",  # MR Clavicle - left W contrast IV
        "48458-4",  # MR Clavicle - right WO contrast
        "48459-2",  # MR Clavicle - left WO contrast
        "48460-0",  # MR Unspecified body region limited
        "48461-8",  # MR Neck limited
        "48462-6",  # XR Knee - left AP
        "48463-4",  # XR Knee - right AP
        "48464-2",  # RF Trachea Views
        "48465-9",  # RF Larynx Views
        "48466-7",  # XR Skull Limited Views
        "48467-5",  # XR Sacroiliac Joint 1 or 2 Views
        "48468-3",  # XR Ribs - bilateral 2 Views and Chest PA
        "48469-1",  # XR Lumbar spine 2 or 3 Views
        "48470-9",  # XR Mastoid - left 3 Views
        "48471-7",  # XR Mastoid - right 3 Views
        "48472-5",  # XR Thoracic spine 3 Views and Swimmers
        "48473-3",  # XR Spine Lumbar and Sacrum 4 Views
        "48474-1",  # XR Hand - bilateral AP and Lateral
        "48476-6",  # XR Foot - right GE 3 Views
        "48477-4",  # XR Foot - left GE 3 Views
        "48478-2",  # XR Foot - bilateral GE 3 Views
        "48479-0",  # XR Facial bones GE 3 Views
        "48480-8",  # XR Ankle - bilateral GE 3 Views
        "48481-6",  # XR Elbow - bilateral GE 3 Views
        "48482-4",  # XR Sternoclavicular joint - bilateral GE 3 Views
        "48483-2",  # XR Wrist - bilateral GE 3 Views
        "48484-0",  # XR Ribs - right GE 3 Views and Chest PA
        "48485-7",  # XR Ribs - bilateral GE 3 Views and Chest PA
        "48486-5",  # XR Ribs - left GE 3 Views and Chest PA
        "48487-3",  # XR Skull GE 4 Views
        "48488-1",  # XR Mastoid - right 1 or 2 Views
        "48489-9",  # XR Mastoid - left 1 or 2 Views
        "48490-7",  # XR Temporomandibular joint - right Open and Closed mouth
        "48491-5",  # XR Temporomandibular joint - left Open and Closed mouth
        "48687-8",  # MR Skull base WO contrast
        "48694-4",  # MR Brain.temporal WO and W contrast IV
        "48695-1",  # XR Skull base Single view
        "48696-9",  # RF Submandibular gland - right Views W contrast intra salivary duct
        "48697-7",  # XR Skull base Views
        "48698-5",  # RF Submandibular gland - bilateral Views W contrast intra salivary duct
        "48699-3",  # XR Temporomandibular joint - unilateral Open and Closed mouth
        "48737-1",  # XR Wrist and Hand 3 Views
        "48738-9",  # XR Wrist - bilateral and Hand - bilateral 3 Views
        "48743-9",  # CT Retroperitoneum WO and W contrast IV
        "48746-2",  # XR Sacroiliac joint - bilateral GE 3 Views
        "48747-0",  # XR Orbit - bilateral GE 4 Views
        "48748-8",  # XR Spine Oblique Views
        "48749-6",  # XR Thoracic spine Oblique Views
        "49507-7",  # MR Unspecified body region W contrast IV
        "49512-7",  # RF Unspecified body region Views
        "49565-5",  # MRA Thoracic spine vessels
        "49570-5",  # XR Ankle - bilateral GE 6 Views
        "50755-8",  # CT Lower extremity - bilateral W contrast IV
        "51387-9",  # XR Knee - bilateral Views and (AP W standing)
        "51388-7",  # XR Wrist - right and Hand - right Views
        "51392-9",  # XR Wrist - left and Hand - left Views
        "51394-5",  # XR Ankle and Foot - right Views
        "51395-2",  # XR Ankle and Foot - left Views
        "53626-8",  # CT Cerebral atrophic index
        "58740-2",  # MRCP Abdomen WO contrast
        "58744-4",  # CT Heart
        "58747-7",  # CT Guidance for ablation of tissue of Unspecified body region
        "58748-5",  # Functional MR Brain
        "58749-3",  # MR Heart W stress and WO and W contrast IV
        "58750-1",  # MR Heart W stress
        "60515-4",  # CT Colon and Rectum W air contrast PR
        "62450-2",  # RF Guidance for placement of catheter in Peritoneum
        "64996-2",  # XR Lung - left Views W contrast intrabronchial
        "64997-0",  # XR Lung - right Views W contrast intrabronchial
        "64998-8",  # RF Guidance for placement of catheter in Fallopian tube - left-- transcervical
        "64999-6",  # RF Guidance for placement of catheter in Fallopian tube - right-- transcervical
        "65799-9",  # RF Kidney - bilateral Single view for cyst
        "65800-5",  # RF Kidney - left Single view for cyst
        "65801-3",  # RF Kidney - right Single view for cyst
        "69055-2",  # XR Acromioclavicular joint - bilateral Views WO weight
        "69056-0",  # XR Elbow - bilateral Views and Obliques
        "69057-8",  # XR Hand - bilateral AP and Lateral and oblique
        "69058-6",  # XR Hip - bilateral 2 Views
        "69059-4",  # XR Hip - bilateral Views and Lateral crosstable
        "69060-2",  # XR Knee - bilateral 2 Views and Sunrise
        "69061-0",  # XR Knee - bilateral 2 Views and Tunnel
        "69062-8",  # XR Knee - bilateral 4 Views W standing
        "69063-6",  # XR Knee - bilateral 4 Views and Sunrise and Tunnel
        "69064-4",  # XR Knee - bilateral Sunrise and (Views W standing)
        "69065-1",  # XR Abdomen AP and Lateral crosstable
        "69069-3",  # XR Patella - bilateral Sunrise
        "69070-1",  # XR Ribs - bilateral Anterior and Lateral
        "69071-9",  # XR Ribs - bilateral and Chest Views
        "69072-7",  # XR Wrist - bilateral Ulnar deviation and Radial deviation
        "69073-5",  # RF Guidance for core needle biopsy of Unspecified body region
        "69074-3",  # RF Guidance for biopsy of Pelvis
        "69075-0",  # RF Guidance for biopsy of Salivary gland
        "69076-8",  # RF guidance for percutaneous biopsy of Bone
        "69078-4",  # RF Guidance for drainage and placement of drainage catheter of Chest
        "69079-2",  # XR Clavicle 45 degree cephalic angle
        "69080-0",  # XR Cervical spine 5 Views W flexion and W extension
        "69081-8",  # XR Cervical spine 5 Views and Swimmers
        "69083-4",  # CT Guidance for biopsy of Abdomen-- WO contrast
        "69087-5",  # CT Ankle - bilateral WO contrast
        "69088-3",  # CT Knee - bilateral W contrast IV
        "69089-1",  # CT Knee - bilateral WO contrast
        "69090-9",  # CT Shoulder - bilateral WO contrast
        "69091-7",  # CT Wrist - bilateral W contrast IV
        "69092-5",  # CT Guidance for biopsy of Liver-- WO contrast
        "69093-3",  # CT Guidance for biopsy of Pelvis-- W contrast IV
        "69094-1",  # CT Guidance for biopsy of Pelvis-- WO contrast
        "69095-8",  # CT Urinary bladder W contrast IV
        "69096-6",  # CT Chest limited W contrast IV
        "69102-2",  # CT Ankle - left Arthrogram
        "69103-0",  # CT Elbow - left Arthrogram
        "69104-8",  # CT Extremity - left WO contrast
        "69105-5",  # CT Hip - left Arthrogram
        "69106-3",  # CT Knee - left Arthrogram
        "69107-1",  # CT Wrist - left Arthrogram
        "69109-7",  # CT Ankle - right Arthrogram
        "69110-5",  # CT Elbow - right Arthrogram
        "69111-3",  # CT Extremity - right WO contrast
        "69112-1",  # CT Hip - right Arthrogram
        "69113-9",  # CT Kidney - right
        "69114-7",  # CT Knee - right Arthrogram
        "69115-4",  # CT Wrist - right Arthrogram
        "69116-2",  # CT Sacrum and Coccyx
        "69117-0",  # CT Scapula
        "69118-8",  # CT Scapula WO contrast
        "69120-4",  # RF Guidance for drainage of abscess and placement of drainage catheter of Neck
        "69121-2",  # RF Guidance for aspiration of cyst of Ovary
        "69122-0",  # RF Guidance for drainage of abscess and placement of drainage catheter of Pancreas
        "69123-8",  # RF Guidance for drainage of abscess and placement of chest tube of Pleural space
        "69124-6",  # RF Guidance for superficial aspiration.fine needle of Tissue
        "69127-9",  # RF Guidance for biopsy of Chest Pleura
        "69129-5",  # RF Guidance for biopsy of Thyroid gland
        "69130-3",  # XR Hand AP and Lateral
        "69131-1",  # XR Hip Views and Danelius Miller
        "69132-9",  # XR Hip Danelius Miller
        "69133-7",  # RF Guidance for drainage and placement of drainage catheter of Hip
        "69136-0",  # XR Knee Sunrise and Tunnel
        "69137-8",  # XR Ankle - left AP and Lateral and oblique W standing
        "69138-6",  # XR Ankle - left 3 Views W standing
        "69139-4",  # XR Hip - left Views and Lateral crosstable
        "69140-2",  # XR Hip - left Views and Danelius Miller
        "69141-0",  # XR Hip - left Danelius Miller
        "69142-8",  # XR Knee - left 2 Views and Sunrise
        "69143-6",  # XR Knee - left 2 views and (Tunnel W standing)
        "69144-4",  # XR Knee - left 4 views and (AP W standing)
        "69145-1",  # XR Knee - left 4 views and Tunnel
        "69146-9",  # XR Knee - left AP and Lateral crosstable
        "69147-7",  # XR Knee - left AP and Lateral and Right oblique and Left oblique
        "69148-5",  # XR Knee - left Views and Tunnel
        "69149-3",  # XR Knee - left Sunrise and (Views W standing)
        "69151-9",  # XR Wrist - left 3 Scaphoid Views
        "69152-7",  # XR Patella - left Single view
        "69153-5",  # XR Shoulder - left AP and Grashey and Axillary
        "69154-3",  # XR Shoulder - left 3 Views and Axillary
        "69155-0",  # XR Shoulder - left 3 Views and Y
        "69156-8",  # XR Shoulder - left Grashey and Y
        "69157-6",  # XR Wrist - left Lateral Views W flexion and W extension
        "69158-4",  # XR Breast Diagnostic for implant
        "69159-2",  # XR Breast Screening for implant
        "69161-8",  # MRA Circle of Willis WO and W contrast IV
        "69162-6",  # MRA Pulmonary artery - bilateral W contrast IA
        "69163-4",  # MR Ankle - bilateral W contrast IV
        "69164-2",  # MR Ankle - bilateral WO contrast
        "69165-9",  # MR Breast - bilateral for implant
        "69166-7",  # MR Breast - bilateral for implant WO and W contrast IV
        "69167-5",  # MR Breast - bilateral for implant W contrast IV
        "69168-3",  # MR Breast - bilateral for implant WO contrast
        "69169-1",  # MR Guidance for biopsy of Breast - bilateral
        "69170-9",  # MR Elbow - bilateral W contrast IV
        "69171-7",  # MR Elbow - bilateral WO contrast
        "69172-5",  # MR Femur - bilateral W contrast IV
        "69173-3",  # MR Femur - bilateral WO contrast
        "69174-1",  # MR Forearm - bilateral WO and W contrast IV
        "69175-8",  # MR Forearm - bilateral W contrast IV
        "69176-6",  # MR Forearm - bilateral WO contrast
        "69177-4",  # MR Hand - bilateral WO and W contrast IV
        "69178-2",  # MR Hand - bilateral W contrast IV
        "69179-0",  # MR Hand - bilateral WO contrast
        "69180-8",  # MR Upper arm - bilateral
        "69181-6",  # MR Upper arm - bilateral WO and W contrast IV
        "69182-4",  # MR Upper arm - bilateral W contrast IV
        "69183-2",  # MR Upper arm - bilateral WO contrast
        "69184-0",  # MR Shoulder - bilateral W contrast IV
        "69185-7",  # MR Lower leg - bilateral WO contrast
        "69186-5",  # MR Upper extremity - bilateral WO and W contrast IV
        "69187-3",  # MR Upper extremity - bilateral W contrast IV
        "69188-1",  # MR Upper extremity - bilateral WO contrast
        "69189-9",  # MR Breast for implant WO and W contrast IV
        "69190-7",  # MR Breast for implant W contrast IV
        "69191-5",  # MR Breast for implant WO contrast
        "69192-3",  # MR Guidance for aspiration of cyst of Breast
        "69193-1",  # MR Extremity
        "69194-9",  # MR Finger WO and W contrast IV
        "69195-6",  # MR Finger W contrast IV
        "69196-4",  # MR Finger WO contrast
        "69197-2",  # MR Guidance for biopsy of Liver
        "69198-0",  # MR Guidance for biopsy of Muscle
        "69199-8",  # MR Guidance for biopsy of Pancreas
        "69200-4",  # MR Guidance for biopsy of Chest Pleura
        "69201-2",  # MR Guidance for biopsy of Salivary gland
        "69202-0",  # MR Guidance for biopsy of Thyroid gland
        "69203-8",  # MR Guidance for biopsy of Breast - left
        "69204-6",  # MR Finger - left WO and W contrast IV
        "69205-3",  # MR Finger - left W contrast IV
        "69206-1",  # MR Finger - left WO contrast
        "69207-9",  # MR Hip - left Arthrogram WO and W contrast
        "69208-7",  # MR Shoulder - left Arthrogram WO and W contrast
        "69209-5",  # MR Wrist - left and Hand - left
        "69210-3",  # MR Lower Extremity Joint Arthrogram
        "69211-1",  # MR Nasal bones
        "69212-9",  # MR Pelvis limited
        "69213-7",  # MR Guidance for biopsy of Breast - right
        "69214-5",  # MR Finger - right WO and W contrast IV
        "69215-2",  # MR Finger - right W contrast IV
        "69216-0",  # MR Finger - right WO contrast
        "69217-8",  # MR Hip - right Arthrogram WO and W contrast
        "69218-6",  # MR Shoulder - right Arthrogram WO and W contrast
        "69219-4",  # MR Wrist - right and Hand - right
        "69220-2",  # MR Skull base WO and W contrast IV
        "69221-0",  # MR Scrotum and testicle W contrast IV
        "69222-8",  # MR Vena cava
        "69223-6",  # MR Unspecified body region WO contrast
        "69226-9",  # RF Guidance for biopsy of Muscle
        "69239-2",  # XR Patella Sunrise
        "69241-8",  # RF Guidance for percutaneous drainage of abscess and placement of drainage catheter of Abdomen
        "69242-6",  # RF Guidance for percutaneous drainage of abscess and placement of drainage catheter of Appendix
        "69243-4",  # RF Guidance for percutaneous drainage of abscess and placement of drainage catheter of Lung
        "69244-2",  # RF Guidance for percutaneous drainage of abscess and placement of drainage catheter of Pelvis
        "69254-1",  # XR Ankle - right 3 Views W standing
        "69255-8",  # XR Knee - right Sunrise and (Tunnel W standing)
        "69256-6",  # XR Knee - right Sunrise
        "69257-4",  # XR Lower extremity - right 2 Views
        "69258-2",  # XR Lower extremity - right AP and Lateral
        "69260-8",  # XR Patella - right Single view
        "69261-6",  # XR Patella - right 3 Views
        "69262-4",  # XR Shoulder - right AP and Grashey and Axillary
        "69263-2",  # XR Wrist - right PA W clenched fist
        "69264-0",  # XR Sacrum Views W standing
        "69265-7",  # XR Shoulder 4 Views
        "69266-5",  # XR Shoulder AP and Y
        "69267-3",  # XR Shoulder Grashey and Axillary and Y
        "69269-9",  # XR Skull AP
        "69270-7",  # XR Skull PA
        "69271-5",  # XR Skull PA and Lateral and Waters and Towne
        "69272-3",  # RF Small bowel Views W contrast via ileostomy
        "69273-1",  # XR Spine thoracolumbar junction 2 Views
        "69274-9",  # XR Thoracic spine 2 Views W standing
        "69275-6",  # XR Thoracic spine Views W standing
        "69302-8",  # XR Wrist Single view W clenched fist
        "69303-6",  # XR Wrist Ulnar deviation and Radial deviation
        "69304-4",  # XR Wrist Ulnar deviation Views
        "69305-1",  # XR Zygomatic arch 2 Views
        "69306-9",  # RF Guidance for aspiration of cyst of Bone
        "69307-7",  # XR Ankle - left Single view
        "69308-5",  # XR Elbow - left Single view
        "69309-3",  # XR Foot - left Single view
        "69310-1",  # XR Hand - left Single view
        "69311-9",  # XR Calcaneus - left Single view
        "69312-7",  # XR Humerus - left Single view
        "69313-5",  # XR Tibia and Fibula - left Single view
        "69314-3",  # XR Ankle - right Single view
        "69315-0",  # XR Elbow - right Single view
        "69316-8",  # XR Foot - right Single view
        "69317-6",  # XR Radius and Ulna - right Single view
        "69318-4",  # XR Hand - right Single view
        "69319-2",  # XR Calcaneus - right Single view
        "69320-0",  # XR Humerus - right Single view
        "69321-8",  # XR Tibia and Fibula - right Single view
        "70918-8",  # RF Guidance for injection of Cervical spine
        "70919-6",  # RF Guidance for injection of Lumbar spine
        "70920-4",  # RF Guidance for injection of Thoracic spine
        "70921-2",  # CT Guidance for nerve block of Cervical spine
        "70922-0",  # CT Guidance for nerve block of Thoracic spine
        "70923-8",  # RF Guidance for percutaneous vertebroplasty of Cervical spine
        "70924-6",  # RF Guidance for percutaneous vertebroplasty of Lumbar spine
        "70925-3",  # RF Guidance for percutaneous vertebroplasty of Thoracic spine
        "70931-1",  # CT Thoracic spine W contrast intradisc
        "70933-7",  # RF Thoracic spine Views W contrast intradisc
        "72238-9",  # MR Toes - right WO and W contrast IV
        "72239-7",  # MR Toes - right WO contrast
        "72240-5",  # MR Toes - right W contrast IV
        "72241-3",  # MR Toes - left WO and W contrast IV
        "72242-1",  # MR Toes - left WO contrast
        "72243-9",  # MR Toes - left W contrast IV
        "72244-7",  # MR Pelvis Endorectal WO and W contrast IV
        "72245-4",  # MR Pelvis Defecography W contrast PR
        "72246-2",  # MR Abdomen and Pelvis W contrast PO and WO and W contrast IV
        "72247-0",  # MR Abdomen and Pelvis W contrast PO and WO contrast IV
        "72248-8",  # MRCP Abdomen WO and W contrast IV
        "72249-6",  # CT Facial bones WO contrast
        "72250-4",  # CT Small bowel W contrast PO and W contrast IV
        "72251-2",  # CT Pulmonary arteries for pulmonary embolus
        "72252-0",  # CT Chest and Abdomen and Pelvis WO and W contrast IV
        "72253-8",  # CT Chest and Abdomen and Pelvis WO contrast
        "72254-6",  # CT Chest and Abdomen and Pelvis W contrast IV
        "72256-1",  # XR Abdomen Views for motility W radioopaque markers
        "72531-7",  # CT Colon and Rectum W contrast IV and W air contrast PR
        "72539-0",  # RF Guidance for denervation of Peripheral nerve
        "72540-8",  # RF Guidance for denervation of Spine facet joint
        "72541-6",  # RF Guidance for denervation of Spine Cervical Facet Joint
        "72542-4",  # RF Guidance for denervation of Lumbar Spine Facet Joint
        "72543-2",  # RF Guidance for denervation of Thoracic spine intercostal nerve
        "72544-0",  # RF Guidance for percutaneous device removal of nephrostomy tube of Kidney - bilateral-- W contrast
        "72549-9",  # RF Guidance for removal of tunneled CV catheter
        "72552-3",  # RF Guidance for kyphoplasty of Lumbar spine
        "72553-1",  # RF Guidance for kyphoplasty of Thoracic spine
        "72554-9",  # RF Guidance for trigger point injection of Muscle
        "72876-6",  # XR Surgical specimen Views
        "75669-2",  # RF Guidance for biopsy of Bone marrow
        "75670-0",  # RF Lumbar spine epidural space Views W contrast epidural
        "75746-8",  # CT Guidance for drainage of abscess and placement of chest tube of Pleural space - bilateral
        "75747-6",  # RF Guidance for drainage of abscess and placement of chest tube of Pleural space - bilateral
        "75748-4",  # CT Guidance for fluid aspiration of Cervical spine Intervertebral disc
        "75749-2",  # RF Guidance for fluid aspiration of Intervertebral disc
        "75750-0",  # RF Guidance for biopsy of Intervertebral disc
        "75751-8",  # RF Guidance for drainage of abscess and placement of chest tube of Pleural space - left
        "75752-6",  # CT Guidance for drainage of abscess and placement of chest tube of Pleural space - left
        "75816-9",  # RF Spine.thoracic epidural space Views W contrast epidural
        "75817-7",  # RF Guidance for drainage of abscess and placement of chest tube of Pleural space - right
        "75818-5",  # CT Guidance for drainage of abscess and placement of chest tube of Pleural space - right
        "75853-2",  # RF Vagina Views W contrast VG
        "77448-9",  # CT Hindfoot and Midfoot
        "77456-2",  # CT Hindfoot and Midfoot W contrast IV
        "77457-0",  # CT Hindfoot and Midfoot WO and W contrast IV
        "77458-8",  # CT Hindfoot and Midfoot WO contrast
        "77466-1",  # CT Hindfoot - left and Midfoot - left W contrast IV
        "77467-9",  # CT Hindfoot - right and Midfoot - right W contrast IV
        "77468-7",  # CT Hindfoot - left and Midfoot - left WO and W contrast IV
        "77469-5",  # CT Hindfoot - right and Midfoot - right WO and W contrast IV
        "77470-3",  # CT Hindfoot - left and Midfoot - left WO contrast
        "77471-1",  # CT Hindfoot - right and Midfoot - right WO contrast
        "79065-9",  # CT Abdomen and Pelvis 3D post processing WO contrast
        "79066-7",  # CT Abdomen 3D post processing WO contrast
        "79067-5",  # CT Airway WO contrast
        "79068-3",  # CT Chest for screening W contrast IV
        "79069-1",  # CT Colon and Rectum for screening WO contrast IV and W air contrast PR
        "79071-7",  # CT Colon and Rectum WO contrast IV and W air contrast PR
        "79072-5",  # CT Guidance for radiation treatment of Unspecified body region
        "79074-1",  # CT Kidney and Ureter and Urinary bladder 3D post processing WO and W contrast IV
        "79075-8",  # CT Pelvis by reconstruction W contrast IV
        "79076-6",  # CT Pelvis by reconstruction WO contrast
        "79078-2",  # CT Cervical spine by reconstruction W contrast IV
        "79079-0",  # CT Cervical spine by reconstruction WO contrast
        "79080-8",  # CT Lumbar spine by reconstruction W contrast IV
        "79081-6",  # CT Lumbar spine by reconstruction WO contrast
        "79082-4",  # CT Thoracic spine by reconstruction W contrast IV
        "79083-2",  # CT Temporal bone by reconstruction W contrast IV
        "79084-0",  # CT Temporal bone by reconstruction WO contrast
        "79085-7",  # CT Biliary ducts WO and W contrast IV
        "79086-5",  # CT Chest for screening WO contrast
        "79087-3",  # CT Heart and Coronary arteries for calcium scoring WO contrast
        "79088-1",  # CT Heart for congenital disease W contrast IV
        "79089-9",  # CT Heart W contrast IV
        "79091-5",  # CT Thoracic spine by reconstruction WO contrast
        "79093-1",  # CT Unspecified body region 3D post processing
        "79094-9",  # CT Urinary bladder W contrast intra bladder
        "79095-6",  # CT Teeth
        "79096-4",  # CT Chest 3D post processing WO contrast
        "79097-2",  # CT Chest and Abdomen 3D post processing WO contrast
        "79098-0",  # CT Chest and Abdomen and Pelvis 3D post processing WO contrast
        "79099-8",  # CT Pelvis 3D post processing WO contrast
        "79101-2",  # CT Colon and Rectum for screening W air contrast PR
        "79103-8",  # CT Abdomen W contrast IV
        "79349-7",  # XR Spine Lumbar and Sacrum GE 6 Views
        "79350-5",  # XR Abdomen GE 3 Views
        "79351-3",  # XR Cervical spine GE 2 Views
        "79352-1",  # XR Cervical spine GE 6 Views
        "79353-9",  # XR Elbow GE 3 Views
        "79354-7",  # XR Finger GE 2 Views
        "79355-4",  # XR Foot 3 Views W standing
        "79356-2",  # XR Hand 1 or 2 Views
        "79357-0",  # XR Hand GE 3 Views
        "79358-8",  # XR Hip - bilateral GE 4 Views
        "79359-6",  # XR Hip - left GE 2 Views
        "79360-4",  # XR Hip - right GE 2 Views
        "79361-2",  # XR Hip GE 2 Views
        "79362-0",  # XR Humerus GE 2 Views
        "79363-8",  # XR Knee - bilateral AP and Lateral and Merchants and (Views W standing)
        "79364-6",  # XR Knee GE 4 Views
        "79365-3",  # XR Ribs - bilateral GE 3 Views
        "79366-1",  # XR Ribs - unilateral and Chest 2 Views
        "79367-9",  # XR Sacrum and Coccyx GE 2 Views
        "79368-7",  # XR Shoulder - left GE 2 Views
        "79369-5",  # XR Shoulder - right GE 2 Views
        "79370-3",  # XR Shoulder GE 2 Views
        "79371-1",  # XR Spine Lumbar and Sacrum GE 2 Views
        "79372-9",  # XR Spine Lumbar and Sacrum GE 4 Views
        "79373-7",  # XR Toe GE 2 Views
        "80495-5",  # MR Mediastinum WO contrast
        "80496-3",  # MR Unspecified body region 3D post processing
        "80497-1",  # MR Guidance for needle localization of Breast - right
        "80498-9",  # MR Guidance for needle localization of Breast - left
        "80499-7",  # MR Whole body WO and W contrast IV
        "80500-2",  # MR Heart W stress and WO contrast
        "80501-0",  # MR Small bowel W contrast PO and WO contrast IV
        "80502-8",  # MRA Abdominal Aorta and Bilateral Runoff Vessels WO and W contrast IV
        "80503-6",  # MR Small bowel W contrast PO and WO and W contrast IV
        "80504-4",  # MR Guidance for biopsy of Unspecified body region
        "80505-1",  # MR Brain for new diagnosis tumor WO and W contrast IV
        "80506-9",  # MR Brain for low grade tumor WO and W contrast IV
        "80507-7",  # MR Brain for high grade tumor WO and W contrast IV
        "80508-5",  # MR Upper extremity.joint Arthrogram
        "80509-3",  # MR Guidance for placement of clip in Unspecified body region
        "80510-1",  # MR Brain for metastasis WO and W contrast IV
        "80511-9",  # MR Brain for postoperative
        "80512-7",  # MR Bone marrow WO contrast
        "80513-5",  # MR Bone marrow W contrast IV
        "80514-3",  # MR Bone marrow WO and W contrast IV
        "80583-8",  # Functional MR Brain for motor function
        "80584-6",  # MR Urethra Endovaginal WO contrast
        "80585-3",  # MR Pelvis Endorectal W contrast IV
        "80990-5",  # Fluoroscopy duration
        "80991-3",  # Fluoroscopy [Energy/mass] dose
        "82123-1",  # MR Guidance for radiation treatment of Unspecified body region
        "82128-0",  # MR Brain and Face WO contrast
        "82129-8",  # MR Brain and Face WO and W contrast IV
        "82130-6",  # MR Face and Neck WO contrast
        "82131-4",  # MR Face and Neck WO and W contrast IV
        "82132-2",  # CT Face and Neck WO and W contrast IV
        "82133-0",  # CT Face and Neck WO contrast
        "82676-8",  # CT Guidance for arthrocentesis of Knee - left
        "82681-8",  # CT Guidance for biopsy of Oral tissue
        "82682-6",  # CT Clavicle - left WO contrast
        "82683-4",  # CT Clavicle - right WO contrast
        "82684-2",  # CT Clavicle WO and W contrast IV
        "82685-9",  # CT Clavicle W contrast IV
        "82686-7",  # CT Clavicle - right W contrast IV
        "82687-5",  # CT Clavicle WO contrast
        "82688-3",  # CT Colon and Rectum WO and W contrast IV and W air contrast PR
        "82689-1",  # CT Small bowel W contrast PO and WO and W contrast IV
        "82690-9",  # CT Head and Cervical spine WO contrast
        "82691-7",  # CT Head and Neck W contrast IV
        "82692-5",  # CT Head and Neck WO contrast
        "82693-3",  # CT Pelvis and Lower extremity W contrast IV
        "82694-1",  # CT Lower extremity - bilateral WO and W contrast IV
        "82695-8",  # CT Pelvis and Lower extremity - bilateral W contrast IV
        "82696-6",  # CT Spine Lumbar and Sacrum W contrast IV
        "82697-4",  # CT Spine Lumbar and Sacrum WO contrast
        "82698-2",  # CT Ribs - left W contrast IV
        "82699-0",  # CT Ribs - left WO contrast
        "82700-6",  # CT Ribs - right W contrast IV
        "82701-4",  # CT Ribs - right WO contrast
        "82702-2",  # CT Ribs - right WO and W contrast IV
        "82703-0",  # CT Sacrum and Coccyx WO and W contrast IV
        "82704-8",  # CT Sacrum and Coccyx W contrast IV
        "82705-5",  # CT Scapula - left WO contrast
        "82706-3",  # CT Scapula - right WO contrast
        "82707-1",  # CT Scapula - left WO and W contrast IV
        "82715-4",  # CT Guidance for arthrocentesis of Knee - right
        "82716-2",  # CT Clavicle - left W contrast IV
        "82717-0",  # CT Ribs - left WO and W contrast IV
        "82718-8",  # CT Scapula - right WO and W contrast IV
        "82742-8",  # CT Head WO and W contrast IV and CT Orbit - bilateral W contrast IV
        "82802-0",  # CT Head WO and W contrast IV and CT Sinuses W contrast IV
        "82803-8",  # CT Head WO and W contrast IV and CT Temporal bone W contrast IV
        "82804-6",  # CT Head WO and W contrast IV and CT Neck W contrast IV
        "8294-1",  # XR Chest Diameter.anterior-posterior
        "8295-8",  # XR Chest Diameter.anterior-posterior W expiration
        "8296-6",  # XR Chest Diameter.anterior-posterior W inspiration
        "83015-8",  # XR Abdomen 2 Views for renal calculus
        "83016-6",  # XR Abdomen GE 3 Views AP and Oblique and Cone
        "83017-4",  # XR Chest View and Abdomen Supine and Upright
        "83018-2",  # XR Ankle 1 or 2 Views
        "83019-0",  # XR Chest and Abdomen and Pelvis View babygram
        "83020-8",  # XR Bones Complete Survey Views
        "83021-6",  # XR Cervical spine 2 or 3 views and (Views W flexion and W extension)
        "83022-4",  # XR Cervical spine 2 or 3 views and (Views W flexion and W extension) and Views oblique
        "83023-2",  # XR Cervical spine 4 or 5 Views
        "83024-0",  # XR Chest 2 Views and Views Lateral-decubitus
        "83025-7",  # XR Coccyx GE 2 Views
        "83026-5",  # XR Elbow 1 or 2 Views
        "83027-3",  # XR Elbow GE 4 Views
        "83028-1",  # XR Cervical and thoracic and lumbar spine GE 2 Views
        "83029-9",  # XR Facial bones and Zygomatic arch 1 or 2 Views
        "83030-7",  # XR Foot 1 or 2 Views
        "83031-5",  # XR Pelvis AP and Hip - bilateral GE 2 Views
        "83032-3",  # XR Hip GE 2 Views preoperative
        "83033-1",  # XR Hip single view during surgery
        "83034-9",  # XR Pelvis and Hip - bilateral GE 2 views for pediatrics
        "83035-6",  # XR Knee 1 or 2 Views during surgery
        "83036-4",  # XR Lower extremity GE 2 Views
        "83037-2",  # XR Lumbar spine Single view during surgery
        "83038-0",  # XR Lumbar spine Greater than 4 views and (Greater than 1 view W R-bending and W L-bending)
        "83039-8",  # XR Mastoid - bilateral GE 3 Views
        "83040-6",  # XR Ribs - unilateral 2 Views
        "83041-4",  # XR Ribs - unilateral 2 Views and Chest Single view
        "83042-2",  # XR Ribs - unilateral 2 Views and Chest AP
        "83043-0",  # XR Sacroiliac joint - bilateral 1 or 2 Views
        "83044-8",  # XR Sacrum GE 2 Views
        "83045-5",  # XR Scapula AP and Lateral
        "83046-3",  # XR Skull LE 3 AP and Lateral Views
        "83047-1",  # XR Sternum GE 2 Views
        "83048-9",  # XR Tibia and Fibula GE 3 Views
        "83049-7",  # XR Upper extremity GE 2 Views
        "83050-5",  # XR Wrist 1 or 2 Views
        "83291-5",  # CT Thumb WO contrast
        "83292-3",  # CT Scapula W contrast
        "83293-1",  # CT Spine Cervical and Spine Lumbar W contrast IV
        "83294-9",  # CT Thoracic and lumbar spine W contrast IV
        "83295-6",  # CT Neck and Superior mediastinum W contrast IV
        "83296-4",  # CT Head W contrast IV and CT Orbit - bilateral WO and W contrast IV
        "83297-2",  # CT Spine Cervical and Spine Lumbar WO and W contrast IV
        "83300-4",  # CT Scapula - bilateral WO and W contrast IV
        "83301-2",  # CT Neck and Superior mediastinum WO and W contrast IV
        "83302-0",  # CT Head and Temporal bone WO contrast
        "83303-8",  # CT Toe WO contrast
        "83304-6",  # CT Cervical and thoracic spine WO contrast
        "83305-3",  # CT Spine Cervical and Spine Lumbar WO contrast
        "83306-1",  # CT Head and Maxillofacial region WO contrast
        "83307-9",  # CT Head and Mandible WO contrast
        "83308-7",  # CT Neck and Superior mediastinum WO contrast
        "83309-5",  # CT Sinuses and Mandible WO contrast
        "83310-3",  # CT Thoracic and lumbar spine WO contrast
        "85040-4",  # CT Unspecified body region 3D printed model
        "85041-2",  # MR Unspecified body region 3D printed model
        "85151-9",  # XR Bone age
        "86372-0",  # RF Kidney and Ureter and Urinary bladder Views W contrast IV
        "86373-8",  # RF AV fistula Views W contrast via additional puncture
        "86376-1",  # RF Biliary ducts Views W contrast via existing catheter
        "86377-9",  # RF Guidance for advancement of feeding tube of Gastrointestinal tract
        "86378-7",  # RF Gastrointestinal tract Views for fistula
        "86379-5",  # RF Small bowel Views for loop diversion
        "86380-3",  # RF Kidney and Ureter and Urinary bladder Views for fistula
        "86381-1",  # RF Colon Screening W air and barium contrast PR
        "86382-9",  # RF Biliary ducts Limited Views during surgery
        "86383-7",  # RF Biliary ducts Views W contrast IV
        "86384-5",  # RF Gallbladder Views W contrast and fatty meal PO
        "86385-2",  # RF Gallbladder Views W contrast PO
        "86386-0",  # RF Gastrointestinal tract upper Views W barium contrast PO
        "86387-8",  # RF Kidney and Ureter and Urinary bladder Views W contrast antegrade
        "86388-6",  # RF Kidney and Ureter and Urinary bladder Views W contrast retrograde
        "86389-4",  # RF Kidney and Ureter and Urinary bladder Views during surgery W contrast retrograde
        "86390-2",  # RF Kidney and Ureter and Urinary bladder Views W contrast via nephrostomy tube
        "86391-0",  # RF AV fistula Views W contrast via existing catheter
        "86392-8",  # RF Kidney and Ureter and Urinary bladder Limited Views W contrast IV
        "86393-6",  # RF Kidney - bilateral and Ureter - bilateral and Urinary bladder Views W contrast retrograde
        "86397-7",  # RF Guidance for drainage and placement of suprapubic catheter of Urinary bladder
        "86398-5",  # RF Cerebral cisterns Views W contrast IT
        "86399-3",  # RF Guidance for Views and Guidance for injection of non-vascular shunt of Unspecified body region
        "86400-9",  # RF Guidance for placement of needle in Unspecified body region
        "86401-7",  # RF Urinary bladder Views W contrast intra bladder
        "86402-5",  # RF Shoulder Arthrogram limited
        "86403-3",  # RF Guidance for placement of catheter in Fallopian tube
        "86404-1",  # RF Guidance for fluid aspiration of Urinary bladder
        "86405-8",  # RF Guidance for exchange of tube of Unspecified body region
        "86406-6",  # RF Unspecified body region Less than 1 hour Views during surgery
        "86407-4",  # RF Guidance of Unspecified body region
        "86408-2",  # RF Pelvis Views for urinary pouch
        "86409-0",  # RF Rectum Views for rectal dysfunction W barium contrast PR
        "86410-8",  # RF Pharynx and Cervical esophagus Views W barium contrast PO
        "86411-6",  # RF Posterior fossa - bilateral Views W contrast IT
        "86413-2",  # RF Guidance for placement of long feeding tube in Gastrointestinal tract
        "86420-7",  # RF Gastrointestinal tract upper Views W air contrast PO and W barium contrast PO
        "86425-6",  # RF Guidance for manometry of Kidney
        "86427-2",  # RF Upper gastrointestinal tract and Small bowel Views W air contrast PO and W barium contrast PO
        "86430-6",  # RF Posterior fossa - unilateral Views W contrast IT
        "86436-3",  # RF Guidance for treatment of Fistula-- W contrast intra fistula
        "86437-1",  # RF Fistula Diagnostic W contrast intra fistula
        "86438-9",  # RF Guidance for check of feeding tube of Gastrointestinal tract upper
        "86439-7",  # RF Cerebral sinuses Views W contrast IV
        "86440-5",  # RF Seminal vesicle Views W contrast intra seminal vesicle
        "86441-3",  # RF Guidance for manometry of Kidney and Ureter and Urinary bladder
        "86443-9",  # RF Ureter Views W contrast intra ureter
        "86956-0",  # CT Heart WO contrast IV and CT Heart for left ventricular function W contrast IV
        "86957-8",  # CT Salivary gland WO and W contrast IV
        "86958-6",  # CT Neck and Chest WO and W contrast IV
        "86959-4",  # CT Cervical and thoracic spine WO and W contrast IV
        "86966-9",  # CT Salivary gland WO contrast
        "86967-7",  # CT Foot - bilateral WO contrast
        "86968-5",  # CT Hand - bilateral W contrast IV
        "86969-3",  # CT Shoulder - bilateral W contrast IV
        "86970-1",  # CT Sacrum and Coccyx WO contrast
        "86972-7",  # CT Head and Neck WO and W contrast IV
        "86973-5",  # CT Foot - bilateral W contrast IV
        "86974-3",  # CT Thoracic and lumbar spine WO and W contrast IV
        "86975-0",  # CT Heart for left ventricular function W contrast IV
        "86977-6",  # CT Head and Temporal bone W contrast IV
        "86978-4",  # CT Head and Sinuses W contrast IV
        "86979-2",  # CT Pelvis and Hip - bilateral WO contrast
        "86984-2",  # CT Cervical and thoracic and lumbar spine W contrast IV
        "86985-9",  # CT Cervical and thoracic spine W contrast IV
        "86986-7",  # CT Neck and Chest W contrast IV
        "86987-5",  # CT Cervical and thoracic and lumbar spine WO contrast
        "86988-3",  # CT Orbit and Face WO contrast
        "86989-1",  # CT Head and Orbit - bilateral W contrast IV
        "86990-9",  # CT Head and Orbit - bilateral WO contrast
        "86991-7",  # CT Head and Maxillofacial region and Cervical spine WO contrast
        "86992-5",  # CT Head and Sinuses WO contrast
        "87279-6",  # CT Chest for screening
        "87859-5",  # CT Thoracic Aorta WO and W contrast IV
        "87860-3",  # CT Thoracic Aorta WO contrast
        "87861-1",  # CT Thoracic and abdominal aorta WO and W contrast IV
        "87862-9",  # CT Abdomen WO and CT Abdomen and Pelvis W contrast IV
        "87863-7",  # CT Abdomen WO and CT Chest and Abdomen W contrast IV
        "87864-5",  # CT Abdomen WO and CT Chest and Abdomen and Pelvis W contrast IV
        "87865-2",  # CT Abdomen and Pelvis WO and CT Chest and Abdomen and Pelvis W contrast IV
        "87866-0",  # CT Kidney and Ureter and Urinary bladder WO and W contrast IV
        "87867-8",  # CT Lumbar spine by reconstruction
        "87868-6",  # CT Lumbar spine by reconstruction WO and W contrast IV
        "87869-4",  # CT Chest and Abdomen and Pelvis
        "87870-2",  # CT Cervical spine to Coccyx WO and W contrast IV
        "87871-0",  # CT Clavicle - left
        "87872-8",  # CT Clavicle - right
        "87873-6",  # CT Lung parenchyma WO and W contrast IV
        "87874-4",  # CT Mediastinum W contrast IV
        "87875-1",  # CT Thoracic spine by reconstruction
        "87876-9",  # CT Thymus gland
        "87877-7",  # CT Neck and Chest WO contrast
        "87878-5",  # CT Knee - bilateral Arthrogram
        "87879-3",  # CT Lower leg - bilateral WO contrast
        "87880-1",  # CT Thigh - bilateral W contrast IV
        "87881-9",  # CT Thigh - bilateral WO contrast
        "87882-7",  # CT Lower leg - left
        "87883-5",  # CT Upper extremity - bilateral WO and W contrast IV
        "87884-3",  # CT Shoulder - bilateral Arthrogram
        "87885-0",  # CT Upper arm - bilateral WO contrast
        "87886-8",  # CT Finger fifth - left WO contrast
        "87887-6",  # CT Finger fourth - left W contrast IV
        "87888-4",  # CT Finger second - left WO contrast
        "87889-2",  # CT Thumb - left WO contrast
        "87890-0",  # CT Finger fifth - right WO contrast
        "87891-8",  # CT Finger fourth - right WO contrast
        "87892-6",  # CT Finger second - right WO contrast
        "87893-4",  # CT Finger third - right WO contrast
        "87894-2",  # CT Thumb - right WO contrast
        "87895-9",  # CT Finger WO contrast
        "87896-7",  # CT Teeth W contrast IV
        "87897-5",  # CT Head and Pituitary and Sella turcica W contrast IV
        "87898-3",  # CT Teeth.maxilla WO contrast
        "87899-1",  # CT Teeth.mandible WO contrast
        "87900-7",  # CT Mastoid W contrast IV
        "87901-5",  # CT Temporal bone - bilateral WO and W contrast IV
        "87902-3",  # CT Temporal bone - bilateral W contrast IV
        "87903-1",  # CT Temporal bone - bilateral WO contrast
        "87904-9",  # CT Temporomandibular joint - bilateral WO contrast
        "87906-4",  # CT Maxillofacial region - right W contrast IV
        "87908-0",  # CT Head and Maxillofacial region W contrast IV
        "87909-8",  # CT Temporomandibular joint Arthrogram
        "87910-6",  # CT Head and Sinuses WO and W contrast IV
        "87911-4",  # CT Head and Maxillofacial region WO and W contrast IV
        "87912-2",  # CT Sinuses and Orbit WO contrast
        "87913-0",  # CT Pelvis by reconstruction
        "87914-8",  # CT Pelvis bones WO and W contrast IV
        "87916-3",  # CT Guidance for injection of cyst of Unspecified body region
        "87917-1",  # CT Pelvis bones WO contrast
        "87918-9",  # CT Parathyroid gland WO and W contrast IV
        "87919-7",  # CT Pelvis bones
        "87920-5",  # CT Pelvis bones W contrast IV
        "87921-3",  # CT Trachea WO contrast
        "87922-1",  # CT Cervical and thoracic spine W contrast IT
        "88316-5",  # CT Guidance for biopsy of Spinal cord
        "88317-3",  # CT Guidance for fluid aspiration of Chest
        "88319-9",  # CT Abdomen and Pelvis and Lower extremity - bilateral W contrast IV
        "88321-5",  # CT Guidance for stereotactic localization of Unspecified body region
        "88323-1",  # CT Guidance for biopsy of Kidney - right
        "88324-9",  # CT Guidance for biopsy of Lung - left
        "88325-6",  # CT Guidance for biopsy of Kidney - left
        "88526-9",  # CT Guidance for biopsy of Lung - right
        "88831-3",  # RF Kidney - right and Ureter Views W contrast retrograde intra ureter
        "88832-1",  # RF Kidney - left and Ureter Views W contrast retrograde intra ureter
        "88833-9",  # RF Kidney - bilateral and Ureter Views W contrast retrograde intra ureter
        "88834-7",  # RF Guidance for dilation of nephrostomy tract, ureter, or urethra
        "89283-6",  # CT Neck+Chest+Abdomen+Pelvis W contrast IV
        "89284-4",  # MR Cervical and thoracic spine W contrast IV
        "89602-7",  # CT Guidance for aspiration of cyst of Kidney - left
        "89603-5",  # CT Guidance for aspiration of cyst of Kidney - right
        "89604-3",  # CT Guidance for aspiration of cyst of Kidney - bilateral
        "89605-0",  # CT Guidance for ablation of tissue of Kidney - right
        "89606-8",  # CT Guidance for ablation of tissue of Kidney - left
        "89607-6",  # CT Guidance for fluid aspiration of Lung - right
        "89608-4",  # CT Guidance for fluid aspiration of Lung - left
        "89609-2",  # CT Guidance for fluid aspiration of Pericardial space
        "89610-0",  # CT Guidance for placement of catheter in Peritoneal space
        "89611-8",  # CT Guidance for fluid aspiration of Pleural space - right
        "89612-6",  # CT Guidance for fluid aspiration of Pleural space - left
        "89613-4",  # CT Guidance for drainage and placement of drainage catheter of Abdomen-- WO contrast
        "89614-2",  # CT Guidance for biopsy of Kidney-- WO contrast
        "89615-9",  # CT Guidance for drainage and placement of drainage catheter of Abdomen-- W contrast IV
        "89616-7",  # CT Guidance for aspiration of cyst of Pancreas-- WO contrast
        "89617-5",  # CT Guidance for aspiration of cyst of Kidney-- W contrast IV
        "89618-3",  # CT Guidance for aspiration of cyst of Kidney-- WO contrast
        "89620-9",  # CT Guidance for biopsy of Abdomen-- W contrast IV
        "89621-7",  # CT Guidance for biopsy of Kidney-- W contrast IV
        "89623-3",  # CT Guidance for drainage and placement of drainage catheter of Peritoneal space
        "89624-1",  # CT Guidance for drainage of abscess and placement of drainage catheter of Peritoneal space
        "89625-8",  # CT Guidance for aspiration of cyst of Kidney
        "89627-4",  # CT Guidance for aspiration of cyst of Ileum - right
        "89628-2",  # CT Guidance for aspiration of cyst of Ileum - left
        "89629-0",  # CT Guidance for aspiration of cyst of Lung - left
        "89630-8",  # CT Guidance for aspiration of cyst of Lung - right
        "89695-1",  # CT Guidance for drainage and placement of drainage catheter of Pelvis-- WO contrast
        "89696-9",  # CT Guidance for drainage and placement of drainage catheter of Pelvis-- W contrast IV
        "89697-7",  # CT Guidance for drainage of pseudocyst and placement of drainage catheter of Pancreas
        "89698-5",  # CT Guidance for injection of Ankle - right
        "89699-3",  # CT Guidance for injection of Ankle - left
        "89700-9",  # CT Guidance for injection of Hip - right
        "89701-7",  # CT Guidance for injection of Hip - left
        "89702-5",  # CT Guidance for injection of Shoulder - bilateral
        "89703-3",  # CT Guidance for injection of Shoulder - left
        "89704-1",  # CT Guidance for injection of Shoulder - right
        "89705-8",  # CT Guidance for injection of Wrist - left
        "89706-6",  # CT Guidance for injection of Knee - bilateral
        "89707-4",  # CT Guidance for injection of Knee - right
        "89708-2",  # CT Guidance for injection of Knee - left
        "89709-0",  # CT Guidance for greater than 2 levels for injection of Spine facet joint
        "89710-8",  # CT Guidance for 2 levels injection of Spine facet joint
        "89711-6",  # CT Guidance for 1 level injection of Spine facet joint
        "89713-2",  # CT Upper extremity joint - right Arthrogram
        "89715-7",  # CT Lower extremity joint - right Arthrogram
        "89716-5",  # CT Lower extremity joint - left Arthrogram
        "89717-3",  # CT Guidance for stereotactic localization of Unspecified body region-- WO and W contrast IV
        "89718-1",  # CT Guidance for stereotactic localization of Unspecified body region-- W contrast IV
        "89719-9",  # CT Guidance for drainage of abscess and placement of drainage catheter of Lung - right
        "89720-7",  # CT Guidance for drainage of abscess and placement of drainage catheter of Lung - left
        "89721-5",  # CT Guidance for drainage of abscess and placement of drainage catheter of Retroperitoneum
        "89827-0",  # CT Spine Lumbar and Sacrum WO and W contrast IV
        "89828-8",  # CT Guidance for superficial biopsy of Muscle
        "89829-6",  # CT Guidance for biopsy of Retroperitoneum-- WO contrast
        "89832-0",  # CT Guidance for deep biopsy of Tissue
        "89833-8",  # CT Unspecified body region by reconstruction
        "89834-6",  # CT Clavicle - bilateral WO contrast
        "89835-3",  # CT Brachial plexus W contrast IV
        "89836-1",  # CT Brachial plexus WO contrast
        "89837-9",  # CT Temporal bone - left WO and W contrast IV
        "89838-7",  # CT Temporal bone - right WO and W contrast IV
        "89839-5",  # CT Guidance for biopsy of Sternum
        "89840-3",  # CT Lumbosacral plexus WO contrast
        "89844-5",  # CT Head and Temporal bone WO and W contrast IV
        "89845-2",  # CT Head and Orbit - bilateral WO and W contrast IV
        "89846-0",  # CT Midfoot - left and Forefoot - left WO and W contrast IV
        "89847-8",  # CT Midfoot - right and Forefoot - right
        "89848-6",  # CT Midfoot - right WO and W contrast IV
        "89849-4",  # CT Finger - right WO contrast
        "89850-2",  # CT Finger - left WO contrast
        "89852-8",  # CT Unspecified body region limited W contrast IV
        "89853-6",  # CT Unspecified body region limited WO contrast
        "89854-4",  # CT Guidance for drainage of abscess and placement of drainage catheter of Perirenal space - left
        "89855-1",  # CT Guidance for drainage of abscess and placement of drainage catheter of Perirenal space - right
        "89856-9",  # CT Guidance for stereotactic localization of Unspecified body region-- WO contrast
        "89857-7",  # CT Guidance for biopsy of Pleura - right
        "89858-5",  # CT Guidance for biopsy of Pleura - left
        "89859-3",  # CT Guidance for transrectal drainage of abscess of Pelvis
        "89860-1",  # CT Chest W inspiration and expiration
        "89925-2",  # CT Pelvis and Lower extremity - bilateral WO and W contrast IV
        "89928-6",  # CT Guidance for fluid aspiration of Lumbar spine Intervertebral disc
        "89929-4",  # CT Guidance for fluid aspiration of Intervertebral disc
        "89930-2",  # CT Guidance for radiofrequency ablation of Bone
        "89931-0",  # CT Guidance for drainage and placement of drainage catheter of Perirectal region
        "89932-8",  # CT Guidance for deep placement of needle of Unspecified body region
        "89952-6",  # CT Guidance for arthrocentesis of Sacroiliac joint - right
        "89953-4",  # CT Guidance for arthrocentesis of Shoulder - right
        "89954-2",  # CT Guidance for arthrocentesis of Shoulder - left
        "89955-9",  # CT Guidance for arthrocentesis of Hip - bilateral
        "89956-7",  # CT Guidance for arthrocentesis of Hip - left
        "89957-5",  # CT Guidance for arthrocentesis of Hip - right
        "89958-3",  # CT Guidance for cryoablation of Pelvis
        "89960-9",  # CT Guidance for drainage of abscess and placement of drainage catheter of Kidney - right
        "89961-7",  # CT Guidance for drainage of abscess and placement of drainage catheter of Kidney - left
        "89962-5",  # CT Guidance for radiofrequency ablation of Lung
        "90049-8",  # CT Guidance for placement of chest tube in Pleural space - left
        "90050-6",  # CT Guidance for placement of chest tube in Pleural space - bilateral
        "90051-4",  # CT Guidance for placement of chest tube in Pleural space - right
        "90307-0",  # CT Guidance for injection of Foot joint - right
        "90308-8",  # CT Guidance for needle localization of Thoracic spine
        "90310-4",  # CT Guidance for drainage and placement of drainage catheter of Retroperitoneum-- WO contrast
        "90311-2",  # CT Guidance for percutaneous replacement of drainage catheter of Unspecified body region
        "90313-8",  # CT Guidance for drainage and placement of chest tube of Pleural space - left
        "90315-3",  # CT Guidance for deep biopsy of Soft tissue
        "90316-1",  # CT Guidance for superficial biopsy of Soft tissue
        "90317-9",  # CT Guidance for drainage and placement of drainage catheter of Lower extremity - left
        "90318-7",  # CT Guidance for drainage and placement of drainage catheter of Lower extremity - right
        "90334-4",  # CT Guidance for injection of Spine Thoracic Facet Joint
        "90335-1",  # CT Guidance for injection of Lumbar Spine Facet Joint
        "90336-9",  # CT Guidance for injection of Muscle
        "90372-4",  # CT Guidance for injection of Tendon
        "90373-2",  # CT Guidance for injection of Tendon or ligament
        "91523-1",  # MR Chest and Abdomen and Pelvis W contrast IV
        "91524-9",  # MR Chest and Abdomen and Pelvis WO and W contrast IV
        "91525-6",  # MR Chest and Abdomen and Pelvis WO contrast
        "91561-1",  # MR Cervical and thoracic and lumbar spine W contrast IV
        "91593-4",  # MR Brain and Orbit - bilateral WO contrast
        "91594-2",  # MR Sacrum and Sacroiliac joint W contrast IV
        "91595-9",  # MR Sacrum and Sacroiliac joint WO and W contrast IV
        "91596-7",  # MR Sacrum and Sacroiliac joint WO contrast
        "91597-5",  # MR Toe WO and W contrast IV
        "91598-3",  # XR Knee GE 2 Views
        "91715-3",  # MR Spine Lumbar and Sacrum W contrast IV
        "91716-1",  # MR Spine Lumbar and Sacrum WO and W contrast IV
        "91717-9",  # MR Spine Lumbar and Sacrum WO contrast
        "91718-7",  # MR Unspecified body region Post mortem
        "91719-5",  # CT Unspecified body region Post mortem
        "91720-3",  # XR Head to Abdomen Views for shunt patency
        "92025-6",  # CT Head and Cervical spine W contrast IV
        "92567-7",  # CT Guidance for percutaneous drainage and placement of drainage catheter of Unspecified body region
        "92569-3",  # CT Guidance for drainage and placement of chest tube of Pleural space - bilateral
        "92677-4",  # XR Pelvis and Hip GE 4 Views
        "92916-6",  # CT Guidance for aspiration of Retroperitoneum
        "92917-4",  # CT Guidance for aspiration of Kidney - right
        "92918-2",  # CT Guidance for aspiration of Kidney - left
        "92919-0",  # CT Guidance for 2 levels injection of Spine Lumbar and Sacrum
        "92920-8",  # CT Guidance for 1 level injection of Spine Lumbar and Sacrum
        "92921-6",  # CT Guidance for 1 level injection of Cervical and thoracic spine
        "92922-4",  # CT Guidance for intrathecal injection of Lumbar spine
        "92923-2",  # CT Guidance for aspiration of Kidney
        "92924-0",  # CT Guidance for aspiration of Abdomen
        "92925-7",  # CT Guidance for injection of Spine cervical and thoracic epidural space
        "92926-5",  # CT Guidance for radiation treatment of Unspecified body region-- WO and W contrast IV
        "92928-1",  # CT Guidance for injection of Spine lumbar and Sacrum epidural space
        "93129-5",  # XR Radius Bone development stage
        "93130-3",  # XR Trapezoid Bone development stage
        "93131-1",  # XR Trapezium Bone development stage
        "93132-9",  # XR Scaphoid Bone development stage
        "93133-7",  # XR Lunate Bone development stage
        "93134-5",  # XR Triquetrum Bone development stage
        "93135-2",  # XR Hamate Bone development stage
        "93136-0",  # XR Capitate Bone development stage
        "93137-8",  # XR Distal phalanx of thumb Bone development stage
        "93138-6",  # XR Distal phalanx of fifth finger Bone development stage
        "93139-4",  # XR Distal phalanx of third finger Bone development stage
        "93140-2",  # XR Middle phalanx of third finger Bone development stage
        "93141-0",  # XR Middle phalanx of fifth finger Bone development stage
        "93142-8",  # XR Proximal phalanx of fifth finger Bone development stage
        "93143-6",  # XR Proximal phalanx of third finger Bone development stage
        "93144-4",  # XR Proximal phalanx of thumb Bone development stage
        "93145-1",  # XR Fifth metacarpal Bone development stage
        "93146-9",  # XR Third metacarpal Bone development stage
        "93147-7",  # XR First metacarpal Bone development stage
        "93148-5",  # XR Ulna Bone development stage
        "93189-9",  # XR Wrist and Hand Total skeletal maturity score
        "93603-9",  # CT Head and Cervical spine WO and W contrast IV
        "93605-4",  # XR Skull to Coccyx 2 or 3 Views
        "93606-2",  # XR Skull to Coccyx 4 or 5 Views
        "93607-0",  # XR Skull to Coccyx GE 6 Views
        "94088-2",  # MR Thoracic and lumbar spine WO and W contrast
        "94089-0",  # MR Chest WO and W contrast IV and MRA Chest W contrast IV
        "94679-8",  # XR Chest Single View and Abdomen Supine and Upright and Lateral-decubitus
        "94682-2",  # XR Calcaneus GE 2 Views
        "94683-0",  # XR Pelvis and Hip - unilateral GE 2 Views
        "94684-8",  # XR Spine Lumbar and Sacrum GE 6 Views W right bending and W left bending
        "94685-5",  # XR Ribs - unilateral GE 3 Views and Chest PA
        "95558-3",  # CT attenuation of adrenal mass
        "95610-2",  # XR Teeth Complete Views
        "95611-0",  # XR Teeth Occlusal Views
        "95923-9",  # MR Heart W stress and W contrast IV
        "95924-7",  # CT Skeletal system Multisection for bone density
        "95925-4",  # CT Skeletal system.axial Multisection for bone density
        "95926-2",  # CT Skeletal system.peripheral Multisection for bone density
        "95927-0",  # CT Radius Multisection for bone density
        "95928-8",  # CT Wrist Multisection for bone density
        "95929-6",  # CT Calcaneus Multisection for bone density
    }


class DxaDualEnergyXrayAbsorptiometryScan(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a diagnostic study for a dual-energy x-ray absorptiometry (DXA) scan.

    **Data Element Scope:** This value set may use a model element related to Diagnostic Study.

    **Inclusion Criteria:** Includes concepts that represent a diagnostic study for bone density using DXA scans of the femur, radius, ulna, lumbar spine, hip, calcaneus and skeletal system.

    **Exclusion Criteria:** Excludes order only codes.

    ** Used in:** CMS249v4
    """

    VALUE_SET_NAME = "DXA (Dual energy Xray Absorptiometry) Scan"
    OID = "2.16.840.1.113883.3.464.1003.113.12.1051"
    DEFINITION_VERSION = "20180310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "24701-5",  # DXA Femur [Mass/Area] Bone density
        "24890-6",  # DXA Radius and Ulna [Mass/Area] Bone density
        "24966-4",  # DXA Lumbar spine [Mass/Area] Bone density
        "38261-4",  # DXA Hip [Mass/Area] Bone density
        "38262-2",  # DXA Calcaneus [Mass/Area] Bone density
        "38263-0",  # DXA Femur [T-score] Bone density
        "38264-8",  # DXA Hip [T-score] Bone density
        "38265-5",  # DXA Radius and Ulna [T-score] Bone density
        "38266-3",  # DXA Calcaneus [T-score] Bone density
        "38267-1",  # DXA Lumbar spine [T-score] Bone density
        "38268-9",  # DXA Skeletal system Views for bone density
        "46278-8",  # DXA Hip - left [Mass/Area] Bone density
        "46279-6",  # DXA Hip - right [Mass/Area] Bone density
        "46383-6",  # DXA Bone [Mass/Area] Bone density
    }


class DexaDualEnergyXrayAbsorptiometry_BoneDensityForUrologyCare(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a diagnostic study measuring bone density by x-ray studies.

    **Data Element Scope:** This value set may use a model element related to Diagnostic Study.

    **Inclusion Criteria:** Includes concepts that represent a diagnostic study of a dual-energy X-ray absorptiometry (DXA, DEXA) with 1 or more axial sites, axial skeleton (hips, pelvis, spine) or 1 or more appendicular skeleton sites (radius, wrist, heel).

    **Exclusion Criteria:** No Exclusions.

    ** Used in:** CMS645v5
    """

    VALUE_SET_NAME = "DEXA Dual Energy Xray Absorptiometry, Bone Density for Urology Care"
    OID = "2.16.840.1.113762.1.4.1151.38"
    DEFINITION_VERSION = "20170812"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "38265-5",  # DXA Radius and Ulna [T-score] Bone density
        "38268-9",  # DXA Skeletal system Views for bone density
    }


__exports__ = get_overrides(locals().copy())
