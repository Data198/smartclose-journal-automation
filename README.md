# ⚡ SmartClose — Automated Journal Entry & Month-End Close Tracker

A month-end close management tool that **automates journal entry generation** from source data, tracks close task completion, and measures close cycle performance. Demonstrates how process automation transforms the monthly close from a manual, error-prone process into a streamlined, data-driven workflow.

**🔗 [Live Demo](https://smartclose-journal-automation.streamlit.app)**

![Built with Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-ff4b4b?logo=streamlit)
![Python](https://img.shields.io/badge/Python-3.10+-3776ab?logo=python)

---

## Automation Impact

| Metric | Before | After | Impact |
|--------|--------|-------|--------|
| **Days to Close** | 6-7 days | 3-4 days | 40-50% faster |
| **Manual Journal Entries** | 140+ /month | <15 /month | 90% automated |
| **Annual Hours Saved** | — | ~250 hours | ~2 FTEs |
| **Close Task On-Time %** | 78% | 95%+ | 17pp improvement |

## Features

| Module | Description |
|--------|-------------|
| **JE Generator** | Upload source transactions, apply automation rules, and generate balanced entries |
| **Close Tracker** | Kanban-style close task dashboard with progress tracking |
| **Close Analytics** | Historical close cycle trends and before/after automation comparison |
| **Reconciliation** | Balance sheet reconciliation status board with variance investigation |
| **Template Library** | 8 pre-built journal entry templates for common SaaS revenue scenarios |

## Key Capabilities

- **Rule-Based Automation Engine** — Map transaction types to proper journal entries
- **Balance Validation** — Automatic debit/credit balance checks on every generated entry
- **Close Task Tracking** — Kanban board with progress bars and bottleneck identification
- **Before/After Analytics** — Quantified automation impact with trend visualization
- **Reconciliation Board** — Status tracking with variance investigation workflows

## Tech Stack

- **Python** · **Streamlit** · **Pandas** · **Plotly** · **NumPy**

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Sample Data

Uses generated data for **NovaCRM Inc.** including:
- 500+ source transactions across 15 customers
- 5 automation rules covering subscriptions, usage, services, and refunds
- 14 close tasks across 5 categories
- 18 months of historical close cycle metrics showing automation progression

---

*Built by a Senior Revenue Accountant to demonstrate accounting process automation expertise.*
