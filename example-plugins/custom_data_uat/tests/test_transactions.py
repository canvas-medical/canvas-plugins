"""Tests for the UAT transaction checks, run against the test database."""

from canvas_sdk.test_utils.factories import PatientFactory
from custom_data_uat.handlers.uat_api import CustomDataUatAPI
from custom_data_uat.models.tag import PatientTag, Tag


def make_api() -> CustomDataUatAPI:
    """Build the API handler without an incoming request."""
    return CustomDataUatAPI.__new__(CustomDataUatAPI)


def test_transactions_pass_and_clean_up() -> None:
    """Commit, rollback, and nested savepoint checks all pass and leave no rows behind."""
    PatientFactory.create()

    section = make_api()._test_transactions()

    assert section["checks"] == {
        "commit_tag_exists": True,
        "commit_pt_exists": True,
        "rollback_tag_gone": True,
        "outer_survived": True,
        "inner_rolled_back": True,
    }
    assert section["passed"] is True
    assert not Tag.objects.exists()
    assert not PatientTag.objects.exists()


def test_transactions_skip_without_patients() -> None:
    """With no patient to tag, the section passes with a note instead of running."""
    section = make_api()._test_transactions()

    assert section == {"passed": True, "checks": {"note": "No patients found — cannot test"}}
