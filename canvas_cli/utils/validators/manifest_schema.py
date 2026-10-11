manifest_schema = {
    "type": "object",
    "properties": {
        "sdk_version": {"type": "string"},
        "plugin_version": {"type": "string"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "variables": {
            "description": "Plugin variables. Each entry has a name, an optional sensitive flag (default false), and an optional default value. Sensitive variables are write-only.",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "sensitive": {"type": "boolean", "default": False},
                    "default": {"type": "string"},
                },
                "required": ["name"],
                "additionalProperties": False,
                "if": {"properties": {"sensitive": {"const": True}}, "required": ["sensitive"]},
                "then": {"not": {"required": ["default"]}},
            },
        },
        "secrets": {
            "description": "Deprecated: use 'variables' with sensitive=true instead.",
            "type": "array",
            "items": {"type": "string"},
        },
        "origins": {"$ref": "#/$defs/origins"},
        "url_permissions": {"$ref": "#/$defs/url_permissions"},
        "components": {
            "type": "object",
            "properties": {
                "commands": {"$ref": "#/$defs/commands"},
                "protocols": {"$ref": "#/$defs/component"},
                "handlers": {"$ref": "#/$defs/component"},
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
        "custom_data": {"$ref": "#/$defs/custom_data"},
        "catalog": {"$ref": "#/$defs/catalog"},
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
                                "CLIPBOARD_READ",
                                "CLIPBOARD_WRITE",
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
                        "additionalProperties": False,
                    },
                },
                "required": ["class", "description"],
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
                    "scope": {
                        "type": "string",
                        "enum": [
                            "patient_specific",
                            "global",
                            "provider_menu_item",
                            "portal_menu_item",
                            "provider_companion",
                            "provider_companion_global",
                            "provider_companion_patient_specific",
                            "provider_companion_note_specific",
                            "full_chart",
                        ],
                    },
                    "menu_position": {
                        "type": "string",
                        "enum": ["top", "bottom"],
                    },
                    "menu_order": {"type": "integer"},
                    "show_in_panel": {"type": "boolean"},
                    "panel_priority": {"type": "integer"},
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
        "commands": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "label": {"type": "string"},
                    "schema_key": {"type": "string"},
                    "section": {
                        "type": "string",
                        "enum": [
                            "subjective",
                            "objective",
                            "assessment",
                            "plan",
                            "procedures",
                            "history",
                            "internal",
                        ],
                    },
                },
                "required": ["name", "schema_key"],
                "additionalProperties": False,
            },
        },
        "custom_data": {
            "type": "object",
            "properties": {
                "namespace": {
                    "type": "string",
                    "pattern": "^[a-z][a-z0-9_]*__[a-z][a-z0-9_]*$",
                    "maxLength": 63,
                    "description": "Namespace name in format 'org__name' (double underscore separator)",
                },
                "access": {
                    "type": "string",
                    "enum": ["read", "read_write"],
                    "description": "Access level: 'read' for read-only, 'read_write' for full access",
                },
            },
            "required": ["namespace", "access"],
            "additionalProperties": False,
        },
        "catalog": {
            "description": (
                "The plugin's listing in the Canvas Platform plugin catalog. Listing copy "
                "ships only from the repository, so the catalog and the running code cannot "
                "disagree. Platform enforces the same rules when the plugin is pushed "
                "(plugins/manifest.py in canvas-medical/platform), and the two copies change "
                "together."
            ),
            "type": "object",
            "properties": {
                "title": {
                    "description": "What the plugin is called on its card and its page.",
                    "$ref": "#/$defs/catalog_text",
                    "maxLength": 64,
                },
                "kind": {
                    "description": "'agent' calls a model and acts with latitude; 'plugin' is deterministic.",
                    "enum": ["agent", "plugin"],
                    "default": "plugin",
                },
                "category": {
                    "enum": [
                        "Billing & RCM",
                        "Charting",
                        "Decision support",
                        "Interoperability",
                        "Labs & devices",
                        "Operations",
                        "Patient engagement",
                        "Population health",
                        "Prescribing",
                        "Scheduling",
                    ],
                },
                "surfaces": {
                    "description": "Every place in Canvas the plugin's work shows up.",
                    "type": "array",
                    "items": {
                        "enum": [
                            "Note",
                            "Chart app",
                            "Command",
                            "Background",
                            "Patient portal",
                            "Waffle",
                        ]
                    },
                    "minItems": 1,
                    "uniqueItems": True,
                },
                "keywords": {
                    "description": "Free search terms, distinct from the fixed 'tags' taxonomy.",
                    "type": "array",
                    "items": {"type": "string", "pattern": r"^[a-z0-9][a-z0-9-]{0,31}$"},
                },
                "screenshots": {
                    "description": "Images inside the package folder, in display order.",
                    "type": "array",
                    "maxItems": 8,
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "description": "Ends in .png, .jpg, .jpeg or .webp, in lowercase.",
                                "type": "string",
                                "pattern": r"^(?!/)(?!.*\.\.)[^\\]+\.(?:png|jpe?g|webp)$",
                            },
                            "caption": {"type": "string", "maxLength": 40},
                            "alt": {"$ref": "#/$defs/catalog_text", "maxLength": 200},
                        },
                        "required": ["path", "alt"],
                        "additionalProperties": False,
                    },
                },
                "agent": {
                    "description": "What an agent decides and what it is not allowed to.",
                    "type": "object",
                    "properties": {
                        "does": {"$ref": "#/$defs/catalog_text"},
                        "does_not": {"$ref": "#/$defs/catalog_text"},
                        "runs_when": {"$ref": "#/$defs/catalog_text"},
                        "models": {
                            "type": "array",
                            "items": {"type": "string", "minLength": 1},
                            "minItems": 1,
                        },
                    },
                    "required": ["does", "does_not", "runs_when", "models"],
                    "additionalProperties": False,
                },
                "integration": {
                    "description": "Present when the plugin is an integration; 'unit' names what its volume counts.",
                    "type": "object",
                    "properties": {"unit": {"$ref": "#/$defs/catalog_text"}},
                    "required": ["unit"],
                    "additionalProperties": False,
                },
                "setup_instructions": {
                    "description": "Path inside the package folder to the file Studio's agent reads when an organization installs the plugin.",
                    "$ref": "#/$defs/catalog_path",
                },
                "release_notes": {
                    "description": "What changed in this plugin_version.",
                    "type": "object",
                    "properties": {
                        "kind": {"enum": ["fix", "performance", "breaking"]},
                        "title": {"$ref": "#/$defs/catalog_text"},
                        "body": {"type": "string"},
                    },
                    "required": ["kind", "title"],
                    "additionalProperties": False,
                },
                "pricing": {"$ref": "#/$defs/catalog_pricing"},
            },
            "required": ["title", "category", "surfaces"],
            "additionalProperties": False,
            "allOf": [
                {
                    "description": "An agent states its boundary; a deterministic plugin has none.",
                    "if": {"properties": {"kind": {"const": "agent"}}, "required": ["kind"]},
                    "then": {"required": ["agent"]},
                    "else": {"not": {"required": ["agent"]}},
                }
            ],
        },
        "catalog_text": {
            "description": "Text with at least one character that is not whitespace.",
            "type": "string",
            "pattern": r"\S",
        },
        "catalog_path": {
            "description": "A path inside the package folder: no leading '/', no '..' anywhere, no backslash.",
            "type": "string",
            "pattern": r"^(?!/)(?!.*\.\.)[^\\]+$",
        },
        "catalog_pricing": {
            "description": (
                "Canvas's price book for the plugin, the same for every organization. Three "
                "independent questions: what Canvas charges (canvas_fee), what a vendor charges "
                "(vendor_fee), and where the plugin's model calls are billed (model_use)."
            ),
            "type": "object",
            "properties": {
                "canvas_fee": {"$ref": "#/$defs/catalog_canvas_fee"},
                "vendor_fee": {"$ref": "#/$defs/catalog_vendor_fee"},
                "model_use": {
                    "description": (
                        "'included_in_unit_price' goes through a Canvas credential not invoiced "
                        "per token; 'organization_tokens' through the organization's own "
                        "inference keys; 'none' calls no model."
                    ),
                    "type": "object",
                    "properties": {
                        "billed_as": {
                            "enum": ["included_in_unit_price", "organization_tokens", "none"]
                        }
                    },
                    "required": ["billed_as"],
                    "additionalProperties": False,
                },
            },
            "required": ["canvas_fee", "vendor_fee", "model_use"],
            "additionalProperties": False,
            "allOf": [
                {
                    "description": "Model calls inside the price need a price to put them inside.",
                    "if": {
                        "properties": {
                            "model_use": {
                                "properties": {"billed_as": {"const": "included_in_unit_price"}}
                            }
                        }
                    },
                    "then": {
                        "properties": {
                            "canvas_fee": {"properties": {"model": {"const": "per_unit"}}}
                        }
                    },
                },
                {
                    "description": "A per-unit price includes the plugin's model calls, so they never also appear as tokens.",
                    "if": {
                        "properties": {
                            "canvas_fee": {"properties": {"model": {"const": "per_unit"}}}
                        }
                    },
                    "then": {
                        "properties": {
                            "model_use": {
                                "properties": {
                                    "billed_as": {"enum": ["included_in_unit_price", "none"]}
                                }
                            }
                        }
                    },
                },
            ],
        },
        "catalog_canvas_fee": {
            "oneOf": [
                {
                    "description": "Covered by the Canvas subscription. No line on any invoice.",
                    "type": "object",
                    "properties": {"model": {"const": "included"}},
                    "required": ["model"],
                    "additionalProperties": False,
                },
                {
                    "description": "Billed by Canvas per unit of work on the Agentic plugins meter.",
                    "type": "object",
                    "properties": {
                        "model": {"const": "per_unit"},
                        "unit": {
                            "description": "Both forms, for '$0.40 per visit' and '1,750 visits'.",
                            "type": "object",
                            "properties": {
                                "singular": {"$ref": "#/$defs/catalog_text"},
                                "plural": {"$ref": "#/$defs/catalog_text"},
                            },
                            "required": ["singular", "plural"],
                            "additionalProperties": False,
                        },
                        "meter": {
                            "type": "object",
                            "properties": {
                                "key": {
                                    "description": "The meter name each usage record carries.",
                                    "type": "string",
                                    "pattern": r"^[a-z][a-z0-9_.]*$",
                                },
                                "billable_stages": {
                                    "description": "Instance stages whose units are billed; units on other stages are rated at zero.",
                                    "type": "array",
                                    "items": {
                                        "enum": ["sandbox", "development", "staging", "production"]
                                    },
                                    "minItems": 1,
                                    "uniqueItems": True,
                                },
                                "aggregation": {"const": "organization_month"},
                            },
                            "required": ["key", "billable_stages", "aggregation"],
                            "additionalProperties": False,
                        },
                        "schedule": {
                            "description": "List price over time, oldest first. Platform checks ordering and contiguity.",
                            "type": "array",
                            "items": {"$ref": "#/$defs/catalog_price_version"},
                            "minItems": 1,
                        },
                    },
                    "required": ["model", "unit", "meter", "schedule"],
                    "additionalProperties": False,
                },
            ]
        },
        "catalog_price_version": {
            "type": "object",
            "properties": {
                "id": {
                    "description": "Pinned on every invoice line rated under this version.",
                    "type": "string",
                    "minLength": 1,
                },
                "effective_from": {"$ref": "#/$defs/catalog_month_start"},
                "effective_to": {
                    "description": "Exclusive. Null while open-ended.",
                    "oneOf": [{"$ref": "#/$defs/catalog_month_start"}, {"type": "null"}],
                },
                "bands": {
                    "description": "Graduated volume bands, ascending. A flat price is one band with up_to null.",
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "up_to": {"type": ["integer", "null"], "minimum": 1},
                            "unit_price": {
                                "description": "Integer USD nanocents: $0.40 is 40000000000.",
                                "type": "integer",
                                "minimum": 0,
                            },
                        },
                        "required": ["up_to", "unit_price"],
                        "additionalProperties": False,
                    },
                    "minItems": 1,
                },
            },
            "required": ["id", "effective_from", "effective_to", "bands"],
            "additionalProperties": False,
        },
        "catalog_vendor_fee": {
            "description": "A partner's own charge for its service. Null when the vendor charges nothing beyond Canvas.",
            "oneOf": [
                {"type": "null"},
                {
                    "type": "object",
                    "properties": {
                        "basis": {
                            "enum": [
                                "included",
                                "usage",
                                "subscription",
                                "per_claim",
                                "per_transaction",
                                "per_page",
                                "per_seat",
                                "per_query",
                            ]
                        },
                        "billed_by": {"enum": ["vendor", "canvas_pass_through"]},
                        "pass_through_service": {"type": ["string", "null"]},
                    },
                    "required": ["basis", "billed_by"],
                    "additionalProperties": False,
                    "if": {"properties": {"billed_by": {"const": "canvas_pass_through"}}},
                    "then": {
                        "required": ["pass_through_service"],
                        "properties": {"pass_through_service": {"type": "string"}},
                    },
                },
            ],
        },
        "catalog_month_start": {
            "description": "The first day of a month, so one billing period is never rated under two prices.",
            "type": "string",
            "pattern": r"^[0-9]{4}-(0[1-9]|1[0-2])-01$",
        },
    },
}
