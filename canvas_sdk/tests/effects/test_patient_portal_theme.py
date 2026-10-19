import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.patient_portal.theme import PatientPortalTheme

EMPTY_DATA = {
    "brand_color": None,
    "menu_background_color": None,
    "menu_selected_background_color": None,
    "menu_text_color": None,
    "page_background_color": None,
    "corner_radius": None,
    "font_family": None,
    "font_source": None,
    "person_word": None,
    "custom_css": None,
}


def test_empty_effect_resets_the_theme() -> None:
    """An effect with no tokens is valid and carries every key as null."""
    applied = PatientPortalTheme().apply()

    assert applied.type == EffectType.PATIENT_PORTAL__THEME_CONFIGURATION
    assert json.loads(applied.payload) == {"data": EMPTY_DATA}


@pytest.mark.parametrize("value", ["#FFF", "red", "#GGGGGG", "#1F293780"])
def test_color_must_be_six_digit_hex(value: str) -> None:
    """Only #RRGGBB is accepted."""
    with pytest.raises(ValidationError):
        PatientPortalTheme(brand_color=value).apply()


@pytest.mark.parametrize("value", [-1, 25])
def test_corner_radius_bounds(value: int) -> None:
    """Radius is 0 to 24 px."""
    with pytest.raises(ValidationError):
        PatientPortalTheme(corner_radius=value).apply()


def test_custom_css_rejects_angle_bracket() -> None:
    """A style element breakout is rejected."""
    with pytest.raises(ValidationError):
        PatientPortalTheme(custom_css="a{} </style><script>alert(1)</script>").apply()


def test_custom_css_is_carried_verbatim() -> None:
    """Valid CSS, child combinator included, is not altered."""
    css = ".card > .header { letter-spacing: 0.02em; }"
    applied = PatientPortalTheme(custom_css=css).apply()

    assert json.loads(applied.payload)["data"]["custom_css"] == css


@pytest.mark.parametrize("value", ["http://fonts.example.com/a.css", "javascript:alert(1)"])
def test_font_source_must_be_https(value: str) -> None:
    """Only https font stylesheets load."""
    with pytest.raises(ValidationError):
        PatientPortalTheme(font_source=value).apply()


def test_font_family_rejects_css_syntax() -> None:
    """A family name cannot carry declarations."""
    with pytest.raises(ValidationError):
        PatientPortalTheme(font_family="Inter; color: red").apply()


def test_person_word_enum() -> None:
    """Only the three supported words are accepted."""
    with pytest.raises(ValidationError):
        PatientPortalTheme(person_word="customer").apply()  # type: ignore[arg-type]


def test_business_line_is_not_a_field() -> None:
    """The event context carries the business line, so the effect rejects it."""
    with pytest.raises(ValidationError):
        PatientPortalTheme(business_line_id="x").apply()  # type: ignore[call-arg]


@pytest.mark.parametrize(
    "source",
    [
        "https://fonts.example.com/inter.css",
        "https://cdn.example.com/fonts.googleapis.com/css2?family=Inter",
        "https://fonts.googleapis.com.evil.example/css2?family=Inter",
        "https://fonts.gstatic.com/s/inter/v1/inter.woff2",
    ],
)
def test_font_source_must_be_google_fonts(source: str) -> None:
    """Only a Google Fonts stylesheet loads, so font_source cannot carry arbitrary CSS."""
    with pytest.raises(ValidationError):
        PatientPortalTheme(font_family="Inter", font_source=source).apply()


@pytest.mark.parametrize(
    "source",
    [
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap",
        "https://fonts.googleapis.com/css?family=Lato",
    ],
)
def test_google_fonts_source_is_accepted(source: str) -> None:
    """Google Fonts css and css2 stylesheets load the font."""
    applied = PatientPortalTheme(font_family="Inter", font_source=source).apply()

    assert json.loads(applied.payload)["data"]["font_source"] == source


@pytest.mark.parametrize("family", ["Inter'", '"Open Sans"', "Inter, 'Helvetica Neue'"])
def test_font_family_rejects_quotes(family: str) -> None:
    """Quotes are written raw into the portal's CSS, where an unbalanced one breaks the styles after it."""
    with pytest.raises(ValidationError):
        PatientPortalTheme(font_family=family).apply()


def test_font_source_requires_font_family() -> None:
    """A stylesheet without a family would drop the default font and set nothing."""
    with pytest.raises(ValidationError) as exc:
        PatientPortalTheme(font_source="https://fonts.googleapis.com/css2?family=Inter").apply()

    assert "font_family" in str(exc.value)


@pytest.mark.parametrize(
    "css",
    [
        "body { background: url(https://x.example/a) }",
        "body { background: URL( 'https://x.example/a' ) }",
        "@import 'https://x.example/a.css';",
        "a { background-image: image-set('https://x.example/a.png' 1x) }",
        "@font-face { font-family: x; src: local(x) }",
        "body { background: \\75 rl(https://x.example/a) }",
    ],
)
def test_custom_css_cannot_load_anything(css: str) -> None:
    """Custom CSS cannot fetch, so it cannot send typed values anywhere."""
    with pytest.raises(ValidationError) as exc:
        PatientPortalTheme(custom_css=css).apply()

    assert "custom_css" in str(exc.value)


@pytest.mark.parametrize(
    ("tokens", "message", "rejected"),
    [
        (
            {"custom_css": "a::before { content: '<b>' }"},
            "custom_css must not contain",
            "custom_css",
        ),
        ({"custom_css": "a { background: url(x.png) }"}, "custom_css must not load", "custom_css"),
        (
            {"font_source": "https://fonts.googleapis.com/css2?family=Nunito"},
            "font_source needs a font_family",
            "font_source",
        ),
    ],
)
def test_validation_errors_report_the_rejected_value(
    tokens: dict[str, str], message: str, rejected: str
) -> None:
    """Each error carries the value it rejects as its input, like the other SDK effects."""
    with pytest.raises(ValidationError) as exc:
        PatientPortalTheme.model_validate(tokens).apply()

    inputs = [error["input"] for error in exc.value.errors() if message in error["msg"]]
    assert inputs == [tokens[rejected]]


def test_colors_are_not_checked_for_contrast() -> None:
    """Any valid hex colors pass, whatever their contrast."""
    applied = PatientPortalTheme(
        menu_background_color="#777777",
        page_background_color="#000000",
        brand_color="#FFFF00",
    ).apply()

    assert json.loads(applied.payload)["data"]["menu_background_color"] == "#777777"
