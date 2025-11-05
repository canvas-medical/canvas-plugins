"""
Example tests demonstrating how to use Canvas SDK factories.

These tests show best practices for using both built-in factories
and custom factories in your tests.
"""

import datetime
from unittest.mock import Mock

from canvas_sdk.test_utils.factories import (
    NoteFactory,
    PatientFactory,
    StaffFactory,
)

# Import your custom factories
# from tests.factories import AppointmentFactory, create_test_appointment_scenario


class TestBuiltInFactories:
    """Examples of using built-in Canvas SDK factories."""

    def test_create_patient_with_defaults(self):
        """Test creating a patient with all default values."""
        patient = PatientFactory.create()

        # Verify patient was created
        assert patient.id is not None

        # Verify auto-generated fields
        assert patient.first_name is not None
        assert patient.last_name is not None
        assert patient.birth_date is not None

        # Verify relationships
        assert patient.user is not None

    def test_create_patient_with_custom_values(self):
        """Test creating a patient with custom values."""
        patient = PatientFactory.create(
            first_name="Alice", last_name="Smith", birth_date=datetime.date(1990, 5, 15)
        )

        assert patient.first_name == "Alice"
        assert patient.last_name == "Smith"
        assert patient.birth_date == datetime.date(1990, 5, 15)

    def test_create_multiple_patients(self):
        """Test creating multiple patients at once."""
        patients = PatientFactory.create_batch(5)

        assert len(patients) == 5
        assert all(p.id is not None for p in patients)

        # Verify they all have different names (thanks to Faker)
        first_names = [p.first_name for p in patients]
        assert len(set(first_names)) > 1  # At least some different names

    def test_create_staff_member(self):
        """Test creating a staff member."""
        staff = StaffFactory.create()

        assert staff.id is not None
        assert staff.first_name is not None
        assert staff.last_name is not None
        assert staff.user is not None

    def test_create_note_with_relationships(self):
        """Test creating a note (which auto-creates related objects)."""
        note = NoteFactory.create()

        # Note automatically creates patient, provider, and location
        assert note.id is not None
        assert note.patient is not None
        assert note.provider is not None
        assert note.location is not None

    def test_create_note_for_specific_patient(self):
        """Test creating a note for a specific patient."""
        # Create patient first
        patient = PatientFactory.create(first_name="Bob", last_name="Jones")

        # Create note for that patient
        note = NoteFactory.create(patient=patient)

        assert note.patient.id == patient.id
        assert note.patient.first_name == "Bob"

    def test_reuse_objects_across_tests(self):
        """Test creating multiple notes for the same patient."""
        patient = PatientFactory.create()
        provider = StaffFactory.create()

        # Create multiple notes for same patient/provider
        note1 = NoteFactory.create(patient=patient, provider=provider)
        note2 = NoteFactory.create(patient=patient, provider=provider)

        assert note1.patient.id == note2.patient.id
        assert note1.provider.id == note2.provider.id
        assert note1.id != note2.id  # But notes are different


class TestFactoriesWithMocks:
    """Examples of combining factories with mocks for protocol testing."""

    def test_protocol_with_factory_data(self):
        """Test a protocol handler using factory data."""
        # Create test data using factories (in-memory only for speed)
        patient = PatientFactory.build(first_name="Carol", birth_date=datetime.date(1975, 3, 20))

        # Create mock event
        mock_event = Mock()
        mock_event.context = {
            "patient": {
                "id": "test-patient-id",
                "first_name": patient.first_name,
                "birth_date": str(patient.birth_date),
            }
        }

        # This would be your actual protocol class
        # protocol = MyProtocol(event=mock_event)
        # effects = protocol.compute()
        # assert len(effects) > 0

        # For this example, just verify our mock setup
        assert mock_event.context["patient"]["first_name"] == "Carol"


class TestFactoryBestPractices:
    """Best practices and patterns for using factories."""

    def test_minimal_overrides(self):
        """Only override fields that matter for the test."""
        # Good: Only override what's relevant
        patient = PatientFactory.create(first_name="TestUser")

        # The test only cares about first_name
        # Everything else uses sensible defaults
        assert patient.first_name == "TestUser"
        assert patient.id is not None

    def test_build_vs_create(self):
        """Use build() when database persistence isn't needed."""
        # build() creates in-memory object (faster)
        patient_memory = PatientFactory.build(first_name="Memory")

        # Note: Some models like Patient may auto-generate IDs even with build()
        # The main benefit is that build() doesn't persist relationships to DB
        assert patient_memory.first_name == "Memory"

        # create() saves to database with all relationships
        patient_db = PatientFactory.create(first_name="Database")

        assert patient_db.id is not None
        assert patient_db.first_name == "Database"

    def test_related_objects_pattern(self):
        """Pattern for creating objects with relationships."""
        # Create shared objects
        patient = PatientFactory.create()
        provider = StaffFactory.create()

        # Use them in multiple contexts
        note1 = NoteFactory.create(patient=patient, provider=provider)
        note2 = NoteFactory.create(patient=patient, provider=provider)

        # Both notes share the same patient and provider
        assert note1.patient.id == note2.patient.id
        assert note1.provider.id == note2.provider.id


class TestFactoryScenarios:
    """Real-world testing scenarios using factories."""

    def test_patient_with_multiple_notes(self):
        """Test scenario with patient who has multiple notes."""
        # Setup: Create a patient with multiple notes
        patient = PatientFactory.create(first_name="Emma")
        provider = StaffFactory.create()

        notes = [NoteFactory.create(patient=patient, provider=provider) for _ in range(3)]

        # Test: Verify patient has notes
        assert len(notes) == 3
        assert all(note.patient.id == patient.id for note in notes)

    def test_provider_with_multiple_patients(self):
        """Test scenario with provider who has multiple patients."""
        # Setup: Create a provider with multiple patients
        provider = StaffFactory.create()
        patients = PatientFactory.create_batch(5)

        notes = [NoteFactory.create(patient=patient, provider=provider) for patient in patients]

        # Test: Verify all notes have same provider
        assert len(notes) == 5
        assert all(note.provider.id == provider.id for note in notes)

    def test_age_based_logic(self):
        """Test logic that depends on patient age."""
        # Create pediatric patient (8 years old)
        pediatric_dob = datetime.date.today() - datetime.timedelta(days=8 * 365)
        pediatric_patient = PatientFactory.create(birth_date=pediatric_dob)

        # Create adult patient (40 years old)
        adult_dob = datetime.date.today() - datetime.timedelta(days=40 * 365)
        adult_patient = PatientFactory.create(birth_date=adult_dob)

        # Calculate ages
        today = datetime.date.today()
        pediatric_age = (today - pediatric_patient.birth_date).days // 365
        adult_age = (today - adult_patient.birth_date).days // 365

        assert pediatric_age < 18
        assert adult_age >= 18


class TestCustomFactories:
    """Examples using custom factories."""

    def test_appointment_factory(self):
        """Test using custom AppointmentFactory."""
        from tests.factories import AppointmentFactory

        appointment = AppointmentFactory.create()

        assert appointment.id is not None
        assert appointment.patient is not None
        assert appointment.provider is not None
        assert appointment.duration_minutes in [15, 30, 45, 60]
        assert appointment.status in ["unconfirmed", "confirmed", "arrived", "roomed"]

    def test_appointment_with_custom_values(self):
        """Test appointment with custom duration and status."""
        from tests.factories import AppointmentFactory

        patient = PatientFactory.create()
        appointment = AppointmentFactory.create(
            patient=patient, duration_minutes=60, status="confirmed"
        )

        assert appointment.patient.id == patient.id
        assert appointment.duration_minutes == 60
        assert appointment.status == "confirmed"

    def test_complete_scenario(self):
        """Test using the helper function for complete scenarios."""
        from tests.factories import create_test_appointment_scenario

        scenario = create_test_appointment_scenario()

        assert scenario["patient"] is not None
        assert scenario["provider"] is not None
        assert scenario["location"] is not None
        assert scenario["appointment"] is not None

        # Verify relationships
        assert scenario["appointment"].patient.id == scenario["patient"].id
        assert scenario["appointment"].provider.id == scenario["provider"].id
