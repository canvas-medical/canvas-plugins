"""Tests that `created`/`modified` are exposed on SDK models whose views emit them.

KOALA-7180 declares the two timestamp columns on the data models whose
``canvas_sdk_data_*`` views already emit ``created``/``modified`` by mixing in
``TimestampedModel``. These tests check that the columns are selected and
filterable and that they populate on create, plus a guard for the NoteType MRO
fix and the explicitly-declared fields on ``Application``.
"""

from typing import Any

import pytest
from django.utils import timezone
from factory.django import DjangoModelFactory

from canvas_sdk.test_utils.factories import (
    CalendarFactory,
    EventFactory,
    LabReportTemplateFactory,
    LabReportTemplateFieldFactory,
    LabReportTemplateFieldOptionFactory,
    ReasonForVisitCodingFactory,
)
from canvas_sdk.v1.data.application import Application
from canvas_sdk.v1.data.base import TimestampedModel
from canvas_sdk.v1.data.calendar import Calendar, Event
from canvas_sdk.v1.data.lab import (
    LabReportTemplate,
    LabReportTemplateField,
    LabReportTemplateFieldOption,
)
from canvas_sdk.v1.data.note import NoteType
from canvas_sdk.v1.data.reason_for_visit import ReasonForVisitCoding

# One concrete model per shared abstract base carrying the mixin, plus Calendar and
# Event. Each view exposes columns literally named `created`/`modified`, so the plain
# TimestampedModel mixin (no db_column) is correct.
TIMESTAMP_MODELS = [
    ReasonForVisitCoding,  # Coding base
    LabReportTemplate,  # BaseReportTemplate base
    LabReportTemplateField,  # BaseReportTemplateField base
    LabReportTemplateFieldOption,  # BaseReportTemplateFieldOption base
    Calendar,
    Event,
]

# Ready factories paired with the model each builds, for the DB-backed round trip.
TIMESTAMP_FACTORIES = [
    ReasonForVisitCodingFactory,
    LabReportTemplateFactory,
    LabReportTemplateFieldFactory,
    LabReportTemplateFieldOptionFactory,
    CalendarFactory,
    EventFactory,
]


@pytest.mark.parametrize("model", TIMESTAMP_MODELS)
def test_timestamp_columns_are_selected(model: type[TimestampedModel]) -> None:
    """The default queryset SELECTs both timestamp columns (no DB needed)."""
    sql = str(model._default_manager.all().query)
    assert "created" in sql
    assert "modified" in sql


@pytest.mark.parametrize("model", TIMESTAMP_MODELS)
def test_modified_is_filterable(model: type[TimestampedModel]) -> None:
    """`modified` resolves as a real field, so the lookup compiles without FieldError."""
    # Would raise FieldError if `modified` were not a declared field.
    sql = str(model._default_manager.filter(modified__gte=timezone.now()).query)
    assert "modified" in sql


@pytest.mark.django_db
@pytest.mark.parametrize("factory", TIMESTAMP_FACTORIES)
def test_timestamps_populated_on_create(factory: type[DjangoModelFactory[Any]]) -> None:
    """Creating a row populates both timestamps via auto_now_add / auto_now."""
    obj = factory.create()
    assert obj.created is not None
    assert obj.modified is not None


def test_note_type_survives_coding_gaining_the_mixin() -> None:
    """Guard the NoteType MRO fix.

    Once ``Coding`` inherits ``TimestampedModel``, listing ``TimestampedModel``
    before ``Coding`` on ``NoteType`` is an illegal MRO that fails the whole SDK
    import. Importing the module and touching ``NoteType`` fails fast if that regresses.
    """
    from canvas_sdk.v1.data import note  # noqa: F401

    assert NoteType.__mro__  # a consistent MRO resolved


def test_application_declares_timestamp_fields() -> None:
    """Application cannot use the mixin (its view has no dbid), so it declares the two
    fields directly; both must resolve on the model.
    """
    assert Application._meta.get_field("created") is not None
    assert Application._meta.get_field("modified") is not None
