from canvas_sdk.v1.data import ModelExtension, Note, Patient, Staff, proxy_field


class StaffProxy(Staff, ModelExtension):
    """Staff with a display_name property."""

    @property
    def display_name(self) -> str:
        """Return 'first last' formatted name."""
        return f"{self.first_name} {self.last_name}"


class PatientProxy(Patient, ModelExtension):
    """Patient with a display_name property."""

    @property
    def display_name(self) -> str:
        """Return 'first last' formatted name."""
        return f"{self.first_name} {self.last_name}"


class NoteProxy(Note, ModelExtension):
    """Proxy for Note that returns proxy instances from FK traversal."""

    patient = proxy_field(PatientProxy)
    provider = proxy_field(StaffProxy)
