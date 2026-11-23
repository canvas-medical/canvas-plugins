import datetime

import factory

from canvas_sdk.v1.data import ChargeDescriptionMaster
from canvas_sdk.v1.data.charge_description_master import CDMCodeSystem


class ChargeDescriptionMasterFactory(factory.django.DjangoModelFactory[ChargeDescriptionMaster]):
    """Factory for creating a ChargeDescriptionMaster."""

    class Meta:
        model = ChargeDescriptionMaster

    cpt_code = factory.Sequence(lambda n: f"{99200 + n}")
    name = factory.Faker("sentence", nb_words=4)
    short_name = factory.Faker("word")
    charge_amount = 100
    effective_date = datetime.date(2026, 1, 1)
    end_date = None
    code_system = CDMCodeSystem.CPT
    ndc_code = ""
