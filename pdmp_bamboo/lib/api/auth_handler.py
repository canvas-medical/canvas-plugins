"""
PDMP Authentication Handler.

Handles authentication for PDMP API requests including header generation and credential management.
"""

import hashlib
import time
import uuid

from logger import log
from pdmp_bamboo.lib.utils.secrets_helper import get_secrets_for_environment


class AuthHandler:
    """Handles authentication for PDMP API requests."""

    def __init__(self):
        self.user_agent = "Canvas-PDMP-Plugin/1.0"

    def create_auth_headers(
        self, secrets: dict[str, str], use_test_env: bool = False
    ) -> dict[str, str]:
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
            f"AuthHandler: Creating PMP Gateway authentication headers for {env_label} environment"
        )

        # Get environment-specific secrets
        try:
            env_secrets = get_secrets_for_environment(secrets, use_test_env)
            username = env_secrets["username"]
            password = env_secrets["password"]
        except ValueError as e:
            raise ValueError(f"Authentication credentials not found: {e}") from e

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

    def validate_credentials(self, secrets: dict[str, str], use_test_env: bool = False) -> bool:
        """
        Validate that required credentials are present.

        Args:
            secrets: Plugin secrets containing authentication info
            use_test_env: If True, uses test environment credentials

        Returns:
            True if credentials are valid, False otherwise
        """
        try:
            env_secrets = get_secrets_for_environment(secrets, use_test_env)
            username = env_secrets.get("username")
            password = env_secrets.get("password")
            return bool(username and password)
        except ValueError:
            return False
