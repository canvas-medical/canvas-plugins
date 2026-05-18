from unittest.mock import MagicMock, patch

import pytest
from data_integration_example.handlers.data_integration_handler import DataIntegrationHandler
from pydantic import ValidationError

from canvas_sdk.events import EventType

MODULE = "data_integration_example.handlers.data_integration_handler"


# ---------------------------------------------------------------------------
# compute() routing
# ---------------------------------------------------------------------------


def test_compute_returns_empty_list_when_document_id_missing(mock_event: MagicMock) -> None:
    """Missing document.id short-circuits before any effect is created."""
    mock_event.context = {"document": {}}
    handler = DataIntegrationHandler(event=mock_event)
    assert handler.compute() == []


def test_compute_routes_document_received_event(mock_event: MagicMock, document_id: str) -> None:
    """DOCUMENT_RECEIVED routes to _handle_document_received."""
    mock_event.type = EventType.DOCUMENT_RECEIVED
    handler = DataIntegrationHandler(event=mock_event)

    with patch.object(handler, "_handle_document_received", return_value=[]) as mock_handle:
        handler.compute()
        mock_handle.assert_called_once_with(document_id)


@pytest.mark.parametrize(
    "event_type",
    [
        EventType.DOCUMENT_LINKED_TO_PATIENT,
        EventType.DOCUMENT_CATEGORIZED,
        EventType.DOCUMENT_REVIEWER_ASSIGNED,
        EventType.DOCUMENT_FIELDS_UPDATED,
        EventType.DOCUMENT_REVIEWED,
        EventType.DOCUMENT_DELETED,
    ],
)
def test_compute_returns_empty_list_for_non_received_events(
    mock_event: MagicMock, event_type: int
) -> None:
    """Lifecycle events (log-only or no-op) return an empty list."""
    mock_event.type = event_type
    handler = DataIntegrationHandler(event=mock_event)
    result = handler.compute()
    assert result == []


# ---------------------------------------------------------------------------
# _handle_document_received
# ---------------------------------------------------------------------------


def test_handle_document_received_collects_all_four_effects(
    mock_event: MagicMock, document_id: str
) -> None:
    """All four effect creators are called and their results are returned."""
    handler = DataIntegrationHandler(event=mock_event)

    fake_effects = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
    with (
        patch.object(handler, "_create_link_document_effect", return_value=fake_effects[0]),
        patch.object(handler, "_create_assign_reviewer_effect", return_value=fake_effects[1]),
        patch.object(handler, "_create_categorize_document_effect", return_value=fake_effects[2]),
        patch.object(
            handler, "_create_prefill_document_fields_effect", return_value=fake_effects[3]
        ),
    ):
        result = handler._handle_document_received(document_id)

    assert result == fake_effects


def test_handle_document_received_skips_none_effects(
    mock_event: MagicMock, document_id: str
) -> None:
    """Effects that return None (e.g. no patient found) are omitted."""
    handler = DataIntegrationHandler(event=mock_event)
    good_effect = MagicMock()

    with (
        patch.object(handler, "_create_link_document_effect", return_value=None),
        patch.object(handler, "_create_assign_reviewer_effect", return_value=good_effect),
        patch.object(handler, "_create_categorize_document_effect", return_value=None),
        patch.object(handler, "_create_prefill_document_fields_effect", return_value=None),
    ):
        result = handler._handle_document_received(document_id)

    assert result == [good_effect]


# ---------------------------------------------------------------------------
# _create_link_document_effect
# ---------------------------------------------------------------------------


def test_create_link_document_effect_links_to_first_patient(
    mock_event: MagicMock, document_id: str
) -> None:
    """LinkDocumentToPatient is constructed with the first patient's key and applied."""
    handler = DataIntegrationHandler(event=mock_event)

    mock_patient = MagicMock()
    mock_patient.id = "patient-key-123"
    mock_applied = MagicMock()

    with (
        patch(f"{MODULE}.Patient.objects.first", return_value=mock_patient),
        patch(f"{MODULE}.LinkDocumentToPatient") as mock_effect_cls,
    ):
        mock_effect_cls.return_value.apply.return_value = mock_applied
        result = handler._create_link_document_effect(document_id)

    mock_effect_cls.assert_called_once()
    call_kwargs = mock_effect_cls.call_args.kwargs
    assert call_kwargs["document_id"] == document_id
    assert call_kwargs["patient_key"] == "patient-key-123"
    assert result is mock_applied


def test_create_link_document_effect_returns_none_when_no_patient(
    mock_event: MagicMock, document_id: str
) -> None:
    """Returns None and does not call the effect when no patient exists in the database."""
    handler = DataIntegrationHandler(event=mock_event)

    with patch(f"{MODULE}.Patient.objects.first", return_value=None):
        result = handler._create_link_document_effect(document_id)

    assert result is None


def test_create_link_document_effect_handles_validation_error(
    mock_event: MagicMock, document_id: str
) -> None:
    """Returns None and logs the error when LinkDocumentToPatient raises ValidationError."""
    handler = DataIntegrationHandler(event=mock_event)

    mock_patient = MagicMock()
    with (
        patch(f"{MODULE}.Patient.objects.first", return_value=mock_patient),
        patch(
            f"{MODULE}.LinkDocumentToPatient",
            side_effect=ValidationError.from_exception_data("", []),
        ),
    ):
        result = handler._create_link_document_effect(document_id)

    assert result is None


# ---------------------------------------------------------------------------
# _create_assign_reviewer_effect
# ---------------------------------------------------------------------------


def test_create_assign_reviewer_effect_assigns_staff(
    mock_event: MagicMock, document_id: str
) -> None:
    """When staff exists, AssignDocumentReviewer is built with reviewer_id."""
    handler = DataIntegrationHandler(event=mock_event)

    mock_staff = MagicMock()
    mock_staff.id = "staff-id-abc"
    mock_team = MagicMock()
    mock_team.id = "team-id-xyz"
    mock_applied = MagicMock()

    with (
        patch(f"{MODULE}.Staff.objects.first", return_value=mock_staff),
        patch(f"{MODULE}.Team.objects.first", return_value=mock_team),
        patch(f"{MODULE}.AssignDocumentReviewer") as mock_effect_cls,
    ):
        mock_effect_cls.return_value.apply.return_value = mock_applied
        result = handler._create_assign_reviewer_effect(document_id)

    call_kwargs = mock_effect_cls.call_args.kwargs
    assert call_kwargs["reviewer_id"] == str(mock_staff.id)
    assert result is mock_applied


def test_create_assign_reviewer_effect_falls_back_to_team(
    mock_event: MagicMock, document_id: str
) -> None:
    """When no staff exists, the team is used instead."""
    handler = DataIntegrationHandler(event=mock_event)

    mock_team = MagicMock()
    mock_team.id = "team-id-xyz"
    mock_applied = MagicMock()

    with (
        patch(f"{MODULE}.Staff.objects.first", return_value=None),
        patch(f"{MODULE}.Team.objects.first", return_value=mock_team),
        patch(f"{MODULE}.AssignDocumentReviewer") as mock_effect_cls,
    ):
        mock_effect_cls.return_value.apply.return_value = mock_applied
        result = handler._create_assign_reviewer_effect(document_id)

    call_kwargs = mock_effect_cls.call_args.kwargs
    assert call_kwargs["team_id"] == str(mock_team.id)
    assert "reviewer_id" not in call_kwargs
    assert result is mock_applied


def test_create_assign_reviewer_effect_returns_none_when_no_staff_or_team(
    mock_event: MagicMock, document_id: str
) -> None:
    """Returns None when neither staff nor team exists — no effect is created."""
    handler = DataIntegrationHandler(event=mock_event)

    with (
        patch(f"{MODULE}.Staff.objects.first", return_value=None),
        patch(f"{MODULE}.Team.objects.first", return_value=None),
    ):
        result = handler._create_assign_reviewer_effect(document_id)

    assert result is None


# ---------------------------------------------------------------------------
# _create_categorize_document_effect
# ---------------------------------------------------------------------------


def test_create_categorize_document_effect_selects_lab_report(
    mock_event: MagicMock, document_id: str, available_document_types: list[dict]
) -> None:
    """When 'Lab Report' is in available_document_types it is used."""
    handler = DataIntegrationHandler(event=mock_event)
    mock_applied = MagicMock()

    with patch(f"{MODULE}.CategorizeDocument") as mock_effect_cls:
        mock_effect_cls.return_value.apply.return_value = mock_applied
        result = handler._create_categorize_document_effect(document_id)

    call_kwargs = mock_effect_cls.call_args.kwargs
    assert call_kwargs["document_type"]["key"] == "lab_report_key_abc"
    assert call_kwargs["document_type"]["name"] == "Lab Report"
    assert result is mock_applied


def test_create_categorize_document_effect_falls_back_to_first_type(
    mock_event: MagicMock, document_id: str
) -> None:
    """When no 'Lab Report' exists the first available type is used."""
    mock_event.context["available_document_types"] = [
        {
            "key": "other_key",
            "name": "Other Report",
            "report_type": "CLINICAL",
            "template_type": None,
        }
    ]
    handler = DataIntegrationHandler(event=mock_event)

    with patch(f"{MODULE}.CategorizeDocument") as mock_effect_cls:
        mock_effect_cls.return_value.apply.return_value = MagicMock()
        handler._create_categorize_document_effect(document_id)

    call_kwargs = mock_effect_cls.call_args.kwargs
    assert call_kwargs["document_type"]["name"] == "Other Report"


def test_create_categorize_document_effect_returns_none_when_no_types(
    mock_event: MagicMock, document_id: str
) -> None:
    """Returns None when available_document_types is empty in the event context."""
    mock_event.context["available_document_types"] = []
    handler = DataIntegrationHandler(event=mock_event)

    result = handler._create_categorize_document_effect(document_id)

    assert result is None


def test_create_categorize_document_effect_uses_report_type_enum(
    mock_event: MagicMock, document_id: str
) -> None:
    """report_type must be a ReportType instance, not a plain string."""
    from canvas_sdk.effects.data_integration.types import ReportType

    handler = DataIntegrationHandler(event=mock_event)

    with patch(f"{MODULE}.CategorizeDocument") as mock_effect_cls:
        mock_effect_cls.return_value.apply.return_value = MagicMock()
        handler._create_categorize_document_effect(document_id)

    call_kwargs = mock_effect_cls.call_args.kwargs
    assert isinstance(call_kwargs["document_type"]["report_type"], ReportType)


def test_create_categorize_document_effect_uses_template_type_enum(
    mock_event: MagicMock, document_id: str
) -> None:
    """template_type must be a TemplateType instance, not a plain string."""
    from canvas_sdk.effects.data_integration.types import TemplateType

    handler = DataIntegrationHandler(event=mock_event)

    with patch(f"{MODULE}.CategorizeDocument") as mock_effect_cls:
        mock_effect_cls.return_value.apply.return_value = MagicMock()
        handler._create_categorize_document_effect(document_id)

    call_kwargs = mock_effect_cls.call_args.kwargs
    assert isinstance(call_kwargs["document_type"]["template_type"], TemplateType)


def test_create_categorize_document_effect_template_type_none_for_no_template(
    mock_event: MagicMock, document_id: str
) -> None:
    """template_type is None when the document type has no template."""
    mock_event.context["available_document_types"] = [
        {
            "key": "admin_key",
            "name": "Administrative",
            "report_type": "ADMINISTRATIVE",
            "template_type": None,
        }
    ]
    handler = DataIntegrationHandler(event=mock_event)

    with patch(f"{MODULE}.CategorizeDocument") as mock_effect_cls:
        mock_effect_cls.return_value.apply.return_value = MagicMock()
        handler._create_categorize_document_effect(document_id)

    call_kwargs = mock_effect_cls.call_args.kwargs
    assert call_kwargs["document_type"]["template_type"] is None


# ---------------------------------------------------------------------------
# _create_prefill_document_fields_effect
# ---------------------------------------------------------------------------


def test_create_prefill_document_fields_effect_applies_all_templates(
    mock_event: MagicMock, document_id: str
) -> None:
    """PrefillDocumentFields is constructed with PREFILL_TEMPLATES and applied."""
    from data_integration_example.templates import PREFILL_TEMPLATES

    handler = DataIntegrationHandler(event=mock_event)
    mock_applied = MagicMock()

    with patch(f"{MODULE}.PrefillDocumentFields") as mock_effect_cls:
        mock_effect_cls.return_value.apply.return_value = mock_applied
        result = handler._create_prefill_document_fields_effect(document_id)

    call_kwargs = mock_effect_cls.call_args.kwargs
    assert call_kwargs["document_id"] == document_id
    assert call_kwargs["templates"] is PREFILL_TEMPLATES
    assert result is mock_applied


def test_create_prefill_document_fields_effect_handles_validation_error(
    mock_event: MagicMock, document_id: str
) -> None:
    """Returns None and logs the error when PrefillDocumentFields raises ValidationError."""
    handler = DataIntegrationHandler(event=mock_event)

    with patch(
        f"{MODULE}.PrefillDocumentFields",
        side_effect=ValidationError.from_exception_data("", []),
    ):
        result = handler._create_prefill_document_fields_effect(document_id)

    assert result is None
