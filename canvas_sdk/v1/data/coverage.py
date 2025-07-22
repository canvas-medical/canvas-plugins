from django.contrib.postgres.fields import ArrayField
from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, Model
from canvas_sdk.v1.data.common import (
    AddressState,
    AddressType,
    AddressUse,
    ContactPointState,
    ContactPointSystem,
    ContactPointUse,
)


class CoverageStack(models.TextChoices):
    """CoverageStack."""

    IN_USE = "IN_USE", "In use"
    OTHER = "OTHER", "Other"
    REMOVED = "REMOVED", "Removed"


class CoverageState(models.TextChoices):
    """CoverageState."""

    ACTIVE = "active", "Active"
    DELETED = "deleted", "Deleted"


class CoverageType(models.TextChoices):
    """CoverageType."""

    COMMERCIAL = "commercial", "Commercial"
    WORKERS_COMP = "workerscomp", "Workers Comp"
    BCBS = "bcbs", "Blue Cross Blue Shield"
    TRICARE = "champus", "Tricare/Champus"
    MEDICAID = "medicaid", "Medicaid"
    MEDICARE = "medicare", "Medicare"
    OTHER = "other", "Other"
    TPA = "tpa", "Third Party Administrator"
    MVA = "motorvehicle", "Motor Vehicle"
    LIEN = "lien", "Attorney/Lien"
    PIP = "pip", "Personal Injury"


class CoverageRelationshipCode(models.TextChoices):
    """CoverageRelationshipCode."""

    SELF = "18", "Self"
    SPOUSE = "01", "Spouse"
    CHILD_INSURED_HAS_FINANCIAL_RESP = "19", "Natural Child, insured has financial responsibility"
    CHILD_HAS_FINANCIAL_RESP = "43", "Natural Child, insured does not have financial responsibility"
    STEP_CHILD = "17", "Step Child"
    FOSTER_CHILD = "10", "Foster Child"
    WARD_OF_COURT = "15", "Ward of the Court"
    EMPLOYEE = "20", "Employee"
    UNKNOWN = "21", "Unknown"
    HANDICAPPED_DEPENDENT = "22", "Handicapped Dependent"
    ORGAN_DONOR = "39", "Organ donor"
    CADAVER_DONOR = "40", "Cadaver donor"
    GRANDCHILD = "05", "Grandchild"
    NIECE_NEPHEW = "07", "Niece/Nephew"
    INJURED_PLAINTIFF = "41", "Injured Plaintiff"
    SPONSORED_DEPENDENT = "23", "Sponsored Dependent"
    MINOR_DEP_OF_MINOR_DEP = "24", "Minor Dependent of a Minor Dependent"
    MOTHER = "32", "Mother"
    FATHER = "33", "Father"
    GRANDPARENT = "04", "Grandparent"
    LIFE_PARTNER = "53", "Life Partner"
    SIGNIFICANT_OTHER = "29", "Significant Other"
    OTHER = "G8", "Other"


class TransactorCoverageType(models.TextChoices):
    """TransactorCoverageType."""

    ANNU = "ANNU", "annuity policy"
    AUTOPOL = "AUTOPOL", "automobile"
    CHAR = "CHAR", "charity program"
    COL = "COL", "collision coverage policy"
    CRIME = "CRIME", "crime victim program"
    DENTAL = "DENTAL", "dental care policy"
    DENTPRG = "DENTPRG", "dental program"
    DIS = "DIS", "disability insurance policy"
    DISEASE = "DISEASE", "disease specific policy"
    DRUGPOL = "DRUGPOL", "drug policy"
    EAP = "EAP", "employee assistance program"
    EWB = "EWB", "employee welfare benefit plan policy"
    ENDRENAL = "ENDRENAL", "end renal program"
    EHCPOL = "EHCPOL", "extended healthcare"
    FLEXP = "FLEXP", "flexible benefit plan policy"
    GOVEMP = "GOVEMP", "government employee health program"
    HIP = "HIP", "health insurance plan policy"
    HMO = "HMO", "health maintenance organization policy"
    HSAPOL = "HSAPOL", "health spending account"
    HIRISK = "HIRISK", "high risk pool program"
    HIVAIDS = "HIVAIDS", "HIV-AIDS program"
    IND = "IND", "indigenous peoples health program"
    LIFE = "LIFE", "life insurance policy"
    LTC = "LTC", "long term care policy"
    MCPOL = "MCPOL", "managed care policy"
    MANDPOL = "MANDPOL", "mandatory health program"
    MENTPOL = "MENTPOL", "mental health policy"
    MENTPRG = "MENTPRG", "mental health program"
    MILITARY = "MILITARY", "military health program"
    PAY = "pay", "Pay"
    POS = "POS", "point of service policy"
    PPO = "PPO", "preferred provider organization policy"
    PNC = "PNC", "property and casualty insurance policy"
    DISEASEPRG = "DISEASEPRG", "public health program"
    PUBLICPOL = "PUBLICPOL", "public healthcare"
    REI = "REI", "reinsurance policy"
    RETIRE = "RETIRE", "retiree health program"
    SAFNET = "SAFNET", "safety net clinic program"
    SOCIAL = "SOCIAL", "social service program"
    SUBSIDIZ = "SUBSIDIZ", "subsidized health program"
    SUBSIDMC = "SUBSIDMC", "subsidized managed care program"
    SUBSUPP = "SUBSUPP", "subsidized supplemental health program"
    SUBPOL = "SUBPOL", "substance use policy"
    SUBPRG = "SUBPRG", "substance use program"
    SURPL = "SURPL", "surplus line insurance policy"
    TLIFE = "TLIFE", "term life insurance policy"
    UMBRL = "UMBRL", "umbrella liability insurance policy"
    UNINSMOT = "UNINSMOT", "uninsured motorist policy"
    ULIFE = "ULIFE", "universal life insurance policy"
    VET = "VET", "veteran health program"
    VISPOL = "VISPOL", "vision care policy"
    CANPRG = "CANPRG", "women's cancer detection program"
    WCBPOL = "WCBPOL", "worker's compensation"


class TransactorType(models.TextChoices):
    """TransactorType."""

    COMMERCIAL = "commercial", "Commercial"
    WORKERS_COMP = "workerscomp", "Workers Comp"
    TRICARE = "champus", "Tricare/Champus"
    MEDICAID = "medicaid", "Medicaid"
    MEDICARE = "medicare", "Medicare"
    MEDICARE_ADVANTAGE = "medicare_advantage", "Medicare Advantage"
    CHIP = "CHIP", "CHIP"
    AUTO = "automobile", "Automobile"
    EMPLOYER = "employer", "Employer"
    DIRECT_CARE = "direct_care", "Direct Care"
    BCBS = "bcbs", "Blue Cross Blue Shield"


class Coverage(IdentifiableModel):
    """Coverage."""

    class Meta:
        db_table = "canvas_sdk_data_api_coverage_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="coverages", null=True
    )
    guarantor = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="dependent_coverages", null=True
    )
    subscriber = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="subscribed_coverages", null=True
    )
    patient_relationship_to_subscriber = models.CharField(
        choices=CoverageRelationshipCode.choices, max_length=2
    )
    issuer = models.ForeignKey(
        "v1.Transactor", on_delete=models.DO_NOTHING, related_name="coverages", null=True
    )
    id_number = models.CharField(max_length=100)
    plan = models.CharField(max_length=255)
    sub_plan = models.CharField(max_length=255)
    group = models.CharField(max_length=255)
    sub_group = models.CharField(max_length=255)
    employer = models.CharField(max_length=255)
    coverage_start_date = models.DateField()
    coverage_end_date = models.DateField()
    coverage_rank = models.IntegerField()
    state = models.CharField(choices=CoverageState.choices, max_length=20)
    plan_type = models.CharField(choices=CoverageType.choices, max_length=20)
    coverage_type = models.CharField(choices=TransactorCoverageType.choices, max_length=64)
    issuer_address = models.ForeignKey(
        "v1.TransactorAddress",
        on_delete=models.DO_NOTHING,
        related_name="coverages",
        null=True,
    )
    issuer_phone = models.ForeignKey(
        "v1.TransactorPhone", on_delete=models.DO_NOTHING, related_name="coverages", null=True
    )
    comments = models.TextField()
    stack = models.CharField(choices=CoverageStack.choices, max_length=8)

    def __str__(self) -> str:
        return f"id={self.id}"


class Transactor(Model):
    """Transactor."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_transactor_001"

    payer_id = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    transactor_type = models.CharField(choices=TransactorType.choices, max_length=100)
    clearinghouse_payer = models.BooleanField()
    institutional = models.BooleanField(null=True)
    institutional_enrollment_req = models.BooleanField(null=True)
    professional = models.BooleanField(null=True)
    professional_enrollment_req = models.BooleanField(null=True)
    era = models.BooleanField(null=True)
    era_enrollment_req = models.BooleanField(null=True)
    eligibility = models.BooleanField(null=True)
    eligibility_enrollment_req = models.BooleanField(null=True)
    workers_comp = models.BooleanField(null=True)
    secondary_support = models.BooleanField(null=True)
    claim_fee = models.BooleanField(null=True)
    remit_fee = models.BooleanField(null=True)
    state = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    active = models.BooleanField()
    use_provider_for_eligibility = models.BooleanField()

    use_for_submission = models.ForeignKey(
        "v1.Transactor",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="used_for_submission_by",
    )

    coverage_types = ArrayField(
        models.CharField(choices=TransactorCoverageType.choices, max_length=64)
    )


class TransactorAddress(IdentifiableModel):
    """TransactorAddress."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_transactoraddress_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    state_code = models.CharField(max_length=2)
    postal_code = models.CharField(max_length=255)
    use = models.CharField(choices=AddressUse.choices, max_length=10)
    type = models.CharField(choices=AddressType.choices, max_length=10)
    longitude = models.FloatField(null=True, default=None, blank=True)
    latitude = models.FloatField(null=True, default=None, blank=True)
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=255)
    state = models.CharField(choices=AddressState.choices, max_length=20)
    transactor = models.ForeignKey(
        "v1.Transactor", on_delete=models.DO_NOTHING, related_name="addresses", null=True
    )

    def __str__(self) -> str:
        return f"id={self.id}"


class TransactorPhone(IdentifiableModel):
    """TransactorPhone."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_transactorphone_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    system = models.CharField(choices=ContactPointSystem.choices, max_length=20)
    value = models.CharField(max_length=100)
    use = models.CharField(choices=ContactPointUse.choices, max_length=20)
    use_notes = models.CharField(max_length=255)
    rank = models.IntegerField()
    state = models.CharField(choices=ContactPointState.choices, max_length=20)
    transactor = models.ForeignKey(
        "v1.Transactor", on_delete=models.DO_NOTHING, related_name="phones", null=True
    )

    def __str__(self) -> str:
        return f"id={self.id}"


__exports__ = (
    "CoverageStack",
    "CoverageState",
    "CoverageType",
    "CoverageRelationshipCode",
    "TransactorCoverageType",
    "TransactorType",
    "Coverage",
    "Transactor",
    "TransactorAddress",
    "TransactorPhone",
)
