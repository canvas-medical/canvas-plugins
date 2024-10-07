manifest_schema = {
    "type": "object",
    "properties": {
        "sdk_version": {"type": "string"},
        "plugin_version": {"type": "string"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "secrets": {"type": "array", "items": {"type": "string"}},
        "components": {
            "type": "object",
            "properties": {
                "commands": {"$ref": "#/$defs/component"},
                "protocols": {"$ref": "#/$defs/component"},
                "content": {"$ref": "#/$defs/component"},
                "effects": {"$ref": "#/$defs/component"},
                "views": {"$ref": "#/$defs/component"},
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
    "$defs": {
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
        }
    },
}
