import pytest

from canvas_sdk.test_utils.factories.django_content_type import ContentTypeFactory
from canvas_sdk.v1.data import ContentType


@pytest.mark.django_db
def test_django_content_type_exposes_integer_id_app_label_and_model() -> None:
    """A Django ContentType is readable by its integer dbid with app_label and model."""
    content_type = ContentTypeFactory.create(app_label="api", model="note")

    fetched = ContentType.objects.get(dbid=content_type.dbid)

    assert isinstance(fetched.dbid, int)
    assert fetched.app_label == "api"
    assert fetched.model == "note"
