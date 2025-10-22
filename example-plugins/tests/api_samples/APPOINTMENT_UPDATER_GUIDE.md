# Testing the Appointment Updater API Locally

This guide shows you how to test the `appointment_updater` API endpoint in your local development environment.

## Quick Start

### 1. Start the Plugin with Test Data

```bash
# From the canvas-plugins directory:
canvas run-plugin example-plugins/api_samples \
  --db-seed-file ./example-plugins/tests/api_samples/seed_appointment_updater.py
```

This will:
- Reset your local database
- Create 5 test patients with appointments
- Create 2 providers (Dr. Smith and Dr. Jones)
- Create 2 practice locations
- Display all the test data details

### 2. Set Your API Key (One-Time Setup)

```bash
canvas config set api_samples my-api-key=test-secret-123
```

### 3. Test the API

Once the plugin is running, use curl to test the endpoint:

```bash
# Update an appointment (use the Note DBID from the seed output)
curl -X PUT http://localhost:8000/plugin-io/api/api_samples/appointments/<NOTE_DBID> \
  -H 'Authorization: test-secret-123' \
  -H 'Content-Type: application/json' \
  -d '{
    "meetingLink": "https://meet.example.com/my-meeting"
  }'
```

**Expected Response:**
```json
{
  "status": "accepted"
}
```

## What the Seed File Creates

The `seed_appointment_updater.py` creates 5 test scenarios:

| # | Patient | Provider | Status | Days from Now | Description |
|---|---------|----------|--------|---------------|-------------|
| 1 | Alice Anderson | Dr. Smith | confirmed | 7 days | Upcoming confirmed appointment |
| 2 | Bob Brown | Dr. Smith | unconfirmed | 3 days | Unconfirmed appointment |
| 3 | Carol Chen | Dr. Jones | confirmed | 14 days | Longer appointment at satellite office |
| 4 | David Davis | Dr. Jones | arrived | Today | Patient already arrived |
| 5 | Emma Evans | Dr. Smith | confirmed | 21 days | Future appointment |

## API Endpoint Details

**URL Pattern:** `PUT /plugin-io/api/api_samples/appointments/<note_dbid>`

**Authentication:** API Key in `Authorization` header

**Request Body:**
```json
{
  "meetingLink": "https://meet.example.com/room-123"
}
```

**What the API Does:**
1. Looks up the appointment by note database ID
2. Creates an effect to update the appointment with:
   - The provided meeting link
   - External identifier (example: system + value)
3. Returns HTTP 202 ACCEPTED if successful
4. Returns HTTP 404 NOT FOUND if appointment doesn't exist

## Testing Scenarios

### ✅ Test 1: Successful Update

```bash
# Get the Note DBID from seed output (look for "Note DBID: XXXX")
curl -X PUT http://localhost:8000/plugin-io/api/api_samples/appointments/1 \
  -H 'Authorization: test-secret-123' \
  -H 'Content-Type: application/json' \
  -d '{"meetingLink": "https://zoom.us/j/123456789"}'
```

Expected: HTTP 202 ACCEPTED

### ❌ Test 2: Appointment Not Found

```bash
curl -X PUT http://localhost:8000/plugin-io/api/api_samples/appointments/99999 \
  -H 'Authorization: test-secret-123' \
  -H 'Content-Type: application/json' \
  -d '{"meetingLink": "https://zoom.us/j/123456789"}'
```

Expected: HTTP 404 NOT FOUND with error message

### 🔒 Test 3: Invalid API Key

```bash
curl -X PUT http://localhost:8000/plugin-io/api/api_samples/appointments/1 \
  -H 'Authorization: wrong-key' \
  -H 'Content-Type: application/json' \
  -d '{"meetingLink": "https://zoom.us/j/123456789"}'
```

Expected: HTTP 401 UNAUTHORIZED

## Using the Test Data

After seeding, you'll see output like this:

```
[1] Alice Anderson
    Patient ID: abc123...
    Note DBID: 1
    Appointment ID: def456...
    Status: confirmed
    Provider: Dr. Smith
    Start Time: 2024-01-15 10:00
    Duration: 30 minutes
```

Use the **Note DBID** (not the Appointment ID) in your API calls.

## Troubleshooting

### Problem: "Authorization failed"
**Solution:** Make sure you set the API key:
```bash
canvas config set api_samples my-api-key=test-secret-123
```

### Problem: "Appointment not found"
**Solution:** Double-check you're using the Note DBID (from seed output), not the appointment ID.

### Problem: Seed file fails
**Solution:** Make sure you're in the `canvas-plugins` directory and the path is correct:
```bash
pwd  # Should show .../canvas-plugins
ls example-plugins/tests/api_samples/seed_appointment_updater.py  # Should exist
```

## Modifying the Seed Data

Edit `seed_appointment_updater.py` to add more test scenarios:

```python
test_scenarios = [
    {
        "patient": {"first_name": "New", "last_name": "Patient", "birth_date": datetime.date(1995, 1, 1)},
        "provider": dr_smith,
        "location": main_office,
        "status": "confirmed",
        "days_from_now": 5,
        "duration": 45,
        "description": "Your custom scenario"
    },
    # ... add more scenarios
]
```

Then restart the plugin to reload the data.

## Next Steps

- Try the other API samples endpoints (HelloWorldAPI, EmailBounceAPI)
- Create your own seed files for different test scenarios
- Use the factories in your own plugins
- Write automated tests using the patterns in `tests/api_samples/`

## Related Files

- Seed file: `example-plugins/tests/api_samples/seed_appointment_updater.py`
- API implementation: `example-plugins/api_samples/routes/appointment_updater.py`
- Tests: `example-plugins/tests/api_samples/test_appointment_updater.py`
- Factory: `example-plugins/tests/factories.py` (AppointmentFactory)
