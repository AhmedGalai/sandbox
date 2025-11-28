"""
Basic usage example of the Ollama multi-agent system.

This example demonstrates:
- Creating agents
- Executing agents with context
- Using the orchestrator for parallel execution
- Handling results and errors
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import OllamaClient, SimpleAgent, AgentOrchestrator
from config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def example_direct_client():
    """Example: Using OllamaClient directly for text generation."""
    logger.info("=== Direct Client Example ===")

    client = OllamaClient()

    try:
        # Simple generation
        logger.info("Generating text...")
        response = await client.generate(
            model="llama3.2:3b",
            prompt="What is the meaning of life?",
            temperature=0.7
        )

        logger.info(f"Response: {response}")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await client.close()


async def example_simple_agent():
    """Example: Using SimpleAgent for structured generation."""
    logger.info("\n=== Simple Agent Example ===")

    settings = get_settings()

    # Create an agent
    agent = SimpleAgent(
        name="assistant",
        model=settings.get_model_for_agent("developer")
    )

    try:
        # Execute with context - note: this requires prompt files
        # For demo, we'll catch the error
        logger.info("Executing agent...")

        # Create inline prompt for demo
        response = await agent.client.generate(
            model=agent.model,
            prompt="Explain async/await in Python in 2 paragraphs",
            temperature=0.7
        )

        logger.info(f"Agent response:\n{response}")

        # Check agent status
        status = agent.get_status()
        logger.info(f"Agent status: {status}")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await agent.close()


async def example_parallel_execution():
    """Example: Using orchestrator for parallel agent execution."""
    logger.info("\n=== Parallel Execution Example ===")

    settings = get_settings()

    # Create multiple agents
    agents = [
        SimpleAgent(
            name="researcher",
            model=settings.get_model_for_agent("researcher")
        ),
        SimpleAgent(
            name="developer",
            model=settings.get_model_for_agent("developer")
        ),
        SimpleAgent(
            name="planner",
            model=settings.get_model_for_agent("planner")
        ),
    ]

    # Create orchestrator with concurrency limit
    orchestrator = AgentOrchestrator(max_concurrent=3)

    try:
        # For this demo, we'll use the client directly
        # In production, agents would have prompts
        tasks = [
            (agents[0], {"topic": "machine learning", "style": "academic"}),
            (agents[1], {"task": "write a function", "language": "Python"}),
            (agents[2], {"goal": "organize a project", "timeframe": "quarterly"}),
        ]

        logger.info(f"Starting parallel execution of {len(tasks)} agents...")

        # Note: This will fail without proper prompts - demo only
        # results = await orchestrator.run_agents_parallel(tasks, timeout=60.0)

        # Instead, let's demonstrate orchestrator directly
        for i, (agent, context) in enumerate(tasks):
            task_id = await orchestrator.dispatch_task(
                agent=agent,
                context=context
            )
            logger.info(f"Dispatched task {i+1}: {task_id}")

        # Get summary
        summary = orchestrator.get_summary()
        logger.info(f"Orchestrator summary:\n{summary}")

    finally:
        # Cleanup all agents
        for agent in agents:
            await agent.close()


async def example_list_models():
    """Example: List available Ollama models."""
    logger.info("\n=== Available Models Example ===")

    client = OllamaClient()

    try:
        logger.info("Fetching available models...")
        models = await client.list_models()

        logger.info(f"Found {len(models)} model(s):")
        for model in models:
            logger.info(f"  - {model.get('name', 'Unknown')}")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await client.close()


async def example_settings():
    """Example: Working with settings."""
    logger.info("\n=== Settings Example ===")

    settings = get_settings()

    logger.info(f"Ollama Host: {settings.ollama_host}")
    logger.info(f"Timeout: {settings.timeout}s")
    logger.info(f"Max Concurrent Agents: {settings.max_concurrent_agents}")
    logger.info(f"Default Model: {settings.default_model}")

    # Get model assignments
    logger.info("\nModel Assignments:")
    for agent_name in ["researcher", "developer", "planner", "vision"]:
        model = settings.get_model_for_agent(agent_name)
        logger.info(f"  {agent_name}: {model}")


async def main():
    """Run all examples."""
    logger.info("Starting Ollama Multi-Agent System Examples\n")

    try:
        # Example 1: Settings
        await example_settings()

        # Example 2: Direct client
        await example_direct_client()

        # Example 3: Simple agent
        await example_simple_agent()

        # Example 4: List models
        await example_list_models()

        # Example 5: Parallel execution (demo only)
        await example_parallel_execution()

        logger.info("\nAll examples completed successfully!")

    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
