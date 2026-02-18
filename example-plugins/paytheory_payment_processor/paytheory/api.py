import json
from decimal import Decimal
from typing import NotRequired, TypedDict

import requests

from paytheory_payment_processor.paytheory.exceptions import TransactionError

PAYTHEORY_GRAPHQL_URL = "https://api.start.paytheory.com/graphql"


class PayorInput(TypedDict):
    """A TypedDict for the input data required to create a payor in PayTheory."""

    address_line1: NotRequired[str]
    address_line2: NotRequired[str]
    city: NotRequired[str]
    country: NotRequired[str]
    email: NotRequired[str]
    full_name: NotRequired[str]
    metadata: NotRequired[dict | str]
    phone: NotRequired[dict]
    postal_code: NotRequired[str]
    region: NotRequired[str]


class TransactionInput(TypedDict):
    """A TypedDict for the input data required to create a transaction in PayTheory."""

    amount: Decimal
    payment_method_id: NotRequired[str]
    account_code: NotRequired[str]
    currency: NotRequired[str]
    fee: NotRequired[int]
    fee_mode: NotRequired[str]
    invoice_id: NotRequired[str]
    metadata: NotRequired[dict | str]
    one_time_use_token: NotRequired[bool]
    receipt_description: NotRequired[str]
    recurring_id: NotRequired[str]
    reference: NotRequired[str]
    send_receipt: NotRequired[bool]


class PaymentMethod(TypedDict):
    """A TypedDict for the payment method data returned by PayTheory."""

    payment_method_id: str | None
    card_brand: str
    exp_date: str
    country: str
    full_name: str | None
    is_active: bool
    last_four: str
    postal_code: str
    is_active: bool


class Transaction(TypedDict):
    """A TypedDict for the transaction data returned by PayTheory."""

    account_code: str
    currency: str
    dispute_status: str
    failure_reasons: list[str]
    fee_mode: str
    fees: int
    gross_amount: int
    is_settled: bool
    merchant_uid: str
    metadata: dict | None
    net_amount: int
    parent_id: str | None
    payment_method: PaymentMethod
    status: str
    timezone: str
    transaction_date: str
    transaction_id: str
    transaction_type: str


class PayTheoryAPI:
    """A class to interact with the PayTheory GraphQL API."""

    def __init__(self, api_key: str, merchant_id: str, endpoint: str = PAYTHEORY_GRAPHQL_URL):
        self.api_key = api_key
        self.merchant_id = merchant_id
        self.endpoint = endpoint or PAYTHEORY_GRAPHQL_URL

    @property
    def _headers(self) -> dict:
        """Return the headers required for the API request."""
        return {
            "Authorization": f"{self.merchant_id};{self.api_key}",
            "Content-Type": "application/json",
        }

    def create_payor(self, input_data: PayorInput) -> str:
        """Create a payor in PayTheory using the provided input data."""
        query = """
        mutation CreatePayor($input: PayorInput!) {
            createPayor(input: $input) {
                payor_id
                merchant_uid
                full_name
                address_line1
                address_line2
                country
                region
                city
                postal_code
                email
                phone
                metadata
            }
        }
        """

        if "metadata" in input_data and isinstance(input_data["metadata"], dict):
            input_data["metadata"] = json.dumps(input_data["metadata"])

        payload = {
            "query": query,
            "variables": {"input": {**input_data, "merchant_uid": self.merchant_id}},
        }

        response = requests.post(self.endpoint, json=payload, headers=self._headers)

        if response.status_code != 200 or "errors" in response.json():
            raise Exception(f"GraphQL error: {response.text}")

        payor_id = response.json().get("data", {}).get("createPayor", {}).get("payor_id")

        return payor_id

    def get_payor_id(self, patient_id: str) -> str | None:
        """Retrieve a payor_id by filtering on metadata.canvas_patient_id."""
        query = f"""
        query Payors($limit: Int) {{
            payors(limit: $limit) {{
                items {{
                    payor_id
                    metadata(query_list: [
                        {{
                            key: "canvas_patient_id"
                            value: "{patient_id}"
                            operator: EQUAL
                            conjunctive_operator: NONE_NEXT
                        }}
                    ])
                }}
                total_row_count
            }}
        }}
        """

        payload = {"query": query, "variables": {"limit": 1}}

        response = requests.post(self.endpoint, json=payload, headers=self._headers)
        data = response.json()

        if response.status_code != 200 or "errors" in data:
            raise Exception(f"GraphQL error: {response.text}")

        payors = data.get("data", {}).get("payors", {}).get("items", [])

        if payors:
            return payors[0].get("payor_id")

        return None

    def get_payment_methods(self, payor_id: str, limit: int = 5) -> list[PaymentMethod]:
        """Retrieve a list of payment methods for the given payor_id."""
        query = """
        query GetPaymentMethods($limit: Int, $payor_id: String!) {
          paymentMethodTokens(
            limit: $limit,
            query: {
              query_list: [
                {
                  key: "is_active",
                  value: "1",
                  operator: EQUAL,
                  conjunctive_operator: NONE_NEXT
                }
              ]
              sort_list: [
                {
                  key: "exp_date",
                  direction: ASC
                }
              ]
            }
          ) {
            items {
              payment_method_id
              card_brand
              country
              exp_date
              full_name
              is_active
              last_four
              postal_code
              payor(query_list: [
                {
                  key: "payor_id",
                  value: $payor_id,
                  operator: EQUAL,
                  conjunctive_operator: NONE_NEXT
                }
              ]) {
                payor_id
              }
            }
            total_row_count
          }
        }
        """

        variables = {"limit": limit, "payor_id": payor_id}

        payload = {"query": query, "variables": variables}

        response = requests.post(self.endpoint, json=payload, headers=self._headers)
        data = response.json()

        if response.status_code != 200 or "errors" in data:
            raise Exception(f"GraphQL error: {response.text}")

        return [
            PaymentMethod(**item)
            for item in data.get("data", {}).get("paymentMethodTokens", {}).get("items", [])
        ]

    def get_payment_method(self, payment_method_id: str, payor_id: str) -> PaymentMethod | None:
        """Retrieve a list of payment methods for the given payor_id."""
        query = """
        query GetPaymentMethods($limit: Int, $payment_method_id: String!, $payor_id: String!) {
          paymentMethodTokens(
            limit: $limit,
            query: {
              query_list: [
                {
                  key: "payment_method_id",
                  value: $payment_method_id,
                  operator: EQUAL,
                  conjunctive_operator: AND_NEXT
                },
                {
                  key: "is_active",
                  value: "1",
                  operator: EQUAL,
                  conjunctive_operator: NONE_NEXT
                }
              ]
              sort_list: [
                {
                  key: "exp_date",
                  direction: ASC
                }
              ]
            }
          ) {
            items {
              payment_method_id
              card_brand
              country
              exp_date
              full_name
              is_active
              last_four
              postal_code
              payor(query_list: [
                {
                  key: "payor_id",
                  value: $payor_id,
                  operator: EQUAL,
                  conjunctive_operator: NONE_NEXT
                }
              ]) {
                payor_id
              }
            }
            total_row_count
          }
        }
        """

        variables = {"limit": 1, "payor_id": payor_id, "payment_method_id": payment_method_id}

        payload = {"query": query, "variables": variables}

        response = requests.post(self.endpoint, json=payload, headers=self._headers)
        data = response.json()

        if response.status_code != 200 or "errors" in data:
            raise Exception(f"GraphQL error: {response.text}")

        return next(
            (
                PaymentMethod(**item)
                for item in data.get("data", {}).get("paymentMethodTokens", {}).get("items", [])
            ),
            None,
        )

    def create_transaction(self, input_data: TransactionInput) -> Transaction:
        """Create a transaction in PayTheory."""
        # Serialize metadata if provided
        if "metadata" in input_data and isinstance(input_data["metadata"], dict):
            input_data["metadata"] = json.dumps(input_data["metadata"])

        query = """
        mutation CreateTransaction($amount: Int!, $payment_method_id: String!, $merchant_uid: String!) {
          createTransaction(
            amount: $amount,
            payment_method_id: $payment_method_id,
            merchant_uid: $merchant_uid
          ) {
            account_code
            currency
            dispute_status
            failure_reasons
            fee_mode
            fees
            gross_amount
            is_settled
            merchant_uid
            metadata
            net_amount
            parent_id
            payment_method {
              payment_method_id
              payor {
                payor_id
              }
            }
            recurring {
              recurring_id
            }
            reference
            refund_reason {
              reason_code
              reason_details
            }
            refunded_amount
            settlement_batch
            status
            timezone
            transaction_date
            transaction_id
            transaction_type
          }
        }
        """

        payload = {
            "query": query,
            "variables": {
                "amount": int(input_data["amount"] * 100),
                "payment_method_id": input_data["payment_method_id"],
                "merchant_uid": self.merchant_id,
            },
        }

        response = requests.post(self.endpoint, json=payload, headers=self._headers)
        data = response.json()

        if response.status_code != 200 or "errors" in data:
            raise TransactionError(api_response=data)

        return Transaction(**data.get("data", {}).get("createTransaction", {}))

    def disable_payment_method(self, payment_method_id: str) -> bool:
        """Disable a payment method."""
        query = """
        mutation DisablePaymentMethod($payment_method_id: String!, $merchant_uid: ID!) {
            updatePaymentMethodToDisabled(merchant_uid: $merchant_uid, payment_method_id: $payment_method_id)
        }
        """

        payload = {
            "query": query,
            "variables": {"payment_method_id": payment_method_id, "merchant_uid": self.merchant_id},
        }

        response = requests.post(self.endpoint, json=payload, headers=self._headers)
        data = response.json()

        if response.status_code != 200 or "errors" in data:
            raise Exception(f"GraphQL error: {response.text}")

        return data.get("data", {}).get("updatePaymentMethodToDisabled")
