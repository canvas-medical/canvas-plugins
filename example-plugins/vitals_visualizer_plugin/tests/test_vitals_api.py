"""Comprehensive tests for vitals_visualizer_plugin vitals_api."""

from datetime import datetime
from typing import Any
from unittest.mock import Mock, patch

from vitals_visualizer_plugin.handlers.vitals_api import VitalsVisualizerAPI


class DummyRequest:
    """A dummy request object for testing VitalsVisualizerAPI."""

    def __init__(self, query_params: dict[str, Any] | None = None) -> None:
        self.query_params = query_params or {}


class DummyEvent:
    """A dummy event object for testing API handlers."""

    def __init__(self, context: dict[str, Any] | None = None) -> None:
        self.context = context or {}


class TestVitalsVisualizerAPI:
    """Test suite for VitalsVisualizerAPI endpoint."""

    def test_api_path_configuration(self) -> None:
        """Test that the API has correct path configuration."""
        assert VitalsVisualizerAPI.PATH == "/visualize"

    def test_get_without_patient_id_returns_400(self) -> None:
        """Test GET endpoint returns 400 error when patient_id is missing."""
        # Create API request without patient_id
        request = DummyRequest(query_params={})

        # Create API instance with proper context
        dummy_context = {"method": "GET", "path": "/visualize"}
        api = VitalsVisualizerAPI(event=DummyEvent(context=dummy_context))
        api.request = request

        # Call GET endpoint
        result = api.get()

        # Verify 400 response with error message
        assert len(result) == 1
        response = result[0]
        assert response.status_code == 400
        assert b"Patient ID is required" in response.content

    def test_get_with_patient_id_returns_html(self) -> None:
        """Test GET endpoint returns HTML response with vitals data."""
        # Create API request with patient_id
        request = DummyRequest(query_params={"patient_id": "patient-123"})

        # Create API instance
        dummy_context = {"method": "GET", "path": "/visualize"}
        api = VitalsVisualizerAPI(event=DummyEvent(context=dummy_context))
        api.request = request

        # Mock the private methods
        mock_vitals_data = {
            "weight": [{"date": "2025-01-01T10:00:00", "value": 150.0, "units": "lbs"}],
            "body_temperature": [{"date": "2025-01-01T10:00:00", "value": 98.6, "units": "°F"}],
            "oxygen_saturation": [{"date": "2025-01-01T10:00:00", "value": 98.0, "units": "%"}],
        }

        mock_html = "<html><body>Vitals Visualization</body></html>"

        with (
            patch.object(api, "_get_vitals_data", return_value=mock_vitals_data),
            patch.object(api, "_generate_visualization_html", return_value=mock_html),
        ):
            result = api.get()

        # Verify HTML response
        assert len(result) == 1
        response = result[0]
        assert response.content == mock_html.encode()

    def test_get_handles_exception_returns_500(self) -> None:
        """Test GET endpoint returns 500 error when exception occurs."""
        # Create API request
        request = DummyRequest(query_params={"patient_id": "patient-123"})

        # Create API instance
        dummy_context = {"method": "GET", "path": "/visualize"}
        api = VitalsVisualizerAPI(event=DummyEvent(context=dummy_context))
        api.request = request

        # Mock _get_vitals_data to raise exception
        with (
            patch.object(api, "_get_vitals_data", side_effect=Exception("Database error")),
            patch("vitals_visualizer_plugin.handlers.vitals_api.log"),
        ):
            result = api.get()

        # Verify 500 response with error message
        assert len(result) == 1
        response = result[0]
        assert response.status_code == 500
        assert b"Database error" in response.content

    def test_get_vitals_data_with_observations(self) -> None:
        """Test _get_vitals_data collects and transforms vitals correctly."""
        # Create API instance
        dummy_context = {"method": "GET", "path": "/visualize"}
        api = VitalsVisualizerAPI(event=DummyEvent(context=dummy_context))

        # Create mock observations
        mock_weight_obs = Mock()
        mock_weight_obs.name = "weight"
        mock_weight_obs.value = "2400"  # 2400 oz = 150 lbs
        mock_weight_obs.effective_datetime = datetime(2025, 1, 1, 10, 0, 0)
        mock_weight_obs.units = "oz"

        mock_temp_obs = Mock()
        mock_temp_obs.name = "body_temperature"
        mock_temp_obs.value = "98.6"
        mock_temp_obs.effective_datetime = datetime(2025, 1, 1, 10, 0, 0)
        mock_temp_obs.units = "°F"

        mock_o2_obs = Mock()
        mock_o2_obs.name = "oxygen_saturation"
        mock_o2_obs.value = "98"
        mock_o2_obs.effective_datetime = datetime(2025, 1, 1, 10, 0, 0)
        mock_o2_obs.units = "%"

        mock_observations = [mock_weight_obs, mock_temp_obs, mock_o2_obs]

        # Mock Observation queryset
        with patch("vitals_visualizer_plugin.handlers.vitals_api.Observation") as mock_obs_class:
            mock_queryset = Mock()
            mock_queryset.for_patient.return_value = mock_queryset
            mock_queryset.filter.return_value = mock_queryset
            mock_queryset.exclude.return_value = mock_queryset
            mock_queryset.select_related.return_value = mock_queryset
            mock_queryset.order_by.return_value = mock_observations
            mock_obs_class.objects = mock_queryset

            result = api._get_vitals_data("patient-123")

        # Verify data structure and transformations
        assert "weight" in result
        assert "body_temperature" in result
        assert "oxygen_saturation" in result

        # Check weight conversion (oz to lbs)
        assert len(result["weight"]) == 1
        assert result["weight"][0]["value"] == 150.0
        assert result["weight"][0]["units"] == "lbs"

        # Check temperature
        assert len(result["body_temperature"]) == 1
        assert result["body_temperature"][0]["value"] == 98.6

        # Check oxygen saturation
        assert len(result["oxygen_saturation"]) == 1
        assert result["oxygen_saturation"][0]["value"] == 98.0

    def test_get_vitals_data_skips_invalid_observations(self) -> None:
        """Test _get_vitals_data skips observations with invalid data."""
        # Create API instance
        dummy_context = {"method": "GET", "path": "/visualize"}
        api = VitalsVisualizerAPI(event=DummyEvent(context=dummy_context))

        # Create mock observations with various issues
        mock_obs_no_value = Mock()
        mock_obs_no_value.name = "weight"
        mock_obs_no_value.value = None
        mock_obs_no_value.effective_datetime = datetime(2025, 1, 1, 10, 0, 0)

        mock_obs_note = Mock()
        mock_obs_note.name = "note"
        mock_obs_note.value = "some note"
        mock_obs_note.effective_datetime = datetime(2025, 1, 1, 10, 0, 0)

        mock_obs_invalid_weight = Mock()
        mock_obs_invalid_weight.name = "weight"
        mock_obs_invalid_weight.value = "not_a_number"
        mock_obs_invalid_weight.effective_datetime = datetime(2025, 1, 1, 10, 0, 0)

        mock_obs_valid_weight = Mock()
        mock_obs_valid_weight.name = "weight"
        mock_obs_valid_weight.value = "1600"  # 100 lbs
        mock_obs_valid_weight.effective_datetime = datetime(2025, 1, 1, 10, 0, 0)

        mock_observations = [
            mock_obs_no_value,
            mock_obs_note,
            mock_obs_invalid_weight,
            mock_obs_valid_weight,
        ]

        # Mock Observation queryset
        with patch("vitals_visualizer_plugin.handlers.vitals_api.Observation") as mock_obs_class:
            mock_queryset = Mock()
            mock_queryset.for_patient.return_value = mock_queryset
            mock_queryset.filter.return_value = mock_queryset
            mock_queryset.exclude.return_value = mock_queryset
            mock_queryset.select_related.return_value = mock_queryset
            mock_queryset.order_by.return_value = mock_observations
            mock_obs_class.objects = mock_queryset

            result = api._get_vitals_data("patient-123")

        # Verify only valid weight observation was processed
        assert len(result["weight"]) == 1
        assert result["weight"][0]["value"] == 100.0

    def test_get_vitals_data_handles_exception(self) -> None:
        """Test _get_vitals_data returns empty data when exception occurs."""
        # Create API instance
        dummy_context = {"method": "GET", "path": "/visualize"}
        api = VitalsVisualizerAPI(event=DummyEvent(context=dummy_context))

        # Mock Observation to raise exception
        with patch("vitals_visualizer_plugin.handlers.vitals_api.Observation") as mock_obs_class:
            mock_obs_class.objects.for_patient.side_effect = Exception("DB error")

            with patch("vitals_visualizer_plugin.handlers.vitals_api.log"):
                result = api._get_vitals_data("patient-123")

        # Verify empty data structure is returned
        assert result == {"weight": [], "body_temperature": [], "oxygen_saturation": []}

    def test_get_vitals_data_handles_invalid_temperature(self) -> None:
        """Test _get_vitals_data skips invalid temperature values."""
        # Create API instance
        dummy_context = {"method": "GET", "path": "/visualize"}
        api = VitalsVisualizerAPI(event=DummyEvent(context=dummy_context))

        # Create mock observation with invalid temperature
        mock_temp_obs = Mock()
        mock_temp_obs.name = "body_temperature"
        mock_temp_obs.value = "invalid"
        mock_temp_obs.effective_datetime = datetime(2025, 1, 1, 10, 0, 0)
        mock_temp_obs.units = "°F"

        mock_observations = [mock_temp_obs]

        # Mock Observation queryset
        with patch("vitals_visualizer_plugin.handlers.vitals_api.Observation") as mock_obs_class:
            mock_queryset = Mock()
            mock_queryset.for_patient.return_value = mock_queryset
            mock_queryset.filter.return_value = mock_queryset
            mock_queryset.exclude.return_value = mock_queryset
            mock_queryset.select_related.return_value = mock_queryset
            mock_queryset.order_by.return_value = mock_observations
            mock_obs_class.objects = mock_queryset

            result = api._get_vitals_data("patient-123")

        # Verify temperature data is empty
        assert len(result["body_temperature"]) == 0

    def test_get_vitals_data_handles_invalid_oxygen_saturation(self) -> None:
        """Test _get_vitals_data skips invalid oxygen saturation values."""
        # Create API instance
        dummy_context = {"method": "GET", "path": "/visualize"}
        api = VitalsVisualizerAPI(event=DummyEvent(context=dummy_context))

        # Create mock observation with invalid oxygen saturation
        mock_o2_obs = Mock()
        mock_o2_obs.name = "oxygen_saturation"
        mock_o2_obs.value = "bad_value"
        mock_o2_obs.effective_datetime = datetime(2025, 1, 1, 10, 0, 0)
        mock_o2_obs.units = "%"

        mock_observations = [mock_o2_obs]

        # Mock Observation queryset
        with patch("vitals_visualizer_plugin.handlers.vitals_api.Observation") as mock_obs_class:
            mock_queryset = Mock()
            mock_queryset.for_patient.return_value = mock_queryset
            mock_queryset.filter.return_value = mock_queryset
            mock_queryset.exclude.return_value = mock_queryset
            mock_queryset.select_related.return_value = mock_queryset
            mock_queryset.order_by.return_value = mock_observations
            mock_obs_class.objects = mock_queryset

            result = api._get_vitals_data("patient-123")

        # Verify oxygen saturation data is empty
        assert len(result["oxygen_saturation"]) == 0

    def test_generate_visualization_html(self) -> None:
        """Test _generate_visualization_html renders template with vitals data."""
        # Create API instance
        dummy_context = {"method": "GET", "path": "/visualize"}
        api = VitalsVisualizerAPI(event=DummyEvent(context=dummy_context))

        # Sample vitals data
        vitals_data = {
            "weight": [{"date": "2025-01-01", "value": 150.0, "units": "lbs"}],
            "body_temperature": [],
            "oxygen_saturation": [],
        }

        # Mock render_to_string
        with patch("vitals_visualizer_plugin.handlers.vitals_api.render_to_string") as mock_render:
            mock_render.return_value = "<html>Rendered HTML</html>"

            result = api._generate_visualization_html(vitals_data)

            # Verify render_to_string was called with correct arguments
            mock_render.assert_called_once()
            call_args = mock_render.call_args
            assert call_args[0][0] == "templates/vitals_visualization.html"
            assert "vitals_data" in call_args[0][1]

            # Verify result
            assert result == "<html>Rendered HTML</html>"
