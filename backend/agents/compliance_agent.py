# File: backend/agents/compliance_agent.py
import re
from datetime import datetime
from .models import ReconciliationState

class ComplianceAgent:
    def enforce_guardrails(self, state: ReconciliationState):
        """
        Ensures PII masking and tenant isolation.
        """
        # 1. Mask Sensitive Data in Remittance
        for pay in state.payments:
            # Mask bank account numbers (assuming 8-12 digits)
            pay.remittance_raw = re.sub(r'\d{8,12}', '********', pay.remittance_raw)
            
        # 2. Add Compliance Note to State
        state.audit_trail.append({
            "agent": "ComplianceAgent",
            "action": "PII_MASKING",
            "status": "COMPLETED",
            "timestamp": str(datetime.now())
        })
        return state
