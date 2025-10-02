"""
DTO Converter Utility

Utility functions for converting DTO objects to dictionaries.
Handles nested DTOs and complex data structures.
"""

from typing import Any, Dict, List, Union
from logger import log


def convert_dto_to_dict(dto: Any) -> Any:
    """
    Convert a DTO object to dictionary, handling nested DTOs recursively.
    
    Args:
        dto: DTO object or any other data type
        
    Returns:
        Dictionary representation of the DTO, or original value if not a DTO
    """
    if not dto or not hasattr(dto, '__dict__'):
        return dto
    
    # Handle lists of DTOs
    if isinstance(dto, list):
        return [convert_dto_to_dict(item) for item in dto]
    
    # Handle dictionaries
    if isinstance(dto, dict):
        return {key: convert_dto_to_dict(value) for key, value in dto.items()}
    
    # Convert DTO to dictionary
    dto_dict = {}
    for attr_name in dir(dto):
        if not attr_name.startswith('_') and not callable(getattr(dto, attr_name)):
            attr_value = getattr(dto, attr_name)
            
            # Recursively convert nested DTOs
            if attr_value and hasattr(attr_value, '__dict__') and not isinstance(attr_value, (str, int, float, bool)):
                dto_dict[attr_name] = convert_dto_to_dict(attr_value)
            else:
                dto_dict[attr_name] = attr_value
    
    return dto_dict


def convert_all_dtos_to_dicts(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert all DTO objects in a dictionary to dictionaries.
    
    Args:
        data: Dictionary containing DTO objects
        
    Returns:
        Dictionary with all DTOs converted to dictionaries
    """
    log.info("DTOConverter: Converting all DTOs to dictionaries")
    
    converted_data = {}
    for key, value in data.items():
        converted_data[key] = convert_dto_to_dict(value)
        log.info(f"DTOConverter: Converted {key} to dictionary")
    
    return converted_data
