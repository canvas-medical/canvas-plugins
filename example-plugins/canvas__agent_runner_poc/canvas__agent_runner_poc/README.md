canvas__agent_runner_poc
========================

## Description

Reference agents for the Canvas Agent Runner Framework.

- **LongitudinalCareAdvisor** runs when a note is locked. It reviews the encounter against prior visits' open protocol cards and adds cards for outstanding follow-up.
- **ChartChat** is a chat application on the patient chart. It keeps each clinician's conversation with a patient's chart in a `Conversation` row, and composes sub-agents for a chart summary and a pre-visit brief. Commands it proposes are staged onto the clinician's open note.
- **ClaimsChat** is a chat application for billing staff, over the claims queue or a single claim.
- **DocumentIntake** reads each document that arrives on a listed channel and suggests its patient, type, and report values on the review form.

Each agent's tool grant and the tools that wait for a user's approval are in `CANVAS_MANIFEST.json` under `components.agents`.

## Configuration

Set these in the plugin's configuration in the Canvas admin:

- `INFERENCE_GATEWAY_KEY` (sensitive): this plugin's key for the inference gateway.
- `INTAKE_CHANNELS`: comma-separated document channels DocumentIntake reads, such as `fax`. With none listed, intake is off.
