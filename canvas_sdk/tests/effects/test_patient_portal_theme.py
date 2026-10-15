import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.patient_portal.theme import PatientPortalTheme, contrast_ratio

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


def test_contrast_ratio_matches_wcag_reference_values() -> None:
    """The ratio uses WCAG relative luminance."""
    assert contrast_ratio("#000000", "#FFFFFF") == pytest.approx(21.0, abs=0.01)
    assert contrast_ratio("#2185D0", "#FFFFFF") == pytest.approx(3.94, abs=0.01)
    assert contrast_ratio("#2185D0", "#E5E5E5") == pytest.approx(3.13, abs=0.01)


def test_empty_effect_resets_the_theme() -> None:
    """An effect with no tokens is valid and carries every key as null."""
    applied = PatientPortalTheme().apply()

    assert applied.type == EffectType.PATIENT_PORTAL__THEME_CONFIGURATION
    assert json.loads(applied.payload) == {"data": EMPTY_DATA}


def test_radius_only_passes_even_though_default_brand_is_below_4_5() -> None:
    """Pairs are checked only when the effect sets one side, and brand pairs use 3.0."""
    applied = PatientPortalTheme(corner_radius=8).apply()

    assert json.loads(applied.payload)["data"]["corner_radius"] == 8


def test_white_page_background_passes_with_default_brand() -> None:
    """Default brand #2185D0 is 3.94:1 on white, above the 3.0 brand floor."""
    applied = PatientPortalTheme(page_background_color="#FFFFFF").apply()

    assert json.loads(applied.payload)["data"]["page_background_color"] == "#FFFFFF"


@pytest.mark.parametrize("menu_background", ["#1F2937", "#FEF3C7"])
def test_ticket_example_rail_colors_pass(menu_background: str) -> None:
    """AC3's dark and light rail colors pass with derived text and selection."""
    applied = PatientPortalTheme(menu_background_color=menu_background).apply()

    assert json.loads(applied.payload)["data"]["menu_background_color"] == menu_background


def test_mid_gray_rail_with_derived_text_fails_and_names_the_pair() -> None:
    """#777777 derives white text at 4.48:1, below 4.5."""
    with pytest.raises(ValidationError) as exc:
        PatientPortalTheme(menu_background_color="#777777").apply()

    message = str(exc.value)
    assert "menu_text_color (derived)" in message
    assert "menu_background_color" in message
    assert "4.48:1" in message


def test_dark_page_background_fails_body_text() -> None:
    """Body text #212121 on a dark page is unreadable."""
    with pytest.raises(ValidationError) as exc:
        PatientPortalTheme(page_background_color="#1F2937").apply()

    assert "page_background_color" in str(exc.value)


def test_brand_on_page_below_3_fails() -> None:
    """A yellow brand on white is 1.22:1."""
    with pytest.raises(ValidationError) as exc:
        PatientPortalTheme(brand_color="#FFEB3B").apply()

    assert "brand_color" in str(exc.value)


def test_brand_on_selected_row_checked_only_on_default_rail() -> None:
    """With the default rail, brand text sits on the selected background."""
    with pytest.raises(ValidationError) as exc:
        PatientPortalTheme(brand_color="#2185D0", menu_selected_background_color="#2185D0").apply()

    assert "menu_selected_background_color" in str(exc.value)


def test_custom_rail_checks_menu_text_on_selected_background() -> None:
    """With a custom rail, the selected row uses the menu text color."""
    with pytest.raises(ValidationError) as exc:
        PatientPortalTheme(
            menu_background_color="#1F2937",
            menu_text_color="#FFFFFF",
            menu_selected_background_color="#F2F2F2",
        ).apply()

    assert "menu_selected_background_color" in str(exc.value)


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
