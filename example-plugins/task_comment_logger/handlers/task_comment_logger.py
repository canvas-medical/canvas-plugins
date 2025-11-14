from canvas_sdk.effects import Effect
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.v1.data.task import NoteTask, Task, TaskComment
from logger import log


class TaskCommentLoggerHandler(BaseHandler):
    """
    Logs all comments associated with a task, including the original internal comment
    from the NoteTask and any subsequently added TaskComments.

    This handler demonstrates how to work with the NoteTask model to access
    the internal_comment field that was entered during task creation.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.TASK_CREATED),
        EventType.Name(EventType.TASK_UPDATED),
        EventType.Name(EventType.TASK_COMMENT_CREATED),
        EventType.Name(EventType.TASK_COMMENT_UPDATED),
    ]

    def compute(self) -> list[Effect]:
        """Log all comments for the task when task or comment events occur."""
        # Get the task ID from the event context
        task_id = self.event.context.get("task_id")

        if not task_id:
            log.warning("[TaskCommentLogger] No task_id found in event context")
            return []

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            log.error(f"[TaskCommentLogger] Task with id {task_id} not found")
            return []

        # Collect all comments
        comments = []

        # Get the original internal comment from NoteTask (if it exists)
        note_tasks = NoteTask.objects.filter(task=task)
        for note_task in note_tasks:
            if note_task.internal_comment:
                comments.append({
                    "type": "internal_comment",
                    "created": note_task.created,
                    "author": note_task.originator.get_full_name() if note_task.originator else "Unknown",
                    "content": note_task.internal_comment,
                })

        # Get all TaskComments
        task_comments = TaskComment.objects.filter(task=task).order_by("created")
        for task_comment in task_comments:
            comments.append({
                "type": "task_comment",
                "created": task_comment.created,
                "author": task_comment.creator.name if task_comment.creator else "Unknown",
                "content": task_comment.body,
            })

        # Sort all comments by creation time
        comments.sort(key=lambda x: x["created"])

        # Log the comments
        log.info(f"[TaskCommentLogger] Task '{task.title}' (ID: {task.id}) has {len(comments)} comment(s):")
        for i, comment in enumerate(comments, 1):
            log.info(
                f"  {i}. [{comment['type']}] {comment['author']} "
                f"({comment['created'].strftime('%Y-%m-%d %H:%M:%S')}): {comment['content']}"
            )

        return []
