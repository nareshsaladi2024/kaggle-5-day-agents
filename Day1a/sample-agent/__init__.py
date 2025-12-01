# Agent module - expose root_agent for ADK discovery
from . import agent
from .agent import root_agent

__all__ = ['root_agent', 'agent']
