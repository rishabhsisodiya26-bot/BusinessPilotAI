-- Database Schema for BusinessPilotAI
-- Target Database: SQLite3
-- Normalized Design supporting User Auth, Multi-tenant Company profiles, Inventory, Sales, Customers, Orders, and Agent / ML Logs.

PRAGMA foreign_keys = ON;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Administrator', 'Manager', 'Analyst')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Companies Table
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    industry TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Products Table
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_cost REAL NOT NULL CHECK(unit_cost >= 0),
    unit_price REAL NOT NULL CHECK(unit_price >= 0),
    current_stock INTEGER NOT NULL DEFAULT 0 CHECK(current_stock >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 4. Customers Table
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    tenure_months INTEGER NOT NULL DEFAULT 0,
    total_spend REAL NOT NULL DEFAULT 0.0 CHECK(total_spend >= 0),
    status TEXT NOT NULL CHECK(status IN ('Active', 'Churned')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 5. Sales Table (Historical aggregates for time-series forecasting)
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    date TEXT NOT NULL, -- Format: YYYY-MM-DD
    revenue REAL NOT NULL CHECK(revenue >= 0),
    orders_count INTEGER NOT NULL CHECK(orders_count >= 0),
    inventory_level INTEGER NOT NULL CHECK(inventory_level >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 6. Orders Table (Detailed transactional logs)
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    order_date TEXT NOT NULL, -- Format: YYYY-MM-DD
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    total_price REAL NOT NULL CHECK(total_price >= 0),
    status TEXT NOT NULL CHECK(status IN ('Completed', 'Returned', 'Pending')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 7. Inventory Transactions Table
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    stock_level INTEGER NOT NULL CHECK(stock_level >= 0),
    reorder_point INTEGER NOT NULL DEFAULT 10 CHECK(reorder_point >= 0),
    last_restocked TEXT, -- Format: YYYY-MM-DD
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- 8. Machine Learning Predictions Table
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    target_type TEXT NOT NULL CHECK(target_type IN ('sales_forecast', 'customer_churn', 'segmentation', 'anomaly')),
    source_id INTEGER, -- Links to user, customer, product, or sales record depending on type
    predicted_value TEXT NOT NULL, -- JSON string or raw text (e.g. class, value, cluster, anomaly score)
    probability REAL, -- Churn risk score or confidence
    metrics_json TEXT, -- Accuracy, Precision, Recall, MSE, etc. for evaluation tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 9. Reports Table
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    report_type TEXT NOT NULL CHECK(report_type IN ('Executive Summary', 'Business Performance', 'Prediction Analysis')),
    file_path TEXT NOT NULL,
    content_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 10. Agent Execution Logs
CREATE TABLE IF NOT EXISTS agent_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    input_query TEXT NOT NULL,
    output_response TEXT NOT NULL,
    latency_seconds REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
