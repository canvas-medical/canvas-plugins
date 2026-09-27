import nh3

ALLOWED_TAGS = frozenset(
    {"a", "b", "br", "div", "em", "i", "li", "ol", "p", "span", "strong", "u", "ul"}
)
# "*" lists attributes allowed on every tag; nh3 allows `lang` and `title` there unless
# it is set explicitly.
ALLOWED_ATTRIBUTES: dict[str, frozenset[str]] = {"a": frozenset({"href"}), "*": frozenset()}
ALLOWED_URL_SCHEMES = frozenset({"http", "https", "mailto"})
LINK_REL = "noopener noreferrer"


def sanitize_html(value: str) -> str:
    """Return `value` with everything outside a small formatting allowlist removed.

    Use this before rendering HTML that came from an untrusted source (a patient,
    an integration, any API input) into a page staff will open.

    Kept: the tags `p br b strong i em u ul ol li a span div`, and `href` on `a`
    when it uses `http`, `https`, or `mailto`. Every link gets
    `rel="noopener noreferrer"`. Removed: all other tags and attributes (including
    `style` and `on*` event handlers), comments, the contents of `script` and
    `style`, and links with any other scheme (`javascript:`, `data:`, ...).
    Text is HTML-escaped, so the result is safe to mark safe in a template.
    """
    return nh3.clean(
        value,
        tags=set(ALLOWED_TAGS),
        attributes={tag: set(attrs) for tag, attrs in ALLOWED_ATTRIBUTES.items()},
        url_schemes=set(ALLOWED_URL_SCHEMES),
        link_rel=LINK_REL,
        strip_comments=True,
    )


__all__ = __exports__ = ("sanitize_html",)
