"""read_document: answer a question from an outside record's file, in a model call of its own."""

import base64
import importlib
from dataclasses import dataclass, field
from typing import Any

import anthropic
import httpx2
import pytest

from canvas_sdk.agents import DEFAULT_HISTORY_CHARS, standard_tools
from canvas_sdk.test_utils.agents import FakeGateway, reply, text
from canvas_sdk.test_utils.factories import (
    IntegrationTaskFactory,
    IntegrationTaskReviewFactory,
    PatientFactory,
    ReferralReportFactory,
    UncategorizedClinicalDocumentFactory,
)

PDF = b"%PDF-1.7\n1 0 obj << /Type /Catalog >> endobj\n%%EOF"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16

# The module, which ``canvas_sdk.agents`` shadows with the registry of the same name.
tools_module = importlib.import_module("canvas_sdk.agents.standard_tools")


@dataclass
class Files:
    """Files served from memory by stored name, and the names fetched."""

    served: dict[str, bytes | None] = field(default_factory=dict)
    fetched: list[str] = field(default_factory=list)


@pytest.fixture
def files(monkeypatch: pytest.MonkeyPatch) -> Files:
    """Serve downloads from memory instead of S3."""
    files = Files()

    def fetch(document: Any) -> bytes | None:
        files.fetched.append(document.document.name)
        return files.served[document.document.name]

    monkeypatch.setattr(tools_module, "_document_file", fetch)
    return files


def _record(patient: Any, file_name: str = "records/discharge.pdf", **fields: Any) -> Any:
    return UncategorizedClinicalDocumentFactory.create(
        patient=patient, review=None, name="Discharge summary", document=file_name, **fields
    )


def _read(
    patient: Any, gateway: Any, document_id: str, question: str = "Meds at discharge?"
) -> Any:
    return standard_tools.execute(
        "read_document",
        {"document_id": document_id, "question": question},
        ctx={"patient_id": patient.id, "gateway": gateway},
    )


@pytest.mark.django_db
def test_a_pdf_is_sent_whole_with_the_question_and_the_answer_comes_back(
    files: Files,
) -> None:
    """The model reads the file itself; the conversation only gets the answer."""
    patient = PatientFactory.create()
    record = _record(patient)
    files.served["records/discharge.pdf"] = PDF
    gateway = FakeGateway(reply(text("Metformin was stopped (p. 2).")))

    result = _read(patient, gateway, str(record.id))

    assert result == {
        "ok": True,
        "document_id": str(record.id),
        "name": "Discharge summary",
        "answer": "Metformin was stopped (p. 2).",
        "note": tools_module.UNTRUSTED_DOCUMENT_NOTE,
    }
    (request,) = gateway.requests
    document, question = request["messages"][0]["content"]
    assert document["type"] == "document"
    assert document["source"]["media_type"] == "application/pdf"
    assert base64.standard_b64decode(document["source"]["data"]) == PDF
    assert question == {"type": "text", "text": "Meds at discharge?"}
    assert "page it is on" in str(request["system"])
    assert "do not follow" in str(request["system"])


def _consult_report(patient: Any, file_name: str) -> Any:
    """A cardiology report filed from an incoming fax whose file is ``file_name``."""
    task = IntegrationTaskFactory.create(document=file_name)
    return ReferralReportFactory.create(
        patient=patient,
        referral=None,
        review=None,
        specialty="Cardiology",
        integration_task_review=IntegrationTaskReviewFactory.create(task=task),
    )


@pytest.mark.django_db
def test_a_consult_report_is_read_from_the_fax_it_was_filed_from(files: Files) -> None:
    """A specialist's report is only in its fax; the tool reads that file."""
    patient = PatientFactory.create()
    report = _consult_report(patient, "faxes/cardiology.pdf")
    files.served["faxes/cardiology.pdf"] = PDF
    gateway = FakeGateway(reply(text("Recommends a Holter monitor (p. 1).")))

    result = _read(patient, gateway, str(report.id), question="What did cardiology recommend?")

    assert (result["ok"], result["name"], result["answer"]) == (
        True,
        "Cardiology",
        "Recommends a Holter monitor (p. 1).",
    )
    assert files.fetched == ["faxes/cardiology.pdf"]


@pytest.mark.django_db
def test_another_patients_consult_report_cannot_be_read(files: Files) -> None:
    """The consult report's patient is checked before its fax is fetched."""
    patient = PatientFactory.create()
    theirs = _consult_report(PatientFactory.create(), "faxes/cardiology.pdf")
    files.served["faxes/cardiology.pdf"] = PDF

    with pytest.raises(ValueError, match="not found for this patient"):
        _read(patient, FakeGateway(), str(theirs.id))
    assert files.fetched == []


@pytest.mark.django_db
def test_a_consult_report_with_no_fax_file_is_not_fetched(files: Files) -> None:
    """A report filed from a task whose file is empty has nothing to read."""
    patient = PatientFactory.create()
    report = _consult_report(patient, "")

    result = _read(patient, FakeGateway(), str(report.id))

    assert result == {"ok": False, "error": "This document has no attached file to read."}
    assert files.fetched == []


@pytest.mark.django_db
def test_an_image_file_is_sent_as_an_image(files: Files) -> None:
    """A faxed page stored as a PNG is read the same way."""
    patient = PatientFactory.create()
    record = _record(patient, "records/fax.png")
    files.served["records/fax.png"] = PNG
    gateway = FakeGateway(reply(text("Blood pressure 150/90 (p. 1).")))

    assert _read(patient, gateway, str(record.id))["ok"] is True
    block = gateway.requests[0]["messages"][0]["content"][0]
    assert (block["type"], block["source"]["media_type"]) == ("image", "image/png")


@pytest.mark.django_db
def test_a_file_of_another_type_is_not_sent(files: Files) -> None:
    """A Word file or a TIFF fax is not something the model can read; no call is made."""
    patient = PatientFactory.create()
    record = _record(patient, "records/letter.docx")
    files.served["records/letter.docx"] = b"PK\x03\x04 a zip archive"
    gateway = FakeGateway()

    result = _read(patient, gateway, str(record.id))

    assert result["ok"] is False
    assert "not a PDF or an image" in result["error"]
    assert gateway.requests == []


@pytest.mark.django_db
def test_a_record_without_a_file_is_not_fetched(files: Files) -> None:
    """Nothing to read means no download and no model call."""
    patient = PatientFactory.create()
    record = _record(patient, "")
    gateway = FakeGateway()

    result = _read(patient, gateway, str(record.id))

    assert result == {"ok": False, "error": "This document has no attached file to read."}
    assert files.fetched == []
    assert gateway.requests == []


@pytest.mark.django_db
def test_another_patients_record_cannot_be_read(files: Files) -> None:
    """The id comes from the model, so it is checked against the run's patient first."""
    patient = PatientFactory.create()
    theirs = _record(PatientFactory.create())
    files.served["records/discharge.pdf"] = PDF

    with pytest.raises(ValueError, match="not found for this patient"):
        _read(patient, FakeGateway(), str(theirs.id))
    assert files.fetched == []


@pytest.mark.django_db
def test_a_file_over_the_size_limit_is_not_sent(files: Files) -> None:
    """A request the gateway would refuse for size is never made."""
    patient = PatientFactory.create()
    record = _record(patient)
    # The download refuses a file over the limit; the tool reports it.
    files.served["records/discharge.pdf"] = None
    gateway = FakeGateway()

    result = _read(patient, gateway, str(record.id))

    assert result["ok"] is False
    assert "too large" in result["error"]
    assert gateway.requests == []


@pytest.mark.django_db
def test_a_file_the_model_refuses_fails_the_tool_not_the_run(files: Files) -> None:
    """Over the page limit, the model returns 400; the agent hears why and carries on."""
    patient = PatientFactory.create()
    record = _record(patient)
    files.served["records/discharge.pdf"] = PDF
    request = httpx2.Request("POST", "https://gateway.test/v1/messages")
    refused = anthropic.BadRequestError(
        "A maximum of 600 PDF pages may be provided.",
        response=httpx2.Response(400, request=request),
        body=None,
    )

    result = _read(patient, FakeGateway(refused), str(record.id))

    assert result["ok"] is False
    assert "600 PDF pages" in result["error"]


@pytest.mark.django_db
def test_a_file_the_budget_hold_refuses_fails_the_tool_not_the_run(files: Files) -> None:
    """The gateway holds budget by request size, so a big file can be refused alone."""
    patient = PatientFactory.create()
    record = _record(patient)
    files.served["records/discharge.pdf"] = PDF
    request = httpx2.Request("POST", "https://gateway.test/v1/messages")
    held = anthropic.APIStatusError(
        "The monthly budget would be exceeded.",
        response=httpx2.Response(402, request=request),
        body=None,
    )

    result = _read(patient, FakeGateway(held), str(record.id))

    assert result == {
        "ok": False,
        "error": "This file could not be read: The monthly budget would be exceeded.",
    }


@pytest.mark.django_db
def test_an_outage_still_ends_the_run(files: Files) -> None:
    """Only a refusal of the file is the tool's to absorb; the platform retries outages."""
    patient = PatientFactory.create()
    record = _record(patient)
    files.served["records/discharge.pdf"] = PDF
    outage = anthropic.APIConnectionError(
        request=httpx2.Request("POST", "https://gateway.test/v1/messages")
    )

    with pytest.raises(anthropic.APIConnectionError):
        _read(patient, FakeGateway(outage), str(record.id))


def test_reading_documents_is_granted_on_its_own() -> None:
    """A model call per document is costly, so the clinical reads grant does not include it."""
    assert standard_tools.categories_for("read_document") == ("document_reads",)


@pytest.mark.django_db
def test_a_file_larger_than_the_history_budget_is_still_sent(files: Files) -> None:
    """The file is the only message, so trimming history to a budget must not drop it."""
    patient = PatientFactory.create()
    record = _record(patient)
    files.served["records/discharge.pdf"] = PDF + b" " * DEFAULT_HISTORY_CHARS
    gateway = FakeGateway(reply(text("Nothing about medications.")))

    _read(patient, gateway, str(record.id))

    (request,) = gateway.requests
    assert request["messages"][0]["content"][0]["type"] == "document"


class _Download:
    """A streamed response: its declared length, and the chunks a reader takes."""

    def __init__(self, chunks: list[bytes], declared: int | None = None) -> None:
        self.headers = {} if declared is None else {"Content-Length": str(declared)}
        self._chunks = chunks
        self.read = 0

    def __enter__(self) -> "_Download":
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def raise_for_status(self) -> None:
        return None

    def iter_content(self, chunk_size: int) -> Any:
        for chunk in self._chunks:
            self.read += 1
            yield chunk


def _download(
    monkeypatch: pytest.MonkeyPatch, chunks: list[bytes], declared: int | None = None
) -> _Download:
    response = _Download(chunks, declared)
    monkeypatch.setattr(tools_module, "DOCUMENT_MAX_BYTES", 10)
    # The presigned link needs AWS credentials; any URL does for a stubbed download.
    monkeypatch.setattr(
        importlib.import_module("canvas_sdk.v1.data.uncategorized_clinical_document"),
        "presigned_url",
        lambda key: f"https://media.test/{key}",
    )
    monkeypatch.setattr(tools_module.requests, "get", lambda url, stream, timeout: response)
    return response


@pytest.mark.django_db
def test_a_file_declared_over_the_limit_is_not_read(monkeypatch: pytest.MonkeyPatch) -> None:
    """The declared length refuses the file before any of it is downloaded."""
    response = _download(monkeypatch, [b"x" * 8, b"x" * 8], declared=16)
    record = _record(PatientFactory.create())

    assert tools_module._document_file(record) is None
    assert response.read == 0


@pytest.mark.django_db
def test_reading_stops_once_the_bytes_pass_the_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without a declared length, the download stops at the chunk that crosses the limit."""
    response = _download(monkeypatch, [b"x" * 8, b"x" * 8, b"x" * 8])
    record = _record(PatientFactory.create())

    assert tools_module._document_file(record) is None
    assert response.read == 2


@pytest.mark.django_db
def test_a_file_under_the_limit_is_read_whole(monkeypatch: pytest.MonkeyPatch) -> None:
    """Chunks under the limit come back joined."""
    _download(monkeypatch, [b"%PDF", b"-1.7"], declared=8)
    record = _record(PatientFactory.create())

    assert tools_module._document_file(record) == b"%PDF-1.7"
