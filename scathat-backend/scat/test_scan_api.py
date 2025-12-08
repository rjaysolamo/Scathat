#!/usr/bin/env python3
"""
Simple test script for the Scathat scan API endpoint.
This demonstrates the contract scanning functionality with mock services.
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.scan_orchestrator_service import ScanOrchestratorService

# Mock services for testing
class MockExplorerService:
    async def get_contract_source_code(self, address):
        return {
            'source_code': 'pragma solidity ^0.8.0; contract Test { function test() public {} }', 
            'contract_name': 'TestContract',
            'verified_status': True
        }
    
    async def get_contract_bytecode(self, address):
        return '0x6080604052'
    
    async def normalize_contract_metadata(self, data):
        return {
            'contract_name': 'TestContract', 
            'verified_status': True,
            'compiler_version': '0.8.0',
            'is_proxy': False
        }

class MockAIService:
    async def analyze_contract_code(self, code):
        return {
            'risk_score': 0.2,
            'confidence': 0.8,
            'explanation': 'Low risk contract with no detected vulnerabilities',
            'detected_issues': [],
            'recommendations': ['No issues detected']
        }

class MockAggregatorService:
    def aggregate_model_outputs(self, outputs):
        class Result:
            risk_score = 0.2
            risk_level = type('RiskLevel', (), {'value': 'Safe'})()
            explanation = 'Low risk contract with no detected vulnerabilities'
        return Result()
    
    def calculate_embedding_vector(self, outputs, metadata):
        return [0.1] * 128

class MockPineconeService:
    def store_embedding(self, contract_address, embedding_vector, metadata):
        print(f"✅ Embedding stored in Pinecone for {contract_address}")
        return True
    
    def is_available(self):
        return True

class MockDatabaseService:
    def save_analysis_log(self, **kwargs):
        print(f"✅ Analysis log saved for {kwargs['contract_address']}")
        return True

async def test_scan_orchestrator():
    """Test the scan orchestrator with mock services"""
    print("🧪 Testing Scan Orchestrator Service...")
    
    orchestrator = ScanOrchestratorService(
        explorer_service=MockExplorerService(),
        web3_service=None,
        ai_services={'test_model': MockAIService()},
        ai_aggregator_service=MockAggregatorService(),
        pinecone_service=MockPineconeService(),
        database_service=MockDatabaseService()
    )
    
    # Test contract address
    contract_address = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
    
    print(f"📋 Scanning contract: {contract_address}")
    result = await orchestrator.scan_contract(contract_address)
    
    print(f"\n📊 Scan Results:")
    print(f"   ✅ Success: {result.success}")
    print(f"   🎯 Risk Level: {result.risk_level}")
    print(f"   📈 Risk Score: {result.final_risk_score}")
    print(f"   📝 Explanation: {result.explanation}")
    
    if result.success:
        print(f"\n🎉 Scan completed successfully!")
        print(f"   - Embedding vectors saved to Pinecone")
        print(f"   - Analysis logs saved to database")
        print(f"   - Risk assessment: {result.risk_level} ({result.final_risk_score})")
    else:
        print(f"\n❌ Scan failed: {result.error}")
    
    return result

if __name__ == "__main__":
    print("🚀 Scathat Backend API - Simple Test")
    print("=" * 50)
    
    result = asyncio.run(test_scan_orchestrator())
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
    print(f"Final result: {'SUCCESS' if result.success else 'FAILED'}")