import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.patient_chart_summary_custom_section import PatientChartSummaryCustomSection


def test_effect_type() -> None:
    """Effect type must be PATIENT_CHART_SUMMARY__CUSTOM_SECTION."""
    assert (
        PatientChartSummaryCustomSection.Meta.effect_type
        == EffectType.PATIENT_CHART_SUMMARY__CUSTOM_SECTION
    )


def test_content_with_icon() -> None:
    """Content + icon is valid."""
    effect = PatientChartSummaryCustomSection(content="<p>hello</p>", icon="🎉")
    assert effect.content == "<p>hello</p>"
    assert effect.icon == "🎉"


def test_url_with_icon_url() -> None:
    """Url + icon_url is valid."""
    effect = PatientChartSummaryCustomSection(
        url="https://example.com", icon_url="https://example.com/icon.png"
    )
    assert effect.url == "https://example.com"
    assert effect.icon_url == "https://example.com/icon.png"


def test_content_with_icon_url() -> None:
    """Content + icon_url is valid."""
    effect = PatientChartSummaryCustomSection(
        content="<p>hello</p>", icon_url="https://example.com/icon.png"
    )
    assert effect.content == "<p>hello</p>"
    assert effect.icon_url == "https://example.com/icon.png"


def test_url_with_icon() -> None:
    """Url + icon is valid."""
    effect = PatientChartSummaryCustomSection(url="https://example.com", icon="🏗️")
    assert effect.url == "https://example.com"
    assert effect.icon == "🏗️"


def test_no_fields_raises() -> None:
    """No fields must raise."""
    with pytest.raises(ValidationError, match="must be provided"):
        PatientChartSummaryCustomSection()


def test_content_without_icon_raises() -> None:
    """Content without icon must raise."""
    with pytest.raises(ValidationError, match="must be provided"):
        PatientChartSummaryCustomSection(content="<p>hello</p>")


def test_url_without_icon_raises() -> None:
    """Url without icon must raise."""
    with pytest.raises(ValidationError, match="must be provided"):
        PatientChartSummaryCustomSection(url="https://example.com")


def test_icon_without_content_raises() -> None:
    """Icon without content or url must raise."""
    with pytest.raises(ValidationError, match="must be provided"):
        PatientChartSummaryCustomSection(icon="🎉")


def test_url_and_content_raises() -> None:
    """Url + content must raise."""
    with pytest.raises(ValidationError, match="mutually exclusive"):
        PatientChartSummaryCustomSection(
            url="https://example.com", content="<p>hello</p>", icon="🎉"
        )


def test_icon_and_icon_url_raises() -> None:
    """Icon + icon_url must raise."""
    with pytest.raises(ValidationError, match="mutually exclusive"):
        PatientChartSummaryCustomSection(
            content="<p>hello</p>", icon="🎉", icon_url="https://example.com/icon.png"
        )


def test_adding_conflicting_url_after_init_raises() -> None:
    """Setting url when content already set must raise."""
    effect = PatientChartSummaryCustomSection(content="<p>hello</p>", icon="🎉")
    with pytest.raises(ValidationError, match="mutually exclusive"):
        effect.url = "https://example.com"


def test_removing_icon_after_init_raises() -> None:
    """Clearing icon must raise."""
    effect = PatientChartSummaryCustomSection(content="<p>hello</p>", icon="🎉")
    with pytest.raises(ValidationError, match="must be provided"):
        effect.icon = None


def test_values() -> None:
    """Values must include all four fields."""
    effect = PatientChartSummaryCustomSection(content="<p>hello</p>", icon="🎉")
    assert effect.values == {"url": None, "content": "<p>hello</p>", "icon": "🎉", "icon_url": None}


def test_apply_payload() -> None:
    """Apply must wrap values under a data key."""
    effect = PatientChartSummaryCustomSection(content="<p>hi</p>", icon="🎉")
    payload = json.loads(effect.apply().payload)
    assert payload == {
        "data": {"url": None, "content": "<p>hi</p>", "icon": "🎉", "icon_url": None}
    }
