from ..value_set import ValueSet


class HospiceCareAmbulatory(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of interventions to identify patients receiving hospice care outside of a hospital or long term care facility.

    **Data Element Scope:** This value set may use a model element related to Procedure or Intervention.

    **Inclusion Criteria:** Includes concepts that represent a procedure or intervention for hospice care.

    **Exclusion Criteria:** Excludes concepts that represent palliative care or comfort measures.

    ** Used in:** CMS131v14
    """

    VALUE_SET_NAME = "Hospice Care Ambulatory"
    OID = "2.16.840.1.113883.3.526.3.1584"
    DEFINITION_VERSION = "20210825"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    CPT = {
        "99377",  # Supervision of a hospice patient (patient not present) requiring complex and multidisciplinary care modalities involving regular development and/or revision of care plans by that individual, review of subsequent reports of patient status, review of related laboratory and other studies, communication (including telephone calls) for purposes of assessment or care decisions with health care professional(s), family member(s), surrogate decision maker(s) (eg, legal guardian) and/or key caregiver(s) involved in patient's care, integration of new information into the medical treatment plan and/or adjustment of medical therapy, within a calendar month; 15-29 minutes
        "99378",  # Supervision of a hospice patient (patient not present) requiring complex and multidisciplinary care modalities involving regular development and/or revision of care plans by that individual, review of subsequent reports of patient status, review of related laboratory and other studies, communication (including telephone calls) for purposes of assessment or care decisions with health care professional(s), family member(s), surrogate decision maker(s) (eg, legal guardian) and/or key caregiver(s) involved in patient's care, integration of new information into the medical treatment plan and/or adjustment of medical therapy, within a calendar month; 30 minutes or more   
    }

    HCPSCLEVELII = {    
        "G0182",  # Physician supervision of a patient under a medicare-approved hospice (patient not present) requiring complex and multidisciplinary care modalities involving regular physician development and/or revision of care plans, review of subsequent reports of patient status, review of laboratory and other studies, communication (including telephone calls) with other health care professionals involved in the patient's care, integration of new information into the medical treatment plan and/or adjustment of medical therapy, within a calendar month, 30 minutes or more
    }
    
    SNOMEDCT = {
        "170935008",  # Full care by hospice (finding)
        "170936009",  # Shared care - hospice and general practitioner (finding)
        "385763009",  # Hospice care (regime/therapy)
    }


class PalliativeCareIntervention(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for palliative care interventions.

    **Data Element Scope:** This value set may use a model element related to Intervention.

    **Inclusion Criteria:** Includes concepts that represent palliative care interventions, including procedures and regime/therapy provided as part of palliative care services.

    **Exclusion Criteria:** Excludes concepts that represent an intervention for hospice.

    ** Used in:** CMS131v14
    """

    VALUE_SET_NAME = "Palliative Care Intervention"
    OID = "2.16.840.1.113883.3.464.1003.198.12.1135"
    DEFINITION_VERSION = "20210224"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

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


__exports__ = (HospiceCareAmbulatory, PalliativeCareIntervention,)