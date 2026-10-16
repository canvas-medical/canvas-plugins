import factory

from canvas_sdk.v1.data import DmeOrder, DmeProduct, DmeProductCodeSystem


class DmeProductFactory(factory.django.DjangoModelFactory[DmeProduct]):
    """Factory for creating a DmeProduct."""

    class Meta:
        model = DmeProduct

    name = factory.Faker("text", max_nb_chars=255)
    code = factory.Sequence(lambda n: f"E{n:04d}")
    code_system = DmeProductCodeSystem.HCPCS
    active = True


class DmeOrderFactory(factory.django.DjangoModelFactory[DmeOrder]):
    """Factory for creating a DmeOrder."""

    class Meta:
        model = DmeOrder

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory("canvas_sdk.test_utils.factories.NoteFactory")
    product = factory.SubFactory(DmeProductFactory)
    item_name = factory.SelfAttribute("product.name")
    item_code = factory.SelfAttribute("product.code")
    item_code_system = factory.SelfAttribute("product.code_system")
    indications = factory.LazyFunction(list)
    quantity = 1
    length_of_need = ""
    supplier = None
    ordering_provider = factory.SubFactory("canvas_sdk.test_utils.factories.StaffFactory")
    patient_height = ""
    patient_weight = ""
