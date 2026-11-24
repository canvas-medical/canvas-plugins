import datetime

import factory

from canvas_sdk.v1.data import Device, DeviceCoding


class DeviceFactory(factory.django.DjangoModelFactory[Device]):
    """Factory for creating a Device."""

    class Meta:
        model = Device

    note_id = factory.Sequence(lambda n: n)
    labeled_contains_NRL = False
    assigning_authority = ""
    scoping_entity = ""
    udi = ""
    di = ""
    issuing_agency = ""
    lot_number = ""
    brand_name = factory.Faker("company")
    mri_safety_status = ""
    version_model_number = ""
    company_name = ""
    gmdnPTName = ""
    status = "active"
    expiration_date = datetime.date(2030, 1, 1)
    expiration_date_original = ""
    serial_number = ""
    manufacturing_date_original = ""
    manufacturing_date = datetime.date(2024, 1, 1)
    manufacturer = ""
    procedure_id = factory.Sequence(lambda n: n)


class DeviceCodingFactory(factory.django.DjangoModelFactory[DeviceCoding]):
    """Factory for creating a DeviceCoding."""

    class Meta:
        model = DeviceCoding

    device = factory.SubFactory(DeviceFactory)
    system = "http://snomed.info/sct"
    code = factory.Faker("numerify", text="#########")
    display = factory.Faker("text", max_nb_chars=200)
