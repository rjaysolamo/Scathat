# Model Aggregator

## 📋 Overview

AI model that combines outputs from specialized models (code analyzer, bytecode detector, behavior analysis) to produce unified risk assessments and comprehensive security evaluations.

## 🎯 Core Capabilities

### Multi-Model Fusion
- Weighted aggregation of model outputs
- Confidence-based score combination
- Conflict resolution between models
- Unified risk assessment

### Decision Making
- Final risk classification
- Confidence scoring
- Explanation generation
- Action recommendation

### Consistency Checking
- Cross-model validation
- Anomaly detection in model outputs
- Confidence calibration
- Uncertainty quantification

## 🏗️ Model Architecture

```python
class AggregatorModel:
    """Neural network for multi-model output aggregation"""
    
    def __init__(self):
        # Attention-based fusion mechanism
        self.attention_fusion = MultiHeadAttentionFusion()
        
        # Confidence-weighted averaging
        self.confidence_weighting = ConfidenceWeightedAverage()
        
        # Explanation generation
        self.explanation_generator = ExplanationGenerator()
        
        # Decision making components
        self.risk_classifier = RiskClassificationHead()
        self.recommendation_engine = RecommendationEngine()
    
    def aggregate_results(self, model_outputs: Dict[str, Dict]) -> Dict:
        """Aggregate results from multiple specialized models"""
        pass
```

## 📊 Input/Output Format

### Input
```json
{
  "code_analysis": {
    "risk_score": 0.85,
    "confidence": 0.92,
    "vulnerabilities": [...],
    "processing_time_ms": 45
  },
  "bytecode_analysis": {
    "risk_score": 0.72,
    "confidence": 0.88,
    "detected_patterns": [...],
    "processing_time_ms": 28
  },
  "behavior_analysis": {
    "behavior_score": 0.68,
    "anomaly_score": 0.82,
    "detected_patterns": [...],
    "processing_time_ms": 75
  }
}
```

### Output
```json
{
  "final_risk_score": 0.78,
  "overall_confidence": 0.89,
  "risk_level": "high",
  "explanation": "Combined analysis indicates multiple risk factors including code vulnerabilities and suspicious behavior patterns",
  "contributing_factors": [
    {
      "factor": "Code vulnerabilities",
      "weight": 0.45,
      "details": "Reentrancy vulnerability detected"
    },
    {
      "factor": "Behavior patterns", 
      "weight": 0.35,
      "details": "Unusual transaction patterns detected"
    },
    {
      "factor": "Bytecode analysis",
      "weight": 0.20,
      "details": "Proxy contract pattern detected"
    }
  ],
  "recommendations": [
    "Immediate review required",
    "Consider blocking interactions",
    "Monitor for suspicious activity"
  ],
  "processing_time_ms": 12
}
```

## 🚀 Integration

### Python API
```python
from model_aggregator import ResultAggregator

aggregator = ResultAggregator.load("latest")
final_result = aggregator.aggregate({
    "code": code_result,
    "bytecode": bytecode_result, 
    "behavior": behavior_result
})
```

### REST Endpoint
```bash
POST /analyze/aggregate
Content-Type: application/json

{"model_outputs": {"code": {...}, "bytecode": {...}, "behavior": {...}}}
```

## 🐳 Deployment

### Using Docker (Recommended)

1. **Build and run**:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

2. **Using Docker Compose**:
   ```bash
   docker-compose up -d
   ```

### Manual Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server**:
   ```bash
   uvicorn api_server:app --host 0.0.0.0 --port 8001 --reload
   ```

### Configuration

#### Environment Variables
- `BYTECODE_API_URL`: URL of the bytecode detector service (default: `http://localhost:8000`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `PYTHONPATH`: Python path (default: current directory)

#### API Endpoints
- `GET /health` - Service health check
- `POST /analyze/bytecode` - Bytecode-only analysis
- `POST /analyze/multimodel` - Multi-model comprehensive analysis
- `GET /models/status` - Model availability status

### Docker Deployment Features
- Multi-stage build for optimized image size
- Health checks and monitoring
- Log persistence to mounted volumes
- Automatic restarts on failure

## 📈 Performance Targets

- **Accuracy**: >98% on final risk assessment
- **Consistency**: >95% agreement with expert assessment
- **Latency**: <20ms per aggregation
- **Throughput**: 200+ aggregations/second

## 🧪 Testing

Comprehensive test suite including:
- Aggregation accuracy validation
- Conflict resolution testing
- Explanation quality assessment
- Performance benchmarking

## 📚 Training Data

Trained on:
- 10,000+ expert-labeled risk assessments
- Multi-model output combinations
- Ground truth risk evaluations
- Explanation quality ratings

## 🔍 Technical Features

- **Attention Mechanisms**: Focus on most relevant model outputs
- **Confidence Weighting**: Weight models by their confidence scores
- **Explanation Generation**: Natural language explanations of decisions
- **Uncertainty Propagation**: Proper handling of model uncertainties
- **Conflict Resolution**: Intelligent resolution of model disagreements

## 🎯 Aggregation Strategies

### Weighted Average
- Models weighted by confidence scores
- Dynamic weighting based on input characteristics

### Hierarchical Fusion
- Multi-level aggregation architecture
- Feature-level and decision-level fusion

### Ensemble Methods
- Bayesian model averaging
- Stacking with meta-learners
- Voting-based approaches

## 📊 Output Quality Metrics

- **Explanation Quality**: Human-evaluated explanation clarity
- **Decision Consistency**: Stability across similar inputs
- **Confidence Calibration**: Proper confidence score calibration
- **Uncertainty Quantification**: Accurate uncertainty estimates

## 🔄 Integration Pipeline

1. **Input Collection**: Gather outputs from all specialized models
2. **Preprocessing**: Normalize scores and format data
3. **Fusion**: Apply aggregation algorithms
4. **Decision Making**: Generate final risk assessment
5. **Explanation**: Create human-readable explanations
6. **Output**: Return comprehensive results

## 🛡️ Quality Assurance

- **Cross-validation**: Ensure robust performance across datasets
- **A/B Testing**: Compare aggregation strategies
- **Human Evaluation**: Validate against expert assessments
- **Continuous Monitoring**: Track performance in production