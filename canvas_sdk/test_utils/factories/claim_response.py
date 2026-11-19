import datetime
from decimal import Decimal

import factory

from canvas_sdk.v1.data import ClaimResponse, ClaimResponseDetail, ClaimResponseStatus


class ClaimResponseFactory(factory.django.DjangoModelFactory[ClaimResponse]):
    """Factory for creating a ClaimResponse."""

    class Meta:
        model = ClaimResponse

    originator = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    claim = factory.SubFactory("canvas_sdk.test_utils.factories.ClaimFactory")
    clearinghouse_claim_id = factory.Sequence(lambda n: f"CH{n:06d}")
    from_date = datetime.date(2026, 1, 1)
    payer_id = "60054"
    sender_name = "Clearinghouse"
    status = ClaimResponseStatus.ACCEPTED
    total_charge = Decimal("150.00")


class ClaimResponseDetailFactory(factory.django.DjangoModelFactory[ClaimResponseDetail]):
    """Factory for creating a ClaimResponseDetail."""

    class Meta:
        model = ClaimResponseDetail

    claim_response = factory.SubFactory(ClaimResponseFactory)
    response_code = "A1"
    response = "The claim has been received."
    status = ClaimResponseStatus.ACCEPTED
