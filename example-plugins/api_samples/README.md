API Samples
===========

## Description

Showcases the usage of the SimpleAPI handler. The sample requests below assume the value of my-api-key is configured to 'test123' in your Canvas instance plugin secrets via the UI or [Console](https://docs.canvasmedical.com/sdk/canvas_cli/#canvas-config-set).

GET
- Adds an API endpoint that returns "Hello World"

Sample request:
```
curl --request GET \
  --url https://xpc-dev.canvasmedical.com/plugin-io/api/api_samples/hello-world \
  --header 'authorization: test123'
```

POST
- Adds an API endpoint that accepts a JSON body and creates a Task in Canvas

Sample request:
```
curl --request POST \
  --url https://xpc-dev.canvasmedical.com/plugin-io/api/api_samples/crm-webhooks/email-bounce \
  --header 'authorization: test123' \
  --header 'content-type: application/json' \
  --data '{
  "mrn": "abc123",
  "email": "test@example.com"
}'
```

PUT
- Adds an API endpoint with a unique identifier in the url that accepts appointment data and calls an Appointment .update() effect.

Sample request:
```
curl --request PUT \
  --url https://xpc-dev.canvasmedical.com/plugin-io/api/api_samples/appointments/1140 \
  --header 'authorization: test123' \
  --header 'content-type: application/json' \
  --data '{
  "meetingLink": "https://www.example.com/video-link",
  "patientId": "d7af3e356368446c85b40a5d6ff7288e"
}'
```

## Configuration

Once installed, see the plugin configuration page to set credentials to make
authenticated requests.
