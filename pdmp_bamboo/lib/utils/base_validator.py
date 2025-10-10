"""
Base Validator.

Abstract base class for all validators with common validation methods.
"""

from abc import ABC, abstractmethod


class BaseValidator(ABC):
    """Base validator with common validation methods."""

    @abstractmethod
    def validate(self, dto) -> list[str]:
        """
        Validate DTO and return list of errors.

        Args:
            dto: Data transfer object to validate

        Returns:
            List of error/warning/info messages
        """
        pass

    def _add_error(self, errors: list, message: str, level: str = "ERROR"):
        """
        Add error with consistent formatting.

        Args:
            errors: List to append error to
            message: Error message text
            level: Severity level (ERROR, WARNING, INFO)
        """
        prefix = {"ERROR": "[ERROR]", "WARNING": "[WARNING]", "INFO": "[INFO]"}
        errors.append(f"{prefix.get(level, '[ERROR]')} {message}")

    def _validate_required(self, value, field_name: str, errors: list):
        """
        Validate required field.

        Args:
            value: Field value to check
            field_name: Name of field for error message
            errors: List to append error to
        """
        if not value:
            self._add_error(errors, f"{field_name} is REQUIRED", "ERROR")

    def _validate_optional(self, value, field_name: str, errors: list):
        """
        Validate optional field (warning if missing).

        Args:
            value: Field value to check
            field_name: Name of field for warning message
            errors: List to append warning to
        """
        if not value:
            self._add_error(errors, f"{field_name} is missing", "WARNING")

    def _validate_info(self, condition: bool, message: str, errors: list):
        """
        Add informational message if condition is met.

        Args:
            condition: Condition to check
            message: Informational message
            errors: List to append info to
        """
        if condition:
            self._add_error(errors, message, "INFO")

