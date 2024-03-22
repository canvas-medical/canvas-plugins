from enum import Enum


class BannerAlertPlacement(Enum):
    """Where the BannerAlert should appear in the Canvas UI."""

    CHART = "chart"
    TIMELINE = "timeline"
    APPOINTMENT_CARD = "appointment_card"
    SCHEDULING_CARD = "scheduling_card"
    PROFILE = "profile"


class BannerAlertIntent(Enum):
    """The intent that should be conveyed in the BannerAlert."""

    INFO = "info"
    WARNING = "warning"
    ALERT = "alert"
