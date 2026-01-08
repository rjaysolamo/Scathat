use anyhow::{Context, Result};
use reqwest::Client;
use scraper::{Html, Selector};
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use std::fs::{File, OpenOptions};
use std::io::{BufReader, BufWriter, Write};
use std::path::Path;
use std::time::Duration;
use tokio::time::sleep;

#[derive(Debug, Serialize, Deserialize, Clone)]
struct VerifiedContract {
    contract_address: String,
    contract_name: String,
    compiler_version: String,
    contract_creator: String,
    source_code: String,
    timestamp: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct ScraperState {
    processed_contracts: HashSet<String>,
}

const BASE_URL: &str = "https://sepolia.basescan.org/contractsVerified";
const STATE_FILE: &str = "scraper_state.json";
const OUTPUT_FILE: &str = "verified_contracts.json";

async fn fetch_page(client: &Client, url: &str) -> Result<String> {
    let response = client
        .get(url)
        .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        .send()
        .await
        .context("Failed to send request")?;
    
    if !response.status().is_success() {
        anyhow::bail!("HTTP error: {}", response.status());
    }
    
    response.text().await.context("Failed to read response text")
}

fn parse_contracts_table(html: &str) -> Result<Vec<VerifiedContract>> {
    let document = Html::parse_document(html);
    let table_selector = Selector::parse("table.table").unwrap();
    let row_selector = Selector::parse("tbody tr").unwrap();
    let cell_selector = Selector::parse("td").unwrap();
    
    let mut contracts = Vec::new();
    
    if let Some(table) = document.select(&table_selector).next() {
        for row in table.select(&row_selector) {
            let cells: Vec<_> = row.select(&cell_selector).collect();
            
            if cells.len() >= 7 {
                let address_cell = cells[0].text().collect::<String>().trim().to_string();
                let name_cell = cells[1].text().collect::<String>().trim().to_string();
                let compiler_cell = cells[2].text().collect::<String>().trim().to_string();
                let creator_cell = cells[3].text().collect::<String>().trim().to_string();
                
                // Extract contract address from the link if available
                let contract_address = if let Some(link) = cells[0].select(&Selector::parse("a").unwrap()).next() {
                    link.value().attr("href")
                        .and_then(|href| href.split('/').nth(2))
                        .unwrap_or(&address_cell)
                        .to_string()
                } else {
                    address_cell
                };
                
                let contract = VerifiedContract {
                    contract_address: contract_address.clone(),
                    contract_name: name_cell,
                    compiler_version: compiler_cell,
                    contract_creator: creator_cell,
                    source_code: "Source code would be fetched from individual contract page".to_string(),
                    timestamp: chrono::Utc::now().to_rfc3339(),
                };
                
                contracts.push(contract);
            }
        }
    }
    
    Ok(contracts)
}

fn load_state() -> Result<ScraperState> {
    if Path::new(STATE_FILE).exists() {
        let file = File::open(STATE_FILE).context("Failed to open state file")?;
        let reader = BufReader::new(file);
        serde_json::from_reader(reader).context("Failed to parse state file")
    } else {
        Ok(ScraperState {
            processed_contracts: HashSet::new(),
        })
    }
}

fn save_state(state: &ScraperState) -> Result<()> {
    let file = File::create(STATE_FILE).context("Failed to create state file")?;
    let writer = BufWriter::new(file);
    serde_json::to_writer_pretty(writer, state).context("Failed to write state file")
}

fn append_to_output(contracts: &[VerifiedContract]) -> Result<()> {
    let file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(OUTPUT_FILE)
        .context("Failed to open output file")?;
    
    let mut writer = BufWriter::new(file);
    
    for contract in contracts {
        serde_json::to_writer(&mut writer, contract).context("Failed to write contract to output")?;
        writer.write_all(b"\n").context("Failed to write newline")?;
    }
    
    Ok(())
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    
    let client = Client::builder()
        .timeout(Duration::from_secs(30))
        .build()
        .context("Failed to create HTTP client")?;
    
    let mut state = load_state()?;
    
    loop {
        log::info!("Fetching verified contracts from: {}", BASE_URL);
        
        match fetch_page(&client, BASE_URL).await {
            Ok(html) => {
                match parse_contracts_table(&html) {
                    Ok(contracts) => {
                        let new_contracts: Vec<_> = contracts
                            .into_iter()
                            .filter(|contract| !state.processed_contracts.contains(&contract.contract_address))
                            .collect();
                        
                        if !new_contracts.is_empty() {
                            log::info!("Found {} new contracts", new_contracts.len());
                            
                            for contract in &new_contracts {
                                state.processed_contracts.insert(contract.contract_address.clone());
                                log::info!("New contract: {} - {}", contract.contract_address, contract.contract_name);
                            }
                            
                            append_to_output(&new_contracts)?;
                            save_state(&state)?;
                        } else {
                            log::info!("No new contracts found");
                        }
                    }
                    Err(e) => {
                        log::error!("Failed to parse contracts table: {}", e);
                    }
                }
            }
            Err(e) => {
                log::error!("Failed to fetch page: {}", e);
            }
        }
        
        // Rate limiting - wait before next scrape
        log::info!("Waiting 5 minutes before next scrape...");
        sleep(Duration::from_secs(300)).await;
    }
}