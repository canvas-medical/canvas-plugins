from typing import Any

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects import Effect
from canvas_sdk.effects.base import _BaseEffect
from canvas_sdk.v1.data.application import Application


class ApplicationNotificationBadge:
    """Fluent builder for updating an Application's notification badge.

    Usage:
        ApplicationNotificationBadge("my_plugin__inbox").broadcast(count=3, staff_ids=["s-1"])
        ApplicationNotificationBadge("my_plugin__inbox").filter(patient_ids=["p-1"]).broadcast(count=5)
        ApplicationNotificationBadge("my_plugin__inbox").broadcast(count=0)  # clears for everyone

    Call ``.broadcast(...)`` to emit the badge update as an ``Effect``. ``.filter(...)``
    is optional and chains before ``.broadcast(...)`` to target patient recipients.

    When both ``staff_ids`` (passed to ``.broadcast``) and ``patient_ids`` (set via
    ``.filter``) are empty, the update is broadcast to every connected user.
    """

    application_identifier: str
    _filters: dict[str, Any] = {}

    def __init__(self, application_identifier: str) -> None:
        """Bind this builder to the target application's identifier.

        ``application_identifier`` must match the ``class`` string declared for the
        application in ``CANVAS_MANIFEST.json`` (and the runtime
        ``Application.identifier`` produced by the SDK base class).
        """
        self.application_identifier = application_identifier

    def filter(self, *, patient_ids: list[str] | None = None) -> "ApplicationNotificationBadge":
        """Restrict the broadcast to specific patient recipients.

        ``patient_ids``: list of patient keys that should receive the badge update.
        The keys must be patient externally-exposable identifiers (matching the SDK's
        ``Patient.id`` convention).

        Returns ``self`` so the call chains into ``.broadcast(...)``.
        """
        filters = {}
        if patient_ids is not None:
            filters["patient_ids"] = patient_ids
        self._filters = filters
        return self

    def broadcast(self, count: int, staff_ids: list[str] | None = None) -> Effect:
        """Emit the badge update as an ``Effect``.

        ``count``: the new badge value. Must be ``>= 0``; ``0`` clears the badge.

        ``staff_ids``: list of staff keys that should receive the update. Combined
        with any ``patient_ids`` previously set via ``.filter(...)``. When both
        lists are empty/omitted, the update is broadcast to every connected user
        (the home-app ``applications.badge.all_users`` channel).

        Returns the wrapped ``Effect`` ready to be appended to a handler's
        ``compute()`` return value.
        """
        return _SetApplicationNotificationBadge(
            application_identifier=self.application_identifier,
            count=count,
            patient_ids=self._filters.get("patient_ids") or [],
            staff_ids=staff_ids or [],
        ).apply()


class _SetApplicationNotificationBadge(_BaseEffect):
    """Internal effect model produced by ``ApplicationNotificationBadge.broadcast``.

    Not part of the public SDK surface; plugin authors should always go through
    the ``ApplicationNotificationBadge`` builder. This class only exists to
    serialize the payload into the protobuf ``Effect`` consumed by home-app.
    """

    class Meta:
        effect_type = EffectType.SET_APPLICATION_NOTIFICATION_BADGE

    application_identifier: str = Field(min_length=1)
    count: int = Field(ge=0)
    staff_ids: list[str] = Field(default_factory=list)
    patient_ids: list[str] = Field(default_factory=list)

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Reject identifiers that don't match an installed Application row."""
        errors = super()._get_error_details(method)

        if (
            self.application_identifier
            and not Application.objects.filter(identifier=self.application_identifier).exists()
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Application '{self.application_identifier}' not found.",
                    self.application_identifier,
                )
            )

        return errors

    @property
    def values(self) -> dict[str, Any]:
        """Serialize this effect's targeting + count into the JSON payload shape."""
        return {
            "application_identifier": self.application_identifier,
            "count": self.count,
            "staff_ids": self.staff_ids,
            "patient_ids": self.patient_ids,
        }


__exports__ = ("ApplicationNotificationBadge",)
