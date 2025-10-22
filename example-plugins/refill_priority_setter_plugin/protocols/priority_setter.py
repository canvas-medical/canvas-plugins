from canvas_sdk.effects import Effect
from canvas_sdk.v1.data.task import TaskPriority
from canvas_sdk.effects.task import UpdateTask
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data import Task, Team
from canvas_sdk.v1.data.team import TeamResponsibility
from canvas_sdk.commands import TaskCommand
from logger import log


class RefillTaskPriorityProtocol(BaseProtocol):
    """
    Protocol that automatically updates task priorities based on team responsibilities.
    
    This protocol listens for task creation and update events and automatically
    sets the priority to URGENT for tasks assigned to teams with refill processing
    responsibilities.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.TASK_CREATED),
        EventType.Name(EventType.TASK_UPDATED),
        EventType.Name(EventType.TASK_COMMAND__POST_UPDATE),
    ]

    def compute(self) -> list[Effect]:
        if self.event.type == EventType.TASK_COMMAND__POST_UPDATE:
            return self.update_task_priority_command()
        else:
            return self.update_task_priority()

    def update_task_priority_command(self) -> list[Effect]:
        """
        Updates the task priority based on the command context.
        
        Returns:
            List containing TaskCommand effect if priority needs updating, empty list otherwise.
        """
        # Extract team from command context
        assigned_to = self.context['fields']['assign_to']['value']
        team = None
        if 'team' in assigned_to:
            _, team_id = assigned_to.split('-')
            team = Team.objects.get(dbid=team_id)
        
        current_priority = self.context['fields']['priority'] or None
        
        return self._update_priority_if_needed(
            current_priority=current_priority,
            team=team,
            use_command=True
        )

    def update_task_priority(self) -> list[Effect]:
        """
        Updates the task priority based on the task.
        """
        task = Task.objects.get(id=self.target)
        
        return self._update_priority_if_needed(
            current_priority=task.priority,
            team=task.team,
            use_command=False
        )

    def _update_priority_if_needed(
        self, 
        current_priority: str | None, 
        team: Team | None, 
        use_command: bool
    ) -> list[Effect]:
        """
        Common logic for updating task priority.
        
        Business Rules:
        - Sets priority to URGENT for teams with refill processing responsibilities
        - Prevents downgrading from URGENT to None unless already URGENT
        - Only updates priority when a change is actually needed
        
        Args:
            current_priority: The current priority of the task
            team: The team assigned to the task
            use_command: Whether to use TaskCommand or UpdateTask effect
            
        Returns:
            List containing the appropriate effect if priority needs updating, empty list otherwise.
        """
        desired_priority = self._get_desired_priority(team)
        desired_priority_value = desired_priority.value if desired_priority else None

        log.info(f"Current priority: {current_priority}, Desired priority: {desired_priority_value}")
        
        if current_priority == desired_priority_value:
            return []

        # If the desired priority is None and the current priority is not URGENT, return early
        # This is to prevent the priority from being set to None if it is not already URGENT
        if not desired_priority_value and current_priority != TaskPriority.URGENT.value:
            return []

        log.info(f"Updating task {self.target} priority from '{current_priority}' to '{desired_priority_value}'.")
        
        if use_command:
            return [TaskCommand(command_uuid=self.target, priority=desired_priority).edit()]
        else:
            return [UpdateTask(id=self.target, priority=desired_priority).apply()]


    def _get_desired_priority(self, team: Team | None) -> TaskPriority | None:
        """
        Determines the correct priority for a task based on its team's responsibilities.
        
        Business Logic:
        - Teams with PROCESS_REFILL_REQUESTS responsibility should have URGENT priority
        - All other teams maintain their current priority (None)
        
        Args:
            team: The team assigned to the task, or None if unassigned
            
        Returns:
            TaskPriority.URGENT if team handles refill requests, None otherwise
        """
        if not team:
            return None

        if (
            team.responsibilities and
            TeamResponsibility.PROCESS_REFILL_REQUESTS in team.responsibilities
        ):
            return TaskPriority.URGENT

        return None