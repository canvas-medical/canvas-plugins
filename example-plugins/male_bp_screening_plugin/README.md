# Male Blood Pressure Screening Plugin

A Canvas plugin to provide blood pressure screening recommendations for male patients aged 18-39 years, following USPSTF guidelines.

## Description

This plugin monitors male patients between ages 18-39 and displays protocol cards recommending blood pressure screening based on the US Preventive Services Task Force (USPSTF) guidelines. The plugin helps ensure appropriate screening intervals and promotes preventive care.

### Clinical Guidelines

Based on USPSTF recommendations for blood pressure screening in adults:
- Men aged 18-39 should be screened for high blood pressure at least every 2-3 years
- More frequent screening may be recommended for patients with elevated blood pressure or risk factors
- Screening helps identify hypertension early for timely intervention

### Events

This plugin responds to the following events:
- `PATIENT_UPDATED` - When patient demographics are updated
- `ENCOUNTER_CREATED` - When a new encounter is created

### Effects

This plugin creates the following effects:
- Protocol cards recommending blood pressure screening for eligible male patients

## Structure

```
male_bp_screening_plugin/
├── protocols/
│   ├── __init__.py
│   └── bp_screening_protocol.py
├── CANVAS_MANIFEST.json
├── README.md
├── validate_plugin.py
└── __init__.py
```

## Validation

This plugin includes a validation script to verify the plugin structure, manifest, and logic without requiring the full Canvas SDK environment.

### Running Validation

To validate the plugin, navigate to the plugin directory and run:

```bash
cd example-plugins/male_bp_screening_plugin
python validate_plugin.py
```

The validation script checks:
- Plugin file structure integrity
- CANVAS_MANIFEST.json validity  
- Protocol code syntax
- Age calculation logic accuracy

### Expected Output

When validation passes, you should see:

```
INFO: All validation checks passed!

Plugin Summary:
- Targets male patients aged 18-39
- Follows USPSTF blood pressure screening guidelines
- Recommends screening every 2-3 years
- Generates protocol cards with actionable recommendations
- Ready for installation in Canvas
```

### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it gets updated if you add, remove, or rename protocols.