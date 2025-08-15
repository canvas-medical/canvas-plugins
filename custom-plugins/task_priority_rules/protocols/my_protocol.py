import json

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.task import TaskPriority, UpdateTask
from canvas_sdk.events import Event, EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data import Task
from canvas_sdk.v1.data.team import TeamResponsibility
from logger import log

def json_default_serializer(o):
    """A helper to serialize objects that json.dumps doesn't know how to handle."""
    return str(o)

# Inherit from BaseProtocol to properly get registered for events
class Protocol(BaseProtocol):
    """A protocol that sets or clears task priority based on business rules."""

    # This protocol needs to respond to both task creation and updates.
    RESPONDS_TO = [
        EventType.Name(EventType.TASK_CREATED),
        EventType.Name(EventType.TASK_UPDATED),
    ]

    def compute(self) -> list[Effect]:
        try:

            event_data = {
                "type": str(self.event.type),
                "context": self.event.context,
                "event_name": self.event.name,
                "target": str(self.event.target),
            }
            log.info(
                f"Received event: {json.dumps(event_data, indent=2, default=json_default_serializer)}"
            )
        except Exception as e:
            log.error(f"Failed to serialize event for logging: {e}")

        """This method gets called when a task is created or updated."""
        if self.event.type == EventType.TASK_CREATED:
            return self.handle_task_created()
        if self.event.type == EventType.TASK_UPDATED:
            return self.handle_task_updated()
        return []

    def handle_task_created(self) -> list[Effect]:
        """Sets priority for new refill request tasks."""
        task_id = self.event.target.id
        try:
            task = Task.objects.get(id=task_id)
            log.info(
                f"Successfully fetched task details: {json.dumps(task.__dict__, indent=2, default=json_default_serializer)}"
            )
        except Exception as e:
            log.error(f"An error occurred while fetching or logging the task: {e}")
            return []

        log.info(f"Team responsibilities: {task.team.responsibilities}")

        has_responsibility = (
                task.team.responsibilities and
                TeamResponsibility.PROCESS_REFILL_REQUESTS in task.team.responsibilities
        )

        if has_responsibility:
            if task.priority != TaskPriority.URGENT.value:
                log.info(f"Task {task.id} matches refill criteria. Setting priority to Urgent.")
                return [UpdateTask(id=str(task.id), priority=TaskPriority.URGENT).apply()]
            else:
                log.info(f"Task {task.id} already has Urgent priority. No action needed.")

        return []
        # is_refill_request = context.get("title") == "Refill requests"
        # team_info = context.get("team") or {}
        # is_correct_team_assigned = (
        #     team_info.get("external_id") == "PROCESS_REFILL_REQUESTS"
        # )
        #
        # if is_refill_request and is_correct_team_assigned:
        #     log.info(
        #         f"Task {task_id} is a refill request for the correct team. "
        #         "Setting priority to Urgent."
        #     )
        #     return [UpdateTask(id=task_id, priority=TaskPriority.URGENT)]
        #
        # return []

    def handle_task_updated(self) -> list[Effect]:
        """Clears priority if the team assignment is removed."""
        log.info("Handling a task update event.")
        context = self.event.context
        task_id = self.event.target.id

        # Simplified Rule: If the task has no team, its priority should be None.
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            log.warning(f"Task with ID {task_id} not found in the database.")
            return []

        if not task.team.id:
            # To prevent infinite update loops, only act if priority is not already cleared.
            if task.priority is not None:
                log.info(f"Task {task.id} has no team assignment. Clearing priority.")
                return [UpdateTask(id=str(task.id), priority=None).apply()]
            else:
                log.info(f"Task {task.id} has no team and priority is already clear. No action needed.")
                # If there's no team and priority is already None, we are done.
                return []

        return []
        # task_id = self.event.target.id
        # log.info("TRYING to fectch task/UPDATE")
        # try:
        #     task = Task.objects.get(id=task_id)
        #     log.info(
        #         f"Successfully fetched task details: {json.dumps(task.__dict__, indent=2, default=json_default_serializer)}"
        #     )
        # except Exception as e:
        #     log.error(f"An error occurred while fetching or logging the task: {e}")
        #     return []

        # task = Task.objects.get(id=task_id)
        # log.info(
        #     f"Successfully fetched task details (UPDATE): {json.dumps(task.__dict__, indent=2, default=json_default_serializer)}"
        # )

        # task_id = context.get("id")
        # if not task_id:
        #     log.warning("Task update event context did not contain an 'id'.")
        #     return []
        #
        # # Rule: If the team assignment was removed, clear the priority.
        # original_team_id = context.get("original", {}).get("team_id")
        # current_team_id = context.get("team_id")
        # team_was_removed = original_team_id and not current_team_id
        #
        # if team_was_removed:
        #     log.info(f"Team assignment was removed from task {task_id}. Clearing priority.")
        #     return [UpdateTask(id=task_id, priority=None)]

        # return []
