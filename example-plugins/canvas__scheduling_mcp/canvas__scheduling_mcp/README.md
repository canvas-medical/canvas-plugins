# canvas__scheduling_mcp

A Model Context Protocol server for scheduling, over the Agent Development Kit standard tools. An outside agent finds providers and open times, and, when the operator allows it, finds a patient, reads their appointments, and books, reschedules, and cancels.

## Setup

1. Install the plugin, then set a key: `canvas config set canvas__scheduling_mcp "MCP_API_KEY=<random secret>"`.
2. Point the MCP client at `https://<instance>/plugin-io/api/canvas__scheduling_mcp/mcp` (Streamable HTTP) with the header `Authorization: Bearer <MCP_API_KEY>`.

## What the key may do

`MCP_TOOLS` is a comma-separated list of tool names and `@category` groups. Unset, the key reads the practice only: `@scheduling_reads` (providers and open times), `find_practice_locations`, `find_note_types`, and `find_reason_for_visit_codes`.

Patient tools are opt-in. Listing them, for example `MCP_TOOLS=find_patient, get_patient_demographics, find_appointments, @scheduling_reads`, lets the key search every patient and read the one it finds, and that patient data goes to the outside MCP client and its model. Calls act as Canvas Bot, so the key is practice-level trust: only a client under a business associate agreement should hold it, and a deployment that sends patient data needs Canvas's security and compliance review first. A key makes at most 20 patient searches a minute. Tools about a patient take a required `patient_id` from `find_patient`.

To let the key book, reschedule, and cancel, add `@scheduling_writes`.

## Try it

```sh
curl -X POST "$URL" -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```
