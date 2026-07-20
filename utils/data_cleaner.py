import pandas as pd
import numpy as np

class DataCleaner:
    @staticmethod
    def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans sales history datasets.
        Handles missing values, parses dates, and caps negative order counts.
        """
        # Create a copy to prevent SettingWithCopyWarning
        df = df.copy()
        
        # Parse Dates
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date').reset_index(drop=True)
            
        # Clean Revenue
        if 'Revenue' in df.columns:
            # Force numeric, turning string errors to NaN
            df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce')
            # Impute NaN with median
            median_revenue = df['Revenue'].median()
            df['Revenue'] = df['Revenue'].fillna(median_revenue)
            # Ensure no negative revenue
            df['Revenue'] = df['Revenue'].clip(lower=0)
            
        # Clean Orders Count
        if 'OrdersCount' in df.columns:
            df['OrdersCount'] = pd.to_numeric(df['OrdersCount'], errors='coerce')
            # Cap negative counts to 0 or median
            median_orders = max(0, df['OrdersCount'].median())
            df['OrdersCount'] = df['OrdersCount'].apply(lambda x: median_orders if pd.isna(x) or x < 0 else x)
            df['OrdersCount'] = df['OrdersCount'].astype(int)
            
        # Clean Inventory Level
        if 'InventoryLevel' in df.columns:
            df['InventoryLevel'] = pd.to_numeric(df['InventoryLevel'], errors='coerce')
            median_inv = df['InventoryLevel'].median()
            df['InventoryLevel'] = df['InventoryLevel'].fillna(median_inv).clip(lower=0).astype(int)
            
        return df

    @staticmethod
    def clean_customer_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans customer behavior datasets.
        Handles email missing values, normalizes status strings, and cleans numeric fields.
        """
        df = df.copy()
        
        # Customer Name
        if 'CustomerName' in df.columns:
            df['CustomerName'] = df['CustomerName'].fillna("Unknown Customer").str.strip()
            
        # Email
        if 'Email' in df.columns:
            df['Email'] = df['Email'].fillna("no-email@example.com").str.strip().str.lower()
            
        # Tenure
        if 'TenureMonths' in df.columns:
            df['TenureMonths'] = pd.to_numeric(df['TenureMonths'], errors='coerce')
            median_tenure = max(0, df['TenureMonths'].median())
            df['TenureMonths'] = df['TenureMonths'].fillna(median_tenure).clip(lower=0).astype(int)
            
        # Spend
        if 'TotalSpend' in df.columns:
            df['TotalSpend'] = pd.to_numeric(df['TotalSpend'], errors='coerce')
            median_spend = df['TotalSpend'].median()
            df['TotalSpend'] = df['TotalSpend'].fillna(median_spend).clip(lower=0)
            
        # Status
        if 'Status' in df.columns:
            # Capitalize to match 'Active' / 'Churned'
            df['Status'] = df['Status'].fillna("Active").str.strip().str.capitalize()
            # Ensure it fits our exact ENUM values
            df['Status'] = df['Status'].apply(lambda x: x if x in ['Active', 'Churned'] else 'Active')
            
        return df

    @staticmethod
    def clean_inventory_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans product inventory datasets.
        """
        df = df.copy()
        
        if 'ProductName' in df.columns:
            df['ProductName'] = df['ProductName'].fillna("Unnamed Product").str.strip()
            
        if 'Category' in df.columns:
            df['Category'] = df['Category'].fillna("General").str.strip()
            
        for numeric_col in ['UnitCost', 'UnitPrice', 'CurrentStock']:
            if numeric_col in df.columns:
                df[numeric_col] = pd.to_numeric(df[numeric_col], errors='coerce')
                median_val = df[numeric_col].median()
                df[numeric_col] = df[numeric_col].fillna(median_val).clip(lower=0)
                if numeric_col == 'CurrentStock':
                    df[numeric_col] = df[numeric_col].astype(int)
                    
        return df
