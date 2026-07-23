from canvas_sdk.effects.codings._base import CodingCrudEffect


class ReasonForVisitSettingCoding(CodingCrudEffect):
    """Effect to create/update/delete a Reason for Visit setting coding entry."""

    class Meta:
        effect_type = "REASON_FOR_VISIT_SETTING_CODING"

    _entity_label: str = "reason for visit setting coding"


__exports__ = ("ReasonForVisitSettingCoding",)
