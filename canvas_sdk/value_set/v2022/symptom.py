from ..value_set import ValueSet


class FrailtySymptom(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for symptoms of frailty.

    **Data Element Scope:** This value set may use a model element related to Symptom.

    **Inclusion Criteria:** Includes concepts that represent a symptom of frailty.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS134v10, CMS165v10, CMS131v10, CMS122v10, CMS125v10, CMS130v10
    """

    VALUE_SET_NAME = "Frailty Symptom"
    OID = "2.16.840.1.113883.3.464.1003.113.12.1075"
    DEFINITION_VERSION = "20190315"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    ICD10CM = {
        "R260",  # Ataxic gait
        "R261",  # Paralytic gait
        "R262",  # Difficulty in walking, not elsewhere classified
        "R2689",  # Other abnormalities of gait and mobility
        "R269",  # Unspecified abnormalities of gait and mobility
        "R4181",  # Age-related cognitive decline
        "R531",  # Weakness
        "R5381",  # Other malaise
        "R5383",  # Other fatigue
        "R54",  # Age-related physical debility
        "R627",  # Adult failure to thrive
        "R634",  # Abnormal weight loss
        "R636",  # Underweight
        "R64",  # Cachexia
    }
    SNOMEDCT = {
        "4468000",  # Oppenheim's gait (finding)
        "8510008",  # Reduced mobility (finding)
        "13791008",  # Asthenia (finding)
        "18726006",  # Senile asthenia (finding)
        "20940004",  # Spinal hemiparesis (finding)
        "22090007",  # Scissoring gait (finding)
        "22325002",  # Abnormal gait (finding)
        "22631008",  # Unsteady when walking (finding)
        "23042008",  # Spinal paraparesis (finding)
        "25136009",  # Ataxic gait (finding)
        "26544005",  # Muscle weakness (finding)
        "41786007",  # Neurological muscle weakness (finding)
        "43005009",  # Shuffling gait (finding)
        "50314001",  # Partial bilateral paresis (finding)
        "67141003",  # Antalgic gait (finding)
        "78119002",  # Complete bilateral paresis (finding)
        "78691002",  # Staggering gait (finding)
        "84229001",  # Fatigue (finding)
        "89362005",  # Weight loss (finding)
        "102492002",  # Failure to maintain weight (finding)
        "102568007",  # Paresis of lower extremity (finding)
        "102891000",  # Age-related cognitive decline (finding)
        "105501005",  # Dependence on enabling machine or device (finding)
        "105503008",  # Dependence on wheelchair (finding)
        "105504002",  # Dependence on walking stick (finding)
        "126013009",  # Subjective muscle weakness (finding)
        "127378008",  # Bilateral paresis (finding)
        "135834002",  # Pseudoparalysis (finding)
        "160681005",  # Mobile outside with aid (finding)
        "160683008",  # Needs walking aid in home (finding)
        "160684002",  # Confined to chair (finding)
        "160685001",  # Bed-ridden (finding)
        "160692006",  # Mobility very poor (finding)
        "160693001",  # Mobility poor (finding)
        "160734000",  # Lives in a nursing home (finding)
        "160737007",  # Lives in an old peoples home (finding)
        "161832001",  # Weight decreasing (finding)
        "161873000",  # Heavy legs (finding)
        "161874006",  # Heavy feeling (finding)
        "162236007",  # Weakness present (finding)
        "162239000",  # Abdominal weakness (finding)
        "163600007",  # On examination - paresis (weakness) (finding)
        "163686004",  # On examination - gait ataxic (finding)
        "163695007",  # On examination - muscle power reduced (finding)
        "165243005",  # Independent in wheelchair (finding)
        "165244004",  # Minimal help in wheelchair (finding)
        "224960004",  # Tired (finding)
        "225612007",  # Wheelchair bound (finding)
        "238108007",  # Cachexia (finding)
        "248269005",  # Tired on least exertion (finding)
        "248278004",  # Attacks of weakness (finding)
        "248279007",  # Frailty (finding)
        "249888000",  # Weakness of sternomastoid (finding)
        "249937002",  # Truncal muscle weakness (finding)
        "249938007",  # Weakness of back (finding)
        "249939004",  # Proximal muscle weakness (finding)
        "249940002",  # Shoulder girdle weakness (finding)
        "249941003",  # Pelvic girdle weakness (finding)
        "249942005",  # Distal muscle weakness (finding)
        "249943000",  # Weakness of distal arms and legs (finding)
        "249946008",  # Pyramidal type muscle weakness (finding)
        "250002000",  # Rapid fatigue of gait (finding)
        "250003005",  # Low level sensorimotor gait disorder (finding)
        "250015009",  # Arthritic gait (finding)
        "250029005",  # Sensory ataxic gait (finding)
        "250032008",  # Vestibular ataxic gait (finding)
        "250033003",  # Visual ataxic gait (finding)
        "250034009",  # Middle level sensorimotor gait disorder (finding)
        "250038007",  # Retropulsion when walking (finding)
        "250043000",  # High level sensorimotor gait disorder (finding)
        "250044006",  # Cautious gait (finding)
        "250045007",  # Tottering gait (finding)
        "250048009",  # Frontal ataxia (finding)
        "250052009",  # Petren's gait (finding)
        "250054005",  # Frontal gait disorder (finding)
        "262285001",  # Weight decreased (finding)
        "267024001",  # Abnormal weight loss (finding)
        "267031002",  # Tiredness symptom (finding)
        "267032009",  # Tired all the time (finding)
        "268964003",  # On examination - festination-Parkinson gait (finding)
        "271795006",  # Malaise and fatigue (finding)
        "271875007",  # Senile debility (finding)
        "272036004",  # Complaining of debility and malaise (finding)
        "272060000",  # Fatigue - symptom (finding)
        "272062008",  # Complaining of "tired all the time" (finding)
        "275313006",  # Dragging leg (finding)
        "284529003",  # Cardiac cachexia (finding)
        "298283006",  # Hand muscle weakness (finding)
        "300948004",  # Quadriceps weakness (finding)
        "309249007",  # Calf muscle weakness (finding)
        "309257005",  # Excessive weight loss (finding)
        "312444006",  # Spastic paraparesis (finding)
        "314109004",  # Feeling tired (finding)
        "365884000",  # Cerebellar ataxic gait (finding)
        "367391008",  # Malaise (finding)
        "371028005",  # Spastic paresis (finding)
        "373931001",  # Sensation of heaviness in limbs (finding)
        "394616008",  # Unsteady gait (finding)
        "397776000",  # Festinating gait (finding)
        "404904002",  # Frail elderly (finding)
        "413121008",  # Dependent on helper pushing wheelchair (finding)
        "418073009",  # Pseudoparalysis due to generalized arthritis (finding)
        "422868009",  # Unexplained weight loss (finding)
        "426977000",  # Recent weight loss (finding)
        "428116008",  # Multifactorial gait problem (finding)
        "428264009",  # Painful gait (finding)
        "429091008",  # Dependence on biphasic positive airway pressure ventilation (finding)
        "429487005",  # Dependence on continuous positive airway pressure ventilation (finding)
        "431524008",  # Abnormal gait due to impairment of balance (finding)
        "432559006",  # Abnormal gait due to muscle weakness (finding)
        "442099003",  # Psychogenic fatigue (finding)
        "444042007",  # Excessive postexertional fatigue (finding)
        "444932008",  # Dependence on ventilator (finding)
        "448765001",  # Unintentional weight loss (finding)
        "713512009",  # Muscle weakness of upper limb (finding)
        "713514005",  # Muscle weakness of limb (finding)
        "713568000",  # Occasionally tired (finding)
        "713655003",  # Dependence on non-invasive ventilation (finding)
        "784317004",  # Fatigue due to chemotherapy (finding)
        "784318009",  # Fatigue due to radiation therapy (finding)
        "788876001",  # Cachexia due to malignant neoplastic disease (finding)
        "788900007",  # Dependence on artificial heart (finding)
        "931000119107",  # Dependence on supplemental oxygen (finding)
        "60631000119109",  # Dependence on home ventilator (finding)
        "60651000119103",  # Dependence on continuous supplemental oxygen (finding)
        "69161000119103",  # Functional gait abnormality (finding)
        "79021000119104",  # Dependence on aspirator (finding)
        "79031000119101",  # Dependence on respirator (finding)
        "85711000119103",  # Stumbling due to lack of coordination (finding)
        "89201000119106",  # Dependence on supplemental oxygen when ambulating (finding)
        "152921000119101",  # Dependence on respiratory device (finding)
        "250991000119100",  # Stumbling gait (finding)
        "459821000124104",  # McArdle sign (finding)
        "15634971000119107",  # Weakness of bilateral upper limbs (finding)
        "16018391000119104",  # Paresis of left lower limb (finding)
        "16018431000119109",  # Paresis of right lower limb (finding)
        "16419651000119103",  # Dependence on biphasic positive airway pressure ventilation due to central sleep apnea syndrome (finding)
    }


__exports__ = ("FrailtySymptom",)
