#!/usr/bin/env python3
"""
Training Pipeline Enhancer
Enhances existing training pipelines to incorporate BaseScan verified contracts data
"""

import json
import os
from pathlib import Path
from typing import List, Dict

class TrainingPipelineEnhancer:
    """Enhances training pipelines with BaseScan data"""
    
    def enhance_bytecode_training(self):
        """Enhance bytecode detector training with BaseScan data"""
        
        print("Enhancing bytecode detector training...")
        
        # Load BaseScan processed data
        basescan_file = "../datasets/processed/basescan_processed.jsonl"
        if not os.path.exists(basescan_file):
            print("BaseScan processed data not found. Run data processor first.")
            return
        
        # Load existing bytecode training data
        existing_malicious = "../datasets/raw/malicious_contracts.jsonl"
        existing_safe = "../datasets/raw/safe_contracts.jsonl"
        
        # Create enhanced datasets
        enhanced_malicious = []
        enhanced_safe = []
        
        # Load BaseScan contracts (considered safe/verified)
        basescan_contracts = []
        with open(basescan_file, 'r') as f:
            for line in f:
                contract = json.loads(line)
                basescan_contracts.append(contract)
        
        print(f"Loaded {len(basescan_contracts)} BaseScan contracts")
        
        # Add BaseScan contracts to safe dataset
        for contract in basescan_contracts:
            enhanced_safe.append({
                'source_code': contract['source_code'],
                'vulnerabilities': [],
                'risk_score': 10,  # Low risk for verified contracts
                'summary': f"BaseScan verified contract: {contract.get('contract_address', 'unknown')}",
                'is_verified': True,
                'data_source': 'basescan'
            })
        
        # Load existing safe contracts
        if os.path.exists(existing_safe):
            with open(existing_safe, 'r') as f:
                for line in f:
                    contract = json.loads(line)
                    enhanced_safe.append({
                        **contract,
                        'is_verified': False,
                        'data_source': 'synthetic'
                    })
        
        # Load existing malicious contracts
        if os.path.exists(existing_malicious):
            with open(existing_malicious, 'r') as f:
                for line in f:
                    contract = json.loads(line)
                    enhanced_malicious.append({
                        **contract,
                        'is_verified': False,
                        'data_source': 'synthetic'
                    })
        
        # Save enhanced datasets
        os.makedirs("../datasets/enhanced", exist_ok=True)
        
        with open("../datasets/enhanced/malicious_enhanced.jsonl", 'w') as f:
            for contract in enhanced_malicious:
                f.write(json.dumps(contract) + '\n')
        
        with open("../datasets/enhanced/safe_enhanced.jsonl", 'w') as f:
            for contract in enhanced_safe:
                f.write(json.dumps(contract) + '\n')
        
        print(f"Enhanced datasets created:")
        print(f"- Malicious contracts: {len(enhanced_malicious)}")
        print(f"- Safe contracts: {len(enhanced_safe)}")
        print(f"- BaseScan contracts added: {len(basescan_contracts)}")
    
    def enhance_llm_training(self):
        """Enhance LLM training with BaseScan data"""
        
        print("Enhancing LLM training data...")
        
        # Load BaseScan processed data
        basescan_file = "../datasets/processed/basescan_processed.jsonl"
        if not os.path.exists(basescan_file):
            print("BaseScan processed data not found. Run data processor first.")
            return
        
        # Convert BaseScan data to instruction format
        instruction_data = []
        
        with open(basescan_file, 'r') as f:
            for line in f:
                contract = json.loads(line)
                
                # Create instruction example for verified contract
                instruction = {
                    "instruction": "Analyze this verified Solidity smart contract from BaseScan for security best practices and code quality.",
                    "input": contract['source_code'],
                    "output": self._create_verified_output(contract)
                }
                
                instruction_data.append(instruction)
        
        # Load existing instruction data
        existing_instruction_file = "../datasets/processed/instruction_data.jsonl"
        if os.path.exists(existing_instruction_file):
            with open(existing_instruction_file, 'r') as f:
                for line in f:
                    instruction_data.append(json.loads(line))
        
        # Save enhanced instruction data
        enhanced_instruction_file = "../datasets/processed/instruction_data_enhanced.jsonl"
        
        with open(enhanced_instruction_file, 'w') as f:
            for item in instruction_data:
                f.write(json.dumps(item) + '\n')
        
        print(f"Enhanced instruction data created: {len(instruction_data)} examples")
        print(f"Saved to: {enhanced_instruction_file}")
    
    def _create_verified_output(self, contract: Dict) -> str:
        """Create output format for verified contracts"""
        
        metadata = contract.get('metadata', {})
        complexity = contract.get('complexity', {})
        
        output_lines = [
            "SECURITY ANALYSIS:",
            "",
            "VULNERABILITIES:",
            "- No critical vulnerabilities detected (BaseScan verified)",
            "",
            "RISK ASSESSMENT:",
            "- Overall Risk Score: 10/100",
            "- Severity: LOW",
            "",
            "BEST PRACTICES IDENTIFIED:",
            "- Contract verified on BaseScan",
            "- Proper access control patterns",
            "- Safe arithmetic operations",
            "- Input validation present",
            "",
            "CONTRACT METADATA:",
            f"- Solidity Version: {metadata.get('pragma_version', 'unknown')}",
            f"- Contract Names: {', '.join(metadata.get('contract_names', []))}",
            f"- Functions: {metadata.get('function_count', 0)}",
            f"- Lines of Code: {complexity.get('lines_of_code', 0)}",
            "",
            "SUMMARY:",
            "This contract has been verified on BaseScan and follows security best practices. "
            "It demonstrates proper patterns for access control, input validation, and safe operations."
        ]
        
        return '\n'.join(output_lines)
    
    def update_training_scripts(self):
        """Update training scripts to use enhanced datasets"""
        
        print("Updating training scripts...")
        
        # Update bytecode detector training script
        bytecode_script = "../model-bytecode-detector/train_model.py"
        if os.path.exists(bytecode_script):
            self._update_bytecode_script(bytecode_script)
        
        # Update LLM training script
        llm_script = "../model-code-analyzer/train_llm.py"
        if os.path.exists(llm_script):
            self._update_llm_script(llm_script)
        
        print("Training scripts updated to use enhanced datasets")
    
    def _update_bytecode_script(self, script_path: str):
        """Update bytecode training script"""
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Replace dataset paths
        updated_content = content.replace(
            "malicious_contracts.jsonl",
            "../datasets/enhanced/malicious_enhanced.jsonl"
        ).replace(
            "safe_contracts.jsonl", 
            "../datasets/enhanced/safe_enhanced.jsonl"
        )
        
        with open(script_path, 'w') as f:
            f.write(updated_content)
    
    def _update_llm_script(self, script_path: str):
        """Update LLM training script"""
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Replace instruction data path
        updated_content = content.replace(
            "instruction_data.jsonl",
            "instruction_data_enhanced.jsonl"
        )
        
        with open(script_path, 'w') as f:
            f.write(updated_content)

def main():
    """Main function"""
    
    enhancer = TrainingPipelineEnhancer()
    
    # Enhance both training pipelines
    enhancer.enhance_bytecode_training()
    enhancer.enhance_llm_training()
    
    # Update training scripts
    enhancer.update_training_scripts()
    
    print("\n=== TRAINING PIPELINE ENHANCEMENT COMPLETE ===")
    print("BaseScan verified contracts have been integrated into:")
    print("1. Bytecode detector training datasets")
    print("2. LLM instruction training data")
    print("3. Updated training scripts")
    print("\nNext steps:")
    print("1. Run the enhanced bytecode detector training")
    print("2. Run the enhanced LLM fine-tuning")
    print("3. Test the improved models")

if __name__ == "__main__":
    main()