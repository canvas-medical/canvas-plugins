import factory

from canvas_sdk.v1.data import AuthGroup, Role, RoleGroup, RoleGroupGroup, StaffRole


class AuthGroupFactory(factory.django.DjangoModelFactory[AuthGroup]):
    """Factory for creating an AuthGroup."""

    class Meta:
        model = AuthGroup

    name = factory.Sequence(lambda n: f"Group {n}")


class RoleFactory(factory.django.DjangoModelFactory[Role]):
    """Factory for creating a Role."""

    class Meta:
        model = Role
        django_get_or_create = ("internal_code",)

    internal_code = factory.Sequence(lambda n: f"R{n}")
    public_abbreviation = "MD"
    domain = StaffRole.RoleDomain.CLINICAL
    name = "Physician"
    domain_privilege_level = 100000
    permissions = factory.LazyFunction(dict)
    role_type = StaffRole.RoleType.PROVIDER


class RoleGroupFactory(factory.django.DjangoModelFactory[RoleGroup]):
    """Factory for creating a RoleGroup."""

    class Meta:
        model = RoleGroup

    role = factory.SubFactory(RoleFactory)


class RoleGroupGroupFactory(factory.django.DjangoModelFactory[RoleGroupGroup]):
    """Factory for linking a RoleGroup to an AuthGroup."""

    class Meta:
        model = RoleGroupGroup

    role_group = factory.SubFactory(RoleGroupFactory)
    group = factory.SubFactory(AuthGroupFactory)
