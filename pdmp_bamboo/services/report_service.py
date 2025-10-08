"""
Report Service

Handles the business logic for PDMP report requests.
Separates business logic from API endpoint concerns.
"""

from typing import Dict, Any, List, Optional, Tuple
from logger import log

from pdmp_bamboo.services.data_extraction import DataExtractionService
from pdmp_bamboo.xml.builders.report_request_builder import ReportRequestXMLBuilder
from pdmp_bamboo.api.client.pdmp_client import PDMPClient
from pdmp_bamboo.utils.dto_converter import convert_all_dtos_to_dicts


class ReportService:
    """Service for handling PDMP report requests."""

    def __init__(self):
        self.data_service = DataExtractionService()
        self.xml_builder = ReportRequestXMLBuilder()
        self.pdmp_client = PDMPClient()

    def fetch_pdmp_report(self,
                          report_id: str,
                          patient_id: str,
                          practitioner_id: str,
                          secrets: Dict[str, Any],
                          use_test_env: bool = False) -> Dict[str, Any]:
        """
        Fetch a PDMP report using the complete workflow.

        Args:
            report_id: The ID of the report to fetch
            patient_id: Canvas patient ID
            practitioner_id: Canvas practitioner ID
            secrets: Plugin secrets
            use_test_env: Whether to use test environment

        Returns:
            Dictionary containing result data and status
        """
        log.info(f"ReportService: Starting PDMP report fetch for report {report_id}")

        try:
            # Step 1: Extract data
            log.info("ReportService: Step 1 - Extracting Canvas data")
            extracted_data, extraction_errors = self.data_service.extract_all_data_for_pdmp(
                patient_id=patient_id,
                practitioner_id=practitioner_id
            )

            if not extracted_data:
                return self._create_error_result(
                    "data_extraction_failed",
                    "Failed to extract Canvas data",
                    extraction_errors
                )

            # Step 2: Convert DTOs to dictionaries for XML builder
            log.info("ReportService: Step 2 - Converting DTOs to dictionaries")
            converted_data = convert_all_dtos_to_dicts(extracted_data)

            # Step 3: Generate ReportRequest XML
            log.info("ReportService: Step 3 - Generating ReportRequest XML")
            report_request_xml = self.xml_builder.build(converted_data)

            # Step 4: Make API request
            log.info("ReportService: Step 4 - Making PDMP API request")
            api_result = self.pdmp_client.fetch_report(
                report_id=report_id,
                report_request_xml=report_request_xml,
                staff_id=practitioner_id,
                secrets=secrets
            )

            # Step 5: Process result
            if api_result["success"]:
                log.info("ReportService: Report fetched successfully")
                return {
                    "success": True,
                    "report_content": api_result["response_text"],
                    "report_id": report_id,
                    "extraction_errors": extraction_errors,
                    "api_result": api_result
                }
            else:
                log.error(f"ReportService: API request failed - {api_result.get('error', 'Unknown error')}")
                return self._create_error_result(
                    "api_request_failed",
                    f"PDMP API request failed: {api_result.get('error', 'Unknown error')}",
                    [],
                    api_result
                )

        except Exception as e:
            log.error(f"ReportService: Unexpected error: {str(e)}")
            return self._create_error_result(
                "unexpected_error",
                f"Unexpected error: {str(e)}",
                []
            )

    def _create_error_result(self,
                             error_type: str,
                             error_message: str,
                             extraction_errors: List[str] = None,
                             api_result: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create standardized error result."""
        return {
            "success": False,
            "error_type": error_type,
            "error_message": error_message,
            "extraction_errors": extraction_errors or [],
            "api_result": api_result or {}
        }