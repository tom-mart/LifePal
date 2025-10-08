#!/usr/bin/env python
"""
Quick test script to verify tool system is working
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from llm_tools import get_tool_registry
from llm_service.ollama_client import OllamaClient
from llm_service.prompt_manager import PromptManager

def test_tool_registry():
    """Test that tools are loaded from database"""
    print("=" * 60)
    print("TEST 1: Tool Registry")
    print("=" * 60)
    
    registry = get_tool_registry()
    
    # List all tools
    tools = registry.list_tools()
    print(f"✓ Tools in registry: {tools}")
    
    # Get tool_retriever
    tool_retriever = registry.get_tool_retriever()
    print(f"✓ Tool_Retriever available: {tool_retriever.function.name}")
    print(f"  Description: {tool_retriever.function.description[:100]}...")
    
    # Get wellbeing tools
    wellbeing_tools = registry.get_tools_by_category('wellbeing')
    print(f"✓ Wellbeing tools: {[t.function.name for t in wellbeing_tools]}")
    
    print()

def test_tool_execution():
    """Test executing tool_retriever"""
    print("=" * 60)
    print("TEST 2: Tool Execution")
    print("=" * 60)
    
    registry = get_tool_registry()
    user = User.objects.first()
    
    if not user:
        print("✗ No users found in database")
        return
    
    # Test tool_retriever with wellbeing category
    result = registry.execute_tool(
        'tool_retriever',
        {'intent_category': 'wellbeing'},
        user
    )
    
    print(f"✓ Tool_Retriever executed")
    print(f"  Success: {result.get('success')}")
    print(f"  Tools found: {result.get('tools_count')}")
    
    if result.get('tools'):
        for tool in result['tools']:
            print(f"    - {tool['name']}: {tool['description'][:80]}...")
    
    print()

def test_system_prompt():
    """Test that system prompt includes tool instructions"""
    print("=" * 60)
    print("TEST 3: System Prompt")
    print("=" * 60)
    
    user = User.objects.first()
    prompt_manager = PromptManager(user=user)
    
    system_prompt = prompt_manager.get_system_prompt(
        include_user_context=False,
        include_tool_instructions=True
    )
    
    # Check if tool instructions are present
    has_tool_retriever = 'tool_retriever' in system_prompt
    has_react = 'ReAct' in system_prompt or 'Reason + Act' in system_prompt
    has_wellbeing = 'wellbeing' in system_prompt
    
    print(f"✓ System prompt generated ({len(system_prompt)} chars)")
    print(f"  Contains 'tool_retriever': {has_tool_retriever}")
    print(f"  Contains ReAct pattern: {has_react}")
    print(f"  Contains wellbeing category: {has_wellbeing}")
    
    if not has_tool_retriever:
        print("\n⚠ WARNING: System prompt doesn't mention tool_retriever!")
        print("First 500 chars of prompt:")
        print(system_prompt[:500])
    
    print()

def test_ollama_tools():
    """Test that Ollama client provides tools correctly"""
    print("=" * 60)
    print("TEST 4: Ollama Client Tools")
    print("=" * 60)
    
    try:
        client = OllamaClient()
        
        if not client.is_available():
            print("✗ Ollama server not available")
            return
        
        print(f"✓ Ollama server available")
        
        # Check what tools are provided
        registry = get_tool_registry()
        tool_retriever = registry.get_tool_retriever()
        
        print(f"✓ Tool_Retriever will be provided to LLM:")
        print(f"  Name: {tool_retriever.function.name}")
        print(f"  Parameters: {tool_retriever.function.parameters}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()

if __name__ == '__main__':
    print("\n🔧 LifePal Tool System Diagnostic\n")
    
    test_tool_registry()
    test_tool_execution()
    test_system_prompt()
    test_ollama_tools()
    
    print("=" * 60)
    print("DIAGNOSIS COMPLETE")
    print("=" * 60)
    print("\nIf all tests pass but LLM still says 'no tools', the issue is likely:")
    print("1. LLM not following instructions to call tool_retriever")
    print("2. LLM response being cut off before tool call")
    print("3. Frontend not handling tool events properly")
    print("\nNext step: Check actual LLM logs during a conversation")
