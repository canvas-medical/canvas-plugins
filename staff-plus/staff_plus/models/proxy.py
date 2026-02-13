from canvas_sdk.v1.data import CustomAttributeAwareManager, CustomAttributeMixin, Patient, Staff


class StaffProxy(Staff, CustomAttributeMixin):
    class Meta:
        proxy = True

    objects = CustomAttributeAwareManager()


class PatientProxy(Patient, CustomAttributeMixin):
    class Meta:
        proxy = True

    objects = CustomAttributeAwareManager()
