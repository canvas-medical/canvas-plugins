fullscript
==========

## Description

This plugin integrates Canvas with Fullscript, allowing healthcare providers to seamlessly prescribe supplements and manage treatment plans within the Canvas platform.

At a high level, this plugin:
1. Embeds the Fullscript catalog application directly in the Canvas patient chart using their JavaScript SDK
2. Implements OAuth2 authentication flow with token caching and automatic refresh
3. Integrates Fullscript supplements into Canvas medication search (both medication statements and prescribe commands)
4. Syncs Fullscript treatment plans back to Canvas as medication statements
5. Creates and links Fullscript patient records with Canvas patients via external identifiers
6. Groups Fullscript supplements in the medication section of the patient chart
7. Supports prescribing Fullscript supplements directly from Canvas

### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it
gets updated if you add, remove, or rename protocols.
