import pytest

from canvas_sdk.test_utils.factories.integration_task import (
    IntegrationTaskFactory,
    IntegrationTaskReviewFactory,
)
from canvas_sdk.test_utils.factories.patient import PatientFactory
from canvas_sdk.test_utils.factories.staff import StaffFactory
from canvas_sdk.v1.data import IntegrationTask, IntegrationTaskReview
from canvas_sdk.v1.data.integration_task import IntegrationTaskChannel, IntegrationTaskStatus


@pytest.mark.django_db
def test_unread_filters_to_unread_status() -> None:
    """Test that unread() filters to tasks with UNREAD status."""
    unread_task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD)
    IntegrationTaskFactory.create(status=IntegrationTaskStatus.READ)
    IntegrationTaskFactory.create(status=IntegrationTaskStatus.PROCESSED)

    result = IntegrationTask.objects.unread()

    assert list(result) == [unread_task]


@pytest.mark.django_db
def test_pending_review_filters_to_unread_and_read() -> None:
    """Test that pending_review() filters to UNREAD and READ statuses."""
    unread_task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD)
    read_task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.READ)
    IntegrationTaskFactory.create(status=IntegrationTaskStatus.PROCESSED)
    IntegrationTaskFactory.create(status=IntegrationTaskStatus.JUNK)

    result = IntegrationTask.objects.pending_review()

    assert set(result) == {unread_task, read_task}


@pytest.mark.django_db
def test_processed_filters_to_processed_and_reviewed() -> None:
    """Test that processed() filters to PROCESSED and REVIEWED statuses."""
    processed_task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.PROCESSED)
    reviewed_task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.REVIEWED)
    IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD)
    IntegrationTaskFactory.create(status=IntegrationTaskStatus.READ)

    result = IntegrationTask.objects.processed()

    assert set(result) == {processed_task, reviewed_task}


@pytest.mark.django_db
def test_with_errors_filters_to_error_statuses() -> None:
    """Test that with_errors() filters to ERROR and UNREAD_ERROR statuses."""
    error_task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.ERROR)
    unread_error_task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD_ERROR)
    IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD)
    IntegrationTaskFactory.create(status=IntegrationTaskStatus.PROCESSED)

    result = IntegrationTask.objects.with_errors()

    assert set(result) == {error_task, unread_error_task}


@pytest.mark.django_db
def test_junked_filters_to_junk_status() -> None:
    """Test that junked() filters to tasks with JUNK status."""
    junked_task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.JUNK)
    IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD)
    IntegrationTaskFactory.create(status=IntegrationTaskStatus.PROCESSED)

    result = IntegrationTask.objects.junked()

    assert list(result) == [junked_task]


@pytest.mark.django_db
def test_not_junked_excludes_junk_status() -> None:
    """Test that not_junked() excludes tasks with JUNK status."""
    unread_task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD)
    processed_task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.PROCESSED)
    IntegrationTaskFactory.create(status=IntegrationTaskStatus.JUNK)

    result = IntegrationTask.objects.not_junked()

    assert set(result) == {unread_task, processed_task}


@pytest.mark.django_db
def test_faxes_filters_to_fax_channel() -> None:
    """Test that faxes() filters to tasks with FAX channel."""
    fax_task = IntegrationTaskFactory.create(channel=IntegrationTaskChannel.FAX)
    IntegrationTaskFactory.create(channel=IntegrationTaskChannel.DOCUMENT_UPLOAD)
    IntegrationTaskFactory.create(channel=IntegrationTaskChannel.FROM_INTEGRATION_ENGINE)

    result = IntegrationTask.objects.faxes()

    assert list(result) == [fax_task]


@pytest.mark.django_db
def test_uploads_filters_to_document_upload_channel() -> None:
    """Test that uploads() filters to tasks with DOCUMENT_UPLOAD channel."""
    upload_task = IntegrationTaskFactory.create(channel=IntegrationTaskChannel.DOCUMENT_UPLOAD)
    IntegrationTaskFactory.create(channel=IntegrationTaskChannel.FAX)

    result = IntegrationTask.objects.uploads()

    assert list(result) == [upload_task]


@pytest.mark.django_db
def test_from_integration_engine_filters_correctly() -> None:
    """Test that from_integration_engine() filters to correct channel."""
    engine_task = IntegrationTaskFactory.create(
        channel=IntegrationTaskChannel.FROM_INTEGRATION_ENGINE
    )
    IntegrationTaskFactory.create(channel=IntegrationTaskChannel.FAX)

    result = IntegrationTask.objects.from_integration_engine()

    assert list(result) == [engine_task]


@pytest.mark.django_db
def test_from_patient_portal_filters_correctly() -> None:
    """Test that from_patient_portal() filters to correct channel."""
    portal_task = IntegrationTaskFactory.create(channel=IntegrationTaskChannel.FROM_PATIENT_PORTAL)
    IntegrationTaskFactory.create(channel=IntegrationTaskChannel.FAX)

    result = IntegrationTask.objects.from_patient_portal()

    assert list(result) == [portal_task]


@pytest.mark.django_db
def test_for_patient_filters_by_patient_id() -> None:
    """Test that for_patient() filters tasks by patient ID."""
    patient = PatientFactory.create()
    patient_task = IntegrationTaskFactory.create(patient=patient)
    IntegrationTaskFactory.create()  # Different patient

    result = IntegrationTask.objects.for_patient(str(patient.id))

    assert list(result) == [patient_task]


@pytest.mark.django_db
def test_queryset_methods_can_be_chained() -> None:
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
def test_is_fax_returns_true_for_fax_channel() -> None:
    """Test that is_fax returns True for FAX channel."""
    task = IntegrationTaskFactory.create(channel=IntegrationTaskChannel.FAX)
    assert task.is_fax is True


@pytest.mark.django_db
def test_is_fax_returns_false_for_other_channels() -> None:
    """Test that is_fax returns False for non-FAX channels."""
    task = IntegrationTaskFactory.create(channel=IntegrationTaskChannel.DOCUMENT_UPLOAD)
    assert task.is_fax is False


@pytest.mark.django_db
def test_is_pending_returns_true_for_unread() -> None:
    """Test that is_pending returns True for UNREAD status."""
    task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD)
    assert task.is_pending is True


@pytest.mark.django_db
def test_is_pending_returns_true_for_read() -> None:
    """Test that is_pending returns True for READ status."""
    task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.READ)
    assert task.is_pending is True


@pytest.mark.django_db
def test_is_pending_returns_false_for_processed() -> None:
    """Test that is_pending returns False for PROCESSED status."""
    task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.PROCESSED)
    assert task.is_pending is False


@pytest.mark.django_db
def test_is_processed_returns_true_for_processed() -> None:
    """Test that is_processed returns True for PROCESSED status."""
    task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.PROCESSED)
    assert task.is_processed is True


@pytest.mark.django_db
def test_is_processed_returns_true_for_reviewed() -> None:
    """Test that is_processed returns True for REVIEWED status."""
    task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.REVIEWED)
    assert task.is_processed is True


@pytest.mark.django_db
def test_is_processed_returns_false_for_unread() -> None:
    """Test that is_processed returns False for UNREAD status."""
    task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD)
    assert task.is_processed is False


@pytest.mark.django_db
def test_has_error_returns_true_for_error() -> None:
    """Test that has_error returns True for ERROR status."""
    task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.ERROR)
    assert task.has_error is True


@pytest.mark.django_db
def test_has_error_returns_true_for_unread_error() -> None:
    """Test that has_error returns True for UNREAD_ERROR status."""
    task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD_ERROR)
    assert task.has_error is True


@pytest.mark.django_db
def test_has_error_returns_false_for_unread() -> None:
    """Test that has_error returns False for UNREAD status."""
    task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD)
    assert task.has_error is False


@pytest.mark.django_db
def test_is_junked_returns_true_for_junk() -> None:
    """Test that is_junked returns True for JUNK status."""
    task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.JUNK)
    assert task.is_junked is True


@pytest.mark.django_db
def test_is_junked_returns_false_for_other_statuses() -> None:
    """Test that is_junked returns False for non-JUNK statuses."""
    task = IntegrationTaskFactory.create(status=IntegrationTaskStatus.UNREAD)
    assert task.is_junked is False


@pytest.mark.django_db
def test_review_for_task_filters_by_task_id() -> None:
    """Test that for_task() filters reviews by task ID."""
    task = IntegrationTaskFactory.create()
    review = IntegrationTaskReviewFactory.create(task=task)
    IntegrationTaskReviewFactory.create()  # Different task

    result = IntegrationTaskReview.objects.for_task(str(task.id))

    assert list(result) == [review]


@pytest.mark.django_db
def test_review_junked_filters_to_junked_reviews() -> None:
    """Test that junked() filters to reviews with junked=True."""
    junked_review = IntegrationTaskReviewFactory.create(junked=True)
    IntegrationTaskReviewFactory.create(junked=False)

    result = IntegrationTaskReview.objects.junked()

    assert list(result) == [junked_review]


@pytest.mark.django_db
def test_review_not_junked_filters_to_non_junked_reviews() -> None:
    """Test that not_junked() filters to reviews with junked=False."""
    active_review = IntegrationTaskReviewFactory.create(junked=False)
    IntegrationTaskReviewFactory.create(junked=True)

    result = IntegrationTaskReview.objects.not_junked()

    assert list(result) == [active_review]


@pytest.mark.django_db
def test_review_active_is_alias_for_not_junked() -> None:
    """Test that active() is an alias for not_junked()."""
    active_review = IntegrationTaskReviewFactory.create(junked=False)
    IntegrationTaskReviewFactory.create(junked=True)

    result = IntegrationTaskReview.objects.active()

    assert list(result) == [active_review]


@pytest.mark.django_db
def test_review_by_reviewer_filters_by_reviewer_id() -> None:
    """Test that by_reviewer() filters reviews by reviewer ID."""
    staff = StaffFactory.create()
    review = IntegrationTaskReviewFactory.create(reviewer=staff)
    IntegrationTaskReviewFactory.create()  # Different reviewer

    result = IntegrationTaskReview.objects.by_reviewer(staff.id)

    assert list(result) == [review]


@pytest.mark.django_db
def test_review_queryset_methods_can_be_chained() -> None:
    """Test that QuerySet methods can be chained together."""
    task = IntegrationTaskFactory.create()
    staff = StaffFactory.create()
    target_review = IntegrationTaskReviewFactory.create(
        task=task,
        reviewer=staff,
        junked=False,
    )
    IntegrationTaskReviewFactory.create(
        task=task,
        reviewer=staff,
        junked=True,
    )
    IntegrationTaskReviewFactory.create(
        reviewer=staff,
        junked=False,
    )

    result = IntegrationTaskReview.objects.for_task(str(task.id)).by_reviewer(staff.id).active()

    assert list(result) == [target_review]


@pytest.mark.django_db
def test_review_is_active_returns_true_for_non_junked() -> None:
    """Test that is_active returns True for non-junked reviews."""
    review = IntegrationTaskReviewFactory.create(junked=False)
    assert review.is_active is True


@pytest.mark.django_db
def test_review_is_active_returns_false_for_junked() -> None:
    """Test that is_active returns False for junked reviews."""
    review = IntegrationTaskReviewFactory.create(junked=True)
    assert review.is_active is False
