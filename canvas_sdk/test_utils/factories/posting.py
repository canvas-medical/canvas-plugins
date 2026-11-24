from decimal import Decimal

import factory

from canvas_sdk.v1.data import (
    BaseRemittanceAdvice,
    BaseRemittanceAdviceClaim,
    BulkPatientPosting,
    CoveragePosting,
    ElectronicRemittanceAdvice,
    ManualRemittanceAdvice,
    NewRemittanceDocument,
    PatientPosting,
)


class BaseRemittanceAdviceFactory(factory.django.DjangoModelFactory[BaseRemittanceAdvice]):
    """Factory for creating a BaseRemittanceAdvice."""

    class Meta:
        model = BaseRemittanceAdvice

    payment_collection = factory.SubFactory(
        "canvas_sdk.test_utils.factories.PaymentCollectionFactory"
    )
    total_paid = Decimal("80.00")


class ManualRemittanceAdviceFactory(BaseRemittanceAdviceFactory):
    """Factory for creating a ManualRemittanceAdvice."""

    class Meta:
        model = ManualRemittanceAdvice


class ElectronicRemittanceAdviceFactory(BaseRemittanceAdviceFactory):
    """Factory for creating an ElectronicRemittanceAdvice."""

    class Meta:
        model = ElectronicRemittanceAdvice

    era_id = factory.Sequence(lambda n: f"ERA{n:06d}")
    check_type = "ACH"
    payer_name = "Acme Health"


class BaseRemittanceAdviceClaimFactory(
    factory.django.DjangoModelFactory[BaseRemittanceAdviceClaim]
):
    """Factory for linking a remit to a Claim."""

    class Meta:
        model = BaseRemittanceAdviceClaim

    remittance = factory.SubFactory(BaseRemittanceAdviceFactory)
    claim = factory.SubFactory("canvas_sdk.test_utils.factories.ClaimFactory")


class NewRemittanceDocumentFactory(factory.django.DjangoModelFactory[NewRemittanceDocument]):
    """Factory for creating a NewRemittanceDocument."""

    class Meta:
        model = NewRemittanceDocument

    originator = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    remittance = factory.SubFactory(ElectronicRemittanceAdviceFactory)
    document = factory.Sequence(lambda n: f"eras/era_{n}.835")


class CoveragePostingFactory(factory.django.DjangoModelFactory[CoveragePosting]):
    """Factory for creating a CoveragePosting."""

    class Meta:
        model = CoveragePosting

    claim = factory.SubFactory("canvas_sdk.test_utils.factories.ClaimFactory")
    claim_coverage = factory.SubFactory(
        "canvas_sdk.test_utils.factories.ClaimCoverageFactory",
        claim=factory.SelfAttribute("..claim"),
    )
    remittance = factory.SubFactory(ElectronicRemittanceAdviceFactory)
    payer_icn = factory.Sequence(lambda n: f"ICN{n:06d}")
    position_in_era = 1


class BulkPatientPostingFactory(factory.django.DjangoModelFactory[BulkPatientPosting]):
    """Factory for creating a BulkPatientPosting."""

    class Meta:
        model = BulkPatientPosting

    payment_collection = factory.SubFactory(
        "canvas_sdk.test_utils.factories.PaymentCollectionFactory"
    )
    payer = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    total_paid = Decimal("20.00")


class PatientPostingFactory(factory.django.DjangoModelFactory[PatientPosting]):
    """Factory for creating a PatientPosting."""

    class Meta:
        model = PatientPosting

    claim = factory.SubFactory("canvas_sdk.test_utils.factories.ClaimFactory")
    claim_patient = factory.SubFactory(
        "canvas_sdk.test_utils.factories.ClaimPatientFactory",
        claim=factory.SelfAttribute("..claim"),
    )
    patient_payment = factory.SubFactory(BulkPatientPostingFactory)
