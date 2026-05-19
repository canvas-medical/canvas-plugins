from unittest.mock import MagicMock

import pytest

from canvas_sdk.events import EventType


@pytest.fixture
def document_id() -> str:
    """Stable document UUID used across tests."""
    return "abc123-document-id"


@pytest.fixture
def available_document_types() -> list[dict]:
    """Two document types including Lab Report, matching the shape supplied by the DOCUMENT_RECEIVED context."""
    return [
        {
            "key": "lab_report_key_abc",
            "name": "Lab Report",
            "report_type": "CLINICAL",
            "template_type": "LabReportTemplate",
        },
        {
            "key": "imaging_report_key_xyz",
            "name": "Imaging Report",
            "report_type": "CLINICAL",
            "template_type": "ImagingReportTemplate",
        },
    ]


@pytest.fixture
def mock_event(document_id: str, available_document_types: list[dict]) -> MagicMock:
    """DOCUMENT_RECEIVED event with a document id and the standard available_document_types list."""
    event = MagicMock()
    event.type = EventType.DOCUMENT_RECEIVED
    event.context = {
        "document": {"id": document_id},
        "available_document_types": available_document_types,
    }
    return event
