"""The probes' tools: the SDK's standard tools, of which the manifest grants only the
configuration reads, which need no patient and read little.
"""

from canvas_sdk.agents import ToolRegistry, standard_tools

tools = ToolRegistry()
tools.extend(standard_tools)
