# Male Blood Pressure Screening Plugin - Installation Guide

## Overview

This Canvas plugin provides blood pressure screening recommendations for male patients aged 18-39 years, following USPSTF (US Preventive Services Task Force) guidelines.

## Features

- **Target Population**: Male patients between 18-39 years old
- **Clinical Guidelines**: Based on USPSTF recommendations for blood pressure screening
- **Screening Frequency**: Recommends screening every 2-3 years
- **Integration**: Uses Canvas protocol cards to display recommendations
- **Event Triggers**: Activates on patient updates and encounter creation

## Installation

1. **Copy Plugin Files**: Copy the entire `male_bp_screening_plugin` directory to your Canvas instance's plugin directory.

2. **Install via Canvas CLI**: Use the Canvas CLI to install the plugin:
   ```bash
   canvas-cli plugin install ./male_bp_screening_plugin
   ```

3. **Configuration**: The plugin uses the `CANVAS_MANIFEST.json` configuration file which defines:
   - Two protocol handlers
   - Required data access permissions
   - Event triggers

## Plugin Components

### Protocols

1. **MaleBPScreeningProtocol**
   - Triggers on: `PATIENT_UPDATED` events
   - Checks patient eligibility (male, age 18-39)
   - Evaluates if screening is due (>2 years since last screening)
   - Generates protocol card with recommendations

2. **MaleBPScreeningEncounterProtocol**
   - Triggers on: `ENCOUNTER_CREATED` events
   - Provides encounter-based screening reminders
   - Displays protocol card during patient visits

### Protocol Card Features

- **Title**: "Blood Pressure Screening Recommended"
- **Clinical Context**: Explains USPSTF guidelines and rationale
- **Recommendations**:
  - Button to document blood pressure measurement
  - Link to USPSTF guidelines
  - Structured command integration

## Validation

Run the validation script to verify plugin integrity:

```bash
python validate_bp_plugin.py
```

This validates:
- Plugin file structure
- CANVAS_MANIFEST.json format
- Protocol code syntax
- Age calculation logic

## Customization

### Screening Intervals
To modify screening frequency, update the `_is_screening_due()` method in `bp_screening_protocol.py`:

```python
# Change from 2 years to 3 years
cutoff_date = datetime.now() - timedelta(days=1095)  # 3 years
```

### Target Age Range
To modify the eligible age range, update the `_is_eligible_for_screening()` method:

```python
# Change from 18-39 to 20-40
return 20 <= age <= 40
```

### Additional Triggers
Add more event types to the `RESPONDS_TO` field to trigger on additional events.

## Data Access

The plugin requires the following data access permissions:
- **Read**: Patient demographics, vital signs, encounter data
- **Write**: Protocol card creation and updates

## Support

For issues or questions:
1. Check the validation script output
2. Review Canvas SDK documentation
3. Verify data access permissions
4. Check Canvas instance logs

## Technical Details

- **SDK Version**: 0.1.4
- **Plugin Version**: 1.0.0
- **Language**: Python 3.12+
- **Dependencies**: Canvas SDK, Django, Pydantic