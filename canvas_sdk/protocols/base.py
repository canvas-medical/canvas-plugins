from typing import Any

from canvas_sdk.data.client import GQL_CLIENT
from canvas_sdk.handlers.base import BaseHandler


class BaseProtocol(BaseHandler):
    """
    The class that protocols inherit from.
    """

    def _beta_run_gql_query(self, query: str, variables: dict | None = None) -> dict[str, Any]:
        return GQL_CLIENT.query(
            query,
            variables=variables,
            extra_args={
                "headers": {
                    "Authorization": f'Bearer {self.secrets["graphql_jwt"]}',
                },
            },
        )
