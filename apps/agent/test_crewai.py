#!/usr/bin/env python3
"""Test script for CrewAI integration with CopilotKit."""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.crewai_agents.service import crewai_service
from app.crewai_agents.config import AGENT_REGISTRY

async def test_crewai_agents():
    """Test CrewAI agents initialization and execution."""
    print("=" * 60)
    print("Testing CrewAI Integration with CopilotKit")
    print("=" * 60)
    
    # Test 1: List all agents
    print("\n1. Listing all CrewAI agents:")
    agents = crewai_service.list_agents()
    for agent in agents:
        print(f"   - {agent['name']}: {agent['description']} ({agent['type']})")
    
    # Test 2: Get specific agent
    print("\n2. Testing agent retrieval:")
    test_agent = crewai_service.get_agent("credit_optimizer")
    if test_agent:
        print(f"   Successfully retrieved: {test_agent.name}")
    else:
        print("   Failed to retrieve credit_optimizer agent")
    
    # Test 3: Execute a flow agent
    print("\n3. Testing flow agent execution:")
    try:
        result = await crewai_service.execute_agent(
            agent_name="credit_optimizer_flow",
            input_data={"credit_score": "650", "goal": "improve_score"},
            tenant_id="test_tenant",
        )
        print(f"   Flow execution result: {result['success']}")
        if result['success']:
            print(f"   Result type: {result['result'].get('type')}")
            print(f"   Final status: {result['result'].get('final_status')}")
    except Exception as e:
        print(f"   Flow execution error: {str(e)}")
    
    # Test 4: Test message emission
    print("\n4. Testing message emission:")
    try:
        await crewai_service.emit_message("Test message from CrewAI integration")
        print("   Message emission successful")
    except Exception as e:
        print(f"   Message emission error: {str(e)}")
    
    # Test 5: Test tool call emission
    print("\n5. Testing tool call emission:")
    try:
        await crewai_service.emit_tool_call(
            tool_name="TestTool",
            tool_args={"param1": "value1", "param2": "value2"},
        )
        print("   Tool call emission successful")
    except Exception as e:
        print(f"   Tool call emission error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("CrewAI Integration Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    # Set environment variables for testing
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "test-key")
    
    # Run the test
    asyncio.run(test_crewai_agents())
