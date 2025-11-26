"""Tomosynthesis (3D Mammography) value set for CMS125v14."""

from canvas_sdk.value_set.value_set import ValueSet


class Tomography(ValueSet):
    """
    Tomosynthesis (3D Mammography) value set for CMS125v14.

    Per CMS125v14 measure specification, tomosynthesis can be used for
    primary breast cancer screening.
    """

    VALUE_SET_NAME = "CMS125v14 Tomography"

    # LOINC codes for digital breast tomosynthesis
    LOINC = {
        "36625-2",  # Mammography unilateral screening with tomosynthesis
        "36626-0",  # Mammography bilateral screening with tomosynthesis
        "46347-5",  # Mammography unilateral diagnostic with tomosynthesis
        "46348-3",  # Mammography bilateral diagnostic with tomosynthesis
        "36319-2",  # Tomosynthesis bilateral screening
        "37038-7",  # Tomosynthesis unilateral screening
        "37039-5",  # Tomosynthesis bilateral diagnostic
        "37040-3",  # Tomosynthesis unilateral diagnostic
    }

    # CPT codes for 3D mammography
    CPT = {
        "77063",  # Screening digital breast tomosynthesis, bilateral
    }

    # HCPCS codes
    HCPCS = {
        "G0279",  # Diagnostic digital breast tomosynthesis, unilateral or bilateral
    }


__exports__ = ("Tomography",)
