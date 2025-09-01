"""
Test script for Agent Creation Endpoint

This script demonstrates how to use the agent creation endpoint.
Make sure the server is running before executing this test.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8080"
LOGIN_URL = f"{BASE_URL}/api/login"
CREATE_AGENT_URL = f"{BASE_URL}/api/agents"

def test_agent_creation():
    """Test the agent creation endpoint"""
    
    # Step 1: Login to get authentication
    login_data = {
        "email": "user@example.com",
        "password": "password123"
    }
    
    print("1. Logging in...")
    login_response = requests.post(LOGIN_URL, json=login_data)
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    print("Login successful!")
    
    # Step 2: Create agent
    agent_data = {
        "name": "My Test Agent",
        "avatar": "https://example.com/avatar.jpg",
        "model": "gpt-3.5-turbo",
        "role": "customer service",
        "description": "A helpful customer service agent",
        "tone": "friendly",
        "short_term_memory": True,
        "long_term_memory": False
    }
    
    print("\n2. Creating agent...")
    print(f"Agent data: {json.dumps(agent_data, indent=2)}")
    
    # Use cookies from login response for authentication
    cookies = login_response.cookies
    
    create_response = requests.post(
        CREATE_AGENT_URL, 
        json=agent_data,
        cookies=cookies
    )
    
    print(f"\nResponse Status: {create_response.status_code}")
    print(f"Response Body: {json.dumps(create_response.json(), indent=2)}")
    
    if create_response.status_code == 201:
        print("\n✅ Agent created successfully!")
        return create_response.json(), cookies
    else:
        print("\n❌ Agent creation failed!")
        return None, None


def test_agent_update(agent_id: int, cookies):
    """Test the agent update endpoint"""
    
    print(f"\n3. Updating agent (ID: {agent_id})...")
    
    # Update data (only some fields)
    update_data = {
        "name": "Updated Test Agent",
        "description": "An updated helpful customer service agent",
        "tone": "casual",
        "short_term_memory": False,
        "status": "active"
    }
    
    print(f"Update data: {json.dumps(update_data, indent=2)}")
    
    update_response = requests.put(
        f"{CREATE_AGENT_URL}/{agent_id}",
        json=update_data,
        cookies=cookies
    )
    
    print(f"\nResponse Status: {update_response.status_code}")
    print(f"Response Body: {json.dumps(update_response.json(), indent=2)}")
    
    if update_response.status_code == 200:
        print("\n✅ Agent updated successfully!")
    else:
        print("\n❌ Agent update failed!")


if __name__ == "__main__":
    # Test creation first
    result, cookies = test_agent_creation()
    
    # If creation was successful, test update
    if result and cookies:
        # Extract agent ID from the response (you might need to adjust this based on your response structure)
        try:
            agent_id = result.get('data', {}).get('id', 1)  # Default to 1 if not found
            test_agent_update(agent_id, cookies)
        except Exception as e:
            print(f"Error extracting agent ID: {e}")
            print("Testing update with default agent ID 1...")
            test_agent_update(1, cookies)

