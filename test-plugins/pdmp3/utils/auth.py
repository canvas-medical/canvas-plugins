"""
Authentication and Certificate Handling for PMP Gateway
"""

import uuid
import time
import hashlib
from typing import Dict
from logger import log

# [Chat: 2025-01-31] Uncommented and enhanced authentication functionality
# Imports for in-memory certificate handling (kept for reference but not used in sandbox)
# import OpenSSL
# from urllib3.contrib.pyopenssl import PyOpenSSLContext
# from requests.adapters import HTTPAdapter


class PMPGatewayAuth:
    """Handles the generation of authentication headers for the PMP Gateway API."""

    @staticmethod
    def generate_auth_headers(username: str, password: str) -> Dict[str, str]:
        """
        Generates the required X-Auth headers for PMP Gateway authentication.

        Args:
            username: PMP Gateway username
            password: PMP Gateway password

        Returns:
            Dict containing authentication headers
        """
        nonce = str(uuid.uuid4())
        timestamp = str(int(time.time()))
        digest_input = f"{password}:{nonce}:{timestamp}"
        digest = hashlib.sha256(digest_input.encode("utf-8")).hexdigest().lower()

        headers = {
            "X-Auth-Username": username,
            "X-Auth-Timestamp": timestamp,
            "X-Auth-Nonce": nonce,
            "X-Auth-PasswordDigest": digest,
            "Content-Type": "application/xml",
        }

        log.debug(f"PDMP3: Generated auth headers for user: {username}")
        return headers

    @staticmethod
    def generate_basic_auth_headers(username: str, password: str) -> Dict[str, str]:
        """
        Generates basic authentication headers as an alternative.

        Args:
            username: Username for basic auth
            password: Password for basic auth

        Returns:
            Dict containing basic auth headers
        """
        import base64

        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()

        headers = {"Authorization": f"Basic {credentials}", "Content-Type": "application/xml"}

        log.debug(f"PDMP3: Generated basic auth headers for user: {username}")
        return headers


# Certificate handling functionality (commented out due to Canvas sandbox restrictions)
# This would be needed for production use with client certificates
#
# class InMemoryCertHTTPAdapter(HTTPAdapter):
#     """
#     An HTTP adapter for `requests` that allows for loading a client-side
#     certificate and private key directly from in-memory strings.
#     """
#     def __init__(self, cert_content: str, key_content: str, *args, **kwargs):
#         self.cert_content = cert_content
#         self.key_content = key_content
#         super().__init__(*args, **kwargs)
#
#     def init_poolmanager(self, *args, **kwargs):
#         """
#         Initializes the connection pool manager with a custom SSL context that
#         is configured with the in-memory certificate and key.
#         """
#         context = PyOpenSSLContext()
#         cert = OpenSSL.crypto.load_certificate(
#             OpenSSL.crypto.FILETYPE_PEM, self.cert_content.encode('utf-8'))
#         key = OpenSSL.crypto.load_privatekey(
#             OpenSSL.crypto.FILETYPE_PEM, self.key_content.encode('utf-8'))
#
#         context._ctx.use_certificate(cert)
#         context._ctx.use_privatekey(key)
#
#         kwargs['ssl_context'] = context
#         super().init_poolmanager(*args, **kwargs)
