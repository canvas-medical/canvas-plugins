"""The claims tools: gated on the revenue capability, defaulting to the run's claim."""

import json
from decimal import Decimal
from typing import Any

import pytest

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.agents import Capability, ToolNotAllowed, standard_tools
from canvas_sdk.test_utils.factories import (
    ClaimBannerAlertFactory,
    ClaimCommentFactory,
    ClaimCoverageFactory,
    ClaimDiagnosisCodeFactory,
    ClaimFactory,
    ClaimLabelFactory,
    ClaimLineItemFactory,
    ClaimLineItemModifierFactory,
    ClaimProviderFactory,
    ClaimQueueFactory,
    StaffFactory,
    TaskLabelFactory,
    TeamFactory,
)
from canvas_sdk.v1.data import Claim, ClaimPatient, ClaimQueue
from canvas_sdk.v1.data.claim import ClaimQueues
from canvas_sdk.v1.data.claim_banner_alert import BannerAlertStatus
from canvas_sdk.v1.data.claim_line_item import ClaimLineItemStatus
from canvas_sdk.v1.data.task import TaskLabelModule

SSN = "123456789"


def _claims_tools() -> list[str]:
    return sorted(
        definition["name"]
        for definition in standard_tools.definitions()
        if {"claims_reads", "claims_writes"}
        & set(standard_tools.categories_for(definition["name"]))
    )


def _ctx(claim: Claim | None = None, **overrides: Any) -> dict[str, Any]:
    return {
        "capabilities": frozenset({Capability.REVENUE}),
        "claim_id": str(claim.id) if claim else None,
        "effects": [],
        **overrides,
    }


def _queue(ordering: ClaimQueues, display_name: str | None = None) -> ClaimQueue:
    return ClaimQueueFactory.create(
        queue_sort_ordering=ordering,
        name=ordering.label,
        display_name=display_name or ordering.label,
        description="",
    )


def _claim(queue: ClaimQueue | None = None, **kwargs: Any) -> Claim:
    claim = ClaimFactory.create(
        current_queue=queue or _queue(ClaimQueues.NEEDS_CODING_REVIEW), **kwargs
    )
    ClaimPatient.objects.create(
        claim=claim,
        photo="",
        dob="1970-01-01",
        first_name="Pat",
        last_name="Ient",
        middle_name="",
        phone="5555550100",
        sex="F",
        ssn=SSN,
        addr1="1 Main St",
        addr2="",
        city="Springfield",
        state="IL",
        zip="62701",
        country="US",
    )
    return claim


# Access ------------------------------------------------------------------------


def test_the_claims_categories_hold_every_claims_tool() -> None:
    """The refusal test below covers each tool through its category."""
    assert len(_claims_tools()) == 14


@pytest.mark.django_db
@pytest.mark.parametrize(
    "capabilities",
    [None, frozenset(), frozenset({"claims"}), ["revenue"], "revenue"],
)
@pytest.mark.parametrize("tool", _claims_tools())
def test_each_claims_tool_refuses_without_the_revenue_capability(
    tool: str, capabilities: Any
) -> None:
    """Only the platform's grant opens a claims tool; nothing is read or staged otherwise."""
    claim = _claim()
    ctx = _ctx(claim, capabilities=capabilities)

    with pytest.raises(ToolNotAllowed, match="'revenue' capability"):
        standard_tools.execute(
            tool,
            {"queue": "x", "labels": ["x"], "comment": "x", "key": "x", "narrative": "x"},
            ctx=ctx,
        )

    assert ctx["effects"] == []


def test_the_claims_tools_are_hidden_from_a_run_without_the_revenue_capability() -> None:
    """The model is never offered a tool the run could not use."""
    hidden = standard_tools.usable_by(None, frozenset())
    shown = standard_tools.usable_by(None, frozenset({Capability.REVENUE}))

    names = {definition["name"] for definition in hidden.definitions()}
    assert names.isdisjoint(_claims_tools())
    assert set(_claims_tools()) <= {definition["name"] for definition in shown.definitions()}


# Reads -------------------------------------------------------------------------


@pytest.mark.django_db
def test_find_claims_excludes_the_trash_and_returns_rows_without_identifiers() -> None:
    """A search with no filters lists live claims, never the snapshot's SSN or address."""
    live = _claim()
    _claim(queue=_queue(ClaimQueues.TRASH))

    rows = standard_tools.execute("find_claims", {}, ctx=_ctx())

    assert [row["id"] for row in rows] == [str(live.id)]
    row = rows[0]
    assert row["patient_name"] == "Pat Ient"
    assert live.note is not None and live.note.patient is not None
    assert row["patient_id"] == str(live.note.patient.id)
    assert row["queue"] == "NeedsCodingReview"
    assert SSN not in json.dumps(rows)
    assert "Main St" not in json.dumps(rows)


@pytest.mark.django_db
def test_find_claims_filters_combine() -> None:
    """Queue by display name, assignment, label, payer, and balance narrow the rows."""
    coding = _queue(ClaimQueues.NEEDS_CODING_REVIEW, display_name="Coding review")
    filed = _queue(ClaimQueues.FILED_AWAITING_RESPONSE)
    biller = StaffFactory.create()
    target = _claim(queue=coding, patient_balance=Decimal("40.00"))
    target.aggregate_coverage_balance = Decimal("80.00")
    target.save()
    ClaimLabelFactory.create(claim=target, label=TaskLabelFactory.create(name="Urgent"))
    target.current_coverage = ClaimCoverageFactory.create(claim=target, payer_name="Acme Health")
    target.save()
    _claim(queue=coding, assignee=biller, patient_balance=Decimal("500.00"))
    _claim(queue=filed, patient_balance=Decimal("500.00"))

    def ids(arguments: dict[str, Any]) -> list[str]:
        return [row["id"] for row in standard_tools.execute("find_claims", arguments, ctx=_ctx())]

    assert len(ids({"queue": "coding review"})) == 2
    assert ids({"queue": "coding review", "unassigned": True}) == [str(target.id)]
    assert ids({"label": "urgent"}) == [str(target.id)]
    assert ids({"payer_name_contains": "acme"}) == [str(target.id)]
    assert ids({"queue": "Coding review", "min_balance": 100}) != []
    assert str(target.id) in ids({"min_balance": 120})
    assert str(target.id) not in ids({"min_balance": 121})
    assert len(ids({"assignee_id": biller.id})) == 1


@pytest.mark.django_db
def test_get_claim_defaults_to_the_runs_claim_and_leaves_out_identifiers() -> None:
    """A chat opened from a claim reads that claim; the snapshot's SSN, DOB, phone, and address stay out."""
    claim = _claim()
    ClaimProviderFactory.create(claim=claim, billing_provider_name="Clinic", provider_npi="1")
    ClaimDiagnosisCodeFactory.create(claim=claim, rank=1, code="E11.9", display="T2DM")
    item = ClaimLineItemFactory.create(claim=claim, proc_code="99213", charge=Decimal("120.00"))
    ClaimLineItemModifierFactory.create(line_item=item, modifier="25")
    ClaimLineItemFactory.create(claim=claim, proc_code="99214", status=ClaimLineItemStatus.REMOVED)
    ClaimBannerAlertFactory.create(claim=claim, key="live", narrative="Prior auth pending")
    ClaimBannerAlertFactory.create(claim=claim, key="old", status=BannerAlertStatus.INACTIVE)
    ClaimCommentFactory.create(claim=claim, comment="Called payer")

    result = standard_tools.execute("get_claim", {}, ctx=_ctx(claim))

    assert result["id"] == str(claim.id)
    assert result["patient"] == {"first_name": "Pat", "last_name": "Ient", "sex": "F"}
    assert [line["proc_code"] for line in result["line_items"]] == ["99213"]
    assert result["line_items"][0]["modifiers"] == ["25"]
    assert result["total_charges"] == "120.00"
    assert result["diagnosis_codes"] == [{"rank": 1, "code": "E11.9", "display": "T2DM"}]
    assert [banner["key"] for banner in result["banners"]] == ["live"]
    assert [comment["comment"] for comment in result["recent_comments"]] == ["Called payer"]
    assert result["provider"]["billing_provider_name"] == "Clinic"
    serialized = json.dumps(result)
    for identifier in (SSN, "1970-01-01", "5555550100", "Main St", "62701"):
        assert identifier not in serialized


@pytest.mark.django_db
def test_get_claim_reads_a_named_claim_over_the_runs() -> None:
    """The model can look at another claim from a claim's chat."""
    opened, other = _claim(), _claim()

    result = standard_tools.execute("get_claim", {"claim_id": str(other.id)}, ctx=_ctx(opened))

    assert result["id"] == str(other.id)


@pytest.mark.django_db
def test_a_claim_tool_with_no_claim_asks_for_one() -> None:
    """A run not opened from a claim has nothing to default to."""
    with pytest.raises(ValueError, match="Name a claim"):
        standard_tools.execute("get_claim", {}, ctx=_ctx())


@pytest.mark.django_db
def test_a_missing_claim_is_refused() -> None:
    """An id the model made up, or read from a comment, names no claim."""
    with pytest.raises(ValueError, match="not found"):
        standard_tools.execute("get_claim", {"claim_id": "nope"}, ctx=_ctx())


@pytest.mark.django_db
def test_summarize_claims_counts_and_totals_per_queue() -> None:
    """Counts and balances group by queue in workflow order, leaving out the trash."""
    coding = _queue(ClaimQueues.NEEDS_CODING_REVIEW)
    filed = _queue(ClaimQueues.FILED_AWAITING_RESPONSE)
    _claim(queue=filed, patient_balance=Decimal("10.00"))
    _claim(queue=coding, patient_balance=Decimal("1.50"))
    _claim(queue=coding, patient_balance=Decimal("2.50"))
    _claim(queue=_queue(ClaimQueues.TRASH), patient_balance=Decimal("99.00"))

    rows = standard_tools.execute("summarize_claims", {}, ctx=_ctx())

    assert [(row["queue"], row["count"], row["patient_balance"]) for row in rows] == [
        ("NeedsCodingReview", 2, "4.00"),
        ("FiledAwaitingResponse", 1, "10.00"),
    ]


@pytest.mark.django_db
def test_find_claim_queues_lists_queues_in_workflow_order() -> None:
    """The model learns the queue names move_claim_to_queue takes."""
    _queue(ClaimQueues.FILED_AWAITING_RESPONSE)
    _queue(ClaimQueues.NEEDS_CODING_REVIEW)

    rows = standard_tools.execute("find_claim_queues", {}, ctx=_ctx())

    assert [row["name"] for row in rows] == ["NeedsCodingReview", "FiledAwaitingResponse"]


@pytest.mark.django_db
def test_find_claim_labels_lists_only_active_claim_labels() -> None:
    """Task-only and inactive labels are not offered."""
    TaskLabelFactory.create(name="Urgent", modules=[TaskLabelModule.CLAIMS])
    TaskLabelFactory.create(name="Retired", modules=[TaskLabelModule.CLAIMS], active=False)
    TaskLabelFactory.create(name="Tasks only", modules=[TaskLabelModule.TASKS])

    rows = standard_tools.execute("find_claim_labels", {}, ctx=_ctx())

    assert [row["name"] for row in rows] == ["Urgent"]


@pytest.mark.django_db
def test_find_claim_assignees_finds_active_staff_and_teams() -> None:
    """Inactive staff cannot be assigned, so they are not offered."""
    active = StaffFactory.create(first_name="Robin", last_name="Biller")
    StaffFactory.create(first_name="Robin", last_name="Gone", active=False)
    team = TeamFactory.create(name="Robin's billing team")

    result = standard_tools.execute("find_claim_assignees", {"name_contains": "robin"}, ctx=_ctx())

    assert result["staff"] == [{"id": str(active.id), "name": "Robin Biller"}]
    assert result["teams"] == [{"id": str(team.id), "name": "Robin's billing team"}]


# Writes ------------------------------------------------------------------------


def _write(tool: str, arguments: dict[str, Any], claim: Claim) -> tuple[dict[str, Any], dict]:
    """Run a write on ``claim`` and return its response and its one staged effect's data."""
    ctx = _ctx(claim)
    response = standard_tools.execute(tool, arguments, ctx=ctx)
    (effect,) = ctx["effects"]
    assert EffectType.Name(effect.type) in standard_tools.effect_types_for(tool)
    return response, json.loads(effect.payload)["data"]


@pytest.mark.django_db
def test_move_claim_to_queue_stages_the_move_by_queue_name() -> None:
    """A display name resolves to the queue's name, which the effect takes."""
    claim = _claim()
    _queue(ClaimQueues.QUEUED_FOR_SUBMISSION, display_name="Ready to submit")

    response, data = _write("move_claim_to_queue", {"queue": "ready to submit"}, claim)

    assert response == {"ok": True, "claim_id": str(claim.id), "queue": "QueuedForSubmission"}
    assert data == {"claim_id": str(claim.id), "queue": "QueuedForSubmission"}


@pytest.mark.django_db
def test_move_claim_to_queue_leaves_the_trash_to_a_person() -> None:
    """The agent cannot trash a claim."""
    claim = _claim()
    _queue(ClaimQueues.TRASH)
    ctx = _ctx(claim)

    with pytest.raises(ValueError, match="trash"):
        standard_tools.execute("move_claim_to_queue", {"queue": "Trash"}, ctx=ctx)

    assert ctx["effects"] == []


@pytest.mark.django_db
def test_move_claim_to_queue_refuses_an_unknown_queue() -> None:
    """The model is pointed at find_claim_queues."""
    with pytest.raises(ValueError, match="find_claim_queues"):
        standard_tools.execute("move_claim_to_queue", {"queue": "Nowhere"}, ctx=_ctx(_claim()))


@pytest.mark.django_db
def test_assign_claim_to_a_staff_member_or_a_team() -> None:
    """Either kind of assignee stages the assignment effect."""
    claim = _claim()
    biller = StaffFactory.create(first_name="Robin", last_name="Biller")
    team = TeamFactory.create(name="Billing")

    response, data = _write("assign_claim", {"staff_id": biller.id}, claim)
    assert response["assignee"] == "Robin Biller"
    assert (data["assignee_id"], data["team_id"]) == (str(biller.id), None)

    response, data = _write("assign_claim", {"team_id": str(team.id)}, claim)
    assert response["assignee"] == "Billing"
    assert (data["assignee_id"], data["team_id"]) == (None, str(team.id))


@pytest.mark.django_db
@pytest.mark.parametrize("arguments", [{}, {"staff_id": "s", "team_id": "t"}])
def test_assign_claim_takes_exactly_one_assignee(arguments: dict[str, str]) -> None:
    """Neither or both is refused; unassign_claim clears an assignment."""
    with pytest.raises(ValueError, match="exactly one"):
        standard_tools.execute("assign_claim", arguments, ctx=_ctx(_claim()))


@pytest.mark.django_db
def test_assign_claim_refuses_an_inactive_staff_member() -> None:
    """Work assigned to someone who left would sit unseen."""
    gone = StaffFactory.create(active=False)

    with pytest.raises(ValueError, match="active staff member"):
        standard_tools.execute("assign_claim", {"staff_id": gone.id}, ctx=_ctx(_claim()))


@pytest.mark.django_db
def test_unassign_claim_clears_the_assignment() -> None:
    """The effect carries no assignee and no team."""
    claim = _claim(assignee=StaffFactory.create())

    _, data = _write("unassign_claim", {}, claim)

    assert (data["assignee_id"], data["team_id"]) == (None, None)


@pytest.mark.django_db
def test_add_claim_labels_takes_configured_labels_by_their_own_names() -> None:
    """The model's casing is mapped to the label's name, so no near-duplicate label is created."""
    claim = _claim()
    TaskLabelFactory.create(name="Urgent", modules=[TaskLabelModule.CLAIMS])

    response, data = _write("add_claim_labels", {"labels": ["urgent"]}, claim)

    assert response["labels"] == ["Urgent"]
    assert data["labels"] == [{"name": "Urgent"}]


@pytest.mark.django_db
def test_add_claim_labels_refuses_a_label_that_does_not_exist() -> None:
    """Creating labels is left to a person."""
    ctx = _ctx(_claim())

    with pytest.raises(ValueError, match="find_claim_labels"):
        standard_tools.execute("add_claim_labels", {"labels": ["Brand new"]}, ctx=ctx)

    assert ctx["effects"] == []


@pytest.mark.django_db
def test_remove_claim_labels_removes_only_labels_the_claim_carries() -> None:
    """A label the claim does not carry is refused rather than silently ignored."""
    claim = _claim()
    ClaimLabelFactory.create(claim=claim, label=TaskLabelFactory.create(name="Urgent"))

    _, data = _write("remove_claim_labels", {"labels": ["URGENT"]}, claim)
    assert data["labels"] == ["Urgent"]

    with pytest.raises(ValueError, match="does not carry"):
        standard_tools.execute("remove_claim_labels", {"labels": ["Other"]}, ctx=_ctx(claim))


@pytest.mark.django_db
def test_add_claim_comment_stages_the_comment() -> None:
    """The comment lands on the claim's thread."""
    claim = _claim()

    _, data = _write("add_claim_comment", {"comment": "  Resubmitted with modifier 25 "}, claim)

    assert data == {"claim_id": str(claim.id), "comment": "Resubmitted with modifier 25"}


@pytest.mark.django_db
def test_add_claim_comment_refuses_an_empty_comment() -> None:
    """Whitespace is not a comment."""
    with pytest.raises(ValueError, match="empty"):
        standard_tools.execute("add_claim_comment", {"comment": "  "}, ctx=_ctx(_claim()))


@pytest.mark.django_db
def test_add_and_remove_a_claim_banner() -> None:
    """A banner is added and removed by its key."""
    claim = _claim()

    _, added = _write(
        "add_claim_banner",
        {"key": "auth", "narrative": "Prior auth pending", "intent": "warning"},
        claim,
    )
    _, removed = _write("remove_claim_banner", {"key": "auth"}, claim)

    assert (added["key"], added["narrative"], added["intent"]) == (
        "auth",
        "Prior auth pending",
        "warning",
    )
    assert removed == {"claim_id": str(claim.id), "key": "auth"}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "tool",
    [name for name in _claims_tools() if standard_tools.effect_types_for(name)],
)
def test_each_write_refuses_a_missing_claim_and_stages_nothing(tool: str) -> None:
    """A made-up claim id stages no effect, whatever the write."""
    ctx = _ctx(claim_id="00000000-0000-0000-0000-000000000000")

    with pytest.raises(ValueError, match="not found"):
        standard_tools.execute(
            tool,
            {"queue": "x", "labels": ["x"], "comment": "x", "key": "x", "narrative": "x"},
            ctx=ctx,
        )

    assert ctx["effects"] == []
