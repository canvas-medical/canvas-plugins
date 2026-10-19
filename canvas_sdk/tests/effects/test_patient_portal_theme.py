import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.patient_portal.theme import (
    PatientPortalTheme,
    band_color,
    contrast_ratio,
    derived_surface,
)

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
    """Pairs are checked only when the effect sets one side of them."""
    applied = PatientPortalTheme(corner_radius=8).apply()

    assert json.loads(applied.payload)["data"]["corner_radius"] == 8


def test_white_page_background_passes_with_default_brand() -> None:
    """A theme without brand_color does not check the default brand #2185D0, which is 3.94:1 on white."""
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


def test_dark_brand_passes_every_brand_text_pair() -> None:
    """#1D4ED8 passes the page, its header band, white labels and the gray selected row at 4.5:1."""
    applied = PatientPortalTheme(brand_color="#1D4ED8").apply()

    assert json.loads(applied.payload)["data"]["brand_color"] == "#1D4ED8"


def test_brand_text_needs_wcag_aa_normal_text_contrast() -> None:
    """Brand links and white labels are normal-size text, so they need 4.5:1, not 3.0:1.

    #5C90C2 is 3.37:1 with white text and 3.11:1 on its header band.
    """
    with pytest.raises(ValidationError) as exc:
        PatientPortalTheme(brand_color="#5C90C2", menu_background_color="#1F2937").apply()

    assert "WCAG AA needs 4.5:1" in str(exc.value)
    assert "3.0:1" not in str(exc.value)


def test_a_failing_pair_is_reported_once() -> None:
    """Without a page background, brand on page and white text on brand are the same colors."""
    with pytest.raises(ValidationError) as exc:
        PatientPortalTheme(brand_color="#FFD54F").apply()

    messages = [error["msg"] for error in exc.value.errors()]
    pairs = [message.split(" has contrast")[0].split(" on ") for message in messages]
    color_pairs = [frozenset(part.split()[-1] for part in pair) for pair in pairs if len(pair) == 2]
    assert len(color_pairs) == len(set(color_pairs))


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


def test_brand_that_fails_its_band_is_rejected() -> None:
    """#6494C2 passes white (3.20:1) but fails its own band tint (2.95:1)."""
    with pytest.raises(ValidationError) as exc:
        PatientPortalTheme(brand_color="#6494C2").apply()

    assert "header band" in str(exc.value)


def test_band_sits_on_the_surface_derived_from_the_page() -> None:
    """With a page background, the band is a brand tint over the lighter surface."""
    assert derived_surface("#F0FDFA") == "#F8FEFD"
    assert band_color("#0F766E", "#F0FDFA") == "#E5F3F2"
    assert band_color("#0F766E", None) == "#ECF4F3"


def test_light_brand_names_white_text_on_brand() -> None:
    """Buttons and sent messages draw white text on the brand, so a light brand names that pair."""
    with pytest.raises(ValidationError) as exc:
        PatientPortalTheme(brand_color="#FFD54F").apply()

    assert "white text" in str(exc.value)


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
