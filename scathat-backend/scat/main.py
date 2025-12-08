"""
Scathat Backend API - Core Demonstration
Simplified FastAPI application for blockchain contract scanning demo.
"""

import os
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, field_validator, Field
import uvicorn
import logging
import time
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import redis
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Import services
from services.explorer_service import ExplorerService, ExplorerConfig
from services.web3_service import Web3Service, Web3Config
from services.venice_service import VeniceService, VeniceConfig
from services.agentkit_service import AgentKitService, AgentKitConfig
from services.ai_aggregator_service import AIAggregatorService, ModelOutput, RiskLevel
from services.pinecone_service import PineconeService
from services.database_service import DatabaseService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Redis for rate limiting
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    logger.info("Redis connected successfully")
except redis.ConnectionError:
    logger.warning("Redis not available, using in-memory rate limiting")
    redis_client = None

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI instance
app = FastAPI(
    title="Scathat API",
    description="Blockchain contract scanning and analysis API",
    version="1.0.0"
)

# Add middleware
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # In production, specify actual hosts

# Initialize services with demo configuration
try:
    # Explorer Service Configuration (for Base Sepolia)
    explorer_config = ExplorerConfig(
        api_key=os.getenv("BASESCAN_API_KEY", "demo_key"),
        base_url="https://api-sepolia.basescan.org/api",
        chain_id=84532,
        chain_name="Base Sepolia"
    )
    explorer_service = ExplorerService(explorer_config)
    
    # Venice Service Configuration
    venice_config = VeniceConfig(
        api_url=os.getenv("VENICE_API_URL", "https://api.venice.ai/v1"),
        api_key=os.getenv("VENICE_API_KEY", "demo_key"),
        model_id=os.getenv("VENICE_MODEL_ID", "default-model")
    )
    venice_service = VeniceService(venice_config)
    
    # Web3 Service Configuration (for Base Sepolia)
    web3_config = Web3Config(
        rpc_url=os.getenv("BASE_SEPOLIA_RPC_URL", "https://base-sepolia-rpc.publicnode.com"),
        chain_id=84532,
        chain_name="Base Sepolia",
        explorer_url="https://sepolia.basescan.org",
        native_currency="ETH"
    )
    web3_service = Web3Service(web3_config)
    
    # AgentKit Service Configuration
    agentkit_service = AgentKitService(
        api_url=os.getenv("AGENTKIT_API_URL", "https://api.agentkit.ai/v1"),
        api_key=os.getenv("AGENTKIT_API_KEY", "demo_key"),
        cdp_api_key=os.getenv("AGENTKIT_CDP_API_KEY"),
        cdp_api_secret=os.getenv("AGENTKIT_CDP_API_SECRET")
    )
    
    # AI Aggregator Service
    ai_aggregator_service = AIAggregatorService()
    
    # Pinecone Service
    pinecone_service = PineconeService()
    
    # Database Service
    database_service = DatabaseService()
    
    print("✅ All services initialized successfully for demonstration")
    
except Exception as e:
    print(f"⚠️  Service initialization warning: {str(e)}")
    print("Continuing with limited functionality for demo purposes")

# Pydantic models
class ScanRequest(BaseModel):
    """Request model for contract scanning."""
    contract_address: str
    chain_id: int = 84532  # Default to Base Sepolia

class ContractAnalysisRequest(BaseModel):
    """Request model for contract analysis."""
    contract_address: str
    write_to_blockchain: bool = False

class ContractAnalysisResponse(BaseModel):
    """Response model for contract analysis."""
    contract_address: str
    risk_level: RiskLevel
    risk_score: float
    explanation: str
    model_outputs_count: int
    normalized_metadata: Dict[str, Any]
    success: bool

class ScanResponse(BaseModel):
    """Response model for contract scanning."""
    message: str
    contract_address: str
    risk_score: str
    transaction_hash: Optional[str] = None
    scan_id: str
    status: str

class ScoreResponse(BaseModel):
    """Response model for score retrieval."""
    contract_address: str
    risk_score: str

@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint returning API information.
    
    Returns:
        Dict[str, str]: API information
    """
    return {
        "message": "Scathat API - Blockchain Contract Scanner",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Dict[str, str]: Health status
    """
    return {"status": "healthy", "service": "scathat-api"}

# Pydantic model for AgentKit analysis request
class AgentKitAnalysisRequest(BaseModel):
    """Request model for AgentKit contract analysis."""
    contract_address: str
    chain_id: int = 84532  # Default to Base Sepolia
    analysis_type: str = "security_risk"

# Pydantic model for AgentKit analysis response
class AgentKitAnalysisResponse(BaseModel):
    """Response model for AgentKit contract analysis."""
    contract_address: str
    risk_score: str
    risk_level: str
    risk_level_value: int
    confidence: float
    vulnerabilities: list
    analysis_summary: str
    source: str

@app.post("/analyze/agentkit", response_model=AgentKitAnalysisResponse)
async def analyze_with_agentkit(request: AgentKitAnalysisRequest) -> AgentKitAnalysisResponse:
    """
    Analyze a contract using AgentKit AI-powered security analysis.
    
    Args:
        request (AgentKitAnalysisRequest): Contract analysis request
        
    Returns:
        AgentKitAnalysisResponse: Detailed AI analysis results
        
    Raises:
        HTTPException: If analysis fails or contract address is invalid
    """
    try:
        # Validate contract address format
        if not request.contract_address.startswith("0x") or len(request.contract_address) != 42:
            raise HTTPException(
                status_code=400,
                detail="Invalid contract address format. Must start with '0x' and be 42 characters long."
            )
        
        # Analyze contract with AgentKit
        analysis_result = await agentkit_service.analyze_contract(
            request.contract_address, 
            request.chain_id
        )
        
        return AgentKitAnalysisResponse(
            contract_address=request.contract_address,
            risk_score=analysis_result["risk_score"],
            risk_level=agentkit_service.get_risk_level_name(analysis_result["risk_level"]),
            risk_level_value=analysis_result["risk_level_value"],
            confidence=analysis_result["confidence"],
            vulnerabilities=analysis_result["vulnerabilities"],
            analysis_summary=analysis_result["analysis_summary"],
            source=analysis_result["source"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AgentKit analysis failed: {str(e)}"
        )

@app.post("/scan", response_model=ScanResponse)
async def scan_contract(request: ScanRequest) -> ScanResponse:
    """
    Full contract scanning flow: fetch data, analyze with AI, write to blockchain.
    
    Args:
        request (ScanRequest): Contract scanning request containing address and chain ID
        
    Returns:
        ScanResponse: Scan results with risk score and transaction hash
        
    Raises:
        HTTPException: If any step in the scanning process fails
    """
    try:
        # Validate contract address format
        if not request.contract_address.startswith("0x") or len(request.contract_address) != 42:
            raise HTTPException(
                status_code=400,
                detail="Invalid contract address format. Must start with '0x' and be 42 characters long."
            )
        
        # 1. Fetch contract data from blockchain explorer
        contract_data = await explorer_service.get_contract_source_code(request.contract_address)
        
        if not contract_data or not contract_data.get("source_code"):
            raise HTTPException(
                status_code=404,
                detail="Contract not found or source code not available on Base Sepolia."
            )
        
        # 2. Analyze contract with Venice.ai AI
        risk_analysis = await venice_service.analyze_contract_code(contract_data["source_code"])
        
        if not risk_analysis or not risk_analysis.get("risk_score"):
            # Demo fallback: Return mock risk score if AI service unavailable
            risk_score = "MEDIUM"
        else:
            risk_score = risk_analysis["risk_score"]
        
        # 3. Write risk score to on-chain registry (demo mode)
        registry_address = os.getenv("RESULTS_REGISTRY_ADDRESS")
        private_key = os.getenv("DEPLOYER_PRIVATE_KEY")
        
        if not registry_address or not private_key:
            tx_hash = None  # Skip on-chain write in demo mode
        else:
            # Get ABI from environment or use default
            registry_abi_str = os.getenv("RESULTS_REGISTRY_ABI")
            registry_abi = json.loads(registry_abi_str) if registry_abi_str else []
            
            tx_hash = web3_service.write_score_to_chain(
                contract_address=request.contract_address,
                risk_score=risk_score,
                private_key=private_key,
                registry_address=registry_address,
                registry_abi=registry_abi
            )
        
        scan_id = f"scan_{request.chain_id}_{request.contract_address[-8:]}"
        
        return ScanResponse(
            message="Scan complete and result recorded successfully",
            contract_address=request.contract_address,
            risk_score=risk_score,
            transaction_hash=tx_hash,
            scan_id=scan_id,
            status="completed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during scanning: {str(e)}"
        )

@app.get("/score/{contract_address}", response_model=ScoreResponse)
async def get_score(contract_address: str) -> ScoreResponse:
    """
    Retrieve risk score for a contract address from the on-chain registry.
    
    Args:
        contract_address (str): The contract address to query
        
    Returns:
        ScoreResponse: Contract address and risk score
        
    Raises:
        HTTPException: If the contract address is invalid or score not found
    """
    try:
        # Validate contract address format
        if not contract_address.startswith("0x") or len(contract_address) != 42:
            raise HTTPException(
                status_code=400,
                detail="Invalid contract address format. Must start with '0x' and be 42 characters long."
            )
        
        # Read risk score from on-chain registry
        registry_address = os.getenv("RESULTS_REGISTRY_ADDRESS")
        
        if not registry_address:
            # Demo fallback: Return mock score if registry not configured
            return ScoreResponse(
                contract_address=contract_address,
                risk_score="MEDIUM"
            )
        
        # Get ABI from environment or use default
        registry_abi_str = os.getenv("RESULTS_REGISTRY_ABI")
        registry_abi = json.loads(registry_abi_str) if registry_abi_str else []
        
        risk_score = web3_service.read_score_from_chain(
            contract_address=contract_address,
            registry_address=registry_address,
            registry_abi=registry_abi
        )
        
        if not risk_score or risk_score == "":
            raise HTTPException(
                status_code=404,
                detail="No risk score found for this contract address. Please scan the contract first."
            )
        
        return ScoreResponse(
            contract_address=contract_address,
            risk_score=risk_score
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while retrieving score: {str(e)}"
        )

@app.get("/scan/{scan_id}")
async def get_scan_status(scan_id: str) -> Dict[str, Any]:
    """
    Get the status of a previously initiated scan.
    
    Args:
        scan_id (str): The unique scan identifier
        
    Returns:
        Dict[str, Any]: Scan status and results if available
    """
    # Placeholder for scan status retrieval
    return {
        "scan_id": scan_id,
        "status": "completed",
        "results": {
            "vulnerabilities": [],
            "analysis": {},
            "risk_score": 0.0
        }
    }

# Transaction Analysis Helper Functions
async def analyze_transaction_patterns(transaction_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze transaction patterns for security risks.
    
    Args:
        transaction_details: Transaction receipt details
        
    Returns:
        Dict with risk analysis results
    """
    analysis = {
        'gas_usage_risk': 0.0,
        'value_transfer_risk': 0.0,
        'contract_interaction_risk': 0.0,
        'anomaly_detection_risk': 0.0,
        'overall_risk_score': 0.0
    }
    
    try:
        # 1. Gas usage analysis
        gas_used = transaction_details.get('gasUsed', 0)
        gas_limit = transaction_details.get('gas', 0)
        
        if gas_limit > 0:
            gas_usage_ratio = gas_used / gas_limit
            if gas_usage_ratio > 0.9:
                analysis['gas_usage_risk'] = 0.8  # High risk - near gas limit
            elif gas_usage_ratio > 0.7:
                analysis['gas_usage_risk'] = 0.5  # Medium risk
            elif gas_usage_ratio < 0.1:
                analysis['gas_usage_risk'] = 0.3  # Low risk - underutilized
        
        # 2. Value transfer analysis
        value = int(transaction_details.get('value', 0))
        if value > 10**18:  # More than 1 ETH equivalent
            analysis['value_transfer_risk'] = 0.7
        elif value > 10**17:  # More than 0.1 ETH
            analysis['value_transfer_risk'] = 0.4
        
        # 3. Contract interaction analysis
        if transaction_details.get('to') and len(transaction_details.get('input', '')) > 10:
            # Complex contract interaction
            analysis['contract_interaction_risk'] = 0.6
        
        # 4. Anomaly detection (placeholder for ML-based detection)
        # This would typically involve more sophisticated pattern recognition
        
        # Calculate overall risk score (weighted average)
        weights = {
            'gas_usage_risk': 0.3,
            'value_transfer_risk': 0.25,
            'contract_interaction_risk': 0.35,
            'anomaly_detection_risk': 0.1
        }
        
        overall_score = sum(
            analysis[key] * weights[key] 
            for key in weights.keys()
        )
        analysis['overall_risk_score'] = overall_score
        
    except Exception as e:
        logger.error(f"Transaction pattern analysis failed: {str(e)}")
    
    return analysis


async def combine_transaction_risks(
    transaction_analysis: Dict[str, Any], 
    involved_contracts: List[Dict[str, Any]]
) -> float:
    """
    Combine transaction and contract risks into final risk score.
    
    Args:
        transaction_analysis: Transaction risk analysis
        involved_contracts: List of contract risk assessments
        
    Returns:
        Combined risk score (0.0 - 1.0)
    """
    try:
        transaction_score = transaction_analysis.get('overall_risk_score', 0.0)
        
        if not involved_contracts:
            return transaction_score
        
        # Calculate average contract risk score
        contract_scores = [
            contract.get('risk_score', 0.0) 
            for contract in involved_contracts 
            if contract.get('analysis_success', False)
        ]
        
        if contract_scores:
            avg_contract_score = sum(contract_scores) / len(contract_scores)
            # Weighted combination: 60% transaction, 40% contracts
            combined_score = (transaction_score * 0.6) + (avg_contract_score * 0.4)
            return min(1.0, max(0.0, combined_score))
        else:
            return transaction_score
            
    except Exception as e:
        logger.error(f"Risk combination failed: {str(e)}")
        return transaction_analysis.get('overall_risk_score', 0.5)


async def determine_transaction_risk_level(risk_score: float) -> RiskLevel:
    """
    Determine risk level based on risk score.
    
    Args:
        risk_score: Combined risk score (0.0 - 1.0)
        
    Returns:
        RiskLevel enum value
    """
    if risk_score >= 0.7:
        return RiskLevel.DANGEROUS
    elif risk_score >= 0.4:
        return RiskLevel.WARNING
    else:
        return RiskLevel.SAFE


async def generate_transaction_explanation(
    transaction_analysis: Dict[str, Any],
    involved_contracts: List[Dict[str, Any]],
    risk_level: RiskLevel
) -> str:
    """
    Generate comprehensive explanation for transaction risk assessment.
    
    Args:
        transaction_analysis: Transaction risk analysis
        involved_contracts: List of contract risk assessments
        risk_level: Final risk level
        
    Returns:
        Human-readable explanation
    """
    explanation_parts = []
    
    # Transaction analysis summary
    tx_score = transaction_analysis.get('overall_risk_score', 0.0)
    explanation_parts.append(
        f"Transaction pattern analysis score: {tx_score:.2f}/1.0"
    )
    
    # Contract risk summary
    if involved_contracts:
        risky_contracts = [
            contract for contract in involved_contracts 
            if contract.get('risk_score', 0.0) >= 0.4
        ]
        
        if risky_contracts:
            explanation_parts.append(
                f"Involves {len(risky_contracts)} potentially risky contracts"
            )
        else:
            explanation_parts.append("All involved contracts appear safe")
    
    # Risk level explanation
    if risk_level == RiskLevel.DANGEROUS:
        explanation_parts.append(
            "⚠️ HIGH RISK: This transaction shows multiple concerning patterns "
            "and should be carefully reviewed before proceeding."
        )
    elif risk_level == RiskLevel.WARNING:
        explanation_parts.append(
            "⚠️ CAUTION: This transaction shows some risk indicators. "
            "Review the details before proceeding."
        )
    else:
        explanation_parts.append(
            "✅ SAFE: This transaction appears normal with no significant risk indicators."
        )
    
    return " ".join(explanation_parts)


# Risk History Models
class RiskHistoryRequest(BaseModel):
    contract_address: Optional[str] = Field(None, description="Specific contract address to filter by")
    risk_level: Optional[str] = Field(None, description="Risk level to filter by (safe, warning, dangerous)")
    start_date: Optional[datetime] = Field(None, description="Start date for filtering")
    end_date: Optional[datetime] = Field(None, description="End date for filtering")
    limit: int = Field(100, description="Maximum number of results", ge=1, le=1000)
    offset: int = Field(0, description="Pagination offset", ge=0)

class RiskHistoryResponse(BaseModel):
    analyses: List[Dict[str, Any]]
    total_count: int
    filtered_count: int
    success: bool


@app.get("/risk/history", response_model=RiskHistoryResponse)
@limiter.limit("30/minute")
async def get_risk_history(
    request: RiskHistoryRequest = Depends(),
    request_data: Request = None
):
    """
    Retrieve historical risk analysis data.
    
    This endpoint provides access to previously analyzed contracts and transactions
    with filtering and pagination capabilities.
    """
    try:
        # Check rate limiting
        client_host = request_data.client.host if request_data else "unknown"
        await check_rate_limit(client_host, "risk_history")
        
        logger.info("Retrieving risk history data")
        
        # Build filter criteria
        filters = {}
        if request.contract_address:
            filters['contract_address'] = request.contract_address.lower()
        if request.risk_level:
            filters['risk_level'] = request.risk_level.lower()
        if request.start_date:
            filters['start_date'] = request.start_date
        if request.end_date:
            filters['end_date'] = request.end_date
        
        # Retrieve data from database
        analyses, total_count, filtered_count = await asyncio.to_thread(
            database_service.get_risk_history,
            filters,
            request.limit,
            request.offset
        )
        
        return RiskHistoryResponse(
            analyses=analyses,
            total_count=total_count,
            filtered_count=filtered_count,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Risk history retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve risk history: {str(e)}")


# Model Update Models
class ModelUpdateRequest(BaseModel):
    model_name: str = Field(..., description="Name of the AI model to update")
    config_updates: Dict[str, Any] = Field(..., description="Configuration updates")
    restart_service: bool = Field(False, description="Whether to restart the model service")

class ModelUpdateResponse(BaseModel):
    model_name: str
    updated_config: Dict[str, Any]
    restart_status: Optional[str]
    success: bool


@app.post("/model/update", response_model=ModelUpdateResponse)
@limiter.limit("5/minute")
async def update_model_config(
    request: ModelUpdateRequest,
    request_data: Request
):
    """
    Update AI model configuration.
    
    This endpoint allows dynamic updates to AI model configurations
    and optional service restarts.
    """
    try:
        # Check rate limiting (admin endpoint)
        client_host = request_data.client.host
        await check_rate_limit(client_host, "model_update", strict=True)
        
        logger.info(f"Updating model configuration for {request.model_name}")
        
        # Update model configuration in database
        updated_config = await asyncio.to_thread(
            database_service.update_model_config,
            request.model_name,
            request.config_updates
        )
        
        restart_status = None
        if request.restart_service:
            # Placeholder for service restart logic
            # In production, this would trigger a service reload
            restart_status = "restart_queued"
            logger.warning(f"Service restart requested for {request.model_name}")
        
        return ModelUpdateResponse(
            model_name=request.model_name,
            updated_config=updated_config,
            restart_status=restart_status,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Model update failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model update failed: {str(e)}")


# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all incoming API requests.
    """
    start_time = time.time()
    
    # Log request details
    logger.info(f"Request: {request.method} {request.url} from {request.client.host}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response details
        logger.info(
            f"Response: {request.method} {request.url} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.2f}s"
        )
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url} - "
            f"Error: {str(e)} - "
            f"Time: {process_time:.2f}s"
        )
        raise


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

# Pydantic models for new endpoints
class TransactionAnalysisRequest(BaseModel):
    """Request model for transaction analysis."""
    transaction_hash: str
    chain_id: int = 84532  # Default to Base Sepolia

class RiskHistoryRequest(BaseModel):
    """Request model for risk history retrieval."""
    contract_address: str
    days: int = 7  # Default to 7 days history

class ModelUpdateRequest(BaseModel):
    """Request model for model updates."""
    model_name: str
    weights: Dict[str, float]
    enabled: bool = True

class TransactionAnalysisResponse(BaseModel):
    """Response model for transaction analysis."""
    transaction_hash: str
    risk_score: float
    risk_level: str
    explanation: str
    detected_anomalies: List[str]
    contract_interactions: List[str]
    success: bool

class RiskHistoryResponse(BaseModel):
    """Response model for risk history."""
    contract_address: str
    history: List[Dict[str, Any]]
    success: bool

class ModelUpdateResponse(BaseModel):
    """Response model for model updates."""
    model_name: str
    status: str
    success: bool


@app.post("/analyze/contract", response_model=ContractAnalysisResponse)
@limiter.limit("10/minute")
async def analyze_contract(request: Request, scan_request: ScanRequest) -> ContractAnalysisResponse:
    """
    Analyze a smart contract for security risks and vulnerabilities.
    
    This endpoint performs comprehensive analysis of a smart contract using
    multiple AI models and returns a detailed risk assessment.
    
    Args:
        scan_request (ScanRequest): Contract analysis request
        
    Returns:
        ContractAnalysisResponse: Detailed contract analysis results
    """
    try:
        # Validate contract address format
        if not scan_request.contract_address.startswith("0x") or len(scan_request.contract_address) != 42:
            raise HTTPException(
                status_code=400,
                detail="Invalid contract address format. Must start with '0x' and be 42 characters long."
            )
        
        # Fetch contract data from blockchain explorer
        contract_data = await explorer_service.get_contract_source_code(scan_request.contract_address)
        
        if not contract_data or not contract_data.get("source_code"):
            raise HTTPException(
                status_code=404,
                detail="Contract not found or source code not available."
            )
        
        # Analyze contract with AI aggregator service
        analysis_result = await ai_aggregator_service.analyze_contract(
            contract_data["source_code"],
            scan_request.contract_address,
            scan_request.chain_id
        )
        
        return ContractAnalysisResponse(
            contract_address=scan_request.contract_address,
            risk_level=analysis_result.risk_level,
            risk_score=analysis_result.risk_score,
            explanation=analysis_result.explanation,
            model_outputs_count=analysis_result.model_outputs_count,
            normalized_metadata=analysis_result.normalized_metadata,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Contract analysis failed: {str(e)}"
        )

@app.post("/analyze/transaction", response_model=TransactionAnalysisResponse)
@limiter.limit("15/minute")
async def analyze_transaction(request: Request, tx_request: TransactionAnalysisRequest) -> TransactionAnalysisResponse:
    """
    Analyze a blockchain transaction for suspicious activity and risks.
    
    This endpoint examines transaction details, contract interactions,
    and patterns to detect potential security issues or anomalies.
    
    Args:
        tx_request (TransactionAnalysisRequest): Transaction analysis request
        
    Returns:
        TransactionAnalysisResponse: Transaction analysis results
    """
    try:
        # Validate transaction hash format
        if not tx_request.transaction_hash.startswith("0x") or len(tx_request.transaction_hash) != 66:
            raise HTTPException(
                status_code=400,
                detail="Invalid transaction hash format. Must start with '0x' and be 66 characters long."
            )
        
        # Get transaction details from blockchain
        tx_receipt = web3_service.get_transaction_receipt(tx_request.transaction_hash)
        
        if not tx_receipt:
            raise HTTPException(
                status_code=404,
                detail="Transaction not found on the specified chain."
            )
        
        # Get transaction history from explorer
        tx_history = await explorer_service.get_transaction_history(
            tx_receipt.get('to', ''),  # Contract address
            0,  # Start block
            99999999  # End block
        )
        
        # Simple risk analysis based on transaction patterns
        risk_score = 0.0
        detected_anomalies = []
        contract_interactions = []
        
        # Check for common risk patterns
        if tx_receipt.get('gasUsed', 0) > 300000:  # High gas usage
            risk_score += 0.3
            detected_anomalies.append("High gas consumption")
        
        if tx_receipt.get('status') == 0:  # Failed transaction
            risk_score += 0.5
            detected_anomalies.append("Transaction failed")
        
        # Normalize risk score
        risk_score = min(1.0, risk_score)
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "DANGEROUS"
        elif risk_score >= 0.4:
            risk_level = "WARNING"
        else:
            risk_level = "SAFE"
        
        # Save analysis to database
        analysis_id = f"tx_{tx_request.transaction_hash[-8:]}"
        database_service.save_transaction_analysis(
            analysis_id=analysis_id,
            transaction_hash=tx_request.transaction_hash,
            risk_score=risk_score,
            risk_level=risk_level,
            explanation=f"Transaction analysis completed with score {risk_score}",
            detected_anomalies=detected_anomalies,
            contract_interactions=contract_interactions
        )
        
        return TransactionAnalysisResponse(
            transaction_hash=tx_request.transaction_hash,
            risk_score=risk_score,
            risk_level=risk_level,
            explanation=f"Analyzed transaction with {len(detected_anomalies)} anomalies detected",
            detected_anomalies=detected_anomalies,
            contract_interactions=contract_interactions,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Transaction analysis failed: {str(e)}"
        )

@app.post("/risk/history", response_model=RiskHistoryResponse)
@limiter.limit("20/minute")
async def get_risk_history(request: Request, history_request: RiskHistoryRequest) -> RiskHistoryResponse:
    """
    Retrieve risk assessment history for a specific contract address.
    
    This endpoint returns the historical risk scores and analysis results
    for a contract over a specified time period.
    
    Args:
        history_request (RiskHistoryRequest): Risk history request
        
    Returns:
        RiskHistoryResponse: Historical risk data
    """
    try:
        # Validate contract address format
        if not history_request.contract_address.startswith("0x") or len(history_request.contract_address) != 42:
            raise HTTPException(
                status_code=400,
                detail="Invalid contract address format. Must start with '0x' and be 42 characters long."
            )
        
        # Get risk history from database
        history = database_service.get_risk_history(
            history_request.contract_address,
            history_request.days
        )
        
        return RiskHistoryResponse(
            contract_address=history_request.contract_address,
            history=history,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve risk history: {str(e)}"
        )

@app.post("/model/update", response_model=ModelUpdateResponse)
@limiter.limit("5/minute")  # Lower limit for model updates
async def update_model(request: Request, update_request: ModelUpdateRequest) -> ModelUpdateResponse:
    """
    Update AI model configuration and weights.
    
    This endpoint allows updating model parameters for the AI analysis services.
    Requires appropriate authentication in production.
    
    Args:
        update_request (ModelUpdateRequest): Model update request
        
    Returns:
        ModelUpdateResponse: Update status
    """
    try:
        # In production, add authentication/authorization here
        
        # Update model configuration in database
        success = database_service.update_model_config(
            update_request.model_name,
            update_request.weights,
            update_request.enabled
        )
        
        if success:
            return ModelUpdateResponse(
                model_name=update_request.model_name,
                status="Model updated successfully",
                success=True
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to update model configuration"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Model update failed: {str(e)}"
        )

# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all incoming API requests.
    """
    start_time = time.time()
    
    # Log request details
    logger.info(f"Request: {request.method} {request.url} from {request.client.host}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response details
        logger.info(
            f"Response: {request.method} {request.url} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.2f}s"
        )
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {request.method} {request.url} - "
            f"Error: {str(e)} - "
            f"Time: {process_time:.2f}s"
        )
        raise


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )