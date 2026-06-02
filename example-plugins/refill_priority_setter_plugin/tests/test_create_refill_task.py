"""Tests for CreateRefillTaskHandler.

The handler reacts to PRESCRIPTION_PENDING events. When the prescription is a
refill (``prescription.is_refill``), it creates a follow-up task assigned to a
team with PROCESS_REFILL_REQUESTS responsibility, skipping duplicates.

Each test patches the SDK data queries (Prescription / Task / Team) and the
AddTask effect; ``_run_compute`` is the shared setup. New scenarios should
generally fit into the parametrized happy/skip pattern below — only break out
into a dedicated test when the scenario needs to inspect the kwargs AddTask was
called with.
"""

from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock, patch

from refill_priority_setter_plugin.handlers.create_refill_task import CreateRefillTaskHandler

from canvas_sdk.effects.task import TaskStatus
from canvas_sdk.events import EventType
from canvas_sdk.v1.data.task import TaskPriority

HANDLER_MODULE = "refill_priority_setter_plugin.handlers.create_refill_task"


def _run_compute(
    *,
    prescription: Any | None,
    patient_id: str = "patient-123",
    target_id: str = "rx-uuid-1",
    existing_task: bool = False,
    team_id: str | None = "team-1",
) -> SimpleNamespace:
    """Invoke the handler with all external lookups patched.

    Returns a namespace with the effects list and every mock the tests want to
    assert against (AddTask class + the patched queryset filters).
    """
    event = Mock(target=Mock(id=target_id))
    handler = CreateRefillTaskHandler(event=event)
    test_context = {"patient": {"id": patient_id}}

    with (
        patch.object(type(handler), "context", property(lambda self: test_context)),
        patch(f"{HANDLER_MODULE}.Prescription.objects.filter") as rx_filter,
        patch(f"{HANDLER_MODULE}.Task.objects.filter") as task_filter,
        patch(f"{HANDLER_MODULE}.Team.objects.filter") as team_filter,
        patch(f"{HANDLER_MODULE}.AddTask") as add_task_cls,
        patch(f"{HANDLER_MODULE}.log"),
    ):
        rx_filter.return_value.first.return_value = prescription
        task_filter.return_value.exists.return_value = existing_task
        team_filter.return_value.values_list.return_value.first.return_value = team_id

        add_task_instance = Mock()
        add_task_instance.apply.return_value = Mock(name="AddTaskEffect")
        add_task_cls.return_value = add_task_instance

        effects = handler.compute()

    return SimpleNamespace(
        effects=effects,
        add_task_cls=add_task_cls,
        add_task_instance=add_task_instance,
        task_filter=task_filter,
    )


def _refill(medication: str = "Lisinopril 10mg") -> Mock:
    """Build a mock Prescription that looks like a refill.

    Note: ``name`` is a reserved kwarg on ``Mock``, so we assign it after
    construction; otherwise it would set the mock's internal name instead of a
    ``.name`` attribute on the mocked Prescription.
    """
    prescription = Mock(is_refill=True, display_name=medication)
    prescription.name = medication
    return prescription


# ---------------------------------------------------------------------------
# Handler contract
# ---------------------------------------------------------------------------


def test_responds_to_prescription_pending() -> None:
    """Handler subscribes to PRESCRIPTION_PENDING."""
    assert EventType.Name(EventType.PRESCRIPTION_PENDING) in CreateRefillTaskHandler.RESPONDS_TO


def test_has_required_attributes() -> None:
    """Handler exposes the contract expected by the plugin runner."""
    assert hasattr(CreateRefillTaskHandler, "RESPONDS_TO")
    assert hasattr(CreateRefillTaskHandler, "compute")


# ---------------------------------------------------------------------------
# Short-circuit paths (handler returns [])
# ---------------------------------------------------------------------------


def test_returns_empty_when_prescription_missing() -> None:
    """No effect when the prescription lookup returns nothing."""
    result = _run_compute(prescription=None)
    assert result.effects == []
    result.add_task_cls.assert_not_called()


def test_returns_empty_for_non_refill_prescription() -> None:
    """No effect for original (non-refill) prescriptions."""
    prescription = Mock(is_refill=False, display_name="Atorvastatin 20mg")
    result = _run_compute(prescription=prescription)
    assert result.effects == []
    result.add_task_cls.assert_not_called()


def test_returns_empty_when_duplicate_task_already_exists() -> None:
    """No effect when a follow-up task already exists for the same medication/patient."""
    result = _run_compute(
        prescription=_refill("Metformin 500mg"),
        patient_id="patient-789",
        existing_task=True,
    )
    assert result.effects == []
    result.add_task_cls.assert_not_called()
    # Duplicate check used the correct filter args.
    result.task_filter.assert_called_once_with(
        title="Follow up on refill of Metformin 500mg",
        status=TaskStatus.OPEN.value,
        patient__id="patient-789",
    )


# ---------------------------------------------------------------------------
# Happy paths (handler emits one AddTask effect)
# ---------------------------------------------------------------------------


def test_creates_task_for_refill_with_team() -> None:
    """Creates an AddTask effect assigned to the refill-processing team."""
    result = _run_compute(
        prescription=_refill("Lisinopril 10mg"),
        patient_id="patient-123",
        team_id="team-456",
    )

    assert len(result.effects) == 1
    result.add_task_cls.assert_called_once_with(
        title="Follow up on refill of Lisinopril 10mg",
        priority=TaskPriority.URGENT,
        patient_id="patient-123",
        team_id="team-456",
    )
    result.add_task_instance.apply.assert_called_once()


def test_creates_task_with_no_team_when_responsibility_unfilled() -> None:
    """Still creates a task (unassigned) when no team carries the responsibility."""
    result = _run_compute(
        prescription=_refill("Aspirin 81mg"),
        patient_id="patient-999",
        team_id=None,
    )

    assert len(result.effects) == 1
    result.add_task_cls.assert_called_once_with(
        title="Follow up on refill of Aspirin 81mg",
        priority=TaskPriority.URGENT,
        patient_id="patient-999",
        team_id=None,
    )


def test_medication_name_uses_display_name() -> None:
    """display_name is preferred over name when both are present."""
    prescription = Mock(is_refill=True, display_name="Atorvastatin 20mg", name="atorvastatin")
    result = _run_compute(prescription=prescription)

    call_kwargs = result.add_task_cls.call_args.kwargs
    assert call_kwargs["title"] == "Follow up on refill of Atorvastatin 20mg"


def test_medication_name_falls_back_to_name() -> None:
    """Falls back to .name when display_name is missing."""
    prescription = Mock(is_refill=True, display_name=None)
    prescription.name = "generic-med"
    result = _run_compute(prescription=prescription)

    call_kwargs = result.add_task_cls.call_args.kwargs
    assert call_kwargs["title"] == "Follow up on refill of generic-med"
