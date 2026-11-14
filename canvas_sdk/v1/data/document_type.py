from django.db import models


class DocumentType(models.Model):
    """A type an incoming document can be filed as, such as a lab report or a referral.

    The types are Canvas's own, the same on every instance of a release. A clinical type
    with a ``template_type`` files its document with a report template: lab, imaging, or
    specialty report. ``template_fields`` describes the form a reviewer fills in for the
    type, as ``[{"name", "label", "type", "required"}, ...]``.
    """

    class Meta:
        db_table = "canvas_sdk_data_data_integration_documenttype_001"

    key = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20)
    template_type = models.CharField(max_length=50, null=True)
    template_fields = models.JSONField(default=list)

    def __str__(self) -> str:
        return self.name


__exports__ = ("DocumentType",)
