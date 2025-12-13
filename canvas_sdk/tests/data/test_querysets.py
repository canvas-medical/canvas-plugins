import inspect
from typing import Any
from unittest.mock import Mock

from django.db.models import Q

from canvas_sdk.v1.data.base import (
    BaseQuerySet,
    CommittableQuerySetMixin,
    ForPatientQuerySetMixin,
    QuerySetProtocol,
    TimeframeLookupQuerySetMixin,
    ValueSetLookupByNameQuerySetMixin,
    ValueSetLookupQuerySetMixin,
)


def test_queryset_protocol_does_not_define_methods_at_runtime() -> None:
    """
    Verify that QuerySetProtocol doesn't define any methods at runtime.

    This is critical to ensure that QuerySetProtocol doesn't shadow Django's
    QuerySet methods (like filter, distinct, etc.) when used as a base class
    for mixins. The protocol should only define method signatures during type
    checking (TYPE_CHECKING=True), but remain empty at runtime.
    """
    protocol_methods = {
        name
        for name, _ in inspect.getmembers(QuerySetProtocol, inspect.ismethod)
        if name in QuerySetProtocol.__dict__ and not name.startswith("_")
    }

    protocol_functions = {
        name
        for name, _ in inspect.getmembers(QuerySetProtocol, inspect.isfunction)
        if name in QuerySetProtocol.__dict__ and not name.startswith("_")
    }

    all_defined_methods = protocol_methods | protocol_functions

    assert not all_defined_methods, (
        f"QuerySetProtocol should not define any methods at runtime, "
        f"but found: {all_defined_methods}"
    )


def test_committable_mixin_calls_filter_correctly() -> None:
    """Verify committed() calls filter with correct parameters."""
    mock_qs = Mock(spec=BaseQuerySet)
    mock_qs.filter.return_value = mock_qs

    class TestQuerySet(CommittableQuerySetMixin):
        @staticmethod
        def filter(*args: Any, **kwargs: Any) -> Mock:
            return mock_qs.filter(*args, **kwargs)

        @staticmethod
        def distinct() -> Mock:
            return mock_qs

    qs = TestQuerySet()
    qs.committed()

    mock_qs.filter.assert_called_once_with(
        committer_id__isnull=False, entered_in_error_id__isnull=True
    )


def test_for_patient_mixin_calls_filter_correctly() -> None:
    """Verify for_patient() calls filter with correct parameters."""
    mock_qs = Mock(spec=BaseQuerySet)
    mock_qs.filter.return_value = mock_qs

    class TestQuerySet(ForPatientQuerySetMixin):
        @staticmethod
        def filter(*args: Any, **kwargs: Any) -> Mock:
            return mock_qs.filter(*args, **kwargs)

        @staticmethod
        def distinct() -> Mock:
            return mock_qs

    qs = TestQuerySet()
    patient_id = "test-patient-123"
    qs.for_patient(patient_id)

    mock_qs.filter.assert_called_once_with(patient__id=patient_id)


def test_value_set_lookup_mixin_q_object_creates_correct_query() -> None:
    """Verify q_object creates the correct Q object."""
    codes = {"123456", "789012"}
    q_obj = ValueSetLookupQuerySetMixin.q_object("http://snomed.info/sct", codes)

    assert isinstance(q_obj, Q)
    assert len(q_obj.children) == 2
    assert ("codings__system", "http://snomed.info/sct") in q_obj.children
    assert ("codings__code__in", codes) in q_obj.children


def test_value_set_lookup_by_name_mixin_codings_returns_name_instead_of_url() -> None:
    """Verify codings() returns code system name instead of URL."""
    mock_value_set = Mock()
    mock_value_set.CODE_SYSTEM_MAPPING = {"LOINC": "http://loinc.org"}
    mock_value_set.values = {"LOINC": {"12345-6", "67890-1"}}

    codings = ValueSetLookupByNameQuerySetMixin.codings(mock_value_set)

    assert len(codings) == 1
    assert codings[0][0] == "LOINC"
    assert codings[0][1] == {"12345-6", "67890-1"}


def test_timeframe_lookup_mixin_within_calls_filter_with_range() -> None:
    """Verify within() calls filter with the correct range."""
    mock_qs = Mock(spec=BaseQuerySet)
    mock_qs.filter.return_value = mock_qs

    class TestQuerySet(TimeframeLookupQuerySetMixin):
        @staticmethod
        def filter(*args: Any, **kwargs: Any) -> Mock:
            return mock_qs.filter(*args, **kwargs)

        @staticmethod
        def distinct() -> Mock:
            return mock_qs

    mock_timeframe = Mock()
    mock_timeframe.start.datetime = "2024-01-01"
    mock_timeframe.end.datetime = "2024-12-31"

    qs = TestQuerySet()
    qs.within(mock_timeframe)

    mock_qs.filter.assert_called_once()
    call_kwargs = mock_qs.filter.call_args[1]
    assert "note__datetime_of_service__range" in call_kwargs
    assert call_kwargs["note__datetime_of_service__range"] == ("2024-01-01", "2024-12-31")
