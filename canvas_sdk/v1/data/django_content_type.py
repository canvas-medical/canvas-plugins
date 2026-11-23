from collections.abc import Mapping
from typing import TypeVar

from django.db import models

from canvas_sdk.v1.data.base import Model

_T = TypeVar("_T", bound=models.Model)


class ContentType(Model):
    """A Django ContentType, exposing the content type id used for generic relations and permalinks."""

    class Meta:
        db_table = "canvas_sdk_data_django_content_type_001"

    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)


def resolve_content_object(
    models_by_key: Mapping[tuple[str, str], type[_T]],
    content_type: ContentType | None,
    object_id: int | None,
) -> _T | None:
    """The instance a content type + object id points at.

    ``models_by_key`` maps a content type's (app_label, model) to its SDK data model. Returns
    None when either part of the link is missing, the content type has no SDK model, or the
    row is hidden by the model's default manager (a soft-deleted row, for example).
    """
    if content_type is None or object_id is None:
        return None
    model = models_by_key.get((content_type.app_label, content_type.model))
    return model._default_manager.filter(dbid=object_id).first() if model else None


__exports__ = ("ContentType",)
