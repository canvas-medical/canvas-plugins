from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel
from canvas_sdk.v1.data.service_provider import ServiceProvider


class OrganizationalEntity(IdentifiableModel):
    """An external entity (e.g. a ServiceProvider) referenced by a generic relation."""

    class Meta:
        db_table = "canvas_sdk_data_api_organizationalentity_001"

    class OrganizationalEntityType(models.TextChoices):
        """OrganizationalEntityType."""

        TRANSACTOR = "Transactor", "Transactor"
        BUSINESS_ENTITY = "Business Entity", "Business Entity"
        VENDOR = "Vendor", "Vendor"
        SERVICE_PROVIDER = "Service Provider", "Service Provider"

    content_type = models.ForeignKey(
        "v1.ContentType", on_delete=models.DO_NOTHING, related_name="+", null=True
    )
    object_id = models.BigIntegerField(null=True)
    name = models.TextField()
    active = models.BooleanField(default=False)
    type = models.CharField(max_length=20, choices=OrganizationalEntityType.choices)

    @property
    def service_provider(self) -> ServiceProvider | None:
        """The external ServiceProvider this entity points at, when it is one."""
        if self.type == self.OrganizationalEntityType.SERVICE_PROVIDER and self.object_id:
            return ServiceProvider.objects.filter(dbid=self.object_id).first()
        return None

    def __str__(self) -> str:
        return self.name


__exports__ = ("OrganizationalEntity",)
