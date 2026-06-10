from unittest.mock import patch

from canvas_sdk.v1.data.visual_exam_finding import VisualExamFinding


def test_image_url_with_image() -> None:
    """image_url returns a presigned URL when image is set."""
    finding = VisualExamFinding()
    finding.image = "visual_exam_findings/finding.png"

    with patch(
        "canvas_sdk.v1.data.visual_exam_finding.presigned_url",
        return_value="https://s3.example.com/presigned",
    ) as mock:
        assert finding.image_url == "https://s3.example.com/presigned"
        mock.assert_called_once_with("visual_exam_findings/finding.png")


def test_image_url_without_image() -> None:
    """image_url returns None when image is empty."""
    finding = VisualExamFinding()
    finding.image = None

    assert finding.image_url is None


def test_finding_fields() -> None:
    """The finding exposes its title, narrative, and patient/note FKs."""
    finding = VisualExamFinding()
    finding.patient_id = 11
    finding.note_id = 22
    finding.title = "Left forearm"
    finding.narrative = "2cm laceration"

    assert finding.patient_id == 11
    assert finding.note_id == 22
    assert finding.title == "Left forearm"
    assert finding.narrative == "2cm laceration"
