# tests/test_system.py
import unittest
import json
from app import app

class TestCreditDecisionSystem(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_health_check(self):
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_application_submission(self):
        application_data = {
            'full_name': 'Test User',
            'age': '35',
            'annual_income': '75000',
            'employment_years': '8',
            'loan_amount': '25000',
            'debt_to_income_ratio': '0.28',
            'credit_history_length': '12',
            'num_credit_cards': '3',
            'total_debt': '18000',
            'credit_utilization': '0.35',
            'payment_history': '0.92'
        }
        
        response = self.app.post('/api/apply', data=application_data)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('decision', data)
        self.assertIn('application_id', data)
    
    def test_metrics_endpoint(self):
        response = self.app.get('/api/metrics')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('total_applications', data)
        self.assertIn('approval_rate', data)
    
    def test_invalid_application(self):
        # Missing required fields
        response = self.app.post('/api/apply', data={'age': 'invalid'})
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()