"""
Exposure Models for Risk Assessment

Implements specialized exposure calculators for different risk categories:
- Data exposure
- Network exposure
- Identity exposure
- Infrastructure exposure
"""

from typing import Any, Dict, List
from loguru import logger


class DataExposureModel:
    """
    Calculates exposure related to sensitive data leaks.
    """
    
    def calculate_exposure(self, entity: Dict[str, Any]) -> float:
        """
        Calculate data exposure score (0-100).
        
        Args:
            entity: Entity dictionary
            
        Returns:
            Exposure score
        """
        exposure_score = 0.0
        metadata = entity.get("metadata", {})
        
        if isinstance(metadata, str):
            import json
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        # Data breach history
        breaches = metadata.get("breaches_found", 0)
        if breaches > 0:
            exposure_score += min(breaches * 15, 40)
        
        # Dark web mentions
        if metadata.get("dark_web_mentions"):
            exposure_score += 25
        
        # PII exposure
        if metadata.get("pii_exposed"):
            exposure_score += 20
        
        # Credentials leaked
        if metadata.get("credentials_leaked"):
            exposure_score += 30
        
        # Database dumps
        if metadata.get("in_database_dump"):
            exposure_score += 25
        
        # Paste sites
        paste_count = metadata.get("paste_mentions", 0)
        if paste_count > 0:
            exposure_score += min(paste_count * 5, 15)
        
        return min(exposure_score, 100)
    
    def get_exposure_details(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed exposure breakdown.
        
        Args:
            entity: Entity dictionary
            
        Returns:
            Detailed exposure information
        """
        metadata = entity.get("metadata", {})
        if isinstance(metadata, str):
            import json
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        return {
            "exposure_score": self.calculate_exposure(entity),
            "breaches_found": metadata.get("breaches_found", 0),
            "dark_web_mentions": metadata.get("dark_web_mentions", False),
            "pii_exposed": metadata.get("pii_exposed", False),
            "credentials_leaked": metadata.get("credentials_leaked", False),
            "paste_mentions": metadata.get("paste_mentions", 0),
            "exposure_level": self._get_level(self.calculate_exposure(entity))
        }
    
    def _get_level(self, score: float) -> str:
        """Convert score to level."""
        if score >= 76:
            return "critical"
        elif score >= 51:
            return "high"
        elif score >= 26:
            return "medium"
        else:
            return "low"


class NetworkExposureModel:
    """
    Calculates exposure related to network topology and connectivity.
    """
    
    def calculate_exposure(self, entity: Dict[str, Any]) -> float:
        """
        Calculate network exposure score (0-100).
        
        Args:
            entity: Entity dictionary
            
        Returns:
            Exposure score
        """
        exposure_score = 0.0
        metadata = entity.get("metadata", {})
        
        if isinstance(metadata, str):
            import json
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        # Open ports
        open_ports = metadata.get("open_ports", [])
        if isinstance(open_ports, list) and open_ports:
            high_risk_ports = [21, 22, 23, 135, 139, 445, 1433, 3306, 3389, 5432]
            
            try:
                port_nums = [p.get("port", 0) if isinstance(p, dict) else p for p in open_ports]
                total_ports = len(port_nums)
                risky_ports = len([p for p in port_nums if p in high_risk_ports])
                
                exposure_score += min(total_ports * 2, 20)
                exposure_score += risky_ports * 8
            except:
                pass
        
        # Publicly accessible
        if metadata.get("publicly_accessible", False):
            exposure_score += 15
        
        # No firewall
        if metadata.get("firewall_detected") == False:
            exposure_score += 20
        
        # Weak encryption
        if metadata.get("weak_encryption"):
            exposure_score += 15
        
        # Outdated protocols
        if metadata.get("uses_outdated_protocols"):
            exposure_score += 10
        
        # High connectivity (many relationships)
        relationship_count = entity.get("relationship_count", 0)
        if relationship_count > 10:
            exposure_score += min(relationship_count, 20)
        
        return min(exposure_score, 100)
    
    def get_exposure_details(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed network exposure breakdown.
        
        Args:
            entity: Entity dictionary
            
        Returns:
            Detailed exposure information
        """
        metadata = entity.get("metadata", {})
        if isinstance(metadata, str):
            import json
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        open_ports = metadata.get("open_ports", [])
        if isinstance(open_ports, list):
            try:
                port_nums = [p.get("port", 0) if isinstance(p, dict) else p for p in open_ports]
            except:
                port_nums = []
        else:
            port_nums = []
        
        return {
            "exposure_score": self.calculate_exposure(entity),
            "open_ports_count": len(port_nums),
            "open_ports": port_nums[:10],  # Limit for display
            "publicly_accessible": metadata.get("publicly_accessible", False),
            "firewall_detected": metadata.get("firewall_detected", True),
            "relationship_count": entity.get("relationship_count", 0),
            "exposure_level": self._get_level(self.calculate_exposure(entity))
        }
    
    def _get_level(self, score: float) -> str:
        """Convert score to level."""
        if score >= 76:
            return "critical"
        elif score >= 51:
            return "high"
        elif score >= 26:
            return "medium"
        else:
            return "low"


class IdentityExposureModel:
    """
    Calculates exposure related to personal identity and PII.
    """
    
    def calculate_exposure(self, entity: Dict[str, Any]) -> float:
        """
        Calculate identity exposure score (0-100).
        
        Args:
            entity: Entity dictionary
            
        Returns:
            Exposure score
        """
        exposure_score = 0.0
        metadata = entity.get("metadata", {})
        
        if isinstance(metadata, str):
            import json
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        entity_type = entity.get("type", "").lower()
        
        # Email/phone exposure
        if entity_type in ["email", "phone"]:
            exposure_score += 10
            
            # If found in breaches
            if metadata.get("breaches_found", 0) > 0:
                exposure_score += 30
        
        # Social media exposure
        if entity_type == "social_handle":
            exposure_score += 5
            
            # Public profile
            if metadata.get("profile_public"):
                exposure_score += 10
            
            # Many followers (high visibility)
            followers = metadata.get("followers", 0)
            if followers > 1000:
                exposure_score += 10
        
        # Personal information exposed
        pii_fields = ["address", "ssn", "dob", "phone", "email", "passport"]
        exposed_pii = sum(1 for field in pii_fields if metadata.get(f"{field}_exposed"))
        exposure_score += exposed_pii * 10
        
        # Identity theft indicators
        if metadata.get("identity_theft_detected"):
            exposure_score += 40
        
        # Multiple online identities
        online_identities = metadata.get("online_identities", [])
        if isinstance(online_identities, list):
            exposure_score += min(len(online_identities) * 3, 15)
        
        return min(exposure_score, 100)
    
    def get_exposure_details(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed identity exposure breakdown.
        
        Args:
            entity: Entity dictionary
            
        Returns:
            Detailed exposure information
        """
        metadata = entity.get("metadata", {})
        if isinstance(metadata, str):
            import json
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        pii_fields = ["address", "ssn", "dob", "phone", "email", "passport"]
        exposed_pii = [field for field in pii_fields if metadata.get(f"{field}_exposed")]
        
        return {
            "exposure_score": self.calculate_exposure(entity),
            "entity_type": entity.get("type"),
            "breaches_found": metadata.get("breaches_found", 0),
            "exposed_pii_fields": exposed_pii,
            "identity_theft_detected": metadata.get("identity_theft_detected", False),
            "online_identities_count": len(metadata.get("online_identities", [])),
            "exposure_level": self._get_level(self.calculate_exposure(entity))
        }
    
    def _get_level(self, score: float) -> str:
        """Convert score to level."""
        if score >= 76:
            return "critical"
        elif score >= 51:
            return "high"
        elif score >= 26:
            return "medium"
        else:
            return "low"


class InfrastructureExposureModel:
    """
    Calculates exposure related to infrastructure vulnerabilities.
    """
    
    def calculate_exposure(self, entity: Dict[str, Any]) -> float:
        """
        Calculate infrastructure exposure score (0-100).
        
        Args:
            entity: Entity dictionary
            
        Returns:
            Exposure score
        """
        exposure_score = 0.0
        metadata = entity.get("metadata", {})
        
        if isinstance(metadata, str):
            import json
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        # SSL/TLS issues
        ssl_expiry = metadata.get("days_until_expiry", 365)
        if ssl_expiry < 30:
            exposure_score += 20
        elif ssl_expiry < 7:
            exposure_score += 35
        
        if not metadata.get("has_ssl", True):
            exposure_score += 25
        
        if metadata.get("ssl_vulnerable"):
            exposure_score += 30
        
        # Software vulnerabilities
        vulnerabilities = metadata.get("vulnerabilities", [])
        if isinstance(vulnerabilities, list):
            cve_count = len(vulnerabilities)
            exposure_score += min(cve_count * 10, 40)
            
            # Critical CVEs
            critical_cves = [v for v in vulnerabilities if isinstance(v, dict) and v.get("severity") == "critical"]
            exposure_score += len(critical_cves) * 5
        
        # Outdated software
        if metadata.get("outdated_software"):
            exposure_score += 15
        
        # Misconfigurations
        if metadata.get("misconfigured"):
            exposure_score += 20
        
        # Unpatched systems
        if metadata.get("unpatched"):
            exposure_score += 25
        
        # Weak authentication
        if metadata.get("weak_auth"):
            exposure_score += 15
        
        # Default credentials
        if metadata.get("default_credentials"):
            exposure_score += 30
        
        return min(exposure_score, 100)
    
    def get_exposure_details(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed infrastructure exposure breakdown.
        
        Args:
            entity: Entity dictionary
            
        Returns:
            Detailed exposure information
        """
        metadata = entity.get("metadata", {})
        if isinstance(metadata, str):
            import json
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        vulnerabilities = metadata.get("vulnerabilities", [])
        if isinstance(vulnerabilities, list):
            vuln_count = len(vulnerabilities)
            critical_vulns = [v for v in vulnerabilities if isinstance(v, dict) and v.get("severity") == "critical"]
        else:
            vuln_count = 0
            critical_vulns = []
        
        return {
            "exposure_score": self.calculate_exposure(entity),
            "ssl_days_until_expiry": metadata.get("days_until_expiry", 365),
            "has_ssl": metadata.get("has_ssl", True),
            "vulnerabilities_count": vuln_count,
            "critical_vulnerabilities": len(critical_vulns),
            "outdated_software": metadata.get("outdated_software", False),
            "misconfigured": metadata.get("misconfigured", False),
            "unpatched": metadata.get("unpatched", False),
            "exposure_level": self._get_level(self.calculate_exposure(entity))
        }
    
    def _get_level(self, score: float) -> str:
        """Convert score to level."""
        if score >= 76:
            return "critical"
        elif score >= 51:
            return "high"
        elif score >= 26:
            return "medium"
        else:
            return "low"


class ExposureAnalyzer:
    """
    Main exposure analyzer that combines all exposure models.
    """
    
    def __init__(self):
        """Initialize all exposure models."""
        self.data_model = DataExposureModel()
        self.network_model = NetworkExposureModel()
        self.identity_model = IdentityExposureModel()
        self.infrastructure_model = InfrastructureExposureModel()
    
    def calculate_total_exposure(self, entity: Dict[str, Any]) -> float:
        """
        Calculate total exposure combining all models.
        
        Args:
            entity: Entity dictionary
            
        Returns:
            Overall exposure score (0-100)
        """
        # Calculate individual exposures
        data_exp = self.data_model.calculate_exposure(entity)
        network_exp = self.network_model.calculate_exposure(entity)
        identity_exp = self.identity_model.calculate_exposure(entity)
        infra_exp = self.infrastructure_model.calculate_exposure(entity)
        
        # Weight by entity type
        entity_type = entity.get("type", "").lower()
        
        if entity_type in ["email", "phone", "person"]:
            # Identity and data exposure more important
            total = (identity_exp * 0.4 + data_exp * 0.3 + 
                    network_exp * 0.15 + infra_exp * 0.15)
        elif entity_type in ["domain", "ip_address", "website"]:
            # Infrastructure and network more important
            total = (infra_exp * 0.35 + network_exp * 0.35 + 
                    data_exp * 0.20 + identity_exp * 0.10)
        elif entity_type in ["vulnerability", "malware"]:
            # Infrastructure critical
            total = (infra_exp * 0.50 + network_exp * 0.25 + 
                    data_exp * 0.15 + identity_exp * 0.10)
        else:
            # Balanced approach
            total = (data_exp * 0.25 + network_exp * 0.25 + 
                    identity_exp * 0.25 + infra_exp * 0.25)
        
        return min(total, 100)
    
    def get_comprehensive_exposure(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get comprehensive exposure analysis.
        
        Args:
            entity: Entity dictionary
            
        Returns:
            Complete exposure breakdown
        """
        return {
            "total_exposure": self.calculate_total_exposure(entity),
            "data_exposure": self.data_model.get_exposure_details(entity),
            "network_exposure": self.network_model.get_exposure_details(entity),
            "identity_exposure": self.identity_model.get_exposure_details(entity),
            "infrastructure_exposure": self.infrastructure_model.get_exposure_details(entity)
        }
