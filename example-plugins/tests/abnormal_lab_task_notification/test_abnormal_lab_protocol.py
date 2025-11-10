"""Comprehensive tests for abnormal_lab_task_notification plugin."""

from unittest.mock import MagicMock, patch

from canvas_sdk.events import EventType


class TestAbnormalLabProtocol:
    """Test suite for AbnormalLabProtocol."""

    def test_responds_to_correct_event(self):
        """Test that AbnormalLabProtocol responds to LAB_REPORT_CREATED event."""
        from abnormal_lab_task_notification.protocols.abnormal_lab_protocol import (
            AbnormalLabProtocol,
        )

        assert EventType.Name(EventType.LAB_REPORT_CREATED) == AbnormalLabProtocol.RESPONDS_TO

    def test_compute_with_abnormal_lab_values(self, monkeypatch):
        """Test that protocol creates task when lab report has abnormal values."""
        from abnormal_lab_task_notification.protocols.abnormal_lab_protocol import (
            AbnormalLabProtocol,
        )

        from canvas_sdk.effects.task import TaskStatus

        # Mock event with lab report ID
        mock_event = MagicMock()
        mock_event.target.id = "test-lab-report-id"

        # Mock patient
        mock_patient = MagicMock()
        mock_patient.id = "test-patient-id"

        # Mock abnormal lab values
        mock_abnormal_value1 = MagicMock()
        mock_abnormal_value1.abnormal_flag = "H"  # High

        mock_abnormal_value2 = MagicMock()
        mock_abnormal_value2.abnormal_flag = "L"  # Low

        # Mock lab report
        mock_lab_report = MagicMock()
        mock_lab_report.patient = mock_patient
        mock_lab_report.values.all.return_value = [mock_abnormal_value1, mock_abnormal_value2]

        # Mock LabReport queryset
        mock_queryset = MagicMock()
        mock_queryset.first.return_value = mock_lab_report

        # Patch LabReport.objects.filter
        with patch(
            "abnormal_lab_task_notification.protocols.abnormal_lab_protocol.LabReport.objects.filter"
        ) as mock_filter:
            mock_filter.return_value = mock_queryset

            # Mock AddTask effect
            with patch(
                "abnormal_lab_task_notification.protocols.abnormal_lab_protocol.AddTask"
            ) as mock_task_class:
                mock_task_instance = MagicMock()
                mock_applied_effect = MagicMock()
                mock_task_instance.apply.return_value = mock_applied_effect
                mock_task_class.return_value = mock_task_instance

                # Execute protocol
                protocol = AbnormalLabProtocol(event=mock_event)
                result = protocol.compute()

                # Verify task was created with correct parameters
                mock_task_class.assert_called_once_with(
                    patient_id="test-patient-id",
                    title="Review Abnormal Lab Values (2 abnormal)",
                    status=TaskStatus.OPEN,
                    labels=["abnormal-lab", "urgent-review"],
                )

                # Verify task was applied
                mock_task_instance.apply.assert_called_once()

                # Verify result
                assert result == [mock_applied_effect]

    def test_compute_with_no_abnormal_values(self):
        """Test that protocol returns empty list when no abnormal values."""
        from abnormal_lab_task_notification.protocols.abnormal_lab_protocol import (
            AbnormalLabProtocol,
        )

        # Mock event
        mock_event = MagicMock()
        mock_event.target.id = "test-lab-report-id"

        # Mock patient
        mock_patient = MagicMock()
        mock_patient.id = "test-patient-id"

        # Mock normal lab values (no abnormal flag)
        mock_normal_value1 = MagicMock()
        mock_normal_value1.abnormal_flag = ""

        mock_normal_value2 = MagicMock()
        mock_normal_value2.abnormal_flag = None

        # Mock lab report
        mock_lab_report = MagicMock()
        mock_lab_report.patient = mock_patient
        mock_lab_report.values.all.return_value = [mock_normal_value1, mock_normal_value2]

        # Mock LabReport queryset
        mock_queryset = MagicMock()
        mock_queryset.first.return_value = mock_lab_report

        with patch(
            "abnormal_lab_task_notification.protocols.abnormal_lab_protocol.LabReport.objects.filter"
        ) as mock_filter:
            mock_filter.return_value = mock_queryset

            protocol = AbnormalLabProtocol(event=mock_event)
            result = protocol.compute()

            assert result == []

    def test_compute_with_lab_report_not_found(self):
        """Test that protocol returns empty list when lab report not found."""
        from abnormal_lab_task_notification.protocols.abnormal_lab_protocol import (
            AbnormalLabProtocol,
        )

        # Mock event
        mock_event = MagicMock()
        mock_event.target.id = "nonexistent-lab-report-id"

        # Mock empty queryset
        mock_queryset = MagicMock()
        mock_queryset.first.return_value = None

        with patch(
            "abnormal_lab_task_notification.protocols.abnormal_lab_protocol.LabReport.objects.filter"
        ) as mock_filter:
            mock_filter.return_value = mock_queryset

            protocol = AbnormalLabProtocol(event=mock_event)
            result = protocol.compute()

            assert result == []

    def test_compute_filters_test_and_junked_reports(self):
        """Test that protocol properly filters out test and junked reports."""
        from abnormal_lab_task_notification.protocols.abnormal_lab_protocol import (
            AbnormalLabProtocol,
        )

        # Mock event
        mock_event = MagicMock()
        mock_event.target.id = "test-lab-report-id"

        # Mock empty queryset (filtered out)
        mock_queryset = MagicMock()
        mock_queryset.first.return_value = None

        with patch(
            "abnormal_lab_task_notification.protocols.abnormal_lab_protocol.LabReport.objects.filter"
        ) as mock_filter:
            mock_filter.return_value = mock_queryset

            protocol = AbnormalLabProtocol(event=mock_event)
            protocol.compute()

            # Verify filter was called with correct parameters
            mock_filter.assert_called_once_with(
                id="test-lab-report-id", for_test_only=False, junked=False, patient__isnull=False
            )

    def test_compute_handles_exception(self):
        """Test that protocol handles exceptions gracefully."""
        from abnormal_lab_task_notification.protocols.abnormal_lab_protocol import (
            AbnormalLabProtocol,
        )

        # Mock event
        mock_event = MagicMock()
        mock_event.target.id = "test-lab-report-id"

        # Mock LabReport.objects.filter to raise exception
        with patch(
            "abnormal_lab_task_notification.protocols.abnormal_lab_protocol.LabReport.objects.filter"
        ) as mock_filter:
            mock_filter.side_effect = Exception("Database error")

            protocol = AbnormalLabProtocol(event=mock_event)
            result = protocol.compute()

            # Should return empty list on exception
            assert result == []

    def test_compute_with_whitespace_abnormal_flag(self):
        """Test that protocol ignores abnormal flags that are only whitespace."""
        from abnormal_lab_task_notification.protocols.abnormal_lab_protocol import (
            AbnormalLabProtocol,
        )

        # Mock event
        mock_event = MagicMock()
        mock_event.target.id = "test-lab-report-id"

        # Mock patient
        mock_patient = MagicMock()
        mock_patient.id = "test-patient-id"

        # Mock lab value with whitespace abnormal flag
        mock_value_with_whitespace = MagicMock()
        mock_value_with_whitespace.abnormal_flag = "   "  # Only whitespace

        # Mock lab report
        mock_lab_report = MagicMock()
        mock_lab_report.patient = mock_patient
        mock_lab_report.values.all.return_value = [mock_value_with_whitespace]

        # Mock LabReport queryset
        mock_queryset = MagicMock()
        mock_queryset.first.return_value = mock_lab_report

        with patch(
            "abnormal_lab_task_notification.protocols.abnormal_lab_protocol.LabReport.objects.filter"
        ) as mock_filter:
            mock_filter.return_value = mock_queryset

            protocol = AbnormalLabProtocol(event=mock_event)
            result = protocol.compute()

            # Should return empty list since whitespace is stripped
            assert result == []

    def test_compute_single_abnormal_value(self):
        """Test task title with single abnormal value."""
        from abnormal_lab_task_notification.protocols.abnormal_lab_protocol import (
            AbnormalLabProtocol,
        )

        from canvas_sdk.effects.task import TaskStatus

        # Mock event
        mock_event = MagicMock()
        mock_event.target.id = "test-lab-report-id"

        # Mock patient
        mock_patient = MagicMock()
        mock_patient.id = "test-patient-id"

        # Mock single abnormal lab value
        mock_abnormal_value = MagicMock()
        mock_abnormal_value.abnormal_flag = "H"

        # Mock lab report
        mock_lab_report = MagicMock()
        mock_lab_report.patient = mock_patient
        mock_lab_report.values.all.return_value = [mock_abnormal_value]

        # Mock LabReport queryset
        mock_queryset = MagicMock()
        mock_queryset.first.return_value = mock_lab_report

        with patch(
            "abnormal_lab_task_notification.protocols.abnormal_lab_protocol.LabReport.objects.filter"
        ) as mock_filter:
            mock_filter.return_value = mock_queryset

            with patch(
                "abnormal_lab_task_notification.protocols.abnormal_lab_protocol.AddTask"
            ) as mock_task_class:
                mock_task_instance = MagicMock()
                mock_applied_effect = MagicMock()
                mock_task_instance.apply.return_value = mock_applied_effect
                mock_task_class.return_value = mock_task_instance

                protocol = AbnormalLabProtocol(event=mock_event)
                protocol.compute()

                # Verify task title for single abnormal value
                mock_task_class.assert_called_once_with(
                    patient_id="test-patient-id",
                    title="Review Abnormal Lab Values (1 abnormal)",
                    status=TaskStatus.OPEN,
                    labels=["abnormal-lab", "urgent-review"],
                )
