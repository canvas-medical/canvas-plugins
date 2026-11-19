import datetime

import pytest

from canvas_sdk.test_utils.factories import (
    AuthorizationDiagnosisCodeFactory,
    AuthorizationFactory,
    ChargeDescriptionMasterFactory,
    ClaimFactory,
    CoverageFactory,
    PatientFactory,
)
from canvas_sdk.v1.data import Authorization, Claim


@pytest.mark.django_db
def test_authorization_reads_its_patient_coverage_and_terms() -> None:
    """An authorization is found by patient and reads its coverage, number, dates and visits."""
    patient = PatientFactory.create()
    coverage = CoverageFactory.create(patient=patient)
    authorization = AuthorizationFactory.create(
        patient=patient,
        coverage=coverage,
        authorization_number="PA-12345",
        start_date=datetime.date(2026, 1, 1),
        expiration_date=datetime.date(2026, 12, 31),
        visits_approved=12,
        unlimited_visits=False,
        referring_provider_npi="1234567893",
    )

    fetched = Authorization.objects.get(patient=patient)

    assert fetched.id == authorization.id
    assert fetched.coverage == coverage
    assert fetched.authorization_number == "PA-12345"
    assert fetched.start_date == datetime.date(2026, 1, 1)
    assert fetched.expiration_date == datetime.date(2026, 12, 31)
    assert fetched.visits_approved == 12
    assert fetched.unlimited_visits is False
    assert fetched.referring_provider_npi == "1234567893"
    assert list(patient.authorizations.all()) == [fetched]
    assert list(coverage.authorizations.all()) == [fetched]


@pytest.mark.django_db
def test_authorization_reads_its_charges_and_diagnosis_codes() -> None:
    """An authorization lists the charges it covers and its diagnosis codes, and back."""
    authorization = AuthorizationFactory.create()
    covered = ChargeDescriptionMasterFactory.create(cpt_code="97110")
    ChargeDescriptionMasterFactory.create(cpt_code="97112")
    authorization.charges.add(covered)
    coding = AuthorizationDiagnosisCodeFactory.create(
        authorization=authorization, code="M545", display="Low back pain"
    )
    AuthorizationDiagnosisCodeFactory.create()

    assert [charge.cpt_code for charge in authorization.charges.all()] == ["97110"]
    assert list(covered.authorizations.all()) == [authorization]
    assert list(authorization.codings.values_list("code", "display")) == [("M545", "Low back pain")]
    assert coding.authorization == authorization


@pytest.mark.django_db
def test_claim_reads_its_authorization() -> None:
    """A claim resolves its authorization, and the authorization lists the claim."""
    authorization = AuthorizationFactory.create()
    claim = ClaimFactory.create(authorization=authorization)
    ClaimFactory.create()

    assert Claim.objects.get(id=claim.id).authorization == authorization
    assert list(authorization.claims.all()) == [claim]
