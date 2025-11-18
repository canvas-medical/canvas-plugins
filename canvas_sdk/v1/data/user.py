from functools import cached_property
from typing import TYPE_CHECKING

from django.db import models

from canvas_sdk.v1.data.base import Model

if TYPE_CHECKING:
    from canvas_sdk.v1.data import Patient, Staff


class CanvasUser(Model):
    """A class representing a Canvas User."""

    class Meta:
        db_table = "canvas_sdk_data_api_auth_user_001"

    email = models.EmailField(db_column="email")
    phone_number = models.CharField(db_column="phone_number", max_length=255)
    last_invite_date_time = models.DateTimeField(null=True, blank=True)
    is_portal_registered = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    @cached_property
    def person_subclass(self) -> "Staff | Patient":
        """
        Return either the related Staff or Patient object.
        """
        return self.staff if self.is_staff else self.patient


__exports__ = ("CanvasUser",)
