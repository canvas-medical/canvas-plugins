"""Visual Exam Finding command.

This is the first SDK command that accepts an attached file. The image is
referenced by an S3 key under the plugin's uploads prefix
(``plugin-uploads/<your-plugin-name>/...``). When the command's
``ORIGINATE_`` or ``EDIT_`` effect is interpreted, Canvas performs a
server-side S3 copy into the visual-exam-finding storage location — no file
bytes pass through your plugin.
"""

from canvas_sdk.commands.base import _BaseCommand as BaseCommand


class VisualExamFindingCommand(BaseCommand):
    """Manage a Visual Exam Finding command (image + title + narrative)
    within a specific note."""

    class Meta:
        key = "visual_exam_finding"

    title: str | None = None
    narrative: str | None = None
    image_upload_key: str | None = None


__exports__ = ("VisualExamFindingCommand",)
