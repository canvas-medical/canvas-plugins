import factory

from canvas_sdk.v1.data.vaccine import Vaccine, VaccineLot


class VaccineFactory(factory.django.DjangoModelFactory[Vaccine]):
    """Factory for creating a Vaccine."""

    class Meta:
        model = Vaccine

    cvx_code = factory.Faker("numerify", text="###")
    name = factory.Faker("word")
    short_name = factory.Faker("word")
    inventory = ""
    ndc_code = factory.Faker("numerify", text="#####-###-##")
    mvx_code = "ASZ"
    route = ""
    active = True
    units = 1


class VaccineLotFactory(factory.django.DjangoModelFactory[VaccineLot]):
    """Factory for creating a VaccineLot."""

    class Meta:
        model = VaccineLot

    vaccine = factory.SubFactory(VaccineFactory)
    lot_number = factory.Sequence(lambda n: f"LOT-{n:05d}")
    ndc_code = ""
    mvx_code = "ASZ"
    diluent_lot_number = ""
    starting_inventory = 25
    quantity_adjustment = 0
    adjustment_notes = ""
    on_hand_inventory = 25
    used_inventory = 0
