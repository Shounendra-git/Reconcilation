# File: ui/dashboard.py
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Reconciliation Dashboard", layout="wide")

st.title("🚀 Bank-Grade Reconciliation AI")
st.markdown("### Operational Overview & Agentic Metrics")

# Sidebar for Context
st.sidebar.header("Customer Context")
customer_id = st.sidebar.text_input("Customer ID", value="CUST-1001")
tenant_name = st.sidebar.text_input("Tenant Name", value="Global Agri-Corp")

if st.sidebar.button("Run Auto-Reconciliation"):
    with st.spinner("Agents are orchestrating..."):
        try:
            response = requests.post("http://localhost:8000/reconcile", json={
                "customer_id": customer_id,
                "tenant_name": tenant_name
            })
            if response.status_code == 200:
                st.session_state['reconciliation_data'] = response.json()
                st.success("Reconciliation Complete!")
            else:
                st.error("Failed to run reconciliation.")
        except Exception as e:
            st.error(f"Error connecting to backend: {e}")

# Metrics Display
if 'reconciliation_data' in st.session_state:
    data = st.session_state['reconciliation_data']
    
    col1, col2, col3, col4 = st.columns(4)
    total_inv = len(data['invoices'])
    total_matches = len(data['matches'])
    recon_rate = (total_matches / total_inv * 100) if total_inv > 0 else 0
    
    col1.metric("Total Invoices", total_inv)
    col2.metric("Total Payments", len(data['payments']))
    col3.metric("Auto-Matches", total_matches)
    col4.metric("Reconciliation Rate", f"{recon_rate:.1f}%")

    # Layout: Matches and Exceptions
    st.divider()
    tab1, tab2, tab3 = st.tabs(["✅ Matches", "⚠️ Outliers & Exceptions", "📜 Audit Trail"])
    
    with tab1:
        if data['matches']:
            st.write("Suggested matches from Hybrid Agent (Rules + Semantics)")
            df_matches = pd.DataFrame(data['matches'])
            # Reorder and rename for better visibility
            cols = ["invoice_id", "invoice_amount", "payment_id", "payment_amount", "confidence", "match_type", "reasons"]
            df_matches = df_matches[cols]
            st.dataframe(df_matches.rename(columns={
                "invoice_id": "Invoice ID",
                "invoice_amount": "Inv Amount",
                "payment_id": "Payment ID",
                "payment_amount": "Pay Amount",
                "confidence": "Conf",
                "match_type": "Type",
                "reasons": "Reasons"
            }), use_container_width=True)
        else:
            st.write("No matches found.")

    with tab2:
        if data['exceptions']:
            st.write("Exceptions flagged by Classification Agent")
            st.table(data['exceptions'])
        else:
            st.write("No exceptions detected.")

    with tab3:
        st.write("Immutable Audit Trail (Agent Activity)")
        st.json(data['audit_trail'])
else:
    st.info("👈 Set customer context and run auto-reconciliation to see results.")
