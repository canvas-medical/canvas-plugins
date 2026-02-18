from datetime import datetime
from hmac import compare_digest

from staff_spy.models.biography import Biography
from staff_spy.models.language import Language
from staff_spy.models.proxy import StaffProxy
from staff_spy.models.specialty import Specialty, StaffSpecialty

from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import APIKeyCredentials, SimpleAPI, api


class MyAPI(SimpleAPI):
    PREFIX = "/profile"

    def authenticate(self, credentials: APIKeyCredentials) -> bool:
        provided_api_key = credentials.key
        api_key = self.secrets["my-api-key"]

        return compare_digest(provided_api_key.encode(), api_key.encode())

    @api.get("/v1/<staff_id>")
    def get_single_profile_v1(self) -> list[Response | Effect]:
        staff_id = self.request.path_params["staff_id"]
        staff = StaffProxy.objects.get(id=staff_id)

        profile = {
            "first_name": staff.first_name,
            "last_name": staff.last_name,
            "biography": staff.get_attribute("biography"),
            "specialties": staff.get_attribute("specialties"),
            "languages": staff.get_attribute("languages"),
            "years_of_experience": datetime.today().year - staff.get_attribute("practicing_since"),
            "accepting_patient": staff.get_attribute("accepting_patients"),
        }

        return [JSONResponse(profile)]

    @api.get("/v2/<staff_id>")
    def get_single_profile_v2(self) -> list[Response | Effect]:
        staff_id = self.request.path_params["staff_id"]
        staff = StaffProxy.objects.with_only(attribute_names="accepting_patients").get(id=staff_id)
        staff_specialties = StaffSpecialty.objects.filter(staff=staff).prefetch_related("specialty")
        specialties = [s.specialty.name for s in staff_specialties.all()]
        languages = [l.name for l in staff.languages.all()]

        profile = {
            "first_name": staff.first_name,
            "last_name": staff.last_name,
            "biography": staff.biography.biography,
            "specialties": specialties,
            "languages": languages,
            "years_of_experience": datetime.today().year - staff.biography.practicing_since
            if staff.biography.practicing_since
            else 0,
            "accepting_patients": staff.get_attribute("accepting_patients"),
        }

        return [JSONResponse(profile)]

    @api.get("/api/<staff_id>")
    def get_single_profile_api(self) -> list[Response | Effect]:
        staff_id = self.request.path_params["staff_id"]
        from canvas_sdk.utils import Http

        http = Http()
        response = http.get(
            "http://localhost:8000/plugin-io/api/staff_plus/profile/v2/dbf184ad28a1408bbed184fc8fd2b029",
            headers={"Authorization": "f2464a67e6fa9839579189a8c1c781e9"},
        )
        return [JSONResponse(response.json())]

    @api.post("/v2/<staff_id>")
    def post_profile_v2(self):
        staff_id = self.request.path_params["staff_id"]
        json_body = self.request.json()
        staff = StaffProxy.objects.filter(id=staff_id).get()
        specialty_names = json_body.get("specialties")
        language_names = json_body.get("languages")
        practicing_since = json_body.get("practicing_since")
        accepting_patients = json_body.get("accepting_patients")

        staff.set_attribute("accepting_patients", accepting_patients)

        for l_name in language_names:
            Language.objects.get_or_create(name=l_name, staff=staff)

        specialties = []
        for name in specialty_names:
            specialty, created = Specialty.objects.get_or_create(name=name)
            specialties.append(specialty)

        # Clear existing associations and create new ones
        StaffSpecialty.objects.filter(staff=staff).delete()

        staff_specialties = [
            StaffSpecialty(staff=staff, specialty=specialty) for specialty in specialties
        ]
        StaffSpecialty.objects.bulk_create(objs=staff_specialties)

        biography_str = json_body.get("biography")
        if staff.biography is None:
            Biography.objects.create(
                staff=staff, biography=biography_str, practicing_since=practicing_since
            )
        else:
            staff.biography.biography = biography_str
            staff.biography.languages = "English"
            staff.biography.practicing_since = practicing_since
            staff.biography.save()

        staff.refresh_from_db()
        staff.biography.refresh_from_db()
        specialties = [s.specialty.name for s in staff_specialties]
        languages = [l.name for l in staff.languages.all()]
        profile = {
            "first_name": staff.first_name,
            "last_name": staff.last_name,
            "biography": staff.biography.biography,
            "specialties": specialties,
            "languages": languages,
            "years_of_experience": datetime.today().year - staff.biography.practicing_since
            if staff.biography.practicing_since
            else 0,
            "accepting_patients": staff.get_attribute("accepting_patients"),
        }

        return [JSONResponse(profile)]
