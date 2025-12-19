# SpecialtyReportTemplate API Testing Documentation

This document describes the comprehensive testing approach for the `SpecialtyReportTemplateAPI` endpoint.

## Overview

The testing approach uses a Python script that executes curl commands against the API endpoint and validates the responses. This provides a practical, executable way to verify all API functionality.

## Test File

**Location:** `tests/test_specialty_report_template_api_manual.py`

**Usage:**
```bash
cd speciality_report_explorer
python tests/test_specialty_report_template_api_manual.py
```

## Test Coverage

### 1. Basic Endpoint Tests
- **Test 1.1**: Get all templates
  - Verifies response structure
  - Validates all required fields are present
  - Confirms 20 template limit

### 2. Active Filter Tests
- **Test 2.1**: Get active templates only
  - Verifies `active=true` filter works
  - Confirms all returned templates have `active=True`

### 3. Search Filter Tests
- **Test 3.1**: Search for "cardiology"
  - Finds templates with "cardiology" in search_keywords
  - Should find TEST_CARD001 and TEST_CARD003
  
- **Test 3.2**: Search for "cardiac"
  - Finds templates with "cardiac" in search_keywords
  - Should find TEST_CARD001 and TEST_CARD002
  
- **Test 3.3**: Search for "heart"
  - Finds templates with "heart" in search_keywords
  - Should find TEST_CARD001 and TEST_CARD002
  
- **Test 3.4**: Search for non-existent term
  - Returns empty result set (count: 0)

### 4. Custom/Builtin Filter Tests
- **Test 4.1**: Get custom templates
  - Returns only templates where `custom=true`
  - Should return TEST_CARD002
  
- **Test 4.2**: Get builtin templates
  - Returns only templates where `custom=false`
  - Should exclude TEST_CARD002

### 5. Specialty Code Filter Tests
- **Test 5.1**: Filter by Cardiology specialty (207RC0000X)
  - Returns all Cardiology templates
  - Should find TEST_CARD001, TEST_CARD002, TEST_CARD003
  
- **Test 5.2**: Filter by Dermatology specialty (207ND0100X)
  - Returns Dermatology templates
  - Should find TEST_DERM001
  
- **Test 5.3**: Filter by non-existent specialty
  - Returns empty result set

### 6. Include Fields Tests
- **Test 6.1**: Get templates with fields
  - Verifies `include_fields=true` adds fields array
  - TEST_CARD001 should have 6 fields
  
- **Test 6.2**: Verify field structure
  - Validates field sequences: [1, 2, 3, 4, 5, 6]
  - Validates field labels and types
  - Confirms all required field data is present

### 7. Include Options Tests
- **Test 7.1**: Get templates with fields and options
  - Verifies `include_options=true` adds options array
  - Assessment field should have 3 options
  - Recommendation field should have 3 options
  
- **Test 7.2**: Verify option structure
  - Validates option keys and labels
  - Confirms all required option data is present

### 8. Combined Filter Tests
- **Test 8.1**: Active + Specialty Code
  - Returns only active Cardiology templates
  - Should exclude TEST_CARD003 (inactive)
  
- **Test 8.2**: Active + Search
  - Returns active templates matching search
  
- **Test 8.3**: Active + Custom
  - Returns active custom templates
  - Should return TEST_CARD002
  
- **Test 8.4**: Active + Builtin
  - Returns active builtin templates
  
- **Test 8.5**: Active + Specialty + Fields
  - Returns active Cardiology templates with fields
  - TEST_CARD001 should have 6 fields
  - TEST_CARD002 should have 0 fields
  
- **Test 8.6**: Active + Specialty + Fields + Options
  - Returns active Cardiology templates with fields and options
  - Assessment and Recommendation fields should have options
  
- **Test 8.7**: Search + Custom + Fields
  - Returns custom templates matching search with fields

### 9. Edge Cases
- **Test 9.1**: Empty result set
  - Returns valid JSON with count: 0
  
- **Test 9.2**: Template without fields (TEST_EMPTY001)
  - Template correctly shows field_count: 0
  - Fields array is empty
  
- **Test 9.3**: Field without options
  - "Select Without Options" field correctly shows empty options
  
- **Test 9.4**: Invalid query parameters
  - Unknown parameters are ignored gracefully
  - Valid response still returned

### 10. Performance and Limits
- **Test 11.1**: Verify 20 template limit
  - Response correctly limited to 20 templates
  - Count matches templates array length

## Test Data Reference

The tests use the following test data created by the verification plugin:

- **TEST_CARD001**: Cardiology Consultation Report
  - Active: true, Custom: false
  - Specialty: 207RC0000X (Cardiology)
  - Fields: 6 (Chief Complaint, Assessment, Ejection Fraction, Recommendation, Notes, Select Without Options)
  - Options: Assessment (3), Recommendation (3)
  
- **TEST_CARD002**: Custom Cardiology Template
  - Active: true, Custom: true
  - Specialty: 207RC0000X (Cardiology)
  - Fields: 0
  
- **TEST_CARD003**: Inactive Cardiology Template
  - Active: false, Custom: false
  - Specialty: 207RC0000X (Cardiology)
  - Fields: 0
  
- **TEST_DERM001**: Dermatology Consultation Report
  - Active: true, Custom: false
  - Specialty: 207ND0100X (Dermatology)
  - Fields: 0
  
- **TEST_EMPTY001**: Empty Template
  - Active: true, Custom: false
  - Specialty: 208D00000X (General)
  - Fields: 0

## Running the Tests

### Prerequisites
- API running at `http://localhost:8000`
- `curl` command available
- Python 3 with `json` module

### Execution
```bash
# From the plugin directory
cd speciality_report_explorer
python tests/test_specialty_report_template_api_manual.py
```

### Expected Output
The script will:
1. Execute each test case
2. Print pass/fail status for each assertion
3. Display a summary at the end showing total tests, passed, and failed

### Example Output
```
============================================================
SpecialtyReportTemplateAPI Manual Testing
============================================================
Base URL: http://localhost:8000/plugin-io/api/speciality_report_explorer/specialty-report-templates

=== Test 1.1: Get all templates ===
✓ PASS - Response has count field
✓ PASS - Response has templates array
...

============================================================
TEST EXECUTION SUMMARY
============================================================

Total tests: 50
Passed: 50
Failed: 0

============================================================
✓ ALL TESTS PASSED
============================================================
```

## Test Structure

Each test function:
1. Constructs the appropriate URL with query parameters
2. Executes curl command via `run_curl()`
3. Validates response using `assert_test()`
4. Records results for summary

### Helper Functions

- **`run_curl(url)`**: Executes curl and parses JSON response
- **`assert_test(name, condition, message)`**: Validates condition and records result

## Adding New Tests

To add a new test:

1. Create a new test function following the naming pattern `test_X_description()`
2. Add a docstring explaining what the test verifies
3. Use `run_curl()` to execute the API call
4. Use `assert_test()` to validate results
5. Call the new test function in `main()`

Example:
```python
def test_new_feature() -> None:
    """
    Test new feature
    
    Verifies:
    - Feature works as expected
    """
    print("\n=== Test: New feature ===")
    url = f"{BASE_URL}?new_param=value"
    data = run_curl(url)
    
    assert_test(
        "New feature works",
        data["count"] > 0,
    )
```

## Troubleshooting

### Tests Fail with Connection Error
- Ensure API is running at `http://localhost:8000`
- Check network connectivity

### Tests Fail with JSON Parse Error
- Verify API is returning valid JSON
- Check API logs for errors

### Tests Fail with Assertion Errors
- Review the test output to see which assertions failed
- Verify test data exists in the database
- Check API response matches expected structure

## Integration with CI/CD

This test script can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run API Tests
  run: |
    cd speciality_report_explorer
    python tests/test_specialty_report_template_api_manual.py
```

The script exits with code 0 on success, 1 on failure, making it suitable for CI/CD.

## Related Documentation

- [README.md](README.md) - API endpoint documentation
- [CANVAS_MANIFEST.json](CANVAS_MANIFEST.json) - Plugin configuration

