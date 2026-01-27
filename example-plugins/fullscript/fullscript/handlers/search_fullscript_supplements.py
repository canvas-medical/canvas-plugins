import json

from canvas_sdk.commands.constants import CodeSystems
from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler

# Import the helper methods from the API
from fullscript.api.fullscript_api import FullscriptAPI
from logger import log


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

        variants = []
        post_processed_results = results.copy()

        result = FullscriptAPI.fetch_products(
            access_token, query, self.secrets["FULLSCRIPT_SEARCH_PAGE_SIZE"]
        )

        if result.get("success"):
            variants = result.get("variants", [])
            log.info(f"!! Found {len(variants)} Fullscript products")
        else:
            log.warning(f"!! Fullscript search failed: {result.get('error')}")

        log.info(f"!! {variants}")

        for variant in variants:
            product_id = variant.get("id", {})
            name = variant.get("product_name", "")
            brand_name = variant.get("product_brand", "")
            code = f"fullscript-{product_id}"
            quantity_description = variant.get("unit_of_measure", "")
            availability = variant.get("availability", "")
            units = variant.get("units", 0)

            product_name = f"{brand_name} - {name}"

            if units != 0:
                product_name = f"{product_name} - {units} {quantity_description}"

            annotations = ["Supp 🌱"]

            if availability.lower() != "in stock":
                annotations.append("Out of Stock ❌")

            post_processed_results.insert(
                0,
                {
                    "text": product_name,
                    "annotations": annotations,
                    "value": code,
                    "extra": {
                        "coding": [
                            {
                                "code": code,
                                "display": product_name,
                                "system": CodeSystems.FULLSCRIPT.value,
                            }
                        ],
                        "clinical_quantities": [
                            {
                                "erx_quantity": units,
                                "representative_ndc": "",
                                "clinical_quantity_description": quantity_description,
                                "erx_ncpdp_script_quantity_qualifier_code": "",
                                "erx_ncpdp_script_quantity_qualifier_description": quantity_description,
                            }
                        ],
                    },
                },
            )

        log.info(f"!! Products: {post_processed_results[:12]}")

        log.info(f"!! Returning {len(post_processed_results)} total results")

        return [
            Effect(
                type=EffectType.AUTOCOMPLETE_SEARCH_RESULTS,
                payload=json.dumps(post_processed_results),
            )
        ]
