import json
from datetime import datetime, timezone, timedelta
from http import HTTPStatus

import requests

from canvas_sdk.effects import Effect
from canvas_sdk.effects.patient import CreatePatientExternalIdentifier
from canvas_sdk.effects.simple_api import HTMLResponse, Response
from canvas_sdk.handlers.simple_api import SimpleAPI, api, StaffSessionAuthMixin
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import Staff, Note, PatientExternalIdentifier, Patient
from canvas_sdk.commands import MedicationStatementCommand
from canvas_sdk.v1.data.coding import Coding
from logger import log
from canvas_sdk.caching.plugins import get_cache

class MyWebApp(StaffSessionAuthMixin, SimpleAPI):
    PREFIX = "/app"

    # Serve templated HTML
    @api.get("/fullscript-app")
    def index(self) -> list[Response | Effect]:
        # logged_in_user = Staff.objects.get(id=self.request.headers["canvas-logged-in-user-id"])

        log.info(f"Fullscript app requested")
        log.info(f"--------------------------------")

        log.info(f"query_string: {self.request.query_string}")

        query_params = dict(param.split('=', 1) for param in self.request.query_string.split('&') if '=' in param)

        log.info(f"params: {query_params}")

        context = {
            "oauthCode": query_params.get("code", ""),
            "patientKey": query_params.get("patient", ""),
        }

        log.info(f"context: {context}")

        return [
            HTMLResponse(
                render_to_string("static/index.html", context),
                status_code=HTTPStatus.OK,
            )
        ]

    # Serve the contents of a js file
    @api.get("/main.js")
    def get_main_js(self) -> list[Response | Effect]:
        return [
            Response(
                render_to_string("static/main.js").encode(),
                status_code=HTTPStatus.OK,
                content_type="text/javascript",
            )
        ]

    # Exchange OAuth code for access token
    @api.post("/exchange-token")
    def exchange_token(self) -> list[Response | Effect]:
        """Exchange OAuth authorization code for access token."""
        user_id = Staff.objects.values_list("id").get(id=self.request.headers["canvas-logged-in-user-id"])
        cache = get_cache()

        try:
            body = self.request.json()
            auth_code = body.get("code")
            redirect_uri = body.get("redirect_uri")

            existing_token = cache.get(user_id)

            log.info(f"!! Existing token: {existing_token}")

            if existing_token:
                expires_in = existing_token["expires_in"]
                created_at = existing_token["created_at"]

                is_expired = datetime.now(timezone.utc) > (datetime.fromisoformat(created_at) + timedelta(seconds=expires_in))

                if is_expired:
                    log.info("!! Expired token, refreshing access token")
                    # Refresh access token
                    response = requests.post(
                        self.FULLSCRIPT_TOKEN_URL,
                        headers={"Content-Type": "application/json"},
                        json={
                            "grant_type": "refresh_token",
                            "client_id": self.FULLSCRIPT_CLIENT_ID,
                            "client_secret": self.FULLSCRIPT_CLIENT_SECRET,
                            "refresh_token": existing_token["refresh_token"],
                            "redirect_uri": redirect_uri,
                        },
                        timeout=10,
                    )
                else:
                    log.info(f"!! Token valid, returning cached access token: {existing_token}")
                    access_token = existing_token["access_token"]

                    return [
                        Response(
                            json.dumps(access_token).encode(),
                            status_code=HTTPStatus.OK,
                            content_type="application/json",
                        )
                    ]
            else:
                log.info("!! No existing token, exchanging code for access token")
                # Exchange code for access token
                response = requests.post(
                    self.FULLSCRIPT_TOKEN_URL,
                    headers={"Content-Type": "application/json"},
                    json={
                        "grant_type": "authorization_code",
                        "client_id": self.FULLSCRIPT_CLIENT_ID,
                        "client_secret": self.FULLSCRIPT_CLIENT_SECRET,
                        "code": auth_code,
                        "redirect_uri": redirect_uri,
                    },
                    timeout=10,
                )

            if response.status_code != 200:
                log.error(f"!! Token exchange failed: {response.text}")
                return [
                    Response(
                        json.dumps(
                            {"error": "Failed to exchange token", "details": response.text}
                        ).encode(),
                        status_code=HTTPStatus.BAD_GATEWAY,
                        content_type="application/json",
                    )
                ]

            token_data = response.json()
            cache.set(user_id, token_data["oauth"])

            log.info(f"!! Token exchange successful")

            return [
                Response(
                    json.dumps(token_data.oauth.access_token).encode(),
                    status_code=HTTPStatus.OK,
                    content_type="application/json",
                )
            ]

        except requests.RequestException as e:
            log.error(f"Token exchange error: {str(e)}")
            return [
                Response(
                    json.dumps({"error": str(e)}).encode(),
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    content_type="application/json",
                )
            ]

    # Generate Fullscript session grant token using access token
    @api.post("/session-grant")
    def create_session_grant(self) -> list[Response | Effect]:
        """Create a Fullscript embeddable session grant using access token."""
        try:
            body = self.request.json()
            access_token = body.get("access_token")

            if not access_token:
                return [
                    Response(
                        json.dumps({"error": "Missing access token"}).encode(),
                        status_code=HTTPStatus.BAD_REQUEST,
                        content_type="application/json",
                    )
                ]

            log.info("!! Creating session grant with access token")

            response = requests.post(
                "https://api-us-snd.fullscript.io/api/clinic/embeddable/session_grants",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}",
                },
                timeout=10,
            )

            if response.status_code != 200:
                log.error(f"!! Session grant creation failed: {response.text}")
                return [
                    Response(
                        json.dumps({"error": "Failed to create session grant", "details": response.text}).encode(),
                        status_code=HTTPStatus.BAD_GATEWAY,
                        content_type="application/json",
                    )
                ]

            data = response.json()
            log.info("!! Session grant created successfully")

            return [
                Response(
                    json.dumps({"token": data.get("secret_token")}).encode(),
                    status_code=HTTPStatus.OK,
                    content_type="application/json",
                )
            ]

        except requests.RequestException as e:
            log.error(f"!! Session grant error: {str(e)}")
            return [
                Response(
                    json.dumps({"error": str(e)}).encode(),
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    content_type="application/json",
                )
            ]

    @api.post("/get-or-create-patient")
    def get_or_create_patient(self) -> list[Response | Effect]:
        """Get or create a Fullscript patient using access token and patient details."""
        log.info("!! Get or create patient")

        try:
            body = self.request.json()
            access_token = body.get("access_token")
            patient_id = body.get("patient_id", "")

            patient = Patient.objects.get(id=patient_id)
            fullscript_id = patient.external_identifiers.filter(system="Fullscript").values_list('value', flat=True).last()

            log.info(f"!! Patient {patient.id}")
            log.info(f"!! Fullscript id {fullscript_id}")

            if fullscript_id:
                return [
                    Response(
                        json.dumps({"id": fullscript_id}).encode(),
                        status_code=HTTPStatus.OK,
                        content_type="application/json",
                    )
                ]
            else:
                email = patient.telecom.filter(system="email").first().value if patient.telecom.filter(system="email").exists() else ""

                log.info(f"!! Patient email {email}")

                response = requests.post(
                    "https://api-us-snd.fullscript.io/api/clinic/patients",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {access_token}",
                    },
                    json={
                        "first_name": patient.first_name,
                        "last_name": patient.last_name,
                        "email": email,
                    },
                    timeout=10,
                )

                if response.status_code != 201:
                    log.error(f"!! Get or create patient failed: {response.text}")
                    return [
                        Response(
                            json.dumps({"error": "Failed to get or create patient", "details": response.text}).encode(),
                            status_code=HTTPStatus.BAD_GATEWAY,
                            content_type="application/json",
                        )
                    ]

                data = response.json()
                fullscript_patient_id = data["patient"]["id"]
                log.info("!! Patient retrieved or created successfully")

                patient_external_identifier = CreatePatientExternalIdentifier(
                    patient_id=patient.id,
                    system="Fullscript",
                    value=fullscript_patient_id,
                )


                return [
                    patient_external_identifier.create(),
                    Response(
                        json.dumps({"id": fullscript_patient_id }).encode(),
                        status_code=HTTPStatus.OK,
                        content_type="application/json",
                    )
                ]

        except requests.RequestException as e:
            log.error(f"!! Get or create patient error: {str(e)}")
            return [
                Response(
                    json.dumps({"error": str(e)}).encode(),
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    content_type="application/json",
                )
            ]

    # Handle treatment plan created event
    @api.post("/treatment-plan-created")
    def treatment_plan_created(self) -> list[Response | Effect]:
        """Handle treatment plan created event from Fullscript embed."""
        user_id = Staff.objects.values_list("id").get(id=self.request.headers["canvas-logged-in-user-id"])
        cache = get_cache()

        try:
            body = self.request.json()
            log.info(f"!! Treatment plan created event received: {body}")

            # Extract treatment plan items
            data = body.get("data", {})
            treatment_plan = data.get("treatmentPlan", {})
            recommendations = treatment_plan.get("recommendations", [])

            if not recommendations:
                log.info("!! No items found in treatment plan")
                return [
                    Response(
                        json.dumps({"error": "No items in treatment plan"}).encode(),
                        status_code=HTTPStatus.BAD_REQUEST,
                        content_type="application/json",
                    )
                ]

            # Get cached access token for API requests
            cached_token = cache.get(user_id)

            if not cached_token:
                log.error("!! No cached access token found for user")
                return [
                    Response(
                        json.dumps({"error": "User not authenticated with Fullscript"}).encode(),
                        status_code=HTTPStatus.UNAUTHORIZED,
                        content_type="application/json",
                    )
                ]

            access_token = cached_token.get("access_token")

            # Process each item in the treatment plan
            processed_items = []
            medications_list = []

            for item in recommendations:
                variant_id = item.get("variantId")

                if not variant_id:
                    log.error(f"!! Item missing variant_id: {item}")
                    continue

                log.info(f"!! Fetching product variant details for variant_id: {variant_id}")

                # Fetch product variant details from Fullscript API
                variant_response = requests.get(
                    f"https://api-us-snd.fullscript.io/api/catalog/variants/{variant_id}",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                    timeout=10,
                )

                if variant_response.status_code != 200:
                    log.error(f"!! Failed to fetch variant {variant_id}: {variant_response.text}")
                    continue

                variant_data = variant_response.json()

                # Combine treatment plan item with full product details
                processed_item = {
                    "variant_id": variant_id,
                    "refill": item.get("refill"),
                    "dosage": item.get("dosage").get("recommendedAmount"),
                    "frequency": item.get("dosage").get("recommendedFrequency"),
                    "format": item.get("dosage").get("format"),
                    "quantity": item.get("unitsToPurchase"),
                    "duration": item.get("dosage").get("recommendedDuration"),
                    "instructions": item.get("additionalInfo"),
                    "product_details": variant_data,
                }

                note_id = Note.objects.values_list("id", flat=True).last()

                coding = Coding(
                    system="https://fullscript.com/",
                    code=variant_data.get("sku", ""),
                    display=variant_data.get("product", {}).get("name", "")
                )

                medication_command = MedicationStatementCommand(
                    fdb_code=coding,
                    sig=f"{processed_item["instructions"]} Take {processed_item["dosage"]} {processed_item["format"]} {processed_item["frequency"]} for {processed_item["duration"]}.",
                    note_uuid=str(note_id),
                )

                medications_list.append(medication_command)

                processed_items.append(processed_item)
                log.info(f"!! Successfully processed variant {variant_id}")

            log.info(f"!! Treatment plan processing complete. Processed {len(processed_items)} items.")


            return [
                *[medication.originate() for medication in medications_list],
                Response(
                    status_code=HTTPStatus.OK,
                    content_type="application/json",
                )
            ]

        except requests.RequestException as e:
            log.error(f"!! Error fetching product variant details: {str(e)}")
            return [
                Response(
                    json.dumps({"error": f"Failed to fetch product details: {str(e)}"}).encode(),
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    content_type="application/json",
                )
            ]
        except Exception as e:
            log.error(f"!! Unexpected error processing treatment plan: {str(e)}")
            return [
                Response(
                    json.dumps({"error": str(e)}).encode(),
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    content_type="application/json",
                )
            ]
