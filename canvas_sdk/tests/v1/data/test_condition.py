from django.db import models

from canvas_sdk.v1.data.condition import Condition


def test_condition_exposes_notes_field() -> None:
    field = Condition._meta.get_field("notes")
    assert isinstance(field, models.CharField)
    assert field.max_length == 1000
