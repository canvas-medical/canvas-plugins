from unittest.mock import MagicMock

from api_samples.routes.hello_world import HelloWorldAPI

from canvas_sdk.effects.simple_api import JSONResponse


class DummyCredentials:
    """Dummy credentials for API key authentication tests."""
    def __init__(self, key):
        self.key = key

def test_hello_world_api_authenticate():
    """Test authentication logic for HelloWorldAPI with correct and incorrect API keys."""
    api = HelloWorldAPI(event=MagicMock())
    api.secrets = {"my-api-key": "secret123"}
    creds_good = DummyCredentials(key="secret123")
    creds_bad = DummyCredentials(key="wrong")
    assert api.authenticate(creds_good) is True
    assert api.authenticate(creds_bad) is False

def test_hello_world_api_get():
    """Test the GET method of HelloWorldAPI returns the expected JSONResponse."""
    api = HelloWorldAPI(event=MagicMock())
    result = api.get()
    assert isinstance(result, list)
    assert isinstance(result[0], JSONResponse)
    import json
    data = json.loads(result[0].content.decode())
    assert data == {"message": "Hello world!"}
