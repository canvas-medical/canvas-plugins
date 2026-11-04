"""Tools exposed to the DocumentIntakeAgent.

The SDK's standard tools; the manifest grants only the intake ones, which act on the
run's incoming document.
"""

from canvas_sdk.agents import ToolRegistry, standard_tools

tools = ToolRegistry()
tools.extend(standard_tools)
