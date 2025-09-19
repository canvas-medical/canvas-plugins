from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import APIKeyCredentials, SimpleAPIRoute

# GET /plugin-io/api/api_samples/hello-world
# Headers: "Authorization <your value for 'my-api-key'>"

class HelloWorldAPI(SimpleAPIRoute):
    """API endpoint that returns 'Hello world!'."""
    PATH = "/hello-world"

    def authenticate(self, credentials: APIKeyCredentials) -> bool:
        """Simple API key authentication."""
        return credentials.key == self.secrets["my-api-key"]

    def get(self) -> list[Response]:
        """Return a message."""
        return [JSONResponse({"message": "Hello world!"})]
