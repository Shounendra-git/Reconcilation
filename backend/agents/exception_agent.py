# File: backend/agents/exception_agent.py
from datetime import datetime
from .models import ReconciliationState

class ExceptionAgent:
    def classify_exceptions(self, state: ReconciliationState):
        """
        Identifies unmatched items and categorizes them.
        """
        matched_invoice_ids = {m['invoice_id'] for m in state.matches}
        matched_payment_ids = {m['payment_id'] for m in state.matches}
        
        # 1. Unmatched Invoices
        for inv in state.invoices:
            if inv.invoice_id not in matched_invoice_ids:
                state.exceptions.append({
                    "entity_id": inv.invoice_id,
                    "type": "UNMATCHED_INVOICE",
                    "amount": inv.amount,
                    "reason": "No payment found with matching ID or amount",
                    "severity": "HIGH" if (datetime.now() - inv.invoice_date).days > 30 else "MEDIUM"
                })
        
        # 2. Unmatched Payments
        for pay in state.payments:
            if pay.payment_id not in matched_payment_ids:
                state.exceptions.append({
                    "entity_id": pay.payment_id,
                    "type": "UNMATCHED_PAYMENT",
                    "amount": pay.amount,
                    "reason": "Payment received without clear reference to an invoice",
                    "severity": "MEDIUM"
                })
        
        return state
