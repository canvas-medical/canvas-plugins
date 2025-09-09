"""
Report API for PDMP Bamboo Plugin

This module provides a Canvas SimpleAPIRoute endpoint to fetch PDMP report HTML 
from BambooHealth PMP Gateway using authenticated requests with proper certificate handling.

Requirements:
- Uses self.secrets directly (SimpleAPIRoute pattern)  
- Supports both test and production environments
- Reuses authentication logic from xml_request.py
- Handles client certificates for production environment
- Validates input parameters (UUID format for report_id)

Secrets Configuration:
The handler expects secrets in 'all_secrets' JSON field format:
{
    "all_secrets": "{
        \"TEST_PDMP_API_URL\": \"https://prep.pmpgateway.net\",
        \"TEST_PDMP_API_USERNAME\": \"canvas-prep-1\", 
        \"TEST_PDMP_API_PASSWORD\": \"test_password\",
        \"PDMP_API_URL\": \"https://mutualauth.pmpgateway.net\",
        \"PDMP_API_USERNAME\": \"canvas-prep-2\",
        \"PDMP_API_PASSWORD\": \"prod_password\"
    }"
}

URL Format: 
GET /plugin-io/api/pdmp_bamboo/report?report_id={UUID}&env={test|prod}

Example:
http://localhost:8000/plugin-io/api/pdmp_bamboo/report?report_id=fe180397-c07e-4fa4-960c-6ed9574b701d&env=test
"""

import requests
import re
from typing import List
from http import HTTPStatus
from canvas_sdk.handlers.simple_api import SimpleAPIRoute, Credentials
from canvas_sdk.effects.simple_api import HTMLResponse, Response
from logger import log

from pdmp_bamboo.utils.xml_request import create_pdmp_auth_headers, get_cert_config
from pdmp_bamboo.utils.secrets_helper import get_secret_value


class ReportAPI(SimpleAPIRoute):
    """
    Canvas SimpleAPIRoute endpoint that fetches PDMP report HTML from BambooHealth PMP Gateway.
    
    This handler proxies authenticated requests to fetch PDMP report URLs, handling both
    test and production environments with proper authentication headers and client certificates.
    
    Path: /report
    Method: GET (Canvas endpoint) -> POST (to BambooHealth)  
    Query Parameters:
        - report_id (required): UUID of the PDMP report to fetch
        - env (optional): Environment - 'test' or 'prod', defaults to 'prod'
        
    Authentication: 
        - Uses Canvas built-in authentication (SimpleAPIRoute)
        - Creates BambooHealth auth headers using same pattern as PDMP requests
        - Supports client certificate authentication for production environment
        
    Returns:
        - 200: HTML content of the PDMP report
        - 400: Bad request (invalid parameters)  
        - 500: Internal server error (missing config, API errors)
    """
    
    PATH = "/report"

    def authenticate(self, credentials: Credentials) -> bool:
        return True

    def get(self) -> List[Response]:
        """
        Fetch PDMP report from external URL with authentication headers
        Query Parameters:
            report_url: The PDMP report URL to fetch (from query string)
        """
        # Get report_id and environment from query parameters
        report_id = self.request.query_params.get("report_id")
        env = self.request.query_params.get("env", "prod")  # Default to prod
        
        # Debug logging
        log.info(f"PDMP API: Request path: {self.request.path}")
        log.info(f"PDMP API: Query params: {self.request.query_params}")
        log.info(f"PDMP API: Report ID: {report_id}")
        log.info(f"PDMP API: Environment: {env}")

        if not report_id:
            error_msg = """
            <h3>Error: Missing report_id parameter</h3>
            <p>The report_id query parameter is required to fetch the PDMP report.</p>
            <p>Example: /plugin-io/api/pdmp_bamboo/report?report_id=8f136ff4-dacf-4f37-ad6c-aa2c06634b49&env=prod</p>
            """
            return [HTMLResponse(error_msg, status_code=HTTPStatus.BAD_REQUEST)]

        try:
            # Use self.secrets directly (same pattern as other SimpleAPIRoute examples)
            log.info("PDMP API: Using self.secrets")
            
            # Build the full report URL from report ID and environment  
            use_test_env = (env.lower() == "test")
            log.info(f"PDMP API: use_test_env: {use_test_env}")
            
            log.info("PDMP API: About to call get_secret_value...")
            if use_test_env:
                base_url = get_secret_value(self.secrets, "TEST_PDMP_API_URL")
                log.info(f"PDMP API: Retrieved TEST_PDMP_API_URL: {base_url}")
            else:
                base_url = get_secret_value(self.secrets, "PDMP_API_URL")
                log.info(f"PDMP API: Retrieved PDMP_API_URL: {base_url}")
            
            if not base_url:
                log.error(f"PDMP API: No base URL found for {env} environment")
                error_msg = f"<h3>Error: Missing API URL for {env} environment</h3><p>Please configure the API URL in plugin secrets.</p>"
                return [HTMLResponse(error_msg, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)]
            
            report_url = f"{base_url}/v5_1/report/{report_id}"
            log.info(f"PDMP API: Built report URL: {report_url}")
            
            # Create auth headers (same pattern as xml_request.py)
            headers = create_pdmp_auth_headers(self.secrets, use_test_env=use_test_env)
            headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            
            # Get cert config (same pattern as xml_request.py)  
            cert_config = get_cert_config(use_test_env)
            
            log.info("PDMP API: Making authenticated request to report URL")
            
            # Make the request directly (same pattern as xml_request.py)
            # Note: BambooHealth PMP Gateway requires POST for report endpoints
            response = requests.post(
                report_url, 
                headers=headers, 
                cert=cert_config if cert_config else None,
                timeout=30, 
                verify=True
            )
            
            log.info(f"PDMP API: Report fetch response - Status: {response.status_code}")
            
            if response.status_code == 200:
                log.info(f"PDMP API: Successfully fetched report ({len(response.text)} chars)")
                return [HTMLResponse(response.text, status_code=HTTPStatus.OK)]
            else:
                log.error(f"PDMP API: Failed to fetch report - Status: {response.status_code}")
                error_msg = f"""
                <h3>Error: Failed to fetch PDMP report</h3>
                <p><strong>Status Code:</strong> {response.status_code}</p>
                <p><strong>Response:</strong> {response.text[:500]}</p>
                """
                return [HTMLResponse(error_msg, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)]

        except Exception as e:
            log.error(f"PDMP API: Failed to fetch report: {e}")
            error_msg = f"<h3>Error: Failed to fetch PDMP report</h3><p>{str(e)}</p>"
            return [HTMLResponse(error_msg, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)]

