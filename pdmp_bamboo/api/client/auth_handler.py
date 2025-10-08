"""
PDMP Authentication Handler

Handles authentication for PDMP API requests including header generation and credential management.
"""

import hashlib
import uuid
import time
from typing import Dict, Optional, Tuple
from logger import log
from pdmp_bamboo.utils.secrets_helper import get_staff_credentials


class AuthHandler:
    """Handles authentication for PDMP API requests."""
    
    def __init__(self):
        self.user_agent = "Canvas-PDMP-Plugin/1.0"

    def get_staff_credentials(self, secrets: Dict[str, str], staff_id: str) -> Optional[Tuple[str, str]]:
        """
        Get PDMP credentials for a specific staff member.

        Args:
            secrets: Plugin secrets containing staff credentials
            staff_id: The staff member's ID

        Returns:
            Tuple of (username, password) or None if not found
        """
        try:
            # Get the staff credentials
            staff_creds = get_staff_credentials(secrets, staff_id)

            if not staff_creds:
                log.error(f"AuthHandler: No credentials found for staff {staff_id}")
                return None

            username = staff_creds["username"]
            password = staff_creds["password"]

            if username and password:
                log.info(f"AuthHandler: Found credentials for staff {staff_id}: {username}")
                return (username, password)
            else:
                log.error(f"AuthHandler: Incomplete credentials for staff {staff_id}")
                return None

        except Exception as e:
            log.error(f"AuthHandler: Error getting staff credentials: {e}")
            return None

    def create_auth_headers(self, secrets: Dict[str, str], staff_id: str) -> Dict[str, str]:
        """
        Create BambooHealth PMP Gateway authentication headers.
        
        Args:
            secrets: Plugin secrets containing authentication info
            staff_id: The staff member's ID

        Returns:
            Dictionary of headers for the request
            
        Raises:
            ValueError: If required authentication credentials are missing
        """

        try:
            # Get staff-specific credentials
            log.info(f"AuthHandler: Creating PMP Gateway authentication headers for STAFF {staff_id}")
            credentials = self.get_staff_credentials(secrets, staff_id)

            if not credentials:
                raise ValueError(f"No PDMP credentials found for staff {staff_id}")

            username, password = credentials
        except ValueError as e:
            raise ValueError(f"Authentication credentials not found: {e}")
        
        log.info(f"AuthHandler: Username present: {'Yes' if username else 'No'}")
        log.info(f"AuthHandler: Password present: {'Yes' if password else 'No'}")
        
        # Generate authentication components
        nonce = str(uuid.uuid4())
        timestamp = str(int(time.time()))
        
        log.info(f"AuthHandler: Generated nonce: {nonce[:8]}...")
        log.info(f"AuthHandler: Timestamp: {timestamp}")
        
        # Create password digest: SHA256(password:nonce:timestamp) in lowercase hex
        digest_string = f"{password}:{nonce}:{timestamp}"
        password_digest = hashlib.sha256(digest_string.encode("utf-8")).hexdigest().lower()
        
        log.info("AuthHandler: Password digest generated successfully")
        
        # Return headers as specified in PMP Gateway documentation
        headers = {
            "X-Auth-Username": username,
            "X-Auth-Nonce": nonce,
            "X-Auth-Timestamp": timestamp,
            "X-Auth-PasswordDigest": password_digest,
            "Content-Type": "application/xml",
            "Accept": "application/xml, text/xml, */*",
            "User-Agent": self.user_agent,
        }
        
        log.info("AuthHandler: Authentication headers created successfully")
        return headers


