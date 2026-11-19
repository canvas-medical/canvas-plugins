from decimal import Decimal
from unittest.mock import patch

import pytest

from canvas_sdk.test_utils.factories import (
    BaseRemittanceAdviceClaimFactory,
    CanvasUserFactory,
    ClaimAssigneeEventFactory,
    ClaimCoverageEventFactory,
    ClaimFactory,
    ClaimQueueFactory,
    ClaimResponseFactory,
    ClaimSnoozeEventFactory,
    ClaimStateChangeEventFactory,
    CollectionStatusHistoryFactory,
    CoveragePostingFactory,
    ElectronicRemittanceAdviceFactory,
    InvoiceClaimFactory,
    LineItemAllowedFactory,
    ManualRemittanceAdviceFactory,
    NewRemittanceDocumentFactory,
    RemarkCodeFactory,
    ResponseFactory,
)
from canvas_sdk.v1.data import (
    BaseRemittanceAdvice,
    Claim,
    ClaimCoverageEventType,
    ClaimResponse,
    ClaimResponseStatus,
    ClaimSnoozeState,
    CollectionStatus,
    ElectronicRemittanceAdvice,
    LineItemAllowed,
    ManualRemittanceAdvice,
    NewRemittanceDocument,
    Patient,
)


@pytest.mark.django_db
def test_claim_queue_history_reads_from_the_claim_and_both_queues() -> None:
    """A queue move is listed on the claim and on the queues it left and entered."""
    filed = ClaimQueueFactory.create(queue_sort_ordering=5)
    rejected = ClaimQueueFactory.create(queue_sort_ordering=7, name="Claim: Rejected")
    event = ClaimStateChangeEventFactory.create(queue_exited=filed, queue_entered=rejected)

    claim = Claim.objects.get(dbid=event.claim.dbid)

    assert list(claim.claim_state_change_events.all()) == [event]
    assert list(rejected.enter_events.all()) == [event]
    assert list(filed.exit_events.all()) == [event]
    assert list(rejected.exit_events.all()) == []


@pytest.mark.django_db
def test_claim_coverage_history_reads_from_the_claim_and_the_coverage() -> None:
    """A coverage change is listed on the claim and on the claim coverage it changed."""
    event = ClaimCoverageEventFactory.create(event_type=ClaimCoverageEventType.DEACTIVATED)

    claim = Claim.objects.get(dbid=event.claim.dbid)

    assert [e.event_type for e in claim.claim_coverage_events.all()] == ["deactivated"]
    assert list(event.claim_coverage.events.all()) == [event]


@pytest.mark.django_db
def test_claim_assignee_history_keeps_the_owner_names() -> None:
    """An assignment is listed on the claim with the owner and the names recorded at the time."""
    event = ClaimAssigneeEventFactory.create(team_name="Billing")

    fetched = Claim.objects.get(dbid=event.claim.dbid).assignee_events.get()

    assert event.assignee is not None
    assert fetched.assignee == event.assignee
    assert fetched.team == event.team
    assert fetched.assignee_name == event.assignee.credentialed_name
    assert fetched.team_name == "Billing"


@pytest.mark.django_db
def test_claim_assignee_history_allows_unassignment_by_a_plugin() -> None:
    """Unassigning leaves both owners empty, and a plugin change has no originator."""
    event = ClaimAssigneeEventFactory.create(
        assignee=None, team=None, assignee_name="", team_name="", originator=None
    )

    fetched = event.claim.assignee_events.get()

    assert (fetched.assignee, fetched.team, fetched.originator) == (None, None, None)


@pytest.mark.django_db
def test_claim_snooze_history_reads_from_the_claim() -> None:
    """Snooze set and clear events are listed on the claim; a clear has no date."""
    claim = ClaimFactory.create()
    snoozed = ClaimSnoozeEventFactory.create(claim=claim)
    ClaimSnoozeEventFactory.create(claim=claim, state=ClaimSnoozeState.CLEAR, date=None)

    events = Claim.objects.get(dbid=claim.dbid).snooze_events.order_by("dbid")

    assert [(e.state, e.date) for e in events] == [("set", snoozed.date), ("clear", None)]


@pytest.mark.django_db
def test_claim_responses_and_their_messages_read_from_the_claim() -> None:
    """A claim's responses and each response's messages are reachable from the claim."""
    claim_response = ClaimResponseFactory.create(status=ClaimResponseStatus.REJECTED)
    message = ResponseFactory.create(claim_response=claim_response, response_code="A7")

    claim = Claim.objects.get(claim_responses=claim_response)
    fetched = claim.claim_responses.get()

    assert fetched.status == "R"
    assert fetched.total_charge == Decimal("150.00")
    assert list(fetched.responses.all()) == [message]
    assert fetched.responses.get().response_code == "A7"


@pytest.mark.django_db
def test_remits_link_to_claims_both_ways() -> None:
    """The remit-to-claim link reads as claim.remits and remittance.claims."""
    link = BaseRemittanceAdviceClaimFactory.create()
    BaseRemittanceAdviceClaimFactory.create()

    claim = Claim.objects.get(dbid=link.claim.dbid)

    assert list(claim.remits.all()) == [link.remittance]
    assert list(link.remittance.claims.all()) == [claim]


@pytest.mark.django_db
def test_remittance_children_share_the_base_remit() -> None:
    """Electronic and manual remits are BaseRemittanceAdvice rows with their own columns."""
    era = ElectronicRemittanceAdviceFactory.create(payer_name="Acme Health", check_type="ACH")
    manual = ManualRemittanceAdviceFactory.create()

    base = BaseRemittanceAdvice.objects.get(dbid=era.dbid)

    assert base.electronicremittanceadvice.payer_name == "Acme Health"
    assert ElectronicRemittanceAdvice.objects.get(id=era.id).check_type == "ACH"
    assert list(ManualRemittanceAdvice.objects.all()) == [manual]
    assert BaseRemittanceAdvice.objects.count() == 2


@pytest.mark.django_db
def test_remittance_document_reads_from_the_remit() -> None:
    """A remit's file is reachable as remittance.document."""
    document = NewRemittanceDocumentFactory.create(document="eras/era_1.835")

    remit = BaseRemittanceAdvice.objects.get(dbid=document.remittance.dbid)

    assert remit.document == document
    assert remit.document.document.name == "eras/era_1.835"


def test_remittance_document_url_presigns_the_file() -> None:
    """document_url presigns the remit file."""
    document = NewRemittanceDocument(document="eras/era_1.835")

    with patch(
        "canvas_sdk.v1.data.posting.presigned_url", return_value="https://s3.example.com/era"
    ) as mock:
        assert document.document_url == "https://s3.example.com/era"
        mock.assert_called_once_with("eras/era_1.835")


def test_remittance_document_url_is_none_without_a_file() -> None:
    """document_url is None when no file is set."""
    assert NewRemittanceDocument(document="").document_url is None


@pytest.mark.django_db
def test_remark_codes_read_per_posting_and_per_claim_line() -> None:
    """A remark code is listed on its coverage posting and on its claim line."""
    posting = CoveragePostingFactory.create()
    remark = RemarkCodeFactory.create(posting=posting, remark_code="N130")
    RemarkCodeFactory.create()

    claim = Claim.objects.get(dbid=posting.claim.dbid)
    claim_posting = claim.postings.get().coverageposting

    assert [r.remark_code for r in claim_posting.remark_codes.all()] == ["N130"]
    assert list(remark.claim_line_item.remark_codes.all()) == [remark]


@pytest.mark.django_db
def test_line_item_allowed_reads_per_posting_and_claim_line() -> None:
    """An allowed amount is listed on its posting and claim line, and active() skips errors."""
    allowed = LineItemAllowedFactory.create(amount=Decimal("80.00"))
    LineItemAllowedFactory.create(
        posting=allowed.posting,
        claim_line_item=allowed.claim_line_item,
        entered_in_error=CanvasUserFactory.create(),
    )

    claim = Claim.objects.get(dbid=allowed.posting.claim.dbid)

    assert list(LineItemAllowed.objects.active()) == [allowed]
    assert claim.postings.get().lineitemalloweds.count() == 2
    assert allowed.claim_line_item.lineitemalloweds.active().get().amount == Decimal("80.00")
    assert list(allowed.billing_line_item.lineitemalloweds.all()) == [allowed]


@pytest.mark.django_db
def test_invoices_link_to_claims_both_ways() -> None:
    """The invoice-to-claim link reads as claim.full_invoices and invoice.claims."""
    link = InvoiceClaimFactory.create()
    InvoiceClaimFactory.create()

    claim = Claim.objects.get(dbid=link.claim.dbid)

    assert list(claim.full_invoices.all()) == [link.invoice]
    assert list(link.invoice.claims.all()) == [claim]


@pytest.mark.django_db
def test_collection_status_history_reads_from_the_patient() -> None:
    """A patient's collection status history is listed on the patient."""
    history = CollectionStatusHistoryFactory.create(status=CollectionStatus.EXTERNAL)
    CollectionStatusHistoryFactory.create()

    patient = Patient.objects.get(id=history.patient.id)

    assert [h.status for h in patient.collection_status_histories.all()] == ["external"]


@pytest.mark.django_db
def test_deleted_claim_responses_are_hidden() -> None:
    """A soft-deleted claim response is left out of queries and of claim.claim_responses."""
    kept = ClaimResponseFactory.create()
    ClaimResponseFactory.create(claim=kept.claim, deleted=True)

    claim = Claim.objects.get(claim_responses=kept)

    assert list(ClaimResponse.objects.all()) == [kept]
    assert list(claim.claim_responses.all()) == [kept]


@pytest.mark.django_db
def test_committed_claim_responses_exclude_uncommitted_and_entered_in_error() -> None:
    """committed() returns only committed responses that were not entered in error."""
    user = CanvasUserFactory.create()
    committed = ClaimResponseFactory.create(committer=user)
    ClaimResponseFactory.create()
    ClaimResponseFactory.create(committer=user, entered_in_error=user)

    assert list(ClaimResponse.objects.committed()) == [committed]


@pytest.mark.django_db
def test_deleted_remittance_documents_are_hidden() -> None:
    """A soft-deleted remit document is left out of queries."""
    kept = NewRemittanceDocumentFactory.create()
    NewRemittanceDocumentFactory.create(deleted=True)

    assert list(NewRemittanceDocument.objects.all()) == [kept]


@pytest.mark.django_db
def test_deleted_allowed_amounts_are_hidden() -> None:
    """A soft-deleted allowed amount is left out of queries, active() and the posting's list."""
    kept = LineItemAllowedFactory.create()
    LineItemAllowedFactory.create(
        posting=kept.posting, claim_line_item=kept.claim_line_item, deleted=True
    )

    assert list(LineItemAllowed.objects.all()) == [kept]
    assert list(LineItemAllowed.objects.active()) == [kept]
    assert list(kept.posting.lineitemalloweds.all()) == [kept]
