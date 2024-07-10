from enum import Enum

from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand


class AssessCommand(_BaseCommand):
    """A class for managing an Assess command within a specific note."""

    class Meta:
        key = "assess"
        originate_required_fields = ("condition_id",)

    class Status(Enum):
        IMPROVED = "improved"
        STABLE = "stable"
        DETERIORATED = "deteriorated"

    condition_id: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "condition"}
    )
    background: str | None = None
    status: Status | None = None
    narrative: str | None = None

    @property
    def values(self) -> dict:
        """The Assess command's field values."""
        return {
            "condition_id": self.condition_id,
            "background": self.background,
            "status": self.status.value if self.status else None,
            "narrative": self.narrative,
        }


# how do we make sure that condition_id is a valid condition for the patient?

# idea1:
# create a class attribute 'pre_validate_condition': bool
#      True: before doing any actions against the home-app instance, will first check
#            if its an active condition for that patient, and it not then logs a message
#            and doesn't do the action. can even create a cache so that we dont always
#            have to keep asking home-app for every patient
#      False: still tries to do it but will run up against whatever home-app barriers
#             we have against actions like that (if those dont already exist, then
#             definitely create them!)


# idea2:
# validator that checks that condition.patient is the same as note.patient
