"""
Manual API Testing Script for SpecialtyReportTemplateAPI

This script performs comprehensive manual testing of the SpecialtyReportTemplateAPI endpoint
by executing curl commands and validating the responses. It tests all query parameters,
filter combinations, and edge cases.

Usage:
    python test_specialty_report_template_api_manual.py

Requirements:
    - curl command available
    - python3 with json module
    - API running at http://localhost:8000
"""

import json
import subprocess
import sys
from typing import Any, Dict, List


# Configuration
BASE_URL = "http://localhost:8000/plugin-io/api/speciality_report_explorer/specialty-report-templates"
TEST_RESULTS: List[Dict[str, Any]] = []


def run_curl(url: str) -> Dict[str, Any]:
    """
    Execute a curl command and parse the JSON response.
    
    Args:
        url: The full URL to query
        
    Returns:
        Parsed JSON response as a dictionary
        
    Raises:
        SystemExit: If curl command fails or response is invalid JSON
    """
    try:
        result = subprocess.run(
            ["curl", "-s", url],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing curl: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON response: {e}")
        print(f"Response: {result.stdout[:200]}")
        sys.exit(1)


def assert_test(name: str, condition: bool, message: str = "") -> None:
    """
    Assert a test condition and record the result.
    
    Args:
        name: Test name/description
        condition: Boolean condition to check
        message: Optional message to display
    """
    status = "✓ PASS" if condition else "✗ FAIL"
    result = {
        "name": name,
        "status": "PASS" if condition else "FAIL",
        "message": message,
    }
    TEST_RESULTS.append(result)
    print(f"{status} - {name}")
    if message:
        print(f"    {message}")


def test_1_1_get_all_templates() -> None:
    """
    Test 1.1: Get all templates
    
    Verifies:
    - Endpoint returns valid JSON
    - Response has 'count' and 'templates' fields
    - All templates have required fields
    - Response is limited to 20 templates
    """
    print("\n=== Test 1.1: Get all templates ===")
    data = run_curl(BASE_URL)
    
    assert_test(
        "Response has count field",
        "count" in data,
        f"Count: {data.get('count', 'missing')}",
    )
    assert_test(
        "Response has templates array",
        "templates" in data,
        f"Templates: {len(data.get('templates', []))}",
    )
    assert_test(
        "Response limited to 20 templates",
        len(data["templates"]) <= 20,
        f"Returned {len(data['templates'])} templates",
    )
    
    if data["templates"]:
        template = data["templates"][0]
        required_fields = [
            "dbid",
            "name",
            "code",
            "code_system",
            "search_keywords",
            "active",
            "custom",
            "search_as",
            "specialty_name",
            "specialty_code",
            "specialty_code_system",
        ]
        for field in required_fields:
            assert_test(
                f"Template has {field} field",
                field in template,
            )


def test_2_1_get_active_templates() -> None:
    """
    Test 2.1: Get active templates only
    
    Verifies:
    - active=true filter returns only active templates
    - All returned templates have active=True
    """
    print("\n=== Test 2.1: Get active templates only ===")
    url = f"{BASE_URL}?active=true"
    data = run_curl(url)
    
    assert_test(
        "Returns templates",
        data["count"] > 0,
        f"Found {data['count']} active templates",
    )
    
    all_active = all(t["active"] for t in data["templates"])
    assert_test(
        "All templates are active",
        all_active,
        f"Checked {len(data['templates'])} templates",
    )


def test_3_search_filters() -> None:
    """
    Test 3.1-3.4: Search filter tests
    
    Verifies:
    - Search for "cardiology" finds matching templates
    - Search for "cardiac" finds matching templates
    - Search for "heart" finds matching templates
    - Search for non-existent term returns empty results
    """
    print("\n=== Test 3.1-3.4: Search filter tests ===")
    
    # Test 3.1: Search for "cardiology"
    print("\nTest 3.1: Search 'cardiology'")
    url = f"{BASE_URL}?search=cardiology"
    data = run_curl(url)
    
    test_templates = [t for t in data["templates"] if t["code"].startswith("TEST_")]
    assert_test(
        "Search 'cardiology' finds test templates",
        len([t for t in test_templates if t["code"] == "TEST_CARD001"]) > 0,
        f"Found {len(test_templates)} test templates",
    )
    
    # Test 3.2: Search for "cardiac"
    print("\nTest 3.2: Search 'cardiac'")
    url = f"{BASE_URL}?search=cardiac"
    data = run_curl(url)
    
    test_templates = [t for t in data["templates"] if t["code"].startswith("TEST_")]
    assert_test(
        "Search 'cardiac' finds TEST_CARD001 and TEST_CARD002",
        len([t for t in test_templates if t["code"] in ["TEST_CARD001", "TEST_CARD002"]]) >= 2,
        f"Found {len(test_templates)} test templates",
    )
    
    # Test 3.3: Search for "heart"
    print("\nTest 3.3: Search 'heart'")
    url = f"{BASE_URL}?search=heart"
    data = run_curl(url)
    
    test_templates = [t for t in data["templates"] if t["code"].startswith("TEST_")]
    assert_test(
        "Search 'heart' finds test templates",
        len(test_templates) >= 2,
        f"Found {len(test_templates)} test templates",
    )
    
    # Test 3.4: Search for non-existent term
    print("\nTest 3.4: Search non-existent term")
    url = f"{BASE_URL}?search=nonexistentterm12345"
    data = run_curl(url)
    
    assert_test(
        "Search non-existent term returns empty",
        data["count"] == 0,
        f"Count: {data['count']}",
    )


def test_4_custom_builtin_filters() -> None:
    """
    Test 4.1-4.2: Custom/Builtin filter tests
    
    Verifies:
    - custom=true returns only custom templates
    - custom=false returns only builtin templates
    """
    print("\n=== Test 4.1-4.2: Custom/Builtin filter tests ===")
    
    # Test 4.1: Get custom templates
    print("\nTest 4.1: Get custom templates")
    url = f"{BASE_URL}?custom=true"
    data = run_curl(url)
    
    test_templates = [t for t in data["templates"] if t["code"].startswith("TEST_")]
    assert_test(
        "Custom filter returns TEST_CARD002",
        len([t for t in test_templates if t["code"] == "TEST_CARD002"]) == 1,
        f"Found {len(test_templates)} test templates",
    )
    
    all_custom = all(t["custom"] for t in data["templates"])
    assert_test(
        "All returned templates are custom",
        all_custom,
        f"Checked {len(data['templates'])} templates",
    )
    
    # Test 4.2: Get builtin templates
    print("\nTest 4.2: Get builtin templates")
    url = f"{BASE_URL}?custom=false"
    data = run_curl(url)
    
    all_builtin = all(not t["custom"] for t in data["templates"])
    assert_test(
        "All returned templates are builtin",
        all_builtin,
        f"Checked {len(data['templates'])} templates",
    )


def test_5_specialty_code_filters() -> None:
    """
    Test 5.1-5.3: Specialty code filter tests
    
    Verifies:
    - Filter by Cardiology specialty (207RC0000X) finds all test templates
    - Filter by Dermatology specialty (207ND0100X) finds TEST_DERM001
    - Filter by non-existent specialty returns empty results
    """
    print("\n=== Test 5.1-5.3: Specialty code filter tests ===")
    
    # Test 5.1: Filter by Cardiology
    print("\nTest 5.1: Filter by Cardiology specialty (207RC0000X)")
    url = f"{BASE_URL}?specialty_code=207RC0000X"
    data = run_curl(url)
    
    test_templates = [t for t in data["templates"] if t["code"].startswith("TEST_")]
    assert_test(
        "Cardiology filter finds all 3 test templates",
        len(test_templates) == 3,
        f"Found {len(test_templates)} test templates: {[t['code'] for t in test_templates]}",
    )
    
    all_cardiology = all(t["specialty_code"] == "207RC0000X" for t in data["templates"])
    assert_test(
        "All templates have Cardiology specialty code",
        all_cardiology,
        f"Checked {len(data['templates'])} templates",
    )
    
    # Test 5.2: Filter by Dermatology
    print("\nTest 5.2: Filter by Dermatology specialty (207ND0100X)")
    url = f"{BASE_URL}?specialty_code=207ND0100X"
    data = run_curl(url)
    
    test_templates = [t for t in data["templates"] if t["code"].startswith("TEST_")]
    assert_test(
        "Dermatology filter finds TEST_DERM001",
        len([t for t in test_templates if t["code"] == "TEST_DERM001"]) == 1,
        f"Found {len(test_templates)} test templates",
    )
    
    # Test 5.3: Filter by non-existent specialty
    print("\nTest 5.3: Filter by non-existent specialty")
    url = f"{BASE_URL}?specialty_code=999XX9999X"
    data = run_curl(url)
    
    assert_test(
        "Non-existent specialty returns empty",
        data["count"] == 0,
        f"Count: {data['count']}",
    )


def test_6_include_fields() -> None:
    """
    Test 6.1-6.2: Include fields tests
    
    Verifies:
    - include_fields=true adds fields array to templates
    - TEST_CARD001 has 6 fields with correct structure
    - Field sequences, labels, and types are correct
    """
    print("\n=== Test 6.1-6.2: Include fields tests ===")
    
    # Test 6.1: Get templates with fields
    print("\nTest 6.1: Get templates with fields")
    url = f"{BASE_URL}?specialty_code=207RC0000X&include_fields=true"
    data = run_curl(url)
    
    test_card = [t for t in data["templates"] if t["code"] == "TEST_CARD001"]
    assert_test(
        "TEST_CARD001 found",
        len(test_card) > 0,
    )
    
    if test_card:
        template = test_card[0]
        assert_test(
            "TEST_CARD001 has field_count field",
            "field_count" in template,
            f"Field count: {template.get('field_count', 'missing')}",
        )
        assert_test(
            "TEST_CARD001 has fields array",
            "fields" in template,
            f"Fields: {len(template.get('fields', []))}",
        )
        assert_test(
            "TEST_CARD001 has 6 fields",
            template["field_count"] == 6 and len(template["fields"]) == 6,
            f"Field count: {template['field_count']}, Fields array: {len(template['fields'])}",
        )
        
        # Test 6.2: Verify field structure
        print("\nTest 6.2: Verify field structure for TEST_CARD001")
        fields = template["fields"]
        sequences = [f["sequence"] for f in fields]
        expected_sequences = [1, 2, 3, 4, 5, 6]
        
        assert_test(
            "Field sequences are correct",
            sequences == expected_sequences,
            f"Sequences: {sequences}",
        )
        
        labels = [f["label"] for f in fields]
        expected_labels = [
            "Chief Complaint",
            "Assessment",
            "Ejection Fraction",
            "Recommendation",
            "Notes",
            "Select Without Options",
        ]
        
        assert_test(
            "Field labels are correct",
            all(label in labels for label in expected_labels),
            f"Labels: {labels}",
        )
        
        field_types = [f["type"] for f in fields]
        expected_types = ["text", "select", "float", "radio", "text", "select"]
        
        assert_test(
            "Field types are correct",
            field_types == expected_types,
            f"Types: {field_types}",
        )
        
        # Verify required field data
        required_field_keys = [
            "dbid",
            "sequence",
            "code",
            "code_system",
            "label",
            "units",
            "type",
            "required",
        ]
        
        for field in fields:
            for key in required_field_keys:
                assert_test(
                    f"Field has {key}",
                    key in field,
                )


def test_7_include_options() -> None:
    """
    Test 7.1-7.2: Include options tests
    
    Verifies:
    - include_options=true adds options array to fields
    - Assessment field has 3 options
    - Recommendation field has 3 options
    - Options have correct structure (dbid, label, key)
    """
    print("\n=== Test 7.1-7.2: Include options tests ===")
    
    # Test 7.1: Get templates with fields and options
    print("\nTest 7.1: Get templates with fields and options")
    url = f"{BASE_URL}?specialty_code=207RC0000X&include_fields=true&include_options=true"
    data = run_curl(url)
    
    test_card = [t for t in data["templates"] if t["code"] == "TEST_CARD001"]
    assert_test(
        "TEST_CARD001 found",
        len(test_card) > 0,
    )
    
    if test_card:
        template = test_card[0]
        assessment = [f for f in template["fields"] if f["label"] == "Assessment"]
        recommendation = [f for f in template["fields"] if f["label"] == "Recommendation"]
        
        assert_test(
            "Assessment field found",
            len(assessment) > 0,
        )
        assert_test(
            "Recommendation field found",
            len(recommendation) > 0,
        )
        
        if assessment:
            assert_test(
                "Assessment has options array",
                "options" in assessment[0],
            )
            assert_test(
                "Assessment has option_count",
                "option_count" in assessment[0],
                f"Option count: {assessment[0].get('option_count', 'missing')}",
            )
            assert_test(
                "Assessment has 3 options",
                assessment[0]["option_count"] == 3 and len(assessment[0]["options"]) == 3,
                f"Options: {len(assessment[0]['options'])}",
            )
        
        if recommendation:
            assert_test(
                "Recommendation has 3 options",
                recommendation[0]["option_count"] == 3 and len(recommendation[0]["options"]) == 3,
                f"Options: {len(recommendation[0]['options'])}",
            )
        
        # Test 7.2: Verify option structure
        print("\nTest 7.2: Verify option structure")
        if assessment and assessment[0]["options"]:
            option = assessment[0]["options"][0]
            required_option_keys = ["dbid", "label", "key"]
            
            for key in required_option_keys:
                assert_test(
                    f"Option has {key}",
                    key in option,
                )
            
            option_keys = [o["key"] for o in assessment[0]["options"]]
            expected_keys = ["TEST_NORMAL", "TEST_ABNORMAL", "TEST_FOLLOWUP"]
            
            assert_test(
                "Assessment option keys are correct",
                all(key in option_keys for key in expected_keys),
                f"Keys: {option_keys}",
            )


def test_8_combined_filters() -> None:
    """
    Test 8.1-8.7: Combined filter tests
    
    Verifies:
    - Active + Specialty Code filter works
    - Active + Search filter works
    - Active + Custom filter works
    - Active + Builtin filter works
    - Active + Specialty + Fields works
    - Active + Specialty + Fields + Options works
    - Search + Custom + Fields works
    """
    print("\n=== Test 8.1-8.7: Combined filter tests ===")
    
    # Test 8.1: Active + Specialty Code
    print("\nTest 8.1: Active + Specialty Code")
    url = f"{BASE_URL}?active=true&specialty_code=207RC0000X"
    data = run_curl(url)
    
    test_templates = [t for t in data["templates"] if t["code"].startswith("TEST_")]
    assert_test(
        "Active + Specialty returns only active test templates",
        len(test_templates) == 2,
        f"Found {len(test_templates)} test templates (expected 2: TEST_CARD001, TEST_CARD002)",
    )
    assert_test(
        "All returned templates are active",
        all(t["active"] for t in data["templates"]),
    )
    
    # Test 8.2: Active + Search
    print("\nTest 8.2: Active + Search")
    url = f"{BASE_URL}?active=true&search=cardiology"
    data = run_curl(url)
    
    test_templates = [t for t in data["templates"] if t["code"].startswith("TEST_")]
    assert_test(
        "Active + Search finds TEST_CARD001",
        len([t for t in test_templates if t["code"] == "TEST_CARD001"]) == 1,
    )
    assert_test(
        "All returned templates are active",
        all(t["active"] for t in data["templates"]),
    )
    
    # Test 8.3: Active + Custom
    print("\nTest 8.3: Active + Custom")
    url = f"{BASE_URL}?active=true&custom=true"
    data = run_curl(url)
    
    test_templates = [t for t in data["templates"] if t["code"].startswith("TEST_")]
    assert_test(
        "Active + Custom returns TEST_CARD002",
        len([t for t in test_templates if t["code"] == "TEST_CARD002"]) == 1,
    )
    
    # Test 8.4: Active + Builtin
    print("\nTest 8.4: Active + Builtin")
    url = f"{BASE_URL}?active=true&custom=false"
    data = run_curl(url)
    
    assert_test(
        "All returned templates are builtin",
        all(not t["custom"] for t in data["templates"]),
        f"Checked {len(data['templates'])} templates",
    )
    
    # Test 8.5: Active + Specialty + Fields
    print("\nTest 8.5: Active + Specialty + Fields")
    url = f"{BASE_URL}?active=true&specialty_code=207RC0000X&include_fields=true"
    data = run_curl(url)
    
    test_card = [t for t in data["templates"] if t["code"] == "TEST_CARD001"]
    test_card2 = [t for t in data["templates"] if t["code"] == "TEST_CARD002"]
    
    assert_test(
        "TEST_CARD001 found with fields",
        len(test_card) > 0 and test_card[0]["field_count"] == 6,
    )
    assert_test(
        "TEST_CARD002 found with 0 fields",
        len(test_card2) > 0 and test_card2[0]["field_count"] == 0,
    )
    
    # Test 8.6: Active + Specialty + Fields + Options
    print("\nTest 8.6: Active + Specialty + Fields + Options")
    url = f"{BASE_URL}?active=true&specialty_code=207RC0000X&include_fields=true&include_options=true"
    data = run_curl(url)
    
    test_card = [t for t in data["templates"] if t["code"] == "TEST_CARD001"]
    if test_card:
        assessment = [f for f in test_card[0]["fields"] if f["label"] == "Assessment"]
        recommendation = [f for f in test_card[0]["fields"] if f["label"] == "Recommendation"]
        
        assert_test(
            "Assessment has options",
            len(assessment) > 0 and assessment[0]["option_count"] == 3,
        )
        assert_test(
            "Recommendation has options",
            len(recommendation) > 0 and recommendation[0]["option_count"] == 3,
        )
    
    # Test 8.7: Search + Custom + Fields
    print("\nTest 8.7: Search + Custom + Fields")
    url = f"{BASE_URL}?search=cardiac&custom=true&include_fields=true"
    data = run_curl(url)
    
    test_templates = [t for t in data["templates"] if t["code"].startswith("TEST_")]
    assert_test(
        "Search + Custom + Fields returns TEST_CARD002",
        len([t for t in test_templates if t["code"] == "TEST_CARD002"]) == 1,
    )


def test_9_edge_cases() -> None:
    """
    Test 9.1-9.4: Edge cases
    
    Verifies:
    - Empty result set returns valid JSON
    - Template without fields (TEST_EMPTY001) works correctly
    - Field without options works correctly
    - Invalid query parameters are ignored gracefully
    """
    print("\n=== Test 9.1-9.4: Edge cases ===")
    
    # Test 9.1: Empty result set
    print("\nTest 9.1: Empty result set")
    url = f"{BASE_URL}?specialty_code=999XX9999X&active=true"
    data = run_curl(url)
    
    assert_test(
        "Empty result set has valid structure",
        "count" in data and "templates" in data,
    )
    assert_test(
        "Empty result set count is 0",
        data["count"] == 0,
    )
    assert_test(
        "Empty result set templates array is empty",
        len(data["templates"]) == 0,
    )
    
    # Test 9.2: Template without fields
    print("\nTest 9.2: Template without fields (TEST_EMPTY001)")
    url = f"{BASE_URL}?search=empty&include_fields=true"
    data = run_curl(url)
    
    test_empty = [t for t in data["templates"] if t["code"] == "TEST_EMPTY001"]
    if test_empty:
        template = test_empty[0]
        assert_test(
            "TEST_EMPTY001 has field_count 0",
            template["field_count"] == 0,
        )
        assert_test(
            "TEST_EMPTY001 has empty fields array",
            len(template["fields"]) == 0,
        )
    else:
        assert_test(
            "TEST_EMPTY001 found",
            False,
            "TEST_EMPTY001 not found in results",
        )
    
    # Test 9.3: Field without options
    print("\nTest 9.3: Field without options (Select Without Options field)")
    url = f"{BASE_URL}?specialty_code=207RC0000X&include_fields=true&include_options=true"
    data = run_curl(url)
    
    test_card = [t for t in data["templates"] if t["code"] == "TEST_CARD001"]
    if test_card:
        select_no_options = [
            f for f in test_card[0]["fields"] if f["label"] == "Select Without Options"
        ]
        if select_no_options:
            field = select_no_options[0]
            assert_test(
                "Select Without Options field has type 'select'",
                field["type"] == "select",
            )
            assert_test(
                "Select Without Options field has 0 options",
                field["option_count"] == 0 and len(field["options"]) == 0,
            )
    
    # Test 9.4: Invalid query parameters
    print("\nTest 9.4: Invalid query parameters (should be ignored)")
    url = f"{BASE_URL}?unknown_param=value"
    data = run_curl(url)
    
    assert_test(
        "Invalid parameter ignored, valid response returned",
        "count" in data and "templates" in data,
    )
    assert_test(
        "Response has templates (unknown param ignored)",
        data["count"] > 0,
    )


def test_11_performance_limits() -> None:
    """
    Test 11.1: Performance and limits
    
    Verifies:
    - Response is limited to 20 templates
    """
    print("\n=== Test 11.1: Performance and limits ===")
    
    url = BASE_URL
    data = run_curl(url)
    
    assert_test(
        "Response limited to 20 templates",
        len(data["templates"]) <= 20,
        f"Returned {len(data['templates'])} templates",
    )
    assert_test(
        "Count matches templates array length",
        data["count"] == len(data["templates"]),
    )


def print_summary() -> None:
    """Print test execution summary."""
    print("\n" + "=" * 60)
    print("TEST EXECUTION SUMMARY")
    print("=" * 60)
    
    total = len(TEST_RESULTS)
    passed = sum(1 for r in TEST_RESULTS if r["status"] == "PASS")
    failed = total - passed
    
    print(f"\nTotal tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print("\nFailed tests:")
        for result in TEST_RESULTS:
            if result["status"] == "FAIL":
                print(f"  ✗ {result['name']}")
                if result["message"]:
                    print(f"    {result['message']}")
    
    print("\n" + "=" * 60)
    if failed == 0:
        print("✓ ALL TESTS PASSED")
    else:
        print(f"✗ {failed} TEST(S) FAILED")
    print("=" * 60 + "\n")


def main() -> None:
    """Main test execution function."""
    print("=" * 60)
    print("SpecialtyReportTemplateAPI Manual Testing")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}\n")
    
    # Execute all test suites
    test_1_1_get_all_templates()
    test_2_1_get_active_templates()
    test_3_search_filters()
    test_4_custom_builtin_filters()
    test_5_specialty_code_filters()
    test_6_include_fields()
    test_7_include_options()
    test_8_combined_filters()
    test_9_edge_cases()
    test_11_performance_limits()
    
    # Print summary
    print_summary()
    
    # Exit with appropriate code
    failed = sum(1 for r in TEST_RESULTS if r["status"] == "FAIL")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()

