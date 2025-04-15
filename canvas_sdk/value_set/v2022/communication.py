from canvas_sdk.value_set._utilities import get_overrides

from ..value_set import ValueSet


class LevelOfSeverityOfRetinopathyFindings(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for diagnoses of the level of severity of retinopathy.

    **Data Element Scope:** This value set may use a model element related to Diagnosis or Communication.

    **Inclusion Criteria:** Includes concepts that represent a diagnosis of mild, moderate, severe, or very severe non-proliferative and proliferative diabetic retinopathy.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS142v10
    """

    VALUE_SET_NAME = "Level of Severity of Retinopathy Findings"
    OID = "2.16.840.1.113883.3.526.3.1283"
    DEFINITION_VERSION = "20210209"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "59276001",  # Proliferative retinopathy due to diabetes mellitus (disorder)
        "312903003",  # Mild nonproliferative retinopathy due to diabetes mellitus (disorder)
        "312904009",  # Moderate nonproliferative retinopathy due to diabetes mellitus (disorder)
        "312905005",  # Severe nonproliferative retinopathy due to diabetes mellitus (disorder)
        "399876000",  # Very severe nonproliferative retinopathy due to diabetes mellitus (disorder)
    }


class MacularEdemaFindingsPresent(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for diagnoses to identify the presence of macular edema.

    **Data Element Scope:** This value set may use a model element related to Diagnosis.

    **Inclusion Criteria:** Includes concepts that represent a diagnosis of macular edema.

    **Exclusion Criteria:** Excludes concepts that represent a diagnosis of non-macular edema.

    ** Used in:** CMS142v10
    """

    VALUE_SET_NAME = "Macular Edema Findings Present"
    OID = "2.16.840.1.113883.3.526.3.1320"
    DEFINITION_VERSION = "20210209"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "37231002",  # Macular retinal edema (disorder)
        "193350004",  # Advanced maculopathy due to diabetes mellitus (disorder)
        "193387007",  # Cystoid macular edema (disorder)
        "232020009",  # Disorder of macula due to diabetes mellitus (disorder)
        "312911008",  # Clinically significant macular edema (disorder)
        "312912001",  # Macular edema due to diabetes mellitus (disorder)
        "312920004",  # Postoperative cystoid macular edema (disorder)
        "312921000",  # Autosomal dominant cystoid macular edema (disorder)
        "312922007",  # Uveitis related cystoid macular edema (disorder)
        "314010006",  # Diffuse exudative maculopathy due to diabetes mellitus (disorder)
        "314011005",  # Focal exudative maculopathy due to diabetes mellitus (disorder)
        "314014002",  # Ischemic maculopathy due to diabetes mellitus (disorder)
        "314015001",  # Mixed maculopathy due to diabetes mellitus (disorder)
        "399864000",  # Macular edema not clinically significant due to diabetes mellitus (disorder)
        "399874002",  # High risk proliferative retinopathy with clinically significant macula edema due to diabetes mellitus (disorder)
        "399875001",  # Non-high-risk proliferative retinopathy with clinically significant macular edema due to diabetes mellitus (disorder)
        "420486006",  # Exudative maculopathy due to type 1 diabetes mellitus (disorder)
        "421779007",  # Exudative maculopathy due to type 2 diabetes mellitus (disorder)
        "432789001",  # Noncystoid edema of macula of retina (disorder)
        "769217008",  # Macular edema of right eye due to diabetes mellitus (disorder)
        "769218003",  # Macular edema of left eye due to diabetes mellitus (disorder)
        "769219006",  # Macular edema due to type 1 diabetes mellitus (disorder)
        "769220000",  # Macular edema due to type 2 diabetes mellitus (disorder)
        "770097006",  # Clinically significant macular edema due to diabetes mellitus (disorder)
        "870529009",  # Persistent macular edema due to diabetes mellitus (disorder)
        "871778008",  # Centrally involved macular edema due to diabetes mellitus (disorder)
        "871781003",  # Non centrally involved macular edema due to diabetes mellitus (disorder)
    }


class ConsultantReport(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for consultant reports.

    **Data Element Scope:** This value set may use a model element related to Assessment.

    **Inclusion Criteria:** Includes concepts that represent various consultant reports and notes.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS50v10
    """

    VALUE_SET_NAME = "Consultant Report"
    OID = "2.16.840.1.113883.3.464.1003.121.12.1006"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    LOINC = {
        "11488-4",  # Consult note
        "34099-2",  # Cardiology Consult note
        "34100-8",  # Intensive care unit Consult note
        "34101-6",  # General medicine Outpatient Consult note
        "34102-4",  # Psychiatry Hospital Consult note
        "34103-2",  # Pulmonary Consult note
        "34104-0",  # Hospital Consult note
        "34749-2",  # Anesthesiology Outpatient Consult note
        "34756-7",  # Dentistry Consult note
        "34758-3",  # Dermatology Consult note
        "34760-9",  # Diabetology Consult note
        "34761-7",  # Gastroenterology Consult note
        "34764-1",  # General medicine Consult note
        "34776-5",  # Geriatric medicine Consult note
        "34777-3",  # Obstetrics and Gynecology Consult note
        "34779-9",  # Hematology+Medical oncology Consult note
        "34781-5",  # Infectious disease Consult note
        "34783-1",  # Kinesiotherapy Consult note
        "34785-6",  # Mental health Consult note
        "34788-0",  # Psychiatry Consult note
        "34791-4",  # Psychology Consult note
        "34795-5",  # Nephrology Consult note
        "34797-1",  # Neurology Consult note
        "34798-9",  # Neurological surgery Consult note
        "34800-3",  # Nutrition and dietetics Consult note
        "34803-7",  # Occupational medicine Consult note
        "34805-2",  # Oncology Consult note
        "34807-8",  # Ophthalmology Consult note
        "34810-2",  # Optometry Consult note
        "34812-8",  # Oral and Maxillofacial Surgery Consult note
        "34814-4",  # Orthopaedic surgery Consult note
        "34816-9",  # Otolaryngology Consult note
        "34820-1",  # Pharmacology Consult note
        "34822-7",  # Physical medicine and rehab Consult note
        "34824-3",  # Physical therapy Consult note
        "34826-8",  # Plastic surgery Consult note
        "34828-4",  # Podiatry Consult note
        "34831-8",  # Radiation oncology Consult note
        "34833-4",  # Recreational therapy Consult note
        "34837-5",  # Respiratory therapy Consult note
        "34839-1",  # Rheumatology Consult note
        "34841-7",  # Social worker Consult note
        "34845-8",  # Speech-language pathology+Audiology Consult note
        "34847-4",  # Surgery Consult note
        "34849-0",  # Cardiothoracic surgery Consult note
        "34851-6",  # Urology Consult note
        "34853-2",  # Vascular surgery Consult note
        "34855-7",  # Occupational therapy Consult note
        "34879-7",  # Endocrinology Consult note
        "51845-6",  # Outpatient Consult note
        "51846-4",  # Emergency department Consult note
        "51854-8",  # Long term care facility Consult note
        "64056-5",  # General medicine Medical student Hospital Consult note
        "64068-0",  # Surgery Medical student Hospital Consult note
        "64072-2",  # Critical care medicine Medical student Hospital Consult note
        "64076-3",  # Cardiothoracic surgery Medical student Hospital Consult note
        "64080-5",  # Pulmonary Medical student Hospital Consult note
        "68469-6",  # Pastoral care Hospital Consult note
        "68486-0",  # Cardiology Medical student Hospital Consult note
        "68551-1",  # Dermatology Hospital Consult note
        "68566-9",  # Obstetrics and Gynecology Hospital Consult note
        "68570-1",  # Occupational therapy Hospital Consult note
        "68575-0",  # Ophthalmology Hospital Consult note
        "68586-7",  # Pharmacology Hospital Consult note
        "68590-9",  # Physical therapy Hospital Consult note
        "68597-4",  # Plastic surgery Hospital Consult note
        "68619-6",  # Adolescent medicine Hospital Consult note
        "68633-7",  # Allergy and Immunology Hospital Consult note
        "68639-4",  # Audiology Hospital Consult note
        "68648-5",  # Child and adolescent psychiatry Hospital Consult note
        "68651-9",  # Clinical biochemical genetics Hospital Consult note
        "68661-8",  # Clinical genetics Hospital Consult note
        "68670-9",  # Developmental-behavioral pediatrics Hospital Consult note
        "68681-6",  # Multi-specialty program Hospital Consult note
        "68685-7",  # Neonatal perinatal medicine Hospital Consult note
        "68694-9",  # Neurological surgery Hospital Consult note
        "68705-3",  # Neurology with special qualifications in child neurology Hospital Consult note
        "68716-0",  # Pain medicine Hospital Consult note
        "68727-7",  # Pediatric cardiology Hospital Consult note
        "68746-7",  # Pediatric gastroenterology Hospital Consult note
        "68757-4",  # Pediatric hematology-oncology Hospital Consult note
        "68765-7",  # Pediatric infectious diseases Hospital Consult note
        "68787-1",  # Pediatric pulmonology Hospital Consult note
        "68802-8",  # Pediatric surgery Hospital Consult note
        "68812-7",  # Pediatric urology Hospital Consult note
        "68821-8",  # Pediatrics Hospital Consult note
        "68837-4",  # Primary care Hospital Consult note
        "68846-5",  # Speech-language pathology Hospital Consult note
        "68852-3",  # Transplant surgery Hospital Consult note
        "68864-8",  # Pediatric transplant hepatology Hospital Consult note
        "68869-7",  # Pediatric nephrology Hospital Consult note
        "68874-7",  # Pediatric otolaryngology Hospital Consult note
        "68879-6",  # Pediatric rheumatology Hospital Consult note
        "68892-9",  # Pediatric dermatology Hospital Consult note
        "68897-8",  # Pediatric endocrinology Hospital Consult note
        "72555-6",  # Interventional radiology Consult note
        "73575-3",  # Radiology Consult note
        "75424-2",  # Audiology Consult note
        "75465-5",  # Orthotics prosthetics Consult note
        "77403-4",  # Anesthesiology Consult note
        "77429-9",  # Allergy and Immunology Consult note
        "78250-8",  # Colon and rectal surgery Consult note
        "78251-6",  # Hematology Consult note
        "78252-4",  # Multi-specialty program Consult note
        "78253-2",  # Family medicine Consult note
        "78254-0",  # Clinical genetics Consult note
        "78405-8",  # Neonatal perinatal medicine Consult note
        "78406-6",  # Nurse practitioner Consult note
        "78496-7",  # Critical care medicine Consult note
        "78498-3",  # Cardiopulmonary Consult note
        "78567-5",  # Pain medicine Consult note
        "78568-3",  # Palliative care Consult note
        "78726-7",  # Pediatrics Consult note
        "78732-5",  # Trauma Consult note
        "78738-2",  # Sports medicine Consult note
        "79428-9",  # Rapid response team Consult note
        "80396-5",  # Gynecologic oncology Consult note
        "80575-4",  # Cardiac surgery Consult note
        "80664-6",  # Clinical neurophysiology Consult note
        "80666-1",  # Vascular neurology Consult note
        "80673-7",  # Maternal and fetal medicine Consult note
        "80736-2",  # Blood banking and transfusion medicine Consult note
        "80801-4",  # Surgical oncology Consult note
        "81191-9",  # Chemical pathology Consult note
        "81192-7",  # Clinical pathology Consult note
        "81193-5",  # Medical microbiology - pathology Consult note
        "81196-8",  # Clinical pharmacology Consult note
        "82356-7",  # Obstetrics Midwife Consult note
        "82359-1",  # Reproductive endocrinology and infertility Consult note
        "83570-2",  # Diabetology Nurse Consult note
        "83578-5",  # Hematology+Medical oncology Nurse Consult note
        "83609-8",  # Psychiatry Nurse Consult note
        "83621-3",  # Geriatric medicine Nurse Consult note
        "83653-6",  # Pain medicine Team Consult note
        "83685-8",  # Hematology+Medical oncology Attending Consult note
        "83720-3",  # Physical medicine and rehab Long term care facility Consult note
        "83722-9",  # Physical medicine and rehabilitation Nurse Consult note
        "83868-0",  # Preventive medicine Consult note
        "83873-0",  # Primary care Consult note
        "83888-8",  # Psychiatry Long term care facility Consult note
        "83909-2",  # Public health Consult note
        "83912-6",  # Pulmonary Patient's home Consult note
        "83926-6",  # Recreational therapy Long term care facility Consult note
        "83931-6",  # Research Consult note
        "83941-5",  # Respiratory therapy Patient's home Consult note
        "83960-5",  # Social worker Patient's home Consult note
        "83967-0",  # Social worker Long term care facility Consult note
        "83984-5",  # Speech-language pathology Consult note
        "83992-8",  # Spinal cord injury medicine Consult note
        "83996-9",  # Spinal cord injury medicine Patient's home Consult note
        "84035-5",  # Transplant surgery Consult note
        "84071-0",  # Chiropractic medicine Consult note
        "84115-5",  # Geriatric medicine Long term care facility Consult note
        "84126-2",  # Surgery of the hand Consult note
        "84131-2",  # Primary care Patient's home Consult note
        "84142-9",  # Hematology+Medical oncology Hospital Consult note
        "84145-2",  # Hematology+Medical oncology Outpatient Consult note
        "84152-8",  # Hepatology Consult note
        "84173-4",  # Interventional cardiology Consult note
        "84190-8",  # Medical toxicology Consult note
        "84213-8",  # Mental health Team Consult note
        "84231-0",  # Neurology Telehealth Consult note
        "84241-9",  # Nurse Consult note
        "84280-7",  # Nutrition and dietetics Patient's home Consult note
        "84292-2",  # Nutrition and dietetics Team Consult note
        "84303-7",  # Wound care management Consult note
        "84312-8",  # Vocational rehabilitation Consult note
        "84324-3",  # Physical therapy Long term care facility Consult note
        "84349-0",  # Pastoral care Consult note
        "84352-4",  # Palliative care Team Consult note
        "84358-1",  # Palliative care Patient's home Consult note
        "84394-6",  # Occupational therapy Patient's home Consult note
        "84398-7",  # Occupational therapy Long term care facility Consult note
        "85174-1",  # Custodial care facility Consult note
        "85208-7",  # Telehealth Consult note
        "85222-8",  # Case manager Consult note
        "85232-7",  # Tumor board Consult note
        "85237-6",  # Acupuncture Consult note
        "85238-4",  # Internal medicine Consult note
        "85517-1",  # Bariatric surgery Consult note
        "85519-7",  # Child and adolescent psychology Consult note
        "85866-2",  # Sleep medicine Consult note
        "85871-2",  # Womens health Consult note
        "85882-9",  # Ophthalmology Teleimaging Consult note
        "85884-5",  # Epilepsy Consult note
        "85886-0",  # Clinical cardiac electrophysiology Consult note
        "85890-2",  # Neuropsychology Consult note
        "85899-3",  # Community health care Consult note
        "86451-2",  # Ethics Consult note
        "87233-3",  # Dialysis Consult note
        "87254-9",  # Addiction medicine Consult note
        "87627-6",  # Brain injury Consult note
        "88351-2",  # Polytrauma Consult note
        "88640-8",  # Community health care Adult day care center Consult note
        "88644-0",  # Outpatient hospital Consult note
        "89031-9",  # Hematology Telehealth Consult note
        "89032-7",  # Nephrology Telehealth Consult note
        "89033-5",  # Urology Telehealth Consult note
        "89216-6",  # Gynecology Consult note
        "89227-3",  # Obstetrics Consult note
        "89446-9",  # Obstetrics Hospital Consult note
        "89447-7",  # Gynecology Hospital Consult note
        "89551-6",  # Environmental health Consult note
        "90006-8",  # Pharmacogenomics Consult note
        "90012-6",  # Burn management Consult note
        "90343-5",  # Nuclear medicine Consult note
        "90354-2",  # Obesity medicine Consult note
        "90709-7",  # Adolescent medicine Consult note
        "90710-5",  # Developmental-behavioral pediatrics Consult note
        "90712-1",  # Sleep medicine Telehealth Consult note
        "90714-7",  # Pain medicine Telehealth Consult note
        "90715-4",  # Palliative care Telehealth Consult note
        "90717-0",  # Heart failure+Transplant cardiology Consult note
        "90771-7",  # Heart failure Consult note
        "91986-0",  # Integrative medicine Consult note
        "92910-9",  # Spinal surgery Consult note
        "92912-5",  # Eating disorders Consult note
        "92915-8",  # Immunology Consult note
        "93024-8",  # Pharmacist Consult note
        "93413-3",  # Mechanical circulatory support Consultation note
        "93955-3",  # Wound, Ostomy, and Continence Care Consult note
    }
    SNOMEDCT = {
        "371530004",  # Clinical consultation report (record artifact)
        "371531000",  # Report of clinical encounter (record artifact)
        "371545006",  # Confirmatory consultation report (record artifact)
    }


__exports__ = get_overrides(locals().copy())
