"""
Contract Scan Orchestrator Service

Coordinates the complete contract scanning workflow:
1. Fetch contract source code (if verified)
2. Fetch bytecode (if unverified) 
3. Normalize contract metadata
4. Send contract to AI models
5. Combine outputs → aggregator → final risk score
6. Save embedding vectors to Pinecone
7. Save analysis logs to database

Simple, focused implementation without over-engineering.
"""

import logging
import uuid
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ScanResult:
    """Data class for scan results."""
    contract_address: str
    source_code: Optional[str] = None
    bytecode: Optional[str] = None
    normalized_metadata: Optional[Dict[str, Any]] = None
    ai_outputs: Optional[Dict[str, Any]] = None
    final_risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    explanation: Optional[str] = None
    success: bool = False
    error: Optional[str] = None
    scan_id: Optional[str] = None


class ScanOrchestratorService:
    """
    Simple orchestrator service for contract scanning workflow.
    Coordinates the complete process from data fetching to risk assessment.
    """

    def __init__(self, 
                 explorer_service,
                 web3_service,
                 ai_services: Dict[str, Any],
                 ai_aggregator_service,
                 pinecone_service=None,
                 database_service=None):
        """
        Initialize the orchestrator with required services.
        
        Args:
            explorer_service: Service for blockchain explorer interactions
            web3_service: Service for direct blockchain interactions
            ai_services: Dictionary of AI analysis services
            ai_aggregator_service: Service for combining AI outputs
            pinecone_service: Service for storing embedding vectors
            database_service: Service for saving analysis logs
        """
        self.explorer_service = explorer_service
        self.web3_service = web3_service
        self.ai_services = ai_services
        self.ai_aggregator_service = ai_aggregator_service
        self.pinecone_service = pinecone_service
        self.database_service = database_service

    async def scan_contract(self, contract_address: str) -> ScanResult:
        """
        Execute the complete contract scanning workflow.
        
        Args:
            contract_address: The contract address to scan
            
        Returns:
            ScanResult: Complete scan results
        """
        scan_id = str(uuid.uuid4())
        result = ScanResult(contract_address=contract_address, scan_id=scan_id)
        
        try:
            # 1. Fetch contract data (source code or bytecode)
            source_code, bytecode, metadata = await self._fetch_contract_data(contract_address)
            result.source_code = source_code
            result.bytecode = bytecode
            result.normalized_metadata = metadata
            
            # 2. Analyze with AI models
            ai_outputs = await self._analyze_with_ai(contract_address, source_code, bytecode)
            result.ai_outputs = ai_outputs
            
            # 3. Combine AI outputs and calculate final risk score
            final_score, risk_level, explanation = await self._aggregate_results(ai_outputs)
            result.final_risk_score = final_score
            result.risk_level = risk_level
            result.explanation = explanation
            
            # 4. Save embedding vector to Pinecone
            await self._save_to_pinecone(contract_address, ai_outputs, metadata, final_score, risk_level)
            
            # 5. Save analysis log to database
            await self._save_to_database(scan_id, contract_address, final_score, risk_level, 
                                       explanation, ai_outputs, metadata)
            
            result.success = True
            
        except Exception as e:
            result.error = f"Scan failed: {str(e)}"
            logger.error(f"Contract scan failed for {contract_address}: {str(e)}")
        
        return result

    async def _fetch_contract_data(self, contract_address: str) -> Tuple[Optional[str], Optional[str], Dict[str, Any]]:
        """
        Fetch contract source code (if verified) or bytecode (if unverified).
        Normalize contract metadata.
        """
        # Try to get source code first
        source_code_data = await self.explorer_service.get_contract_source_code(contract_address)
        
        if source_code_data and source_code_data.get("source_code"):
            # Contract is verified - use source code
            source_code = source_code_data["source_code"]
            bytecode = None
            
            # Normalize metadata
            normalized_metadata = await self.explorer_service.normalize_contract_metadata(source_code_data)
            
        else:
            # Contract is unverified - get bytecode
            source_code = None
            bytecode = await self.explorer_service.get_contract_bytecode(contract_address)
            
            # Create minimal metadata for unverified contracts
            normalized_metadata = {
                'contract_address': contract_address.lower(),
                'contract_name': 'Unverified Contract',
                'compiler_version': 'Unknown',
                'optimization_used': False,
                'runs': 0,
                'verified_status': False,
                'is_proxy': False
            }
        
        return source_code, bytecode, normalized_metadata

    async def _analyze_with_ai(self, 
                              contract_address: str, 
                              source_code: Optional[str], 
                              bytecode: Optional[str]) -> Dict[str, Any]:
        """
        Send contract to all available AI models for analysis.
        """
        ai_outputs = {}
        
        # Analyze with each AI service
        for service_name, ai_service in self.ai_services.items():
            try:
                if source_code:
                    # Use source code for analysis
                    analysis_result = await ai_service.analyze_contract_code(source_code)
                elif bytecode:
                    # Use bytecode for analysis (if service supports it)
                    if hasattr(ai_service, 'analyze_bytecode'):
                        analysis_result = await ai_service.analyze_bytecode(bytecode)
                    else:
                        analysis_result = {
                            'risk_score': 0.5,  # Default medium risk for unverified contracts
                            'confidence': 0.3,   # Lower confidence for bytecode analysis
                            'explanation': 'Analysis based on bytecode only',
                            'detected_issues': ['Unverified contract - limited analysis'],
                            'recommendations': ['Verify contract source code for comprehensive analysis']
                        }
                else:
                    # No data available
                    analysis_result = {
                        'risk_score': 0.7,  # Higher risk for unavailable data
                        'confidence': 0.1,
                        'explanation': 'No contract data available for analysis',
                        'detected_issues': ['Contract data unavailable'],
                        'recommendations': ['Check contract address and blockchain explorer']
                    }
                
                ai_outputs[service_name] = analysis_result
                
            except Exception as e:
                logger.warning(f"AI analysis failed for {service_name}: {str(e)}")
                # Add fallback result for failed analysis
                ai_outputs[service_name] = {
                    'risk_score': 0.5,
                    'confidence': 0.1,
                    'explanation': f'Analysis failed: {str(e)}',
                    'detected_issues': ['AI service unavailable'],
                    'recommendations': ['Retry analysis or use alternative service']
                }
        
        return ai_outputs

    async def _aggregate_results(self, ai_outputs: Dict[str, Any]) -> Tuple[float, str, str]:
        """
        Combine AI outputs using the aggregator service.
        """
        try:
            # Convert AI outputs to ModelOutput format for aggregator
            model_outputs = []
            
            for service_name, output in ai_outputs.items():
                from services.ai_aggregator_service import ModelOutput
                
                model_outputs.append(ModelOutput(
                    model_name=service_name,
                    risk_score=output.get('risk_score', 0.5),
                    confidence=output.get('confidence', 0.5),
                    explanation=output.get('explanation', 'No explanation provided'),
                    detected_issues=output.get('detected_issues', []),
                    recommendations=output.get('recommendations', [])
                ))
            
            # Use aggregator to combine results
            aggregated_result = self.ai_aggregator_service.aggregate_model_outputs(model_outputs)
            
            return (
                aggregated_result.risk_score,
                aggregated_result.risk_level.value,
                aggregated_result.explanation
            )

        except Exception as e:
            logger.error(f"Failed to aggregate results: {str(e)}")
            return 0.5, "Warning", f"Aggregation failed: {str(e)}"

    async def _save_to_pinecone(self,
                              contract_address: str,
                              ai_outputs: Dict[str, Any],
                              metadata: Dict[str, Any],
                              risk_score: float,
                              risk_level: str) -> bool:
        """
        Save embedding vector to Pinecone.
        """
        if not self.pinecone_service:
            logger.warning("Pinecone service not available, skipping embedding storage")
            return False
        
        try:
            # Convert AI outputs to ModelOutput format for embedding calculation
            model_outputs = []
            for service_name, output in ai_outputs.items():
                from services.ai_aggregator_service import ModelOutput
                model_outputs.append(ModelOutput(
                    model_name=service_name,
                    risk_score=output.get('risk_score', 0.5),
                    confidence=output.get('confidence', 0.5),
                    explanation=output.get('explanation', ''),
                    detected_issues=output.get('detected_issues', []),
                    recommendations=output.get('recommendations', [])
                ))
            
            # Calculate embedding vector
            embedding_vector = self.ai_aggregator_service.calculate_embedding_vector(
                model_outputs, metadata
            )
            
            # Prepare metadata for Pinecone
            pinecone_metadata = {
                'risk_score': risk_score,
                'risk_level': risk_level,
                'contract_address': contract_address.lower(),
                'verified_status': metadata.get('verified_status', False),
                'contract_name': metadata.get('contract_name', 'Unknown'),
                'compiler_version': metadata.get('compiler_version', 'Unknown'),
                'is_proxy': metadata.get('is_proxy', False)
            }
            
            # Store embedding in Pinecone
            success = self.pinecone_service.store_embedding(
                contract_address=contract_address,
                embedding_vector=embedding_vector,
                metadata=pinecone_metadata
            )
            
            if success:
                logger.info(f"Embedding stored in Pinecone for contract {contract_address}")
            else:
                logger.warning(f"Failed to store embedding for contract {contract_address}")
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to save to Pinecone: {str(e)}")
            return False

    async def _save_to_database(self,
                             scan_id: str,
                             contract_address: str,
                             risk_score: float,
                             risk_level: str,
                             explanation: str,
                             ai_outputs: Dict[str, Any],
                             metadata: Dict[str, Any]) -> bool:
        """
        Save analysis log to scathat-data-base.
        """
        if not self.database_service:
            logger.warning("Database service not available, skipping analysis log")
            return False
        
        try:
            # Extract detected issues and recommendations from AI outputs
            all_issues = []
            all_recommendations = []
            model_contributions = {}
            
            for service_name, output in ai_outputs.items():
                all_issues.extend(output.get('detected_issues', []))
                all_recommendations.extend(output.get('recommendations', []))
                model_contributions[service_name] = output.get('confidence', 0.5)
            
            # Calculate embedding vector for database storage
            embedding_vector = []
            if self.pinecone_service and self.pinecone_service.is_available():
                model_outputs = []
                for service_name, output in ai_outputs.items():
                    from services.ai_aggregator_service import ModelOutput
                    model_outputs.append(ModelOutput(
                        model_name=service_name,
                        risk_score=output.get('risk_score', 0.5),
                        confidence=output.get('confidence', 0.5),
                        explanation=output.get('explanation', ''),
                        detected_issues=output.get('detected_issues', []),
                        recommendations=output.get('recommendations', [])
                    ))
                
                embedding_vector = self.ai_aggregator_service.calculate_embedding_vector(
                    model_outputs, metadata
                )
            
            # Save to database
            success = self.database_service.save_analysis_log(
                scan_id=scan_id,
                contract_address=contract_address,
                risk_score=risk_score,
                risk_level=risk_level,
                explanation=explanation,
                detected_issues=all_issues,
                recommendations=all_recommendations,
                model_contributions=model_contributions,
                normalized_metadata=metadata,
                embedding_vector=embedding_vector
            )
            
            if success:
                logger.info(f"Analysis log saved to database for contract {contract_address}")
            else:
                logger.warning(f"Failed to save analysis log for contract {contract_address}")
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to save to database: {str(e)}")
            return False

    async def get_scan_summary(self, contract_address: str) -> Dict[str, Any]:
        """
        Get a summary of the scan results for a contract.
        Simple method to demonstrate the workflow.
        """
        result = await self.scan_contract(contract_address)
        
        return {
            'contract_address': result.contract_address,
            'verified': result.source_code is not None,
            'risk_score': result.final_risk_score,
            'risk_level': result.risk_level,
            'ai_models_used': list(result.ai_outputs.keys()) if result.ai_outputs else [],
            'success': result.success,
            'error': result.error
        }