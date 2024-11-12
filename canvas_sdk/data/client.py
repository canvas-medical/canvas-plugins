from typing import Any, cast

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

from settings import GRAPHQL_ENDPOINT


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

    For use in plugins, it is included in the instantiation of Protocol class. This means
    it can simply be referred to as self.client in plugin code.
    """

    def __init__(self) -> None:
        self.client = Client(
            transport=AIOHTTPTransport(url=GRAPHQL_ENDPOINT),
            # TODO: follow the documentation in the link below to specify a
            # cached copy of the schema
            # https://gql.readthedocs.io/en/stable/usage/validation.html#using-a-provided-schema
            fetch_schema_from_transport=False,
        )

    def query(
        self,
        gql_query: str,
        variables: dict[str, Any] | None = None,
        extra_args: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if variables is None:
            query_variables = {}
        else:
            query_variables = variables

        return self.client.execute(
            gql(gql_query),
            variable_values=query_variables,
            extra_args=extra_args,
        )


GQL_CLIENT = _CanvasGQLClient()
