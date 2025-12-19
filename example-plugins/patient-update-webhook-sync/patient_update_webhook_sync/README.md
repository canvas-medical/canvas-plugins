patient-update-webhook-sync
===========================

## Description

This plugin automatically syncs patient updates to an external webhook endpoint and sends Slack notifications when the sync fails.

## How It Works

The plugin responds to `PATIENT_UPDATED` events in Canvas. When a patient record is updated, it:

1. Posts the patient's Canvas ID to the configured webhook endpoint
2. Logs the result of the sync operation
3. Sends a Slack notification if the webhook fails (connection error or non-2xx status code)

## Required Secrets

Configure these secrets when installing the plugin:

- `PARTNER_WEBHOOK_URL` - The external webhook endpoint URL to receive patient updates
- `PARTNER_API_KEY` - API key for authenticating with the webhook endpoint
- `SLACK_ENDPOINT_URL` - Slack webhook or API endpoint for error notifications
- `SLACK_API_KEY` - Bearer token for Slack API authentication

## Error Handling

The plugin handles two types of failures:

1. **Connection Errors**: Network issues or unreachable webhook endpoint
2. **HTTP Errors**: Non-2xx status codes from the webhook

In both cases, the plugin logs the error and sends a formatted Slack notification with:
- Patient Canvas ID
- Error details (truncated to 500 characters)
- HTTP status code (when applicable)

### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it
gets updated if you add, remove, or rename protocols.
