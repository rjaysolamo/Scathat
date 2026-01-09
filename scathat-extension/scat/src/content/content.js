// Content script for Scathat extension - runs in web pages
class ScathatContent {
  constructor() {
    this.initialized = false;
    this.contractElements = [];
    this.liveModals = new Set();
    this.badgedLinks = new WeakSet();
    this.urlRegex = /(https?:\/\/[^\s<>'")\]])|(\b[a-z0-9-]+\.eth\b)|(0x[a-fA-F0-9]{40})/gi;
    this.chatSelectors = [
      'div[data-testid="message-container"]',
      'div[role="row"]',
      'div[aria-label="Message"]',
      'div[role="textbox"]',
      'main',
      'article',
      'body'
    ];
    this.walletDetected = false;
    this.walletConnected = false;
    this.init();
  }

  init() {
    this.setupMutationObserver();
    this.scanChatMessages();
    this.setupMessageListeners();
    this.setupLifecycleGuards();
    this.detectEthereumWallet();
    this.initialized = true;
    console.log('Scathat content script initialized');
  }

  setupLifecycleGuards() {
    const cleanup = () => {
      try {
        this.liveModals.forEach((m) => {
          if (m && m.remove) m.remove();
        });
        this.liveModals.clear();
      } catch {}
    };
    window.addEventListener('pagehide', cleanup);
    window.addEventListener('beforeunload', cleanup);
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') cleanup();
    });
  }

  // Ethereum wallet detection and connection
  detectEthereumWallet() {
    // Check for MetaMask or other Ethereum providers
    if (typeof window.ethereum !== 'undefined') {
      this.walletDetected = true;
      console.log('Ethereum wallet detected:', window.ethereum);
      
      // Listen for wallet connection requests from background script
      chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.type === 'CONNECT_WALLET') {
          this.connectWallet().then(result => {
            sendResponse({ success: true, connected: result });
          }).catch(error => {
            sendResponse({ success: false, error: error.message });
          });
          return true; // Keep message channel open for async response
        }
        
        if (message.type === 'GET_WALLET_STATUS') {
          sendResponse({ 
            detected: this.walletDetected, 
            connected: this.walletConnected,
            accounts: window.ethereum?.selectedAddress ? [window.ethereum.selectedAddress] : []
          });
        }

        if (message.type === 'SIGN_MESSAGE') {
          this.signMessage(message.data).then(signature => {
            sendResponse({ success: true, signature });
          }).catch(error => {
            sendResponse({ success: false, error: error.message });
          });
          return true;
        }

        if (message.type === 'INTERACT_WITH_CONTRACT') {
          this.interactWithContract(message.data).then(result => {
            sendResponse({ success: true, result });
          }).catch(error => {
            sendResponse({ success: false, error: error.message });
          });
          return true;
        }
      });
    } else {
      console.log('No Ethereum wallet detected');
    }
  }

  async connectWallet() {
    if (!this.walletDetected) {
      throw new Error('No Ethereum wallet detected');
    }

    try {
      // Request account access
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts'
      });
      
      if (accounts && accounts.length > 0) {
        this.walletConnected = true;
        console.log('Wallet connected successfully:', accounts[0]);
        return true;
      } else {
        throw new Error('User denied account access');
      }
    } catch (error) {
      console.error('Wallet connection failed:', error);
      this.walletConnected = false;
      throw error;
    }
  }

  // Sign a message with the connected wallet
  async signMessage(message) {
    if (!this.walletConnected) {
      throw new Error('Wallet not connected');
    }

    try {
      // Use personal_sign for better wallet compatibility
      const signature = await window.ethereum.request({
        method: 'personal_sign',
        params: [message, await this.getCurrentAccount()]
      });
      
      console.log('Message signed successfully:', signature);
      return signature;
    } catch (error) {
      console.error('Message signing failed:', error);
      throw new Error('User denied message signature');
    }
  }

  // Interact with smart contract (requires user signature)
  async interactWithContract(transactionData) {
    if (!this.walletConnected) {
      throw new Error('Wallet not connected');
    }

    try {
      // Send transaction to contract (this will trigger wallet signature prompt)
      const txHash = await window.ethereum.request({
        method: 'eth_sendTransaction',
        params: [transactionData]
      });
      
      console.log('Contract interaction successful:', txHash);
      return txHash;
    } catch (error) {
      console.error('Contract interaction failed:', error);
      throw new Error('User denied transaction signature');
    }
  }

  // Get current account address
  async getCurrentAccount() {
    const accounts = await window.ethereum.request({
      method: 'eth_accounts'
    });
    return accounts[0];
  }

  // ... (script content truncated for brevity; full content mirrors source in workspace)
}

// Instantiate when loaded
(() => {
  try {
    new ScathatContent();
  } catch (e) {
    console.warn('ScathatContent failed to initialize:', e);
  }
})();

