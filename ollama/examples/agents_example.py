"""
Examples demonstrating the usage of specialized agents.

This module shows how to use ResearcherAgent, DeveloperAgent,
PlannerAgent, and VisionAgent for various tasks.
"""

import asyncio
import logging
from pathlib import Path

from agents import ResearcherAgent, DeveloperAgent, PlannerAgent, VisionAgent
from agents import AgentFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def example_researcher_agent():
    """Example: Using ResearcherAgent for information synthesis."""
    logger.info("=" * 60)
    logger.info("EXAMPLE 1: ResearcherAgent")
    logger.info("=" * 60)

    researcher = ResearcherAgent()

    context = {
        "Topic": "Machine Learning in Production",
        "Key Questions": [
            "What are best practices for ML in production?",
            "What are common pitfalls?",
        ],
        "Known Information": "Basic knowledge of ML and software engineering",
        "Sources to Prioritize": "Recent research papers, industry best practices",
        "Desired Output Format": "Structured summary with key points",
        "task": "Research and synthesize information about deploying "
        "machine learning systems in production environments",
    }

    try:
        result = await researcher.execute(context)
        print("\nResearch Result:")
        print("-" * 40)
        print(result[:500] + "..." if len(result) > 500 else result)
    except Exception as e:
        logger.error(f"Research failed: {e}")

    await researcher.close()


async def example_developer_agent():
    """Example: Using DeveloperAgent for code generation."""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 2: DeveloperAgent")
    logger.info("=" * 60)

    developer = DeveloperAgent()

    context = {
        "Project Name": "User Authentication API",
        "Technology Stack": "Python, FastAPI, SQLAlchemy",
        "Codebase Style": "PEP 8, type hints, docstrings",
        "Architectural Patterns": "Repository pattern, dependency injection",
        "Testing Framework": "pytest with fixtures",
        "task": "Generate a user authentication endpoint that validates "
        "email and password with proper error handling",
    }

    try:
        result = await developer.execute(context)
        print("\nDeveloper Result:")
        print("-" * 40)
        print(result[:500] + "..." if len(result) > 500 else result)
    except Exception as e:
        logger.error(f"Development task failed: {e}")

    await developer.close()


async def example_planner_agent():
    """Example: Using PlannerAgent for project planning."""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 3: PlannerAgent")
    logger.info("=" * 60)

    planner = PlannerAgent()

    context = {
        "Project Name": "Data Processing Pipeline",
        "Project Goals": [
            "Process 1M records daily",
            "Reduce processing time from 8h to 2h",
            "Improve data quality by 20%",
        ],
        "Available Resources": "2 data engineers, 4 core CPU, 16GB RAM",
        "Timeline": "3 months",
        "Key Milestones": "MVP in 6 weeks, Production in 3 months",
        "task": "Create a detailed project roadmap with nested steps, "
        "identifying dependencies and potential blockers",
    }

    try:
        result = await planner.execute(context)
        print("\nPlanning Result:")
        print("-" * 40)
        print(result[:500] + "..." if len(result) > 500 else result)
    except Exception as e:
        logger.error(f"Planning failed: {e}")

    await planner.close()


async def example_vision_agent():
    """Example: Using VisionAgent for image analysis."""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 4: VisionAgent")
    logger.info("=" * 60)

    vision = VisionAgent()

    # Create a simple test image if it doesn't exist
    test_image_path = Path("/tmp/test_image.png")

    if not test_image_path.exists():
        logger.info("Creating test image for demonstration...")
        try:
            from PIL import Image

            # Create a simple test image
            img = Image.new("RGB", (100, 100), color="red")
            img.save(test_image_path)
            logger.info(f"Test image created at {test_image_path}")
        except ImportError:
            logger.warning(
                "PIL/Pillow not available, skipping vision example"
            )
            await vision.close()
            return

    context = {
        "Image Path": str(test_image_path),
        "Analysis Focus": "Colors and composition",
        "Specific Questions": "What colors are present?",
        "Expected Output": "Detailed visual analysis",
        "Detail Level": "High",
        "task": "Analyze the image and describe its visual properties",
    }

    try:
        result = await vision.execute(context)
        print("\nVision Analysis Result:")
        print("-" * 40)
        print(result[:500] + "..." if len(result) > 500 else result)
    except Exception as e:
        logger.error(f"Vision analysis failed: {e}")

    await vision.close()


async def example_agent_factory():
    """Example: Using AgentFactory for dynamic agent creation."""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 5: AgentFactory")
    logger.info("=" * 60)

    factory = AgentFactory()

    # List available agents
    print("\nAvailable agents:")
    agents_info = factory.get_available_agents()
    for agent_type, info in agents_info.items():
        print(f"  - {agent_type}: {info['model']}")
        print(f"    {info['description']}")

    # Create an agent dynamically
    try:
        researcher = factory.create_agent(
            "researcher",
            config={"name": "custom_researcher"},
        )
        print(f"\nDynamically created: {researcher.name}")
        print(f"Model: {researcher.model}")
    except Exception as e:
        logger.error(f"Agent creation failed: {e}")

    await factory.close()


async def example_streaming():
    """Example: Using streaming responses for real-time output."""
    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE 6: Streaming Responses")
    logger.info("=" * 60)

    researcher = ResearcherAgent()

    context = {
        "Topic": "Artificial Intelligence",
        "Key Questions": "What is the future of AI?",
        "Known Information": "General knowledge",
        "Sources to Prioritize": "Recent articles",
        "Desired Output Format": "Narrative",
        "task": "Provide insights on AI future",
    }

    print("\nStreaming response (first 200 chars):")
    print("-" * 40)

    try:
        chunk_count = 0
        async for chunk in researcher.handle_streaming(context):
            print(chunk, end="", flush=True)
            chunk_count += 1
            # Demo: print first few chunks then break
            if chunk_count > 10:
                print("\n... (streaming would continue)")
                break
    except Exception as e:
        logger.error(f"Streaming failed: {e}")

    await researcher.close()


async def main():
    """Run all examples."""
    logger.info("Starting Specialized Agents Examples")
    logger.info("=" * 60)

    # Run examples (comment out any you don't want to run)
    await example_researcher_agent()
    await example_developer_agent()
    await example_planner_agent()
    # await example_vision_agent()  # Uncomment if PIL/Pillow available
    await example_agent_factory()
    # await example_streaming()  # Uncomment to test streaming

    logger.info("\n" + "=" * 60)
    logger.info("All examples completed!")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
