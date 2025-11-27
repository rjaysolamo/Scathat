// Background service worker for Scathat extension

// In a Chrome extension background script, the chrome global is already provided
// by the extension runtime; require() is not available and causes the error.
// Simply remove the require line and use chrome directly.

xxxxx


async function handleContractScan(contractAddress: string) {
  try {
    const response = await fetch("https://api.scathat.io/scan", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ address: contractAddress }),
    })

    if (!response.ok) throw new Error("Scan failed")
    return await response.json()
  } catch (error) {
    throw error
  }
}

// Listen for tab changes to inject content script
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete" && tab.url?.includes("etherscan")) {
    chrome.scripting.executeScript({
      target: { tabId },
      function: injectScathatButton,
    })
  }
})


function injectScathatButton() {
  const button = document.createElement("button")
  button.id = "scathat-inject-button"
  button.textContent = "Scan with Scathat"
  button.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: 10px 20px;
    background-color: #00bcd4;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
    z-index: 10000;
  `
  document.body.appendChild(button)
}
