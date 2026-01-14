from datetime import datetime
from hmac import compare_digest

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.simple_api import Response, JSONResponse
from canvas_sdk.handlers.simple_api import SimpleAPI, APIKeyCredentials, api
from logger import log
from staff_spy.models.biography import Biography
from staff_spy.models.proxy import StaffProxy
from staff_spy.models.specialty import StaffSpecialty


class MyAPI(SimpleAPI):
    PREFIX = "/profile"

    def authenticate(self, credentials: APIKeyCredentials) -> bool:
        provided_api_key = credentials.key
        api_key = self.secrets["my-api-key"]

        return compare_digest(provided_api_key.encode(), api_key.encode())


    @api.get("/db/<staff_id>")
    def get_single_profile_db(self) -> list[Response | Effect]:
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
            "years_of_experience": datetime.today().year - staff.biography.practicing_since if staff.biography.practicing_since else 0,
            "accepting_patients": staff.get_attribute("accepting_patients")
        }

        return [JSONResponse(profile)]

    @api.get("/api/<staff_id>")
    def get_single_profile_api(self) -> list[Response | Effect]:
        staff_id = self.request.path_params["staff_id"]
        from canvas_sdk.utils import Http

        http = Http()
        response = http.get("http://localhost:8000/plugin-io/api/staff_plus/profile/v2/dbf184ad28a1408bbed184fc8fd2b029",
                 headers={"Authorization": f"f2464a67e6fa9839579189a8c1c781e9"})
        return [JSONResponse(response.json())]
