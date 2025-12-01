fullscript
==========

## Description

This plugin integrates Canvas with Fullscript, allowing healthcare providers to seamlessly prescribe supplements and manage treatment plans within the Canvas platform.

At a high level, this plugin:
1. Embeds the Fullscript catalog application directly in the Canvas patient chart using their JavaScript SDK
2. Implements OAuth2 authentication flow with token caching and automatic refresh
3. Integrates Fullscript supplements into Canvas medication search (both medication statements and prescribe commands)
4. Syncs Fullscript treatment plans back to Canvas as medication statements
5. Creates and links Fullscript patient records with Canvas patients via external identifiers
6. Groups Fullscript supplements in the medication section of the patient chart
7. Supports prescribing Fullscript supplements directly from Canvas

## SDK Features

- Creates an [Application](/sdk/handlers-applications/) that launches an embedded Fullscript interface in the patient chart
- Implements [Simple API](/sdk/handlers-simple-api-http/) endpoints with [StaffSessionAuthMixin](/sdk/handlers-simple-api-http/#staff-session) for:
  - OAuth2 token exchange and refresh
  - Fullscript session grant generation
  - Patient creation and linking
  - Treatment plan webhook handling
- Uses [BaseHandler](/sdk/handlers-basehandler/) handlers to:
  - Inject Fullscript supplements into medication search results (MEDICATION_STATEMENT__MEDICATION__POST_SEARCH event)
  - Inject Fullscript supplements into prescribe search results (PRESCRIBE__PRESCRIBE__POST_SEARCH event)
  - Group Fullscript supplements in the patient chart (PATIENT_CHART__MEDICATIONS event)
- Uses [Canvas plugin caching](/sdk/caching/) for storing OAuth tokens per user
- Uses [Patient External Identifiers](/sdk/effect-create-patient-external-identifier/) to link Canvas and Fullscript patient records
- Uses [MedicationStatementCommand](/sdk/commands/#medicationstatement/) to create supplement orders in Canvas

## Configuration

### Secrets

This plugin requires three secrets to be configured in the Canvas Admin UI - Plugins. [Read more about secrets](/sdk/secrets/)

#### FULLSCRIPT_CLIENT_ID
The OAuth2 client ID provided by Fullscript for API authentication.

#### FULLSCRIPT_CLIENT_SECRET
The OAuth2 client secret provided by Fullscript for API authentication.

#### FULLSCRIPT_SEARCH_PAGE_SIZE
The number of products to return when searching Fullscript supplements (e.g., "20").

## Integration Flow

### First-Time Setup

1. User opens the Fullscript application from a patient chart
2. Frontend displays "Connect with Fullscript" button
3. User clicks button and is redirected to Fullscript OAuth page
4. User authorizes the connection
5. Fullscript redirects back to Canvas with authorization code
6. Backend exchanges code for access token and refresh token
7. Tokens are cached in Canvas keyed by staff user ID
8. Backend creates or retrieves Fullscript patient ID
9. Frontend embeds Fullscript catalog interface

### Subsequent Usage

1. User opens the Fullscript application
2. Frontend attempts to use cached access token
3. If token is expired, backend automatically refreshes it
4. Fullscript interface loads immediately without re-authorization

### Supplement Search

1. Clinician types in medication search field in Canvas
2. Canvas performs standard medication search
3. `SearchFullscriptSupplements` protocol handler is triggered
4. Handler fetches matching supplements from Fullscript API
5. Supplements are injected at the top of search results with "Supp" annotation
6. Clinician can select and add supplements like regular medications

### Treatment Plan Sync

1. Clinician creates treatment plan in embedded Fullscript interface
2. Clinician reviews the treatment plan in Fullscript
3. Fullscript SDK emits `treatmentPlan.activated` event
4. Frontend JavaScript catches the event and sends data to backend webhook
5. Backend fetches detailed product information for each recommendation
6. Backend creates `MedicationStatementCommand` effects for each supplement
7. Supplements appear in the patient's current note
8. Supplements are grouped in a dedicated "Supplements" section of the chart


## api/

### fullscriptAPI.py

This file contains all the API endpoints for the Fullscript integration, handling OAuth2 flows, token management, patient synchronization, and treatment plan event.

**POST /exchange-token**

- Handles OAuth2 authorization code exchange for access tokens
- Checks for existing cached tokens and refreshes them if expired
- If no cached token exists, exchanges the authorization code for a new token
- Stores tokens in the Canvas plugin cache keyed by user ID
- Returns the access token to the frontend

**POST /session-grant**

- Creates a Fullscript embeddable session grant using an access token
- Makes a POST request to Fullscript's session grants endpoint
- Returns the session grant token for use in the frontend

**POST /get-or-create-patient**

- Links Canvas patients with Fullscript patient records
- First checks if the Canvas patient already has a Fullscript external identifier
- If not, creates a new patient in Fullscript with name and email
- Creates a `PatientExternalIdentifier` effect to link the two systems
- Returns the Fullscript patient ID for use in the embedded interface

**POST /treatment-plan-created**

- Endpoint called when a treatment plan is reviewed in Fullscript
- Receives treatment plan recommendations from the frontend
- For each recommended supplement:
  - Fetches detailed product variant information from Fullscript API
  - Creates a `MedicationStatementCommand` with the variant details
- Returns a list of `MedicationStatementCommand` effects to create the supplements in Canvas and add them to the patient's chart

**Error Handling:**

All endpoints include comprehensive error handling for:
- Network request failures
- Invalid or expired tokens
- Missing required data
- Fullscript API errors


## static/

### main.js

Contains the frontend JavaScript logic for OAuth authentication and Fullscript SDK integration.

**OAuth Flow:**

1. `startOAuthFlow()`: Redirects the user to Fullscript's OAuth authorization page
2. `exchangeToken(oauthCode)`: Exchanges the authorization code for an access token via the backend
3. `fetchSessionGrant(accessToken)`: Obtains a session grant for the Fullscript SDK
4. `getOrCreatePatient(accessToken)`: Ensures the patient exists in both Canvas and Fullscript

**Fullscript SDK Integration:**

- `mountFullscriptApp(sessionGrantToken, fullScriptPatientId)`: Initializes and mounts the Fullscript SDK
- Configures the SDK to show the catalog entrypoint
- Listens for the `treatmentPlan.activated` event from Fullscript
- When a treatment plan is activated, sends the data to the backend webhook

**Token Caching:**

- `tryInitializeWithCachedToken()`: Attempts to use a cached token from the backend
- If successful, skips the OAuth flow entirely for a seamless experience
- If the cached token is invalid or expired, shows the OAuth button

**Event Handling:**

- `handleTreatmentPlanCreated(treatmentPlanEvent)`: Sends treatment plan data to the backend for processing
- The backend creates corresponding medication statements in Canvas

### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it
gets updated if you add, remove, or rename protocols.
