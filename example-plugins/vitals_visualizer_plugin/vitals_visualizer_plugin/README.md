=============================
Vitals Visualizer Plugin
=============================

A Canvas plugin that displays a "Visualize" button in the vitals section of the chart summary and shows interactive vital signs visualizations.

## Structure

```
vitals_visualizer_plugin/
├── handlers/
│   ├── __init__.py
│   ├── vitals_button.py      # Action button handler
│   └── vitals_api.py         # API endpoint with visualization
├── templates/
│   └── vitals_visualization.html # HTML template for visualization UI
├── CANVAS_MANIFEST.json      # Plugin configuration
└── README.md                 # Documentation
```

## Features

- Adds a "Visualize" button to the vitals section of the chart summary
- When clicked, opens a modal in the right chart pane displaying:
  - Dropdown selector for vital signs (weight, body temperature, o2sat)
  - Interactive line graph with modern styling and tooltips
  - Tabular display of the same data below the chart
  - Shows all historical vital signs data

## Vital Signs Supported

- **Weight**: Patient weight measurements over time
- **Body Temperature**: Temperature readings with different measurement sites
- **Oxygen Saturation (O2Sat)**: Oxygen saturation percentage readings
