"""SDK-provided claims tools, registered on :data:`standard_tools`.

A claims run is not about one patient, so these tools are not patient-scoped.
They require instead that the platform granted the run
:attr:`Capability.REVENUE`, which it grants only to a staff member holding the
revenue permission with access to every patient. Each declares it, so the
platform hides them from a run without it and the registry refuses them, and an
agent cannot grant it: ``capabilities`` is a reserved
:meth:`AgentPlugin.tool_context` key.

A tool that takes a ``claim_id`` defaults to the run's claim, ``ctx["claim_id"]``,
so a chat opened from a claim acts on that claim unless the model names another.

The claim's patient snapshot carries the SSN, date of birth, phone, and address;
no tool returns them.
"""

from decimal import Decimal
from typing import Any
from uuid import UUID

from django.db.models import Count, DecimalField, F, Q, Sum, Value
from django.db.models.functions import Coalesce

from canvas_sdk.agents.capabilities import Capability
from canvas_sdk.agents.standard_tools import standard_tools
from canvas_sdk.effects.claim import BannerAlertIntent, ClaimEffect, Label
from canvas_sdk.v1.data import Claim, ClaimQueue, Staff, TaskLabel, Team
from canvas_sdk.v1.data.claim import ClaimQueues
from canvas_sdk.v1.data.claim_banner_alert import BannerAlertStatus
from canvas_sdk.v1.data.claim_line_item import ClaimLineItemStatus
from canvas_sdk.v1.data.task import TaskLabelModule

FIND_CLAIMS_LIMIT_DEFAULT = 25
FIND_CLAIMS_LIMIT_MAX = 100
RECENT_COMMENTS = 10

# Every claims tool needs the revenue capability; the platform hides them without it.
REVENUE = (Capability.REVENUE,)

CLAIM_ID_PROPERTY = {
    "type": "string",
    "description": (
        "The claim's `id`, from find_claims. Omit to act on the claim the agent was opened from."
    ),
}


def _requesters_claim(claim_id: str | None, ctx: dict[str, Any]) -> Claim:
    """The claim a tool acts on: the one named, else the run's claim."""
    claim_id = claim_id or ctx.get("claim_id")
    if not claim_id:
        raise ValueError("Name a claim by its id, or open the agent from a claim.")
    claim = (
        Claim.objects.filter(id=_parse_id(claim_id, "claim"))
        .select_related("current_queue", "current_coverage", "assignee", "team")
        .first()
    )
    if claim is None:
        raise ValueError(f"claim {claim_id!r} not found")
    return claim


def _parse_id(value: Any, label: str) -> UUID:
    """``value`` as a UUID; a malformed id names no record, so it is reported as not found."""
    try:
        return UUID(str(value))
    except ValueError:
        raise ValueError(f"{label} {value!r} not found") from None


def _money(value: Decimal | None) -> str:
    return str(Decimal(value or 0).quantize(Decimal("0.01")))


def _staff_name(staff: Staff | None) -> str | None:
    return f"{staff.first_name} {staff.last_name}".strip() if staff else None


def _patient_name(claim: Claim) -> str | None:
    snapshot = getattr(claim, "patient", None)
    if snapshot is None:
        return None
    return f"{snapshot.first_name} {snapshot.last_name}".strip() or None


def _serialize_claim_row(claim: Claim) -> dict[str, Any]:
    """One claim as find_claims returns it."""
    coverage = claim.current_coverage
    note = claim.note
    return {
        "id": str(claim.id),
        "queue": claim.current_queue.name,
        "queue_display": claim.current_queue.display_name,
        "patient_id": str(note.patient.id) if note and note.patient else None,
        "patient_name": _patient_name(claim),
        "date_of_service": (
            note.datetime_of_service.date().isoformat()
            if note and note.datetime_of_service
            else None
        ),
        "payer_name": coverage.payer_name or None if coverage else None,
        "assignee": _staff_name(claim.assignee),
        "team": claim.team.name if claim.team else None,
        "patient_balance": _money(claim.patient_balance),
        "coverage_balance": _money(claim.aggregate_coverage_balance),
        "labels": [label.name for label in claim.labels.all()],
        "snoozed_until": claim.snoozed_until.isoformat() if claim.snoozed_until else None,
    }


@standard_tools.tool(
    name="find_claims",
    description=(
        "Search claims with optional filters, most recently created first. Excludes "
        "trashed claims unless `queue` names the trash queue. Each row has the claim's "
        "`id`, its queue, patient, date of service, current payer, assignee or team, "
        "balances, and labels. Use get_claim for one claim's full detail. Requires the "
        "run's revenue capability."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "queue": {
                "type": "string",
                "description": (
                    "Queue `name` or `display_name` from find_claim_queues, matched "
                    "case-insensitively."
                ),
            },
            "patient_id": {
                "type": "string",
                "description": "Only claims for this patient's `id`.",
            },
            "assignee_id": {
                "type": "string",
                "description": "Only claims assigned to this staff `id`, from find_claim_assignees.",
            },
            "team_id": {
                "type": "string",
                "description": "Only claims assigned to this team `id`, from find_claim_assignees.",
            },
            "unassigned": {
                "type": "boolean",
                "description": "When true, only claims with no assignee and no team.",
            },
            "label": {
                "type": "string",
                "description": "Only claims carrying this label name, matched case-insensitively.",
            },
            "payer_name_contains": {
                "type": "string",
                "description": "Case-insensitive substring of the current payer's name.",
            },
            "min_balance": {
                "type": "number",
                "description": "Only claims whose patient plus coverage balance is at least this.",
            },
            "service_on_or_after": {
                "type": "string",
                "format": "date",
                "description": "ISO 8601 date; only claims whose note's date of service is on or after it.",
            },
            "service_on_or_before": {
                "type": "string",
                "format": "date",
                "description": "ISO 8601 date; only claims whose note's date of service is on or before it.",
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": FIND_CLAIMS_LIMIT_MAX,
                "description": f"Maximum results. Defaults to {FIND_CLAIMS_LIMIT_DEFAULT}.",
            },
        },
    },
    categories=("claims_reads",),
    required_capabilities=REVENUE,
    returns_description=(
        "Array of objects with `id`, `queue`, `queue_display`, `patient_id`, "
        "`patient_name`, `date_of_service`, `payer_name`, `assignee`, `team`, "
        "`patient_balance`, `coverage_balance` (decimal strings), `labels`, "
        "`snoozed_until`."
    ),
)
def _find_claims(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """Filter claims for a run with the revenue capability."""
    claims = Claim.objects.all()
    if queue := arguments.get("queue"):
        claims = claims.filter(
            Q(current_queue__name__iexact=queue) | Q(current_queue__display_name__iexact=queue)
        )
    else:
        claims = claims.active()
    if patient_id := arguments.get("patient_id"):
        claims = claims.filter(note__patient__id=patient_id)
    if assignee_id := arguments.get("assignee_id"):
        claims = claims.filter(assignee__id=assignee_id)
    if team_id := arguments.get("team_id"):
        claims = claims.filter(team__id=team_id)
    if arguments.get("unassigned"):
        claims = claims.filter(assignee__isnull=True, team__isnull=True)
    if label := arguments.get("label"):
        claims = claims.filter(labels__name__iexact=label)
    if payer := arguments.get("payer_name_contains"):
        claims = claims.filter(current_coverage__payer_name__icontains=payer)
    if (min_balance := arguments.get("min_balance")) is not None:
        claims = claims.annotate(
            total_balance=F("patient_balance") + F("aggregate_coverage_balance")
        ).filter(total_balance__gte=Decimal(str(min_balance)))
    if on_or_after := arguments.get("service_on_or_after"):
        claims = claims.filter(note__datetime_of_service__date__gte=on_or_after)
    if on_or_before := arguments.get("service_on_or_before"):
        claims = claims.filter(note__datetime_of_service__date__lte=on_or_before)

    limit = min(int(arguments.get("limit") or FIND_CLAIMS_LIMIT_DEFAULT), FIND_CLAIMS_LIMIT_MAX)
    rows = (
        claims.distinct()
        .select_related(
            "current_queue", "current_coverage", "assignee", "team", "note__patient", "patient"
        )
        .prefetch_related("labels")
        .order_by("-created")[:limit]
    )
    return [_serialize_claim_row(claim) for claim in rows]


@standard_tools.tool(
    name="get_claim",
    description=(
        "Return one claim's full detail: queue, assignee, balances, narrative, "
        "coverages, providers, diagnosis codes, active line items with modifiers and "
        "diagnosis pointers, labels, active banners, and recent comments. Omit "
        "`claim_id` for the claim the agent was opened from. The patient section "
        "carries the name and sex only. Requires the run's revenue capability."
    ),
    input_schema={"type": "object", "properties": {"claim_id": CLAIM_ID_PROPERTY}},
    categories=("claims_reads",),
    required_capabilities=REVENUE,
    returns_description=(
        "Object with the find_claims row fields plus `narrative`, `account_number`, "
        "`prior_auth`, `total_charges`, `patient` (`first_name`, `last_name`, `sex`), "
        "`coverages`, `provider`, `diagnosis_codes`, `line_items`, `banners`, and "
        "`recent_comments`."
    ),
)
def _get_claim(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Read one claim, leaving out the patient snapshot's identifiers."""
    claim = _requesters_claim(arguments.get("claim_id"), ctx)
    snapshot = getattr(claim, "patient", None)
    provider = getattr(claim, "provider", None)
    line_items = (
        claim.line_items.filter(status=ClaimLineItemStatus.ACTIVE)
        .exclude_copay_and_unlinked()
        .prefetch_related("modifiers", "diagnosis_codes")
    )
    return {
        **_serialize_claim_row(claim),
        "narrative": claim.narrative or None,
        "account_number": claim.account_number or None,
        "prior_auth": claim.prior_auth or None,
        "total_charges": _money(sum((item.charge for item in line_items), Decimal("0.00"))),
        "patient": (
            {
                "first_name": snapshot.first_name,
                "last_name": snapshot.last_name,
                "sex": snapshot.sex or None,
            }
            if snapshot
            else None
        ),
        "coverages": [
            {
                "id": str(coverage.id),
                "payer_name": coverage.payer_name,
                "payer_id": coverage.payer_id,
                "payer_order": coverage.payer_order,
                "subscriber_number": coverage.subscriber_number,
            }
            for coverage in claim.coverages.active().order_by("payer_order")
        ],
        "provider": (
            {
                "billing_provider_name": provider.billing_provider_name,
                "billing_provider_npi": provider.billing_provider_npi,
                "rendering_provider_name": (
                    f"{provider.provider_first_name} {provider.provider_last_name}".strip()
                ),
                "rendering_provider_npi": provider.provider_npi,
                "facility_name": provider.facility_name,
            }
            if provider
            else None
        ),
        "diagnosis_codes": [
            {"rank": code.rank, "code": code.code, "display": code.display}
            for code in claim.diagnosis_codes.order_by("rank")
        ],
        "line_items": [
            {
                "id": str(item.id),
                "proc_code": item.proc_code,
                "display": item.display,
                "charge": _money(item.charge),
                "units": item.units,
                "from_date": item.from_date,
                "thru_date": item.thru_date,
                "place_of_service": item.place_of_service,
                "modifiers": [modifier.modifier for modifier in item.modifiers.all()],
                "diagnosis_codes": [
                    pointer.code for pointer in item.diagnosis_codes.all() if pointer.linked
                ],
            }
            for item in line_items
        ],
        "banners": [
            {"key": banner.key, "narrative": banner.narrative, "intent": banner.intent}
            for banner in claim.banner_alerts.filter(status=BannerAlertStatus.ACTIVE)
        ],
        "recent_comments": [
            {"comment": comment.comment, "created": comment.created.isoformat()}
            for comment in claim.comments.filter(deleted=False).order_by("-created")[
                :RECENT_COMMENTS
            ]
        ],
    }


@standard_tools.tool(
    name="summarize_claims",
    description=(
        "Count claims and total their balances per queue, excluding trashed claims. "
        "Optionally limited to one assignee or team. Use this for questions like "
        "'how many claims are waiting on coding review' or 'what is my open balance'. "
        "Requires the run's revenue capability."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "assignee_id": {
                "type": "string",
                "description": "Only claims assigned to this staff `id`.",
            },
            "team_id": {
                "type": "string",
                "description": "Only claims assigned to this team `id`.",
            },
        },
    },
    categories=("claims_reads",),
    required_capabilities=REVENUE,
    returns_description=(
        "Array, in queue order, of objects with `queue`, `queue_display`, `count`, "
        "`patient_balance`, and `coverage_balance` (decimal strings)."
    ),
)
def _summarize_claims(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """Per-queue counts and balance totals."""
    claims = Claim.objects.active()
    if assignee_id := arguments.get("assignee_id"):
        claims = claims.filter(assignee__id=assignee_id)
    if team_id := arguments.get("team_id"):
        claims = claims.filter(team__id=team_id)
    zero = Value(Decimal("0.00"), output_field=DecimalField(max_digits=12, decimal_places=2))
    rows = (
        claims.values(
            "current_queue__name",
            "current_queue__display_name",
            "current_queue__queue_sort_ordering",
        )
        .annotate(
            count=Count("id"),
            patient_balance_total=Coalesce(Sum("patient_balance"), zero),
            coverage_balance_total=Coalesce(Sum("aggregate_coverage_balance"), zero),
        )
        .order_by("current_queue__queue_sort_ordering")
    )
    return [
        {
            "queue": row["current_queue__name"],
            "queue_display": row["current_queue__display_name"],
            "count": row["count"],
            "patient_balance": _money(row["patient_balance_total"]),
            "coverage_balance": _money(row["coverage_balance_total"]),
        }
        for row in rows
    ]


@standard_tools.tool(
    name="find_claim_queues",
    description=(
        "List the instance's claim queues in workflow order. move_claim_to_queue and "
        "find_claims take a queue's `name`. Requires the run's revenue capability."
    ),
    input_schema={"type": "object", "properties": {}},
    categories=("claims_reads",),
    required_capabilities=REVENUE,
    returns_description="Array of objects with `name`, `display_name`, and `description`.",
)
def _find_claim_queues(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """The claim queues, in their sort order."""
    return [
        {"name": queue.name, "display_name": queue.display_name, "description": queue.description}
        for queue in ClaimQueue.objects.order_by("queue_sort_ordering")
    ]


@standard_tools.tool(
    name="find_claim_labels",
    description=(
        "List the active labels configured for claims. add_claim_labels accepts only "
        "these names. Requires the run's revenue capability."
    ),
    input_schema={"type": "object", "properties": {}},
    categories=("claims_reads",),
    required_capabilities=REVENUE,
    returns_description="Array of objects with `name` and `color`.",
)
def _find_claim_labels(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    """Active labels whose modules include claims."""
    return [{"name": label.name, "color": label.color or None} for label in _claim_labels()]


def _claim_labels() -> list[TaskLabel]:
    """Active labels offered on claims, in their display order.

    Matched in Python: labels number in the dozens, and ``modules`` is an array
    column whose containment lookup differs by database backend.
    """
    labels = TaskLabel.objects.filter(active=True).order_by("position", "name")
    return [label for label in labels if TaskLabelModule.CLAIMS in (label.modules or [])]


@standard_tools.tool(
    name="find_claim_assignees",
    description=(
        "Find active staff members and teams a claim can be assigned to, by name. "
        "assign_claim takes a staff member's or a team's `id`. Requires the "
        "run's revenue capability."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "name_contains": {
                "type": "string",
                "description": "Case-insensitive substring of the staff member's or team's name.",
            },
        },
    },
    categories=("claims_reads",),
    required_capabilities=REVENUE,
    returns_description=(
        "Object with `staff` (array of `id`, `name`) and `teams` (array of `id`, `name`), "
        "each capped at 25."
    ),
)
def _find_claim_assignees(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Staff and teams matching a name."""
    staff = Staff.objects.filter(active=True)
    teams = Team.objects.all()
    if name := (arguments.get("name_contains") or "").strip():
        staff = staff.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name))
        teams = teams.filter(name__icontains=name)
    return {
        "staff": [
            {"id": str(member.id), "name": _staff_name(member)}
            for member in staff.order_by("last_name", "first_name")[:25]
        ],
        "teams": [{"id": str(team.id), "name": team.name} for team in teams.order_by("name")[:25]],
    }


def _staged(ctx: dict[str, Any], effect: Any, claim: Claim, **details: Any) -> dict[str, Any]:
    """Stage ``effect`` and confirm it to the model."""
    ctx["effects"].append(effect)
    return {"ok": True, "claim_id": str(claim.id), **details}


@standard_tools.tool(
    name="move_claim_to_queue",
    description=(
        "Move a claim to another queue, such as from coding review to queued for "
        "submission. Takes a queue `name` or `display_name` from find_claim_queues. "
        "Trashing a claim is left to a person. Requires the run's revenue capability."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "queue": {"type": "string", "description": "Target queue `name` or `display_name`."},
            "claim_id": CLAIM_ID_PROPERTY,
        },
        "required": ["queue"],
    },
    categories=("claims_writes",),
    required_capabilities=REVENUE,
    returns_description="`{ok, claim_id, queue}` with the queue's `name`.",
    effect_types=("MOVE_CLAIM_TO_QUEUE",),
)
def _move_claim_to_queue(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Stage a queue move, refusing the trash queue."""
    claim = _requesters_claim(arguments.get("claim_id"), ctx)
    requested = arguments["queue"]
    queue = ClaimQueue.objects.filter(
        Q(name__iexact=requested) | Q(display_name__iexact=requested)
    ).first()
    if queue is None:
        raise ValueError(f"queue {requested!r} not found; find_claim_queues lists them")
    if queue.queue_sort_ordering == ClaimQueues.TRASH:
        raise ValueError("Moving a claim to the trash is left to a person.")
    effect = ClaimEffect(claim_id=claim.id).move_to_queue(queue.name)
    return _staged(ctx, effect, claim, queue=queue.name)


@standard_tools.tool(
    name="assign_claim",
    description=(
        "Assign a claim to a staff member or a team, given exactly one `id` from "
        "find_claim_assignees. Requires the run's revenue capability."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "staff_id": {"type": "string", "description": "The staff member's `id`."},
            "team_id": {"type": "string", "description": "The team's `id`."},
            "claim_id": CLAIM_ID_PROPERTY,
        },
    },
    categories=("claims_writes",),
    required_capabilities=REVENUE,
    returns_description="`{ok, claim_id, assignee}` with the staff member's or team's name.",
    effect_types=("UPDATE_CLAIM_ASSIGNEE",),
)
def _assign_claim(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Stage an assignment to one staff member or one team."""
    claim = _requesters_claim(arguments.get("claim_id"), ctx)
    staff_id = arguments.get("staff_id")
    team_id = arguments.get("team_id")
    if bool(staff_id) == bool(team_id):
        raise ValueError("Give exactly one of staff_id or team_id.")
    if staff_id:
        staff = Staff.objects.filter(id=staff_id, active=True).first()
        if staff is None:
            raise ValueError(f"active staff member {staff_id!r} not found")
        effect = ClaimEffect(claim_id=claim.id).assign(assignee_id=str(staff.id))
        return _staged(ctx, effect, claim, assignee=_staff_name(staff))
    team = Team.objects.filter(id=_parse_id(team_id, "team")).first()
    if team is None:
        raise ValueError(f"team {team_id!r} not found")
    effect = ClaimEffect(claim_id=claim.id).assign(team_id=str(team.id))
    return _staged(ctx, effect, claim, assignee=team.name)


@standard_tools.tool(
    name="unassign_claim",
    description=("Clear a claim's assignee or team. Requires the run's revenue capability."),
    input_schema={"type": "object", "properties": {"claim_id": CLAIM_ID_PROPERTY}},
    categories=("claims_writes",),
    required_capabilities=REVENUE,
    returns_description="`{ok, claim_id}`.",
    effect_types=("UPDATE_CLAIM_ASSIGNEE",),
)
def _unassign_claim(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Stage clearing the assignment."""
    claim = _requesters_claim(arguments.get("claim_id"), ctx)
    return _staged(ctx, ClaimEffect(claim_id=claim.id).unassign(), claim)


LABELS_PROPERTY = {
    "type": "array",
    "items": {"type": "string"},
    "minItems": 1,
    "description": "Label names, from find_claim_labels.",
}


@standard_tools.tool(
    name="add_claim_labels",
    description=(
        "Add labels to a claim. Only labels find_claim_labels lists are accepted; "
        "creating a new label is left to a person. Requires the run's revenue "
        "capability."
    ),
    input_schema={
        "type": "object",
        "properties": {"labels": LABELS_PROPERTY, "claim_id": CLAIM_ID_PROPERTY},
        "required": ["labels"],
    },
    categories=("claims_writes",),
    required_capabilities=REVENUE,
    returns_description="`{ok, claim_id, labels}`.",
    effect_types=("ADD_CLAIM_LABEL",),
)
def _add_claim_labels(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Stage adding existing claim labels."""
    claim = _requesters_claim(arguments.get("claim_id"), ctx)
    labels = _existing_label_names(arguments["labels"])
    effect = ClaimEffect(claim_id=claim.id).add_labels(list[str | Label](labels))
    return _staged(ctx, effect, claim, labels=labels)


@standard_tools.tool(
    name="remove_claim_labels",
    description="Remove labels from a claim. Requires the run's revenue capability.",
    input_schema={
        "type": "object",
        "properties": {"labels": LABELS_PROPERTY, "claim_id": CLAIM_ID_PROPERTY},
        "required": ["labels"],
    },
    categories=("claims_writes",),
    required_capabilities=REVENUE,
    returns_description="`{ok, claim_id, labels}`.",
    effect_types=("REMOVE_CLAIM_LABEL",),
)
def _remove_claim_labels(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Stage removing labels the claim carries."""
    claim = _requesters_claim(arguments.get("claim_id"), ctx)
    carried = {label.name.lower(): label.name for label in claim.labels.all()}
    missing = [name for name in arguments["labels"] if name.lower() not in carried]
    if missing:
        raise ValueError(f"the claim does not carry {missing}")
    labels = [carried[name.lower()] for name in arguments["labels"]]
    return _staged(ctx, ClaimEffect(claim_id=claim.id).remove_labels(labels), claim, labels=labels)


def _existing_label_names(requested: list[str]) -> list[str]:
    """The configured claim labels' own names for ``requested``, or an error naming the rest."""
    configured = {label.name.lower(): label.name for label in _claim_labels()}
    missing = [name for name in requested if name.lower() not in configured]
    if missing:
        raise ValueError(f"no claim label named {missing}; find_claim_labels lists them")
    return [configured[name.lower()] for name in requested]


@standard_tools.tool(
    name="add_claim_comment",
    description=(
        "Add a comment to a claim's comment thread, visible to everyone working the "
        "claim. Requires the run's revenue capability."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "comment": {"type": "string", "minLength": 1, "description": "The comment text."},
            "claim_id": CLAIM_ID_PROPERTY,
        },
        "required": ["comment"],
    },
    categories=("claims_writes",),
    required_capabilities=REVENUE,
    returns_description="`{ok, claim_id}`.",
    effect_types=("ADD_CLAIM_COMMENT",),
)
def _add_claim_comment(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Stage a claim comment."""
    claim = _requesters_claim(arguments.get("claim_id"), ctx)
    comment = (arguments.get("comment") or "").strip()
    if not comment:
        raise ValueError("comment is empty")
    return _staged(ctx, ClaimEffect(claim_id=claim.id).add_comment(comment), claim)


@standard_tools.tool(
    name="add_claim_banner",
    description=(
        "Show a banner on a claim, such as a reminder that a prior authorization is "
        "pending. Requires the run's revenue capability."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "minLength": 1,
                "description": "Identifier for the banner; remove_claim_banner takes it.",
            },
            "narrative": {
                "type": "string",
                "minLength": 1,
                "maxLength": 90,
                "description": "Banner text, at most 90 characters.",
            },
            "intent": {
                "type": "string",
                "enum": [intent.value for intent in BannerAlertIntent],
                "description": "Severity: info, warning, or alert.",
            },
            "claim_id": CLAIM_ID_PROPERTY,
        },
        "required": ["key", "narrative", "intent"],
    },
    categories=("claims_writes",),
    required_capabilities=REVENUE,
    returns_description="`{ok, claim_id, key}`.",
    effect_types=("ADD_CLAIM_BANNER_ALERT",),
)
def _add_claim_banner(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Stage a claim banner."""
    claim = _requesters_claim(arguments.get("claim_id"), ctx)
    effect = ClaimEffect(claim_id=claim.id).add_banner(
        key=arguments["key"],
        narrative=arguments["narrative"],
        intent=BannerAlertIntent(arguments["intent"]),
    )
    return _staged(ctx, effect, claim, key=arguments["key"])


@standard_tools.tool(
    name="remove_claim_banner",
    description=(
        "Remove a claim banner by its `key`, from get_claim's `banners`. Requires the "
        "run's revenue capability."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "key": {"type": "string", "minLength": 1, "description": "The banner's `key`."},
            "claim_id": CLAIM_ID_PROPERTY,
        },
        "required": ["key"],
    },
    categories=("claims_writes",),
    required_capabilities=REVENUE,
    returns_description="`{ok, claim_id, key}`.",
    effect_types=("REMOVE_CLAIM_BANNER_ALERT",),
)
def _remove_claim_banner(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Stage removing a claim banner."""
    claim = _requesters_claim(arguments.get("claim_id"), ctx)
    effect = ClaimEffect(claim_id=claim.id).remove_banner(arguments["key"])
    return _staged(ctx, effect, claim, key=arguments["key"])


__exports__ = ()
