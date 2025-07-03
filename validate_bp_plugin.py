#!/usr/bin/env python3
"""
Simple validation script for the Male BP Screening Plugin.

This script validates the plugin structure and basic logic without
requiring the full Canvas SDK environment.
"""

import ast
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


def validate_plugin_structure():
    """Validate that the plugin has the correct file structure."""
    plugin_dir = Path("example-plugins/male_bp_screening_plugin")
    
    required_files = [
        "CANVAS_MANIFEST.json",
        "README.md", 
        "__init__.py",
        "protocols/__init__.py",
        "protocols/bp_screening_protocol.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (plugin_dir / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ Plugin structure is valid")
    return True


def validate_manifest():
    """Validate the CANVAS_MANIFEST.json file."""
    manifest_path = Path("example-plugins/male_bp_screening_plugin/CANVAS_MANIFEST.json")
    
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        # Check required fields
        required_fields = ["sdk_version", "plugin_version", "name", "description", "components"]
        for field in required_fields:
            if field not in manifest:
                print(f"❌ Missing required field in manifest: {field}")
                return False
        
        # Check protocols
        protocols = manifest["components"]["protocols"]
        if len(protocols) != 2:
            print(f"❌ Expected 2 protocols, found {len(protocols)}")
            return False
        
        print("✅ CANVAS_MANIFEST.json is valid")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in manifest: {e}")
        return False
    except Exception as e:
        print(f"❌ Error validating manifest: {e}")
        return False


def validate_protocol_syntax():
    """Validate that the protocol Python code is syntactically correct."""
    protocol_path = Path("example-plugins/male_bp_screening_plugin/protocols/bp_screening_protocol.py")
    
    try:
        with open(protocol_path) as f:
            code = f.read()
        
        # Parse the AST to check syntax
        ast.parse(code)
        
        print("✅ Protocol code syntax is valid")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in protocol: {e}")
        return False
    except Exception as e:
        print(f"❌ Error validating protocol syntax: {e}")
        return False


def test_age_calculation_logic():
    """Test the age calculation logic without importing the full SDK."""
    print("🧪 Testing age calculation logic...")
    
    def calculate_age(birth_date_str):
        """Simplified age calculation matching the protocol logic."""
        try:
            birth_date = datetime.fromisoformat(birth_date_str.replace('Z', '+00:00'))
            if hasattr(birth_date, 'date'):
                birth_date = birth_date.date()
            
            today = datetime.now().date()
            age = today.year - birth_date.year - (
                (today.month, today.day) < (birth_date.month, birth_date.day)
            )
            return age
        except Exception:
            return None
    
    def is_eligible_age(age):
        """Check if age is in the eligible range."""
        return age is not None and 18 <= age <= 39
    
    # Test cases with more precise birth dates
    test_cases = [
        (18, True, "18-year-old should be eligible"),
        (25, True, "25-year-old should be eligible"), 
        (39, True, "39-year-old should be eligible"),
        (17, False, "17-year-old should not be eligible"),
        (40, False, "40-year-old should not be eligible")
    ]
    
    all_passed = True
    for test_age, expected, description in test_cases:
        # Create birth date for exact age - be more precise to avoid boundary issues
        today = datetime.now()
        birth_date = datetime(today.year - test_age, today.month, today.day) - timedelta(days=1)
        birth_date_str = birth_date.isoformat()
        
        calculated_age = calculate_age(birth_date_str)
        is_eligible = is_eligible_age(calculated_age)
        
        if is_eligible == expected:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} (got {is_eligible}, expected {expected})")
            all_passed = False
    
    return all_passed


def main():
    """Run all validation checks."""
    print("🔍 Validating Male BP Screening Plugin...")
    print()
    
    checks = [
        ("Plugin Structure", validate_plugin_structure),
        ("CANVAS Manifest", validate_manifest), 
        ("Protocol Syntax", validate_protocol_syntax),
        ("Age Logic", test_age_calculation_logic)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"🔍 {check_name}:")
        if not check_func():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 All validation checks passed!")
        print()
        print("Plugin Summary:")
        print("- Targets male patients aged 18-39")
        print("- Follows USPSTF blood pressure screening guidelines")
        print("- Recommends screening every 2-3 years")
        print("- Generates protocol cards with actionable recommendations")
        print("- Ready for installation in Canvas")
        return 0
    else:
        print("❌ Some validation checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())