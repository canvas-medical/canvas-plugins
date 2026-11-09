import json

import pytest
from canvas__agent_runner_poc.handlers.intake_trigger import DocumentIntakeTrigger

from canvas_sdk.effects import EffectType
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.test_utils.factories import IntegrationTaskFactory


@pytest.mark.django_db
def test_a_received_document_starts_intake_on_it() -> None:
    """Each incoming document on a listed channel gets its own run, keyed on the document."""
    document = IntegrationTaskFactory.create(patient=None)
    event = Event(
        EventRequest(
            type=EventType.DOCUMENT_RECEIVED,
            target=str(document.id),
            context=json.dumps(
                {"document": {"id": str(document.id), "channel": "fax"}, "patient": None}
            ),
        )
    )

    [effect] = DocumentIntakeTrigger(event, {"INTAKE_CHANNELS": "fax"}).compute()

    assert effect.type == EffectType.RUN_AGENT
    data = json.loads(effect.payload)["data"]
    assert data["agent_id"].endswith(":DocumentIntakeAgent")
    assert (data["scope"], data["document_id"], data["patient_id"]) == (
        "document",
        str(document.id),
        None,
    )


def _received(channel: str) -> Event:
    document = IntegrationTaskFactory.create(patient=None)
    return Event(
        EventRequest(
            type=EventType.DOCUMENT_RECEIVED,
            target=str(document.id),
            context=json.dumps({"document": {"id": str(document.id), "channel": channel}}),
        )
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("channels", "channel", "runs"),
    [
        ("", "document_upload", 0),
        ("", "fax", 0),
        ("fax", "fax", 1),
        ("fax", "document_upload", 0),
        (" Fax, lab ", "lab", 1),
    ],
)
def test_intake_runs_only_on_the_channels_an_operator_lists(
    channels: str, channel: str, runs: int
) -> None:
    """Intake runs on the channels INTAKE_CHANNELS lists, and is off until it lists one.

    Every run sends a document to the model, so a fresh install starts none: uploads and lab
    feeds would otherwise each start one.
    """
    secrets = {"INTAKE_CHANNELS": channels} if channels else {}

    effects = DocumentIntakeTrigger(_received(channel), secrets).compute()

    assert len(effects) == runs
