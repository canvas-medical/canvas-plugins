"""Tests for the example auto-populate command handlers.

Each handler is described by a HandlerCase dataclass and the same set of
parametrized tests runs against both. See _compute_with_mocks for the shared
setup that patches the SDK Command class and the logger.

To run: `uv run pytest` (coverage runs automatically — see pyproject.toml).
"""

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock, patch

import pytest
from example_commands.handlers.example_imaging_order import AutoPopulateImagingOrderCommand
from example_commands.handlers.example_refer import AutoPopulateReferCommand

from canvas_sdk.commands import ImagingOrderCommand
from canvas_sdk.commands.commands.refer import ReferCommand
from canvas_sdk.events import EventType


@dataclass
class HandlerCase:
    """Per-handler parameters shared across the parametrized tests."""

    name: str
    handler_cls: Any
    handler_module: str
    real_command_cls: Any
    expected_event: int
    expected_priorities: list[Any]
    expected_kwargs: dict[str, Any]
    service_provider_fields: dict[str, str]

    @property
    def command_path(self) -> str:
        """Dotted path to the SDK Command class as imported into the handler module."""
        return f"{self.handler_module}.{self.real_command_cls.__name__}"

    @property
    def log_path(self) -> str:
        """Dotted path to the logger imported into the handler module."""
        return f"{self.handler_module}.log"


REFER_CASE = HandlerCase(
    name="refer",
    handler_cls=AutoPopulateReferCommand,
    handler_module="example_commands.handlers.example_refer",
    real_command_cls=ReferCommand,
    expected_event=EventType.REFER_COMMAND__POST_ORIGINATE,
    expected_priorities=[
        ReferCommand.Priority.URGENT,
        ReferCommand.Priority.ROUTINE,
        ReferCommand.Priority.STAT,
        None,
    ],
    expected_kwargs={
        "diagnosis_codes": ["E119"],
        "clinical_question": ReferCommand.ClinicalQuestion.DIAGNOSTIC_UNCERTAINTY,
        "comment": "this is a comment",
        "notes_to_specialist": "This is a note to specialist",
        "include_visit_note": True,
    },
    service_provider_fields={
        "first_name": "Clinic",
        "last_name": "Acupuncture",
        "practice_name": "Clinic Acupuncture",
        "specialty": "Acupuncture",
        "business_address": "Street Address",
        "business_phone": "1234569874",
        "business_fax": "1234569874",
    },
)

IMAGING_CASE = HandlerCase(
    name="imaging_order",
    handler_cls=AutoPopulateImagingOrderCommand,
    handler_module="example_commands.handlers.example_imaging_order",
    real_command_cls=ImagingOrderCommand,
    expected_event=EventType.IMAGING_ORDER_COMMAND__POST_ORIGINATE,
    expected_priorities=[
        ImagingOrderCommand.Priority.ROUTINE,
        ImagingOrderCommand.Priority.URGENT,
        ImagingOrderCommand.Priority.STAT,
        None,
    ],
    expected_kwargs={
        "image_code": "G0204",
        "diagnosis_codes": ["E119"],
        "additional_details": "Auto-populated imaging order details",
        "comment": "Example comment for imaging order",
    },
    service_provider_fields={
        "first_name": "Clinic",
        "last_name": "Imaging",
        "practice_name": "Clinic Imaging",
        "specialty": "Radiology",
        "business_address": "123 Imaging St",
        "business_phone": "1234569874",
        "business_fax": "1234569874",
    },
)

CASES = [REFER_CASE, IMAGING_CASE]


def _compute_with_mocks(case: HandlerCase, target_id: str = "test-uuid") -> SimpleNamespace:
    """Run handler.compute() with the SDK Command class and logger patched.

    The real Priority / ClinicalQuestion enums are attached to the mocked
    Command class so the handler still picks real enum values. Returns a
    namespace with the effects, the mocks, and the kwargs the command was
    called with.
    """
    event = Mock(target=Mock(id=target_id))
    handler = case.handler_cls(event=event)
    with patch(case.command_path) as cmd_cls, patch(case.log_path) as mock_log:
        cmd_instance = Mock()
        cmd_instance.edit.return_value = Mock()
        cmd_cls.return_value = cmd_instance
        cmd_cls.Priority = case.real_command_cls.Priority
        if hasattr(case.real_command_cls, "ClinicalQuestion"):
            cmd_cls.ClinicalQuestion = case.real_command_cls.ClinicalQuestion
        effects = handler.compute()
    return SimpleNamespace(
        effects=effects,
        cmd_cls=cmd_cls,
        cmd_instance=cmd_instance,
        mock_log=mock_log,
        call_kwargs=cmd_cls.call_args.kwargs,
    )


# ---------------------------------------------------------------------------
# Parametrized handler tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.name)
def test_handler_responds_to_expected_event(case: HandlerCase) -> None:
    """Handler subscribes to the post-originate event for its command type."""
    assert EventType.Name(case.expected_event) in case.handler_cls.RESPONDS_TO


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.name)
def test_handler_has_required_attributes(case: HandlerCase) -> None:
    """Handler exposes the contract expected by the plugin runner."""
    assert hasattr(case.handler_cls, "RESPONDS_TO")
    assert hasattr(case.handler_cls, "compute")


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.name)
def test_compute_returns_one_effect(case: HandlerCase) -> None:
    """compute() returns exactly one Effect."""
    result = _compute_with_mocks(case)
    assert len(result.effects) == 1
    assert result.effects[0] is not None


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.name)
def test_compute_populates_command_kwargs(case: HandlerCase) -> None:
    """All static command kwargs (everything except priority/service_provider) are populated."""
    result = _compute_with_mocks(case, target_id=f"{case.name}-uuid")

    result.cmd_cls.assert_called_once()
    assert result.call_kwargs["command_uuid"] == f"{case.name}-uuid"
    for key, expected in case.expected_kwargs.items():
        assert result.call_kwargs[key] == expected
    assert result.call_kwargs["priority"] in case.expected_priorities
    assert result.call_kwargs["service_provider"] is not None
    result.cmd_instance.edit.assert_called_once()


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.name)
def test_compute_populates_service_provider(case: HandlerCase) -> None:
    """All service_provider fields on the emitted command match the handler's hardcoded values."""
    result = _compute_with_mocks(case)
    sp = result.call_kwargs["service_provider"]
    for attr, expected in case.service_provider_fields.items():
        assert getattr(sp, attr) == expected


@pytest.mark.parametrize("case", CASES, ids=lambda c: c.name)
def test_compute_logs_command_uuid(case: HandlerCase) -> None:
    """At least one log.info call includes the command UUID."""
    target_id = f"{case.name}-uuid-log"
    result = _compute_with_mocks(case, target_id=target_id)
    log_messages = [call.args[0] for call in result.mock_log.info.call_args_list]
    assert log_messages, "expected at least one log.info call"
    assert any(target_id in msg for msg in log_messages)
