import pytest
from django.core.exceptions import ImproperlyConfigured

from canvas_sdk.commands.commands.review.base import _BaseReview


def test_base_review_init_subclass_raises_error_when_meta_key_missing() -> None:
    """Test that __init_subclass__ raises an error when Meta.key is missing on a review command."""
    with pytest.raises(ImproperlyConfigured, match="must specify Meta.key"):

        class ReviewWithoutKey(_BaseReview):
            class Meta:
                model = object  # Placeholder model


def test_base_review_init_subclass_raises_error_when_meta_key_empty() -> None:
    """Test that __init_subclass__ raises an error when Meta.key is an empty string on a review command."""
    with pytest.raises(ImproperlyConfigured, match="must specify Meta.key"):

        class ReviewWithEmptyKey(_BaseReview):
            class Meta:
                key = ""
                model = object  # Placeholder model


def test_base_review_init_subclass_raises_error_when_meta_model_missing() -> None:
    """Test that __init_subclass__ raises an error when Meta.model is missing on a review command."""
    with pytest.raises(ImproperlyConfigured, match="must specify Meta.model"):

        class ReviewWithoutModel(_BaseReview):
            class Meta:
                key = "test_review"


def test_base_review_init_subclass_raises_error_when_meta_model_none() -> None:
    """Test that __init_subclass__ raises an error when Meta.model is None on a review command."""
    with pytest.raises(ImproperlyConfigured, match="must specify Meta.model"):

        class ReviewWithNoneModel(_BaseReview):
            class Meta:
                key = "test_review"
                model = None


def test_base_review_init_subclass_allows_valid_review_command() -> None:
    """Test that __init_subclass__ allows review commands with valid Meta.key and Meta.model."""

    # Mock model class for testing
    class MockModel:
        objects = None

    # Should not raise an error
    class ValidReview(_BaseReview):
        class Meta:
            key = "test_review"
            model = MockModel

    # Verify the class was created successfully
    assert ValidReview.Meta.key == "test_review"
    assert ValidReview.Meta.model == MockModel
