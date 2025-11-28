"""
Specialized agent implementations for multi-agent system.

This module provides specialized agents for different tasks:
- ResearcherAgent: Information synthesis and research
- DeveloperAgent: Code generation and development
- PlannerAgent: Strategic planning and project management
- VisionAgent: Image analysis and visual understanding

Usage:
    from agents import ResearcherAgent, DeveloperAgent, PlannerAgent, VisionAgent
    from agents import AgentFactory

    # Create agents directly
    researcher = ResearcherAgent()
    developer = DeveloperAgent()
    planner = PlannerAgent()
    vision = VisionAgent()

    # Or use factory for dynamic creation
    factory = AgentFactory()
    agent = factory.create_agent("researcher", config={"model": "qwen2.5:7b"})
"""

from .agent_factory import AgentFactory
from .developer_agent import DeveloperAgent
from .planner_agent import PlannerAgent
from .researcher_agent import ResearcherAgent
from .vision_agent import VisionAgent

# Agent registry for type mapping
AGENT_REGISTRY = {
    "researcher": ResearcherAgent,
    "developer": DeveloperAgent,
    "planner": PlannerAgent,
    "vision": VisionAgent,
}

__all__ = [
    "ResearcherAgent",
    "DeveloperAgent",
    "PlannerAgent",
    "VisionAgent",
    "AgentFactory",
    "AGENT_REGISTRY",
]
