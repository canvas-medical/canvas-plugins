# Note Management App Plugin

A comprehensive Canvas Medical plugin demonstrating external application integration with OAuth 2.0 authentication for note management operations.

> **⚠️ IMPORTANT: This is a Proof of Concept / Example Plugin**
>
> This plugin is designed for **demonstration and learning purposes only**. It showcases how to build external applications with OAuth 2.0 integration for Canvas Medical but **should not be used in production environments** without proper security hardening, testing, and validation.

## Description

This plugin provides:

1. **RESTful API Endpoints** for note operations:
   - Lock notes
   - Sign notes
   - Unlock notes
   - Check-in appointments
   - Mark appointments as no-show
   - Fetch recent notes with status

2. **External Web Application** with OAuth 2.0 integration:
   - Authorization Code Flow with PKCE
   - Automatic token refresh
   - Real-time notes table with patient information
   - Dynamic action buttons based on note state
   - User-friendly interface for note management

3. **Action Buttons** for quick note operations within Canvas UI

## Features

- **Secure OAuth 2.0 Authentication**: Implements Authorization Code Flow with PKCE for secure, browser-based authentication
- **Automatic Token Refresh**: Access tokens are automatically refreshed before expiration
- **External Application**: Opens in a new tab with full note management capabilities
- **Real-time Notes Dashboard**: Displays 10 most recent notes with patient names, status, and available actions
- **Smart Action Buttons**: Contextual actions based on note state (Created, Unlocked, Locked, Signed)
- **RESTful API**: Clean API design for programmatic access

## Quick Start

> **Note**: This is for development and learning purposes only.

### 1. Set Up OAuth Application

1. Log in to Canvas as administrator
2. Go to **Settings > Integrations > OAuth Applications**
3. Create a new application:
   - **Client Type**: Public
   - **Authorization Grant Type**: Authorization Code
   - **Redirect URI**: `https://your-instance.canvasmedical.com/plugin-io/api/note_management_app/app`
   - **Scopes**: `offline_access`
4. Copy the **Client ID**


### 2. Install the Plugin

```bash
canvas install note_management_app/note_management_app --secret client_id=<YOUR_CLIENT_ID>
```

### 3. Launch the Application

- Open Canvas
- Navigate to the app drawer or settings
- Click "Note Management"
- Authenticate and start managing notes

## Documentation

For comprehensive documentation including:
- Detailed OAuth 2.0 setup instructions
- Plugin architecture explanation
- API endpoint specifications
- Implementation details
- Security considerations

**See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)**

## API Endpoints

All endpoints are available at: `https://your-instance.canvasmedical.com/plugin-io/api/note_management_app`

| Endpoint                | Method | Description                                           |
|-------------------------|--------|-------------------------------------------------------|
| `/app`                  | GET    | Serve the note management application                 |
| `/notes/recent`         | GET    | Get 10 most recent notes with patient info and status |
| `/notes/<id>/lock`      | POST   | Lock a note                                           |
| `/notes/<id>/sign`      | POST   | Sign a note                                           |
| `/notes/<id>/lock_sign` | POST   | Lock and sign a note                                  |
| `/notes/<id>/unlock`    | POST   | Unlock a note                                         |
| `/notes/<id>/checkin`   | POST   | Check-in appointment                                  |
| `/notes/<id>/noshow`    | POST   | Mark appointment as no-show                           |

### Note States and Available Actions

The application intelligently determines which actions are available based on the note's current state:

| Note State   | Available Actions                   | Description                               |
|--------------|-------------------------------------|-------------------------------------------|
| **Created**  | Lock, Lock & Sign (if sig required) | Newly created notes                       |
| **Unlocked** | Lock, Lock & Sign (if sig required) | Notes that have been unlocked for editing |
| **Locked**   | Unlock, Sign (if sig required)      | Notes that are locked but not yet signed  |
| **Signed**   | Amend (Unlock)                      | Notes that have been signed and locked    |

## Components

### Application Handler
`handlers/application.py` - Launches the external web application

### API Handlers
`handlers/api.py` - Provides:
- `AppApi`: Serves the HTML application
- `NoteApi`: RESTful API for note operations

### HTML Application
`templates/note_management_app.html` - Single-page application with:
- OAuth 2.0 authentication flow with PKCE
- Real-time notes table displaying recent notes
- Patient information and note status
- Dynamic action buttons based on note state
- Automatic token refresh
- Modern, responsive UI

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                        Canvas Medical                      │
│  ┌────────────────┐                    ┌─────────────────┐ │
│  │  Application   │                    │  OAuth Server   │ │
│  │  Launcher      │                    │                 │ │
│  └────────┬───────┘                    └────────┬────────┘ │
│           │                                     │          │
│           │ Opens in new window                 │          │
│           ▼                                     │          │
│  ┌──────────────────────────────────────┐       │          │
│  │  HTML Application (/app)             │       │          │
│  │  ┌────────────────────────────────┐  │       │          │
│  │  │ OAuth Flow with PKCE           │◄─┼───────┘          │
│  │  └────────────────────────────────┘  │                  │
│  │  ┌────────────────────────────────┐  │                  │
│  │  │ Recent Notes Table             │  │                  │
│  │  │ - Patient Name                 │  │                  │
│  │  │ - Note Status (Created,        │  │                  │
│  │  │   Unlocked, Locked, Signed)    │  │                  │
│  │  │ - Dynamic Action Buttons       │  │                  │
│  │  └────────────┬───────────────────┘  │                  │
│  └───────────────┼──────────────────────┘                  │
│                  │                                         │
│                  │ API calls with Bearer token             │
│                  ▼                                         │
│  ┌─────────────────────────────────────────────────┐       │
│  │  Note API (/notes/*)                            │       │
│  │  - recent: list notes with status               │       │
│  │  - lock, sign, unlock, checkin, noshow          │       │
│  └─────────────────────────────────────────────────┘       │
└────────────────────────────────────────────────────────────┘
```



## Development

### Project Structure
```
note_management_app/
├── assets/
│   └── note_icon.png       # Application icon
├── handlers/
│   ├── __init__.py
│   ├── api.py              # API endpoints (AppApi + NoteApi)
│   └── application.py      # Application launcher
├── templates/
│   └── note_management_app.html  # HTML application with OAuth and notes table
├── CANVAS_MANIFEST.json    # Plugin configuration
├── INTEGRATION_GUIDE.md    # Comprehensive documentation
└── README.md              # This file
```

### Key Implementation Details

**Note State Management**
The API returns human-readable display states ("Created", "Unlocked", "Locked", "Signed") using `get_state_display()` for better UX.

**Smart Action Logic**
Action buttons are dynamically generated based on:
- Current note state
- Whether signature is required (`is_sig_required` from note type)
