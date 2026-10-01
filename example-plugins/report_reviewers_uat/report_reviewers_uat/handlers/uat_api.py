from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING, Any

from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import SimpleAPI, StaffSessionAuthMixin, api
from canvas_sdk.v1.data import (
    ImagingReport,
    LabReport,
    PatientAdministrativeDocument,
    ReferralReport,
    Staff,
    UncategorizedClinicalDocument,
)

if TYPE_CHECKING:
    from typing import TypeAlias

    from django.db.models import QuerySet

    Document: TypeAlias = (
        LabReport
        | ImagingReport
        | ReferralReport
        | UncategorizedClinicalDocument
        | PatientAdministrativeDocument
    )

DOCUMENT_TYPES: dict[str, type[Document]] = {
    "lab_report": LabReport,
    "imaging_report": ImagingReport,
    "referral_report": ReferralReport,
    "uncategorized_clinical_document": UncategorizedClinicalDocument,
    "patient_administrative_document": PatientAdministrativeDocument,
}

SAMPLE_SIZE = 5


def serialize_staff(staff: Staff) -> dict[str, str]:
    """Return the identifying fields of a staff member."""
    return {"id": str(staff.id), "name": f"{staff.first_name} {staff.last_name}"}


def serialize_document(document: Document) -> dict[str, Any]:
    """Return a document's identifiers, review state and assigned reviewers (no clinical content)."""
    return {
        "id": str(document.id),
        "assigned_date": document.assigned_date.isoformat() if document.assigned_date else None,
        "reviewed": document.review_id is not None,
        "reviewers": [serialize_staff(staff) for staff in document.reviewers.all()],
    }


def assigned_documents(model: type[Document]) -> QuerySet[Document]:
    """Return the documents of a type that have at least one assigned reviewer."""
    return (
        model.objects.filter(reviewers__isnull=False)
        .distinct()
        .prefetch_related("reviewers")
        .order_by("-dbid")
    )


def check_document_type(model: type[Document]) -> dict[str, Any]:
    """Read a sample of assigned documents and confirm the reviewer filter agrees with them."""
    documents = list(assigned_documents(model)[:SAMPLE_SIZE])
    mismatches = [
        {"document": str(document.id), "reviewer": str(staff.id)}
        for document in documents
        for staff in document.reviewers.all()
        if not model.objects.filter(dbid=document.dbid, reviewers__id=staff.id).exists()
    ]
    return {
        "passed": not mismatches,
        "has_data": bool(documents),
        "total": model.objects.count(),
        "assigned": assigned_documents(model).count(),
        "sample": [serialize_document(document) for document in documents],
        "filter_mismatches": mismatches,
    }


class ReportReviewersUatAPI(StaffSessionAuthMixin, SimpleAPI):
    """UAT endpoints for the reviewers relation on report and document data models.

    Open the endpoints in a browser while logged in to the instance as staff.
    """

    PREFIX = ""

    @api.get("/run")
    def run(self) -> list[Response | Effect]:
        """Check every document type and report whether reviewers resolve and filter correctly."""
        results: dict[str, Any] = {}
        for name, model in DOCUMENT_TYPES.items():
            try:
                results[name] = check_document_type(model)
            except Exception as e:
                results[name] = {"passed": False, "error": f"{e.__class__.__name__}: {e}"}

        sections = list(results.values())
        return [
            JSONResponse(
                {
                    "all_passed": all(section["passed"] for section in sections),
                    "types_without_assigned_documents": [
                        name for name, section in results.items() if not section.get("has_data")
                    ],
                    "results": results,
                }
            )
        ]

    @api.get("/queue")
    def queue(self) -> list[Response | Effect]:
        """List the documents assigned to a staff member (default: the logged-in user)."""
        staff_id = self.request.query_params.get("staff_id") or self.request.headers.get(
            "canvas-logged-in-user-id"
        )
        staff = Staff.objects.filter(id=staff_id).first()
        if staff is None:
            return [JSONResponse({"error": f"Staff {staff_id} not found"}, HTTPStatus.NOT_FOUND)]

        queue = {
            name: [
                serialize_document(document)
                for document in model.objects.filter(reviewers__id=staff.id)
                .prefetch_related("reviewers")
                .order_by("-dbid")
            ]
            for name, model in DOCUMENT_TYPES.items()
        }
        return [JSONResponse({"staff": serialize_staff(staff), "queue": queue})]

    @api.get("/document")
    def document(self) -> list[Response | Effect]:
        """Return the reviewers of one document, given ?type=<document type>&id=<document id>."""
        document_type = self.request.query_params.get("type", "")
        model = DOCUMENT_TYPES.get(document_type)
        if model is None:
            return [
                JSONResponse(
                    {"error": f"type must be one of {sorted(DOCUMENT_TYPES)}"},
                    HTTPStatus.BAD_REQUEST,
                )
            ]

        document = (
            model.objects.filter(id=self.request.query_params.get("id"))
            .prefetch_related("reviewers")
            .first()
        )
        if document is None:
            return [JSONResponse({"error": "Document not found"}, HTTPStatus.NOT_FOUND)]

        return [JSONResponse(serialize_document(document))]
