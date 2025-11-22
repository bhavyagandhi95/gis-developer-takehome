import unittest
import json
import os
import shutil
import tempfile
import pandas as pd
from unittest.mock import MagicMock, patch

# Import your modules
# Ensure arcgis_client.py, compliance_checker.py, and session_manager.py are in the same folder
from arcgis_client import ArcGISClient
from compliance_checker import run_compliance_check, generate_recommendation
from session_manager import SessionManager

class TestGISWorkflow(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for saving session files during tests
        self.test_dir = tempfile.mkdtemp()
        self.session_manager = SessionManager(storage_dir=self.test_dir)

    def tearDown(self):
        # Clean up the temporary directory after tests finish
        shutil.rmtree(self.test_dir)

    # ============================================================
    # TEST 1: ArcGIS Client (Network Query)
    # ============================================================
    @patch('arcgis_client.requests.Session')
    def test_arcgis_query(self, mock_session_cls):
        """
        Tests the ArcGISClient by mocking the HTTP response so we don't 
        actually hit the internet.
        """
        # 1. Setup the Mock Response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "type": "FeatureCollection",
            "features": [
                {"type": "Feature", "properties": {"NAME": "Travis"}, "geometry": {}}
            ]
        }
        
        # Link the mock response to the session.get() call
        mock_session_instance = mock_session_cls.return_value
        mock_session_instance.get.return_value = mock_response

        # 2. Run the Code
        client = ArcGISClient("http://fake-url.com/FeatureServer/0")
        result = client.query(where="1=1")

        # 3. Assertions
        self.assertEqual(len(result['features']), 1)
        self.assertEqual(result['features'][0]['properties']['NAME'], "Travis")
        print("\n✅ Test 1 Passed: ArcGIS Client (Mocked)")

    # ============================================================
    # TEST 2: Compliance Checker (Business Logic)
    # ============================================================
    @patch('compliance_checker.load_and_process_geojson')
    def test_compliance_logic(self, mock_loader):
        """
        Tests the compliance logic by providing a fake DataFrame instead 
        of reading a real GeoJSON file.
        """
        # 1. Setup Mock Data (2 counties: 1 Pass, 1 Fail)
        mock_df = pd.DataFrame([
            {"name": "Big County", "area_sqmi": 5000.0},  # > 2500 (Pass)
            {"name": "Tiny County", "area_sqmi": 100.0}   # < 2500 (Fail)
        ])
        mock_loader.return_value = mock_df

        # 2. Run the Code
        # The filename doesn't matter because we mocked the loader
        report = run_compliance_check("dummy_file.geojson", threshold_sqmi=2500)

        # 3. Assertions
        self.assertEqual(report['statistics']['non_compliant_count'], 1)
        
        # Verify the logic calculated the shortfall correctly
        failed_item = report['non_compliant_regions'][0]
        self.assertEqual(failed_item['name'], "Tiny County")
        self.assertEqual(failed_item['shortfall_sqmi'], 2400.0) # 2500 - 100
        
        # Verify recommendation string generation
        self.assertIn("CRITICAL", failed_item['recommendation'])
        print("✅ Test 2 Passed: Compliance Logic")

    # ============================================================
    # TEST 3: Session Manager (Save/Load)
    # ============================================================
    def test_session_persistence(self):
        """
        Tests saving data to disk and loading it back.
        """
        # 1. Define Test Data
        session_name = "Unit_Test_Session"
        params = {"where": "state='TX'"}
        results = [{"name": "Test", "val": 1}]
        report = {"status": "checked"}
        user = "tester_bot"

        # 2. Save
        file_path = self.session_manager.save(session_name, params, results, report, user)
        self.assertTrue(os.path.exists(file_path), "File should exist after save")

        # 3. Load
        loaded_data = self.session_manager.load(session_name)

        # 4. Assertions
        self.assertEqual(loaded_data['meta']['created_by'], user)
        self.assertEqual(loaded_data['parameters']['where'], "state='TX'")
        print("✅ Test 3 Passed: Session Save/Load")

if __name__ == '__main__':
    unittest.main()