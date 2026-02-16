
from fpdf import FPDF

class ProjectDoc(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Bank-Grade Reconciliation AI - Project Documentation', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 10, body)
        self.ln()

def generate_pdf(output_path):
    pdf = ProjectDoc()
    pdf.add_page()

    # Section 1: Introduction
    pdf.chapter_title('1. Project Overview')
    pdf.chapter_body(
        "The Bank-Grade Reconciliation AI is a specialized multi-agent system designed to automate financial "
        "reconciliation between invoices and bank payments. It leverages Oracle 23AI's converged database "
        "capabilities, including Vector Search and JSON storage, to handle semi-structured remittance data."
    )

    # Section 2: Architecture
    pdf.chapter_title('2. System Architecture')
    pdf.chapter_body(
        "- Frontend: Streamlit dashboard for monitoring and manual intervention.\n"
        "- Backend: FastAPI orchestrator managing the agent lifecycle.\n"
        "- Database: Oracle 23AI as a unified relational, JSON, and Vector store.\n"
        "- Integration: RESTful communication between UI and Backend services."
    )

    # Section 3: Why Agentic AI?
    pdf.chapter_title('3. The Agentic AI Pillars')
    pdf.chapter_body(
        "Unlike traditional automation, this solution is 'Agentic' because it exhibits:\n"
        "- Specialization: Independent units (Agents) with specific domain logic (Intake, Matching, Audit).\n"
        "- Reasoning: The ability to interpret messy 'dirty' remittance text and find semantic similarities.\n"
        "- State Management: An orchestrator that manages a complex lifecycle and handles handovers.\n"
        "- Goal-Orientation: Moving toward a 'High Confidence Match' rather than just executing rigid scripts."
    )

    # Section 4: Key Use Cases
    pdf.chapter_title('4. Primary Use Cases')
    pdf.chapter_body(
        "A. Ambiguous N:1 Bulk Matching:\n"
        "Resolving cases where a single large payment references multiple partial invoice codes buried in "
        "unstructured text. The AI extracts references, sums invoice totals, and validates the match.\n\n"
        "B. Intelligent Exception Classification:\n"
        "Identifying 'Short Payments' (Deductions) hidden in text, such as early payment discounts or "
        "disputed items, and classifying them correctly for manual review."
    )

    # Section 5: Human-in-the-Loop (Manual Override)
    pdf.chapter_title('5. Human-in-the-Loop & Governance')
    pdf.chapter_body(
        "The system explicitly supports a 'Human-in-the-Loop' model. When confidence scores drop below "
        "pre-defined thresholds, the AI flags the transaction as an 'Outlier.' Finance operators can then:\n"
        "- Manually link invoices to payments via the UI.\n"
        "- Provide a structured justification (Reasoning).\n"
        "- Maintain a bank-grade Audit Trail where every human decision is logged, versioned, and immutable."
    )

    # Section 6: Technical Stack
    pdf.chapter_title('6. Technical Stack Summary')
    pdf.chapter_body(
        "- Language: Python (FastAPI, Streamlit, Pydantic)\n"
        "- Database: Oracle 23AI (SQL, VECTOR, JSON)\n"
        "- AI Models: OpenAI/Gemini for semantic extraction and reasoning\n"
        "- Security: Environment-based credential management (.env) and multi-tenant isolation."
    )

    pdf.output(output_path)
    print(f"PDF generated at: {output_path}")

if __name__ == '__main__':
    generate_pdf('d:/Antigravity/Reconcilation/Project_Theory_Documentation.pdf')
