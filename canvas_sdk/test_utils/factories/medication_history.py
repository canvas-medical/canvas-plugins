
import factory

from canvas_sdk.test_utils.factories.patient import PatientFactory
from canvas_sdk.v1.data import MedicationHistoryMedication


class MedicationHistoryMedicationFactory(factory.django.DjangoModelFactory[MedicationHistoryMedication]):
    """Factory for creating a MedicationHistoryMedication."""

    class Meta:
        model = MedicationHistoryMedication

    patient = factory.SubFactory(PatientFactory)

    drug_description = models.TextField()

    strength_value = models.CharField(max_length=255, blank=True, default="")
    strength_form = models.CharField(max_length=255, blank=True, default="")
    strength_unit_of_measure = models.CharField(max_length=255, blank=True, default="")

    quantity = models.FloatField(null=True)
    quantity_unit_of_measure = models.CharField(max_length=255, blank=True, default="")
    quantity_code_list_qualifier = models.CharField(max_length=255, blank=True, default="")

    days_supply = models.IntegerField(null=True)

    last_fill_date = models.DateTimeField(db_index=True)
    written_date = models.DateTimeField(blank=True, null=True)

    other_date = models.DateTimeField(blank=True, null=True)
    other_date_qualifier = models.CharField(max_length=255, blank=True, default="")

    substitutions = models.BooleanField(null=True)

    refills_remaining = models.IntegerField(null=True)

    diagnosis_code = models.CharField(max_length=255, blank=True, default="")
    diagnosis_qualifier = models.CharField(max_length=255, blank=True, default="")
    diagnosis_description = models.CharField(max_length=255, blank=True, default="")

    secondary_diagnosis_code = models.CharField(max_length=255, blank=True, default="")
    secondary_diagnosis_qualifier = models.CharField(max_length=255, blank=True, default="")
    secondary_diagnosis_description = models.CharField(max_length=255, blank=True, default="")

    dea_schedule = models.CharField(max_length=255, blank=True, default="")

    potency_unit_code = models.CharField(max_length=20, blank=True, default="")
    etc_path_id = ArrayField(base_field=models.IntegerField(), null=True)
    etc_path_name = ArrayField(base_field=models.CharField(max_length=255), null=True)

    fill_number = models.IntegerField(blank=True, null=True)

    prescriber_order_number = models.CharField(max_length=255, blank=True, default="")

    source_description = models.CharField(max_length=255, blank=True, default="")
    source_qualifier = models.CharField(max_length=255, blank=True, default="")
    source_payer_id = models.CharField(max_length=255, blank=True, default="")
    source_type = models.CharField(max_length=255, blank=True, default="")

    note = models.TextField(blank=True, default="")
    sig = models.TextField(blank=True, default="")

    prior_authorization_status = models.CharField(max_length=255, blank=True, default="")
    prior_authorization = models.CharField(max_length=255, blank=True, default="")

    pharmacy_name = models.CharField(max_length=255, blank=True, default="")
    pharmacy_ncpdp_id = models.CharField(max_length=255, blank=True, default="")
    pharmacy_npi = models.CharField(max_length=255, blank=True, default="")

    prescriber_business_name = models.CharField(max_length=255, blank=True, default="")
    prescriber_first_name = models.CharField(max_length=255, blank=True, default="")
    prescriber_last_name = models.CharField(max_length=255, blank=True, default="")
    prescriber_npi = models.CharField(max_length=255, blank=True, default="")
    prescriber_dea_number = models.CharField(max_length=255, blank=True, default="")
