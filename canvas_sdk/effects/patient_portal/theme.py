import re
from typing import Any, Literal

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

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.custom_css and "<" in self.custom_css:
            errors.append(
                self._create_error_detail(
                    "value", "custom_css must not contain '<'", self.custom_css
                )
            )
        if self.custom_css and CSS_LOADERS.search(self.custom_css):
            errors.append(
                self._create_error_detail(
                    "value",
                    "custom_css must not load anything: no url(), @import, image-set(), "
                    "@font-face or backslash escapes",
                    self.custom_css,
                )
            )
        if self.font_source and not self.font_family:
            errors.append(
                self._create_error_detail(
                    "value", "font_source needs a font_family to apply", self.font_source
                )
            )

        return errors


__exports__ = ("PatientPortalTheme",)
