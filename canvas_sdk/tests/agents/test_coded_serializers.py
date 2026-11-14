"""Each read tool's row names its record by the record's first coding."""

from collections.abc import Callable
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest

from canvas_sdk.agents import standard_tools as standard_tools_module  # noqa: F401
from canvas_sdk.agents.standard_tools import (
    _serialize_allergy,
    _serialize_assessment,
    _serialize_immunization,
    _serialize_lab_value,
    _serialize_medication,
    _serialize_medication_statement,
    _serialize_prescription,
    _serialize_stop_med_event,
    _serialize_vital,
)

CODING = SimpleNamespace(display="Metformin 500 mg tablet", name="Hemoglobin A1c", code="4548-4")


def _coded() -> Any:
    """A record whose codings are CODING; its other fields are stand-ins."""
    record = MagicMock()
    record.codings.all.return_value = [CODING]
    return record


def _holding(attribute: str, **fields: Any) -> Callable[[], Any]:
    def build() -> Any:
        record = MagicMock(**fields)
        setattr(record, attribute, _coded())
        return record

    return build


@pytest.mark.parametrize(
    ("serialize", "build", "field", "expected"),
    [
        (_serialize_medication, _coded, "name", CODING.display),
        (_serialize_lab_value, _coded, "test", CODING.name),
        (_serialize_allergy, _coded, "display", CODING.display),
        (_serialize_allergy, _coded, "code", CODING.code),
        (_serialize_immunization, _coded, "display", CODING.display),
        (_serialize_vital, _coded, "code", CODING.code),
        (_serialize_assessment, _holding("condition"), "condition_display", CODING.display),
        (
            _serialize_medication_statement,
            _holding("medication"),
            "medication_name",
            CODING.display,
        ),
        (
            _serialize_prescription,
            _holding("medication", response_type=""),
            "medication_name",
            CODING.display,
        ),
        (_serialize_stop_med_event, _holding("medication"), "medication_name", CODING.display),
    ],
    ids=[
        "medication",
        "lab value",
        "allergy display",
        "allergy code",
        "immunization",
        "vital",
        "assessment",
        "medication statement",
        "prescription",
        "stop medication",
    ],
)
def test_a_row_names_its_record_by_its_first_coding(
    serialize: Callable[[Any], dict[str, Any]], build: Callable[[], Any], field: str, expected: str
) -> None:
    """Read from the prefetched codings, which a row without them would name as unknown."""
    assert serialize(build())[field] == expected
