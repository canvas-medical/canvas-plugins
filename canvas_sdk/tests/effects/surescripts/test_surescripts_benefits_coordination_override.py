import json

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.surescripts import SurescriptsBenefitsCoordinationOverride
from canvas_sdk.events import EventType


def test_effect_type_enum_value_is_pinned() -> None:
    """Pin the proto enum value so a re-numbering fails the test."""
    assert EffectType.SURESCRIPTS_BENEFITS_COORDINATION_OVERRIDE == 1606


def test_pre_send_event_enum_value_is_pinned() -> None:
    """Plugin handlers respond to this event; pin its value and name."""
    assert EventType.PRESCRIBE_COMMAND__PRE_SEND == 33026
    assert EventType.Name(EventType.PRESCRIBE_COMMAND__PRE_SEND) == "PRESCRIBE_COMMAND__PRE_SEND"


def test_apply_with_all_fields_emits_full_payload() -> None:
    """All set fields appear in the effect payload under data."""
    effect = SurescriptsBenefitsCoordinationOverride(
        iin_number="610415",
        processor_identification_number="MEDDPRIME",
        group_id="TTC1",
        pbm_member_id="ABC123456",
    )

    proto_effect = effect.apply()

    assert proto_effect.type == EffectType.SURESCRIPTS_BENEFITS_COORDINATION_OVERRIDE
    assert json.loads(proto_effect.payload) == {
        "data": {
            "iin_number": "610415",
            "processor_identification_number": "MEDDPRIME",
            "group_id": "TTC1",
            "pbm_member_id": "ABC123456",
        }
    }


def test_apply_with_single_field() -> None:
    """A single field can be the sole override."""
    effect = SurescriptsBenefitsCoordinationOverride(iin_number="610415")

    proto_effect = effect.apply()

    assert json.loads(proto_effect.payload) == {"data": {"iin_number": "610415"}}


def test_apply_omits_unset_fields() -> None:
    """Fields left as None are excluded from the payload entirely.

    A plugin overriding only one value should not stomp the others to None on
    the home-app side; the contract is "absent = no override".
    """
    effect = SurescriptsBenefitsCoordinationOverride(group_id="TTC1")

    proto_effect = effect.apply()

    assert json.loads(proto_effect.payload) == {"data": {"group_id": "TTC1"}}


def test_empty_override_emits_empty_data() -> None:
    """An effect with no fields set is a valid no-op; payload is data: {}."""
    effect = SurescriptsBenefitsCoordinationOverride()

    proto_effect = effect.apply()

    assert proto_effect.type == EffectType.SURESCRIPTS_BENEFITS_COORDINATION_OVERRIDE
    assert json.loads(proto_effect.payload) == {"data": {}}
