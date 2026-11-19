import datetime

import pytest

from canvas_sdk.test_utils.factories import (
    LabReportFactory,
    LabReportProducerFactory,
    LabTestAOEFactory,
    LabTestFactory,
)
from canvas_sdk.v1.data import LabReportProducer, LabTestAOE
from canvas_sdk.v1.data.lab import LabTestAOEAnswerType


@pytest.mark.django_db
def test_lab_report_producer_is_read_through_its_report() -> None:
    """A report lists its producers with their free-text name and address."""
    report = LabReportFactory.create()
    producer = LabReportProducerFactory.create(
        report=report, unstructured_name="Acme Labs", unstructured_address="1 Main St"
    )
    LabReportProducerFactory.create()

    fetched = LabReportProducer.objects.get(report=report)

    assert fetched.id == producer.id
    assert fetched.unstructured_name == "Acme Labs"
    assert fetched.unstructured_address == "1 Main St"
    assert list(report.producers.all()) == [fetched]


@pytest.mark.django_db
def test_lab_test_aoe_is_read_through_its_test_and_report() -> None:
    """A test lists its AOE answers, and its report finds the test by an AOE code."""
    report = LabReportFactory.create()
    test = LabTestFactory.create(report=report)
    aoe = LabTestAOEFactory.create(
        test=test,
        code="FAST",
        aoe_type=LabTestAOEAnswerType.DATE,
        text_value=None,
        date_value=datetime.date(2026, 11, 1),
    )
    LabTestAOEFactory.create()

    fetched = LabTestAOE.objects.get(test=test)

    assert fetched.id == aoe.id
    assert fetched.aoe_type == LabTestAOEAnswerType.DATE
    assert fetched.date_value == datetime.date(2026, 11, 1)
    assert fetched.boolean_value is None
    assert fetched.text_value is None
    assert list(test.aoes.all()) == [fetched]
    assert list(report.tests.filter(aoes__code="FAST")) == [test]
