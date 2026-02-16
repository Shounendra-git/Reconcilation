# File: backend/agents/models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class CustomerContext(BaseModel):
    customer_id: str
    tenant_name: str

class Invoice(BaseModel):
    invoice_id: str
    amount: float
    currency: str
    vendor_name: str
    po_number: Optional[str] = None
    invoice_date: datetime

class Payment(BaseModel):
    payment_id: str
    amount: float
    currency: str
    sender_name: str
    trace_id: Optional[str] = None
    remittance_raw: str
    payment_date: datetime

class AgentResponse(BaseModel):
    agent_name: str
    status: str # SUCCESS, FAILURE, ESCALATED
    data: Dict[str, Any]
    reasoning: str
    confidence: float = 1.0

class ReconciliationState(BaseModel):
    context: CustomerContext
    invoices: List[Invoice] = []
    payments: List[Payment] = []
    extractions: List[Dict[str, Any]] = []
    matches: List[Dict[str, Any]] = []
    exceptions: List[Dict[str, Any]] = []
    audit_trail: List[Dict[str, Any]] = []
    history: List[AgentResponse] = []
