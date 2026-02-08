#!/usr/bin/env python3
"""
Example test script for Instant-RAG Platform
Demonstrates how to use the API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print()

def test_trust_beacon():
    """Test trust beacon"""
    print("🔍 Testing trust beacon...")
    response = requests.get(f"{BASE_URL}/trust/beacon")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_full_workflow():
    """Test complete RAG workflow"""
    print("🔄 Testing full RAG workflow...")
    
    # Note: You need to issue a token first using:
    # docker compose exec app python -c "from identity.passport import passport; print(passport.issue('test-agent'))"
    
    agent_id = "test-agent"
    token = input("Enter your token (or press Enter to skip): ").strip()
    
    if not token:
        print("⏭️  Skipping workflow test (no token provided)")
        return
    
    # Create a test document
    print("📄 Creating test document...")
    with open("/tmp/test_doc.txt", "w") as f:
        f.write("""
        Machine Learning is a subset of Artificial Intelligence.
        It focuses on creating systems that can learn from data.
        Deep Learning uses neural networks with multiple layers.
        Natural Language Processing helps computers understand human language.
        """)
    
    # Ingest the document
    print("📤 Ingesting document...")
    with open("/tmp/test_doc.txt", "rb") as f:
        files = {"file": f}
        data = {"agent_id": agent_id, "token": token}
        response = requests.post(f"{BASE_URL}/ingest", files=files, data=data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print()
    
    # Query the system
    print("❓ Querying the system...")
    payload = {
        "text": "What is machine learning?",
        "agent_id": agent_id,
        "token": token
    }
    response = requests.post(f"{BASE_URL}/query", json=payload)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Answer: {result.get('answer', 'N/A')[:200]}...")
    print(f"   Confidence: {result.get('confidence', 'N/A')}")
    print(f"   Citations: {len(result.get('citations', []))}")
    print()
    
    # Get statistics
    print("📊 Getting agent statistics...")
    response = requests.get(f"{BASE_URL}/stats/{agent_id}?token={token}")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("Instant-RAG Platform Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_health()
        test_trust_beacon()
        test_full_workflow()
        
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to the API.")
        print("   Make sure the service is running: docker compose up")
    except Exception as e:
        print(f"❌ Error: {e}")
