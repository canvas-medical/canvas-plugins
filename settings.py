import os
import sys
from pathlib import Path
from urllib import parse

from dotenv import load_dotenv
from env_tools import env_to_bool

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.resolve()

ENV = os.getenv("ENV", "development")
IS_PRODUCTION = ENV == "production"
IS_PRODUCTION_CUSTOMER = env_to_bool("IS_PRODUCTION_CUSTOMER", IS_PRODUCTION)
IS_TESTING = env_to_bool("IS_TESTING", "pytest" in sys.argv[0] or sys.argv[0] == "-c")
IS_SCRIPT = env_to_bool("IS_SCRIPT", "plugin_runner.py" not in sys.argv[0])
CUSTOMER_IDENTIFIER = os.getenv("CUSTOMER_IDENTIFIER", "local")
APP_NAME = os.getenv("APP_NAME")

INTEGRATION_TEST_URL = os.getenv("INTEGRATION_TEST_URL")
INTEGRATION_TEST_CLIENT_ID = os.getenv("INTEGRATION_TEST_CLIENT_ID")
INTEGRATION_TEST_CLIENT_SECRET = os.getenv("INTEGRATION_TEST_CLIENT_SECRET")

GRAPHQL_ENDPOINT = os.getenv("GRAPHQL_ENDPOINT", "http://localhost:8000/plugins-graphql")
REDIS_ENDPOINT = os.getenv("REDIS_ENDPOINT", f"redis://{APP_NAME}-redis:6379")


METRICS_ENABLED = env_to_bool("PLUGINS_METRICS_ENABLED", not IS_SCRIPT)

INSTALLED_APPS = [
    "canvas_sdk.v1",
]

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

if os.getenv("DATABASE_URL"):
    parsed_url = parse.urlparse(os.getenv("DATABASE_URL"))

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": parsed_url.path[1:],
            "USER": os.getenv("CANVAS_SDK_DATABASE_ROLE"),
            "PASSWORD": os.getenv("CANVAS_SDK_DATABASE_ROLE_PASSWORD"),
            "HOST": parsed_url.hostname,
            "PORT": parsed_url.port,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": CANVAS_SDK_DB_NAME,
            "USER": CANVAS_SDK_DB_USERNAME,
            "PASSWORD": CANVAS_SDK_DB_PASSWORD,
            "HOST": CANVAS_SDK_DB_HOST,
            "PORT": CANVAS_SDK_DB_PORT,
        }
    }

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
MEDIA_S3_BUCKET_NAME = os.getenv("MEDIA_S3_BUCKET_NAME", "canvas-client-media")

# ONTOLOGIES_SIGNING_KEY = os.getenv("ONTOLOGIES_SIGNING_KEY", "")
PLUGIN_RUNNER_SIGNING_KEY = os.getenv("PLUGIN_RUNNER_SIGNING_KEY", "")
# SCIENCE_SIGNING_KEY = os.getenv("SCIENCE_SIGNING_KEY", "")

PLUGIN_DIRECTORY = os.getenv(
    "PLUGIN_DIRECTORY",
    (
        "/plugin-runner/custom-plugins"
        if IS_PRODUCTION
        else (BASE_DIR / "plugin_runner/tests/data/plugins").as_posix()
        if IS_TESTING
        else (BASE_DIR / "custom-plugins").as_posix()
    ),
)
PLUGINS_PUBSUB_CHANNEL = os.getenv("PLUGINS_PUBSUB_CHANNEL", default="plugins")
CHANNEL_NAME = f"{CUSTOMER_IDENTIFIER}:{PLUGINS_PUBSUB_CHANNEL}"
MANIFEST_FILE_NAME = "CANVAS_MANIFEST.json"

SECRETS_FILE_NAME = "SECRETS.json"

SENTRY_DSN = os.getenv("SENTRY_DSN")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": False,
        "OPTIONS": {},
    },
]
