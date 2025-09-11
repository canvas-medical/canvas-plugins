"""
XML Request Utilities for PDMP Bamboo Plugin

This module provides HTTP request functionality for sending XML templates
to BambooHealth PMP Gateway and handling responses with certificate authentication.
"""

import requests
import hashlib
import uuid
import time
from typing import Dict, Any, Optional
from logger import log

from pdmp_bamboo_simple.utils.secrets_helper import get_secrets_for_environment


def send_pdmp_request(
    api_url: str,
    xml_content: str,
    headers: Dict[str, str],
    secrets: Dict[str, str],
    timeout: int = 30,
    use_test_env: bool = False,
) -> Dict[str, Any]:
    """
    Sends XML content to BambooHealth PMP Gateway.

    Args:
        api_url: The API endpoint URL
        xml_content: The XML content to send
        headers: Request headers
        secrets: Plugin secrets containing configuration
        timeout: Request timeout in seconds (default: 30)
        use_test_env: If True, uses test environment without certificates

    Returns:
        Dict containing status, response data, and request details
    """
    env_label = "Test Environment" if use_test_env else "Production Environment"
    log.info(f"PDMP-Request: Sending PDMP request to {api_url}")
    log.info(f"PDMP-Request: Request timeout: {timeout} seconds")
    log.info(f"PDMP-Request: Environment: {env_label}")

    try:
        log.info(f"PDMP-Request: Using XML content ({len(xml_content)} characters)")

        # Get certificate configuration based on environment
        cert_config = get_cert_config(use_test_env)

        log.info("PDMP-Request: Making POST request to PMP Gateway")
        response = requests.post(
            api_url,
            data=xml_content.encode("utf-8"),
            headers=headers,
            cert=cert_config if cert_config else None,
            timeout=timeout,
            verify=True,
        )

        log.info(f"PDMP-Request: Received response - Status: {response.status_code}")
        log.info(f"PDMP-Request: Response URL: {response.url}")
        log.info(f"PDMP-Request: Response reason: {response.reason}")

        if response.status_code == 200:
            log.info("PDMP-Request: Request successful")
            return {
                "status": "success",
                "status_code": response.status_code,
                "raw_response": response.text,
                "request_xml": xml_content,
                "response_headers": dict(response.headers),
                "response_url": response.url,
            }
        else:
            log.warning(f"PDMP-Request: Request failed with status {response.status_code}")
            return {
                "status": "error",
                "status_code": response.status_code,
                "error": f"PDMP Gateway Error {response.status_code}: {response.text[:500]}",
                "request_xml": xml_content,
                "raw_response": response.text,
                "response_url": response.url,
                "response_reason": response.reason,
            }

    except requests.exceptions.Timeout:
        log.error(f"PDMP-Request: Request timed out after {timeout} seconds")
        return {
            "status": "error",
            "error": f"Request timed out after {timeout} seconds",
        }
    except requests.exceptions.ConnectionError as e:
        log.error(f"PDMP-Request: Connection error: {e}")
        return {
            "status": "error",
            "error": f"Connection error: {str(e)}",
        }
    except requests.exceptions.RequestException as e:
        log.error(f"PDMP-Request: Request exception: {e}")
        return {"status": "error", "error": f"Request failed: {str(e)}"}
    except Exception as e:
        log.error(f"PDMP-Request: Unexpected error during request: {e}")
        return {
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
        }


def create_pdmp_auth_headers(secrets: Dict[str, str], use_test_env: bool = False) -> Dict[str, str]:
    """
    Create BambooHealth PMP Gateway authentication headers.

    Args:
        secrets: Plugin secrets containing authentication info
        use_test_env: If True, uses test environment credentials

    Returns:
        Dictionary of headers for the request

    Raises:
        ValueError: If required authentication credentials are missing
    """
    env_label = "test" if use_test_env else "production"
    log.info(
        f"PDMP-Request: Creating PMP Gateway authentication headers for {env_label} environment"
    )

    # Get environment-specific secrets with all_secrets fallback
    try:
        env_secrets = get_secrets_for_environment(secrets, use_test_env)
        username = env_secrets["username"]
        password = env_secrets["password"]
    except ValueError as e:
        raise ValueError(f"Authentication credentials not found: {e}")

    log.info(f"PDMP-Request: Username present: {'Yes' if username else 'No'}")
    log.info(f"PDMP-Request: Password present: {'Yes' if password else 'No'}")

    # Generate unique nonce - UUID is recommended by BambooHealth docs
    nonce = str(uuid.uuid4())

    # Get current timestamp
    timestamp = str(int(time.time()))

    log.info(f"PDMP-Request: Generated nonce: {nonce[:8]}...")
    log.info(f"PDMP-Request: Timestamp: {timestamp}")

    # Create password digest: SHA256(password:nonce:timestamp) in lowercase hex
    digest_string = f"{password}:{nonce}:{timestamp}"
    password_digest = hashlib.sha256(digest_string.encode("utf-8")).hexdigest().lower()

    log.info("PDMP-Request: Password digest generated successfully")

    # Return headers as specified in PMP Gateway documentation
    headers = {
        "X-Auth-Username": username,
        "X-Auth-Nonce": nonce,
        "X-Auth-Timestamp": timestamp,
        "X-Auth-PasswordDigest": password_digest,
        "Content-Type": "application/xml",
        "Accept": "application/xml, text/xml, */*",
        "User-Agent": "Canvas-PDMP-Plugin/1.0",
    }

    log.info("PDMP-Request: Authentication headers created successfully")
    return headers


def get_cert_config(use_test_env: bool) -> Optional[tuple]:
    """
    Get certificate configuration for PMP Gateway requests based on environment.

    Args:
        use_test_env: If True, uses test environment without certificates

    Returns:
        Tuple of (cert_file, key_file) for client certificates, or None for test environment

    Raises:
        ValueError: If production environment is configured but certificates are missing
    """
    environment = "test" if use_test_env else "production"
    log.info(f"PDMP-Request: Environment configuration: {environment}")

    if not use_test_env:
        log.info("PDMP-Request: Production environment - client certificates required")

        # Build certificate paths relative to plugin root
        module_path = __file__
        base_dir = "/".join(module_path.split("/")[:-2])  # Go up 2 levels from utils/xml_request.py
        cert_file = f"{base_dir}/certs/bamboo_client.crt"
        key_file = f"{base_dir}/certs/bamboo_client_nopass.key"

        log.info(f"PDMP-Request: Certificate file: {cert_file}")
        log.info(f"PDMP-Request: Key file: {key_file}")

        # In production, certificates are required
        return (cert_file, key_file)
    else:
        log.info("PDMP-Request: Test environment - no client certificates required")
        return None


def build_pdmp_api_url(base_url: str) -> str:
    """
    Build the full PDMP API URL from base URL.

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

    log.info(f"PDMP-Request: Built API URL: {api_url}")
    return api_url
