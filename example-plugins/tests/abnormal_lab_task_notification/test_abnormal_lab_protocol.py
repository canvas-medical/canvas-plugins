"""Basic smoke tests for abnormal_lab_task_notification plugin."""


def test_import_abnormal_lab_protocol():
    """Test that AbnormalLabProtocol can be imported without errors."""
    from abnormal_lab_task_notification.protocols.abnormal_lab_protocol import (
        AbnormalLabProtocol,
    )

    # Verify the class exists and has expected attributes
    assert AbnormalLabProtocol is not None
    assert hasattr(AbnormalLabProtocol, "RESPONDS_TO")
    assert hasattr(AbnormalLabProtocol, "compute")


def test_abnormal_lab_protocol_responds_to():
    """Test that AbnormalLabProtocol responds to LAB_REPORT_CREATED event."""
    from abnormal_lab_task_notification.protocols.abnormal_lab_protocol import (
        AbnormalLabProtocol,
    )

    from canvas_sdk.events import EventType

    # Verify RESPONDS_TO is configured correctly
    assert AbnormalLabProtocol.RESPONDS_TO == EventType.Name(EventType.LAB_REPORT_CREATED)
