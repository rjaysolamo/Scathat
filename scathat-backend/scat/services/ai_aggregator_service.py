"""
AI Model Aggregator Service for combining outputs from multiple AI models
and generating a final risk assessment with explanations.
"""

import logging
from typing import Dict, List, Any, Optional
from enum import Enum
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level enumeration for contract assessment."""
    SAFE = "Safe"
    WARNING = "Warning"
    DANGEROUS = "Dangerous"


@dataclass
class ModelOutput:
    """Data class for individual model outputs."""
    model_name: str
    risk_score: float  # 0.0 (safe) to 1.0 (dangerous)
    confidence: float  # 0.0 to 1.0
    explanation: str
    detected_issues: List[str]
    recommendations: List[str]


@dataclass
class AggregatedResult:
    """Data class for final aggregated result."""
    final_risk_level: RiskLevel
    final_risk_score: float
    confidence: float
    explanation: str
    detected_issues: List[str]
    recommendations: List[str]
    model_contributions: Dict[str, float]  # Weight contribution of each model


class AIAggregatorService:
    """
    Service for aggregating outputs from multiple AI models and generating
    a comprehensive risk assessment with weighted confidence scoring.
    """

    def __init__(self):
        # Model weights based on reliability and performance
        self.model_weights = {
            "agentkit": 0.4,    # Coinbase AgentKit - high reliability
            "venice": 0.3,      # Venice Protocol - decentralized AI
            "local_llm": 0.2,   # Local LLM analysis
            "heuristics": 0.1   # Rule-based heuristics
        }
        
        # Risk level thresholds
        self.risk_thresholds = {
            RiskLevel.SAFE: 0.3,
            RiskLevel.WARNING: 0.7,
            RiskLevel.DANGEROUS: 1.0
        }

    def aggregate_model_outputs(self, model_outputs: List[ModelOutput]) -> AggregatedResult:
        """
        Aggregate outputs from multiple AI models using weighted averaging
        and generate a comprehensive risk assessment.
        
        Args:
            model_outputs (List[ModelOutput]): List of outputs from different models
            
        Returns:
            AggregatedResult: Final aggregated risk assessment
        """
        if not model_outputs:
            return self._create_default_result()

        # Calculate weighted risk score
        weighted_scores = []
        confidences = []
        all_issues = []
        all_recommendations = []
        model_contributions = {}

        for output in model_outputs:
            weight = self.model_weights.get(output.model_name, 0.1)
            weighted_score = output.risk_score * weight * output.confidence
            weighted_scores.append(weighted_score)
            confidences.append(output.confidence)
            
            all_issues.extend(output.detected_issues)
            all_recommendations.extend(output.recommendations)
            
            # Track model contribution
            model_contributions[output.model_name] = weighted_score

        # Calculate final scores
        total_weight = sum(self.model_weights.get(output.model_name, 0.1) 
                          for output in model_outputs)
        
        if total_weight > 0:
            final_risk_score = sum(weighted_scores) / total_weight
            final_confidence = np.mean(confidences) if confidences else 0.5
        else:
            final_risk_score = 0.5
            final_confidence = 0.5

        # Determine risk level
        final_risk_level = self._determine_risk_level(final_risk_score)
        
        # Generate comprehensive explanation
        explanation = self._generate_explanation(
            final_risk_level, 
            final_risk_score, 
            model_outputs,
            all_issues
        )

        # Normalize model contributions
        total_contribution = sum(model_contributions.values())
        if total_contribution > 0:
            normalized_contributions = {
                model: contribution / total_contribution
                for model, contribution in model_contributions.items()
            }
        else:
            normalized_contributions = {model: 0.0 for model in model_contributions}

        return AggregatedResult(
            final_risk_level=final_risk_level,
            final_risk_score=final_risk_score,
            confidence=final_confidence,
            explanation=explanation,
            detected_issues=list(set(all_issues)),  # Remove duplicates
            recommendations=list(set(all_recommendations)),
            model_contributions=normalized_contributions
        )

    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on score thresholds."""
        if risk_score <= self.risk_thresholds[RiskLevel.SAFE]:
            return RiskLevel.SAFE
        elif risk_score <= self.risk_thresholds[RiskLevel.WARNING]:
            return RiskLevel.WARNING
        else:
            return RiskLevel.DANGEROUS

    def _generate_explanation(self, 
                            risk_level: RiskLevel, 
                            risk_score: float,
                            model_outputs: List[ModelOutput],
                            detected_issues: List[str]) -> str:
        """Generate comprehensive explanation for the risk assessment."""
        
        base_explanation = f"Contract assessed as {risk_level.value} "
        base_explanation += f"(score: {risk_score:.2f}/1.0). "
        
        if risk_level == RiskLevel.SAFE:
            base_explanation += "The contract appears to be well-written and follows security best practices. "
            if detected_issues:
                base_explanation += "Minor issues were identified but don't pose significant risks."
            else:
                base_explanation += "No significant security issues detected."
                
        elif risk_level == RiskLevel.WARNING:
            base_explanation += "The contract has some concerning patterns that require careful review. "
            if detected_issues:
                base_explanation += f"Key issues: {', '.join(detected_issues[:3])}. "
            base_explanation += "Thorough auditing is recommended before interaction."
            
        else:  # DANGEROUS
            base_explanation += "The contract exhibits multiple high-risk patterns and should be avoided. "
            if detected_issues:
                base_explanation += f"Critical issues: {', '.join(detected_issues[:5])}. "
            base_explanation += "Immediate security review and avoidance strongly recommended."

        # Add model consensus information
        model_names = [output.model_name for output in model_outputs]
        if len(model_names) > 1:
            base_explanation += f" Consensus reached across {len(model_names)} AI models."

        return base_explanation

    def _create_default_result(self) -> AggregatedResult:
        """Create a default result when no model outputs are available."""
        return AggregatedResult(
            final_risk_level=RiskLevel.WARNING,
            final_risk_score=0.5,
            confidence=0.3,
            explanation="No AI model analysis available. Manual review recommended.",
            detected_issues=["No analysis performed"],
            recommendations=["Perform comprehensive security analysis"],
            model_contributions={}
        )

    def calculate_embedding_vector(self, 
                                 model_outputs: List[ModelOutput],
                                 contract_metadata: Dict[str, Any]) -> List[float]:
        """
        Calculate embedding vector for Pinecone storage based on analysis results.
        
        Args:
            model_outputs (List[ModelOutput]): Model outputs
            contract_metadata (Dict[str, Any]): Normalized contract metadata
            
        Returns:
            List[float]: Embedding vector for storage
        """
        # Extract features for embedding
        features = []
        
        # Risk scores from models
        for output in model_outputs:
            features.append(output.risk_score)
            features.append(output.confidence)
        
        # Contract metadata features
        if contract_metadata.get('source_code_length'):
            features.append(min(contract_metadata['source_code_length'] / 10000, 1.0))
        
        features.append(1.0 if contract_metadata.get('verified_status') else 0.0)
        features.append(1.0 if contract_metadata.get('is_proxy') else 0.0)
        features.append(1.0 if contract_metadata.get('library_usage') else 0.0)
        features.append(1.0 if contract_metadata.get('has_comments') else 0.0)
        
        # Pad or truncate to fixed length (128 dimensions)
        target_length = 128
        if len(features) < target_length:
            features.extend([0.0] * (target_length - len(features)))
        else:
            features = features[:target_length]
            
        return features

    def validate_model_output(self, output: ModelOutput) -> bool:
        """Validate that model output contains reasonable values."""
        if not (0 <= output.risk_score <= 1.0):
            return False
        if not (0 <= output.confidence <= 1.0):
            return False
        if not output.explanation or len(output.explanation.strip()) < 10:
            return False
        if not isinstance(output.detected_issues, list):
            return False
        if not isinstance(output.recommendations, list):
            return False
            
        return True