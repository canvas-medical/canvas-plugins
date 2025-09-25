# Abnormal Lab Task Notification Plugin

This Canvas EMR plugin automatically creates task notifications whenever lab results with abnormal values are received, ensuring critical lab findings are flagged for prompt clinical review.

## What This Plugin Does

When lab results come into Canvas EMR, this plugin:

1. **Monitors all incoming lab reports** - Automatically checks every new lab report
2. **Identifies abnormal values** - Looks for lab values flagged as abnormal by the lab
3. **Creates immediate notifications** - Generates tasks that appear in your Canvas task list
4. **Prioritizes for review** - Labels tasks as "abnormal-lab" and "urgent-review" for easy filtering

## Why Use This Plugin

- **Never miss critical results** - Ensures abnormal lab values don't get overlooked
- **Saves time** - No manual checking required - the plugin does it automatically  
- **Improves patient safety** - Faster response to abnormal results leads to better care
- **Easy integration** - Works seamlessly with your existing Canvas workflow

## Example Scenario

**Without this plugin:**
- Lab results come in and sit in the lab section
- Providers must manually review all lab reports
- Abnormal values might be missed during busy periods

**With this plugin:**
- Lab results with abnormal values immediately generate tasks
- Tasks appear in your task list with clear titles like "Review Abnormal Lab Values (3 abnormal)"
- You can filter tasks by "abnormal-lab" label to see all abnormal results at once

## Task Details

When abnormal lab values are found, the plugin creates a task with:

- **Clear title** showing how many abnormal values were found
- **Patient association** so the task appears in the correct patient's workflow
- **Priority labels** ("abnormal-lab", "urgent-review") for easy filtering and sorting
- **Open status** ensuring the task requires attention

## Setup

This plugin requires no configuration - it works automatically once installed. It will:

- Monitor all lab reports (except test reports and junked reports)
- Create tasks only when abnormal values are present
- Associate tasks with the correct patient automatically

## Technical Details

**Event Triggered By:** New lab reports entering the Canvas system  
**Detection Method:** Checks the `abnormal_flag` field on lab values  
**Task Creation:** Uses Canvas SDK's AddTask effect  
**Labels Applied:** "abnormal-lab", "urgent-review"  

The plugin is designed to be safe and efficient:
- Filters out test-only and invalid lab reports
- Handles missing data gracefully
- Includes comprehensive error logging for troubleshooting