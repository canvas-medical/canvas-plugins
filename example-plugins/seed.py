from canvas_sdk.test_utils.factories import PatientFactory
from canvas_sdk.v1.data.discount import Discount

PatientFactory.create(first_name="Seeded", last_name="Patient")

Discount.objects.create(
    name="20%",
    adjustment_group="X",
    adjustment_code="Y",
    discount=0.20
)

