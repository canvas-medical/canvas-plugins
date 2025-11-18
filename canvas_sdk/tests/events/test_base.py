import json
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest
from django.db import models

from canvas_generated.messages.events_pb2 import Event as EventRequest
from canvas_generated.messages.events_pb2 import EventType
from canvas_sdk.events.base import Actor, Event, TargetType

if TYPE_CHECKING:
    from canvas_sdk.v1.data import CanvasUser


@pytest.fixture
def user(db: None) -> "CanvasUser":
    """Fixture for a CanvasUser instance."""
    from canvas_sdk.test_utils.factories import CanvasUserFactory

    return CanvasUserFactory.create()


def test_target_type_init() -> None:
    """Test TargetType initialization."""
    mock_model = Mock(spec=models.Model)
    target = TargetType(id="123", type=mock_model)

    assert target.id == "123"
    assert target.type == mock_model


def test_target_type_instance_returns_model_instance() -> None:
    """Test that instance property returns the correct model instance."""
    mock_model = Mock(spec=models.Model)
    mock_manager = Mock()
    mock_instance = Mock()
    mock_manager.filter.return_value.first.return_value = mock_instance
    mock_model._default_manager = mock_manager

    target = TargetType(id="123", type=mock_model)
    result = target.instance

    mock_manager.filter.assert_called_once_with(id="123")
    assert result == mock_instance


def test_target_type_instance_returns_none_when_not_found() -> None:
    """Test that instance property returns None when model not found."""
    mock_model = Mock(spec=models.Model)
    mock_manager = Mock()
    mock_manager.filter.return_value.first.return_value = None
    mock_model._default_manager = mock_manager

    target = TargetType(id="123", type=mock_model)
    result = target.instance

    assert result is None


def test_target_type_instance_returns_none_when_type_is_none() -> None:
    """Test that instance property returns None when type is None."""
    target = TargetType(id="123", type=None)
    result = target.instance

    assert result is None


def test_target_type_instance_cached() -> None:
    """Test that instance property is cached."""
    mock_model = Mock(spec=models.Model)
    mock_manager = Mock()
    mock_instance = Mock()
    mock_manager.filter.return_value.first.return_value = mock_instance
    mock_model._default_manager = mock_manager

    target = TargetType(id="123", type=mock_model)

    result1 = target.instance
    result2 = target.instance

    mock_manager.filter.assert_called_once()
    assert result1 == result2


def test_actor_init() -> None:
    """Test Actor initialization."""
    actor = Actor(id="user_123")
    assert actor.id == "user_123"


def test_actor_init_with_none() -> None:
    """Test Actor initialization with None id."""
    actor = Actor(id=None)
    assert actor.id is None


def test_actor_instance_returns_user(user: "CanvasUser") -> None:
    """Test that instance property returns the correct CanvasUser."""
    actor = Actor(id=str(user.dbid))
    result = actor.instance

    assert result == user


@pytest.mark.django_db
def test_actor_instance_returns_none_when_not_found() -> None:
    """Test that instance property returns None when user not found."""
    actor = Actor(id="1")
    result = actor.instance

    assert result is None


def test_actor_instance_returns_none_when_id_is_none() -> None:
    """Test that instance property returns None when id is None."""
    actor = Actor(id=None)
    result = actor.instance

    assert result is None


@patch("canvas_sdk.v1.data.CanvasUser._meta.default_manager")
def test_actor_instance_cached(mock_manager: Mock) -> None:
    """Test that instance property is cached."""
    from canvas_sdk.v1.data import CanvasUser

    mock_user = Mock(spec=CanvasUser)
    mock_manager.filter.return_value.first.return_value = mock_user

    actor = Actor(id="user_123")

    result1 = actor.instance
    result2 = actor.instance

    mock_manager.filter.assert_called_once()
    assert result1 == result2


@patch("canvas_sdk.events.base.apps.get_model")
def test_event_init_with_valid_model(mock_get_model: Mock) -> None:
    """Test Event initialization with valid target model."""
    mock_model = Mock(spec=models.Model)
    mock_get_model.return_value = mock_model

    event_request = EventRequest()
    event_request.type = EventType.UNKNOWN
    event_request.target_type = "Patient"
    event_request.target = "1"
    event_request.actor = "1"
    event_request.context = json.dumps({"key": "value"})

    event = Event(event_request)

    assert event.type == EventType.UNKNOWN
    assert event.name == EventType.Name(EventType.UNKNOWN)
    assert event.context == {"key": "value"}
    assert event.target.id == "1"
    assert event.target.type == mock_model
    assert event.actor.id == "1"
    mock_get_model.assert_called_once_with(app_label="v1", model_name="Patient")


@patch("canvas_sdk.events.base.apps.get_model")
def test_event_init_with_invalid_model(mock_get_model: Mock) -> None:
    """Test Event initialization when model lookup fails."""
    mock_get_model.side_effect = LookupError("Model not found")

    event_request = EventRequest()
    event_request.type = EventType.UNKNOWN
    event_request.target_type = "InvalidModel"
    event_request.target = "target_123"
    event_request.actor = "user_123"
    event_request.context = "{}"

    event = Event(event_request)

    assert event.type == EventType.UNKNOWN
    assert event.target.id == "target_123"
    assert event.target.type is None


@patch("canvas_sdk.events.base.apps.get_model")
def test_event_init_with_invalid_json_context(mock_get_model: Mock) -> None:
    """Test Event initialization with invalid JSON context."""
    mock_get_model.return_value = Mock()

    event_request = EventRequest()
    event_request.type = EventType.UNKNOWN
    event_request.target_type = "SomeModel"
    event_request.target = "target_123"
    event_request.actor = "user_123"
    event_request.context = "invalid json"

    event = Event(event_request)

    assert event.context == {}


def test_event_init_source() -> None:
    """Test Event initialization with valid source."""
    event_request = EventRequest()
    event_request.type = EventType.UNKNOWN
    event_request.target_type = "SomeModel"
    event_request.target = "target_123"
    event_request.actor = "user_123"
    event_request.source = "api"

    event = Event(event_request)

    assert event.source == "api"
