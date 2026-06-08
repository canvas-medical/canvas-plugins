"""Tests for the Team model."""

import uuid

import pytest

from canvas_sdk.test_utils.factories import TeamFactory
from canvas_sdk.v1.data.team import Team


@pytest.mark.django_db
def test_group_id_defaults_to_none() -> None:
    """Test that Team.group_id is null when not set."""
    team = TeamFactory.create()
    assert team.group_id is None


@pytest.mark.django_db
def test_group_id_round_trips() -> None:
    """Test that a populated Team.group_id is persisted and read back unchanged."""
    group_id = uuid.uuid4()
    team = TeamFactory.create(group_id=group_id)

    refetched = Team.objects.get(dbid=team.dbid)
    assert refetched.group_id == group_id
