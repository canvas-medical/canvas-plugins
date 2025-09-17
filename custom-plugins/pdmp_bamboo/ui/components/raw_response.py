"""
Raw Response Component

Displays the raw PDMP response for debugging purposes.
"""

from typing import Optional
from logger import log


class RawResponseComponent:
    """Component for displaying raw PDMP response."""
    
    def create_component(self, raw_response: str) -> Optional[str]:
        """
        Create raw response component.
        
        Args:
            raw_response: Raw XML response from PDMP API
            
        Returns:
            HTML string for raw response display, or None if no response
        """
        if not raw_response:
            return None
        
        log.info("RawResponseComponent: Creating raw response component")
        
        return f"""
        <div style="background-color: #e8f5e8; padding: 15px; border-radius: 4px; margin: 15px 0;">
            <h4>Raw PDMP Response:</h4>
            <details>
                <summary style="cursor: pointer; color: #1976d2;">Click to view raw XML response</summary>
                <pre style="background-color: white; padding: 10px; border-radius: 4px; overflow-x: auto; max-height: 300px; margin-top: 10px;">{raw_response}</pre>
            </details>
        </div>
        """
