import unittest
import os
import sys
import sqlite3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.ceo_agent import CEOAgent
from agents.analyst_agent import AnalystAgent
from agents.prediction_agent import PredictionAgent
from agents.advisor_agent import AdvisorAgent

class TestAgentSystems(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use database seeded during Phase 3 since we need real numbers to verify agent metrics lookup!
        cls.db_path = "./database/database.db"
        cls.ceo = CEOAgent(db_path=cls.db_path)
        cls.analyst = AnalystAgent(db_path=cls.db_path)
        cls.predictor = PredictionAgent(db_path=cls.db_path)
        cls.advisor = AdvisorAgent(db_path=cls.db_path)

    def test_01_analyst_agent(self):
        report = self.analyst.analyze_business_data(session_id="test_sess_agent", company_id=1)
        self.assertIn("Exploratory Data Analysis", report)
        self.assertIn("Gross Revenue", report)

    def test_02_predictor_agent(self):
        # Predictions are already cached from our Phase 5 run!
        report = self.predictor.generate_prediction_summary(session_id="test_sess_agent", company_id=1)
        self.assertIn("Machine Learning Modules", report)
        self.assertIn("Sales & Demand Forecasting", report)

    def test_03_advisor_agent(self):
        report = self.advisor.generate_strategy_report(session_id="test_sess_agent", company_id=1)
        self.assertIn("Executive Strategic Advisory Report", report)
        self.assertIn("SWOT Analysis", report)

    def test_04_ceo_agent_workflow(self):
        result = self.ceo.execute_workflow("What is the sales trend?", company_id=1)
        self.assertIsNotNone(result["session_id"])
        self.assertIn("executive_summary", result)
        self.assertTrue(result["total_latency"] > 0)
