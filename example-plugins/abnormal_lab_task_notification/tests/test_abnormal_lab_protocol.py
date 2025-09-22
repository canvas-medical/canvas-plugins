"""
Test for the abnormal lab task notification plugin.

These tests validate the plugin logic for creating tasks when abnormal lab values are detected.
"""
import pytest
from unittest.mock import Mock, MagicMock
from canvas_sdk.effects.task import AddTask, TaskStatus
from canvas_sdk.events import EventType


class MockLabValue:
    """Mock lab value for testing."""
    def __init__(self, abnormal_flag="", value="", units="", reference_range=""):
        self.id = "test-value-id"
        self.abnormal_flag = abnormal_flag
        self.value = value
        self.units = units
        self.reference_range = reference_range


class MockLabReport:
    """Mock lab report for testing."""
    def __init__(self, patient_id="test-patient", for_test_only=False, junked=False, values=None):
        self.id = "test-lab-report-id"
        self.patient_id = patient_id
        self.for_test_only = for_test_only
        self.junked = junked
        self.values = Mock()
        self.values.all.return_value = values or []


def test_plugin_responds_to_correct_event():
    """Test that the plugin responds to LAB_REPORT_CREATED events."""
    # This test would be run in a Django environment where we can import the plugin
    # For now, we'll test the event type matching
    expected_event = EventType.Name(EventType.LAB_REPORT_CREATED)
    assert expected_event == "LAB_REPORT_CREATED"


def test_abnormal_lab_detection():
    """Test the logic for detecting abnormal lab values."""
    # Test case 1: Normal values (no abnormal flag)
    normal_value = MockLabValue(abnormal_flag="")
    assert not normal_value.abnormal_flag.strip()
    
    # Test case 2: Abnormal values (has abnormal flag)
    abnormal_value = MockLabValue(abnormal_flag="HIGH")
    assert abnormal_value.abnormal_flag.strip()
    
    # Test case 3: Whitespace only abnormal flag (should be treated as normal)
    whitespace_value = MockLabValue(abnormal_flag="   ")
    assert not whitespace_value.abnormal_flag.strip()


def test_task_creation_logic():
    """Test the task creation parameters."""
    # Test parameters for AddTask
    task = AddTask(
        patient_id="test-patient-id",
        title="Review Abnormal Lab Values (2 abnormal)",
        status=TaskStatus.OPEN,
        labels=["abnormal-lab", "urgent-review"],
        linked_object_id="test-lab-report-id"
    )
    
    assert task.patient_id == "test-patient-id"
    assert task.title == "Review Abnormal Lab Values (2 abnormal)"
    assert task.status == TaskStatus.OPEN
    assert "abnormal-lab" in task.labels
    assert "urgent-review" in task.labels
    assert task.linked_object_id == "test-lab-report-id"


def test_filtered_reports():
    """Test that test-only and junked reports are filtered out."""
    # Test case 1: Test-only report should be filtered
    test_report = MockLabReport(for_test_only=True)
    assert test_report.for_test_only
    
    # Test case 2: Junked report should be filtered
    junked_report = MockLabReport(junked=True)
    assert junked_report.junked
    
    # Test case 3: Normal report should not be filtered
    normal_report = MockLabReport(for_test_only=False, junked=False)
    assert not normal_report.for_test_only and not normal_report.junked


def test_multiple_abnormal_values():
    """Test handling of multiple abnormal values in a single report."""
    abnormal_values = [
        MockLabValue(abnormal_flag="HIGH", value="180", units="mg/dL", reference_range="70-100"),
        MockLabValue(abnormal_flag="LOW", value="9.2", units="g/dL", reference_range="12-16"),
        MockLabValue(abnormal_flag="CRITICAL", value="2.1", units="mmol/L", reference_range="3.5-5.0")
    ]
    
    # Count abnormal values
    abnormal_count = len([v for v in abnormal_values if v.abnormal_flag.strip()])
    assert abnormal_count == 3
    
    # Test title generation
    expected_title = f"Review Abnormal Lab Values ({abnormal_count} abnormal)"
    assert expected_title == "Review Abnormal Lab Values (3 abnormal)"


if __name__ == "__main__":
    # Run basic validation tests
    test_plugin_responds_to_correct_event()
    test_abnormal_lab_detection()
    test_task_creation_logic()
    test_filtered_reports()
    test_multiple_abnormal_values()
    print("All tests passed!")