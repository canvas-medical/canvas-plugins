from datetime import UTC, datetime, timedelta
from http import HTTPStatus

import requests

from canvas_sdk.caching.plugins import get_cache
from canvas_sdk.commands import MedicationStatementCommand
from canvas_sdk.commands.constants import CodeSystems, Coding
from canvas_sdk.effects import Effect
from canvas_sdk.effects.patient import CreatePatientExternalIdentifier
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import SimpleAPI, StaffSessionAuthMixin, api
from canvas_sdk.v1.data import Note, Patient, Staff
from canvas_sdk.v1.data.common import ContactPointSystem
from canvas_sdk.v1.data.patient import SexAtBirth
from logger import log


def is_expired(token: dict) -> bool:
    """Check if the current access token is expired."""
    expires_in = token["expires_in"]
    created_at = token["created_at"]

    return datetime.now(UTC) > (datetime.fromisoformat(created_at) + timedelta(seconds=expires_in))


def get_patient_data(patient: Patient) -> dict:
    """Helper method to extract patient data for Fullscript API."""
    email = patient.telecom.filter(system=ContactPointSystem.EMAIL).first()
    email = email.value if email else ""

    phone_number = patient.telecom.filter(system=ContactPointSystem.PHONE).first()
    phone_number = f"+1{phone_number.value}" if phone_number else ""

    gender = (
        "male"
        if patient.sex_at_birth == SexAtBirth.MALE
        else ("female" if patient.sex_at_birth == SexAtBirth.FEMALE else "x")
    )

    log.info(f"!! Patient name {patient.first_name} {patient.last_name}")
    log.info(f"!! Patient email {email}")
    log.info(f"!! Patient phone {phone_number}")
    log.info(f"!! Patient gender {gender}")

    return {
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "email": email,
        "date_of_birth": patient.birth_date.isoformat() if patient.birth_date else None,
        "gender": gender,
        "mobile_number": phone_number,
    }


class FullscriptAPI(StaffSessionAuthMixin, SimpleAPI):
    """API endpoints for Fullscript integration."""

    PREFIX = "/app"

    FULLSCRIPT_TOKEN_URL = "https://api-us-snd.fullscript.io/api/oauth/token"

    @staticmethod
    def get_valid_access_token(user_id: str, client_id: str, client_secret: str) -> dict:
        """
        Helper method to get a valid access token for a user.
        Handles token refresh if the cached token is expired.
        """
        cache = get_cache()
        cached_token = cache.get(user_id)

        log.info(f"!! Getting valid access token for user {user_id}")

        if not cached_token:
            log.info("!! No cached token found")
            return {"success": False, "error": "No cached token found"}

        if not is_expired(cached_token):
            # Token is still valid
            log.info("!! Token is still valid")
            return {"success": True, "access_token": cached_token.get("access_token")}

        # Token is expired, refresh it
        log.info("!! Token expired, refreshing")
        refresh_token = cached_token.get("refresh_token")

        try:
            response = requests.post(
                FullscriptAPI.FULLSCRIPT_TOKEN_URL,
                headers={"Content-Type": "application/json"},
                json={
                    "grant_type": "refresh_token",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "refresh_token": refresh_token,
                },
                timeout=10,
            )

            if response.status_code != 200:
                log.error(f"!! Token refresh failed: {response.status_code} - {response.text}")
                return {"success": False, "error": "Token refresh failed", "details": response.text}

            token_data = response.json()
            oauth_data = token_data["oauth"]

            # Update cache with new token
            cache.set(user_id, oauth_data)
            log.info("!! Token refreshed successfully")

            return {"success": True, "access_token": oauth_data.get("access_token")}

        except requests.RequestException as e:
            log.error(f"!! Token refresh error: {str(e)}")
            return {"success": False, "error": str(e)}

    # Exchange OAuth code for access token
    @api.post("/exchange-token")
    def exchange_token(self) -> list[Response | Effect]:
        """Exchange OAuth authorization code for access token."""
        user_id = Staff.objects.values_list("id", flat=True).get(
            id=self.request.headers["canvas-logged-in-user-id"]
        )
        cache = get_cache()

        try:
            body = self.request.json()
            auth_code = body.get("code")
            redirect_uri = body.get("redirect_uri")

            existing_token = cache.get(user_id)

            log.info(f"!! Existing token: {existing_token}")

            if existing_token:
                if is_expired(existing_token):
                    log.info("!! Expired token, refreshing access token")
                    # Refresh access token
                    response = requests.post(
                        self.FULLSCRIPT_TOKEN_URL,
                        headers={"Content-Type": "application/json"},
                        json={
                            "grant_type": "refresh_token",
                            "client_id": self.secrets["FULLSCRIPT_CLIENT_ID"],
                            "client_secret": self.secrets["FULLSCRIPT_CLIENT_SECRET"],
                            "refresh_token": existing_token["refresh_token"],
                            "redirect_uri": redirect_uri,
                        },
                        timeout=10,
                    )
                else:
                    log.info(f"!! Token valid, returning cached access token: {existing_token}")
                    access_token = existing_token["access_token"]

                    return [JSONResponse({"token": access_token}, status_code=HTTPStatus.OK)]
            else:
                log.info("!! No existing token, exchanging code for access token")
                # Exchange code for access token
                response = requests.post(
                    self.FULLSCRIPT_TOKEN_URL,
                    headers={"Content-Type": "application/json"},
                    json={
                        "grant_type": "authorization_code",
                        "client_id": self.secrets["FULLSCRIPT_CLIENT_ID"],
                        "client_secret": self.secrets["FULLSCRIPT_CLIENT_SECRET"],
                        "code": auth_code,
                        "redirect_uri": redirect_uri,
                    },
                    timeout=10,
                )

            if response.status_code != 200:
                log.error(f"!! Token exchange failed: {response.text}")
                return [
                    JSONResponse(
                        {"error": "Failed to exchange token", "details": response.text},
                        status_code=HTTPStatus(response.status_code),
                    )
                ]

            token_data = response.json()
            cache.set(user_id, token_data["oauth"])

            log.info("!! Token exchange successful")

            return [
                JSONResponse(
                    {"token": token_data.get("oauth", {}).get("access_token", None)},
                    status_code=HTTPStatus(response.status_code),
                )
            ]

        except requests.RequestException as e:
            log.error(f"Token exchange error: {str(e)}")
            return [
                JSONResponse(
                    {"error": str(e)},
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
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
                    JSONResponse(
                        {"error": "Missing access token"},
                        status_code=HTTPStatus.BAD_REQUEST,
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
                    JSONResponse(
                        {"error": "Failed to create session grant", "details": response.text},
                        status_code=HTTPStatus(response.status_code),
                    )
                ]

            data = response.json()
            log.info("!! Session grant created successfully")

            return [
                JSONResponse(
                    {"token": data.get("secret_token")},
                    status_code=HTTPStatus(response.status_code),
                )
            ]

        except requests.RequestException as e:
            log.error(f"!! Session grant error: {str(e)}")
            return [
                JSONResponse(
                    {"error": str(e)},
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
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
            fullscript_id = (
                patient.external_identifiers.filter(system="Fullscript")
                .values_list("value", flat=True)
                .last()
            )

            log.info(f"!! Patient {patient.id}")
            log.info(f"!! Fullscript id {fullscript_id}")

            if fullscript_id:
                # update existing patient
                self.update_patient(access_token, patient, fullscript_id)

                return [
                    JSONResponse(
                        {"id": fullscript_id},
                        status_code=HTTPStatus.OK,
                    )
                ]
            else:
                patient_data = get_patient_data(patient)

                response = requests.post(
                    "https://api-us-snd.fullscript.io/api/clinic/patients",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {access_token}",
                    },
                    json=patient_data,
                    timeout=10,
                )

                if response.status_code != 201:
                    log.error(f"!! Get or create patient failed: {response.text}")
                    return [
                        JSONResponse(
                            {
                                "error": "Failed to get or create patient",
                                "details": response.text,
                            },
                            status_code=HTTPStatus(response.status_code),
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
                    JSONResponse(
                        {"id": fullscript_patient_id},
                        status_code=HTTPStatus(response.status_code),
                    ),
                ]

        except requests.RequestException as e:
            log.error(f"!! Get or create patient error: {str(e)}")
            return [
                JSONResponse(
                    {"error": str(e)},
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                )
            ]

    # Handle treatment plan created event
    @api.post("/treatment-plan-created")
    def treatment_plan_created(self) -> list[Response]:
        """Handle treatment plan created event from Fullscript embed."""
        user_id = Staff.objects.values_list("id", flat=True).get(
            id=self.request.headers["canvas-logged-in-user-id"]
        )
        cache = get_cache()

        try:
            body = self.request.json()
            log.info(f"!! Treatment plan created event received: {body}")

            # Extract treatment plan items
            patient_id = body.get("patient_id", "")
            note_id = body.get("note_id", None)
            treatment_plan = body.get("treatment", {}).get("data", {}).get("treatmentPlan", {})

            recommendations = treatment_plan.get("recommendations", [])

            if not recommendations:
                log.info("!! No items found in treatment plan")
                return [
                    JSONResponse(
                        {"error": "No items in treatment plan"},
                        status_code=HTTPStatus.BAD_REQUEST,
                    )
                ]

            # Get cached access token for API requests
            cached_token = cache.get(user_id)

            log.info(f"!! Cached token: {cached_token}")

            if not cached_token:
                log.error("!! No cached access token found for user")
                return [
                    JSONResponse(
                        {"error": "User not authenticated with Fullscript"},
                        status_code=HTTPStatus.UNAUTHORIZED,
                    )
                ]

            access_token = cached_token.get("access_token")

            medications_list = []
            patient = Patient.objects.get(id=patient_id)

            if note_id:
                note_id = Note.objects.filter(dbid=note_id).values_list("id", flat=True).first()
                log.info(f"!! Note retrieved or created successfully: {note_id}")
            else:
                note_id = patient.notes.last().id if patient.notes else None
                log.info(f"!! Note retrieved or created successfully from patient: {note_id}")

            # TODO: should we create a new note if none exists?

            if not note_id:
                log.error(f"!! Missing note_id: {note_id}")
                return [
                    JSONResponse(
                        {"error": "Missing note"},
                        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    )
                ]

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

                log.info(f"!! Fetching product variant details for variant_id: {variant_data}")

                dosage = item.get("dosage", {})

                quantity = dosage.get("recommendedAmount", None)
                frequency = dosage.get("recommendedFrequency", None)
                duration = dosage.get("recommendedDuration", None)
                format = dosage.get("format", None)
                refill = item.get("refill", None)

                product_variant = variant_data.get("variant", None)

                if product_variant is None:
                    log.error(f"!! missing 'product variant': {variant_data}")
                    continue

                product_id = f"fullscript-{product_variant.get('id', '')}"
                product_display_name = product_variant.get("product", {}).get("name", "")

                log.info(f"!! Fetching product display name: {product_display_name}")

                sig = f"Dosage: {quantity}" if quantity is not None else ""
                if format is not None:
                    sig += f"\nFormat: {format}"
                if frequency is not None:
                    sig += f"\nFrequency: {frequency}"
                if duration is not None:
                    sig += f"\nDuration: {duration}"
                if refill is not None:
                    sig += f"\nRefill: {'Yes' if refill else 'No'}"

                coding = Coding(
                    system=CodeSystems.UNSTRUCTURED, code=product_id, display=product_display_name
                )
                medication_command = MedicationStatementCommand(
                    fdb_code=coding,
                    sig=sig,
                    note_uuid=str(note_id),
                )

                medications_list.append(medication_command.originate())

                log.info(f"!! Successfully processed variant {variant_id}")

            return [
                *medications_list,
                JSONResponse(
                    {"status": "ok"},
                    status_code=HTTPStatus.OK,
                ),
            ]

        except requests.RequestException as e:
            log.error(f"!! Error fetching product variant details: {str(e)}")
            return [
                JSONResponse(
                    {"error": f"Failed to fetch product details: {str(e)}"},
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                )
            ]
        except Exception as e:
            log.error(f"!! Unexpected error processing treatment plan: {str(e)}")
            return [
                JSONResponse(
                    {"error": str(e)},
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                )
            ]

    @staticmethod
    def create_treatment_plan(access_token: str, medications: list, patient_id: str) -> dict:
        """Create a Fullscript treatment plan using access token and treatment details."""
        log.info("!! Create treatment plan")

        patient = Patient.objects.get(id=patient_id)
        patient_fullscript_id = (
            patient.external_identifiers.filter(system="Fullscript")
            .values_list("value", flat=True)
            .last()
        )

        if not patient_fullscript_id:
            log.error("!! No Fullscript patient identifier found")
            return {"success": False, "error": "No Fullscript patient identifier found"}

        try:
            response = requests.post(
                f"https://api-us-snd.fullscript.io/api/clinic/patients/{patient_fullscript_id}/treatment_plans",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}",
                },
                json={"recommendations": medications},
                timeout=10,
            )

            if response.status_code != 201:
                log.error(f"!! Create treatment plan failed: {response.text}")
                return {
                    "success": False,
                    "error": "Failed to create treatment plan",
                    "details": response.text,
                }

            data = response.json()
            log.info("!! Treatment plan created successfully")

            return {"success": True, "treatment_plan_id": data.get("treatment_plan", {}).get("id")}

        except requests.RequestException as e:
            log.error(f"!! Create treatment plan error: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def create_treatment_checkout(access_token: str, treatment_plan_id: str) -> dict:
        """
        Helper method to create a Fullscript treatment checkout via API.
        """
        try:
            log.info(f"!! Creating Fullscript treatment checkout for plan {treatment_plan_id}")

            response = requests.post(
                f"https://api-us-snd.fullscript.io/api/clinic/treatment_plans/{treatment_plan_id}/in_office_checkout",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}",
                },
                timeout=10,
            )

            if response.status_code == 201:
                data = response.json()
                log.info("!! Treatment checkout created successfully")
                return {
                    "success": True,
                    "checkout_url": data.get("in_office_checkout", {}).get("url", ""),
                }
            else:
                log.error(
                    f"!! Fullscript treatment checkout creation failed: {response.status_code} - {response.text}"
                )
                return {
                    "success": False,
                    "error": "Failed to create treatment checkout",
                    "details": response.text,
                }

        except requests.RequestException as e:
            log.error(f"!! Error creating treatment checkout: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def update_patient(access_token: str, patient: Patient, fullscript_patient_id: str) -> dict:
        """
        Helper method to update a Fullscript patient via API.
        """
        try:
            log.info(f"!! Updating Fullscript patient {patient.first_name} {patient.last_name}")
            log.info(f"!! Fullscript id {fullscript_patient_id}")

            patient_data = get_patient_data(patient)

            response = requests.put(
                f"https://api-us-snd.fullscript.io/api/clinic/patients/{fullscript_patient_id}",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}",
                },
                json=patient_data,
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                log.info("!! Patient updated successfully")
                return {"success": True, "patient": data.get("patient", {})}
            else:
                log.error(
                    f"!! Fullscript patient update failed: {response.status_code} - {response.text}"
                )
                return {
                    "success": False,
                    "error": "Failed to update patient",
                    "details": response.text,
                }

        except requests.RequestException as e:
            log.error(f"!! Error updating patient: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def fetch_products(access_token: str, query: str | None, page_size: str | None) -> dict:
        """
        Helper method to fetch products from Fullscript catalog API.
        """
        try:
            log.info("!! Fetching Fullscript products:")

            response = requests.get(
                "https://api-us-snd.fullscript.io/api/catalog/search/products",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}",
                },
                params={
                    "query": query,
                    "page[size]": page_size or 20,
                },
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                products = data.get("products", [])
                log.info(f"!! Found {len(products)} Fullscript products")
                return {"success": True, "products": products}
            else:
                log.error(f"!! Fullscript search failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": "Failed to get products",
                    "details": response.text,
                }

        except requests.RequestException as e:
            log.error(f"!! Error fetching products: {str(e)}")
            return {"success": False, "error": str(e)}
