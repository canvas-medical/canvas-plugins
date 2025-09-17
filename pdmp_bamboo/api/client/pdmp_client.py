"""
PDMP API Client

Handles HTTP requests to the PDMP API with proper error handling and response management.
"""

import requests
from typing import Dict, Any, Optional, Tuple
from logger import log

from pdmp_bamboo.api.client.auth_handler import AuthHandler


class PDMPClient:
    """HTTP client for PDMP API requests."""

    def __init__(self):
        self.auth_handler = AuthHandler()
        self.default_timeout = 60

    def send_patient_request(self,
                            api_url: str,
                            xml_content: str,
                            secrets: Dict[str, str],
                            use_test_env: bool = False,
                            timeout: Optional[int] = None) -> Dict[str, Any]:
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

        log.info(f"PDMPClient: Sending PDMP patient request to {api_url}")
        log.info(f"PDMPClient: Request timeout: {timeout} seconds")
        log.info(f"PDMPClient: Environment: {env_label}")
        log.info(f"PDMPClient: Using XML content ({len(xml_content)} characters)")

        try:
            # Create authentication headers
            headers = self.auth_handler.create_auth_headers(secrets, use_test_env)

            # Get certificate configuration
            cert_config = self._get_cert_config(use_test_env)

            # Make the request
            log.info("PDMPClient: Making POST request to PMP Gateway")

            log.info(f"PDMPClient: xml_content: {xml_content}")
            response = requests.post(
                api_url,
                data=xml_content.encode("utf-8"),
                headers=headers,
                cert=cert_config if cert_config else None,
                timeout=timeout,
                verify=True,
            )

            log.info(f"PDMPClient: response: {response}")
            # Process response
            return self._process_response(response, xml_content, env_label)

        except requests.exceptions.Timeout:
            log.error(f"PDMPClient: Request timed out after {timeout} seconds")
            return self._create_error_result("timeout", f"Request timed out after {timeout} seconds")

        except requests.exceptions.ConnectionError as e:
            log.error(f"PDMPClient: Connection error: {e}")
            return self._create_error_result("connection_error", f"Connection error: {str(e)}")

        except requests.exceptions.RequestException as e:
            log.error(f"PDMPClient: Request exception: {e}")
            return self._create_error_result("request_error", f"Request failed: {str(e)}")

        except Exception as e:
            log.error(f"PDMPClient: Unexpected error during request: {e}")
            return self._create_error_result("unexpected_error", f"Unexpected error: {str(e)}")

    def fetch_report(self,
                     report_id: str,
                     report_request_xml: str,
                     secrets: Dict[str, str],
                     use_test_env: bool = False,
                     timeout: Optional[int] = None) -> Dict[str, Any]:
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
        log.info(f"PDMPClient: Environment: {env_label}")
        log.info(f"PDMPClient: Using XML content ({len(report_request_xml)} characters)")

        # Log the complete XML content for debugging
        log.info("=" * 80)
        log.info("PDMPClient: COMPLETE REPORT REQUEST XML CONTENT:")
        log.info("=" * 80)
        log.info(report_request_xml)
        log.info("=" * 80)

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
            cert_config = self._get_cert_config(use_test_env)
            log.info(f"PDMPClient: Certificate config: {cert_config}")

            # Make the request
            log.info("PDMPClient: Making POST request to PMP Gateway for report")
            log.info(f"PDMPClient: Request details:")
            log.info(f"  - URL: {report_url}")
            log.info(f"  - Method: POST")
            log.info(f"  - Content-Type: {headers.get('Content-Type', 'Not set')}")
            log.info(f"  - Body length: {len(report_request_xml)} characters")
            log.info(f"  - Timeout: {timeout} seconds")
            log.info(f"  - Verify SSL: True")
            log.info(f"  - Use certificates: {cert_config is not None}")

            response = requests.post(
                report_url,
                data=report_request_xml.encode("utf-8"),
                headers=headers,
                cert=cert_config if cert_config else None,
                timeout=timeout,
                verify=True
            )

            # Process response with detailed logging
            return self._process_report_response(response, report_request_xml, env_label)

        except requests.exceptions.Timeout:
            log.error(f"PDMPClient: Request timed out after {timeout} seconds")
            return self._create_error_result("timeout", f"Request timed out after {timeout} seconds")

        except requests.exceptions.ConnectionError as e:
            log.error(f"PDMPClient: Connection error: {e}")
            return self._create_error_result("connection_error", f"Connection error: {str(e)}")

        except requests.exceptions.RequestException as e:
            log.error(f"PDMPClient: Request exception: {e}")
            return self._create_error_result("request_error", f"Request failed: {str(e)}")

        except Exception as e:
            log.error(f"PDMPClient: Unexpected error during request: {e}")
            return self._create_error_result("unexpected_error", f"Unexpected error: {str(e)}")

    def _process_report_response(self, response: requests.Response, xml_content: str, env_label: str) -> Dict[str, Any]:
        """Process the HTTP response from the PDMP API for report requests with detailed logging."""
        log.info(f"PDMPClient: Received response - Status: {response.status_code}")
        log.info(f"PDMPClient: Response URL: {response.url}")
        log.info(f"PDMPClient: Response reason: {response.reason}")

        # Log response headers
        log.info("PDMPClient: Response headers:")
        for key, value in response.headers.items():
            log.info(f"  {key}: {value}")

        # Log response content
        log.info(f"PDMPClient: Response content length: {len(response.text)} characters")
        log.info("=" * 80)
        log.info("PDMPClient: COMPLETE RESPONSE CONTENT:")
        log.info("=" * 80)
        log.info(response.text)
        log.info("=" * 80)

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

    def _process_response(self, response: requests.Response, xml_content: str, env_label: str) -> Dict[str, Any]:
        """Process the HTTP response from the PDMP API."""
        log.info(f"PDMPClient: Received response - Status: {response.status_code}")
        log.info(f"PDMPClient: Response URL: {response.url}")
        log.info(f"PDMPClient: Response reason: {response.reason}")

        # Log response content for debugging
        log.info(f"PDMPClient: Response content length: {len(response.text)} characters")
        log.info("=" * 80)
        log.info("PDMPClient: COMPLETE RESPONSE CONTENT:")
        log.info("=" * 80)
        log.info(response.text)
        log.info("=" * 80)

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

    def _get_cert_config(self, use_test_env: bool) -> Optional[Tuple[str, str]]:
        """Get certificate configuration for PMP Gateway requests based on environment."""
        environment = "test" if use_test_env else "production"
        log.info(f"PDMPClient: Environment configuration: {environment}")

        if not use_test_env:
            log.info("PDMPClient: Production environment - client certificates required")

            # Build certificate paths relative to plugin root
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            plugin_root = os.path.join(current_dir, "..", "..")
            cert_file = os.path.join(plugin_root, "certs", "bamboo_client.crt")
            key_file = os.path.join(plugin_root, "certs", "bamboo_client_nopass.key")

            log.info(f"PDMPClient: Certificate file: {cert_file}")
            log.info(f"PDMPClient: Key file: {key_file}")

            return (cert_file, key_file)
        else:
            log.info("PDMPClient: Test environment - no client certificates required")
            return None

    def _get_base_url(self, secrets: Dict[str, str], use_test_env: bool) -> str:
        """Get the base URL from secrets for the specified environment."""
        from pdmp_bamboo.utils.secrets_helper import get_secrets_for_environment

        env_secrets = get_secrets_for_environment(secrets, use_test_env)
        return env_secrets["url"]

    def _create_report_headers(self, secrets: Dict[str, str], use_test_env: bool) -> Dict[str, str]:
        """Create request headers specifically for report requests."""
        # Use the same auth headers as regular requests
        headers = self.auth_handler.create_auth_headers(secrets, use_test_env)

        # Add report-specific headers
        headers["Content-Type"] = "application/xml"
        headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"

        return headers

    def _create_error_result(self, error_type: str, error_message: str) -> Dict[str, Any]:
        """Create standardized error result."""
        return {
            "status": "error",
            "error_type": error_type,
            "error": error_message,
        }

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