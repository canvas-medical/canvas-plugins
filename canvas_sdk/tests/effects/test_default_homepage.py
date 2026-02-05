import pytest
from pydantic import ValidationError

from canvas_sdk.effects.default_homepage import DefaultHomepageEffect


def test_apply_succeeds_with_page() -> None:
    """Test that the apply method succeeds when page is provided."""
    effect = DefaultHomepageEffect(page=DefaultHomepageEffect.Pages.PATIENTS)
    applied = effect.apply()

    assert applied.payload == '{"data": {"page": "/patients", "application_url": null}}'


def test_apply_succeeds_with_application_url() -> None:
    """Test that the apply method succeeds when application_url is provided."""
    effect = DefaultHomepageEffect(application_url="/application/#app=test123")
    applied = effect.apply()

    assert (
        applied.payload
        == '{"data": {"page": null, "application_url": "/application/#app=test123"}}'
    )


def test_apply_succeeds_with_both_page_and_application_url() -> None:
    """Test that the apply method succeeds when both page and application_url are provided."""
    effect = DefaultHomepageEffect(
        page=DefaultHomepageEffect.Pages.SCHEDULE,
        application_url="/application/#app=test123",
    )
    applied = effect.apply()

    assert (
        applied.payload
        == '{"data": {"page": "/schedule", "application_url": "/application/#app=test123"}}'
    )


def test_apply_raises_error_without_page_or_application_url() -> None:
    """Test that the apply method raises an error when neither page nor application_url is provided."""
    effect = DefaultHomepageEffect()

    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    err_msg = repr(exc_info.value)
    assert "1 validation error for DefaultHomepageEffect" in err_msg
    assert "Either page or application_url must be provided" in err_msg


def test_values_property_returns_correct_dict_with_page() -> None:
    """Test that the values property returns the correct dictionary when page is set."""
    effect = DefaultHomepageEffect(page=DefaultHomepageEffect.Pages.REVENUE)

    assert effect.values == {
        "page": "/revenue",
        "application_url": None,
    }


def test_values_property_returns_correct_dict_with_application_url() -> None:
    """Test that the values property returns the correct dictionary when application_url is set."""
    effect = DefaultHomepageEffect(application_url="/application/#app=test123")

    assert effect.values == {
        "page": None,
        "application_url": "/application/#app=test123",
    }


def test_effect_payload_wraps_values_in_data_key() -> None:
    """Test that the effect_payload property wraps values in a data key."""
    effect = DefaultHomepageEffect(page=DefaultHomepageEffect.Pages.PATIENTS)

    assert effect.effect_payload == {
        "data": {
            "page": "/patients",
            "application_url": None,
        }
    }
