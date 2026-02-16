# Bank-Grade Agentic Reconciliation AI

This repository contains a multi-agent system for automated invoice and payment reconciliation using FastAPI, OpenAI, and Oracle 26AI patterns.

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- OpenAI API Key (Exported as `OPENAI_API_KEY`)

### 2. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Start Backend
uvicorn backend.main:app --reload
```
# Start Frontend (Different Terminal)
streamlit run ui/dashboard.py
```

### 3. Usage
- Open the Dashboard (usually `localhost:8501`).
- Enter a **Customer ID** to see specific scenarios:
    - `CUST-001`: Simple 1:1 matches.
    - `CUST-002`: Bulk pay (Many-to-1).
    - `CUST-004`: Short-pays (Exceptions).
    - `CUST-005`: Split payments (Multiple links).
    - `CUST-006`: Mystery payments (Outliers).
    - `CUST-010`: Duplicate invoices/payments.
- Click **Run Auto-Reconciliation**.

## 🧠 Architecture
The system uses a 7-agent workflow:
1. **Intake Agent**: Data normalization.
2. **Extraction Agent**: ID extraction from remittance text.
3. **Matching Agent**: Hybrid Rule-based + Semantic match.
4. **Exception Agent**: Classification of missing links.
5. **Compliance Agent**: PII masking & Guardrails.
6. **Decision Agent**: Confidence-based proposals.
7. **Audit Agent**: Immutable trail creation.

## 🗄 Database (Oracle 26AI)
Refer to `db/schema.sql` for the relational, JSON, and Vector schema definitions.
