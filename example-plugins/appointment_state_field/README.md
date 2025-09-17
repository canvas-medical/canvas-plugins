Appointment State Field Plugin
==============================

## Description

This plugin adds a US state selection field to appointment forms and intelligently filters available providers based on their licensing in the selected state. This ensures that only providers who are licensed to practice in the chosen state are presented as options during appointment scheduling.

## Features

- **State Selection Field**: Adds a dropdown field with all 50 US states to appointment forms
- **Provider Filtering**: Automatically filters the list of available providers based on their medical licenses for the selected state
- **Seamless Integration**: Works with existing Canvas appointment forms without disrupting the current workflow

## How It Works

1. **Form Enhancement**: The plugin adds a "State" dropdown field to appointment forms with all US states as options
2. **Dynamic Provider Filtering**: When a state is selected, the system automatically filters providers to show only those with valid licenses in that state
3. **Real-time Updates**: Provider options update dynamically based on state selection without requiring page refreshes

## Technical Components

- `AppointmentFormFields`: Handler that adds the state selection field to appointment forms
- `AppointmentProviderFormField`: Handler that filters providers based on the selected state and their licensing information

### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it gets updated if you add, remove, or rename handlers.
