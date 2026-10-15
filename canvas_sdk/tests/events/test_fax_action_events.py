from typing import Any

import pytest
from factory.django import DjangoModelFactory

from canvas_generated.messages.events_pb2 import Event as EventRequest
from canvas_generated.messages.events_pb2 import EventType
from canvas_sdk.events.base import Event
from canvas_sdk.test_utils.factories import (
    ImagingOrderActionEventFactory,
    IntegrationTaskActionEventFactory,
    LabOrderActionEventFactory,
    NoteActionEventFactory,
    ReferralActionEventFactory,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("event_factory", "target_type", "event_prefix"),
    [
        (NoteActionEventFactory, "NoteActionEvent", "NOTE_ACTION_EVENT"),
        (ReferralActionEventFactory, "ReferralActionEvent", "REFERRAL_ACTION_EVENT"),
        (ImagingOrderActionEventFactory, "ImagingOrderActionEvent", "IMAGING_ORDER_ACTION_EVENT"),
        (LabOrderActionEventFactory, "LabOrderActionEvent", "LAB_ORDER_ACTION_EVENT"),
        (
            IntegrationTaskActionEventFactory,
            "IntegrationTaskActionEvent",
            "INTEGRATION_TASK_ACTION_EVENT",
        ),
    ],
)
@pytest.mark.parametrize("action", ["CREATED", "UPDATED"])
def test_action_event_events_resolve_their_target(
    event_factory: type[DjangoModelFactory[Any]],
    target_type: str,
    event_prefix: str,
    action: str,
) -> None:
    """Each fax action event type is a named event whose target loads the action event."""
    action_event = event_factory.create()
    event_name = f"{event_prefix}_{action}"

    event = Event(
        EventRequest(type=event_name, target=str(action_event.id), target_type=target_type)
    )

    assert event.type == EventType.Value(event_name)
    assert event.name == event_name
    assert event.target.instance == action_event
