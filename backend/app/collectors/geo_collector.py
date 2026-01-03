"""
Geolocation OSINT Collector

Collects OSINT data for geolocation including:
- Reverse geocoding (coordinates to address)
- Forward geocoding (address to coordinates)
- Nearby business discovery
- Location relationship extraction
"""

import asyncio
from typing import Any, Dict, List, Optional

from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from loguru import logger

from app.collectors.base_collector import (BaseCollector, CollectionResult,
                                           CollectorConfig, DataType,
                                           RiskLevel)


class GeoCollector(BaseCollector):
    """
    Geolocation OSINT Collector

    Collects geolocation data and relationships.
    """

    def __init__(self, config: CollectorConfig):
        super().__init__(config, name="GeoCollector")

        self.geolocator = None
        self.use_osmnx = False

    async def collect(self) -> CollectionResult:
        """
        Collect OSINT data for the target location.

        Returns:
            CollectionResult with discovered entities
        """
        result = CollectionResult(
            success=False, collector_name=self.name, correlation_id=self.correlation_id
        )

        try:
            target = self.config.target

            logger.info(f"Collecting geolocation OSINT for: {target}")

            # Initialize geocoder
            await self._init_geolocator()

            # Determine if target is coordinates or address
            if self._is_coordinates(target):
                # Coordinates: lat,lon
                lat, lon = map(float, target.split(","))
                tasks = [
                    self._reverse_geocode(lat, lon),
                    self._get_nearby_businesses(lat, lon),
                ]
            else:
                # Address or place name
                tasks = [
                    self._forward_geocode(target),
                ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Aggregate results
            for i, task_result in enumerate(results):
                if isinstance(task_result, Exception):
                    logger.error(f"Task {i} failed: {task_result}")
                    result.errors.append(str(task_result))
                elif task_result:
                    result.data.extend(task_result)

            result.success = len(result.errors) == 0
            result.metadata = {
                "target": target,
                "tasks_completed": len(
                    [r for r in results if not isinstance(r, Exception)]
                ),
            }

        except Exception as e:
            logger.exception(f"Error in geolocation collection: {e}")
            result.errors.append(str(e))

        return result

    def _is_coordinates(self, target: str) -> bool:
        """Check if target is in coordinate format (lat,lon)"""
        try:
            parts = target.split(",")
            if len(parts) == 2:
                lat, lon = map(float, parts)
                return -90 <= lat <= 90 and -180 <= lon <= 180
        except Exception:
            pass
        return False

    async def _init_geolocator(self):
        """Initialize geolocator"""
        try:
            self.geolocator = Nominatim(user_agent="ReconVault-OSINT", timeout=10)
            logger.debug("Geolocator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize geolocator: {e}")

    async def _reverse_geocode(self, lat: float, lon: float) -> List[Dict[str, Any]]:
        """Get address from coordinates"""
        entities = []

        try:
            # Run blocking geocoding in thread pool
            loop = asyncio.get_event_loop()

            location = await loop.run_in_executor(
                None,
                self.geolocator.reverse,
                f"{lat},{lon}",
                None,  # language
                True,  # address details
            )

            if location:
                address_data = location.raw.get("address", {})

                entity = self._create_entity(
                    entity_type="METADATA",
                    value=f"{lat},{lon}",
                    risk_level=RiskLevel.INFO,
                    metadata={
                        "type": "location",
                        "display_name": location.address,
                        "coordinates": {"lat": lat, "lon": lon},
                        "country": address_data.get("country"),
                        "country_code": address_data.get("country_code"),
                        "state": address_data.get(
                            "state", address_data.get("province")
                        ),
                        "city": address_data.get(
                            "city",
                            address_data.get("town", address_data.get("village")),
                        ),
                        "postcode": address_data.get("postcode"),
                        "street": address_data.get("road"),
                        "house_number": address_data.get("house_number"),
                    },
                )

                entities.append(entity)

                # Create LOCATED_AT relationship
                entities.append(
                    {
                        "relationship_type": "LOCATED_AT",
                        "source": "location",
                        "target": f"{lat},{lon}",
                        "metadata": {"coordinates": {"lat": lat, "lon": lon}},
                    }
                )

                logger.info(f"Reverse geocoded {lat},{lon}: {location.address}")

        except Exception as e:
            logger.error(f"Error reverse geocoding {lat},{lon}: {e}")

        return entities

    async def _forward_geocode(self, address: str) -> List[Dict[str, Any]]:
        """Get coordinates from address"""
        entities = []

        try:
            # Run blocking geocoding in thread pool
            loop = asyncio.get_event_loop()

            location = await loop.run_in_executor(
                None,
                self.geolocator.geocode,
                address,
                None,  # country_codes
                False,  # exactly_one
            )

            if location:
                entity = self._create_entity(
                    entity_type="METADATA",
                    value=address,
                    risk_level=RiskLevel.INFO,
                    metadata={
                        "type": "location",
                        "display_name": location.address,
                        "coordinates": {
                            "lat": location.latitude,
                            "lon": location.longitude,
                        },
                        "importance": location.raw.get("importance", 0),
                    },
                )

                entities.append(entity)

                # Create LOCATED_AT relationship
                entities.append(
                    {
                        "relationship_type": "LOCATED_AT",
                        "source": address,
                        "target": f"{location.latitude},{location.longitude}",
                        "metadata": {
                            "coordinates": {
                                "lat": location.latitude,
                                "lon": location.longitude,
                            }
                        },
                    }
                )

                logger.info(
                    f"Forward geocoded '{address}': {location.latitude},{location.longitude}"
                )

        except Exception as e:
            logger.error(f"Error forward geocoding '{address}': {e}")

        return entities

    async def _get_nearby_businesses(
        self, lat: float, lon: float, radius: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get nearby businesses within radius (meters)"""
        entities = []

        try:
            # Use Overpass API (OpenStreetMap)
            overpass_url = "http://overpass-api.de/api/interpreter"

            # Overpass QL query
            bbox = (lon - 0.01, lat - 0.01, lon + 0.01, lat + 0.01)

            query = f"""
            [out:json][timeout:25];
            (
                node["shop"](around:{radius},{lat},{lon});
                node["amenity"](around:{radius},{lat},{lon});
                node["office"](around:{radius},{lat},{lon});
            );
            out;
            """

            params = {"data": query}

            try:
                response = await self.session.get(
                    overpass_url, params=params, timeout=30
                )

                if response.status_code == 200:
                    data = response.json()

                    businesses = []

                    for element in data.get("elements", []):
                        tags = element.get("tags", {})
                        business_name = tags.get(
                            "name", tags.get("shop", tags.get("amenity", "Unknown"))
                        )

                        # Calculate distance
                        if element.get("lat") and element.get("lon"):
                            coord1 = (lat, lon)
                            coord2 = (element["lat"], element["lon"])
                            distance = geodesic(coord1, coord2).meters

                            business = {
                                "name": business_name,
                                "type": tags.get(
                                    "shop", tags.get("amenity", tags.get("office"))
                                ),
                                "coordinates": {
                                    "lat": element["lat"],
                                    "lon": element["lon"],
                                },
                                "distance_meters": round(distance, 1),
                                "tags": tags,
                            }

                            businesses.append(business)

                    # Sort by distance
                    businesses.sort(key=lambda x: x["distance_meters"])

                    if businesses:
                        entities.append(
                            self._create_entity(
                                entity_type="METADATA",
                                value=f"{lat},{lon}",
                                risk_level=RiskLevel.INFO,
                                metadata={
                                    "type": "nearby_businesses",
                                    "center": {"lat": lat, "lon": lon},
                                    "radius_meters": radius,
                                    "businesses_found": len(businesses),
                                    "businesses": businesses[:20],  # Limit to 20
                                },
                            )
                        )

                        # Create ORG entities for businesses
                        for i, business in enumerate(businesses[:10]):
                            entities.append(
                                self._create_entity(
                                    entity_type="ORG",
                                    value=business["name"],
                                    risk_level=RiskLevel.INFO,
                                    metadata={
                                        "type": "business",
                                        "business_type": business["type"],
                                        "location": business["coordinates"],
                                        "distance_from_center": business[
                                            "distance_meters"
                                        ],
                                    },
                                )
                            )

                            # Create LOCATED_AT relationship
                            entities.append(
                                {
                                    "relationship_type": "LOCATED_AT",
                                    "source": business["name"],
                                    "target": f"{business['coordinates']['lat']},{business['coordinates']['lon']}",
                                    "metadata": {
                                        "distance_meters": business["distance_meters"]
                                    },
                                }
                            )

                        logger.info(f"Found {len(businesses)} nearby businesses")

            except Exception as e:
                logger.debug(f"Error querying Overpass API: {e}")

        except Exception as e:
            logger.error(f"Error getting nearby businesses: {e}")

        return entities

    async def _extract_location_relationships(
        self, locations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract relationships between locations"""
        entities = []

        try:
            # Cluster locations by proximity
            if len(locations) > 1:
                for i, loc1 in enumerate(locations):
                    for loc2 in locations[i + 1 :]:
                        try:
                            coord1 = (loc1.get("lat"), loc1.get("lon"))
                            coord2 = (loc2.get("lat"), loc2.get("lon"))

                            if all(coord1) and all(coord2):
                                distance = geodesic(coord1, coord2).kilometers

                                if distance < 10:  # Within 10 km
                                    entities.append(
                                        {
                                            "relationship_type": "NEAR",
                                            "source": loc1.get("name", str(coord1)),
                                            "target": loc2.get("name", str(coord2)),
                                            "metadata": {
                                                "distance_km": round(distance, 2)
                                            },
                                        }
                                    )

                        except Exception:
                            continue

        except Exception as e:
            logger.error(f"Error extracting location relationships: {e}")

        return entities

    def normalize(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Normalize raw geolocation data"""
        return raw_data if isinstance(raw_data, list) else []

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate normalized data"""
        if isinstance(data, dict) and "relationship_type" in data:
            return True
        required_fields = ["entity_type", "value"]
        return all(field in data for field in required_fields)
