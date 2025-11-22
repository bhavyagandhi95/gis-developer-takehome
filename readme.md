# **ArcGIS Compliance & Session Manager**

## **Overview**

This project allows Land Analysts to query GIS feature services, analyze lease compliance against business rules (e.g., minimum acreage), and save their work sessions for later review.

## **Components**

1. **arcgis\_client.py**: Connects to ArcGIS REST APIs to fetch feature data as GeoJSON.  
2. **compliance\_checker.py**: Analyzes local GeoJSON files to find tracts smaller than 2,500 sq mi.  
3. **session\_manager.py**: Saves and loads the state of an analysis (query params, results, reports).

## **Setup Instructions**

### **1\. Install Dependencies**

Ensure you have Python 3.8+ installed. Install the required geospatial libraries:

pip install requests pandas geopandas

### **2\. Project Structure**

Ensure your folder looks like this:

/project\_folder  
   ├── arcgis\_client.py       \# (The code you provided)  
   ├── compliance\_checker.py  \# (From Part 2\)  
   ├── session\_manager.py     \# (From Part 3\)  
   ├── test\_suite.py          \# (The testing file provided below)  
   └── README.md

## **Usage Examples**

### **Step 1: Query Data (ArcGIS Client)**

from arcgis\_client import ArcGISClient

client \= ArcGISClient("\[https://services.arcgis.com/.../FeatureServer/0\](https://services.arcgis.com/.../FeatureServer/0)")  
\# Get data 50 miles around a point  
data \= client.query\_nearby((-97.74, 30.26), 50\)

### **Step 2: Run Compliance Check**

from compliance\_checker import run\_compliance\_check

\# Analyzes the file and finds counties \< 2500 sq mi  
results \= run\_compliance\_check('austin\_counties.geojson', threshold\_sqmi=2500)  
print(results\['non\_compliant\_regions'\])

### **Step 3: Save Session**

from session\_manager import SessionManager

sm \= SessionManager()  
sm.save(  
    name="Austin\_Audit",   
    query\_params={"dist": 50},   
    results=results,   
    compliance\_report=results\['non\_compliant\_regions'\],   
    user="Analyst\_1"  
)

## **Assumptions**

* **Coordinate Systems:** The compliance checker assumes input GeoJSON is WGS84 (Lat/Lon) and automatically projects it to **Texas Albers (EPSG:3081)** for accurate area calculation.  
* **ArcGIS API:** The client assumes the Feature Service supports GeoJSON output (f=geojson).  
* **File Permissions:** The script assumes it has write permissions to the local directory to save JSON sessions.