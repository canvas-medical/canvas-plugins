"""The units an FDB medication is dispensed in, as the chart's Prescribe command offers them.

``find_clinical_codes`` (kind ``medication``) lists them with each candidate, and
``originate_prescribe_medication`` takes one back by its ``representative_ndc``, checked
against the same medication here, so a draft's dispense unit is always one its medication has.
"""

from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import quote

from canvas_sdk.utils.http import ontologies_http


class DispenseUnitsUnavailable(RuntimeError):
    """The ontologies service did not answer; the model is told to try again."""


def _unit_quantity(value: Any) -> str:
    """A unit's size as written plainly: ``"6"`` for FDB's ``"6.0000000"``."""
    try:
        return f"{Decimal(str(value)).normalize():f}"
    except (InvalidOperation, ValueError):
        return ""


def dispense_units(row: dict[str, Any]) -> list[dict[str, str]]:
    """A grouped medication's dispense units, each one a Prescribe command can take.

    A unit with no NDC cannot be named on a prescription, so it is left out.
    """
    return [
        {
            "representative_ndc": unit["representative_ndc"],
            "description": str(unit.get("clinical_quantity_description") or ""),
            "unit_quantity": _unit_quantity(unit.get("erx_quantity")),
            "ncpdp_quantity_qualifier_code": str(
                unit.get("erx_ncpdp_script_quantity_qualifier_code") or ""
            ),
            "ncpdp_quantity_qualifier_description": str(
                unit.get("erx_ncpdp_script_quantity_qualifier_description") or ""
            ),
        }
        for unit in row.get("clinical_quantities") or []
        if isinstance(unit, dict)
        and isinstance(unit.get("representative_ndc"), str)
        and unit["representative_ndc"]
    ]


def dispense_unit(fdb_code: str, representative_ndc: str) -> dict[str, str] | None:
    """The dispense unit of ``fdb_code`` with this NDC, or ``None`` when it has none.

    Raises:
        DispenseUnitsUnavailable: The ontologies service did not answer.
    """
    try:
        response = ontologies_http.get_json(f"/fdb/grouped-medication/{quote(fdb_code, safe='')}/")
    except Exception as exc:
        raise DispenseUnitsUnavailable("The medication lookup did not answer; try again.") from exc
    if response.status_code == 404:
        return None
    if response.status_code != 200:
        raise DispenseUnitsUnavailable(
            f"The medication lookup answered {response.status_code}; try again."
        )
    body = response.json()
    units = dispense_units(body) if isinstance(body, dict) else []
    return next((unit for unit in units if unit["representative_ndc"] == representative_ndc), None)


__exports__ = ()
