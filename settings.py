import os

from dotenv import load_dotenv

load_dotenv()

INTEGRATION_TEST_URL = os.getenv("INTEGRATION_TEST_URL")
INTEGRATION_TEST_CLIENT_ID = os.getenv("INTEGRATION_TEST_CLIENT_ID")
INTEGRATION_TEST_CLIENT_SECRET = os.getenv("INTEGRATION_TEST_CLIENT_SECRET")

GRAPHQL_ENDPOINT = os.getenv("GRAPHQL_ENDPOINT", "http://localhost:8000/plugins-graphql")

INSTALLED_APPS = ["canvas_sdk"]

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "This value is the key to securing signed data – it is vital you keep this secure, or attackers could use it to generate their own signed values.",
)

# Use BigAutoField for Default Primary Key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CANVAS_SDK_DB_NAME = os.getenv("CANVAS_SDK_DB_NAME", "home-app")
CANVAS_SDK_DB_USERNAME = os.getenv("CANVAS_SDK_DB_USERNAME", "app")
CANVAS_SDK_DB_PASSWORD = os.getenv("CANVAS_SDK_DB_PASSWORD", "app")
CANVAS_SDK_DB_HOST = os.getenv("CANVAS_SDK_DB_HOST", "home-app-db")
CANVAS_SDK_DB_PORT = os.getenv("CANVAS_SDK_DB_PORT", "5432")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": CANVAS_SDK_DB_NAME,
        "USER": CANVAS_SDK_DB_USERNAME,
        "PASSWORD": CANVAS_SDK_DB_PASSWORD,
        "HOST": CANVAS_SDK_DB_HOST,
        "PORT": CANVAS_SDK_DB_PORT,
    }
}
