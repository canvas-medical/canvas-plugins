import pytest

from canvas_sdk.test_utils.factories.django_content_type import DjangoContentTypeFactory
from canvas_sdk.v1.data import DjangoContentType


@pytest.mark.django_db
def test_django_content_type_exposes_integer_id_app_label_and_model() -> None:
    """A DjangoContentType is readable by its integer dbid with app_label and model."""
    content_type = DjangoContentTypeFactory(app_label="api", model="note")

    fetched = DjangoContentType.objects.get(dbid=content_type.dbid)

    assert isinstance(fetched.dbid, int)
    assert fetched.app_label == "api"
    assert fetched.model == "note"
