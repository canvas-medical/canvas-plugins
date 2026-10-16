import re
from typing import Any, Literal, NamedTuple

from pydantic import ConfigDict, Field
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect

HEX_COLOR = r"^#[0-9A-Fa-f]{6}$"
# Quotes are not allowed: the family is written raw into the portal's CSS, where
# an unbalanced quote breaks the declarations after it. Multi-word names work
# unquoted.
FONT_FAMILY = r"^[A-Za-z0-9 ,-]+$"
# Only Google Fonts stylesheets, which contain only @font-face rules. Any other
# stylesheet could carry the CSS that custom_css rejects.
GOOGLE_FONTS_STYLESHEET = r"^https://fonts\.googleapis\.com/css2?\?\S+$"

# Anything that makes the browser fetch. Without a fetch, custom CSS cannot send a
# typed value anywhere. Backslashes are rejected because CSS escapes such as
# "\\75 rl(" spell url( in disguise.
CSS_LOADERS = re.compile(r"url\s*\(|@import|image-set\s*\(|@font-face|\\", re.IGNORECASE)

# The portal's default colors. When the effect leaves one side of a pair unset,
# the pair is checked against the default for that side.
DEFAULT_BRAND = "#2185D0"
DEFAULT_MENU_BACKGROUND = "#F2F2F2"
DEFAULT_SELECTED_BACKGROUND = "#E5E5E5"
DEFAULT_PAGE_BACKGROUND = "#FFFFFF"
BODY_TEXT = "#212121"
DARK_TEXT = "#262626"
LIGHT_TEXT = "#FFFFFF"

# WCAG AA for normal-size text. Every checked pair draws text: rail labels,
# body text, brand links and headers, and white labels on the brand.
TEXT_FLOOR = 4.5


def _channels(hex_color: str) -> tuple[int, ...]:
    """Return the red, green and blue channels of a #RRGGBB color."""
    return tuple(bytes.fromhex(hex_color[1:]))


def _relative_luminance(hex_color: str) -> float:
    r, g, b = (
        c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        for c in (channel / 255 for channel in _channels(hex_color))
    )
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(first: str, second: str) -> float:
    """Return the WCAG 2 contrast ratio between two #RRGGBB colors."""
    a, b = _relative_luminance(first), _relative_luminance(second)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def derived_text_color(background: str) -> str:
    """Return the rail text color the portal derives for a background.

    Same rule as contrastTextColor in the home-app frontend.
    """
    r, g, b = _channels(background)
    perceived = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return DARK_TEXT if perceived > 0.5 else LIGHT_TEXT


def mix_colors(foreground: str, background: str, foreground_share: float = 0.1) -> str:
    """Return the background with a share of the foreground mixed in."""
    # Halves round up, as JavaScript's Math.round does in the portal, so the
    # colors checked here are the colors the browser paints.
    mixed = (
        int(f * foreground_share + b * (1 - foreground_share) + 0.5)
        for f, b in zip(_channels(foreground), _channels(background), strict=True)
    )
    return "#" + "".join(f"{channel:02X}" for channel in mixed)


def derived_surface(page_background: str | None) -> str:
    """Return the card and panel color: halfway from the page background to white.

    Lighter than the page, so cards still read as raised surfaces, and text and
    brand keep at least their contrast against the page.
    """
    return mix_colors(LIGHT_TEXT, page_background, 0.5) if page_background else LIGHT_TEXT


def band_color(brand: str, page_background: str | None) -> str:
    """Return the section and accordion header band: an 8% brand tint over the surface."""
    return mix_colors(brand, derived_surface(page_background), 0.08)


class _Pair(NamedTuple):
    """A foreground and background the portal draws together, and the contrast they need."""

    foreground_label: str
    foreground: str
    background_label: str
    background: str
    floor: float


class PatientPortalTheme(_BaseEffect):
    """The patient portal theme, the answer to PATIENT_PORTAL__GET_THEME_CONFIGURATION.

    A handler responds to that event and returns this effect. The event context
    carries the business line the portal page is for. An unset token uses the
    portal default, and an effect without tokens is the default theme.
    """

    class Meta:
        effect_type = EffectType.PATIENT_PORTAL__THEME_CONFIGURATION

    # An unknown token is an error, so a misspelled token does not silently do nothing.
    model_config = ConfigDict(extra="forbid")

    brand_color: str | None = Field(default=None, pattern=HEX_COLOR)
    menu_background_color: str | None = Field(default=None, pattern=HEX_COLOR)
    menu_selected_background_color: str | None = Field(default=None, pattern=HEX_COLOR)
    menu_text_color: str | None = Field(default=None, pattern=HEX_COLOR)
    page_background_color: str | None = Field(default=None, pattern=HEX_COLOR)
    corner_radius: int | None = Field(default=None, ge=0, le=24)
    font_family: str | None = Field(default=None, max_length=200, pattern=FONT_FAMILY)
    font_source: str | None = Field(default=None, max_length=2000, pattern=GOOGLE_FONTS_STYLESHEET)
    person_word: Literal["patient", "member", "client"] | None = None
    custom_css: str | None = Field(default=None, max_length=50_000)

    @property
    def values(self) -> dict[str, Any]:
        """Theme values: every token this effect declares, in declaration order."""
        # Every effect inherits patient_filter from _BaseEffect; it is not a theme token.
        tokens = type(self).model_fields.keys() - _BaseEffect.model_fields.keys()
        return self.model_dump(include=tokens)

    def _contrast_pairs(self) -> list[_Pair]:
        """Return the pairs this theme must pass, each pair of colors once.

        A pair is checked when the theme sets at least one side of it. Brand
        pairs are checked when the theme sets the brand: the default brand is the
        portal's own choice.
        """
        brand = self.brand_color or DEFAULT_BRAND
        page = self.page_background_color or DEFAULT_PAGE_BACKGROUND
        menu = self.menu_background_color or DEFAULT_MENU_BACKGROUND
        if self.menu_text_color:
            menu_text, menu_text_label = self.menu_text_color, "menu_text_color"
        else:
            menu_text = derived_text_color(menu) if self.menu_background_color else DARK_TEXT
            menu_text_label = "menu_text_color (derived)"

        pairs = []
        if self.menu_text_color or self.menu_background_color:
            pairs.append(
                _Pair(menu_text_label, menu_text, "menu_background_color", menu, TEXT_FLOOR)
            )
        if self.page_background_color:
            pairs.append(_Pair("body text", BODY_TEXT, "page_background_color", page, TEXT_FLOOR))
        if self.brand_color:
            band = band_color(brand, self.page_background_color)
            # Primary buttons and sent messages draw white text on the brand. First,
            # so on a white page it is the name the shared pair is reported under.
            pairs.append(_Pair("white text", LIGHT_TEXT, "brand_color", brand, TEXT_FLOOR))
            pairs.append(_Pair("brand_color", brand, "page_background_color", page, TEXT_FLOOR))
            pairs.append(_Pair("brand_color", brand, "header band", band, TEXT_FLOOR))

        # A custom rail draws the selected row in the menu text color. The
        # default rail draws it in the brand color.
        if self.menu_background_color:
            selected = self.menu_selected_background_color or mix_colors(menu_text, menu)
            pairs.append(
                _Pair(
                    menu_text_label,
                    menu_text,
                    "menu_selected_background_color",
                    selected,
                    TEXT_FLOOR,
                )
            )
        elif self.brand_color or self.menu_selected_background_color:
            selected = self.menu_selected_background_color or DEFAULT_SELECTED_BACKGROUND
            pairs.append(
                _Pair("brand_color", brand, "menu_selected_background_color", selected, TEXT_FLOOR)
            )

        # The same two colors can meet twice, for example brand on a white page and
        # white text on the brand. Report each pair of colors once.
        unique: dict[frozenset[str], _Pair] = {}
        for pair in pairs:
            unique.setdefault(frozenset((pair.foreground, pair.background)), pair)
        return list(unique.values())

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.custom_css and "<" in self.custom_css:
            errors.append(
                self._create_error_detail("value", "custom_css must not contain '<'", "custom_css")
            )
        if self.custom_css and CSS_LOADERS.search(self.custom_css):
            errors.append(
                self._create_error_detail(
                    "value",
                    "custom_css must not load anything: no url(), @import, image-set(), "
                    "@font-face or backslash escapes",
                    "custom_css",
                )
            )
        if self.font_source and not self.font_family:
            errors.append(
                self._create_error_detail(
                    "value", "font_source needs a font_family to apply", "font_source"
                )
            )

        for pair in self._contrast_pairs():
            ratio = contrast_ratio(pair.foreground, pair.background)
            if ratio < pair.floor:
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"{pair.foreground_label} {pair.foreground} on {pair.background_label} "
                        f"{pair.background} has contrast {ratio:.2f}:1; "
                        f"WCAG AA needs {pair.floor}:1",
                        pair.foreground,
                    )
                )

        return errors


__exports__ = ("PatientPortalTheme",)
