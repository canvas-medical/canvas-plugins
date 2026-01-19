# Data Integration Example Plugin

This example plugin demonstrates how to use all available Data Integration effects to process documents in the Data Integration queue.

## Overview

When a document enters the Data Integration queue, this plugin:

1. Responds to the `DOCUMENT_RECEIVED` event
2. Checks the event context for action flags to determine which effects to apply
3. Creates and returns the appropriate Data Integration effects:
   - **LINK_DOCUMENT_TO_PATIENT**: Link documents to patients using patient key
   - **JUNK_DOCUMENT**: Mark documents as junk/spam
   - **REMOVE_DOCUMENT_FROM_PATIENT**: Remove/unlink documents from patients
   - **ASSIGN_DOCUMENT_REVIEWER**: Assign a reviewer (staff or team) to documents

## How It Works

The handler reads action flags from the event context:

- `context.link_to_patient` - Creates a `LinkDocumentToPatient` effect
- `context.mark_as_junk` - Creates a `JunkDocument` effect
- `context.remove_from_patient` - Creates a `RemoveDocumentFromPatient` effect
- `context.assign_reviewer` - Creates an `AssignDocumentReviewer` effect


## Quick Start

1. **Link a document to a patient:**
   ```json
   {
     "event": {
       "type": "DOCUMENT_RECEIVED",
       "target": { "id": "12345" },
       "context": {
         "link_to_patient": {
           "patient_key": "5e4e107888564e359e1b3592e08f502f"
         }
       }
     }
   }
   ```

2. **Mark a document as junk:**
   ```json
   {
     "event": {
       "type": "DOCUMENT_RECEIVED",
       "target": { "id": "12345" },
       "context": {
         "mark_as_junk": { "confidence": 0.90 }
       }
     }
   }
   ```

3. **Remove a document from a patient:**
   ```json
   {
     "event": {
       "type": "DOCUMENT_RECEIVED",
       "target": { "id": "12345" },
       "context": {
         "remove_from_patient": {
           "patient_id": "patient-123",
           "confidence": 0.85
         }
       }
     }
   }
   ```

4. **Assign a reviewer to a document:**
   ```json
   {
     "event": {
       "type": "DOCUMENT_RECEIVED",
       "target": { "id": "12345" },
       "context": {
         "assign_reviewer": {
           "reviewer_id": "staff-uuid",
           "team_id": "team-uuid",
           "priority": "HIGH",
           "review_mode": "REVIEW_REQUIRED",
           "confidence_scores": {
             "document_id": 0.95
           }
         }
       }
     }
   }
   ```


## Available Effects

### 1. LINK_DOCUMENT_TO_PATIENT

Links a document to a patient using the patient's key. The plugin is responsible for finding/matching the patient and providing their key.

```python
from canvas_sdk.effects.data_integration import LinkDocumentToPatient
from canvas_sdk.v1.data import Patient

# Fetch patient (in production, this would come from patient matching logic)
patient = Patient.objects.first()

effect = LinkDocumentToPatient(
    document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",  # Required: IntegrationTask UUID
    patient_key=str(patient.id),                         # Required: patient's key (32-char hex string)
    annotations=[                                        # Optional: display annotations
        {"text": "AI 95%", "color": "#00AA00"},
        {"text": "DOB matched", "color": "#2196F3"},
    ],
    source_protocol="llm_v1",                            # Optional: protocol/plugin identifier
)
```

**Fields:**
- `document_id` (str/int, required): The IntegrationTask UUID to link
- `patient_key` (str, required): The patient's key (32-character hex string, not a UUID)
- `annotations` (list[dict], optional): Display annotations with `text` and `color` fields
- `source_protocol` (str, optional): Protocol/plugin identifier for tracking

**Behavior:**
- Looks up the patient by key
- Links the document to that patient
- Creates an IntegrationTaskPrefill record with patient data and annotations
- Raises ValidationError if patient or document doesn't exist

### 2. JUNK_DOCUMENT

Marks a document in the Data Integration queue as junk (spam).

```python
from canvas_sdk.effects.data_integration import JunkDocument

effect = JunkDocument(
    document_id="12345",         # Required: IntegrationTask ID
    confidence_scores={          # Optional: confidence score for monitoring
        "junk": 0.90,
    },
)
```

**Fields:**
- `document_id` (str/int, required): The IntegrationTask ID to mark as junk
- `confidence_scores` (dict, optional): Confidence score for the junk decision (0.0-1.0)

**Behavior:**
- Validates the document exists
- Marks the document as junk by setting IntegrationTask.status to "JUN" (JUNK constant)
- Documents marked as junk are excluded from normal processing workflows

### 3. REMOVE_DOCUMENT_FROM_PATIENT

Removes/unlinks a document from a patient in the Data Integration queue.

```python
from canvas_sdk.effects.data_integration import RemoveDocumentFromPatient

effect = RemoveDocumentFromPatient(
    document_id="12345",         # Required: IntegrationTask ID
    patient_id="patient-123",    # Optional: specific patient ID to unlink
    confidence_scores={          # Optional: confidence score for monitoring
        "removal": 0.85,
    },
)
```

**Fields:**
- `document_id` (str/int, required): The IntegrationTask ID to unlink
- `patient_id` (str, optional): Specific patient ID to unlink. If not provided, removes current patient association
- `confidence_scores` (dict, optional): Confidence score for the removal decision (0.0-1.0)

**Behavior:**
- Finds the document by document_id
- Removes the patient association from the document
- Optionally filters by patient_id if multiple patients could be linked

### 4. ASSIGN_DOCUMENT_REVIEWER

Assigns a reviewer (staff member or team) to a document in the Data Integration queue.

```python
from canvas_sdk.effects.data_integration import AssignDocumentReviewer, Priority, ReviewMode

effect = AssignDocumentReviewer(
    document_id="12345",         # Required: IntegrationTask ID
    reviewer_id="staff-uuid",    # Optional: Staff member key to assign as reviewer
    team_id="team-uuid",         # Optional: Team UUID to assign as reviewer
    priority=Priority.HIGH,       # Optional: Priority level (NORMAL or HIGH), defaults to NORMAL
    review_mode=ReviewMode.REVIEW_REQUIRED,  # Optional: Review mode, defaults to REVIEW_REQUIRED
    confidence_scores={          # Optional: confidence score for monitoring
        "document_id": 0.95,
    },
)
```

**Fields:**
- `document_id` (str/int, required): The IntegrationTask ID to assign a reviewer to
- `reviewer_id` (str, optional): Staff member key to assign as reviewer. At least one of `reviewer_id` or `team_id` must be provided
- `team_id` (str, optional): Team UUID to assign as reviewer. At least one of `reviewer_id` or `team_id` must be provided
- `priority` (Priority, optional): Priority level - `Priority.NORMAL` or `Priority.HIGH`, defaults to `Priority.NORMAL`
- `review_mode` (ReviewMode, optional): Review mode - `ReviewMode.REVIEW_REQUIRED`, `ReviewMode.ALREADY_REVIEWED`, or `ReviewMode.REVIEW_NOT_REQUIRED`, defaults to `ReviewMode.REVIEW_REQUIRED`
- `confidence_scores` (dict, optional): Confidence score for the assignment decision (0.0-1.0)

**Review Modes:**
- `REVIEW_REQUIRED`: Document requires review (default)
- `ALREADY_REVIEWED`: Document has already been reviewed
- `REVIEW_NOT_REQUIRED`: Document does not require review

**Behavior:**
- Validates the document exists
- Assigns either a staff member or team as the reviewer
- Sets the priority level for the review
- Configures the review mode based on document status
- At least one of `reviewer_id` or `team_id` must be provided

## How It Works

1. When a document is received, the `DataIntegrationHandler` is triggered
2. The handler demonstrates how to create each type of effect:
   - Fetches first available patient for `LinkDocumentToPatient` (in production, would use patient matching)
   - Determines if document is junk (simulated) for `JunkDocument`
   - Determines if document should be removed (simulated) for `RemoveDocumentFromPatient`
   - Fetches first available staff/team for `AssignDocumentReviewer`
3. Returns a list of effects to apply

## Implementation Notes

This is an **example plugin** that demonstrates the structure and usage of Data Integration effects. In a production implementation, you would:

1. **Match Patient** (for `LinkDocumentToPatient`):
   - Fetch the document content
   - Use an LLM or OCR system to extract patient demographics from the document
   - Use the extracted demographics to find matching patients in the system
   - Handle confidence scores returned by the matching system
   - Implement retry logic or manual review workflows for ambiguous matches

2. **Classify Documents** (for `JunkDocument`):
   - Analyze the document content
   - Use an LLM or classification model to determine if it's junk/spam
   - Return confidence scores for monitoring/debugging

3. **Determine Document Removal** (for `RemoveDocumentFromPatient`):
   - Check if document is incorrectly linked to a patient
   - Determine which patient link to remove
   - Handle cases where multiple patients might be linked

4. **Assign Reviewers** (for `AssignDocumentReviewer`):
   - Determine appropriate reviewer based on document type, specialty, or workload
   - Assign to staff member or team based on routing rules
   - Set priority level based on document urgency
   - Configure review mode based on document status

## Confidence Scores

All effects support optional `confidence_scores` for monitoring and debugging:

- **LinkDocumentToPatient**: Scores for `first_name`, `last_name`, `date_of_birth`
- **JunkDocument**: Score for `junk` decision
- **RemoveDocumentFromPatient**: Score for `removal` decision
- **AssignDocumentReviewer**: Score for `document_id` assignment

Confidence scores are logged by the interpreters and can be used for:
- Monitoring extraction/classification accuracy
- Debugging issues with document processing
- Building analytics dashboards

## Testing

To test this plugin:

1. Ensure the plugin is registered in your Canvas instance
2. Send a `DOCUMENT_RECEIVED` event with a document
3. Verify the appropriate effects are applied based on your implementation logic
