import json

import pytest
from canvas__agent_runner_poc.handlers.intake_trigger import DocumentIntakeTrigger

from canvas_sdk.effects import EffectType
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.test_utils.factories import IntegrationTaskFactory


@pytest.mark.django_db
def test_a_received_document_starts_intake_on_it() -> None:
    """Each incoming document gets its own run, keyed on the document."""
    document = IntegrationTaskFactory.create(patient=None)
    event = Event(
        EventRequest(
            type=EventType.DOCUMENT_RECEIVED,
            target=str(document.id),
            context=json.dumps({"document": {"id": str(document.id)}, "patient": None}),
        )
    )

    [effect] = DocumentIntakeTrigger(event).compute()

    assert effect.type == EffectType.RUN_AGENT
    data = json.loads(effect.payload)["data"]
    assert data["agent_id"].endswith(":DocumentIntakeAgent")
    assert (data["scope"], data["document_id"], data["patient_id"]) == (
        "document",
        str(document.id),
        None,
    )
