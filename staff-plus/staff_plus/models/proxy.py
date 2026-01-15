from canvas_sdk.v1.data import CustomAttributeAwareManager, CustomAttributeMixin, Staff


# Proxy classes are kinda like database views, and can re-present the proxied
# model
class StaffProxy(Staff, CustomAttributeMixin):
    class Meta:
        proxy = True

    objects = CustomAttributeAwareManager()

    # Unable to do M2Ms this way, some "source" field never gets mapped. Only explanation after much
    # testing is that proxy classes cannot support it
    # specialties = ManyToManyField("staff_plus.Specialty", related_name="staff",
    #                               through="staff_plus.StaffSpecialty",through_fields=('staff', 'specialty'))
