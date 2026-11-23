from enum import StrEnum
from typing import NoReturn

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand, _OptionalId
from canvas_sdk.effects import Effect
from canvas_sdk.v1.data import RefillRequest

# Surescripts carries at most 70 printable ASCII characters in a note to the pharmacist.
_NOTE_TO_PHARMACIST_MAX_LENGTH = 70
_PRINTABLE_ASCII = r"^[ -~]*$"


class _RefillResponseCommand(_BaseCommand):
    """A staged answer to a pharmacy's refill request.

    The medication, quantity, sig and pharmacy come from the refill request. A plugin can start,
    edit and delete the card, and only the provider can send it to the pharmacy, from the card.
    """

    class Meta:
        key = ""
        abstract = True
        originate_required_fields = ("refill_request_id",)

    refill_request_id: _OptionalId = None
    note_to_pharmacist: str | None = Field(
        default=None, max_length=_NOTE_TO_PHARMACIST_MAX_LENGTH, pattern=_PRINTABLE_ASCII
    )

    def _get_error_details(self, method: str) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.refill_request_id is None:
            return errors

        request_patient_id = (
            RefillRequest.objects.filter(id=self.refill_request_id)
            .values_list("patient__id", flat=True)
            .first()
        )

        if request_patient_id is None or not self._is_target_patient(request_patient_id):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Refill request {self.refill_request_id} does not belong to this command's patient",
                    self.refill_request_id,
                )
            )

        return errors

    def _not_supported(self, what: str) -> NoReturn:
        raise ValueError(
            f"{type(self).__name__} cannot {what}: the provider sends it to the pharmacy from the card."
        )

    def originate(self, line_number: int = -1, commit: bool = False) -> Effect:
        """Originate the response in the note body, staged for the provider to send."""
        if commit:
            self._not_supported("be committed")

        return super().originate(line_number=line_number)

    def edit(self) -> Effect:
        """Edit the note to the pharmacist (and, for a denial, the reason) on an unsent card."""
        if self.is_dirty("refill_request_id"):
            raise ValueError(
                "refill_request_id cannot be changed. Delete the card and start a new one."
            )

        return super().edit()

    def commit(self) -> Effect:
        """Refused: only the provider commits a refill response, by sending it from the card."""
        self._not_supported("be committed")

    def enter_in_error(self) -> Effect:
        """Refused: a refill response is never entered in error by a plugin."""
        self._not_supported("be entered in error")

    def set_custom_html(self, custom_html: str | None) -> Effect:
        """Refused: a plugin cannot change what the provider sees on the card."""
        self._not_supported("carry custom HTML")

    def recommendation_context(self) -> dict:
        """Protocol cards insert commands outside the plugin effect path, so they cannot carry one."""
        self._not_supported("be recommended in a protocol card")


class ApproveRefillCommand(_RefillResponseCommand):
    """Approve a pharmacy's refill request."""

    class Meta(_RefillResponseCommand.Meta):
        key = "approveRefill"
        abstract = False


class DenyRefillCommand(_RefillResponseCommand):
    """Deny a pharmacy's refill request."""

    class Meta(_RefillResponseCommand.Meta):
        key = "denyRefill"
        abstract = False

    class Reason(StrEnum):
        """NCPDP SCRIPT denial reasons."""

        PATIENT_UNKNOWN_TO_PRESCRIBER = "AA"
        PATIENT_NEVER_UNDER_PROVIDER_CARE = "AB"
        PATIENT_NO_LONGER_UNDER_PROVIDER_CARE = "AC"
        REFILL_TOO_SOON = "AD"
        MEDICATION_NEVER_PRESCRIBED = "AE"
        PATIENT_SHOULD_CONTACT_PROVIDER = "AF"
        REFILL_NOT_APPROPRIATE = "AG"
        PATIENT_PICKED_UP_PRESCRIPTION = "AH"
        PATIENT_PICKED_UP_PARTIAL_FILL = "AJ"
        NOT_PICKED_UP_RETURNED_TO_STOCK = "AK"
        PATIENT_NEEDS_APPOINTMENT = "AM"
        PRESCRIBER_NOT_AT_PRACTICE = "AN"
        NO_PRIOR_AUTHORIZATION_ATTEMPT = "AO"
        RESPONDED_BY_OTHER_MEANS = "AP"

    reason_code: Reason | None = None


__exports__ = ("ApproveRefillCommand", "DenyRefillCommand")
