"""
Request Context Model.

Encapsulates all context information for PDMP requests to eliminate parameter passing hell.
"""


class RequestContext:
    """
    Encapsulates all context information for a PDMP request.

    This replaces passing multiple parameters (patient_id, practitioner_id, etc.)
    across multiple method calls, reducing coupling and improving maintainability.
    """

    def __init__(
        self,
        patient_id: str,
        practitioner_id: str | None = None,
        organization_id: str | None = None,
        practice_location_id: str | None = None,
        staff_id: str | None = None,
        note_id: str | None = None,
    ):
        """
        Initialize request context.

        Args:
            patient_id: Canvas patient ID (required)
            practitioner_id: Canvas practitioner/staff ID
            organization_id: Canvas organization ID
            practice_location_id: Canvas practice location ID
            staff_id: Staff ID used for credential resolution (optional)
            note_id: Associated note ID if request originated from a note
        """
        self.patient_id = patient_id
        self.practitioner_id = practitioner_id
        self.organization_id = organization_id
        self.practice_location_id = practice_location_id
        self.staff_id = staff_id
        self.note_id = note_id

    @property
    def env_label(self) -> str:
        """Deprecated – kept for compatibility, always 'production'."""
        return "production"

    @property
    def env_code(self) -> str:
        """Deprecated – kept for compatibility, always 'prod'."""
        return "prod"

    def __repr__(self) -> str:
        """String representation for logging."""
        return (
            f"RequestContext(patient_id={self.patient_id}, "
            f"practitioner_id={self.practitioner_id}, "
            f"organization_id={self.organization_id}, "
            f"env={self.env_label})"
        )
