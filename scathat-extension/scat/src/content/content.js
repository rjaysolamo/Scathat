// Content Script - Wallet Bridge
class WalletBridge {
  constructor() {
    this.initialized = false;
    this.walletDetected = false;
    this.walletConnected = false;
    this.currentAccount = null;
    this.currentChainId = null;
    this.walletEvents = new Map();
    
    this.setupMessageListeners();
    this.detectWallet();
    this.setupWalletEventListeners();
    
    this.initialized = true;
    console.log('WalletBridge initialized');
    
    // Notify background that content script is ready
    chrome.runtime.sendMessage({ 
      type: 'CONTENT_SCRIPT_READY',
      tabId: this.getCurrentTabId()
    });
  }
  
  getCurrentTabId() {
    // Get tab ID from URL parameters or other means
    const match = window.location.href.match(/tabId=(\d+)/);
    return match ? parseInt(match[1]) : null;
  }

  setupMessageListeners() {
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      switch (message.type) {
        case 'PING':
          sendResponse({ ready: true, initialized: this.initialized });
          return true;
          
        case 'DETECT_WALLET':
          this.detectWallet().then(result => sendResponse(result));
          return true;
          
        case 'CONNECT_WALLET':
          this.connectWallet().then(result => sendResponse(result));
          return true;
          
        case 'GET_ACCOUNTS':
          this.getAccounts().then(result => sendResponse(result));
          return true;
          
        case 'GET_CHAIN_ID':
          this.getChainId().then(result => sendResponse(result));
          return true;
          
        case 'SWITCH_TO_BASE_SEPOLIA':
          this.switchToBaseSepolia().then(result => sendResponse(result));
          return true;
          
        case 'SIGN_MESSAGE':
          this.signMessage(message.data).then(result => sendResponse(result));
          return true;
          
        case 'SEND_TRANSACTION':
          this.sendTransaction(message.data).then(result => sendResponse(result));
          return true;
      }
    });
  }

  async detectWallet() {
    try {
      // Check if we're on a browser internal page
      if (window.location.protocol === 'chrome:' || window.location.protocol === 'about:') {
        return {
          success: false,
          error: 'Cannot detect wallet on browser internal pages',
          detected: false,
          wallets: {}
        };
      }
      
      const wallets = this.detectMultipleWallets();
      this.walletDetected = Object.keys(wallets).length > 0;
      
      return {
        success: true,
        wallets,
        detected: this.walletDetected
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        detected: false,
        wallets: {}
      };
    }
  }

  detectMultipleWallets() {
    const detectedWallets = {};
    
    // Check for standard Ethereum providers
    if (window.ethereum) {
      detectedWallets.ethereum = {
        isMetaMask: window.ethereum.isMetaMask,
        isRabby: window.ethereum.isRabby,
        isOKExWallet: window.ethereum.isOKExWallet,
        isTrust: window.ethereum.isTrust,
        isCoinbaseWallet: window.ethereum.isCoinbaseWallet,
        providers: window.ethereum.providers || []
      };
    }
    
    // Check for individual wallet flags
    if (window.ethereum?.isMetaMask) detectedWallets.metamask = true;
    if (window.ethereum?.isRabby) detectedWallets.rabby = true;
    if (window.ethereum?.isOKExWallet) detectedWallets.okx = true;
    if (window.ethereum?.isTrust) detectedWallets.trust = true;
    if (window.ethereum?.isCoinbaseWallet) detectedWallets.coinbase = true;
    
    // Check for Phantom
    if (window.phantom?.ethereum) detectedWallets.phantom = true;
    
    return detectedWallets;
  }

  async connectWallet() {
    try {
      // Security: Validate we're on a regular website
      if (window.location.protocol === 'chrome:' || window.location.protocol === 'about:') {
        throw new Error('Cannot connect wallet on browser internal pages');
      }

      if (!this.walletDetected) {
        throw new Error('No Ethereum wallet detected');
      }

      if (!window.ethereum || typeof window.ethereum.request !== 'function') {
        throw new Error('Ethereum provider not ready');
      }

      // Security: Only allow specific methods
      const allowedMethods = ['eth_requestAccounts', 'eth_accounts', 'eth_chainId'];
      
      // Validate method is allowed (security measure)
      const method = 'eth_requestAccounts';
      if (!allowedMethods.includes(method)) {
        throw new Error(`Method ${method} not allowed`);
      }
      
      // Request account access
      const accounts = await window.ethereum.request({
        method: method
      });

      if (accounts && accounts.length > 0) {
        this.walletConnected = true;
        this.currentAccount = accounts[0];
        
        // Get current chain ID
        const chainId = await window.ethereum.request({
          method: 'eth_chainId'
        });
        this.currentChainId = chainId;

        // FORCE switch to Base Sepolia - don't continue if not on correct network
        if (chainId !== '0x14a34') {
           try {
             // Directly call the Ethereum provider to switch networks
             await window.ethereum.request({
               method: 'wallet_switchEthereumChain',
               params: [{ chainId: '0x14a34' }]
             });
             
             // Update chain ID after successful switch
             this.currentChainId = '0x14a34';
             // Get fresh accounts after network switch
             const freshAccounts = await window.ethereum.request({
               method: 'eth_accounts'
             });
             if (freshAccounts && freshAccounts.length > 0) {
               this.currentAccount = freshAccounts[0];
             }
             
           } catch (switchError) {
             console.error('Failed to switch to Base Sepolia:', switchError);
             
             // If chain is not added to wallet, add it
             if (switchError.code === 4902) {
               try {
                 await window.ethereum.request({
                   method: 'wallet_addEthereumChain',
                   params: [{
                     chainId: '0x14a34',
                     chainName: 'Base Sepolia',
                     nativeCurrency: {
                       name: 'Ether',
                       symbol: 'ETH',
                       decimals: 18
                     },
                     rpcUrls: ['https://sepolia.base.org'],
                     blockExplorerUrls: ['https://sepolia.basescan.org']
                   }]
                 });
                 
                 // After adding, try switching again
                 await window.ethereum.request({
                   method: 'wallet_switchEthereumChain',
                   params: [{ chainId: '0x14a34' }]
                 });
                 
                 // Update chain ID after successful switch
                 this.currentChainId = '0x14a34';
                 
               } catch (addError) {
                 console.error('Failed to add Base Sepolia network:', addError);
                 throw new Error(`Failed to add Base Sepolia network: ${addError.message}`);
               }
             } else {
               // Re-throw to prevent connection on wrong network
               throw new Error(`Wallet connection aborted: Must be on Base Sepolia network. Failed to switch: ${switchError.message}`);
             }
           }
         }

        return {
          success: true,
          account: this.currentAccount,
          chainId: this.currentChainId,
          walletConnected: true
        };
      } else {
        throw new Error('No accounts returned from wallet');
      }
    } catch (error) {
      console.error('Wallet connection failed:', error);
      
      // Handle specific error codes
      if (error.code === 4001) {
        throw new Error('Connection rejected by user');
      } else if (error.code === -32002) {
        throw new Error('Wallet connection already pending');
      }
      
      throw error;
    }
  }

  async getAccounts() {
    try {
      if (!this.walletConnected) {
        throw new Error('Wallet not connected');
      }

      const accounts = await window.ethereum.request({
        method: 'eth_accounts'
      });

      return {
        success: true,
        accounts: accounts || []
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  async getChainId() {
    try {
      if (!this.walletConnected) {
        throw new Error('Wallet not connected');
      }

      const chainId = await window.ethereum.request({
        method: 'eth_chainId'
      });

      return {
        success: true,
        chainId: chainId
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  async signMessage({ message, account }) {
    try {
      // Security: Validate we're on a regular website
      if (window.location.protocol === 'chrome:' || window.location.protocol === 'about:') {
        throw new Error('Cannot sign messages on browser internal pages');
      }

      if (!this.walletConnected) {
        throw new Error('Wallet not connected');
      }

      // Security: Validate message parameters
      if (typeof message !== 'string' || message.length > 10000) {
        throw new Error('Invalid message format');
      }

      const result = await window.ethereum.request({
        method: 'personal_sign',
        params: [message, account]
      });

      return {
        success: true,
        signature: result
      };
    } catch (error) {
      if (error.code === 4001) {
        throw new Error('Signature rejected by user');
      }
      throw error;
    }
  }

  async sendTransaction(transaction) {
    try {
      // Security: Validate we're on a regular website
      if (window.location.protocol === 'chrome:' || window.location.protocol === 'about:') {
        throw new Error('Cannot send transactions on browser internal pages');
      }

      if (!this.walletConnected) {
        throw new Error('Wallet not connected');
      }

      // Security: Validate transaction parameters
      if (!transaction || typeof transaction !== 'object') {
        throw new Error('Invalid transaction object');
      }

      // Security: Basic transaction validation
      const allowedKeys = ['from', 'to', 'value', 'data', 'gas', 'gasPrice', 'chainId'];
      const transactionKeys = Object.keys(transaction);
      if (transactionKeys.some(key => !allowedKeys.includes(key))) {
        throw new Error('Transaction contains invalid parameters');
      }

      // Security: Validate Ethereum addresses

      // Contract detection: Check if transaction is interacting with a contract
      if (transaction.to && transaction.data && transaction.data !== '0x') {
        // This is a contract interaction
        const contractInfo = await this.detectContractInteraction(transaction.to, transaction.data);
        if (contractInfo) {
          // Notify background about contract interaction
          this.notifyBackground('CONTRACT_INTERACTION', {
            to: transaction.to,
            data: transaction.data,
            contractInfo: contractInfo
          });
          
          // Trigger AI analysis for dApp contract labeling
          this.analyzeDAppContract(transaction.to, transaction.data);
        }
      }
      if (transaction.from && !this.isValidEthereumAddress(transaction.from)) {
        throw new Error('Invalid from address');
      }
      
      if (transaction.to && !this.isValidEthereumAddress(transaction.to)) {
        throw new Error('Invalid to address');
      }

      // Security: Validate value format
      if (transaction.value && !/^0x[a-fA-F0-9]+$/.test(transaction.value)) {
        throw new Error('Invalid value format');
      }

      // Security: Validate gas limits
      if (transaction.gas) {
        const gasLimit = parseInt(transaction.gas, 16);
        if (gasLimit > 30000000) { // 30 million gas limit
          throw new Error('Gas limit too high');
        }
      }

      const result = await window.ethereum.request({
        method: 'eth_sendTransaction',
        params: [transaction]
      });

      return {
        success: true,
        transactionHash: result
      };
    } catch (error) {
      if (error.code === 4001) {
        throw new Error('Transaction rejected by user');
      }
      throw error;
    }
  }

  setupWalletEventListeners() {
    if (window.ethereum) {
      // Security: Only setup listeners on regular websites
      if (window.location.protocol === 'chrome:' || window.location.protocol === 'about:') {
        console.warn('Skipping wallet event listeners on internal page');
        return;
      }

      // Handle account changes
      window.ethereum.on('accountsChanged', (accounts) => {
        this.handleAccountsChanged(accounts);
      });

      // Handle chain changes
      window.ethereum.on('chainChanged', (chainId) => {
        this.handleChainChanged(chainId);
      });

      // Handle disconnect
      window.ethereum.on('disconnect', (error) => {
        this.handleDisconnect(error);
      });
      
      // Handle connection events
      window.ethereum.on('connect', (connectionInfo) => {
        this.handleConnect(connectionInfo);
      });
    }
  }
  
  handleConnect(connectionInfo) {
    this.walletConnected = true;
    this.notifyBackground('CONNECTED', { connectionInfo });
  }

  handleAccountsChanged(accounts) {
    if (accounts.length === 0) {
      // Wallet disconnected
      this.walletConnected = false;
      this.currentAccount = null;
      this.notifyBackground('ACCOUNTS_CHANGED', { accounts: [] });
    } else {
      // Account changed
      this.currentAccount = accounts[0];
      this.notifyBackground('ACCOUNTS_CHANGED', { accounts });
    }
  }

  handleChainChanged(chainId) {
    this.currentChainId = chainId;
    this.notifyBackground('CHAIN_CHANGED', { chainId });
  }

  handleDisconnect(error) {
    this.walletConnected = false;
    this.currentAccount = null;
    this.currentChainId = null;
    this.notifyBackground('DISCONNECTED', { error: error?.message });
  }

  notifyBackground(event, data) {
    // Security: Validate event types before sending
    const allowedEvents = ['CONNECTED', 'DISCONNECTED', 'ACCOUNTS_CHANGED', 'CHAIN_CHANGED'];
    
    if (!allowedEvents.includes(event)) {
      console.warn('Attempted to send unauthorized event:', event);
      return;
    }
    
    // Security: Sanitize data before sending
    const sanitizedData = this.sanitizeWalletData(data);
    
    chrome.runtime.sendMessage({
      type: 'WALLET_EVENT',
      event,
      data: sanitizedData
    });
  }
  
  sanitizeWalletData(data) {
    // Security: Prevent sending sensitive information
    const sanitized = { ...data };
    
    // Remove any private keys or sensitive data
    if (sanitized.privateKey) delete sanitized.privateKey;
    if (sanitized.seedPhrase) delete sanitized.seedPhrase;
    if (sanitized.mnemonic) delete sanitized.mnemonic;
    
    // Truncate large data
    if (sanitized.message && sanitized.message.length > 1000) {
      sanitized.message = sanitized.message.substring(0, 1000) + '...';
    }
    
    return sanitized;
  }
  
  // Security: Validate Ethereum addresses
  isValidEthereumAddress(address) {
    return /^0x[a-fA-F0-9]{40}$/.test(address);
  }
  
  // Security: Validate chain IDs
  isValidChainId(chainId) {
    const validChainIds = new Set(['0x1', '0x5', '0xaa36a7', '0x89', '0x13881', '0x38', '0x61', '0x14a34']);
    return validChainIds.has(chainId);
  }
  
  // Switch to Base Sepolia network
  async switchToBaseSepolia() {
    try {
      if (!this.walletConnected) {
        throw new Error('Wallet not connected');
      }

      const baseSepoliaChainId = '0x14a34';
      
      // Check if already on Base Sepolia
      const currentChainId = await window.ethereum.request({
        method: 'eth_chainId'
      });
      
      if (currentChainId === baseSepoliaChainId) {
        // Already on Base Sepolia, update internal state
        this.currentChainId = baseSepoliaChainId;
        return { success: true, alreadyOnNetwork: true };
      }

      // Request network switch
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: baseSepoliaChainId }]
      });

      // Update internal state to reflect the new network
      this.currentChainId = baseSepoliaChainId;
      
      // Get fresh accounts after network switch
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts'
      });
      
      if (accounts && accounts.length > 0) {
        this.currentAccount = accounts[0];
      }

      return { success: true };
    } catch (error) {
      console.error('Failed to switch to Base Sepolia:', error);
      
      // If chain is not added to wallet, add it and try again
      if (error.code === 4902) {
        const addResult = await this.addBaseSepoliaNetwork();
        if (addResult.success) {
          // Network added, now switch to it
          return await this.switchToBaseSepolia();
        }
        throw new Error('Failed to add Base Sepolia network');
      }
      
      throw error;
    }
  }

  // Contract detection methods
  async detectContractInteraction(contractAddress, transactionData) {
    try {
      if (!this.walletConnected) {
        return null;
      }

      // Basic contract detection - check if address is a contract
      const isContract = await this.isContractAddress(contractAddress);
      if (!isContract) {
        return null;
      }

      // Analyze transaction data to detect contract interactions
      const contractInfo = await this.analyzeContractInteraction(contractAddress, transactionData);
      
      return {
        contractAddress,
        isContract: true,
        interactionType: this.detectInteractionType(transactionData),
        ...contractInfo
      };
    } catch (error) {
      console.warn('Contract detection failed:', error);
      return null;
    }
  }

  async isContractAddress(address) {
    try {
      if (!window.ethereum) return false;
      
      // Check if address has code (indicating it's a contract)
      const code = await window.ethereum.request({
        method: 'eth_getCode',
        params: [address, 'latest']
      });
      
      return code !== '0x' && code !== '0x0';
    } catch (error) {
      console.warn('Contract address check failed:', error);
      return false;
    }
  }

  detectInteractionType(transactionData) {
    if (!transactionData || transactionData === '0x') return 'transfer';
    
    // Simple function signature detection
    const functionSignature = transactionData.substring(0, 10);
    
    // Common function signatures
    const signatures = {
      '0xa9059cbb': 'transfer',
      '0x23b872dd': 'transferFrom',
      '0x095ea7b3': 'approve',
      '0x70a08231': 'balanceOf',
      '0x18160ddd': 'totalSupply',
      '0x313ce567': 'decimals'
    };
    
    return signatures[functionSignature] || 'unknown_contract_call';
  }

  async analyzeContractInteraction(contractAddress, transactionData) {
    try {
      // Get contract details using etherscan-like API or local analysis
      const contractDetails = await this.getContractDetails(contractAddress);
      
      return {
        contractName: contractDetails?.name || 'Unknown Contract',
        contractSymbol: contractDetails?.symbol || '',
        contractType: this.detectContractType(transactionData)
      };
    } catch (error) {
      console.warn('Contract analysis failed:', error);
      return {
        contractName: 'Unknown Contract',
        contractSymbol: '',
        contractType: 'unknown'
      };
    }
  }

  detectContractType(transactionData) {
    if (!transactionData || transactionData === '0x') return 'native_transfer';
    
    const functionSig = transactionData.substring(0, 10);
    
    // ERC-20 function signatures
    const erc20Sigs = ['0xa9059cbb', '0x23b872dd', '0x095ea7b3', '0x70a08231', '0x18160ddd', '0x313ce567'];
    if (erc20Sigs.includes(functionSig)) return 'erc20';
    
    // ERC-721 function signatures
    const erc721Sigs = ['0x23b872dd', '0x42842e0e', '0xb88d4fde', '0x095ea7b3', '0x70a08231', '0x6352211e'];
    if (erc721Sigs.includes(functionSig)) return 'erc721';
    
    // ERC-1155 function signatures
    const erc1155Sigs = ['0xf242432a', '0x2eb2c2d6', '0x29535249'];
    if (erc1155Sigs.includes(functionSig)) return 'erc1155';
    
    return 'custom_contract';
  }

  async getContractDetails(contractAddress) {
    try {
      // In a real implementation, this would call an API like Etherscan
      // For now, return basic info
      return {
        name: 'Detected Contract',
        symbol: 'CONTRACT',
        address: contractAddress
      };
    } catch (error) {
      console.warn('Contract details fetch failed:', error);
      return null;
    }
  }

  // Analyze dApp contracts with AI for labeling and security assessment
  async analyzeDAppContract(contractAddress, transactionData = null) {
    try {
      console.log('Analyzing dApp contract with AI:', contractAddress);
      
      // Check if this is a new dApp contract that needs analysis
      const dAppContracts = await this.getStoredDAppContracts();
      if (dAppContracts[contractAddress]) {
        // Contract already analyzed, check if analysis is recent
        const lastAnalysis = dAppContracts[contractAddress].last_analyzed;
        if (Date.now() - lastAnalysis < 24 * 60 * 60 * 1000) { // 24 hours
          console.log('Contract analysis is recent, skipping');
          return;
        }
      }

      // Request AI analysis from background script
      const analysisResult = await this.requestAIAnalysis(contractAddress, transactionData);
      
      if (analysisResult.success) {
        // Store analysis results for dApp labeling
        await this.storeDAppContractAnalysis(contractAddress, analysisResult);
        
        // Show notification based on analysis results
        this.showDAppContractNotification(contractAddress, analysisResult);
        
        // Label the contract in the dApp interface
        this.labelDAppContract(contractAddress, analysisResult);
      }
      
    } catch (error) {
      console.warn('dApp contract analysis failed:', error);
    }
  }

  // Request AI analysis from background script
  async requestAIAnalysis(contractAddress, transactionData) {
    try {
      return await chrome.runtime.sendMessage({
        type: 'ANALYZE_CONTRACT_AI',
        data: {
          contractAddress: contractAddress,
          transactionData: transactionData
        }
      });
    } catch (error) {
      console.warn('AI analysis request failed:', error);
      return { success: false, error: error.message };
    }
  }

  // Store dApp contract analysis results
  async storeDAppContractAnalysis(contractAddress, analysisResult) {
    try {
      const dAppContracts = await this.getStoredDAppContracts();
      
      dAppContracts[contractAddress] = {
        verification_status: analysisResult.verification_status,
        malicious_code_detected: analysisResult.malicious_code_detected,
        malicious_patterns: analysisResult.malicious_patterns || [],
        risk_score: analysisResult.ai_analysis?.risk_score || 0.5,
        risk_level: analysisResult.ai_analysis?.risk_level || 'medium',
        contract_type: this.detectContractTypeFromAnalysis(analysisResult),
        last_analyzed: Date.now(),
        analysis_timestamp: Date.now(),
        dapp_url: window.location.hostname
      };

      await chrome.storage.local.set({ dAppContracts: dAppContracts });
      
    } catch (error) {
      console.warn('Failed to store dApp contract analysis:', error);
    }
  }

  // Get stored dApp contracts
  async getStoredDAppContracts() {
    try {
      const result = await chrome.storage.local.get(['dAppContracts']);
      return result.dAppContracts || {};
    } catch (error) {
      console.warn('Failed to get stored dApp contracts:', error);
      return {};
    }
  }

  // Detect contract type from AI analysis
  detectContractTypeFromAnalysis(analysisResult) {
    if (analysisResult.ai_analysis?.contract_type) {
      return analysisResult.ai_analysis.contract_type;
    }
    
    // Fallback detection based on function patterns
    if (analysisResult.malicious_patterns?.includes('erc20_pattern')) return 'erc20';
    if (analysisResult.malicious_patterns?.includes('erc721_pattern')) return 'erc721';
    if (analysisResult.malicious_patterns?.includes('erc1155_pattern')) return 'erc1155';
    
    return 'unknown';
  }

  // Show notification for dApp contract analysis
  showDAppContractNotification(contractAddress, analysisResult) {
    try {
      const shortAddress = contractAddress.substring(0, 8) + '...';
      
      let message = '';
      let title = 'Contract Analysis';
      
      if (analysisResult.verification_status === 'unverified') {
        title = '⚠️ Unverified Contract';
        message = `Contract ${shortAddress} is NOT verified. Proceed with caution.`;
      } else if (analysisResult.verification_status === 'verified') {
        title = '✅ Verified Contract';
        message = `Contract ${shortAddress} is verified and safe.`;
      }
      
      if (analysisResult.malicious_code_detected) {
        title = '🚨 MALICIOUS CONTRACT';
        message = `DANGER: Contract ${shortAddress} contains malicious code!`;
      }
      
      // Create browser notification
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, {
          body: message,
          icon: chrome.runtime.getURL('assets/icons/security.png')
        });
      }
      
    } catch (error) {
      console.warn('Failed to show dApp contract notification:', error);
    }
  }

  // Label dApp contract in the interface
  labelDAppContract(contractAddress, analysisResult) {
    try {
      // Find contract address elements in the dApp
      const addressElements = this.findContractAddressElements(contractAddress);
      
      addressElements.forEach(element => {
        this.applyContractLabel(element, analysisResult);
      });
      
    } catch (error) {
      console.warn('Failed to label dApp contract:', error);
    }
  }

  // Find elements containing contract addresses
  findContractAddressElements(contractAddress) {
    const elements = [];
    const shortAddress = contractAddress.substring(2, 8); // First 6 chars after 0x
    
    // Search for elements containing the contract address
    const possibleSelectors = [
      `*[data-address*="${contractAddress}"]`,
      `*[data-contract*="${contractAddress}"]`,
      `*[href*="${contractAddress}"]`,
      `*:contains("${contractAddress}")`,
      `*:contains("${shortAddress}")`
    ];
    
    possibleSelectors.forEach(selector => {
      try {
        const matches = document.querySelectorAll(selector);
        matches.forEach(element => elements.push(element));
      } catch (error) {
        // Some selectors might not be supported
      }
    });
    
    return elements;
  }

  // Apply contract label to UI elements
  applyContractLabel(element, analysisResult) {
    const label = this.createContractLabel(analysisResult);
    
    // Add label near the contract address
    if (element.parentNode) {
      const labelElement = document.createElement('span');
      labelElement.className = 'scathat-contract-label';
      labelElement.innerHTML = label;
      labelElement.style.cssText = `
        margin-left: 8px;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        ${this.getLabelStyles(analysisResult)}
      `;
      
      element.parentNode.insertBefore(labelElement, element.nextSibling);
    }
  }

  // Create contract label HTML
  createContractLabel(analysisResult) {
    if (analysisResult.malicious_code_detected) {
      return '🚨 MALICIOUS';
    } else if (analysisResult.verification_status === 'unverified') {
      return '⚠️ UNVERIFIED';
    } else if (analysisResult.verification_status === 'verified') {
      return '✅ VERIFIED';
    } else if (analysisResult.risk_level === 'high') {
      return '⚠️ HIGH RISK';
    } else {
      return '🔍 ANALYZED';
    }
  }

  // Get CSS styles for label based on analysis
  getLabelStyles(analysisResult) {
    if (analysisResult.malicious_code_detected) {
      return 'background-color: #ff4444; color: white; border: 1px solid #cc0000;';
    } else if (analysisResult.verification_status === 'unverified') {
      return 'background-color: #ff9800; color: white; border: 1px solid #f57c00;';
    } else if (analysisResult.verification_status === 'verified') {
      return 'background-color: #4caf50; color: white; border: 1px solid #388e3c;';
    } else if (analysisResult.risk_level === 'high') {
      return 'background-color: #ff6d00; color: white; border: 1px solid #e65100;';
    } else {
      return 'background-color: #2196f3; color: white; border: 1px solid #1976d2;';
    }
  }
  
  // Add Base Sepolia network to wallet
  async addBaseSepoliaNetwork() {
    try {
      await window.ethereum.request({
        method: 'wallet_addEthereumChain',
        params: [{
          chainId: '0x14a34',
          chainName: 'Base Sepolia',
          nativeCurrency: {
            name: 'Ether',
            symbol: 'ETH',
            decimals: 18
          },
          rpcUrls: ['https://sepolia.base.org'],
          blockExplorerUrls: ['https://sepolia.basescan.org']
        }]
      });
      
      return { success: true, networkAdded: true };
    } catch (error) {
      console.error('Failed to add Base Sepolia network:', error);
      throw error;
    }
  }
}

// Initialize the wallet bridge when content script loads
window.scathatWalletBridge = new WalletBridge();