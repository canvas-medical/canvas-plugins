"""
PDMP Workflow Handler Function

This module provides the main workflow function for handling PDMP requests
that can be used by both production and test protocol buttons.
"""

from typing import Any, Dict, List
from datetime import datetime
from uuid import uuid4
from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.v1.data.note import Note
from canvas_sdk.v1.data.questionnaire import Questionnaire
from canvas_sdk.v1.data.staff import Staff
from canvas_sdk.commands import StructuredAssessmentCommand
from logger import log


from pdmp_bamboo_simple.utils.data_extractor import extract_all_data_for_pdmp
from pdmp_bamboo_simple.utils.xml_mapper import create_pdmp_xml
from pdmp_bamboo_simple.utils.xml_request import (
    send_pdmp_request,
    create_pdmp_auth_headers,
    build_pdmp_api_url,
)
from pdmp_bamboo_simple.utils.error_html import create_error_html
from pdmp_bamboo_simple.utils.pdmp_parser import (
    parse_pdmp_response,
    generate_report_button_html,
    generate_scores_html,
    generate_messages_html,
)
from pdmp_bamboo_simple.utils.secrets_helper import get_secret_value


def handle_pdmp_request(
    target: str, context: dict, secrets: dict, event, use_test_env: bool = False
) -> List[Effect]:
    """
    Extract Canvas data and send PDMP request with environment flag.

    Args:
        target: Patient ID from button target
        context: Canvas context dict containing user info
        secrets: Plugin secrets dict
        event: Canvas event object
        use_test_env: If True, uses test credentials and no certificates

    Returns:
        List of Effects (assessment effects + modal effects)
    """
    env_label = "test" if use_test_env else "production"
    log.info(f"PDMP-Workflow: Starting PDMP request workflow for {env_label} environment")

    try:
        # Get patient ID and practitioner ID
        patient_id = target
        practitioner_id = None
        if isinstance(context, dict) and context.get("user"):
            practitioner_id = context["user"].get("id")

        # Validate secrets and build API URL based on environment
        try:
            url_key = "TEST_PDMP_API_URL" if use_test_env else "PDMP_API_URL"
            base_url = get_secret_value(secrets, url_key)
            if not base_url:
                return [
                    _create_error_modal(
                        "Configuration Error",
                        [
                            f"Secret '{url_key}' is required but not provided in plugin secrets or all_secrets JSON"
                        ],
                    )
                ]
            api_url = build_pdmp_api_url(base_url)
        except ValueError as e:
            return [_create_error_modal("Configuration Error", [str(e)])]

        # Extract Canvas data
        canvas_data, extraction_errors = extract_all_data_for_pdmp(patient_id, practitioner_id)

        if not canvas_data:
            return [_create_error_modal("Data Extraction Failed", extraction_errors)]

        # Create PDMP XML
        try:
            pdmp_xml = create_pdmp_xml(canvas_data)
        except Exception as e:
            return [_create_error_modal("XML Creation Error", [str(e)])]

        # Create auth headers
        try:
            headers = create_pdmp_auth_headers(secrets, use_test_env=use_test_env)
        except ValueError as e:
            return [_create_error_modal("Authentication Error", [str(e)])]

        # Send PDMP request
        result = send_pdmp_request(
            api_url=api_url,
            xml_content=pdmp_xml,
            headers=headers,
            secrets=secrets,
            timeout=60,
            use_test_env=use_test_env,
        )

        # Add context
        result["patient_id"] = patient_id
        result["extraction_errors"] = extraction_errors

        # Create structured assessment to document PDMP check
        assessment_effects = []
        try:
            if result.get("status") == "success":
                # Only create assessment if PDMP request was successful
                assessment_effects = _create_pdmp_assessment(patient_id, practitioner_id, event)
                log.info(
                    f"PDMP-Workflow: Created structured assessment effects: {len(assessment_effects)}"
                )
                result["assessment_created"] = len(assessment_effects) > 0
            else:
                result["assessment_created"] = False
                log.info("PDMP-Workflow: Skipping assessment creation due to failed PDMP request")
        except Exception as e:
            log.error(f"PDMP-Workflow: Error creating structured assessment: {str(e)}")
            result["assessment_created"] = False
            result["assessment_error"] = str(e)

        # Display result
        modal_effects = []
        if result.get("status") == "success":
            modal_effects = [_create_success_modal(result, use_test_env, patient_id, practitioner_id)]
        else:
            modal_effects = [_create_request_error_modal(result, use_test_env)]

        # Return both assessment effects and modal effects
        return assessment_effects + modal_effects

    except Exception as e:
        log.error(f"PDMP-Workflow: Unexpected error: {str(e)}")
        return [_create_error_modal("Unexpected Error", [str(e)])]


def _create_success_modal(result: Dict[str, Any], use_test_env: bool = False,
                          patient_id: str = None, practitioner_id: str = None, organization_id: str = None) -> Effect:
    """Create success modal with assessment status and parsed PDMP data."""

    # Parse PDMP response for enhanced display
    raw_response = result.get("raw_response", "")
    parsed_data = parse_pdmp_response(raw_response)

    # Assessment status HTML
    assessment_html = ""
    if result.get("assessment_created"):
        assessment_html = f"""
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 4px; margin: 15px 0; border: 1px solid #bbdefb;">
            <h4 style="color: #1976d2; margin-top: 0;">📋 Documentation Created</h4>
            <p style="margin: 5px 0; color: #666;">✅ Structured assessment added to note documenting PDMP check was performed</p>
        </div>
        """
    elif result.get("assessment_error"):
        assessment_html = f"""
        <div style="background-color: #fff3cd; padding: 15px; border-radius: 4px; margin: 15px 0; border: 1px solid #ffeaa7;">
            <h4 style="color: #f57c00; margin-top: 0;">⚠️ Documentation Warning</h4>
            <p style="margin: 5px 0; color: #8b4513;">Could not create structured assessment: {result.get("assessment_error", "Unknown error")}</p>
        </div>
        """

    # Generate scores HTML if available
    scores_html = ""
    if parsed_data.get("parsed") and parsed_data.get("narx_scores"):
        scores_html = f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 4px; margin: 15px 0; border: 1px solid #dee2e6;">
            <h4 style="margin-top: 0; color: #495057;">📊 NarxCare Risk Scores</h4>
            {generate_scores_html(parsed_data["narx_scores"])}
        </div>
        """

    # Generate messages HTML if available
    messages_html = ""
    if parsed_data.get("parsed") and parsed_data.get("narx_messages"):
        messages_html = f"""
        <div style="background-color: #fff3cd; padding: 15px; border-radius: 4px; margin: 15px 0; border: 1px solid #ffeaa7;">
            <h4 style="margin-top: 0; color: #856404;">🚨 Clinical Alerts</h4>
            {generate_messages_html(parsed_data["narx_messages"])}
        </div>
        """

    # Generate report button HTML
    report_button_html = ""
    if parsed_data.get("parsed") and parsed_data.get("report_url"):
        report_url = parsed_data.get("report_url", "")
        expiration_date = parsed_data.get("report_expiration", "Unknown")
        env = "test" if use_test_env else "prod"
        report_button_html = generate_report_button_html(
            report_url, 
            expiration_date, 
            env,
            patient_id=patient_id,
            practitioner_id=practitioner_id,
            organization_id=organization_id
        )

    html_content = f"""
    <div style="padding: 20px; font-family: Arial, sans-serif;">
        <h3 style="color: #2e7d32;">✅ PDMP Request Successful</h3>
        
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; margin: 15px 0;">
            <p><strong>Status Code:</strong> {result.get("status_code", "N/A")}</p>
            <p><strong>Patient ID:</strong> {result.get("patient_id", "N/A")}</p>
            <p><strong>Environment:</strong> {"Test Environment" if use_test_env else "Production Environment"}</p>
            {"<p><strong>Request ID:</strong> " + parsed_data.get("request_id", "N/A") + "</p>" if parsed_data.get("request_id") else ""}
        </div>
        
        {assessment_html}
        {scores_html}
        {messages_html}
        {report_button_html}
        
        <div style="background-color: #e8f5e8; padding: 15px; border-radius: 4px; margin: 15px 0;">
            <h4>Raw PDMP Response:</h4>
            <details>
                <summary style="cursor: pointer; color: #1976d2;">Click to view raw XML response</summary>
                <pre style="background-color: white; padding: 10px; border-radius: 4px; overflow-x: auto; max-height: 300px; margin-top: 10px;">{raw_response}</pre>
            </details>
        </div>
    </div>
    """

    modal_title = (
        "✅ PDMP Test Request Successful" if use_test_env else "✅ PDMP Request Successful"
    )
    return LaunchModalEffect(
        content=html_content,
        target=LaunchModalEffect.TargetType.DEFAULT_MODAL,
        title=modal_title,
    ).apply()


def _create_request_error_modal(result: Dict[str, Any], use_test_env: bool = False) -> Effect:
    """Create request error modal."""
    error_list = [
        f"PDMP API Error: {result.get('error', 'Unknown error')}",
        f"Status Code: {result.get('status_code', 'N/A')}",
    ]

    if result.get("extraction_errors"):
        error_list.extend(result["extraction_errors"])

    # Add response text if available
    log.info(f"PDMP-Workflow: result keys: {list(result.keys())}")
    log.info(f"PDMP-Workflow: raw_response present: {bool(result.get('raw_response'))}")
    if result.get("raw_response"):
        log.info(
            f"PDMP-Workflow: Adding raw_response to error list ({len(result['raw_response'])} characters)"
        )
        error_list.append("--- Server Response ---")
        error_list.append(result["raw_response"])
    else:
        log.info("PDMP-Workflow: No raw_response found in result")

    error_title = "PDMP Test Request Failed" if use_test_env else "PDMP Request Failed"
    modal_title = "❌ PDMP Test Request Failed" if use_test_env else "❌ PDMP Request Failed"
    html_content = create_error_html(error_list, error_title)

    # Return a single effect instead of a list
    return LaunchModalEffect(
        content=html_content,
        target=LaunchModalEffect.TargetType.DEFAULT_MODAL,
        title=modal_title,
    ).apply()


def _create_error_modal(title: str, errors: List[str]) -> Effect:
    """Create simple error modal."""
    html_content = create_error_html(errors, title)

    return LaunchModalEffect(
        content=html_content,
        target=LaunchModalEffect.TargetType.DEFAULT_MODAL,
        title=f"❌ {title}",
    ).apply()


def _create_pdmp_assessment(patient_id: str, practitioner_id: str, event) -> List[Effect]:
    """Create structured assessment to document PDMP check."""
    log.info("PDMP-Workflow: Creating structured assessment for PDMP check")

    try:
        # Get the note from context
        note_id = event.context.get("note_id")
        if not note_id:
            log.error("PDMP-Workflow: No note_id found in event context")
            return []

        note = Note.objects.get(dbid=note_id)
        log.info(f"PDMP-Workflow: Retrieved note UUID={note.id}")

        # Get the questionnaire
        questionnaire = Questionnaire.objects.get(name="PDMP Check", can_originate_in_charting=True)
        log.info(f"PDMP-Workflow: Found questionnaire: ID={questionnaire.id}")

        # Get practitioner info for "checked by" field
        reviewed_by = _get_practitioner_name(practitioner_id)
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Create structured assessment command
        assessment = StructuredAssessmentCommand(
            note_uuid=str(note.id),
            questionnaire_id=str(questionnaire.id),
            command_uuid=str(uuid4()),
        )
        log.info(
            f"PDMP-Workflow: Created StructuredAssessmentCommand UUID={assessment.command_uuid}"
        )

        # Populate responses
        log.info(f"PDMP-Workflow: Found {len(assessment.questions)} questions in assessment")
        for i, question in enumerate(assessment.questions):
            log.info(
                f"PDMP-Workflow: Question {i + 1}: label='{question.label}', name='{question.name}'"
            )
            try:
                if "PDMP checked by" in question.label:
                    question.add_response(text=reviewed_by)
                    log.info(f"PDMP-Workflow: Set 'PDMP checked by' = {reviewed_by}")
                elif "Date checked" in question.label:
                    question.add_response(text=current_date)
                    log.info(f"PDMP-Workflow: Set 'Date checked' = {current_date}")
                else:
                    log.warning(f"PDMP-Workflow: No match for question label: '{question.label}'")
            except Exception as e:
                log.error(f"PDMP-Workflow: Error setting response for '{question.label}': {e}")

        # Generate effects to finalize the assessment
        effects = [assessment.originate(), assessment.edit(), assessment.commit()]
        log.info("PDMP-Workflow: Generated structured assessment effects")
        return effects

    except Note.DoesNotExist:
        log.error(f"PDMP-Workflow: Note not found (dbid={note_id})")
        return []
    except Questionnaire.DoesNotExist:
        log.error("PDMP-Workflow: PDMP Check questionnaire not found")
        return []
    except Exception as e:
        log.error(f"PDMP-Workflow: Error creating structured assessment: {str(e)}")
        return []


def _get_practitioner_name(practitioner_id: str) -> str:
    """Get practitioner name for assessment."""
    try:
        staff = Staff.objects.get(id=practitioner_id)
        first_name = staff.first_name or ""
        last_name = staff.last_name or ""
        name = f"{first_name} {last_name}".strip()
        return name if name else f"User {practitioner_id}"
    except Exception as e:
        log.error(f"PDMP-Workflow: Error getting practitioner name: {str(e)}")
        return f"User {practitioner_id}"

