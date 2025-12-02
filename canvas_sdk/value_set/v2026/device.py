from ..value_set import ValueSet


class FrailtyDevice(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of devices for durable medical equipment (DME) used by frail patients.

    **Data Element Scope:** This value set may use a model element related to Device.

    **Inclusion Criteria:** Includes concepts that represent durable medical equipment (DME) or devices for frailty.

    **Exclusion Criteria:** No exclusions.

    ** Used in:** CMS131v14
    """

    VALUE_SET_NAME = "Frailty Device"
    OID = "2.16.840.1.113883.3.464.1003.118.12.1300"
    DEFINITION_VERSION = "20200310"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "466986006",   # Walking table (physical object)
        "1142151007",  # Oxygen composite cylinder (physical object)
        "1255320005",  # Wheeled walker (physical object)
        "1256013004",  # Gait rehabilitation electronic wheeled walker (physical object)
        "1256014005",  # Basic non-foldable wheeled walker (physical object)
        "1256015006",  # Basic foldable wheeled walker (physical object)
        "1256019000",  # Wheeled non-foldable walking chair (physical object)
        "1256020006",  # Wheeled foldable walking chair (physical object)
        "1256022003",  # Wheeled walking table (physical object)
        "183240000",   # Self-propelled wheelchair (physical object)
        "183241001",   # Pedal powered wheelchair (physical object)
        "183248007",   # Attendant powered wheelchair (physical object)
        "228869008",   # Manual wheelchair (physical object)
        "23366006",    # Motorized wheelchair device (physical object)
        "23562009",    # Household ventilator, device (physical object)
        "261323006",   # Portable oxygen cylinder (physical object)
        "262177002",   # Static oxygen cylinder (physical object)
        "266731002",   # Walking frame (physical object)
        "336608004",   # Oxygen cylinder (physical object)
        "360006004",   # Walking stick (physical object)
        "360008003",   # Commode (physical object)
        "360299009",   # Long cane (physical object)
        "371786002",   # Pressure support ventilator (physical object)
        "37874008",    # Continuing positive airway pressure unit, device (physical object)
        "391685000",   # Oxygen gas cylinder DD (physical object)
        "391686004",   # Oxygen gas cylinder HD (physical object)
        "391687008",   # Oxygen gas cylinder RD (physical object)
        "391688003",   # Oxygen gas cylinder DF (physical object)
        "391689006",   # Oxygen gas cylinder HX (physical object)
        "391880008",   # Oxygen gas cylinder F (physical object)
        "391881007",   # Oxygen gas cylinder AF (physical object)
        "426160001",   # Oxygen ventilator (physical object)
        "464002006",   # Portable ventilator, electric (physical object)
        "464157006",   # Multiple-base walking stick (physical object)
        "464405003",   # Multi-terrain sports wheelchair, attendant/occupant-driven (physical object)
        "464443000",   # Stand-up wheelchair (physical object)
        "464571009",   # Multi-terrain sports wheelchair, electric-motor-driven (physical object)
        "464752005",   # Multi-terrain sports wheelchair, occupant-driven (physical object)
        "465159000",   # Stair-climbing wheelchair (physical object)
        "465556004",   # Single-base walking stick (physical object)
        "465565006",   # Transport wheelchair, collapsible (physical object)
        "465921009",   # Ventilation rocking bed (physical object)
        "466182009",   # Wheelchair, occupant-driven, front-wheels-operated, non-collapsible (physical object)
        "466193006",   # Wheelchair, power-assisted, occupant-controlled, non-collapsible (physical object)
        "466213002",   # Wheelchair, electric-motor-driven, occupant-controlled, manual-steering, collapsible (physical object)
        "466229005",   # Wheelchair, occupant-driven, bimanual-lever-operated, non-collapsible (physical object)
        "466284002",   # Wheelchair, attendant/occupant-driven, bimanual-lever-operated, collapsible (physical object)
        "466316007",   # Wheelchair, combustion-engine-driven, non-collapsible (physical object)
        "466322003",   # Wheelchair, power-assisted, attendant/occupant-controlled, non-collapsible (physical object)
        "466331003",   # Wheelchair, attendant/occupant-driven, single-rear-wheel-operated, non-collapsible (physical object)
        "466337004",   # Wheelchair, attendant/occupant-driven, foot-operated, non-collapsible (physical object)
        "466340004",   # Wheelchair, occupant-driven, bimanual-lever-operated, collapsible (physical object)
        "466344008",   # Wheelchair, electric-motor-driven, occupant-controlled, powered-steering, non-collapsible (physical object)
        "466364003",   # Wheelchair, attendant/occupant-driven, rear-wheels-operated, collapsible (physical object)
        "466365002",  # Wheelchair, electric-motor-driven, attendant/occupant-controlled, manual-steering, collapsible (physical object)
        "466366001",  # Wheelchair, attendant/occupant-driven, single-lever-operated, non-collapsible (physical object)
        "466378002",  # Wheelchair, electric-motor-driven, occupant-controlled, powered-steering, collapsible (physical object)
        "466381007",  # Wheelchair, attendant-driven, non-collapsible (physical object)
        "466382000",  # Basic walking frame, non-foldable (physical object)
        "466407009",  # Walking stick/seat (physical object)
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
        "466989004",  # Wheelchair, attendant/occupant-driven, front-wheels-operated, non-collapsible (physical object)
        "466999009",  # Wheelchair, electric-motor-driven, attendant-controlled, powered-steering, collapsible (physical object)
        "467018005",  # Wheelchair, occupant-driven, single-lever-operated, non-collapsible (physical object)
        "467065004",  # Wheelchair, occupant-driven, single-front-wheel-operated, collapsible (physical object)
        "467068002",  # Basic walking frame, foldable (physical object)
        "467077009",  # Wheelchair, electric-motor-driven, attendant/occupant-controlled, manual-steering, non-collapsible (physical object)
        "467095007",  # Wheelchair, power-assisted, occupant-controlled, collapsible (physical object)
        "467137003",  # Wheelchair, occupant-driven, single-rear-wheel-operated, non-collapsible (physical object)
        "467163008",  # Wheelchair, occupant-driven, single-front-wheel-operated, non-collapsible (physical object)
        "469860004",  # All-plastic conventional wheelchair (physical object)
        "470174002",  # Heat/moisture exchanger insertable filter (physical object)
        "58938008",   # Wheelchair device (physical object)
        "66435007",   # Electric bed, device (physical object)
        "700593005",  # Heated respiratory humidifier (physical object)
        "700705005",  # Non-heated respiratory humidifier (physical object)
        "700910000",  # Ultrasonic respiratory humidifier (physical object)
        "702172008",  # Home continuous positive airway pressure unit (physical object)
        "702173003",  # Home bilevel positive airway pressure unit (physical object)
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
        "71545009",   # Household humidifier, device (physical object)
        "87405001",   # Cane, device (physical object)
    }

class GraduatedCompressionStockings(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts for a device of graduated compression stocking devices used to prevent venous thromboembolism (VTE) in patients.

    **Data Element Scope:** This value set may use a model element related to Device.

    **Inclusion Criteria:** Includes concepts that represent a device for graduated compression stockings.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Graduated compression stockings"
    OID = "2.16.840.1.113883.3.117.1.7.1.256"
    DEFINITION_VERSION = "20240203"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "1142009002",  # Compression hosiery class I thigh length (physical object)
        "1142010007",  # Compression hosiery class I below knee (physical object)
        "1142011006",  # Compression hosiery class II anklet (physical object)
        "1142012004",  # Compression hosiery class II kneecap (physical object)
        "1142014003",  # Compression hosiery class II thigh length (physical object)
        "1142015002",  # Compression hosiery class II below knee (physical object)
        "1142016001",  # Compression hosiery class III kneecap (physical object)
        "1142017005",  # Compression hosiery class III below knee (physical object)
        "1142018000",  # Compression hosiery class III thigh length (physical object)
        "1142019008",  # Compression hosiery class III anklet (physical object)
        "348681001",  # Graduated compression elastic hosiery (physical object)
        "401622003",  # Compression hosiery class I below knee stocking lightweight elastic net made to measure (physical object)
        "401624002",  # Compression hosiery class I thigh length stocking lightweight elastic net made to measure (physical object)
        "401625001",  # Compression hosiery class I thigh length stocking lightweight elastic net made to measure with fitted suspender (physical object)
        "401626000",  # Compression hosiery class II anklet circular knit made to measure (physical object)
        "401628004",  # Compression hosiery class II anklet flatbed knit made to measure (physical object)
        "401630002",  # Compression hosiery class II anklet net made to measure (physical object)
        "401631003",  # Compression hosiery class II below knee stocking circular knit made to measure (physical object)
        "401633000",  # Compression hosiery class II below knee stocking flatbed knit made to measure (physical object)
        "401634006",  # Compression hosiery class II below knee stocking net made to measure (physical object)
        "401635007",  # Compression hosiery class II kneecap circular knit made to measure (physical object)
        "401637004",  # Compression hosiery class II kneecap flatbed knit made to measure (physical object)
        "401639001",  # Compression hosiery class II kneecap net made to measure (physical object)
        "401640004",  # Compression hosiery class II thigh length stocking circular knit made to measure (physical object)
        "401642007",  # Compression hosiery class II thigh length stocking flatbed knit made to measure (physical object)
        "401643002",  # Compression hosiery class II thigh length stocking flatbed knit made to measure with fitted suspender (physical object)
        "401644008",  # Compression hosiery class II thigh length stocking net made to measure (physical object)
        "401645009",  # Compression hosiery class II thigh length stocking net made to measure with fitted suspender (physical object)
        "401646005",  # Compression hosiery class III anklet flatbed knit made to measure (physical object)
        "401648006",  # Compression hosiery class III below knee stocking circular knit made to measure (physical object)
        "401650003",  # Compression hosiery class III below knee stocking flatbed knit made to measure (physical object)
        "401651004",  # Compression hosiery class III kneecap circular knit made to measure (physical object)
        "401652006",  # Compression hosiery class III kneecap flatbed knit made to measure (physical object)
        "401654007",  # Compression hosiery class III thigh length stocking circular knit made to measure (physical object)
        "401656009",  # Compression hosiery class III thigh length stocking flatbed knit made to measure (physical object)
        "401657000",  # Compression hosiery class III thigh length stocking flatbed knit made to measure with fitted suspender (physical object)
        "401776005",  # Class I compression hosiery (physical object)
        "401777001",  # Class II compression hosiery (physical object)
        "401778006",  # Class III compression hosiery (physical object)
        "408127000",  # Class I bacteriostatic thigh length stocking (physical object)
        "408128005",  # Class I bacteriostatic below knee stocking (physical object)
        "408129002",  # Class II bacteriostatic thigh length stocking (physical object)
        "408130007",  # Class II bacteriostatic b-knee stocking (physical object)
        "408131006",  # Class III bacteriostatic thigh length stocking (physical object)
        "408132004",  # Class III bacteriostatic below knee stocking (physical object)
    }

class IntermittentPneumaticCompressionDevices(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to represent concepts of devices using intermittent pneumatic compression devices for venous thromboembolism (VTE) prophylaxis.

    **Data Element Scope:** This value set may use a model element related to Device.

    **Inclusion Criteria:** Includes concepts that represent a device for intermittent pneumatic compression.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Intermittent pneumatic compression devices"
    OID = "2.16.840.1.113883.3.117.1.7.1.214"
    DEFINITION_VERSION = "20230117"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "428411000124104",  # Intermittent pneumatic compression boot (physical object)
        "428421000124107",  # Intermittent pneumatic compression sleeve (physical object)
        "432441000124100",  # Intermittent pneumatic compression device (physical object)
        "442111003",  # Intermittent pneumatic compression stockings (physical object)
        "469317002",  # Intermittent venous compression system pump (physical object)
        "469365001",  # Intermittent venous compression system (physical object)
    }

class VenousFootPumps(ValueSet):
    """
    **Clinical Focus:** The purpose of this value set is to identify concepts for a device for a venous pump applied for venous thromboembolism (VTE) prophylaxis.

    **Data Element Scope:** This value set may use a model element related to Device.

    **Inclusion Criteria:** Includes concepts that represent a device used for venous thromboembolism (VTE) prophylaxis.

    **Exclusion Criteria:** No exclusions.
    """

    VALUE_SET_NAME = "Venous foot pumps"
    OID = "2.16.840.1.113883.3.117.1.7.1.230"
    DEFINITION_VERSION = "20210220"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "442023007",  # Venous foot pump, device (physical object)
    }

class NonInvasiveOxygenTherapyDeviceCodes(ValueSet):
    """
    **Clinical Focus:** N/A

    **Data Element Scope:** N/A

    **Inclusion Criteria:** N/A

    **Exclusion Criteria:** N/A
    """

    VALUE_SET_NAME = "Non Invasive Oxygen Therapy Device Codes"
    OID = "2.16.840.1.113762.1.4.1170.57"
    DEFINITION_VERSION = "20250207"
    EXPANSION_VERSION = "eCQM Update 2025-05-08"

    SNOMEDCT = {
        "257420000",  # Breathing circuit (physical object)
        "26397000",  # Breathing bag, device (physical object)
        "297120004",  # Anesthetic face mask (physical object)
        "320917000",  # Product containing only oxygen in conventional release gas for inhalation (medicinal product form)
        "336602003",  # Oxygen mask (physical object)
        "336608004",  # Oxygen cylinder (physical object)
        "336623009",  # Oxygen nasal cannula (physical object)
        "405642002",  # Anesthesia breathing circuit (physical object)
        "425478008",  # Blow by oxygen mask (physical object)
        "425826004",  # Bilevel positive airway pressure oxygen nasal cannula (physical object)
        "426294006",  # Face tent oxygen delivery device (physical object)
        "426851007",  # Aerosol oxygen mask (physical object)
        "426854004",  # High flow oxygen nasal cannula (physical object)
        "427591007",  # Nonrebreather oxygen mask (physical object)
        "427594004",  # Oxyhood (physical object)
        "428285009",  # Venturi mask (physical object)
        "442398003",  # Nasal mask (physical object)
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
        "701254008",  # Bidirectional-anesthesia breathing circuit (physical object)
        "701582002",  # Vortex oxygen face mask (physical object)
        "706175007",  # Ventilator breathing circuit (physical object)
        "719705009",  # Capnography oxygen mask (physical object)
    }

__exports__ = (
    "FrailtyDevice",
    "GraduatedCompressionStockings",
    "IntermittentPneumaticCompressionDevices",
    "VenousFootPumps",
    "NonInvasiveOxygenTherapyDeviceCodes",
)
