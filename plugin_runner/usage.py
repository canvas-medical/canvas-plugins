"""Which usage a plugin may record: the units its own manifest prices.

A `RecordUsage` effect is dropped here, before it reaches home-app, when its unit is not one
the plugin's manifest `catalog.pricing` lists or when it asks to run asynchronously. home-app
writes what remains, attributed to the plugin the runner loaded, so a plugin can record usage
only under its own name and only in units it is priced in.
"""

import json
from collections.abc import Mapping
from typing import Any

from canvas_generated.messages.effects_pb2 import Effect, EffectType
from canvas_sdk.effects.usage import MAX_KEY, MAX_QUANTITY
from logger import log

# Priced by the inference gateway, so never recorded as plugin usage.
TOKEN_UNIT = "token"


def unit_name(value: str) -> str:
    """How a unit is matched: lowercase, with runs of whitespace as one space, as Platform does."""
    return " ".join(value.split()).lower()


def usage_units(manifest: Mapping[str, Any]) -> frozenset[str]:
    """The units a manifest's `catalog.pricing` lists, `token` aside."""
    catalog = manifest.get("catalog")
    pricing = catalog.get("pricing") if isinstance(catalog, Mapping) else None
    if not isinstance(pricing, list):
        return frozenset()
    units = {
        unit_name(component["unit"])
        for component in pricing
        if isinstance(component, Mapping) and isinstance(component.get("unit"), str)
    }
    return frozenset(units - {TOKEN_UNIT, ""})


def _record(payload: Any) -> tuple[str, str, int] | None:
    """The unit, key and quantity a payload carries, or None unless all three are well formed.

    `RecordUsage` validates these in the plugin, but a plugin can build an `Effect` with any
    payload, so the runner checks them again.
    """
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        return None
    unit, key, quantity = data.get("unit"), data.get("key"), data.get("quantity")
    if not isinstance(unit, str) or not isinstance(key, str) or not 1 <= len(key) <= MAX_KEY:
        return None
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        return None
    if not 1 <= quantity <= MAX_QUANTITY:
        return None
    return unit_name(unit), key, quantity


def permitted_usage(effects: list[Effect], units: frozenset[str]) -> list[Effect]:
    """`effects` without the usage records the plugin may not make, each rewritten to carry only
    its unit, as matched, its key and its quantity.
    """
    permitted = []
    for effect in effects:
        if effect.type != EffectType.RECORD_USAGE:
            permitted.append(effect)
            continue
        try:
            payload = json.loads(effect.payload)
        except ValueError:
            payload = None
        record = _record(payload)
        if record is None:
            log.warning(f"Discarding a malformed RECORD_USAGE effect from {effect.plugin_name}.")
            continue
        unit, key, quantity = record
        if "async_props" in payload:
            log.warning(
                f"Discarding a RECORD_USAGE effect from {effect.plugin_name}: usage is recorded "
                "with the effects it counts, so it cannot run asynchronously."
            )
            continue
        if unit not in units:
            log.warning(
                f"Discarding a RECORD_USAGE effect from {effect.plugin_name}: '{unit}' is not a "
                "unit its manifest's catalog.pricing lists."
            )
            continue
        effect.payload = json.dumps({"data": {"unit": unit, "key": key, "quantity": quantity}})
        permitted.append(effect)
    return permitted
