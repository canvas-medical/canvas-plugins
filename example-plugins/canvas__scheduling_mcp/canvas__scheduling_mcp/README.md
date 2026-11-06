# canvas__scheduling_mcp

A Model Context Protocol server for scheduling, over the Agent Runner Framework standard tools. An outside agent finds a patient, providers, and open times, reads the patient's appointments, and, when the operator allows it, books, reschedules, and cancels.

## Setup

1. Install the plugin, then set a key: `canvas config set canvas__scheduling_mcp "MCP_API_KEY=<random secret>"`.
2. Point the MCP client at `https://<instance>/plugin-io/api/canvas__scheduling_mcp/mcp` (Streamable HTTP) with the header `Authorization: Bearer <MCP_API_KEY>`.

## What the key may do

`MCP_TOOLS` is a comma-separated list of tool names and `@category` groups. Unset, the key gets reads only: `find_patient`, `get_patient_demographics`, `find_appointments`, `@scheduling_reads`, `find_practice_locations`, `find_note_types`, and `find_reason_for_visit_codes`. To let it book, add the writes, for example `MCP_TOOLS=find_patient, find_appointments, @scheduling_reads, @scheduling_writes`.

Calls act as Canvas Bot, so the key is practice-level trust: it can find any patient. Tools about a patient take a required `patient_id` from `find_patient`.

## Try it

```sh
curl -X POST "$URL" -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```
