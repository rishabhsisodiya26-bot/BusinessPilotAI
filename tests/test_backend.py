import unittest
import sqlite3
import os
import sys

# Ensure project root is in import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.auth import AuthService
from backend.api import BusinessService

class TestBackendService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use a temporary test database
        cls.db_path = "./database/test_database.db"
        cls.schema_path = "./database/schema.sql"
        
        # Create test DB and apply schema
        conn = sqlite3.connect(cls.db_path)
        with open(cls.schema_path, "r") as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
        
        cls.auth = AuthService(db_path=cls.db_path)
        cls.biz = BusinessService(db_path=cls.db_path)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def test_01_registration_and_login(self):
        # Register user
        success, msg = self.auth.register_user("testuser", "test@example.com", "pass123", "Analyst")
        self.assertTrue(success)
        self.assertEqual(msg, "User registered successfully.")
        
        # Register duplicate
        success, msg = self.auth.register_user("testuser", "test@example.com", "pass123", "Analyst")
        self.assertFalse(success)
        
        # Valid login
        ok, user = self.auth.login_user("testuser", "pass123")
        self.assertTrue(ok)
        self.assertEqual(user["username"], "testuser")
        self.assertEqual(user["role"], "Analyst")
        self.assertIsNotNone(user["company"])
        
        # Invalid password login
        ok, msg = self.auth.login_user("testuser", "wrongpass")
        self.assertFalse(ok)
        self.assertEqual(msg, "Invalid username or password.")

    def test_02_company_kpis_empty(self):
        # Test KPIs for empty company database
        kpis = self.biz.get_dashboard_kpis(company_id=1)
        self.assertEqual(kpis["total_revenue"], 0.0)
        self.assertEqual(kpis["total_orders"], 0)
        self.assertEqual(kpis["total_customers"], 0)
