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
    """The schema accepts a name with or without a publisher prefix."""
    validate_manifest_file(_make_application_manifest("global") | {"name": name})


def test_manifest_accepts_a_publisher() -> None:
    """A manifest may name the Canvas Platform organization that publishes it."""
    validate_manifest_file(_make_application_manifest("global") | {"publisher": "acme"})


def test_manifest_publisher_is_optional() -> None:
    """A manifest without a publisher validates."""
    assert "publisher" not in _make_application_manifest("global")
    validate_manifest_file(_make_application_manifest("global"))


def test_manifest_rejects_a_publisher_that_is_not_a_string() -> None:
    """The publisher is a slug, so a number is refused."""
    with pytest.raises(jsonschema.ValidationError):
        validate_manifest_file(_make_application_manifest("global") | {"publisher": 3})


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
    "pricing": [
        {"unit": "visit", "price_per_unit": "5.75"},
        {"unit": "token"},
    ],
    "vendors": [
        {"name": "Twilio", "relationship": "self_managed", "additional_fees": True},
    ],
    "setup_instructions": "setup_instructions.md",
    "setup_guide": "setup_guide.md",
    "icon": "assets/icon.png",
    "video": {
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "poster": "assets/video-poster.png",
        "caption": "Drafting a note",
    },
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
VIDEO: dict[str, Any] = {"url": "https://youtu.be/dQw4w9WgXcQ", "poster": "assets/poster.png"}

ACCEPTED = {
    "full": LISTING,
    "minimal": MINIMAL,
    "no-keywords": {**MINIMAL, "keywords": []},
    "sub-cent-price": {**MINIMAL, "pricing": [{"unit": "page", "price_per_unit": "0.0025"}]},
    "free-unit": {**MINIMAL, "pricing": [{"unit": "visit", "price_per_unit": "0"}]},
    "token-markup": {**MINIMAL, "pricing": [{"unit": "token", "markup_bps": 1500}]},
    "token-markup-zero": {**MINIMAL, "pricing": [{"unit": "token", "markup_bps": 0}]},
    "canvas-managed-vendor": {
        **MINIMAL,
        "vendors": [{"name": "Nabla", "relationship": "canvas_managed", "additional_fees": False}],
    },
    "video-watch-url": {
        **MINIMAL,
        "video": {**VIDEO, "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s"},
    },
    "video-short-link": {**MINIMAL, "video": {**VIDEO, "url": "https://youtu.be/dQw4w9WgXcQ?si=x"}},
    "video-embed-url": {
        **MINIMAL,
        "video": {**VIDEO, "url": "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ"},
    },
    "video-without-caption": {**MINIMAL, "video": VIDEO},
}

VISIT = {"unit": "visit", "price_per_unit": "5.75"}
VENDOR = {"name": "Twilio", "relationship": "self_managed", "additional_fees": True}

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
    "null-video": {**MINIMAL, "video": None},
    "video-no-url": {**MINIMAL, "video": {"poster": "assets/poster.png"}},
    "video-no-poster": {**MINIMAL, "video": {"url": VIDEO["url"]}},
    "video-poster-escapes": {**MINIMAL, "video": {**VIDEO, "poster": "../poster.png"}},
    "video-poster-not-an-image": {**MINIMAL, "video": {**VIDEO, "poster": "poster.gif"}},
    "video-not-youtube": {**MINIMAL, "video": {**VIDEO, "url": "https://vimeo.com/76979871"}},
    "video-http": {**MINIMAL, "video": {**VIDEO, "url": "http://youtu.be/dQw4w9WgXcQ"}},
    "video-short-id": {**MINIMAL, "video": {**VIDEO, "url": "https://youtu.be/dQw4w9WgXc"}},
    "video-long-id": {**MINIMAL, "video": {**VIDEO, "url": "https://youtu.be/dQw4w9WgXcQQ"}},
    "video-shorts": {
        **MINIMAL,
        "video": {**VIDEO, "url": "https://www.youtube.com/shorts/dQw4w9WgXcQ"},
    },
    "video-lookalike-host": {
        **MINIMAL,
        "video": {**VIDEO, "url": "https://youtu.be.example.com/dQw4w9WgXcQ"},
    },
    "video-extra-field": {**MINIMAL, "video": {**VIDEO, "autoplay": True}},
    "video-long-caption": {**MINIMAL, "video": {**VIDEO, "caption": "x" * 41}},
    "video-list": {**MINIMAL, "video": [VIDEO]},
    "video-playlist-embed": {
        **MINIMAL,
        "video": {**VIDEO, "url": "https://www.youtube.com/embed/videoseries?list=PL0123456789"},
    },
    "video-live-stream-embed": {
        **MINIMAL,
        "video": {**VIDEO, "url": "https://www.youtube.com/embed/live_stream?channel=UC0123"},
    },
    "integration-block": {**MINIMAL, "integration": {"unit": "visits"}},
    "empty-pricing": {**MINIMAL, "pricing": []},
    "null-pricing": {**MINIMAL, "pricing": None},
    "pricing-number": {**MINIMAL, "pricing": [{"unit": "visit", "price_per_unit": 5.75}]},
    "pricing-five-places": {**MINIMAL, "pricing": [{"unit": "visit", "price_per_unit": "0.00001"}]},
    "pricing-negative": {**MINIMAL, "pricing": [{"unit": "visit", "price_per_unit": "-1"}]},
    "pricing-no-price": {**MINIMAL, "pricing": [{"unit": "visit"}]},
    "pricing-no-unit": {**MINIMAL, "pricing": [{"price_per_unit": "1"}]},
    "pricing-long-unit": {**MINIMAL, "pricing": [{"unit": "x" * 41, "price_per_unit": "1"}]},
    "pricing-extra-field": {**MINIMAL, "pricing": [{**VISIT, "currency": "USD"}]},
    "pricing-repeated-unit": {**MINIMAL, "pricing": [VISIT, {**VISIT, "unit": "Visit"}]},
    "pricing-too-many": {
        **MINIMAL,
        "pricing": [{"unit": f"unit {n}", "price_per_unit": "1"} for n in range(11)],
    },
    "token-with-price": {**MINIMAL, "pricing": [{"unit": "token", "price_per_unit": "0.01"}]},
    "markup-on-unit": {**MINIMAL, "pricing": [{**VISIT, "markup_bps": 1500}]},
    "markup-too-high": {**MINIMAL, "pricing": [{"unit": "token", "markup_bps": 10_001}]},
    "markup-negative": {**MINIMAL, "pricing": [{"unit": "token", "markup_bps": -1}]},
    "markup-string": {**MINIMAL, "pricing": [{"unit": "token", "markup_bps": "1500"}]},
    "markup-boolean": {**MINIMAL, "pricing": [{"unit": "token", "markup_bps": True}]},
    "markup-null": {**MINIMAL, "pricing": [{"unit": "token", "markup_bps": None}]},
    "markup-float": {**MINIMAL, "pricing": [{"unit": "token", "markup_bps": 1500.0}]},
    "empty-vendors": {**MINIMAL, "vendors": []},
    "null-vendors": {**MINIMAL, "vendors": None},
    "vendor-unknown-relationship": {**MINIMAL, "vendors": [{**VENDOR, "relationship": "partner"}]},
    "vendor-fees-not-boolean": {**MINIMAL, "vendors": [{**VENDOR, "additional_fees": "yes"}]},
    "vendor-no-fees": {
        **MINIMAL,
        "vendors": [{"name": "Twilio", "relationship": "self_managed"}],
    },
    "vendor-no-name": {
        **MINIMAL,
        "vendors": [{"relationship": "self_managed", "additional_fees": False}],
    },
    "vendor-long-name": {**MINIMAL, "vendors": [{**VENDOR, "name": "x" * 65}]},
    "vendor-extra-field": {**MINIMAL, "vendors": [{**VENDOR, "url": "https://twilio.com"}]},
    "vendor-repeated": {**MINIMAL, "vendors": [VENDOR, {**VENDOR, "name": "twilio"}]},
    "vendors-too-many": {
        **MINIMAL,
        "vendors": [{**VENDOR, "name": f"Vendor {n}"} for n in range(11)],
    },
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


def _dependency(name: str = "scribe_core", **overrides: Any) -> dict:
    """Return a valid dependency entry, with any key overridden."""
    return {"name": name, "publisher": "canvas-medical", "version": "1.16.0", **overrides}


def _without(entry: dict, key: str) -> dict:
    """Return ``entry`` without ``key``."""
    return {k: v for k, v in entry.items() if k != key}


def _bundle_manifest(**overrides: Any) -> dict:
    """Return a valid bundle manifest, with any top-level key overridden."""
    return {
        "sdk_version": "0.260.0",
        "plugin_version": "2.0.0",
        "name": "scribe",
        "description": "A bundle of plugins deployed together.",
        "bundle": True,
        "dependencies": [
            _dependency(),
            _dependency("commands_kit", version="0.1.1"),
            _dependency("scribe_admin", publisher="acme", version="1.4.0rc1"),
        ],
        "tags": {},
        "license": "",
        "readme": "README.md",
        **overrides,
    }


def test_manifest_accepts_bundle() -> None:
    """A bundle naming each dependency by name, publisher and exact version validates."""
    validate_manifest_file(_bundle_manifest())


def test_manifest_accepts_dependencies_on_a_plugin_with_code(
    handler_manifest_example: dict,
) -> None:
    """A plugin that is not a bundle may still declare dependencies."""
    handler_manifest_example["dependencies"] = [_dependency("commands_kit")]
    validate_manifest_file(handler_manifest_example)


def test_manifest_accepts_one_name_from_two_publishers() -> None:
    """Two publishers' plugins of the same name are two dependencies."""
    validate_manifest_file(
        _bundle_manifest(dependencies=[_dependency(), _dependency(publisher="acme")])
    )


def test_manifest_requires_components_unless_bundle(handler_manifest_example: dict) -> None:
    """A plugin that is not a bundle still needs components."""
    del handler_manifest_example["components"]
    with pytest.raises(ValidationError):
        validate_manifest_file(handler_manifest_example)


def test_manifest_names_the_code_keys_a_bundle_carries() -> None:
    """A bundle carrying code keys is refused with a message naming them."""
    manifest = _bundle_manifest(
        variables=[{"name": "API_KEY"}], custom_data={"namespace": "a__b", "access": "read"}
    )
    with pytest.raises(ValidationError, match="cannot declare custom_data, variables"):
        validate_manifest_file(manifest)


@pytest.mark.parametrize("version", ["~=1.16", "~=0.1.1", "~=1.16.0", "~=2.0rc1"])
def test_manifest_accepts_a_compatible_release_pin(version: str) -> None:
    """A `~=` pin with at least two release components is accepted alongside exact versions."""
    validate_manifest_file(_bundle_manifest(dependencies=[_dependency(version=version)]))


@pytest.mark.parametrize(
    "version",
    [
        ">=1.16",
        "<2",
        "==1.16.0",
        "!=1.16.0",
        "===1.16.0",
        ">=1,<2",
        "~=1.16,<1.18",
        "1.*",
        "==1.*",
        "~=1",
        "~=1.*",
        "~= 1.16",
        "latest",
    ],
)
def test_manifest_refuses_any_other_version_specifier_with_a_clear_sentence(version: str) -> None:
    """Anything but an exact version or a `~=X.Y` pin is refused with a sentence naming both
    accepted forms and what `~=` allows.
    """
    manifest = _bundle_manifest(dependencies=[_dependency(version=version)])
    with pytest.raises(ValidationError) as error:
        validate_manifest_file(manifest)
    assert error.value.message == (
        f"dependency 'scribe_core': {version!r} is not a version a dependency accepts. "
        "Name one exact version, such as '1.16.0', or a compatible release, such as "
        "'~=1.16' (1.16 or later, below 2.0) or '~=0.1.1' (0.1.1 or later, below 0.2)."
    )


BUNDLE_REFUSED: dict[str, dict] = {
    "no-dependencies": _bundle_manifest(dependencies=[]),
    "dependencies-missing": _without(_bundle_manifest(), "dependencies"),
    "components": _bundle_manifest(
        components={"handlers": [{"class": "scribe.handlers:Handler", "description": "x"}]}
    ),
    "custom-data": _bundle_manifest(custom_data={"namespace": "a__b", "access": "read"}),
    "variables": _bundle_manifest(variables=[{"name": "API_KEY"}]),
    "secrets": _bundle_manifest(secrets=["API_KEY"]),
    "dependency-without-publisher": _bundle_manifest(
        dependencies=[_without(_dependency(), "publisher")]
    ),
    "dependency-empty-publisher": _bundle_manifest(dependencies=[_dependency(publisher="")]),
    "dependency-without-version": _bundle_manifest(
        dependencies=[_without(_dependency(), "version")]
    ),
    "dependency-bad-name": _bundle_manifest(dependencies=[_dependency("Scribe-Core")]),
    "dependency-range": _bundle_manifest(dependencies=[_dependency(version=">=1,<2")]),
    "dependency-compatible-release-one-component": _bundle_manifest(
        dependencies=[_dependency(version="~=1")]
    ),
    "dependency-bad-version": _bundle_manifest(dependencies=[_dependency(version="latest")]),
    "dependency-source": _bundle_manifest(
        dependencies=[_dependency(source={"git": "https://github.com/canvas-medical/scribe"})]
    ),
    "dependency-repeated": _bundle_manifest(
        dependencies=[_dependency(), _dependency(version="1.17.0")]
    ),
    "dependency-on-itself": _bundle_manifest(dependencies=[_dependency("scribe")]),
}


@pytest.mark.parametrize("manifest", BUNDLE_REFUSED.values(), ids=BUNDLE_REFUSED.keys())
def test_manifest_rejects_malformed_bundle(manifest: dict) -> None:
    """A bundle that carries code, or whose dependencies are malformed, fails validation."""
    with pytest.raises(ValidationError):
        validate_manifest_file(manifest)


def test_manifest_accepts_a_dependency_name_of_256_characters() -> None:
    """Plugin names run up to 256 characters on instances, so a dependency can name one."""
    validate_manifest_file(_bundle_manifest(dependencies=[_dependency("c" * 256)]))


@pytest.mark.parametrize("name", ["c" * 257, "Scribe-Core"], ids=["too-long", "bad-name"])
def test_manifest_refuses_a_dependency_name_outside_the_plugin_name_rule(name: str) -> None:
    """A dependency name follows the plugin name rule, refused with the sentence Canvas
    Platform gives (its `test_manifest.py` holds the same 257-character case).
    """
    with pytest.raises(ValidationError) as error:
        validate_manifest_file(_bundle_manifest(dependencies=[_dependency(name)]))
    assert "at most 256" in error.value.message
    assert "lowercase letters, digits and underscores" in error.value.message


@pytest.mark.parametrize(
    ("version", "normalized"),
    [("v1.16.0", "1.16.0"), (" 1.16.0", "1.16.0"), ("1.16.0 ", "1.16.0"), ("V2", "2")],
)
def test_manifest_refuses_an_exact_version_not_written_in_normal_form(
    version: str, normalized: str
) -> None:
    """An exact version PEP 440 parses but writes differently is refused, naming its normal form."""
    manifest = _bundle_manifest(dependencies=[_dependency(version=version)])
    with pytest.raises(ValidationError) as error:
        validate_manifest_file(manifest)
    assert f"write it as {normalized!r}" in error.value.message


def test_manifest_accepts_a_dependency_sharing_its_name_from_another_publisher() -> None:
    """A plugin of the same name from a different publisher is another plugin, not itself."""
    validate_manifest_file(_bundle_manifest(publisher="acme", dependencies=[_dependency("scribe")]))


@pytest.mark.parametrize("publisher", [None, "canvas-medical"])
def test_manifest_refuses_a_dependency_on_itself(publisher: str | None) -> None:
    """A dependency of the plugin's own name is itself unless another publisher is named."""
    overrides: dict[str, Any] = {"dependencies": [_dependency("scribe")]}
    if publisher:
        overrides["publisher"] = publisher
    with pytest.raises(ValidationError, match="is the plugin itself"):
        validate_manifest_file(_bundle_manifest(**overrides))
