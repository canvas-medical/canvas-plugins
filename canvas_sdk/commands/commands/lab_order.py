from typing import Literal
from uuid import UUID

from django.db.models.query_utils import Q
from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.v1.data.lab import LabPartner, LabPartnerTest


class LabOrderCommand(BaseCommand):
    """A class for managing a Lab Order command within a specific note."""

    class Meta:
        key = "labOrder"

    lab_partner: UUID | str | None = None
    tests_order_codes: list[str] = Field(
        default=[], json_schema_extra={"commands_api_name": "tests"}
    )
    ordering_provider_key: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "ordering_provider"}
    )
    diagnosis_codes: list[str] = Field(
        default=[], json_schema_extra={"commands_api_name": "diagnosis"}
    )
    fasting_required: bool = False
    comment: str | None = None

    def _get_error_details(
        self, method: Literal["originate", "edit", "delete", "commit", "enter_in_error"]
    ) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        lab_partner_obj = None
        if self.lab_partner:
            query = {}
            try:
                UUID(str(self.lab_partner))
            except ValueError:
                query["name"] = self.lab_partner
            else:
                query["id"] = self.lab_partner

            lab_partner_obj = LabPartner.objects.filter(**query).values("id", "dbid").first()

            if not lab_partner_obj:
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"lab partner with Id or Name {self.lab_partner} not found",
                        self.lab_partner,
                    )
                )

        if self.tests_order_codes:
            if not lab_partner_obj:
                errors.append(
                    self._create_error_detail(
                        "value", "lab partner is required to find tests", self.tests_order_codes
                    )
                )
            else:
                uuid_tests = []
                order_code_tests = []

                for code in self.tests_order_codes:
                    try:
                        uuid_tests.append(UUID(str(code)))
                    except ValueError:
                        order_code_tests.append(code)

                tests = LabPartnerTest.objects.filter(
                    Q(order_code__in=order_code_tests) | Q(id__in=uuid_tests),
                    lab_partner_id=lab_partner_obj["dbid"],
                ).values_list("id", "order_code")

                if tests.count() != len(self.tests_order_codes):
                    missing_tests = [
                        test
                        for test in self.tests_order_codes
                        if not any(
                            test == str(test_id) or test == order_code
                            for test_id, order_code in tests
                        )
                    ]

                    errors.append(
                        self._create_error_detail(
                            "value",
                            f"tests with order codes {missing_tests} not found",
                            self.tests_order_codes,
                        )
                    )

        return errors


__exports__ = ("LabOrderCommand",)
