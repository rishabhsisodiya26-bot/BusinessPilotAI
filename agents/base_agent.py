import os
import time
import sqlite3
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class BaseAgent:
    def __init__(self, name: str, role_description: str, db_path: str = "./database/database.db"):
        self.name = name
        self.role_description = role_description
        self.db_path = db_path
        
        # Check for API key in environment
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def set_api_key(self, api_key: str):
        """Allows dynamic setting of API key from UI Settings."""
        self.api_key = api_key
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None

    def log_agent_execution(self, session_id: str, query: str, response: str, latency: float):
        """Log agent activities into the SQLite database."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO agent_logs (session_id, agent_name, input_query, output_response, latency_seconds)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, self.name, query, response, latency))
            conn.commit()
        except Exception as e:
            print(f"Failed to write agent log: {e}")
        finally:
            conn.close()

    def query_llm(self, prompt: str, system_prompt: str) -> str:
        """
        Sends the prompt to OpenAI API if available.
        Otherwise returns None (signals to caller to run local fallback).
        """
        if not self.client:
            return None
            
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API Call failed: {e}. Falling back to Local Intelligence Engine.")
            return None
