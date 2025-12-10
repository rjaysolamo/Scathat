#!/usr/bin/env python3
"""
BaseScan Verified Contracts Scraper
Scrapes verified smart contracts from BaseScan for AI model training
"""

import requests
import json
import time
import os
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from pathlib import Path

class BaseScanScraper:
    """Scraper for BaseScan verified contracts"""
    
    def __init__(self, base_url: str = "https://basescan.org"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_verified_contracts_list(self, page: int = 1, per_page: int = 100) -> List[Dict]:
        """Get list of verified contracts from BaseScan"""
        
        # BaseScan uses paginated API for verified contracts
        url = f"{self.base_url}/contractsVerified?ps={per_page}&p={page}"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            contracts = []
            
            # Parse the contracts table
            table = soup.find('table', {'class': 'table'})
            if table:
                rows = table.find_all('tr')[1:]  # Skip header row
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 6:
                        # Extract full address from the link href instead of truncated text
                        address_link = cols[0].find('a')
                        if address_link and address_link.get('href'):
                            href = address_link['href']
                            # Extract address from href like "/address/0x1234...5678"
                            if '/address/' in href:
                                full_address = href.split('/address/')[1].split('#')[0].split('?')[0]
                            else:
                                full_address = cols[0].text.strip()
                        else:
                            full_address = cols[0].text.strip()
                        
                        contract = {
                            'address': full_address,
                            'contract_name': cols[1].text.strip(),
                            'compiler': cols[2].text.strip(),
                            'version': cols[3].text.strip(),
                            'balance': cols[4].text.strip(),
                            'txns': cols[5].text.strip(),
                            'verified_date': cols[6].text.strip() if len(cols) > 6 else ''
                        }
                        contracts.append(contract)
            
            return contracts
            
        except Exception as e:
            print(f"Error fetching contracts list: {e}")
            return []
    
    def get_contract_details(self, contract_address: str) -> Optional[Dict]:
        """Get complete contract details including source code, bytecode, ABI, and metadata"""
        
        url = f"{self.base_url}/address/{contract_address}#code"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Initialize contract data with basic information
            contract_data = {
                'address': contract_address,
                'verified': True,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'source_code': "",
                'deployed_bytecode': "",
                'creation_bytecode': "",
                'abi': "",
                'compiler_version': "",
                'contract_name': ""
            }
            
            # Extract source code and related data from pre tags
            pre_tags = soup.find_all('pre')
            
            for pre in pre_tags:
                content = pre.text.strip()
                
                # Source code (contains Solidity keywords)
                if 'pragma solidity' in content or 'contract ' in content:
                    contract_data['source_code'] = content
                
                # ABI (JSON array format)
                elif content.startswith('[') and content.endswith(']') and 'function' in content:
                    contract_data['abi'] = content
                
                # Bytecode (starts with 0x, reasonable length)
                elif content.startswith('0x') and len(content) > 100:
                    # Check if it's creation or deployed bytecode based on context
                    parent = pre.find_parent()
                    parent_text = parent.text.lower() if parent else ""
                    
                    if 'creation' in parent_text or 'constructor' in parent_text:
                        contract_data['creation_bytecode'] = content
                    elif 'deployed' in parent_text or 'runtime' in parent_text:
                        contract_data['deployed_bytecode'] = content
                    else:
                        # Default to deployed bytecode if context is unclear
                        contract_data['deployed_bytecode'] = content
            
            # Extract bytecode information with more specific targeting
            # Look for bytecode in specific sections and tabs
            bytecode_selectors = [
                'div[data-target="bytecode.tab"]',
                'div.tab-pane[data-target*="bytecode"]',
                'div.card:has(div.card-header:contains("Bytecode"))',
                'pre:contains("0x")',  # Bytecode typically starts with 0x
                'code:contains("0x")'
            ]
            
            for selector in bytecode_selectors:
                try:
                    elements = soup.select(selector)
                    for elem in elements:
                        elem_text = elem.text.strip().lower()
                        code_text = elem.text.strip()
                        
                        # Check if this looks like bytecode (starts with 0x, reasonable length)
                        if code_text.startswith('0x') and len(code_text) > 50:
                            if 'deployed' in elem_text or 'runtime' in elem_text:
                                contract_data['deployed_bytecode'] = code_text
                            elif 'creation' in elem_text or 'constructor' in elem_text or 'init' in elem_text:
                                contract_data['creation_bytecode'] = code_text
                            elif not contract_data['deployed_bytecode']:  # Default to deployed if unsure
                                contract_data['deployed_bytecode'] = code_text
                except:
                    continue
            
            # Extract ABI (Application Binary Interface) with better targeting
            abi_selectors = [
                'div[data-target="abi.tab"]',
                'div.tab-pane[data-target*="abi"]',
                'div.card:has(div.card-header:contains("ABI"))',
                'pre:contains("[")',  # ABI is JSON array
                'textarea:contains("[")',
                'code:contains("function")'  # ABI contains function definitions
            ]
            
            for selector in abi_selectors:
                try:
                    elements = soup.select(selector)
                    for elem in elements:
                        abi_text = elem.text.strip()
                        # Basic validation that this looks like ABI JSON
                        if abi_text.startswith('[') and abi_text.endswith(']') and 'function' in abi_text:
                            contract_data['abi'] = abi_text
                            break
                except:
                    continue
            
            # Extract detailed contract metadata from info cards
            info_cards = soup.find_all('div', {'class': 'card'})
            for card in info_cards:
                card_title = card.find('div', {'class': 'card-header'})
                if card_title:
                    title_text = card_title.text.strip().lower()
                    
                    # Contract details section
                    if 'contract details' in title_text or 'overview' in title_text:
                        rows = card.find_all('tr')
                        for row in rows:
                            cols = row.find_all('td')
                            if len(cols) >= 2:
                                key = cols[0].text.strip().lower().replace(' ', '_')
                                value = cols[1].text.strip()
                                
                                # Map common fields to standardized names
                                if 'contract_name' in key or 'name' in key:
                                    contract_data['contract_name'] = value
                                elif 'compiler' in key or 'version' in key:
                                    contract_data['compiler_version'] = value
                                elif 'balance' in key:
                                    contract_data['balance'] = value
                                elif 'transactions' in key or 'txns' in key:
                                    contract_data['transactions'] = value
                                else:
                                    contract_data[key] = value
            
            # If contract name not found in metadata, try to extract from source code
            if not contract_data['contract_name'] and contract_data['source_code']:
                import re
                contract_match = re.search(r'contract\s+(\w+)', contract_data['source_code'])
                if contract_match:
                    contract_data['contract_name'] = contract_match.group(1)
            
            # If compiler version not found in metadata, try to extract from source code
            if not contract_data['compiler_version'] and contract_data['source_code']:
                import re
                compiler_match = re.search(r'pragma solidity\s+(.*?);', contract_data['source_code'])
                if compiler_match:
                    contract_data['compiler_version'] = compiler_match.group(1)
            
            # Extract bytecode and ABI from info cards (this should be separate from the source code extraction)
            info_cards = soup.find_all('div', {'class': 'card'})
            for card in info_cards:
                card_title = card.find('div', {'class': 'card-header'})
                if card_title:
                    title_text = card_title.text.strip().lower()
                    
                    # Bytecode sections
                    if 'bytecode' in title_text:
                        code_elem = card.find('pre') or card.find('code')
                        if code_elem:
                            code_text = code_elem.text.strip()
                            if 'deployed' in title_text:
                                contract_data['deployed_bytecode'] = code_text
                            elif 'creation' in title_text:
                                contract_data['creation_bytecode'] = code_text
                    
                    # ABI section
                    elif 'abi' in title_text or 'interface' in title_text:
                        code_elem = card.find('pre') or card.find('code') or card.find('textarea')
                        if code_elem and code_elem.text.strip():
                            contract_data['abi'] = code_elem.text.strip()
            
            # Additional metadata extraction
            # Look for contract name in page title or headings
            page_title = soup.find('title')
            if page_title and contract_address.lower() in page_title.text.lower():
                title_parts = page_title.text.split('-')
                if len(title_parts) > 1:
                    potential_name = title_parts[0].strip()
                    if potential_name and len(potential_name) > 2:
                        contract_data['contract_name'] = potential_name
            
            # Look for compiler version in meta tags or specific elements
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                if meta.get('name') and 'compiler' in meta.get('name', '').lower():
                    contract_data['compiler_version'] = meta.get('content', '')
            
            return contract_data
            
        except Exception as e:
            print(f"Error fetching contract details for {contract_address}: {e}")
            return None
    
    def scrape_contracts(self, max_contracts: int = 1000, output_dir: str = "../datasets/external/basescan") -> None:
        """Scrape multiple verified contracts"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Starting BaseScan contract scraping...")
        print(f"Target: {max_contracts} contracts")
        print(f"Output directory: {output_dir}")
        
        scraped_count = 0
        page = 1
        
        while scraped_count < max_contracts:
            print(f"Fetching page {page}...")
            
            contracts_list = self.get_verified_contracts_list(page=page)
            if not contracts_list:
                print("No more contracts found.")
                break
            
            for contract in contracts_list:
                if scraped_count >= max_contracts:
                    break
                
                contract_address = contract['address']
                print(f"Scraping contract {scraped_count + 1}/{max_contracts}: {contract_address}")
                
                contract_data = self.get_contract_details(contract_address)
                if contract_data:
                    # Save contract data
                    filename = f"{contract_address}.json"
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, 'w') as f:
                        json.dump(contract_data, f, indent=2)
                    
                    scraped_count += 1
                    print(f"Saved contract {contract_address}")
                
                # Be respectful with rate limiting
                time.sleep(2)
            
            page += 1
            
            # Add delay between pages
            time.sleep(5)
        
        print(f"Scraping completed. Saved {scraped_count} contracts.")
    
    def create_training_dataset(self, input_dir: str, output_file: str) -> None:
        """Create training dataset from scraped contracts"""
        
        contracts_data = []
        
        # Load all scraped contracts
        for file_path in Path(input_dir).glob("*.json"):
            with open(file_path, 'r') as f:
                contract_data = json.load(f)
                contracts_data.append(contract_data)
        
        print(f"Loaded {len(contracts_data)} contracts")
        
        # Convert to training format with enhanced contract data
        training_data = []
        for contract in contracts_data:
            training_example = {
                'source_code': contract.get('source_code', ''),
                'contract_address': contract.get('address', ''),
                'contract_name': contract.get('contract_name', ''),
                'compiler_version': contract.get('compiler_version', ''),
                'deployed_bytecode': contract.get('deployed_bytecode', ''),
                'creation_bytecode': contract.get('creation_bytecode', ''),
                'abi': contract.get('abi', ''),
                'verified': True,
                'scraped_from': 'basescan',
                'vulnerabilities': [],  # Will be analyzed later
                'risk_score': 0,       # Will be calculated later
                'summary': 'BaseScan verified contract',
                'balance': contract.get('balance', ''),
                'transactions': contract.get('transactions', ''),
                'verified_date': contract.get('verified_date', '')
            }
            training_data.append(training_example)
        
        # Save as JSONL
        with open(output_file, 'w') as f:
            for item in training_data:
                f.write(json.dumps(item) + '\n')
        
        print(f"Created training dataset with {len(training_data)} examples at {output_file}")

def main():
    """Main function"""
    
    scraper = BaseScanScraper()
    
    # Scrape contracts
    scraper.scrape_contracts(
        max_contracts=500,  # Start with 500 contracts for initial training
        output_dir="../datasets/external/basescan"
    )
    
    # Create training dataset
    scraper.create_training_dataset(
        input_dir="../datasets/external/basescan",
        output_file="../datasets/raw/basescan_contracts.jsonl"
    )

if __name__ == "__main__":
    main()