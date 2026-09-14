# example_sdk_effect_create_questionnaire

Creates a Canvas questionnaire at runtime with the `CreateQuestionnaire` effect.

The plugin exposes two SimpleAPI routes. `POST /create-questionnaire` accepts a screening
definition in the caller's own shape and builds a `QuestionnaireConfig` from it in Python: the
caller never sees Canvas's questionnaire schema, response codes are generated, choices are scored
by position, and a follow-up question is wired to an earlier answer with `enabled_conditions`.
Changing the questions means posting a different body, not releasing a new plugin.

`GET /questionnaire?name=...` reads one back through the data module, including its branching. The
effect is fire and forget, so it cannot tell the plugin what it produced; this route is how a
plugin confirms what was written.

Each item is a single select unless it says otherwise. `"type"` takes `single`, `multi`, `text` or
`date`. Single and multi select carry the caller's `choices`; text and date take none.

## Install

```
canvas install example-plugins/example_sdk_effect_create_questionnaire
canvas config set example_sdk_effect_create_questionnaire api-key="<your key>"
```

## Use

```
curl -X POST \
  https://<instance>/plugin-io/api/example_sdk_effect_create_questionnaire/create-questionnaire \
  -H "Authorization: <your key>" \
  -H "Content-Type: application/json" \
  -d '{
        "title": "Depression screening",
        "code": "44249-1",
        "items": [
          {"prompt": "Little interest or pleasure in doing things?",
           "choices": ["Not at all", "Several days", "More than half the days"]},
          {"prompt": "Which of these apply?", "type": "multi",
           "choices": ["Sleep", "Appetite", "Concentration"]},
          {"prompt": "Describe anything else you would like us to know", "type": "text"},
          {"prompt": "When did this start?", "type": "date"}
        ],
        "follow_up": {"prompt": "How long has this been going on?",
                      "when_answer": "Several days"}
      }'
```

## Read it back

```
curl -G https://<instance>/plugin-io/api/example_sdk_effect_create_questionnaire/questionnaire \
  --data-urlencode "name=Depression screening" \
  -H "Authorization: <your key>"
```

Returns the questionnaire with each question's response type, its options, and the conditions that
decide when it is shown, keyed by code rather than by database id.

## Behavior worth knowing

Questionnaire names are globally unique. Posting a title that is already in use archives the
existing questionnaire, renames it `<title> (v<id>)`, and creates a new one, so each post publishes
a version rather than editing the current one. Drive this from an explicit call like the route
above, not from a handler that fires on a recurring event.

A body the route cannot translate, such as one missing `title` or naming a question type it does
not support, comes back as a 400 saying what was wrong.

`CreateQuestionnaire` validates the configuration when the effect is applied, and reports every
problem with it at once, so a questionnaire the schema rejects also comes back as a 400 rather
than reaching Canvas. Failures on the Canvas side after that are reported to Sentry and are not
visible to the plugin.
