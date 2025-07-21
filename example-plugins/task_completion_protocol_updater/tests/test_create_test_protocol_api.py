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

        # Mock the apply methods
        with patch.object(ProtocolCard, 'apply') as mock_card_apply, \
             patch.object(AddTask, 'apply') as mock_task_apply:
            
            mock_card_apply.return_value = "mocked_card_effect"
            mock_task_apply.return_value = "mocked_task_effect"

            # Call the method
            responses = api.post()

            # Verify responses
            assert len(responses) == 3
            assert responses[0] == "mocked_card_effect"
            assert responses[1] == "mocked_task_effect"
            assert isinstance(responses[2], JSONResponse)
            assert responses[2].content == {"message": "Protocol card and task created"}

            # Verify ProtocolCard was created with correct parameters
            mock_card_apply.assert_called_once()
            
            # Verify AddTask was created with correct parameters  
            mock_task_apply.assert_called_once()

            # Verify time shift was called correctly
            mock_now.shift.assert_called_once_with(days=5)

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