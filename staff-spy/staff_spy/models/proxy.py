from canvas_sdk.v1.data import CustomAttributeAwareManager, CustomAttributeMixin, Staff


class StaffProxy(Staff, CustomAttributeMixin):
    class Meta:
        proxy = True

    objects = CustomAttributeAwareManager()
