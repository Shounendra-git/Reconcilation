# File: backend/agents/audit_agent.py
from datetime import datetime
from .models import ReconciliationState

class AuditAgent:
    def record_activity(self, state: ReconciliationState):
        """
        Creates an immutable-ready record of all agent decisions.
        """
        # This would normally write to the Oracle 'audit_trail' table
        for match in state.matches:
            state.audit_trail.append({
                "entity_type": "MATCH",
                "entity_id": f"{match['invoice_id']}:{match['payment_id']}",
                "action": "AUTO_MATCH",
                "confidence": match['confidence'],
                "timestamp": str(datetime.now())
            })
        return state
