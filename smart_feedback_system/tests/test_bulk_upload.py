import os
import sys
import unittest
import io

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app import app

class TestBulkUpload(unittest.TestCase):
    def test_csv_upload_endpoint(self):
        client = app.test_client()
        csv_content = """feedback
"The lab computer was not working and I couldn't complete my assignment."
"Sir, portal open nahi ho raha hai aur kal assignment submission hai."
"Excellent teaching and clear explanations."
"""
        data = {
            'file': (io.BytesIO(csv_content.encode('utf-8')), 'test.csv')
        }
        response = client.post('/api/upload-csv', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        res_json = response.get_json()
        self.assertEqual(res_json['summary']['total_processed'], 3)
        self.assertGreaterEqual(res_json['summary']['negative'], 2)
        self.assertGreaterEqual(res_json['summary']['positive'], 1)

if __name__ == "__main__":
    unittest.main()
