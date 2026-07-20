import streamlit as st
import pandas as pd
import os
from utils.data_cleaner import DataCleaner
from backend.api import BusinessService

def show_upload_page(company_id: int):
    st.markdown("## 📥 Smart Dataset Uploader & Cleaning")
    st.markdown("Upload transactional files, analyze schema health, clean records automatically, and import directly into the database.")
    
    biz_service = BusinessService()
    
    # 1. Dataset Type Select
    data_type = st.selectbox("Choose Target Schema Category", ["Sales", "Customers", "Inventory"])
    
    # Uploader file selector
    uploaded_file = st.file_uploader(f"Upload {data_type} CSV File", type=["csv"])
    
    # Quick demo loaders
    st.markdown("💡 **Demo files available:**")
    demo_cols = st.columns(3)
    load_demo = False
    demo_file_path = ""
    
    with demo_cols[0]:
        if st.button("Load Demo Sales CSV", use_container_width=True):
            demo_file_path = "./datasets/raw_sales.csv"
            load_demo = True
            st.session_state['data_type_select'] = "Sales"
            
    with demo_cols[1]:
        if st.button("Load Demo Customers CSV", use_container_width=True):
            demo_file_path = "./datasets/raw_customers.csv"
            load_demo = True
            st.session_state['data_type_select'] = "Customers"
            
    with demo_cols[2]:
        if st.button("Load Demo Inventory CSV", use_container_width=True):
            demo_file_path = "./datasets/raw_inventory.csv"
            load_demo = True
            st.session_state['data_type_select'] = "Inventory"
            
    raw_df = None
    if uploaded_file is not None:
        try:
            raw_df = pd.read_csv(uploaded_file)
            st.success("File uploaded successfully!")
        except Exception as e:
            st.error(f"Error reading file: {e}")
            
    elif load_demo:
        if os.path.exists(demo_file_path):
            try:
                raw_df = pd.read_csv(demo_file_path)
                st.success(f"Successfully loaded {os.path.basename(demo_file_path)} from local datasets!")
            except Exception as e:
                st.error(f"Failed to read demo file: {e}")
        else:
            st.error("Demo files are missing. Please run database seeding first.")
            
    if raw_df is not None:
        st.markdown("---")
        st.subheader("🔍 Pre-Cleaning Dataset Inspection")
        
        row_count, col_count = raw_df.shape
        st.info(f"Dimensions: **{row_count} rows** by **{col_count} columns**.")
        
        # Missing values report
        missing_counts = raw_df.isnull().sum()
        has_missing = missing_counts.sum() > 0
        
        col_summary, col_table = st.columns([1, 2])
        with col_summary:
            st.write("**Missing Values Summary:**")
            if has_missing:
                st.warning(f"Total missing values: **{missing_counts.sum()}**")
                for col, count in missing_counts.items():
                    if count > 0:
                        st.write(f"- `{col}`: {count} nulls")
            else:
                st.success("No missing values detected.")
                
        with col_table:
            st.write("**Dataset Preview:**")
            st.dataframe(raw_df.head(5), use_container_width=True)
            
        # 2. Cleaning Actions
        st.markdown("---")
        st.subheader("🛠️ Automated Pre-processing Pipeline")
        st.markdown("This triggers the cleaning pipeline: parses datetimes, caps negative numbers, and imputes null values using column medians.")
        
        if st.button("🧼 Run Pre-processing & Imputation", use_container_width=True):
            clean_df = None
            if data_type == "Sales":
                clean_df = DataCleaner.clean_sales_data(raw_df)
            elif data_type == "Customers":
                clean_df = DataCleaner.clean_customer_data(raw_df)
            elif data_type == "Inventory":
                clean_df = DataCleaner.clean_inventory_data(raw_df)
                
            if clean_df is not None:
                st.session_state['cleaned_df'] = clean_df
                st.session_state['cleaned_type'] = data_type
                st.success("Pre-processing complete! See cleaned table below.")
            else:
                st.error("Data cleaning failed.")
                
        # 3. Import Actions
        if 'cleaned_df' in st.session_state and st.session_state['cleaned_type'] == data_type:
            cleaned_df = st.session_state['cleaned_df']
            
            st.markdown("### Cleaned Preview")
            st.dataframe(cleaned_df.head(5), use_container_width=True)
            
            st.markdown("---")
            st.subheader("💾 Load into Database")
            st.markdown("Confirming below will merge this cleaned dataset with existing SQLite tables.")
            
            if st.button("📥 Commit Cleaned Data to SQLite", use_container_width=True):
                success, msg = biz_service.import_cleaned_dataset(company_id, data_type, cleaned_df)
                if success:
                    st.success(msg)
                    # Clear session states
                    del st.session_state['cleaned_df']
                    del st.session_state['cleaned_type']
                else:
                    st.error(msg)
