from unittest.mock import Mock, patch

from canvas_sdk.effects.task import TaskStatus
from canvas_sdk.events import EventType
from canvas_sdk.v1.data.task import TaskPriority

from refill_priority_setter_plugin.protocols.create_refill_task import CreateRefillTaskProtocol


def test_create_refill_task_protocol_configuration() -> None:
    """Test that the protocol is configured to respond to the correct event type."""
    assert EventType.Name(EventType.REFILL_COMMAND__POST_COMMIT) in CreateRefillTaskProtocol.RESPONDS_TO


def test_create_refill_task_protocol_imports() -> None:
    """Test that the protocol can be imported and has expected attributes."""
    assert CreateRefillTaskProtocol is not None
    assert hasattr(CreateRefillTaskProtocol, "RESPONDS_TO")
    assert hasattr(CreateRefillTaskProtocol, "compute")


def test_create_refill_task_creates_task_for_new_refill() -> None:
    """Test that a task is created when a refill command is committed."""
    # Create a mock event
    mock_event = Mock()
    mock_event.target = Mock()
    mock_event.target.id = "test-refill-uuid-123"

    # Create protocol instance with mock context
    protocol = CreateRefillTaskProtocol(event=mock_event)

    # Mock context
    test_context = {
        'fields': {
            'prescribe': {
                'text': 'Lisinopril 10mg'
            }
        },
        'patient': {
            'id': 'patient-123'
        }
    }

    with patch.object(type(protocol), 'context', property(lambda self: test_context)):
        # Mock Task.objects.filter to return no existing tasks
        with patch('refill_priority_setter_plugin.protocols.create_refill_task.Task.objects.filter') as mock_task_filter:
            mock_queryset = Mock()
            mock_queryset.exists.return_value = False
            mock_task_filter.return_value = mock_queryset

            # Mock Team.objects.filter to return a team
            with patch('refill_priority_setter_plugin.protocols.create_refill_task.Team.objects.filter') as mock_team_filter:
                mock_team_queryset = Mock()
                mock_team_queryset.values_list.return_value.first.return_value = 'team-456'
                mock_team_filter.return_value = mock_team_queryset

                # Mock AddTask
                with patch('refill_priority_setter_plugin.protocols.create_refill_task.AddTask') as mock_add_task_class:
                    mock_add_task_instance = Mock()
                    mock_applied_effect = Mock()
                    mock_add_task_instance.apply.return_value = mock_applied_effect
                    mock_add_task_class.return_value = mock_add_task_instance

                    with patch('refill_priority_setter_plugin.protocols.create_refill_task.log'):
                        effects = protocol.compute()

                    # Verify AddTask was called with correct parameters
                    mock_add_task_class.assert_called_once_with(
                        title='Follow up on refill of Lisinopril 10mg',
                        priority=TaskPriority.URGENT,
                        patient_id='patient-123',
                        team_id='team-456'
                    )

                    # Verify apply() was called
                    mock_add_task_instance.apply.assert_called_once()

                    # Verify effects were returned
                    assert len(effects) == 1
                    assert effects[0] == mock_applied_effect


def test_create_refill_task_skips_duplicate_task() -> None:
    """Test that no task is created if one already exists for the same medication."""
    # Create a mock event
    mock_event = Mock()
    mock_event.target = Mock()
    mock_event.target.id = "test-refill-uuid-456"

    # Create protocol instance
    protocol = CreateRefillTaskProtocol(event=mock_event)

    # Mock context
    test_context = {
        'fields': {
            'prescribe': {
                'text': 'Metformin 500mg'
            }
        },
        'patient': {
            'id': 'patient-789'
        }
    }

    with patch.object(type(protocol), 'context', property(lambda self: test_context)):
        # Mock Task.objects.filter to return an existing task
        with patch('refill_priority_setter_plugin.protocols.create_refill_task.Task.objects.filter') as mock_task_filter:
            mock_queryset = Mock()
            mock_queryset.exists.return_value = True
            mock_task_filter.return_value = mock_queryset

            with patch('refill_priority_setter_plugin.protocols.create_refill_task.log'):
                effects = protocol.compute()

            # Verify no effects were returned
            assert len(effects) == 0

            # Verify Task.objects.filter was called with correct parameters
            mock_task_filter.assert_called_once_with(
                title='Follow up on refill of Metformin 500mg',
                status=TaskStatus.OPEN.value,
                patient__id='patient-789'
            )


def test_create_refill_task_handles_no_team() -> None:
    """Test that task is created with None team_id when no team is found."""
    # Create a mock event
    mock_event = Mock()
    mock_event.target = Mock()
    mock_event.target.id = "test-refill-uuid-789"

    # Create protocol instance
    protocol = CreateRefillTaskProtocol(event=mock_event)

    # Mock context
    test_context = {
        'fields': {
            'prescribe': {
                'text': 'Aspirin 81mg'
            }
        },
        'patient': {
            'id': 'patient-999'
        }
    }

    with patch.object(type(protocol), 'context', property(lambda self: test_context)):
        # Mock Task.objects.filter to return no existing tasks
        with patch('refill_priority_setter_plugin.protocols.create_refill_task.Task.objects.filter') as mock_task_filter:
            mock_queryset = Mock()
            mock_queryset.exists.return_value = False
            mock_task_filter.return_value = mock_queryset

            # Mock Team.objects.filter to return None (no team found)
            with patch('refill_priority_setter_plugin.protocols.create_refill_task.Team.objects.filter') as mock_team_filter:
                mock_team_queryset = Mock()
                mock_team_queryset.values_list.return_value.first.return_value = None
                mock_team_filter.return_value = mock_team_queryset

                # Mock AddTask
                with patch('refill_priority_setter_plugin.protocols.create_refill_task.AddTask') as mock_add_task_class:
                    mock_add_task_instance = Mock()
                    mock_applied_effect = Mock()
                    mock_add_task_instance.apply.return_value = mock_applied_effect
                    mock_add_task_class.return_value = mock_add_task_instance

                    with patch('refill_priority_setter_plugin.protocols.create_refill_task.log'):
                        effects = protocol.compute()

                    # Verify AddTask was called with team_id=None
                    mock_add_task_class.assert_called_once_with(
                        title='Follow up on refill of Aspirin 81mg',
                        priority=TaskPriority.URGENT,
                        patient_id='patient-999',
                        team_id=None
                    )

                    # Verify effects were returned
                    assert len(effects) == 1


def test_create_refill_task_extracts_medication_from_context() -> None:
    """Test that medication name is correctly extracted from the context."""
    # Create a mock event
    mock_event = Mock()
    mock_event.target = Mock()
    mock_event.target.id = "test-refill-uuid"

    # Create protocol instance
    protocol = CreateRefillTaskProtocol(event=mock_event)

    # Mock context with specific medication
    test_context = {
        'fields': {
            'prescribe': {
                'text': 'Atorvastatin 20mg'
            }
        },
        'patient': {
            'id': 'patient-123'
        }
    }

    with patch.object(type(protocol), 'context', property(lambda self: test_context)):
        with patch('refill_priority_setter_plugin.protocols.create_refill_task.Task.objects.filter') as mock_task_filter:
            mock_queryset = Mock()
            mock_queryset.exists.return_value = False
            mock_task_filter.return_value = mock_queryset

            with patch('refill_priority_setter_plugin.protocols.create_refill_task.Team.objects.filter') as mock_team_filter:
                mock_team_queryset = Mock()
                mock_team_queryset.values_list.return_value.first.return_value = 'team-123'
                mock_team_filter.return_value = mock_team_queryset

                with patch('refill_priority_setter_plugin.protocols.create_refill_task.AddTask') as mock_add_task_class:
                    mock_add_task_instance = Mock()
                    mock_add_task_instance.apply.return_value = Mock()
                    mock_add_task_class.return_value = mock_add_task_instance

                    with patch('refill_priority_setter_plugin.protocols.create_refill_task.log'):
                        protocol.compute()

                    # Verify the medication name was used in the task title
                    call_kwargs = mock_add_task_class.call_args[1]
                    assert 'Atorvastatin 20mg' in call_kwargs['title']
                    assert call_kwargs['title'] == 'Follow up on refill of Atorvastatin 20mg'
