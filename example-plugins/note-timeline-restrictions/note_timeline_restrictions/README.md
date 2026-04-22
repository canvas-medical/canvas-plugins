# Note Access Restriction — Example Plugin

This plugin demonstrates how to use [`RestrictNoteEffect`](../../canvas_sdk/effects/note/restrict_note.py) to restrict access to notes and letters in the Canvas EHR. It covers two of the four use-cases from the SDK specification:

| Use case | Implemented by |
|---|---|
| Prevent multiple users from editing the same note simultaneously | `RestrictNoteOnConcurrentEdit`, `RestrictNoteOnLetterEdit`, `ExpireNoteRestrictionsCron` |
| Prevent certain staff from editing certain note types | `NoteAccessPermissionsHandler`, `NoteTypeAccessConfig` |

The other two use-cases (preventing staff from seeing sensitive notes, break-the-glass workflows) can be built by following the same pattern — return a `RestrictNoteEffect` from a `GET_NOTE_RESTRICTIONS` handler.

---

## How it works

```
User saves a note
  ↓
RestrictNoteOnConcurrentEdit detects body checksum changed
  ↓
Writes NoteMetadata(key="restriction", value={active, editor_staff_id, blur, message, last_edited_at})
  + emits NoteRestrictionsUpdatedEffect directly
  ↓
Frontend subscription triggers → refetches GET_NOTE_RESTRICTIONS
  ↓
NoteAccessPermissionsHandler reads the restriction, returns RestrictNoteEffect(restrict_access=True)
  ↓
Banner shown, note body blurred, all inputs disabled for other users

Meanwhile, ExpireNoteRestrictionsCron runs every minute, clears stale restrictions,
and emits NoteRestrictionsUpdatedEffect so the UI updates immediately.
```

---

## Data storage

This plugin uses two distinct storage mechanisms:

### Concurrent edit restrictions — `NoteMetadata`

Active edit locks are stored in `NoteMetadata` under the key `restriction`. This ties the lock to the note it protects and uses the built-in metadata infrastructure.

```json
{
  "active": true,
  "editor_staff_id": "<staff-uuid>",
  "blur": true,
  "message": "This note is currently being edited by another user.",
  "last_edited_at": "2025-01-01T12:00:00+00:00"
}
```

A cleared restriction is represented as an empty object `{}`.

### Note-type access configuration — `NoteTypeAccessConfig` (CustomModel)

Role-based access rules are stored in a plugin-owned table (`NoteTypeAccessConfig`) created via Canvas [custom data storage](https://docs.canvasmedical.com/sdk/custom-data/). One row per note type; each row records which staff members may access notes of that type.

The table lives in the `note_timeline__restrictions` schema, declared in the manifest under `custom_data`. The plugin runner creates this schema and table automatically on install — no manual migrations needed.

| Field | Type | Description |
|---|---|---|
| `note_type_id` | `TextField` (unique) | `NoteType.unique_identifier` as a UUID string |
| `allowed_staff_ids` | `JSONField` | List of `Staff.id` values permitted to access this note type |

---

## Handlers

### `TrackNoteBodyChecksum`
Responds to `NOTE_CREATED`. Writes an MD5 checksum of the note body to `NoteMetadata` (key `note_timeline_restrictions:body_checksum`). This baseline is compared on every subsequent save to detect whether the content changed.

### `RestrictNoteOnConcurrentEdit`
Responds to `NOTE_UPDATED`. Compares the current body checksum against the stored baseline. If the content changed, writes a restriction attributing it to the editing staff member and immediately emits `NoteRestrictionsUpdatedEffect` so other users see the banner in real time. Always updates the checksum so the same user's next save does not re-trigger the restriction.

### `RestrictNoteOnLetterEdit`
Responds to `LETTER_UPDATED`. Writes a restriction on the parent note (since letter edits do not change the note body and would not be caught by the checksum comparison) and immediately emits `NoteRestrictionsUpdatedEffect`.

### `NoteAccessPermissionsHandler`
Responds to `GET_NOTE_RESTRICTIONS`. Evaluates two policies in order:

1. **Role-based** — checks `NoteTypeAccessConfig` for the note's type. If a row exists and the actor's `Staff.id` is not in `allowed_staff_ids`, access is denied with a blur and banner. Configure note-type access rules from the **Note Type Access** tab in the dashboard.
2. **Concurrent edit restriction** — if an active restriction exists in `NoteMetadata` and the actor is not the staff member who holds it, returns `RestrictNoteEffect` with the restriction's blur and message settings.

Returning no effects leaves the note unrestricted.

### `ExpireNoteRestrictionsCron`
Runs every minute (`SCHEDULE = "* * * * *"`). Scans all `restriction` metadata entries and releases any whose `last_edited_at` is older than `RESTRICTION_EXPIRY_MINUTES`. Emits `NoteRestrictionsUpdatedEffect` for each released restriction.

---

## Dashboard

The plugin ships a global dashboard (`NoteRestrictionDashboard`) that lets administrators view and manage note restrictions in real time.

**Access:** The dashboard opens as a full-page modal from the Canvas application launcher.

**Tab 1 — Active Restrictions:**
- Search notes by patient name
- Filter by note state and restriction status
- **Apply Restriction** — manually restrict an unrestricted note
- **Remove Restriction** — release an active restriction immediately (same effect as the cron, but on demand)
- Live "since X ago" display of how long a restriction has been active

**Tab 2 — Note Type Access:**
- View all active note types with their current access configuration
- Select which staff members may access each note type (multi-select)
- **Save** — persists the allow-list to `NoteTypeAccessConfig`
- **Remove Restriction** — clears the rule, making the note type accessible to all staff

**API endpoints** (`/plugin-io/api/note_timeline_restrictions`):

| Method | Path | Description |
|---|---|---|
| `GET` | `/notes` | Paginated note list with restriction status. Supports `patient_search`, `state`, `locked`, `page`, `page_size` query params. |
| `POST` | `/notes/<id>/restrict` | Apply a restriction to a note. Optional body: `{"blur": true, "message": "..."}` |
| `POST` | `/notes/<id>/unrestrict` | Remove the restriction from a note. |
| `GET` | `/note-types` | List all active note types with their current access configuration. |
| `PUT` | `/note-types/<id>/access` | Set the allowed staff IDs for a note type. Body: `{"allowed_staff_ids": [...]}` or `{"allowed_staff_ids": null}` to remove. |
| `GET` | `/staff` | List active staff members for the access-control multi-select. |
| `GET` | `/states` | List available note states for the filter dropdown. |

---

## Configuration

All tuneable values are module-level constants in `handlers/event_handlers.py`:

| Constant | Default | Description |
|---|---|---|
| `RESTRICTION_KEY` | `"restriction"` | NoteMetadata key for the concurrent edit lock |
| `CHECKSUM_KEY` | `"note_timeline_restrictions:body_checksum"` | NoteMetadata key for the body checksum |
| `RESTRICTION_EXPIRY_MINUTES` | `1` | Minutes before a stale restriction is released |

---

## SDK effects used

| Effect | Purpose |
|---|---|
| `RestrictNoteEffect` | Communicates whether a note is restricted, blurred, and what banner to display |
| `NoteRestrictionsUpdatedEffect` | Triggers real-time permission refetch in the frontend |
| `NoteEffect.upsert_metadata()` | Writes concurrent edit lock data to NoteMetadata |
| `PatientTimelineEffect` | Controls which note types are visible in the patient timeline |

---

## SDK data models used

| Model | Purpose |
|---|---|
| `NoteMetadata` | Stores per-note concurrent edit locks (key `restriction`) and body checksums |
| `NoteTypeAccessConfig` *(CustomModel)* | Stores role-based access rules per note type, persisted in the `note_timeline__restrictions` schema |
| `NoteType` | Looked up to get the note's type UUID and name for access control decisions |
| `Staff` | Looked up to resolve actor user ID → staff UUID for lock ownership comparison |
