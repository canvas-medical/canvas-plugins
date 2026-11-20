import datetime

import factory

from canvas_sdk.v1.data import (
    ClaimAssigneeEvent,
    ClaimCoverageEvent,
    ClaimCoverageEventType,
    ClaimSnoozeEvent,
    ClaimSnoozeState,
    ClaimStateChangeEvent,
)


class ClaimStateChangeEventFactory(factory.django.DjangoModelFactory[ClaimStateChangeEvent]):
    """Factory for creating a ClaimStateChangeEvent."""

    class Meta:
        model = ClaimStateChangeEvent

    claim = factory.SubFactory("canvas_sdk.test_utils.factories.ClaimFactory")
    queue_entered = factory.SubFactory("canvas_sdk.test_utils.factories.ClaimQueueFactory")
    queue_exited = None
    originator = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")


class ClaimCoverageEventFactory(factory.django.DjangoModelFactory[ClaimCoverageEvent]):
    """Factory for creating a ClaimCoverageEvent."""

    class Meta:
        model = ClaimCoverageEvent

    claim = factory.SubFactory("canvas_sdk.test_utils.factories.ClaimFactory")
    claim_coverage = factory.SubFactory(
        "canvas_sdk.test_utils.factories.ClaimCoverageFactory",
        claim=factory.SelfAttribute("..claim"),
    )
    event_type = ClaimCoverageEventType.ACTIVATE
    originator = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")


class ClaimAssigneeEventFactory(factory.django.DjangoModelFactory[ClaimAssigneeEvent]):
    """Factory for creating a ClaimAssigneeEvent."""

    class Meta:
        model = ClaimAssigneeEvent

    claim = factory.SubFactory("canvas_sdk.test_utils.factories.ClaimFactory")
    assignee = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    team = factory.SubFactory("canvas_sdk.test_utils.factories.TeamFactory")
    assignee_name = factory.LazyAttribute(
        lambda o: o.assignee.credentialed_name if o.assignee else ""
    )
    team_name = factory.LazyAttribute(lambda o: o.team.name if o.team else "")
    originator = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")


class ClaimSnoozeEventFactory(factory.django.DjangoModelFactory[ClaimSnoozeEvent]):
    """Factory for creating a ClaimSnoozeEvent."""

    class Meta:
        model = ClaimSnoozeEvent

    claim = factory.SubFactory("canvas_sdk.test_utils.factories.ClaimFactory")
    state = ClaimSnoozeState.SET
    date = datetime.date(2026, 12, 1)
    originator = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
