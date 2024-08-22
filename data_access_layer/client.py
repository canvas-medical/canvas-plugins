from typing import Any, cast

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

from settings import DAL_GRAPHQL_AUTH_KEY, DAL_GRAPHQL_ENDPOINT


class _CanvasGQLClient:
    """
    This is a GraphQL client that can be used to query home-app in order to fetch data for use in plugins.

    Usage Examples:

    A query with no parameters:

    TEST_QUERY_NO_PARAMS = '''
      query PatientsAll {
        patients {
          edges {
            node {
              firstName
              lastName
              birthDate
            }
          }
        }
      }
    '''

    client = _CanvasGQLClient()
    result = client.query(TEST_QUERY_NO_PARAMS)
    print(result) # returns dictionary

    A query with parameters:

    TEST_QUERY_WITH_PARAMS = '''
        query PatientGet($patientKey: String!) {
          patient(patientKey: $patientKey) {
            firstName
            lastName
            birthDate
          }
        }
    '''

    client = _CanvasGQLClient()
    result = client.query(TEST_QUERY_NO_PARAMS)
    print(result)
    """

    def __init__(self) -> None:
        transport = AIOHTTPTransport(
            url=cast(str, DAL_GRAPHQL_ENDPOINT),
            headers={"Authorization": f"{cast(str, DAL_GRAPHQL_AUTH_KEY)}"},
        )
        self.client = Client(transport=transport, fetch_schema_from_transport=True)

    def query(self, gql_query: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if params is None:
            query_params = {}
        else:
            query_params = params

        result = self.client.execute(gql(gql_query), variable_values=query_params)
        return result


GQL_CLIENT = _CanvasGQLClient()
