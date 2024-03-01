manifest_schema = {
    "type": "object",
    "properties": {
        "sdk_version": {"type": "string"},
        "plugin_version": {"type": "string"},
        "name": {"type": "string"},
        "description": {"type": "string"},
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
    },
    "required": ["sdk_version", "plugin_version", "name", "description", "components"],
    "additionalProperties": False,
    "$defs": {
        "component": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "class": {"type": "string"},
                    "description": {"type": "string"},
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
