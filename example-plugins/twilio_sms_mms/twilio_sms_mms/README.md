# Twilio SMS/MMS Plugin

A Canvas Medical plugin that integrates Twilio SMS/MMS capabilities, demonstrating the Canvas SDK integration with Twilio.

## Description

This plugin provides a complete SMS/MMS communication solution using Twilio's API.
It includes a user-friendly interface for managing phone numbers, sending messages, viewing message history, and handling inbound/outbound message webhooks.

## Features

- **Send SMS/MMS Messages**: Send text messages from any of your Twilio phone numbers
- **Message History**: View sent and received messages with filtering by phone number and direction
- **Phone Number Management**: List all Twilio phone numbers with their capabilities and status
- **Webhook Configuration**: Configure inbound message webhooks for each phone number
- **Media Support**: View and manage MMS attachments (images, videos, audio)
- **Message Deletion**: Delete messages from Twilio records
- **Automatic Replies**: Built-in inbound message handler with auto-reply functionality
- **Status Callbacks**: Track message delivery status through callback webhooks

## Prerequisites

- Canvas Medical SDK version 0.85.0 or higher
- Active Twilio account with:
  - Account SID
  - API Key
  - API Secret
  - At least one active phone number with SMS/MMS capabilities

## Installation

1. Ensure the plugin is installed in your Canvas instance
2. Configure the required secrets in Canvas:
   - `TwilioAccountSID`: Your Twilio Account SID
   - `TwilioAPIKey`: Your Twilio API Key
   - `TwilioAPISecret`: Your Twilio API Secret

## Configuration

### Required Secrets

The plugin requires three secrets to be configured in Canvas:

| Secret Name | Description |
|-------------|-------------|
| `TwilioAccountSID` | Your Twilio Account SID (found in Twilio Console) |
| `TwilioAPIKey` | Your Twilio API Key |
| `TwilioAPISecret` | Your Twilio API Secret |

### Webhook URLs

The plugin can define several webhook endpoints and manage them:

- **Outbound Status Callback**: `https://{customer}.canvasmedical.com/plugin-io/api/twilio_sms_mms/outbound_api_status`
- **Inbound Message Handler**: `https://{customer}.canvasmedical.com/plugin-io/api/twilio_sms_mms/inbound_treatment`


## Usage

### Accessing the Application

The SMS Twilio application can be launched from within Canvas. It opens in the right chart pane and provides three main tabs:

#### 1. Log Tab

View message history for your Twilio phone numbers:
- Select a phone number from the dropdown
- Choose message direction (sent or received)
- Click on any message to view details
- View MMS attachments inline
- Delete messages using the trash icon

#### 2. Send Tab

Send new SMS messages:
- Select a "From" phone number
- Enter the recipient's phone number (E.164 format: +1234567890)
- Optionally specify a callback URL for delivery status
- Enter your message text
- Click "Send SMS"

#### 3. Phones Tab

Manage your Twilio phone numbers:
- View all phone numbers and their capabilities
- Check phone number status
- Configure inbound webhook URLs
- Set webhook HTTP method (GET or POST)

## API Endpoints

The plugin provides the following REST API endpoints:

### Phone Numbers

- `GET /phone_list` - Retrieve all phone numbers
  - Returns: List of phone numbers with capabilities and webhook configuration

### Messages

- `GET /message_list/<number>/<direction>` - List messages for a phone number
  - Parameters:
    - `number`: Phone number to filter by
    - `direction`: Either "from" or "to"
  - Returns: List of messages with SID, status, sent date, and media count

- `GET /message/<message_sid>` - Get message details
  - Parameters:
    - `message_sid`: Twilio message SID
  - Returns: Complete message details

- `GET /medias/<message_sid>` - Retrieve message media
  - Parameters:
    - `message_sid`: Twilio message SID
  - Returns: Media content with appropriate content type

- `DELETE /message_delete/<message_sid>` - Delete a message
  - Parameters:
    - `message_sid`: Twilio message SID
  - Returns: Deletion status

- `POST /sms_send` - Send an SMS message
  - Body:
    ```json
    {
      "numberFrom": "+1234567890",
      "numberFromSid": "PNXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
      "numberTo": "+1234567890",
      "callbackUrl": "https://example.com/callback",
      "text": "Your message text"
    }
    ```
  - Returns: Sent message details

### Webhooks

- `POST /inbound_webhook/<phone_sid>` - Configure inbound webhook
  - Parameters:
    - `phone_sid`: Phone number SID
  - Body:
    ```json
    {
      "url": "https://example.com/webhook",
      "method": "POST"
    }
    ```
  - Returns: Configuration result

- `POST /outbound_api_status` - Handle outbound message status callbacks
  - Body: Twilio status callback payload (form-encoded)
  - Returns: HTTP 200 OK

- `POST /inbound_treatment` - Handle inbound messages
  - Body: Twilio inbound message payload (form-encoded)
  - Returns: TwiML response with auto-reply

## Components

### Handlers

#### SmsManip (handlers/sms_manip.py)

REST API handler that provides all SMS/MMS management endpoints. Handles:
- Phone number listing
- Message sending and retrieval
- Media management
- Webhook configuration
- Status callbacks

#### SmsFormApp (handlers/sms_form_app.py)

Canvas Application handler that launches the SMS management UI.

### Constants

Configuration constants are defined in `constants/constants.py`:
- Twilio credential keys
- API route prefixes
- Environment variable names

## Auto-Reply Feature

The plugin includes a built-in auto-reply handler for inbound messages:

- Messages containing "hello" (case-insensitive) receive: "Hello! ♥️" with an image attachment
- Other messages receive: "Say hello! 👻"

This can be customized by modifying the `inbound_treatment` method in `handlers/sms_manip.py`.

## Development

### Project Structure

```
twilio_sms_mms/
├── __init__.py
├── CANVAS_MANIFEST.json
├── README.md
├── constants/
│   ├── __init__.py
│   └── constants.py
├── handlers/
│   ├── __init__.py
│   ├── sms_form_app.py
│   └── sms_manip.py
├── static/
│   └── twilio_sms_mms.png
└── templates/
    └── sms_form.html
```

### Authentication

The current implementation uses a simplified authentication mechanism that always returns `True`.

For production use, implement proper authentication in the `SmsManip.authenticate()` method.

## Troubleshooting

### Messages Not Sending

- Verify that your Twilio credentials are correct
- Check that the "From" phone number has SMS capabilities enabled
- Ensure the "To" number is in E.164 format (+1234567890)
- Check Twilio console for any account restrictions

### Webhooks Not Working

- Verify the webhook URL is publicly accessible
- Check that the URL matches your Canvas instance domain
- Ensure the phone number's webhook configuration is saved
- Review Twilio's webhook debugger in the console

### Media Not Displaying

- Verify the message has media attachments (mediaCount > 0)
- Check browser console for CORS or loading errors
- Ensure the media content type is supported

## Important Notes

- The CANVAS_MANIFEST.json is used when installing your plugin.
- Phone numbers must be in E.164 format (e.g., +1234567890)
- Message status callbacks require a publicly accessible URL
- Some Twilio features may require additional account configuration or verification

## Support

For issues or questions:
- Review Twilio's documentation at https://www.twilio.com/docs
- Check Canvas Medical SDK documentation at https://docs.canvasmedical.com/sdk/
