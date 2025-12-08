"""
AI Engine Service - Simple Orchestration with Batching & Caching

Implements:
- Source Code Model
- Bytecode Model  
- Behavior Model
- Aggregator Model
- Batching + caching for <200ms response
"""

import logging
import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import functools
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Simple in-memory cache with TTL
class SimpleCache:
    def __init__(self, max_size=1000, ttl_seconds=300):
        self.cache = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
    
    def get(self, key):
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl_seconds:
                return entry['value']
            else:
                del self.cache[key]
        return None
    
    def set(self, key, value):
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }

@dataclass
class ModelResult:
    risk_score: float
    confidence: float
    explanation: str
    detected_issues: List[str]
    recommendations: List[str]
    processing_time_ms: int

class AIEngineService:
    """
    Simple AI Engine with batching and caching for fast response times.
    """
    
    def __init__(self):
        self.cache = SimpleCache(max_size=5000, ttl_seconds=600)  # 10 minute TTL
        self.batch_size = 10
        self.max_batch_time_ms = 50  # Max time to wait for batching
        
        # Thread pool for parallel processing
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        logger.info("AI Engine Service initialized with batching and caching")
    
    async def analyze_contract(self, contract_data: Dict[str, Any]) -> ModelResult:
        """
        Main entry point - analyzes contract with all models using batching and caching.
        Target: <200ms response time
        """
        start_time = time.time()
        
        # Generate cache key
        cache_key = self._generate_cache_key(contract_data)
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for contract analysis")
            return cached_result
        
        # Run all models in parallel
        source_code_task = asyncio.create_task(
            self._analyze_source_code(contract_data)
        )
        bytecode_task = asyncio.create_task(
            self._analyze_bytecode(contract_data)
        )
        behavior_task = asyncio.create_task(
            self._analyze_behavior(contract_data)
        )
        
        # Wait for all models to complete with timeout
        try:
            source_result, bytecode_result, behavior_result = await asyncio.wait_for(
                asyncio.gather(source_code_task, bytecode_task, behavior_task),
                timeout=0.15  # 150ms timeout for individual models
            )
        except asyncio.TimeoutError:
            # Fallback if any model times out
            logger.warning("Model analysis timeout, using fallback results")
            source_result = self._create_fallback_result("source_code_timeout")
            bytecode_result = self._create_fallback_result("bytecode_timeout") 
            behavior_result = self._create_fallback_result("behavior_timeout")
        
        # Aggregate results
        final_result = await self._aggregate_results(
            source_result, bytecode_result, behavior_result
        )
        
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        final_result.processing_time_ms = processing_time_ms
        
        # Cache the result
        self.cache.set(cache_key, final_result)
        
        logger.info(f"Analysis completed in {processing_time_ms}ms")
        return final_result
    
    def _generate_cache_key(self, contract_data: Dict[str, Any]) -> str:
        """Generate unique cache key from contract data"""
        source_code = contract_data.get('source_code', '')
        bytecode = contract_data.get('bytecode', '')
        address = contract_data.get('contract_address', '')
        
        # Use hash of content for cache key
        import hashlib
        content = f"{source_code[:1000]}{bytecode[:100]}{address}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def _analyze_source_code(self, contract_data: Dict[str, Any]) -> ModelResult:
        """Source Code Model - analyzes Solidity source code"""
        start_time = time.time()
        
        source_code = contract_data.get('source_code')
        if not source_code:
            return self._create_fallback_result("no_source_code")
        
        try:
            # Simulate AI analysis - in real implementation, call actual AI service
            await asyncio.sleep(0.02)  # 20ms processing time
            
            # Simple heuristic analysis
            risk_score = 0.2
            confidence = 0.8
            issues = []
            recommendations = ["No critical issues detected"]
            
            # Basic security checks
            if "selfdestruct" in source_code.lower():
                risk_score = 0.7
                issues.append("Contains selfdestruct function")
                recommendations.append("Review selfdestruct usage carefully")
            
            if "delegatecall" in source_code.lower():
                risk_score = max(risk_score, 0.6)
                issues.append("Uses delegatecall")
                recommendations.append("Audit delegatecall usage for security")
            
            explanation = f"Source code analysis: {len(issues)} potential issues found"
            
            processing_time = int((time.time() - start_time) * 1000)
            return ModelResult(
                risk_score=risk_score,
                confidence=confidence,
                explanation=explanation,
                detected_issues=issues,
                recommendations=recommendations,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Source code analysis failed: {e}")
            return self._create_fallback_result(f"source_error: {str(e)}")
    
    async def _analyze_bytecode(self, contract_data: Dict[str, Any]) -> ModelResult:
        """Bytecode Model - analyzes EVM bytecode"""
        start_time = time.time()
        
        bytecode = contract_data.get('bytecode')
        if not bytecode or bytecode == '0x':
            return self._create_fallback_result("no_bytecode")
        
        try:
            # Simulate bytecode analysis
            await asyncio.sleep(0.015)  # 15ms processing time
            
            # Simple bytecode heuristics
            risk_score = 0.3  # Higher default risk for bytecode-only
            confidence = 0.5  # Lower confidence for bytecode analysis
            issues = ["Analysis based on bytecode only"]
            recommendations = ["Verify contract source code for comprehensive analysis"]
            
            # Basic bytecode checks
            bytecode_length = len(bytecode)
            if bytecode_length > 10000:  # Large contract
                risk_score = 0.4
                issues.append("Large contract size - increased attack surface")
            
            explanation = f"Bytecode analysis: contract size {bytecode_length} bytes"
            
            processing_time = int((time.time() - start_time) * 1000)
            return ModelResult(
                risk_score=risk_score,
                confidence=confidence,
                explanation=explanation,
                detected_issues=issues,
                recommendations=recommendations,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Bytecode analysis failed: {e}")
            return self._create_fallback_result(f"bytecode_error: {str(e)}")
    
    async def _analyze_behavior(self, contract_data: Dict[str, Any]) -> ModelResult:
        """Behavior Model - analyzes contract interactions and patterns"""
        start_time = time.time()
        
        try:
            # Simulate behavior analysis
            await asyncio.sleep(0.025)  # 25ms processing time
            
            # Simple behavior heuristics
            risk_score = 0.25
            confidence = 0.7
            issues = []
            recommendations = ["Standard contract behavior patterns detected"]
            
            # Check if contract is a proxy
            is_proxy = contract_data.get('is_proxy', False)
            if is_proxy:
                risk_score = 0.5
                issues.append("Proxy contract detected")
                recommendations.append("Review proxy implementation for upgrade safety")
            
            explanation = "Behavior analysis: standard contract patterns"
            if is_proxy:
                explanation = "Behavior analysis: proxy contract detected"
            
            processing_time = int((time.time() - start_time) * 1000)
            return ModelResult(
                risk_score=risk_score,
                confidence=confidence,
                explanation=explanation,
                detected_issues=issues,
                recommendations=recommendations,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Behavior analysis failed: {e}")
            return self._create_fallback_result(f"behavior_error: {str(e)}")
    
    async def _aggregate_results(self, 
                                source_result: ModelResult,
                                bytecode_result: ModelResult,
                                behavior_result: ModelResult) -> ModelResult:
        """Aggregator Model - combines results from all models"""
        start_time = time.time()
        
        try:
            # Weighted aggregation
            weights = {
                'source': 0.5,   # Source code gets highest weight
                'bytecode': 0.3, # Bytecode gets medium weight  
                'behavior': 0.2  # Behavior gets lower weight
            }
            
            # Calculate weighted risk score
            total_weight = weights['source'] + weights['bytecode'] + weights['behavior']
            weighted_risk = (
                source_result.risk_score * weights['source'] +
                bytecode_result.risk_score * weights['bytecode'] +
                behavior_result.risk_score * weights['behavior']
            ) / total_weight
            
            # Calculate weighted confidence
            weighted_confidence = (
                source_result.confidence * weights['source'] +
                bytecode_result.confidence * weights['bytecode'] +
                behavior_result.confidence * weights['behavior']
            ) / total_weight
            
            # Combine all issues and recommendations
            all_issues = (
                source_result.detected_issues +
                bytecode_result.detected_issues + 
                behavior_result.detected_issues
            )
            
            all_recommendations = (
                source_result.recommendations +
                bytecode_result.recommendations +
                behavior_result.recommendations
            )
            
            # Determine risk level
            if weighted_risk < 0.3:
                risk_level = "Safe"
            elif weighted_risk < 0.7:
                risk_level = "Warning"
            else:
                risk_level = "Dangerous"
            
            explanation = (
                f"Aggregated analysis: {risk_level} risk. "
                f"Source: {source_result.explanation}. "
                f"Bytecode: {bytecode_result.explanation}. "
                f"Behavior: {behavior_result.explanation}"
            )
            
            processing_time = int((time.time() - start_time) * 1000)
            return ModelResult(
                risk_score=weighted_risk,
                confidence=weighted_confidence,
                explanation=explanation,
                detected_issues=all_issues,
                recommendations=all_recommendations,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Aggregation failed: {e}")
            return self._create_fallback_result("aggregation_error")
    
    def _create_fallback_result(self, reason: str) -> ModelResult:
        """Create fallback result when analysis fails"""
        return ModelResult(
            risk_score=0.5,  # Medium risk
            confidence=0.2,  # Low confidence
            explanation=f"Fallback analysis: {reason}",
            detected_issues=[f"Analysis limited: {reason}"],
            recommendations=["Retry analysis or perform manual review"],
            processing_time_ms=0
        )

# Simple singleton instance
ai_engine = AIEngineService()