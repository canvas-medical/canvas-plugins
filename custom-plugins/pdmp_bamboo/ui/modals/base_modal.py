"""
Base Modal Component

Provides base functionality for all modal components.
"""

from typing import Dict, Any, List, Optional
from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from logger import log


class BaseModal:
    """Base class for all modal components."""
    
    def __init__(self):
        self.default_styles = {
            "container": "padding: 20px; font-family: Arial, sans-serif; max-width: 800px;",
            "title": "margin-top: 0; color: #333;",
            "section": "margin: 15px 0; padding: 15px; border-radius: 4px;",
            "success": "background-color: #e8f5e8; border: 1px solid #c8e6c9;",
            "warning": "background-color: #fff3cd; border: 1px solid #ffeaa7;",
            "error": "background-color: #ffebee; border: 1px solid #ffcdd2;",
            "info": "background-color: #e3f2fd; border: 1px solid #bbdefb;",
            "neutral": "background-color: #f5f5f5; border: 1px solid #dee2e6;"
        }
    
    def create_modal(self, title: str, content: str, target_type: str = "DEFAULT_MODAL") -> Effect:
        """
        Create a modal effect with the given title and content.
        
        Args:
            title: Modal title
            content: Modal content HTML
            target_type: Target type for the modal
            
        Returns:
            LaunchModalEffect
        """
        log.info(f"BaseModal: Creating modal with title: {title}")
        
        target_enum = getattr(LaunchModalEffect.TargetType, target_type, LaunchModalEffect.TargetType.DEFAULT_MODAL)
        
        return LaunchModalEffect(
            content=content,
            target=target_enum,
            title=title
        ).apply()
    
    def create_section(self, content: str, style_type: str = "neutral") -> str:
        """
        Create a styled section with the given content.
        
        Args:
            content: Section content
            style_type: Style type (success, warning, error, info, neutral)
            
        Returns:
            Styled HTML section
        """
        style = self.default_styles.get(style_type, self.default_styles["neutral"])
        return f'<div style="{self.default_styles["section"]} {style}">{content}</div>'
    
    def create_title(self, text: str, level: int = 3, color: str = "#333") -> str:
        """
        Create a styled title.
        
        Args:
            text: Title text
            level: Heading level (1-6)
            color: Title color
            
        Returns:
            Styled HTML title
        """
        return f'<h{level} style="{self.default_styles["title"]} color: {color};">{text}</h{level}>'
    
    def create_info_box(self, title: str, items: List[str], icon: str = "ℹ️") -> str:
        """
        Create an information box with a list of items.
        
        Args:
            title: Box title
            items: List of items to display
            icon: Icon to display
            
        Returns:
            Styled HTML information box
        """
        items_html = ""
        for item in items:
            items_html += f"<li>{item}</li>\n"
        
        return f"""
        <div style="{self.default_styles["section"]} {self.default_styles["info"]}">
            <h4 style="margin-top: 0; color: #1976d2;">{icon} {title}</h4>
            <ul style="color: #1976d2; margin: 10px 0; padding-left: 20px;">
                {items_html}
            </ul>
        </div>
        """
    
    def create_error_box(self, title: str, errors: List[str], icon: str = "❌") -> str:
        """
        Create an error box with a list of errors.
        
        Args:
            title: Box title
            errors: List of errors to display
            icon: Icon to display
            
        Returns:
            Styled HTML error box
        """
        errors_html = ""
        for error in errors:
            errors_html += f"<li>{error}</li>\n"
        
        return f"""
        <div style="{self.default_styles["section"]} {self.default_styles["error"]}">
            <h4 style="margin-top: 0; color: #d32f2f;">{icon} {title}</h4>
            <ul style="color: #d32f2f; margin: 10px 0; padding-left: 20px;">
                {errors_html}
            </ul>
        </div>
        """
