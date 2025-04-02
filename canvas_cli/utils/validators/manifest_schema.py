manifest_schema = {
    "type": "object",
    "properties": {
        "sdk_version": {"type": "string"},
        "plugin_version": {"type": "string"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "secrets": {"type": "array", "items": {"type": "string"}},
        "origins": {"$ref": "#/$defs/origins"},
        "url_permissions": {"$ref": "#/$defs/url_permissions"},
        "components": {
            "type": "object",
            "properties": {
                "commands": {"$ref": "#/$defs/component"},
                "protocols": {"$ref": "#/$defs/component"},
                "content": {"$ref": "#/$defs/component"},
                "effects": {"$ref": "#/$defs/component"},
                "views": {"$ref": "#/$defs/component"},
                "applications": {"$ref": "#/$defs/applications"},
                "questionnaires": {"$ref": "#/$defs/questionnaires"},
            },
            "additionalProperties": False,
            "minProperties": 1,
        },
        "tags": {
            "type": "object",
            "properties": {
                "patient_sourcing_and_intake": {
                    "type": "array",
                    "items": {"enum": ["symptom_triage", "coverage_capture"]},
                },
                "interaction_modes_and_utilization": {
                    "type": "array",
                    "items": {"enum": ["supply_policies", "demand_policies", "auto_followup"]},
                },
                "diagnostic_range_and_inputs": {"type": "array", "items": {"enum": []}},
                "pricing_and_payments": {"type": "array", "items": {"enum": []}},
                "care_team_composition": {"type": "array", "items": {"enum": []}},
                "interventions_and_safety": {"type": "array", "items": {"enum": []}},
                "content": {"type": "array", "items": {"enum": ["patient_intake"]}},
            },
            "additionalProperties": False,
        },
        "references": {"type": "array", "items": {"type": "string"}},
        "license": {"type": "string"},
        "diagram": {"type": ["boolean", "string"]},
        "readme": {"type": ["boolean", "string"]},
    },
    "required": [
        "sdk_version",
        "plugin_version",
        "name",
        "description",
        "components",
        "tags",
        "license",
        "readme",
    ],
    "additionalProperties": False,
    "allOf": [{"not": {"required": ["url_permissions", "origins"]}}],
    "$defs": {
        "origins": {
            "type": "object",
            "properties": {
                "urls": {"type": "array", "items": {"type": "string"}},
                "scripts": {"type": "array", "items": {"type": "string"}},
            },
        },
        "url_permissions": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "url": {"type": "string"},
                    "permissions": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": [
                                "SCRIPTS",
                                "ALLOW_SAME_ORIGIN",
                                "MICROPHONE",
                                "CAMERA",
                            ],
                        },
                    },
                },
                "required": ["url", "permissions"],
            },
        },
        "component": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "class": {"type": "string"},
                    "description": {"type": "string"},
                    "meta": {"type": "object"},
                    "data_access": {
                        "type": "object",
                        "properties": {
                            "event": {"type": "string"},
                            "read": {"type": "array", "items": {"type": "string"}},
                            "write": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["event", "read", "write"],
                        "additionalProperties": False,
                    },
                },
                "required": ["class", "description", "data_access"],
                "additionalProperties": False,
            },
        },
        "applications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "class": {"type": "string"},
                    "name": {"type": "string", "maxLength": 32},
                    "description": {"type": "string", "maxLength": 256},
                    "icon": {"type": "string"},
                    "scope": {"type": "string", "enum": ["patient_specific", "global"]},
                },
                "required": ["class", "icon", "scope", "name", "description"],
                "additionalProperties": False,
            },
        },
        "questionnaires": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "template": {"type": "string"},
                },
                "required": ["template"],
                "additionalProperties": False,
            },
        },
    },
}
