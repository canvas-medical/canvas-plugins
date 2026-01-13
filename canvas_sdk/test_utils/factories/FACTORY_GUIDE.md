# Canvas SDK Factory Guide

This guide explains how to use the existing Canvas SDK test factories and how to create your own custom factories.

## Available Factories

The Canvas SDK provides the following built-in factories in `canvas_sdk.test_utils.factories`:

### Core Entity Factories
- **PatientFactory** - Creates test patient records
- **StaffFactory** - Creates staff/provider records
- **CanvasUserFactory** (UserFactory) - Creates user accounts
- **OrganizationFactory** - Creates organization entities
- **FacilityFactory** - Creates healthcare facilities
- **PracticeLocationFactory** - Creates practice locations

### Clinical Data Factories
- **NoteFactory** - Creates clinical notes (automatically creates initial state)
- **ClaimFactory** - Creates insurance claims
- **ClaimDiagnosisCodeFactory** - Creates diagnosis codes for claims
- **MedicationHistoryMedicationFactory** - Creates medication history records
- **ProtocolCurrentFactory** - Creates protocol instances

### Related Factories
- **PatientAddressFactory** - Creates patient addresses
- **StaffAddressFactory** - Creates staff addresses
- **StaffContactPointFactory** - Creates staff contact info
- **StaffLicenseFactory** - Creates staff licenses
- **StaffRoleFactory** - Creates staff role assignments
- **NoteStateChangeEventFactory** - Creates note state change events

## Using Existing Factories

### Basic Usage

```python
from canvas_sdk.test_utils.factories import PatientFactory, StaffFactory, NoteFactory

def test_example():
    # Create a patient with random data
    patient = PatientFactory.create()

    # Access generated fields
    assert patient.first_name is not None
    assert patient.last_name is not None
    assert patient.birth_date is not None

    # Patient automatically has a user account
    assert patient.user is not None
```

### Customizing Factory Data

```python
def test_with_custom_data():
    # Override specific fields
    patient = PatientFactory.create(
        first_name="John",
        last_name="Doe",
        birth_date=datetime.date(1980, 1, 1)
    )

    assert patient.first_name == "John"
    assert patient.last_name == "Doe"
```

### Creating Multiple Instances

```python
def test_multiple_patients():
    # Create 5 patients at once
    patients = PatientFactory.create_batch(5)

    assert len(patients) == 5
    assert all(p.id is not None for p in patients)
```

### Using Factories with Related Objects

```python
def test_note_with_patient():
    # Create a note (automatically creates patient, provider, and location)
    note = NoteFactory.create()

    assert note.patient is not None
    assert note.provider is not None
    assert note.location is not None

    # Note automatically has initial state
    assert note.state == NoteStates.NEW
```

### Creating Related Objects Together

```python
def test_note_for_specific_patient():
    # Create a patient first
    patient = PatientFactory.create(first_name="Jane")

    # Create a note for that specific patient
    note = NoteFactory.create(patient=patient)

    assert note.patient.first_name == "Jane"
```

## Creating Custom Factories

### Basic Custom Factory

Here's how to create a custom factory for a model that doesn't have one yet:

```python
import factory
from factory.fuzzy import FuzzyDate, FuzzyChoice
import datetime

from canvas_sdk.v1.data.appointment import Appointment as AppointmentData
from canvas_sdk.test_utils.factories import PatientFactory, StaffFactory, PracticeLocationFactory


class AppointmentFactory(factory.django.DjangoModelFactory):
    """Factory for creating test Appointments."""

    class Meta:
        model = AppointmentData

    # Required relationships
    patient = factory.SubFactory(PatientFactory)
    provider = factory.SubFactory(StaffFactory)
    location = factory.SubFactory(PracticeLocationFactory)

    # Date/time fields with reasonable defaults
    start_time = factory.LazyFunction(
        lambda: datetime.datetime.now() + datetime.timedelta(days=7)
    )

    # Use FuzzyChoice for fields with limited options
    duration_minutes = FuzzyChoice([15, 30, 45, 60])

    # Simple string fields
    comment = factory.Faker("sentence")
    description = factory.Faker("sentence")
```

### Usage of Custom Factory

```python
def test_with_custom_appointment_factory():
    """Example test using the custom AppointmentFactory."""
    # Basic creation
    appointment = AppointmentFactory.create()

    assert appointment.id is not None
    assert appointment.patient is not None
    assert appointment.provider is not None

    # With custom values
    specific_patient = PatientFactory.create(first_name="Alice")
    appointment = AppointmentFactory.create(
        patient=specific_patient,
        duration_minutes=60
    )

    assert appointment.patient.first_name == "Alice"
    assert appointment.duration_minutes == 60
```

### Advanced Factory Features

#### 1. Post-Generation Hooks

Use `@factory.post_generation` to perform actions after object creation:

```python
class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Faker("sentence")
    patient = factory.SubFactory(PatientFactory)

    @factory.post_generation
    def add_labels(self, create, extracted, **kwargs):
        """Add labels to the task after creation."""
        if not create:
            return

        if extracted:
            # Use provided labels
            for label in extracted:
                self.labels.add(label)
        else:
            # Add default labels
            self.labels.add("test-label")

# Usage:
task = TaskFactory.create(add_labels=["urgent", "review"])
```

#### 2. Lazy Attributes

Use `factory.LazyAttribute` for fields that depend on other fields:

```python
class StaffFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Staff

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    # Email based on name
    email = factory.LazyAttribute(
        lambda obj: f"{obj.first_name.lower()}.{obj.last_name.lower()}@example.com"
    )
```

#### 3. Sequences

Use `factory.Sequence` for unique values:

```python
class PatientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Patient

    # Creates patient-1@example.com, patient-2@example.com, etc.
    email = factory.Sequence(lambda n: f"patient-{n}@example.com")
```

#### 4. Conditional SubFactories

Use `factory.Maybe` for conditional relationships:

```python
class NoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Note

    is_signed = factory.Faker("boolean")

    # Only create signing provider if note is signed
    signing_provider = factory.Maybe(
        "is_signed",
        yes_declaration=factory.SubFactory(StaffFactory),
        no_declaration=None
    )
```

## Factory Best Practices

### 1. Use Factories for All Test Data

```python
# Good: Using factories
def test_patient_lookup():
    patient = PatientFactory.create(first_name="John")
    result = lookup_patient(patient.id)
    assert result.first_name == "John"

# Avoid: Manual object creation
def test_patient_lookup_manual():
    patient = Patient.objects.create(
        first_name="John",
        last_name="Doe",
        birth_date=datetime.date(1980, 1, 1),
        # ... many more required fields
    )
```

### 2. Create Factories in a Shared Location

Place custom factories in a dedicated file:

```
tests/
  ├── __init__.py
  ├── factories.py          # Your custom factories
  └── test_my_plugin.py     # Your tests
```

### 3. Override Only What You Need

```python
# Good: Only override relevant fields
patient = PatientFactory.create(first_name="Alice")

# Avoid: Overriding everything
patient = PatientFactory.create(
    first_name="Alice",
    last_name="Smith",  # Could use default
    birth_date=datetime.date(1990, 1, 1),  # Could use default
)
```

### 4. Use build() Instead of create() When Database Isn't Needed

```python
# Creates object in database
patient = PatientFactory.create()

# Creates object in memory only (faster for unit tests)
patient = PatientFactory.build()
```

## Common Patterns

### Testing Protocols with Factories

```python
from canvas_sdk.test_utils.factories import PatientFactory, NoteFactory

def test_my_protocol():
    # Create test data
    patient = PatientFactory.create(
        first_name="Test",
        birth_date=datetime.date(1980, 1, 1)
    )

    note = NoteFactory.create(patient=patient)

    # Create a mock event
    mock_event = Mock()
    mock_event.context = {"patient": {"id": patient.id}}

    # Test your protocol
    protocol = MyProtocol(event=mock_event)
    effects = protocol.compute()

    assert len(effects) > 0
```

### Testing API Handlers with Factories

```python
from canvas_sdk.test_utils.factories import PatientFactory, StaffFactory

def test_appointment_api():
    # Create test data
    patient = PatientFactory.create()
    provider = StaffFactory.create()

    # Create API request
    api = AppointmentAPI(event=mock_event)
    api.request = DummyRequest(
        json_body={
            "patient_id": str(patient.id),
            "provider_id": str(provider.id),
            "start_time": "2024-01-01T10:00:00"
        }
    )

    # Test the API
    result = api.post()
    assert result[0].status_code == HTTPStatus.CREATED
```

## References

- [Factory Boy Documentation](https://factoryboy.readthedocs.io/)
- [Canvas SDK Testing Utils](https://docs.canvasmedical.com/sdk/testing-utils/)
- [Canvas SDK Factory Source](https://github.com/canvas-medical/canvas-plugins/tree/main/canvas_sdk/test_utils/factories)
