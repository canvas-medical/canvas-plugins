from django.db import models

from canvas_sdk.v1.data.condition import Condition


def test_condition_exposes_notes_field() -> None:
    """The notes field is exposed on the Condition model with the expected max_length."""
    field = Condition._meta.get_field("notes")
    assert isinstance(field, models.CharField)
    assert field.max_length == 1000
