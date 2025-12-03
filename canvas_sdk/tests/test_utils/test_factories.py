"""Tests for test factories."""

import importlib
import inspect
import pkgutil
from decimal import Decimal

import arrow
import factory
import pytest

from canvas_sdk.test_utils import factories
from canvas_sdk.test_utils.factories import (
    BillingLineItemFactory,
    ConditionCodingFactory,
    ConditionFactory,
    ImagingReportCodingFactory,
    ImagingReportFactory,
    PatientFactory,
)
from canvas_sdk.v1.data.billing import BillingLineItem, BillingLineItemStatus
from canvas_sdk.v1.data.condition import ClinicalStatus, Condition, ConditionCoding
from canvas_sdk.v1.data.imaging import ImagingReport, ImagingReportCoding
from canvas_sdk.v1.data.patient import Patient


def get_factory_classes_from_data() -> set[str]:
    """Collect names of all top-level factory classes."""
    factory_class_names = set()

    for _, module_name, _ in pkgutil.iter_modules(factories.__path__):
        if module_name.startswith("_"):
            continue

        full_module_name = f"{factories.__name__}.{module_name}"
        module = importlib.import_module(full_module_name)

        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == full_module_name and issubclass(
                obj, factory.django.DjangoModelFactory
            ):
                factory_class_names.add(name)

    return factory_class_names


def test_all_factories_are_exported() -> None:
    """Ensure all factories are exported in the factories module's __all__."""
    declared_exports = set(getattr(factories, "__all__", []))
    factory_classes = get_factory_classes_from_data()

    missing = factory_classes - declared_exports
    assert not missing, f"Factories missing from __all__: {sorted(missing)}"


@pytest.mark.django_db
def test_factory_is_instantiable() -> None:
    """Ensure each factory can be instantiated without errors."""
    factory_classes: list[type] = [
        getattr(factories, factory_name) for factory_name in get_factory_classes_from_data()
    ]

    for factory_class in factory_classes:
        try:
            factory_class()
        except Exception as ex:
            raise Exception(f"Failed to instantiate factory '{factory_class.__name__}'") from ex


@pytest.mark.django_db
class TestBillingLineItemFactory:
    """Tests for BillingLineItemFactory."""

    def test_create_billing_line_item_default(self) -> None:
        """Test creating a BillingLineItem with default values."""
        billing_item: BillingLineItem = BillingLineItemFactory.create()

        assert isinstance(billing_item, BillingLineItem)
        assert billing_item.patient is not None
        assert billing_item.note is not None
        assert billing_item.cpt == "99213"
        assert billing_item.charge == Decimal("100.00")
        assert billing_item.description == "Office Visit"
        assert billing_item.units == 1
        assert billing_item.command_type == "encounter"
        assert billing_item.status == BillingLineItemStatus.ACTIVE

    def test_create_billing_line_item_custom_cpt(self) -> None:
        """Test creating a BillingLineItem with custom CPT code."""
        billing_item: BillingLineItem = BillingLineItemFactory.create(cpt="99214")

        assert billing_item.cpt == "99214"

    def test_create_billing_line_item_with_patient(self) -> None:
        """Test creating a BillingLineItem for a specific patient."""
        patient: Patient = PatientFactory.create()
        billing_item: BillingLineItem = BillingLineItemFactory.create(patient=patient)

        assert billing_item.patient == patient
        # Note should also be for the same patient
        assert billing_item.note is not None
        assert billing_item.note.patient == patient

    def test_create_billing_line_item_custom_charge(self) -> None:
        """Test creating a BillingLineItem with custom charge."""
        billing_item: BillingLineItem = BillingLineItemFactory.create(
            charge=Decimal("250.50"), description="Complex Visit"
        )

        assert billing_item.charge == Decimal("250.50")
        assert billing_item.description == "Complex Visit"


@pytest.mark.django_db
class TestConditionFactory:
    """Tests for ConditionFactory."""

    def test_create_condition_default(self) -> None:
        """Test creating a Condition with default values."""
        condition: Condition = ConditionFactory.create()

        assert isinstance(condition, Condition)
        assert condition.patient is not None
        assert condition.onset_date is not None
        assert condition.deleted is False
        assert condition.clinical_status == ClinicalStatus.ACTIVE
        assert condition.surgical is True
        # Resolution date should be far in the future
        assert condition.resolution_date == arrow.get("9999-12-31").date()

    def test_create_condition_with_patient(self) -> None:
        """Test creating a Condition for a specific patient."""
        patient: Patient = PatientFactory.create()
        condition: Condition = ConditionFactory.create(patient=patient)

        assert condition.patient == patient

    def test_create_condition_custom_dates(self) -> None:
        """Test creating a Condition with custom dates."""
        onset = arrow.get("2023-01-15").date()
        resolution = arrow.get("2023-06-30").date()

        condition: Condition = ConditionFactory.create(onset_date=onset, resolution_date=resolution)

        assert condition.onset_date == onset
        assert condition.resolution_date == resolution

    def test_create_condition_non_surgical(self) -> None:
        """Test creating a non-surgical condition."""
        condition: Condition = ConditionFactory.create(surgical=False)

        assert condition.surgical is False


@pytest.mark.django_db
class TestConditionCodingFactory:
    """Tests for ConditionCodingFactory."""

    def test_create_condition_coding_default(self) -> None:
        """Test creating a ConditionCoding with default values."""
        coding: ConditionCoding = ConditionCodingFactory.create()

        assert isinstance(coding, ConditionCoding)
        assert coding.condition is not None
        assert coding.system == "http://snomed.info/sct"
        assert coding.code == "12345"

    def test_create_condition_coding_with_condition(self) -> None:
        """Test creating a ConditionCoding for a specific condition."""
        condition: Condition = ConditionFactory.create()
        coding: ConditionCoding = ConditionCodingFactory.create(condition=condition)

        assert coding.condition == condition

    def test_create_condition_coding_custom_code(self) -> None:
        """Test creating a ConditionCoding with custom code."""
        coding: ConditionCoding = ConditionCodingFactory.create(system="ICD-10", code="E11.9")

        assert coding.system == "ICD-10"
        assert coding.code == "E11.9"

    def test_create_multiple_codings_for_condition(self) -> None:
        """Test creating multiple codings for one condition."""
        condition: Condition = ConditionFactory.create()

        coding1: ConditionCoding = ConditionCodingFactory.create(
            condition=condition, system="http://snomed.info/sct", code="73211009"
        )

        coding2: ConditionCoding = ConditionCodingFactory.create(
            condition=condition, system="ICD-10", code="E11.9"
        )

        assert coding1.condition == condition
        assert coding2.condition == condition
        assert condition.codings.count() == 2


@pytest.mark.django_db
class TestImagingReportFactory:
    """Tests for ImagingReportFactory."""

    def test_create_imaging_report_default(self) -> None:
        """Test creating an ImagingReport with default values."""
        report: ImagingReport = ImagingReportFactory.create()

        assert isinstance(report, ImagingReport)
        assert report.patient is not None
        assert report.original_date is not None
        assert report.result_date is not None
        assert report.assigned_date is not None
        assert report.junked is False
        assert report.requires_signature is False

    def test_create_imaging_report_with_patient(self) -> None:
        """Test creating an ImagingReport for a specific patient."""
        patient: Patient = PatientFactory.create()
        report: ImagingReport = ImagingReportFactory.create(patient=patient)

        assert report.patient == patient

    def test_create_imaging_report_custom_dates(self) -> None:
        """Test creating an ImagingReport with custom dates."""
        original = arrow.get("2023-05-15").date()
        result = arrow.get("2023-05-20").date()

        report: ImagingReport = ImagingReportFactory.create(
            original_date=original, result_date=result
        )

        assert report.original_date == original
        assert report.result_date == result

    def test_create_imaging_report_requires_signature(self) -> None:
        """Test creating an ImagingReport that requires signature."""
        report: ImagingReport = ImagingReportFactory.create(requires_signature=True)

        assert report.requires_signature is True


@pytest.mark.django_db
class TestImagingReportCodingFactory:
    """Tests for ImagingReportCodingFactory."""

    def test_create_imaging_report_coding_default(self) -> None:
        """Test creating an ImagingReportCoding with default values."""
        coding: ImagingReportCoding = ImagingReportCodingFactory.create()

        assert isinstance(coding, ImagingReportCoding)
        assert coding.report is not None
        assert coding.system == "http://loinc.org"
        # Code is generated by Faker with pattern "#####-#"
        assert coding.code is not None
        assert coding.display is not None

    def test_create_imaging_report_coding_with_report(self) -> None:
        """Test creating an ImagingReportCoding for a specific report."""
        report: ImagingReport = ImagingReportFactory.create()
        coding: ImagingReportCoding = ImagingReportCodingFactory.create(report=report)

        assert coding.report == report

    def test_create_imaging_report_coding_custom_code(self) -> None:
        """Test creating an ImagingReportCoding with custom code."""
        coding: ImagingReportCoding = ImagingReportCodingFactory.create(
            system="http://snomed.info/sct", code="71651007", display="Mammography"
        )

        assert coding.system == "http://snomed.info/sct"
        assert coding.code == "71651007"
        assert coding.display == "Mammography"

    def test_create_multiple_codings_for_report(self) -> None:
        """Test creating multiple codings for one imaging report."""
        report: ImagingReport = ImagingReportFactory.create()

        coding1: ImagingReportCoding = ImagingReportCodingFactory.create(
            report=report, system="http://loinc.org", code="24606-6"
        )

        coding2: ImagingReportCoding = ImagingReportCodingFactory.create(
            report=report, system="http://snomed.info/sct", code="71651007"
        )

        assert coding1.report == report
        assert coding2.report == report
        assert report.codings.count() == 2
