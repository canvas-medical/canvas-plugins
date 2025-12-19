import pytest

from canvas_sdk.test_utils.factories.integration_task import IntegrationTaskFactory
from canvas_sdk.test_utils.factories.patient import PatientFactory
from canvas_sdk.v1.data import IntegrationTask
from canvas_sdk.v1.data.integration_task import IntegrationTaskChannel, IntegrationTaskStatus


@pytest.mark.django_db
class TestIntegrationTaskQuerySet:
    """Tests for IntegrationTaskQuerySet filter methods."""

    def test_unread_filters_to_unread_status(self) -> None:
        """Test that unread() filters to tasks with UNREAD status."""
        unread_task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD)
        IntegrationTaskFactory.create(status=IntegrationTaskStatus.READ)
        IntegrationTaskFactory.create(status=IntegrationTaskStatus.PROCESSED)

        result = IntegrationTask.objects.unread()

        assert list(result) == [unread_task]

    def test_pending_review_filters_to_unread_and_read(self) -> None:
        """Test that pending_review() filters to UNREAD and READ statuses."""
        unread_task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD)
        read_task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.READ)
        IntegrationTaskFactory.create(status=IntegrationTaskStatus.PROCESSED)
        IntegrationTaskFactory.create(status=IntegrationTaskStatus.JUNK)

        result = IntegrationTask.objects.pending_review()

        assert set(result) == {unread_task, read_task}

    def test_processed_filters_to_processed_and_reviewed(self) -> None:
        """Test that processed() filters to PROCESSED and REVIEWED statuses."""
        processed_task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.PROCESSED)
        reviewed_task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.REVIEWED)
        IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD)
        IntegrationTaskFactory.create(status=IntegrationTaskStatus.READ)

        result = IntegrationTask.objects.processed()

        assert set(result) == {processed_task, reviewed_task}

    def test_with_errors_filters_to_error_statuses(self) -> None:
        """Test that with_errors() filters to ERROR and UNREAD_ERROR statuses."""
        error_task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.ERROR)
        unread_error_task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD_ERROR)
        IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD)
        IntegrationTaskFactory.create(status=IntegrationTaskStatus.PROCESSED)

        result = IntegrationTask.objects.with_errors()

        assert set(result) == {error_task, unread_error_task}

    def test_junked_filters_to_junk_status(self) -> None:
        """Test that junked() filters to tasks with JUNK status."""
        junked_task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.JUNK)
        IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD)
        IntegrationTaskFactory.create(status=IntegrationTaskStatus.PROCESSED)

        result = IntegrationTask.objects.junked()

        assert list(result) == [junked_task]

    def test_not_junked_excludes_junk_status(self) -> None:
        """Test that not_junked() excludes tasks with JUNK status."""
        unread_task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD)
        processed_task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.PROCESSED)
        IntegrationTaskFactory.create(status=IntegrationTaskStatus.JUNK)

        result = IntegrationTask.objects.not_junked()

        assert set(result) == {unread_task, processed_task}

    def test_faxes_filters_to_fax_channel(self) -> None:
        """Test that faxes() filters to tasks with FAX channel."""
        fax_task = IntegrationTaskFactory.create(channel=IntegrationTaskChannel.FAX)
        IntegrationTaskFactory.create(channel=IntegrationTaskChannel.DOCUMENT_UPLOAD)
        IntegrationTaskFactory.create(channel=IntegrationTaskChannel.FROM_INTEGRATION_ENGINE)

        result = IntegrationTask.objects.faxes()

        assert list(result) == [fax_task]

    def test_uploads_filters_to_document_upload_channel(self) -> None:
        """Test that uploads() filters to tasks with DOCUMENT_UPLOAD channel."""
        upload_task = IntegrationTaskFactory.create(channel=IntegrationTaskChannel.DOCUMENT_UPLOAD)
        IntegrationTaskFactory.create(channel=IntegrationTaskChannel.FAX)

        result = IntegrationTask.objects.uploads()

        assert list(result) == [upload_task]

    def test_from_integration_engine_filters_correctly(self) -> None:
        """Test that from_integration_engine() filters to correct channel."""
        engine_task = IntegrationTaskFactory.create(
            channel=IntegrationTaskChannel.FROM_INTEGRATION_ENGINE
        )
        IntegrationTaskFactory.create(channel=IntegrationTaskChannel.FAX)

        result = IntegrationTask.objects.from_integration_engine()

        assert list(result) == [engine_task]

    def test_from_patient_portal_filters_correctly(self) -> None:
        """Test that from_patient_portal() filters to correct channel."""
        portal_task = IntegrationTaskFactory.create(
            channel=IntegrationTaskChannel.FROM_PATIENT_PORTAL
        )
        IntegrationTaskFactory.create(channel=IntegrationTaskChannel.FAX)

        result = IntegrationTask.objects.from_patient_portal()

        assert list(result) == [portal_task]

    def test_for_patient_filters_by_patient_id(self) -> None:
        """Test that for_patient() filters tasks by patient ID."""
        patient = PatientFactory.create()
        patient_task = IntegrationTaskFactory.create(patient=patient)
        IntegrationTaskFactory.create()  # Different patient

        result = IntegrationTask.objects.for_patient(str(patient.id))

        assert list(result) == [patient_task]

    def test_queryset_methods_can_be_chained(self) -> None:
        """Test that QuerySet methods can be chained together."""
        patient = PatientFactory.create()
        target_task = IntegrationTaskFactory.create(
            patient=patient,
            status=IntegrationTaskStatus.UNREAD,
            channel=IntegrationTaskChannel.FAX,
        )
        IntegrationTaskFactory.create(
            patient=patient,
            status=IntegrationTaskStatus.PROCESSED,
            channel=IntegrationTaskChannel.FAX,
        )
        IntegrationTaskFactory.create(
            status=IntegrationTaskStatus.UNREAD,
            channel=IntegrationTaskChannel.FAX,
        )

        result = IntegrationTask.objects.for_patient(str(patient.id)).faxes().pending_review()

        assert list(result) == [target_task]


@pytest.mark.django_db
class TestIntegrationTaskProperties:
    """Tests for IntegrationTask property helpers."""

    def test_is_fax_returns_true_for_fax_channel(self) -> None:
        """Test that is_fax returns True for FAX channel."""
        task = IntegrationTaskFactory.create(channel=IntegrationTaskChannel.FAX)
        assert task.is_fax is True

    def test_is_fax_returns_false_for_other_channels(self) -> None:
        """Test that is_fax returns False for non-FAX channels."""
        task = IntegrationTaskFactory.create(channel=IntegrationTaskChannel.DOCUMENT_UPLOAD)
        assert task.is_fax is False

    def test_is_pending_returns_true_for_unread(self) -> None:
        """Test that is_pending returns True for UNREAD status."""
        task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD)
        assert task.is_pending is True

    def test_is_pending_returns_true_for_read(self) -> None:
        """Test that is_pending returns True for READ status."""
        task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.READ)
        assert task.is_pending is True

    def test_is_pending_returns_false_for_processed(self) -> None:
        """Test that is_pending returns False for PROCESSED status."""
        task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.PROCESSED)
        assert task.is_pending is False

    def test_is_processed_returns_true_for_processed(self) -> None:
        """Test that is_processed returns True for PROCESSED status."""
        task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.PROCESSED)
        assert task.is_processed is True

    def test_is_processed_returns_true_for_reviewed(self) -> None:
        """Test that is_processed returns True for REVIEWED status."""
        task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.REVIEWED)
        assert task.is_processed is True

    def test_is_processed_returns_false_for_unread(self) -> None:
        """Test that is_processed returns False for UNREAD status."""
        task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD)
        assert task.is_processed is False

    def test_has_error_returns_true_for_error(self) -> None:
        """Test that has_error returns True for ERROR status."""
        task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.ERROR)
        assert task.has_error is True

    def test_has_error_returns_true_for_unread_error(self) -> None:
        """Test that has_error returns True for UNREAD_ERROR status."""
        task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD_ERROR)
        assert task.has_error is True

    def test_has_error_returns_false_for_unread(self) -> None:
        """Test that has_error returns False for UNREAD status."""
        task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD)
        assert task.has_error is False

    def test_is_junked_returns_true_for_junk(self) -> None:
        """Test that is_junked returns True for JUNK status."""
        task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.JUNK)
        assert task.is_junked is True

    def test_is_junked_returns_false_for_other_statuses(self) -> None:
        """Test that is_junked returns False for non-JUNK statuses."""
        task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD)
        assert task.is_junked is False
