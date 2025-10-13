"""
Tests for the AddBillingLineItemToAutismDiagnoses handler.

These tests validate the handler logic for creating billing line items when autism 
diagnosis conditions are detected with the correct ICD-10 coding.
"""
from unittest.mock import Mock, patch

from canvas_sdk.effects.billing_line_item import AddBillingLineItem
from canvas_sdk.events import EventType

from autism_diagnosis_billing.handlers.add_billing_line_item_handler import AddBillingLineItemToAutismDiagnoses


class MockCoding:
    """Mock ICD-10 coding for testing."""
    def __init__(self, code="Z13.41", system="ICD10"):
        self.code = code
        self.system = system


class MockCodings:
    """Mock codings queryset for testing."""
    def __init__(self, codes=None):
        self.codes = codes or []

    def filter(self, system=None):
        return self
    
    def first(self):
        return self.codes[0] if self.codes else None


class MockAssessment:
    """Mock assessment for testing."""
    def __init__(self, assessment_id="test-assessment-id"):
        self.id = assessment_id


class MockAssessments:
    """Mock assessments queryset for testing."""
    def __init__(self, assessments=None):
        self.assessments = assessments or []
    
    def last(self):
        return self.assessments[-1] if self.assessments else None


class MockDiagnosis:
    """Mock diagnosis/condition for testing."""
    def __init__(self, diagnosis_id="test-diagnosis-id", codings=None, assessments=None):
        self.id = diagnosis_id
        self.codings = MockCodings(codings)
        self.assessments = MockAssessments(assessments)


class MockNote:
    """Mock note for testing."""
    def __init__(self, note_id="test-note-id"):
        self.id = note_id


class MockCommand:
    """Mock command for testing."""
    def __init__(self, command_id="test-command-id", anchor_object=None, note=None):
        self.id = command_id
        self.anchor_object = anchor_object
        self.note = note or MockNote()


class MockEvent:
    """Mock event for testing."""
    def __init__(self, target_id="test-command-id"):
        self.target = Mock()
        self.target.id = target_id


def test_handler_responds_to_correct_event():
    """Test that the handler responds to DIAGNOSE_COMMAND__POST_COMMIT events."""
    expected_event = EventType.Name(EventType.DIAGNOSE_COMMAND__POST_COMMIT)
    assert AddBillingLineItemToAutismDiagnoses.RESPONDS_TO == expected_event
    assert expected_event == "DIAGNOSE_COMMAND__POST_COMMIT"


@patch('autism_diagnosis_billing.handlers.add_billing_line_item_handler.Command')
def test_autism_diagnosis_creates_billing_line_item(mock_command_model):
    """Test that autism diagnosis (Z13.41) creates a billing line item."""
    # Setup mocks
    assessment = MockAssessment("assessment-123")
    coding = MockCoding("Z13.41", "ICD10")
    diagnosis = MockDiagnosis(
        "diagnosis-123", 
        codings=[coding], 
        assessments=[assessment]
    )
    note = MockNote("note-456")
    command = MockCommand("command-789", anchor_object=diagnosis, note=note)
    
    mock_command_model.objects.get.return_value = command
    
    event = MockEvent("command-789")
    handler = AddBillingLineItemToAutismDiagnoses(event)
    
    with patch.object(AddBillingLineItem, 'apply') as mock_apply:
        mock_apply.return_value = Mock()
        
        effects = handler.compute()
        
        # Verify billing line item was created
        assert len(effects) == 1
        mock_apply.assert_called_once()


@patch('autism_diagnosis_billing.handlers.add_billing_line_item_handler.Command')  
def test_autism_diagnosis_with_dots_creates_billing_line_item(mock_command_model):
    """Test that autism diagnosis with dots in code (Z13.41) creates a billing line item."""
    # Setup mocks with dotted ICD-10 code
    assessment = MockAssessment("assessment-123")
    coding = MockCoding("Z13.41", "ICD10")  # Code with dots
    diagnosis = MockDiagnosis(
        "diagnosis-123", 
        codings=[coding], 
        assessments=[assessment]
    )
    note = MockNote("note-456")
    command = MockCommand("command-789", anchor_object=diagnosis, note=note)
    
    mock_command_model.objects.get.return_value = command
    
    event = MockEvent("command-789")
    handler = AddBillingLineItemToAutismDiagnoses(event)
    
    with patch.object(AddBillingLineItem, 'apply') as mock_apply:
        mock_apply.return_value = Mock()
        
        effects = handler.compute()
        
        # Verify billing line item was created (dots should be removed)
        assert len(effects) == 1
        mock_apply.assert_called_once()


@patch('autism_diagnosis_billing.handlers.add_billing_line_item_handler.Command')
def test_non_autism_diagnosis_no_billing_line_item(mock_command_model):
    """Test that non-autism diagnoses don't create billing line items."""
    # Setup mocks with different ICD-10 code
    coding = MockCoding("Z00.00", "ICD10")  # Different code
    diagnosis = MockDiagnosis("diagnosis-123", codings=[coding])
    command = MockCommand("command-789", anchor_object=diagnosis)
    
    mock_command_model.objects.get.return_value = command
    
    event = MockEvent("command-789")
    handler = AddBillingLineItemToAutismDiagnoses(event)
    
    effects = handler.compute()
    
    # Verify no billing line item was created
    assert len(effects) == 0


@patch('autism_diagnosis_billing.handlers.add_billing_line_item_handler.Command')
def test_diagnosis_without_icd10_coding_no_billing_line_item(mock_command_model):
    """Test that diagnoses without ICD-10 coding don't create billing line items."""
    # Setup mocks with no ICD-10 coding
    diagnosis = MockDiagnosis("diagnosis-123", codings=[])  # No codings
    command = MockCommand("command-789", anchor_object=diagnosis)
    
    mock_command_model.objects.get.return_value = command
    
    event = MockEvent("command-789")
    handler = AddBillingLineItemToAutismDiagnoses(event)
    
    effects = handler.compute()
    
    # Verify no billing line item was created
    assert len(effects) == 0


@patch('autism_diagnosis_billing.handlers.add_billing_line_item_handler.Command')
def test_command_without_anchor_object_no_billing_line_item(mock_command_model):
    """Test that commands without anchor objects don't create billing line items."""
    # Setup mocks with no anchor object
    command = MockCommand("command-789", anchor_object=None)
    
    mock_command_model.objects.get.return_value = command
    
    event = MockEvent("command-789")
    handler = AddBillingLineItemToAutismDiagnoses(event)
    
    effects = handler.compute()
    
    # Verify no billing line item was created
    assert len(effects) == 0


@patch('autism_diagnosis_billing.handlers.add_billing_line_item_handler.Command')
def test_autism_diagnosis_without_assessments(mock_command_model):
    """Test autism diagnosis without assessments still creates billing line item."""
    # Setup mocks without assessments
    coding = MockCoding("Z13.41", "ICD10")
    diagnosis = MockDiagnosis("diagnosis-123", codings=[coding], assessments=[])  # No assessments
    note = MockNote("note-456")
    command = MockCommand("command-789", anchor_object=diagnosis, note=note)
    
    mock_command_model.objects.get.return_value = command
    
    event = MockEvent("command-789")
    handler = AddBillingLineItemToAutismDiagnoses(event)
    
    with patch.object(AddBillingLineItem, 'apply') as mock_apply:
        mock_apply.return_value = Mock()
        
        effects = handler.compute()
        
        # Verify billing line item was created with empty assessment_ids
        assert len(effects) == 1
        mock_apply.assert_called_once()


@patch('autism_diagnosis_billing.handlers.add_billing_line_item_handler.Command')
def test_command_does_not_exist_error_handling(mock_command_model):
    """Test error handling when command does not exist."""
    from canvas_sdk.v1.data.command import Command
    
    # Setup mock to raise DoesNotExist
    mock_command_model.DoesNotExist = Command.DoesNotExist
    mock_command_model.objects.get.side_effect = Command.DoesNotExist()
    
    event = MockEvent("nonexistent-command")
    handler = AddBillingLineItemToAutismDiagnoses(event)
    
    effects = handler.compute()
    
    # Verify no effects returned and error handled gracefully
    assert len(effects) == 0


@patch('autism_diagnosis_billing.handlers.add_billing_line_item_handler.Command')
def test_billing_line_item_parameters(mock_command_model):
    """Test that the billing line item is created with correct parameters."""
    # Setup mocks
    assessment = MockAssessment("assessment-123")
    coding = MockCoding("Z13.41", "ICD10")
    diagnosis = MockDiagnosis(
        "diagnosis-123", 
        codings=[coding], 
        assessments=[assessment]
    )
    note = MockNote("note-456")
    command = MockCommand("command-789", anchor_object=diagnosis, note=note)
    
    mock_command_model.objects.get.return_value = command
    
    event = MockEvent("command-789")
    handler = AddBillingLineItemToAutismDiagnoses(event)
    
    with patch.object(AddBillingLineItem, '__init__', return_value=None) as mock_init, \
         patch.object(AddBillingLineItem, 'apply') as mock_apply:
        
        mock_apply.return_value = Mock()
        
        handler.compute()
        
        # Verify AddBillingLineItem was called with correct parameters
        mock_init.assert_called_once_with(
            note_id="note-456",
            cpt="AUTISM_DX",
            assessment_ids=["assessment-123"],
        )


@patch('autism_diagnosis_billing.handlers.add_billing_line_item_handler.Command')
def test_icd_code_normalization(mock_command_model):
    """Test that ICD-10 codes are properly normalized (dots removed)."""
    # Test various formats of the same code
    test_cases = [
        "Z13.41",    # With dot
        "Z1341",     # Without dot
        "Z13..41",   # Multiple dots
        "Z.1.3.4.1", # Dots throughout
    ]
    
    for icd_code in test_cases:
        assessment = MockAssessment("assessment-123")
        coding = MockCoding(icd_code, "ICD10")
        diagnosis = MockDiagnosis(
            "diagnosis-123", 
            codings=[coding], 
            assessments=[assessment]
        )
        note = MockNote("note-456")
        command = MockCommand("command-789", anchor_object=diagnosis, note=note)
        
        mock_command_model.objects.get.return_value = command
        
        event = MockEvent("command-789")
        handler = AddBillingLineItemToAutismDiagnoses(event)
        
        with patch.object(AddBillingLineItem, 'apply') as mock_apply:
            mock_apply.return_value = Mock()
            
            effects = handler.compute()
            
            # All should create billing line item since they normalize to Z1341
            assert len(effects) == 1, f"Failed for ICD code: {icd_code}"
            mock_apply.assert_called_once()
            mock_apply.reset_mock()


if __name__ == "__main__":
    # Run basic validation tests
    test_handler_responds_to_correct_event()
    print("✓ Event type test passed")
    
    test_autism_diagnosis_creates_billing_line_item()
    print("✓ Autism diagnosis test passed")
    
    test_non_autism_diagnosis_no_billing_line_item()
    print("✓ Non-autism diagnosis test passed")
    
    test_diagnosis_without_icd10_coding_no_billing_line_item()
    print("✓ No ICD-10 coding test passed")
    
    test_command_without_anchor_object_no_billing_line_item()
    print("✓ No anchor object test passed")
    
    test_autism_diagnosis_without_assessments()
    print("✓ No assessments test passed")
    
    test_command_does_not_exist_error_handling()
    print("✓ Command not found error handling test passed")
    
    test_billing_line_item_parameters()
    print("✓ Billing line item parameters test passed")
    
    test_icd_code_normalization()
    print("✓ ICD code normalization test passed")
    
    print("\nAll tests passed! ✨")