"""
Secrets Helper Utility for PDMP Bamboo Plugin

This module provides functionality to read secrets for the PDMP plugin.

Required Secrets:
- PDMP_API_URL: The base URL for the PDMP API
- PDMP_STAFF_CREDENTIALS: JSON array containing staff-specific credentials
"""

import json
from typing import Dict, Optional
from logger import log


def get_pdmp_api_url(secrets: Dict[str, str]) -> str:
    """Get the PDMP API URL from secrets."""
    return secrets.get("PDMP_API_URL", "")


def get_staff_credentials(secrets: Dict[str, str], staff_id: str) -> Optional[Dict[str, str]]:
    """Get PDMP credentials for a specific staff member."""
    try:
        staff_credentials_json = secrets.get("PDMP_STAFF_CREDENTIALS")
        if not staff_credentials_json:
            log.error("PDMP-Secrets: PDMP_STAFF_CREDENTIALS not found")
            return None

        staff_credentials = json.loads(staff_credentials_json)

        for staff_cred in staff_credentials:
            if staff_cred.get("staff_id") == staff_id:
                username = staff_cred.get("pdmp_username")
                password = staff_cred.get("pdmp_password")

                if username and password:
                    return {"username": username, "password": password}

        log.error(f"PDMP-Secrets: No credentials found for staff {staff_id}")
        return None

    except Exception as e:
        log.error(f"PDMP-Secrets: Error getting staff credentials: {e}")
        return None