from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.commands.commands.goal import GoalCommand


class CloseGoalCommand(BaseCommand):
    class Meta:
        key = "closeGoal"
        commit_required_fields = ("goal_id",)

    goal_id: int | None = None
    achievement_status: GoalCommand.AchievementStatus | None = None
    progress: str | None = None

    @property
    def values(self) -> dict:
        return {
            "goal_id": self.goal_id,
            "achievement_status": (
                self.achievement_status.value if self.achievement_status else None
            ),
            "progress": self.progress,
        }
