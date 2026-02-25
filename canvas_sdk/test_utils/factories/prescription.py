import factory

from canvas_sdk.v1.data import Prescription


class PrescriptionFactory(factory.django.DjangoModelFactory):
    """Factory for Prescription."""

    class Meta:
        model = Prescription

    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory",
        patient=factory.SelfAttribute("..patient"),
        originator=factory.SelfAttribute("..originator"),
    )
    originator = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    prescriber = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    supervising_provider = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")

    count_of_refills_allowed = 1
    dispense_quantity = 4
    dose_form = "tablet"
    dose_frequency = 2.2
    dose_frequency_interval = "day"
    dose_quantity = 1.1
    dose_route = "by mouth"
    duration_in_days = 22
    generic_substitutions_allowed = False
    message_id = "2944ae21dbab4cdb9f3a9fee6c184efa"
    pharmacy_address = "1234 Main Street"
    pharmacy_is_read_only = False
    pharmacy_name = "Walgreens"
    pharmacy_ncpdp_id = "1367084"
    pharmacy_phone_number = "4155353439"
    sig_original_input = "1 tab bid po"
