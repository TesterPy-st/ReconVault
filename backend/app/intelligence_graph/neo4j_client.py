"""
Neo4j client for ReconVault intelligence graph.

This module handles Neo4j database connection management and
provides a client interface for graph database operations.
"""

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
from typing import Dict, List, Any, Optional
import logging
from app.config import settings

# Configure logging
logger = logging.getLogger("reconvault.neo4j")


class Neo4jClient:
    """
    Neo4j database client for intelligence graph operations.
    
    Provides connection management and basic database operations
    for the ReconVault intelligence graph system.
    """
    
    def __init__(self, uri: str = None, user: str = None, password: str = None, database: str = None):
        """
        Initialize Neo4j client.
        
        Args:
            uri: Neo4j URI (defaults to settings)
            user: Neo4j username (defaults to settings)
            password: Neo4j password (defaults to settings)
            database: Neo4j database name (defaults to settings)
        """
        self.uri = uri or settings.NEO4J_URI
        self.user = user or settings.NEO4J_USER
        self.password = password or settings.NEO4J_PASSWORD
        self.database = database or settings.NEO4J_DATABASE
        self.driver = None
        
        logger.info(f"Initializing Neo4j client for {self.uri}")
    
    def connect(self) -> bool:
        """
        Establish connection to Neo4j database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            logger.info("Connecting to Neo4j database...")
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                max_connection_lifetime=300,
                max_connection_pool_size=50,
                connection_acquisition_timeout=60
            )
            
            # Verify connectivity
            self.verify_connectivity()
            logger.info("Neo4j connection established successfully")
            return True
            
        except AuthError as e:
            logger.error(f"Neo4j authentication failed: {e}")
            return False
        except ServiceUnavailable as e:
            logger.error(f"Neo4j service unavailable: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            return False
    
    def close(self) -> None:
        """
        Close Neo4j connection.
        """
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def verify_connectivity(self) -> bool:
        """
        Verify Neo4j connection is working.
        
        Returns:
            bool: True if connection verified, False otherwise
        
        Raises:
            Exception: If connectivity check fails
        """
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run("RETURN 1 AS test")
                result.single()
            logger.info("Neo4j connectivity verified")
            return True
        except Exception as e:
            logger.error(f"Neo4j connectivity check failed: {e}")
            raise
    
    def run_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
        
        Returns:
            List[Dict[str, Any]]: Query results
        """
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Neo4j query failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Parameters: {parameters}")
            raise
    
    def create_node(self, label: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a node in the graph.
        
        Args:
            label: Node label
            properties: Node properties
        
        Returns:
            Dict[str, Any]: Created node data
        """
        query = f"""
        CREATE (n:{label} $properties)
        RETURN n
        """
        results = self.run_query(query, {"properties": properties})
        return results[0]["n"] if results else {}
    
    def create_relationship(
        self,
        start_node_label: str,
        start_node_properties: Dict[str, Any],
        relationship_type: str,
        end_node_label: str,
        end_node_properties: Dict[str, Any],
        relationship_properties: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a relationship between two nodes.
        
        Args:
            start_node_label: Label of start node
            start_node_properties: Properties of start node
            relationship_type: Type of relationship
            end_node_label: Label of end node
            end_node_properties: Properties of end node
            relationship_properties: Properties of relationship
        
        Returns:
            Dict[str, Any]: Created relationship data
        """
        query = f"""
        MERGE (start:{start_node_label} $start_properties)
        MERGE (end:{end_node_label} $end_properties)
        MERGE (start)-[r:{relationship_type} $relationship_properties]->(end)
        RETURN start, r, end
        """
        
        parameters = {
            "start_properties": start_node_properties,
            "end_properties": end_node_properties,
            "relationship_properties": relationship_properties or {}
        }
        
        results = self.run_query(query, parameters)
        return results[0] if results else {}
    
    def find_node(self, label: str, properties: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a node by properties.
        
        Args:
            label: Node label
            properties: Node properties to match
        
        Returns:
            Optional[Dict[str, Any]]: Found node or None
        """
        query = f"""
        MATCH (n:{label} $properties)
        RETURN n
        """
        results = self.run_query(query, {"properties": properties})
        return results[0]["n"] if results else None
    
    def get_node_by_id(self, node_id: int) -> Optional[Dict[str, Any]]:
        """
        Get node by Neo4j internal ID.
        
        Args:
            node_id: Neo4j internal node ID
        
        Returns:
            Optional[Dict[str, Any]]: Found node or None
        """
        query = """
        MATCH (n)
        WHERE ID(n) = $node_id
        RETURN n
        """
        results = self.run_query(query, {"node_id": node_id})
        return results[0]["n"] if results else None
    
    def update_node(self, label: str, match_properties: Dict[str, Any], update_properties: Dict[str, Any]) -> bool:
        """
        Update node properties.
        
        Args:
            label: Node label
            match_properties: Properties to match the node
            update_properties: Properties to update
        
        Returns:
            bool: True if update successful
        """
        query = f"""
        MATCH (n:{label} $match_properties)
        SET n += $update_properties
        RETURN n
        """
        
        parameters = {
            "match_properties": match_properties,
            "update_properties": update_properties
        }
        
        try:
            self.run_query(query, parameters)
            return True
        except Exception as e:
            logger.error(f"Failed to update node: {e}")
            return False
    
    def delete_node(self, label: str, properties: Dict[str, Any]) -> bool:
        """
        Delete a node and its relationships.
        
        Args:
            label: Node label
            properties: Properties to match the node
        
        Returns:
            bool: True if deletion successful
        """
        query = f"""
        MATCH (n:{label} $properties)
        DETACH DELETE n
        """
        
        try:
            self.run_query(query, {"properties": properties})
            return True
        except Exception as e:
            logger.error(f"Failed to delete node: {e}")
            return False
    
    def get_relationships(self, node_id: int, direction: str = "both") -> List[Dict[str, Any]]:
        """
        Get relationships for a node.
        
        Args:
            node_id: Neo4j internal node ID
            direction: Relationship direction ("in", "out", "both")
        
        Returns:
            List[Dict[str, Any]]: List of relationships
        """
        if direction == "in":
            query = """
            MATCH (n)<-[r]-(related)
            WHERE ID(n) = $node_id
            RETURN ID(n) as source_id, ID(related) as target_id, type(r) as relationship_type, r as properties
            """
        elif direction == "out":
            query = """
            MATCH (n)-[r]->(related)
            WHERE ID(n) = $node_id
            RETURN ID(n) as source_id, ID(related) as target_id, type(r) as relationship_type, r as properties
            """
        else:  # both
            query = """
            MATCH (n)-[r]-(related)
            WHERE ID(n) = $node_id
            RETURN ID(n) as source_id, ID(related) as target_id, type(r) as relationship_type, r as properties
            """
        
        results = self.run_query(query, {"node_id": node_id})
        return results
    
    def get_subgraph(self, node_id: int, depth: int = 2) -> Dict[str, Any]:
        """
        Get subgraph starting from a node.
        
        Args:
            node_id: Starting node ID
            depth: Maximum depth to traverse
        
        Returns:
            Dict[str, Any]: Subgraph data with nodes and relationships
        """
        query = f"""
        MATCH path = (start)-[*1..{depth}]-(related)
        WHERE ID(start) = $node_id
        WITH collect(DISTINCT nodes(path)) as node_lists, 
             collect(DISTINCT relationships(path)) as rel_lists
        UNWIND node_lists[0] as node_list
        UNWIND rel_lists[0] as rel_list
        RETURN collect(DISTINCT node_list) as nodes, 
               collect(DISTINCT rel_list) as relationships
        """
        
        results = self.run_query(query, {"node_id": node_id})
        return results[0] if results else {"nodes": [], "relationships": []}
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get database information.
        
        Returns:
            Dict[str, Any]: Database information
        """
        query = """
        CALL dbms.components() YIELD name, versions, edition
        RETURN collect({name: name, versions: versions, edition: edition}) as components
        """
        
        results = self.run_query(query)
        return results[0] if results else {}
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """
        Get graph statistics.
        
        Returns:
            Dict[str, Any]: Graph statistics
        """
        queries = {
            "node_count": "MATCH (n) RETURN count(n) as count",
            "relationship_count": "MATCH ()-[r]->() RETURN count(r) as count",
            "label_counts": "CALL db.labels() YIELD label RETURN collect({label: label, count: gds.util.nodeCount(null, [label])}) as labels"
        }
        
        stats = {}
        for key, query in queries.items():
            try:
                results = self.run_query(query)
                stats[key] = results[0] if results else {}
            except Exception as e:
                logger.warning(f"Failed to get {key}: {e}")
                stats[key] = {}
        
        return stats


# Global Neo4j client instance
neo4j_client = Neo4jClient()


def get_neo4j_client() -> Neo4jClient:
    """
    Get global Neo4j client instance.
    
    Returns:
        Neo4jClient: Global Neo4j client
    """
    return neo4j_client


def init_neo4j_connection() -> bool:
    """
    Initialize Neo4j connection.
    
    Returns:
        bool: True if connection successful
    """
    try:
        return neo4j_client.connect()
    except Exception as e:
        logger.error(f"Failed to initialize Neo4j connection: {e}")
        return False


def close_neo4j_connection() -> None:
    """
    Close Neo4j connection.
    """
    neo4j_client.close()