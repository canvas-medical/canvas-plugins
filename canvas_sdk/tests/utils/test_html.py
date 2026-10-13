import pytest

from canvas_sdk.templates.filters import sanitize_html as sanitize_html_filter
from canvas_sdk.utils.html import sanitize_html


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ("<script>alert(1)</script>", ""),
        ("hi<script>alert(1)</script>there", "hithere"),
        ("<SCRIPT SRC=//evil.example/x.js></SCRIPT>", ""),
        ('<img src="x" onerror="alert(1)">', ""),
        ("<svg onload=alert(1)>", ""),
        ("<svg><script>alert(1)</script></svg>", ""),
        ('<iframe src="javascript:alert(1)"></iframe>', ""),
        ("<style>body{background:url(javascript:alert(1))}</style>", ""),
        ('<p style="width: expression(alert(1))">x</p>', "<p>x</p>"),
        ('<p onclick="alert(1)">x</p>', "<p>x</p>"),
        ('<div onmouseover="alert(1)">x</div>', "<div>x</div>"),
        ('<a href="javascript:alert(1)">x</a>', '<a rel="noopener noreferrer">x</a>'),
        ('<a href="JaVaScRiPt:alert(1)">x</a>', '<a rel="noopener noreferrer">x</a>'),
        (
            '<a href="&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;alert(1)">x</a>',
            '<a rel="noopener noreferrer">x</a>',
        ),
        ('<a href="java\tscript:alert(1)">x</a>', '<a rel="noopener noreferrer">x</a>'),
        (
            '<a href="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">x</a>',
            '<a rel="noopener noreferrer">x</a>',
        ),
        ('<a href="vbscript:msgbox(1)">x</a>', '<a rel="noopener noreferrer">x</a>'),
        ("<!-- <script>alert(1)</script> -->ok", "ok"),
        ("<p>unclosed <b>bold", "<p>unclosed <b>bold</b></p>"),
        ("<<script>script>alert(1)<</script>/script>", "&lt;/script&gt;"),
        ("<p><img src=x onerror=alert(1)//<p>x", "<p>x</p>"),
        ('<form action="https://evil.example"><input name="x"></form>', ""),
        ('<object data="javascript:alert(1)"></object>', ""),
        ('<span class="x" id="y" title="z" lang="en">t</span>', "<span>t</span>"),
    ],
)
def test_sanitize_html_removes_script_vectors(payload: str, expected: str) -> None:
    """Script-capable markup, attributes, and URL schemes are removed."""
    assert sanitize_html(payload) == expected


@pytest.mark.parametrize(
    "markup",
    [
        "<p>Hello</p>",
        "line one<br>line two",
        "<strong>bold</strong> <b>b</b> <em>em</em> <i>i</i> <u>u</u>",
        "<ul><li>one</li></ul><ol><li>two</li></ol>",
        "<div><span>nested</span></div>",
    ],
)
def test_sanitize_html_keeps_allowed_markup(markup: str) -> None:
    """Allowed formatting tags pass through unchanged."""
    assert sanitize_html(markup) == markup


@pytest.mark.parametrize(
    ("link", "expected"),
    [
        (
            '<a href="https://example.com/a?b=1&amp;c=2">x</a>',
            '<a href="https://example.com/a?b=1&amp;c=2" rel="noopener noreferrer">x</a>',
        ),
        (
            '<a href="http://example.com">x</a>',
            '<a href="http://example.com" rel="noopener noreferrer">x</a>',
        ),
        (
            '<a href="mailto:care@example.com">x</a>',
            '<a href="mailto:care@example.com" rel="noopener noreferrer">x</a>',
        ),
        (
            '<a href="https://example.com" target="_blank" rel="opener">x</a>',
            '<a href="https://example.com" rel="noopener noreferrer">x</a>',
        ),
    ],
)
def test_sanitize_html_keeps_safe_links(link: str, expected: str) -> None:
    """Links with allowed schemes keep their href and get rel=noopener noreferrer."""
    assert sanitize_html(link) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Can I refill my prescription?", "Can I refill my prescription?"),
        ("5 < 6 & 7 > 3", "5 &lt; 6 &amp; 7 &gt; 3"),
        ("", ""),
    ],
)
def test_sanitize_html_escapes_plain_text(text: str, expected: str) -> None:
    """Plain text is unchanged apart from HTML escaping."""
    assert sanitize_html(text) == expected


def test_sanitize_html_filter_marks_output_safe() -> None:
    """The template filter sanitizes and returns a SafeString."""
    result = sanitize_html_filter('<p onclick="alert(1)">hi</p><script>x</script>')
    assert result == "<p>hi</p>"
    assert hasattr(result, "__html__")


def test_sanitize_html_filter_renders_none_as_empty() -> None:
    """None renders as an empty string rather than the text 'None'."""
    assert sanitize_html_filter(None) == ""
