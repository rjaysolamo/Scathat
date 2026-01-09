// Smart contract client for interacting with ResultsRegistry
import { ethers } from './ethers.min.js';

class ContractClient {
    constructor() {
        this.provider = null;
        this.signer = null;
        this.contract = null;
        this.contractAddress = '0x8dCcDf8Be8B32492896281413B45e075B1f5EDe5';
        this.contractABI = [
            // Contract ABI will be loaded dynamically
        ];
    }

    // Initialize with Ethereum provider
    async initialize(ethereumProvider) {
        try {
            this.provider = new ethers.BrowserProvider(ethereumProvider);
            this.signer = await this.provider.getSigner();
            
            // Load contract ABI dynamically
            await this.loadContractABI();
            
            this.contract = new ethers.Contract(
                this.contractAddress,
                this.contractABI,
                this.signer
            );
            
            console.log('Contract client initialized successfully');
            return true;
        } catch (error) {
            console.error('Failed to initialize contract client:', error);
            throw error;
        }
    }

    // Load contract ABI from the smart contract project
    async loadContractABI() {
        try {
            // In a real implementation, this would fetch the ABI from the artifacts
            // For now, we'll use a minimal ABI for the required functions
            this.contractABI = [
                {
                    "inputs": [
                        {"internalType": "address", "name": "_contractAddress", "type": "address"},
                        {"internalType": "string", "name": "_riskScore", "type": "string"},
                        {"internalType": "uint8", "name": "_riskLevel", "type": "uint8"}
                    ],
                    "name": "writeRiskScore",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [
                        {"internalType": "address", "name": "_contractAddress", "type": "address"},
                        {"internalType": "string", "name": "_riskScore", "type": "string"},
                        {"internalType": "uint8", "name": "_riskLevel", "type": "uint8"}
                    ],
                    "name": "updateRiskScore",
                    "outputs": [],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [{"internalType": "address", "name": "_contractAddress", "type": "address"}],
                    "name": "getRiskScore",
                    "outputs": [{"internalType": "string", "name": "", "type": "string"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [{"internalType": "address", "name": "writer", "type": "address"}],
                    "name": "isAuthorizedWriter",
                    "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                    "stateMutability": "view",
                    "type": "function"
                }
            ];
        } catch (error) {
            console.error('Failed to load contract ABI:', error);
            throw error;
        }
    }

    // Check if current address is authorized to write to contract
    async isAuthorized() {
        try {
            const address = await this.signer.getAddress();
            return await this.contract.isAuthorizedWriter(address);
        } catch (error) {
            console.error('Authorization check failed:', error);
            return false;
        }
    }

    // Write risk score to contract (requires signature)
    async writeRiskScore(contractAddress, riskScore, riskLevel) {
        try {
            // Check authorization first
            const isAuthorized = await this.isAuthorized();
            if (!isAuthorized) {
                throw new Error('Wallet not authorized to write to contract');
            }

            // Send transaction (this will trigger wallet signature)
            const tx = await this.contract.writeRiskScore(
                contractAddress,
                riskScore,
                riskLevel
            );

            console.log('Transaction sent:', tx.hash);
            
            // Wait for confirmation
            const receipt = await tx.wait();
            console.log('Transaction confirmed:', receipt);
            
            return {
                success: true,
                transactionHash: tx.hash,
                blockNumber: receipt.blockNumber
            };
        } catch (error) {
            console.error('Failed to write risk score:', error);
            throw error;
        }
    }

    // Get risk score from contract
    async getRiskScore(contractAddress) {
        try {
            return await this.contract.getRiskScore(contractAddress);
        } catch (error) {
            console.error('Failed to get risk score:', error);
            throw error;
        }
    }

    // Sign a message with the wallet (for authentication)
    async signMessage(message) {
        try {
            const signature = await this.signer.signMessage(message);
            return signature;
        } catch (error) {
            console.error('Failed to sign message:', error);
            throw error;
        }
    }

    // Get current wallet address
    async getAddress() {
        try {
            return await this.signer.getAddress();
        } catch (error) {
            console.error('Failed to get address:', error);
            throw error;
        }
    }
}

export default new ContractClient();