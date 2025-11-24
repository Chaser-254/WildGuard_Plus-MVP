import math

class MapService:
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates in kilometers"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c

    @staticmethod
    def get_bounding_box(latitude, longitude, radius_km=10):
        """Get bounding box coordinates for a given point and radius"""
        R = 6371  # Earth's radius in kilometers
        
        # Convert radius to radians
        radius_rad = radius_km / R
        
        # Calculate latitude bounds
        min_lat = latitude - math.degrees(radius_rad)
        max_lat = latitude + math.degrees(radius_rad)
        
        # Calculate longitude bounds (adjust for latitude)
        delta_lon = math.asin(math.sin(radius_rad) / math.cos(math.radians(latitude)))
        min_lon = longitude - math.degrees(delta_lon)
        max_lon = longitude + math.degrees(delta_lon)
        
        return {
            'min_lat': min_lat,
            'max_lat': max_lat,
            'min_lon': min_lon,
            'max_lon': max_lon
        }

map_service = MapService()