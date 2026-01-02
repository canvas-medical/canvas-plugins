from logger import log

log.info("Loading staff-plus models")

from staff_plus.models.biography import Biography
from staff_plus.models.proxy import StaffProxy
from staff_plus.models.specialty import Specialty, StaffSpecialty
