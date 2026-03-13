"""Journal Entry Template Library Page."""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.formatters import fmt_currency

st.set_page_config(page_title="Template Library | SmartClose", page_icon="📚", layout="wide")
st.title("📚 Journal Entry Template Library")
st.caption("Pre-built templates for common SaaS revenue accounting entries")

# Define templates
TEMPLATES = [
    {
        "id": "TPL-001",
        "name": "Monthly SaaS Revenue Recognition",
        "category": "Revenue Recognition",
        "frequency": "Monthly",
        "description": "Recognize monthly portion of deferred subscription revenue",
        "entries": [
            {"account": "2400 - Deferred Revenue", "debit": 10000, "credit": 0},
            {"account": "4100 - Subscription Revenue", "debit": 0, "credit": 10000},
        ],
    },
    {
        "id": "TPL-002",
        "name": "Annual Subscription Billing",
        "category": "Billing",
        "frequency": "Annual",
        "description": "Record annual subscription invoice and establish deferred revenue",
        "entries": [
            {"account": "1200 - Accounts Receivable", "debit": 120000, "credit": 0},
            {"account": "2400 - Deferred Revenue", "debit": 0, "credit": 120000},
        ],
    },
    {
        "id": "TPL-003",
        "name": "Usage-Based Revenue Accrual",
        "category": "Accrual",
        "frequency": "Monthly",
        "description": "Accrue usage-based revenue for services consumed but not yet billed",
        "entries": [
            {"account": "1310 - Unbilled Revenue", "debit": 5000, "credit": 0},
            {"account": "4200 - Usage Revenue", "debit": 0, "credit": 5000},
        ],
    },
    {
        "id": "TPL-004",
        "name": "Services Revenue - Point in Time",
        "category": "Revenue Recognition",
        "frequency": "As needed",
        "description": "Recognize services revenue upon completion of implementation/onboarding",
        "entries": [
            {"account": "2400 - Deferred Revenue", "debit": 25000, "credit": 0},
            {"account": "4300 - Services Revenue", "debit": 0, "credit": 25000},
        ],
    },
    {
        "id": "TPL-005",
        "name": "Customer Refund / Credit Memo",
        "category": "Adjustments",
        "frequency": "As needed",
        "description": "Process customer refund — reverse revenue and reduce receivable",
        "entries": [
            {"account": "4100 - Subscription Revenue", "debit": 3000, "credit": 0},
            {"account": "1200 - Accounts Receivable", "debit": 0, "credit": 3000},
        ],
    },
    {
        "id": "TPL-006",
        "name": "Contract Asset Reclassification",
        "category": "Reclassification",
        "frequency": "Monthly",
        "description": "Reclassify contract assets to receivable when right to payment becomes unconditional",
        "entries": [
            {"account": "1200 - Accounts Receivable", "debit": 15000, "credit": 0},
            {"account": "1300 - Contract Assets", "debit": 0, "credit": 15000},
        ],
    },
    {
        "id": "TPL-007",
        "name": "Deferred Revenue Reclassification (LT to ST)",
        "category": "Reclassification",
        "frequency": "Quarterly",
        "description": "Reclassify non-current deferred revenue to current as it comes within 12 months",
        "entries": [
            {"account": "2410 - Deferred Revenue (Non-Current)", "debit": 40000, "credit": 0},
            {"account": "2400 - Deferred Revenue (Current)", "debit": 0, "credit": 40000},
        ],
    },
    {
        "id": "TPL-008",
        "name": "Bad Debt Write-Off",
        "category": "Adjustments",
        "frequency": "As needed",
        "description": "Write off uncollectible accounts receivable against allowance",
        "entries": [
            {"account": "1205 - Allowance for Doubtful Accounts", "debit": 8000, "credit": 0},
            {"account": "1200 - Accounts Receivable", "debit": 0, "credit": 8000},
        ],
    },
]

# Category filter
categories = sorted(set(t["category"] for t in TEMPLATES))
selected_cat = st.selectbox("Filter by Category", ["All"] + categories)

filtered = TEMPLATES if selected_cat == "All" else [t for t in TEMPLATES if t["category"] == selected_cat]

st.write(f"**{len(filtered)} templates available**")

# Display templates
for template in filtered:
    with st.expander(f"📋 {template['id']}: {template['name']}"):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"**Description:** {template['description']}")
            st.markdown(f"**Category:** {template['category']} | **Frequency:** {template['frequency']}")

        with col2:
            total_debit = sum(e["debit"] for e in template["entries"])
            total_credit = sum(e["credit"] for e in template["entries"])
            st.metric("Amount", fmt_currency(total_debit))

        st.markdown("**Journal Entry:**")

        entry_rows = []
        for entry in template["entries"]:
            entry_rows.append({
                "Account": entry["account"],
                "Debit": fmt_currency(entry["debit"]) if entry["debit"] > 0 else "",
                "Credit": fmt_currency(entry["credit"]) if entry["credit"] > 0 else "",
            })
        st.dataframe(pd.DataFrame(entry_rows), use_container_width=True, hide_index=True)

        # Balance check
        balanced = abs(total_debit - total_credit) < 0.01
        st.markdown(f"**Balance Check:** {'✅ Balanced' if balanced else '❌ Unbalanced'}")

# Template usage guide
st.divider()
st.subheader("Template Usage Guide")

st.markdown("""
### How to Use These Templates

1. **Select a template** that matches your transaction type
2. **Adjust the amounts** to reflect actual transaction values
3. **Modify account codes** if your chart of accounts differs
4. **Post the entry** after manager review and approval

### Template Categories

| Category | Description | Typical Frequency |
|----------|-------------|-------------------|
| **Revenue Recognition** | Recognize deferred revenue as performance obligations are satisfied | Monthly |
| **Billing** | Record customer invoices and establish deferred revenue | Per invoice |
| **Accrual** | Accrue unbilled revenue for services consumed | Monthly |
| **Reclassification** | Reclassify balances between current/non-current or between accounts | Monthly/Quarterly |
| **Adjustments** | Refunds, write-offs, and other corrections | As needed |

### Best Practices

- Always verify debit/credit balance before posting
- Include sufficient description for audit trail
- Attach supporting documentation (invoice, contract, calculation)
- Follow four-eyes principle: preparer and reviewer must be different individuals
- Recurring entries should be reviewed each period for continued accuracy
""")
