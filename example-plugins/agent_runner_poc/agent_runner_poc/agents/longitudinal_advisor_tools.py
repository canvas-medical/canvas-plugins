"""Tools exposed to the LongitudinalCareAdvisor agent.

The full surface comes from :data:`canvas_sdk.agents.standard_tools` via
``tools.extend(standard_tools)`` below — clinical reads (find_*,
get_patient_demographics) and the protocol-card lifecycle
(add_or_update_protocol_card + find_protocol_cards) the agent uses
for cross-visit recommendation tracking.

The trigger handler in ``longitudinal_trigger.py`` sets ``ctx["note_id"]``
from the trigger payload so any future originate-on-note tools also
resolve cleanly. Today the agent is read+ProtocolCard only.
"""

from canvas_sdk.agents import ToolRegistry, standard_tools

tools = ToolRegistry()
tools.extend(standard_tools)
