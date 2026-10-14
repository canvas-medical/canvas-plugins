import json
from datetime import date
from enum import Enum, StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect
from canvas_sdk.v1.data.coverage import Coverage as CoverageModel
from canvas_sdk.v1.data.coverage import (
    CoverageRank,
    CoverageRelationshipCode,
    CoverageStack,
    Transactor,
    TransactorCoverageType,
)
from canvas_sdk.v1.data.patient import Patient

# Fields a plugin can set on create and update.
WRITABLE_FIELDS: tuple[str, ...] = (
    "issuer_id",
    "issuer_address_id",
    "issuer_phone_id",
    "subscriber_id",
    "patient_relationship_to_subscriber",
    "subscriber_identifier",
    "coverage_rank",
    "coverage_type",
    "stack",
    "id_number",
    "plan",
    "sub_plan",
    "group",
    "sub_group",
    "employer",
    "coverage_start_date",
    "coverage_end_date",
    "comments",
    "card_image_front_upload_key",
    "card_image_back_upload_key",
)

CREATE_REQUIRED_FIELDS: tuple[str, ...] = (
    "patient_id",
    "issuer_id",
    "coverage_rank",
    "id_number",
    "patient_relationship_to_subscriber",
)

# Fields that may be omitted on update but never set to None.
UPDATE_NON_NULLABLE_FIELDS: tuple[str, ...] = (
    "issuer_id",
    "coverage_rank",
    "id_number",
    "patient_relationship_to_subscriber",
    "stack",
    "subscriber_id",
    "coverage_start_date",
    "card_image_front_upload_key",
    "card_image_back_upload_key",
)

UPLOAD_KEY_FIELDS: tuple[str, ...] = ("card_image_front_upload_key", "card_image_back_upload_key")


def _is_plugin_upload_key(key: str) -> bool:
    """Return whether the key looks like one returned by a ``file_uploads="stored"`` route."""
    return key.startswith("plugin-uploads/") or "/plugin-uploads/" in key


class PhotoSide(StrEnum):
    """Side of an insurance card."""

    FRONT = "FRONT"
    BACK = "BACK"


class Coverage(TrackableFieldsModel):
    """
    Effect to create, update, expire, or remove a patient's insurance coverage.

    Card images (PNG or JPEG) are attached by passing the ``key`` of a
    ``StoredFilePart`` received on a SimpleAPI route declared with
    ``file_uploads="stored"``. Canvas copies the file into the coverage, then deletes
    the upload, so a key can be attached once.

    The plan type is taken from the payer (``issuer_id``) and cannot be set directly.

    On update, only the fields you set are changed, and setting a field to ``None``
    clears it.

    Example (create):
        Coverage(
            patient_id="patient-id",
            issuer_id="transactor-id",
            coverage_rank=CoverageRank.PRIMARY,
            id_number="ABC123",
            patient_relationship_to_subscriber=CoverageRelationshipCode.SELF,
            card_image_front_upload_key=front_part.key,
            card_image_back_upload_key=back_part.key,
        ).create()

    Example (update the back of the card only):
        Coverage(coverage_id="coverage-id", card_image_back_upload_key=part.key).update()

    Example (expire):
        Coverage(coverage_id="coverage-id").expire(coverage_end_date=date(2026, 12, 31))
    """

    class Meta:
        effect_type = "COVERAGE"

    coverage_id: str | UUID | None = None
    patient_id: str | None = None

    issuer_id: str | UUID | None = None
    issuer_address_id: str | UUID | None = None
    issuer_phone_id: str | UUID | None = None

    subscriber_id: str | None = None
    patient_relationship_to_subscriber: CoverageRelationshipCode | None = Field(
        default=None, strict=False
    )
    subscriber_identifier: str | None = None

    coverage_rank: CoverageRank | None = Field(default=None, strict=False)
    coverage_type: TransactorCoverageType | None = Field(default=None, strict=False)
    stack: CoverageStack | None = Field(default=None, strict=False)

    id_number: str | None = None
    plan: str | None = None
    sub_plan: str | None = None
    group: str | None = None
    sub_group: str | None = None
    employer: str | None = None
    coverage_start_date: date | None = None
    coverage_end_date: date | None = None
    comments: str | None = None

    card_image_front_upload_key: str | None = None
    card_image_back_upload_key: str | None = None

    def _data(self, fields: tuple[str, ...]) -> dict[str, Any]:
        """Return the serialized values of the given fields that were explicitly set."""
        data: dict[str, Any] = {}
        for field in fields:
            if not self.is_dirty(field):
                continue
            value = getattr(self, field)
            if isinstance(value, Enum):
                value = value.value
            elif isinstance(value, date):
                value = value.isoformat()
            elif isinstance(value, UUID):
                value = str(value)
            data[field] = value
        return data

    def _coverage_id_errors(self, method: str) -> list[InitErrorDetails]:
        if not self.coverage_id:
            return [
                self._create_error_detail(
                    "missing",
                    f"Field 'coverage_id' is required to {method} a coverage.",
                    self.coverage_id,
                )
            ]
        if not CoverageModel.objects.filter(id=self.coverage_id).exists():
            return [
                self._create_error_detail(
                    "value",
                    f"Coverage with id: {self.coverage_id} does not exist.",
                    self.coverage_id,
                )
            ]
        return []

    def _write_errors(self) -> list[InitErrorDetails]:
        """Errors shared by create and update."""
        errors: list[InitErrorDetails] = []

        if self.issuer_id and not Transactor.objects.filter(id=self.issuer_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Payer with id: {self.issuer_id} does not exist.",
                    self.issuer_id,
                )
            )

        for field in UPLOAD_KEY_FIELDS:
            key = getattr(self, field)
            if key is not None and not _is_plugin_upload_key(key):
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Field '{field}' must be the key of a file uploaded through a "
                        "SimpleAPI route declared with file_uploads='stored'.",
                        key,
                    )
                )

        return errors

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if method == "create":
            if self.coverage_id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Field 'coverage_id' should not be set when creating a coverage.",
                        self.coverage_id,
                    )
                )
            for field in CREATE_REQUIRED_FIELDS:
                if getattr(self, field) in (None, ""):
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            f"Field '{field}' is required to create a coverage.",
                            getattr(self, field),
                        )
                    )
            if self.patient_id and not Patient.objects.filter(id=self.patient_id).exists():
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Patient with id: {self.patient_id} does not exist.",
                        self.patient_id,
                    )
                )
            is_self = self.patient_relationship_to_subscriber == CoverageRelationshipCode.SELF
            if is_self and self.subscriber_id is not None and self.subscriber_id != self.patient_id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Field 'subscriber_id' must be omitted or equal 'patient_id' when the "
                        "patient is the subscriber.",
                        self.subscriber_id,
                    )
                )
            if (
                self.patient_relationship_to_subscriber is not None
                and not is_self
                and not self.subscriber_id
            ):
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'subscriber_id' is required when the patient is not the subscriber.",
                        None,
                    )
                )
            errors.extend(self._write_errors())

        elif method == "update":
            errors.extend(self._coverage_id_errors("update"))
            if self.is_dirty("patient_id"):
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Field 'patient_id' cannot be changed on an existing coverage.",
                        self.patient_id,
                    )
                )
            for field in UPDATE_NON_NULLABLE_FIELDS:
                if self.is_dirty(field) and getattr(self, field) is None:
                    errors.append(
                        self._create_error_detail(
                            "value",
                            f"Field '{field}' cannot be set to null when updating a coverage.",
                            None,
                        )
                    )
            errors.extend(self._write_errors())

        elif method == "expire":
            errors.extend(self._coverage_id_errors("expire"))
            if self.coverage_end_date is None:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'coverage_end_date' is required to expire a coverage.",
                        None,
                    )
                )

        elif method == "remove":
            errors.extend(self._coverage_id_errors("remove"))

        elif method == "remove_photo":
            errors.extend(self._coverage_id_errors("remove a card image from"))

        return errors

    def create(self) -> Effect:
        """Create a new coverage."""
        self._validate_before_effect("create")
        data = {"patient_id": self.patient_id, **self._data(WRITABLE_FIELDS)}
        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": data}),
        )

    def update(self) -> Effect:
        """Update an existing coverage, changing only the fields that were set."""
        self._validate_before_effect("update")
        data = {"coverage_id": str(self.coverage_id), **self._data(WRITABLE_FIELDS)}
        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": data}),
        )

    def expire(self, coverage_end_date: date | None = None) -> Effect:
        """Expire an existing coverage by setting its end date."""
        if coverage_end_date is not None:
            self.coverage_end_date = coverage_end_date
        self._validate_before_effect("expire")
        return Effect(
            type=f"EXPIRE_{self.Meta.effect_type}",
            payload=json.dumps(
                {
                    "data": {
                        "coverage_id": str(self.coverage_id),
                        "coverage_end_date": self.coverage_end_date.isoformat()
                        if self.coverage_end_date
                        else None,
                    }
                }
            ),
        )

    def remove(self) -> Effect:
        """Move an existing coverage to the removed stack."""
        self._validate_before_effect("remove")
        return Effect(
            type=f"REMOVE_{self.Meta.effect_type}",
            payload=json.dumps({"data": {"coverage_id": str(self.coverage_id)}}),
        )

    def remove_photo(self, side: PhotoSide) -> Effect:
        """Remove the front or back card file from an existing coverage."""
        side = PhotoSide(side)
        self._validate_before_effect("remove_photo")
        return Effect(
            type=f"REMOVE_{self.Meta.effect_type}_PHOTO",
            payload=json.dumps({"data": {"coverage_id": str(self.coverage_id), "side": side}}),
        )


class CoverageReorderEntry(BaseModel):
    """The new position of one coverage in a ``CoverageReorder``."""

    coverage_id: str | UUID
    coverage_rank: CoverageRank
    stack: CoverageStack


class CoverageReorder(TrackableFieldsModel):
    """
    Effect to set the rank and stack of several of a patient's coverages at once.

    Within each stack, ranks must be unique and consecutive starting at 1.

    Example:
        CoverageReorder(
            patient_id="patient-id",
            ordering=[
                CoverageReorderEntry(coverage_id="a", coverage_rank=1, stack=CoverageStack.IN_USE),
                CoverageReorderEntry(coverage_id="b", coverage_rank=2, stack=CoverageStack.IN_USE),
            ],
        ).apply()
    """

    class Meta:
        effect_type = "REORDER_COVERAGE"

    patient_id: str
    ordering: list[CoverageReorderEntry]

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if not Patient.objects.filter(id=self.patient_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Patient with id: {self.patient_id} does not exist.",
                    self.patient_id,
                )
            )

        if not self.ordering:
            errors.append(
                self._create_error_detail(
                    "missing", "Field 'ordering' must contain at least one coverage.", []
                )
            )

        coverage_ids = [str(entry.coverage_id) for entry in self.ordering]
        if len(set(coverage_ids)) != len(coverage_ids):
            errors.append(
                self._create_error_detail(
                    "value", "Field 'ordering' contains the same coverage more than once.", None
                )
            )
        elif CoverageModel.objects.filter(
            id__in=coverage_ids, patient__id=self.patient_id
        ).count() != len(coverage_ids):
            errors.append(
                self._create_error_detail(
                    "value",
                    "Every coverage in 'ordering' must exist and belong to the patient.",
                    coverage_ids,
                )
            )

        ranks_by_stack: dict[str, list[int]] = {}
        for entry in self.ordering:
            ranks_by_stack.setdefault(entry.stack.value, []).append(entry.coverage_rank.value)
        for stack, ranks in ranks_by_stack.items():
            if sorted(ranks) != list(range(1, len(ranks) + 1)):
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Ranks in stack {stack} must be unique and consecutive starting at 1.",
                        sorted(ranks),
                    )
                )

        return errors

    def apply(self) -> Effect:
        """Apply the new ordering."""
        self._validate_before_effect("apply")
        ordering = [
            {
                "coverage_id": str(entry.coverage_id),
                "coverage_rank": entry.coverage_rank.value,
                "stack": entry.stack.value,
            }
            for entry in self.ordering
        ]
        return Effect(
            type=self.Meta.effect_type,
            payload=json.dumps({"data": {"patient_id": self.patient_id, "ordering": ordering}}),
        )


__exports__ = ("Coverage", "CoverageReorder", "CoverageReorderEntry", "PhotoSide")
