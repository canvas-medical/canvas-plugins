# Junk Document Plugin

Example plugin that demonstrates how to use the `JUNK_DOCUMENT` effect to mark documents in the Data Integration queue as junk (spam).

## Overview

This plugin listens for `DOCUMENT_RECEIVED` events and automatically marks documents as junk. This is useful for filtering out spam, test documents, or unwanted content from the document processing workflow.

## Features

- Listens to `DOCUMENT_RECEIVED` events
- Emits `JUNK_DOCUMENT` effect to mark documents as junk

## How It Works

1. When a document is received, the `JunkDocumentHandler` is triggered
2. The handler extracts the document ID from the event context
3. Emits `JUNK_DOCUMENT` effect with:
   - `document_id`: The ID of the document to mark as junk

## Example Usage

When a document is received:

```json
{
  "document": {
    "id": "12345"
  }
}
```

The plugin will emit:

```json
{
  "type": "JUNK_DOCUMENT",
  "payload": "{\"data\": {\"document_id\": \"12345\"}}"
}
```

## Testing

To test this plugin:

1. Ensure the plugin is registered in your Canvas instance
2. Send a `DOCUMENT_RECEIVED` event with a document
3. Verify the document status is set to "JUN" (JUNK)

## Notes

- Documents marked as junk will be excluded from normal processing workflows
- This is a simple example - you can add custom logic to determine when to mark documents as junk
