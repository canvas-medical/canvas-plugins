"""Tests for appointment_state_field.utils.constants module."""

from appointment_state_field.utils.constants import FIELD_STATE_KEY, STATES, STATES_DICT


class TestConstants:
    """Tests for constants in the appointment_state_field plugin."""

    def test_field_state_key_value(self):
        """Test that FIELD_STATE_KEY has the correct value."""
        assert FIELD_STATE_KEY == "state"

    def test_states_list_not_empty(self):
        """Test that STATES list is not empty."""
        assert len(STATES) > 0

    def test_states_list_contains_all_50_states(self):
        """Test that STATES list contains all 50 US states."""
        assert len(STATES) == 50

    def test_states_list_contains_california(self):
        """Test that STATES list contains California."""
        assert "California" in STATES

    def test_states_list_contains_new_york(self):
        """Test that STATES list contains New York."""
        assert "New York" in STATES

    def test_states_dict_not_empty(self):
        """Test that STATES_DICT is not empty."""
        assert len(STATES_DICT) > 0

    def test_states_dict_contains_all_50_states(self):
        """Test that STATES_DICT contains all 50 US states."""
        assert len(STATES_DICT) == 50

    def test_states_dict_maps_california_correctly(self):
        """Test that STATES_DICT maps California to CA."""
        assert STATES_DICT["California"] == "CA"

    def test_states_dict_maps_new_york_correctly(self):
        """Test that STATES_DICT maps New York to NY."""
        assert STATES_DICT["New York"] == "NY"

    def test_states_dict_maps_texas_correctly(self):
        """Test that STATES_DICT maps Texas to TX."""
        assert STATES_DICT["Texas"] == "TX"

    def test_all_states_in_dict(self):
        """Test that all states in STATES list are keys in STATES_DICT."""
        for state in STATES:
            assert state in STATES_DICT, f"State {state} not found in STATES_DICT"

    def test_all_dict_keys_in_states_list(self):
        """Test that all keys in STATES_DICT are in STATES list."""
        for state in STATES_DICT.keys():
            assert state in STATES, f"State {state} from STATES_DICT not found in STATES list"

    def test_state_abbreviations_are_two_characters(self):
        """Test that all state abbreviations in STATES_DICT are 2 characters."""
        for abbreviation in STATES_DICT.values():
            assert len(abbreviation) == 2, f"Abbreviation {abbreviation} is not 2 characters"

    def test_state_abbreviations_are_uppercase(self):
        """Test that all state abbreviations in STATES_DICT are uppercase."""
        for abbreviation in STATES_DICT.values():
            assert abbreviation.isupper(), f"Abbreviation {abbreviation} is not uppercase"
