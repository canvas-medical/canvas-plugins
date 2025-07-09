import unittest
from datetime import datetime, timedelta, date
from unittest.mock import Mock, patch

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
    
    def create_mock_event(self, patient_id: str = "patient_123"):
        """Create a mock event with patient ID."""
        mock_event = Mock(spec=Event)
        mock_event.target.id = patient_id
        return mock_event
    
    def create_mock_patient(self, sex_at_birth: str, birth_date: date, first_name: str = "John", last_name: str = "Doe"):
        """Create a mock patient object."""
        mock_patient = Mock()
        mock_patient.sex_at_birth = sex_at_birth
        mock_patient.birth_date = birth_date
        mock_patient.first_name = first_name
        mock_patient.last_name = last_name
        return mock_patient
    
    def test_eligible_male_patient_18_years(self):
        """Test that an 18-year-old male patient is eligible for screening."""
        if not hasattr(self, 'protocol_class'):
            self.skipTest("Protocol class not available")
            
        # Create patient for 18-year-old male
        birth_date = date.today() - timedelta(days=18*365)
        mock_patient = self.create_mock_patient("M", birth_date)
        
        mock_event = self.create_mock_event()
        protocol = self.protocol_class(mock_event)
        
        # Test eligibility check
        is_eligible = protocol._is_eligible_for_screening(mock_patient)
        self.assertTrue(is_eligible, "18-year-old male should be eligible for screening")
    
    def test_eligible_male_patient_39_years(self):
        """Test that a 39-year-old male patient is eligible for screening."""
        if not hasattr(self, 'protocol_class'):
            self.skipTest("Protocol class not available")
            
        # Create patient for 39-year-old male
        birth_date = date.today() - timedelta(days=39*365)
        mock_patient = self.create_mock_patient("M", birth_date)
        
        mock_event = self.create_mock_event()
        protocol = self.protocol_class(mock_event)
        
        # Test eligibility check
        is_eligible = protocol._is_eligible_for_screening(mock_patient)
        self.assertTrue(is_eligible, "39-year-old male should be eligible for screening")
    
    def test_ineligible_male_patient_17_years(self):
        """Test that a 17-year-old male patient is not eligible for screening."""
        if not hasattr(self, 'protocol_class'):
            self.skipTest("Protocol class not available")
            
        # Create patient for 17-year-old male
        birth_date = date.today() - timedelta(days=17*365)
        mock_patient = self.create_mock_patient("M", birth_date)
        
        mock_event = self.create_mock_event()
        protocol = self.protocol_class(mock_event)
        
        # Test eligibility check
        is_eligible = protocol._is_eligible_for_screening(mock_patient)
        self.assertFalse(is_eligible, "17-year-old male should not be eligible for screening")
    
    def test_ineligible_male_patient_40_years(self):
        """Test that a 40-year-old male patient is not eligible for screening."""
        if not hasattr(self, 'protocol_class'):
            self.skipTest("Protocol class not available")
            
        # Create patient for 40-year-old male
        birth_date = date.today() - timedelta(days=40*365)
        mock_patient = self.create_mock_patient("M", birth_date)
        
        mock_event = self.create_mock_event()
        protocol = self.protocol_class(mock_event)
        
        # Test eligibility check
        is_eligible = protocol._is_eligible_for_screening(mock_patient)
        self.assertFalse(is_eligible, "40-year-old male should not be eligible for screening")
    
    def test_ineligible_female_patient(self):
        """Test that female patients are not eligible for this specific screening protocol."""
        if not hasattr(self, 'protocol_class'):
            self.skipTest("Protocol class not available")
            
        # Create patient for 25-year-old female
        birth_date = date.today() - timedelta(days=25*365)
        mock_patient = self.create_mock_patient("F", birth_date, "Jane", "Doe")
        
        mock_event = self.create_mock_event()
        protocol = self.protocol_class(mock_event)
        
        # Test eligibility check
        is_eligible = protocol._is_eligible_for_screening(mock_patient)
        self.assertFalse(is_eligible, "Female patients should not be eligible for male-specific screening")
    
    @patch('male_bp_screening_plugin.protocols.bp_screening_protocol.Observation.objects')
    def test_screening_due_no_prior_measurements(self, mock_observation_objects):
        """Test that screening is due when there are no prior blood pressure measurements."""
        if not hasattr(self, 'protocol_class'):
            self.skipTest("Protocol class not available")
            
        # Mock no existing blood pressure observations
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.exists.return_value = False
        mock_observation_objects.filter.return_value = mock_queryset
        
        # Create patient
        birth_date = date.today() - timedelta(days=25*365)
        mock_patient = self.create_mock_patient("M", birth_date)
        mock_patient.id = "patient_123"
        
        mock_event = self.create_mock_event()
        protocol = self.protocol_class(mock_event)
        
        # Test screening due check
        is_due = protocol._is_screening_due(mock_patient)
        self.assertTrue(is_due, "Screening should be due when there are no prior measurements")
    
    @patch('male_bp_screening_plugin.protocols.bp_screening_protocol.Observation.objects')
    def test_screening_due_old_measurement(self, mock_observation_objects):
        """Test that screening is due when last measurement is over 2 years old."""
        if not hasattr(self, 'protocol_class'):
            self.skipTest("Protocol class not available")
            
        # Mock an old blood pressure observation (3 years ago)
        old_date = datetime.now() - timedelta(days=3*365)
        mock_observation = Mock()
        mock_observation.effective_datetime = old_date
        
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.exists.return_value = True
        mock_queryset.first.return_value = mock_observation
        mock_observation_objects.filter.return_value = mock_queryset
        
        # Create patient
        birth_date = date.today() - timedelta(days=25*365)
        mock_patient = self.create_mock_patient("M", birth_date)
        mock_patient.id = "patient_123"
        
        mock_event = self.create_mock_event()
        protocol = self.protocol_class(mock_event)
        
        # Test screening due check
        is_due = protocol._is_screening_due(mock_patient)
        self.assertTrue(is_due, "Screening should be due when last measurement is over 2 years old")
    
    @patch('male_bp_screening_plugin.protocols.bp_screening_protocol.Observation.objects')
    def test_screening_not_due_recent_measurement(self, mock_observation_objects):
        """Test that screening is not due when last measurement is within 2 years."""
        if not hasattr(self, 'protocol_class'):
            self.skipTest("Protocol class not available")
            
        # Mock a recent blood pressure observation (1 year ago)
        recent_date = datetime.now() - timedelta(days=365)
        mock_observation = Mock()
        mock_observation.effective_datetime = recent_date
        
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.exists.return_value = True
        mock_queryset.first.return_value = mock_observation
        mock_observation_objects.filter.return_value = mock_queryset
        
        # Create patient
        birth_date = date.today() - timedelta(days=25*365)
        mock_patient = self.create_mock_patient("M", birth_date)
        mock_patient.id = "patient_123"
        
        mock_event = self.create_mock_event()
        protocol = self.protocol_class(mock_event)
        
        # Test screening due check
        is_due = protocol._is_screening_due(mock_patient)
        self.assertFalse(is_due, "Screening should not be due when last measurement is within 2 years")
    
    def test_calculate_age_accuracy(self):
        """Test age calculation accuracy for edge cases."""
        if not hasattr(self, 'protocol_class'):
            self.skipTest("Protocol class not available")
            
        mock_event = self.create_mock_event()
        protocol = self.protocol_class(mock_event)
        
        # Test exact 18th birthday (today)
        birth_date_18_today = date.today() - timedelta(days=18*365)
        mock_patient_18 = self.create_mock_patient("M", birth_date_18_today)
        age_18 = protocol._calculate_age(mock_patient_18)
        self.assertEqual(age_18, 18, "Age calculation should be accurate for 18-year-old")
        
        # Test exact 39th birthday
        birth_date_39 = date.today() - timedelta(days=39*365)
        mock_patient_39 = self.create_mock_patient("M", birth_date_39)
        age_39 = protocol._calculate_age(mock_patient_39)
        self.assertEqual(age_39, 39, "Age calculation should be accurate for 39-year-old")
    
    @patch('male_bp_screening_plugin.protocols.bp_screening_protocol.Observation.objects')
    @patch('male_bp_screening_plugin.protocols.bp_screening_protocol.Patient.find')
    def test_compute_with_eligible_patient(self, mock_patient_find, mock_observation_objects):
        """Test compute method with eligible patient who needs screening."""
        if not hasattr(self, 'protocol_class'):
            self.skipTest("Protocol class not available")
            
        # Setup mock patient
        birth_date = date.today() - timedelta(days=25*365)
        mock_patient = self.create_mock_patient("M", birth_date)
        mock_patient.id = "patient_123"
        mock_patient_find.return_value = mock_patient
        
        # Mock no existing blood pressure observations (screening due)
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.exists.return_value = False
        mock_observation_objects.filter.return_value = mock_queryset
        
        mock_event = self.create_mock_event()
        mock_event.target.id = "patient_123"
        
        protocol = self.protocol_class(mock_event)
        
        # Mock the target property
        protocol.target = "patient_123"
        
        effects = protocol.compute()
        
        # Should return one effect (protocol card)
        self.assertEqual(len(effects), 1, "Should return one protocol card effect for eligible patient")
        mock_patient_find.assert_called_once_with("patient_123")
    
    @patch('male_bp_screening_plugin.protocols.bp_screening_protocol.Observation.objects')
    @patch('male_bp_screening_plugin.protocols.bp_screening_protocol.Patient.find')
    def test_compute_with_eligible_patient_not_due(self, mock_patient_find, mock_observation_objects):
        """Test compute method with eligible patient who doesn't need screening."""
        if not hasattr(self, 'protocol_class'):
            self.skipTest("Protocol class not available")
            
        # Setup mock patient
        birth_date = date.today() - timedelta(days=25*365)
        mock_patient = self.create_mock_patient("M", birth_date)
        mock_patient.id = "patient_123"
        mock_patient_find.return_value = mock_patient
        
        # Mock recent blood pressure observation (screening not due)
        recent_date = datetime.now() - timedelta(days=365)
        mock_observation = Mock()
        mock_observation.effective_datetime = recent_date
        
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.exists.return_value = True
        mock_queryset.first.return_value = mock_observation
        mock_observation_objects.filter.return_value = mock_queryset
        
        mock_event = self.create_mock_event()
        
        protocol = self.protocol_class(mock_event)
        protocol.target = "patient_123"
        
        effects = protocol.compute()
        
        # Should return no effects for patient not due for screening
        self.assertEqual(len(effects), 0, "Should return no effects for patient not due for screening")
    
    @patch('male_bp_screening_plugin.protocols.bp_screening_protocol.Patient.find')
    def test_compute_with_ineligible_patient(self, mock_patient_find):
        """Test compute method with ineligible patient."""
        if not hasattr(self, 'protocol_class'):
            self.skipTest("Protocol class not available")
            
        # Setup mock patient - female
        birth_date = date.today() - timedelta(days=25*365)
        mock_patient = self.create_mock_patient("F", birth_date, "Jane", "Doe")
        mock_patient_find.return_value = mock_patient
        
        mock_event = self.create_mock_event()
        
        protocol = self.protocol_class(mock_event)
        protocol.target = "patient_123"
        
        effects = protocol.compute()
        
        # Should return no effects for ineligible patient
        self.assertEqual(len(effects), 0, "Should return no effects for ineligible patient")
    
    @patch('male_bp_screening_plugin.protocols.bp_screening_protocol.Patient.find')
    def test_compute_patient_not_found(self, mock_patient_find):
        """Test compute method when patient is not found."""
        if not hasattr(self, 'protocol_class'):
            self.skipTest("Protocol class not available")
            
        # Mock Patient.DoesNotExist exception
        from canvas_sdk.v1.data import Patient
        mock_patient_find.side_effect = Patient.DoesNotExist("Patient not found")
        
        mock_event = self.create_mock_event()
        protocol = self.protocol_class(mock_event)
        protocol.target = "nonexistent_patient"
        
        effects = protocol.compute()
        
        # Should return no effects when patient not found
        self.assertEqual(len(effects), 0, "Should return no effects when patient not found")


if __name__ == "__main__":
    unittest.main()