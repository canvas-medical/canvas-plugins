from canvas_sdk.effects.codings._coding import CodingEffect


class ReasonForVisitSettingCoding(CodingEffect):
    """Create, update, or delete a structured reason-for-visit option. ``id`` is its id."""

    class Meta:
        effect_type = "REASON_FOR_VISIT_SETTING_CODING"

    _entity_label: str = "reason for visit coding"


__exports__ = ("ReasonForVisitSettingCoding",)
