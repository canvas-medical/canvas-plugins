from django.db import models

from canvas_sdk.v1.data.base import TimestampedModel
from canvas_sdk.v1.data.coverage import Transactor


class PostingRuleBehavior(models.TextChoices):
    """What a PostingRule does with a matching adjustment."""

    WRITE_OFF = "write_off", "Write off adjustment"
    NON_WRITE_OFF = "non_write_off", "Non write off adjustment"
    TRANSFER = "transfer", "Transfer adjustment to next payer"


class PostingRulePayerOrder(models.TextChoices):
    """Which payer position a PostingRule applies to."""

    PRIMARY = "primary", "Primary"
    SUPPLEMENTARY = "supplementary", "Supplementary"


class PostingRule(TimestampedModel):
    """An ERA posting rule mapping an adjustment group/code to a posting behavior."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_postingrule_001"

    description = models.CharField(max_length=500)
    adjustment_group = models.CharField(max_length=3)
    adjustment_code = models.CharField(max_length=3, blank=True)
    behavior = models.CharField(max_length=13, choices=PostingRuleBehavior.choices)
    payer_order = models.CharField(max_length=13, choices=PostingRulePayerOrder.choices, blank=True)
    transactor = models.ForeignKey(
        Transactor,
        on_delete=models.DO_NOTHING,
        related_name="posting_rules",
        null=True,
    )
    automated_action_review = models.BooleanField(default=False)
    is_preset = models.BooleanField(default=False)


__exports__ = ("PostingRule", "PostingRuleBehavior", "PostingRulePayerOrder")
