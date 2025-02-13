import os
import sys
from typing import cast
from urllib import parse

from dotenv import load_dotenv
from env_tools import env_to_bool

load_dotenv()

ENV = os.getenv("ENV", "development")
IS_PRODUCTION = ENV == "production"
IS_TESTING = env_to_bool("IS_TESTING", "pytest" in sys.argv[0] or sys.argv[0] == "-c")
CUSTOMER_IDENTIFIER = os.getenv("CUSTOMER_IDENTIFIER", "local")
APP_NAME = os.getenv("APP_NAME")

INTEGRATION_TEST_URL = os.getenv("INTEGRATION_TEST_URL")
INTEGRATION_TEST_CLIENT_ID = os.getenv("INTEGRATION_TEST_CLIENT_ID")
INTEGRATION_TEST_CLIENT_SECRET = os.getenv("INTEGRATION_TEST_CLIENT_SECRET")

GRAPHQL_ENDPOINT = os.getenv("GRAPHQL_ENDPOINT", "http://localhost:8000/plugins-graphql")
REDIS_ENDPOINT = os.getenv("REDIS_ENDPOINT", f"redis://{APP_NAME}-redis:6379")

INSTALLED_APPS = [
    "canvas_sdk.v1",
]

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "This value is the key to securing signed data – it is vital you keep this secure, or attackers could use it to generate their own signed values.",
)

# Use BigAutoField for Default Primary Key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "home-app",
        "USER": os.getenv("CANVAS_SDK_DATABASE_ROLE", "app"),
        "PASSWORD": os.getenv("CANVAS_SDK_DATABASE_ROLE_PASSWORD", "app"),
        "HOST": "home-app-db",
        "PORT": "5432",
    }
}

if os.getenv("DATABASE_URL"):
    # Override the specified values if DATABASE_URL is set (it will always be
    # set in production) to specify the database name, host and port specified
    # by Aptible
    parsed_url = parse.urlparse(os.getenv("DATABASE_URL"))

    DATABASES["default"]["NAME"] = cast(str, parsed_url.path[1:])
    DATABASES["default"]["HOST"] = cast(str, parsed_url.hostname)
    DATABASES["default"]["PORT"] = f"{parsed_url.port}"

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
MEDIA_S3_BUCKET_NAME = os.getenv("MEDIA_S3_BUCKET_NAME", "canvas-client-media")

PLUGIN_RUNNER_SIGNING_KEY = os.getenv("PLUGIN_RUNNER_SIGNING_KEY", "")

PLUGIN_DIRECTORY = os.getenv(
    "PLUGIN_DIRECTORY",
    (
        "/plugin-runner/custom-plugins"
        if IS_PRODUCTION
        else "./plugin_runner/tests/data/plugins"
        if IS_TESTING
        else "./custom-plugins"
    ),
)
PLUGINS_PUBSUB_CHANNEL = os.getenv("PLUGINS_PUBSUB_CHANNEL", default="plugins")
CHANNEL_NAME = f"{CUSTOMER_IDENTIFIER}:{PLUGINS_PUBSUB_CHANNEL}"
MANIFEST_FILE_NAME = "CANVAS_MANIFEST.json"

SECRETS_FILE_NAME = "SECRETS.json"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": False,
        "OPTIONS": {},
    },
]
