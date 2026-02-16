# File: backend/agents/orchestrator.py
from typing import List, Optional
import os
from .models import ReconciliationState, AgentResponse, CustomerContext
from .intake_agent import IntakeAgent
from .matching_agent import MatchingAgent
from .exception_agent import ExceptionAgent
from .compliance_agent import ComplianceAgent
from .audit_agent import AuditAgent
from openai import OpenAI

# Initialize client (mocking for ahora, will use env in prod)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "mock-key"))

class ReconciliationOrchestrator:
    def __init__(self, state: ReconciliationState):
        self.state = state
        self.max_steps = 10
        self.current_step = 0

    async def run(self):
        """
        Executes the agentic workflow: 
        Intake -> Extraction -> Matching -> Exception -> Compliance -> Decision -> Audit
        """
        print(f"Starting reconciliation workflow for customer: {self.state.context.customer_id}")
        
        # 1. Intake & Validation
        await self.run_intake()
        
        # 2. Reference Extraction
        await self.run_extraction()
        
        # 3. Hybrid Matching
        await self.run_matching()
        
        # 4. Exception Classification
        await self.run_exception_analysis()
        
        # 5. Risk & Compliance
        await self.run_compliance_check()
        
        # 6. Decision & Escalation
        await self.run_decision_logic()
        
        # 7. Audit Logging
        await self.run_audit_trail()
        
        return self.state

    async def run_intake(self):
        agent = IntakeAgent(self.state.context.customer_id)
        # Fetch exclusively from Oracle 26AI
        invoices, payments = await agent.fetch_from_db()
        self.state.invoices = invoices
        self.state.payments = payments

    async def run_extraction(self):
        # Already handled by Intake for now, but extraction_agent would go here
        pass

    async def run_matching(self):
        agent = MatchingAgent(client)
        self.state = agent.hybrid_match(self.state)

    async def run_exception_analysis(self):
        agent = ExceptionAgent()
        self.state = agent.classify_exceptions(self.state)

    async def run_compliance_check(self):
        agent = ComplianceAgent()
        self.state = agent.enforce_guardrails(self.state)

    async def run_decision_logic(self):
        # Propose matches as final if confidence > 0.8
        for match in self.state.matches:
            if match['confidence'] >= 0.8:
                match['status'] = 'PROPOSED'
        pass

    async def run_audit_trail(self):
        agent = AuditAgent()
        self.state = agent.record_activity(self.state)
