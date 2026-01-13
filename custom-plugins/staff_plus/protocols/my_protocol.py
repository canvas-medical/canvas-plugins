from datetime import datetime
from hmac import compare_digest

from logger import log
from staff_plus.models.language import Language
from staff_plus.models.biography import Biography
from staff_plus.models.proxy import StaffProxy
from staff_plus.models.specialty import Specialty, StaffSpecialty

from canvas_sdk.effects import Effect
from canvas_sdk.effects.custom_model.create import BulkCreate, Create, GetOrCreate
from canvas_sdk.effects.custom_model.delete import Delete
from canvas_sdk.effects.custom_model.update import Update
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import APIKeyCredentials, SimpleAPI, api
from canvas_sdk.protocols import BaseProtocol


class MyAPI(SimpleAPI):
    PREFIX = "/profile"

    def authenticate(self, credentials: APIKeyCredentials) -> bool:
        provided_api_key = credentials.key
        api_key = self.secrets["my-api-key"]

        return compare_digest(provided_api_key.encode(), api_key.encode())

    @api.post("/<staff_id>")
    def post_profile(self):
        staff_id = self.request.path_params["staff_id"]
        json_body = self.request.json()
        biography = json_body.get("biography")
        specialties = json_body.get("specialties")
        languages = json_body.get("languages")
        accepting_patients = json_body.get("accepting_patients")
        staff = StaffProxy.objects.get(id=staff_id)
        staff.set_attributes({
            "biography": biography,
            "specialties": specialties,
            "languages": languages,
            "practicing_since": json_body.get("practicing_since"),
            "accepting_patients": accepting_patients,
        })
        staff.refresh_from_db()
        return [
            JSONResponse(
                {
                    "first_name": staff.first_name,
                    "last_name": staff.last_name,
                    "biography": staff.get_attribute("biography"),
                    "specialties": staff.get_attribute("specialties"),
                    "languages": staff.get_attribute("languages"),
                    "years_of_experience": datetime.today().year - int(staff.get_attribute("practicing_since")),
                }
            )
        ]

    @api.get("/<staff_id>")
    def get_single_profile(self) -> list[Response | Effect]:
        staff_id = self.request.path_params["staff_id"]
        staff = StaffProxy.objects.get(id=staff_id)

        profile = {
            "first_name": staff.first_name,
            "last_name": staff.last_name,
            "biography": staff.get_attribute("biography"),
            "specialties": staff.get_attribute("specialties"),
            "languages": staff.get_attribute("languages"),
            "years_of_experience": datetime.today().year - staff.get_attribute("practicing_since"),
            "accepting_patient": staff.get_attribute("accepting_patients")
        }

        return [JSONResponse(profile)]

    @api.get("/search/")
    def search(self) -> list[Response | Effect]:
        query_params = self.request.query_params
        specialties_param = query_params.get("specialties")
        specialties = specialties_param.split(",")
        from django.db.models import Q

        # Create combined filter: name="specialties" AND (specialty1 OR specialty2 OR ...)
        specialty_filters = Q()
        for specialty in specialties:
            specialty_filters |= Q(custom_attributes__json_value__contains=specialty.strip())

        # Combine the name requirement with the OR conditions
        combined_filter = Q(custom_attributes__name="specialties") & specialty_filters

        matching_staff = (
            StaffProxy.objects
            .filter(combined_filter)
            .all()
        )
        info = {}
        for staff in matching_staff:
            info[staff.id] = {
                "first_name": staff.first_name,
                "last_name": staff.last_name,
                "biography": staff.get_attribute("biography"),
                "specialties": staff.get_attribute("specialties"),
                "languages": staff.get_attribute("languages"),
                "years_of_experience": datetime.today().year - staff.get_attribute("practicing_since"),
                "accepting_patients": staff.get_attribute("accepting_patients")
            }

        return [JSONResponse(info)]

    @api.get("/")
    def get_all_profiles(self) -> list[Response | Effect]:
        all_staff = StaffProxy.objects.all()
        info = {}
        for staff in all_staff:
            info[staff.id] = {
                "first_name": staff.first_name,
                "last_name": staff.last_name,
                "biography": staff.get_attribute("biography"),
                "specialties": staff.get_attribute("specialties"),
                "languages": staff.get_attribute("languages"),
                "years_of_experience": datetime.today().year - staff.get_attribute("practicing_since") if staff.get_attribute("practicing_since") else 0,
                "accepting_patient": staff.get_attribute("accepting_patients")
            }

        return [JSONResponse(info)]

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
            language, created = GetOrCreate(qs=Language.objects, name=l_name, staff=staff).apply()

        specialties = []
        for name in specialty_names:
            # specialty, created = Specialty.objects.get_or_create(name=name)
            specialty, created = GetOrCreate(qs=Specialty.objects, name=name).apply()
            specialties.append(specialty)

        # Clear existing associations and create new ones
        # StaffSpecialty.objects.filter(staff=staff).delete()
        qs = StaffSpecialty.objects.filter(staff=staff)
        Delete(qs=qs).apply()

        staff_specialties = [
            StaffSpecialty(staff=staff, specialty=specialty) for specialty in specialties
        ]
        # StaffSpecialty.objects.bulk_create(staff_specialties)
        BulkCreate(StaffSpecialty.objects, objs=staff_specialties).apply()

        biography_str = json_body.get("biography")
        if staff.biography is None:
            # Biography.objects.create(staff=staff, biography=biography_str)
            Create(qs=Biography.objects, staff=staff, biography=biography_str, language="English",
                   practicing_since=practicing_since).apply()
        else:
            # staff.biography.biography = biography_str
            # staff.biography.save()
            Update(Biography.objects.filter(staff=staff), biography=biography_str, language="English",
                   practicing_since=practicing_since).apply()

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
            "years_of_experience": datetime.today().year - staff.biography.practicing_since if staff.biography.practicing_since else 0,
            "accepting_patients": staff.get_attribute("accepting_patients"),
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
            "years_of_experience": datetime.today().year - staff.biography.practicing_since if staff.biography.practicing_since else 0,
            "accepting_patients": staff.get_attribute("accepting_patients")
        }

        return [JSONResponse(profile)]

    @api.get("/v2/")
    def get_all_profile_v2(self) -> list[Response | Effect]:
        all_staff = (
            StaffProxy.objects.with_only(attribute_names=["accepting_patients"])
            .prefetch_related("biography")
            .prefetch_related("staff_specialties__specialty")
            .all()
        )

        info = {}
        for staff in all_staff:
            info[staff.id] = {}
            info[staff.id]["first_name"] = staff.first_name
            info[staff.id]["last_name"] = staff.last_name
            info[staff.id]["biography"] = staff.biography.biography
            info[staff.id]["specialties"] = []
            info[staff.id]["languages"] = [l.name for l in staff.languages.all()]
            info[staff.id]["years_of_experience"] = datetime.today().year - staff.biography.practicing_since if staff.biography.practicing_since else 0
            info[staff.id]["accepting_patients"] = staff.get_attribute("accepting_patients")
            for staff_specialty in staff.staff_specialties.all():
                info[staff.id]["specialties"].append(staff_specialty.specialty.name)

        return [JSONResponse(info)]

    @api.get("/v2/search/")
    def search_v2(self) -> list[Response | Effect]:
        query_params = self.request.query_params
        specialties_param = query_params.get("specialties")
        specialties = specialties_param.split(",")

        staff_ids = StaffSpecialty.objects.filter(specialty__name__in=specialties).values_list(
            "staff_id", flat=True
        )

        matching_staff = (
            StaffProxy.objects
            .with_only(attribute_names=["accepting_patients"])
            .prefetch_related("biography")
            .prefetch_related("staff_specialties__specialty")
            .filter(dbid__in=staff_ids)
        )

        info = {}
        for staff in matching_staff:
            info[staff.id] = {}
            info[staff.id]["first_name"] = staff.first_name
            info[staff.id]["last_name"] = staff.last_name
            info[staff.id]["biography"] = staff.biography.biography
            info[staff.id]["specialties"] = []
            info[staff.id]["languages"] = [l.name for l in staff.languages.all()]
            info[staff.id]["years_of_experience"] = datetime.today().year - staff.biography.practicing_since if staff.biography.practicing_since else 0
            info[staff.id]["accepting_patients"] = staff.get_attribute("accepting_patients")
            for staff_specialty in staff.staff_specialties.all():
                info[staff.id]["specialties"].append(staff_specialty.specialty.name)

        return [JSONResponse(info)]


# Inherit from BaseProtocol to properly get registered for events
class Protocol(BaseProtocol):
    """You should put a helpful description of this protocol's behavior here."""
