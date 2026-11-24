import pytest

from canvas_sdk.test_utils.factories import (
    AppointmentFactory,
    AssessmentFactory,
    CanvasUserFactory,
    CommandFactory,
    DetectedIssueMitigationFactory,
    DiagnosticViewElementFactory,
    DiagnosticViewFactory,
    DmeOrderActionEventFactory,
    ImagingOrderFactory,
    InterviewFactory,
    NoteTaskFactory,
    NoteTypeFactory,
    QuestionFactory,
    ScheduleDurationFactory,
    TaskLabelFactory,
)
from canvas_sdk.v1.data import (
    Appointment,
    Command,
    DetectedIssue,
    DiagnosticView,
    DmeOrder,
    ImagingOrder,
    Interview,
    NoteType,
    TaskLabel,
)


@pytest.mark.django_db
def test_appointments_booked_together_resolve_from_either_side() -> None:
    """Booking appointments together writes a row in each direction, so either side lists the other."""
    first, second, other = AppointmentFactory.create_batch(3)
    first.scheduled_together.add(second)
    second.scheduled_together.add(first)

    assert list(Appointment.objects.get(dbid=first.dbid).scheduled_together.all()) == [second]
    assert list(Appointment.objects.get(dbid=second.dbid).scheduled_together.all()) == [first]
    assert list(other.scheduled_together.all()) == []


@pytest.mark.django_db
def test_imaging_order_assessments_resolve_both_ways() -> None:
    """An imaging order lists its assessments, and an assessment lists its imaging orders."""
    order = ImagingOrderFactory.create()
    assessment = AssessmentFactory.create()
    AssessmentFactory.create()
    order.assessments.add(assessment)

    assert list(ImagingOrder.objects.get(dbid=order.dbid).assessments.all()) == [assessment]
    assert list(assessment.imaging_orders.all()) == [order]


@pytest.mark.django_db
def test_interview_skipped_questions_resolve_both_ways() -> None:
    """An interview lists the questions skipped in it, and a question lists those interviews."""
    interview = InterviewFactory.create()
    skipped = QuestionFactory.create()
    QuestionFactory.create()
    interview.skipped_questions.add(skipped)

    assert list(Interview.objects.get(dbid=interview.dbid).skipped_questions.all()) == [skipped]
    assert list(skipped.interview_set.all()) == [interview]


@pytest.mark.django_db
def test_note_type_possible_durations_resolve_both_ways() -> None:
    """A note type lists its schedule durations, and a duration lists its note types."""
    note_type = NoteTypeFactory.create()
    offered = ScheduleDurationFactory.create()
    ScheduleDurationFactory.create()
    note_type.possible_durations.add(offered)

    assert list(NoteType.objects.get(dbid=note_type.dbid).possible_durations.all()) == [offered]
    assert list(offered.note_types.all()) == [note_type]


@pytest.mark.django_db
def test_task_label_note_tasks_resolve_both_ways() -> None:
    """A task label lists its note tasks, and a note task lists its labels."""
    label = TaskLabelFactory.create()
    note_task = NoteTaskFactory.create()
    NoteTaskFactory.create()
    label.note_tasks.add(note_task)

    assert list(TaskLabel.objects.get(dbid=label.dbid).note_tasks.all()) == [note_task]
    assert list(note_task.labels.all()) == [label]


@pytest.mark.django_db
def test_command_edited_by_resolves_both_ways() -> None:
    """A command lists the users who edited it, and a user lists the commands they edited."""
    command = CommandFactory.create()
    editor = CanvasUserFactory.create()
    CanvasUserFactory.create()
    command.edited_by.add(editor)

    assert list(Command.objects.get(dbid=command.dbid).edited_by.all()) == [editor]
    assert list(editor.commands_edited.all()) == [command]


@pytest.mark.django_db
def test_detected_issue_mitigations_resolve_from_issue_and_author() -> None:
    """Mitigations resolve from their detected issue and from the staff member who authored them."""
    mitigation = DetectedIssueMitigationFactory.create()
    DetectedIssueMitigationFactory.create()

    issue = DetectedIssue.objects.get(dbid=mitigation.detected_issue.dbid)

    assert list(issue.mitigations.all()) == [mitigation]
    assert list(mitigation.author.detected_issue_mitigations.all()) == [mitigation]


@pytest.mark.django_db
def test_diagnostic_view_elements_resolve_from_view() -> None:
    """A diagnostic view lists its elements."""
    view = DiagnosticViewFactory.create()
    first = DiagnosticViewElementFactory.create(view=view, ordering=0)
    second = DiagnosticViewElementFactory.create(view=view, ordering=1)
    DiagnosticViewElementFactory.create()

    elements = DiagnosticView.objects.get(dbid=view.dbid).elements.order_by("ordering")

    assert list(elements) == [first, second]


@pytest.mark.django_db
def test_dme_order_action_events_resolve_from_order_and_fax() -> None:
    """A DME order lists its action events, and so does the fax that sent it."""
    event = DmeOrderActionEventFactory.create()
    DmeOrderActionEventFactory.create()

    order = DmeOrder.objects.get(dbid=event.dme_order.dbid)

    assert event.fax is not None
    assert event.originator is not None
    assert list(order.action_events.all()) == [event]
    assert list(event.fax.dmeorderactionevents.all()) == [event]
    assert list(event.originator.dmeorderactionevent_set.all()) == [event]
