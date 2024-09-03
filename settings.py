import os

from dotenv import load_dotenv

load_dotenv()

INTEGRATION_TEST_URL = os.getenv("INTEGRATION_TEST_URL")
INTEGRATION_TEST_CLIENT_ID = os.getenv("INTEGRATION_TEST_CLIENT_ID")
INTEGRATION_TEST_CLIENT_SECRET = os.getenv("INTEGRATION_TEST_CLIENT_SECRET")

PLUGIN_RUNNER_DAL_TARGET = os.getenv("PLUGIN_RUNNER_DAL_TARGET")

GRAPHQL_ENDPOINT = os.getenv("GRAPHQL_ENDPOINT", 'http://localhost:8000/plugins/internal-graphql')
