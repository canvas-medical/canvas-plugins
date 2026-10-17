from enum import StrEnum
from uuid import UUID

from pydantic import Field

from canvas_sdk.effects._config_crud import ConfigCrudEffect


class PostingRuleBehavior(StrEnum):
    """What an ERA posting rule does with a matching adjustment."""

    WRITE_OFF = "write_off"
    NON_WRITE_OFF = "non_write_off"
    TRANSFER = "transfer"


class PostingRulePayerOrder(StrEnum):
    """Which payer position a posting rule applies to."""

    PRIMARY = "primary"
    SUPPLEMENTARY = "supplementary"


class PostingRule(ConfigCrudEffect):
    """Create, update, or delete an ERA posting rule.

    ``id`` is the rule's ``dbid``. A blank ``adjustment_code`` matches every code in
    the group; a null ``insurer_id`` applies the rule to every insurer. Preset rules
    cannot be deleted.
    """

    class Meta:
        effect_type = "POSTING_RULE"

    _entity_label: str = "posting rule"
    _create_required: tuple[str, ...] = ("description", "adjustment_group", "behavior")

    description: str | None = None
    adjustment_group: str | None = None
    adjustment_code: str | None = None
    behavior: PostingRuleBehavior | None = Field(default=None, strict=False)
    payer_order: PostingRulePayerOrder | None = Field(default=None, strict=False)
    insurer_id: str | UUID | None = None
    automated_action_review: bool | None = None


__exports__ = ("PostingRule", "PostingRuleBehavior", "PostingRulePayerOrder")
