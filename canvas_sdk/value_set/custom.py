from canvas_sdk.value_set.value_set import ValueSet


class Hcc005v1AnnualWellnessVisit(ValueSet):
    """Hcc005v1AnnualWellnessVisit."""

    VALUE_SET_NAME = "Annual Wellness Visit"

    HCPCS = {
        "G0438",
        "G0439",
        "G0402",
        "99387",
        "99397",
    }
