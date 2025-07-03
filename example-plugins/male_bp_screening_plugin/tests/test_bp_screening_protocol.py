import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock

from canvas_sdk.events import Event, EventType


class TestMaleBPScreeningProtocol(unittest.TestCase):
    """Test cases for the Male Blood Pressure Screening Protocol."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Import here to avoid Django setup issues in CI
        try:
            from male_bp_screening_plugin.protocols.bp_screening_protocol import MaleBPScreeningProtocol
            self.protocol_class = MaleBPScreeningProtocol
        except ImportError:
            self.skipTest("SDK not available for import")
    
    def create_mock_event(self, patient_data: dict):
        """Create a mock event with patient data."""
        mock_event = Mock(spec=Event)
        mock_event.target.id = "patient_123"
        return mock_event
    
    def test_eligible_male_patient_18_years(self):
        """Test that an 18-year-old male patient is eligible for screening."""
        if not hasattr(self, 'protocol_class'):
            self.skipTest("Protocol class not available")
            
        # Create patient data for 18-year-old male
        birth_date = datetime.now() - timedelta(days=18*365)
        patient_data = {
            "id": "patient_123",
            "gender": "male",
            "birth_date": birth_date.isoformat()
        }
        
        mock_event = self.create_mock_event(patient_data)
        protocol = self.protocol_class(mock_event)
        
        # Test eligibility check
        is_eligible = protocol._is_eligible_for_screening(patient_data)
        self.assertTrue(is_eligible, "18-year-old male should be eligible for screening")
    
    def test_eligible_male_patient_39_years(self):
        """Test that a 39-year-old male patient is eligible for screening."""
        if not hasattr(self, 'protocol_class'):
            self.skipTest("Protocol class not available")
            
        # Create patient data for 39-year-old male
        birth_date = datetime.now() - timedelta(days=39*365)
        patient_data = {
            "id": "patient_123", 
            "gender": "male",
            "birth_date": birth_date.isoformat()
        }
        
        mock_event = self.create_mock_event(patient_data)
        protocol = self.protocol_class(mock_event)
        
        # Test eligibility check
        is_eligible = protocol._is_eligible_for_screening(patient_data)
        self.assertTrue(is_eligible, "39-year-old male should be eligible for screening")
    
    def test_ineligible_male_patient_17_years(self):
        """Test that a 17-year-old male patient is not eligible for screening."""
        if not hasattr(self, 'protocol_class'):
            self.skipTest("Protocol class not available")
            
        # Create patient data for 17-year-old male
        birth_date = datetime.now() - timedelta(days=17*365)
        patient_data = {
            "id": "patient_123",
            "gender": "male", 
            "birth_date": birth_date.isoformat()
        }
        
        mock_event = self.create_mock_event(patient_data)
        protocol = self.protocol_class(mock_event)
        
        # Test eligibility check
        is_eligible = protocol._is_eligible_for_screening(patient_data)
        self.assertFalse(is_eligible, "17-year-old male should not be eligible for screening")
    
    def test_ineligible_male_patient_40_years(self):
        """Test that a 40-year-old male patient is not eligible for screening."""
        if not hasattr(self, 'protocol_class'):
            self.skipTest("Protocol class not available")
            
        # Create patient data for 40-year-old male
        birth_date = datetime.now() - timedelta(days=40*365)
        patient_data = {
            "id": "patient_123",
            "gender": "male",
            "birth_date": birth_date.isoformat()
        }
        
        mock_event = self.create_mock_event(patient_data)
        protocol = self.protocol_class(mock_event)
        
        # Test eligibility check
        is_eligible = protocol._is_eligible_for_screening(patient_data)
        self.assertFalse(is_eligible, "40-year-old male should not be eligible for screening")
    
    def test_ineligible_female_patient(self):
        """Test that female patients are not eligible for this specific screening protocol."""
        if not hasattr(self, 'protocol_class'):
            self.skipTest("Protocol class not available")
            
        # Create patient data for 25-year-old female
        birth_date = datetime.now() - timedelta(days=25*365)
        patient_data = {
            "id": "patient_123",
            "gender": "female",
            "birth_date": birth_date.isoformat()
        }
        
        mock_event = self.create_mock_event(patient_data)
        protocol = self.protocol_class(mock_event)
        
        # Test eligibility check
        is_eligible = protocol._is_eligible_for_screening(patient_data)
        self.assertFalse(is_eligible, "Female patients should not be eligible for male-specific screening")
    
    def test_screening_due_no_previous_screening(self):
        """Test that screening is due when no previous screening date is available."""
        if not hasattr(self, 'protocol_class'):
            self.skipTest("Protocol class not available")
            
        patient_data = {
            "id": "patient_123"
            # No last_bp_screening_date provided
        }
        
        mock_event = self.create_mock_event(patient_data)
        protocol = self.protocol_class(mock_event)
        
        # Test screening due check
        is_due = protocol._is_screening_due(patient_data)
        self.assertTrue(is_due, "Screening should be due when no previous screening date exists")
    
    def test_screening_due_old_screening(self):
        """Test that screening is due when last screening was over 2 years ago."""
        if not hasattr(self, 'protocol_class'):
            self.skipTest("Protocol class not available")
            
        # Last screening was 3 years ago
        old_screening_date = datetime.now() - timedelta(days=3*365)
        patient_data = {
            "id": "patient_123",
            "last_bp_screening_date": old_screening_date.isoformat()
        }
        
        mock_event = self.create_mock_event(patient_data)
        protocol = self.protocol_class(mock_event)
        
        # Test screening due check
        is_due = protocol._is_screening_due(patient_data)
        self.assertTrue(is_due, "Screening should be due when last screening was over 2 years ago")
    
    def test_screening_not_due_recent_screening(self):
        """Test that screening is not due when last screening was within 2 years."""
        if not hasattr(self, 'protocol_class'):
            self.skipTest("Protocol class not available")
            
        # Last screening was 1 year ago
        recent_screening_date = datetime.now() - timedelta(days=365)
        patient_data = {
            "id": "patient_123",
            "last_bp_screening_date": recent_screening_date.isoformat()
        }
        
        mock_event = self.create_mock_event(patient_data)
        protocol = self.protocol_class(mock_event)
        
        # Test screening due check
        is_due = protocol._is_screening_due(patient_data)
        self.assertFalse(is_due, "Screening should not be due when last screening was within 2 years")


if __name__ == "__main__":
    unittest.main()