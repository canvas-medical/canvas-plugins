import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from canvas_sdk.test_utils.factories import (
    LabOrderFactory,
    LabReportFactory,
    LabTestFactory,
    LabValueFactory,
)
from canvas_sdk.v1.data.lab import LabReport


@pytest.mark.django_db
def test_ordered_tests_returns_only_tests_with_orders() -> None:
    """Test ordered_tests excludes tests where order is null."""
    report = LabReportFactory.create()
    ordered_test = LabTestFactory.create(report=report, order=LabOrderFactory.create())
    LabTestFactory.create(report=report, order=None)

    ordered = list(report.ordered_tests)

    assert [t.id for t in ordered] == [ordered_test.id]


@pytest.mark.django_db
def test_ordered_tests_empty_when_no_orders() -> None:
    """Test ordered_tests returns empty when a report is not linked to ordered tests."""
    report = LabReportFactory.create()
    LabTestFactory.create(report=report, order=None)
    LabTestFactory.create(report=report, order=None)

    assert list(report.ordered_tests) == []


@pytest.mark.django_db
def test_result_tests_returns_only_tests_without_orders() -> None:
    """Test result_tests excludes tests that have an order set."""
    report = LabReportFactory.create()
    result_test = LabTestFactory.create(report=report, order=None)
    LabTestFactory.create(report=report, order=LabOrderFactory.create())

    results = list(report.result_tests)

    assert [t.id for t in results] == [result_test.id]


@pytest.mark.django_db
def test_result_tests_empty_when_only_ordered() -> None:
    """Test result_tests returns empty when a report is not linked to result tests."""
    report = LabReportFactory.create()
    LabTestFactory.create(report=report, order=LabOrderFactory.create())

    assert list(report.result_tests) == []


@pytest.mark.django_db
def test_with_result_tests_and_values_partitions_data_per_report() -> None:
    """Test with_result_tests_and_values() returns each report with its own tests and values, with no cross-contamination."""
    report_a = LabReportFactory.create()
    test_a = LabTestFactory.create(report=report_a, order=None)
    value_a = LabValueFactory.create(report=report_a, test=test_a)

    report_b = LabReportFactory.create()
    test_b = LabTestFactory.create(report=report_b, order=None)
    value_b = LabValueFactory.create(report=report_b, test=test_b)

    fetched = {
        r.id: r
        for r in LabReport.objects.with_result_tests_and_values().filter(
            id__in=[report_a.id, report_b.id]
        )
    }

    a_tests = list(fetched[report_a.id].tests.all())
    b_tests = list(fetched[report_b.id].tests.all())
    assert [t.id for t in a_tests] == [test_a.id]
    assert [t.id for t in b_tests] == [test_b.id]
    assert [v.id for v in a_tests[0].values.all()] == [value_a.id]
    assert [v.id for v in b_tests[0].values.all()] == [value_b.id]


@pytest.mark.django_db
def test_with_result_tests_and_values_prefetches_filtered_tests() -> None:
    """Test with_result_tests_and_values() prefetches the tests relation filtered to result tests."""
    report = LabReportFactory.create()
    result_test = LabTestFactory.create(report=report, order=None)
    LabTestFactory.create(report=report, order=LabOrderFactory.create())

    fetched = LabReport.objects.with_result_tests_and_values().get(id=report.id)

    with CaptureQueriesContext(connection) as ctx:
        prefetched_tests = list(fetched.tests.all())
    assert [t.id for t in prefetched_tests] == [result_test.id]
    assert len(ctx.captured_queries) == 0


@pytest.mark.django_db
def test_with_result_tests_and_values_prefetches_test_values() -> None:
    """Test with_result_tests_and_values() also prefetches each result test's values."""
    report = LabReportFactory.create()
    result_test = LabTestFactory.create(report=report, order=None)
    LabValueFactory.create(report=report, test=result_test)

    fetched = LabReport.objects.with_result_tests_and_values().get(id=report.id)
    test = list(fetched.tests.all())[0]

    with CaptureQueriesContext(connection) as ctx:
        values = list(test.values.all())
    assert len(values) == 1
    assert len(ctx.captured_queries) == 0


@pytest.mark.django_db
def test_with_result_tests_and_values_prefetches_report_values() -> None:
    """Test with_result_tests_and_values() prefetches the report's full values relation."""
    report = LabReportFactory.create()
    LabValueFactory.create(report=report, test=None)

    fetched = LabReport.objects.with_result_tests_and_values().get(id=report.id)

    with CaptureQueriesContext(connection) as ctx:
        values = list(fetched.values.all())
    assert len(values) == 1
    assert len(ctx.captured_queries) == 0
