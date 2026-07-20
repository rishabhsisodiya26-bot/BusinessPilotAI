import sqlite3
import os
import random
from datetime import datetime, timedelta
import json
import csv

# Safe password hashing fallback if bcrypt is not yet installed
try:
    import bcrypt
    def hash_password(password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
except ImportError:
    import hashlib
    def hash_password(password):
        # Fallback SHA256 hashing for seeding if bcrypt is missing
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

DB_PATH = os.path.join(".", "database", "database.db")
SCHEMA_PATH = os.path.join(".", "database", "schema.sql")
DATASETS_DIR = os.path.join(".", "datasets")

def run_schema(conn):
    print("Reading and applying schema...")
    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()

def seed_users(conn):
    print("Seeding users...")
    cursor = conn.cursor()
    # Passwords are: admin123, manager123, analyst123
    users_data = [
        ("admin", "admin@businesspilot.ai", hash_password("admin123"), "Administrator"),
        ("manager", "manager@businesspilot.ai", hash_password("manager123"), "Manager"),
        ("analyst", "analyst@businesspilot.ai", hash_password("analyst123"), "Analyst")
    ]
    cursor.executemany("""
        INSERT INTO users (username, email, password_hash, role)
        VALUES (?, ?, ?, ?)
    """, users_data)
    conn.commit()
    return cursor.lastrowid

def seed_companies(conn):
    print("Seeding companies...")
    cursor = conn.cursor()
    companies_data = [
        (1, "Apex Retail Tech", "E-commerce & Retail"),
        (2, "Nova SaaS Systems", "Technology Solutions")
    ]
    cursor.executemany("""
        INSERT INTO companies (user_id, name, industry)
        VALUES (?, ?, ?)
    """, companies_data)
    conn.commit()

def seed_products(conn):
    print("Seeding products...")
    cursor = conn.cursor()
    # Products for Apex Retail Tech (Company 1)
    products_data = [
        (1, "Pro Laptop 15", "Electronics", 800.0, 1200.0, 45),
        (1, "Wireless Headphones", "Accessories", 60.0, 110.0, 120),
        (1, "Mechanical Keyboard", "Accessories", 45.0, 85.0, 75),
        (1, "Ergonomic Office Chair", "Furniture", 120.0, 240.0, 20),
        (1, "UltraWide Monitor 34", "Electronics", 250.0, 450.0, 15),
        (1, "Smart Fitness Tracker", "Electronics", 30.0, 65.0, 110),
        (1, "Leather Messenger Bag", "Apparel", 40.0, 95.0, 30),
        (1, "Noise-Cancelling Earbuds", "Accessories", 50.0, 99.0, 80)
    ]
    cursor.executemany("""
        INSERT INTO products (company_id, name, category, unit_cost, unit_price, current_stock)
        VALUES (?, ?, ?, ?, ?, ?)
    """, products_data)
    conn.commit()

def seed_customers(conn):
    print("Seeding customers...")
    cursor = conn.cursor()
    
    first_names = ["John", "Emily", "Michael", "Sarah", "David", "Jessica", "James", "Amanda", "Robert", "Ashley", "William", "Megan", "Joseph", "Elizabeth", "Charles", "Jennifer"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas"]
    
    customers_data = []
    # Seed 60 customers for Apex Retail Tech (Company 1)
    random.seed(42) # Replicable random data
    for i in range(1, 61):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        email = f"{name.lower().replace(' ', '.')}@example.com"
        tenure = random.randint(1, 36)
        
        # High tenure and spending is less likely to churn. Lower tenure or spending is more likely to churn.
        status = "Active"
        if i % 6 == 0:
            status = "Churned"
            spend = round(random.uniform(50.0, 400.0), 2)
        else:
            spend = round(random.uniform(200.0, 5000.0), 2)
            
        customers_data.append((1, name, email, tenure, spend, status))
        
    cursor.executemany("""
        INSERT INTO customers (company_id, name, email, tenure_months, total_spend, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, customers_data)
    conn.commit()

def seed_sales_and_orders(conn):
    print("Seeding sales history and orders...")
    cursor = conn.cursor()
    
    # 365 Days history
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # Let's read products
    cursor.execute("SELECT id, unit_price, unit_cost FROM products WHERE company_id = 1")
    products = cursor.fetchall()
    
    # Let's read customers
    cursor.execute("SELECT id, status FROM customers WHERE company_id = 1")
    customers = cursor.fetchall()
    
    current_date = start_date
    sales_records = []
    order_records = []
    
    # Generate daily sales and individual orders
    random.seed(123)
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Seasonality factors: Weekly seasonality (higher sales on Friday-Sunday)
        weekday = current_date.weekday()
        weekday_factor = 1.4 if weekday in [4, 5, 6] else 0.9
        
        # Upward trend over the year
        days_from_start = (current_date - start_date).days
        trend_factor = 1.0 + (days_from_start / 365.0) * 0.4 # up to 40% growth
        
        # Random noise
        noise = random.uniform(0.8, 1.2)
        
        # Determine number of orders today (e.g. 5 to 15)
        num_orders = int(random.randint(4, 12) * weekday_factor * trend_factor)
        
        daily_revenue = 0.0
        daily_orders_count = 0
        
        for _ in range(num_orders):
            customer = random.choice(customers)
            # Active customers buy more. Churned customers only buy in their early tenure
            # If customer is churned, only buy if days_from_start is low
            if customer[1] == 'Churned' and days_from_start > 180:
                continue
                
            product = random.choice(products)
            prod_id, prod_price, prod_cost = product
            qty = random.randint(1, 3)
            total_price = prod_price * qty
            
            # Record order
            order_records.append((customer[0], prod_id, date_str, qty, total_price, "Completed"))
            daily_revenue += total_price
            daily_orders_count += 1
            
        # Daily sales aggregate
        # Simulated inventory level declining and then restocked occasionally
        inv_level = int(2000 - (days_from_start % 60) * 20 + random.randint(-50, 50))
        sales_records.append((1, date_str, round(daily_revenue, 2), daily_orders_count, max(100, inv_level)))
        
        current_date += timedelta(days=1)
        
    cursor.executemany("""
        INSERT INTO orders (customer_id, product_id, order_date, quantity, total_price, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, order_records)
    
    cursor.executemany("""
        INSERT INTO sales (company_id, date, revenue, orders_count, inventory_level)
        VALUES (?, ?, ?, ?, ?)
    """, sales_records)
    
    conn.commit()

def seed_inventory_and_logs(conn):
    print("Seeding inventory and logs...")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, current_stock FROM products")
    products = cursor.fetchall()
    
    inv_data = []
    for prod in products:
        reorder = random.choice([5, 10, 15, 20])
        inv_data.append((prod[0], prod[1], reorder, (datetime.now() - timedelta(days=random.randint(1, 15))).strftime("%Y-%m-%d")))
        
    cursor.executemany("""
        INSERT INTO inventory (product_id, stock_level, reorder_point, last_restocked)
        VALUES (?, ?, ?, ?)
    """, inv_data)
    
    # Seed a few reports
    reports_data = [
        (1, "Q2 Performance Report", "Executive Summary", "reports/q2_exec_summary.pdf", "Executive overview of Q2 sales metrics showing 15% growth."),
        (1, "Customer Health Audit", "Prediction Analysis", "reports/churn_audit_july.pdf", "Customer churn prediction summary forecasting high retention.")
    ]
    cursor.executemany("""
        INSERT INTO reports (company_id, name, report_type, file_path, content_summary)
        VALUES (?, ?, ?, ?, ?)
    """, reports_data)
    
    # Seed agent logs
    agent_logs = [
        ("sess_01", "CEOAgent", "Analyze sales performance", "Data Analyst Agent ran cleaning. ML Agent ran forecasting showing positive trend. Business Advisor Agent recommends product upsells.", 0.85),
        ("sess_01", "DataAnalystAgent", "Generate summary statistics", "Parsed 365 days of sales records. Average daily revenue is $1250.", 0.45)
    ]
    cursor.executemany("""
        INSERT INTO agent_logs (session_id, agent_name, input_query, output_response, latency_seconds)
        VALUES (?, ?, ?, ?, ?)
    """, agent_logs)
    
    conn.commit()

def export_csv_datasets(conn):
    print("Exporting raw CSV files to datasets/ directory for validation/cleaning uploads...")
    if not os.path.exists(DATASETS_DIR):
        os.makedirs(DATASETS_DIR)
        
    cursor = conn.cursor()
    
    # 1. Export raw sales
    cursor.execute("SELECT date, revenue, orders_count, inventory_level FROM sales WHERE company_id = 1")
    sales_rows = cursor.fetchall()
    sales_file = os.path.join(DATASETS_DIR, "raw_sales.csv")
    with open(sales_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Revenue", "OrdersCount", "InventoryLevel"])
        # Let's introduce some missing values/outliers for cleaning demonstration
        for i, row in enumerate(sales_rows):
            date, rev, ord_cnt, inv = row
            # Introduce a missing revenue value every 40 rows
            if i % 40 == 0:
                rev = ""
            # Introduce a negative order count outlier every 80 rows
            if i % 80 == 0:
                ord_cnt = -10
            writer.writerow([date, rev, ord_cnt, inv])
            
    # 2. Export raw customers
    cursor.execute("SELECT name, email, tenure_months, total_spend, status FROM customers WHERE company_id = 1")
    customer_rows = cursor.fetchall()
    customer_file = os.path.join(DATASETS_DIR, "raw_customers.csv")
    with open(customer_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["CustomerName", "Email", "TenureMonths", "TotalSpend", "Status"])
        for i, row in enumerate(customer_rows):
            name, email, tenure, spend, status = row
            # Introduce missing email or misspelled status occasionally
            if i % 15 == 0:
                email = ""
            if i % 25 == 0:
                status = "active" # lowercase to test normalizer
            writer.writerow([name, email, tenure, spend, status])
            
    # 3. Export raw inventory/products
    cursor.execute("SELECT name, category, unit_cost, unit_price, current_stock FROM products WHERE company_id = 1")
    product_rows = cursor.fetchall()
    inventory_file = os.path.join(DATASETS_DIR, "raw_inventory.csv")
    with open(inventory_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ProductName", "Category", "UnitCost", "UnitPrice", "CurrentStock"])
        for row in product_rows:
            writer.writerow(row)
            
    print("CSV Export Complete!")

def main():
    # Make sure parent directory database/ exists
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        
    if os.path.exists(DB_PATH):
        print(f"Removing old database at {DB_PATH}")
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    try:
        run_schema(conn)
        seed_users(conn)
        seed_companies(conn)
        seed_products(conn)
        seed_customers(conn)
        seed_sales_and_orders(conn)
        seed_inventory_and_logs(conn)
        export_csv_datasets(conn)
        print("Database seeding completed successfully!")
    except Exception as e:
        print(f"Error during seeding: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()
