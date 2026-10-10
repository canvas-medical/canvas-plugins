from typing import Any

import jsonschema
import pytest
from jsonschema import ValidationError

from canvas_cli.utils.validators import validate_manifest_file


@pytest.fixture
def handler_manifest_example() -> dict:
    """Return a valid handler manifest example."""
    return {
        "sdk_version": "0.3.1",
        "plugin_version": "1.0.1",
        "name": "Prompt to prescribe when assessing condition",
        "description": "To assist in ....",
        "components": {
            "handlers": [
                {
                    "class": "prompt_to_prescribe.handlers.prompt_when_assessing.PromptWhenAssessing",
                    "description": "probably the same as the plugin's description",
                    "data_access": {
                        "event": "",
                        "read": ["conditions"],
                        "write": ["commands"],
                    },
                }
            ]
        },
        "tags": {"patient_sourcing_and_intake": ["symptom_triage"]},
        "references": [],
        "license": "",
        "diagram": False,
        "readme": "README.MD",
    }


def _make_application_manifest(scope: str) -> dict:
    """Return a valid manifest with a single application using the given scope."""
    return {
        "sdk_version": "0.1.4",
        "plugin_version": "0.0.1",
        "name": "test_plugin",
        "description": "A test plugin",
        "components": {
            "applications": [
                {
                    "class": "test_plugin.apps.my_app:MyApp",
                    "name": "My App",
                    "description": "A test application",
                    "scope": scope,
                    "icon": "assets/icon.png",
                }
            ]
        },
        "tags": {},
        "license": "",
        "readme": "README.md",
    }


def test_manifest_file_schema(handler_manifest_example: dict) -> None:
    """Test that no exception raised when a valid manifest file is validated."""
    validate_manifest_file(handler_manifest_example)


@pytest.mark.parametrize(
    "scope",
    [
        "provider_companion",
        "provider_companion_global",
        "provider_companion_patient_specific",
        "provider_companion_note_specific",
        "patient_specific",
        "global",
        "provider_menu_item",
        "portal_menu_item",
        "full_chart",
    ],
    ids=lambda s: s,
)
def test_manifest_validates_application_scope(scope: str) -> None:
    """Test that all supported application scopes pass manifest validation."""
    validate_manifest_file(_make_application_manifest(scope))


def test_manifest_rejects_invalid_application_scope() -> None:
    """Test that an unrecognized application scope fails manifest validation."""
    with pytest.raises(ValidationError, match="is not one of"):
        validate_manifest_file(_make_application_manifest("not_a_real_scope"))


def test_manifest_with_variables(handler_manifest_example: dict) -> None:
    """Test that variables array with name and sensitive fields validates."""
    handler_manifest_example["variables"] = [
        {"name": "OPENAI_API_KEY", "sensitive": True},
        {"name": "WEBHOOK_URL", "sensitive": False},
        {"name": "PLAIN_VAR"},
    ]
    validate_manifest_file(handler_manifest_example)


def test_manifest_with_legacy_secrets(
    handler_manifest_example: dict, capsys: pytest.CaptureFixture
) -> None:
    """Test that legacy secrets array still validates with a deprecation warning."""
    handler_manifest_example["secrets"] = ["MY_SECRET"]
    validate_manifest_file(handler_manifest_example)
    captured = capsys.readouterr()
    assert "deprecated" in captured.out.lower()


def test_manifest_with_empty_variables(handler_manifest_example: dict) -> None:
    """Test that an empty variables array validates."""
    handler_manifest_example["variables"] = []
    validate_manifest_file(handler_manifest_example)


def test_manifest_variable_with_default(handler_manifest_example: dict) -> None:
    """Test that non-sensitive variables can have a default value."""
    handler_manifest_example["variables"] = [
        {"name": "WEBHOOK_URL", "default": "https://example.com/webhook"},
        {"name": "RETRY_COUNT", "sensitive": False, "default": "3"},
    ]
    validate_manifest_file(handler_manifest_example)


def test_manifest_sensitive_variable_rejects_default(handler_manifest_example: dict) -> None:
    """Test that sensitive variables cannot have a default value."""
    handler_manifest_example["variables"] = [
        {"name": "API_KEY", "sensitive": True, "default": "secret123"},
    ]
    with pytest.raises(jsonschema.ValidationError):
        validate_manifest_file(handler_manifest_example)


def test_manifest_variable_rejects_extra_fields(handler_manifest_example: dict) -> None:
    """Test that variables with unknown fields are rejected."""
    handler_manifest_example["variables"] = [
        {"name": "KEY", "sensitive": True, "extra": "bad"},
    ]
    with pytest.raises(jsonschema.ValidationError):
        validate_manifest_file(handler_manifest_example)


def test_manifest_accepts_an_ordinary_application() -> None:
    """The application entry carries identity and an icon, and nothing about layout."""
    validate_manifest_file(_make_application_manifest("patient_specific"))


@pytest.mark.parametrize("name", ["intake", "acme__intake"])
def test_manifest_name_needs_no_publisher_prefix(name: str) -> None:
    """The schema accepts a name with or without a publisher prefix, so plugins installed with
    `canvas install` keep validating; only `canvas deploy` requires the prefix.
    """
    validate_manifest_file(_make_application_manifest("global") | {"name": name})


LISTING: dict[str, Any] = {
    "title": "Scribe",
    "kind": "agent",
    "category": "Charting",
    "surfaces": ["Note", "Command"],
    "keywords": ["ambient", "llm"],
    "screenshots": [{"path": "shots/chart.png", "caption": "In the chart", "alt": "A note"}],
    "agent": {
        "does": "Drafts commands.",
        "does_not": "Does not commit a draft.",
        "runs_when": "Note",
        "models": ["claude-sonnet-5"],
    },
    "integration": {"unit": "visits"},
    "setup_instructions": "setup_instructions.md",
    "setup_guide": "setup_guide.md",
    "icon": "assets/icon.png",
    "release_notes": {"kind": "fix", "title": "Cache transcripts", "body": "Cheaper."},
}

# The same cases, under the same ids, are in canvas-medical/platform's
# `plugins/tests/test_manifest.py`, which checks the copy of these rules Platform
# enforces when a plugin is pushed. Change both together: a listing `canvas validate`
# accepts and a push refuses, or the other way round, is a plugin nobody can publish.
MINIMAL: dict[str, Any] = {
    "title": "Claims",
    "category": "Billing & RCM",
    "surfaces": ["Background"],
}
AGENT: dict[str, Any] = LISTING["agent"]

ACCEPTED = {
    "full": LISTING,
    "minimal": MINIMAL,
    "no-keywords": {**MINIMAL, "keywords": []},
}

REFUSED = {
    "unknown-field": {**MINIMAL, "tagline": "x"},
    "missing-title": {"category": "Charting", "surfaces": ["Note"]},
    "blank-title": {**MINIMAL, "title": "   "},
    "long-title": {**MINIMAL, "title": "x" * 65},
    "missing-category": {"title": "No category", "surfaces": ["Note"]},
    "unknown-category": {**MINIMAL, "category": "Fun"},
    "no-surfaces": {**MINIMAL, "surfaces": []},
    "repeated-surface": {**MINIMAL, "surfaces": ["Note", "Note"]},
    "bad-keyword": {**MINIMAL, "keywords": ["Not OK"]},
    "agent-without-boundary": {**MINIMAL, "kind": "agent"},
    "plugin-with-boundary": {**MINIMAL, "agent": AGENT},
    "agent-extra-field": {**MINIMAL, "kind": "agent", "agent": {**AGENT, "budget": 3}},
    "screenshot-escapes": {**MINIMAL, "screenshots": [{"path": "../x.png", "alt": "a"}]},
    "double-dot-in-a-name": {**MINIMAL, "screenshots": [{"path": "shots/a..b.png", "alt": "a"}]},
    "screenshot-absolute": {**MINIMAL, "screenshots": [{"path": "/x.png", "alt": "a"}]},
    "screenshot-gif": {**MINIMAL, "screenshots": [{"path": "x.gif", "alt": "a"}]},
    "screenshot-uppercase": {**MINIMAL, "screenshots": [{"path": "x.PNG", "alt": "a"}]},
    "screenshot-no-alt": {**MINIMAL, "screenshots": [{"path": "x.png"}]},
    "screenshot-extra-field": {
        **MINIMAL,
        "screenshots": [{"path": "x.png", "alt": "a", "width": 3}],
    },
    "unknown-release-kind": {**MINIMAL, "release_notes": {"kind": "feature", "title": "t"}},
    "release-extra-field": {
        **MINIMAL,
        "release_notes": {"kind": "fix", "title": "t", "author": "me"},
    },
    "null-release-notes": {**MINIMAL, "release_notes": None},
    "setup-outside-package": {**MINIMAL, "setup_instructions": "/etc/passwd"},
    "setup-escapes": {**MINIMAL, "setup_instructions": "../setup.md"},
    "setup-guide-outside-package": {**MINIMAL, "setup_guide": "/etc/passwd"},
    "setup-guide-escapes": {**MINIMAL, "setup_guide": "../guide.md"},
    "null-setup-guide": {**MINIMAL, "setup_guide": None},
    "icon-escapes": {**MINIMAL, "icon": "../icon.png"},
    "icon-not-an-image": {**MINIMAL, "icon": "icon.svg"},
    "icon-uppercase": {**MINIMAL, "icon": "icon.PNG"},
    "null-icon": {**MINIMAL, "icon": None},
}


@pytest.mark.parametrize("catalog", ACCEPTED.values(), ids=ACCEPTED.keys())
def test_manifest_accepts_catalog_listing(handler_manifest_example: dict, catalog: dict) -> None:
    """Test that a well-formed catalog listing validates."""
    handler_manifest_example["catalog"] = catalog
    validate_manifest_file(handler_manifest_example)


@pytest.mark.parametrize("catalog", REFUSED.values(), ids=REFUSED.keys())
def test_manifest_rejects_malformed_catalog_listing(
    handler_manifest_example: dict, catalog: dict
) -> None:
    """Test that a malformed catalog listing fails manifest validation."""
    handler_manifest_example["catalog"] = catalog
    with pytest.raises(ValidationError):
        validate_manifest_file(handler_manifest_example)
