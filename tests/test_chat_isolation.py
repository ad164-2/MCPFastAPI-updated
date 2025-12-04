"""
Integration test for chat isolation fix
Tests that multiple chat sessions don't share responses
"""

import asyncio
import pytest
from langchain_core.messages import HumanMessage, AIMessage
from app.llm_functions.LLMCall import CallAgentGraph


@pytest.mark.asyncio
async def test_chat_isolation_different_contexts():
    """
    Test that two different chat_id values maintain separate contexts
    """
    # Chat 1: Ask about Python
    response_1 = await CallAgentGraph(
        query="What is Python?",
        chat_id=1001,
        history=None
    )
    
    # Chat 2: Ask about JavaScript  
    response_2 = await CallAgentGraph(
        query="What is JavaScript?",
        chat_id=1002,
        history=None
    )
    
    # Responses should be different and relevant to their queries
    assert response_1 != response_2
    # Python response should mention Python, not JavaScript
    assert "python" in response_1.lower() or "py" in response_1.lower()
    # JavaScript response should mention JavaScript, not Python
    assert "javascript" in response_2.lower() or "js" in response_2.lower()


@pytest.mark.asyncio
async def test_chat_with_history():
    """
    Test that chat history is properly maintained within a session
    """
    chat_id = 2001
    
    # First message
    response_1 = await CallAgentGraph(
        query="My name is Alice",
        chat_id=chat_id,
        history=None
    )
    
    # Second message with history
    history = [
        HumanMessage(content="My name is Alice"),
        AIMessage(content=response_1)
    ]
    
    response_2 = await CallAgentGraph(
        query="What is my name?",
        chat_id=chat_id,
        history=history
    )
    
    # Should remember the name from history
    assert "alice" in response_2.lower()


@pytest.mark.asyncio
async def test_concurrent_chats():
    """
    Test that concurrent chat sessions don't interfere with each other
    """
    # Run two chats concurrently
    task_1 = CallAgentGraph(
        query="Tell me about cats",
        chat_id=3001,
        history=None
    )
    
    task_2 = CallAgentGraph(
        query="Tell me about dogs",
        chat_id=3002,
        history=None
    )
    
    # Execute concurrently
    response_1, response_2 = await asyncio.gather(task_1, task_2)
    
    # Verify responses are different and relevant
    assert response_1 != response_2
    # Each response should be about the correct topic
    assert "cat" in response_1.lower() or "feline" in response_1.lower()
    assert "dog" in response_2.lower() or "canine" in response_2.lower()
    # Responses should NOT be swapped
    assert "dog" not in response_1.lower() or "cat" in response_1.lower()  # Cats response shouldn't talk only about dogs
    assert "cat" not in response_2.lower() or "dog" in response_2.lower()  # Dogs response shouldn't talk only about cats


if __name__ == "__main__":
    # Run tests manually
    print("Testing chat isolation...")
    
    async def run_tests():
        print("\n1. Testing different contexts...")
        await test_chat_isolation_different_contexts()
        print("✓ Different contexts test passed")
        
        print("\n2. Testing chat with history...")
        await test_chat_with_history()
        print("✓ Chat history test passed")
        
        print("\n3. Testing concurrent chats...")
        await test_concurrent_chats()
        print("✓ Concurrent chats test passed")
        
        print("\n✅ All tests passed!")
    
    asyncio.run(run_tests())
