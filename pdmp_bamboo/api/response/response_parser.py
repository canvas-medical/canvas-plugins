"""
PDMP Response Parser

Parses PDMP API responses and extracts relevant information.
"""

from typing import Dict, Any, Optional
from logger import log

from pdmp_bamboo.utils.pdmp_parser import parse_pdmp_response


class ResponseParser:
    """Parses PDMP API responses."""
    
    def __init__(self):
        self.parser = parse_pdmp_response  # Use existing parser for now
    
    def parse_response(self, raw_response: str) -> Dict[str, Any]:
        """
        Parse PDMP response and extract relevant information.
        
        Args:
            raw_response: Raw XML response from PDMP API
            
        Returns:
            Dictionary containing parsed response data
        """
        log.info("ResponseParser: Parsing PDMP response")
        
        try:
            # Use existing parser
            parsed_data = self.parser(raw_response)
            
            log.info(f"ResponseParser: Parsing completed - Success: {parsed_data.get('parsed', False)}")
            
            return {
                "parsed": parsed_data.get("parsed", False),
                "request_id": parsed_data.get("request_id"),
                "report_url": parsed_data.get("report_url"),
                "report_expiration": parsed_data.get("report_expiration"),
                "narx_scores": parsed_data.get("narx_scores", []),
                "narx_messages": parsed_data.get("narx_messages", []),
                "raw_response": raw_response,
                "parsing_errors": parsed_data.get("errors", [])
            }
            
        except Exception as e:
            log.error(f"ResponseParser: Error parsing response: {str(e)}")
            return {
                "parsed": False,
                "parsing_errors": [f"Error parsing response: {str(e)}"],
                "raw_response": raw_response
            }
    
    def extract_request_id(self, raw_response: str) -> Optional[str]:
        """Extract request ID from response."""
        try:
            parsed_data = self.parser(raw_response)
            return parsed_data.get("request_id")
        except Exception:
            return None
    
    def has_narx_scores(self, parsed_data: Dict[str, Any]) -> bool:
        """Check if response contains NarxCare scores."""
        return bool(parsed_data.get("narx_scores"))
    
    def has_narx_messages(self, parsed_data: Dict[str, Any]) -> bool:
        """Check if response contains NarxCare messages."""
        return bool(parsed_data.get("narx_messages"))
    
    def has_report_url(self, parsed_data: Dict[str, Any]) -> bool:
        """Check if response contains report URL."""
        return bool(parsed_data.get("report_url"))
