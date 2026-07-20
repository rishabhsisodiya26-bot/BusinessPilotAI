import sqlite3
import os
import bcrypt

DB_PATH = os.path.join(".", "database", "database.db")

class AuthService:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def hash_password(self, password: str) -> str:
        """Hashes a password using BCrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str, hashed: str) -> bool:
        """Verifies a password against its BCrypt hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False

    def register_user(self, username: str, email: str, password: str, role: str = 'Analyst') -> tuple:
        """
        Registers a new user.
        Returns (success_boolean, message_string)
        """
        if not username or not email or not password:
            return False, "All fields (username, email, password) are required."
            
        if role not in ['Administrator', 'Manager', 'Analyst']:
            return False, "Invalid role specified."
            
        hashed_pw = self.hash_password(password)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                return False, "Username or Email already registered."
                
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            """, (username, email, hashed_pw, role))
            
            # Automatically create a default company for the new user
            user_id = cursor.lastrowid
            company_name = f"{username.capitalize()}'s Enterprise"
            cursor.execute("""
                INSERT INTO companies (user_id, name, industry)
                VALUES (?, ?, ?)
            """, (user_id, company_name, "General Business"))
            
            conn.commit()
            return True, "User registered successfully."
            
        except Exception as e:
            conn.rollback()
            return False, f"Database error during registration: {str(e)}"
        finally:
            conn.close()

    def login_user(self, username_or_email: str, password: str) -> tuple:
        """
        Authenticates a user.
        Returns (success_boolean, user_dict_or_message)
        """
        if not username_or_email or not password:
            return False, "Username/Email and Password are required."
            
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row  # Access columns by name
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, username, email, password_hash, role 
                FROM users 
                WHERE username = ? OR email = ?
            """, (username_or_email, username_or_email))
            
            user_row = cursor.fetchone()
            if not user_row:
                return False, "Invalid username or password."
                
            user_dict = dict(user_row)
            
            # Verify password
            if self.check_password(password, user_dict['password_hash']):
                # Fetch company ID associated with the user
                cursor.execute("SELECT id, name, industry FROM companies WHERE user_id = ?", (user_dict['id'],))
                company_row = cursor.fetchone()
                if company_row:
                    user_dict['company'] = dict(company_row)
                else:
                    user_dict['company'] = None
                    
                # Clean sensitive data from returned dict
                del user_dict['password_hash']
                return True, user_dict
            else:
                return False, "Invalid username or password."
                
        except Exception as e:
            return False, f"Database error during login: {str(e)}"
        finally:
            conn.close()
