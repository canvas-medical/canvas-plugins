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
    def test_compute_with_no_task_id(self, mock_log, mock_task_comment, mock_note_task, mock_task):
        """Test that handler logs warning when task_id is missing from event context."""
        # Setup
        mock_event = MagicMock()
        mock_event.context = {}

        handler = TaskCommentLoggerHandler(event=mock_event)

        # Execute
        result = handler.compute()

        # Verify
        assert result == []
        mock_log.warning.assert_called_once_with("[TaskCommentLogger] No task_id found in event context")
        mock_task.objects.get.assert_not_called()

    @patch("task_comment_logger.handlers.task_comment_logger.Task")
    @patch("task_comment_logger.handlers.task_comment_logger.log")
    def test_compute_with_nonexistent_task(self, mock_log, mock_task):
        """Test that handler logs error when task is not found."""
        # Setup
        from django.core.exceptions import ObjectDoesNotExist

        task_id = str(uuid4())
        mock_event = MagicMock()
        mock_event.context = {"task_id": task_id}

        # Create a proper DoesNotExist exception class
        mock_task.DoesNotExist = type('DoesNotExist', (ObjectDoesNotExist,), {})
        mock_task.objects.get.side_effect = mock_task.DoesNotExist

        handler = TaskCommentLoggerHandler(event=mock_event)

        # Execute
        result = handler.compute()

        # Verify
        assert result == []
        mock_log.error.assert_called_once_with(f"[TaskCommentLogger] Task with id {task_id} not found")

    @patch("task_comment_logger.handlers.task_comment_logger.Task")
    @patch("task_comment_logger.handlers.task_comment_logger.NoteTask")
    @patch("task_comment_logger.handlers.task_comment_logger.TaskComment")
    @patch("task_comment_logger.handlers.task_comment_logger.log")
    def test_compute_with_internal_comment_only(
        self, mock_log, mock_task_comment, mock_note_task, mock_task
    ):
        """Test logging when task has only an internal comment from NoteTask."""
        # Setup task
        task_id = str(uuid4())
        mock_task_obj = Mock()
        mock_task_obj.id = task_id
        mock_task_obj.title = "Test Task"
        mock_task.objects.get.return_value = mock_task_obj

        # Setup NoteTask with internal comment
        mock_originator = Mock()
        mock_originator.get_full_name.return_value = "Dr. Smith"
        mock_note_task_obj = Mock()
        mock_note_task_obj.internal_comment = "Patient needs follow-up"
        mock_note_task_obj.created = datetime(2025, 1, 15, 10, 30, 0)
        mock_note_task_obj.originator = mock_originator
        mock_note_task.objects.filter.return_value = [mock_note_task_obj]

        # No TaskComments
        mock_task_comment.objects.filter.return_value.order_by.return_value = []

        mock_event = MagicMock()
        mock_event.context = {"task_id": task_id}

        handler = TaskCommentLoggerHandler(event=mock_event)

        # Execute
        result = handler.compute()

        # Verify
        assert result == []
        mock_log.info.assert_any_call(
            "[TaskCommentLogger] Task 'Test Task' (ID: " + task_id + ") has 1 comment(s):"
        )

    @patch("task_comment_logger.handlers.task_comment_logger.Task")
    @patch("task_comment_logger.handlers.task_comment_logger.NoteTask")
    @patch("task_comment_logger.handlers.task_comment_logger.TaskComment")
    @patch("task_comment_logger.handlers.task_comment_logger.log")
    def test_compute_with_multiple_comments(
        self, mock_log, mock_task_comment, mock_note_task, mock_task
    ):
        """Test logging when task has both internal comment and TaskComments."""
        # Setup task
        task_id = str(uuid4())
        mock_task_obj = Mock()
        mock_task_obj.id = task_id
        mock_task_obj.title = "Follow up on labs"
        mock_task.objects.get.return_value = mock_task_obj

        # Setup NoteTask with internal comment
        mock_originator = Mock()
        mock_originator.get_full_name.return_value = "Dr. Smith"
        mock_note_task_obj = Mock()
        mock_note_task_obj.internal_comment = "Abnormal lipid panel"
        mock_note_task_obj.created = datetime(2025, 1, 15, 10, 0, 0)
        mock_note_task_obj.originator = mock_originator
        mock_note_task.objects.filter.return_value = [mock_note_task_obj]

        # Setup TaskComments
        mock_creator1 = Mock()
        mock_creator1.name = "Nurse Johnson"
        mock_comment1 = Mock()
        mock_comment1.body = "Called patient"
        mock_comment1.created = datetime(2025, 1, 16, 14, 0, 0)
        mock_comment1.creator = mock_creator1

        mock_creator2 = Mock()
        mock_creator2.name = "Dr. Smith"
        mock_comment2 = Mock()
        mock_comment2.body = "Scheduled follow-up"
        mock_comment2.created = datetime(2025, 1, 17, 9, 0, 0)
        mock_comment2.creator = mock_creator2

        mock_task_comment.objects.filter.return_value.order_by.return_value = [
            mock_comment1,
            mock_comment2,
        ]

        mock_event = MagicMock()
        mock_event.context = {"task_id": task_id}

        handler = TaskCommentLoggerHandler(event=mock_event)

        # Execute
        result = handler.compute()

        # Verify
        assert result == []
        # Check that the summary was logged
        mock_log.info.assert_any_call(
            "[TaskCommentLogger] Task 'Follow up on labs' (ID: " + task_id + ") has 3 comment(s):"
        )

    @patch("task_comment_logger.handlers.task_comment_logger.Task")
    @patch("task_comment_logger.handlers.task_comment_logger.NoteTask")
    @patch("task_comment_logger.handlers.task_comment_logger.TaskComment")
    @patch("task_comment_logger.handlers.task_comment_logger.log")
    def test_compute_with_no_comments(self, mock_log, mock_task_comment, mock_note_task, mock_task):
        """Test logging when task has no comments."""
        # Setup task
        task_id = str(uuid4())
        mock_task_obj = Mock()
        mock_task_obj.id = task_id
        mock_task_obj.title = "Empty Task"
        mock_task.objects.get.return_value = mock_task_obj

        # No NoteTask internal comments
        mock_note_task.objects.filter.return_value = []

        # No TaskComments
        mock_task_comment.objects.filter.return_value.order_by.return_value = []

        mock_event = MagicMock()
        mock_event.context = {"task_id": task_id}

        handler = TaskCommentLoggerHandler(event=mock_event)

        # Execute
        result = handler.compute()

        # Verify
        assert result == []
        mock_log.info.assert_called_once_with(
            "[TaskCommentLogger] Task 'Empty Task' (ID: " + task_id + ") has 0 comment(s):"
        )
