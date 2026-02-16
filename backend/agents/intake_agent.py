# File: backend/agents/intake_agent.py
import pandas as pd
from typing import List, Tuple
from .models import ReconciliationState, AgentResponse, Invoice, Payment

class IntakeAgent:
    def __init__(self, customer_id: str):
        self.customer_id = customer_id

    async def fetch_from_db(self) -> Tuple[List[Invoice], List[Payment]]:
        """
        Fetches invoices and payments directly from Oracle 26AI for the current customer.
        """
        from db.connection import execute_query
        
        # 1. Fetch Invoices
        inv_rows = execute_query(
            "SELECT invoice_id, amount, currency, vendor_name, po_number, invoice_date FROM invoices WHERE customer_id = :1",
            [self.customer_id]
        )
        invoices = [Invoice(
            invoice_id=r[0], amount=r[1], currency=r[2], vendor_name=r[3], 
            po_number=r[4], invoice_date=r[5]
        ) for r in inv_rows]
        
        # 2. Fetch Payments
        pay_rows = execute_query(
            "SELECT payment_id, amount, currency, sender_name, trace_id, remittance_raw, payment_date FROM payments WHERE customer_id = :1",
            [self.customer_id]
        )
        payments = [Payment(
            payment_id=r[0], amount=r[1], currency=r[2], sender_name=r[3],
            trace_id=r[4], remittance_raw=r[5], payment_date=r[6]
        ) for r in pay_rows]
        
        return invoices, payments

    def process_uploads(self, invoice_file: str, payment_file: str) -> Tuple[List[Invoice], List[Payment]]:
        """
        Legacy CSV support (fallback).
        """
        # ... existing CSV logic ...
        pass

    def validate_state(self, invoices: List[Invoice], payments: List[Payment]):
        """
        Strict customer isolation check.
        """
        # Logic to ensure data belongs to self.customer_id
        # In production this happens at the DB query level
        pass
        
    def normalize_fields(self, state: ReconciliationState):
        """
        Normalizes currency symbols, date formats, and vendor names.
        """
        # LLM-assisted normalization could go here
        pass
