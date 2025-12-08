"""
Database Service for storing analysis logs and results in scathat-data-base
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for interacting with scathat-data-base"""

    def __init__(self, db_path: str = "/Users/rackerjoyjugalbot/Scathat/scathat-data-base/scathat.db"):
        """
        Initialize database service with SQLite connection.
        
        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_database_exists()

    def _ensure_database_exists(self):
        """Ensure database file and tables exist"""
        try:
            # Create directory if it doesn't exist
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            # Connect to database and create tables
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create analysis_logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id TEXT UNIQUE,
                    contract_address TEXT NOT NULL,
                    risk_score REAL,
                    risk_level TEXT,
                    explanation TEXT,
                    detected_issues TEXT,
                    recommendations TEXT,
                    model_contributions TEXT,
                    normalized_metadata TEXT,
                    embedding_vector TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create risk_history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS risk_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contract_address TEXT NOT NULL,
                    risk_score REAL,
                    risk_level TEXT,
                    analysis_id TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (analysis_id) REFERENCES analysis_logs (scan_id)
                )
            """)
            
            # Create transaction_analysis table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transaction_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT UNIQUE,
                    transaction_hash TEXT NOT NULL,
                    risk_score REAL,
                    risk_level TEXT,
                    explanation TEXT,
                    detected_anomalies TEXT,
                    contract_interactions TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create model_config table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT UNIQUE,
                    weights TEXT,
                    enabled BOOLEAN DEFAULT TRUE,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info(f"Database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

    def save_analysis_log(self, 
                         scan_id: str, 
                         contract_address: str, 
                         risk_score: float, 
                         risk_level: str,
                         explanation: str,
                         detected_issues: List[str],
                         recommendations: List[str],
                         model_contributions: Dict[str, float],
                         normalized_metadata: Dict[str, Any],
                         embedding_vector: List[float]) -> bool:
        """
        Save contract analysis log to database.
        
        Args:
            scan_id (str): Unique scan identifier
            contract_address (str): Contract address analyzed
            risk_score (float): Final risk score
            risk_level (str): Risk level (Safe/Warning/Dangerous)
            explanation (str): Risk explanation
            detected_issues (List[str]): List of detected issues
            recommendations (List[str]): List of recommendations
            model_contributions (Dict[str, float]): Model contribution weights
            normalized_metadata (Dict[str, Any]): Normalized contract metadata
            embedding_vector (List[float]): Embedding vector for Pinecone
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO analysis_logs 
                (scan_id, contract_address, risk_score, risk_level, explanation, 
                 detected_issues, recommendations, model_contributions, 
                 normalized_metadata, embedding_vector)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scan_id,
                contract_address.lower(),
                risk_score,
                risk_level,
                explanation,
                json.dumps(detected_issues),
                json.dumps(recommendations),
                json.dumps(model_contributions),
                json.dumps(normalized_metadata),
                json.dumps(embedding_vector)
            ))
            
            # Also add to risk history
            cursor.execute("""
                INSERT INTO risk_history 
                (contract_address, risk_score, risk_level, analysis_id)
                VALUES (?, ?, ?, ?)
            """, (
                contract_address.lower(),
                risk_score,
                risk_level,
                scan_id
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Analysis log saved for contract {contract_address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save analysis log: {str(e)}")
            return False

    def get_risk_history(self, contract_address: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get risk history for a contract.
        
        Args:
            contract_address (str): Contract address
            days (int): Number of days of history to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of historical risk records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    timestamp, 
                    risk_score, 
                    risk_level, 
                    analysis_id
                FROM risk_history 
                WHERE contract_address = ? 
                AND timestamp >= datetime('now', ?)
                ORDER BY timestamp DESC
            """, (contract_address.lower(), f'-{days} days'))
            
            results = cursor.fetchall()
            conn.close()
            
            history = []
            for row in results:
                history.append({
                    'timestamp': row[0],
                    'risk_score': row[1],
                    'risk_level': row[2],
                    'analysis_id': row[3]
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get risk history: {str(e)}")
            return []

    def save_transaction_analysis(self,
                                 analysis_id: str,
                                 transaction_hash: str,
                                 risk_score: float,
                                 risk_level: str,
                                 explanation: str,
                                 detected_anomalies: List[str],
                                 contract_interactions: List[str]) -> bool:
        """
        Save transaction analysis to database.
        
        Args:
            analysis_id (str): Unique analysis identifier
            transaction_hash (str): Transaction hash
            risk_score (float): Risk score
            risk_level (str): Risk level
            explanation (str): Explanation
            detected_anomalies (List[str]): Detected anomalies
            contract_interactions (List[str]): Contract interactions
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO transaction_analysis 
                (analysis_id, transaction_hash, risk_score, risk_level, explanation,
                 detected_anomalies, contract_interactions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_id,
                transaction_hash.lower(),
                risk_score,
                risk_level,
                explanation,
                json.dumps(detected_anomalies),
                json.dumps(contract_interactions)
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Transaction analysis saved for {transaction_hash}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save transaction analysis: {str(e)}")
            return False

    def update_model_config(self, 
                           model_name: str, 
                           weights: Dict[str, float], 
                           enabled: bool) -> bool:
        """
        Update AI model configuration.
        
        Args:
            model_name (str): Model name
            weights (Dict[str, float]): Model weights
            enabled (bool): Whether model is enabled
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO model_config 
                (model_name, weights, enabled)
                VALUES (?, ?, ?)
            """, (
                model_name,
                json.dumps(weights),
                enabled
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Model configuration updated for {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update model configuration: {str(e)}")
            return False

    def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get model configuration.
        
        Args:
            model_name (str): Model name
            
        Returns:
            Optional[Dict[str, Any]]: Model configuration
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT weights, enabled, updated_at 
                FROM model_config 
                WHERE model_name = ?
            """, (model_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'weights': json.loads(result[0]),
                    'enabled': bool(result[1]),
                    'updated_at': result[2]
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get model configuration: {str(e)}")
            return None

    def get_recent_analyses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent contract analyses.
        
        Args:
            limit (int): Number of analyses to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of recent analyses
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    scan_id, contract_address, risk_score, risk_level, 
                    explanation, created_at
                FROM analysis_logs 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            analyses = []
            for row in results:
                analyses.append({
                    'scan_id': row[0],
                    'contract_address': row[1],
                    'risk_score': row[2],
                    'risk_level': row[3],
                    'explanation': row[4],
                    'created_at': row[5]
                })
            
            return analyses
            
        except Exception as e:
            logger.error(f"Failed to get recent analyses: {str(e)}")
            return []

    def get_analysis_by_id(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """
        Get analysis by scan ID.
        
        Args:
            scan_id (str): Scan identifier
            
        Returns:
            Optional[Dict[str, Any]]: Analysis details
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    scan_id, contract_address, risk_score, risk_level, 
                    explanation, detected_issues, recommendations,
                    model_contributions, normalized_metadata, created_at
                FROM analysis_logs 
                WHERE scan_id = ?
            """, (scan_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'scan_id': result[0],
                    'contract_address': result[1],
                    'risk_score': result[2],
                    'risk_level': result[3],
                    'explanation': result[4],
                    'detected_issues': json.loads(result[5]),
                    'recommendations': json.loads(result[6]),
                    'model_contributions': json.loads(result[7]),
                    'normalized_metadata': json.loads(result[8]),
                    'created_at': result[9]
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get analysis by ID: {str(e)}")
            return None