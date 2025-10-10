"""
SecretsManager

Centralized helper to read and validate PDMP plugin secrets using the new model:
- PDMP_API_URL: base HTTPS URL (e.g., https://secure.prep.pmpgateway.net)
- PDMP_STAFF_CREDENTIALS: JSON array of objects: [{staff_id, pdmp_username, pdmp_password}, ...]

Notes:
- Secrets may be provided as a dict or a JSON string by the runtime.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple

from logger import log


class SecretsManager:
    """
    Resolve PDMP secrets and per-staff credentials.
    """

    def __init__(self, secrets: Dict[str, Any] | str | None):
        self._raw = secrets or {}
        self._parsed: Dict[str, Any] = self._ensure_dict(self._raw)
        self._staff_creds_cache: List[Dict[str, str]] | None = None

    def _ensure_dict(self, value: Dict[str, Any] | str) -> Dict[str, Any]:
        if isinstance(value, dict):
            return value
        try:
            parsed = json.loads(value or "{}")
            if isinstance(parsed, dict):
                return parsed
            log.warning("SecretsManager: top-level secrets JSON is not a dict; using empty dict")
            return {}
        except json.JSONDecodeError as e:
            log.error(f"SecretsManager: Failed to parse secrets JSON: {e}")
            return {}

    def _load_staff_credentials(self) -> List[Dict[str, str]]:
        if self._staff_creds_cache is not None:
            return self._staff_creds_cache

        raw = self._parsed.get("PDMP_STAFF_CREDENTIALS")
        # Accept either a list already, or a JSON string containing a list
        records: List[Dict[str, str]] = []
        if isinstance(raw, list):
            records = raw  # assume list of dicts
        elif isinstance(raw, str):
            try:
                maybe = json.loads(raw)
                if isinstance(maybe, list):
                    records = maybe
                else:
                    log.error("SecretsManager: PDMP_STAFF_CREDENTIALS JSON is not a list")
            except json.JSONDecodeError as e:
                log.error(f"SecretsManager: Invalid PDMP_STAFF_CREDENTIALS JSON: {e}")
        elif raw is None:
            log.error("SecretsManager: PDMP_STAFF_CREDENTIALS not set")
        else:
            log.error(f"SecretsManager: Unsupported PDMP_STAFF_CREDENTIALS type: {type(raw)}")

        # Normalize record keys to strings and validate shape
        normalized: List[Dict[str, str]] = []
        for idx, rec in enumerate(records):
            if not isinstance(rec, dict):
                log.error(f"SecretsManager: credential at index {idx} is not an object")
                continue
            staff_id = str(rec.get("staff_id") or "").strip()
            username = str(rec.get("pdmp_username") or "").strip()
            password = str(rec.get("pdmp_password") or "").strip()
            if not staff_id or not username or not password:
                log.error(
                    f"SecretsManager: credential at index {idx} missing required fields (staff_id/username/password)"
                )
                continue
            normalized.append({
                "staff_id": staff_id,
                "pdmp_username": username,
                "pdmp_password": password,
            })

        self._staff_creds_cache = normalized
        log.info(f"SecretsManager: Loaded {len(self._staff_creds_cache)} staff credential records")
        return self._staff_creds_cache

    def get_api_base_url(self) -> str:
        """
        Return the base HTTPS URL for PDMP API.
        Raises ValueError if missing/invalid.
        """
        base_url = (self._parsed.get("PDMP_API_URL") or "").strip()
        if not base_url:
            raise ValueError("Secret 'PDMP_API_URL' is required but not found")
        if not base_url.startswith("https://"):
            raise ValueError(f"PDMP_API_URL must start with https://. Provided: {base_url}")
        # Normalize: no trailing slash
        return base_url[:-1] if base_url.endswith("/") else base_url

    def get_staff_credentials(self, staff_id: str) -> Tuple[str, str]:
        """
        Resolve (username, password) for a given staff_id.
        Raises ValueError if not found.
        """
        if not staff_id:
            raise ValueError("Staff ID is required to resolve PDMP credentials")

        for rec in self._load_staff_credentials():
            if rec.get("staff_id") == staff_id:
                return rec["pdmp_username"], rec["pdmp_password"]

        raise ValueError(
            "No PDMP credentials found for the current staff user. Please add an entry to PDMP_STAFF_CREDENTIALS."
        )


