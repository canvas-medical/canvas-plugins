from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from canvas_sdk.effects.base import EffectType, _BaseEffect


class _LabValueIn(BaseModel):
    """A single LabValue to attach to a HealthGorillaLabReportIngest.

    Plain Pydantic model (not _BaseEffect) — these are nested children of
    the parent ingest effect, not standalone effects, so they don't need
    EffectType / patient_filter.
    """

    ontology_test_code: str
    ontology_test_name: str = ""
    value: str
    units: str = ""
    reference_range: str = ""
    abnormal_flag: str = ""
    observation_status: str = "final"
    comment: str = ""

    @property
    def values(self) -> dict[str, Any]:
        return self.model_dump()


class HealthGorillaLabOrderIngest(_BaseEffect):
    """Create a Canvas LabOrder that originated outside Canvas (e.g. on a
    partner's HG tenant or on a third-party LIS).

    The order is created with `hg_request_result` set non-empty so Canvas's
    send-to-HG worker treats it as already-sent and does not try to forward
    the order to HG. One LabTest row is created per `test_codes` entry.

    Use this from a SimpleAPI route a partner POSTs to when they place a
    standing or recurring order on their side and want Canvas to surface it
    in the chart.

    Required:
      - `patient_id`: Canvas Patient external id (uuid)
      - `ordering_provider_npi`: NPI used to look up the Staff record
      - `note_id`: Canvas Note external id (uuid). LabOrders require a Note
        FK in home-app
      - `ontology_lab_partner`: ontology lab partner name (e.g. "QUEST")
      - `date_ordered`: when the order was authored on the partner side
      - `hg_request_result`: skip-send marker; convention is the partner's
        HG RequestGroup URL or id so Canvas can correlate later
      - `test_codes`: HG order codes; one LabTest per code

    Optional:
      - `external_id`: stored on `LabOrder.healthgorilla_id` for dedup
      - `comment`: stored on `LabOrder.comment`
    """

    class Meta:
        effect_type = EffectType.HEALTH_GORILLA_LAB_ORDER_INGEST

    patient_id: str
    ordering_provider_npi: str
    note_id: str
    ontology_lab_partner: str
    date_ordered: datetime
    hg_request_result: str
    test_codes: list[str]
    external_id: str = ""
    comment: str = ""

    @property
    def values(self) -> dict[str, Any]:
        """Serialize the effect's fields into the proto payload dict."""
        return {
            "patient_id": self.patient_id,
            "ordering_provider_npi": self.ordering_provider_npi,
            "note_id": self.note_id,
            "ontology_lab_partner": self.ontology_lab_partner,
            "date_ordered": self.date_ordered.isoformat(),
            "hg_request_result": self.hg_request_result,
            "test_codes": list(self.test_codes),
            "external_id": self.external_id,
            "comment": self.comment,
        }


class HealthGorillaLabReportIngest(_BaseEffect):
    """Create a Canvas LabReport with attached LabValues and an attached PDF
    for a lab result that originated outside Canvas.

    Equivalent to `LabEngineInboundService.process_and_store_report` minus
    the HG fetch — the partner provides the PDF (via URL the home-app
    interpreter fetches, or inline base64) and Canvas stores it through the
    existing S3 / ElectronicLabIntegrationTask path.

    Dedup is keyed on `(external_id, version)`:
      - new external_id            → create new LabReport
      - same external_id, higher version → replace LabReport
      - same external_id, same/lower version → no-op (existing record kept)

    Required:
      - `lab_order_id`: Canvas LabOrder external id (uuid) the report belongs to
      - `patient_id`: Canvas Patient external id (uuid)
      - `external_id`: partner-side report id; used for dedup
      - `version`: report version, monotonically increasing per external_id
      - `date_performed`: when the report was generated on the partner side
      - `lab_values`: list of test code + value rows

    PDF (exactly one of the following must be set):
      - `pdf_url`: URL the plugin runner can GET the PDF from. Recommended
        for large PDFs to avoid blowing up the proto context.
      - `pdf_base64`: PDF bytes inline as base64. Use only for small PDFs.

    Optional:
      - `status`: report status; defaults to "final"
    """

    class Meta:
        effect_type = EffectType.HEALTH_GORILLA_LAB_REPORT_INGEST

    lab_order_id: str
    patient_id: str
    external_id: str
    version: int = Field(ge=1)
    status: str = "final"
    date_performed: datetime
    lab_values: list[_LabValueIn]
    pdf_url: str = ""
    pdf_base64: str = ""

    @property
    def values(self) -> dict[str, Any]:
        """Serialize the effect's fields into the proto payload dict."""
        return {
            "lab_order_id": self.lab_order_id,
            "patient_id": self.patient_id,
            "external_id": self.external_id,
            "version": self.version,
            "status": self.status,
            "date_performed": self.date_performed.isoformat(),
            "lab_values": [value.values for value in self.lab_values],
            "pdf_url": self.pdf_url,
            "pdf_base64": self.pdf_base64,
        }


__exports__ = ("HealthGorillaLabOrderIngest", "HealthGorillaLabReportIngest")
