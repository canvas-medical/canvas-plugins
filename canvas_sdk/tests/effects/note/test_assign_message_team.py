import json
from collections.abc import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.note.message import AssignMessageTeam


@pytest.fixture
def mock_db() -> Generator[dict[str, MagicMock]]:
    """Mock message and team lookups to exist by default."""
    with (
        patch("canvas_sdk.v1.data.Message.objects") as mock_message,
        patch("canvas_sdk.v1.data.Team.objects") as mock_team,
    ):
        mock_message.filter.return_value.exists.return_value = True
        mock_team.filter.return_value.exists.return_value = True
        yield {"message": mock_message, "team": mock_team}


def test_assign_payload(mock_db: dict[str, MagicMock]) -> None:
    """Assigning sends the message and team ids."""
    message_id, team_id = uuid4(), uuid4()
    effect = AssignMessageTeam(message_id=message_id, team_id=team_id).apply()

    assert effect.type == EffectType.ASSIGN_MESSAGE_TEAM
    assert json.loads(effect.payload) == {
        "data": {"message_id": str(message_id), "team_id": str(team_id)}
    }


def test_unassign_payload(mock_db: dict[str, MagicMock]) -> None:
    """A None team unassigns without looking up a team."""
    message_id = uuid4()
    effect = AssignMessageTeam(message_id=message_id, team_id=None).apply()

    assert json.loads(effect.payload) == {"data": {"message_id": str(message_id), "team_id": None}}
    mock_db["team"].filter.assert_not_called()


def test_unknown_message(mock_db: dict[str, MagicMock]) -> None:
    """An unknown message is rejected."""
    mock_db["message"].filter.return_value.exists.return_value = False
    message_id = uuid4()

    with pytest.raises(ValidationError) as exc_info:
        AssignMessageTeam(message_id=message_id, team_id=uuid4()).apply()

    assert f"Message with id {message_id} does not exist" in str(exc_info.value)


def test_unknown_team(mock_db: dict[str, MagicMock]) -> None:
    """An unknown team is rejected."""
    mock_db["team"].filter.return_value.exists.return_value = False
    team_id = uuid4()

    with pytest.raises(ValidationError) as exc_info:
        AssignMessageTeam(message_id=uuid4(), team_id=team_id).apply()

    assert f"Team with id {team_id} does not exist" in str(exc_info.value)


@pytest.mark.parametrize("team_id", ["", "not-a-uuid"])
def test_malformed_team_id_is_a_validation_error(
    mock_db: dict[str, MagicMock], team_id: str
) -> None:
    """A malformed team id fails pydantic validation before any lookup."""
    with pytest.raises(ValidationError):
        AssignMessageTeam(message_id=uuid4(), team_id=team_id).apply()

    mock_db["team"].filter.assert_not_called()


@pytest.mark.parametrize("message_id", ["", "not-a-uuid"])
def test_malformed_message_id_is_a_validation_error(
    mock_db: dict[str, MagicMock], message_id: str
) -> None:
    """A malformed message id fails pydantic validation before any lookup."""
    with pytest.raises(ValidationError):
        AssignMessageTeam(message_id=message_id, team_id=uuid4()).apply()

    mock_db["message"].filter.assert_not_called()


def test_team_id_is_required(mock_db: dict[str, MagicMock]) -> None:
    """Leaving team_id out is an error; unassigning takes an explicit None."""
    with pytest.raises(ValidationError):
        AssignMessageTeam(message_id=uuid4()).apply()  # type: ignore[call-arg]
