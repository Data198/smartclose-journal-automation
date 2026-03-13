"""Balance Sheet Reconciliation Status Board."""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.csv_handler import load_reconciliations
from utils.formatters import fmt_currency

st.set_page_config(page_title="Reconciliation | SmartClose", page_icon="✅", layout="wide")
st.title("✅ Balance Sheet Reconciliation Status")
st.caption("Track reconciliation status for revenue-related balance sheet accounts")

# Load data
recon_data = load_reconciliations()
recons = recon_data["reconciliations"]
period = recon_data["period"]

st.subheader(f"Period: {period}")

# Summary metrics
reconciled = sum(1 for r in recons if r["status"] == "reconciled")
under_threshold = sum(1 for r in recons if r["status"] == "variance_under_threshold")
over_threshold = sum(1 for r in recons if r["status"] == "variance_over_threshold")
total = len(recons)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Accounts", total)
m2.metric("Reconciled", reconciled, help="Variance = $0")
m3.metric("Under Threshold", under_threshold, help="Variance exists but within acceptable range")
m4.metric("Over Threshold", over_threshold, help="Variance exceeds materiality threshold — action required")

# Progress
pct = reconciled / total * 100
st.progress(pct / 100)
st.caption(f"{pct:.0f}% fully reconciled")

# Status board
st.divider()
st.subheader("Reconciliation Detail")

status_colors = {
    "reconciled": "🟢",
    "variance_under_threshold": "🟡",
    "variance_over_threshold": "🔴",
    "not_started": "⬜",
}

status_labels = {
    "reconciled": "Reconciled",
    "variance_under_threshold": "Variance (Under Threshold)",
    "variance_over_threshold": "Variance (Over Threshold)",
    "not_started": "Not Started",
}

recon_rows = []
for r in recons:
    recon_rows.append({
        "Status": f"{status_colors.get(r['status'], '')} {status_labels.get(r['status'], r['status'])}",
        "Account": r["account"],
        "GL Balance": fmt_currency(r["gl_balance"]),
        "Sub-Ledger Balance": fmt_currency(r["sub_ledger_balance"]),
        "Variance": fmt_currency(r["variance"]),
        "Preparer": r["preparer"],
        "Reviewer": r["reviewer"],
    })

st.dataframe(pd.DataFrame(recon_rows), use_container_width=True, hide_index=True)

# Accounts with variances
st.divider()
st.subheader("Variance Investigation")

variance_accounts = [r for r in recons if r["variance"] != 0]

if not variance_accounts:
    st.success("All accounts are fully reconciled with no variances.")
else:
    for r in variance_accounts:
        severity = "🟡" if r["status"] == "variance_under_threshold" else "🔴"
        with st.expander(f"{severity} {r['account']} — Variance: {fmt_currency(r['variance'])}"):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("GL Balance", fmt_currency(r["gl_balance"]))
                st.metric("Sub-Ledger Balance", fmt_currency(r["sub_ledger_balance"]))
            with col2:
                st.metric("Variance", fmt_currency(r["variance"]))
                variance_pct = (r["variance"] / r["gl_balance"] * 100) if r["gl_balance"] != 0 else 0
                st.metric("Variance %", f"{variance_pct:.2f}%")

            st.markdown(f"**Preparer:** {r['preparer']} | **Reviewer:** {r['reviewer']}")

            if r["status"] == "variance_over_threshold":
                st.error("This variance exceeds the materiality threshold and requires investigation.")
                st.markdown("""
                **Recommended Actions:**
                1. Review sub-ledger detail for missing or duplicate entries
                2. Check for timing differences (cutoff issues)
                3. Verify manual adjustments posted in the period
                4. Document findings and escalate if unresolved
                """)
            else:
                st.warning("Variance is within acceptable threshold but should be monitored.")

# Reconciliation metrics over time (simulated)
st.divider()
st.subheader("Reconciliation Completion Trend")
st.caption("Historical view of reconciliation status at each month-end")

import plotly.graph_objects as go

months = ["Jul'23", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan'24", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
reconciled_pct = [62, 75, 62, 75, 75, 62, 75, 75, 88, 88, 88, 75, 88, 88, 88, 88, 88, 88]
target = [100] * len(months)

fig = go.Figure()
fig.add_trace(go.Scatter(x=months, y=reconciled_pct, mode="lines+markers",
                          name="% Reconciled", line=dict(color="#1E3A5F", width=2.5)))
fig.add_trace(go.Scatter(x=months, y=target, mode="lines",
                          name="Target (100%)", line=dict(color="#dc3545", dash="dash")))
fig.update_layout(
    title="Monthly Reconciliation Completion Rate",
    yaxis_title="% Reconciled", yaxis_range=[0, 105],
    plot_bgcolor="rgba(0,0,0,0)", height=350,
)
st.plotly_chart(fig, use_container_width=True)
