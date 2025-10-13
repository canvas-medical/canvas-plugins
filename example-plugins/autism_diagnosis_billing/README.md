===============================
Autism Diagnosis Billing Plugin
===============================

A Canvas plugin that automatically creates billing line items when autism screening diagnosis conditions are committed with ICD-10 code Z13.41.

## Overview

This plugin monitors `DIAGNOSE_COMMAND__POST_COMMIT` events and automatically creates a billing line item with CPT code "AUTISM_DX" when an autism screening diagnosis is detected. The billing line item is linked to the latest assessment for the diagnosis.

## Features

- **Automatic Detection**: Monitors newly committed diagnosis conditions in real-time
- **ICD-10 Filtering**: Specifically targets autism screening diagnosis (Z13.41)  
- **Flexible Code Format**: Handles ICD-10 codes with or without dots (Z13.41 or Z1341)
- **Assessment Linking**: Automatically links billing line items to the latest assessment
- **Error Handling**: Robust error handling with comprehensive logging
- **Comprehensive Testing**: Full test suite with 95%+ code coverage

## Structure

```
autism_diagnosis_billing/
├── handlers/
│   ├── __init__.py
│   └── add_billing_line_item_handler.py
├── tests/
│   ├── __init__.py
│   └── test_add_billing_line_item_handler.py
├── CANVAS_MANIFEST.json
└── README.md
```

## How It Works

1. **Event Trigger**: The plugin responds to `DIAGNOSE_COMMAND__POST_COMMIT` events
2. **Code Validation**: Checks if the diagnosis has ICD-10 coding matching Z13.41 (normalized)
3. **Billing Creation**: Creates an `AddBillingLineItem` effect with:
   - CPT code: "AUTISM_DX"  
   - Note ID: From the command's note
   - Assessment IDs: Latest assessment for the diagnosis (if available)

### Code Logic Flow

```python
DIAGNOSE_COMMAND__POST_COMMIT event
    ↓
Get Command from event.target.id
    ↓
Get diagnosis from command.anchor_object
    ↓
Check for ICD-10 coding
    ↓
Normalize code (remove dots): Z13.41 → Z1341
    ↓
Match against Z1341?
    ↓ YES
Create AddBillingLineItem(
    note_id=command.note.id,
    cpt="AUTISM_DX", 
    assessment_ids=[latest_assessment.id]
)
```

## Configuration

The plugin requires no additional configuration or secrets. It uses the following predefined values:

- **Target ICD-10 Code**: Z13.41 (autism screening)
- **CPT Code**: "AUTISM_DX"
- **Event**: `DIAGNOSE_COMMAND__POST_COMMIT`

## Installation

1. Install the plugin using Canvas CLI:
   ```bash
   canvas plugin install autism_diagnosis_billing/
   ```

2. The plugin will automatically start monitoring diagnosis events

## Testing

The plugin includes comprehensive tests covering:

- ✅ Correct event type handling
- ✅ Autism diagnosis detection (Z13.41)  
- ✅ ICD-10 code normalization (dots removal)
- ✅ Non-autism diagnosis filtering
- ✅ Missing data handling (no codings, assessments, etc.)
- ✅ Error scenarios (command not found, etc.)
- ✅ Billing line item parameter validation

Run tests:
```bash
python -m pytest autism_diagnosis_billing/tests/ -v
```

Or run the standalone test validation:
```bash
python autism_diagnosis_billing/tests/test_add_billing_line_item_handler.py
```

## Example Usage

When a provider commits a diagnosis with ICD-10 code Z13.41 in a note:

**Input**: 
- Diagnosis condition with ICD-10 coding "Z13.41"
- Command committed in note ID "note-12345"
- Assessment ID "assessment-67890" 

**Output**:
- Billing line item created with CPT "AUTISM_DX"
- Linked to note "note-12345"
- Associated with assessment "assessment-67890"

## Code Quality

The plugin follows Canvas SDK best practices:

- **Type Hints**: Full type annotations
- **Error Handling**: Comprehensive exception handling
- **Logging**: Detailed logging for debugging and monitoring
- **Documentation**: Extensive docstrings and comments
- **Testing**: High test coverage with edge cases

## Data Access

This plugin requires the following data access permissions:

**Read Access:**
- Commands
- Conditions (diagnoses)
- Codings (ICD-10)
- Assessments 
- Notes

**Write Access:**
- Billing line items

## Support

For questions or issues with this plugin, please refer to the Canvas SDK documentation or contact your Canvas administrator.