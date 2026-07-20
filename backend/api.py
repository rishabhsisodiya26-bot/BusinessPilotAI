import sqlite3
import os
import json
import pandas as pd
from datetime import datetime

DB_PATH = os.path.join(".", "database", "database.db")

class BusinessService:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_dashboard_kpis(self, company_id: int = 1) -> dict:
        """
        Calculates and returns main dashboard KPIs.
        """
        conn = self._get_connection()
        kpis = {
            "total_revenue": 0.0,
            "total_orders": 0,
            "total_customers": 0,
            "active_inventory": 0,
            "revenue_change_pct": 0.0,
            "orders_change_pct": 0.0
        }
        
        try:
            cursor = conn.cursor()
            
            # 1. Total Revenue & Orders
            cursor.execute("""
                SELECT SUM(revenue), SUM(orders_count) 
                FROM sales 
                WHERE company_id = ?
            """, (company_id,))
            rev, ords = cursor.fetchone()
            kpis["total_revenue"] = float(rev) if rev else 0.0
            kpis["total_orders"] = int(ords) if ords else 0
            
            # 2. Customer counts
            cursor.execute("SELECT COUNT(*) FROM customers WHERE company_id = ?", (company_id,))
            kpis["total_customers"] = cursor.fetchone()[0]
            
            # 3. Active inventory stock
            cursor.execute("SELECT SUM(current_stock) FROM products WHERE company_id = ?", (company_id,))
            kpis["active_inventory"] = cursor.fetchone()[0] or 0
            
            # 4. Period changes (Compare last 30 days vs previous 30 days)
            sales_df = pd.read_sql_query("""
                SELECT date, revenue, orders_count 
                FROM sales 
                WHERE company_id = ? 
                ORDER BY date DESC
            """, conn, params=(company_id,))
            
            if len(sales_df) >= 60:
                recent_rev = sales_df.iloc[:30]['revenue'].sum()
                prev_rev = sales_df.iloc[30:60]['revenue'].sum()
                kpis["revenue_change_pct"] = ((recent_rev - prev_rev) / prev_rev * 100) if prev_rev > 0 else 0.0
                
                recent_ords = sales_df.iloc[:30]['orders_count'].sum()
                prev_ords = sales_df.iloc[30:60]['orders_count'].sum()
                kpis["orders_change_pct"] = ((recent_ords - prev_ords) / prev_ords * 100) if prev_ords > 0 else 0.0
                
        except Exception as e:
            print(f"Error loading dashboard KPIs: {e}")
        finally:
            conn.close()
            
        return kpis

    def get_sales_chart_data(self, company_id: int = 1, limit: int = 180) -> pd.DataFrame:
        """Retrieves sales aggregate records for visualization."""
        conn = self._get_connection()
        try:
            df = pd.read_sql_query("""
                SELECT date as Date, revenue as Revenue, orders_count as OrdersCount, inventory_level as InventoryLevel
                FROM sales 
                WHERE company_id = ? 
                ORDER BY date DESC 
                LIMIT ?
            """, conn, params=(company_id, limit))
            # Return chronologically
            return df.iloc[::-1].reset_index(drop=True)
        except Exception as e:
            print(f"Error loading sales chart data: {e}")
            return pd.DataFrame()
        finally:
            conn.close()

    def get_inventory_alerts(self, company_id: int = 1) -> list:
        """Lists products that are at or below reorder threshold."""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.name, p.category, p.current_stock, i.reorder_point 
                FROM products p
                JOIN inventory i ON p.id = i.product_id
                WHERE p.company_id = ? AND p.current_stock <= i.reorder_point
            """, (company_id,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error loading inventory alerts: {e}")
            return []
        finally:
            conn.close()

    def get_predictions_by_type(self, company_id: int = 1, target_type: str = 'sales_forecast') -> list:
        """Retrieves prediction runs of a specific ML model type."""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, target_type, source_id, predicted_value, probability, metrics_json, created_at
                FROM predictions
                WHERE company_id = ? AND target_type = ?
            """, (company_id, target_type))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error retrieving predictions: {e}")
            return []
        finally:
            conn.close()

    def save_report_meta(self, company_id: int, name: str, report_type: str, file_path: str, summary: str):
        """Saves generated report pathways into the database."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO reports (company_id, name, report_type, file_path, content_summary)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, name, report_type, file_path, summary))
            conn.commit()
        except Exception as e:
            print(f"Error saving report metadata: {e}")
            conn.rollback()
        finally:
            conn.close()

    def get_saved_reports(self, company_id: int = 1) -> list:
        """Retrieves list of generated reports."""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, report_type, file_path, content_summary, created_at 
                FROM reports 
                WHERE company_id = ? 
                ORDER BY created_at DESC
            """, (company_id,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error loading reports list: {e}")
            return []
        finally:
            conn.close()

    def get_agent_audit_logs(self) -> list:
        """Retrieves step-by-step logs of multi-agent conversations."""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, agent_name, input_query, output_response, latency_seconds, created_at
                FROM agent_logs
                ORDER BY created_at DESC
                LIMIT 50
            """)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error loading agent audit logs: {e}")
            return []
        finally:
            conn.close()

    def import_cleaned_dataset(self, company_id: int, data_type: str, df: pd.DataFrame) -> tuple:
        """
        Saves user-uploaded and cleaned data into appropriate database tables.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if data_type == "Sales":
                # Expect columns: Date, Revenue, OrdersCount, InventoryLevel
                # Drop rows for the dates already present in the database to prevent duplicate keys
                dates = tuple(df['Date'].dt.strftime("%Y-%m-%d").tolist())
                if dates:
                    placeholders = ','.join('?' for _ in dates)
                    cursor.execute(f"DELETE FROM sales WHERE company_id = ? AND date IN ({placeholders})", (company_id, *dates))
                
                sales_data = []
                for _, row in df.iterrows():
                    sales_data.append((
                        company_id,
                        row['Date'].strftime("%Y-%m-%d"),
                        float(row['Revenue']),
                        int(row['OrdersCount']),
                        int(row['InventoryLevel'])
                    ))
                cursor.executemany("""
                    INSERT INTO sales (company_id, date, revenue, orders_count, inventory_level)
                    VALUES (?, ?, ?, ?, ?)
                """, sales_data)
                
            elif data_type == "Customers":
                # Expect columns: CustomerName, Email, TenureMonths, TotalSpend, Status
                # Upsert by Email
                for _, row in df.iterrows():
                    cursor.execute("SELECT id FROM customers WHERE company_id = ? AND email = ?", (company_id, row['Email']))
                    exists = cursor.fetchone()
                    if exists:
                        cursor.execute("""
                            UPDATE customers 
                            SET name = ?, tenure_months = ?, total_spend = ?, status = ?
                            WHERE id = ?
                        """, (row['CustomerName'], int(row['TenureMonths']), float(row['TotalSpend']), row['Status'], exists[0]))
                    else:
                        cursor.execute("""
                            INSERT INTO customers (company_id, name, email, tenure_months, total_spend, status)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (company_id, row['CustomerName'], row['Email'], int(row['TenureMonths']), float(row['TotalSpend']), row['Status']))
                        
            elif data_type == "Inventory":
                # Expect columns: ProductName, Category, UnitCost, UnitPrice, CurrentStock
                for _, row in df.iterrows():
                    cursor.execute("SELECT id FROM products WHERE company_id = ? AND name = ?", (company_id, row['ProductName']))
                    exists = cursor.fetchone()
                    if exists:
                        prod_id = exists[0]
                        cursor.execute("""
                            UPDATE products 
                            SET category = ?, unit_cost = ?, unit_price = ?, current_stock = ?
                            WHERE id = ?
                        """, (row['Category'], float(row['UnitCost']), float(row['UnitPrice']), int(row['CurrentStock']), prod_id))
                    else:
                        cursor.execute("""
                            INSERT INTO products (company_id, name, category, unit_cost, unit_price, current_stock)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (company_id, row['ProductName'], row['Category'], float(row['UnitCost']), float(row['UnitPrice']), int(row['CurrentStock'])))
                        prod_id = cursor.lastrowid
                        # Seed inventory configuration
                        cursor.execute("""
                            INSERT INTO inventory (product_id, stock_level, reorder_point, last_restocked)
                            VALUES (?, ?, 10, ?)
                        """, (prod_id, datetime.now().strftime("%Y-%m-%d")))
                        
            conn.commit()
            return True, f"Successfully imported {len(df)} {data_type} records."
        except Exception as e:
            conn.rollback()
            return False, f"Failed to import data: {str(e)}"
        finally:
            conn.close()
