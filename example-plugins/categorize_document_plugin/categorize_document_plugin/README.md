Categorize Document Plugin

Example plugin that demonstrates how to use the CATEGORIZE_DOCUMENT effect to categorize documents in the Data Integration queue into specific document types.

Overview

This plugin listens for DOCUMENT_RECEIVED events and automatically categorizes documents into specific document types. This is useful for automated document processing workflows where an LLM system or other classification logic identifies the document type from the document's content.

Features

- Listens to DOCUMENT_RECEIVED events
- Emits CATEGORIZE_DOCUMENT effect to categorize documents
- Uses exact UUID keys from available_document_types
- Includes nested confidence scores for monitoring/debugging

How It Works

When a document is received, the CategorizeDocumentHandler is triggered:

1. Extracts the document ID from event.context["document"]["id"]
2. Finds matching document type from event.context["available_document_types"]
3. Emits CATEGORIZE_DOCUMENT effect with:
   - document_id: The UUID from document.id
   - document_type: Dict with key, name, report_type, template_type from available_document_types
   - confidence_scores: Optional nested confidence scores for monitoring/debugging

Example Usage

When a document is received:

```json
{
  "document": {
    "id": "47fc2fac-d736-4cc0-bd98-ee476632e4a8"
  },
  "available_document_types": [
    {
      "key": "f605e084dcad4beca16c0f62e6586d76",
      "name": "Lab Report",
      "report_type": "CLINICAL",
      "template_type": "LabReportTemplate"
    }
  ]
}
```

The plugin will emit:

```json
{
  "type": "CATEGORIZE_DOCUMENT",
  "payload": "{\"document_id\": \"47fc2fac-d736-4cc0-bd98-ee476632e4a8\", \"document_type\": {\"key\": \"f605e084dcad4beca16c0f62e6586d76\", \"name\": \"Lab Report\", \"report_type\": \"CLINICAL\", \"template_type\": \"LabReportTemplate\"}, \"confidence_scores\": {\"document_id\": 0.90, \"document_type\": {\"key\": 0.90, \"name\": 0.95, \"report_type\": 0.85, \"template_type\": 0.90}}}"
}
```

**Note**: The payload is at the root level, not wrapped in a "data" key.

Testing

To test this plugin:

1. Ensure the plugin is registered in your Canvas instance
2. Send a DOCUMENT_RECEIVED event with a document
3. Verify the document is categorized with the appropriate document type

Notes

- All document_type fields must come from the same entry in available_document_types
- The confidence score is for monitoring/debugging only, not used in categorization logic
- This is a simple example - you can add custom logic to determine the document type
