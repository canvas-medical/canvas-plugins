"""
PDMP API Client.

Handles HTTP requests to the PDMP API with proper error handling and response management.
"""

from typing import Any

from pdmp_bamboo.api.client.auth_handler import AuthHandler
from pdmp_bamboo.utils.secrets_helper import get_pdmp_api_url


class PDMPClient:
    """HTTP client for PDMP API requests."""

    def __init__(self):
        self.auth_handler = AuthHandler()
        self.default_timeout = 60

    def send_patient_request(self,
                            api_url: str,
                            xml_content: str,
                            staff_id: str,
                            secrets: Dict[str, str],
                            timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Send PDMP patient data request to the API.

        Args:
            api_url: The API endpoint URL
            xml_content: The XML content to send
            staff_id: The staff member's ID for authentication
            secrets: Plugin secrets containing configuration
            timeout: Request timeout in seconds (default: 60)

        Returns:
            Dict containing status, response data, and request details
        """
        timeout = timeout or self.default_timeout

        log.info(f"PDMPClient: Sending PDMP patient request to {api_url}")
        log.info(f"PDMPClient: Request timeout: {timeout} seconds")
        log.info(f"PDMPClient: Using XML content ({len(xml_content)} characters)")

        try:
            # Create authentication headers
            headers = self.auth_handler.create_auth_headers(secrets, staff_id)

            # Get certificate configuration
            # cert_config = self._get_cert_config(use_test_env) # TODO: fix this
            cert_config = None

            # Make the request using Canvas SDK Http
            http = Http()
            log.info(f"PDMPClient: Sending request to {api_url}")
            
            # Canvas SDK Http.post expects data as string, headers dict
            # Note: Canvas SDK Http does not support timeout or cert parameters
            response = http.post(
                api_url,
                data=xml_content,
                headers=headers,
            )

            log.info(f"PDMPClient: response: {response}")
            return self._process_response(response, xml_content)

        except TimeoutError:
            log.error(f"PDMPClient: Request timed out after {timeout} seconds")
            return create_error_result(
                "timeout", f"Request timed out after {timeout} seconds"
            )

        except ConnectionError as e:
            log.error(f"PDMPClient: Connection error: {e}")
            return create_error_result("connection_error", f"Connection error: {str(e)}")

        except Exception as e:
            log.error(f"PDMPClient: Unexpected error during request: {e}")
            return create_error_result("unexpected_error", f"Unexpected error: {str(e)}")

    def fetch_report(self,
                     report_id: str,
                     report_request_xml: str,
                     staff_id: str,
                     secrets: Dict[str, str],
                     timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetch a PDMP report using the report ID and ReportRequest XML.

        Args:
            report_id: The ID of the report to fetch
            report_request_xml: The ReportRequest XML content
            staff_id: The staff member's ID for authentication
            secrets: Plugin secrets containing configuration
            timeout: Request timeout in seconds (default: 60)

        Returns:
            Dict containing response data and status
        """
        timeout = timeout or self.default_timeout

        log.info(f"PDMPClient: Fetching report {report_id}")
        log.info(f"PDMPClient: Using XML content ({len(report_request_xml)} characters)")

        # Log XML summary
        log.info(f"Report request XML: {len(report_request_xml)} characters")

        try:
            # Build report URL
            base_url = get_pdmp_api_url(secrets)
            report_url = f"{base_url}/v5_1/report/{report_id}"

            # Create headers for report request
            headers = self._create_report_headers(secrets, staff_id)

            # Log headers (mask sensitive data)
            log.info("PDMPClient: Request headers:")
            for key, value in headers.items():
                if "auth" in key.lower() or "password" in key.lower() or "token" in key.lower():
                    log.info(f"  {key}: {value[:10]}...")
                else:
                    log.info(f"  {key}: {value}")

            # Get certificate configuration
            # cert_config = self._get_cert_config(use_test_env) TODO: fix this
            # log.info(f"PDMPClient: Certificate config: {cert_config}")

            # Make the request using Canvas SDK Http
            log.info("PDMPClient: Making POST request to PMP Gateway for report")
            log.info(f"  - URL: {report_url}")
            log.info(f"  - Body length: {len(report_request_xml)} characters")
            log.info(f"  - Timeout: {timeout} seconds")
            log.info(f"  - Verify SSL: True")
            # log.info(f"  - Use certificates: {cert_config is not None}")

            http = Http()
            response = http.post(
                report_url,
                data=report_request_xml,
                headers=headers,
                # cert=cert_config if cert_config else None,
                timeout=timeout,
                verify=True
            )

            # Process response with detailed logging
            return self._process_report_response(response, report_request_xml)

        except TimeoutError:
            log.error(f"PDMPClient: Request timed out after {timeout} seconds")
            return create_error_result(
                "timeout", f"Request timed out after {timeout} seconds"
            )

        except ConnectionError as e:
            log.error(f"PDMPClient: Connection error: {e}")
            return create_error_result("connection_error", f"Connection error: {str(e)}")

        except Exception as e:
            log.error(f"PDMPClient: Unexpected error during request: {e}")
            return create_error_result("unexpected_error", f"Unexpected error: {str(e)}")

    def _process_report_response(self, response: requests.Response, xml_content: str) -> Dict[str, Any]:
        """Process the HTTP response from the PDMP API for report requests with detailed logging."""
        log.info(f"PDMPClient: Received response - Status: {response.status_code}")
        log.info(f"PDMPClient: Response URL: {response.url}")
        log.info(f"PDMPClient: Response reason: {response.reason}")

        # Log response headers
        log.info("PDMPClient: Response headers:")
        for key, value in response.headers.items():
            log.info(f"  {key}: {value}")

        # Log response summary
        log.info(f"Response content: {len(response.text)} characters")

        if response.status_code == 200:
            log.info("PDMPClient: Report request successful")
            return {
                "success": True,
                "response_text": response.text,
                "status_code": response.status_code,
                "request_xml": xml_content,
                "response_headers": dict(response.headers),
                "response_url": response.url,
            }
        else:
            log.warning(f"PDMPClient: Report request failed with status {response.status_code}")

            # Additional error analysis
            if response.status_code == 400:
                log.error("PDMPClient: 400 Bad Request - Response body:")
                log.error(f"PDMPClient: 400 body:\n{response.text}")
                log.error("PDMPClient: 400 Bad Request - Possible causes:")
                log.error("  1. Invalid XML format or structure")
                log.error("  2. Missing required fields in XML")
                log.error("  3. Invalid authentication credentials")
                log.error("  4. Incorrect API endpoint URL")
                log.error("  5. Invalid request headers")
                log.error("  6. XML validation errors")
                log.error("  7. Missing required PDMP fields")
                log.error("  8. Invalid report ID format")
                log.error("  9. Report request XML schema validation errors")

            return {
                "success": False,
                "error": f"PDMP Gateway Error {response.status_code}: {response.text[:500]}",
                "error_message": response.text,
                "status_code": response.status_code,
                "request_xml": xml_content,
                "raw_response": response.text,
                "response_url": response.url,
                "response_reason": response.reason,
            }

    def _process_response(self, response: requests.Response, xml_content: str) -> Dict[str, Any]:
        """Process the HTTP response from the PDMP API."""
        log.info(f"PDMPClient: Received response - Status: {response.status_code}")
        log.info(f"PDMPClient: Response URL: {response.url}")
        log.info(f"PDMPClient: Response reason: {response.reason}")

        # Log response summary
        log.info(f"Response content: {len(response.text)} characters")

        if response.status_code == 200:
            log.info("PDMPClient: Request successful")
            return {
                "status": "success",
                "status_code": response.status_code,
                "raw_response": response.text,
                "request_xml": xml_content,
                "response_headers": dict(response.headers),
                "response_url": response.url,
                # "environment": env_label,
            }
        else:
            log.warning(f"PDMPClient: Request failed with status {response.status_code}")

            # Additional error analysis
            if response.status_code == 400:
                log.error("PDMPClient: 400 Bad Request - Response body:")
                log.error(f"PDMPClient: 400 body:\n{response.text}")
                log.error("PDMPClient: 400 Bad Request - Possible causes:")
                log.error("  1. Invalid XML format or structure")
                log.error("  2. Missing required fields in XML")
                log.error("  3. Invalid authentication credentials")
                log.error("  4. Incorrect API endpoint URL")
                log.error("  5. Invalid request headers")
                log.error("  6. XML validation errors")
                log.error("  7. Missing required PDMP fields")

            return {
                "status": "error",
                "status_code": response.status_code,
                "error": f"PDMP Gateway Error {response.status_code}: {response.text[:500]}",
                "request_xml": xml_content,
                "raw_response": response.text,
                "response_url": response.url,
                "response_reason": response.reason,
                # "environment": env_label,
            }

    def _get_cert_config(self, use_test_env: bool, secrets: dict[str, str]) -> tuple[str, str] | None:
        """
        Get certificate configuration for PMP Gateway requests based on environment.
        
        Certificates are read from plugin secrets instead of file system.
        
        Args:
            use_test_env: Whether using test environment
            secrets: Plugin secrets containing cert paths or content
            
        Returns:
            Tuple of (cert_path, key_path) or None for test environment
        """
        environment = "test" if use_test_env else "production"
        log.info(f"PDMPClient: Environment configuration: {environment}")

        if not use_test_env:
            log.info("PDMPClient: Production environment - client certificates required")

            # Build certificate paths relative to plugin root
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            plugin_root = os.path.join(current_dir, "..", "..")
            cert_file = os.path.join(plugin_root, "certs", "client.crt")
            key_file = os.path.join(plugin_root, "certs", "client-no-password.key")

            if not cert_file or not key_file:
                log.warning("PDMPClient: Certificate paths not configured in secrets")
                log.warning("PDMPClient: Production requests may fail without certificates")
                return None

            log.info(f"PDMPClient: Certificate configured: {bool(cert_file)}")
            log.info(f"PDMPClient: Key configured: {bool(key_file)}")

            return (cert_file, key_file)
        else:
            log.info("PDMPClient: Test environment - no client certificates required")
            return None


    def _create_report_headers(self, secrets: Dict[str, str], staff_id: str) -> Dict[str, str]:
        """Create request headers specifically for report requests."""
        # Use the same auth headers as regular requests
        headers = self.auth_handler.create_auth_headers(secrets, staff_id)

        # Add report-specific headers
        headers["Content-Type"] = "application/xml"
        headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"

        return headers


    def validate_api_url(self, base_url: str) -> str:
        """
        Validate and build the full PDMP API URL from base URL.

        Args:
            base_url: The base API URL from secrets

        Returns:
            Full API URL for PDMP requests

        Raises:
            ValueError: If base URL is invalid
        """
        if not base_url:
            raise ValueError("PDMP_API_URL is required but not provided in plugin secrets")

        if not base_url.startswith("https://"):
            raise ValueError(f"PDMP_API_URL must be a valid HTTPS URL. Provided: {base_url}")

        # Append the PDMP endpoint path
        if base_url.endswith("/"):
            api_url = f"{base_url}v5_1/patient"
        else:
            api_url = f"{base_url}/v5_1/patient"

        log.info(f"PDMPClient: Built API URL: {api_url}")
        return api_url
