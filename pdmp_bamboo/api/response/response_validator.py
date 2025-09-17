"""
PDMP Response Validator

Validates PDMP API responses for completeness and correctness.
"""

from typing import Dict, Any, List
from logger import log


class ResponseValidator:
    """Validates PDMP API responses."""
    
    def validate_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate PDMP response data.
        
        Args:
            response_data: Response data from PDMP API
            
        Returns:
            Dictionary containing validation results
        """
        log.info("ResponseValidator: Validating PDMP response")
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check basic response structure
        if not response_data.get("raw_response"):
            validation_result["errors"].append("No response content received")
            validation_result["is_valid"] = False
        
        # Check status code
        status_code = response_data.get("status_code")
        if status_code != 200:
            validation_result["errors"].append(f"Invalid status code: {status_code}")
            validation_result["is_valid"] = False
        
        # Check for parsing errors
        parsed_data = response_data.get("parsed_data", {})
        if parsed_data.get("parsing_errors"):
            validation_result["warnings"].extend(parsed_data["parsing_errors"])
        
        # Check for required fields in parsed data
        if parsed_data.get("parsed"):
            if not parsed_data.get("request_id"):
                validation_result["warnings"].append("No request ID found in response")
        
        log.info(f"ResponseValidator: Validation completed - Valid: {validation_result['is_valid']}, Errors: {len(validation_result['errors'])}, Warnings: {len(validation_result['warnings'])}")
        
        return validation_result
