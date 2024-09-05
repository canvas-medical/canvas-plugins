from peewee import AutoField, BooleanField, CharField, DateField, ForeignKeyField
from peewee import Model as PWModel
from peewee import PostgresqlDatabase, UUIDField
from pydantic_core import ValidationError

from canvas_sdk.base import Model


class DataModel(Model):
    class Meta:
        update_required_fields = ("id",)

    def model_dump_json_nested(self, *args, **kwargs) -> str:
        """
        Returns the model's json representation nested in a {"data": {..}} key.
        """
        return f'{{"data": {self.model_dump_json(*args, **kwargs)}}}'

    def _validate_before_effect(self, method: str) -> None:
        if method == "create" and getattr(self, "id", None):
            error = self._create_error_detail(
                "value", "create cannot be called on a model with an id", "id"
            )
            raise ValidationError.from_exception_data(self.__class__.__name__, [error])
        super()._validate_before_effect(method)


psql_db = PostgresqlDatabase("home-app", user="app", password="app", host="localhost", port=5435)


class OrmModel(PWModel):
    class Meta:
        database = psql_db


class CoolPatient(OrmModel):
    class Meta:
        table_name = "dal_patient"

    id = UUIDField(column_name="key")
    dbid = AutoField(column_name="id", primary_key=True)
    first_name = CharField()
    last_name = CharField()
    birth_date = DateField()

    @classmethod
    def find(cls, uuid: str):
        return CoolPatient.select().where(CoolPatient.id == uuid).first()

    def __str__(self) -> str:
        return f"{first_name} {last_name} {birth_date} {id}"


class Condition(OrmModel):
    class Meta:
        table_name = "dal_api_condition"

    id = UUIDField()
    dbid = AutoField(primary_key=True)
    onset_date = DateField()
    resolution_date = DateField
    patient = ForeignKeyField(CoolPatient, column_name="patient_id", backref="conditions")

    @classmethod
    def find(cls, uuid: str):
        return Condition.select().where(Condition.id == uuid).first()


class ConditionCoding(OrmModel):
    class Meta:
        table_name = "dal_api_conditioncoding"

    dbid = AutoField(primary_key=True)
    system = CharField()
    version = CharField()
    code = CharField()
    display = CharField()
    user_selected = BooleanField()
    condition = ForeignKeyField(Condition, column_name="condition_dbid", backref="codings")


class Medication(OrmModel):
    class Meta:
        table_name = "dal_api_medication"

    id = UUIDField()
    dbid = AutoField(primary_key=True)
    patient = ForeignKeyField(CoolPatient, column_name="patient_id", backref="medications")
    status = CharField()
    start_date = DateField()
    end_date = DateField()
    quantity_qualifier_description = CharField()
    clinical_quantity_description = CharField()
    potency_unit_code = CharField()
    national_drug_code = CharField()
    erx_quantity = CharField()

    @classmethod
    def find(cls, uuid: str):
        return Medication.select().where(Medication.id == uuid).first()


class MedicationCoding(OrmModel):
    class Meta:
        table_name = "dal_api_medicationcoding"

    dbid = AutoField(primary_key=True)
    system = CharField()
    version = CharField()
    code = CharField()
    display = CharField()
    user_selected = BooleanField()
    medication = ForeignKeyField(Medication, column_name="medication_dbid", backref="codings")
