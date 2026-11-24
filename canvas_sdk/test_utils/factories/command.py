import factory

from canvas_sdk.v1.data import Command


class CommandFactory(factory.django.DjangoModelFactory[Command]):
    """Factory for creating a Command."""

    class Meta:
        model = Command

    note = factory.SubFactory("canvas_sdk.test_utils.factories.NoteFactory")
    patient = factory.SelfAttribute("note.patient")
    state = "staged"
    schema_key = "plan"
    data = factory.LazyFunction(dict)
    origination_source = "plugin"
    anchor_object_type = ""
    anchor_object_dbid = 0
