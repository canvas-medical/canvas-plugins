"""
A simple, focused utility for making HTTP requests.
"""

import requests
from typing import Dict, Any, Optional
from logger import log
from canvas_sdk.utils import Http

# [Chat: 2025-01-31] Enhanced request functionality with proper error handling and logging


def send_pdmp_request(
    api_url: str,
    xml_payload: str,
    headers: Dict[str, str],
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    Sends the XML payload to the PMP Gateway.

    Args:
        api_url: The PMP Gateway API endpoint URL
        xml_payload: The XML payload to send
        headers: Authentication and content headers
        timeout: Request timeout in seconds (default: 30)

    Returns:
        Dict containing status, response data, and request details
    """
    log.info(f"PDMP3: Sending request to {api_url[:50]}...")
    log.debug(f"PDMP3: Request headers: {headers}")
    log.debug(f"PDMP3: XML payload length: {len(xml_payload)} characters")

    try:
        # [Chat: 2025-01-31] Make actual POST request with comprehensive error handling
        log.info("PDMP3: Making actual POST request to PMP Gateway")

        response = requests.post(
            api_url,
            data=xml_payload.encode("utf-8"),
            headers=headers,
            timeout=timeout,
            verify=True,  # Keep SSL verification enabled
        )

        log.info(f"PDMP3: Received response - Status: {response.status_code}")
        log.debug(f"PDMP3: Response headers: {dict(response.headers)}")

        if response.status_code == 200:
            log.info("PDMP3: Request successful")
            return {
                "status": "success",
                "status_code": response.status_code,
                "raw_response": response.text,
                "request_xml": xml_payload,
                "response_headers": dict(response.headers),
            }
        else:
            log.warning(f"PDMP3: Request failed with status {response.status_code}")
            return {
                "status": "error",
                "status_code": response.status_code,
                "error": f"API Error {response.status_code}: {response.text[:500]}",
                "request_xml": xml_payload,
                "raw_response": response.text,
            }

    except requests.exceptions.Timeout:
        log.error(f"PDMP3: Request timed out after {timeout} seconds")
        return {
            "status": "error",
            "error": f"Request timed out after {timeout} seconds",
            "request_xml": xml_payload,
        }
    except requests.exceptions.ConnectionError as e:
        log.error(f"PDMP3: Connection error: {e}")
        return {
            "status": "error",
            "error": f"Connection error: {str(e)}",
            "request_xml": xml_payload,
        }
    except requests.exceptions.RequestException as e:
        log.error(f"PDMP3: Request exception: {e}")
        return {"status": "error", "error": f"Request failed: {str(e)}", "request_xml": xml_payload}
    except Exception as e:
        log.error(f"PDMP3: Unexpected error during request: {e}")
        return {
            "status": "error",
            "error": f"Unexpected error: {str(e)}",
            "request_xml": xml_payload,
        }


def send_http_request(
    url: str,
    method: str = "POST",
    data: Optional[str] = None,
    json_data: Optional[Dict] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    Generic HTTP request function for various API calls.

    Args:
        url: The API endpoint URL
        method: HTTP method (GET, POST, PUT, DELETE)
        data: Raw data to send (for XML, text, etc.)
        json_data: JSON data to send
        headers: Request headers
        timeout: Request timeout in seconds

    Returns:
        Dict containing response data and metadata
    """
    headers = headers or {}

    log.info(f"PDMP3: Making {method} request to {url[:50]}...")
    log.debug(f"PDMP3: Request headers: {headers}")

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method.upper() == "POST":
            if json_data:
                response = requests.post(url, json=json_data, headers=headers, timeout=timeout)
            else:
                response = requests.post(url, data=data, headers=headers, timeout=timeout)
        elif method.upper() == "PUT":
            if json_data:
                response = requests.put(url, json=json_data, headers=headers, timeout=timeout)
            else:
                response = requests.put(url, data=data, headers=headers, timeout=timeout)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        log.info(f"PDMP3: {method} request completed - Status: {response.status_code}")

        return {
            "status": "success" if 200 <= response.status_code < 300 else "error",
            "status_code": response.status_code,
            "response_text": response.text,
            "response_headers": dict(response.headers),
            "url": url,
            "method": method,
        }

    except Exception as e:
        log.error(f"PDMP3: {method} request failed: {e}")
        return {"status": "error", "error": str(e), "url": url, "method": method}


def send_report_request(
    report_url: str,
    headers: Dict[str, str],
    staff_data: Dict[str, Any],
    location_data: Dict[str, Any],
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    Sends a ReportRequest to retrieve detailed report data from PMP Gateway.

    Args:
        report_url: The report URL from PatientResponse ReportRequestURLs
        headers: Authentication headers
        staff_data: Provider information for the request
        location_data: Location information for the request
        timeout: Request timeout in seconds

    Returns:
        Dict containing report response data and metadata
    """
    log.info(f"PDMP3: Sending report request to {report_url[:50]}...")

    # Generate ReportRequest XML (simpler than PatientRequest)
    report_xml = _generate_report_request_xml(staff_data, location_data)

    try:
        log.info("PDMP3: Making report POST request to PMP Gateway")

        response = requests.post(
            report_url,
            data=report_xml.encode("utf-8"),
            headers=headers,
            timeout=timeout,
            verify=True,
        )

        log.info(f"PDMP3: Report response received - Status: {response.status_code}")

        if response.status_code == 200:
            log.info("PDMP3: Report request successful")
            return {
                "status": "success",
                "status_code": response.status_code,
                "raw_response": response.text,
                "request_xml": report_xml,
                "response_headers": dict(response.headers),
                "report_url": report_url,
            }
        else:
            log.warning(f"PDMP3: Report request failed with status {response.status_code}")
            return {
                "status": "error",
                "status_code": response.status_code,
                "error": f"Report API Error {response.status_code}: {response.text[:500]}",
                "request_xml": report_xml,
                "raw_response": response.text,
                "report_url": report_url,
            }

    except Exception as e:
        log.error(f"PDMP3: Report request failed: {e}")
        return {
            "status": "error",
            "error": f"Report request failed: {str(e)}",
            "request_xml": report_xml,
            "report_url": report_url,
        }


def _generate_report_request_xml(staff_data: Dict[str, Any], location_data: Dict[str, Any]) -> str:
    """
    Generates ReportRequest XML for fetching detailed reports.
    Uses fallback values to ensure valid XML structure.

    Args:
        staff_data: Provider information
        location_data: Location information

    Returns:
        ReportRequest XML string
    """
    # Use fallback values to ensure valid XML structure
    provider_role = staff_data.get("role", "Physician")
    provider_first = staff_data.get("first_name", "Test")
    provider_last = staff_data.get("last_name", "Provider")
    provider_dea = staff_data.get("dea_number", "AB1234579")
    provider_npi = staff_data.get("npi_number", "1212345671")

    location_name = location_data.get("name", "Test Clinic")
    location_dea = location_data.get("dea", "AB1234579")
    location_npi = location_data.get("npi", "1234567890")
    location_street = location_data.get("street", "123 Test St")
    location_city = location_data.get("city", "Test City")
    location_state = location_data.get("state", "KS")
    location_zip = location_data.get("zip_code", "67203")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<ReportRequest xmlns="http://xml.appriss.com/gateway/v5_1">
  <Requester>
    <Provider>
      <Role>{provider_role}</Role>
      <FirstName>{provider_first}</FirstName>
      <LastName>{provider_last}</LastName>
      <DEANumber>{provider_dea}</DEANumber>
      <NPINumber>{provider_npi}</NPINumber>
    </Provider>
    <Location>
      <Name>{location_name}</Name>
      <DEANumber>{location_dea}</DEANumber>
      <NPINumber>{location_npi}</NPINumber>
      <Address>
        <Street>{location_street}</Street>
        <City>{location_city}</City>
        <StateCode>{location_state}</StateCode>
        <ZipCode>{location_zip}</ZipCode>
      </Address>
    </Location>
  </Requester>
</ReportRequest>"""
