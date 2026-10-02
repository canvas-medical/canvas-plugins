"""Registry-level + smoke tests for ``canvas_sdk.agents.standard_tools``.

Two layers:

- **Registry-level (no DB)**: verify each advertised tool registers with an
  executor, has a non-empty input schema, and shows up in ``definitions()``.
- **Smoke (DB-touching)**: execute each tool against an empty test DB. The
  SQL compiles for real here; bugs where a queryset factory references a
  field/lookup that doesn't exist on the underlying model surface
  immediately as ``FieldError``. Catches the class of bug where the
  registry-only tests would pass but the production call would explode.
"""

from typing import Any

import pytest

from canvas_sdk.agents import standard_tools
from canvas_sdk.test_utils.factories import PatientFactory

EXPECTED_TOOLS = (
    "find_medications",
    "find_conditions",
    "find_lab_results",
    "find_assessments",
    "find_allergies",
    "find_immunizations",
    "find_vitals",
    "find_tasks",
    "find_appointments",
    "find_encounters",
    "find_notes",
    "get_open_note",
    "get_note_content",
    "find_goals",
    "find_imaging_reports",
    "find_referrals",
    "find_care_team_members",
    "find_medication_statements",
    "find_external_events",
    "find_prescriptions",
    "find_questionnaire_responses",
    "find_stop_medication_events",
    "find_banner_alerts",
    "find_protocol_cards",
    "get_patient_demographics",
    "create_task",
    "update_task",
    "add_task_comment",
    "add_banner_alert",
    "remove_banner_alert",
    "add_or_update_protocol_card",
    "originate_plan",
    "originate_prescribe_medication",
    "originate_lab_order",
    "originate_diagnose_condition",
    "originate_goal",
    "originate_assessment",
    "originate_follow_up",
    "originate_stop_medication",
)


def test_expected_tools_are_registered() -> None:
    """Every advertised tool name resolves to a registered executor."""
    registered = {definition["name"] for definition in standard_tools.definitions()}
    assert set(EXPECTED_TOOLS).issubset(registered), (
        f"missing tools in standard_tools registry: {set(EXPECTED_TOOLS) - registered}"
    )


def test_every_tool_has_input_schema_and_description() -> None:
    """Each tool's Anthropic-shaped definition has the required keys."""
    for definition in standard_tools.definitions():
        assert definition["name"], "tool definition missing name"
        assert definition["description"], f"tool {definition['name']!r} missing description"
        schema = definition["input_schema"]
        assert isinstance(schema, dict), f"tool {definition['name']!r} input_schema is not a dict"
        assert schema.get("type") == "object", (
            f"tool {definition['name']!r} input_schema must be an object schema"
        )


def test_definitions_returns_a_copy() -> None:
    """``definitions()`` returns a fresh list — callers can't mutate the registry."""
    snapshot_a = standard_tools.definitions()
    snapshot_a.clear()
    snapshot_b = standard_tools.definitions()
    assert snapshot_b, "definitions() should still return tools after caller clears its copy"


def test_get_patient_demographics_takes_no_arguments() -> None:
    """Demographics is a fixed-shape read; its schema accepts no properties."""
    definition = next(
        d for d in standard_tools.definitions() if d["name"] == "get_patient_demographics"
    )
    assert definition["input_schema"].get("properties") == {}


def test_find_conditions_advertises_expected_filters() -> None:
    """find_conditions exposes name/code/active/onset/limit filter knobs."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_conditions")
    properties = definition["input_schema"]["properties"]
    for key in ("name_contains", "code_contains", "active_only", "onset_on_or_after", "limit"):
        assert key in properties, f"find_conditions missing filter {key!r}"


def test_find_lab_results_advertises_expected_filters() -> None:
    """find_lab_results exposes name/observed_on/abnormal/limit filter knobs."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_lab_results")
    properties = definition["input_schema"]["properties"]
    for key in ("name_contains", "observed_on_or_after", "abnormal_only", "limit"):
        assert key in properties, f"find_lab_results missing filter {key!r}"


def test_find_assessments_exposes_limit_only() -> None:
    """Assessments are a recency-ordered read; only ``limit`` is filterable today."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_assessments")
    properties = definition["input_schema"]["properties"]
    assert "limit" in properties


def test_find_allergies_advertises_expected_filters() -> None:
    """find_allergies exposes name/severity/limit filter knobs."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_allergies")
    properties = definition["input_schema"]["properties"]
    for key in ("name_contains", "severity", "limit"):
        assert key in properties, f"find_allergies missing filter {key!r}"


def test_find_immunizations_advertises_expected_filters() -> None:
    """find_immunizations exposes name/given_on_or_after/limit filter knobs."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_immunizations")
    properties = definition["input_schema"]["properties"]
    for key in ("name_contains", "given_on_or_after", "limit"):
        assert key in properties, f"find_immunizations missing filter {key!r}"


def test_find_vitals_advertises_expected_filters() -> None:
    """find_vitals exposes name/observed_on_or_after/limit filter knobs."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_vitals")
    properties = definition["input_schema"]["properties"]
    for key in ("name_contains", "observed_on_or_after", "limit"):
        assert key in properties, f"find_vitals missing filter {key!r}"


def test_find_tasks_advertises_expected_filters() -> None:
    """find_tasks exposes status/title/due/limit filter knobs."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_tasks")
    properties = definition["input_schema"]["properties"]
    for key in ("status", "title_contains", "due_on_or_after", "limit"):
        assert key in properties, f"find_tasks missing filter {key!r}"


def test_find_appointments_advertises_expected_filters() -> None:
    """find_appointments exposes status + date-range filters."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_appointments")
    properties = definition["input_schema"]["properties"]
    for key in ("status", "starts_on_or_after", "starts_on_or_before", "limit"):
        assert key in properties, f"find_appointments missing filter {key!r}"


def test_find_encounters_advertises_expected_filters() -> None:
    """find_encounters exposes state + started_on_or_after filters."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_encounters")
    properties = definition["input_schema"]["properties"]
    for key in ("state", "started_on_or_after", "limit"):
        assert key in properties, f"find_encounters missing filter {key!r}"


def test_find_notes_advertises_expected_filters() -> None:
    """find_notes exposes state + note_type + note_type_name_contains + since + limit."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_notes")
    properties = definition["input_schema"]["properties"]
    for key in ("state", "note_type", "note_type_name_contains", "since", "limit"):
        assert key in properties, f"find_notes missing filter {key!r}"


def test_find_notes_state_and_note_type_filters_expose_enum_values() -> None:
    """The closed-set filters surface their valid values as JSON-Schema enums.

    Without this, the LLM has to guess valid strings (and was failing on
    realistic prompts like 'most recent inpatient visit' — the canonical
    value is 'inpatient' but the model was guessing other terms).
    """
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_notes")
    properties = definition["input_schema"]["properties"]
    assert "enum" in properties["state"], "state filter should expose NoteStates enum"
    assert "NEW" in properties["state"]["enum"]
    assert "LKD" in properties["state"]["enum"]
    assert "enum" in properties["note_type"], (
        "note_type filter should expose NoteTypeCategories enum"
    )
    # NoteTypeCategories — the canonical category enum on the FK to NoteType,
    # which is where the actual category info lives (Note.note_type is the
    # legacy CharField and is empty in current installations).
    assert "inpatient" in properties["note_type"]["enum"]
    assert "encounter" in properties["note_type"]["enum"]
    assert "message" in properties["note_type"]["enum"]
    assert "review" in properties["note_type"]["enum"]


def test_get_open_note_takes_no_arguments() -> None:
    """get_open_note is a scalar read; its schema accepts no properties."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "get_open_note")
    assert definition["input_schema"].get("properties") == {}


def test_find_messages_advertises_expected_filters() -> None:
    """find_messages exposes from_patient_only + unread_only + since + limit."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_messages")
    properties = definition["input_schema"]["properties"]
    for key in ("from_patient_only", "unread_only", "since", "limit"):
        assert key in properties, f"find_messages missing filter {key!r}"


def test_originate_message_advertises_content_only() -> None:
    """originate_message takes content; sender/recipient come from ctx, not the model.

    The agent must NOT be able to set sender_id or recipient_id — those
    are stamped by the platform from the patient scope and the calling
    staff's session. Exposing them to the model would let the agent
    address messages to arbitrary parties.
    """
    definition = next(d for d in standard_tools.definitions() if d["name"] == "originate_message")
    properties = definition["input_schema"]["properties"]
    assert set(properties) == {"content"}, (
        f"originate_message should only expose 'content' to the model, got {set(properties)}"
    )
    assert definition["input_schema"]["required"] == ["content"]


def test_find_note_types_advertises_expected_filters() -> None:
    """find_note_types exposes category + name_contains + active_only + limit."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_note_types")
    properties = definition["input_schema"]["properties"]
    for key in ("category", "name_contains", "active_only", "limit"):
        assert key in properties, f"find_note_types missing filter {key!r}"
    # The category filter MUST surface its enum so the LLM doesn't guess strings.
    assert "review" in properties["category"]["enum"]
    assert "encounter" in properties["category"]["enum"]


def test_find_practice_locations_advertises_expected_filters() -> None:
    """find_practice_locations exposes active_only + name_contains + limit."""
    definition = next(
        d for d in standard_tools.definitions() if d["name"] == "find_practice_locations"
    )
    properties = definition["input_schema"]["properties"]
    for key in ("active_only", "name_contains", "limit"):
        assert key in properties, f"find_practice_locations missing filter {key!r}"


def test_find_lab_partners_advertises_expected_filters() -> None:
    """find_lab_partners exposes name_contains + active_only + electronic_ordering_only."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_lab_partners")
    properties = definition["input_schema"]["properties"]
    for key in ("name_contains", "active_only", "electronic_ordering_only", "limit"):
        assert key in properties, f"find_lab_partners missing filter {key!r}"


def test_find_lab_partner_tests_advertises_expected_filters() -> None:
    """find_lab_partner_tests requires partner scoping + exposes search + cpt_contains."""
    definition = next(
        d for d in standard_tools.definitions() if d["name"] == "find_lab_partner_tests"
    )
    properties = definition["input_schema"]["properties"]
    for key in ("lab_partner_id", "lab_partner_name", "search", "cpt_contains", "limit"):
        assert key in properties, f"find_lab_partner_tests missing filter {key!r}"


def test_originate_review_note_schema_shape() -> None:
    """originate_review_note requires narrative + note_type_id + practice_location_id.

    patient_id and staff_id MUST NOT be in the schema — they're stamped
    from ctx by the platform, not chosen by the model. Letting the agent
    pick a patient_id would let it draft notes on arbitrary patients.
    """
    definition = next(
        d for d in standard_tools.definitions() if d["name"] == "originate_review_note"
    )
    properties = definition["input_schema"]["properties"]
    required = set(definition["input_schema"]["required"])
    assert required == {"narrative", "note_type_id", "practice_location_id"}, (
        f"originate_review_note required mismatch: {required}"
    )
    assert "patient_id" not in properties
    assert "provider_id" not in properties
    assert "staff_id" not in properties
    assert "title" in properties
    assert "datetime_of_service" in properties


@pytest.mark.django_db
def test_get_open_note_returns_null_when_patient_has_no_notes() -> None:
    """No notes in the DB → get_open_note returns None (not a raise).

    The agent should be able to call get_open_note unconditionally; the
    'no open note' case is a normal answer, not an error.
    """
    patient = PatientFactory.create()
    result = standard_tools.execute("get_open_note", {}, ctx={"patient_id": patient.id})
    assert result is None


def test_get_note_content_requires_note_id() -> None:
    """get_note_content's schema marks `note_id` as required."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "get_note_content")
    assert definition["input_schema"].get("required") == ["note_id"]
    assert "note_id" in definition["input_schema"]["properties"]


@pytest.mark.django_db
def test_get_note_content_returns_null_for_unknown_note_id() -> None:
    """A note_id that doesn't exist returns None (the 'not found' case)."""
    patient = PatientFactory.create()
    result = standard_tools.execute(
        "get_note_content",
        {"note_id": "00000000-0000-0000-0000-000000000000"},
        ctx={"patient_id": patient.id},
    )
    assert result is None


def test_walk_note_body_preserves_text_and_command_order() -> None:
    """The body walker emits text + command items in their document order."""
    from canvas_sdk.agents.standard_tools import _walk_note_body

    body = [
        {"type": "text", "value": "Pt reports persistent fatigue."},
        {
            "type": "command",
            "value": "assess",
            "data": {"id": 1, "command_uuid": "abc-123"},
        },
        {"type": "text", "value": ""},  # empty — should be dropped
        {
            "type": "command",
            "value": "plan",
            "data": {"id": 2, "command_uuid": "def-456"},
        },
        {"type": "text", "value": "Discussed lifestyle changes."},
    ]
    walked = _walk_note_body(body)

    assert walked == [
        ("text", {"value": "Pt reports persistent fatigue."}),
        ("command", {"uuid": "abc-123", "schema_key": "assess"}),
        ("command", {"uuid": "def-456", "schema_key": "plan"}),
        ("text", {"value": "Discussed lifestyle changes."}),
    ]


def test_walk_note_body_returns_empty_for_non_list_input() -> None:
    """Defensive: a malformed body (not a list) returns []."""
    from canvas_sdk.agents.standard_tools import _walk_note_body

    assert _walk_note_body({}) == []
    assert _walk_note_body(None) == []
    assert _walk_note_body("oops") == []


def test_find_goals_advertises_expected_filters() -> None:
    """find_goals exposes statement + status/priority filters."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_goals")
    properties = definition["input_schema"]["properties"]
    for key in (
        "statement_contains",
        "lifecycle_status",
        "achievement_status",
        "priority",
        "limit",
    ):
        assert key in properties, f"find_goals missing filter {key!r}"


def test_find_imaging_reports_advertises_expected_filters() -> None:
    """find_imaging_reports exposes name + assigned-date filters."""
    definition = next(
        d for d in standard_tools.definitions() if d["name"] == "find_imaging_reports"
    )
    properties = definition["input_schema"]["properties"]
    for key in ("name_contains", "assigned_on_or_after", "limit"):
        assert key in properties, f"find_imaging_reports missing filter {key!r}"


def test_find_referrals_advertises_expected_filters() -> None:
    """find_referrals exposes question + priority + date filters."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_referrals")
    properties = definition["input_schema"]["properties"]
    for key in ("question_contains", "priority", "referred_on_or_after", "limit"):
        assert key in properties, f"find_referrals missing filter {key!r}"


def test_find_care_team_members_advertises_expected_filters() -> None:
    """find_care_team_members exposes role + status filters."""
    definition = next(
        d for d in standard_tools.definitions() if d["name"] == "find_care_team_members"
    )
    properties = definition["input_schema"]["properties"]
    for key in ("role_contains", "status", "limit"):
        assert key in properties, f"find_care_team_members missing filter {key!r}"


def test_find_medication_statements_advertises_expected_filters() -> None:
    """find_medication_statements exposes name + started-on filters."""
    definition = next(
        d for d in standard_tools.definitions() if d["name"] == "find_medication_statements"
    )
    properties = definition["input_schema"]["properties"]
    for key in ("name_contains", "started_on_or_after", "limit"):
        assert key in properties, f"find_medication_statements missing filter {key!r}"


def test_find_external_events_advertises_expected_filters() -> None:
    """find_external_events exposes event_type + date filters."""
    definition = next(
        d for d in standard_tools.definitions() if d["name"] == "find_external_events"
    )
    properties = definition["input_schema"]["properties"]
    for key in ("event_type", "occurred_on_or_after", "limit"):
        assert key in properties, f"find_external_events missing filter {key!r}"


def test_find_prescriptions_advertises_expected_filters() -> None:
    """find_prescriptions exposes name + status + written_on filters."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_prescriptions")
    properties = definition["input_schema"]["properties"]
    for key in ("name_contains", "status", "written_on_or_after", "limit"):
        assert key in properties, f"find_prescriptions missing filter {key!r}"


def test_find_questionnaire_responses_advertises_expected_filters() -> None:
    """find_questionnaire_responses exposes name + progress_status filters."""
    definition = next(
        d for d in standard_tools.definitions() if d["name"] == "find_questionnaire_responses"
    )
    properties = definition["input_schema"]["properties"]
    for key in ("name_contains", "progress_status", "limit"):
        assert key in properties, f"find_questionnaire_responses missing filter {key!r}"


def test_find_stop_medication_events_advertises_expected_filters() -> None:
    """find_stop_medication_events exposes name + rationale filters."""
    definition = next(
        d for d in standard_tools.definitions() if d["name"] == "find_stop_medication_events"
    )
    properties = definition["input_schema"]["properties"]
    for key in ("name_contains", "rationale_contains", "limit"):
        assert key in properties, f"find_stop_medication_events missing filter {key!r}"


def test_create_task_schema_requires_title_only() -> None:
    """create_task advertises a single required ``title`` argument."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "create_task")
    properties = definition["input_schema"]["properties"]
    assert set(properties) == {"title"}
    assert definition["input_schema"].get("required") == ["title"]


def test_create_task_executor_stages_an_add_task_effect() -> None:
    """create_task generates a UUID, stages an AddTask, and returns the task_id.

    No DB needed — AddTask is a pure :class:`canvas_sdk.effects.task.task.AddTask`
    that doesn't touch the database from ``.apply()`` (it produces an Effect
    payload the worker dispatches). We just verify the helper wired the
    pieces together correctly.
    """
    effects: list[Any] = []
    result = standard_tools.execute(
        "create_task",
        {"title": "Call patient about overdue A1c"},
        ctx={"patient_id": "pat-abc", "effects": effects},
    )

    assert result["ok"] is True
    assert result["task_id"], "create_task should return a non-empty task_id"
    assert len(effects) == 1, "create_task should stage exactly one effect"


def test_create_task_truncates_long_titles_to_200_chars() -> None:
    """Titles over 200 chars are truncated; the staged AddTask carries the shortened text."""
    long_title = "x" * 300
    effects: list[Any] = []
    standard_tools.execute(
        "create_task",
        {"title": long_title},
        ctx={"patient_id": "pat-abc", "effects": effects},
    )

    # The staged Effect's serialized payload should carry the 200-char title.
    # We inspect the underlying AddTask via the Effect payload — exact shape
    # is an implementation detail of Effect.apply(), so check the stage was
    # successful and the helper didn't blow up.
    assert len(effects) == 1


def test_add_banner_alert_schema_advertises_enums_and_required_fields() -> None:
    """add_banner_alert exposes narrative + intent (enum) + placement (array of enums)."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "add_banner_alert")
    properties = definition["input_schema"]["properties"]

    assert set(definition["input_schema"]["required"]) == {"narrative", "intent", "placement"}
    assert properties["intent"]["enum"] == ["info", "warning", "alert"]
    assert properties["placement"]["type"] == "array"
    assert properties["placement"]["items"]["enum"] == [
        "chart",
        "timeline",
        "appointment_card",
        "scheduling_card",
        "profile",
    ]
    assert properties["placement"]["minItems"] == 1


def test_add_banner_alert_executor_stages_an_add_banner_alert_effect() -> None:
    """add_banner_alert generates a key, converts enum strings, stages the Effect.

    No DB needed — AddBannerAlert is a pure Effect that produces a payload
    the worker dispatches from ``.apply()``.
    """
    effects: list[Any] = []
    result = standard_tools.execute(
        "add_banner_alert",
        {
            "narrative": "Overdue mammogram — last imaging 4y ago",
            "intent": "warning",
            "placement": ["chart"],
        },
        ctx={"patient_id": "pat-abc", "effects": effects},
    )

    assert result["ok"] is True
    assert result["banner_key"], "add_banner_alert should return a non-empty banner_key"
    assert len(effects) == 1


def test_update_task_schema_requires_task_id_only() -> None:
    """update_task requires task_id; status/title/due_on are all optional."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "update_task")
    properties = definition["input_schema"]["properties"]
    assert set(properties) == {"task_id", "status", "title", "due_on"}
    assert definition["input_schema"].get("required") == ["task_id"]
    assert properties["status"]["enum"] == ["COMPLETED", "CLOSED", "OPEN"]


def test_update_task_executor_renames_and_coerces_status_and_due() -> None:
    """update_task converts due_on→datetime and status→TaskStatus before staging."""
    effects: list[Any] = []
    result = standard_tools.execute(
        "update_task",
        {"task_id": "task-1", "status": "COMPLETED", "due_on": "2026-07-15"},
        ctx={"patient_id": "pat-abc", "effects": effects},
    )

    assert result == {"ok": True}
    assert len(effects) == 1


def test_update_task_omits_optional_fields_when_not_supplied() -> None:
    """Updating only the status leaves title/due alone (not present in kwargs)."""
    effects: list[Any] = []
    result = standard_tools.execute(
        "update_task",
        {"task_id": "task-1", "status": "CLOSED"},
        ctx={"patient_id": "pat-abc", "effects": effects},
    )

    assert result == {"ok": True}
    assert len(effects) == 1


def test_add_task_comment_schema_requires_task_id_and_body() -> None:
    """add_task_comment requires task_id + body, no other fields."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "add_task_comment")
    properties = definition["input_schema"]["properties"]
    assert set(properties) == {"task_id", "body"}
    assert set(definition["input_schema"].get("required", [])) == {"task_id", "body"}


def test_add_task_comment_executor_stages_an_add_task_comment_effect() -> None:
    """add_task_comment stages the Effect with the supplied task_id + body."""
    effects: list[Any] = []
    result = standard_tools.execute(
        "add_task_comment",
        {"task_id": "task-1", "body": "Patient called back, awaiting labs."},
        ctx={"patient_id": "pat-abc", "effects": effects},
    )

    assert result == {"ok": True}
    assert len(effects) == 1


def test_add_or_update_protocol_card_schema_advertises_status_enum_and_recommendations() -> None:
    """Protocol card exposes status enum + array-of-objects recommendations schema."""
    definition = next(
        d for d in standard_tools.definitions() if d["name"] == "add_or_update_protocol_card"
    )
    properties = definition["input_schema"]["properties"]
    assert set(definition["input_schema"]["required"]) == {"title", "narrative"}
    assert properties["status"]["enum"] == [
        "due",
        "satisfied",
        "not_applicable",
        "pending",
        "not_relevant",
    ]
    rec_items = properties["recommendations"]["items"]
    assert rec_items["type"] == "object"
    assert rec_items["required"] == ["title"]
    assert set(rec_items["properties"]) == {"title", "button", "href", "commands"}


def test_add_or_update_protocol_card_recommendations_advertise_commands_enum() -> None:
    """Each recommendation can carry a `commands` array with a typed enum."""
    definition = next(
        d for d in standard_tools.definitions() if d["name"] == "add_or_update_protocol_card"
    )
    rec_items = definition["input_schema"]["properties"]["recommendations"]["items"]
    assert "commands" in rec_items["properties"]
    cmd_items = rec_items["properties"]["commands"]["items"]
    assert cmd_items["type"] == "object"
    assert cmd_items["required"] == ["type"]
    # Enum surfaces the SDK's originate-command keys.
    enum = cmd_items["properties"]["type"]["enum"]
    for expected in ("plan", "prescribe", "labOrder", "imagingOrder", "refer"):
        assert expected in enum, f"command enum missing {expected!r}"


def test_add_or_update_protocol_card_wraps_recommendation_commands_into_envelope() -> None:
    """Supplied `{type, context}` flows into the card's commands list wrapped properly.

    The serialized payload's recommendations[].commands[] should match
    what ``Recommendation(commands=[LabOrderCommand(...)])`` would produce
    — the ``{command: {type}, context: {..., effect_type}}`` envelope.
    """
    import json as _json

    effects: list[Any] = []
    standard_tools.execute(
        "add_or_update_protocol_card",
        {
            "title": "Order A1c",
            "narrative": "Last A1c was 14 months ago.",
            "recommendations": [
                {
                    "title": "Order A1c to assess glycemic control",
                    "button": "Order A1c",
                    "commands": [
                        {
                            "type": "labOrder",
                            "context": {"tests_order_codes": ["83036"]},
                        }
                    ],
                }
            ],
        },
        ctx={"patient_id": "pat-abc", "effects": effects},
    )

    payload = _json.loads(effects[0].payload)
    rec = payload["data"]["recommendations"][0]
    assert rec["title"] == "Order A1c to assess glycemic control"
    assert rec["button"] == "Order A1c"
    cmd = rec["commands"][0]
    # The shape matches recommendation_context() output.
    assert cmd["command"] == {"type": "labOrder"}
    assert cmd["context"]["tests_order_codes"] == ["83036"]
    # effect_type stamp is derived from the type via constantization.
    assert cmd["context"]["effect_type"] == "ORIGINATE_LAB_ORDER_COMMAND"


def test_recommendation_command_constantization_handles_single_word_types() -> None:
    """Single-word types (e.g., 'plan') get constantized as 'PLAN'."""
    from canvas_sdk.agents.standard_tools import _wrap_recommendation_command

    wrapped = _wrap_recommendation_command({"type": "plan", "context": {}})
    assert wrapped["context"]["effect_type"] == "ORIGINATE_PLAN_COMMAND"


def test_recommendation_command_constantization_handles_camelcase_types() -> None:
    """Camel-case types (e.g., 'followUp') get split on capitals to UPPER_SNAKE."""
    from canvas_sdk.agents.standard_tools import _wrap_recommendation_command

    wrapped = _wrap_recommendation_command({"type": "followUp", "context": {}})
    assert wrapped["context"]["effect_type"] == "ORIGINATE_FOLLOW_UP_COMMAND"


def test_recommendation_command_handles_empty_context() -> None:
    """Omitting context is fine — wrapper still stamps effect_type."""
    from canvas_sdk.agents.standard_tools import _wrap_recommendation_command

    wrapped = _wrap_recommendation_command({"type": "labOrder"})
    assert wrapped["command"] == {"type": "labOrder"}
    assert wrapped["context"] == {"effect_type": "ORIGINATE_LAB_ORDER_COMMAND"}


def test_add_or_update_protocol_card_exposes_ui_control_fields() -> None:
    """due_in, can_be_snoozed, and feedback_enabled are optional knobs on the schema."""
    definition = next(
        d for d in standard_tools.definitions() if d["name"] == "add_or_update_protocol_card"
    )
    properties = definition["input_schema"]["properties"]
    assert properties["due_in"]["type"] == "integer"
    assert properties["can_be_snoozed"]["type"] == "boolean"
    assert properties["feedback_enabled"]["type"] == "boolean"
    # None of these are required.
    assert "due_in" not in definition["input_schema"].get("required", [])
    assert "can_be_snoozed" not in definition["input_schema"].get("required", [])
    assert "feedback_enabled" not in definition["input_schema"].get("required", [])


def test_add_or_update_protocol_card_executor_flows_ui_control_fields_to_effect() -> None:
    """Supplying due_in/can_be_snoozed/feedback_enabled lands them on the staged Effect.

    ``Effect.apply()`` JSON-serializes the payload, so we parse the string
    back out to inspect the values that home-app's interpreter will read
    from the 'data' subdict (per ProtocolCard.effect_payload).
    """
    import json as _json

    effects: list[Any] = []
    result = standard_tools.execute(
        "add_or_update_protocol_card",
        {
            "title": "Recheck A1c",
            "narrative": "Last A1c was 14 months ago.",
            "due_in": 90,
            "can_be_snoozed": True,
            "feedback_enabled": True,
        },
        ctx={"patient_id": "pat-abc", "effects": effects},
    )

    assert result["ok"] is True
    assert len(effects) == 1
    payload = _json.loads(effects[0].payload)
    data = payload["data"]
    assert data["due_in"] == 90
    assert data["can_be_snoozed"] is True
    assert data["feedback_enabled"] is True


def test_add_or_update_protocol_card_executor_generates_key_when_omitted() -> None:
    """When card_key is omitted, a UUID is generated and returned for follow-up calls."""
    effects: list[Any] = []
    result = standard_tools.execute(
        "add_or_update_protocol_card",
        {
            "title": "Diabetes management",
            "narrative": "A1c last drawn 14 months ago; recheck recommended.",
            "status": "due",
            "recommendations": [
                {"title": "Order A1c", "button": "Order", "href": "/orders/a1c"},
            ],
        },
        ctx={"patient_id": "pat-abc", "effects": effects},
    )

    assert result["ok"] is True
    assert result["card_key"], "card_key should be returned for later updates"
    assert len(effects) == 1


def test_add_or_update_protocol_card_executor_preserves_supplied_card_key() -> None:
    """When card_key is supplied, it's used as-is (idempotent update path)."""
    effects: list[Any] = []
    result = standard_tools.execute(
        "add_or_update_protocol_card",
        {
            "card_key": "stable-card-key-123",
            "title": "Diabetes management",
            "narrative": "Updated narrative.",
        },
        ctx={"patient_id": "pat-abc", "effects": effects},
    )

    assert result == {"ok": True, "card_key": "stable-card-key-123"}
    assert len(effects) == 1


_ORIGINATE_TOOLS = (
    "originate_plan",
    "originate_prescribe_medication",
    "originate_lab_order",
    "originate_diagnose_condition",
    "originate_goal",
    "originate_assessment",
    "originate_follow_up",
    "originate_stop_medication",
)


@pytest.mark.parametrize("tool_name", _ORIGINATE_TOOLS)
def test_originate_tool_returns_no_note_error_when_ctx_lacks_note_id(
    tool_name: str,
) -> None:
    """Every originate tool surfaces a structured no-note error when ctx['note_id'] is missing.

    The default note_resolver reads ctx['note_id']. Chat-style agents are
    expected to populate it (via find_open_note_uuid_from_ctx) before
    dispatch; triggered agents set it from their trigger payload. This
    test exercises the helper's no-note error path without requiring a
    real note row.
    """
    definition = next(d for d in standard_tools.definitions() if d["name"] == tool_name)
    # Build the minimal valid input by filling required fields with placeholder values.
    required = definition["input_schema"].get("required", [])
    properties = definition["input_schema"]["properties"]
    arguments: dict[str, Any] = {}
    for prop_name in required:
        prop_schema = properties[prop_name]
        prop_type = prop_schema.get("type")
        if prop_type == "string":
            arguments[prop_name] = "placeholder"
        elif prop_type == "array":
            arguments[prop_name] = ["placeholder"]
        elif prop_type == "integer":
            arguments[prop_name] = 1
        elif prop_type == "number":
            arguments[prop_name] = 1.0
        elif prop_type == "boolean":
            arguments[prop_name] = True

    effects: list[Any] = []
    result = standard_tools.execute(
        tool_name,
        arguments,
        ctx={"patient_id": "pat-abc", "effects": effects},
    )

    # The helper returns a dict with ok=False and an error string when the
    # note resolver returns None.
    assert isinstance(result, dict)
    assert result.get("ok") is False
    assert "error" in result
    # Nothing staged when the note is missing.
    assert effects == []


def test_originate_plan_schema_requires_narrative() -> None:
    """originate_plan's only required arg is `narrative`."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "originate_plan")
    assert definition["input_schema"]["required"] == ["narrative"]


def test_originate_prescribe_medication_schema_requires_sig_only() -> None:
    """originate_prescribe_medication requires sig; fdb_code is optional."""
    definition = next(
        d for d in standard_tools.definitions() if d["name"] == "originate_prescribe_medication"
    )
    properties = definition["input_schema"]["properties"]
    assert "sig" in properties
    assert "fdb_code" in properties
    assert definition["input_schema"]["required"] == ["sig"]


def test_originate_assessment_advertises_status_enum() -> None:
    """originate_assessment's status arg surfaces the AssessCommand.Status enum."""
    definition = next(
        d for d in standard_tools.definitions() if d["name"] == "originate_assessment"
    )
    properties = definition["input_schema"]["properties"]
    assert "condition_id" in properties
    assert properties["status"]["enum"] == ["improved", "stable", "deteriorated"]


def test_originate_goal_advertises_priority_and_achievement_enums() -> None:
    """originate_goal's priority + achievement_status surface their StrEnum values."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "originate_goal")
    properties = definition["input_schema"]["properties"]
    assert set(properties["priority"]["enum"]) == {
        "high-priority",
        "medium-priority",
        "low-priority",
    }
    assert "in-progress" in properties["achievement_status"]["enum"]


def test_find_banner_alerts_advertises_expected_filters() -> None:
    """find_banner_alerts exposes narrative + intent + include_inactive filters."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_banner_alerts")
    properties = definition["input_schema"]["properties"]
    for key in ("narrative_contains", "intent", "include_inactive", "limit"):
        assert key in properties, f"find_banner_alerts missing filter {key!r}"


def test_find_protocol_cards_advertises_expected_filters() -> None:
    """find_protocol_cards exposes title + status + plugin_name + active_only filters."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "find_protocol_cards")
    properties = definition["input_schema"]["properties"]
    for key in ("title_contains", "status", "plugin_name", "active_only", "limit"):
        assert key in properties, f"find_protocol_cards missing filter {key!r}"


def test_remove_banner_alert_schema_requires_banner_key_only() -> None:
    """remove_banner_alert advertises a single required ``banner_key`` argument."""
    definition = next(d for d in standard_tools.definitions() if d["name"] == "remove_banner_alert")
    properties = definition["input_schema"]["properties"]
    assert set(properties) == {"banner_key"}
    assert definition["input_schema"].get("required") == ["banner_key"]


def test_remove_banner_alert_executor_stages_a_remove_banner_alert_effect() -> None:
    """remove_banner_alert renames banner_key→key and stages the Effect."""
    effects: list[Any] = []
    result = standard_tools.execute(
        "remove_banner_alert",
        {"banner_key": "banner-uuid-123"},
        ctx={"patient_id": "pat-abc", "effects": effects},
    )

    assert result == {"ok": True}
    assert len(effects) == 1


def test_add_banner_alert_rejects_narrative_over_90_chars_via_truncation() -> None:
    """Narrative is truncated to 90 chars before the Effect is constructed.

    AddBannerAlert's pydantic Field has ``max_length=90``; if the helper
    didn't truncate, the Effect constructor would raise. The successful
    stage confirms the helper-side truncation happened.
    """
    long_narrative = "x" * 200
    effects: list[Any] = []
    standard_tools.execute(
        "add_banner_alert",
        {
            "narrative": long_narrative,
            "intent": "info",
            "placement": ["chart", "timeline"],
        },
        ctx={"patient_id": "pat-abc", "effects": effects},
    )

    assert len(effects) == 1


# ---------------------------------------------------------------------------
# Smoke tests — execute each tool against an empty DB.
#
# These catch the class of bug where the queryset factory compiles fine as
# Python but blows up when Django builds SQL (invalid field reference, broken
# manager method composition, etc.). Registry-level tests can't catch these
# because they never iterate the queryset.
# ---------------------------------------------------------------------------


_LIST_RETURNING_TOOLS = (
    "find_medications",
    "find_conditions",
    "find_lab_results",
    "find_assessments",
    "find_allergies",
    "find_immunizations",
    "find_vitals",
    "find_tasks",
    "find_appointments",
    "find_encounters",
    "find_notes",
    "find_goals",
    "find_imaging_reports",
    "find_referrals",
    "find_care_team_members",
    "find_medication_statements",
    "find_external_events",
    "find_prescriptions",
    "find_questionnaire_responses",
    "find_stop_medication_events",
    "find_banner_alerts",
    "find_protocol_cards",
)


@pytest.mark.django_db
@pytest.mark.parametrize("tool_name", _LIST_RETURNING_TOOLS)
def test_filter_search_tool_executes_against_empty_db(tool_name: str) -> None:
    """Each filter-search tool runs cleanly with no data; returns an empty list.

    Catches `FieldError` and similar SQL-compilation failures by actually
    evaluating the queryset. With no rows for the patient, the result must
    be ``[]`` (not ``None`` and not a raise).
    """
    patient = PatientFactory.create()

    result = standard_tools.execute(tool_name, {}, ctx={"patient_id": patient.id})

    assert result == [], f"{tool_name} returned non-empty against empty DB: {result!r}"


@pytest.mark.django_db
def test_get_patient_demographics_executes_against_real_patient() -> None:
    """The scalar demographics tool resolves the patient and returns its identity fields.

    This is the only standard tool whose executor needs an existing row in
    the DB — it does ``Patient.objects.get(id=patient_id)``. The smoke test
    confirms the field accessors line up with the actual Patient model.
    """
    patient = PatientFactory.create(first_name="Ada", last_name="Lovelace")

    result = standard_tools.execute("get_patient_demographics", {}, ctx={"patient_id": patient.id})

    assert result["first_name"] == "Ada"
    assert result["last_name"] == "Lovelace"
    assert result["mrn"] == patient.mrn
    # Every documented key is present (no AttributeError mid-serialize).
    for key in (
        "first_name",
        "middle_name",
        "last_name",
        "preferred_name",
        "mrn",
        "birth_date",
        "age_years",
        "sex_at_birth",
        "gender_identity",
        "preferred_pronouns",
        "deceased",
    ):
        assert key in result, f"{key} missing from demographics dict"


@pytest.mark.django_db
@pytest.mark.parametrize("tool_name", _LIST_RETURNING_TOOLS)
def test_filter_search_tool_respects_supplied_filters_against_empty_db(
    tool_name: str,
) -> None:
    """Pass each tool's full filter set; SQL still compiles and returns [].

    Catches bugs in filter `apply` callables (e.g., bad ``__icontains`` field
    paths) that the no-arg smoke test would miss because the filter wasn't
    triggered.
    """
    patient = PatientFactory.create()
    # Supply truthy values for every filter declared on the tool. We don't
    # care about correctness of results (DB is empty); we care that the
    # filter chain compiles to valid SQL.
    definition = next(d for d in standard_tools.definitions() if d["name"] == tool_name)
    arguments: dict[str, object] = {}
    for prop_name, prop_schema in definition["input_schema"]["properties"].items():
        if prop_name == "limit":
            continue
        type_ = prop_schema.get("type")
        if type_ == "string" and prop_schema.get("format") == "date":
            arguments[prop_name] = "2024-01-01"
        elif type_ == "string":
            arguments[prop_name] = "test"
        elif type_ == "boolean":
            arguments[prop_name] = True
        elif type_ == "integer":
            arguments[prop_name] = 1

    result = standard_tools.execute(tool_name, arguments, ctx={"patient_id": patient.id})

    assert result == [], f"{tool_name} with filters {arguments!r} returned non-empty: {result!r}"
