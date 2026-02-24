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


@pytest.mark.parametrize(
    ("channel", "expected"),
    [
        (IntegrationTaskChannel.FAX, True),
        (IntegrationTaskChannel.DOCUMENT_UPLOAD, False),
    ],
)
@pytest.mark.django_db
def test_is_fax(channel: str, expected: bool) -> None:
    """Test that is_fax reflects whether the channel is FAX."""
    task = IntegrationTaskFactory.create(channel=channel)
    assert task.is_fax is expected


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (IntegrationTaskStatus.UNREAD, True),
        (IntegrationTaskStatus.READ, True),
        (IntegrationTaskStatus.PROCESSED, False),
    ],
)
@pytest.mark.django_db
def test_is_pending(status: str, expected: bool) -> None:
    """Test that is_pending reflects UNREAD/READ statuses."""
    task = IntegrationTaskFactory.create(status=status)
    assert task.is_pending is expected


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (IntegrationTaskStatus.PROCESSED, True),
        (IntegrationTaskStatus.REVIEWED, True),
        (IntegrationTaskStatus.UNREAD, False),
    ],
)
@pytest.mark.django_db
def test_is_processed(status: str, expected: bool) -> None:
    """Test that is_processed reflects PROCESSED/REVIEWED statuses."""
    task = IntegrationTaskFactory.create(status=status)
    assert task.is_processed is expected


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (IntegrationTaskStatus.ERROR, True),
        (IntegrationTaskStatus.UNREAD_ERROR, True),
        (IntegrationTaskStatus.UNREAD, False),
    ],
)
@pytest.mark.django_db
def test_has_error(status: str, expected: bool) -> None:
    """Test that has_error reflects ERROR/UNREAD_ERROR statuses."""
    task = IntegrationTaskFactory.create(status=status)
    assert task.has_error is expected


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (IntegrationTaskStatus.JUNK, True),
        (IntegrationTaskStatus.UNREAD, False),
    ],
)
@pytest.mark.django_db
def test_is_junked(status: str, expected: bool) -> None:
    """Test that is_junked reflects JUNK status."""
    task = IntegrationTaskFactory.create(status=status)
    assert task.is_junked is expected


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


@pytest.mark.parametrize(
    ("junked", "expected"),
    [
        (False, True),
        (True, False),
    ],
)
@pytest.mark.django_db
def test_review_is_active(junked: bool, expected: bool) -> None:
    """Test that is_active reflects the inverse of junked status."""
    review = IntegrationTaskReviewFactory.create(junked=junked)
    assert review.is_active is expected
