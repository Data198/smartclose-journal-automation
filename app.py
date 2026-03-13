"""SmartClose: Automated Journal Entry & Month-End Close Tracker.

A month-end close management tool that automates journal entry generation
and tracks close task completion, built by a Senior Revenue Accountant.
"""

import streamlit as st

st.set_page_config(
    page_title="SmartClose — Journal Automation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚡ SmartClose")
st.subheader("Automated Journal Entry & Month-End Close Tracker")

st.markdown("""
**SmartClose** is a month-end close management tool that automates journal entry
generation from source data, tracks close task completion, and measures close cycle
performance. It demonstrates how process automation can transform the monthly close
from a manual, error-prone process into a streamlined, data-driven workflow.

---

### Tool Pages

| Page | Description |
|------|-------------|
| **JE Generator** | Upload source transactions, apply automation rules, and generate balanced entries |
| **Close Tracker** | Kanban-style close task dashboard with progress tracking |
| **Close Analytics** | Historical close cycle trends and before/after automation comparison |
| **Reconciliation** | Balance sheet reconciliation status board with variance investigation |
| **Template Library** | Pre-built journal entry templates for common SaaS revenue scenarios |

---

### Automation Impact Story

This tool showcases the real-world impact of accounting process automation:

| Metric | Before | After | Impact |
|--------|--------|-------|--------|
| **Days to Close** | 6-7 days | 3-4 days | 40-50% faster |
| **Manual Journal Entries** | 140+ per month | <15 per month | 90% automated |
| **Annual Hours Saved** | — | ~250 hours | ~2 FTEs |
| **Close Task On-Time %** | 78% | 95%+ | 17pp improvement |

---

### How It Works

1. **Source Data Ingestion** — Upload billing, usage, and refund transactions (CSV)
2. **Rule Engine** — Match transactions to accounting rules automatically
3. **JE Generation** — Produce balanced debit/credit entries with full audit trail
4. **Validation** — Auto-check balance, completeness, and data integrity
5. **Export** — Download entries for ERP upload (CSV format)

---

### Key Features

- **Rule-Based Automation Engine** — Map transaction types to proper journal entries
- **Balance Validation** — Automatic debit/credit balance checks on every generated entry
- **Close Task Tracking** — Kanban board with progress bars and bottleneck identification
- **Before/After Analytics** — Quantified automation impact with trend visualization
- **Reconciliation Board** — Status tracking with variance investigation workflows
- **Template Library** — 8 pre-built templates covering common SaaS revenue scenarios

---

### Sample Data

This app uses generated sample data for **NovaCRM Inc.** including:
- 500+ source transactions across 15 customers
- 5 automation rules covering subscriptions, usage, services, and refunds
- 14 close tasks across 5 categories
- 18 months of historical close cycle metrics showing automation progression

---

*Built with Python, Streamlit, Pandas, and Plotly*
""")

st.sidebar.success("Select a page above to explore the tool.")
