#!/usr/bin/env python3
"""
Test script to debug Anthropic API key loading and client initialization
"""
import os
import asyncio
from dotenv import load_dotenv
from anthropic import AsyncAnthropic

async def test_anthropic_connection():
    print("=== Anthropic API Test ===")
    
    # Test 1: Load .env file
    print(f"Current working directory: {os.getcwd()}")
    env_loaded = load_dotenv()
    print(f".env file loaded: {env_loaded}")
    
    # Test 2: Check if .env file exists
    env_file_exists = os.path.exists(".env")
    print(f".env file exists: {env_file_exists}")
    
    # Test 3: Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    print(f"ANTHROPIC_API_KEY found: {api_key is not None}")
    
    if api_key:
        print(f"API key length: {len(api_key)}")
        print(f"API key starts with: {api_key[:10]}...")
        print(f"API key ends with: ...{api_key[-10:]}")
        
        # Test 4: Initialize client
        try:
            print("Attempting to initialize Anthropic client...")
            client = AsyncAnthropic(api_key=api_key)
            print("✅ Anthropic client initialized successfully")
            
            # Test 5: Make a simple API call
            print("Making test API call...")
            response = await client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            print("✅ API call successful")
            print(f"Response: {response.content[0].text}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print(f"Exception type: {type(e)}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
    else:
        print("❌ No API key found")
        # List all environment variables starting with 'A'
        all_env_vars = {k: v for k, v in os.environ.items() if k.startswith('A')}
        print(f"Environment variables starting with 'A': {list(all_env_vars.keys())}")

if __name__ == "__main__":
    asyncio.run(test_anthropic_connection())