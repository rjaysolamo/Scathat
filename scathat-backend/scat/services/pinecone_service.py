"""
Pinecone Service for storing and retrieving embedding vectors
"""

import logging
from typing import List, Dict, Any, Optional
import pinecone
from datetime import datetime

logger = logging.getLogger(__name__)


class PineconeService:
    """Service for interacting with Pinecone vector database"""

    def __init__(self, api_key: str, environment: str = "us-east1-gcp"):
        """
        Initialize Pinecone service.
        
        Args:
            api_key (str): Pinecone API key
            environment (str): Pinecone environment
        """
        self.api_key = api_key
        self.environment = environment
        self.index_name = "scathat-contracts"
        self.dimension = 128  # Must match embedding vector dimension
        self.metric = "cosine"
        
        try:
            # Initialize Pinecone
            pinecone.init(api_key=api_key, environment=environment)
            
            # Create index if it doesn't exist
            if self.index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=self.metric
                )
                logger.info(f"Created Pinecone index: {self.index_name}")
            
            # Connect to index
            self.index = pinecone.Index(self.index_name)
            logger.info(f"Pinecone service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone service: {str(e)}")
            self.index = None

    def is_available(self) -> bool:
        """Check if Pinecone service is available"""
        return self.index is not None

    def store_embedding(self, 
                       contract_address: str, 
                       embedding_vector: List[float], 
                       metadata: Dict[str, Any]) -> bool:
        """
        Store embedding vector in Pinecone.
        
        Args:
            contract_address (str): Contract address as unique ID
            embedding_vector (List[float]): Embedding vector
            metadata (Dict[str, Any]): Additional metadata
            
        Returns:
            bool: True if storage was successful, False otherwise
        """
        if not self.is_available():
            logger.warning("Pinecone service not available")
            return False
        
        if len(embedding_vector) != self.dimension:
            logger.error(f"Embedding vector dimension mismatch: expected {self.dimension}, got {len(embedding_vector)}")
            return False
        
        try:
            # Prepare metadata with timestamp
            full_metadata = {
                **metadata,
                'contract_address': contract_address.lower(),
                'stored_at': datetime.utcnow().isoformat(),
                'vector_dimension': self.dimension
            }
            
            # Upsert vector to Pinecone
            self.index.upsert(
                vectors=[(
                    contract_address.lower(),  # Use contract address as ID
                    embedding_vector,
                    full_metadata
                )]
            )
            
            logger.info(f"Embedding stored for contract {contract_address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store embedding: {str(e)}")
            return False

    def query_similar_contracts(self, 
                              embedding_vector: List[float], 
                              top_k: int = 5,
                              filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Query similar contracts based on embedding similarity.
        
        Args:
            embedding_vector (List[float]): Query embedding vector
            top_k (int): Number of similar results to return
            filter_metadata (Optional[Dict[str, Any]]): Metadata filters
            
        Returns:
            List[Dict[str, Any]]: List of similar contracts with scores
        """
        if not self.is_available():
            logger.warning("Pinecone service not available")
            return []
        
        if len(embedding_vector) != self.dimension:
            logger.error(f"Embedding vector dimension mismatch: expected {self.dimension}, got {len(embedding_vector)}")
            return []
        
        try:
            # Query Pinecone for similar vectors
            query_response = self.index.query(
                vector=embedding_vector,
                top_k=top_k,
                include_metadata=True,
                filter=filter_metadata
            )
            
            results = []
            for match in query_response.get('matches', []):
                results.append({
                    'contract_address': match['id'],
                    'similarity_score': match['score'],
                    'metadata': match['metadata']
                })
            
            logger.info(f"Found {len(results)} similar contracts")
            return results
            
        except Exception as e:
            logger.error(f"Failed to query similar contracts: {str(e)}")
            return []

    def get_contract_embedding(self, contract_address: str) -> Optional[Dict[str, Any]]:
        """
        Get embedding and metadata for a specific contract.
        
        Args:
            contract_address (str): Contract address
            
        Returns:
            Optional[Dict[str, Any]]: Embedding data with metadata
        """
        if not self.is_available():
            logger.warning("Pinecone service not available")
            return None
        
        try:
            # Fetch vector by ID
            fetch_response = self.index.fetch(ids=[contract_address.lower()])
            
            vectors = fetch_response.get('vectors', {})
            if contract_address.lower() in vectors:
                vector_data = vectors[contract_address.lower()]
                return {
                    'embedding': vector_data['values'],
                    'metadata': vector_data['metadata']
                }
            else:
                logger.warning(f"No embedding found for contract {contract_address}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get contract embedding: {str(e)}")
            return None

    def update_contract_metadata(self, 
                               contract_address: str, 
                               new_metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for an existing contract embedding.
        
        Args:
            contract_address (str): Contract address
            new_metadata (Dict[str, Any]): New metadata to merge
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        if not self.is_available():
            logger.warning("Pinecone service not available")
            return False
        
        try:
            # First get current embedding and metadata
            current_data = self.get_contract_embedding(contract_address)
            if not current_data:
                logger.warning(f"Cannot update metadata: contract {contract_address} not found")
                return False
            
            # Merge metadata
            updated_metadata = {
                **current_data['metadata'],
                **new_metadata,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Update the vector with merged metadata
            self.index.upsert(
                vectors=[(
                    contract_address.lower(),
                    current_data['embedding'],
                    updated_metadata
                )]
            )
            
            logger.info(f"Metadata updated for contract {contract_address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update contract metadata: {str(e)}")
            return False

    def delete_contract_embedding(self, contract_address: str) -> bool:
        """
        Delete embedding for a contract.
        
        Args:
            contract_address (str): Contract address
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        if not self.is_available():
            logger.warning("Pinecone service not available")
            return False
        
        try:
            self.index.delete(ids=[contract_address.lower()])
            logger.info(f"Embedding deleted for contract {contract_address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete contract embedding: {str(e)}")
            return False

    def get_index_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get Pinecone index statistics.
        
        Returns:
            Optional[Dict[str, Any]]: Index statistics
        """
        if not self.is_available():
            logger.warning("Pinecone service not available")
            return None
        
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vectors': stats['total_vector_count'],
                'index_dimension': stats['dimension'],
                'index_fullness': stats.get('index_fullness', 0),
                'namespaces': stats['namespaces']
            }
            
        except Exception as e:
            logger.error(f"Failed to get index stats: {str(e)}")
            return None

    def search_by_risk_level(self, 
                           risk_level: str, 
                           top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search contracts by risk level using metadata filtering.
        
        Args:
            risk_level (str): Risk level to filter by
            top_k (int): Number of results to return
            
        Returns:
            List[Dict[str, Any]]: Contracts with specified risk level
        """
        if not self.is_available():
            logger.warning("Pinecone service not available")
            return []
        
        try:
            # Use empty vector with metadata filter
            dummy_vector = [0.0] * self.dimension
            
            query_response = self.index.query(
                vector=dummy_vector,
                top_k=top_k,
                include_metadata=True,
                filter={"risk_level": {"$eq": risk_level.lower()}}
            )
            
            results = []
            for match in query_response.get('matches', []):
                results.append({
                    'contract_address': match['id'],
                    'similarity_score': match['score'],
                    'metadata': match['metadata']
                })
            
            logger.info(f"Found {len(results)} contracts with risk level {risk_level}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search by risk level: {str(e)}")
            return []