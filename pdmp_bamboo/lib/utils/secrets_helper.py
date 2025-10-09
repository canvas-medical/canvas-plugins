"""
Secrets Helper Utility for PDMP Bamboo Plugin.

This module provides functionality to read secrets with priority-based lookup system.

Priority Order:
1. Individual secrets (higher priority): Direct secret fields like "TEST_PDMP_API_URL"
2. all_secrets JSON (fallback): Consolidated JSON field containing all secrets
3. Returns None if neither source contains the requested secret
"""

import json
from typing import Any

from logger import log


def get_secret_value(secrets, secret_name: str) -> str | None:
    """
    Get a secret value from secrets with priority-based lookup.

    Args:
        secrets: Dictionary or JSON string containing plugin secrets
        secret_name: Name of the secret to retrieve

    Returns:
        Secret value as string, or None if not found

    Priority Order:
        1. Individual secrets (higher priority): secrets[secret_name]
        2. all_secrets JSON (fallback): JSON.parse(secrets["all_secrets"])[secret_name]
        3. None if neither contains valid value
    """
    try:
        log.info(f"PDMP-Secrets: Looking for '{secret_name}' in secrets")

        # If secrets is a string (JSON), parse it first
        if isinstance(secrets, str):
            log.info(f"PDMP-Secrets: Parsing JSON string: {secrets[:100]}...")
            secrets = json.loads(secrets)

        # Now secrets should be a dict
        if isinstance(secrets, dict):
            log.info(f"PDMP-Secrets: Available keys: {list(secrets.keys())}")

            # PRIORITY 1: Check individual secrets first (higher priority)
            if secret_name in secrets and secrets[secret_name]:
                value = str(secrets[secret_name])
                log.info(f"PDMP-Secrets: Found individual '{secret_name}' = '{value}'")
                return value
            else:
                log.info(
                    f"PDMP-Secrets: Individual '{secret_name}' not found or empty, checking all_secrets fallback"
                )

            # PRIORITY 2: Fallback to all_secrets JSON
            all_secrets_json = secrets.get("all_secrets")
            if all_secrets_json:
                log.info(
                    f"PDMP-Secrets: Found all_secrets field with {len(all_secrets_json)} characters"
                )
                try:
                    all_secrets = json.loads(all_secrets_json)
                    log.info(f"PDMP-Secrets: Parsed all_secrets keys: {list(all_secrets.keys())}")
                    if (
                        isinstance(all_secrets, dict)
                        and secret_name in all_secrets
                        and all_secrets[secret_name]
                    ):
                        value = str(all_secrets[secret_name])
                        log.info(f"PDMP-Secrets: Found in all_secrets '{secret_name}' = '{value}'")
                        return value
                    else:
                        log.warning(
                            f"PDMP-Secrets: '{secret_name}' not found or empty in all_secrets keys: {list(all_secrets.keys())}"
                        )
                except json.JSONDecodeError as e:
                    log.error(f"PDMP-Secrets: Failed to parse all_secrets JSON: {e}")
            else:
                log.warning("PDMP-Secrets: No all_secrets field found or it's empty")

            # Neither individual nor all_secrets contains the secret
            log.error(
                f"PDMP-Secrets: '{secret_name}' not found in either individual secrets or all_secrets"
            )
        else:
            log.warning("PDMP-Secrets: Secrets is not a dict after parsing")

        return None

    except (json.JSONDecodeError, TypeError, AttributeError) as e:
        log.error(f"PDMP-Secrets: Error retrieving secret {secret_name}: {e}")
        return None


def get_required_secret(secrets, secret_name: str) -> str:
    """
    Get a required secret value from secrets (can be dict or JSON string).

    Args:
        secrets: Dictionary or JSON string containing plugin secrets
        secret_name: Name of the secret to retrieve

    Returns:
        Secret value as string

    Raises:
        ValueError: If secret is not found
    """
    secret_value = get_secret_value(secrets, secret_name)
    if secret_value is None:
        raise ValueError(f"Secret '{secret_name}' is required but not found")
    return secret_value


def get_secrets_for_environment(secrets, use_test_env: bool = False) -> dict[str, str]:
    """
    Get all secrets for a specific environment (production or test).

    Args:
        secrets: Dictionary or JSON string containing plugin secrets
        use_test_env: If True, returns test environment secrets, otherwise production

    Returns:
        Dictionary containing environment-specific secrets

    Raises:
        ValueError: If required secrets are missing
    """
    env_label = "test" if use_test_env else "production"
    log.info(f"PDMP-Secrets: Getting secrets for {env_label} environment")

    if use_test_env:
        url_key = "TEST_PDMP_API_URL"
        username_key = "TEST_PDMP_API_USERNAME"
        password_key = "TEST_PDMP_API_PASSWORD"
    else:
        url_key = "PDMP_API_URL"
        username_key = "PDMP_API_USERNAME"
        password_key = "PDMP_API_PASSWORD"

    try:
        env_secrets = {
            "url": get_required_secret(secrets, url_key),
            "username": get_required_secret(secrets, username_key),
            "password": get_required_secret(secrets, password_key),
        }

        log.info(f"PDMP-Secrets: Successfully retrieved {env_label} environment secrets")
        return env_secrets

    except ValueError as e:
        log.error(f"PDMP-Secrets: Missing required secrets for {env_label} environment: {e}")
        raise


def validate_secrets_configuration(secrets) -> dict[str, Any]:
    """
    Validate secrets configuration and return status information.

    Args:
        secrets: Dictionary or JSON string containing plugin secrets

    Returns:
        Dictionary with validation results including:
        - has_individual_secrets: Boolean indicating if individual secrets are present
        - has_all_secrets: Boolean indicating if all_secrets JSON is present
        - all_secrets_valid: Boolean indicating if all_secrets JSON is valid
        - missing_secrets: List of missing required secrets
        - available_secrets: List of available secrets
    """
    result = {
        "has_individual_secrets": False,
        "has_all_secrets": False,
        "all_secrets_valid": False,
        "missing_secrets": [],
        "available_secrets": [],
    }

    # Parse secrets if it's a JSON string
    try:
        if isinstance(secrets, str):
            secrets = json.loads(secrets)
    except json.JSONDecodeError:
        log.error("PDMP-Secrets: Invalid JSON in secrets")
        return result

    # Check for individual secrets
    individual_secrets = [
        "PDMP_API_URL",
        "PDMP_API_USERNAME",
        "PDMP_API_PASSWORD",
        "TEST_PDMP_API_URL",
        "TEST_PDMP_API_USERNAME",
        "TEST_PDMP_API_PASSWORD",
    ]

    if isinstance(secrets, dict):
        available_individual = [
            secret for secret in individual_secrets if secret in secrets and secrets[secret]
        ]
        result["has_individual_secrets"] = len(available_individual) > 0
        result["available_secrets"].extend(available_individual)

    # Check for missing required secrets
    for secret in individual_secrets:
        if not get_secret_value(secrets, secret):
            result["missing_secrets"].append(secret)

    return result
