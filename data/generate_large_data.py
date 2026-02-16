# File: data/generate_large_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_data(num_customers=50, invoices_per_cust=40):
    customers = [f"CUST-{1000 + i}" for i in range(num_customers)]
    
    invoices = []
    payments = []
    
    for cust in customers:
        for i in range(invoices_per_cust):
            inv_id = f"INV-{cust}-{i:04d}"
            amount = round(random.uniform(500, 10000), 2)
            inv_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 180))
            vendor = random.choice(["Global Logistics", "Compute Cloud", "Office Supply Co", "Enterprise SaaS", "Steel Fab Inc"])
            po = f"PO-{random.randint(10000, 99999)}"
            
            invoices.append({
                "invoice_id": inv_id,
                "customer_id": cust,
                "amount": amount,
                "currency": "USD",
                "vendor_name": vendor,
                "po_number": po,
                "invoice_date": inv_date.strftime("%Y-%m-%d")
            })
            
            # Scenario Logic
            scenario = random.random()
            
            if scenario < 0.7: # 1:1 Match
                payments.append({
                    "payment_id": f"PAY-{inv_id}",
                    "customer_id": cust,
                    "amount": amount,
                    "currency": "USD",
                    "sender_name": vendor,
                    "trace_id": f"TR-{random.randint(100000, 999999)}",
                    "remittance_raw": f"Full payment for {inv_id}",
                    "payment_date": (inv_date + timedelta(days=random.randint(5, 15))).strftime("%Y-%m-%d")
                })
            elif scenario < 0.85: # 1:N Match (Multiple Payments for one Invoice)
                num_splits = random.randint(2, 4)
                split_amounts = np.random.dirichlet(np.ones(num_splits), size=1)[0] * amount
                for s in range(num_splits):
                    payments.append({
                        "payment_id": f"PAY-{inv_id}-S{s}",
                        "customer_id": cust,
                        "amount": round(split_amounts[s], 2),
                        "currency": "USD",
                        "sender_name": vendor,
                        "trace_id": f"TR-{random.randint(100000, 999999)}",
                        "remittance_raw": f"Partial payment {s+1}/{num_splits} for {inv_id}",
                        "payment_date": (inv_date + timedelta(days=random.randint(5, 30))).strftime("%Y-%m-%d")
                    })
            else: # Exception (Unmatched Invoice or Unmatched Payment)
                if random.choice([True, False]):
                    # Payment with no invoice
                    err_id = f"PAY-ERR-{cust}-{len(payments)}"
                    payments.append({
                        "payment_id": err_id,
                        "customer_id": cust,
                        "amount": round(random.uniform(100, 500), 2),
                        "currency": "USD",
                        "sender_name": "Unknown Entity",
                        "trace_id": f"TR-ERR-{random.randint(100000, 999999)}",
                        "remittance_raw": "Zyxel maintenance fee",
                        "payment_date": "2024-02-15"
                    })
                # If False, the invoice just stays PENDING (unmatched)

    pd.DataFrame(invoices).to_csv("data/synthetic_invoices.csv", index=False)
    pd.DataFrame(payments).to_csv("data/synthetic_payments.csv", index=False)
    print(f"Generated {len(invoices)} invoices and {len(payments)} payments across {num_customers} customers.")

if __name__ == "__main__":
    generate_data()
