# Charting API Examples

This example plugin provides several examples of APIs you might define when
automating charting in Canvas.

- Notes
  - Creating a note
  - Getting information about a note
  - Searching for notes by patient, type, and date of service
  - Adding billing line items to a note
- Commands
  - Creating a command
  - Creating multiple commands from a single request
  - Creating a command and committing it in a single request

## Configuration

All of the example endpoints in this plugin are protected with [API key
authentication](https://docs.canvasmedical.com/sdk/handlers-simple-api-http/#api-key-1).
Once installed, you'll need to set the `simpleapi-api-key` value on the plugin's
configuration page in your EHR.

## Endpoint Documentation

### Search Notes

`GET /plugin-io/api/charting_api_examples/notes/`

This endpoint allows the retrieval of an optionally filtered set of notes. The results are paginated, and the client can exert some control over the page size. The response body will include an attribute, `next_page`, which will either contain a URL to the next page of the same filtered set or be `null`, indicating there are no more records to fetch.

#### Optional query parameters:

##### limit

*int*

Determines the number of results to return per page.

- If unspecified, the default is 10.
- If a number less than 1 is specified, 1 will be used.
- If a number greate than 100 is specified, 100 will be used.

##### offset

*int*

Number of records to skip with returning results. When used with **limit**, this enables the pagination of results.

- If unspecified, the default is 0.
- If a number less than 0 is specified, 0 will be used.


##### patient_id

*str*

Filters the notes returned to just those associated with the given patient.

##### note_type

*coding*

You can search by just the code value or you can search by the
system and code in the format "system|code" (e.g. `http://snomed.info/sct|308335008`).

##### datetime_of_service

*iso8601 formatted datetime string*

Exact match for notes with the given datetime.

##### datetime_of_service__gt

*iso8601 formatted datetime string*

Filter to notes occurring after the given datetime.

##### datetime_of_service__gte

*iso8601 formatted datetime string*

Filter to notes occurring at or after the given datetime.

##### datetime_of_service__lt

*iso8601 formatted datetime string*

Filter to notes occurring before the given datetime.

##### datetime_of_service__lte

*iso8601 formatted datetime string*

Filter to notes occurring at or before the given datetime.

#### Example Request

```bash
curl --request GET \
  --url 'https://training.canvasmedical.com/plugin-io/api/charting_api_examples/notes/?limit=2&offset=4' \
  --header 'Authorization: <your-api-key-goes-here>'
```

#### Example Response

```json
{
  "next_page": "https://training.canvasmedical.com/plugin-io/api/charting_api_examples/notes/?limit=2&offset=6",
  "count": 2,
  "notes": [
    {
      "id": "10ff2047-6301-4ab4-81cd-b500e7df8ef7",
      "patient_id": "5350cd20de8a470aa570a852859ac87e",
      "provider_id": "5843991a8c934118ab4f424c839b340f",
      "datetime_of_service": "2025-02-21 23:31:45.627894+00:00",
      "note_type": {
        "id": "c5df4f03-58e4-442b-ad6c-0d3dadc6b726",
        "name": "Office visit",
        "coding": {
          "display": "Office Visit",
          "code": "308335008",
          "system": "http://snomed.info/sct"
        }
      }
    },
    {
      "id": "4dba128f-96cc-4dd0-814b-a064bfdcde7e",
      "patient_id": "5350cd20de8a470aa570a852859ac87e",
      "provider_id": "336159560091471cb6b0e149d9054697",
      "datetime_of_service": "2025-02-21 23:31:45.928071+00:00",
      "note_type": {
        "id": "c5df4f03-58e4-442b-ad6c-0d3dadc6b726",
        "name": "Office visit",
        "coding": {
          "display": "Office Visit",
          "code": "308335008",
          "system": "http://snomed.info/sct"
        }
      }
    }
  ]
}
```

### Read a Note

`GET /plugin-io/api/charting_api_examples/notes/<note-id>/`

#### Example Response

```json
{
  "note": {
    "id": "1490b8db-00a9-47d9-9170-ec142460b586",
    "patient_id": "5350cd20de8a470aa570a852859ac87e",
    "provider_id": "6b33e69474234f299a56d480b03476d3",
    "datetime_of_service": "2025-10-02 23:30:00+00:00",
    "state": "NEW",
    "note_type": {
      "id": "c5df4f03-58e4-442b-ad6c-0d3dadc6b726",
      "name": "Office visit",
      "coding": {
        "display": "Office Visit",
        "code": "308335008",
        "system": "http://snomed.info/sct"
      }
    }
  }
}
```

### Create a Note

`POST /plugin-io/api/charting_api_examples/notes/`

#### Example Request Body

```json
{
  "practice_location_id": "306b19f0-231a-4cd4-ad2d-a55c885fd9f8",
  "note_type_id": "c5df4f03-58e4-442b-ad6c-0d3dadc6b726",
  "patient_id": "5350cd20de8a470aa570a852859ac87e",
  "provider_id": "6b33e69474234f299a56d480b03476d3",
  "datetime_of_service": "2025-10-04 23:30:00",
  "title": "My cool note"
}
```

### Add Billing Line Item to a Note

`POST /plugin-io/api/charting_api_examples/notes/<note-id>/billing_line_items/`

#### Example Request Body

```json
{
  "cpt_code": "98008"
}
```

### Add a Diagnose Command to a Note

`POST /plugin-io/api/charting_api_examples/notes/<note-id>/diagnose/`

`icd10_code` is required, but `committed` may be true, false, or omitted entirely.

#### Example Request Body

```json
{
  "icd10_code": "E119",
  "committed": true
}
```

### Add Multiple Commands to a Note

`POST /plugin-io/api/charting_api_examples/notes/<note-id>/prechart/`

#### Example Request Body

```json
null
```
