"""
PDMP Authentication Handler.

Builds BambooHealth PMP Gateway WSSE-style authentication headers from username/password.
"""

import hashlib
import time
import uuid

from logger import log
 


class AuthHandler:
    """Handles authentication for PDMP API requests."""

    def __init__(self):
        self.user_agent = "Canvas-PDMP-Plugin/1.0"

    def create_auth_headers(
        self, username: str, password: str
    ) -> dict[str, str]:
        """
        Create BambooHealth PMP Gateway authentication headers.

        Args:
            username: PDMP gateway username for the current staff
            password: PDMP gateway password for the current staff

        Returns:
            Dictionary of headers for the request

        Raises:
            ValueError: If required authentication credentials are missing
        """
        log.info("AuthHandler: Creating PMP Gateway authentication headers")

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

    def validate_credentials(self, username: str | None, password: str | None) -> bool:
        """Simple validation helper for presence of credentials."""
        return bool(username and password)
