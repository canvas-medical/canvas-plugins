"""
PDMP API Client.

Handles HTTP requests to the PDMP API with proper error handling and response management.
"""

from typing import Any

from canvas_sdk.utils import Http
from logger import log
from pdmp_bamboo.lib.api.auth_handler import AuthHandler
from pdmp_bamboo.lib.utils.common import create_error_result


class PDMPClient:
    """HTTP client for PDMP API requests."""

    def __init__(self):
        self.auth_handler = AuthHandler()
        self.default_timeout = 60

    def send_patient_request(
        self,
        api_url: str,
        xml_content: str,
        secrets: dict[str, str],
        use_test_env: bool = False,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        """
        Send PDMP patient data request to the API.

        Args:
            api_url: The API endpoint URL
            xml_content: The XML content to send
            secrets: Plugin secrets containing configuration
            use_test_env: If True, uses test environment without certificates
            timeout: Request timeout in seconds (default: 60)

        Returns:
            Dict containing status, response data, and request details
        """
        env_label = "Test Environment" if use_test_env else "Production Environment"
        timeout = timeout or self.default_timeout

        try:
            # Create authentication headers
            headers = self.auth_handler.create_auth_headers(secrets, use_test_env)

            # Get certificate configuration
            cert_config = self._get_cert_config(use_test_env, secrets)

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

            log.info(f"PDMPClient: Response status: {response.status_code}")
            # Process response
            return self._process_response(response, xml_content, env_label)

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

    def fetch_report(
        self,
        report_id: str,
        report_request_xml: str,
        secrets: dict[str, str],
        use_test_env: bool = False,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        """
        Fetch a PDMP report using the report ID and ReportRequest XML.

        Args:
            report_id: The ID of the report to fetch
            report_request_xml: The ReportRequest XML content
            secrets: Plugin secrets containing configuration
            use_test_env: If True, uses test environment without certificates
            timeout: Request timeout in seconds (default: 60)

        Returns:
            Dict containing response data and status
        """
        env_label = "Test Environment" if use_test_env else "Production Environment"
        timeout = timeout or self.default_timeout

        log.info(f"PDMPClient: Fetching report {report_id}")
        log.info(f"PDMPClient: Using XML content ({len(report_request_xml)} characters)")

        # Log XML summary
        log.info(f"Report request XML: {len(report_request_xml)} characters")

        try:
            # Build report URL
            base_url = self._get_base_url(secrets, use_test_env)
            report_url = f"{base_url}/v5_1/report/{report_id}"

            # Create headers for report request
            headers = self._create_report_headers(secrets, use_test_env)

            # Log headers (mask sensitive data)
            log.info("PDMPClient: Request headers:")
            for key, value in headers.items():
                if "auth" in key.lower() or "password" in key.lower() or "token" in key.lower():
                    log.info(f"  {key}: {value[:10]}...")
                else:
                    log.info(f"  {key}: {value}")

            # Get certificate configuration
            cert_config = self._get_cert_config(use_test_env, secrets)
            log.info(f"PDMPClient: Certificate config: {cert_config}")

            # Make the request using Canvas SDK Http
            log.info("PDMPClient: Making POST request to PMP Gateway for report")
            log.info(f"  - URL: {report_url}")
            log.info(f"  - Body length: {len(report_request_xml)} characters")
            log.info(f"  - Timeout: {timeout} seconds")

            http = Http()
            response = http.post(
                report_url,
                data=report_request_xml,
                headers=headers,
            )

            # Process response with detailed logging
            return self._process_report_response(response, report_request_xml, env_label)

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

    def _process_report_response(
        self, response: Any, xml_content: str, env_label: str
    ) -> dict[str, Any]:
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
                "environment": env_label,
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
                "environment": env_label,
            }

    def _process_response(
        self, response: Any, xml_content: str, env_label: str
    ) -> dict[str, Any]:
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
                "environment": env_label,
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
                "environment": env_label,
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

            # Get certificate paths from secrets (not file system)
            cert_file = secrets.get("PDMP_CLIENT_CERT_PATH")
            key_file = secrets.get("PDMP_CLIENT_KEY_PATH")

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

    def _get_base_url(self, secrets: dict[str, str], use_test_env: bool) -> str:
        """Get the base URL from secrets for the specified environment."""
        from pdmp_bamboo.lib.utils.secrets_helper import get_secrets_for_environment

        env_secrets = get_secrets_for_environment(secrets, use_test_env)
        return env_secrets["url"]

    def _create_report_headers(self, secrets: dict[str, str], use_test_env: bool) -> dict[str, str]:
        """Create request headers specifically for report requests."""
        # Use the same auth headers as regular requests
        headers = self.auth_handler.create_auth_headers(secrets, use_test_env)

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
