import arrow
from unittest.mock import Mock, patch

import pytest

from canvas_sdk.effects.protocol_card import ProtocolCard
from canvas_sdk.effects.simple_api import JSONResponse
from canvas_sdk.effects.task import AddTask
from canvas_sdk.handlers.simple_api import APIKeyCredentials

from task_completion_protocol_updater.routes.create_test_protocol import CreateTestProtocolAPI


class TestCreateTestProtocolAPI:
    """Test the CreateTestProtocolAPI endpoint."""

    def test_authenticate_with_correct_key(self):
        """Test authentication with correct API key."""
        api = CreateTestProtocolAPI()
        api.secrets = {"api-key": "test-key-123"}
        
        credentials = APIKeyCredentials(key="test-key-123")
        assert api.authenticate(credentials) is True

    def test_authenticate_with_incorrect_key(self):
        """Test authentication with incorrect API key."""
        api = CreateTestProtocolAPI()
        api.secrets = {"api-key": "test-key-123"}
        
        credentials = APIKeyCredentials(key="wrong-key")
        assert api.authenticate(credentials) is False

    @patch('arrow.utcnow')
    def test_post_creates_protocol_card_and_task(self, mock_utcnow):
        """Test POST creates both protocol card and task with correct data."""
        # Setup mock time
        mock_now = Mock()
        mock_shifted = Mock()
        mock_shifted.datetime = "2025-01-26T12:00:00Z"
        mock_now.shift.return_value = mock_shifted
        mock_utcnow.return_value = mock_now

        # Setup API instance
        api = CreateTestProtocolAPI()
        api.request = Mock()
        api.request.json.return_value = {"patient_id": "12345"}

        # Call the method without mocking apply methods to check actual task creation
        responses = api.post()

        # Verify responses
        assert len(responses) == 3
        
        # Check that we have a ProtocolCard effect
        protocol_card_effect = responses[0]
        assert hasattr(protocol_card_effect, 'values')
        
        # Check that we have an AddTask effect
        add_task_effect = responses[1] 
        assert hasattr(add_task_effect, 'values')
        
        # Verify AddTask has correct labels
        task_values = add_task_effect.values
        assert 'labels' in task_values
        assert task_values['labels'] == ["LINKED_PROTOCOL_CARD", "PROTOCOL_CARD_annual_exam_2025"]
        
        # Verify other task properties
        assert task_values['patient']['id'] == "12345"
        assert task_values['title'] == "Please close out this protocol card."
        assert task_values['status'] == "OPEN"
        
        # Check JSON response
        assert isinstance(responses[2], JSONResponse)
        assert responses[2].content == {"message": "Protocol card and task created"}

        # Verify time shift was called correctly
        mock_now.shift.assert_called_once_with(days=5)

    @patch('arrow.utcnow') 
    def test_task_labels_are_set_correctly(self, mock_utcnow):
        """Test that AddTask instance has correct labels set."""
        # Setup mock time
        mock_now = Mock()
        mock_shifted = Mock()
        mock_shifted.datetime = "2025-01-26T12:00:00Z"
        mock_now.shift.return_value = mock_shifted  
        mock_utcnow.return_value = mock_now

        # Setup API instance
        api = CreateTestProtocolAPI()
        api.request = Mock()
        api.request.json.return_value = {"patient_id": "test-patient"}

        # Call the method
        responses = api.post()

        # Get the AddTask effect (second response)
        add_task_effect = responses[1]
        
        # Check that it's an AddTask instance
        assert isinstance(add_task_effect.effect, AddTask)
        
        # Verify the labels are set correctly on the AddTask instance
        task = add_task_effect.effect
        assert task.labels == ["LINKED_PROTOCOL_CARD", "PROTOCOL_CARD_annual_exam_2025"]
        
        # Also verify in the values dict
        task_values = task.values
        assert task_values['labels'] == ["LINKED_PROTOCOL_CARD", "PROTOCOL_CARD_annual_exam_2025"]

    def test_post_missing_patient_id(self):
        """Test POST with missing patient_id returns error."""
        api = CreateTestProtocolAPI()
        api.request = Mock()
        api.request.json.return_value = {}

        responses = api.post()

        assert len(responses) == 1
        assert isinstance(responses[0], JSONResponse)
        assert responses[0].content == {"error": "patient_id is required"}
        assert responses[0].status_code == 400

    def test_post_empty_patient_id(self):
        """Test POST with empty patient_id returns error."""
        api = CreateTestProtocolAPI()
        api.request = Mock()
        api.request.json.return_value = {"patient_id": ""}

        responses = api.post()

        assert len(responses) == 1
        assert isinstance(responses[0], JSONResponse)
        assert responses[0].content == {"error": "patient_id is required"}
        assert responses[0].status_code == 400

    def test_post_none_patient_id(self):
        """Test POST with None patient_id returns error."""
        api = CreateTestProtocolAPI()
        api.request = Mock()
        api.request.json.return_value = {"patient_id": None}

        responses = api.post()

        assert len(responses) == 1
        assert isinstance(responses[0], JSONResponse)
        assert responses[0].content == {"error": "patient_id is required"}
        assert responses[0].status_code == 400