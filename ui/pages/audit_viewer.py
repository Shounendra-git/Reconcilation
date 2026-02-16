# File: ui/pages/audit_viewer.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Audit Viewer", layout="wide")

st.title("📜 Immutable Audit Explorer")

if 'reconciliation_data' not in st.session_state:
    st.warning("No data available. Please run reconciliation first.")
else:
    data = st.session_state['reconciliation_data']
    audit_logs = data.get('audit_trail', [])
    
    st.write("Complete history of agent decisions and manual overrides.")
    
    search_query = st.text_input("Search audit logs (by ID, Action, or Agent)...")
    
    df_audit = pd.DataFrame(audit_logs)
    
    if search_query:
        df_audit = df_audit[df_audit.apply(lambda row: search_query.lower() in str(row).lower(), axis=1)]
        
    st.dataframe(df_audit, use_container_width=True)
    
    if st.button("Export CSV for Compliance"):
        df_audit.to_csv("reconciliation_audit_export.csv", index=False)
        st.success("Exported to 'reconciliation_audit_export.csv'")
