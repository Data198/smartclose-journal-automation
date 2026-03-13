"""KPI metric display widgets."""

import streamlit as st


def render_close_metrics(days_to_close, auto_pct, tasks_on_time_pct, errors_caught, hours_saved):
    """Render close cycle KPI cards."""
    cols = st.columns(5)
    cols[0].metric("Days to Close", f"{days_to_close}", help="Business days from period end to close")
    cols[1].metric("Automation Rate", f"{auto_pct:.0f}%", help="% of journal entries generated automatically")
    cols[2].metric("Tasks On Time", f"{tasks_on_time_pct:.0f}%", help="% of close tasks completed by target date")
    cols[3].metric("Errors Caught", str(errors_caught), help="Validation errors caught by automation")
    cols[4].metric("Hours Saved", f"{hours_saved:.0f}h", help="Manual hours saved through automation this period")
