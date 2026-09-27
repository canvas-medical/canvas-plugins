from django import template
from django.utils.safestring import SafeString, mark_safe

from canvas_sdk.utils.html import sanitize_html as _sanitize_html

register = template.Library()


@register.filter(name="sanitize_html")
def sanitize_html(value: object) -> SafeString:
    """Template filter form of `canvas_sdk.utils.html.sanitize_html`.

    `{{ message.content|sanitize_html }}` renders the allowed formatting as HTML and
    removes everything else. `None` renders as an empty string.
    """
    if value is None:
        return mark_safe("")
    return mark_safe(_sanitize_html(str(value)))


# Loaded by the template engine as a builtin library; plugins use the filter, not the module.
__exports__ = ()
