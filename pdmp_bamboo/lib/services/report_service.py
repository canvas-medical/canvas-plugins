"""
Report Service.

Handles the business logic for PDMP report requests.
Separates business logic from API endpoint concerns.
"""

import re
from typing import Any

from canvas_sdk.utils import Http
from logger import log
from pdmp_bamboo.lib.api.pdmp_client import PDMPClient
from pdmp_bamboo.lib.services.data_extraction import DataExtractionService
from pdmp_bamboo.lib.utils.common import create_error_result
from pdmp_bamboo.lib.xml.builders.report_request_builder import ReportRequestXMLBuilder


class ReportService:
    """Service for handling PDMP report requests."""

    def __init__(self):
        self.data_service = DataExtractionService()
        self.xml_builder = ReportRequestXMLBuilder()
        self.pdmp_client = PDMPClient()

    def fetch_pdmp_report(
        self,
        report_id: str,
        patient_id: str,
        practitioner_id: str,
        secrets: dict[str, Any],
        use_test_env: bool = False,
    ) -> dict[str, Any]:
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
                patient_id=patient_id, practitioner_id=practitioner_id
            )

            if not extracted_data:
                return create_error_result(
                    "data_extraction_failed", "Failed to extract Canvas data", extraction_errors=extraction_errors
                )

            # Step 2: Convert DTOs to dictionaries for XML builder
            log.info("ReportService: Step 2 - Converting DTOs to dictionaries")
            converted_data = {
                key: value.to_dict() if hasattr(value, 'to_dict') else value
                for key, value in extracted_data.items()
            }

            # Step 3: Generate ReportRequest XML
            log.info("ReportService: Step 3 - Generating ReportRequest XML")
            report_request_xml = self.xml_builder.build(converted_data)

            # Step 4: Make API request
            log.info("ReportService: Step 4 - Making PDMP API request")
            api_result = self.pdmp_client.fetch_report(
                report_id=report_id,
                report_request_xml=report_request_xml,
                secrets=secrets,
                use_test_env=use_test_env,
            )

            # Step 5: Process result
            if api_result["success"]:
                log.info("ReportService: Report fetched successfully")

                # Step 6: Parse response to extract report URL
                response_text = api_result["response_text"]
                report_url = self._extract_report_url(response_text)

                if not report_url:
                    log.error("ReportService: Could not extract report URL from response")
                    return create_error_result(
                        "url_extraction_failed",
                        "Could not extract report URL from API response",
                        extraction_errors=extraction_errors,
                        api_result=api_result,
                    )

                # Step 7: Fetch the actual HTML report from the URL
                log.info(f"ReportService: Fetching report HTML from {report_url}")
                report_html = self._fetch_report_html(report_url)

                if not report_html:
                    return create_error_result(
                        "html_fetch_failed",
                        f"Failed to fetch HTML content from {report_url}",
                        extraction_errors=extraction_errors,
                        api_result=api_result,
                    )

                log.info("ReportService: Successfully fetched report HTML")
                return {
                    "success": True,
                    "report_content": report_html,
                    "report_url": report_url,
                    "report_id": report_id,
                    "extraction_errors": extraction_errors,
                    "api_result": api_result,
                }
            else:
                log.error(f"ReportService: API request failed - {api_result.get('error', 'Unknown error')}")
                return create_error_result(
                    "api_request_failed",
                    f"PDMP API request failed: {api_result.get('error', 'Unknown error')}",
                    extraction_errors=[],
                    api_result=api_result,
                )

        except Exception as e:
            log.error(f"ReportService: Unexpected error: {str(e)}")
            return create_error_result("unexpected_error", f"Unexpected error: {str(e)}", extraction_errors=[])

    def _extract_report_url(self, response_text: str) -> str | None:
        """
        Extract the report URL from the PDMP API XML response.

        <ReportResponse xmlns="http://xml.appriss.com/gateway/v5_1">
            <ReportLink>https://prep.pmpgateway.net/v5_1/report_link/...</ReportLink>
        </ReportResponse>

        Args:
            response_text: The XML response text from PDMP API

        Returns:
            The extracted URL, or None if not found
        """
        if not response_text:
            return None

        # Try to extract ReportLink from XML
        # This handles XML with or without namespaces
        report_link_pattern = r"<ReportLink[^>]*>(https?://[^<]+)</ReportLink>"
        match = re.search(report_link_pattern, response_text)

        if match:
            url = match.group(1)
            log.info(f"ReportService: Extracted report URL: {url}")
            return url

        # Look for URLs that contain 'report_link' or 'pmpgateway'
        url_pattern = r'(https?://[^\s<>"]+(?:report_link|pmpgateway)[^\s<>"]*)'
        match = re.search(url_pattern, response_text)

        if match:
            url = match.group(1)
            log.info(f"ReportService: Extracted report URL (fallback): {url}")
            return url

        log.warning(f"ReportService: Could not extract URL from response: {response_text}")
        return None

    def _fetch_report_html(self, report_url: str) -> str | None:
        """
        Fetch the actual HTML report content from the report URL.

        Args:
            report_url: The URL to fetch the report from

        Returns:
            The HTML content, or None if fetch failed
        """
        try:
            http = Http()
            response = http.get(report_url)

            if response.status_code == 200:
                log.info(
                    f"ReportService: Successfully fetched HTML ({len(response.text)} characters)"
                )
                return response.text
            else:
                log.error(f"ReportService: Failed to fetch HTML. Status: {response.status_code}")
                return None

        except Exception as e:
            log.error(f"ReportService: Error fetching report HTML: {str(e)}")
            return None

