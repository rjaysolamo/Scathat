#!/usr/bin/env python3
"""
BaseScan Data Processor
Processes and cleans scraped BaseScan contracts for AI model training
"""

import json
import re
import os
from pathlib import Path
from typing import List, Dict, Any
import hashlib

class BaseScanDataProcessor:
    """Processor for cleaning and preparing BaseScan contract data"""
    
    def __init__(self):
        self.solidity_patterns = {
            'pragma': r'pragma solidity\s+[^;]+;',
            'contract': r'contract\s+\w+',
            'function': r'function\s+\w+\s*\([^)]*\)',
            'import': r'import\s+[^;]+;'

        }
    
    def validate_contract_data(self, contract_data: Dict) -> bool:
        """Validate contract data meets minimum quality standards"""
        
        # Check required fields
        if not contract_data.get('source_code'):
            return False
        
        source_code = contract_data['source_code']
        
        # Minimum length check
        if len(source_code.strip()) < 100:
            return False
        
        # Check if it contains Solidity keywords
        solidity_keywords = ['pragma', 'contract', 'function', 'returns', 'public', 'private']
        has_keywords = any(keyword in source_code for keyword in solidity_keywords)
        
        if not has_keywords:
            return False
        
        return True
    
    def clean_source_code(self, source_code: str) -> str:
        """Clean and normalize Solidity source code"""
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', source_code)
        
        # Remove comments
        cleaned = re.sub(r'//.*?\n', '\n', cleaned)  # Single line comments
        cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)  # Multi-line comments
        
        # Normalize line endings
        cleaned = cleaned.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove multiple consecutive empty lines
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        
        return cleaned.strip()
    
    def extract_contract_metadata(self, source_code: str) -> Dict[str, Any]:
        """Extract metadata from Solidity source code"""
        
        metadata = {
            'pragma_version': '',
            'contract_names': [],
            'function_count': 0,
            'import_count': 0,
            'code_hash': ''
        }
        
        # Extract pragma version
        pragma_match = re.search(self.solidity_patterns['pragma'], source_code)
        if pragma_match:
            metadata['pragma_version'] = pragma_match.group(0)
        
        # Extract contract names
        contract_matches = re.findall(self.solidity_patterns['contract'], source_code)
        metadata['contract_names'] = [match.split()[1] for match in contract_matches if len(match.split()) > 1]
        
        # Count functions
        function_matches = re.findall(self.solidity_patterns['function'], source_code)
        metadata['function_count'] = len(function_matches)
        
        # Count imports
        import_matches = re.findall(self.solidity_patterns['import'], source_code)
        metadata['import_count'] = len(import_matches)
        
        # Calculate code hash
        metadata['code_hash'] = hashlib.sha256(source_code.encode()).hexdigest()
        
        return metadata
    
    def analyze_contract_complexity(self, source_code: str) -> Dict[str, Any]:
        """Analyze contract complexity metrics"""
        
        complexity = {
            'lines_of_code': 0,
            'cyclomatic_complexity': 0,
            'nesting_depth': 0,
            'modifier_count': 0,
            'event_count': 0
        }
        
        # Count lines of code
        complexity['lines_of_code'] = len(source_code.split('\n'))
        
        # Count modifiers
        modifier_matches = re.findall(r'modifier\s+\w+', source_code)
        complexity['modifier_count'] = len(modifier_matches)
        
        # Count events
        event_matches = re.findall(r'event\s+\w+', source_code)
        complexity['event_count'] = len(event_matches)
        
        # Simple cyclomatic complexity approximation
        decision_points = len(re.findall(r'(if|for|while|catch)\s*\(', source_code))
        complexity['cyclomatic_complexity'] = decision_points + 1
        
        return complexity
    
    def process_contracts_batch(self, input_file: str, output_file: str) -> None:
        """Process a batch of contracts from JSONL file"""
        
        processed_contracts = []
        
        print(f"Processing contracts from {input_file}...")
        
        with open(input_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    contract_data = json.loads(line)
                    
                    # Validate contract
                    if not self.validate_contract_data(contract_data):
                        print(f"Skipping invalid contract at line {line_num}")
                        continue
                    
                    # Clean source code
                    cleaned_code = self.clean_source_code(contract_data['source_code'])
                    
                    # Extract metadata
                    metadata = self.extract_contract_metadata(cleaned_code)
                    
                    # Analyze complexity
                    complexity = self.analyze_contract_complexity(cleaned_code)
                    
                    # Create enhanced contract data
                    enhanced_contract = {
                        **contract_data,
                        'source_code': cleaned_code,
                        'metadata': metadata,
                        'complexity': complexity,
                        'processed': True,
                        'processing_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    processed_contracts.append(enhanced_contract)
                    
                    if line_num % 100 == 0:
                        print(f"Processed {line_num} contracts...")
                        
                except json.JSONDecodeError:
                    print(f"Invalid JSON at line {line_num}")
                except Exception as e:
                    print(f"Error processing contract at line {line_num}: {e}")
        
        # Save processed contracts
        with open(output_file, 'w') as f:
            for contract in processed_contracts:
                f.write(json.dumps(contract) + '\n')
        
        print(f"Processed {len(processed_contracts)} contracts. Saved to {output_file}")
        
        # Print statistics
        self.print_processing_stats(processed_contracts)
    
    def print_processing_stats(self, contracts: List[Dict]) -> None:
        """Print processing statistics"""
        
        total_contracts = len(contracts)
        
        if total_contracts == 0:
            print("No contracts processed.")
            return
        
        # Calculate averages
        avg_lines = sum(c['complexity']['lines_of_code'] for c in contracts) / total_contracts
        avg_functions = sum(c['metadata']['function_count'] for c in contracts) / total_contracts
        avg_complexity = sum(c['complexity']['cyclomatic_complexity'] for c in contracts) / total_contracts
        
        print(f"\n=== PROCESSING STATISTICS ===")
        print(f"Total contracts processed: {total_contracts}")
        print(f"Average lines of code: {avg_lines:.1f}")
        print(f"Average functions per contract: {avg_functions:.1f}")
        print(f"Average cyclomatic complexity: {avg_complexity:.1f}")
        
        # Count contracts by Solidity version
        version_counts = {}
        for contract in contracts:
            version = contract['metadata']['pragma_version']
            version_counts[version] = version_counts.get(version, 0) + 1
        
        print(f"\nSolidity versions distribution:")
        for version, count in version_counts.items():
            if version:  # Skip empty versions
                percentage = (count / total_contracts) * 100
                print(f"  {version}: {count} contracts ({percentage:.1f}%)")

def main():
    """Main function"""
    
    processor = BaseScanDataProcessor()
    
    # Process BaseScan contracts
    processor.process_contracts_batch(
        input_file="../datasets/raw/basescan_contracts.jsonl",
        output_file="../datasets/processed/basescan_processed.jsonl"
    )
    
    # Also create a sample for testing
    processor.process_contracts_batch(
        input_file="../datasets/raw/basescan_contracts.jsonl",
        output_file="../datasets/test/basescan_sample.jsonl"
    )

if __name__ == "__main__":
    import time
    main()