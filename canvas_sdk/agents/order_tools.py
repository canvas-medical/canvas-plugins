"""SDK-provided tools for imaging orders and referrals, registered on :data:`standard_tools`.

``find_service_providers`` searches the instance's directory of outside providers, the
same list the chart's Refer and Imaging Order commands pick from, and the study an
imaging order names comes from ``find_clinical_codes`` (kind ``imaging_study``). The
``originate_*`` tools stage a draft of each order on the patient's open note, never
committing it: a clinician reviews, completes, and signs it.
"""

from typing import Any

from canvas_sdk.agents.standard_tools import _ORIGINATE_RETURNS, standard_tools
from canvas_sdk.agents.tool_registry import EffectField, FilterSpec
from canvas_sdk.commands import ImagingOrderCommand, ReferCommand
from canvas_sdk.commands.constants import ServiceProvider as CommandServiceProvider
from canvas_sdk.v1.data import ServiceProvider

# Diagnosis codes an order may carry, as the chart's indications field allows.
MAX_ORDER_DIAGNOSES = 4


def _active_providers() -> Any:
    return ServiceProvider.objects.filter(is_active=True)


@standard_tools.filter_search_tool(
    name="find_service_providers",
    description=(
        "Search the practice's directory of outside providers and facilities, the list "
        "the chart's Refer and Imaging Order commands pick from. Returns each with `id` "
        "(pass it as `service_provider_id` to `originate_refer` or "
        "`originate_imaging_order`), name, specialty, and practice. Practice-level "
        "config, not patient-scoped. When several fit, ask the clinician which one."
    ),
    queryset_factory=lambda args, pid: _active_providers(),
    patient_scoped=False,
    filters={
        "specialty_contains": FilterSpec(
            type="string",
            description="Case-insensitive match on the specialty (e.g. 'cardiology', 'radiology').",
            apply=lambda qs, v: qs.filter(specialty__icontains=v),
        ),
        "name_contains": FilterSpec(
            type="string",
            description="Case-insensitive match on the provider's first or last name or practice.",
            apply=lambda qs, v: (
                qs.filter(first_name__icontains=v)
                | qs.filter(last_name__icontains=v)
                | qs.filter(practice_name__icontains=v)
            ),
        ),
    },
    ordering=("specialty", "last_name", "first_name"),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results. Defaults to 25.",
    categories=("config_reads",),
    model=ServiceProvider,
    citable=False,
    returns_description=(
        "Array of objects with `id`, `name`, `specialty`, `practice_name`, "
        "`business_phone`, `business_fax`, and `business_address`."
    ),
    progress_label="Searching the provider directory",
)
def _serialize_service_provider(provider: Any) -> dict[str, Any]:
    """Per-row serializer for find_service_providers."""
    return {
        "id": str(provider.id),
        "name": provider.full_name.strip(),
        "specialty": provider.specialty,
        "practice_name": provider.practice_name or "",
        "business_phone": provider.business_phone or "",
        "business_fax": provider.business_fax or "",
        "business_address": provider.business_address or "",
    }


def _service_provider(provider_id: str) -> CommandServiceProvider:
    """The directory provider ``provider_id`` names, as the order commands carry it."""
    provider = _active_providers().filter(id=provider_id).first()
    if provider is None:
        raise ValueError(
            f"No active service provider with id {provider_id!r}. Look one up with "
            "find_service_providers and pass its `id`."
        )
    return CommandServiceProvider(
        first_name=provider.first_name,
        last_name=provider.last_name,
        specialty=provider.specialty,
        practice_name=provider.practice_name or "",
        business_fax=provider.business_fax,
        business_phone=provider.business_phone,
        business_address=provider.business_address,
        notes=provider.notes or None,
    )


def _with_service_provider(arguments: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    provider_id = arguments.get("service_provider_id")
    return {"service_provider": _service_provider(str(provider_id))} if provider_id else {}


_DIAGNOSIS_CODES = EffectField(
    type="array",
    items={"type": "string"},
    max_items=MAX_ORDER_DIAGNOSES,
    description=(
        "ICD-10 codes for the problems the order is for, from find_conditions or "
        "find_clinical_codes (kind 'condition'). Signing requires at least one."
    ),
)
_PRIORITIES = [priority.value for priority in ImagingOrderCommand.Priority]


standard_tools.originate_command_tool(
    name="originate_imaging_order",
    description=(
        "Stage a draft Imaging Order on the patient's open note for the clinician to "
        "review and sign. NEVER commits. Look the study up first with "
        "`find_clinical_codes` (kind 'imaging_study') and pass its `image_code`; never "
        "write a study code from memory. Use when the clinician asks to order imaging."
    ),
    command_class=ImagingOrderCommand,
    fields={
        "image_code": EffectField(
            type="string",
            description="The study's `image_code` from find_clinical_codes (kind 'imaging_study').",
            required=True,
        ),
        "diagnosis_codes": _DIAGNOSIS_CODES,
        "priority": EffectField(
            type="string",
            enum=_PRIORITIES,
            description="How urgent the study is. Omit when the clinician did not say.",
            editable=True,
        ),
        "service_provider_id": EffectField(
            type="string",
            description=(
                "Where the study is performed: an `id` from find_service_providers. "
                "Optional; the clinician can choose when reviewing."
            ),
            pre_build_only=True,
        ),
        "additional_details": EffectField(
            type="string",
            description="Details for whoever performs the study, such as side or contrast.",
            editable=True,
        ),
        "comment": EffectField(type="string", description="A comment on the order.", editable=True),
    },
    pre_build=_with_service_provider,
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


standard_tools.originate_command_tool(
    name="originate_refer",
    description=(
        "Stage a draft Referral on the patient's open note for the clinician to review "
        "and sign. NEVER commits. Look the provider up first with "
        "`find_service_providers` and pass its `id`. Use when the clinician asks to "
        "refer the patient."
    ),
    command_class=ReferCommand,
    fields={
        "service_provider_id": EffectField(
            type="string",
            description="Who the patient is referred to: an `id` from find_service_providers.",
            required=True,
            pre_build_only=True,
        ),
        "diagnosis_codes": _DIAGNOSIS_CODES,
        "clinical_question": EffectField(
            type="string",
            enum=[question.value for question in ReferCommand.ClinicalQuestion],
            description="What the referral asks of the specialist.",
            editable=True,
        ),
        "priority": EffectField(
            type="string",
            enum=[priority.value for priority in ReferCommand.Priority],
            description="How urgent the referral is. Omit when the clinician did not say.",
            editable=True,
        ),
        "notes_to_specialist": EffectField(
            type="string",
            description="What the specialist should know, in the clinician's words.",
            editable=True,
        ),
        "include_visit_note": EffectField(
            type="boolean",
            description="Whether to send this visit's note with the referral.",
            editable=True,
        ),
        "comment": EffectField(
            type="string", description="An internal comment on the referral.", editable=True
        ),
    },
    pre_build=_with_service_provider,
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


standard_tools.set_progress_labels(
    {
        "originate_imaging_order": "Drafting an imaging order",
        "originate_refer": "Drafting a referral",
    }
)


__exports__ = ()
