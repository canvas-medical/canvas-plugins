# Note Management External Application Integration Guide

This guide demonstrates how to build an external application that integrates with Canvas Medical using OAuth 2.0 authentication to manage notes (lock, sign, unlock, check-in, no-show).

## Table of Contents

1. [Overview](#overview)
2. [OAuth 2.0 Setup](#oauth-20-setup)
3. [Plugin Architecture](#plugin-architecture)
4. [Implementation Details](#implementation-details)
5. [API Endpoints](#api-endpoints)

---

## Overview

This plugin demonstrates a complete integration pattern for external applications that need to:

1. Authorize users via OAuth 2.0 Authorization Code Flow with PKCE
2. Automatically refresh access tokens
3. Call Canvas Simple API endpoints to perform note operations

### Key Components

- **Application Handler**: Launches the web application in a new tab
- **HTML Application**: Single-page application with OAuth flow and note management UI
- **API Endpoints**: RESTful API for note operations (lock, sign, unlock, check-in, no-show)

---

## OAuth 2.0 Setup

### Step 1: Create an OAuth Application in Canvas

1. Log in to your Canvas instance as an administrator
2. Navigate to **Settings > Integrations > OAuth Applications**
3. Click **Create Application**
4. Configure the application:
   - **Name**: `Note Management App` (or your preferred name)
   - **Client Type**: `Public` (for browser-based apps that cannot securely store client secrets)
   - **Authorization Grant Type**: `Authorization Code`
   - **Redirect URIs**: Add your application's redirect URI
     - For production: `https://your-instance.canvasmedical.com/plugin-io/api/note_sign_api/app`
   - **Scopes**: Add `offline_access` (this allows the app to receive refresh tokens)

5. **Save** the application
6. Copy the **Client ID** - you'll need this in the next step

### Step 2. Install the Plugin

```bash
canvas install note_management_app/note_management_app --secret client_id=<YOUR_CLIENT_ID>
```

### OAuth Flow Details

#### Authorization Code Flow with PKCE

This application implements the OAuth 2.0 Authorization Code Flow with Proof Key for Code Exchange (PKCE), which is the recommended flow for public clients (browser-based applications).

**Why PKCE?**
- Protects against authorization code interception attacks
- No client secret needed (suitable for public clients)
- More secure for browser-based applications

**Flow Steps:**

1. **Generate Code Verifier and Challenge**
   ```javascript
   // Generate a random string (43-128 characters)
   const codeVerifier = generateRandomString(128);

   // Create SHA-256 hash and base64url encode
   const codeChallenge = await generateCodeChallenge(codeVerifier);
   ```

2. **Authorization Request**
   ```shell
   GET /auth/authorize/?
     response_type=code&
     client_id={CLIENT_ID}&
     redirect_uri={REDIRECT_URI}&
     scope=offline_access&
     code_challenge={CODE_CHALLENGE}&
     code_challenge_method=S256&
     launch=e30K
   ```

   **Parameters:**
   - `response_type=code`: Request an authorization code
   - `client_id`: Your application's client ID
   - `redirect_uri`: Where Canvas will redirect after authorization
   - `scope=offline_access`: Request a refresh token for long-lived access
   - `code_challenge`: Base64url-encoded SHA-256 hash of the code verifier
   - `code_challenge_method=S256`: Indicates SHA-256 hashing
   - `launch=e30K`: Launch context (base64-encoded empty JSON object `{}`)

3. **User Authorization**
   - User is redirected to Canvas login/authorization page
   - User authenticates and authorizes the application
   - Canvas redirects back to `redirect_uri` with an authorization code

4. **Token Exchange**
   ```javascript
   POST /auth/token/
   Content-Type: application/x-www-form-urlencoded

   grant_type=authorization_code&
   code={AUTHORIZATION_CODE}&
   redirect_uri={REDIRECT_URI}&
   client_id={CLIENT_ID}&
   code_verifier={CODE_VERIFIER}
   ```

   **Response:**
   ```json
   {
     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
     "refresh_token": "6KHq3fjkSWQ1vaBbF6WHG9...",
     "token_type": "Bearer",
     "expires_in": 36000,
     "scope": "offline_access"
   }
   ```

   **Token Lifetimes:**
   - **Access Token**: Valid for 10 hours (36,000 seconds)
   - **Refresh Token**: Non-expiring, single-use token

5. **Token Refresh**
   ```javascript
   POST /auth/token/
   Content-Type: application/x-www-form-urlencoded

   grant_type=refresh_token&
   refresh_token={REFRESH_TOKEN}&
   client_id={CLIENT_ID}&
   scope=offline_access
   ```

   **Response:** Returns new access token and new refresh token

---

## Plugin Architecture

### Directory Structure

```shell
note_sign_api/
├── handlers/
│   ├── __init__.py
│   ├── api.py              # API endpoints for note operations
│   ├── application.py       # Application handler
├── templates/
│   └── note_management_app.html  # HTML application
├── CANVAS_MANIFEST.json
└── README.md
```

### Component Overview

#### 1. Application Handler (`handlers/application.py`)

The Application handler launches the web application when triggered:

```python
from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.application import Application


class NoteManagementApplication(Application):
    """External note management application with OAuth integration."""

    def on_open(self) -> Effect:
        """Handle the application open event.

        Launches the note management application in a new window.
        """
        # Build the URL to the API endpoint that serves the HTML
        # Using relative path - Canvas will resolve to the correct instance
        app_url = "/plugin-io/api/note_sign_api/app"

        return LaunchModalEffect(
            url=app_url,
            target=LaunchModalEffect.TargetType.NEW_WINDOW,
        ).apply()
```


#### 2. App API Handler (`handlers/api.py` - AppApi class)

Serves the HTML application:

```python
from http import HTTPStatus

from canvas_sdk.effects import Effect
from canvas_sdk.effects.note import Note
from canvas_sdk.effects.simple_api import HTMLResponse, JSONResponse, Response
from canvas_sdk.handlers.simple_api import Credentials, SimpleAPI, api
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import Note as NoteModel


class AppApi(SimpleAPI):
    """API handler for serving the note management application."""

    PREFIX = ""

    def authenticate(self, credentials: Credentials) -> bool:
        """Allow access without authentication.
        The OAuth flow will handle authentication within the app.
        """
        return True

    @api.get("/app")
    def note_management_app(self) -> list[Response | Effect]:
        """Serve the note management application HTML."""
        # Get the Canvas instance URL from the request Host header
        host = self.request.headers.get("Host", "localhost:8000")

        # Determine protocol based on host
        if "localhost" in host or "127.0.0.1" in host:
            canvas_instance = f"http://{host}"
        else:
            canvas_instance = f"https://{host}"

        # Render the HTML template with context
        context = {"canvas_instance": canvas_instance}

        return [
            HTMLResponse(
                render_to_string("templates/note_management_app.html", context),
                status_code=HTTPStatus.OK,
            )
        ]
```

#### 3. Note API Handler (`handlers/api.py` - NoteApi class)

Provides RESTful API endpoints for note operations:

```python
from http import HTTPStatus

from canvas_sdk.effects import Effect
from canvas_sdk.effects.note import Note
from canvas_sdk.effects.simple_api import HTMLResponse, JSONResponse, Response
from canvas_sdk.handlers.simple_api import Credentials, SimpleAPI, api
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import Note as NoteModel

class NoteApi(SimpleAPI):
    """API handler for note-related operations."""

    PREFIX = "/notes"

    def authenticate(self, credentials: Credentials) -> bool:
        """Authenticate requests."""
        return self.event.actor.instance is not None

    @api.post("/<id>/lock")
    def lock_note(self) -> list[Response | Effect]:
        """Lock a note."""
        note_id = self.request.path_params["id"]

        try:
            note_instance = NoteModel.objects.get(id=note_id)
        except NoteModel.DoesNotExist:
            return [
                JSONResponse(
                    {"error": "Note not found."},
                    status_code=404,
                )
            ]

        note = Note(instance_id=note_instance.id)
        return [note.lock()]
```

---

## Implementation Details

#### Key JavaScript Functions

##### PKCE Implementation

```javascript
// Generate random string for code verifier
function generateRandomString(length) {
    const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
    let result = '';
    const randomValues = new Uint8Array(length);
    crypto.getRandomValues(randomValues);
    for (let i = 0; i < length; i++) {
        result += charset[randomValues[i] % charset.length];
    }
    return result;
}

// Generate code challenge from verifier
async function generateCodeChallenge(codeVerifier) {
    const encoder = new TextEncoder();
    const data = encoder.encode(codeVerifier);
    const hash = await crypto.subtle.digest('SHA-256', data);
    const base64 = btoa(String.fromCharCode(...new Uint8Array(hash)));
    return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}
```

##### OAuth Initiation

```javascript
async function initiateOAuth() {
    // Generate PKCE values
    const codeVerifier = generateRandomString(128);
    const codeChallenge = await generateCodeChallenge(codeVerifier);

    // Store verifier for token exchange
    sessionStorage.setItem('code_verifier', codeVerifier);

    // Build authorization URL
    const authUrl = `${CANVAS_INSTANCE}/auth/authorize/?` +
        `response_type=code` +
        `&client_id=${encodeURIComponent(CLIENT_ID)}` +
        `&redirect_uri=${encodeURIComponent(REDIRECT_URI)}` +
        `&scope=${encodeURIComponent(SCOPES)}` +
        `&code_challenge=${codeChallenge}` +
        `&code_challenge_method=S256` +
        `&launch=${LAUNCH_CONTEXT}`;

    // Redirect to Canvas authorization
    window.location.href = authUrl;
}
```

##### Token Exchange

```javascript
async function handleAuthCallback() {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');

    if (code) {
        const codeVerifier = sessionStorage.getItem('code_verifier');

        const response = await fetch(`${CANVAS_INSTANCE}/auth/token/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                grant_type: 'authorization_code',
                code: code,
                redirect_uri: REDIRECT_URI,
                client_id: CLIENT_ID,
                code_verifier: codeVerifier
            })
        });

        const data = await response.json();
        saveTokens(data);

        // Clean up
        window.history.replaceState({}, document.title, window.location.pathname);
        sessionStorage.removeItem('code_verifier');

        updateUI();
    }
}
```

##### Token Storage and Refresh

```javascript
function saveTokens(tokenData) {
    localStorage.setItem(ACCESS_TOKEN_KEY, tokenData.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokenData.refresh_token);

    // Calculate expiry time
    const expiryTime = Date.now() + (tokenData.expires_in * 1000);
    localStorage.setItem(TOKEN_EXPIRY_KEY, expiryTime.toString());

    // Schedule refresh 5 minutes before expiry
    scheduleTokenRefresh(tokenData.expires_in - 300);
}

async function refreshAccessToken() {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);

    const response = await fetch(`${CANVAS_INSTANCE}/auth/token/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            grant_type: 'refresh_token',
            refresh_token: refreshToken,
            client_id: CLIENT_ID
        })
    });

    const data = await response.json();
    saveTokens(data);
    showSuccess('Access token refreshed automatically');
}
```

##### API Calls

```javascript
async function performAction(action) {
    const noteId = document.getElementById('noteId').value.trim();
    const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);

    const actionMap = {
        'lock': '/lock',
        'sign': '/sign',
        'unlock': '/unlock',
        'lock_sign': '/lock_sign',
        'checkin': '/checkin',
        'noshow': '/noshow'
    };

    const endpoint = actionMap[action];

    const response = await fetch(
        `${CANVAS_INSTANCE}/plugins/note_sign_api/notes/${noteId}${endpoint}`,
        {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        }
    );

    if (!response.ok) {
        // Handle errors, possibly refresh token if 401
        if (response.status === 401) {
            await refreshAccessToken();
        }
    }
}
```

---

## API Endpoints

### Base URL

All plugin API endpoints are prefixed with:
```shell
https://your-instance.canvasmedical.com/plugin-io/api/note_sign_api/
```

### Available Endpoints

#### 1. Serve Application

```shell
GET /app
```

**Description**: Serves the HTML application

---

#### 2. Lock Note

```shell
POST /notes/<note_id>/lock
```

**Description**: Locks a note to prevent further editing

---

#### 3. Sign Note

```shell
POST /notes/<note_id>/sign
```

**Description**: Signs a note (if signature is required)

---

#### 4. Lock and Sign Note

```shell
POST /notes/<note_id>/lock_sign
```

**Description**: Locks and signs a note in one operation

---

#### 5. Unlock Note

```shell
POST /notes/<note_id>/unlock
```

**Description**: Unlocks a previously locked or signed note

---

#### 6. Check In

```shell
POST /notes/<note_id>/checkin
```

**Description**: Marks an appointment as checked in

---

#### 7. No Show

```shell
POST /notes/<note_id>/noshow
```

**Description**: Marks an appointment as no-show

---

## Security Considerations

### 1. Token Storage

**Current Implementation**: Tokens are stored in `localStorage`

**Considerations**:
- `localStorage` is vulnerable to XSS attacks
- For production, consider using:
  - HTTP-only cookies (requires backend support)
  - Session storage (cleared when tab closes)
  - Encrypted storage solutions

### 2. PKCE Protection

- PKCE prevents authorization code interception attacks
- Code verifier is stored in `sessionStorage` (temporary)
- Code challenge is sent to authorization server
- Server verifies verifier matches challenge during token exchange

### 3. Token Refresh

- Refresh tokens are single-use (Canvas rotates them)
- Access tokens are short-lived (10 hours)
- Automatic refresh happens before expiry
- Failed refresh triggers re-authentication

### 4. API Authentication

> **⚠️ Important**: The current implementation relies on the OAuth-authenticated user from Canvas. This is a simplified example for demonstration purposes.

**Current Implementation**:
```python
from canvas_sdk.handlers.simple_api import Credentials
def authenticate(self, credentials: Credentials) -> bool:
    return self.event.actor.instance is not None
```

This basic authentication check verifies that there is an authenticated Canvas user making the request.

**Production Recommendations**:

See the official documentation for supported authentication mechanisms: [Canvas SDK Authentication Guide](https://docs.canvasmedical.com/sdk/handlers-simple-api-http/#authentication)

---

## Additional Resources

- [Canvas Customer Authentication Documentation](https://docs.canvasmedical.com/api/customer-authentication/)
- [OAuth 2.0 Authorization Code Flow](https://oauth.net/2/grant-types/authorization-code/)
- [PKCE RFC 7636](https://tools.ietf.org/html/rfc7636)
