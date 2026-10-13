import json
from collections.abc import Callable, Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.fax import (
    FaxImagingOrderEffect,
    FaxLabOrderEffect,
    FaxLetterEffect,
    FaxNoteEffect,
    FaxReferralEffect,
)
from canvas_sdk.effects.fax.base import (
    BaseFaxEffectOptionalRecipient,
    BaseFaxEffectRequiredRecipient,
)

DOCUMENT_EFFECTS = [
    pytest.param(
        FaxReferralEffect, "referral_id", "Referral", EffectType.FAX_REFERRAL, id="referral"
    ),
    pytest.param(
        FaxImagingOrderEffect,
        "imaging_order_id",
        "Imaging order",
        EffectType.FAX_IMAGING_ORDER,
        id="imaging_order",
    ),
    pytest.param(
        FaxLabOrderEffect, "lab_order_id", "Lab order", EffectType.FAX_LAB_ORDER, id="lab_order"
    ),
    pytest.param(FaxLetterEffect, "letter_id", "Letter", EffectType.FAX_LETTER, id="letter"),
]


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock], None, None]:
    """Mock the existence checks for practice locations and every faxable document."""
    with (
        patch("canvas_sdk.v1.data.PracticeLocation.objects") as mock_pl,
        patch("canvas_sdk.v1.data.Referral.objects") as mock_referral,
        patch("canvas_sdk.v1.data.ImagingOrder.objects") as mock_imaging_order,
        patch("canvas_sdk.v1.data.LabOrder.objects") as mock_lab_order,
        patch("canvas_sdk.v1.data.Letter.objects") as mock_letter,
    ):
        mocks = {
            "practice_location": mock_pl,
            "referral_id": mock_referral,
            "imaging_order_id": mock_imaging_order,
            "lab_order_id": mock_lab_order,
            "letter_id": mock_letter,
        }
        for mock in mocks.values():
            mock.filter.return_value.exists.return_value = True
        yield mocks


@pytest.mark.parametrize(("effect_class", "id_field", "label", "effect_type"), DOCUMENT_EFFECTS)
def test_apply_sends_document_id_and_recipient(
    mock_db_queries: dict[str, MagicMock],
    effect_class: Callable[..., BaseFaxEffectOptionalRecipient],
    id_field: str,
    label: str,
    effect_type: int,
) -> None:
    """Each effect has its own type and sends the document id with the recipient."""
    document_id = uuid4()
    effect = effect_class(
        **{id_field: document_id},
        recipient_name="Dr. John Doe",
        recipient_fax_number="555-123-4567",
    ).apply()

    assert effect.type == effect_type
    assert json.loads(effect.payload)["data"] == {
        id_field: str(document_id),
        "recipient_name": "Dr. John Doe",
        "recipient_fax_number": "555-123-4567",
        "include_coversheet": False,
        "subject": None,
        "comment": None,
        "location_id": None,
    }
    mock_db_queries[id_field].filter.assert_called_once_with(id=document_id)


@pytest.mark.parametrize(("effect_class", "id_field", "label", "effect_type"), DOCUMENT_EFFECTS)
def test_nonexistent_document_raises(
    mock_db_queries: dict[str, MagicMock],
    effect_class: Callable[..., BaseFaxEffectOptionalRecipient],
    id_field: str,
    label: str,
    effect_type: int,
) -> None:
    """Applying an effect for a document that doesn't exist raises."""
    mock_db_queries[id_field].filter.return_value.exists.return_value = False
    document_id = str(uuid4())
    effect = effect_class(
        **{id_field: document_id},
        recipient_name="Dr. John Doe",
        recipient_fax_number="555-123-4567",
    )

    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert any(
        f"{label} with ID {document_id} does not exist" in str(e) for e in exc_info.value.errors()
    )


@pytest.mark.parametrize(("effect_class", "id_field", "label", "effect_type"), DOCUMENT_EFFECTS)
def test_coversheet_fields_required(
    mock_db_queries: dict[str, MagicMock],
    effect_class: Callable[..., BaseFaxEffectOptionalRecipient],
    id_field: str,
    label: str,
    effect_type: int,
) -> None:
    """The cover sheet needs a subject, comment and location, as for FaxNoteEffect."""
    effect = effect_class(
        **{id_field: str(uuid4())},
        recipient_name="Dr. John Doe",
        recipient_fax_number="555-123-4567",
        include_coversheet=True,
    )

    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    assert len(exc_info.value.errors()) == 3


@pytest.mark.parametrize(
    ("effect_class", "id_field"),
    [
        (FaxReferralEffect, "referral_id"),
        (FaxImagingOrderEffect, "imaging_order_id"),
    ],
)
def test_recipient_is_optional_for_orders_sent_to_a_service_provider(
    mock_db_queries: dict[str, MagicMock],
    effect_class: Callable[..., BaseFaxEffectOptionalRecipient],
    id_field: str,
) -> None:
    """A referral or imaging order can leave the recipient for home-app to default."""
    effect = effect_class(**{id_field: str(uuid4())}).apply()

    data = json.loads(effect.payload)["data"]
    assert data["recipient_name"] is None
    assert data["recipient_fax_number"] is None


@pytest.mark.parametrize(
    ("effect_class", "id_field"),
    [
        (FaxLabOrderEffect, "lab_order_id"),
        (FaxLetterEffect, "letter_id"),
        (FaxNoteEffect, "note_id"),
    ],
)
def test_recipient_is_required_without_a_service_provider(
    effect_class: Callable[..., BaseFaxEffectRequiredRecipient], id_field: str
) -> None:
    """Lab orders, letters and notes have no service provider, so they need a recipient."""
    with pytest.raises(ValidationError) as exc_info:
        effect_class(**{id_field: str(uuid4())})

    assert {e["loc"][0] for e in exc_info.value.errors()} == {
        "recipient_name",
        "recipient_fax_number",
    }
