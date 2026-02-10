from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from canvas_sdk.effects.default_homepage import DefaultHomepageEffect


def test_apply_succeeds_with_page() -> None:
    """Test that the apply method succeeds when page is provided."""
    effect = DefaultHomepageEffect(page=DefaultHomepageEffect.Pages.PATIENTS)
    applied = effect.apply()

    assert applied.payload == '{"data": {"page": "/patients", "application_identifier": null}}'


@patch("canvas_sdk.effects.default_homepage.Application.objects.filter")
def test_apply_succeeds_with_application_identifier(mock_filter: MagicMock) -> None:
    """Test that the apply method succeeds when application_identifier is provided."""
    mock_filter.return_value.exists.return_value = True

    effect = DefaultHomepageEffect(application_identifier="my_plugin.apps:MyApp")
    applied = effect.apply()

    assert (
        applied.payload
        == '{"data": {"page": null, "application_identifier": "my_plugin.apps:MyApp"}}'
    )


@patch("canvas_sdk.effects.default_homepage.Application.objects.filter")
def test_apply_succeeds_with_both_page_and_application_identifier(mock_filter: MagicMock) -> None:
    """Test that the apply method succeeds when both page and application_identifier are provided."""
    mock_filter.return_value.exists.return_value = True

    effect = DefaultHomepageEffect(
        page=DefaultHomepageEffect.Pages.SCHEDULE,
        application_identifier="my_plugin.apps:MyApp",
    )
    applied = effect.apply()

    assert (
        applied.payload
        == '{"data": {"page": "/schedule", "application_identifier": "my_plugin.apps:MyApp"}}'
    )


def test_apply_raises_error_without_page_or_application_identifier() -> None:
    """Test that the apply method raises an error when neither page nor application_identifier is provided."""
    effect = DefaultHomepageEffect()

    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    err_msg = repr(exc_info.value)
    assert "1 validation error for DefaultHomepageEffect" in err_msg
    assert "Either page or application must be provided" in err_msg


@patch("canvas_sdk.effects.default_homepage.Application.objects.filter")
def test_apply_raises_error_when_application_does_not_exist(mock_filter: MagicMock) -> None:
    """Test that the apply method raises an error when application_identifier doesn't exist."""
    mock_filter.return_value.exists.return_value = False

    effect = DefaultHomepageEffect(application_identifier="nonexistent.apps:NoApp")

    with pytest.raises(ValidationError) as exc_info:
        effect.apply()

    err_msg = repr(exc_info.value)
    assert "Application with identifier nonexistent.apps:NoApp does not exist" in err_msg
