from typing import Any, Literal

from pydantic import ConfigDict, Field
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect

HEX_COLOR = r"^#[0-9A-Fa-f]{6}$"
FONT_FAMILY = r"^[A-Za-z0-9 ,'\"-]+$"

# The portal's current colors. A pair that uses one of these is checked
# against what the patient sees today when the effect leaves that side unset.
DEFAULT_BRAND = "#2185D0"
DEFAULT_MENU_BACKGROUND = "#F2F2F2"
DEFAULT_SELECTED_BACKGROUND = "#E5E5E5"
DEFAULT_PAGE_BACKGROUND = "#FFFFFF"
BODY_TEXT = "#212121"
DARK_TEXT = "#262626"
LIGHT_TEXT = "#FFFFFF"

TEXT_FLOOR = 4.5
BRAND_FLOOR = 3.0


def _channels(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def _relative_luminance(hex_color: str) -> float:
    linear = []
    for channel in _channels(hex_color):
        c = channel / 255
        linear.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(first: str, second: str) -> float:
    """Return the WCAG 2 contrast ratio between two #RRGGBB colors."""
    lighter, darker = sorted(
        (_relative_luminance(first), _relative_luminance(second)), reverse=True
    )
    return (lighter + 0.05) / (darker + 0.05)


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


class PatientPortalTheme(_BaseEffect):
    """The patient portal theme, returned from PATIENT_PORTAL__THEME_CONFIGURATION.

    The event context carries the business line the portal page is for. An
    unset token uses the portal default, and an effect without tokens is the
    default theme.
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
    font_source: str | None = Field(default=None, max_length=2000, pattern=r"^https://\S+$")
    person_word: Literal["patient", "member", "client"] | None = None
    custom_css: str | None = Field(default=None, max_length=50_000)

    @property
    def values(self) -> dict[str, Any]:
        """Theme values."""
        return {
            "brand_color": self.brand_color,
            "menu_background_color": self.menu_background_color,
            "menu_selected_background_color": self.menu_selected_background_color,
            "menu_text_color": self.menu_text_color,
            "page_background_color": self.page_background_color,
            "corner_radius": self.corner_radius,
            "font_family": self.font_family,
            "font_source": self.font_source,
            "person_word": self.person_word,
            "custom_css": self.custom_css,
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return {"data": self.values}

    def _contrast_pairs(self) -> list[tuple[str, str, str, str, float, bool]]:
        """Return (fg_label, fg, bg_label, bg, floor, is_checked) for every pair."""
        brand = self.brand_color or DEFAULT_BRAND
        page = self.page_background_color or DEFAULT_PAGE_BACKGROUND
        menu = self.menu_background_color or DEFAULT_MENU_BACKGROUND
        if self.menu_text_color:
            menu_text, menu_text_label = self.menu_text_color, "menu_text_color"
        elif self.menu_background_color:
            menu_text = derived_text_color(menu)
            menu_text_label = "menu_text_color (derived)"
        else:
            menu_text, menu_text_label = DARK_TEXT, "menu_text_color (default)"

        pairs = [
            (
                menu_text_label,
                menu_text,
                "menu_background_color",
                menu,
                TEXT_FLOOR,
                bool(self.menu_text_color or self.menu_background_color),
            ),
            (
                "body text",
                BODY_TEXT,
                "page_background_color",
                page,
                TEXT_FLOOR,
                bool(self.page_background_color),
            ),
            (
                "brand_color",
                brand,
                "page_background_color",
                page,
                BRAND_FLOOR,
                bool(self.brand_color or self.page_background_color),
            ),
            (
                "brand_color",
                brand,
                "header band",
                band_color(brand, self.page_background_color),
                BRAND_FLOOR,
                bool(self.brand_color),
            ),
        ]

        # A custom rail draws the selected row in the menu text color. The
        # default rail draws it in the brand color.
        if self.menu_background_color:
            selected = self.menu_selected_background_color or mix_colors(menu_text, menu)
            pairs.append(
                (
                    menu_text_label,
                    menu_text,
                    "menu_selected_background_color",
                    selected,
                    TEXT_FLOOR,
                    True,
                )
            )
        else:
            selected = self.menu_selected_background_color or DEFAULT_SELECTED_BACKGROUND
            pairs.append(
                (
                    "brand_color",
                    brand,
                    "menu_selected_background_color",
                    selected,
                    BRAND_FLOOR,
                    bool(self.brand_color or self.menu_selected_background_color),
                )
            )
        return pairs

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.custom_css and "<" in self.custom_css:
            errors.append(
                self._create_error_detail("value", "custom_css must not contain '<'", "custom_css")
            )

        for fg_label, fg, bg_label, bg, floor, is_checked in self._contrast_pairs():
            if not is_checked:
                continue
            ratio = contrast_ratio(fg, bg)
            if ratio < floor:
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"{fg_label} {fg} on {bg_label} {bg} has contrast {ratio:.2f}:1; "
                        f"WCAG AA needs {floor}:1",
                        fg,
                    )
                )

        return errors


__exports__ = ("PatientPortalTheme",)
