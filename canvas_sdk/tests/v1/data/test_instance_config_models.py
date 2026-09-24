from datetime import timedelta

import pytest

from canvas_sdk.v1.data import LetterTemplate, PostingRule, Role, ScheduleDuration
from canvas_sdk.v1.data.letter_template import LetterTemplateType
from canvas_sdk.v1.data.posting_rule import PostingRuleBehavior
from canvas_sdk.v1.data.role import RoleType
from canvas_sdk.v1.data.staff import StaffRole


@pytest.mark.django_db
def test_role_round_trips_home_app_columns() -> None:
    """Role reads back every api_role column the view projects."""
    Role.objects.create(
        internal_code="MD",
        public_abbreviation="MD",
        domain=StaffRole.RoleDomain.CLINICAL,
        name="Physician",
        domain_privilege_level=100000,
        role_type=RoleType.PROVIDER,
    )

    role = Role.objects.get(internal_code="MD")
    assert role.domain == "CLI"
    assert role.role_type == "PROVIDER"
    assert role.domain_privilege_level == 100000


@pytest.mark.django_db
def test_schedule_duration_filters_appointment_options() -> None:
    """ScheduleDuration exposes the duration and the appointment-option flag."""
    ScheduleDuration.objects.create(duration=timedelta(minutes=30))
    ScheduleDuration.objects.create(
        duration=timedelta(minutes=45), is_appointment_duration_option=False
    )

    options = ScheduleDuration.objects.filter(is_appointment_duration_option=True)
    assert [d.duration for d in options] == [timedelta(minutes=30)]


@pytest.mark.django_db
def test_letter_template_stores_type_and_locations() -> None:
    """LetterTemplate reads back its array columns."""
    LetterTemplate.objects.create(
        name="Welcome",
        template_type=[LetterTemplateType.LETTER, LetterTemplateType.MESSAGE],
        locations=["SF"],
    )

    template = LetterTemplate.objects.get(name="Welcome")
    assert template.active is True
    assert template.template_type == ["letter", "message"]
    assert template.locations == ["SF"]


@pytest.mark.django_db
def test_posting_rule_without_transactor() -> None:
    """PostingRule allows a null transactor (a rule that applies to every payer)."""
    PostingRule.objects.create(
        description="Contractual obligation write-off",
        adjustment_group="CO",
        adjustment_code="45",
        behavior=PostingRuleBehavior.WRITE_OFF,
    )

    rule = PostingRule.objects.get(adjustment_group="CO")
    assert rule.transactor is None
    assert rule.is_preset is False
