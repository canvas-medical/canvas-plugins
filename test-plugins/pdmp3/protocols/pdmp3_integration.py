"""
PDMP v3 - Main Orchestration File
"""

import json
from http import HTTPStatus
from typing import Dict, Any, Optional, List

from canvas_sdk.handlers.action_button import ActionButton
from canvas_sdk.handlers.simple_api import SimpleAPI, api, Credentials
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.effects.simple_api import HTMLResponse, Response
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data.note import Note
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.staff import Staff
from logger import log

from pdmp3.utils.auth import PMPGatewayAuth
from pdmp3.utils.data_extractor import PDMPDataExtractor
from pdmp3.utils.validators import PDMPDataValidator
from pdmp3.utils.xml import PMPGatewayXMLGenerator
from pdmp3.utils.simple_request import send_pdmp_request, send_report_request


class DataDisplayButton(ActionButton):
    BUTTON_TITLE, BUTTON_KEY, BUTTON_LOCATION = (
        "Show Info (PDMP3)",
        "show_info_pdmp3",
        ActionButton.ButtonLocation.NOTE_HEADER,
    )

    def visible(self) -> bool:
        return True

    def handle(self):
        """
        Handle the button click by launching the PDMP3 modal.

        For NOTE_HEADER buttons, `self.target` is the Note ID, not the Patient ID.
        We therefore fetch the Note to derive the correct Patient ID that the
        SimpleAPI endpoint needs.
        """
        note_id: str = self.target
        try:
            note: Note = Note.objects.get(id=note_id)
            patient_id: str = str(note.patient_id)
        except Note.DoesNotExist:  # pragma: no cover
            log.warning(f"PDMP3: Note with ID '{note_id}' not found – falling back to raw target.")
            patient_id = note_id  # Will likely fail validation later
        log.info(f"PDMP3: Launching modal for patient: {patient_id} (note: {note_id})")
        return [
            LaunchModalEffect(
                url=f"/plugin-io/api/pdmp3/?patient_id={patient_id}", title="Information"
            ).apply()
        ]


class InfoDisplayAPI(SimpleAPI):
    def authenticate(self, credentials: Credentials) -> bool:
        return True

    @api.get("/")
    def get_info_modal(self) -> List[Response]:
        patient_id = self.request.query_params.get("patient_id")
        practitioner_id = self.request.headers.get("canvas-logged-in-user-id")

        # 1. Get Data
        log.info(
            f"PDMP3: Extracting data for patient_id={patient_id}, practitioner_id={practitioner_id}"
        )
        patient_data = PDMPDataExtractor.get_patient_data(patient_id) if patient_id else None
        practitioner_data = (
            PDMPDataExtractor.get_staff_data(practitioner_id) if practitioner_id else None
        )

        log.debug(f"PDMP3: Patient data extracted: {bool(patient_data)} - {patient_data}")
        log.debug(
            f"PDMP3: Practitioner data extracted: {bool(practitioner_data)} - {practitioner_data}"
        )

        # Extract facility data from Canvas (pass patient data for state fallback)
        location_data = PDMPDataExtractor.get_facility_data(patient_data) or {}
        log.debug(f"PDMP3: Location data prepared: {location_data}")

        # 2. Validate Data
        error_message = None
        if not patient_data or not practitioner_data:
            error_message = "Could not retrieve patient or practitioner data."
            log.error(
                f"PDMP3: Data retrieval failed - patient_data: {bool(patient_data)}, practitioner_data: {bool(practitioner_data)}"
            )
        else:
            try:
                # [Chat: 2025-01-31] Fixed TypeError by creating missing validate_xml_data_complete method
                # and adding comprehensive logging to debug validation issues
                log.info(
                    f"PDMP3: Starting validation with PDMPDataValidator.validate_xml_data_complete"
                )
                log.debug(
                    f"PDMP3: Calling validation method: {PDMPDataValidator.validate_xml_data_complete}"
                )
                validation = PDMPDataValidator.validate_xml_data_complete(
                    patient_data, practitioner_data, location_data
                )
                log.info(f"PDMP3: Validation completed: {validation}")

                if not validation["valid"]:
                    error_message = "Missing required fields: " + ", ".join(
                        validation["missing_fields"]
                    )
                    log.warning(f"PDMP3: Validation failed - {error_message}")
                    # Continue anyway - we'll show the validation warnings to the user
                else:
                    log.info("PDMP3: All validation checks passed")
            except Exception as e:
                error_message = f"Validation error: {str(e)}"
                log.error(f"PDMP3: Exception during validation: {e}")

        # 3. Prepare for API Call (even if validation fails, to show the XML)
        xml_payload = PMPGatewayXMLGenerator.generate_patient_request_xml(
            patient_data or {}, practitioner_data or {}, location_data
        )

        # Log the generated XML for debugging
        log.info(f"PDMP3: Generated XML payload (first 500 chars): {xml_payload[:500]}")
        log.debug(f"PDMP3: Full XML payload: {xml_payload}")

        api_response = None
        api_call_error = None

        # 4. Always make the API Call - show validation warnings but proceed anyway
        # Use working credentials as fallback for now
        username_secret = self.secrets.get("pmp_gateway_username")
        password_secret = self.secrets.get("pmp_gateway_password")
        api_url_secret = self.secrets.get("pmp_gateway_api_url")

        log.debug(
            f"PDMP3: Raw secrets - username: '{username_secret}', password: '{password_secret}', api_url: '{api_url_secret}'"
        )

        username = username_secret or "canvas-prep-1"
        password = password_secret or "j;%KAIGPI!o0Az>iSu{6"
        api_url = api_url_secret or "https://prep.pmpgateway.net/v5_1/patient"

        log.info(
            f"PDMP3: Preparing API call - URL configured: {bool(api_url)}, Username configured: {bool(username)}"
        )

        if not api_url or not username or not password:
            api_call_error = "Missing required API configuration (URL, username, or password). Please configure the PDMP Gateway credentials in Canvas plugin settings."
            log.error(f"PDMP3: {api_call_error}")
        else:
            try:
                # Generate authentication headers
                headers = PMPGatewayAuth.generate_auth_headers(username, password)
                log.info("PDMP3: Authentication headers generated successfully")

                # Make the request
                api_response = send_pdmp_request(api_url, xml_payload, headers)
                log.info(f"PDMP3: API request completed - Status: {api_response.get('status')}")

                # Check for errors in response
                if api_response and api_response.get("status") == "error":
                    api_call_error = api_response.get("error")
                    log.warning(f"PDMP3: API response error: {api_call_error}")
                    # Log the XML that caused the error for debugging
                    log.error(f"PDMP3: XML that caused error: {xml_payload}")
                elif api_response and api_response.get("status") in ["success", "mock_success"]:
                    log.info("PDMP3: API request successful")

                    # Parse response and extract report URLs
                    parsed_data = self._parse_patient_response(api_response.get("raw_response", ""))
                    api_response["parsed_data"] = parsed_data

                    # Make report requests if URLs are found
                    if parsed_data.get("report_urls"):
                        log.info(f"PDMP3: Found {len(parsed_data['report_urls'])} report URLs")
                        report_responses = []

                        for report_url in parsed_data["report_urls"]:
                            try:
                                log.info(f"PDMP3: Requesting report from {report_url[:50]}...")
                                report_response = send_report_request(
                                    report_url, headers, practitioner_data or {}, location_data
                                )
                                report_responses.append(report_response)
                                log.info(
                                    f"PDMP3: Report request completed - Status: {report_response.get('status')}"
                                )
                            except Exception as report_error:
                                log.error(f"PDMP3: Report request failed: {report_error}")
                                report_responses.append(
                                    {
                                        "status": "error",
                                        "error": str(report_error),
                                        "report_url": report_url,
                                    }
                                )

                        api_response["report_responses"] = report_responses

            except Exception as e:
                api_call_error = f"API call failed: {str(e)}"
                log.error(f"PDMP3: Exception during API call: {e}")

        # Prepare validation results for template
        validation_for_template = None
        try:
            validation_for_template = validation
        except NameError:
            validation_for_template = None

        context = {
            "patient": patient_data or {},
            "practitioner": practitioner_data or {},
            "error_message": error_message,
            "validation_results": validation_for_template,
            "xml_payload": xml_payload,
            "api_response": api_response,
            "api_call_error": api_call_error,
        }
        log.debug(f"PDMP3: Rendering context: {json.dumps(context, default=str)[:1000]}")

        return [HTMLResponse(render_to_string("templates/pdmp3_modal.html", context=context))]

    def _parse_patient_response(self, xml_response: str) -> Dict[str, Any]:
        """
        Parses the PatientResponse XML to extract structured data using regex (Canvas-compatible).
        Uses re.search() instead of re.findall() which is blocked by Canvas.
        """
        import re

        try:
            log.info("PDMP3: Parsing patient response XML with regex (search-based)")

            parsed_data = {
                "report_urls": [],
                "narx_scores": [],
                "clinical_messages": [],
                "request_id": "",
                "report_expiration": "",
                "response_destinations": [],
                "disallowed_states": [],
                "errors": [],
            }

            # Extract request ID
            request_id_match = re.search(
                r"<(?:\w+:)?RequestId[^>]*>(.*?)</(?:\w+:)?RequestId>", xml_response, re.DOTALL
            )
            if request_id_match:
                parsed_data["request_id"] = request_id_match.group(1).strip()

            # Extract errors (high priority)
            error_match = re.search(
                r"<(?:\w+:)?Error[^>]*>(.*?)</(?:\w+:)?Error>", xml_response, re.DOTALL
            )
            if error_match:
                error_section = error_match.group(1)

                # Extract error message
                msg_match = re.search(
                    r"<(?:\w+:)?Message[^>]*>(.*?)</(?:\w+:)?Message>", error_section, re.DOTALL
                )
                error_msg = msg_match.group(1).strip() if msg_match else "Unknown error"

                # Extract error source
                src_match = re.search(
                    r"<(?:\w+:)?Source[^>]*>(.*?)</(?:\w+:)?Source>", error_section, re.DOTALL
                )
                error_source = src_match.group(1).strip() if src_match else "UNKNOWN"

                parsed_data["errors"].append({"message": error_msg, "source": error_source})

            # Only extract data elements if no errors found
            if not parsed_data["errors"]:
                # Extract report URLs using search in a loop (since findall is blocked)
                remaining_text = xml_response
                while True:
                    url_match = re.search(
                        r"<(?:\w+:)?ViewableReport[^>]*>(.*?)</(?:\w+:)?ViewableReport>",
                        remaining_text,
                        re.DOTALL,
                    )
                    if not url_match:
                        break

                    url = url_match.group(1).strip()
                    if url:
                        parsed_data["report_urls"].append(url)

                    # Move past this match for next iteration
                    remaining_text = remaining_text[url_match.end() :]

                # Extract NARX scores using search in a loop
                remaining_text = xml_response
                while True:
                    score_match = re.search(
                        r"<(?:\w+:)?Score[^>]*>(.*?)</(?:\w+:)?Score>", remaining_text, re.DOTALL
                    )
                    if not score_match:
                        break

                    score_block = score_match.group(1)

                    # Extract score type and value from this block
                    type_match = re.search(
                        r"<(?:\w+:)?ScoreType[^>]*>(.*?)</(?:\w+:)?ScoreType>",
                        score_block,
                        re.DOTALL,
                    )
                    value_match = re.search(
                        r"<(?:\w+:)?ScoreValue[^>]*>(.*?)</(?:\w+:)?ScoreValue>",
                        score_block,
                        re.DOTALL,
                    )

                    if type_match and value_match:
                        score_value = value_match.group(1).strip()
                        try:
                            score_int = int(score_value)
                        except ValueError:
                            score_int = 0
                            log.warning(
                                f"PDMP3: Invalid score value '{score_value}', defaulting to 0"
                            )

                        parsed_data["narx_scores"].append(
                            {
                                "type": type_match.group(1).strip(),
                                "value": score_value,
                                "value_int": score_int,
                            }
                        )

                    # Move past this match for next iteration
                    remaining_text = remaining_text[score_match.end() :]

                # Extract clinical messages from NarxMessages section
                narx_messages_match = re.search(
                    r"<(?:\w+:)?NarxMessages[^>]*>(.*?)</(?:\w+:)?NarxMessages>",
                    xml_response,
                    re.DOTALL,
                )
                if narx_messages_match:
                    messages_section = narx_messages_match.group(1)
                    remaining_text = messages_section

                    while True:
                        msg_match = re.search(
                            r"<(?:\w+:)?Message[^>]*>(.*?)</(?:\w+:)?Message>",
                            remaining_text,
                            re.DOTALL,
                        )
                        if not msg_match:
                            break

                        message_block = msg_match.group(1)

                        # Extract message components
                        type_match = re.search(
                            r"<(?:\w+:)?MessageType[^>]*>(.*?)</(?:\w+:)?MessageType>",
                            message_block,
                            re.DOTALL,
                        )
                        text_match = re.search(
                            r"<(?:\w+:)?MessageText[^>]*>(.*?)</(?:\w+:)?MessageText>",
                            message_block,
                            re.DOTALL,
                        )
                        severity_match = re.search(
                            r"<(?:\w+:)?MessageSeverity[^>]*>(.*?)</(?:\w+:)?MessageSeverity>",
                            message_block,
                            re.DOTALL,
                        )

                        parsed_data["clinical_messages"].append(
                            {
                                "type": type_match.group(1).strip() if type_match else "",
                                "text": text_match.group(1).strip() if text_match else "",
                                "severity": severity_match.group(1).strip()
                                if severity_match
                                else "INFO",
                            }
                        )

                        # Move past this match for next iteration
                        remaining_text = remaining_text[msg_match.end() :]

                # Extract report expiration
                exp_match = re.search(
                    r"<(?:\w+:)?ReportExpiration[^>]*>(.*?)</(?:\w+:)?ReportExpiration>",
                    xml_response,
                    re.DOTALL,
                )
                if exp_match:
                    parsed_data["report_expiration"] = exp_match.group(1).strip()

                # Extract response destinations
                remaining_text = xml_response
                while True:
                    pmp_match = re.search(
                        r"<(?:\w+:)?Pmp[^>]*>(.*?)</(?:\w+:)?Pmp>", remaining_text, re.DOTALL
                    )
                    if not pmp_match:
                        break

                    pmp = pmp_match.group(1).strip()
                    if pmp:
                        parsed_data["response_destinations"].append(pmp)

                    # Move past this match for next iteration
                    remaining_text = remaining_text[pmp_match.end() :]

                # Extract disallowed states
                remaining_text = xml_response
                while True:
                    disallowed_match = re.search(
                        r"<(?:\w+:)?Disallowed[^>]*>(.*?)</(?:\w+:)?Disallowed>",
                        remaining_text,
                        re.DOTALL,
                    )
                    if not disallowed_match:
                        break

                    disallowed_block = disallowed_match.group(1)

                    # Extract disallowed components
                    msg_match = re.search(
                        r"<(?:\w+:)?Message[^>]*>(.*?)</(?:\w+:)?Message>",
                        disallowed_block,
                        re.DOTALL,
                    )
                    src_match = re.search(
                        r"<(?:\w+:)?Source[^>]*>(.*?)</(?:\w+:)?Source>",
                        disallowed_block,
                        re.DOTALL,
                    )
                    details_match = re.search(
                        r"<(?:\w+:)?Details[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</(?:\w+:)?Details>",
                        disallowed_block,
                        re.DOTALL,
                    )

                    parsed_data["disallowed_states"].append(
                        {
                            "message": msg_match.group(1).strip() if msg_match else "",
                            "source": src_match.group(1).strip() if src_match else "",
                            "details": details_match.group(1).strip() if details_match else "",
                        }
                    )

                    # Move past this match for next iteration
                    remaining_text = remaining_text[disallowed_match.end() :]

            log.info(
                f"PDMP3: Parsed response - {len(parsed_data['errors'])} errors, "
                f"{len(parsed_data['report_urls'])} URLs, {len(parsed_data['narx_scores'])} scores, "
                f"{len(parsed_data['clinical_messages'])} messages"
            )

            return parsed_data

        except Exception as e:
            log.error(f"PDMP3: Response parsing error: {e}")
            return {"error": f"Response parsing failed: {str(e)}"}
