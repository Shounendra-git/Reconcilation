# File: ui/pages/outliers.py
import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Manual Reconciliation", layout="wide")

st.title("⚠️ Exception Management & Manual Override")

if 'reconciliation_data' not in st.session_state:
    st.warning("Please run reconciliation from the Dashboard first.")
else:
    data = st.session_state['reconciliation_data']
    exceptions = data.get('exceptions', [])
    
    if not exceptions:
        st.success("No exceptions found! All items reconciled.")
    else:
        st.write(f"Found {len(exceptions)} exceptions requiring attention.")
        
        # Display Exceptions Table
        df_exc = pd.DataFrame(exceptions)
        st.dataframe(df_exc.rename(columns={
            "entity_id": "Entity ID",
            "type": "Type",
            "amount": "Amount",
            "reason": "Reason",
            "severity": "Severity"
        }), use_container_width=True)
        
        st.divider()
        st.subheader("Manual Link Action")
        
        col1, col2 = st.columns(2)
        with col1:
            inv_options = [e['entity_id'] for e in exceptions if e['type'] == 'UNMATCHED_INVOICE']
            invoice_to_link = st.selectbox("Select Unmatched Invoice", inv_options)
            # Show selected invoice amount
            selected_inv = next((e for e in exceptions if e['entity_id'] == invoice_to_link), None)
            if selected_inv:
                st.info(f"Invoice Amount: {selected_inv['amount']}")

        with col2:
            pay_options = [e['entity_id'] for e in exceptions if e['type'] == 'UNMATCHED_PAYMENT']
            payment_to_link = st.selectbox("Select Unmatched Payment", pay_options)
            # Show selected payment amount
            selected_pay = next((e for e in exceptions if e['entity_id'] == payment_to_link), None)
            if selected_pay:
                st.info(f"Payment Amount: {selected_pay['amount']}")
            
        reason = st.text_area("Adjustment Reason / Note", placeholder="e.g., Short-pay accepted due to damaged goods")
        
        if st.button("Confirm Manual Override"):
            try:
                # Call real backend persistence
                resp = requests.post("http://localhost:8000/manual-match", json={
                    "invoice_id": invoice_to_link,
                    "payment_id": payment_to_link,
                    "customer_id": data['context']['customer_id'],
                    "reason": reason
                })
                
                if resp.status_code == 200:
                    st.success(f"Successfully persisted link: {invoice_to_link} to {payment_to_link} in Oracle 26AI.")
                    st.info("Audit entry created: MANUAL_OVERRIDE by operator.")
                    
                    # Update local session state to reflect the change immediately
                    data['audit_trail'].append({
                        "entity_type": "MATCH",
                        "entity_id": f"{invoice_to_link}:{payment_to_link}",
                        "action": "MANUAL_OVERRIDE",
                        "operator": "USER-01",
                        "note": reason,
                        "timestamp": str(datetime.now())
                    })
                    st.session_state['reconciliation_data'] = data
                else:
                    st.error(f"Failed to persist match: {resp.text}")
            except Exception as e:
                st.error(f"Backend connection error: {e}")
