from unittest.mock import MagicMock, Mock

import pytest

from canvas_sdk.effects.protocol_card import ProtocolCard
from canvas_sdk.events import EventRequest, EventType
from task_completion_protocol_updater.protocols.task_completion_protocol import Protocol


class TestTaskCompletionProtocol:
    """Test the task completion protocol."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.event_request = EventRequest(
            type=EventType.TASK_COMPLETED,
            target="task-uuid-123",
            target_type="Task",
            context="{}",
        )

    def test_protocol_responds_to_task_completed_event(self) -> None:
        """Test that the protocol responds to TASK_COMPLETED events."""
        assert Protocol.RESPONDS_TO == EventType.Name(EventType.TASK_COMPLETED)

    def test_compute_returns_empty_when_no_task_found(self) -> None:
        """Test that compute returns empty list when no task instance is found."""
        protocol = Protocol(self.event_request)
        protocol.target.instance = None

        result = protocol.compute()

        assert result == []

    def test_compute_returns_empty_when_no_linked_protocol_card_label(self) -> None:
        """Test that compute returns empty list when task has no LINKED_PROTOCOL_CARD label."""
        # Mock task with labels but no LINKED_PROTOCOL_CARD
        mock_task = Mock()
        mock_label1 = Mock()
        mock_label1.name = "SOME_OTHER_LABEL"
        mock_label2 = Mock()
        mock_label2.name = "ANOTHER_LABEL"
        mock_task.labels.all.return_value = [mock_label1, mock_label2]
        mock_task.id = "task-uuid-123"

        protocol = Protocol(self.event_request)
        protocol.target.instance = mock_task

        result = protocol.compute()

        assert result == []

    def test_compute_returns_empty_when_no_protocol_card_key_label(self) -> None:
        """Test that compute returns empty list when task has LINKED_PROTOCOL_CARD but no PROTOCOL_CARD_{key} label."""
        # Mock task with LINKED_PROTOCOL_CARD but no PROTOCOL_CARD_{key}
        mock_task = Mock()
        mock_label1 = Mock()
        mock_label1.name = "LINKED_PROTOCOL_CARD"
        mock_label2 = Mock()
        mock_label2.name = "SOME_OTHER_LABEL"
        mock_task.labels.all.return_value = [mock_label1, mock_label2]
        mock_task.id = "task-uuid-123"

        protocol = Protocol(self.event_request)
        protocol.target.instance = mock_task

        result = protocol.compute()

        assert result == []

    def test_compute_returns_empty_when_no_patient(self) -> None:
        """Test that compute returns empty list when task has no associated patient."""
        # Mock task with proper labels but no patient
        mock_task = Mock()
        mock_label1 = Mock()
        mock_label1.name = "LINKED_PROTOCOL_CARD"
        mock_label2 = Mock()
        mock_label2.name = "PROTOCOL_CARD_annual_wellness"
        mock_task.labels.all.return_value = [mock_label1, mock_label2]
        mock_task.id = "task-uuid-123"
        mock_task.patient = None

        protocol = Protocol(self.event_request)
        protocol.target.instance = mock_task

        result = protocol.compute()

        assert result == []

    def test_compute_updates_protocol_card_when_valid_task(self) -> None:
        """Test that compute returns protocol card update when task has valid labels and patient."""
        # Mock task with proper labels and patient
        mock_task = Mock()
        mock_label1 = Mock()
        mock_label1.name = "LINKED_PROTOCOL_CARD"
        mock_label2 = Mock()
        mock_label2.name = "PROTOCOL_CARD_annual_wellness"
        mock_task.labels.all.return_value = [mock_label1, mock_label2]
        mock_task.id = "task-uuid-123"
        
        # Mock patient
        mock_patient = Mock()
        mock_patient.id = "patient-uuid-456"
        mock_task.patient = mock_patient

        protocol = Protocol(self.event_request)
        protocol.target.instance = mock_task

        result = protocol.compute()

        assert len(result) == 1
        effect = result[0]
        
        # Verify it's a protocol card effect with NOT_RELEVANT status
        assert effect.type.name == "ADD_OR_UPDATE_PROTOCOL_CARD"
        
        # Parse the payload to verify the content
        import json
        payload_data = json.loads(effect.payload)
        assert payload_data["patient"] == "patient-uuid-456"
        assert payload_data["key"] == "annual_wellness"
        assert payload_data["data"]["status"] == "not_relevant"

    def test_compute_handles_multiple_protocol_card_labels(self) -> None:
        """Test that compute uses the first protocol card key when multiple PROTOCOL_CARD_{key} labels exist."""
        # Mock task with multiple PROTOCOL_CARD_ labels
        mock_task = Mock()
        mock_label1 = Mock()
        mock_label1.name = "LINKED_PROTOCOL_CARD"
        mock_label2 = Mock()
        mock_label2.name = "PROTOCOL_CARD_first_protocol"
        mock_label3 = Mock()
        mock_label3.name = "PROTOCOL_CARD_second_protocol"
        mock_task.labels.all.return_value = [mock_label1, mock_label2, mock_label3]
        mock_task.id = "task-uuid-123"
        
        # Mock patient
        mock_patient = Mock()
        mock_patient.id = "patient-uuid-456"
        mock_task.patient = mock_patient

        protocol = Protocol(self.event_request)
        protocol.target.instance = mock_task

        result = protocol.compute()

        assert len(result) == 1
        effect = result[0]
        
        # Parse the payload to verify it uses the first key
        import json
        payload_data = json.loads(effect.payload)
        assert payload_data["key"] == "first_protocol"