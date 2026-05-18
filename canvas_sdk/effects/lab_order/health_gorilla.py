from typing import Any, Literal

from canvas_sdk.effects.base import EffectType, _BaseEffect

BillToCode = Literal["self", "patient", "guarantor", "thirdParty"]


class HealthGorillaLabOrderOverride(_BaseEffect):
    """Inject FHIR-shaped values into the outbound Health Gorilla lab-order
    payload. Returned by a handler of `EventType.LAB_ORDER_COMMAND__PRE_SEND`.

    Any field left as None is treated as "no override" — Canvas falls through
    to its existing resolution path for that field. This means a plugin can
    override a single value (e.g. just `bill_to_code`) without disturbing the
    rest of the payload build.

    Field semantics:
      - `practitioner_account_number`: lab account number stamped on the
        contained Practitioner identifier.
      - `organizational_account_number`: lab account number stamped on the
        contained authorizing Organization identifier.
      - `hg_organization_id`: Health Gorilla facility id (`f-...`) used for
        the `requestgroup-performer` reference. When set, skips the
        ontology-based lookup by lab partner name.
      - `hg_tenant_id`: Health Gorilla sub-tenant Organization id. When set,
        Canvas adds a `requestgroup-authorizedBy` extension. With only
        `hg_tenant_id`, the reference is `Organization/t-{hg_tenant_id}`.
        With both `hg_tenant_id` and `hg_location_id` set, the reference is
        `Organization/tl-{hg_tenant_id}-{hg_location_id}` (the HG sub-tenant
        location form).
      - `hg_location_id`: Health Gorilla tenant-location id. Combined with
        `hg_tenant_id` to produce a `tl-` `requestgroup-authorizedBy`
        reference. Has no effect on its own.
      - `hg_practitioner_id`: Health Gorilla Practitioner id, appended as an
        additional identifier on the contained Practitioner with system
        `https://www.healthgorilla.com`. Use this when the ordering provider
        is registered with HG and you want to surface that registration on
        the outbound order alongside the NPI.
      - `bill_to_code`: explicit Account.type coding. Overrides the existing
        coverage-derived inference.
    """

    class Meta:
        effect_type = EffectType.HEALTH_GORILLA_LAB_ORDER_OVERRIDE

    practitioner_account_number: str | None = None
    organizational_account_number: str | None = None
    hg_organization_id: str | None = None
    hg_tenant_id: str | None = None
    hg_location_id: str | None = None
    hg_practitioner_id: str | None = None
    bill_to_code: BillToCode | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Only include fields the plugin set; absent keys mean 'no override'."""
        return {
            key: value
            for key, value in (
                ("practitioner_account_number", self.practitioner_account_number),
                ("organizational_account_number", self.organizational_account_number),
                ("hg_organization_id", self.hg_organization_id),
                ("hg_tenant_id", self.hg_tenant_id),
                ("hg_location_id", self.hg_location_id),
                ("hg_practitioner_id", self.hg_practitioner_id),
                ("bill_to_code", self.bill_to_code),
            )
            if value is not None
        }


__exports__ = ("HealthGorillaLabOrderOverride", "BillToCode")
