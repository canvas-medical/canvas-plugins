"""Tools exposed to the ChartChatAgent.

The chat agent's full tool surface comes from the SDK's
:data:`canvas_sdk.agents.standard_tools` registry via
``tools.extend(standard_tools)`` below — clinical reads, task tools,
banner-alert tools, protocol cards, and the originate-on-note commands
(Plan / Prescribe / LabOrder / Diagnose / Goal / Assessment / FollowUp /
StopMedication).

Plugin-specific composition tools live here too:

- ``generate_chart_summary`` — single sub-agent that reads the patient's
  chart and returns a concise narrative. Replaces the original
  ChartSummary AgentPlugin + ChartSummaryTrigger (which always fired on
  new-encounter creation, regardless of whether the clinician asked).
  On-demand now; the parent decides whether to surface the text inline,
  originate a Plan onto an open encounter, draft it as a review note,
  or message it to the patient.
- ``generate_pre_visit_brief`` — fans out to four focused sub-agents in
  parallel (labs trends / meds changes / recent visits / outstanding work),
  each with a narrow system prompt and a tiny tool subset, then
  synthesizes their summaries into a single brief.

Both demonstrate the "sub-agent as role, not class" pattern from
canvas_sdk.agents.subagent — pure config dataclasses, no AgentPlugin
registration, no per-spec manifest entries.

ChartChatAgent.respond() resolves the patient's current open note once
per turn via :func:`canvas_sdk.agents.find_open_note_uuid_from_ctx`
and stores it on ``tool_ctx["note_id"]``. It also stamps the run's
``gateway`` and parent ``tools`` registry onto the ctx so composition
tools like ``generate_pre_visit_brief`` can spawn sub-agents.
"""

from typing import Any

from canvas_sdk.agents import (
    SubAgentSpec,
    ToolRegistry,
    run_subagent,
    run_subagents,
    standard_tools,
)

tools = ToolRegistry()
tools.extend(standard_tools)


# Chart-summary sub-agent. Demoted from a standalone AgentPlugin
# (and its always-on note-creation trigger) — the auto-fire was
# undesirable, and the summary logic naturally fits the same role-as-
# config shape as the pre-visit-brief specs. ChartChat now calls
# `generate_chart_summary` on demand; the parent decides whether to
# surface the text inline, originate a Plan onto an open encounter,
# draft it as a review note, or send it as a patient message.
_CHART_SUMMARY_SUBAGENT = SubAgentSpec(
    name="chart_summary",
    system_prompt=(
        "You are a clinical documentation sub-agent. Read this patient's "
        "chart with the find_* tools (active conditions, recent labs, "
        "current medications, allergies, immunizations as relevant) and "
        "produce a concise narrative summary the clinician can scan in "
        "10-15 seconds. Plain prose paragraph OR a tight bulleted list — "
        "whichever fits the patient better. No headers, no preamble. "
        "Prioritize clinically actionable items (abnormal labs, recent "
        "diagnoses, deprescribing candidates) over comprehensive "
        "enumeration. Don't recommend actions — the parent agent decides "
        "what to do with your summary."
    ),
    allowed_tool_names=frozenset(
        {
            "find_conditions",
            "find_lab_results",
            "find_medications",
            "find_allergies",
            "find_immunizations",
            "find_vitals",
        }
    ),
)


def _generate_chart_summary(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Run the chart_summary sub-agent and return its narrative.

    Read-only — emits no effects. The parent decides how to surface the
    text. Composition-tool ctx contract: ``parent_tools`` and ``gateway``
    must be on ctx (stamped by ChartChatAgent.run before each turn).
    """
    parent_tools = ctx.get("parent_tools")
    gateway = ctx.get("gateway")
    if parent_tools is None or gateway is None:
        return {
            "ok": False,
            "error": (
                "generate_chart_summary requires parent_tools and gateway on ctx; "
                "the calling agent must stamp them before invoking composition tools."
            ),
        }

    summary = run_subagent(
        _CHART_SUMMARY_SUBAGENT,
        "Summarize this patient's chart for the clinician.",
        parent_tools=parent_tools,
        parent_ctx=ctx,
        gateway=gateway,
    )
    return {"ok": True, "summary": summary}


tools.register(
    {
        "name": "generate_chart_summary",
        "description": (
            "Generate a concise narrative summary of this patient's chart by "
            "delegating to a focused sub-agent with read-only access. Returns "
            "`{ok: true, summary: <text>}` — the sub-agent does NOT originate "
            "any effects; you decide what to do with the text. Common follow-ups: "
            "paste the summary into the chat reply, feed it to `originate_review_note` "
            "as the narrative, feed it to `originate_plan` to land it on the "
            "patient's current open encounter, or feed it to `originate_message` "
            "as the body of a message to the patient. Use when the clinician asks "
            "to summarize the patient, draft a chart-review note, or wants a "
            "quick overview."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    _generate_chart_summary,
    categories=("composition",),
    metadata={
        "returns_description": (
            "Object with `ok: true` and a `summary` string containing the "
            "sub-agent's narrative. Read-only; no effects originated."
        ),
    },
)


# Pre-visit brief fan-out: 4 focused sub-agents, parallel.
# Each persona's system prompt is intentionally narrow — fan-out's
# win is that the model isn't juggling 30 tools and the full
# instruction set; it focuses on one domain and returns a tight
# summary. Tool allowlists are subsets of the parent's manifest grant,
# enforced via ToolRegistry.scope() inside run_subagent.
_PRE_VISIT_BRIEF_SUBAGENTS = (
    SubAgentSpec(
        name="labs_trends",
        system_prompt=(
            "You are a clinical sub-agent. The parent agent has asked "
            "you to identify what's notable about this patient's recent "
            "labs for an upcoming visit. Call `find_lab_results` "
            "(typically with `since` set to the last 6-12 months and a "
            "limit of 25-50). Identify abnormal results, recent changes "
            "worth discussing, and any trends (worsening, improving, "
            "stable). Return 3-5 short bullet points. No headers, no "
            "preamble — bullets only. If there's nothing notable, "
            "return one bullet: '- No notable lab changes.'"
        ),
        allowed_tool_names=frozenset({"find_lab_results"}),
    ),
    SubAgentSpec(
        name="meds_changes",
        system_prompt=(
            "You are a clinical sub-agent. The parent agent has asked "
            "you to summarize what's notable about this patient's "
            "medications for an upcoming visit. Call `find_medications` "
            "with `active_only=true`, then optionally a second call "
            "with `active_only=false` to see recently stopped meds. "
            "Identify recent starts/stops, dose changes worth "
            "discussing, and any potential interactions or deprescribing "
            "candidates. Return 3-5 short bullet points. No headers, no "
            "preamble — bullets only. If nothing notable, return one "
            "bullet: '- No recent medication changes.'"
        ),
        allowed_tool_names=frozenset({"find_medications"}),
    ),
    SubAgentSpec(
        name="recent_visits",
        system_prompt=(
            "You are a clinical sub-agent. The parent agent has asked "
            "you to summarize this patient's recent visits for an "
            "upcoming appointment. Call `find_notes` filtering for "
            "encounter-type notes (note_type='encounter') with a "
            "`since` of the last 6 months, limit 10. Pull recent "
            "encounters and pick out reasons for visit, key findings, "
            "and any plans made. Return 3-5 short bullet points. No "
            "headers, no preamble — bullets only. Include the visit "
            "date in each bullet."
        ),
        allowed_tool_names=frozenset({"find_notes", "get_note_content"}),
    ),
    SubAgentSpec(
        name="outstanding_work",
        system_prompt=(
            "You are a clinical sub-agent. The parent agent has asked "
            "you to summarize this patient's outstanding clinical work "
            "for an upcoming visit. Call `find_tasks` (OPEN tasks) and "
            "`find_protocol_cards` (status='due' or 'pending'). Pull "
            "what's not yet addressed and what the clinician should "
            "follow up on. Return 3-5 short bullet points. No headers, "
            "no preamble — bullets only. If nothing's outstanding, "
            "return one bullet: '- No outstanding tasks or protocols.'"
        ),
        allowed_tool_names=frozenset({"find_tasks", "find_protocol_cards"}),
    ),
)


def _generate_pre_visit_brief(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """Fan out to 4 focused sub-agents and return their per-domain summaries.

    Composition-tool executor — accesses the parent's gateway and tools
    registry off ``ctx`` (stamped by ChartChatAgent.run before each
    turn). Sub-agents share the same ``ctx`` so any write effects they
    originate flow into the parent's accumulator.
    """
    parent_tools = ctx.get("parent_tools")
    gateway = ctx.get("gateway")
    if parent_tools is None or gateway is None:
        return {
            "ok": False,
            "error": (
                "generate_pre_visit_brief requires parent_tools and gateway on ctx; "
                "the calling agent must stamp them before invoking composition tools."
            ),
        }

    # All four sub-agents get the same prompt — the persona's system
    # prompt is what differentiates them, not the user message.
    delegation = (
        "Summarize what's notable about this patient for an upcoming "
        "visit, within your domain. Be concise; the parent will "
        "synthesize across domains."
    )

    results = run_subagents(
        _PRE_VISIT_BRIEF_SUBAGENTS,
        delegation,
        parent_tools=parent_tools,
        parent_ctx=ctx,
        gateway=gateway,
    )
    return {"ok": True, "domains": results}


tools.register(
    {
        "name": "generate_pre_visit_brief",
        "description": (
            "Generate a pre-visit clinical brief for this patient by fanning "
            "out to four focused sub-agents in parallel — labs trends, "
            "medication changes, recent visits, and outstanding work. Each "
            "returns 3-5 bullets in its domain; you synthesize across them. "
            "Use when the clinician asks for a pre-visit summary, 'what do "
            "I need to know about this patient before their appointment', "
            "or similar. Faster and more focused than calling find_* tools "
            "yourself — each sub-agent has a tight context scoped to its "
            "domain. Returns `{ok: true, domains: {labs_trends: '...', "
            "meds_changes: '...', recent_visits: '...', outstanding_work: '...'}}`. "
            "Read all four domain summaries, then write a unified brief "
            "for the clinician — don't just paste the sub-agent output."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    _generate_pre_visit_brief,
    categories=("composition",),
    metadata={
        "returns_description": (
            "Object with `ok: true` and a `domains` map: keys are "
            "'labs_trends', 'meds_changes', 'recent_visits', "
            "'outstanding_work'; values are short bullet-point summaries."
        ),
    },
)
