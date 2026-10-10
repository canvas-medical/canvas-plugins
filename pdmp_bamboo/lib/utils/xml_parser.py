"""
XML Parser Utility.

Simple XML parser for extracting reportlink URLs from PDMP responses.
Parses XML by hand without external libraries.
"""

import re
from typing import Any

from logger import log


class SimpleXMLParser:
    """Simple XML parser for PDMP report responses."""

    @staticmethod
    def extract_reportlink(xml_content: str) -> str | None:
        """
        Extract the reportlink URL from XML content.

        Args:
            xml_content: Raw XML string containing reportresponse

        Returns:
            The reportlink URL if found, None otherwise
        """
        if not xml_content:
            log.warning("SimpleXMLParser: Empty XML content provided")
            return None

        log.info("SimpleXMLParser: Extracting reportlink from XML")
        log.debug(f"SimpleXMLParser: XML content preview: {xml_content[:200]}...")

        try:
            # Clean up the XML content - remove extra whitespace and newlines
            cleaned_xml = re.sub(r"\s+", " ", xml_content.strip())

            # Look for reportlink tag using regex
            # Pattern matches: <reportlink>URL</reportlink>
            reportlink_pattern = r"<reportlink[^>]*>(.*?)</reportlink>"
            match = re.search(reportlink_pattern, cleaned_xml, re.IGNORECASE | re.DOTALL)

            if match:
                reportlink_url = match.group(1).strip()
                log.info(f"SimpleXMLParser: Found reportlink URL: {reportlink_url}")
                return reportlink_url
            else:
                log.warning("SimpleXMLParser: No reportlink tag found in XML")
                return None

        except Exception as e:
            log.error(f"SimpleXMLParser: Error parsing XML: {str(e)}")
            return None

    @staticmethod
    def extract_report_request_id(xml_content: str) -> str | None:
        """
        Extract the report request ID from XML content.

        Args:
            xml_content: Raw XML string containing reportresponse

        Returns:
            The report request ID if found, None otherwise
        """
        if not xml_content:
            return None

        try:
            cleaned_xml = re.sub(r"\s+", " ", xml_content.strip())

            # Look for reportrequestid tag
            id_pattern = r"<reportrequestid[^>]*>(.*?)</reportrequestid>"
            match = re.search(id_pattern, cleaned_xml, re.IGNORECASE | re.DOTALL)

            if match:
                request_id = match.group(1).strip()
                log.info(f"SimpleXMLParser: Found report request ID: {request_id}")
                return request_id
            else:
                log.warning("SimpleXMLParser: No reportrequestid tag found in XML")
                return None

        except Exception as e:
            log.error(f"SimpleXMLParser: Error extracting report request ID: {str(e)}")
            return None

    @staticmethod
    def parse_report_response(xml_content: str) -> dict[str, Any]:
        """
        Parse complete report response XML.

        Args:
            xml_content: Raw XML string containing reportresponse

        Returns:
            Dictionary with parsed data including reportlink and request ID
        """
        result = {"parsed": False, "reportlink": None, "report_request_id": None, "error": None}

        try:
            if not xml_content:
                result["error"] = "Empty XML content"
                return result

            # Extract reportlink
            reportlink = SimpleXMLParser.extract_reportlink(xml_content)
            if reportlink:
                result["reportlink"] = reportlink
                result["parsed"] = True

            # Extract report request ID
            request_id = SimpleXMLParser.extract_report_request_id(xml_content)
            if request_id:
                result["report_request_id"] = request_id

            if not reportlink:
                result["error"] = "No reportlink found in XML response"

        except Exception as e:
            result["error"] = f"XML parsing error: {str(e)}"
            log.error(f"SimpleXMLParser: Error parsing report response: {str(e)}")

        return result
