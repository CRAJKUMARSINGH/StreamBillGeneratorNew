import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Test Upload",
    page_icon="📁",
    layout="wide"
)

st.title("Test File Upload")

# Simple file uploader test
uploaded_file = st.file_uploader(
    "Choose a single Excel file",
    type=['xlsx', 'xls', 'xlsm']
)

if uploaded_file is not None:
    st.success(f"File uploaded: {uploaded_file.name}")
    st.write(f"File size: {uploaded_file.size} bytes")
    
    try:
        # Try to read the file
        df = pd.read_excel(uploaded_file, sheet_name=None)
        st.write(f"Sheets found: {list(df.keys())}")
        
        for sheet_name, data in df.items():
            st.subheader(f"Sheet: {sheet_name}")
            st.dataframe(data.head())
            
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")