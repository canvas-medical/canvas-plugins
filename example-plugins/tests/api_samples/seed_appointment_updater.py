"""
Seed file for testing the appointment_updater API.

This creates a variety of test scenarios for the AppointmentAPI endpoint:
- Multiple patients with upcoming appointments
- Different appointment statuses
- Various providers and locations

Usage:
    canvas run-plugin example-plugins/api_samples \
        --db-seed-file ./example-plugins/tests/api_samples/seed_appointment_updater.py
"""

import datetime
import os

# Import our custom AppointmentFactory
import sys

from canvas_sdk.test_utils.factories import (
    NoteFactory,
    PatientFactory,
    PracticeLocationFactory,
    StaffFactory,
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from factories import AppointmentFactory

print("\n" + "="*60)
print("Seeding database for appointment_updater API testing")
print("="*60 + "\n")

# Create test providers
print("Creating providers...")
dr_smith = StaffFactory.create(
    first_name="Sarah",
    last_name="Smith"
)
print(f"  ✓ Created provider: Dr. {dr_smith.first_name} {dr_smith.last_name}")

dr_jones = StaffFactory.create(
    first_name="Michael",
    last_name="Jones"
)
print(f"  ✓ Created provider: Dr. {dr_jones.first_name} {dr_jones.last_name}")

# Create test locations
print("\nCreating practice locations...")
main_office = PracticeLocationFactory.create()
print(f"  ✓ Created location: Main Office (ID: {main_office.id})")

satellite_office = PracticeLocationFactory.create()
print(f"  ✓ Created location: Satellite Office (ID: {satellite_office.id})")

# Create test patients with appointments
print("\nCreating test patients with appointments...\n")

test_scenarios = [
    {
        "patient": {"first_name": "Alice", "last_name": "Anderson", "birth_date": datetime.date(1985, 3, 15)},
        "provider": dr_smith,
        "location": main_office,
        "status": "confirmed",
        "days_from_now": 7,
        "duration": 30,
        "description": "Upcoming confirmed appointment"
    },
    {
        "patient": {"first_name": "Bob", "last_name": "Brown", "birth_date": datetime.date(1972, 7, 22)},
        "provider": dr_smith,
        "location": main_office,
        "status": "unconfirmed",
        "days_from_now": 3,
        "duration": 45,
        "description": "Unconfirmed appointment needing confirmation"
    },
    {
        "patient": {"first_name": "Carol", "last_name": "Chen", "birth_date": datetime.date(1990, 11, 8)},
        "provider": dr_jones,
        "location": satellite_office,
        "status": "confirmed",
        "days_from_now": 14,
        "duration": 60,
        "description": "Longer appointment at satellite office"
    },
    {
        "patient": {"first_name": "David", "last_name": "Davis", "birth_date": datetime.date(1965, 5, 30)},
        "provider": dr_jones,
        "location": main_office,
        "status": "arrived",
        "days_from_now": 0,
        "duration": 30,
        "description": "Patient arrived for today's appointment"
    },
    {
        "patient": {"first_name": "Emma", "last_name": "Evans", "birth_date": datetime.date(1988, 9, 12)},
        "provider": dr_smith,
        "location": satellite_office,
        "status": "confirmed",
        "days_from_now": 21,
        "duration": 30,
        "description": "Future appointment ready for updates"
    },
]

appointments_info = []

for i, scenario in enumerate(test_scenarios, 1):
    # Create patient
    patient = PatientFactory.create(**scenario["patient"])

    # Create note for the appointment
    note = NoteFactory.create(
        patient=patient,
        provider=scenario["provider"],
        location=scenario["location"]
    )

    # Calculate appointment time
    start_time = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=scenario["days_from_now"])

    # Create appointment
    appointment = AppointmentFactory.create(
        note=note,
        patient=patient,
        provider=scenario["provider"],
        location=scenario["location"],
        status=scenario["status"],
        start_time=start_time,
        duration_minutes=scenario["duration"]
    )

    # Store info for summary
    appointments_info.append({
        "number": i,
        "patient_name": f"{patient.first_name} {patient.last_name}",
        "note_dbid": note.dbid,
        "appointment_id": str(appointment.id),
        "status": appointment.status,
        "provider": f"Dr. {scenario['provider'].last_name}",
        "location": scenario["location"],
        "start_time": start_time.strftime("%Y-%m-%d %H:%M"),
        "description": scenario["description"]
    })

    print(f"[{i}] {patient.first_name} {patient.last_name}")
    print(f"    Patient ID: {patient.id}")
    print(f"    Note DBID: {note.dbid}")
    print(f"    Appointment ID: {appointment.id}")
    print(f"    Status: {appointment.status}")
    print(f"    Provider: Dr. {scenario['provider'].last_name}")
    print(f"    Start Time: {start_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"    Duration: {scenario['duration']} minutes")
    print(f"    Description: {scenario['description']}")
    print()

# Print testing instructions
print("\n" + "="*60)
print("✅ Database seeded successfully!")
print("="*60)
print("\n📋 Test the AppointmentAPI with these examples:\n")

print("🔑 First, set your API key secret:")
print("    canvas config set api_samples my-api-key=your-secret-key-here\n")

for info in appointments_info[:3]:  # Show first 3 examples
    print(f"📝 Test #{info['number']}: {info['description']}")
    print(f"   Patient: {info['patient_name']}")
    print(f"   curl -X PUT http://localhost:8000/plugin-io/api/api_samples/appointments/{info['note_dbid']} \\")
    print("     -H 'Authorization: your-secret-key-here' \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\n")
    print(f"       \"meetingLink\": \"https://meet.example.com/{info['patient_name'].replace(' ', '-').lower()}\"")
    print("     }'\n")

print("\n💡 Tips:")
print("   • Use the Note DBID (not appointment ID) in the URL path")
print("   • The API will add meeting links and external identifiers")
print("   • Check the response for status code 202 (ACCEPTED)")
print("   • Try the 404 test with note_dbid=99999")
print("\n" + "="*60 + "\n")
