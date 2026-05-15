# custom_data_room_booking

Room booking tracker with custom data models. Used as a test harness for custom data features
including `ModelExtension` proxies, `proxy_field`, and `CustomModel` relationships.

## API Endpoints

All endpoints require the `Authorization` header:

```
Authorization: f2464a67e6fa9839579189a8c1c781e9
```Move

### List Staff

```bash
curl -s -H "Authorization: f2464a67e6fa9839579189a8c1c781e9" \
  "http://localhost:8000/plugin-io/api/custom_data_room_booking/staff"
```

### Create Room

```bash
curl -s -X POST "http://localhost:8000/plugin-io/api/custom_data_room_booking/rooms" \
  -H "Authorization: f2464a67e6fa9839579189a8c1c781e9" \
  -H "Content-Type: application/json" \
  -d '{"name": "Room A"}'
```

### Delete Room

```bash
curl -s -X DELETE "http://localhost:8000/plugin-io/api/custom_data_room_booking/rooms/1" \
  -H "Authorization: f2464a67e6fa9839579189a8c1c781e9"
```

### Make Staff Bookable

```bash
curl -s -X POST "http://localhost:8000/plugin-io/api/custom_data_room_booking/staff/4150cd20de8a470aa570a852859ac87e/bookable" \
  -H "Authorization: f2464a67e6fa9839579189a8c1c781e9"
```

### Create Booking

```bash
curl -s -X POST "http://localhost:8000/plugin-io/api/custom_data_room_booking/bookings" \
  -H "Authorization: f2464a67e6fa9839579189a8c1c781e9" \
  -H "Content-Type: application/json" \
  -d '{"room_id": 1, "staff_id": "4150cd20de8a470aa570a852859ac87e", "patient_id": "405ecf7a18cc48f989d46af2f112e6fc", "scheduled_at": "2026-03-15T10:00:00"}'
```

### Get Room Schedule

```bash
curl -s "http://localhost:8000/plugin-io/api/custom_data_room_booking/rooms/1/schedule" \
  -H "Authorization: f2464a67e6fa9839579189a8c1c781e9"
```

### List Notes

Returns recent notes with patient and provider names. Uses `NoteProxy` with `proxy_field` so
that `note.patient` and `note.provider` return `PatientProxy`/`StaffProxy` instances with
`display_name` available.

```bash
curl -s -H "Authorization: f2464a67e6fa9839579189a8c1c781e9" \
  "http://localhost:8000/plugin-io/api/custom_data_room_booking/notes"
```

### Get Note

```bash
curl -s -H "Authorization: f2464a67e6fa9839579189a8c1c781e9" \
  "http://localhost:8000/plugin-io/api/custom_data_room_booking/notes/227"
```

## Full Test Sequence

These commands were used to exercise all endpoints end-to-end:

```bash
# List available staff
curl -s -H "Authorization: f2464a67e6fa9839579189a8c1c781e9" \
  "http://localhost:8000/plugin-io/api/custom_data_room_booking/staff" | python3 -m json.tool

# Create rooms
curl -s -X POST "http://localhost:8000/plugin-io/api/custom_data_room_booking/rooms" \
  -H "Authorization: f2464a67e6fa9839579189a8c1c781e9" \
  -H "Content-Type: application/json" -d '{"name": "Room A"}'

curl -s -X POST "http://localhost:8000/plugin-io/api/custom_data_room_booking/rooms" \
  -H "Authorization: f2464a67e6fa9839579189a8c1c781e9" \
  -H "Content-Type: application/json" -d '{"name": "Room B"}'

# Make staff bookable
curl -s -X POST "http://localhost:8000/plugin-io/api/custom_data_room_booking/staff/4150cd20de8a470aa570a852859ac87e/bookable" \
  -H "Authorization: f2464a67e6fa9839579189a8c1c781e9"

curl -s -X POST "http://localhost:8000/plugin-io/api/custom_data_room_booking/staff/def9038ce8d446bdac9c10af8a9f45cf/bookable" \
  -H "Authorization: f2464a67e6fa9839579189a8c1c781e9"

# Create bookings
curl -s -X POST "http://localhost:8000/plugin-io/api/custom_data_room_booking/bookings" \
  -H "Authorization: f2464a67e6fa9839579189a8c1c781e9" \
  -H "Content-Type: application/json" \
  -d '{"room_id": 1, "staff_id": "4150cd20de8a470aa570a852859ac87e", "patient_id": "405ecf7a18cc48f989d46af2f112e6fc", "scheduled_at": "2026-03-15T10:00:00"}'

curl -s -X POST "http://localhost:8000/plugin-io/api/custom_data_room_booking/bookings" \
  -H "Authorization: f2464a67e6fa9839579189a8c1c781e9" \
  -H "Content-Type: application/json" \
  -d '{"room_id": 1, "staff_id": "2a6cfdb145c8469b9d935fe91f6b0172", "patient_id": "405ecf7a18cc48f989d46af2f112e6fc", "scheduled_at": "2026-03-15T11:00:00"}'

curl -s -X POST "http://localhost:8000/plugin-io/api/custom_data_room_booking/bookings" \
  -H "Authorization: f2464a67e6fa9839579189a8c1c781e9" \
  -H "Content-Type: application/json" \
  -d '{"room_id": 1, "staff_id": "4150cd20de8a470aa570a852859ac87e", "patient_id": "d51a4d0ce83540efba4e96461685b3ec", "scheduled_at": "2026-03-15T14:00:00"}'

curl -s -X POST "http://localhost:8000/plugin-io/api/custom_data_room_booking/bookings" \
  -H "Authorization: f2464a67e6fa9839579189a8c1c781e9" \
  -H "Content-Type: application/json" \
  -d '{"room_id": 3, "staff_id": "4150cd20de8a470aa570a852859ac87e", "patient_id": "405ecf7a18cc48f989d46af2f112e6fc", "scheduled_at": "2026-03-15T09:00:00"}'

curl -s -X POST "http://localhost:8000/plugin-io/api/custom_data_room_booking/bookings" \
  -H "Authorization: f2464a67e6fa9839579189a8c1c781e9" \
  -H "Content-Type: application/json" \
  -d '{"room_id": 3, "staff_id": "def9038ce8d446bdac9c10af8a9f45cf", "patient_id": "d51a4d0ce83540efba4e96461685b3ec", "scheduled_at": "2026-03-15T10:00:00"}'

curl -s -X POST "http://localhost:8000/plugin-io/api/custom_data_room_booking/bookings" \
  -H "Authorization: f2464a67e6fa9839579189a8c1c781e9" \
  -H "Content-Type: application/json" \
  -d '{"room_id": 4, "staff_id": "4150cd20de8a470aa570a852859ac87e", "patient_id": "998279c9c268436bb4f13c6e7004bda4", "scheduled_at": "2026-03-15T11:00:00"}'

# View room schedules
curl -s "http://localhost:8000/plugin-io/api/custom_data_room_booking/rooms/1/schedule" \
  -H "Authorization: f2464a67e6fa9839579189a8c1c781e9" | python3 -m json.tool

curl -s "http://localhost:8000/plugin-io/api/custom_data_room_booking/rooms/3/schedule" \
  -H "Authorization: f2464a67e6fa9839579189a8c1c781e9" | python3 -m json.tool

curl -s "http://localhost:8000/plugin-io/api/custom_data_room_booking/rooms/4/schedule" \
  -H "Authorization: f2464a67e6fa9839579189a8c1c781e9" | python3 -m json.tool

# Delete rooms (cascades to bookings)
curl -s -X DELETE "http://localhost:8000/plugin-io/api/custom_data_room_booking/rooms/1" \
  -H "Authorization: f2464a67e6fa9839579189a8c1c781e9"

curl -s -X DELETE "http://localhost:8000/plugin-io/api/custom_data_room_booking/rooms/2" \
  -H "Authorization: f2464a67e6fa9839579189a8c1c781e9"

curl -s -X DELETE "http://localhost:8000/plugin-io/api/custom_data_room_booking/rooms/3" \
  -H "Authorization: f2464a67e6fa9839579189a8c1c781e9"

# List notes (proxy_field demo)
curl -s -H "Authorization: f2464a67e6fa9839579189a8c1c781e9" \
  "http://localhost:8000/plugin-io/api/custom_data_room_booking/notes"

# Get single note
curl -s -H "Authorization: f2464a67e6fa9839579189a8c1c781e9" \
  "http://localhost:8000/plugin-io/api/custom_data_room_booking/notes/227"
```
