"""
Example Custom Plugin for Observability

This demonstrates how to create a custom plugin that tracks
agent and tool invocations for observability.

Usage:
    This is a reference example. Import and use in your agents.
"""

import logging
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.plugins.base_plugin import BasePlugin


class CountInvocationPlugin(BasePlugin):
    """A custom plugin that counts agent and tool invocations."""

    def __init__(self) -> None:
        """Initialize the plugin with counters."""
        super().__init__(name="count_invocation")
        self.agent_count: int = 0
        self.tool_count: int = 0
        self.llm_request_count: int = 0

    # Callback 1: Runs before an agent is called
    async def before_agent_callback(
        self, *, agent: BaseAgent, callback_context: CallbackContext
    ) -> None:
        """Count agent runs."""
        self.agent_count += 1
        logging.info(f"[Plugin] Agent run count: {self.agent_count}")

    # Callback 2: Runs before a model is called
    async def before_model_callback(
        self, *, callback_context: CallbackContext, llm_request: LlmRequest
    ) -> None:
        """Count LLM requests."""
        self.llm_request_count += 1
        logging.info(f"[Plugin] LLM request count: {self.llm_request_count}")

    # Callback 3: Runs before a tool is called
    async def before_tool_callback(
        self, *, callback_context: CallbackContext, tool_name: str, tool_input: dict
    ) -> None:
        """Count tool calls."""
        self.tool_count += 1
        logging.info(f"[Plugin] Tool call count: {self.tool_count}")
        logging.info(f"[Plugin] Tool: {tool_name}, Input: {tool_input}")

    def get_stats(self) -> dict:
        """Get current statistics."""
        return {
            "agent_count": self.agent_count,
            "tool_count": self.tool_count,
            "llm_request_count": self.llm_request_count,
        }


# Example usage:
# from Day4a.observability_plugin_example import CountInvocationPlugin
# 
# plugin = CountInvocationPlugin()
# runner = InMemoryRunner(
#     agent=my_agent,
#     plugins=[plugin]
# )
# 
# # After running agent
# stats = plugin.get_stats()
# print(f"Stats: {stats}")

