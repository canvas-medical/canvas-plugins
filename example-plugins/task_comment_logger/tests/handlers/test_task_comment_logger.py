"""Tests for task_comment_logger.handlers.task_comment_logger module."""

from datetime import datetime
from unittest.mock import MagicMock, Mock, patch
from uuid import uuid4

from canvas_sdk.events import EventType
from task_comment_logger.handlers.task_comment_logger import TaskCommentLoggerHandler


class TestTaskCommentLoggerHandler:
    """Tests for TaskCommentLoggerHandler class."""

    def test_handler_responds_to_correct_events(self):
        """Test that handler is configured to respond to task and comment events."""
        expected_events = [
            EventType.Name(EventType.TASK_CREATED),
            EventType.Name(EventType.TASK_UPDATED),
            EventType.Name(EventType.TASK_COMMENT_CREATED),
            EventType.Name(EventType.TASK_COMMENT_UPDATED),
        ]
        assert expected_events == TaskCommentLoggerHandler.RESPONDS_TO

    @patch("task_comment_logger.handlers.task_comment_logger.Task")
    @patch("task_comment_logger.handlers.task_comment_logger.NoteTask")
    @patch("task_comment_logger.handlers.task_comment_logger.TaskComment")
    @patch("task_comment_logger.handlers.task_comment_logger.log")
    def test_task_created_event_with_no_comments(
        self, mock_log, mock_task_comment, mock_note_task, mock_task
    ):
        """Test handling TASK_CREATED event when task has no comments."""
        # Setup
        task_id = str(uuid4())
        mock_task_obj = Mock()
        mock_task_obj.id = task_id
        mock_task_obj.title = "New Task"
        mock_task.objects.get.return_value = mock_task_obj

        # No NoteTask internal comments
        mock_note_task.objects.filter.return_value = []

        # No TaskComments
        mock_task_comment.objects.filter.return_value.order_by.return_value = []

        mock_event = MagicMock()
        mock_event.type = "TASK_CREATED"
        mock_event.context = {}
        mock_event.target = Mock()
        mock_event.target.id = task_id
        mock_event.target.type = "Task"

        handler = TaskCommentLoggerHandler(event=mock_event)

        # Execute
        result = handler.compute()

        # Verify
        assert result == []
        # Check debug logs were called
        assert mock_log.info.call_count >= 4  # 3 debug + 1 summary
        # Check the task summary log
        mock_log.info.assert_any_call(
            f"[TaskCommentLogger] Task 'New Task' (ID: {task_id}) has 0 comment(s):"
        )

    @patch("task_comment_logger.handlers.task_comment_logger.Task")
    @patch("task_comment_logger.handlers.task_comment_logger.NoteTask")
    @patch("task_comment_logger.handlers.task_comment_logger.TaskComment")
    @patch("task_comment_logger.handlers.task_comment_logger.log")
    def test_task_updated_event_with_internal_comment(
        self, mock_log, mock_task_comment, mock_note_task, mock_task
    ):
        """Test handling TASK_UPDATED event when task has internal comment."""
        # Setup
        task_id = str(uuid4())
        mock_task_obj = Mock()
        mock_task_obj.id = task_id
        mock_task_obj.title = "Updated Task"
        mock_task.objects.get.return_value = mock_task_obj

        # Setup NoteTask with internal comment
        mock_originator = Mock()
        mock_originator.get_full_name.return_value = "Dr. Smith"
        mock_note_task_obj = Mock()
        mock_note_task_obj.internal_comment = "Patient needs follow-up"
        mock_note_task_obj.created = datetime(2025, 1, 15, 10, 0, 0)
        mock_note_task_obj.originator = mock_originator
        mock_note_task.objects.filter.return_value = [mock_note_task_obj]

        # No TaskComments
        mock_task_comment.objects.filter.return_value.order_by.return_value = []

        mock_event = MagicMock()
        mock_event.type = "TASK_UPDATED"
        mock_event.context = {}
        mock_event.target = Mock()
        mock_event.target.id = task_id
        mock_event.target.type = "Task"

        handler = TaskCommentLoggerHandler(event=mock_event)

        # Execute
        result = handler.compute()

        # Verify
        assert result == []
        # Check the task summary log
        mock_log.info.assert_any_call(
            f"[TaskCommentLogger] Task 'Updated Task' (ID: {task_id}) has 1 comment(s):"
        )
        # Check internal comment was logged
        mock_log.info.assert_any_call(
            "  1. [internal_comment] Dr. Smith (2025-01-15 10:00:00): Patient needs follow-up"
        )

    @patch("task_comment_logger.handlers.task_comment_logger.Task")
    @patch("task_comment_logger.handlers.task_comment_logger.NoteTask")
    @patch("task_comment_logger.handlers.task_comment_logger.TaskComment")
    @patch("task_comment_logger.handlers.task_comment_logger.log")
    def test_task_comment_created_event(
        self, mock_log, mock_task_comment_model, mock_note_task, mock_task
    ):
        """Test handling TASK_COMMENT_CREATED event."""
        # Setup
        task_id = str(uuid4())
        comment_id = str(uuid4())

        mock_task_obj = Mock()
        mock_task_obj.id = task_id
        mock_task_obj.title = "Task with Comment"
        mock_task.objects.get.return_value = mock_task_obj

        # Setup TaskComment lookup
        mock_comment_obj = Mock()
        mock_comment_obj.task = Mock()
        mock_comment_obj.task.id = task_id
        mock_task_comment_model.objects.get.return_value = mock_comment_obj

        # No NoteTask internal comments
        mock_note_task.objects.filter.return_value = []

        # Setup TaskComment
        mock_creator = Mock()
        mock_creator.name = "Nurse Johnson"
        mock_task_comment_obj = Mock()
        mock_task_comment_obj.body = "Called patient"
        mock_task_comment_obj.created = datetime(2025, 1, 16, 14, 0, 0)
        mock_task_comment_obj.creator = mock_creator
        mock_task_comment_model.objects.filter.return_value.order_by.return_value = [
            mock_task_comment_obj
        ]

        mock_event = MagicMock()
        mock_event.type = "TASK_COMMENT_CREATED"
        mock_event.context = {}
        mock_event.target = Mock()
        mock_event.target.id = comment_id
        mock_event.target.type = "TaskComment"

        handler = TaskCommentLoggerHandler(event=mock_event)

        # Execute
        result = handler.compute()

        # Verify
        assert result == []
        mock_task_comment_model.objects.get.assert_called_once_with(id=comment_id)
        mock_log.info.assert_any_call(
            f"[TaskCommentLogger] Task 'Task with Comment' (ID: {task_id}) has 1 comment(s):"
        )
        mock_log.info.assert_any_call(
            "  1. [task_comment] Nurse Johnson (2025-01-16 14:00:00): Called patient"
        )

    @patch("task_comment_logger.handlers.task_comment_logger.TaskComment")
    @patch("task_comment_logger.handlers.task_comment_logger.log")
    def test_task_comment_event_comment_not_found(self, mock_log, mock_task_comment_model):
        """Test handling TASK_COMMENT event when comment doesn't exist."""
        # Setup
        from django.core.exceptions import ObjectDoesNotExist

        comment_id = str(uuid4())

        mock_task_comment_model.DoesNotExist = type("DoesNotExist", (ObjectDoesNotExist,), {})
        mock_task_comment_model.objects.get.side_effect = mock_task_comment_model.DoesNotExist

        mock_event = MagicMock()
        mock_event.type = "TASK_COMMENT_UPDATED"
        mock_event.context = {}
        mock_event.target = Mock()
        mock_event.target.id = comment_id
        mock_event.target.type = "TaskComment"

        handler = TaskCommentLoggerHandler(event=mock_event)

        # Execute
        result = handler.compute()

        # Verify
        assert result == []
        mock_log.error.assert_called_once_with(
            f"[TaskCommentLogger] TaskComment with id {comment_id} not found"
        )

    @patch("task_comment_logger.handlers.task_comment_logger.TaskComment")
    @patch("task_comment_logger.handlers.task_comment_logger.log")
    def test_task_comment_event_no_associated_task(
        self, mock_log, mock_task_comment_model
    ):
        """Test handling TASK_COMMENT event when TaskComment has no task."""
        # Setup
        comment_id = str(uuid4())

        mock_comment_obj = Mock()
        mock_comment_obj.task = None
        mock_task_comment_model.objects.get.return_value = mock_comment_obj

        mock_event = MagicMock()
        mock_event.type = "TASK_COMMENT_CREATED"
        mock_event.context = {}
        mock_event.target = Mock()
        mock_event.target.id = comment_id
        mock_event.target.type = "TaskComment"

        handler = TaskCommentLoggerHandler(event=mock_event)

        # Execute
        result = handler.compute()

        # Verify
        assert result == []
        mock_log.warning.assert_called_once_with("[TaskCommentLogger] No task_id found")

    @patch("task_comment_logger.handlers.task_comment_logger.Task")
    @patch("task_comment_logger.handlers.task_comment_logger.log")
    def test_unknown_event_type(self, mock_log, mock_task):
        """Test handling unknown event type."""
        # Setup
        mock_event = MagicMock()
        mock_event.type = "UNKNOWN_EVENT"
        mock_event.context = {}
        mock_event.target = Mock()
        mock_event.target.id = str(uuid4())
        mock_event.target.type = "Unknown"

        handler = TaskCommentLoggerHandler(event=mock_event)

        # Execute
        result = handler.compute()

        # Verify
        assert result == []
        mock_log.warning.assert_called_once_with("[TaskCommentLogger] No task_id found")

    @patch("task_comment_logger.handlers.task_comment_logger.Task")
    @patch("task_comment_logger.handlers.task_comment_logger.log")
    def test_task_not_found(self, mock_log, mock_task):
        """Test handling when task is not found in database."""
        # Setup
        from django.core.exceptions import ObjectDoesNotExist

        task_id = str(uuid4())

        mock_task.DoesNotExist = type("DoesNotExist", (ObjectDoesNotExist,), {})
        mock_task.objects.get.side_effect = mock_task.DoesNotExist

        mock_event = MagicMock()
        mock_event.type = "TASK_CREATED"
        mock_event.context = {}
        mock_event.target = Mock()
        mock_event.target.id = task_id
        mock_event.target.type = "Task"

        handler = TaskCommentLoggerHandler(event=mock_event)

        # Execute
        result = handler.compute()

        # Verify
        assert result == []
        mock_log.error.assert_called_once_with(
            f"[TaskCommentLogger] Task with id {task_id} not found"
        )

    @patch("task_comment_logger.handlers.task_comment_logger.Task")
    @patch("task_comment_logger.handlers.task_comment_logger.NoteTask")
    @patch("task_comment_logger.handlers.task_comment_logger.TaskComment")
    @patch("task_comment_logger.handlers.task_comment_logger.log")
    def test_multiple_comments_sorted_chronologically(
        self, mock_log, mock_task_comment, mock_note_task, mock_task
    ):
        """Test that comments are sorted chronologically."""
        # Setup
        task_id = str(uuid4())
        mock_task_obj = Mock()
        mock_task_obj.id = task_id
        mock_task_obj.title = "Task with Multiple Comments"
        mock_task.objects.get.return_value = mock_task_obj

        # Setup NoteTask with internal comment (earliest)
        mock_originator = Mock()
        mock_originator.get_full_name.return_value = "Dr. Smith"
        mock_note_task_obj = Mock()
        mock_note_task_obj.internal_comment = "Initial comment"
        mock_note_task_obj.created = datetime(2025, 1, 15, 10, 0, 0)
        mock_note_task_obj.originator = mock_originator
        mock_note_task.objects.filter.return_value = [mock_note_task_obj]

        # Setup TaskComments (later timestamps)
        mock_creator1 = Mock()
        mock_creator1.name = "Nurse Johnson"
        mock_comment1 = Mock()
        mock_comment1.body = "Second comment"
        mock_comment1.created = datetime(2025, 1, 16, 14, 0, 0)
        mock_comment1.creator = mock_creator1

        mock_creator2 = Mock()
        mock_creator2.name = "Dr. Smith"
        mock_comment2 = Mock()
        mock_comment2.body = "Third comment"
        mock_comment2.created = datetime(2025, 1, 17, 9, 0, 0)
        mock_comment2.creator = mock_creator2

        mock_task_comment.objects.filter.return_value.order_by.return_value = [
            mock_comment1,
            mock_comment2,
        ]

        mock_event = MagicMock()
        mock_event.type = "TASK_UPDATED"
        mock_event.context = {}
        mock_event.target = Mock()
        mock_event.target.id = task_id
        mock_event.target.type = "Task"

        handler = TaskCommentLoggerHandler(event=mock_event)

        # Execute
        result = handler.compute()

        # Verify
        assert result == []
        mock_log.info.assert_any_call(
            f"[TaskCommentLogger] Task 'Task with Multiple Comments' (ID: {task_id}) has 3 comment(s):"
        )
        # Verify chronological order
        mock_log.info.assert_any_call(
            "  1. [internal_comment] Dr. Smith (2025-01-15 10:00:00): Initial comment"
        )
        mock_log.info.assert_any_call(
            "  2. [task_comment] Nurse Johnson (2025-01-16 14:00:00): Second comment"
        )
        mock_log.info.assert_any_call(
            "  3. [task_comment] Dr. Smith (2025-01-17 09:00:00): Third comment"
        )
