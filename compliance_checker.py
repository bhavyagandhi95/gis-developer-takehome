import geopandas as gpd
import json
import os

# specific conversion constants
SQ_METERS_TO_SQ_MILES = 1 / 2589988.11

def load_and_process_geojson(filepath):
    """
    Loads GeoJSON, projects it to a metric CRS, and calculates area.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Could not find file: {filepath}")

    # 1. Read the GeoJSON file
    gdf = gpd.read_file(filepath)

    # 2. Project to an Equal Area CRS for accurate measurement.
    # GeoJSON is typically WGS84 (Lat/Lon). We cannot calculate area in degrees.
    gdf_projected = gdf.to_crs(epsg=3081)

    # 3. Calculate Area dynamically based on the polygon geometry
    # Result is in square meters (because EPSG:3081 is in meters)
    gdf_projected['calculated_sq_meters'] = gdf_projected.geometry.area
    
    # 4. Convert to Square Miles
    gdf_projected['area_sqmi'] = gdf_projected['calculated_sq_meters'] * SQ_METERS_TO_SQ_MILES
    
    # Return only the columns we need for the business logic, dropping the heavy geometry
    name_col = 'NAME' if 'NAME' in gdf_projected.columns else gdf_projected.columns[0]
    
    return gdf_projected[[name_col, 'area_sqmi']].rename(columns={name_col: 'name'})

def generate_recommendation(shortfall):
    """
    Business Logic: Generates advice based on shortfall severity.
    """
    if shortfall > 2000:
        return "CRITICAL: Requires major consolidation."
    elif shortfall > 1000:
        return "WARNING: Seek waiver or combine with neighbor."
    else:
        return "NOTICE: Minor boundary adjustment required."

def run_compliance_check(geojson_path, threshold_sqmi=2500):
    """
    Main function to process GIS file against business rules.
    """
    # 1. Load and process the real GIS data
    try:
        df = load_and_process_geojson(geojson_path)
    except Exception as e:
        return {"error": str(e)}

    # 2. Apply Business Logic (Vectorized)
    df['is_compliant'] = df['area_sqmi'] >= threshold_sqmi
    
    # 3. Filter for Non-Compliance
    non_compliant = df[~df['is_compliant']].copy()
    
    # 4. Calculate Shortfall
    non_compliant['required_sqmi'] = threshold_sqmi
    non_compliant['shortfall_sqmi'] = non_compliant['required_sqmi'] - non_compliant['area_sqmi']
    
    # 5. Apply Recommendation Engine
    non_compliant['recommendation'] = non_compliant['shortfall_sqmi'].apply(generate_recommendation)
    
    # 6. Rank by Shortfall (Largest gap first)
    non_compliant = non_compliant.sort_values(by='shortfall_sqmi', ascending=False)
    
    # Round floats for cleaner JSON output
    non_compliant['area_sqmi'] = non_compliant['area_sqmi'].round(2)
    non_compliant['shortfall_sqmi'] = non_compliant['shortfall_sqmi'].round(2)

    # 7. Construct Structured Output
    result_payload = {
        "meta": {
            "report_type": "GIS Compliance Check",
            "source_file": geojson_path,
            "rule": f"Minimum {threshold_sqmi} sq mi"
        },
        "statistics": {
            "total_features_checked": int(len(df)),
            "non_compliant_count": int(len(non_compliant))
        },
        "non_compliant_regions": non_compliant.to_dict(orient="records")
    }
    
    return result_payload

if __name__ == "__main__":
    # provide geojson file path below <<--
    file_path = r"D:\Python\austin_counties.geojson"
    
    # Create a dummy file for demonstration if it doesn't exist
    if not os.path.exists(file_path):
        print(f"File {file_path} not found")
    else:
        results = run_compliance_check(file_path)
        print(json.dumps(results, indent=4))