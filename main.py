from session_manager import SessionManager
import pandas as pd

# 1. SETUP: Mocking the GIS Data & Analysis Results
# (In a real app, these come from compliance_checker.py)

# Simulated query parameters used to get the data
current_query = {
    "where_clause": "STATE_NAME = 'Texas'",
    "layer": "counties_2024",
    "min_acres": 2500
}

# Simulated raw GIS results (A DataFrame)
gis_results_df = pd.DataFrame([
    {"name": "Rockwall", "area": 147.6},
    {"name": "Dallas", "area": 908.0},
    {"name": "Harris", "area": 1777.0}
])

# Simulated Compliance Report (The output dictionary from the previous step)
compliance_output = {
    "status": "Review Required",
    "non_compliant_count": 3,
    "flagged_items": ["Rockwall", "Dallas", "Harris"]
}

# ==========================================
# 2. THE SESSION MANAGER WORKFLOW
# ==========================================

def run_demo():
    # A. Initialize Manager
    session = SessionManager(storage_dir="my_analysis_sessions")

    print("--- 1. SAVING SESSION ---")
    # B. Save the current state
    session.save(
        name="Texas Lease Audit 2024",
        query_params=current_query,
        results=gis_results_df,  # Passing the DataFrame directly
        compliance_report=compliance_output,
        user="analyst@energy-corp.com"
    )

    print("\n--- 2. SIMULATING TIME PASSING ---")
    print("... Analyst goes to lunch ...\n")

    print("--- 3. LOADING SESSION ---")
    # C. Load the session back
    restored_data = session.load("Texas Lease Audit 2024")

    if restored_data:
        # D. Verify the data
        print("\n--- RESTORED DATA INSPECTION ---")
        print(f"User: {restored_data['meta']['created_by']}")
        print(f"Query Used: {restored_data['parameters']['where_clause']}")
        
        # Check specific compliance data
        count = restored_data['compliance_report']['non_compliant_count']
        print(f"Non-Compliant Count: {count}")
        
        # Check if the DataFrame data came back (it will be a list of dicts now)
        first_county = restored_data['gis_results_snapshot'][0]['name']
        print(f"First County in Data: {first_county}")

if __name__ == "__main__":
    run_demo()