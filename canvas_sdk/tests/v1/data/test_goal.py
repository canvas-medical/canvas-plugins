import pytest

from canvas_sdk.test_utils.factories import UpdateGoalFactory
from canvas_sdk.v1.data.goal import (
    GoalAchievementStatus,
    GoalLifecycleStatus,
    GoalPriority,
    UpdateGoal,
)


def test_update_goal_exposes_its_fields() -> None:
    """An UpdateGoal exposes its goal FK, statuses, priority, and progress."""
    update = UpdateGoal()
    update.patient_id = 11
    update.note_id = 22
    update.goal_id = 33
    update.lifecycle_status = GoalLifecycleStatus.COMPLETED
    update.achievement_status = GoalAchievementStatus.ACHIEVED
    update.priority = GoalPriority.HIGH
    update.progress = "Met target A1c"

    assert update.patient_id == 11
    assert update.note_id == 22
    assert update.goal_id == 33
    assert update.lifecycle_status == "completed"
    assert update.achievement_status == "achieved"
    assert update.priority == "high-priority"
    assert update.progress == "Met target A1c"


def test_update_goal_links_back_to_goal_via_updates() -> None:
    """The goal FK exposes a reverse `updates` accessor on Goal (mirroring home-app)."""
    from canvas_sdk.v1.data.goal import Goal

    accessor = UpdateGoal._meta.get_field("goal").remote_field.get_accessor_name()
    assert accessor == "updates"
    assert hasattr(Goal, "updates")


@pytest.mark.django_db
def test_update_goal_factory_round_trips_and_links_to_goal() -> None:
    """UpdateGoalFactory persists a linked update reachable via Goal's `updates` accessor."""
    update = UpdateGoalFactory.create(progress="Down to 6.8% A1c")

    fetched = UpdateGoal.objects.get(dbid=update.dbid)

    assert fetched.progress == "Down to 6.8% A1c"
    assert fetched.goal == update.goal
    assert fetched.note_id == update.note_id
    assert fetched.patient_id == update.patient_id
    assert list(update.goal.updates.all()) == [fetched]
