from canvas_sdk.value_set._utilities import get_overrides

from ..value_set import ValueSet


class FrailtyDevice(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of devices for durable medical equipment (DME) used by frail patients.

    **Data Element Scope:** This value set may use a model element related to Device.

    **Inclusion Criteria:** Includes concepts that represent  durable medical equipment (DME) or devices for frailty.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS134v10, CMS165v10, CMS131v10, CMS122v10, CMS125v10, CMS130v10
    """

    VALUE_SET_NAME = "Frailty Device"
    OID = "2.16.840.1.113883.3.464.1003.118.12.1300"
    DEFINITION_VERSION = "20200310"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "23366006",  # Motorized wheelchair device (physical object)
        "23562009",  # Household ventilator, device (physical object)
        "37874008",  # Continuing positive airway pressure unit, device (physical object)
        "58938008",  # Wheelchair device (physical object)
        "66435007",  # Electric bed, device (physical object)
        "71545009",  # Household humidifier, device (physical object)
        "87405001",  # Cane, device (physical object)
        "183240000",  # Self-propelled wheelchair (physical object)
        "183241001",  # Pedal powered wheelchair (physical object)
        "183248007",  # Attendant powered wheelchair (physical object)
        "228869008",  # Manual wheelchair (physical object)
        "261323006",  # Portable oxygen cylinder (physical object)
        "262177002",  # Static oxygen cylinder (physical object)
        "360006004",  # Walking stick (physical object)
        "360008003",  # Commode (physical object)
        "360299009",  # Long cane (physical object)
        "371786002",  # Pressure support ventilator (physical object)
        "391685000",  # Oxygen gas cylinder DD (physical object)
        "391686004",  # Oxygen gas cylinder HD (physical object)
        "391687008",  # Oxygen gas cylinder RD (physical object)
        "391688003",  # Oxygen gas cylinder DF (physical object)
        "391689006",  # Oxygen gas cylinder HX (physical object)
        "391880008",  # Oxygen gas cylinder F (physical object)
        "391881007",  # Oxygen gas cylinder AF (physical object)
        "401953003",  # Oxygen composite cylinder with integral headset 1360 liters (physical object)
        "401954009",  # Oxygen cylinder 1360 liters (physical object)
        "401955005",  # Oxygen cylinder 300 liters (physical object)
        "426160001",  # Oxygen ventilator (physical object)
        "462987000",  # Patient/medical device walker (physical object)
        "463093001",  # Patient/medical device walker, home-use (physical object)
        "464002006",  # Portable ventilator, electric (physical object)
        "464157006",  # Multiple-base walking stick (physical object)
        "464405003",  # Multi-terrain sports wheelchair, attendant/occupant-driven (physical object)
        "464443000",  # Stand-up wheelchair (physical object)
        "464571009",  # Multi-terrain sports wheelchair, electric-motor-driven (physical object)
        "464752005",  # Multi-terrain sports wheelchair, occupant-driven (physical object)
        "465159000",  # Stair-climbing wheelchair (physical object)
        "465556004",  # Single-base walking stick (physical object)
        "465565006",  # Transport wheelchair, collapsible (physical object)
        "465921009",  # Ventilation rocking bed (physical object)
        "466182009",  # Wheelchair, occupant-driven, front-wheels-operated, non-collapsible (physical object)
        "466193006",  # Wheelchair, power-assisted, occupant-controlled, non-collapsible (physical object)
        "466213002",  # Wheelchair, electric-motor-driven, occupant-controlled, manual-steering, collapsible (physical object)
        "466229005",  # Wheelchair, occupant-driven, bimanual-lever-operated, non-collapsible (physical object)
        "466284002",  # Wheelchair, attendant/occupant-driven, bimanual-lever-operated, collapsible (physical object)
        "466316007",  # Wheelchair, combustion-engine-driven, non-collapsible (physical object)
        "466317003",  # Basic walker, foldable (physical object)
        "466322003",  # Wheelchair, power-assisted, attendant/occupant-controlled, non-collapsible (physical object)
        "466331003",  # Wheelchair, attendant/occupant-driven, single-rear-wheel-operated, non-collapsible (physical object)
        "466337004",  # Wheelchair, attendant/occupant-driven, foot-operated, non-collapsible (physical object)
        "466340004",  # Wheelchair, occupant-driven, bimanual-lever-operated, collapsible (physical object)
        "466344008",  # Wheelchair, electric-motor-driven, occupant-controlled, powered-steering, non-collapsible (physical object)
        "466351004",  # Walking chair, foldable (physical object)
        "466364003",  # Wheelchair, attendant/occupant-driven, rear-wheels-operated, collapsible (physical object)
        "466365002",  # Wheelchair, electric-motor-driven, attendant/occupant-controlled, manual-steering, collapsible (physical object)
        "466366001",  # Wheelchair, attendant/occupant-driven, single-lever-operated, non-collapsible (physical object)
        "466378002",  # Wheelchair, electric-motor-driven, occupant-controlled, powered-steering, collapsible (physical object)
        "466381007",  # Wheelchair, attendant-driven, non-collapsible (physical object)
        "466407009",  # Walking stick/seat (physical object)
        "466464004",  # Basic walker, non-foldable (physical object)
        "466466002",  # Wheelchair, occupant-driven, foot-operated, collapsible (physical object)
        "466473007",  # Wheelchair, electric-motor-driven, attendant-controlled, manual-steering, collapsible (physical object)
        "466477008",  # Wheelchair, electric-motor-driven, occupant-controlled, manual-steering, non-collapsible (physical object)
        "466486003",  # Wheelchair, attendant/occupant-driven, bimanual-lever-operated, non-collapsible (physical object)
        "466494005",  # Wheelchair, power-assisted, attendant-controlled, collapsible (physical object)
        "466524001",  # Wheelchair, attendant-driven, collapsible (physical object)
        "466533004",  # Wheelchair, attendant/occupant-driven, foot-operated, collapsible (physical object)
        "466538008",  # Room humidifier (physical object)
        "466550002",  # Wheelchair, attendant/occupant-driven, rear-wheels-operated, non-collapsible (physical object)
        "466553000",  # Wheelchair, occupant-driven, single-lever-operated, collapsible (physical object)
        "466576002",  # Wheelchair, occupant-driven, bimanual-chain-operated, collapsible (physical object)
        "466607002",  # Wheelchair, attendant/occupant-driven, single-lever-operated, collapsible (physical object)
        "466616003",  # Wheelchair, attendant/occupant-driven, single-rear-wheel-operated, collapsible (physical object)
        "466619005",  # Wheelchair, attendant/occupant-driven, bimanual-chain-operated, non-collapsible (physical object)
        "466644002",  # Wheelchair, occupant-driven, bimanual-chain-operated, non-collapsible (physical object)
        "466671002",  # Wheelchair, combustion-engine-driven, collapsible (physical object)
        "466695000",  # Wheelchair, attendant/occupant-driven, single-front-wheel-operated, collapsible (physical object)
        "466699006",  # Wheelchair, power-assisted, attendant/occupant-controlled, collapsible (physical object)
        "466721007",  # Wheelchair, power-assisted, attendant-controlled, non-collapsible (physical object)
        "466739003",  # Wheelchair, occupant-driven, front-wheels-operated, collapsible (physical object)
        "466758007",  # Wheelchair, electric-motor-driven, attendant-controlled, manual-steering, non-collapsible (physical object)
        "466786004",  # Basic electric hospital bed (physical object)
        "466809001",  # Wheelchair, attendant/occupant-driven, bimanual-chain-operated, collapsible (physical object)
        "466813008",  # Wheelchair, electric-motor-driven, attendant-controlled, powered-steering, non-collapsible (physical object)
        "466851008",  # Wheelchair, attendant/occupant-driven, front-wheels-operated, collapsible (physical object)
        "466871004",  # Wheelchair, electric-motor-driven, attendant/occupant-controlled, powered-steering, non-collapsible (physical object)
        "466889003",  # Wheelchair, attendant/occupant-driven, single-front-wheel-operated, non-collapsible (physical object)
        "466926008",  # Wheelchair, occupant-driven, rear-wheels-operated, collapsible (physical object)
        "466927004",  # Wheelchair, electric-motor-driven, attendant/occupant-controlled, powered-steering, collapsible (physical object)
        "466938004",  # Wheelchair, occupant-driven, single-rear-wheel-operated, collapsible (physical object)
        "466947007",  # Wheelchair, occupant-driven, rear-wheels-operated, non-collapsible (physical object)
        "466966007",  # Wheelchair, occupant-driven, foot-operated, non-collapsible (physical object)
        "466986006",  # Walking table (physical object)
        "466989004",  # Wheelchair, attendant/occupant-driven, front-wheels-operated, non-collapsible (physical object)
        "466999009",  # Wheelchair, electric-motor-driven, attendant-controlled, powered-steering, collapsible (physical object)
        "467018005",  # Wheelchair, occupant-driven, single-lever-operated, non-collapsible (physical object)
        "467065004",  # Wheelchair, occupant-driven, single-front-wheel-operated, collapsible (physical object)
        "467077009",  # Wheelchair, electric-motor-driven, attendant/occupant-controlled, manual-steering, non-collapsible (physical object)
        "467095007",  # Wheelchair, power-assisted, occupant-controlled, collapsible (physical object)
        "467137003",  # Wheelchair, occupant-driven, single-rear-wheel-operated, non-collapsible (physical object)
        "467155007",  # Walking chair, non-foldable (physical object)
        "467163008",  # Wheelchair, occupant-driven, single-front-wheel-operated, non-collapsible (physical object)
        "469361005",  # Heat/moisture exchanger, reusable (physical object)
        "469860004",  # All-plastic conventional wheelchair (physical object)
        "470119002",  # Heat/moisture exchanger, single-use (physical object)
        "470174002",  # Heat/moisture exchanger insertable filter (physical object)
        "700593005",  # Heated respiratory humidifier (physical object)
        "700705005",  # Non-heated respiratory humidifier (physical object)
        "700910000",  # Ultrasonic respiratory humidifier (physical object)
        "702172008",  # Home continuous positive airway pressure unit (physical object)
        "702173003",  # Home bilevel positive airway pressure unit (physical object)
        "705404007",  # Walker/Walking frame (physical object)
        "705406009",  # Walker (physical object)
        "705419008",  # Special-function wheelchair (physical object)
        "705421003",  # Sports wheelchair (physical object)
        "705422005",  # Power-driven wheelchair (physical object)
        "705423000",  # Electric-motor-driven wheelchair (physical object)
        "705425007",  # Attendant/occupant-controlled electric-motor-driven wheelchair (physical object)
        "705426008",  # Attendant-controlled electric-motor-driven wheelchair (physical object)
        "705427004",  # Power-assisted wheelchair (physical object)
        "705428009",  # Manual-driven wheelchair (physical object)
        "706180003",  # Respiratory humidifier (physical object)
        "714700001",  # Bilevel positive airway pressure unit hand held (physical object)
        "781471009",  # Gait rehabilitation electronic walker (physical object)
    }


class CardiacPacer(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a cardiac pacer device.

    **Data Element Scope:** This value set may use a model element related to Device.

    **Inclusion Criteria:** Includes concepts that represent a device that is a cardiac pacer.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS144v10, CMS145v10
    """

    VALUE_SET_NAME = "Cardiac Pacer"
    OID = "2.16.840.1.113883.3.526.3.1193"
    DEFINITION_VERSION = "20170504"
    EXPANSION_VERSION = "eCQM Update 2021-05-06"

    SNOMEDCT = {
        "14106009",  # Cardiac pacemaker, device (physical object)
        "56961003",  # Cardiac transvenous pacemaker, device (physical object)
        "360127006",  # Intravenous cardiac pacemaker system (physical object)
        "360128001",  # Intravenous triggered cardiac pacemaker system (physical object)
        "424921004",  # Permanent cardiac pacemaker, device (physical object)
    }


__exports__ = get_overrides(locals().copy())
