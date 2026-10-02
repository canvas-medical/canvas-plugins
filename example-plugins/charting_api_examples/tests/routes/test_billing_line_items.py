"""Tests for charting_api_examples.routes.billing_line_items module."""

from unittest.mock import MagicMock

from charting_api_examples.routes.billing_line_items import BillingLineItemAPI


class TestBillingLineItemAPI:
    """Tests for BillingLineItemAPI class."""

    def test_prefix_configuration(self):
        """Test that the API prefix is correctly configured."""
        assert BillingLineItemAPI.PREFIX == "/notes"

    def test_api_inherits_from_expected_classes(self):
        """Test that BillingLineItemAPI inherits from the correct base classes."""
        from canvas_sdk.handlers.simple_api import APIKeyAuthMixin, SimpleAPI

        assert issubclass(BillingLineItemAPI, APIKeyAuthMixin)
        assert issubclass(BillingLineItemAPI, SimpleAPI)

    def test_api_instance_creation(self):
        """Test that BillingLineItemAPI can be instantiated."""
        mock_event = MagicMock()
        api = BillingLineItemAPI(event=mock_event)
        assert api is not None
        assert hasattr(api, "add_billing_line_item")
