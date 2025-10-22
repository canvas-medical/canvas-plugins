"""
Custom test factories for example-plugins.

This module contains custom factories for models that don't have built-in
factories in canvas_sdk.test_utils.factories.

Usage:
    from tests.factories import AppointmentFactory

    appointment = AppointmentFactory.create()
"""

import datetime

import factory
from factory.fuzzy import FuzzyChoice

from canvas_sdk.test_utils.factories import (
    PatientFactory,
    PracticeLocationFactory,
    StaffFactory,
)
from canvas_sdk.v1.data.appointment import Appointment


class AppointmentFactory(factory.django.DjangoModelFactory[Appointment]):
    """Factory for creating test Appointments.

    Example:
        # Create with default values
        appointment = AppointmentFactory.create()

        # Create with custom patient
        patient = PatientFactory.create(first_name="Alice")
        appointment = AppointmentFactory.create(patient=patient)

        # Create with specific duration and status
        appointment = AppointmentFactory.create(
            duration_minutes=60,
            status='confirmed'
        )
    """

    class Meta:  # type: ignore[misc]
        model = Appointment

    # Required relationships
    patient = factory.SubFactory(PatientFactory)
    provider = factory.SubFactory(StaffFactory)
    location = factory.SubFactory(PracticeLocationFactory)

    # Required: Date/time fields - appointment is 7 days in the future by default
    start_time = factory.LazyFunction(
        lambda: datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=7)
    )

    # Required: Common appointment durations (in minutes)
    duration_minutes = FuzzyChoice([15, 30, 45, 60])

    # Required: Status field with valid choices
    # Choices: unconfirmed, attempted, confirmed, arrived, roomed, exited, noshowed, cancelled
    status = FuzzyChoice(["unconfirmed", "confirmed", "arrived", "roomed"])

    # Required: Boolean field for telehealth instructions
    telehealth_instructions_sent = False

    # Optional string fields
    comment = factory.Faker("sentence", nb_words=6)


# Example factories for demonstration purposes only
# These are commented out because the models don't exist in the test environment
# Uncomment and adapt these when you need to create factories for similar models

# class TaskFactory(factory.django.DjangoModelFactory):
#     """Factory for creating test Tasks.
#
#     Example:
#         # Create a task
#         task = TaskFactory.create()
#
#         # Create a task with specific patient and title
#         patient = PatientFactory.create()
#         task = TaskFactory.create(
#             patient=patient,
#             title="Review lab results"
#         )
#     """
#
#     class Meta:
#         model = "v1.Task"
#
#     title = factory.Faker("sentence", nb_words=5)
#     patient = factory.SubFactory(PatientFactory)
#     assigned_to = factory.SubFactory(StaffFactory)
#     created_by = factory.SubFactory(StaffFactory)
#     status = FuzzyChoice(["OPEN", "IN_PROGRESS", "COMPLETED", "CANCELLED"])
#     due_date = factory.LazyFunction(
#         lambda: datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=3)
#     )


# Example of a factory with post-generation hooks (commented out)
# class LabReportFactory(factory.django.DjangoModelFactory):
#     """Factory for creating test Lab Reports.
#
#     This is an example showing how to use post-generation hooks
#     to create related objects.
#
#     Example:
#         # Create a lab report with default values
#         report = LabReportFactory.create()
#
#         # Create a lab report with specific number of values
#         report = LabReportFactory.create(value_count=5)
#     """
#
#     class Meta:
#         model = "v1.LabReport"
#
#     patient = factory.SubFactory(PatientFactory)
#     for_test_only = False
#     junked = False
#
#     @factory.post_generation
#     def create_lab_values(self, create, extracted, **kwargs):
#         """Create lab values after the report is created."""
#         if not create:
#             return
#         # Uncomment and implement when LabValueFactory is available:
#         # count = extracted if extracted is not None else 3
#         # for i in range(count):
#         #     LabValueFactory.create(report=self, ...)


# Example of a factory with lazy attributes (commented out)
# class PrescriptionFactory(factory.django.DjangoModelFactory):
#     """Factory for creating test Prescriptions.
#
#     This shows how to use LazyAttribute for dependent fields.
#
#     Example:
#         # Create prescription
#         prescription = PrescriptionFactory.create()
#
#         # The sig will automatically reference the medication name
#         print(prescription.sig)  # e.g., "Take Lisinopril 10mg once daily"
#     """
#
#     class Meta:
#         model = "v1.Prescription"
#
#     patient = factory.SubFactory(PatientFactory)
#     prescriber = factory.SubFactory(StaffFactory)
#     medication_name = factory.Faker(
#         "random_element", elements=["Lisinopril", "Metformin", "Amlodipine", "Atorvastatin"]
#     )
#     dosage = factory.LazyAttribute(lambda obj: f"{obj.medication_name} 10mg")
#     sig = factory.LazyAttribute(lambda obj: f"Take {obj.dosage} once daily")
#     quantity = FuzzyInteger(30, 90)
#     refills = FuzzyChoice([0, 1, 3, 6, 11])


# Example of factory with sequences for unique values (commented out - Patient doesn't have these fields)
# class ExternalSystemPatientFactory(PatientFactory):
#     """Factory for patients with external system identifiers.
#
#     This extends PatientFactory to add unique external IDs.
#
#     Example:
#         # Create patients with unique external IDs
#         patient1 = ExternalSystemPatientFactory.create()
#         patient2 = ExternalSystemPatientFactory.create()
#
#         # patient1.external_id will be "EXT-0001"
#         # patient2.external_id will be "EXT-0002"
#     """
#
#     external_id = factory.Sequence(lambda n: f"EXT-{n:04d}")
#     mrn = factory.Sequence(lambda n: f"MRN{n:06d}")


# Helper function to create complete test scenarios
def create_test_appointment_scenario():
    """Create a complete appointment scenario for testing.

    Returns a dictionary with all related objects:
        {
            'patient': Patient instance,
            'provider': Staff instance,
            'location': PracticeLocation instance,
            'appointment': Appointment instance
        }

    Example:
        scenario = create_test_appointment_scenario()
        appointment = scenario['appointment']
        patient = scenario['patient']
    """
    patient = PatientFactory.create(
        first_name="Test", last_name="Patient", birth_date=datetime.date(1980, 1, 1)
    )

    provider = StaffFactory.create(first_name="Dr.", last_name="Provider")

    location = PracticeLocationFactory.create()

    appointment = AppointmentFactory.create(
        patient=patient,
        provider=provider,
        location=location,
        start_time=datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1),
        duration_minutes=30,
    )

    return {
        "patient": patient,
        "provider": provider,
        "location": location,
        "appointment": appointment,
    }
