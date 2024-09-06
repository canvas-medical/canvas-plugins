import os

from dotenv import load_dotenv

load_dotenv()

INTEGRATION_TEST_URL = os.getenv("INTEGRATION_TEST_URL")
INTEGRATION_TEST_CLIENT_ID = os.getenv("INTEGRATION_TEST_CLIENT_ID")
INTEGRATION_TEST_CLIENT_SECRET = os.getenv("INTEGRATION_TEST_CLIENT_SECRET")

PLUGIN_RUNNER_DAL_TARGET = os.getenv("PLUGIN_RUNNER_DAL_TARGET")

GRAPHQL_ENDPOINT = os.getenv("GRAPHQL_ENDPOINT", "http://localhost:8000/plugins-graphql")

INSTALLED_APPS = ["canvas_sdk"]

# SECURITY WARNING: Modify this secret key if using in production!
SECRET_KEY = "abc123"

# Use BigAutoField for Default Primary Key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "home-app",
        "USER": "app",
        "PASSWORD": "app",
        "HOST": "localhost",
        "PORT": "5435",
    }
}
