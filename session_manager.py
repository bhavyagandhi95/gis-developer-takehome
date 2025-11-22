import json
import os
import datetime
from pathlib import Path
import pandas as pd
import geopandas as gpd

class SessionManager:
    def __init__(self, storage_dir="saved_sessions"):
        """
        Initialize the session manager.
        Creates the storage directory if it doesn't exist.
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _serialize_data(self, data):
        """
        Helper to handle DataFrame/GeoDataFrame serialization for JSON.
        """
        if isinstance(data, (pd.DataFrame, gpd.GeoDataFrame)):
            # Convert DataFrame to a list of dictionaries (records)
            return data.to_dict(orient="records")
        return data

    def save(self, name, query_params, results, compliance_report, user):
        """
        Saves the current analysis state to a JSON file.
        """
        # Sanitize filename (replace spaces with underscores)
        safe_filename = f"{name.replace(' ', '_').lower()}.json"
        file_path = self.storage_dir / safe_filename

        # Construct the session payload
        session_data = {
            "meta": {
                "session_name": name,
                "created_by": user,
                "timestamp": datetime.datetime.now().isoformat(),
                "version": "1.0"
            },
            "parameters": query_params,
            # compliance_report is already a dict from previous step
            "compliance_report": compliance_report, 
            # specific GIS results (converted to list if currently a DataFrame)
            "gis_results_snapshot": self._serialize_data(results) 
        }

        try:
            with open(file_path, 'w') as f:
                json.dump(session_data, f, indent=4)
            print(f"✅ Session saved successfully: {file_path}")
            return str(file_path)
        except Exception as e:
            print(f"❌ Error saving session: {e}")
            return None

    def load(self, name):
        """
        Loads a session by name.
        """
        safe_filename = f"{name.replace(' ', '_').lower()}.json"
        file_path = self.storage_dir / safe_filename

        if not file_path.exists():
            raise FileNotFoundError(f"Session '{name}' not found at {file_path}")

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            print(f"✅ Session loaded: {data['meta']['session_name']} (from {data['meta']['timestamp']})")
            return data
        except Exception as e:
            print(f"❌ Error loading session: {e}")
            return None

    def list_sessions(self):
        """
        Returns a list of available session files.
        """
        return [f.name for f in self.storage_dir.glob("*.json")]