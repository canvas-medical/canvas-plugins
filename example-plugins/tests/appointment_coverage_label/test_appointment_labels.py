"""Comprehensive tests for appointment_coverage_label plugin."""

from unittest.mock import MagicMock, patch

import pytest

from canvas_sdk.events import EventType


@pytest.mark.django_db
class TestAppointmentLabelsProtocol:
    """Test suite for AppointmentLabelsProtocol."""

    def test_responds_to_correct_events(self):
        """Test that protocol responds to both COVERAGE_CREATED and APPOINTMENT_CREATED events."""
        from appointment_coverage_label.protocols.appointment_labels import (
            AppointmentLabelsProtocol,
        )

        expected_events = [
            EventType.Name(EventType.COVERAGE_CREATED),
            EventType.Name(EventType.APPOINTMENT_CREATED),
        ]
        assert expected_events == AppointmentLabelsProtocol.RESPONDS_TO

    def test_compute_routes_to_coverage_created_handler(self, monkeypatch):
        """Test that compute() routes COVERAGE_CREATED events to correct handler."""
        from appointment_coverage_label.protocols.appointment_labels import (
            AppointmentLabelsProtocol,
        )

        # Mock event
        mock_event = MagicMock()
        mock_event.type = EventType.COVERAGE_CREATED

        # Mock context
        dummy_context = {"patient": {"id": "test-patient-id"}}

        # Create protocol instance
        protocol = AppointmentLabelsProtocol(event=mock_event)
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        # Mock the handler method
        with patch.object(
            protocol, "handle_coverage_created", return_value=[]
        ) as mock_handler:
            protocol.compute()
            mock_handler.assert_called_once()

    def test_compute_routes_to_appointment_created_handler(self, monkeypatch):
        """Test that compute() routes APPOINTMENT_CREATED events to correct handler."""
        from appointment_coverage_label.protocols.appointment_labels import (
            AppointmentLabelsProtocol,
        )

        # Mock event
        mock_event = MagicMock()
        mock_event.type = EventType.APPOINTMENT_CREATED

        # Mock context
        dummy_context = {"patient": {"id": "test-patient-id"}}

        # Create protocol instance
        protocol = AppointmentLabelsProtocol(event=mock_event)
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        # Mock the handler method
        with patch.object(
            protocol, "handle_appointment_created", return_value=[]
        ) as mock_handler:
            protocol.compute()
            mock_handler.assert_called_once()

    def test_compute_with_unexpected_event_type(self, monkeypatch):
        """Test that compute() handles unexpected event types gracefully."""
        from appointment_coverage_label.protocols.appointment_labels import (
            AppointmentLabelsProtocol,
        )

        # Mock event with unexpected type
        mock_event = MagicMock()
        mock_event.type = EventType.PATIENT_CREATED

        # Mock context
        dummy_context = {"patient": {"id": "test-patient-id"}}

        # Create protocol instance
        protocol = AppointmentLabelsProtocol(event=mock_event)
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        result = protocol.compute()
        assert result == []

    def test_handle_coverage_created_removes_labels(self, monkeypatch):
        """Test that handle_coverage_created removes MISSING_COVERAGE labels."""
        from appointment_coverage_label.protocols.appointment_labels import (
            AppointmentLabelsProtocol,
        )

        # Mock event and context
        mock_event = MagicMock()
        dummy_context = {"patient": {"id": "test-patient-id"}}

        # Mock patient
        mock_patient = MagicMock()
        mock_patient.id = "test-patient-id"

        # Mock appointments with MISSING_COVERAGE label
        mock_appt1 = MagicMock()
        mock_appt1.id = "appt-1"
        mock_appt2 = MagicMock()
        mock_appt2.id = "appt-2"

        # Mock queryset
        mock_queryset = MagicMock()
        mock_queryset.exists.return_value = True
        mock_queryset.__len__.return_value = 2
        mock_queryset.__iter__.return_value = iter([mock_appt1, mock_appt2])

        protocol = AppointmentLabelsProtocol(event=mock_event)
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        with patch(
            "appointment_coverage_label.protocols.appointment_labels.Patient.objects.get"
        ) as mock_patient_get:
            mock_patient_get.return_value = mock_patient

            with patch(
                "appointment_coverage_label.protocols.appointment_labels.Appointment.objects.filter"
            ) as mock_filter:
                mock_filter.return_value.prefetch_related.return_value = mock_queryset

                with patch(
                    "appointment_coverage_label.protocols.appointment_labels.RemoveAppointmentLabel"
                ) as mock_effect_class:
                    mock_effect_instance = MagicMock()
                    mock_applied_effect = MagicMock()
                    mock_effect_instance.apply.return_value = mock_applied_effect
                    mock_effect_class.return_value = mock_effect_instance

                    result = protocol.handle_coverage_created()

                    # Verify RemoveAppointmentLabel was called for both appointments
                    assert mock_effect_class.call_count == 2
                    assert len(result) == 2

    def test_handle_coverage_created_no_appointments_to_update(self, monkeypatch):
        """Test handle_coverage_created when no appointments need labels removed."""
        from appointment_coverage_label.protocols.appointment_labels import (
            AppointmentLabelsProtocol,
        )

        # Mock event and context
        mock_event = MagicMock()
        dummy_context = {"patient": {"id": "test-patient-id"}}

        # Mock patient
        mock_patient = MagicMock()

        # Mock empty queryset
        mock_queryset = MagicMock()
        mock_queryset.exists.return_value = False

        protocol = AppointmentLabelsProtocol(event=mock_event)
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        with patch(
            "appointment_coverage_label.protocols.appointment_labels.Patient.objects.get"
        ) as mock_patient_get:
            mock_patient_get.return_value = mock_patient

            with patch(
                "appointment_coverage_label.protocols.appointment_labels.Appointment.objects.filter"
            ) as mock_filter:
                mock_filter.return_value.prefetch_related.return_value = mock_queryset

                result = protocol.handle_coverage_created()
                assert result == []

    def test_handle_coverage_created_patient_not_found(self, monkeypatch):
        """Test handle_coverage_created when patient doesn't exist."""
        from appointment_coverage_label.protocols.appointment_labels import (
            AppointmentLabelsProtocol,
        )

        # Mock event and context
        mock_event = MagicMock()
        dummy_context = {"patient": {"id": "nonexistent-patient"}}

        protocol = AppointmentLabelsProtocol(event=mock_event)
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        with patch(
            "appointment_coverage_label.protocols.appointment_labels.Patient.objects.get"
        ) as mock_patient_get:
            from appointment_coverage_label.protocols.appointment_labels import Patient

            mock_patient_get.side_effect = Patient.DoesNotExist()

            result = protocol.handle_coverage_created()
            assert result == []

    def test_handle_appointment_created_adds_labels_when_no_coverage(self, monkeypatch):
        """Test that handle_appointment_created adds labels when patient has no coverage."""
        from appointment_coverage_label.protocols.appointment_labels import (
            AppointmentLabelsProtocol,
        )

        # Mock event and context
        mock_event = MagicMock()
        dummy_context = {"patient": {"id": "test-patient-id"}}

        # Mock patient
        mock_patient = MagicMock()
        mock_patient.id = "test-patient-id"

        # Mock appointments without labels
        mock_appt1 = MagicMock()
        mock_appt1.id = "appt-1"
        mock_appt2 = MagicMock()
        mock_appt2.id = "appt-2"

        # Mock queryset for appointments
        mock_appt_queryset = MagicMock()
        mock_appt_queryset.exists.return_value = True
        mock_appt_queryset.__len__.return_value = 2
        mock_appt_queryset.__iter__.return_value = iter([mock_appt1, mock_appt2])

        # Mock coverage queryset (no coverage)
        mock_coverage_queryset = MagicMock()
        mock_coverage_queryset.exists.return_value = False

        protocol = AppointmentLabelsProtocol(event=mock_event)
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        with patch(
            "appointment_coverage_label.protocols.appointment_labels.Patient.objects.get"
        ) as mock_patient_get:
            mock_patient_get.return_value = mock_patient

            with patch(
                "appointment_coverage_label.protocols.appointment_labels.Coverage.objects.filter"
            ) as mock_coverage_filter:
                mock_coverage_filter.return_value = mock_coverage_queryset

                with patch(
                    "appointment_coverage_label.protocols.appointment_labels.Appointment.objects.filter"
                ) as mock_appt_filter:
                    mock_appt_filter.return_value.exclude.return_value.prefetch_related.return_value = (
                        mock_appt_queryset
                    )

                    with patch(
                        "appointment_coverage_label.protocols.appointment_labels.AddAppointmentLabel"
                    ) as mock_effect_class:
                        mock_effect_instance = MagicMock()
                        mock_applied_effect = MagicMock()
                        mock_effect_instance.apply.return_value = mock_applied_effect
                        mock_effect_class.return_value = mock_effect_instance

                        result = protocol.handle_appointment_created()

                        # Verify AddAppointmentLabel was called for both appointments
                        assert mock_effect_class.call_count == 2
                        assert len(result) == 2

    def test_handle_appointment_created_no_labels_when_has_coverage(self, monkeypatch):
        """Test that handle_appointment_created doesn't add labels when patient has coverage."""
        from appointment_coverage_label.protocols.appointment_labels import (
            AppointmentLabelsProtocol,
        )

        # Mock event and context
        mock_event = MagicMock()
        dummy_context = {"patient": {"id": "test-patient-id"}}

        # Mock patient
        mock_patient = MagicMock()

        # Mock coverage queryset (has coverage)
        mock_coverage_queryset = MagicMock()
        mock_coverage_queryset.exists.return_value = True

        protocol = AppointmentLabelsProtocol(event=mock_event)
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        with patch(
            "appointment_coverage_label.protocols.appointment_labels.Patient.objects.get"
        ) as mock_patient_get:
            mock_patient_get.return_value = mock_patient

            with patch(
                "appointment_coverage_label.protocols.appointment_labels.Coverage.objects.filter"
            ) as mock_coverage_filter:
                mock_coverage_filter.return_value = mock_coverage_queryset

                result = protocol.handle_appointment_created()
                assert result == []

    def test_handle_appointment_created_all_appointments_already_labeled(self, monkeypatch):
        """Test handle_appointment_created when all appointments already have labels."""
        from appointment_coverage_label.protocols.appointment_labels import (
            AppointmentLabelsProtocol,
        )

        # Mock event and context
        mock_event = MagicMock()
        dummy_context = {"patient": {"id": "test-patient-id"}}

        # Mock patient
        mock_patient = MagicMock()

        # Mock coverage queryset (no coverage)
        mock_coverage_queryset = MagicMock()
        mock_coverage_queryset.exists.return_value = False

        # Mock empty appointment queryset (all already labeled)
        mock_appt_queryset = MagicMock()
        mock_appt_queryset.exists.return_value = False

        protocol = AppointmentLabelsProtocol(event=mock_event)
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        with patch(
            "appointment_coverage_label.protocols.appointment_labels.Patient.objects.get"
        ) as mock_patient_get:
            mock_patient_get.return_value = mock_patient

            with patch(
                "appointment_coverage_label.protocols.appointment_labels.Coverage.objects.filter"
            ) as mock_coverage_filter:
                mock_coverage_filter.return_value = mock_coverage_queryset

                with patch(
                    "appointment_coverage_label.protocols.appointment_labels.Appointment.objects.filter"
                ) as mock_appt_filter:
                    mock_appt_filter.return_value.exclude.return_value.prefetch_related.return_value = (
                        mock_appt_queryset
                    )

                    result = protocol.handle_appointment_created()
                    assert result == []

    def test_handle_appointment_created_patient_not_found(self, monkeypatch):
        """Test handle_appointment_created when patient doesn't exist."""
        from appointment_coverage_label.protocols.appointment_labels import (
            AppointmentLabelsProtocol,
        )

        # Mock event and context
        mock_event = MagicMock()
        dummy_context = {"patient": {"id": "nonexistent-patient"}}

        protocol = AppointmentLabelsProtocol(event=mock_event)
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        with patch(
            "appointment_coverage_label.protocols.appointment_labels.Patient.objects.get"
        ) as mock_patient_get:
            from appointment_coverage_label.protocols.appointment_labels import Patient

            mock_patient_get.side_effect = Patient.DoesNotExist()

            result = protocol.handle_appointment_created()
            assert result == []

    def test_handle_coverage_created_handles_effect_exception(self, monkeypatch):
        """Test that handle_coverage_created handles exceptions when creating effects."""
        from appointment_coverage_label.protocols.appointment_labels import (
            AppointmentLabelsProtocol,
        )

        # Mock event and context
        mock_event = MagicMock()
        dummy_context = {"patient": {"id": "test-patient-id"}}

        # Mock patient
        mock_patient = MagicMock()

        # Mock appointment
        mock_appt = MagicMock()
        mock_appt.id = "appt-1"

        # Mock queryset
        mock_queryset = MagicMock()
        mock_queryset.exists.return_value = True
        mock_queryset.__len__.return_value = 1
        mock_queryset.__iter__.return_value = iter([mock_appt])

        protocol = AppointmentLabelsProtocol(event=mock_event)
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        with patch(
            "appointment_coverage_label.protocols.appointment_labels.Patient.objects.get"
        ) as mock_patient_get:
            mock_patient_get.return_value = mock_patient

            with patch(
                "appointment_coverage_label.protocols.appointment_labels.Appointment.objects.filter"
            ) as mock_filter:
                mock_filter.return_value.prefetch_related.return_value = mock_queryset

                # Mock log.error to prevent exc_info TypeError
                with patch("appointment_coverage_label.protocols.appointment_labels.log"):
                    with patch(
                        "appointment_coverage_label.protocols.appointment_labels.RemoveAppointmentLabel"
                    ) as mock_effect_class:
                        # Make the effect creation raise an exception
                        mock_effect_class.side_effect = Exception("Effect creation failed")

                        result = protocol.handle_coverage_created()

                        # Should handle exception gracefully and return empty list
                        assert result == []

    def test_handle_appointment_created_handles_effect_exception(self, monkeypatch):
        """Test that handle_appointment_created handles exceptions when creating effects."""
        from appointment_coverage_label.protocols.appointment_labels import (
            AppointmentLabelsProtocol,
        )

        # Mock event and context
        mock_event = MagicMock()
        dummy_context = {"patient": {"id": "test-patient-id"}}

        # Mock patient
        mock_patient = MagicMock()

        # Mock appointment
        mock_appt = MagicMock()
        mock_appt.id = "appt-1"

        # Mock querysets
        mock_appt_queryset = MagicMock()
        mock_appt_queryset.exists.return_value = True
        mock_appt_queryset.__len__.return_value = 1
        mock_appt_queryset.__iter__.return_value = iter([mock_appt])

        mock_coverage_queryset = MagicMock()
        mock_coverage_queryset.exists.return_value = False

        protocol = AppointmentLabelsProtocol(event=mock_event)
        monkeypatch.setattr(type(protocol), "context", property(lambda self: dummy_context))

        with patch(
            "appointment_coverage_label.protocols.appointment_labels.Patient.objects.get"
        ) as mock_patient_get:
            mock_patient_get.return_value = mock_patient

            with patch(
                "appointment_coverage_label.protocols.appointment_labels.Coverage.objects.filter"
            ) as mock_coverage_filter:
                mock_coverage_filter.return_value = mock_coverage_queryset

                with patch(
                    "appointment_coverage_label.protocols.appointment_labels.Appointment.objects.filter"
                ) as mock_appt_filter:
                    mock_appt_filter.return_value.exclude.return_value.prefetch_related.return_value = (
                        mock_appt_queryset
                    )

                    # Mock log.error to prevent exc_info TypeError
                    with patch("appointment_coverage_label.protocols.appointment_labels.log"):
                        with patch(
                            "appointment_coverage_label.protocols.appointment_labels.AddAppointmentLabel"
                        ) as mock_effect_class:
                            # Make the effect creation raise an exception
                            mock_effect_class.side_effect = Exception("Effect creation failed")

                            result = protocol.handle_appointment_created()

                            # Should handle exception gracefully and return empty list
                            assert result == []
