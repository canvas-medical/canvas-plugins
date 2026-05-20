import json
from datetime import date
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect
from canvas_sdk.v1.data.coverage import (
    Coverage as CoverageModel,
)
from canvas_sdk.v1.data.coverage import (
    CoverageRank,
    CoverageRelationshipCode,
    CoverageType,
    TransactorCoverageType,
)
from canvas_sdk.v1.data.coverage import (
    CoverageStack as CoverageStackChoice,
)
from canvas_sdk.v1.data.patient import Patient


class CoverageStack(StrEnum):
    """Where in the patient's coverage list this coverage sits."""

    IN_USE = "IN_USE"
    OTHER = "OTHER"
    REMOVED = "REMOVED"


class PhotoSide(StrEnum):
    """Card photo side."""

    FRONT = "FRONT"
    BACK = "BACK"


_PLUGIN_UPLOAD_SEGMENT = "/plugin-uploads/"


def _check_upload_key(key: str | None) -> str | None:
    """Return an error message if the upload key is malformed, else None.

    The S3 keys returned by an ``upload_files=True`` SimpleAPI route always
    contain the segment ``/plugin-uploads/<plugin>/...`` somewhere after the
    customer prefix. We just sanity-check that the segment is present here;
    the platform enforces the *strict* full prefix (customer + plugin) when
    the effect is interpreted.
    """
    if key is None:
        return None
    if _PLUGIN_UPLOAD_SEGMENT not in ("/" + key):
        return (
            f"Card image upload key must contain '{_PLUGIN_UPLOAD_SEGMENT}'. "
            f"Got: {key!r}"
        )
    return None


class Coverage(TrackableFieldsModel):
    """Effect for creating, updating, expiring, removing, or stripping a photo
    from a patient's insurance coverage.

    Card images are attached by passing S3 keys under your plugin's uploads
    prefix (``plugin-uploads/<your-plugin-name>/...``) on
    ``card_image_front_upload_key`` / ``card_image_back_upload_key``.
    Canvas server-side-copies them into the coverage's image storage; no
    bytes pass through your plugin.

    Example (create):
        effect = Coverage(
            patient_id="abc...",
            issuer_id="...",
            coverage_rank=1,
            plan_type=CoverageType.COMMERCIAL,
            id_number="ABC123",
            patient_relationship_to_subscriber=CoverageRelationshipCode.SELF,
            card_image_front_upload_key="plugin-uploads/my_plugin/...front.jpg",
        )
        return [effect.create()]

    Example (update with new back photo only):
        effect = Coverage(
            coverage_id="...",
            card_image_back_upload_key="plugin-uploads/my_plugin/...back.jpg",
        )
        return [effect.update()]
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
    plan_type: CoverageType | None = Field(default=None, strict=False)
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

    def _validate_create(self) -> list[InitErrorDetails]:
        errors: list[InitErrorDetails] = []
        if self.coverage_id is not None:
            errors.append(
                self._create_error_detail(
                    "value",
                    "Field 'coverage_id' must not be set when creating a coverage.",
                    self.coverage_id,
                )
            )
        required_create = {
            "patient_id": self.patient_id,
            "issuer_id": self.issuer_id,
            "coverage_rank": self.coverage_rank,
            "plan_type": self.plan_type,
            "id_number": self.id_number,
            "patient_relationship_to_subscriber": self.patient_relationship_to_subscriber,
        }
        for name, value in required_create.items():
            if value is None or value == "":
                errors.append(
                    self._create_error_detail(
                        "missing",
                        f"Field '{name}' is required to create a coverage.",
                        value,
                    )
                )
        if self.patient_id and not Patient.objects.filter(id=self.patient_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Patient with id {self.patient_id} does not exist.",
                    self.patient_id,
                )
            )
        # When the subscriber is the patient, the platform sets subscriber_id
        # automatically. Reject a mismatched explicit value so the contract
        # is unambiguous.
        if (
            self.patient_relationship_to_subscriber == CoverageRelationshipCode.SELF
            and self.subscriber_id is not None
            and self.subscriber_id != self.patient_id
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    "For SELF relationship, 'subscriber_id' must equal 'patient_id' or be omitted.",
                    self.subscriber_id,
                )
            )
        return errors

    def _validate_coverage_id_required(self, action: str) -> list[InitErrorDetails]:
        errors: list[InitErrorDetails] = []
        if not self.coverage_id:
            errors.append(
                self._create_error_detail(
                    "missing",
                    f"Field 'coverage_id' is required to {action} a coverage.",
                    self.coverage_id,
                )
            )
        elif not CoverageModel.objects.filter(id=self.coverage_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Coverage with id {self.coverage_id} does not exist.",
                    self.coverage_id,
                )
            )
        return errors

    def _validate_upload_keys(self) -> list[InitErrorDetails]:
        errors: list[InitErrorDetails] = []
        for field_name in ("card_image_front_upload_key", "card_image_back_upload_key"):
            err = _check_upload_key(getattr(self, field_name))
            if err:
                errors.append(self._create_error_detail("value", err, getattr(self, field_name)))
        return errors

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if method == "create":
            errors.extend(self._validate_create())
            errors.extend(self._validate_upload_keys())
        elif method == "update":
            errors.extend(self._validate_coverage_id_required("update"))
            errors.extend(self._validate_upload_keys())
        elif method == "expire":
            errors.extend(self._validate_coverage_id_required("expire"))
            if self.coverage_end_date is None:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'coverage_end_date' is required to expire a coverage.",
                        self.coverage_end_date,
                    )
                )
        elif method == "remove":
            errors.extend(self._validate_coverage_id_required("remove"))
        elif method == "remove_photo":
            errors.extend(self._validate_coverage_id_required("remove photo from"))

        return errors

    def create(self) -> Effect:
        """Create a new Coverage."""
        self._validate_before_effect("create")
        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def update(self) -> Effect:
        """Update an existing Coverage. Only fields you set are changed."""
        self._validate_before_effect("update")
        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def expire(self, coverage_end_date: date | None = None) -> Effect:
        """Expire an existing Coverage by setting its end date.

        ``coverage_end_date`` may be passed directly or set on the instance.
        Passing it here overrides any earlier assignment.
        """
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
                        if self.coverage_end_date is not None
                        else None,
                    }
                }
            ),
        )

    def remove(self) -> Effect:
        """Take a Coverage out of the patient's active stack."""
        self._validate_before_effect("remove")
        return Effect(
            type=f"REMOVE_{self.Meta.effect_type}",
            payload=json.dumps({"data": {"coverage_id": str(self.coverage_id)}}),
        )

    def remove_photo(self, side: PhotoSide | str) -> Effect:
        """Clear the front or back card image on this Coverage."""
        side_value = PhotoSide(side) if not isinstance(side, PhotoSide) else side
        self._validate_before_effect("remove_photo")
        return Effect(
            type=f"REMOVE_{self.Meta.effect_type}_PHOTO",
            payload=json.dumps(
                {
                    "data": {
                        "coverage_id": str(self.coverage_id),
                        "side": side_value.value,
                    }
                }
            ),
        )


class CoverageReorder(TrackableFieldsModel):
    """Effect for re-ranking a patient's coverages in one operation.

    Each ``ordering`` entry must contain ``coverage_id``, ``coverage_rank``
    (1-5), and ``stack`` ("IN_USE", "OTHER", or "REMOVED"). Within a stack,
    ranks must be unique and consecutive starting at 1.

    Example::

        CoverageReorder(
            patient_id="abc...",
            ordering=[
                {"coverage_id": "...", "coverage_rank": 1, "stack": "IN_USE"},
                {"coverage_id": "...", "coverage_rank": 2, "stack": "IN_USE"},
            ],
        ).apply()
    """

    class Meta:
        effect_type = "REORDER_COVERAGE"

    patient_id: str | None = None
    ordering: list[dict[str, Any]] | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if method != "apply":
            return errors

        if not self.patient_id:
            errors.append(
                self._create_error_detail(
                    "missing",
                    "Field 'patient_id' is required to reorder coverages.",
                    self.patient_id,
                )
            )
        elif not Patient.objects.filter(id=self.patient_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Patient with id {self.patient_id} does not exist.",
                    self.patient_id,
                )
            )

        if not self.ordering:
            errors.append(
                self._create_error_detail(
                    "missing",
                    "Field 'ordering' is required and must contain at least one entry.",
                    self.ordering,
                )
            )
            return errors

        seen_ids: set[str] = set()
        ranks_by_stack: dict[str, list[int]] = {}
        valid_stacks = {s.value for s in CoverageStackChoice}
        for index, entry in enumerate(self.ordering):
            for required_key in ("coverage_id", "coverage_rank", "stack"):
                if required_key not in entry:
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            f"ordering[{index}] is missing '{required_key}'.",
                            entry,
                        )
                    )
            coverage_id = entry.get("coverage_id")
            if coverage_id is not None:
                if coverage_id in seen_ids:
                    errors.append(
                        self._create_error_detail(
                            "value",
                            f"ordering contains duplicate coverage_id {coverage_id!r}.",
                            coverage_id,
                        )
                    )
                seen_ids.add(coverage_id)
            stack = entry.get("stack")
            rank = entry.get("coverage_rank")
            if stack is not None and stack not in valid_stacks:
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"ordering[{index}].stack must be one of {sorted(valid_stacks)}.",
                        stack,
                    )
                )
            if isinstance(rank, int) and stack in valid_stacks:
                ranks_by_stack.setdefault(stack, []).append(rank)

        for stack, ranks in ranks_by_stack.items():
            sorted_ranks = sorted(ranks)
            if sorted_ranks != list(range(1, len(sorted_ranks) + 1)):
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"ranks for stack {stack!r} must be unique and consecutive "
                        f"starting at 1; got {sorted_ranks}.",
                        ranks,
                    )
                )

        return errors

    def apply(self) -> Effect:
        """Apply the reorder."""
        self._validate_before_effect("apply")
        normalized = [
            {
                "coverage_id": str(entry.get("coverage_id")),
                "coverage_rank": entry.get("coverage_rank"),
                "stack": entry.get("stack"),
            }
            for entry in (self.ordering or [])
        ]
        return Effect(
            type=self.Meta.effect_type,
            payload=json.dumps({"data": {"patient_id": self.patient_id, "ordering": normalized}}),
        )


__exports__ = ("Coverage", "CoverageReorder", "CoverageStack", "PhotoSide")
