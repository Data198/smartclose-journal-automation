"""Automated Journal Entry Generator Page."""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.csv_handler import load_sample_transactions, load_automation_rules
from engine.rule_processor import process_transactions
from engine.je_builder import validate_balance, summarize_by_account, summarize_by_rule
from engine.validators import validate_entries_batch
from utils.formatters import fmt_currency

st.set_page_config(page_title="JE Generator | SmartClose", page_icon="⚡", layout="wide")
st.title("⚡ Automated Journal Entry Generator")
st.caption("Upload source transactions, apply automation rules, and generate balanced journal entries")

# Data source selection
st.subheader("1. Source Data")
data_source = st.radio("Select data source:", ["Use Sample Data", "Upload CSV"], horizontal=True)

if data_source == "Upload CSV":
    uploaded = st.file_uploader("Upload source transactions CSV", type=["csv"])
    if uploaded:
        transactions = pd.read_csv(uploaded)
    else:
        st.info("Upload a CSV with columns: transaction_id, date, customer_id, customer_name, product, transaction_type, amount, currency")
        st.stop()
else:
    transactions = load_sample_transactions()

st.write(f"**{len(transactions)} transactions loaded**")
with st.expander("Preview Source Data"):
    st.dataframe(transactions.head(20), use_container_width=True, hide_index=True)

# Automation Rules
st.divider()
st.subheader("2. Automation Rules")

rules_data = load_automation_rules()
rules = rules_data["rules"]

st.write(f"**{len(rules)} automation rules available**")

for rule in rules:
    with st.expander(f"📋 {rule['rule_id']}: {rule['name']}"):
        st.markdown(f"**Description:** {rule['description']}")
        st.markdown(f"**Trigger:** Transaction type = `{rule['trigger'].get('transaction_type', 'any')}` "
                    f"{', Product pattern = `' + rule['trigger']['product_pattern'] + '`' if rule['trigger'].get('product_pattern') else ''}")

        st.markdown("**Journal Entry Template:**")
        for event, lines in rule["journal_entry"].items():
            st.markdown(f"*{event.replace('_', ' ').title()}:*")
            for line in lines:
                st.markdown(f"  - {line['type'].upper()}: {line['account']} ({line['amount']})")

# Process
st.divider()
st.subheader("3. Generate Journal Entries")

if st.button("Run Automation Engine", type="primary"):
    with st.spinner("Processing transactions..."):
        entries_df, processing_log = process_transactions(transactions, rules)

    if entries_df.empty:
        st.warning("No journal entries generated. Check that transactions match automation rules.")
        st.stop()

    # Processing summary
    matched = sum(1 for l in processing_log if l["status"] == "processed")
    unmatched = sum(1 for l in processing_log if l["status"] == "unmatched")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Transactions Processed", matched)
    m2.metric("Unmatched", unmatched)
    m3.metric("Journal Lines Generated", len(entries_df))

    # Balance validation
    is_balanced, total_d, total_c, diff = validate_balance(entries_df)
    m4.metric("Balance Check", "✅ Balanced" if is_balanced else f"❌ Off by {fmt_currency(diff)}")

    # Validation
    st.divider()
    st.subheader("4. Validation Results")

    issues = validate_entries_batch(entries_df)
    if issues.empty:
        st.success("All journal entries passed validation checks.")
    else:
        st.error(f"{len(issues)} validation issues found:")
        st.dataframe(issues, use_container_width=True, hide_index=True)

    # Summary by Account
    st.divider()
    st.subheader("5. Summary by Account")
    acct_summary = summarize_by_account(entries_df)
    acct_display = acct_summary.copy()
    for col in ["total_debit", "total_credit", "net"]:
        acct_display[col] = acct_display[col].apply(lambda x: fmt_currency(x))
    st.dataframe(acct_display, use_container_width=True, hide_index=True)

    # Summary by Rule
    st.subheader("Summary by Automation Rule")
    rule_summary = summarize_by_rule(entries_df)
    for col in ["total_debit", "total_credit"]:
        rule_summary[col] = rule_summary[col].apply(lambda x: fmt_currency(x))
    st.dataframe(rule_summary, use_container_width=True, hide_index=True)

    # Preview entries
    st.divider()
    st.subheader("6. Journal Entry Preview")

    entry_type_filter = st.selectbox("Filter by type:", ["All", "billing", "recognition"])
    preview = entries_df.copy()
    if entry_type_filter != "All":
        preview = preview[preview["entry_type"] == entry_type_filter]

    preview_display = preview.copy()
    preview_display["debit"] = preview_display["debit"].apply(lambda x: fmt_currency(x) if x > 0 else "")
    preview_display["credit"] = preview_display["credit"].apply(lambda x: fmt_currency(x) if x > 0 else "")
    st.dataframe(preview_display.head(50), use_container_width=True, hide_index=True)

    if len(preview) > 50:
        st.caption(f"Showing first 50 of {len(preview)} entries. Download full set below.")

    # Before/After comparison
    st.divider()
    st.subheader("7. Automation Impact")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Before Automation (Manual Process)**")
        st.markdown(f"- Transactions to review: **{len(transactions)}**")
        st.markdown(f"- Estimated manual time: **{len(transactions) * 3:.0f} minutes** (~3 min/entry)")
        st.markdown(f"- Error risk: **Medium-High** (manual data entry)")

    with col2:
        st.markdown("**After Automation**")
        st.markdown(f"- Auto-generated entries: **{len(entries_df)}**")
        st.markdown(f"- Processing time: **< 1 second**")
        st.markdown(f"- Validation: **{'All passed' if issues.empty else f'{len(issues)} issues flagged'}**")

    # Export
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        csv = entries_df.to_csv(index=False)
        st.download_button("Download Journal Entries (CSV)", csv,
                           "automated_journal_entries.csv", "text/csv")
    with col2:
        log_df = pd.DataFrame(processing_log)
        log_csv = log_df.to_csv(index=False)
        st.download_button("Download Processing Log (CSV)", log_csv,
                           "processing_log.csv", "text/csv")
