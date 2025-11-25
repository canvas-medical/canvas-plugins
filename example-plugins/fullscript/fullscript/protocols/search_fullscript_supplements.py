import json

from canvas_sdk.commands.constants import CodeSystems
from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler

# Import the helper methods from the API
from fullscript.api.fullscript_api import FullscriptAPI
from logger import log


class SearchFullscriptSupplements(BaseHandler):
    """Protocol to add Fullscript supplement products to medication statement search results."""

    RESPONDS_TO = EventType.Name(EventType.MEDICATION_STATEMENT__MEDICATION__POST_SEARCH)

    def compute(self) -> list[Effect]:
        """Fetch Fullscript products and add them to the medication search autocomplete results."""
        log.info("!! Fullscript search protocol")

        user_id = self.context.get("user", {}).get("staff", None)
        query = self.context.get("search_term", None)
        results = self.context.get("results", [])

        log.info(f"!! USER {user_id}")
        log.info(f"!! QUERY {query}")

        if not user_id:
            log.warning("!! No user_id available, skipping Fullscript search")
            return [
                Effect(type=EffectType.AUTOCOMPLETE_SEARCH_RESULTS, payload=json.dumps(results))
            ]

        # Get valid access token (handles refresh if needed)
        client_id = self.secrets["FULLSCRIPT_CLIENT_ID"]
        client_secret = self.secrets["FULLSCRIPT_CLIENT_SECRET"]

        token_result = FullscriptAPI.get_valid_access_token(
            user_id=user_id, client_id=client_id, client_secret=client_secret
        )

        if not token_result.get("success"):
            log.info(f"!! Failed to get valid token: {token_result.get('error')}")
            return [
                Effect(type=EffectType.AUTOCOMPLETE_SEARCH_RESULTS, payload=json.dumps(results))
            ]

        access_token = token_result.get("access_token", "")

        fullscript_products = []
        post_processed_results = results.copy()

        result = FullscriptAPI.fetch_products(
            access_token, query, self.secrets["FULLSCRIPT_SEARCH_PAGE_SIZE"]
        )

        if result.get("success"):
            fullscript_products = result.get("products", [])
            log.info(f"!! Found {len(fullscript_products)} Fullscript products")
        else:
            log.warning(f"!! Fullscript search failed: {result.get('error')}")

        for product in fullscript_products:
            sku = product.get("primary_variant", {}).get("sku", "")
            name = product.get("name", "")
            code = f"fullscript-{sku}"

            post_processed_results.insert(
                0,
                {
                    "text": name,
                    "annotations": ["Supp 🌱"],
                    "value": code,
                    "extra": {
                        "coding": [{"code": code, "display": name, "system": "UNSTRUCTURED"}]
                    },
                },
            )

        log.info(f"!! Returning {len(post_processed_results)} total results")

        return [
            Effect(
                type=EffectType.AUTOCOMPLETE_SEARCH_RESULTS,
                payload=json.dumps(post_processed_results),
            )
        ]


class SearchFullscriptSupplementsForPrescribe(BaseHandler):
    """Protocol to add Fullscript supplement products to prescribe search results with clinical quantities."""

    RESPONDS_TO = EventType.Name(EventType.PRESCRIBE__PRESCRIBE__POST_SEARCH)

    def compute(self) -> list[Effect]:
        """Fetch Fullscript products and add them to the prescribe autocomplete with clinical quantities."""
        log.info("!! Fullscript search protocol")

        user_id = self.context.get("user", {}).get("staff", None)
        query = self.context.get("search_term", None)
        results = self.context.get("results", [])

        log.info(f"!! USER {user_id}")
        log.info(f"!! QUERY {query}")

        if not user_id:
            log.warning("!! No user_id available, skipping Fullscript search")
            return [
                Effect(type=EffectType.AUTOCOMPLETE_SEARCH_RESULTS, payload=json.dumps(results))
            ]

        # Get valid access token (handles refresh if needed)
        client_id = self.secrets["FULLSCRIPT_CLIENT_ID"]
        client_secret = self.secrets["FULLSCRIPT_CLIENT_SECRET"]

        token_result = FullscriptAPI.get_valid_access_token(
            user_id=user_id, client_id=client_id, client_secret=client_secret
        )

        if not token_result.get("success"):
            log.info(f"!! Failed to get valid token: {token_result.get('error')}")
            return [
                Effect(type=EffectType.AUTOCOMPLETE_SEARCH_RESULTS, payload=json.dumps(results))
            ]

        access_token = token_result.get("access_token", "")

        fullscript_products = []
        post_processed_results = results.copy()

        result = FullscriptAPI.fetch_products(
            access_token, query, self.secrets["FULLSCRIPT_SEARCH_PAGE_SIZE"]
        )

        if result.get("success"):
            fullscript_products = result.get("products", [])
            log.info(f"!! Found {len(fullscript_products)} Fullscript products")
        else:
            log.warning(f"!! Fullscript search failed: {result.get('error')}")

        log.info(f"!! {fullscript_products}")

        for product in fullscript_products:
            sku = product.get("primary_variant", {}).get("sku", "")
            name = product.get("name", "")
            code = f"fullscript-{sku}"
            quantity_description = product.get("primary_variant", {}).get("unit_of_measure", "")
            units = product.get("primary_variant", {}).get("units", "")

            post_processed_results.insert(
                0,
                {
                    "text": name,
                    "annotations": ["Supp 🌱"],
                    "value": code,
                    "extra": {
                        "coding": [
                            {
                                "code": code,
                                "display": name,
                                "system": CodeSystems.FDB,  # TODO: Using FDB as a placeholder
                            }
                        ],
                        "clinical_quantities": [
                            {
                                "erx_quantity": units,
                                "representative_ndc": "",
                                "clinical_quantity_description": quantity_description,
                                "erx_ncpdp_script_quantity_qualifier_code": "F111",  # TODO: Map properly
                                "erx_ncpdp_script_quantity_qualifier_description": quantity_description,
                            }
                        ],
                    },
                },
            )

        log.info(f"!! Returning {len(post_processed_results)} total results")

        return [
            Effect(
                type=EffectType.AUTOCOMPLETE_SEARCH_RESULTS,
                payload=json.dumps(post_processed_results),
            )
        ]
