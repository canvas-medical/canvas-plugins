"""
Report API for PDMP Bamboo Simple Plugin
"""

# from canvas_sdk.handlers.simple_api import SimpleAPIRoute
# from canvas_sdk.handlers.simple_api.security import Credentials
# from canvas_sdk.effects.simple_api import HTMLResponse
# from http import HTTPStatus
# from logger import log
#
# # Import the same data extraction function used in the main workflow
# from pdmp_bamboo_simple.utils.data_extractor import extract_all_data_for_pdmp
# from pdmp_bamboo_simple.utils.xml_mapper import create_report_request_xml
# from pdmp_bamboo_simple.utils.xml_request import (
#     create_pdmp_auth_headers,
#     get_cert_config,
# )
# from pdmp_bamboo_simple.utils.secrets_helper import get_secret_value
# import requests
#
#
# class ReportAPI(SimpleAPIRoute):
#     """Report API for PDMP requests"""
#
#     PATH = "/report"
#
#     def authenticate(self, credentials: Credentials) -> bool:
#         return True
#
#     def get(self) -> list:
#         """Handle report requests using the same data extraction as main workflow"""
#
#         # Get parameters
#         report_id = self.request.query_params.get("report_id")
#         env = self.request.query_params.get("env", "test")
#         patient_id = self.request.query_params.get("patient_id")
#         practitioner_id = self.request.query_params.get("practitioner_id")
#         organization_id = self.request.query_params.get("organization_id")
#
#         # Add comprehensive logging
#         log.info("=" * 80)
#         log.info("PDMP-Simple-ReportAPI: Starting report request")
#         log.info(f"PDMP-Simple-ReportAPI: Report ID: {report_id}")
#         log.info(f"PDMP-Simple-ReportAPI: Environment: {env}")
#         log.info("PDMP-Simple-ReportAPI: Canvas Context IDs:")
#         log.info(f"  - Patient ID: {patient_id}")
#         log.info(f"  - Practitioner ID: {practitioner_id}")
#         log.info(f"  - Organization ID: {organization_id}")
#         log.info("PDMP-Simple-ReportAPI: All query parameters:")
#         for key, value in self.request.query_params.items():
#             log.info(f"  - {key}: {value}")
#         log.info("=" * 80)
#
#         # Validate required parameters
#         if not report_id:
#             log.error("PDMP-Simple-ReportAPI: Missing report_id parameter")
#             return [HTMLResponse(
#                 "<h3>Error: Missing Report ID</h3><p>Report ID is required to fetch the PDMP report.</p>",
#                 status_code=HTTPStatus.BAD_REQUEST
#             )]
#
#         if not patient_id or not practitioner_id:
#             log.error("PDMP-Simple-ReportAPI: Missing required Canvas context IDs")
#             return [HTMLResponse(
#                 "<h3>Error: Missing Context</h3><p>Patient ID and Practitioner ID are required.</p>",
#                 status_code=HTTPStatus.BAD_REQUEST
#             )]
#
#         try:
#             # Use the same data extraction as the main workflow
#             log.info("PDMP-Simple-ReportAPI: Extracting Canvas data using same method as main workflow")
#             canvas_data, extraction_errors = extract_all_data_for_pdmp(
#                 patient_id=patient_id,
#                 practitioner_id=practitioner_id
#             )
#
#             if not canvas_data:
#                 log.error("PDMP-Simple-ReportAPI: Failed to extract Canvas data")
#                 return [HTMLResponse(
#                     "<h3>Error: Data Extraction Failed</h3><p>Could not extract Canvas data for report request.</p>",
#                     status_code=HTTPStatus.INTERNAL_SERVER_ERROR
#                 )]
#
#             log.info("PDMP-Simple-ReportAPI: Canvas data extracted successfully")
#             log.info(f"PDMP-Simple-ReportAPI: Extracted data keys: {list(canvas_data.keys())}")
#
#             # Log detailed extracted data
#             log.info("PDMP-Simple-ReportAPI: Detailed extracted data:")
#             for key, value in canvas_data.items():
#                 if key != "extraction_errors":
#                     log.info(f"  {key}: {value}")
#
#             if extraction_errors:
#                 log.warning(f"PDMP-Simple-ReportAPI: Extraction errors: {extraction_errors}")
#
#             # Create ReportRequest XML using the extracted data
#             log.info("PDMP-Simple-ReportAPI: Creating ReportRequest XML from extracted data")
#             report_request_xml = create_report_request_xml(canvas_data)
#
#             log.info(f"PDMP-Simple-ReportAPI: Created ReportRequest XML ({len(report_request_xml)} characters)")
#             log.info("PDMP-Simple-ReportAPI: ReportRequest XML content:")
#             log.info("=" * 60)
#             log.info(report_request_xml)
#             log.info("=" * 60)
#
#             # Get API configuration
#             use_test_env = (env.lower() == "test")
#             log.info(f"PDMP-Simple-ReportAPI: Using test environment: {use_test_env}")
#
#             # Get base URL from secrets
#             if use_test_env:
#                 base_url = get_secret_value(self.secrets, "TEST_PDMP_API_URL")
#                 log.info(f"PDMP-Simple-ReportAPI: Retrieved TEST_PDMP_API_URL: {base_url}")
#             else:
#                 base_url = get_secret_value(self.secrets, "PDMP_API_URL")
#                 log.info(f"PDMP-Simple-ReportAPI: Retrieved PDMP_API_URL: {base_url}")
#
#             if not base_url:
#                 log.error(f"PDMP-Simple-ReportAPI: No base URL found for {env} environment")
#                 return [HTMLResponse(
#                     f"<h3>Error: Missing API URL</h3><p>Please configure the API URL in plugin secrets.</p>",
#                     status_code=HTTPStatus.INTERNAL_SERVER_ERROR
#                 )]
#
#             # Build report URL
#             report_url = f"{base_url}/v5_1/report/{report_id}"
#             log.info(f"PDMP-Simple-ReportAPI: Built report URL: {report_url}")
#
#             # Create authentication headers
#             log.info("PDMP-Simple-ReportAPI: Creating authentication headers")
#             headers = create_pdmp_auth_headers(self.secrets, use_test_env=use_test_env)
#             headers["Content-Type"] = "application/xml"
#             headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
#
#             log.info("PDMP-Simple-ReportAPI: Request headers:")
#             for key, value in headers.items():
#                 # Don't log sensitive auth headers in full
#                 if "auth" in key.lower() or "password" in key.lower():
#                     log.info(f"  {key}: {value[:10]}...")
#                 else:
#                     log.info(f"  {key}: {value}")
#
#             # Get certificate configuration
#             cert_config = get_cert_config(use_test_env)
#             log.info(f"PDMP-Simple-ReportAPI: Certificate config: {cert_config}")
#
#             log.info("PDMP-Simple-ReportAPI: Making authenticated request to report URL")
#             log.info(f"PDMP-Simple-ReportAPI: Request details:")
#             log.info(f"  - URL: {report_url}")
#             log.info(f"  - Method: POST")
#             log.info(f"  - Content-Type: {headers['Content-Type']}")
#             log.info(f"  - Body length: {len(report_request_xml)} characters")
#
#             # Make the POST request with ReportRequest XML body
#             response = requests.post(
#                 report_url,
#                 data=report_request_xml.encode("utf-8"),
#                 headers=headers,
#                 cert=cert_config if cert_config else None,
#                 timeout=30,
#                 verify=True
#             )
#
#             log.info("PDMP-Simple-ReportAPI: Response received")
#             log.info(f"PDMP-Simple-ReportAPI: Response status code: {response.status_code}")
#             log.info(f"PDMP-Simple-ReportAPI: Response headers:")
#             for key, value in response.headers.items():
#                 log.info(f"  {key}: {value}")
#
#             log.info(f"PDMP-Simple-ReportAPI: Response content length: {len(response.text)} characters")
#             log.info("PDMP-Simple-ReportAPI: Full response content:")
#             log.info("=" * 60)
#             log.info(response.text)
#             log.info("=" * 60)
#
#             if response.status_code == 200:
#                 return [HTMLResponse(response.text, status_code=HTTPStatus.OK)]
#                 # log.info(f"PDMP-Simple-ReportAPI: Successfully fetched report ({len(response.text)} chars)")
#                 #
#                 # # Parse the response to extract the report link
#                 # report_link = _extract_report_link_from_response(response.text)
#                 #
#                 # if report_link:
#                 #     log.info(f"PDMP-Simple-ReportAPI: Redirecting to report link: {report_link}")
#                 #
#                 #     # Return HTML that redirects to the report link
#                 #     redirect_html = f"""
#                 #     <!DOCTYPE html>
#                 #     <html>
#                 #     <head>
#                 #         <title>PDMP Report</title>
#                 #         <meta http-equiv="refresh" content="0; url={report_link}">
#                 #         <script>
#                 #             // Immediate redirect
#                 #             window.location.href = '{report_link}';
#                 #         </script>
#                 #     </head>
#                 #     <body>
#                 #         <h3>Opening PDMP Report...</h3>
#                 #         <p>If you are not redirected automatically, <a href="{report_link}" target="_blank">click here</a> to open the report.</p>
#                 #     </body>
#                 #     </html>
#                 #     """
#                 #
#                 #     return [HTMLResponse(response.text, status_code=HTTPStatus.OK)]
#                 # else:
#                 #     log.error("PDMP-Simple-ReportAPI: Could not extract report link from response")
#                 #     return [HTMLResponse(
#                 #         f"""
#                 #         <h3>Error: Could not extract report link</h3>
#                 #         <p>Response received but no report link found.</p>
#                 #         <p><strong>Response:</strong> {response.text[:500]}</p>
#                 #         """,
#                 #         status_code=HTTPStatus.INTERNAL_SERVER_ERROR
#                 #     )]
#             else:
#                 log.error(f"PDMP-Simple-ReportAPI: Failed to fetch report - Status: {response.status_code}")
#                 log.error(f"PDMP-Simple-ReportAPI: Error response: {response.text}")
#
#                 # Try to extract more details from the error response
#                 if "Invalid Report Request" in response.text:
#                     log.error("PDMP-Simple-ReportAPI: BambooHealth returned 'Invalid Report Request' error")
#                     log.error("PDMP-Simple-ReportAPI: This usually means:")
#                     log.error("  1. ReportRequest XML format is incorrect")
#                     log.error("  2. Missing required fields in ReportRequest")
#                     log.error("  3. Provider/Location data doesn't match original PatientRequest")
#                     log.error("  4. Report ID is invalid or expired")
#
#                 return [HTMLResponse(
#                     f"""
#                     <h3>Error: Failed to fetch PDMP report</h3>
#                     <p><strong>Status Code:</strong> {response.status_code}</p>
#                     <p><strong>Error:</strong> {response.text}</p>
#                     <p><strong>Report ID:</strong> {report_id}</p>
#                     <p><strong>Environment:</strong> {env}</p>
#                     """,
#                     status_code=HTTPStatus.INTERNAL_SERVER_ERROR
#                 )]
#
#         except Exception as e:
#             log.error(f"PDMP-Simple-ReportAPI: Exception occurred: {str(e)}")
#             import traceback
#             log.error(f"PDMP-Simple-ReportAPI: Full traceback:")
#             log.error(traceback.format_exc())
#             return [HTMLResponse(
#                 f"<h3>Error: Failed to fetch PDMP report</h3><p>{str(e)}</p>",
#                 status_code=HTTPStatus.INTERNAL_SERVER_ERROR
#             )]
#
#
# def _extract_report_link_from_response(response_text: str) -> str:
#     """
#     Extract the report link from the BambooHealth response.
#
#     The response should contain a report link like:
#     https://prep.pmpgateway.net/v5_1/report_link/66fcd8ac-f555-4fd1-9de5-00bee6ded9dd
#     """
#     import re
#
#     log.info("PDMP-Simple-ReportAPI: Extracting report link from response")
#
#     # Look for report link pattern
#     report_link_pattern = r'https://[^/]+/v5_1/report_link/[a-f0-9-]+'
#     matches = re.findall(report_link_pattern, response_text)
#
#     if matches:
#         report_link = matches[0]
#         log.info(f"PDMP-Simple-ReportAPI: Found report link: {report_link}")
#         return report_link
#     else:
#         log.warning("PDMP-Simple-ReportAPI: No report link found in response")
#         log.warning(f"PDMP-Simple-ReportAPI: Response content: {response_text}")
#         return None

