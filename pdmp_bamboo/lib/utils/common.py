"""
Common Utilities.

Shared helper functions used across PDMP components.
"""

from typing import Any


def safe_get_attr(obj: Any, attr_name: str, default: Any = None) -> Any:
    """
    Safely get attribute from object, returning default if not found.
    
    Args:
        obj: Object to get attribute from
        attr_name: Name of attribute
        default: Default value if attribute not found
        
    Returns:
        Attribute value or default
    """
    try:
        return getattr(obj, attr_name, default)
    except (AttributeError, TypeError):
        return default


def create_error_result(error_type: str, message: str, **extras: Any) -> dict[str, Any]:
    """
    Create standardized error result dictionary.
    
    Args:
        error_type: Type of error (e.g., 'validation', 'api', 'network')
        message: Error message
        **extras: Additional fields to include in result
        
    Returns:
        Standardized error result dictionary
    """
    return {
        "success": False,
        "error_type": error_type,
        "error_message": message,
        **extras
    }

