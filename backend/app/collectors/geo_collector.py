"""
Geolocation OSINT Collector for ReconVault intelligence system.

This module provides geospatial intelligence gathering using geopy,
OSMnx, and location-based data analysis.
"""

import asyncio
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from geopy.geocoders import Nominatim
from geopy.exc import GeopyException
from geopy.distance import geodesic
import networkx as nx

# Conditional imports for optional dependencies
try:
    import folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False
    folium = None

try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False
    gpd = None

from .base_collector import BaseCollector, CollectorConfig


class GeoCollector(BaseCollector):
    """Geolocation OSINT collector for geographic intelligence"""
    
    def __init__(self, config: CollectorConfig):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Initialize geocoders
        self.geolocator = Nominatim(
            user_agent="ReconVault-OSINT-Collector/1.0",
            timeout=config.timeout
        )
        
        # Placeholder for OSMnx graph (would be initialized per city)
        self.osm_graph = None
    
    async def collect(self) -> Dict[str, Any]:
        """Collect geolocation intelligence data"""
        self.logger.info(f"Starting geolocation collection for target: {self.config.target}")
        
        results = {
            "target": self.config.target,
            "entities": [],
            "relationships": [],
            "metadata": {}
        }
        
        try:
            # Detect location input type
            location_type = self._detect_location_type(self.config.target)
            
            if location_type == "coordinates":
                # Reverse geocoding
                coords = self._parse_coordinates(self.config.target)
                if coords:
                    location_data = await self.reverse_geocode(coords[0], coords[1])
                    if location_data:
                        results["entities"].extend(location_data.get("entities", []))
                        results["relationships"].extend(location_data.get("relationships", []))
                        results["metadata"]["reverse_geocode"] = location_data.get("metadata", {})
                        
                        # Get nearby points of interest
                        nearby_data = await self.get_nearby_businesses(coords[0], coords[1], radius=1000)
                        results["entities"].extend(nearby_data.get("entities", []))
                        results["metadata"]["nearby"] = nearby_data.get("metadata", {})
            
            elif location_type == "address":
                # Forward geocoding
                geo_data = await self.forward_geocode(self.config.target)
                if geo_data:
                    results["entities"].extend(geo_data.get("entities", []))
                    results["relationships"].extend(geo_data.get("relationships", []))
                    results["metadata"]["geocode"] = geo_data.get("metadata", {})
                    
                    # Get coordinates for further analysis
                    coords = (geo_data["metadata"]["latitude"], geo_data["metadata"]["longitude"])
                    
                    # Get nearby businesses
                    nearby_data = await self.get_nearby_businesses(coords[0], coords[1], radius=1000)
                    results["entities"].extend(nearby_data.get("entities", []))
            
            elif location_type == "business_name":
                # Search by business name
                search_data = await self.search_location(self.config.target)
                results["entities"].extend(search_data.get("entities", []))
                results["relationships"].extend(search_data.get("relationships", []))
                results["metadata"]["search"] = search_data.get("metadata", {})
            
            else:
                self.logger.warning(f"Unknown location format: {self.config.target}")
            
            # Extract location relationships
            if results["entities"]:
                relationship_data = await self.extract_location_relationships(results["entities"])
                results["relationships"].extend(relationship_data.get("relationships", []))
                results["metadata"]["relationships"] = relationship_data.get("metadata", {})
            
            return results
            
        except Exception as e:
            self.logger.error(f"Geolocation collection failed: {e}")
            raise
    
    def _detect_location_type(self, target: str) -> str:
        """Detect the type of location input"""
        # Check for coordinates pattern (lat, lon)
        coord_pattern = r'[-+]?\d+\.\d+\s*,\s*[-+]?\d+\.\d+'
        if re.match(coord_pattern, target.replace(' ', '')):
            return "coordinates"
        
        # Check if it looks like an address (contains typical address elements)
        address_indicators = ['street', 'st', 'avenue', 'ave', 'road', 'rd', 'boulevard', 'blvd',
                            'city', 'town', 'state', 'province', 'country', 'zip', 'postal']
        
        target_lower = target.lower()
        if any(indicator in target_lower for indicator in address_indicators) or len(target.split(',')) >= 3:
            return "address"
        
        # Default to business name search
        return "business_name"
    
    def _parse_coordinates(self, target: str) -> Optional[Tuple[float, float]]:
        """Parse latitude and longitude from string"""
        try:
            # Remove any characters except numbers, decimal points, minus, plus, and comma
            coords = re.sub(r'[^0-9+\-.]', '', target)
            parts = coords.split(',')
            
            if len(parts) == 2:
                lat = float(parts[0].strip())
                lon = float(parts[1].strip())
                
                # Validate coordinate ranges
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return (lat, lon)
            
            return None
        
        except Exception as e:
            self.logger.error(f"Error parsing coordinates: {e}")
            return None
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Convert coordinates to address/location"""
        try:
            self.logger.debug(f"Reverse geocoding: {latitude}, {longitude}")
            
            location = self.geolocator.reverse((latitude, longitude), language='en')
            
            if location:
                address = location.raw.get('address', {})
                display_name = location.raw.get('display_name', '')
                
                # Create location entity
                location_entity = {
                    "value": display_name,
                    "type": "LOCATION",
                    "metadata": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "address": address,
                        "display_name": display_name,
                        "importance": location.raw.get('importance', 0),
                        "osm_type": location.raw.get('osm_type'),
                        "osm_id": location.raw.get('osm_id'),
                        "source": "nominatim",
                        "collected_at": datetime.utcnow().isoformat()
                    },
                    "source": "geolocation_service"
                }
                
                # Extract address components
                entities = [location_entity]
                relationships = []
                
                # Create separate entities for address components
                if 'country' in address:
                    country_entity = {
                        "value": address['country'],
                        "type": "COUNTRY",
                        "metadata": {
                            "source": address.get('country_code', '').upper(),
                            "collected_at": datetime.utcnow().isoformat()
                        },
                        "source": "geolocation_service"
                    }
                    entities.append(country_entity)
                    
                    relationships.append({
                        "type": "LOCATED_IN",
                        "source_value": display_name,
                        "source_type": "LOCATION",
                        "target_value": address['country'],
                        "target_type": "COUNTRY",
                        "metadata": {
                            "strength": 1.0
                        }
                    })
                
                if 'state' in address or 'province' in address:
                    state_name = address.get('state') or address.get('province')
                    state_entity = {
                        "value": state_name,
                        "type": "STATE",
                        "metadata": {
                            "country": address.get('country'),
                            "collected_at": datetime.utcnow().isoformat()
                        },
                        "source": "geolocation_service"
                    }
                    entities.append(state_entity)
                
                if 'city' in address or 'town' in address:
                    city_name = address.get('city') or address.get('town')
                    city_entity = {
                        "value": city_name,
                        "type": "CITY",
                        "metadata": {
                            "state": address.get('state') or address.get('province'),
                            "country": address.get('country'),
                            "collected_at": datetime.utcnow().isoformat()
                        },
                        "source": "geolocation_service"
                    }
                    entities.append(city_entity)
                
                return {
                    "entities": entities,
                    "relationships": relationships,
                    "metadata": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "address": address,
                        "service": "nominatim"
                    }
                }
            
        except Exception as e:
            self.logger.error(f"Error in reverse geocoding: {e}")
        
        return None
    
    async def forward_geocode(self, address: str) -> Optional[Dict[str, Any]]:
        """Convert address to coordinates"""
        try:
            self.logger.debug(f"Geocoding address: {address}")
            
            location = self.geolocator.geocode(address, language='en')
            
            if location:
                address = location.raw.get('address', {})
                display_name = location.raw.get('display_name', '')
                
                location_entity = {
                    "value": display_name,
                    "type": "LOCATION",
                    "metadata": {
                        "latitude": location.latitude,
                        "longitude": location.longitude,
                        "address": address,
                        "display_name": display_name,
                        "search_query": address,
                        "importance": location.raw.get('importance', 0),
                        "osm_type": location.raw.get('osm_type'),
                        "osm_id": location.raw.get('osm_id'),
                        "source": "nominatim",
                        "collected_at": datetime.utcnow().isoformat()
                    },
                    "source": "geolocation_service"
                }
                
                return {
                    "entities": [location_entity],
                    "relationships": [],
                    "metadata": {
                        "latitude": location.latitude,
                        "longitude": location.longitude,
                        "address": address,
                        "found_matches": 1,
                        "confidence": location.raw.get('importance', 0)
                    }
                }
            
        except Exception as e:
            self.logger.error(f"Error in forward geocoding: {e}")
        
        return None
    
    async def search_location(self, query: str) -> Dict[str, Any]:
        """Search for location by name or business"""
        results = {
            "entities": [],
            "relationships": [],
            "metadata": {
                "query": query,
                "results_found": 0
            }
        }
        
        try:
            self.logger.debug(f"Searching location: {query}")
            
            # Use geolocator search
            locations = self.geolocator.geocode(query, exactly_one=False, limit=10, language='en')
            
            if locations:
                entities = []
                
                for i, location in enumerate(locations):
                    address = location.raw.get('address', {})
                    display_name = location.raw.get('display_name', '')
                    
                    location_entity = {
                        "value": display_name,
                        "type": "LOCATION",
                        "metadata": {
                            "latitude": location.latitude,
                            "longitude": location.longitude,
                            "address": address,
                            "search_rank": i + 1,
                            "importance": location.raw.get('importance', 0),
                            "osm_type": location.raw.get('osm_type'),
                            "osm_id": location.raw.get('osm_id'),
                            "source": "nominatim",
                            "collected_at": datetime.utcnow().isoformat()
                        },
                        "source": "geolocation_service"
                    }
                    
                    entities.append(location_entity)
                
                results["entities"] = entities
                results["metadata"]["results_found"] = len(entities)
        
        except Exception as e:
            self.logger.error(f"Error searching location: {e}")
        
        return results
    
    async def get_nearby_businesses(self, latitude: float, longitude: float, radius: int = 1000) -> Dict[str, Any]:
        """Get businesses near coordinates"""
        results = {
            "entities": [],
            "metadata": {
                "center": {"lat": latitude, "lon": longitude},
                "radius_meters": radius,
                "businesses_found": 0
            }
        }
        
        try:
            self.logger.debug(f"Finding businesses near {latitude}, {longitude} within {radius}m")
            
            # This would use OSMnx or Overpass API for nearby business search
            # For now, we'll use a simplified approach
            
            # Use Nominatim's search with proximity bias
            search_query = f"business near {latitude},{longitude}"
            
            # In a full implementation, would use Overpass API or similar
            # to query OpenStreetMap for nearby businesses
            
            # For demonstration, create some sample business entities
            # that would be found in this area
            business_categories = [
                "restaurant", "cafe", "hotel", "shop", "bank", 
                "pharmacy", "hospital", "school", "office"
            ]
            
            # Note: Real implementation would query OSM data
            self.logger.debug("Would query OpenStreetMap for nearby businesses")
            
            # Create relationship entities for area
            area_entity = {
                "value": f"AREA_{latitude:.4f}_{longitude:.4f}",
                "type": "GEOGRAPHIC_AREA",
                "metadata": {
                    "center_lat": latitude,
                    "center_lon": longitude,
                    "radius_meters": radius,
                    "source": "geofence",
                    "collected_at": datetime.utcnow().isoformat()
                },
                "source": "geolocation_service"
            }
            
            results["entities"].append(area_entity)
            results["metadata"]["businesses_found"] = 0  # Would be populated by real query
        
        except Exception as e:
            self.logger.error(f"Error finding nearby businesses: {e}")
        
        return results
    
    async def extract_location_relationships(self, location_entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract geographic relationships between locations"""
        relationships = []
        
        try:
            self.logger.debug("Extracting location relationships")
            
            # Extract locations with coordinates
            locations = []
            for entity in location_entities:
                if entity.get("type") == "LOCATION" and "latitude" in entity.get("metadata", {}):
                    locations.append({
                        "value": entity["value"],
                        "lat": entity["metadata"]["latitude"],
                        "lon": entity["metadata"]["longitude"],
                        "metadata": entity.get("metadata", {})
                    })
            
            # Calculate geographic relationships
            for i, loc1 in enumerate(locations):
                for j, loc2 in enumerate(locations):
                    if i >= j:
                        continue
                    
                    # Calculate distance
                    coords_1 = (loc1["lat"], loc1["lon"])
                    coords_2 = (loc2["lat"], loc2["lon"])
                    
                    distance_km = geodesic(coords_1, coords_2).kilometers
                    
                    # Create proximity-based relationship
                    if distance_km < 1:
                        relationship_type = "VERY_CLOSE_TO"
                        strength = 1.0
                    elif distance_km < 5:
                        relationship_type = "CLOSE_TO"
                        strength = 0.8
                    elif distance_km < 25:
                        relationship_type = "NEAR_TO"
                        strength = 0.6
                    elif distance_km < 100:
                        relationship_type = "IN_REGION_OF"
                        strength = 0.4
                    else:
                        relationship_type = "DISTANT_FROM"
                        strength = 0.2
                    
                    relationship = {
                        "type": relationship_type,
                        "source_value": loc1["value"],
                        "source_type": "LOCATION",
                        "target_value": loc2["value"],
                        "target_type": "LOCATION",
                        "metadata": {
                            "distance_km": distance_km,
                            "strength": strength,
                            "relationship": "geographic_proximity"
                        }
                    }
                    
                    relationships.append(relationship)
            
            self.logger.debug(f"Found {len(relationships)} geographic relationships")
        
        except Exception as e:
            self.logger.error(f"Error extracting location relationships: {e}")
        
        return {
            "relationships": relationships,
            "metadata": {
                "relationship_count": len(relationships)
            }
        }
    
    def normalize(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize geolocation collection results"""
        entities = []
        
        if isinstance(data, dict):
            if "entities" in data:
                # Already normalized format
                return data["entities"]
            
            # Handle direct entity data
            target = data.get("target", self.config.target)
            if target:
                entities.append({
                    "value": target,
                    "type": "LOCATION",
                    "metadata": data.get("metadata", {}),
                    "source": data.get("source", "geo_collector")
                })
        
        return entities