# File: backend/main.py
from fastapi import FastAPI, HTTPException
from .agents.models import ReconciliationState, CustomerContext
from .agents.orchestrator import ReconciliationOrchestrator
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

app = FastAPI(title="Bank-Grade Reconciliation AI")

class ReconciliationRequest(BaseModel):
    customer_id: str
    tenant_name: str

class ManualMatchRequest(BaseModel):
    invoice_id: str
    payment_id: str
    customer_id: str
    operator: str = "USER-01"
    reason: str = ""

@app.post("/reconcile")
async def start_reconciliation(request: ReconciliationRequest):
    if not request.customer_id:
        raise HTTPException(status_code=400, detail="Customer context missing. Please specify customer/session scope.")
    
    # Initialize state
    state = ReconciliationState(
        context=CustomerContext(customer_id=request.customer_id, tenant_name=request.tenant_name)
    )
    
    # Orchestrate workflow
    orchestrator = ReconciliationOrchestrator(state)
    final_state = await orchestrator.run()
    
    return final_state
@app.post("/manual-match")
async def manual_match(request: ManualMatchRequest):
    from db.connection import execute_statement
    import datetime
    
    try:
        # 1. Insert into reconciliation_matches
        execute_statement(
            "INSERT INTO reconciliation_matches (invoice_id, payment_id, customer_id, match_type, confidence_score, explanation) "
            "VALUES (:1, :2, :3, 'MANUAL_OVERRIDE', 1.0, :4)",
            [request.invoice_id, request.payment_id, request.customer_id, request.reason]
        )
        
        # 2. Update Invoice Status
        execute_statement(
            "UPDATE invoices SET status = 'MATCHED' WHERE invoice_id = :1 AND customer_id = :2",
            [request.invoice_id, request.customer_id]
        )
        
        # 3. Update Payment Status
        execute_statement(
            "UPDATE payments SET status = 'MATCHED' WHERE payment_id = :1 AND customer_id = :2",
            [request.payment_id, request.customer_id]
        )
        
        # 4. Log to Audit Trail
        execute_statement(
            "INSERT INTO audit_trail (entity_type, entity_id, customer_id, action, operator_id, timestamp) "
            "VALUES ('MATCH', :1, :2, 'MANUAL_OVERRIDE', :3, CURRENT_TIMESTAMP)",
            [f"{request.invoice_id}:{request.payment_id}", request.customer_id, request.operator]
        )
        
        return {"status": "success", "message": f"Persisted manual match: {request.invoice_id} -> {request.payment_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database persistence failed: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "oracle_26ai_ready"}
