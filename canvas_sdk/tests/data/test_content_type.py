import pytest

from canvas_sdk.test_utils.factories.content_type import ContentTypeFactory
from canvas_sdk.v1.data import ContentType


@pytest.mark.django_db
def test_content_type_exposes_integer_id_app_label_and_model() -> None:
    """A ContentType is readable by its integer dbid with app_label and model."""
    content_type = ContentTypeFactory(app_label="api", model="note")

    fetched = ContentType.objects.get(dbid=content_type.dbid)

    assert isinstance(fetched.dbid, int)
    assert fetched.app_label == "api"
    assert fetched.model == "note"
