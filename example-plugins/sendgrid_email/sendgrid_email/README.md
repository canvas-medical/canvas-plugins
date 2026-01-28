# SendGrid Email Plugin

A Canvas plugin that enables sending emails, retrieving sent email logs, and managing inbound/outbound webhooks using the SendGrid API.

## Features

- **Send Emails**: Send emails with support for CC, inline images, and attachments
- **Email Logs**: Query sent emails with filters and retrieve detailed email events
- **Inbound Webhook**: Configure SendGrid to parse incoming emails
- **Outbound Webhook**: Configure SendGrid to send email status events (delivered, opened, clicked, etc.)
- **Event Caching**: Store and retrieve the latest webhook events for display

## Components

### Protocol: `EmailManip`

A SimpleAPI handler that exposes REST endpoints for SendGrid operations.

**API Endpoints:**

| Method | Endpoint | Description | SDK Method |
|--------|----------|-------------|------------|
| POST | `/send_email` | Send an email with optional attachments | `simple_send` |
| POST | `/emails_sent` | Query sent emails with filters | `logged_emails` |
| GET | `/email_events/<message_id>` | Get events for a specific email | `logged_email` |
| GET | `/inbound_webhook` | Get inbound parse webhook status | `parser_setting_list` |
| POST | `/inbound_webhook` | Enable/disable inbound parse webhook | `parser_setting_add` / `parser_setting_delete` |
| GET | `/outbound_webhook` | Get outbound event webhook status | `event_webhook_list` |
| POST | `/outbound_webhook` | Enable/disable outbound event webhook | `event_webhook_add` / `event_webhook_delete` |
| GET | `/inbound_email` | Retrieve cached inbound emails |  |
| POST | `/inbound_email` | Receive parsed inbound emails from SendGrid | _(webhook receiver)_ |
| GET | `/outbound_email_status` | Retrieve cached email status events |  |
| POST | `/outbound_email_status` | Receive email status events from SendGrid | _(webhook receiver)_ |

### Application: `EmailFormApp`

A patient-specific application that launches a right side panel interface for:

- Composing and sending emails
- Viewing sent email history and events
- Managing webhook configurations
- Viewing received inbound emails and outbound status events

## Configuration

### Required Secrets

Configure this secret in your Canvas plugin settings:

| Secret Name | Description |
|-------------|-------------|
| `SendgridAPIKey` | SendGrid API Key with Mail Send and Email Activity permissions |

## Installation

1. Install the plugin via the command line: `canvas install email_sender`
2. Configure the required secret with your SendGrid API key (`https://xxxx.canvasmedical.com/admin/plugin_io/plugin/`)
3. Access the application from a patient's chart in the drawer menu

## Usage

1. Open a patient chart
2. Launch the "Emails Sendgrid" application
3. Use the interface to send emails, view logs, or configure webhooks

### Webhook Setup

**Inbound Email Parsing:**
- Enable the inbound webhook via the application interface
- Configure your domain's MX records to point to SendGrid
- SendGrid will parse incoming emails and POST them to your Canvas instance

**Outbound Event Tracking:**
- Enable the outbound webhook via the application interface
- SendGrid will send status events (delivered, opened, clicked, bounced, etc.) to your Canvas instance

## SendGrid API Permissions

Ensure your API key has the following permissions:

- **Mail Send**: Full Access
- **Email Activity**: Read Access
- **Inbound Parse**: Full Access (for inbound webhook)
- **Webhook Settings**: Full Access (for outbound webhook)

## Important Note

The `CANVAS_MANIFEST.json` is used when installing your plugin. Please ensure it gets updated if you add, remove, or rename protocols.
