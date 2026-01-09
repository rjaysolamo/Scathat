// Scathat Popup JavaScript
class ScathatPopup {
    constructor() {
        this.connected = false;
        this.sessionId = null;
        this.settings = {};
        this.stats = {
            scannedContracts: 0,
            threatsBlocked: 0,
            savedFunds: 0
        };
        
        // Wallet connection properties
        this.walletDetected = false;
        this.walletConnected = false;
        this.walletAccounts = [];
        this.walletSignature = null;
        this.contractAuthorized = false;
        
        this.init();
    }

    async init() {
        await this.loadSettings();
        await this.checkConnectionStatus();
        await this.checkWalletStatus();
        this.setupEventListeners();
        this.updateUI();
        this.updateWalletUI();
        
        console.log('Scathat popup initialized');
    }

    async loadSettings() {
        try {
            const result = await chrome.storage.local.get(['settings', 'stats']);
            this.settings = result.settings || {
                autoScan: true,
                notifications: true,
                highlightContracts: true
            };
            
            if (result.stats) {
                this.stats = result.stats;
            }
            
            this.updateSettingsUI();
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }

    updateUI() {
        const indicator = document.getElementById('statusIndicator');
        const dot = indicator.querySelector('.status-dot');
        const text = indicator.querySelector('.status-text');
        
        if (this.connected) {
            dot.classList.add('connected');
            text.textContent = 'Connected';
        } else {
            dot.classList.remove('connected');
            text.textContent = 'Disconnected';
        }
        
        document.getElementById('disconnectBtn').style.display = this.connected ? '' : 'none';
    }

    setupEventListeners() {
        document.getElementById('connectBtn').addEventListener('click', async () => {
            await this.connectWallet();
        });

        document.getElementById('disconnectBtn').addEventListener('click', async () => {
            await this.disconnect();
        });

        document.getElementById('connectWalletBtn').addEventListener('click', async () => {
            await this.connectWallet();
        });

        document.getElementById('disconnectWalletBtn').addEventListener('click', async () => {
            await this.disconnectWallet();
        });

        document.getElementById('scanCurrentPage').addEventListener('click', async () => {
            await this.scanCurrentPage();
        });

        document.getElementById('openDashboard').addEventListener('click', () => {
            this.openDashboard();
        });
        
        document.getElementById('autoScanToggle').addEventListener('change', (e) => {
            this.updateSetting('autoScan', e.target.checked);
        });
        
        document.getElementById('notificationsToggle').addEventListener('change', (e) => {
            this.updateSetting('notifications', e.target.checked);
        });
        
        document.getElementById('highlightToggle').addEventListener('change', (e) => {
            this.updateSetting('highlightContracts', e.target.checked);
        });
        
        document.getElementById('helpLink').addEventListener('click', (e) => {
            e.preventDefault();
            this.openHelp();
        });
        
        document.getElementById('feedbackLink').addEventListener('click', (e) => {
            e.preventDefault();
            this.openFeedback();
        });
    }

    async checkConnectionStatus() {
        try {
            const result = await chrome.runtime.sendMessage({ type: 'GET_STATUS' });
            this.connected = !!(result && result.connected);
        } catch (error) {
            console.error('Error checking connection status:', error);
        }
        this.updateUI();
    }

    async connect() {
        try {
            const result = await chrome.runtime.sendMessage({ type: 'CONNECT' });
            if (result && result.success) {
                this.connected = true;
                this.sessionId = result.sessionId;
                this.addActivity('Connected to Scathat', 'connect');
                await this.saveStats();
            } else {
                this.showError('Connection failed');
            }
        } catch (error) {
            console.error('Connection error:', error);
            this.showError('Connection error: ' + error.message);
        }
        this.updateUI();
    }

    async disconnect() {
        try {
            await chrome.runtime.sendMessage({ type: 'DISCONNECT' });
            this.connected = false;
            this.sessionId = null;
            this.addActivity('Disconnected from Scathat', 'disconnect');
        } catch (error) {
            console.error('Disconnect error:', error);
        }
        this.updateUI();
    }

    // Wallet connection methods
    async checkWalletStatus() {
        try {
            // Send message to background script to check wallet status
            const response = await chrome.runtime.sendMessage({ type: 'GET_WALLET_STATUS' });
            this.walletDetected = response?.detected || false;
            this.walletConnected = response?.connected || false;
            this.walletAccounts = response?.accounts || [];
        } catch (error) {
            console.log('No wallet detected or content script not ready:', error.message);
            this.walletDetected = false;
            this.walletConnected = false;
            this.walletAccounts = [];
        }
    }

    async connectWallet() {
        try {
            const response = await chrome.runtime.sendMessage({ type: 'CONNECT_WALLET' });
            if (response.success) {
                this.walletConnected = true;
                this.addActivity('Wallet connected successfully', 'connect');
                
                // After connecting, try to sign a message for authentication
                await this.signAuthenticationMessage();
            } else {
                this.showError('Wallet connection failed: ' + response.error);
            }
        } catch (error) {
            console.error('Wallet connection error:', error);
            this.showError('Wallet connection error: ' + error.message);
        }
        this.updateWalletUI();
    }

    // Sign an authentication message to prove wallet ownership
    async signAuthenticationMessage() {
        try {
            const message = `Scathat Authentication: ${Date.now()}`;
            const response = await chrome.runtime.sendMessage({ 
                type: 'SIGN_MESSAGE', 
                data: message 
            });
            
            if (response.success) {
                console.log('Authentication signature:', response.signature);
                this.addActivity('Wallet authentication successful', 'security');
                
                // Store the signature for future contract interactions
                this.walletSignature = response.signature;
                
                // Check if we can interact with the smart contract
                await this.checkContractAuthorization();
            } else {
                this.showError('Authentication failed: ' + response.error);
            }
        } catch (error) {
            console.error('Authentication error:', error);
            this.showError('Authentication error: ' + error.message);
        }
    }

    // Check if wallet is authorized to interact with the smart contract
    async checkContractAuthorization() {
        try {
            // This would be implemented to check against the smart contract
            // For now, we'll simulate the check
            const isAuthorized = true; // Simulated authorization check
            
            if (isAuthorized) {
                this.addActivity('Contract access authorized', 'contract');
                this.contractAuthorized = true;
            } else {
                this.addActivity('Contract access not authorized', 'warning');
                this.contractAuthorized = false;
            }
        } catch (error) {
            console.error('Authorization check failed:', error);
            this.contractAuthorized = false;
        }
    }

    // Interact with smart contract (example method)
    async interactWithContract() {
        try {
            if (!this.walletConnected) {
                throw new Error('Wallet not connected');
            }

            if (!this.contractAuthorized) {
                throw new Error('Not authorized to interact with contract');
            }

            // Example contract interaction data
            const transactionData = {
                from: this.walletAccounts[0],
                to: '0x8dCcDf8Be8B32492896281413B45e075B1f5EDe5', // Contract address
                value: '0x0', // No value transfer
                data: '0x12345678' // Example contract call data
            };

            const response = await chrome.runtime.sendMessage({
                type: 'INTERACT_WITH_CONTRACT',
                data: transactionData
            });

            if (response.success) {
                this.addActivity('Contract interaction successful', 'contract');
                return response.result;
            } else {
                throw new Error(response.error);
            }
        } catch (error) {
            console.error('Contract interaction failed:', error);
            this.showError('Contract interaction failed: ' + error.message);
            throw error;
        }
    }

    async disconnectWallet() {
        // For Ethereum wallets, disconnection is typically handled by the wallet itself
        // We just update our local state
        this.walletConnected = false;
        this.walletAccounts = [];
        this.addActivity('Wallet disconnected', 'disconnect');
        this.updateWalletUI();
    }

    updateWalletUI() {
        const walletStatus = document.getElementById('walletStatus');
        const walletDot = walletStatus.querySelector('.wallet-dot');
        const walletText = walletStatus.querySelector('.wallet-text');
        const connectBtn = document.getElementById('connectWalletBtn');
        const disconnectBtn = document.getElementById('disconnectWalletBtn');

        if (this.walletConnected) {
            walletDot.classList.add('connected');
            walletDot.classList.remove('detected');
            walletText.textContent = this.walletAccounts.length > 0 
                ? `Connected: ${this.walletAccounts[0].slice(0, 8)}...`
                : 'Wallet Connected';
            connectBtn.style.display = 'none';
            disconnectBtn.style.display = '';
        } else if (this.walletDetected) {
            walletDot.classList.add('detected');
            walletDot.classList.remove('connected');
            walletText.textContent = 'Wallet Detected';
            connectBtn.style.display = '';
            disconnectBtn.style.display = 'none';
        } else {
            walletDot.classList.remove('connected', 'detected');
            walletText.textContent = 'No Wallet Found';
            connectBtn.style.display = 'none';
            disconnectBtn.style.display = 'none';
        }
    }

    async scanCurrentPage() {
        try {
            // Get current active tab
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            if (tab) {
                const url = tab.url || '';
                const allowed = url.startsWith('http://') || url.startsWith('https://');
                if (!allowed) {
                    this.showError('Scan error: Current page does not allow content scripts');
                    return;
                }
                // Send message to content script to scan the page
                const response = await chrome.tabs.sendMessage(tab.id, {
                    type: 'SCAN_CURRENT_PAGE'
                });

                if (response && response.success) {
                    this.addActivity(`Scanned page: ${response.results.length} contracts found`, 'scan');
                    
                    // Update stats
                    this.stats.scannedContracts += response.results.length;
                    this.updateStatsUI();
                    await this.saveStats();
                } else {
                    this.showError('Scan error: Unable to reach content script');
                }
            }
        } catch (error) {
            console.error('Scan error:', error);
            this.showError('Scan error: ' + error.message);
        }
    }

    openDashboard() {
        // Open the main Scathat dashboard
        chrome.tabs.create({
            url: chrome.runtime.getURL('../../dashboard/index.html')
        });
    }

    async updateSetting(key, value) {
        this.settings[key] = value;
        
        try {
            await chrome.storage.local.set({ settings: this.settings });
            
            // Notify background script of setting changes
            await chrome.runtime.sendMessage({
                type: 'UPDATE_SETTINGS',
                data: { [key]: value }
            });
            
            this.addActivity(`Setting updated: ${key} = ${value}`, 'settings');
        } catch (error) {
            console.error('Error updating setting:', error);
        }
    }

    async saveStats() {
        try {
            await chrome.storage.local.set({ stats: this.stats });
        } catch (error) {
            console.error('Error saving stats:', error);
        }
    }

    updateStatsUI() {
        document.getElementById('scannedContracts').textContent = String(this.stats.scannedContracts);
        document.getElementById('threatsBlocked').textContent = String(this.stats.threatsBlocked);
        document.getElementById('savedFunds').textContent = `$${this.stats.savedFunds}`;
    }

    addActivity(text, type) {
        const item = document.createElement('div');
        item.className = 'activity-item';
        const icon = type === 'error' ? '⚠️' : type === 'scan' ? '🔍' : type === 'connect' ? '🔗' : type === 'disconnect' ? '❌' : 'ℹ️';
        item.innerHTML = `<span class="activity-icon">${icon}</span><span class="activity-text">${text}</span><span class="activity-time">${new Date().toLocaleTimeString()}</span>`;
        document.getElementById('activityList').prepend(item);
    }

    showError(message) {
        this.addActivity(message, 'error');
        
        // Show temporary error notification
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: hsl(0 84% 60%);
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            z-index: 1000;
            font-size: 14px;
        `;
        errorDiv.textContent = message;
        
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 3000);
    }

    openHelp() {
        chrome.tabs.create({
            url: 'https://docs.scathat.com/extension-help'
        });
    }

    openFeedback() {
        chrome.tabs.create({
            url: 'https://github.com/scathat/extension/issues'
        });
    }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ScathatPopup();
});

