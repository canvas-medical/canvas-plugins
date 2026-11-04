import json
from datetime import date
from typing import Any

import pytest
from canvas__agent_runner_poc.agents.intake import DocumentIntakeAgent

from canvas_sdk.agents import RunSubject
from canvas_sdk.effects import EffectType
from canvas_sdk.test_utils.agents import (
    FakeGateway,
    prepare_agent,
    reply,
    run_agent,
    text,
    tool_use,
)
from canvas_sdk.test_utils.factories import (
    DocumentTypeFactory,
    IntegrationTaskFactory,
    PatientFactory,
)

# The intake agent's grant in CANVAS_MANIFEST.json.
GRANT = ["@intake_reads", "@intake_writes"]


def _agent(document: Any) -> DocumentIntakeAgent:
    agent: DocumentIntakeAgent = prepare_agent(
        DocumentIntakeAgent, allowed=GRANT, subject=RunSubject(document_id=str(document.id))
    )
    return agent


@pytest.mark.django_db
def test_intake_suggests_the_patient_and_type_the_document_names() -> None:
    """Suggestions the model makes are effects the grant lets the platform apply."""
    document = IntegrationTaskFactory.create(patient=None)
    patient = PatientFactory.create(last_name="Doe", birth_date=date(1980, 4, 2))
    lab = DocumentTypeFactory.create(name="Lab Report", report_type="CLINICAL")
    gateway = FakeGateway(
        reply(tool_use("suggest_patient", {"last_name": "Doe", "birth_date": "1980-04-02"})),
        reply(tool_use("categorize_document", {"document_type_key": lab.key})),
        reply(text("Suggested the patient and the type.")),
    )

    run = run_agent(_agent(document), gateway)

    assert [effect.type for effect in run.effects] == [
        EffectType.LINK_DOCUMENT_TO_PATIENT,
        EffectType.CATEGORIZE_DOCUMENT,
    ]
    assert json.loads(run.effects[0].payload)["data"]["patient_key"] == patient.id
    assert run.dropped == []


@pytest.mark.django_db
def test_intake_has_only_the_intake_tools() -> None:
    """The agent cannot reach a chart, a task, or a message: only the document."""
    agent = _agent(IntegrationTaskFactory.create(patient=None))

    assert {d["name"] for d in agent.tools.definitions()} == {
        "read_incoming_document",
        "match_patient",
        "find_document_types",
        "find_report_templates",
        "suggest_patient",
        "categorize_document",
        "prefill_document_fields",
        "assign_document_reviewer",
    }


@pytest.mark.django_db
def test_intake_tells_the_model_which_document_without_its_contents() -> None:
    """The document's text reaches the model only through read_incoming_document."""
    document = IntegrationTaskFactory.create(patient=None, title="Fax from Valley Lab")
    gateway = FakeGateway(reply(text("Nothing to do.")))

    run_agent(_agent(document), gateway)

    sent = json.dumps(gateway.requests[0]["messages"])
    assert "Fax from Valley Lab" in sent and str(document.id) not in sent
