# [Chat: 2025-01-31] Separate test integration file for PDMP test button and API
"""
Test PDMP Integration - Button and API for testing with mock data

This module provides test functionality for the PDMP plugin using complete
mock REQUEST data that generates proper XML for BambooHealth testing.
Separated from main integration to keep production code clean.
"""

from typing import Dict, List, Any

from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.handlers.action_button import ActionButton
from canvas_sdk.handlers.simple_api import SimpleAPI, api, Credentials
from canvas_sdk.effects.simple_api import HTMLResponse, Response
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data.note import Note
from logger import log

from pdmp3.utils.xml import PMPGatewayXMLGenerator
from pdmp3.utils.auth import PMPGatewayAuth
from pdmp3.utils.simple_request import send_pdmp_request, send_report_request


class TestDataButton(ActionButton):
    """
    Test PDMP Button - Creates a test scenario with mock data
    """

    BUTTON_TITLE = "🧪 Test PDMP (Mock Data)"
    BUTTON_KEY = "test_pdmp_mock"
    BUTTON_LOCATION = ActionButton.ButtonLocation.NOTE_HEADER

    def visible(self) -> bool:
        return True

    def handle(self):
        """
        Handle the test button click by launching the test PDMP modal with mock data.
        """
        note_id: str = self.target
        try:
            note: Note = Note.objects.get(id=note_id)
            patient_id: str = str(note.patient_id)

            return [
                LaunchModalEffect(
                    url=f"/plugin-io/api/pdmp3/test?patient_id={patient_id}",
                    title="Test PDMP (Mock Data)",
                ).apply()
            ]
        except Note.DoesNotExist:
            log.error(f"PDMP3: Note with ID '{note_id}' not found.")
            return [
                LaunchModalEffect(
                    url=f"/plugin-io/api/pdmp3/test?patient_id=test-patient",
                    title="Test PDMP (Mock Data)",
                ).apply()
            ]


class TestDataAPI(SimpleAPI):
    """
    Test PDMP API - Handles mock data workflow for generating proper REQUEST XML
    """

    def authenticate(self, credentials: Credentials) -> bool:
        return True

    @api.get("/test")
    def get_test_modal(self) -> List[Response]:
        """
        Creates a test PDMP request using complete mock REQUEST data from bamboo_request.py
        This generates proper XML to send to BambooHealth for testing.
        """
        log.info("PDMP3: Starting test workflow with mock REQUEST data")

        # Complete mock REQUEST data that matches bamboo_request.py working values
        # This data is used to generate the XML REQUEST to send to BambooHealth
        mock_patient_data = {
            "id": "test-patient-123",
            "first_name": "John",
            "last_name": "Doe",
            "dob": "1985-03-15",
            "sex": "M",
            "address": {
                "street": "123 Main St",
                "city": "Test City",
                "state": "KS",
                "zip_code": "67203",
            },
        }

        mock_practitioner_data = {
            "full_name": "Test Provider",
            "first_name": "Test",
            "last_name": "Provider",
            "npi": "1212345671",
            "dea_number": "AB1234579",
            "role": "Physician",
        }

        mock_location_data = {
            "name": "Test Clinic",
            "state": "KS",
            "npi": "1234567890",
            "dea": "AB1234579",
            "street": "123 Test St",
            "city": "Test City",
            "zip_code": "67203",
        }

        # Generate XML REQUEST with mock data (this is what gets sent to BambooHealth)
        xml_payload = PMPGatewayXMLGenerator.generate_patient_request_xml(
            mock_patient_data, mock_practitioner_data, mock_location_data
        )

        log.info("PDMP3: Generated test XML REQUEST with complete mock data")

        # Make the actual API call to BambooHealth with the generated REQUEST XML
        error_message = None
        api_response = None

        # Get credentials for test API call - using defaults for testing
        username = self.secrets.get("pmp_username", "canvas-prep-1")
        password = self.secrets.get("pmp_password", "j;%KAIGPI!o0Az>iSu{6")
        api_url = self.secrets.get("pmp_api_url", "https://prep.pmpgateway.net/v5_1/patient")

        try:
            # Generate authentication headers
            headers = PMPGatewayAuth.generate_auth_headers(username, password)

            # Make the request to BambooHealth
            api_response = send_pdmp_request(api_url, xml_payload, headers)
            log.info(f"PDMP3: Test API request completed - Status: {api_response.get('status')}")

            # Parse RESPONSE if successful
            if api_response and api_response.get("status") in ["success", "mock_success"]:
                parsed_data = self._parse_patient_response(api_response.get("raw_response", ""))
                api_response["parsed_data"] = parsed_data

                # Make report requests if URLs are found in the RESPONSE
                if parsed_data.get("report_urls"):
                    log.info(
                        f"PDMP3: Found {len(parsed_data['report_urls'])} report URLs in test response"
                    )
                    report_responses = []

                    for report_url in parsed_data["report_urls"]:
                        try:
                            report_response = send_report_request(
                                report_url, headers, mock_practitioner_data, mock_location_data
                            )
                            report_responses.append(report_response)
                        except Exception as report_error:
                            log.error(f"PDMP3: Test report request failed: {report_error}")
                            report_responses.append(
                                {
                                    "status": "error",
                                    "error": str(report_error),
                                    "report_url": report_url,
                                }
                            )

                    api_response["report_responses"] = report_responses

        except Exception as e:
            error_message = f"Test API call failed: {str(e)}"
            log.error(f"PDMP3: Test exception: {e}")

        context = {
            "patient": mock_patient_data,
            "practitioner": mock_practitioner_data,
            "error_message": error_message,
            "validation_results": {
                "valid": True,
                "missing_fields": [],
            },  # Mock data is always valid
            "xml_payload": xml_payload,
            "api_response": api_response,
            "is_test_mode": True,
        }

        log.info("PDMP3: Rendering test modal with mock data results")
        return [HTMLResponse(render_to_string("templates/pdmp3_modal.html", context=context))]

    def _parse_patient_response(self, xml_response: str) -> Dict[str, Any]:
        """
        Parse patient RESPONSE XML using regex - duplicated to avoid instantiation issues.

        This parses the XML RESPONSE received back from BambooHealth after sending our REQUEST.
        """
        import re

        try:
            log.info("PDMP3: Parsing patient response XML with regex")

            parsed_data = {
                "report_urls": [],
                "narx_scores": [],
                "clinical_messages": [],
                "request_id": "",
                "report_expiration": "",
                "response_destinations": [],
                "disallowed_states": [],
            }

            # Extract request ID
            request_id_match = re.search(
                r"<(?:\w+:)?RequestId[^>]*>(.*?)</(?:\w+:)?RequestId>", xml_response, re.DOTALL
            )
            if request_id_match:
                parsed_data["request_id"] = request_id_match.group(1).strip()

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
                score_type_match = re.search(
                    r"<(?:\w+:)?ScoreType[^>]*>(.*?)</(?:\w+:)?ScoreType>", score_block, re.DOTALL
                )
                score_value_match = re.search(
                    r"<(?:\w+:)?ScoreValue[^>]*>(.*?)</(?:\w+:)?ScoreValue>", score_block, re.DOTALL
                )

                if score_type_match and score_value_match:
                    score_value = score_value_match.group(1).strip()
                    try:
                        score_int = int(score_value)
                    except ValueError:
                        score_int = 0
                        log.warning(f"PDMP3: Invalid score value '{score_value}', defaulting to 0")

                    parsed_data["narx_scores"].append(
                        {
                            "type": score_type_match.group(1).strip(),
                            "value": score_value,  # Keep original string
                            "value_int": score_int,  # Add integer version for template
                        }
                    )

                # Move past this match for next iteration
                remaining_text = remaining_text[score_match.end() :]

            # Extract clinical messages (only from NarxMessages section to avoid Disallowed messages)
            narx_messages_section = re.search(
                r"<(?:\w+:)?NarxMessages[^>]*>(.*?)</(?:\w+:)?NarxMessages>",
                xml_response,
                re.DOTALL,
            )
            if narx_messages_section:
                messages_section = narx_messages_section.group(1)
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
                    msg_type_match = re.search(
                        r"<(?:\w+:)?MessageType[^>]*>(.*?)</(?:\w+:)?MessageType>",
                        message_block,
                        re.DOTALL,
                    )
                    msg_text_match = re.search(
                        r"<(?:\w+:)?MessageText[^>]*>(.*?)</(?:\w+:)?MessageText>",
                        message_block,
                        re.DOTALL,
                    )
                    msg_severity_match = re.search(
                        r"<(?:\w+:)?MessageSeverity[^>]*>(.*?)</(?:\w+:)?MessageSeverity>",
                        message_block,
                        re.DOTALL,
                    )

                    parsed_data["clinical_messages"].append(
                        {
                            "type": msg_type_match.group(1).strip() if msg_type_match else "",
                            "text": msg_text_match.group(1).strip() if msg_text_match else "",
                            "severity": msg_severity_match.group(1).strip()
                            if msg_severity_match
                            else "INFO",
                        }
                    )

                    # Move past this match for next iteration
                    remaining_text = remaining_text[msg_match.end() :]

            # Extract report expiration
            expiration_match = re.search(
                r"<(?:\w+:)?ReportExpiration[^>]*>(.*?)</(?:\w+:)?ReportExpiration>",
                xml_response,
                re.DOTALL,
            )
            if expiration_match:
                parsed_data["report_expiration"] = expiration_match.group(1).strip()

            # Extract response destinations using search in a loop
            remaining_text = xml_response
            while True:
                pmp_match = re.search(
                    r"<(?:\w+:)?(?:Pmp|Destination)[^>]*>(.*?)</(?:\w+:)?(?:Pmp|Destination)>",
                    remaining_text,
                    re.DOTALL,
                )
                if not pmp_match:
                    break

                pmp = pmp_match.group(1).strip()
                if pmp:
                    parsed_data["response_destinations"].append(pmp)

                # Move past this match for next iteration
                remaining_text = remaining_text[pmp_match.end() :]

            # Extract disallowed states using search in a loop
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
                msg_match = re.search(
                    r"<(?:\w+:)?Message[^>]*>(.*?)</(?:\w+:)?Message>", disallowed_block, re.DOTALL
                )
                source_match = re.search(
                    r"<(?:\w+:)?Source[^>]*>(.*?)</(?:\w+:)?Source>", disallowed_block, re.DOTALL
                )
                details_match = re.search(
                    r"<(?:\w+:)?Details[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</(?:\w+:)?Details>",
                    disallowed_block,
                    re.DOTALL,
                )

                parsed_data["disallowed_states"].append(
                    {
                        "message": msg_match.group(1).strip() if msg_match else "",
                        "source": source_match.group(1).strip() if source_match else "",
                        "details": details_match.group(1).strip() if details_match else "",
                    }
                )

                # Move past this match for next iteration
                remaining_text = remaining_text[disallowed_match.end() :]

            log.info(
                f"PDMP3: Parsed response - {len(parsed_data['report_urls'])} URLs, "
                f"{len(parsed_data['narx_scores'])} scores, {len(parsed_data['clinical_messages'])} messages"
            )

            return parsed_data

        except Exception as e:
            log.error(f"PDMP3: Response parsing error: {e}")
            return {"error": f"Response parsing failed: {str(e)}"}
