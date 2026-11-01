"""Citations: an agent's reply cites the chart records its tools returned.

The model cites a record by writing ``[[cite:<id>]]`` after a statement, with the ``id``
of a row a read tool returned (see :data:`CITATION_GUIDANCE`). :class:`Sources` collects,
from a conversation's stored messages, every row that a citable read tool returned, and
:func:`cite` turns a reply's markers into numbered references with a :class:`Citation`
for each. A marker whose id no tool returned is dropped, so every citation is a row the
SDK read from the chart, described from that row rather than from text the model wrote.

A tool is citable when it was registered with a ``model`` (as
:meth:`ToolRegistry.filter_search_tool` does) and not marked ``citable=False``, or with
``cites=<record type>`` (as :meth:`ToolRegistry.tool` takes).
"""

import json
import re
from dataclasses import dataclass
from typing import Any, NamedTuple

from canvas_sdk.agents.tool_registry import ToolRegistry

CITATION_GUIDANCE = (
    "\n\nCitations (required): the chat shows every record you cite as a numbered "
    "source the user can check, and a statement drawn from the chart without one reads "
    "as unsourced. End every statement that comes from a tool result with "
    "[[cite:<id>]], copying that row's full `id`; in a list, cite each item. For "
    "example, given the row "
    '{"id": "a8850d4a-b118-4244-86eb-d91862e650ae", "name": "Metformin ER 1,000 mg"}, '
    "write:\n"
    "- Metformin ER 1,000 mg, active [[cite:a8850d4a-b118-4244-86eb-d91862e650ae]]\n"
    "Cite only ids a tool returned in this conversation, never one you did not read. "
    "Statements that are not about the chart need no citation."
)

MARKER = re.compile(r"[ \t]?\[\[cite:([A-Za-z0-9_-]+)\]\]")

# Longest detail text a card shows, so a message or a sig does not fill the panel.
MAX_DETAIL_CHARS = 160


class CardFields(NamedTuple):
    """Which fields of a tool's row describe a cited record.

    ``kind_field`` names a row field that holds the kind, for a tool whose rows are of
    several kinds; ``kind`` is used when the row leaves it empty.
    """

    kind: str
    label: str
    details: tuple[str, ...] = ()
    date: str | None = None
    kind_field: str | None = None


# Keyed by the SDK model's class name, or the record type a tool cites. A type missing
# here is described generically.
CARD_FIELDS: dict[str, CardFields] = {
    "Medication": CardFields("Medication", "name", ("status",), "start_date"),
    "Condition": CardFields("Condition", "display", ("clinical_status", "code"), "onset_date"),
    "LabValue": CardFields("Lab result", "test", ("value", "units", "abnormal_flag"), "date"),
    "Assessment": CardFields("Assessment", "condition_display", ("status",), "date"),
    "AllergyIntolerance": CardFields("Allergy", "display", ("severity", "status"), "onset_date"),
    "Immunization": CardFields("Immunization", "display", ("status",), "date_administered"),
    "Observation": CardFields("Vital", "name", ("value", "units"), "date"),
    "Task": CardFields("Task", "title", ("status",), "due"),
    "Message": CardFields("Message", "sender_name", ("content",), "sent_at"),
    "Appointment": CardFields(
        "Appointment", "description", ("status", "provider_name"), "start_time"
    ),
    "Encounter": CardFields("Encounter", "medium", ("state",), "start_time"),
    "Note": CardFields("Note", "title", ("note_type_name", "provider_name"), "datetime_of_service"),
    "Goal": CardFields("Goal", "goal_statement", ("achievement_status",), "start_date"),
    "ImagingReport": CardFields("Imaging report", "name", (), "assigned_date"),
    "Referral": CardFields(
        "Referral", "service_provider_name", ("clinical_question",), "date_referred"
    ),
    "CareTeamMembership": CardFields("Care team", "staff_name", ("role_display",)),
    "MedicationStatement": CardFields(
        "Medication statement", "medication_name", ("sig_original_input",), "start_date"
    ),
    "ExternalEvent": CardFields(
        "External event", "event_type", ("facility_name",), "event_datetime"
    ),
    "Prescription": CardFields(
        "Prescription", "medication_name", ("status", "sig_original_input"), "written_date"
    ),
    "Interview": CardFields("Questionnaire", "name", ("status",), "answered_at"),
    "StopMedicationEvent": CardFields(
        "Stopped medication", "medication_name", ("rationale",), "stopped_at"
    ),
    "OpenLoop": CardFields("Order", "item", ("summary",), "ordered_on", kind_field="type"),
    "Document": CardFields(
        "Document", "name", ("category", "from", "review"), "date", kind_field="type"
    ),
}


@dataclass(frozen=True)
class Source:
    """A row a citable read tool returned: the record and what the tool said about it.

    ``model`` is the SDK model's class name, or the record type the tool cites.
    """

    id: str
    tool: str
    model: str
    row: dict[str, Any]


@dataclass(frozen=True)
class Citation:
    """A numbered reference in a reply, described from the row its tool returned.

    ``note_dbid`` is set for a note, or for a record whose row names the note it was
    made on, so a chart surface can navigate to it.
    """

    number: int
    id: str
    kind: str
    label: str
    detail: str
    date: str | None
    note_dbid: int | None

    def to_dict(self) -> dict[str, Any]:
        """The citation as JSON for a chat UI."""
        return {
            "number": self.number,
            "id": self.id,
            "kind": self.kind,
            "label": self.label,
            "detail": self.detail,
            "date": self.date,
            "note_dbid": self.note_dbid,
        }


class Sources:
    """The rows citable tools returned across a conversation's stored messages.

    Add messages in order: a tool result counts once the assistant turn that called its
    tool has been added.
    """

    def __init__(self, tools: ToolRegistry) -> None:
        self._tools = tools
        self._calls: dict[str, str] = {}
        self._rows: dict[str, Source] = {}

    def add(self, message: dict[str, Any]) -> None:
        """Take in one stored message: tool calls from the assistant, results from the user."""
        content = message.get("content")
        if not isinstance(content, list):
            return
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use" and message.get("role") == "assistant":
                self._calls[str(block.get("id"))] = str(block.get("name"))
            elif block.get("type") == "tool_result" and message.get("role") == "user":
                self._add_result(block)

    def add_all(self, messages: list[dict[str, Any]]) -> "Sources":
        """Take in every message, in order; returns ``self``."""
        for message in messages:
            self.add(message)
        return self

    def get(self, record_id: str) -> Source | None:
        """The row with ``record_id``, if a citable tool returned one."""
        return self._rows.get(record_id)

    def _add_result(self, block: dict[str, Any]) -> None:
        tool = self._calls.get(str(block.get("tool_use_id")))
        if tool is None or block.get("is_error"):
            return
        metadata = self._tools.metadata_for(tool)
        model = metadata.get("model")
        record_type = metadata.get("record_type") or (model.__name__ if model else None)
        if record_type is None or not metadata.get("citable", True):
            return
        try:
            rows = json.loads(block.get("content") or "")
        except ValueError:
            # A result cut short to fit the model's context is not valid JSON; its rows
            # cannot be cited.
            return
        if isinstance(rows, dict):
            rows = [rows]
        if not isinstance(rows, list):
            return
        for row in rows:
            if isinstance(row, dict) and row.get("id"):
                record_id = str(row["id"])
                self._rows[record_id] = Source(record_id, tool, record_type, row)


def cite(text: str, sources: Sources) -> tuple[str, list[Citation]]:
    """Number the citation markers in ``text`` and describe each cited record.

    A record cited more than once keeps its first number. A marker for an id no
    citable tool returned is removed.
    """
    numbers: dict[str, int] = {}
    citations: list[Citation] = []

    def replace(match: re.Match[str]) -> str:
        record_id = match.group(1)
        source = sources.get(record_id)
        if source is None:
            return ""
        if record_id not in numbers:
            numbers[record_id] = len(numbers) + 1
            citations.append(_citation(numbers[record_id], source))
        return f" [{numbers[record_id]}]"

    return MARKER.sub(replace, text), citations


def _citation(number: int, source: Source) -> Citation:
    row = source.row
    fields = CARD_FIELDS.get(source.model)
    if fields is None:
        label = next((str(v) for k, v in row.items() if k != "id" and isinstance(v, str) and v), "")
        fields = CardFields(_humanize(source.model), "")
    else:
        label = _text(row.get(fields.label))
    kind = _text(row.get(fields.kind_field)) if fields.kind_field else ""
    detail = ", ".join(text for key in fields.details if (text := _text(row.get(key))))
    date = _text(row.get(fields.date)) if fields.date else ""
    return Citation(
        number=number,
        id=source.id,
        kind=kind or fields.kind,
        label=label or kind or fields.kind,
        detail=detail[:MAX_DETAIL_CHARS],
        date=date or None,
        note_dbid=row.get("dbid") if source.model == "Note" else row.get("note_dbid"),
    )


def _text(value: Any) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if item)
    return str(value).strip()


def _humanize(name: str) -> str:
    words = re.sub(r"(?<!^)(?=[A-Z])", " ", name).lower()
    return words[:1].upper() + words[1:]


__exports__ = ("CITATION_GUIDANCE", "Citation", "Sources", "cite")
