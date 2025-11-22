import requests
import json
import urllib.parse

class ArcGISClient:
    """
    A lightweight client for querying ArcGIS Feature Services and returning GeoJSON.
    """

    def __init__(self, service_url):
        self.base_url = service_url.rstrip('/')
        self.query_url = f"{self.base_url}/query"
        self.session = requests.Session()

    def query(self, where="1=1", out_fields="*", geometry_params=None):
        all_features = []
        offset = 0
        record_count = 1000 
        
        print(f"Querying: {where}...")

        while True:
            params = {
                'where': where,
                'outFields': out_fields,
                'f': 'geojson',
                'resultOffset': offset,
                'resultRecordCount': record_count,
                'outSR': 4326,
            }

            if geometry_params:
                params.update(geometry_params)

            try:
                response = self.session.get(self.query_url, params=params)
                response.raise_for_status()
                data = response.json()

                if 'error' in data:
                    raise Exception(f"ArcGIS API Error: {data['error'].get('message', 'Unknown error')}")

                current_features = data.get('features', [])
                if not current_features:
                    break

                all_features.extend(current_features)
                
                if len(current_features) < record_count:
                    break

                offset += record_count
                print(f"  ...fetched {len(all_features)} features so far...")

            except requests.exceptions.RequestException as e:
                print(f"HTTP Request failed: {e}")
                raise
            except json.JSONDecodeError:
                print("Failed to decode JSON response")
                raise

        return {
            "type": "FeatureCollection",
            "features": all_features
        }

    def query_nearby(self, point, distance_miles, where="1=1"):
        lon, lat = point
        geometry_params = {
            'geometry': f"{lon},{lat}",
            'geometryType': 'esriGeometryPoint',
            'inSR': 4326,
            'spatialRel': 'esriSpatialRelIntersects',
            'distance': distance_miles,
            'units': 'esriSRUnit_StatuteMile'
        }
        return self.query(where=where, geometry_params=geometry_params)

# --- usage demonstration ---
if __name__ == "__main__":
    SERVICE_URL = "https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/USA_Census_Counties/FeatureServer/0"
    client = ArcGISClient(SERVICE_URL)

    # --- 1. Perform the Query ---
    print("\n--- Querying: 50 miles from Austin ---")
    austin_coords = (-97.7431, 30.2672)
    
    # Get the data into a variable
    nearby_results = client.query_nearby(
        point=austin_coords, 
        distance_miles=50
    )
    
    print(f"Found {len(nearby_results['features'])} counties.")

    # --- 2. Save to File (The New Part) ---
    output_filename = "austin_counties.geojson"
    
    print(f"\nSaving data to {output_filename}...")
    
    # This block opens a file in 'write' mode ('w')
    with open(output_filename, "w") as f:
        # json.dump writes the python dictionary into the file as text
        json.dump(nearby_results, f, indent=2)
        
    print("Success! File saved.")