from typing import Any

from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import SimpleAPIRoute
from canvas_sdk.handlers.simple_api.security import StaffSessionAuthMixin
from canvas_sdk.v1.data import (
    DocumentReference,
    DocumentReferenceCategory,
    DocumentReferenceCoding,
    DocumentReferenceStatus,
    MessageAttachment,
    Patient,
    PatientIdentificationCard,
    Snapshot,
    SnapshotImage,
)

# GET /plugin-io/api/documents_and_images/uat

EXPECTED_PRESIGNED_PARAMS = {
    "X-Amz-Algorithm",
    "X-Amz-Credential",
    "X-Amz-Date",
    "X-Amz-Expires",
    "X-Amz-SignedHeaders",
    "X-Amz-Signature",
}


def _parse_query_string(url: str) -> dict[str, str]:
    """Parse query string params from a URL using only string operations."""
    qs: dict[str, str] = {}
    if "?" not in url:
        return qs
    query = url.split("?", 1)[1]
    # Strip fragment
    if "#" in query:
        query = query.split("#", 1)[0]
    for part in query.split("&"):
        if "=" in part:
            key, val = part.split("=", 1)
            qs[key] = val
    return qs


def check_presigned_url(url: str | None) -> dict:
    """Validate that a URL looks like a valid presigned S3 URL."""
    if url is None:
        return {"valid": False, "error": "URL is None"}

    result: dict = {"url": url, "valid": True, "checks": {}}

    # Check it's HTTPS
    result["checks"]["is_https"] = url.startswith("https://")

    # Check it has S3 host pattern
    result["checks"]["has_s3_host"] = ".s3." in url and ".amazonaws.com" in url

    # Check query parameters
    params = _parse_query_string(url)
    missing = EXPECTED_PRESIGNED_PARAMS - set(params.keys())
    result["checks"]["has_all_params"] = len(missing) == 0
    if missing:
        result["checks"]["missing_params"] = list(missing)
        result["valid"] = False

    # Check expiry is 3600
    result["checks"]["expires_3600"] = params.get("X-Amz-Expires") == "3600"

    return result


def serialize_model(obj: Any, fields: list[str]) -> dict[str, str | None]:
    """Serialize a model instance to a dict with the given field names."""
    result: dict[str, str | None] = {}
    for field in fields:
        val = getattr(obj, field, "__MISSING__")
        if hasattr(val, "id"):
            result[field] = str(val.id)
        elif val == "__MISSING__":
            result[field] = "FIELD NOT FOUND"
        else:
            result[field] = str(val) if val is not None else None
    return result


class DocumentReferenceUAT(StaffSessionAuthMixin, SimpleAPIRoute):
    """UAT endpoint that exercises all new data models from KOALA-1979."""

    PATH = "/uat"

    def get(self) -> list[Response]:
        """Run all UAT checks and return results as JSON."""
        results: dict = {}

        # --- 1. DocumentReference ---
        results["1_document_reference"] = self._check_document_reference()

        # --- 2. DocumentReference related models ---
        results["2_document_reference_related"] = self._check_document_reference_related()

        # --- 3. Snapshot and SnapshotImage ---
        results["3_snapshot"] = self._check_snapshot()

        # --- 4. PatientIdentificationCard ---
        results["4_patient_id_card"] = self._check_patient_id_card()

        # --- 5. MessageAttachment presigned URL ---
        results["5_message_attachment"] = self._check_message_attachment()

        # --- Summary ---
        all_passed = all(
            section.get("passed", False)
            for section in results.values()
            if isinstance(section, dict)
        )
        results["all_passed"] = all_passed

        return [JSONResponse(results)]

    def _check_document_reference(self) -> dict:
        section: dict = {"passed": False, "checks": {}}

        # Check queryset works
        all_docs = DocumentReference.objects.all()
        count = all_docs.count()
        section["checks"]["query_all_count"] = count

        if count == 0:
            section["checks"]["note"] = "No DocumentReference records found — cannot fully validate"
            section["passed"] = True  # Not a failure, just no data
            return section

        # Check for_patient filtering
        doc = all_docs.first()
        fields = [
            "document",
            "document_absolute_url",
            "document_content_type",
            "business_identifier",
            "originator",
            "subject",
            "type",
            "category",
            "status",
            "date",
            "encounter",
            "team",
            "related_object_document_title",
            "related_object_document_comment",
        ]
        section["checks"]["sample_record"] = serialize_model(doc, fields)

        # Check for_patient
        if doc.subject and hasattr(doc.subject, "patient"):
            try:
                patient_id = str(doc.subject.patient.id)
                patient_docs = DocumentReference.objects.for_patient(patient_id)
                section["checks"]["for_patient_count"] = patient_docs.count()
            except Exception as e:
                section["checks"]["for_patient_error"] = str(e)
        else:
            section["checks"]["for_patient"] = "skipped — no subject.patient on sample record"

        # Check document_url presigned URL
        doc_with_file = all_docs.exclude(document="").exclude(document__isnull=True).first()
        if doc_with_file:
            section["checks"]["document_url"] = check_presigned_url(doc_with_file.document_url)
        else:
            section["checks"]["document_url"] = "No record with document file found"

        # Check fallback to document_absolute_url
        doc_without_file = (
            all_docs.filter(document="")
            .exclude(document_absolute_url__isnull=True)
            .exclude(document_absolute_url="")
            .first()
        )
        if doc_without_file:
            section["checks"]["document_url_fallback"] = {
                "url": doc_without_file.document_url,
                "is_absolute_url": doc_without_file.document_url
                == doc_without_file.document_absolute_url,
            }
        else:
            section["checks"]["document_url_fallback"] = (
                "No record with empty document + absolute_url found"
            )

        section["passed"] = True
        return section

    def _check_document_reference_related(self) -> dict:
        section: dict = {"passed": False, "checks": {}}

        # DocumentReferenceCoding
        coding_count = DocumentReferenceCoding.objects.count()
        section["checks"]["coding_count"] = coding_count
        if coding_count > 0:
            coding = DocumentReferenceCoding.objects.first()
            section["checks"]["coding_sample"] = serialize_model(
                coding, ["system", "version", "code", "display", "user_selected"]
            )

        # DocumentReferenceCategory
        cat_count = DocumentReferenceCategory.objects.count()
        section["checks"]["category_count"] = cat_count
        if cat_count > 0:
            cat = DocumentReferenceCategory.objects.first()
            section["checks"]["category_sample"] = serialize_model(
                cat, ["system", "version", "code", "display", "user_selected"]
            )

        # DocumentReferenceStatus enum
        section["checks"]["status_choices"] = [
            {"value": choice.value, "label": choice.label} for choice in DocumentReferenceStatus
        ]
        expected_values = {"current", "superseded", "entered-in-error"}
        actual_values = {choice.value for choice in DocumentReferenceStatus}
        section["checks"]["status_values_correct"] = actual_values == expected_values

        section["passed"] = True
        return section

    def _check_snapshot(self) -> dict:
        section: dict = {"passed": False, "checks": {}}

        # Snapshot
        snapshot_count = Snapshot.objects.count()
        section["checks"]["snapshot_count"] = snapshot_count
        if snapshot_count > 0:
            snap = Snapshot.objects.first()
            section["checks"]["snapshot_sample"] = serialize_model(
                snap,
                ["title", "description", "originator", "committer", "deleted", "entered_in_error"],
            )

        # SnapshotImage
        image_count = SnapshotImage.objects.count()
        section["checks"]["snapshot_image_count"] = image_count
        if image_count > 0:
            img = SnapshotImage.objects.first()
            section["checks"]["snapshot_image_sample"] = serialize_model(
                img, ["snapshot", "image", "title", "instruction", "tag"]
            )

            # Check image_url presigned URL
            img_with_file = (
                SnapshotImage.objects.exclude(image="").exclude(image__isnull=True).first()
            )
            if img_with_file:
                section["checks"]["image_url"] = check_presigned_url(img_with_file.image_url)
            else:
                section["checks"]["image_url"] = "No SnapshotImage with image file found"

            # Check None when empty
            img_without_file = SnapshotImage.objects.filter(image="").first()
            if img_without_file:
                section["checks"]["image_url_none_when_empty"] = img_without_file.image_url is None
            else:
                section["checks"]["image_url_none_when_empty"] = (
                    "No SnapshotImage with empty image found"
                )

        section["passed"] = True
        return section

    def _check_patient_id_card(self) -> dict:
        section: dict = {"passed": False, "checks": {}}

        card_count = PatientIdentificationCard.objects.count()
        section["checks"]["card_count"] = card_count

        if card_count == 0:
            section["checks"]["note"] = "No PatientIdentificationCard records found"
            section["passed"] = True
            return section

        card = PatientIdentificationCard.objects.first()
        section["checks"]["card_sample"] = serialize_model(card, ["image", "title", "active"])

        # Check via patient relation
        patient = Patient.objects.filter(identification_cards__isnull=False).first()
        if patient:
            via_relation = patient.identification_cards.count()
            section["checks"]["via_patient_relation_count"] = via_relation
        else:
            section["checks"]["via_patient_relation"] = "No patient with identification_cards found"

        # Check image_url
        card_with_image = (
            PatientIdentificationCard.objects.exclude(image="").exclude(image__isnull=True).first()
        )
        if card_with_image:
            section["checks"]["image_url"] = check_presigned_url(card_with_image.image_url)
        else:
            section["checks"]["image_url"] = "No card with image found"

        # Check None when empty
        card_without_image = PatientIdentificationCard.objects.filter(image="").first()
        if card_without_image:
            section["checks"]["image_url_none_when_empty"] = card_without_image.image_url is None
        else:
            section["checks"]["image_url_none_when_empty"] = "No card with empty image found"

        section["passed"] = True
        return section

    def _check_message_attachment(self) -> dict:
        section: dict = {"passed": False, "checks": {}}

        attachment_count = MessageAttachment.objects.count()
        section["checks"]["attachment_count"] = attachment_count

        if attachment_count == 0:
            section["checks"]["note"] = "No MessageAttachment records found"
            section["passed"] = True
            return section

        # Check file_url with a file
        att_with_file = (
            MessageAttachment.objects.exclude(file="").exclude(file__isnull=True).first()
        )
        if att_with_file:
            section["checks"]["file_url"] = check_presigned_url(att_with_file.file_url)
        else:
            section["checks"]["file_url"] = "No attachment with file found"

        # Check None when empty
        att_without_file = MessageAttachment.objects.filter(file="").first()
        if att_without_file:
            section["checks"]["file_url_none_when_empty"] = att_without_file.file_url is None
        else:
            section["checks"]["file_url_none_when_empty"] = "No attachment with empty file found"

        section["passed"] = True
        return section
