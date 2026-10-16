import json
from datetime import date, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect
from canvas_sdk.effects._field_errors import (
    blank_field_errors,
    existing_record_errors,
    upload_key_errors,
)
from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data.coverage import Coverage as CoverageModel
from canvas_sdk.v1.data.coverage import (
    CoverageRank,
    CoverageRelationshipCode,
    CoverageStack,
    Transactor,
    TransactorAddress,
    TransactorCoverageType,
    TransactorPhone,
)
from canvas_sdk.v1.data.patient import Patient
from settings import INSTALLATION_TIME_ZONE

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

# Fields that may be omitted but, when set, never hold None or an empty string.
NON_BLANK_FIELDS: tuple[str, ...] = (
    "issuer_id",
    "coverage_rank",
    "id_number",
    "patient_relationship_to_subscriber",
    "stack",
    "subscriber_id",
    "coverage_start_date",
)


def _today() -> date:
    """Today's date where the practice is, as Canvas counts it."""
    return datetime.now(ZoneInfo(INSTALLATION_TIME_ZONE)).date()


def _date_order_errors(
    model: TrackableFieldsModel,
    start: date | None,
    end: date | None,
) -> list[InitErrorDetails]:
    """Return an error when the coverage would end before it starts."""
    if start and end and start > end:
        return [
            model._create_error_detail(
                "value",
                "The coverage start date must be on or before its end date.",
                end,
            )
        ]
    return []


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
    Changing the payer clears the payer address, phone and coverage type unless new ones
    are set in the same update.

    On update, only the fields you set are changed, and setting an optional field to
    ``None`` clears it. Use ``remove()`` to move a coverage to the removed stack.

    Example (create):
        from canvas_sdk.v1.data.coverage import CoverageRank, CoverageRelationshipCode

        Coverage(
            patient_id="patient-id",
            issuer_id=payer.id,
            coverage_rank=CoverageRank.PRIMARY,
            id_number="ABC123",
            patient_relationship_to_subscriber=CoverageRelationshipCode.SELF,
            card_image_front_upload_key=front_part.key,
            card_image_back_upload_key=back_part.key,
        ).create()

    Example (update the back of the card only):
        Coverage(coverage_id=coverage.id, card_image_back_upload_key=part.key).update()

    Example (expire):
        Coverage(coverage_id=coverage.id).expire(coverage_end_date=date(2026, 12, 31))
    """

    model_config = ConfigDict(extra="forbid")

    class Meta:
        effect_type = "COVERAGE"
        create_required_fields = (
            "patient_id",
            "issuer_id",
            "coverage_rank",
            "id_number",
            "patient_relationship_to_subscriber",
        )
        expire_required_fields = ("coverage_end_date",)

    coverage_id: UUID | None = Field(default=None, strict=False)
    patient_id: str | None = None

    issuer_id: UUID | None = Field(default=None, strict=False)
    issuer_address_id: UUID | None = Field(default=None, strict=False)
    issuer_phone_id: UUID | None = Field(default=None, strict=False)

    subscriber_id: str | None = None
    patient_relationship_to_subscriber: CoverageRelationshipCode | None = Field(
        default=None, strict=False
    )
    subscriber_identifier: str | None = Field(default=None, max_length=100)

    coverage_rank: CoverageRank | None = Field(default=None, strict=False)
    coverage_type: TransactorCoverageType | None = Field(default=None, strict=False)
    stack: CoverageStack | None = Field(default=None, strict=False)

    id_number: str | None = Field(default=None, max_length=100)
    plan: str | None = Field(default=None, max_length=255)
    sub_plan: str | None = Field(default=None, max_length=255)
    group: str | None = Field(default=None, max_length=255)
    sub_group: str | None = Field(default=None, max_length=255)
    employer: str | None = Field(default=None, max_length=255)
    coverage_start_date: date | None = None
    coverage_end_date: date | None = None
    comments: str | None = None

    card_image_front_upload_key: str | None = None
    card_image_back_upload_key: str | None = None

    def _existing(self) -> CoverageModel | None:
        """Return the coverage being updated, if it exists."""
        if self.coverage_id is None:
            return None
        return (
            CoverageModel.objects.select_related(
                "patient",
                "subscriber",
                "issuer",
            )
            .filter(id=self.coverage_id)
            .first()
        )

    def _pick(
        self,
        field: str,
        existing: Any,
    ) -> Any:
        """Return the value set for ``field``, or the stored value when it was not set."""
        return getattr(self, field) if self.is_dirty(field) else existing

    def _write_errors(self, existing: CoverageModel | None) -> list[InitErrorDetails]:
        """Errors shared by create and update; ``existing`` is the coverage being updated."""
        errors = blank_field_errors(self, NON_BLANK_FIELDS)
        errors += upload_key_errors(
            self,
            "card_image_front_upload_key",
            "card_image_back_upload_key",
        )

        if self.stack == CoverageStack.REMOVED:
            errors.append(
                self._create_error_detail(
                    "value", "Use remove() to move a coverage to the removed stack.", self.stack
                )
            )

        issuer_id = self._pick(
            "issuer_id", existing.issuer.id if existing and existing.issuer else None
        )
        errors += existing_record_errors(self, "issuer_id", Transactor.objects, "payer")
        for field, contacts in (
            ("issuer_address_id", TransactorAddress.objects),
            ("issuer_phone_id", TransactorPhone.objects),
        ):
            value = getattr(self, field)
            if value and not contacts.filter(id=value, transactor__id=issuer_id).exists():
                errors.append(
                    self._create_error_detail(
                        "value", f"Field '{field}' must belong to the coverage's payer.", value
                    )
                )

        patient_id = existing.patient.id if existing and existing.patient else self.patient_id
        relationship = self._pick(
            "patient_relationship_to_subscriber",
            existing.patient_relationship_to_subscriber if existing else None,
        )
        subscriber_id = self._pick(
            "subscriber_id", existing.subscriber.id if existing and existing.subscriber else None
        )
        errors += existing_record_errors(self, "subscriber_id", Patient.objects, "patient")
        if relationship == CoverageRelationshipCode.SELF:
            if self.subscriber_id and self.subscriber_id != patient_id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Field 'subscriber_id' must be omitted or equal the patient when the "
                        "patient is the subscriber.",
                        self.subscriber_id,
                    )
                )
        elif relationship is not None and (not subscriber_id or subscriber_id == patient_id):
            errors.append(
                self._create_error_detail(
                    "value",
                    "Field 'subscriber_id' must name someone other than the patient when the "
                    "patient is not the subscriber.",
                    subscriber_id,
                )
            )

        # A new coverage without a start date starts today.
        start = self._pick(
            "coverage_start_date", existing.coverage_start_date if existing else _today()
        )
        end = self._pick("coverage_end_date", existing.coverage_end_date if existing else None)
        return errors + _date_order_errors(self, start, end)

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
            errors += existing_record_errors(self, "patient_id", Patient.objects, "patient")
            stack = self.stack or CoverageStack.IN_USE
            if (
                self.coverage_rank
                and CoverageModel.objects.filter(
                    patient__id=self.patient_id, coverage_rank=self.coverage_rank, stack=stack
                )
                .exclude(coverage_end_date__lt=_today())
                .exists()
            ):
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"The patient already has an active {stack} coverage with rank "
                        f"{self.coverage_rank}.",
                        self.coverage_rank,
                    )
                )
            errors.extend(self._write_errors(None))

        elif method == "update":
            errors.extend(
                existing_record_errors(
                    self,
                    "coverage_id",
                    CoverageModel.objects,
                    "coverage",
                    method,
                )
            )
            if self.is_dirty("patient_id"):
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Field 'patient_id' cannot be changed on an existing coverage.",
                        self.patient_id,
                    )
                )
            errors.extend(self._write_errors(self._existing()))

        elif method in ("expire", "remove", "remove_photo"):
            action = "remove a card image from" if method == "remove_photo" else method
            errors.extend(
                existing_record_errors(
                    self,
                    "coverage_id",
                    CoverageModel.objects,
                    "coverage",
                    action,
                )
            )
            if method == "expire" and (existing := self._existing()):
                errors += _date_order_errors(
                    self,
                    existing.coverage_start_date,
                    self.coverage_end_date,
                )

        return errors

    def create(self) -> Effect:
        """Create a new coverage."""
        self._validate_before_effect("create")
        data = {"patient_id": self.patient_id, **self.values_for(WRITABLE_FIELDS)}
        return Effect(type=f"CREATE_{self.Meta.effect_type}", payload=json.dumps({"data": data}))

    def update(self) -> Effect:
        """Update an existing coverage, changing only the fields that were set."""
        self._validate_before_effect("update")
        data = {"coverage_id": str(self.coverage_id), **self.values_for(WRITABLE_FIELDS)}
        return Effect(type=f"UPDATE_{self.Meta.effect_type}", payload=json.dumps({"data": data}))

    def expire(self, coverage_end_date: date | None = None) -> Effect:
        """Expire an existing coverage by setting its end date."""
        if coverage_end_date is not None:
            self.coverage_end_date = coverage_end_date
        self._validate_before_effect("expire")
        assert self.coverage_end_date is not None
        data = {
            "coverage_id": str(self.coverage_id),
            "coverage_end_date": self.coverage_end_date.isoformat(),
        }
        return Effect(type=f"EXPIRE_{self.Meta.effect_type}", payload=json.dumps({"data": data}))

    def remove(self) -> Effect:
        """Move an existing coverage to the removed stack."""
        self._validate_before_effect("remove")
        data = {"coverage_id": str(self.coverage_id)}
        return Effect(type=f"REMOVE_{self.Meta.effect_type}", payload=json.dumps({"data": data}))

    def remove_photo(self, side: PhotoSide) -> Effect:
        """Remove the front or back card file from an existing coverage."""
        try:
            side = PhotoSide(side)
        except ValueError:
            raise ValidationError.from_exception_data(
                self.__class__.__name__,
                [self._create_error_detail("value", "Field 'side' must be FRONT or BACK.", side)],
            ) from None
        self._validate_before_effect("remove_photo")
        data = {"coverage_id": str(self.coverage_id), "side": side}
        return Effect(
            type=f"REMOVE_{self.Meta.effect_type}_PHOTO", payload=json.dumps({"data": data})
        )


class CoverageReorderEntry(BaseModel):
    """The new position of one coverage in a ``CoverageReorder``."""

    model_config = ConfigDict(validate_assignment=True)

    coverage_id: UUID
    coverage_rank: CoverageRank
    stack: CoverageStack


class CoverageReorder(_BaseEffect):
    """
    Effect to set the rank and stack of several of a patient's coverages at once.

    Within each stack, ranks must be unique and consecutive starting at 1, and the ordering
    must list every active coverage of each stack it places a coverage in. Use
    ``Coverage.remove()`` to move a coverage to the removed stack.

    Example:
        from canvas_sdk.v1.data.coverage import CoverageStack

        CoverageReorder(
            patient_id="patient-id",
            ordering=[
                CoverageReorderEntry(coverage_id=a.id, coverage_rank=1, stack=CoverageStack.IN_USE),
                CoverageReorderEntry(coverage_id=b.id, coverage_rank=2, stack=CoverageStack.IN_USE),
            ],
        ).apply()
    """

    class Meta:
        effect_type = EffectType.REORDER_COVERAGE

    patient_id: str
    ordering: list[CoverageReorderEntry] = Field(min_length=1)

    @property
    def values(self) -> dict[str, Any]:
        """The patient and each coverage's new rank and stack."""
        return {
            "patient_id": self.patient_id,
            "ordering": [entry.model_dump(mode="json") for entry in self.ordering],
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        errors += existing_record_errors(self, "patient_id", Patient.objects, "patient")

        coverage_ids = [entry.coverage_id for entry in self.ordering]
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
                    [str(coverage_id) for coverage_id in coverage_ids],
                )
            )

        ranks_by_stack: dict[str, list[int]] = {}
        for entry in self.ordering:
            ranks_by_stack.setdefault(entry.stack.value, []).append(entry.coverage_rank.value)
        if CoverageStack.REMOVED.value in ranks_by_stack:
            errors.append(
                self._create_error_detail(
                    "value", "Use Coverage.remove() to move a coverage to the removed stack.", None
                )
            )
        today = _today()
        unlisted = (
            CoverageModel.objects.filter(
                patient__id=self.patient_id,
                stack__in=ranks_by_stack,
                coverage_start_date__lte=today,
            )
            .exclude(coverage_end_date__lt=today)
            .exclude(id__in=coverage_ids)
        )
        if unlisted.exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    "Field 'ordering' must list every active coverage of each stack it places "
                    "a coverage in.",
                    sorted(
                        str(coverage_id) for coverage_id in unlisted.values_list("id", flat=True)
                    ),
                )
            )
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


__exports__ = ("Coverage", "CoverageReorder", "CoverageReorderEntry", "PhotoSide")
