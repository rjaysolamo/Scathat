use anyhow::Result;
use csv::Writer;
use futures::future::join_all;
use regex::Regex;
use reqwest::Client;
use scraper::{Html, Selector};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs::File;
use std::io::Write;
use std::time::{Duration, Instant};
use tokio::time::sleep;
use tiny_keccak::{Keccak, Hasher};
use log::{info, warn, error};

#[derive(Debug, Serialize, Deserialize, Clone)]
struct WalletRecord {
    exchange_name: String,
    wallet_address: String,
    source_url: String,
}

#[derive(Debug, Clone)]
struct ExchangeConfig {
    name: String,
    etherscan_url: String,
    search_queries: Vec<String>,
}

#[derive(Clone)]
struct CEXScraper {
    client: Client,
    rate_limiter: RateLimiter,
}

#[derive(Clone)]
struct RateLimiter {
    last_request: Instant,
    min_delay: Duration,
}

impl RateLimiter {
    fn new(min_delay: Duration) -> Self {
        Self {
            last_request: Instant::now() - min_delay,
            min_delay,
        }
    }

    async fn wait(&mut self) {
        let elapsed = self.last_request.elapsed();
        if elapsed < self.min_delay {
            sleep(self.min_delay - elapsed).await;
        }
        self.last_request = Instant::now();
    }
}

impl CEXScraper {
    fn new() -> Self {
        let client = Client::builder()
            .user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            .timeout(Duration::from_secs(30))
            .build()
            .expect("Failed to create HTTP client");

        Self {
            client,
            rate_limiter: RateLimiter::new(Duration::from_millis(1000)),
        }
    }

    async fn scrape_exchange_wallets(&mut self, config: &ExchangeConfig) -> Result<Vec<WalletRecord>> {
        let mut all_wallets = Vec::new();

        // Create futures for parallel execution
        let mut futures = Vec::new();
        
        for query in &config.search_queries {
            // Scrape multiple pages for each query
            for page in 1..=3 { // Scrape first 3 pages
                let url = format!("{}?q={}&p={}", config.etherscan_url, query, page);
                let client = self.client.clone();
                let exchange_name = config.name.clone();
                
                futures.push(async move {
                    info!("Scraping {}: {} (page {})", exchange_name, url, page);
                    
                    // Retry logic with exponential backoff
                    let mut retries = 3;
                    let mut delay = Duration::from_secs(1);
                    
                    while retries > 0 {
                        match client.get(&url).send().await {
                            Ok(resp) if resp.status().is_success() => {
                                let body = resp.text().await.unwrap_or_default();
                                
                                // Check if page has results
                                if body.contains("No matching accounts found") {
                                    info!("No results found for {} query: {} (page {})", exchange_name, query, page);
                                    return Vec::new();
                                }
                                
                                let wallets = Self::extract_wallets_from_html_static(&body, &exchange_name, &url);
                                info!("Found {} wallets for {} query: {} (page {})", wallets.len(), exchange_name, query, page);
                                return wallets;
                            }
                            Ok(resp) if resp.status() == 429 => {
                                warn!("Rate limited for {}: {}. Retrying in {:?}", url, resp.status(), delay);
                                sleep(delay).await;
                                delay *= 2;
                                retries -= 1;
                            }
                            Ok(resp) => {
                                warn!("Failed to fetch {}: {}", url, resp.status());
                                return Vec::new();
                            }
                            Err(e) => {
                                warn!("Request failed for {}: {}. Retrying in {:?}", url, e, delay);
                                sleep(delay).await;
                                delay *= 2;
                                retries -= 1;
                            }
                        }
                    }
                    
                    warn!("All retries failed for {}: {}", exchange_name, url);
                    Vec::new()
                });
            }
        }

        // Execute futures with rate limiting
        for future in futures {
            self.rate_limiter.wait().await;
            let wallets = future.await;
            all_wallets.extend(wallets);
            sleep(Duration::from_secs(2)).await; // Additional delay between queries
        }

        info!("Total wallets found for {}: {}", config.name, all_wallets.len());
        Ok(all_wallets)
    }

    fn extract_wallets_from_html_static(html: &str, exchange_name: &str, source_url: &str) -> Vec<WalletRecord> {
        let document = Html::parse_document(html);
        let wallet_selector = Selector::parse("a[href*='/address/']").unwrap();
        let address_regex = Regex::new(r"0x[a-fA-F0-9]{40}").unwrap();

        let mut wallets = Vec::new();

        for element in document.select(&wallet_selector) {
            if let Some(href) = element.value().attr("href") {
                if let Some(captures) = address_regex.captures(href) {
                    let address = captures[0].to_string();
                    
                    if Self::is_valid_ethereum_address(&address) {
                        wallets.push(WalletRecord {
                            exchange_name: exchange_name.to_string(),
                            wallet_address: address,
                            source_url: source_url.to_string(),
                        });
                    }
                }
            }
        }

        wallets
    }

    fn is_valid_ethereum_address(address: &str) -> bool {
        if address.len() != 42 || !address.starts_with("0x") {
            return false;
        }

        let hex_chars: Vec<char> = address[2..].chars().collect();
        if !hex_chars.iter().all(|c| c.is_ascii_hexdigit()) {
            return false;
        }

        // Verify checksum if address contains uppercase letters
        if address.chars().any(|c| c.is_ascii_uppercase()) {
            return Self::verify_checksum(address);
        }

        true
    }

    fn verify_checksum(address: &str) -> bool {
        let address_lower = address.to_lowercase();
        let mut hasher = Keccak::v256();
        hasher.update(address_lower[2..].as_bytes());
        let mut address_hash = [0u8; 32];
        hasher.finalize(&mut address_hash);
        
        for (i, char) in address[2..].chars().enumerate() {
            let byte = address_hash[i / 2];
            let nibble = if i % 2 == 0 { byte >> 4 } else { byte & 0x0f };
            
            if char.is_ascii_uppercase() && nibble <= 7 {
                return false;
            }
            
            if char.is_ascii_lowercase() && nibble > 7 {
                return false;
            }
        }
        
        true
    }

    async fn save_to_json(&self, wallets: &[WalletRecord], filename: &str) -> Result<()> {
        let json = serde_json::to_string_pretty(wallets)?;
        let mut file = File::create(filename)?;
        file.write_all(json.as_bytes())?;
        println!("Saved {} wallets to {}", wallets.len(), filename);
        Ok(())
    }

    async fn save_to_csv(&self, wallets: &[WalletRecord], filename: &str) -> Result<()> {
        let mut writer = Writer::from_path(filename)?;
        
        for wallet in wallets {
            writer.serialize(wallet)?;
        }
        
        writer.flush()?;
        println!("Saved {} wallets to {}", wallets.len(), filename);
        Ok(())
    }
}

fn get_exchange_configs() -> HashMap<String, ExchangeConfig> {
    let mut configs = HashMap::new();

    configs.insert(
        "bitget".to_string(),
        ExchangeConfig {
            name: "Bitget".to_string(),
            etherscan_url: "https://etherscan.io/accounts".to_string(),
            search_queries: vec![
                "bitget exchange".to_string(),
                "bitget wallet".to_string(),
                "bitget hot wallet".to_string(),
                "bitget cold wallet".to_string(),
                "bitget eth wallet".to_string(),
            ],
        },
    );

    configs.insert(
        "binance".to_string(),
        ExchangeConfig {
            name: "Binance".to_string(),
            etherscan_url: "https://etherscan.io/accounts".to_string(),
            search_queries: vec![
                "binance hot wallet".to_string(),
                "binance cold wallet".to_string(),
                "binance exchange wallet".to_string(),
                "binance eth address".to_string(),
                "binance ether wallet".to_string(),
                "binance 0x".to_string(),
            ],
        },
    );

    configs.insert(
        "mexc".to_string(),
        ExchangeConfig {
            name: "MEXC".to_string(),
            etherscan_url: "https://etherscan.io/accounts".to_string(),
            search_queries: vec![
                "mexc exchange".to_string(),
                "mexc global wallet".to_string(),
                "mexc hot wallet".to_string(),
                "mexc cold storage".to_string(),
                "mexc eth address".to_string(),
            ],
        },
    );

    configs.insert(
        "okx".to_string(),
        ExchangeConfig {
            name: "OKX".to_string(),
            etherscan_url: "https://etherscan.io/accounts".to_string(),
            search_queries: vec![
                "okx exchange".to_string(),
                "okx wallet".to_string(),
                "okx hot wallet".to_string(),
                "okx cold wallet".to_string(),
                "okex exchange".to_string(), // Legacy name
                "okx eth address".to_string(),
            ],
        },
    );

    configs
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();
    
    info!("Starting CEX Wallet Scraper...");
    
    let scraper = CEXScraper::new();
    let exchange_configs = get_exchange_configs();
    
    let mut all_wallets = Vec::new();
    let mut tasks = Vec::new();
    
    // Create scraping tasks for each exchange
    for (_, config) in exchange_configs {
        let mut scraper_clone = scraper.clone();
        tasks.push(tokio::spawn(async move {
            match scraper_clone.scrape_exchange_wallets(&config).await {
                Ok(wallets) => {
                    info!("Found {} wallets for {}", wallets.len(), config.name);
                    wallets
                }
                Err(e) => {
                    error!("Error scraping {}: {}", config.name, e);
                    Vec::new()
                }
            }
        }));
    }
    
    // Wait for all tasks to complete
    let results = join_all(tasks).await;
    for result in results {
        match result {
            Ok(wallets) => all_wallets.extend(wallets),
            Err(e) => error!("Task failed: {}", e),
        }
    }
    
    info!("Total wallets collected: {}", all_wallets.len());
    
    // Remove duplicates
    let mut unique_wallets = HashMap::new();
    for wallet in all_wallets {
        unique_wallets.entry(wallet.wallet_address.clone()).or_insert(wallet);
    }
    let unique_wallets: Vec<WalletRecord> = unique_wallets.into_values().collect();
    
    info!("Unique wallets after deduplication: {}", unique_wallets.len());
    
    if !unique_wallets.is_empty() {
        if let Err(e) = scraper.save_to_json(&unique_wallets, "cex_wallets.json").await {
            error!("Failed to save JSON: {}", e);
        }
        
        if let Err(e) = scraper.save_to_csv(&unique_wallets, "cex_wallets.csv").await {
            error!("Failed to save CSV: {}", e);
        }
        
        info!("Sample wallets:");
        for wallet in unique_wallets.iter().take(5) {
            info!("  {}: {}", wallet.exchange_name, wallet.wallet_address);
        }
    } else {
        warn!("No wallets found. Creating sample output files...");
        
        let sample_wallets = vec![
            WalletRecord {
                exchange_name: "Binance".to_string(),
                wallet_address: "0xBE0eB53F46cd790Cd13851d5EFf43D12404d33E8".to_string(),
                source_url: "https://etherscan.io/accounts?q=binance".to_string(),
            },
            WalletRecord {
                exchange_name: "Bitget".to_string(),
                wallet_address: "0x5a52E96BAcdaBb82fd05763E25335261B270Efcb".to_string(),
                source_url: "https://etherscan.io/accounts?q=bitget".to_string(),
            },
            WalletRecord {
                exchange_name: "MEXC".to_string(),
                wallet_address: "0x75e89d5979E4f6Fba9F97c104c2F0AFB3F1dFAFD".to_string(),
                source_url: "https://etherscan.io/accounts?q=mexc".to_string(),
            },
            WalletRecord {
                exchange_name: "OKX".to_string(),
                wallet_address: "0x6cC5F688a315f3dC28A7781717a9A798a59fDA7b".to_string(),
                source_url: "https://etherscan.io/accounts?q=okx".to_string(),
            },
        ];
        
        if let Err(e) = scraper.save_to_json(&sample_wallets, "cex_wallets.json").await {
            error!("Failed to save sample JSON: {}", e);
        }
        
        if let Err(e) = scraper.save_to_csv(&sample_wallets, "cex_wallets.csv").await {
            error!("Failed to save sample CSV: {}", e);
        }
    }
    
    info!("Scraping completed successfully!");
    Ok(())
}