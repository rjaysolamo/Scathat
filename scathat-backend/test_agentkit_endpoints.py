#!/usr/bin/env python3
"""
Test script for AgentKit Server Action Endpoints
Tests the three main protection endpoints: block, limit, and pause
"""

import asyncio
import httpx
import json

async def test_agentkit_endpoints():
    """Test the AgentKit server action endpoints"""
    print("🧪 Testing AgentKit Server Action Endpoints...")
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Block contract endpoint
        print("\n1️⃣  Testing /agent/block endpoint...")
        block_data = {
            "contract_address": "0x1234567890123456789012345678901234567890",
            "chain_id": 84532,
            "reason": "High risk contract detected by AI analysis"
        }
        
        try:
            response = await client.post(f"{base_url}/agent/block", json=block_data, timeout=10)
            result = response.json()
            print(f"✅ Block response: {result}")
        except Exception as e:
            print(f"❌ Block test failed: {e}")
        
        # Test 2: Set approval limit endpoint
        print("\n2️⃣  Testing /agent/limit endpoint...")
        limit_data = {
            "contract_address": "0x1234567890123456789012345678901234567890",
            "chain_id": 84532,
            "token_address": "0xabcdef1234567890abcdef1234567890abcdef12",
            "max_amount": 1000.0
        }
        
        try:
            response = await client.post(f"{base_url}/agent/limit", json=limit_data, timeout=10)
            result = response.json()
            print(f"✅ Limit response: {result}")
        except Exception as e:
            print(f"❌ Limit test failed: {e}")
        
        # Test 3: Pause protection endpoint
        print("\n3️⃣  Testing /agent/pause endpoint...")
        pause_data = {
            "duration_minutes": 30
        }
        
        try:
            response = await client.post(f"{base_url}/agent/pause", json=pause_data, timeout=10)
            result = response.json()
            print(f"✅ Pause response: {result}")
        except Exception as e:
            print(f"❌ Pause test failed: {e}")
        
        # Test 4: Error cases
        print("\n4️⃣  Testing error cases...")
        
        # Invalid contract address
        invalid_block_data = {
            "contract_address": "invalid_address",
            "chain_id": 84532,
            "reason": "Test invalid address"
        }
        
        try:
            response = await client.post(f"{base_url}/agent/block", json=invalid_block_data, timeout=10)
            result = response.json()
            print(f"✅ Invalid address handled: {result}")
        except Exception as e:
            print(f"❌ Invalid address test failed: {e}")
        
        # Negative amount
        invalid_limit_data = {
            "contract_address": "0x1234567890123456789012345678901234567890",
            "chain_id": 84532,
            "token_address": "0xabcdef1234567890abcdef1234567890abcdef12",
            "max_amount": -100.0
        }
        
        try:
            response = await client.post(f"{base_url}/agent/limit", json=invalid_limit_data, timeout=10)
            result = response.json()
            print(f"✅ Negative amount handled: {result}")
        except Exception as e:
            print(f"❌ Negative amount test failed: {e}")

async def main():
    """Main test function"""
    print("🚀 Starting AgentKit endpoint tests...")
    print("📡 Make sure the server is running on http://localhost:8000")
    
    await test_agentkit_endpoints()
    
    print("\n🎉 AgentKit endpoint tests completed!")

if __name__ == "__main__":
    asyncio.run(main())