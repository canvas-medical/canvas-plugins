from ..value_set import ValueSet


class InpatientFalls(ValueSet):
    """
    **Clinical Focus:** The purpose of this Grouped value set is to represent concepts for falls within the hospital setting.

    **Data Element Scope:** This value set may use a model element related to Adverse Event.

    **Inclusion Criteria:** Includes concepts that represent falls within the hospital setting.

    **Exclusion Criteria:** Excludes concepts that represent falls outside of the hospital setting.
    """

    VALUE_SET_NAME = "Inpatient Falls"
    OID = "2.16.840.1.113762.1.4.1147.171"
    DEFINITION_VERSION = "20210605"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    ICD10CM = {
        "W010XXA",  # Fall on same level from slipping, tripping and stumbling without subsequent striking against object, initial encounter
        "W0110XA",  # Fall on same level from slipping, tripping and stumbling with subsequent striking against unspecified object, initial encounter
        "W01110A",  # Fall on same level from slipping, tripping and stumbling with subsequent striking against sharp glass, initial encounter
        "W01111A",  # Fall on same level from slipping, tripping and stumbling with subsequent striking against power tool or machine, initial encounter
        "W01118A",  # Fall on same level from slipping, tripping and stumbling with subsequent striking against other sharp object, initial encounter
        "W01119A",  # Fall on same level from slipping, tripping and stumbling with subsequent striking against unspecified sharp object, initial encounter
        "W01190A",  # Fall on same level from slipping, tripping and stumbling with subsequent striking against furniture, initial encounter
        "W01198A",  # Fall on same level from slipping, tripping and stumbling with subsequent striking against other object, initial encounter
        "W03XXXA",  # Other fall on same level due to collision with another person, initial encounter
        "W04XXXA",  # Fall while being carried or supported by other persons, initial encounter
        "W050XXA",  # Fall from non-moving wheelchair, initial encounter
        "W051XXA",  # Fall from non-moving nonmotorized scooter, initial encounter
        "W052XXA",  # Fall from non-moving motorized mobility scooter, initial encounter
        "W06XXXA",  # Fall from bed, initial encounter
        "W07XXXA",  # Fall from chair, initial encounter
        "W08XXXA",  # Fall from other furniture, initial encounter
        "W101XXA",  # Fall (on)(from) sidewalk curb, initial encounter
        "W102XXA",  # Fall (on)(from) incline, initial encounter
        "W108XXA",  # Fall (on) (from) other stairs and steps, initial encounter
        "W109XXA",  # Fall (on) (from) unspecified stairs and steps, initial encounter
        "W133XXA",  # Fall through floor, initial encounter
        "W134XXA",  # Fall from, out of or through window, initial encounter
        "W138XXA",  # Fall from, out of or through other building or structure, initial encounter
        "W139XXA",  # Fall from, out of or through building, not otherwise specified, initial encounter
        "W16211A",  # Fall in (into) filled bathtub causing drowning and submersion, initial encounter
        "W16212A",  # Fall in (into) filled bathtub causing other injury, initial encounter
        "W16221A",  # Fall in (into) bucket of water causing drowning and submersion, initial encounter
        "W16222A",  # Fall in (into) bucket of water causing other injury, initial encounter
        "W1789XA",  # Other fall from one level to another, initial encounter
        "W1800XA",  # Striking against unspecified object with subsequent fall, initial encounter
        "W1801XA",  # Striking against sports equipment with subsequent fall, initial encounter
        "W1802XA",  # Striking against glass with subsequent fall, initial encounter
        "W1809XA",  # Striking against other object with subsequent fall, initial encounter
        "W1811XA",  # Fall from or off toilet without subsequent striking against object, initial encounter
        "W1812XA",  # Fall from or off toilet with subsequent striking against object, initial encounter
        "W182XXA",  # Fall in (into) shower or empty bathtub, initial encounter
        "W1830XA",  # Fall on same level, unspecified, initial encounter
        "W1831XA",  # Fall on same level due to stepping on an object, initial encounter
        "W1839XA",  # Other fall on same level, initial encounter
        "W19XXXA",  # Unspecified fall, initial encounter
    }

    SNOMEDCT = {
        "14047009",  # Fall from building (event)
        "161898004",  # Falls (finding)
        "17886000",  # Fall from wheelchair (event)
        "1912002",  # Fall (event)
        "20902002",  # Fall from bed (event)
        "217082002",  # Accidental fall (event)
        "217083007",  # Fall on or from stairs or steps (event)
        "217088003",  # Fall on or from stairs (event)
        "217090002",  # Fall from stairs (event)
        "217092005",  # Fall on or from steps (event)
        "217093000",  # Fall on steps (event)
        "217094006",  # Fall from steps (event)
        "217142006",  # Fall from chair or bed (event)
        "217154006",  # Fall on same level from slipping, tripping or stumbling (event)
        "217155007",  # Fall on same level from slipping (event)
        "217156008",  # Fall on same level from tripping (event)
        "217157004",  # Fall on same level from stumbling (event)
        "217173005",  # Fall from bump against object (event)
        "242389003",  # Fall due to wet surface (event)
        "242390007",  # Fall due to polished surface (event)
        "242391006",  # Fall due to discarded object (event)
        "242392004",  # Fall in bath or shower (event)
        "242394003",  # Fall due to accidental trip by another person (event)
        "242395002",  # Fall due to trip on loose carpet (event)
        "242396001",  # Fall due to uneven surface indoors (event)
        "242398000",  # Fall due to loss of equilibrium (event)
        "242399008",  # Fall due to failure of support (event)
        "242400001",  # Fall due to failure of rail (event)
        "242401002",  # Fall due to leaning on insecure furniture (event)
        "242402009",  # Fall on same level due to accidental impact with another person (event)
        "242403004",  # Fall on same level due to deliberate assault by another person (event)
        "242413007",  # Fall from furniture (event)
        "242415000",  # Fall from hospital gurney (event)
        "242417008",  # Fall from ambulance stretcher (event)
        "242419006",  # Fall from toilet seat (event)
        "249995008",  # Legs give way - falling (finding)
        "269699007",  # Fall on same level from impact against object (event)
        "274918000",  # Fall on same level due to nature of surface (event)
        "274919008",  # Fall on same level due to impact against another person (event)
        "279992002",  # Recurrent falls (finding)
        "298344006",  # Elderly fall (finding)
        "33036003",  # Fall on same level (event)
        "404911003",  # Unexplained recurrent falls (finding)
        "404912005",  # Unexplained falls (finding)
        "408561005",  # Falls caused by medication (finding)
        "414190009",  # Fall on stairs (event)
        "427849003",  # Fall on hard surface (event)
        "429012000",  # Fall on soft surface (event)
        "429482004",  # Fall from high place (event)
        "429621003",  # Fall on concrete (event)
        "429636000",  # Fall into water (event)
        "435901000124102",  # Fall due to seizure (event)
        "44188002",  # Fall in shower (event)
        "48015001",  # Fall through window (event)
        "56307009",  # Fall from table (event)
        "60594001",  # Fall while being carried (event)
        "713397003",  # Fall from operating room table (event)
        "74541001",  # Fall from bench (event)
        "83468000",  # Fall from chair (event)
        "90619006",  # Fall in bathtub (event)
        "90639005",  # Fall from window (event)
    }


class ThrombolyticMedications(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for thrombolytic medications used for treatment of ST-segment elevation myocardial infaction (STEMI).

    **Data Element Scope:** This value set may use a model element related to Medication.

    **Inclusion Criteria:** Includes RXNORM codes that represent ingredients in thrombolytic medications for STEMI treatment.

    **Exclusion Criteria:** No exclusions
    """

    VALUE_SET_NAME = "Thrombolytic medications"
    OID = "2.16.840.1.113762.1.4.1170.4"
    DEFINITION_VERSION = "20211007"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    RXNORM = {
        "10106",  # streptokinase
        "11055",  # urokinase
        "259280",  # tenecteplase
        "40028",  # anistreplase
        "76895",  # reteplase
        "8410",  # alteplase
    }


__exports__ = (
    "InpatientFalls",
    "ThrombolyticMedications",
)
