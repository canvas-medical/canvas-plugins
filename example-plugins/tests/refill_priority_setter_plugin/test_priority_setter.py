from unittest.mock import Mock, patch

from canvas_sdk.effects.task import TaskStatus
from canvas_sdk.events import EventType
from canvas_sdk.v1.data.task import TaskPriority
from canvas_sdk.v1.data.team import TeamResponsibility

from refill_priority_setter_plugin.protocols.priority_setter import RefillTaskPriorityProtocol


def test_priority_setter_protocol_configuration() -> None:
    """Test that the protocol is configured to respond to the correct event types."""
    assert EventType.Name(EventType.TASK_CREATED) in RefillTaskPriorityProtocol.RESPONDS_TO
    assert EventType.Name(EventType.TASK_UPDATED) in RefillTaskPriorityProtocol.RESPONDS_TO
    assert EventType.Name(EventType.TASK_COMMAND__POST_UPDATE) in RefillTaskPriorityProtocol.RESPONDS_TO


def test_priority_setter_protocol_imports() -> None:
    """Test that the protocol can be imported and has expected attributes."""
    assert RefillTaskPriorityProtocol is not None
    assert hasattr(RefillTaskPriorityProtocol, "RESPONDS_TO")
    assert hasattr(RefillTaskPriorityProtocol, "compute")


def test_priority_setter_sets_urgent_for_refill_team() -> None:
    """Test that priority is set to URGENT for tasks assigned to refill teams."""
    # Create a mock event
    mock_event = Mock()
    mock_event.type = EventType.TASK_CREATED
    mock_event.target = Mock()
    mock_event.target.id = "task-123"

    # Create protocol instance
    protocol = RefillTaskPriorityProtocol(event=mock_event)

    # Mock task with a team that has PROCESS_REFILL_REQUESTS responsibility
    mock_task = Mock()
    mock_task.status = TaskStatus.OPEN.value
    mock_task.priority = None
    mock_team = Mock()
    mock_team.responsibilities = [TeamResponsibility.PROCESS_REFILL_REQUESTS]
    mock_task.team = mock_team

    with patch('refill_priority_setter_plugin.protocols.priority_setter.Task.objects.get', return_value=mock_task):
        # Mock UpdateTask
        with patch('refill_priority_setter_plugin.protocols.priority_setter.UpdateTask') as mock_update_task_class:
            mock_update_task_instance = Mock()
            mock_applied_effect = Mock()
            mock_update_task_instance.apply.return_value = mock_applied_effect
            mock_update_task_class.return_value = mock_update_task_instance

            # Mock AddTask
            with patch('refill_priority_setter_plugin.protocols.priority_setter.AddTask') as mock_add_task_class:
                mock_add_task_instance = Mock()
                mock_add_task_instance.apply.return_value = Mock()
                mock_add_task_class.return_value = mock_add_task_instance

                with patch('refill_priority_setter_plugin.protocols.priority_setter.log'):
                    effects = protocol.compute()

                # Verify UpdateTask was called with URGENT priority
                mock_update_task_class.assert_called_once_with(
                    id="task-123",
                    priority=TaskPriority.URGENT
                )

                # Verify effects were returned
                assert len(effects) == 2


def test_priority_setter_skips_closed_tasks() -> None:
    """Test that priority is not updated for closed tasks."""
    # Create a mock event
    mock_event = Mock()
    mock_event.type = EventType.TASK_UPDATED
    mock_event.target = Mock()
    mock_event.target.id = "task-456"

    # Create protocol instance
    protocol = RefillTaskPriorityProtocol(event=mock_event)

    # Mock task with CLOSED status
    mock_task = Mock()
    mock_task.status = TaskStatus.CLOSED.value
    mock_task.priority = None
    mock_task.team = None

    with patch('refill_priority_setter_plugin.protocols.priority_setter.Task.objects.get', return_value=mock_task):
        with patch('refill_priority_setter_plugin.protocols.priority_setter.log'):
            effects = protocol.compute()

        # Verify no effects were returned
        assert len(effects) == 0


def test_priority_setter_skips_already_urgent_tasks() -> None:
    """Test that priority is not updated if already URGENT."""
    # Create a mock event
    mock_event = Mock()
    mock_event.type = EventType.TASK_CREATED
    mock_event.target = Mock()
    mock_event.target.id = "task-789"

    # Create protocol instance
    protocol = RefillTaskPriorityProtocol(event=mock_event)

    # Mock task with URGENT priority
    mock_task = Mock()
    mock_task.status = TaskStatus.OPEN.value
    mock_task.priority = TaskPriority.URGENT.value
    mock_team = Mock()
    mock_team.responsibilities = [TeamResponsibility.PROCESS_REFILL_REQUESTS]
    mock_task.team = mock_team

    with patch('refill_priority_setter_plugin.protocols.priority_setter.Task.objects.get', return_value=mock_task):
        with patch('refill_priority_setter_plugin.protocols.priority_setter.log'):
            effects = protocol.compute()

        # Verify no effects were returned
        assert len(effects) == 0


def test_priority_setter_handles_no_team() -> None:
    """Test that priority is not updated when task has no team assigned."""
    # Create a mock event
    mock_event = Mock()
    mock_event.type = EventType.TASK_CREATED
    mock_event.target = Mock()
    mock_event.target.id = "task-999"

    # Create protocol instance
    protocol = RefillTaskPriorityProtocol(event=mock_event)

    # Mock task with no team
    mock_task = Mock()
    mock_task.status = TaskStatus.OPEN.value
    mock_task.priority = None
    mock_task.team = None

    with patch('refill_priority_setter_plugin.protocols.priority_setter.Task.objects.get', return_value=mock_task):
        with patch('refill_priority_setter_plugin.protocols.priority_setter.log'):
            effects = protocol.compute()

        # Verify no effects were returned
        assert len(effects) == 0


def test_priority_setter_handles_team_without_refill_responsibility() -> None:
    """Test that priority is not updated for teams without refill responsibilities."""
    # Create a mock event
    mock_event = Mock()
    mock_event.type = EventType.TASK_CREATED
    mock_event.target = Mock()
    mock_event.target.id = "task-111"

    # Create protocol instance
    protocol = RefillTaskPriorityProtocol(event=mock_event)

    # Mock task with team that doesn't have PROCESS_REFILL_REQUESTS responsibility
    mock_task = Mock()
    mock_task.status = TaskStatus.OPEN.value
    mock_task.priority = None
    mock_team = Mock()
    mock_team.responsibilities = []  # Empty responsibilities, no refill processing
    mock_task.team = mock_team

    with patch('refill_priority_setter_plugin.protocols.priority_setter.Task.objects.get', return_value=mock_task):
        with patch('refill_priority_setter_plugin.protocols.priority_setter.log'):
            effects = protocol.compute()

        # Verify no effects were returned
        assert len(effects) == 0


def test_priority_setter_command_event_type() -> None:
    """Test that the protocol handles TASK_COMMAND__POST_UPDATE events."""
    # Create a mock event
    mock_event = Mock()
    mock_event.type = EventType.TASK_COMMAND__POST_UPDATE
    mock_event.target = Mock()
    mock_event.target.id = "task-command-123"

    # Create protocol instance
    protocol = RefillTaskPriorityProtocol(event=mock_event)

    # Mock context for command event
    test_context = {
        'fields': {
            'assign_to': {
                'value': 'team-456'
            },
            'priority': None
        }
    }

    with patch.object(type(protocol), 'context', property(lambda self: test_context)):
        # Mock Team.objects.get
        mock_team = Mock()
        mock_team.responsibilities = [TeamResponsibility.PROCESS_REFILL_REQUESTS]

        with patch('refill_priority_setter_plugin.protocols.priority_setter.Team.objects.get', return_value=mock_team):
            # Mock TaskCommand
            with patch('refill_priority_setter_plugin.protocols.priority_setter.TaskCommand') as mock_task_command_class:
                mock_task_command_instance = Mock()
                mock_edit_effect = Mock()
                mock_task_command_instance.edit.return_value = mock_edit_effect
                mock_task_command_class.return_value = mock_task_command_instance

                with patch('refill_priority_setter_plugin.protocols.priority_setter.log'):
                    effects = protocol.compute()

                # Verify TaskCommand was called with URGENT priority
                mock_task_command_class.assert_called_once_with(
                    command_uuid="task-command-123",
                    priority=TaskPriority.URGENT
                )

                # Verify effects were returned
                assert len(effects) == 1
                assert effects[0] == mock_edit_effect


def test_priority_setter_get_desired_priority_with_refill_team() -> None:
    """Test that _get_desired_priority returns URGENT for refill teams."""
    # Create a mock event
    mock_event = Mock()
    mock_event.target = Mock()
    mock_event.target.id = "task-test"

    # Create protocol instance
    protocol = RefillTaskPriorityProtocol(event=mock_event)

    # Mock team with PROCESS_REFILL_REQUESTS responsibility
    mock_team = Mock()
    mock_team.responsibilities = [TeamResponsibility.PROCESS_REFILL_REQUESTS]

    # Call the method
    desired_priority = protocol._get_desired_priority(mock_team)

    # Verify URGENT is returned
    assert desired_priority == TaskPriority.URGENT


def test_priority_setter_get_desired_priority_without_refill_team() -> None:
    """Test that _get_desired_priority returns None for non-refill teams."""
    # Create a mock event
    mock_event = Mock()
    mock_event.target = Mock()
    mock_event.target.id = "task-test"

    # Create protocol instance
    protocol = RefillTaskPriorityProtocol(event=mock_event)

    # Mock team without PROCESS_REFILL_REQUESTS responsibility
    mock_team = Mock()
    mock_team.responsibilities = []  # Empty responsibilities, no refill processing

    # Call the method
    desired_priority = protocol._get_desired_priority(mock_team)

    # Verify None is returned
    assert desired_priority is None


def test_priority_setter_get_desired_priority_with_no_team() -> None:
    """Test that _get_desired_priority returns None when no team is provided."""
    # Create a mock event
    mock_event = Mock()
    mock_event.target = Mock()
    mock_event.target.id = "task-test"

    # Create protocol instance
    protocol = RefillTaskPriorityProtocol(event=mock_event)

    # Call the method with None
    desired_priority = protocol._get_desired_priority(None)

    # Verify None is returned
    assert desired_priority is None


def test_priority_setter_prevents_downgrade_from_routine_to_none() -> None:
    """Test that priority is not changed from ROUTINE to None for non-refill teams.

    This prevents accidentally clearing priority from tasks that are already prioritized
    but not URGENT when they are assigned to teams without refill responsibilities.
    """
    # Create a mock event
    mock_event = Mock()
    mock_event.type = EventType.TASK_CREATED
    mock_event.target = Mock()
    mock_event.target.id = "task-routine"

    # Create protocol instance
    protocol = RefillTaskPriorityProtocol(event=mock_event)

    # Mock task with ROUTINE priority and team without refill responsibilities
    mock_task = Mock()
    mock_task.status = TaskStatus.OPEN.value
    mock_task.priority = TaskPriority.ROUTINE.value  # Key: non-URGENT priority
    mock_team = Mock()
    mock_team.responsibilities = []  # No refill responsibility = desired priority is None
    mock_task.team = mock_team

    with patch('refill_priority_setter_plugin.protocols.priority_setter.Task.objects.get', return_value=mock_task):
        with patch('refill_priority_setter_plugin.protocols.priority_setter.log'):
            effects = protocol.compute()

        # Verify no effects were returned (priority not downgraded to None)
        assert len(effects) == 0


def test_priority_setter_command_event_assigned_to_user() -> None:
    """Test that the protocol handles TASK_COMMAND__POST_UPDATE when assigned to a user (not a team).

    When a task is assigned to a user instead of a team, no priority changes should occur.
    """
    # Create a mock event
    mock_event = Mock()
    mock_event.type = EventType.TASK_COMMAND__POST_UPDATE
    mock_event.target = Mock()
    mock_event.target.id = "task-command-user-assigned"

    # Create protocol instance
    protocol = RefillTaskPriorityProtocol(event=mock_event)

    # Mock context for command event assigned to a user (not a team)
    test_context = {
        'fields': {
            'assign_to': {
                'value': 'user-789'  # Assigned to user, not team
            },
            'priority': None
        }
    }

    with patch.object(type(protocol), 'context', property(lambda self: test_context)):
        with patch('refill_priority_setter_plugin.protocols.priority_setter.log'):
            effects = protocol.compute()

        # Verify no effects were returned (no team = no priority update)
        assert len(effects) == 0
