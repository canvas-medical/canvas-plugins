"""
Simple HTML Error Display Utilities

This module provides simple HTML error display functionality for PDMP plugin.
All errors are displayed in a consistent, simple format as requested.
"""

from typing import List
from logger import log


def create_error_html(errors: List[str], title: str = "PDMP Request Errors") -> str:
    """
    Create simple HTML error display from list of error messages.

    Args:
        errors: List of error message strings
        title: Title for the error display

    Returns:
        HTML string with simple error display
    """
    if not errors:
        return create_simple_message_html("No errors to display", "✅", "#2e7d32")

    html = f"""
    <div style="padding: 20px; font-family: Arial, sans-serif; max-width: 600px;">
        <h2 style="color: #d32f2f; margin-top: 0;">❌ {title}</h2>
        <div style="background-color: #ffebee; padding: 15px; border-radius: 4px; margin: 15px 0; border: 1px solid #ffcdd2;">
            <h3 style="margin-top: 0; color: #c62828;">The following errors occurred:</h3>
            <ul style="color: #c62828; margin: 10px 0; padding-left: 20px;">
    """

    # Add each error as a list item
    for error in errors:
        html += f"                <li>{error}</li>\n"

    html += """
            </ul>
            <div style="margin-top: 15px; padding: 10px; background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px;">
                <strong>💡 What to do:</strong>
                <p style="margin: 5px 0;">Please ensure all required data is present in Canvas and try again. Contact your system administrator if these errors persist.</p>
            </div>
        </div>
    </div>
    """

    log.info(f"PDMP-ErrorHTML: Created error HTML ({len(html)} characters)")
    return html


def create_data_validation_html(missing_data: List[str], available_data: dict = None) -> str:
    """
    Create HTML for data validation errors with details about missing data.

    Args:
        missing_data: List of missing data field descriptions
        available_data: Dictionary of available data for context

    Returns:
        HTML string with data validation error display
    """
    log.info(
        f"PDMP-ErrorHTML: Creating data validation HTML with {len(missing_data)} missing items"
    )

    html = f"""
    <div style="padding: 20px; font-family: Arial, sans-serif; max-width: 700px;">
        <h2 style="color: #f57c00; margin-top: 0;">⚠️ PDMP Data Validation</h2>
        <p style="color: #666; margin-bottom: 20px;">The following data is missing or incomplete for the PDMP request:</p>
    """

    if missing_data:
        html += """
        <div style="background-color: #fff3cd; padding: 15px; border-radius: 4px; margin: 15px 0; border: 1px solid #ffeaa7;">
            <h3 style="margin-top: 0; color: #f57c00;">Missing Required Data:</h3>
            <ul style="color: #8b4513; margin: 10px 0; padding-left: 20px;">
        """

        for missing_item in missing_data:
            html += f"                <li>{missing_item}</li>\n"

        html += """
            </ul>
        </div>
        """

    # Show available data summary if provided
    if available_data:
        html += """
        <div style="background-color: #e8f5e8; padding: 15px; border-radius: 4px; margin: 15px 0; border: 1px solid #c8e6c9;">
            <h3 style="margin-top: 0; color: #2e7d32;">Available Data Summary:</h3>
            <ul style="color: #2e7d32; margin: 10px 0; padding-left: 20px;">
        """

        patient_data = available_data.get("patient", {})
        if patient_data:
            patient_name = (
                f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}"
            )
            html += f"                <li>Patient: {patient_name.strip() or 'Name not available'}</li>\n"

        practitioner_data = available_data.get("practitioner", {})
        if practitioner_data:
            practitioner_name = f"{practitioner_data.get('first_name', '')} {practitioner_data.get('last_name', '')}"
            html += f"                <li>Practitioner: {practitioner_name.strip() or 'Name not available'}</li>\n"

        organization_data = available_data.get("organization", {})
        if organization_data:
            org_name = organization_data.get("name", "Organization name not available")
            html += f"                <li>Organization: {org_name}</li>\n"

        html += """
            </ul>
        </div>
        """

    html += """
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; margin: 15px 0;">
            <h3 style="margin-top: 0; color: #666;">Next Steps:</h3>
            <ol style="color: #666; margin: 10px 0; padding-left: 20px;">
                <li>Complete missing patient information in Canvas EMR</li>
                <li>Ensure practitioner has required NPI or DEA numbers</li>
                <li>Verify organization and practice location data</li>
                <li>Try the PDMP request again</li>
            </ol>
        </div>
    </div>
    """

    return html


def create_simple_message_html(message: str, icon: str = "ℹ️", color: str = "#1976d2") -> str:
    """
    Create simple HTML for displaying a single message.

    Args:
        message: The message to display
        icon: Icon emoji to show
        color: CSS color for the message

    Returns:
        HTML string with simple message display
    """
    return f"""
    <div style="padding: 20px; font-family: Arial, sans-serif; max-width: 600px;">
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; text-align: center;">
            <div style="font-size: 24px; margin-bottom: 10px;">{icon}</div>
            <p style="color: {color}; margin: 0; font-size: 16px;">{message}</p>
        </div>
    </div>
    """
