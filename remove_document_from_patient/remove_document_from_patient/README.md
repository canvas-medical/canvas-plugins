# Remove Document From Patient

## Description

API endpoint for removing/unlinking patients from documents in the Data Integration queue.

## API Endpoint

### POST /remove-document-from-patient

Removes/unlinks a patient association from a document in the Data Integration queue.

**Request Body:**
```json
{
    "document_id": 12345,
    "patient_id": 67890,
    "confidence_score": 0.95
}
```

**Required Fields:**
- `document_id` (int): The ID of the IntegrationTask/document
- `patient_id` (int): The ID of the patient (used for logging/audit)

**Optional Fields:**
- `confidence_score` (float): Confidence level between 0.0 and 1.0 (for monitoring/debugging)

**Response:**
```json
{
    "success": true,
    "message": "Patient 67890 removed from document 12345",
    "document_id": 12345,
    "patient_id": 67890
}
```

## Usage Examples

### Basic Request (curl)

```bash
curl -X POST /plugin-io/api/remove_document_from_patient/remove-document-from-patient \
     -H "Content-Type: application/json" \
     -d '{"document_id": 12345, "patient_id": 67890}'
```

### With Confidence Score

```bash
curl -X POST /plugin-io/api/remove_document_from_patient/remove-document-from-patient \
     -H "Content-Type: application/json" \
     -d '{"document_id": 12345, "patient_id": 67890, "confidence_score": 0.95}'
```

## Behavior

- The effect works regardless of whether the document is currently linked to a patient (no-op if not linked)
- On the home-app side, the interpreter will:
  1. Validate the document (IntegrationTask) exists
  2. Remove the patient link by setting `IntegrationTask.patient` to `null`

## Typical Use Cases

This API is typically called by LLM-based document processing systems when:
- The system determines a document should not be linked to a patient
- Automated document-to-patient unlinking workflows are triggered
- Document classification/routing logic determines incorrect patient association

## Error Responses

- `400 Bad Request`: Missing required fields or invalid parameter types
- `500 Internal Server Error`: Unexpected processing error
