# File: backend/agents/matching_agent.py
import os
from typing import List, Tuple
from .models import ReconciliationState, Invoice, Payment
from openai import OpenAI

class MatchingAgent:
    def __init__(self, client: OpenAI):
        self.client = client

    def get_oracle_vector_match(self, payment_id: str, customer_id: str) -> List[dict]:
        """
        Oracle 26AI Vector Search implementation.
        Finds the top 3 invoices that are semantically similar to a payment's remittance.
        """
        from db.connection import execute_query
        
        # This query uses Oracle's native VECTOR_DISTANCE feature
        query = """
            SELECT source_id, VECTOR_DISTANCE(embedding, (SELECT embedding FROM metadata_vectors WHERE source_id = :pid AND source_type = 'PAYMENT'), COSINE) as dist
            FROM metadata_vectors
            WHERE source_type = 'INVOICE' AND customer_id = :cid
            ORDER BY dist
            FETCH FIRST 3 ROWS ONLY
        """
        try:
            results = execute_query(query, {"pid": payment_id, "cid": customer_id})
            return [{"invoice_id": r[0], "distance": r[1]} for r in results]
        except Exception as e:
            print(f"Oracle Vector Search error: {e}")
            return []

    def hybrid_match(self, state: ReconciliationState):
        """
        Optimized Matching Logic for Large Datasets:
        1. Index invoices by amount and reference.
        2. Perform O(1) lookups for 1:1 and N:1 matches.
        3. Efficiently group payments for 1:N matches.
        """
        matched_invoices = set()
        matched_payments = set()

        # 1. Indexing Invoices
        invoice_by_amt = {} # amt -> list of invoices
        invoice_by_ref = {} # ref -> invoice
        
        for inv in state.invoices:
            amt = round(inv.amount, 2)
            if amt not in invoice_by_amt:
                invoice_by_amt[amt] = []
            invoice_by_amt[amt].append(inv)
            
            invoice_by_ref[inv.invoice_id] = inv
            if inv.po_number:
                invoice_by_ref[inv.po_number] = inv

        # Phase 1: FAST 1:1 Matches
        for payment in state.payments:
            pay_amt = round(payment.amount, 2)
            # Try exact amount lookup
            if pay_amt in invoice_by_amt:
                for inv in invoice_by_amt[pay_amt]:
                    if inv.invoice_id in matched_invoices: continue
                    
                    # Check semantic/reference overlap
                    if (inv.invoice_id in (payment.remittance_raw or "") or 
                        (inv.po_number and inv.po_number in (payment.remittance_raw or ""))):
                        state.matches.append({
                            "invoice_id": inv.invoice_id,
                            "payment_id": payment.payment_id,
                            "invoice_amount": inv.amount,
                            "payment_amount": payment.amount,
                            "confidence": 1.0,
                            "reasons": ["Exact 1:1 Match (Optimized Index Lookup)"],
                            "match_type": "AUTO_1_1"
                        })
                        matched_invoices.add(inv.invoice_id)
                        matched_payments.add(payment.payment_id)
                        break

        # Phase 2: N:1 (Bulk) - One payment for multiple invoices
        for payment in state.payments:
            if payment.payment_id in matched_payments: continue
            
            # Simple regex/split to find IDs in remittance (mocked here by string search)
            # We look for references that exist in our index
            candidates = []
            for ref, inv in invoice_by_ref.items():
                if inv.invoice_id in matched_invoices: continue
                if ref in (payment.remittance_raw or ""):
                    if inv not in candidates: candidates.append(inv)
            
            if candidates:
                total_inv_amt = sum(inv.amount for inv in candidates)
                if abs(total_inv_amt - payment.amount) < 0.01:
                    for inv in candidates:
                        state.matches.append({
                            "invoice_id": inv.invoice_id,
                            "payment_id": payment.payment_id,
                            "invoice_amount": inv.amount,
                            "payment_amount": payment.amount,
                            "confidence": 0.95,
                            "reasons": ["N:1 Bulk Match (Indexed Reference Search)"],
                            "match_type": "AUTO_MANY_1"
                        })
                        matched_invoices.add(inv.invoice_id)
                    matched_payments.add(payment.payment_id)

        # Phase 3: 1:N (Splits) - One invoice for multiple payments
        # Index unmatched payments by mentioned invoice ID
        pay_by_inv_ref = {}
        for p in state.payments:
            if p.payment_id in matched_payments: continue
            # Check for invoice ID in remittance
            for inv_id in invoice_by_ref: # Quick check against known IDs
                if inv_id in (p.remittance_raw or ""):
                    if inv_id not in pay_by_inv_ref: pay_by_inv_ref[inv_id] = []
                    pay_by_inv_ref[inv_id].append(p)

        for inv_id, candidate_pays in pay_by_inv_ref.items():
            if inv_id in matched_invoices: continue
            inv = invoice_by_ref.get(inv_id)
            if not inv: continue
            
            total_pay_amt = sum(p.amount for p in candidate_pays)
            if abs(total_pay_amt - inv.amount) < 0.01:
                for p in candidate_pays:
                    state.matches.append({
                        "invoice_id": inv.invoice_id,
                        "payment_id": p.payment_id,
                        "invoice_amount": inv.amount,
                        "payment_amount": p.amount,
                        "confidence": 0.95,
                        "reasons": ["1:N Split Match (Sum of payments matches invoice)"],
                        "match_type": "AUTO_1_MANY"
                    })
                    matched_payments.add(p.payment_id)
                matched_invoices.add(inv.invoice_id)

        return state
