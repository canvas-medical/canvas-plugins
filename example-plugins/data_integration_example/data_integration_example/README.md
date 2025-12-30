# Data Integration Example Plugin

This example plugin demonstrates how to use all available Data Integration effects to process documents in the Data Integration queue.

## Overview

When a document enters the Data Integration queue, this plugin:

1. Responds to the `DOCUMENT_RECEIVED` event
2. Checks the event context for action flags to determine which effects to apply
3. Creates and returns the appropriate Data Integration effects:
   - **LINK_DOCUMENT_TO_PATIENT**: Link documents to patients based on demographics
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
           "first_name": "John",
           "last_name": "Doe",
           "date_of_birth": "1990-05-15"
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

Links a document to a patient based on patient demographics (first name, last name, date of birth).

```python
from datetime import date
from canvas_sdk.effects.data_integration import LinkDocumentToPatient

effect = LinkDocumentToPatient(
    first_name="John",           # Required: patient's first name
    last_name="Doe",             # Required: patient's last name
    date_of_birth=date(1990, 5, 15),  # Required: patient's DOB
    document_id="12345",         # Required: IntegrationTask ID
    confidence_scores={          # Optional: confidence scores for monitoring
        "first_name": 0.95,
        "last_name": 0.90,
        "date_of_birth": 0.85,
    },
)
```

**Fields:**
- `first_name` (str, required): Patient's first name (non-empty)
- `last_name` (str, required): Patient's last name (non-empty)
- `date_of_birth` (date, required): Patient's date of birth
- `document_id` (str/int, required): The IntegrationTask ID to link
- `confidence_scores` (dict, optional): Confidence scores for each field (0.0-1.0)

**Matching Logic:**
- Filters patients by demographics (case-insensitive names, exact date match)
- If exactly one patient matches, links the document to that patient
- If zero or multiple patients match, throws an exception

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
   - Extracts patient demographics (simulated) for `LinkDocumentToPatient`
   - Determines if document is junk (simulated) for `JunkDocument`
   - Determines if document should be removed (simulated) for `RemoveDocumentFromPatient`
   - Determines reviewer assignment (simulated) for `AssignDocumentReviewer`
3. Returns a list of effects to apply

## Implementation Notes

This is an **example plugin** that demonstrates the structure and usage of Data Integration effects. In a production implementation, you would:

1. **Extract Patient Demographics** (for `LinkDocumentToPatient`):
   - Fetch the document content
   - Use an LLM or OCR system to extract patient demographics
   - Handle confidence scores returned by the extraction system
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
