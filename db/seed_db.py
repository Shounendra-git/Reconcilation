# File: db/seed_db.py
import pandas as pd
import os
import oracledb
from openai import OpenAI
from connection import get_connection
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text):
    """
    Generates an embedding for the given text using OpenAI's text-embedding-3-small.
    """
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding


def exec_stmt(statement, params=None, retries=3, timeout=10):
    """
    Execute a single statement with its own short-lived connection.
    Retries on transient connection errors.
    """
    import time
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            with get_connection(timeout=timeout) as conn:
                with conn.cursor() as cursor:
                    if params is not None:
                        cursor.execute(statement, params)
                    else:
                        cursor.execute(statement)
                conn.commit()
            return
        except Exception as e:
            last_exc = e
            err_str = str(e)
            print(f"exec_stmt attempt {attempt} failed: {err_str}")
            # If final attempt, re-raise
            if attempt == retries:
                raise
            time.sleep(1 * attempt)

def create_schema():
    print("Creating Oracle 26AI Schema...")
    with open("db/schema.sql", "r") as f:
        schema_sql = f.read()
    
    # Improved SQL splitting: Remove comments first, then split by semicolon
    import re
    # Remove single line comments
    clean_sql = re.sub(r'--.*', '', schema_sql)
    # Split by semicolon and filter empty
    statements = [s.strip() for s in clean_sql.split(";") if s.strip()]
    
    with get_connection(timeout=10) as conn:
        with conn.cursor() as cursor:
            for statement in statements:
                try:
                    cursor.execute(statement)
                    print(f"Executed success: {statement[:40]}...")
                except oracledb.Error as e:
                    # Ignore "table already exists" or "index already exists"
                    if "ORA-00955" in str(e) or "ORA-02260" in str(e):
                        continue
                    print(f"Statement skipped: {statement[:40]}... Error: {e}")
            conn.commit()

def clean_db():
    print("Cleaning existing data for a fresh seed...")
    print("Deleting tables individually (robust to reconnects)...")
    tables = [
        "reconciliation_matches",
        "metadata_vectors",
        "invoices",
        "payments",
        "audit_trail",
        "customers",
    ]
    for t in tables:
        try:
            print(f"Deleting from {t}...")
            exec_stmt(f"DELETE FROM {t}")
            print(f"Deleted from {t}.")
        except Exception as e:
            print(f"Warning deleting from {t}: {e}")
    print("Cleanup complete (individual commits).")

def seed_data():
    clean_db()
    
    invoices_df = pd.read_csv("data/synthetic_invoices.csv", comment='#')
    payments_df = pd.read_csv("data/synthetic_payments.csv", comment='#')
    
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # 1. Seed Customers
            print("Seeding customers...")
            customer_ids = set(invoices_df['customer_id']).union(set(payments_df['customer_id']))
            cust_data = [[cid, f"Tenant {cid}"] for cid in customer_ids]
            cursor.executemany("INSERT INTO customers (customer_id, name) VALUES (:1, :2)", cust_data)
            
            # 2. Seed Invoices
            print(f"Seeding {len(invoices_df)} invoices...")
            inv_rows = []
            vec_rows = []
            for _, row in invoices_df.iterrows():
                iid = str(row['invoice_id'])
                cid = str(row['customer_id'])
                vname = str(row['vendor_name'])
                amt = float(row['amount'])
                curr = str(row['currency'])
                idat = str(row['invoice_date']).split(' ')[0]
                pno = str(row['po_number']) if pd.notna(row['po_number']) else None
                
                inv_rows.append([iid, cid, vname, amt, curr, idat, pno])
                
                metadata_text = f"Invoice {iid} from {vname} for {amt} {curr}. PO: {pno}"
                vec_rows.append([iid, cid, metadata_text])

            cursor.executemany(
                "INSERT INTO invoices (invoice_id, customer_id, vendor_name, amount, currency, invoice_date, po_number, status) "
                "VALUES (:1, :2, :3, :4, :5, TO_DATE(:6, 'YYYY-MM-DD'), :7, 'PENDING')",
                inv_rows
            )
            
            cursor.executemany(
                "INSERT INTO metadata_vectors (source_type, source_id, customer_id, metadata_text) "
                "VALUES ('INVOICE', :1, :2, :3)",
                vec_rows
            )

            # 3. Seed Payments
            print(f"Seeding {len(payments_df)} payments...")
            pay_rows = []
            pay_vec_rows = []
            for _, row in payments_df.iterrows():
                pid = str(row['payment_id'])
                cid = str(row['customer_id'])
                sname = str(row['sender_name'])
                amt = float(row['amount'])
                curr = str(row['currency'])
                pdat = str(row['payment_date']).split(' ')[0]
                trid = str(row['trace_id'])
                rraw = str(row['remittance_raw'])
                
                pay_rows.append([pid, cid, sname, amt, curr, pdat, trid, rraw])
                
                metadata_text = f"Payment {pid} from {sname} for {amt} {curr}. Trace: {trid}. Remittance: {rraw}"
                pay_vec_rows.append([pid, cid, metadata_text])

            cursor.executemany(
                "INSERT INTO payments (payment_id, customer_id, sender_name, amount, currency, payment_date, trace_id, remittance_raw, status) "
                "VALUES (:1, :2, :3, :4, :5, TO_DATE(:6, 'YYYY-MM-DD'), :7, :8, 'UNMATCHED')",
                pay_rows
            )
            
            cursor.executemany(
                "INSERT INTO metadata_vectors (source_type, source_id, customer_id, metadata_text) "
                "VALUES ('PAYMENT', :1, :2, :3)",
                pay_vec_rows
            )

            conn.commit()
    print("Seeding process completed!")

if __name__ == "__main__":
    try:
        # Step 1: Ensure Schema exists
        # create_schema() # We can skip if already created, or run it once more
        
        # Step 2: Seed
        seed_data()
    except Exception as e:
        print(f"Error during seeding: {e}")
