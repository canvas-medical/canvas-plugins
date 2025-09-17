"""
NarxCare Messages Component

Displays clinical alert messages from PDMP responses.
"""

from typing import Dict, Any, List, Optional
from logger import log


class NarxMessagesComponent:
    """Component for displaying clinical alert messages."""
    
    def create_component(self, parsed_data: Dict[str, Any]) -> Optional[str]:
        """
        Create clinical messages component.
        
        Args:
            parsed_data: Parsed PDMP response data
            
        Returns:
            HTML string for messages display, or None if no messages
        """
        if not parsed_data.get("parsed") or not parsed_data.get("narx_messages"):
            return None
        
        messages = parsed_data["narx_messages"]
        log.info(f"NarxMessagesComponent: Creating messages component with {len(messages)} messages")
        
        return self._build_messages_html(messages)
    
    def _build_messages_html(self, messages: List[Dict[str, Any]]) -> str:
        """Build HTML for displaying clinical messages."""
        messages_html = ""
        for message in messages:
            messages_html += self._build_message_item(message)
        
        return f"""
        <div style="background-color: #fff3cd; padding: 15px; border-radius: 4px; margin: 15px 0; border: 1px solid #ffeaa7;">
            <h4 style="margin-top: 0; color: #856404;">🚨 Clinical Alerts</h4>
            {messages_html}
        </div>
        """
    
    def _build_message_item(self, message: Dict[str, Any]) -> str:
        """Build HTML for a single message item."""
        return f"""
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 8px; margin: 3px 0; border-radius: 4px;">
            <span style="color: {message.get('severity_color', '#666')}; font-weight: bold;">{message.get('severity', 'Unknown')} Alert:</span> {message.get('text', 'No message text')}
        </div>
        """


