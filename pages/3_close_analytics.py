"""Close Cycle Analytics Page — Historical trends and automation impact."""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.csv_handler import load_historical_metrics
from components.metric_cards import render_close_metrics
from components.charts import (
    close_cycle_trend, automation_progress_chart,
    hours_saved_chart, before_after_comparison,
)
from utils.formatters import fmt_currency

st.set_page_config(page_title="Close Analytics | SmartClose", page_icon="📈", layout="wide")
st.title("📈 Close Cycle Analytics")
st.caption("Historical performance tracking and automation impact analysis")

# Load data
metrics = load_historical_metrics()

# Latest period metrics
latest = metrics.iloc[-1]
total_je = latest["manual_je_count"] + latest["automated_je_count"]
auto_pct = latest["automated_je_count"] / total_je * 100 if total_je > 0 else 0
tasks_pct = latest["tasks_on_time"] / latest["total_tasks"] * 100

st.subheader(f"Current Period: {latest['period']}")
render_close_metrics(
    days_to_close=int(latest["business_days_to_close"]),
    auto_pct=auto_pct,
    tasks_on_time_pct=tasks_pct,
    errors_caught=int(latest["errors_caught"]),
    hours_saved=latest["automation_hours_saved"],
)

# Close Cycle Trend
st.divider()
st.subheader("Close Cycle Duration Trend")
st.plotly_chart(close_cycle_trend(metrics), use_container_width=True)

# Automation Progress
st.divider()
st.subheader("Journal Entry Automation Progress")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(automation_progress_chart(metrics), use_container_width=True)
with col2:
    st.plotly_chart(hours_saved_chart(metrics), use_container_width=True)

# Cumulative impact
total_hours_saved = metrics["automation_hours_saved"].sum()
total_auto_je = metrics["automated_je_count"].sum()

impact_cols = st.columns(3)
impact_cols[0].metric("Total Hours Saved", f"{total_hours_saved:.0f} hours",
                       help="Cumulative hours saved across all periods")
impact_cols[1].metric("Equivalent FTEs", f"{total_hours_saved / 2080:.1f}",
                       help="Based on 2,080 working hours per year")
impact_cols[2].metric("Total Automated JEs", f"{total_auto_je:,}",
                       help="Total journal entries generated automatically")

# Before vs After Comparison
st.divider()
st.subheader("Before vs. After Automation")
st.caption("Comparing first 6 months (manual) with last 6 months (automated)")

st.plotly_chart(before_after_comparison(metrics), use_container_width=True)

# Detailed metrics table
pre = metrics.head(6)
post = metrics.tail(6)

comparison_data = {
    "Metric": [
        "Avg. Days to Close",
        "Avg. Manual JEs per Month",
        "Avg. Automated JEs per Month",
        "Automation Rate",
        "Avg. Errors Caught",
        "Tasks On Time %",
        "Avg. Hours Saved per Month",
    ],
    "Before Automation": [
        f"{pre['business_days_to_close'].mean():.1f} days",
        f"{pre['manual_je_count'].mean():.0f}",
        f"{pre['automated_je_count'].mean():.0f}",
        f"{pre['automated_je_count'].sum() / (pre['manual_je_count'].sum() + pre['automated_je_count'].sum()) * 100:.0f}%",
        f"{pre['errors_caught'].mean():.1f}",
        f"{(pre['tasks_on_time'] / pre['total_tasks'] * 100).mean():.0f}%",
        f"{pre['automation_hours_saved'].mean():.0f}h",
    ],
    "After Automation": [
        f"{post['business_days_to_close'].mean():.1f} days",
        f"{post['manual_je_count'].mean():.0f}",
        f"{post['automated_je_count'].mean():.0f}",
        f"{post['automated_je_count'].sum() / (post['manual_je_count'].sum() + post['automated_je_count'].sum()) * 100:.0f}%",
        f"{post['errors_caught'].mean():.1f}",
        f"{(post['tasks_on_time'] / post['total_tasks'] * 100).mean():.0f}%",
        f"{post['automation_hours_saved'].mean():.0f}h",
    ],
    "Improvement": [
        f"{pre['business_days_to_close'].mean() - post['business_days_to_close'].mean():.1f} days faster",
        f"{pre['manual_je_count'].mean() - post['manual_je_count'].mean():.0f} fewer",
        f"+{post['automated_je_count'].mean():.0f} automated",
        "Manual → Automated",
        f"{post['errors_caught'].mean() - pre['errors_caught'].mean():+.1f}",
        f"+{((post['tasks_on_time'] / post['total_tasks'] * 100).mean() - (pre['tasks_on_time'] / pre['total_tasks'] * 100).mean()):.0f}pp",
        f"+{post['automation_hours_saved'].mean():.0f}h/month",
    ],
}

st.dataframe(comparison_data, use_container_width=True, hide_index=True)

# Annualized savings highlight
st.divider()
st.subheader("Annualized Savings")

annual_hours = post["automation_hours_saved"].mean() * 12
hourly_rate = 75  # Assumed blended rate

savings_cols = st.columns(4)
savings_cols[0].metric("Annual Hours Saved", f"{annual_hours:.0f} hours")
savings_cols[1].metric("Equivalent FTEs", f"{annual_hours / 2080:.1f}",
                        help="~2 FTEs based on 2,080 hrs/year")
savings_cols[2].metric("Estimated Cost Savings", fmt_currency(annual_hours * hourly_rate),
                        help=f"At ${hourly_rate}/hr blended rate")
savings_cols[3].metric("Close Cycle Reduction", f"{pre['business_days_to_close'].mean() - post['business_days_to_close'].mean():.0f} days",
                        help="Average reduction in business days to close")
