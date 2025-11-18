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
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "18188000",   # Ophthalmoscopy under general anesthesia (procedure)
        "20067007",   # Ocular fundus photography (procedure)
        "21593001",   # Ophthalmodynamography (procedure)
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
        "3047001",    # Kowa fundus photography (procedure)
        "308110009",  # Direct fundoscopy following mydriatic (procedure)
        "30842004",   # Ophthalmoscopy with medical evaluation, extended, with fundus photography (procedure)
        "314971001",  # Camera fundoscopy (procedure)
        "314972008",  # Indirect fundoscopy following mydriatic (procedure)
        "36844005",   # Ophthalmoscopy with medical evaluation, extended, with ophthalmodynamometry (procedure)
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
        "53524009",   # Ophthalmoscopy (procedure)
        "56072006",   # Ophthalmoscopy with medical evaluation, extended, for retinal detachment mapping (procedure)
        "56204000",   # Ophthalmodynamometry (procedure)
        "6615001",    # Electroretinography (procedure)
        "700070005",  # Optical coherence tomography of retina (procedure)
        "722161008",  # Diabetic retinal eye exam (procedure)
    }
    

__exports__ = (RetinalOrDilatedEyeExam,)