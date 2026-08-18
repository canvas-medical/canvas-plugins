import json
from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    CommittableModelManager,
    CommittableQuerySet,
    IdentifiableModel,
)


def _get_text(node: dict) -> str:
    return cast(str, node.get("leaves", [{"text": ""}])[0].get("text", ""))


def _get_inline(node: dict) -> str:
    return f"{node.get('data', {}).get('concept', '')} '"


def string_from_narrative_json(narrative_json: str | dict | None) -> str:
    """Render a Slate ``narrative_json`` document as a plain string (ported from home-app)."""
    narrative = ""

    if not narrative_json:
        return narrative

    # The value may be a JSON string or an already-parsed object depending on where it's read from.
    if isinstance(narrative_json, str):
        try:
            narrative_json = json.loads(narrative_json)
        except ValueError:
            return cast(str, narrative_json)

    if isinstance(narrative_json, str):
        return narrative_json

    nodes = narrative_json.get("document", {}).get("nodes", [])

    for node in nodes:
        if node.get("object") == "text":
            narrative += _get_text(node)

        if node.get("object") == "inline":
            narrative += _get_inline(node)

        if node.get("object") == "block":
            for block_node in node.get("nodes", []):
                if block_node.get("object") == "text":
                    narrative += _get_text(block_node)

                if block_node.get("object") == "inline":
                    narrative += _get_inline(block_node)

            if nodes.index(node) != len(nodes) - 1:
                # add a carriage return between each paragraph block (except the last one)
                narrative += "\n"

    return narrative


class HistoryOfPresentIllness(AuditedModel, IdentifiableModel):
    """History of Present Illness (HPI) recorded on a note."""

    class Meta:
        db_table = "canvas_sdk_data_api_historyofpresentillness_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="histories_of_present_illness"
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="histories_of_present_illness"
    )
    legacy_narrative = models.TextField(default="", blank=True, db_column="narrative")
    narrative_json = models.JSONField(null=True, blank=True)

    @property
    def narrative(self) -> str:
        """The HPI narrative as a string.

        Prefers ``legacy_narrative`` (populated by commands created before the commands SDK);
        otherwise renders the structured ``narrative_json``, so callers only read one field.
        """
        if self.legacy_narrative:
            return self.legacy_narrative
        return string_from_narrative_json(self.narrative_json)


__exports__ = ("HistoryOfPresentIllness",)
