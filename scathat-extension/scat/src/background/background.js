// Background service worker for Scathat extension
import { scathatAPI } from '../api-client.js';

class ScathatBackground {
  constructor() {
    this.connected = false;
    this.sessionId = null;
    this.apiClient = null;
    this.init();
  }

  async init() {
    this.setupListeners();
    await this.initializeStorage();
    await this.initializeAPIClient();
    console.log('Scathat background service initialized');
  }

  setupListeners() {
    chrome.runtime.onInstalled.addListener((details) => {
      if (details.reason === 'install') this.onExtensionInstall();
      if (details.reason === 'update') this.onExtensionUpdate();
    });

    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      switch (message.type) {
        case 'CONNECT':
          this.handleConnect(message.data).then((res) => sendResponse(res));
          return true;
        case 'DISCONNECT':
          this.handleDisconnect().then((res) => sendResponse(res));
          return true;
        case 'UPDATE_SETTINGS':
          this.updateSettings(message.data).then((res) => sendResponse(res));
          return true;
        case 'SCAN_CONTRACT':
          this.scanContract(message.data).then((res) => sendResponse(res));
          return true;
        case 'GET_STATUS':
          sendResponse({ connected: this.connected, sessionId: this.sessionId });
          return true;
        case 'CONNECT_WALLET':
          this.handleWalletConnect(sender.tab?.id).then((res) => sendResponse(res));
          return true;
        case 'GET_WALLET_STATUS':
          this.handleWalletStatus(sender.tab?.id).then((res) => sendResponse(res));
          return true;
        case 'SIGN_MESSAGE':
          this.handleSignMessage(sender.tab?.id, message.data).then((res) => sendResponse(res));
          return true;
        case 'INTERACT_WITH_CONTRACT':
          this.handleContractInteraction(sender.tab?.id, message.data).then((res) => sendResponse(res));
          return true;
      }
    });
  }

  async initializeStorage() {
    try {
      const result = await chrome.storage.local.get(['settings', 'stats']);
      if (!result.settings) {
        await chrome.storage.local.set({
          settings: {
            autoScan: true,
            notifications: true,
            highlightContracts: true,
            backendURL: 'http://localhost:8000'
          },
          stats: {
            scannedContracts: 0,
            threatsBlocked: 0,
            savedFunds: 0
          }
        });
      }
    } catch (e) {
      console.error('initializeStorage error:', e);
    }
  }

  async initializeAPIClient() {
    try {
      this.apiClient = scathatAPI({ baseURL: 'http://localhost:8000' });
    } catch (e) {
      console.error('initializeAPIClient error:', e);
    }
  }

  onExtensionInstall() {
    console.log('Scathat extension installed');
    this.showWelcomeNotification();
  }

  onExtensionUpdate() {
    console.log('Scathat extension updated');
  }

  showWelcomeNotification() {
    chrome.notifications.create('welcome', {
      type: 'basic',
      iconUrl: chrome.runtime.getURL('assets/icons/logo1.jpg'),
      title: 'Scathat Installed',
      message: 'Your AI-powered smart contract security shield is now active!',
      priority: 2
    });
  }

  async handleConnect(data) {
    try {
      this.connected = true;
      this.sessionId = crypto.randomUUID();
      return { success: true, sessionId: this.sessionId };
    } catch (e) {
      return { success: false, error: e.message };
    }
  }

  async handleDisconnect() {
    try {
      this.connected = false;
      this.sessionId = null;
      return { success: true };
    } catch (e) {
      return { success: false, error: e.message };
    }
  }

  async updateSettings(partial) {
    try {
      const result = await chrome.storage.local.get(['settings']);
      const settings = { ...(result.settings || {}), ...(partial || {}) };
      await chrome.storage.local.set({ settings });
      return { success: true };
    } catch (e) {
      return { success: false, error: e.message };
    }
  }

  async scanContract({ address }) {
    try {
      // Simulate scan call
      const res = await this.apiClient.analyze(address);
      return { success: true, result: res };
    } catch (e) {
      return { success: false, error: e.message };
    }
  }

  // Wallet connection handlers
  async handleWalletConnect(tabId) {
    try {
      // If no tabId provided, try to use the active tab first
      let targetTabId = tabId;
      
      if (!targetTabId) {
        // Try to get the active tab first
        try {
          const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
          if (activeTab && activeTab.id) {
            targetTabId = activeTab.id;
          }
        } catch (error) {
          console.log('Could not get active tab:', error.message);
        }
        
        // If no active tab available, use a different approach
        if (!targetTabId) {
          // For Manifest V3, we need to use a different approach than about:blank
          // We'll use the content script to handle wallet detection on regular pages
          throw new Error('Please navigate to a regular website to connect your wallet');
        }
      }
      
      try {
        // Use content script messaging instead of direct scripting
        // This works better with Manifest V3 security restrictions
        const response = await chrome.tabs.sendMessage(targetTabId, {
          type: 'CONNECT_WALLET'
        });
        
        return response;
        
      } catch (error) {
        console.error('Wallet connection via content script failed:', error);
        throw new Error('Failed to connect wallet: ' + error.message);
      }
      
    } catch (error) {
      console.error('Wallet connection error:', error);
      return { 
        success: false, 
        error: error.message || 'Failed to connect wallet. Please make sure you have an Ethereum wallet installed.',
        detected: false,
        connected: false
      };
    }
  }

  async handleWalletStatus(tabId) {
    try {
      // Try to get status via content script if we have an active tab
      if (tabId) {
        try {
          const response = await chrome.tabs.sendMessage(tabId, { type: 'GET_WALLET_STATUS' });
          if (response) return response;
        } catch (contentScriptError) {
          console.log('Content script wallet status check failed:', contentScriptError.message);
        }
      }
      
      // Background script cannot access window.ethereum directly
      // Create a temporary tab to check wallet status
      const tempTab = await chrome.tabs.create({ 
        url: 'about:blank',
        active: false 
      });
      
      // Wait for tab to load
      await new Promise(resolve => {
        chrome.tabs.onUpdated.addListener(function listener(tabId, info) {
          if (tabId === tempTab.id && info.status === 'complete') {
            chrome.tabs.onUpdated.removeListener(listener);
            resolve();
          }
        });
      });
      
      try {
        // Execute wallet status check script
        const results = await chrome.scripting.executeScript({
          target: { tabId: tempTab.id },
          func: () => {
            try {
              if (typeof window !== 'undefined' && window.ethereum) {
                return window.ethereum.request({ method: 'eth_accounts' })
                  .then(accounts => ({
                    detected: true,
                    connected: accounts.length > 0,
                    accounts: accounts
                  }))
                  .catch(error => ({
                    detected: true,
                    connected: false,
                    accounts: [],
                    error: error.message
                  }));
              } else {
                return {
                  detected: false,
                  connected: false,
                  accounts: []
                };
              }
            } catch (error) {
              return {
                detected: false,
                connected: false,
                accounts: [],
                error: error.message
              };
            }
          }
        });
        
        // Close the temporary tab
        chrome.tabs.remove(tempTab.id);
        
        if (results && results[0] && results[0].result) {
          return results[0].result;
        }
        
        return { detected: false, connected: false, accounts: [] };
        
      } catch (error) {
        // Close the temporary tab on error
        chrome.tabs.remove(tempTab.id);
        return { detected: false, connected: false, accounts: [], error: error.message };
      }
      
    } catch (error) {
      console.log('Wallet status check failed:', error.message);
      return { detected: false, connected: false, accounts: [] };
    }
  }

  // Handle message signing requests
  async handleSignMessage(tabId, message) {
    try {
      if (!tabId) {
        return { success: false, error: 'No active tab found' };
      }
      
      // Send message to content script to sign the message
      const response = await chrome.tabs.sendMessage(tabId, { 
        type: 'SIGN_MESSAGE', 
        data: message 
      });
      
      return response;
    } catch (error) {
      console.error('Message signing failed:', error);
      return { 
        success: false, 
        error: error.message || 'Failed to sign message. Make sure wallet is connected.' 
      };
    }
  }

  // Handle contract interaction requests
  async handleContractInteraction(tabId, transactionData) {
    try {
      if (!tabId) {
        return { success: false, error: 'No active tab found' };
      }
      
      // Send message to content script to interact with contract
      const response = await chrome.tabs.sendMessage(tabId, { 
        type: 'INTERACT_WITH_CONTRACT', 
        data: transactionData 
      });
      
      return response;
    } catch (error) {
      console.error('Contract interaction failed:', error);
      return { 
        success: false, 
        error: error.message || 'Failed to interact with contract. Make sure wallet is connected.' 
      };
    }
  }
}

export default new ScathatBackground();

