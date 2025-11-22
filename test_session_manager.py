import unittest
import sys
import os
import shutil
import tempfile
import json

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from session_manager import SessionManager

class TestSessionManager(unittest.TestCase):

    def setUp(self):
        # Create a specific temp folder for these tests
        self.test_dir = tempfile.mkdtemp()
        self.manager = SessionManager(storage_dir=self.test_dir)

    def tearDown(self):
        # Cleanup temp folder
        shutil.rmtree(self.test_dir)

    def test_save_and_load_cycle(self):
        """
        Test the full save -> load lifecycle to ensure data integrity.
        """
        # 1. Create Mock Session Data
        session_name = "Test_Session_001"
        params = {"buffer": 50, "units": "miles"}
        compliance_data = {"status": "Failed", "count": 5}
        gis_results = [{"id": 101, "name": "Tract A"}] # Simplified list of dicts
        user = "test_user"

        # 2. Save
        saved_path = self.manager.save(session_name, params, gis_results, compliance_data, user)
        self.assertTrue(os.path.exists(saved_path), "Saved file should exist on disk")

        # 3. Load
        loaded = self.manager.load(session_name)

        # 4. Verify Content
        self.assertEqual(loaded['meta']['created_by'], user)
        self.assertEqual(loaded['parameters']['buffer'], 50)
        self.assertEqual(loaded['compliance_report']['status'], "Failed")
        
        print("✅ Session Manager Test Passed")

if __name__ == '__main__':
    unittest.main()