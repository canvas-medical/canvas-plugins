"""Basic smoke tests for email_bounce plugin."""


def test_import_email_bounce_api():
    """Test that EmailBounceAPI can be imported without errors."""
    from api_samples.routes.email_bounce import EmailBounceAPI

    # Verify the class exists and has expected attributes
    assert EmailBounceAPI is not None
    assert hasattr(EmailBounceAPI, "PATH")
    assert hasattr(EmailBounceAPI, "post")


def test_email_bounce_api_configuration():
    """Test that EmailBounceAPI has correct path configuration."""
    from api_samples.routes.email_bounce import EmailBounceAPI

    # Verify PATH is configured
    assert EmailBounceAPI.PATH == "/crm-webhooks/email-bounce"
